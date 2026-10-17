from beanie import PydanticObjectId

from app.models import Doctor
from app.repositories.doctor_repository import DoctorRepository
from app.schemas import DoctorCreate
from app.utils.exceptions import ResourceNotFoundError


class DoctorService:
    @staticmethod
    async def create(payload: DoctorCreate) -> Doctor:
        return await DoctorRepository.insert(Doctor(**payload.model_dump()))

    @staticmethod
    async def get_all() -> list[Doctor]:
        return await DoctorRepository.find_all()

    @staticmethod
    async def get_by_id(doctor_id: PydanticObjectId) -> Doctor:
        doctor = await DoctorRepository.find_by_id(doctor_id)
        if doctor is None:
            raise ResourceNotFoundError("Médico", str(doctor_id))
        return doctor
