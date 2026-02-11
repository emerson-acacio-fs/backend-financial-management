import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    color: str | None = Field(default=None, max_length=20)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    color: str | None = Field(default=None, max_length=20)


class CategoryOut(ORMBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    color: str | None
    created_at: datetime
