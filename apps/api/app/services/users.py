from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from typing import Any, Dict, Optional

from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException
from prisma import Prisma

from ..core.config import get_settings
from ..core.security import get_password_hash
from ..utils.mail import send_templated_email


async def get_user_by_email(email: str, client: Optional[Prisma] = None):
  prisma = client or Prisma()
  owns_client = client is None
  if not prisma.is_connected():
    await prisma.connect()
  try:
    return await prisma.user.find_unique(where={"email": email.lower()})
  finally:
    if owns_client:
      await prisma.disconnect()


async def get_user_by_id(user_id: str, client: Optional[Prisma] = None):
  prisma = client or Prisma()
  owns_client = client is None
  if not prisma.is_connected():
    await prisma.connect()
  try:
    return await prisma.user.find_unique(where={"id": user_id})
  finally:
    if owns_client:
      await prisma.disconnect()


async def create_user(data: Dict[str, Any]):
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  try:
    try:
      validated = validate_email(data["email"])
    except EmailNotValidError as exc:
      raise HTTPException(status_code=400, detail=str(exc))

    hashed_password = get_password_hash(data.pop("password"))
    user = await prisma.user.create(
      data={
        **data,
        "email": validated.email.lower(),
        "password_hash": hashed_password,
        "email_verified": False,
        "verification_token": await _generate_token(prisma, "verification"),
      }
    )

    settings = get_settings()
    await send_templated_email(
      to=user.email,
      subject="Verify your email",
      template="verify_email.html",
      context={"token": user.verification_token, "frontend_base": settings.frontend_base_url},
    )

    return user
  finally:
    await prisma.disconnect()


async def request_password_reset(email: str):
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  try:
    user = await prisma.user.find_unique(where={"email": email.lower()})
    if not user:
      return
    token = await _generate_token(prisma, "reset")
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    await prisma.user.update(
      where={"id": user.id},
      data={"reset_token": token, "reset_token_expires": expire}
    )
    settings = get_settings()
    await send_templated_email(
      to=user.email,
      subject="Reset your password",
      template="password_reset.html",
      context={"token": token, "frontend_base": settings.frontend_base_url},
    )
  finally:
    await prisma.disconnect()


async def confirm_password_reset(token: str, password: str):
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  try:
    user = await prisma.user.find_first(where={"reset_token": token})
    if not user:
      raise HTTPException(status_code=400, detail="Invalid token")
    if user.reset_token_expires and user.reset_token_expires < datetime.now(timezone.utc):
      raise HTTPException(status_code=400, detail="Token expired")
    await prisma.user.update(
      where={"id": user.id},
      data={"password_hash": get_password_hash(password), "reset_token": None, "reset_token_expires": None}
    )
  finally:
    await prisma.disconnect()


async def verify_email(token: str):
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  try:
    user = await prisma.user.find_first(where={"verification_token": token})
    if not user:
      raise HTTPException(status_code=400, detail="Invalid token")
    await prisma.user.update(
      where={"id": user.id},
      data={"email_verified": True, "verification_token": None}
    )
  finally:
    await prisma.disconnect()


async def _generate_token(_: Prisma, prefix: str) -> str:
  return f"{prefix}_{token_urlsafe(32)}"
