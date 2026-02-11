import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import ParticipantType


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    expense_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("expenses.id", ondelete="CASCADE"), index=True
    )
    participant_type: Mapped[ParticipantType] = mapped_column(
        Enum(ParticipantType, name="participant_type_enum")
    )
    participant_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=True
    )
    participant_friend_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("friends.id"), nullable=True
    )
    share_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    share_percentage: Mapped[Decimal | None] = mapped_column(Numeric(7, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
