import enum


class SplitType(str, enum.Enum):
    amount = "amount"
    percentage = "percentage"


class ParticipantType(str, enum.Enum):
    user = "user"
    friend = "friend"
