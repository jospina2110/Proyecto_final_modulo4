from pydantic import BaseModel, EmailStr, Field


class PatientCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    document_id: str = Field(min_length=1, max_length=30)
    email: EmailStr
    phone: str = Field(min_length=1, max_length=30)
