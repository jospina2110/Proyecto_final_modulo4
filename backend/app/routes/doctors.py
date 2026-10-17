from fastapi import APIRouter, status

from app.models import Doctor
from app.schemas import DoctorCreate
from app.services.doctor_service import DoctorService

router = APIRouter(prefix="/doctors", tags=["Médicos"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Doctor)
async def register_doctor(payload: DoctorCreate) -> Doctor:
    return await DoctorService.create(payload)


@router.get("", response_model=list[Doctor])
async def list_doctors() -> list[Doctor]:
    return await DoctorService.get_all()
