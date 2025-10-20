from datetime import datetime
from typing import Dict

from fastapi import HTTPException
from prisma import Prisma

from .audit import log_event


async def create_appointment(*, user_id: str, payload: Dict):
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  start = datetime.fromisoformat(payload["startTime"])
  end = datetime.fromisoformat(payload["endTime"])
  if end <= start:
    raise HTTPException(status_code=400, detail="End must be after start")
  data = {
    "title": payload["title"],
    "start_time": start,
    "end_time": end,
    "timezone": payload["timezone"],
    "participant": {"connect": {"id": user_id}}
  }
  if payload.get("requestId"):
    data["request"] = {"connect": {"id": payload["requestId"]}}
  try:
    appointment = await prisma.appointment.create(data=data)
    await log_event(action="appointment.created", user_id=user_id, request_id=payload.get("requestId"))
    return appointment
  finally:
    await prisma.disconnect()


async def list_appointments(user_id: str):
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  try:
    return await prisma.appointment.find_many(
      where={
        "OR": [
          {"participant_id": user_id},
          {"consultant": {"is": {"user_id": user_id}}},
        ]
      },
      order={"start_time": "asc"}
    )
  finally:
    await prisma.disconnect()
