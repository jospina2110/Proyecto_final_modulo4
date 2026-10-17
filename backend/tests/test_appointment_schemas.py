import pytest
from pydantic import ValidationError

from app.models import AppointmentStatus
from app.schemas import AppointmentCreate, AppointmentStatusUpdate

VALID_PAYLOAD = {
    "patient_id": "6a1f1a1a1a1a1a1a1a1a1a1a",
    "doctor_id": "6a1f1a1a1a1a1a1a1a1a1a1b",
    "scheduled_at": "2026-11-05T09:00:00",
    "duration_minutes": 30,
    "reason": "Consulta general",
}


def test_appointment_requires_reason() -> None:
    with pytest.raises(ValidationError):
        AppointmentCreate(**{**VALID_PAYLOAD, "reason": ""})


def test_appointment_rejects_invalid_duration() -> None:
    with pytest.raises(ValidationError):
        AppointmentCreate(**{**VALID_PAYLOAD, "duration_minutes": 0})


def test_appointment_requires_scheduled_at() -> None:
    payload = {key: value for key, value in VALID_PAYLOAD.items() if key != "scheduled_at"}
    with pytest.raises(ValidationError):
        AppointmentCreate(**payload)


def test_status_update_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError):
        AppointmentStatusUpdate(status="estado-invalido")


def test_status_update_accepts_valid_status() -> None:
    update = AppointmentStatusUpdate(status="confirmada")

    assert update.status is AppointmentStatus.CONFIRMED
