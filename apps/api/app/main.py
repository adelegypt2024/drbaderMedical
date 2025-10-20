from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .routers import admin, appointments, auth, consultants, dashboard, payments, requests

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(requests.router)
app.include_router(consultants.router)
app.include_router(appointments.router)
app.include_router(payments.router)
app.include_router(admin.router)


@app.get("/health")
async def healthcheck():
  return {"status": "ok"}
