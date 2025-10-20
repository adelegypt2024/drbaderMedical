from types import SimpleNamespace

import pytest

from app.services import requests as requests_service
from app.services import files as file_service


@pytest.fixture(autouse=True)
def mock_current_user(monkeypatch):
  async def fake_get_current_user():
    return SimpleNamespace(id="user-1", role="client")

  monkeypatch.setattr("app.routers.requests.get_current_user", fake_get_current_user)
  yield


def test_create_request(monkeypatch, client):
  async def fake_create_request(client_id, payload):
    assert client_id == "user-1"
    return SimpleNamespace(
      id="req-1",
      title=payload["title"],
      category=payload["category"],
      budget=payload["budget"],
      target_date="2024-01-01T00:00:00",
      status="OPEN"
    )

  async def fake_get_detail(request_id):
    return SimpleNamespace(
      id="req-1",
      title="Need help",
      category="Ops",
      budget="$5k",
      target_date="2024-01-01T00:00:00",
      status="OPEN"
    )

  async def fake_save_file(*args, **kwargs):
    return {"id": "file-1", "filename": "doc.pdf", "url": "s3://bucket/doc.pdf"}

  monkeypatch.setattr(requests_service, "create_request", fake_create_request)
  monkeypatch.setattr(requests_service, "get_request_detail", fake_get_detail)
  monkeypatch.setattr(file_service, "save_file", fake_save_file)

  response = client.post(
    "/requests",
    data={
      "title": "Need help",
      "description": "desc",
      "category": "Ops",
      "budget": "$5k",
      "targetDate": "2024-01-01T00:00:00"
    }
  )
  assert response.status_code == 200
  payload = response.json()
  assert payload["title"] == "Need help"


def test_consultant_proposal(monkeypatch, client):
  async def fake_user():
    return SimpleNamespace(id="consultant-1", role="consultant")

  async def fake_submit(**kwargs):
    assert kwargs["scope"] == "Scope"
    return {"id": "prop-1", "status": "PENDING"}

  monkeypatch.setattr("app.routers.requests.get_current_user", fake_user)
  monkeypatch.setattr(requests_service, "submit_proposal", fake_submit)

  response = client.post(
    "/requests/req-1/proposals",
    json={"scope": "Scope", "timeline": "2 weeks", "cost": 5000}
  )
  assert response.status_code == 200
