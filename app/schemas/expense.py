import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.models.enums import ParticipantType, SplitType
from app.schemas.common import ORMBase


class ExpenseSplitIn(BaseModel):
    participant_type: ParticipantType
    user_id: uuid.UUID | None = None
    friend_id: uuid.UUID | None = None
    share_amount: Decimal | None = None
    share_percentage: Decimal | None = None

    @model_validator(mode="after")
    def validate_participant(self):
        if self.user_id and self.friend_id:
            raise ValueError("participant cannot have both user_id and friend_id")
        if self.participant_type == ParticipantType.user and not self.user_id:
            raise ValueError("user participant requires user_id")
        if self.participant_type == ParticipantType.friend and not self.friend_id:
            raise ValueError("friend participant requires friend_id")
        return self


class ExpenseBase(BaseModel):
    description: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(gt=0)
    currency: str = Field(default="BRL", min_length=3, max_length=3)
    date: date = Field(default_factory=date.today)
    category_id: uuid.UUID | None = None
    group_id: uuid.UUID | None = None
    split_type: SplitType
    splits: list[ExpenseSplitIn]


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    description: str | None = Field(default=None, min_length=1, max_length=255)
    amount: Decimal | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    date: date | None = None
    category_id: uuid.UUID | None = None
    group_id: uuid.UUID | None = None
    split_type: SplitType | None = None
    splits: list[ExpenseSplitIn] | None = None


class ExpenseSplitOut(ORMBase):
    id: uuid.UUID
    expense_id: uuid.UUID
    participant_type: ParticipantType
    participant_user_id: uuid.UUID | None
    participant_friend_id: uuid.UUID | None
    share_amount: Decimal
    share_percentage: Decimal | None
    created_at: datetime


class ExpenseOut(ORMBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    description: str
    amount: Decimal
    currency: str
    date: date = Field(default_factory=date.today)
    category_id: uuid.UUID | None
    group_id: uuid.UUID | None
    split_type: SplitType
    created_at: datetime
    splits: list[ExpenseSplitOut]
