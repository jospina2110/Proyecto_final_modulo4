from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from app.models import AppointmentStatus


class AppointmentCreate(BaseModel):
    patient_id: PydanticObjectId
    doctor_id: PydanticObjectId
    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=5, le=240)
    reason: str = Field(min_length=1, max_length=200)


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class PatientSummary(BaseModel):
    id: PydanticObjectId
    full_name: str


class DoctorSummary(BaseModel):
    id: PydanticObjectId
    full_name: str
    specialty: str


class AppointmentResponse(BaseModel):
    id: PydanticObjectId
    patient: PatientSummary
    doctor: DoctorSummary
    scheduled_at: datetime
    duration_minutes: int
    reason: str
    status: AppointmentStatus
