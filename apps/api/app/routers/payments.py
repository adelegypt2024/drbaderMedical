from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_current_user, require_roles
from ..schemas import PaymentWebhook
from ..services.contracts import activate_contract, handle_payment_webhook

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/activate", dependencies=[Depends(require_roles("client"))])
async def activate(proposal_id: str, current_user=Depends(get_current_user)):
  contract = await activate_contract(proposal_id=proposal_id, milestones=[{"amount": 5000, "due_in_days": 30}])
  return contract


@router.post("/webhook")
async def webhook(payload: PaymentWebhook):
  return await handle_payment_webhook(
    invoice_id=payload.invoiceId,
    status=payload.status,
    provider_reference=payload.providerReference,
  )
