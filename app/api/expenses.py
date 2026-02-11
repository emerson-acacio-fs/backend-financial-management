import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.category import Category
from app.models.expense import Expense
from app.models.expense_split import ExpenseSplit
from app.models.group import Group
from app.models.user import User
from app.schemas.common import SuccessListResponse, SuccessResponse
from app.schemas.expense import ExpenseCreate, ExpenseOut, ExpenseSplitOut, ExpenseUpdate
from app.services.pagination import paginate
from app.services.split_service import validate_and_compute_splits

router = APIRouter(prefix="/expenses", tags=["expenses"])


def _ensure_owner_refs(db: Session, user: User, category_id, group_id):
    if category_id:
        category = db.scalar(
            select(Category).where(Category.id == category_id, Category.owner_id == user.id)
        )
        if not category:
            raise HTTPException(status_code=422, detail="Invalid category_id")
    if group_id:
        group = db.scalar(select(Group).where(Group.id == group_id, Group.owner_id == user.id))
        if not group:
            raise HTTPException(status_code=422, detail="Invalid group_id")


def _to_expense_out(db: Session, expense: Expense):
    splits = db.scalars(select(ExpenseSplit).where(ExpenseSplit.expense_id == expense.id)).all()
    return ExpenseOut.model_validate(
        {
            **expense.__dict__,
            "splits": [ExpenseSplitOut.model_validate(s) for s in splits],
        }
    )


@router.post("", response_model=SuccessResponse[ExpenseOut])
def create_expense(
    payload: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_owner_refs(db, current_user, payload.category_id, payload.group_id)
    computed = validate_and_compute_splits(
        db=db,
        owner_id=current_user.id,
        total_amount=payload.amount,
        split_type=payload.split_type,
        splits=payload.splits,
    )
    expense = Expense(owner_id=current_user.id, **payload.model_dump(exclude={"splits"}))
    db.add(expense)
    db.flush()
    for c in computed:
        sp = c["split"]
        db.add(
            ExpenseSplit(
                expense_id=expense.id,
                participant_type=sp.participant_type,
                participant_user_id=sp.user_id,
                participant_friend_id=sp.friend_id,
                share_amount=c["amount"],
                share_percentage=c["percentage"],
            )
        )
    db.commit()
    db.refresh(expense)
    return {"data": _to_expense_out(db, expense)}


@router.get("", response_model=SuccessListResponse[ExpenseOut])
def list_expenses(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    date_from: str | None = None,
    date_to: str | None = None,
    category_id: uuid.UUID | None = None,
    group_id: uuid.UUID | None = None,
    q: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conditions = [Expense.owner_id == current_user.id]
    if category_id:
        conditions.append(Expense.category_id == category_id)
    if group_id:
        conditions.append(Expense.group_id == group_id)
    if date_from:
        conditions.append(Expense.date >= date_from)
    if date_to:
        conditions.append(Expense.date <= date_to)
    if q:
        conditions.append(Expense.description.ilike(f"%{q}%"))

    stmt = select(Expense).where(and_(*conditions)).order_by(Expense.date.desc())
    items, meta = paginate(db, stmt, page, limit)
    return {"data": [_to_expense_out(db, i) for i in items], "meta": meta}


@router.get("/{expense_id}", response_model=SuccessResponse[ExpenseOut])
def get_expense(
    expense_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expense = db.scalar(
        select(Expense).where(Expense.id == expense_id, Expense.owner_id == current_user.id)
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"data": _to_expense_out(db, expense)}


@router.patch("/{expense_id}", response_model=SuccessResponse[ExpenseOut])
def update_expense(
    expense_id: uuid.UUID,
    payload: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expense = db.scalar(
        select(Expense).where(Expense.id == expense_id, Expense.owner_id == current_user.id)
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    update_data = payload.model_dump(exclude_unset=True)
    new_amount = update_data.get("amount", expense.amount)
    new_split_type = update_data.get("split_type", expense.split_type)
    new_splits = update_data.get("splits")

    _ensure_owner_refs(
        db,
        current_user,
        update_data.get("category_id", expense.category_id),
        update_data.get("group_id", expense.group_id),
    )

    for key, value in update_data.items():
        if key != "splits":
            setattr(expense, key, value)

    if new_splits is not None:
        computed = validate_and_compute_splits(
            db=db,
            owner_id=current_user.id,
            total_amount=new_amount,
            split_type=new_split_type,
            splits=new_splits,
        )
        db.query(ExpenseSplit).filter(ExpenseSplit.expense_id == expense.id).delete()
        for c in computed:
            sp = c["split"]
            db.add(
                ExpenseSplit(
                    expense_id=expense.id,
                    participant_type=sp.participant_type,
                    participant_user_id=sp.user_id,
                    participant_friend_id=sp.friend_id,
                    share_amount=c["amount"],
                    share_percentage=c["percentage"],
                )
            )

    db.commit()
    db.refresh(expense)
    return {"data": _to_expense_out(db, expense)}


@router.delete("/{expense_id}", response_model=SuccessResponse[dict])
def delete_expense(
    expense_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expense = db.scalar(
        select(Expense).where(Expense.id == expense_id, Expense.owner_id == current_user.id)
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.query(ExpenseSplit).filter(ExpenseSplit.expense_id == expense.id).delete()
    db.delete(expense)
    db.commit()
    return {"data": {"deleted": True}}
