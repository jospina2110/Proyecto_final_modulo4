from fastapi import APIRouter, status

from app.models import Patient
from app.schemas import PatientCreate
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["Pacientes"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Patient)
async def register_patient(payload: PatientCreate) -> Patient:
    return await PatientService.create(payload)


@router.get("", response_model=list[Patient])
async def list_patients() -> list[Patient]:
    return await PatientService.get_all()
