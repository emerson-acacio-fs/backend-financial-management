import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.schemas.common import SuccessListResponse, SuccessResponse
from app.services.pagination import paginate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=SuccessResponse[CategoryOut])
def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    category = Category(owner_id=current_user.id, **payload.model_dump())
    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Category name already exists")
    db.refresh(category)
    return {"data": CategoryOut.model_validate(category)}


@router.get("", response_model=SuccessListResponse[CategoryOut])
def list_categories(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    name: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(Category).where(Category.owner_id == current_user.id)
    if name:
        stmt = stmt.where(Category.name.ilike(f"%{name}%"))
    stmt = stmt.order_by(Category.created_at.desc())
    items, meta = paginate(db, stmt, page, limit)
    return {"data": [CategoryOut.model_validate(i) for i in items], "meta": meta}


@router.get("/{category_id}", response_model=SuccessResponse[CategoryOut])
def get_category(
    category_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    category = db.scalar(
        select(Category).where(Category.id == category_id, Category.owner_id == current_user.id)
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"data": CategoryOut.model_validate(category)}


@router.patch("/{category_id}", response_model=SuccessResponse[CategoryOut])
def update_category(
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    category = db.scalar(
        select(Category).where(Category.id == category_id, Category.owner_id == current_user.id)
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Category name already exists")
    db.refresh(category)
    return {"data": CategoryOut.model_validate(category)}


@router.delete("/{category_id}", response_model=SuccessResponse[dict])
def delete_category(
    category_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    category = db.scalar(
        select(Category).where(Category.id == category_id, Category.owner_id == current_user.id)
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"data": {"deleted": True}}
