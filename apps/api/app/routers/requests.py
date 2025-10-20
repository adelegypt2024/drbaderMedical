from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from fastapi import HTTPException, status

from ..dependencies import get_current_user
from ..schemas import MessageCreate, ProposalCreate, RequestSummary
from ..services import files as file_service
from ..services import requests as requests_service

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("", response_model=RequestSummary)
async def create_request(
  title: str = Form(...),
  description: str = Form(...),
  category: str = Form(...),
  budget: str = Form(...),
  targetDate: str = Form(...),
  files: List[UploadFile] | None = File(default=None),
  current_user=Depends(get_current_user)
):
  if current_user.role != "client":
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
  payload = {"title": title, "description": description, "category": category, "budget": budget, "targetDate": targetDate}
  created = await requests_service.create_request(client_id=current_user.id, payload=payload)
  if files:
    for upload in files:
      await file_service.save_file(upload, uploader_id=current_user.id, request_id=created.id)
  detail = await requests_service.get_request_detail(created.id)
  return RequestSummary.model_validate(detail, from_attributes=True)


@router.get("", response_model=List[RequestSummary])
async def list_requests(current_user=Depends(get_current_user)):
  requests = await requests_service.list_open_requests({}) if current_user.role == "consultant" else await requests_service.list_open_requests({"client_id": current_user.id})
  return [RequestSummary.model_validate(item, from_attributes=True) for item in requests]


@router.get("/{request_id}")
async def get_request(request_id: str, current_user=Depends(get_current_user)):
  request = await requests_service.get_request_detail(request_id)
  return request


@router.post("/{request_id}/messages")
async def post_message(request_id: str, payload: MessageCreate, current_user=Depends(get_current_user)):
  message = await requests_service.create_message(request_id=request_id, author_id=current_user.id, body=payload.body)
  return message


@router.post("/{request_id}/proposals")
async def create_proposal(request_id: str, payload: ProposalCreate, current_user=Depends(get_current_user)):
  if current_user.role != "consultant":
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
  proposal = await requests_service.submit_proposal(
    request_id=request_id,
    consultant_id=current_user.id,
    scope=payload.scope,
    timeline=payload.timeline,
    cost=payload.cost
  )
  return proposal
