from datetime import datetime
from typing import Dict, List, Optional

from fastapi import HTTPException
from prisma import Prisma
from prisma.enums import ProposalStatus, RequestStatus

from .audit import log_event


async def create_request(*, client_id: str, payload: Dict, files: Optional[List[Dict]] = None):
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  try:
    created = await prisma.request.create(
      data={
        "title": payload["title"],
        "description": payload["description"],
        "category": payload["category"],
        "budget": payload["budget"],
        "target_date": datetime.fromisoformat(payload["targetDate"]),
        "client": {"connect": {"id": client_id}}
      }
    )
    await log_event(action="request.created", user_id=client_id, request_id=created.id)
    return created
  finally:
    await prisma.disconnect()


async def list_open_requests(filters: Dict) -> List[Dict]:
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  try:
    where: Dict = {}
    if filters.get("client_id"):
      where["client_id"] = filters["client_id"]
    else:
      where["status"] = RequestStatus.OPEN
    if filters.get("category"):
      where["category"] = {"contains": filters["category"], "mode": "insensitive"}
    if filters.get("budget"):
      where["budget"] = filters["budget"]
    if filters.get("timeframe"):
      try:
        where["target_date"] = {"lte": datetime.fromisoformat(filters["timeframe"])}
      except ValueError:
        pass
    return await prisma.request.find_many(where=where, order={"target_date": "asc"})
  finally:
    await prisma.disconnect()


async def get_request_detail(request_id: str):
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  try:
    request = await prisma.request.find_unique(
      where={"id": request_id},
      include={"messages": {"include": {"author": True}}, "proposals": True}
    )
    if not request:
      raise HTTPException(status_code=404, detail="Request not found")
    return request
  finally:
    await prisma.disconnect()


async def create_message(*, request_id: str, author_id: str, body: str):
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  try:
    created = await prisma.message.create(
      data={
        "request": {"connect": {"id": request_id}},
        "author": {"connect": {"id": author_id}},
        "body": body
      },
      include={"author": True}
    )
    await log_event(action="message.posted", user_id=author_id, request_id=request_id)
    return created
  finally:
    await prisma.disconnect()


async def submit_proposal(*, request_id: str, consultant_id: str, scope: str, timeline: str, cost: float):
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  try:
    proposal = await prisma.proposal.create(
      data={
        "request": {"connect": {"id": request_id}},
        "consultant": {"connect": {"id": consultant_id}},
        "scope": scope,
        "timeline": timeline,
        "cost": cost
      }
    )
    await log_event(action="proposal.submitted", user_id=consultant_id, request_id=request_id)
    return proposal
  finally:
    await prisma.disconnect()


async def accept_proposal(proposal_id: str):
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  proposal = await prisma.proposal.update(
    where={"id": proposal_id},
    data={"status": ProposalStatus.ACCEPTED}
  )
  await log_event(action="proposal.accepted", request_id=proposal.request_id)
  return proposal
