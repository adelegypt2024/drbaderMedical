from fastapi import APIRouter, Depends

from ..dependencies import get_current_user
from ..schemas import AppointmentCreate, AppointmentOut
from ..services import appointments as appointment_service

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("", response_model=list[AppointmentOut])
async def list_appointments(current_user=Depends(get_current_user)):
  items = await appointment_service.list_appointments(current_user.id)
  return [AppointmentOut.model_validate(item, from_attributes=True) for item in items]


@router.post("", response_model=AppointmentOut)
async def create_appointment(payload: AppointmentCreate, current_user=Depends(get_current_user)):
  appointment = await appointment_service.create_appointment(user_id=current_user.id, payload=payload.model_dump())
  return AppointmentOut.model_validate(appointment, from_attributes=True)
