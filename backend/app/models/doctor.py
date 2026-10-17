from beanie import Document
from pydantic import EmailStr, Field


class Doctor(Document):
    full_name: str = Field(min_length=1, max_length=100)
    specialty: str = Field(min_length=1, max_length=80)
    email: EmailStr

    class Settings:
        name = "doctors"
