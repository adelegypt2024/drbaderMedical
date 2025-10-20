from fastapi import APIRouter, Depends

from ..dependencies import get_current_user, require_roles
from ..schemas import ConsultantProfileOut, ConsultantProfileUpdate, RequestSummary
from ..services import requests as requests_service
from ..services.consultants import get_profile, upsert_profile

router = APIRouter(prefix="/consultants", tags=["consultants"], dependencies=[Depends(require_roles("consultant"))])


@router.get("/me", response_model=ConsultantProfileOut)
async def my_profile(current_user=Depends(get_current_user)):
  profile = await get_profile(current_user.id)
  return ConsultantProfileOut.model_validate(profile, from_attributes=True)


@router.put("/me", response_model=ConsultantProfileOut)
async def update_profile(payload: ConsultantProfileUpdate, current_user=Depends(get_current_user)):
  profile = await upsert_profile(current_user.id, payload.model_dump())
  return ConsultantProfileOut.model_validate(profile, from_attributes=True)


@router.get("/requests", response_model=list[RequestSummary])
async def open_requests(category: str | None = None, budget: str | None = None, timeframe: str | None = None):
  filters = {"category": category, "budget": budget, "timeframe": timeframe}
  filtered = await requests_service.list_open_requests(filters)
  return [RequestSummary.model_validate(item, from_attributes=True) for item in filtered]
