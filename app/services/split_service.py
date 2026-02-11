from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.enums import ParticipantType, SplitType
from app.models.friend import Friend
from app.models.user import User
from app.schemas.expense import ExpenseSplitIn

TWOPLACES = Decimal("0.01")


def validate_and_compute_splits(
    db: Session,
    owner_id,
    total_amount: Decimal,
    split_type: SplitType,
    splits: list[ExpenseSplitIn],
):
    if not splits:
        raise HTTPException(status_code=422, detail="Split must have at least one participant")

    for split in splits:
        if split.participant_type == ParticipantType.user:
            user = db.get(User, split.user_id)
            if not user:
                raise HTTPException(status_code=422, detail="Invalid user participant")
        else:
            friend = db.get(Friend, split.friend_id)
            if not friend or friend.owner_id != owner_id:
                raise HTTPException(status_code=422, detail="Invalid friend participant")

    computed = []
    if split_type == SplitType.amount:
        sum_amount = Decimal("0")
        for split in splits:
            if split.share_amount is None:
                raise HTTPException(
                    status_code=422, detail="share_amount is required for amount split"
                )
            sum_amount += split.share_amount
            computed.append({"amount": split.share_amount, "percentage": None, "split": split})
        if sum_amount.quantize(TWOPLACES) != total_amount.quantize(TWOPLACES):
            raise HTTPException(status_code=422, detail="Split amounts must equal expense amount")
        return computed

    sum_percentage = Decimal("0")
    for split in splits:
        if split.share_percentage is None:
            raise HTTPException(
                status_code=422, detail="share_percentage is required for percentage split"
            )
        sum_percentage += split.share_percentage
    if sum_percentage.quantize(Decimal("0.0001")) != Decimal("100.0000"):
        raise HTTPException(status_code=422, detail="Split percentages must equal 100")

    running = Decimal("0")
    for idx, split in enumerate(splits):
        if idx == len(splits) - 1:
            amount = (total_amount - running).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
        else:
            amount = (total_amount * split.share_percentage / Decimal("100")).quantize(
                TWOPLACES, rounding=ROUND_HALF_UP
            )
            running += amount
        computed.append({"amount": amount, "percentage": split.share_percentage, "split": split})
    return computed
