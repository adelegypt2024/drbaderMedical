from fastapi import APIRouter, Depends

from ..dependencies import get_current_user
from ..schemas import DashboardResponse
from ..services.dashboard import fetch_dashboard_counts

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(current_user=Depends(get_current_user)):
  data = await fetch_dashboard_counts(current_user.id, current_user.role)
  return DashboardResponse.model_validate(data)
