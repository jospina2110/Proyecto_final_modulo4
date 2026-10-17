from datetime import date, datetime, timedelta

from beanie import PydanticObjectId

from app.models import Appointment, AppointmentStatus, Doctor, Patient
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.doctor_repository import DoctorRepository
from app.repositories.patient_repository import PatientRepository
from app.schemas import (
    AppointmentCreate,
    AppointmentResponse,
    DoctorSummary,
    PatientSummary,
)
from app.services.doctor_service import DoctorService
from app.services.patient_service import PatientService
from app.utils.exceptions import (
    AppointmentConflictError,
    InvalidStatusTransitionError,
    ResourceNotFoundError,
)


_ALLOWED_TRANSITIONS: dict[AppointmentStatus, frozenset[AppointmentStatus]] = {
    AppointmentStatus.PENDING: frozenset({AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED}),
    AppointmentStatus.CONFIRMED: frozenset({AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED}),
    AppointmentStatus.COMPLETED: frozenset(),
    AppointmentStatus.CANCELLED: frozenset(),
}


class AppointmentService:
    @staticmethod
    async def schedule(payload: AppointmentCreate) -> AppointmentResponse:
        patient = await PatientService.get_by_id(payload.patient_id)
        doctor = await DoctorService.get_by_id(payload.doctor_id)
        ends_at = payload.scheduled_at + timedelta(minutes=payload.duration_minutes)
        await _ensure_doctor_is_available(payload.doctor_id, payload.scheduled_at, ends_at)

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            scheduled_at=payload.scheduled_at,
            ends_at=ends_at,
            duration_minutes=payload.duration_minutes,
            reason=payload.reason,
        )
        await AppointmentRepository.insert(appointment)
        return _build_response(appointment, {patient.id: patient}, {doctor.id: doctor})

    @staticmethod
    async def get_all(
        status: AppointmentStatus | None = None,
        day: date | None = None,
        patient_id: PydanticObjectId | None = None,
        doctor_id: PydanticObjectId | None = None,
    ) -> list[AppointmentResponse]:
        appointments = await AppointmentRepository.find_all(status, day, patient_id, doctor_id)
        return await _build_responses(appointments)

    @staticmethod
    async def get_by_id(appointment_id: PydanticObjectId) -> AppointmentResponse:
        appointment = await AppointmentRepository.find_by_id(appointment_id)
        if appointment is None:
            raise ResourceNotFoundError("Cita", str(appointment_id))
        return (await _build_responses([appointment]))[0]

    @staticmethod
    async def update_status(
        appointment_id: PydanticObjectId,
        status: AppointmentStatus,
    ) -> AppointmentResponse:
        appointment = await AppointmentRepository.find_by_id(appointment_id)
        if appointment is None:
            raise ResourceNotFoundError("Cita", str(appointment_id))
        if appointment.status is not status:
            _ensure_transition_is_allowed(appointment.status, status)
            appointment.status = status
            await AppointmentRepository.save(appointment)
        return (await _build_responses([appointment]))[0]

    @staticmethod
    async def cancel(appointment_id: PydanticObjectId) -> AppointmentResponse:
        return await AppointmentService.update_status(appointment_id, AppointmentStatus.CANCELLED)


def _ensure_transition_is_allowed(current: AppointmentStatus, target: AppointmentStatus) -> None:
    if target not in _ALLOWED_TRANSITIONS.get(current, frozenset()):
        raise InvalidStatusTransitionError(current.value, target.value)


async def _ensure_doctor_is_available(doctor_id: PydanticObjectId, start: datetime, end: datetime) -> None:
    conflicts = await AppointmentRepository.find_conflicts(doctor_id, start, end)
    if conflicts:
        raise AppointmentConflictError(
            f"El médico ya tiene una cita programada entre {start:%Y-%m-%d %H:%M} y {end:%H:%M}"
        )


async def _build_responses(appointments: list[Appointment]) -> list[AppointmentResponse]:
    patient_ids = list({appointment.patient_id for appointment in appointments})
    doctor_ids = list({appointment.doctor_id for appointment in appointments})
    patients = await PatientRepository.find_by_ids(patient_ids)
    doctors = await DoctorRepository.find_by_ids(doctor_ids)
    patients_by_id = {patient.id: patient for patient in patients}
    doctors_by_id = {doctor.id: doctor for doctor in doctors}
    return [_build_response(appointment, patients_by_id, doctors_by_id) for appointment in appointments]


def _build_response(
    appointment: Appointment,
    patients_by_id: dict[PydanticObjectId, Patient],
    doctors_by_id: dict[PydanticObjectId, Doctor],
) -> AppointmentResponse:
    patient = patients_by_id[appointment.patient_id]
    doctor = doctors_by_id[appointment.doctor_id]
    return AppointmentResponse(
        id=appointment.id,
        patient=PatientSummary(id=patient.id, full_name=patient.full_name),
        doctor=DoctorSummary(id=doctor.id, full_name=doctor.full_name, specialty=doctor.specialty),
        scheduled_at=appointment.scheduled_at,
        duration_minutes=appointment.duration_minutes,
        reason=appointment.reason,
        status=appointment.status,
    )