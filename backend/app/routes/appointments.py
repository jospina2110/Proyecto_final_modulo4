from datetime import date

from beanie import PydanticObjectId
from fastapi import APIRouter, Query, status

from app.models import AppointmentStatus
from app.schemas import AppointmentCreate, AppointmentResponse, AppointmentStatusUpdate
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["Citas"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AppointmentResponse)
async def schedule_appointment(payload: AppointmentCreate) -> AppointmentResponse:
    return await AppointmentService.schedule(payload)


@router.get("", response_model=list[AppointmentResponse])
async def list_appointments(
    status_filter: AppointmentStatus | None = Query(default=None, alias="status"),
    day: date | None = Query(default=None, alias="date"),
    patient_id: PydanticObjectId | None = None,
    doctor_id: PydanticObjectId | None = None,
) -> list[AppointmentResponse]:
    return await AppointmentService.get_all(status_filter, day, patient_id, doctor_id)


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: PydanticObjectId) -> AppointmentResponse:
    return await AppointmentService.get_by_id(appointment_id)


@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
async def update_appointment_status(
    appointment_id: PydanticObjectId,
    payload: AppointmentStatusUpdate,
) -> AppointmentResponse:
    return await AppointmentService.update_status(appointment_id, payload.status)


@router.delete("/{appointment_id}", response_model=AppointmentResponse)
async def cancel_appointment(appointment_id: PydanticObjectId) -> AppointmentResponse:
    return await AppointmentService.cancel(appointment_id)
