from beanie import PydanticObjectId

from app.models import Patient
from app.repositories.patient_repository import PatientRepository
from app.schemas import PatientCreate
from app.utils.exceptions import DuplicatePatientError, ResourceNotFoundError


class PatientService:
    @staticmethod
    async def create(payload: PatientCreate) -> Patient:
        if await PatientRepository.find_by_email(payload.email) is not None:
            raise DuplicatePatientError("Ya existe un paciente registrado con ese correo electrónico")
        if await PatientRepository.find_by_document_id(payload.document_id) is not None:
            raise DuplicatePatientError("Ya existe un paciente registrado con ese documento de identidad")
        return await PatientRepository.insert(Patient(**payload.model_dump()))

    @staticmethod
    async def get_all() -> list[Patient]:
        return await PatientRepository.find_all()

    @staticmethod
    async def get_by_id(patient_id: PydanticObjectId) -> Patient:
        patient = await PatientRepository.find_by_id(patient_id)
        if patient is None:
            raise ResourceNotFoundError("Paciente", str(patient_id))
        return patient