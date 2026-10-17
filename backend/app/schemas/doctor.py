from pydantic import BaseModel, EmailStr, Field


class DoctorCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    specialty: str = Field(min_length=1, max_length=80)
    email: EmailStr
