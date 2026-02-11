import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class GroupBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None


class GroupOut(ORMBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
