from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from .core.config import get_settings
from .services import users as users_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_prisma_client():
  from prisma import Prisma

  client = Prisma()
  if not client.is_connected():
    await client.connect()
  return client


async def get_current_user(token: str = Depends(oauth2_scheme)):
  settings = get_settings()
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
  )
  try:
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    user_id: str | None = payload.get("sub")
    if user_id is None:
      raise credentials_exception
  except JWTError as exc:  # pragma: no cover - defensive
    raise credentials_exception from exc

  user = await users_service.get_user_by_id(user_id)
  if user is None:
    raise credentials_exception
  return user


def require_roles(*roles: str):
  async def _dependency(user=Depends(get_current_user)):
    if user.role not in roles:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return user

  return _dependency
