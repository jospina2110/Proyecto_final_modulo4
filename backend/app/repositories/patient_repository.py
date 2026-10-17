from beanie import PydanticObjectId
from beanie.operators import In

from app.models import Patient


class PatientRepository:
    @staticmethod
    async def insert(patient: Patient) -> Patient:
        return await patient.insert()

    @staticmethod
    async def find_all() -> list[Patient]:
        return await Patient.find_all().to_list()

    @staticmethod
    async def find_by_id(patient_id: PydanticObjectId) -> Patient | None:
        return await Patient.get(patient_id)

    @staticmethod
    async def find_by_email(email: str) -> Patient | None:
        return await Patient.find_one(Patient.email == email)

    @staticmethod
    async def find_by_document_id(document_id: str) -> Patient | None:
        return await Patient.find_one(Patient.document_id == document_id)

    @staticmethod
    async def find_by_ids(patient_ids: list[PydanticObjectId]) -> list[Patient]:
        if not patient_ids:
            return []
        return await Patient.find(In(Patient.id, patient_ids)).to_list()