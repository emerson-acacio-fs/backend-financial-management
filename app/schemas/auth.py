from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserOut


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1, max_length=120)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthOut(TokenOut):
    user: UserOut
