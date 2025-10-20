from types import SimpleNamespace

import pytest

from app.core.security import get_password_hash
from app.services import users as users_service


@pytest.mark.asyncio
async def test_login_success(monkeypatch, client):
  hashed = get_password_hash("secret")
  user = SimpleNamespace(id="user-1", password_hash=hashed, email_verified=True)

  async def fake_get_user(email):
    assert email == "test@example.com"
    return user

  monkeypatch.setattr(users_service, "get_user_by_email", fake_get_user)

  response = client.post(
    "/auth/login",
    data={"username": "test@example.com", "password": "secret"},
    headers={"content-type": "application/x-www-form-urlencoded"}
  )

  assert response.status_code == 200
  assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_requires_verification(monkeypatch, client):
  hashed = get_password_hash("secret")
  user = SimpleNamespace(id="user-1", password_hash=hashed, email_verified=False)

  async def fake_get_user(email):
    return user

  monkeypatch.setattr(users_service, "get_user_by_email", fake_get_user)

  response = client.post(
    "/auth/login",
    data={"username": "test@example.com", "password": "secret"},
    headers={"content-type": "application/x-www-form-urlencoded"}
  )

  assert response.status_code == 400
  assert response.json()["detail"] == "Email not verified"
