from beanie import PydanticObjectId
from beanie.operators import In

from app.models import Doctor


class DoctorRepository:
    @staticmethod
    async def insert(doctor: Doctor) -> Doctor:
        return await doctor.insert()

    @staticmethod
    async def find_all() -> list[Doctor]:
        return await Doctor.find_all().to_list()

    @staticmethod
    async def find_by_id(doctor_id: PydanticObjectId) -> Doctor | None:
        return await Doctor.get(doctor_id)

    @staticmethod
    async def find_by_ids(doctor_ids: list[PydanticObjectId]) -> list[Doctor]:
        if not doctor_ids:
            return []
        return await Doctor.find(In(Doctor.id, doctor_ids)).to_list()
