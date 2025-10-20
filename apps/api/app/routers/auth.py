from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from prisma import Prisma

from ..core.config import get_settings
from ..core.security import create_access_token, verify_password
from ..dependencies import get_current_user
from ..schemas import (
  EmailVerification,
  PasswordResetConfirm,
  PasswordResetRequest,
  Token,
  UserBase,
  UserCreate,
)
from ..services import users as users_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserBase, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate):
  existing = await users_service.get_user_by_email(payload.email)
  if existing:
    raise HTTPException(status_code=400, detail="Email already registered")
  created = await users_service.create_user(
    {
      "email": payload.email,
      "first_name": payload.firstName,
      "last_name": payload.lastName,
      "role": payload.role,
      "password": payload.password,
    }
  )
  return UserBase.model_validate(created, from_attributes=True)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
  user = await users_service.get_user_by_email(form_data.username)
  if not user or not verify_password(form_data.password, user.password_hash):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
  if not user.email_verified:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not verified")
  token = create_access_token(subject=user.id)
  return Token(access_token=token)


@router.get("/me", response_model=UserBase)
async def get_me(current_user=Depends(get_current_user)):
  return UserBase.model_validate(current_user, from_attributes=True)


@router.post("/password-reset")
async def password_reset(payload: PasswordResetRequest):
  await users_service.request_password_reset(payload.email)
  return {"status": "ok"}


@router.post("/password-reset/confirm")
async def password_reset_confirm(payload: PasswordResetConfirm):
  await users_service.confirm_password_reset(payload.token, payload.password)
  return {"status": "ok"}


@router.post("/verify-email")
async def verify_email(payload: EmailVerification):
  await users_service.verify_email(payload.token)
  return {"status": "ok"}
