from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int


class SuccessResponse(BaseModel, Generic[T]):
    data: T


class SuccessListResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: PaginationMeta


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict | list | None = None


class ErrorResponse(BaseModel):
    error: ErrorPayload


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
