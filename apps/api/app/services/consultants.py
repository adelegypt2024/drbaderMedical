from typing import Dict

from fastapi import HTTPException
from prisma import Prisma


async def get_profile(user_id: str):
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  profile = await prisma.consultantprofile.find_unique(where={"user_id": user_id})
  if not profile:
    profile = await prisma.consultantprofile.create(
      data={
        "user": {"connect": {"id": user_id}},
        "specialties": [],
        "hourly_rate": 0,
        "years_experience": 0
      }
    )
  return profile


async def upsert_profile(user_id: str, payload: Dict):
  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  return await prisma.consultantprofile.upsert(
    where={"user_id": user_id},
    data={
      "create": {
        "user": {"connect": {"id": user_id}},
        "specialties": payload.get("specialties", []),
        "hourly_rate": payload.get("hourlyRate", 0),
        "years_experience": payload.get("yearsExperience", 0),
        "bio": payload.get("bio"),
        "availability": payload.get("availability"),
        "portfolio_url": payload.get("portfolioUrl"),
      },
      "update": {
        "specialties": payload.get("specialties", []),
        "hourly_rate": payload.get("hourlyRate", 0),
        "years_experience": payload.get("yearsExperience", 0),
        "bio": payload.get("bio"),
        "availability": payload.get("availability"),
        "portfolio_url": payload.get("portfolioUrl"),
      }
    }
  )
