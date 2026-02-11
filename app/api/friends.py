import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.friend import Friend
from app.models.user import User
from app.schemas.common import SuccessListResponse, SuccessResponse
from app.schemas.friend import FriendCreate, FriendOut, FriendUpdate
from app.services.pagination import paginate

router = APIRouter(prefix="/friends", tags=["friends"])


@router.post("", response_model=SuccessResponse[FriendOut])
def create_friend(
    payload: FriendCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    friend = Friend(owner_id=current_user.id, **payload.model_dump())
    db.add(friend)
    db.commit()
    db.refresh(friend)
    return {"data": FriendOut.model_validate(friend)}


@router.get("", response_model=SuccessListResponse[FriendOut])
def list_friends(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    name: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(Friend).where(Friend.owner_id == current_user.id)
    if name:
        stmt = stmt.where(Friend.name.ilike(f"%{name}%"))
    stmt = stmt.order_by(Friend.created_at.desc())
    items, meta = paginate(db, stmt, page, limit)
    return {"data": [FriendOut.model_validate(i) for i in items], "meta": meta}


@router.get("/{friend_id}", response_model=SuccessResponse[FriendOut])
def get_friend(
    friend_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    friend = db.scalar(
        select(Friend).where(Friend.id == friend_id, Friend.owner_id == current_user.id)
    )
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
    return {"data": FriendOut.model_validate(friend)}


@router.patch("/{friend_id}", response_model=SuccessResponse[FriendOut])
def update_friend(
    friend_id: uuid.UUID,
    payload: FriendUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    friend = db.scalar(
        select(Friend).where(Friend.id == friend_id, Friend.owner_id == current_user.id)
    )
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(friend, key, value)
    db.commit()
    db.refresh(friend)
    return {"data": FriendOut.model_validate(friend)}


@router.delete("/{friend_id}", response_model=SuccessResponse[dict])
def delete_friend(
    friend_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    friend = db.scalar(
        select(Friend).where(Friend.id == friend_id, Friend.owner_id == current_user.id)
    )
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
    db.delete(friend)
    db.commit()
    return {"data": {"deleted": True}}
