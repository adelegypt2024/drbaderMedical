from datetime import datetime, timedelta
from typing import Dict

from fastapi import HTTPException
from prisma import Prisma
from prisma.enums import ContractStatus, InvoiceStatus, PaymentStatus, ProposalStatus

from .audit import log_event


async def activate_contract(*, proposal_id: str, milestones: list[Dict]):
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  try:
    proposal = await prisma.proposal.find_unique(
      where={"id": proposal_id},
      include={"request": True}
    )
    if not proposal:
      raise HTTPException(status_code=404, detail="Proposal not found")
    if proposal.status != ProposalStatus.ACCEPTED:
      raise HTTPException(status_code=400, detail="Proposal must be accepted before activation")
    contract = await prisma.contract.create(
      data={
        "proposal": {"connect": {"id": proposal_id}},
        "status": ContractStatus.ACTIVE,
        "effective_date": datetime.utcnow(),
        "terms": "Standard consulting agreement"
      }
    )
    for milestone in milestones:
      invoice = await prisma.invoice.create(
        data={
          "contract": {"connect": {"id": contract.id}},
          "amount": float(milestone.get("amount", 0)),
          "due_date": datetime.utcnow() + timedelta(days=int(milestone.get("due_in_days", 30)))
        }
      )
      await prisma.payment.create(
        data={
          "invoice": {"connect": {"id": invoice.id}},
          "payer": {"connect": {"id": proposal.request.client_id}},
          "payee": {"connect": {"id": proposal.consultant_id}},
          "amount": invoice.amount
        }
      )
    await log_event(action="contract.activated", contract_id=contract.id, request_id=proposal.request_id)
    return contract
  finally:
    await prisma.disconnect()


async def handle_payment_webhook(*, invoice_id: str, status: str, provider_reference: str | None):
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  try:
    invoice = await prisma.invoice.find_unique(where={"id": invoice_id})
    if not invoice:
      raise HTTPException(status_code=404, detail="Invoice not found")
    payment = await prisma.payment.find_first(where={"invoice_id": invoice_id})
    if not payment:
      raise HTTPException(status_code=404, detail="Payment not found")
    await prisma.invoice.update(
      where={"id": invoice_id},
      data={"status": InvoiceStatus.PAID if status == "SUCCEEDED" else InvoiceStatus.OPEN}
    )
    await prisma.payment.update(
      where={"id": payment.id},
      data={
        "status": PaymentStatus.SUCCEEDED if status == "SUCCEEDED" else PaymentStatus.FAILED,
        "processed_at": datetime.utcnow(),
        "provider_ref": provider_reference
      }
    )
    await log_event(action="payment.updated", contract_id=invoice.contract_id, metadata={"status": status})
    return {"status": status}
  finally:
    await prisma.disconnect()
