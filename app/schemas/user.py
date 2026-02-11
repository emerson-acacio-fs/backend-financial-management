import uuid
from datetime import datetime

from app.schemas.common import ORMBase


class UserOut(ORMBase):
    id: uuid.UUID
    email: str
    name: str
    created_at: datetime
