import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2] / 'apps' / 'api'))

from prisma import Prisma
from prisma.enums import UserRole, ProposalStatus

from app.core.security import get_password_hash


data = {
  "organizations": [
    {"name": "Health Partners", "industry": "Healthcare"},
    {"name": "Wellness Group", "industry": "Telemedicine"}
  ],
  "users": [
    {
      "email": "admin@example.com",
      "first_name": "Alice",
      "last_name": "Admin",
      "role": UserRole.admin,
      "password_hash": get_password_hash("adminpass"),
      "email_verified": True
    },
    {
      "email": "client@example.com",
      "first_name": "Cathy",
      "last_name": "Client",
      "role": UserRole.client,
      "password_hash": get_password_hash("clientpass"),
      "email_verified": True
    },
    {
      "email": "consultant@example.com",
      "first_name": "Carlos",
      "last_name": "Consultant",
      "role": UserRole.consultant,
      "password_hash": get_password_hash("consultantpass"),
      "email_verified": True
    }
  ]
}


async def run():
  prisma = Prisma()
  await prisma.connect()

  for org in data["organizations"]:
    await prisma.organization.upsert(
      where={"name": org["name"]},
      data={
        "create": org,
        "update": {}
      }
    )

  client = await prisma.user.find_unique(where={"email": "client@example.com"})
  consultant = await prisma.user.find_unique(where={"email": "consultant@example.com"})

  if client and consultant:
    await prisma.consultantprofile.upsert(
      where={"user_id": consultant.id},
      data={
        "create": {
          "user": {"connect": {"id": consultant.id}},
          "specialties": ["Telehealth", "Operations"],
          "hourly_rate": 250,
          "years_experience": 8,
          "bio": "Experienced medical operations consultant.",
          "availability": "Weekdays",
          "portfolio_url": "https://portfolio.example.com/carlos"
        },
        "update": {
          "specialties": ["Telehealth", "Operations"],
          "hourly_rate": 250
        }
      }
    )

    request = await prisma.request.upsert(
      where={"id": "seed-request"},
      data={
        "create": {
          "id": "seed-request",
          "title": "Telehealth workflow audit",
          "description": "Review our telehealth processes and suggest improvements.",
          "category": "Operations",
          "budget": "$10k-$25k",
          "target_date": datetime.utcnow() + timedelta(days=30),
          "client": {"connect": {"id": client.id}},
        },
        "update": {}
      },
      include={"proposals": True}
    )

    if not request.proposals:
      await prisma.proposal.create(
        data={
          "request": {"connect": {"id": request.id}},
          "consultant": {"connect": {"id": consultant.id}},
          "scope": "End-to-end audit with recommendations",
          "timeline": "4 weeks",
          "cost": 12000,
          "status": ProposalStatus.PENDING
        }
      )

  await prisma.disconnect()


if __name__ == "__main__":
  asyncio.run(run())
