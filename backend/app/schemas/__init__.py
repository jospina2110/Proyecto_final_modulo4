from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentStatusUpdate,
    DoctorSummary,
    PatientSummary,
)
from app.schemas.doctor import DoctorCreate
from app.schemas.patient import PatientCreate

__all__ = [
    "AppointmentCreate",
    "AppointmentResponse",
    "AppointmentStatusUpdate",
    "DoctorCreate",
    "DoctorSummary",
    "PatientCreate",
    "PatientSummary",
]
