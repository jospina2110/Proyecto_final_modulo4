from beanie import Document
from pymongo import ASCENDING, IndexModel
from pydantic import EmailStr, Field


class Patient(Document):
    full_name: str = Field(min_length=1, max_length=100)
    document_id: str = Field(min_length=1, max_length=30)
    email: EmailStr
    phone: str = Field(min_length=1, max_length=30)

    class Settings:
        name = "patients"
        # Unicidad de negocio: email y document_id identifican al paciente.
        indexes = [
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("document_id", ASCENDING)], unique=True),
        ]
