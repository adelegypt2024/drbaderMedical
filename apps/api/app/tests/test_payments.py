import pytest

from app.services import contracts as contract_service


@pytest.mark.asyncio
async def test_webhook(monkeypatch, client):
  async def fake_handle(**kwargs):
    return {"status": kwargs["status"]}

  monkeypatch.setattr(contract_service, "handle_payment_webhook", fake_handle)

  response = client.post(
    "/payments/webhook",
    json={"invoiceId": "inv-1", "status": "SUCCEEDED", "providerReference": "abc"}
  )
  assert response.status_code == 200
  assert response.json()["status"] == "SUCCEEDED"
