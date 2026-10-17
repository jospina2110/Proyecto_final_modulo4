from datetime import datetime
from enum import Enum

from beanie import Document, PydanticObjectId
from pymongo import ASCENDING, IndexModel
from pydantic import Field


class AppointmentStatus(str, Enum):
    PENDING = "pendiente"
    CONFIRMED = "confirmada"
    COMPLETED = "completada"
    CANCELLED = "cancelada"


class Appointment(Document):
    patient_id: PydanticObjectId
    doctor_id: PydanticObjectId
    scheduled_at: datetime
    ends_at: datetime
    duration_minutes: int = Field(default=30, ge=5, le=240)
    reason: str = Field(min_length=1, max_length=200)
    status: AppointmentStatus = AppointmentStatus.PENDING

    class Settings:
        name = "appointments"
        # Filtros reales de GET /appointments: status, date, patient_id, doctor_id.
        indexes = [
            # Compuesto: cubre doctor_id + rango de scheduled_at.
            IndexModel([("doctor_id", ASCENDING), ("scheduled_at", ASCENDING)]),
            # Filtros de igualdad/rango: no requieren unicidad.
            IndexModel([("status", ASCENDING)]),
            IndexModel([("patient_id", ASCENDING)]),
            IndexModel([("scheduled_at", ASCENDING)]),
        ]
