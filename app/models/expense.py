import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import SplitType


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    description: Mapped[str] = mapped_column(String(255), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="BRL")
    date: Mapped[date] = mapped_column(Date)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("categories.id"), nullable=True
    )
    group_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("groups.id"), nullable=True)
    split_type: Mapped[SplitType] = mapped_column(Enum(SplitType, name="split_type_enum"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
