from typing import Any, Dict, Optional

from prisma import Prisma


async def log_event(*, action: str, user_id: Optional[str] = None, request_id: Optional[str] = None, contract_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  try:
    await prisma.audit.create(
      data={
        "action": action,
        "user_id": user_id,
        "request_id": request_id,
        "contract_id": contract_id,
        "metadata": metadata or {}
      }
    )
  finally:
    await prisma.disconnect()
