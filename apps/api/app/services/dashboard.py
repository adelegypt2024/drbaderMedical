from prisma import Prisma


async def fetch_dashboard_counts(user_id: str, role: str) -> dict:
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  try:
    if role == "client":
      requests_count = await prisma.request.count(where={"client_id": user_id})
      proposals_count = await prisma.proposal.count(where={"request": {"is": {"client_id": user_id}}})
    elif role == "consultant":
      requests_count = await prisma.request.count(where={"status": "OPEN"})
      proposals_count = await prisma.proposal.count(where={"consultant_id": user_id})
    else:
      requests_count = await prisma.request.count()
      proposals_count = await prisma.proposal.count()
    contracts_count = await prisma.contract.count()
    invoices_count = await prisma.invoice.count()
    return {
      "requests": requests_count,
      "proposals": proposals_count,
      "contracts": contracts_count,
      "invoices": invoices_count,
      "notifications": []
    }
  finally:
    await prisma.disconnect()


async def fetch_admin_dashboard() -> dict:
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  try:
    revenue_result = await prisma.invoice.aggregate(_sum={"amount": True})
    return {
      "users": await prisma.user.count(),
      "requests": await prisma.request.count(),
      "contracts": await prisma.contract.count(),
      "revenue": float(revenue_result["_sum"]["amount"] or 0),
      "reports": [
        {"label": "Open requests", "value": await prisma.request.count(where={"status": "OPEN"})},
        {"label": "Accepted proposals", "value": await prisma.proposal.count(where={"status": "ACCEPTED"})},
      ]
    }
  finally:
    await prisma.disconnect()
