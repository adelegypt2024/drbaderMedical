from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class Token(BaseModel):
  access_token: str
  token_type: str = "bearer"


class UserBase(BaseModel):
  id: str
  email: EmailStr
  firstName: str = Field(alias="first_name")
  lastName: str = Field(alias="last_name")
  role: str
  emailVerified: bool = Field(alias="email_verified")

  model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class UserCreate(BaseModel):
  email: EmailStr
  password: str
  firstName: str
  lastName: str
  role: str


class UserLogin(BaseModel):
  email: EmailStr
  password: str


class PasswordResetRequest(BaseModel):
  email: EmailStr


class PasswordResetConfirm(BaseModel):
  token: str
  password: str


class EmailVerification(BaseModel):
  token: str


class RequestCreate(BaseModel):
  title: str
  description: str
  category: str
  budget: str
  targetDate: datetime


class RequestSummary(BaseModel):
  id: str
  title: str
  category: str
  budget: str
  targetDate: datetime = Field(alias="target_date")
  status: str

  model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class MessageCreate(BaseModel):
  body: str


class ProposalCreate(BaseModel):
  scope: str
  timeline: str
  cost: float


class ProposalOut(BaseModel):
  id: str
  requestId: str = Field(alias="request_id")
  scope: str
  timeline: str
  cost: float
  status: str

  model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class ConsultantProfileUpdate(BaseModel):
  specialties: List[str]
  hourlyRate: float
  yearsExperience: int
  bio: Optional[str] = None
  availability: Optional[str] = None
  portfolioUrl: Optional[str] = None


class ConsultantProfileOut(BaseModel):
  id: str
  specialties: List[str]
  hourlyRate: float = Field(alias="hourly_rate")
  yearsExperience: int = Field(alias="years_experience")
  bio: Optional[str]
  availability: Optional[str]
  portfolioUrl: Optional[str] = Field(alias="portfolio_url")

  model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class AppointmentCreate(BaseModel):
  title: str
  startTime: datetime
  endTime: datetime
  timezone: str
  requestId: Optional[str] = None


class AppointmentOut(BaseModel):
  id: str
  title: str
  startTime: datetime = Field(alias="start_time")
  endTime: datetime = Field(alias="end_time")
  timezone: str

  model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class DashboardResponse(BaseModel):
  requests: int
  proposals: int
  contracts: int
  invoices: int
  notifications: List[str] = []


class AdminDashboardResponse(BaseModel):
  users: int
  requests: int
  contracts: int
  revenue: float
  reports: List[dict]


class PaymentWebhook(BaseModel):
  invoiceId: str
  status: str
  providerReference: Optional[str]


class FileUploadResult(BaseModel):
  id: str
  filename: str
  url: str
