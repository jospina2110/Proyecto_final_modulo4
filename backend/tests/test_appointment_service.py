from datetime import datetime

import pytest

from app.models import AppointmentStatus, Doctor, Patient
from app.schemas import AppointmentCreate
from app.services.appointment_service import AppointmentService
from app.utils.exceptions import AppointmentConflictError, ResourceNotFoundError

pytestmark = pytest.mark.usefixtures("db")


async def create_patient() -> Patient:
    patient = Patient(
        full_name="Ana María López",
        document_id="CC-1001",
        email="ana.lopez@example.com",
        phone="+57 300 111 0001",
    )
    return await patient.insert()


async def create_doctor() -> Doctor:
    doctor = Doctor(
        full_name="Dra. Carolina Mendoza",
        specialty="Medicina general",
        email="carolina.mendoza@hospital.com",
    )
    return await doctor.insert()


def build_payload(patient: Patient, doctor: Doctor, start: datetime) -> AppointmentCreate:
    return AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        scheduled_at=start,
        duration_minutes=30,
        reason="Consulta general",
    )


async def test_schedules_appointment_with_pending_status() -> None:
    patient = await create_patient()
    doctor = await create_doctor()

    response = await AppointmentService.schedule(
        build_payload(patient, doctor, datetime(2026, 11, 5, 9, 0))
    )

    assert response.status is AppointmentStatus.PENDING
    assert response.patient.full_name == patient.full_name
    assert response.doctor.specialty == doctor.specialty


async def test_rejects_overlapping_appointment_for_same_doctor() -> None:
    patient = await create_patient()
    doctor = await create_doctor()
    await AppointmentService.schedule(build_payload(patient, doctor, datetime(2026, 11, 5, 9, 0)))

    with pytest.raises(AppointmentConflictError):
        await AppointmentService.schedule(
            build_payload(patient, doctor, datetime(2026, 11, 5, 9, 15))
        )


async def test_allows_back_to_back_appointment_for_same_doctor() -> None:
    patient = await create_patient()
    doctor = await create_doctor()
    await AppointmentService.schedule(build_payload(patient, doctor, datetime(2026, 11, 5, 9, 0)))

    response = await AppointmentService.schedule(
        build_payload(patient, doctor, datetime(2026, 11, 5, 9, 30))
    )

    assert response.status is AppointmentStatus.PENDING


async def test_rejects_appointment_with_unknown_patient() -> None:
    patient = await create_patient()
    doctor = await create_doctor()
    payload = build_payload(patient, doctor, datetime(2026, 11, 5, 9, 0))
    payload.patient_id = doctor.id

    with pytest.raises(ResourceNotFoundError):
        await AppointmentService.schedule(payload)


async def test_cancel_appointment_keeps_history() -> None:
    patient = await create_patient()
    doctor = await create_doctor()
    appointment = await AppointmentService.schedule(
        build_payload(patient, doctor, datetime(2026, 11, 5, 9, 0))
    )

    cancelled = await AppointmentService.cancel(appointment.id)

    assert cancelled.status is AppointmentStatus.CANCELLED
    assert await AppointmentService.get_by_id(appointment.id)


async def test_cancelled_appointment_frees_the_time_slot() -> None:
    patient = await create_patient()
    doctor = await create_doctor()
    appointment = await AppointmentService.schedule(
        build_payload(patient, doctor, datetime(2026, 11, 5, 9, 0))
    )
    await AppointmentService.cancel(appointment.id)

    response = await AppointmentService.schedule(
        build_payload(patient, doctor, datetime(2026, 11, 5, 9, 15))
    )

    assert response.status is AppointmentStatus.PENDING


async def test_filters_appointments_by_status_and_date() -> None:
    patient = await create_patient()
    doctor = await create_doctor()
    await AppointmentService.schedule(build_payload(patient, doctor, datetime(2026, 11, 5, 9, 0)))
    await AppointmentService.schedule(build_payload(patient, doctor, datetime(2026, 11, 6, 9, 0)))

    same_day = await AppointmentService.get_all(day=datetime(2026, 11, 5).date())
    pending = await AppointmentService.get_all(status=AppointmentStatus.PENDING)

    assert len(same_day) == 1
    assert len(pending) == 2
