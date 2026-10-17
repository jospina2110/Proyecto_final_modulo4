from datetime import date, datetime, time, timedelta

from beanie import PydanticObjectId

from app.models import Appointment, AppointmentStatus


class AppointmentRepository:
    @staticmethod
    async def insert(appointment: Appointment) -> Appointment:
        return await appointment.insert()

    @staticmethod
    async def save(appointment: Appointment) -> Appointment:
        await appointment.save()
        return appointment

    @staticmethod
    async def find_by_id(appointment_id: PydanticObjectId) -> Appointment | None:
        return await Appointment.get(appointment_id)

    @staticmethod
    async def find_all(
        status: AppointmentStatus | None = None,
        day: date | None = None,
        patient_id: PydanticObjectId | None = None,
        doctor_id: PydanticObjectId | None = None,
    ) -> list[Appointment]:
        filters = _build_filters(status, day, patient_id, doctor_id)
        return await Appointment.find(*filters).to_list()

    @staticmethod
    async def find_conflicts(
        doctor_id: PydanticObjectId,
        start: datetime,
        end: datetime,
    ) -> list[Appointment]:
        return await Appointment.find(
            Appointment.doctor_id == doctor_id,
            Appointment.status != AppointmentStatus.CANCELLED,
            Appointment.scheduled_at < end,
            Appointment.ends_at > start,
        ).to_list()


def _build_filters(
    status: AppointmentStatus | None,
    day: date | None,
    patient_id: PydanticObjectId | None,
    doctor_id: PydanticObjectId | None,
) -> list:
    filters = []
    if status is not None:
        filters.append(Appointment.status == status)
    if day is not None:
        day_start = datetime.combine(day, time.min)
        filters.append(Appointment.scheduled_at >= day_start)
        filters.append(Appointment.scheduled_at < day_start + timedelta(days=1))
    if patient_id is not None:
        filters.append(Appointment.patient_id == patient_id)
    if doctor_id is not None:
        filters.append(Appointment.doctor_id == doctor_id)
    return filters
