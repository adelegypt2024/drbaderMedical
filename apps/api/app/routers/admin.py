from fastapi import APIRouter, Depends

from ..dependencies import require_roles
from ..schemas import AdminDashboardResponse
from ..services.dashboard import fetch_admin_dashboard

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_roles("admin"))])


@router.get("/dashboard", response_model=AdminDashboardResponse)
async def admin_dashboard():
  data = await fetch_admin_dashboard()
  return AdminDashboardResponse.model_validate(data)
