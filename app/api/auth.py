from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.auth import AuthOut, LoginIn, RegisterIn, TokenOut
from app.schemas.common import SuccessResponse
from app.schemas.user import UserOut
from app.services.auth_service import login_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=SuccessResponse[AuthOut])
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    token, user = register_user(db, payload)
    return {"data": AuthOut(access_token=token, user=UserOut.model_validate(user))}


@router.post("/login", response_model=SuccessResponse[TokenOut])
def login(payload: LoginIn, db: Session = Depends(get_db)):
    token = login_user(db, payload)
    return {"data": TokenOut(access_token=token)}


@router.get("/me", response_model=SuccessResponse[UserOut])
def me(current_user: User = Depends(get_current_user)):
    return {"data": UserOut.model_validate(current_user)}
