import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class FriendBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    notes: str | None = None


class FriendCreate(FriendBase):
    pass


class FriendUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    notes: str | None = None


class FriendOut(ORMBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    notes: str | None
    created_at: datetime
