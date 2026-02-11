import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.group import Group
from app.models.user import User
from app.schemas.common import SuccessListResponse, SuccessResponse
from app.schemas.group import GroupCreate, GroupOut, GroupUpdate
from app.services.pagination import paginate

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("", response_model=SuccessResponse[GroupOut])
def create_group(
    payload: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = Group(owner_id=current_user.id, **payload.model_dump())
    db.add(group)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Group name already exists")
    db.refresh(group)
    return {"data": GroupOut.model_validate(group)}


@router.get("", response_model=SuccessListResponse[GroupOut])
def list_groups(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    name: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(Group).where(Group.owner_id == current_user.id)
    if name:
        stmt = stmt.where(Group.name.ilike(f"%{name}%"))
    stmt = stmt.order_by(Group.created_at.desc())
    items, meta = paginate(db, stmt, page, limit)
    return {"data": [GroupOut.model_validate(i) for i in items], "meta": meta}


@router.get("/{group_id}", response_model=SuccessResponse[GroupOut])
def get_group(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = db.scalar(select(Group).where(Group.id == group_id, Group.owner_id == current_user.id))
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"data": GroupOut.model_validate(group)}


@router.patch("/{group_id}", response_model=SuccessResponse[GroupOut])
def update_group(
    group_id: uuid.UUID,
    payload: GroupUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = db.scalar(select(Group).where(Group.id == group_id, Group.owner_id == current_user.id))
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(group, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Group name already exists")
    db.refresh(group)
    return {"data": GroupOut.model_validate(group)}


@router.delete("/{group_id}", response_model=SuccessResponse[dict])
def delete_group(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = db.scalar(select(Group).where(Group.id == group_id, Group.owner_id == current_user.id))
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    db.delete(group)
    db.commit()
    return {"data": {"deleted": True}}
