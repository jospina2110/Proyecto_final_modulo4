import asyncio
from datetime import datetime, timedelta

from beanie import PydanticObjectId

from app.config.database import init_database
from app.models import Appointment, AppointmentStatus, Doctor, Patient

BASE_DATE = datetime(2026, 11, 2, 8, 0)
APPOINTMENT_DURATION_MINUTES = 30

PATIENTS = [
    {"full_name": "Ana María López", "document_id": "CC-1001", "email": "ana.lopez@example.com", "phone": "+57 300 111 0001"},
    {"full_name": "Carlos Andrés Gómez", "document_id": "CC-1002", "email": "carlos.gomez@example.com", "phone": "+57 300 111 0002"},
    {"full_name": "Laura Sofía Martínez", "document_id": "CC-1003", "email": "laura.martinez@example.com", "phone": "+57 300 111 0003"},
    {"full_name": "Juan Pablo Rodríguez", "document_id": "CC-1004", "email": "juan.rodriguez@example.com", "phone": "+57 300 111 0004"},
    {"full_name": "Valentina Torres", "document_id": "CC-1005", "email": "valentina.torres@example.com", "phone": "+57 300 111 0005"},
    {"full_name": "Santiago Ramírez", "document_id": "CC-1006", "email": "santiago.ramirez@example.com", "phone": "+57 300 111 0006"},
    {"full_name": "Isabella Castro", "document_id": "CC-1007", "email": "isabella.castro@example.com", "phone": "+57 300 111 0007"},
    {"full_name": "Sebastián Vargas", "document_id": "CC-1008", "email": "sebastian.vargas@example.com", "phone": "+57 300 111 0008"},
    {"full_name": "Camila Herrera", "document_id": "CC-1009", "email": "camila.herrera@example.com", "phone": "+57 300 111 0009"},
    {"full_name": "Mateo Jiménez", "document_id": "CC-1010", "email": "mateo.jimenez@example.com", "phone": "+57 300 111 0010"},
    {"full_name": "Daniela Moreno", "document_id": "CC-1011", "email": "daniela.moreno@example.com", "phone": "+57 300 111 0011"},
    {"full_name": "Alejandro Muñoz", "document_id": "CC-1012", "email": "alejandro.munoz@example.com", "phone": "+57 300 111 0012"},
    {"full_name": "Gabriela Rojas", "document_id": "CC-1013", "email": "gabriela.rojas@example.com", "phone": "+57 300 111 0013"},
    {"full_name": "Nicolás Ortiz", "document_id": "CC-1014", "email": "nicolas.ortiz@example.com", "phone": "+57 300 111 0014"},
    {"full_name": "Mariana Silva", "document_id": "CC-1015", "email": "mariana.silva@example.com", "phone": "+57 300 111 0015"},
    {"full_name": "Andrés Felipe Peña", "document_id": "CC-1016", "email": "andres.pena@example.com", "phone": "+57 300 111 0016"},
    {"full_name": "Sara Lucía Guzmán", "document_id": "CC-1017", "email": "sara.guzman@example.com", "phone": "+57 300 111 0017"},
    {"full_name": "Diego Fernando Salazar", "document_id": "CC-1018", "email": "diego.salazar@example.com", "phone": "+57 300 111 0018"},
    {"full_name": "Paula Andrea Ríos", "document_id": "CC-1019", "email": "paula.rios@example.com", "phone": "+57 300 111 0019"},
    {"full_name": "Felipe Aguilar", "document_id": "CC-1020", "email": "felipe.aguilar@example.com", "phone": "+57 300 111 0020"},
]

DOCTORS = [
    {"full_name": "Dra. Carolina Mendoza", "specialty": "Medicina general", "email": "carolina.mendoza@hospital.com"},
    {"full_name": "Dr. Ricardo Salcedo", "specialty": "Pediatría", "email": "ricardo.salcedo@hospital.com"},
    {"full_name": "Dra. Elena Navarro", "specialty": "Cardiología", "email": "elena.navarro@hospital.com"},
    {"full_name": "Dr. Óscar Beltrán", "specialty": "Dermatología", "email": "oscar.beltran@hospital.com"},
]

REASONS = [
    "Consulta general",
    "Control de seguimiento",
    "Revisión de exámenes",
    "Dolor persistente",
    "Chequeo preventivo",
]

STATUS_CYCLE = [
    AppointmentStatus.PENDING,
    AppointmentStatus.PENDING,
    AppointmentStatus.CONFIRMED,
    AppointmentStatus.PENDING,
    AppointmentStatus.COMPLETED,
    AppointmentStatus.PENDING,
    AppointmentStatus.CONFIRMED,
    AppointmentStatus.CANCELLED,
]


def build_appointments(patients: list[Patient], doctors: list[Doctor]) -> list[Appointment]:
    appointments = []
    for index in range(len(patients)):
        doctor = doctors[index % len(doctors)]
        scheduled_at = BASE_DATE + timedelta(hours=index // len(doctors))
        appointments.append(
            Appointment(
                patient_id=patients[index].id,
                doctor_id=doctor.id,
                scheduled_at=scheduled_at,
                ends_at=scheduled_at + timedelta(minutes=APPOINTMENT_DURATION_MINUTES),
                duration_minutes=APPOINTMENT_DURATION_MINUTES,
                reason=REASONS[index % len(REASONS)],
                status=STATUS_CYCLE[index % len(STATUS_CYCLE)],
            )
        )
    return appointments


async def seed() -> None:
    client = await init_database()

    await Appointment.delete_all()
    await Patient.delete_all()
    await Doctor.delete_all()

    # Beanie 1.30 no asigna el id en memoria tras insert_many: se generan los
    # ObjectId en cliente para que las referencias de las citas sean validas.
    patients = [Patient(id=PydanticObjectId(), **data) for data in PATIENTS]
    doctors = [Doctor(id=PydanticObjectId(), **data) for data in DOCTORS]
    await Patient.insert_many(patients)
    await Doctor.insert_many(doctors)
    appointments = build_appointments(patients, doctors)
    await Appointment.insert_many(appointments)

    print(f"Seed completado: {len(patients)} pacientes, {len(doctors)} médicos, {len(appointments)} citas")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
