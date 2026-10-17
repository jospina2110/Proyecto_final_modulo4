"""Utilidades compartidas por las pruebas de API (httpx + mongomock-motor).

Contrato observado: los documentos Patient/Doctor exponen su ObjectId bajo
`_id` (alias por defecto de Beanie + FastAPI), mientras que las respuestas de
citas usan `id`. Los helpers fijan `_id` para detectar cambios de contrato.
"""

from httpx import AsyncClient

PATIENT_PAYLOAD = {
    "full_name": "Ana Mar\u00eda L\u00f3pez",
    "document_id": "CC-1001",
    "email": "ana.lopez@example.com",
    "phone": "+57 300 111 0001",
}

DOCTOR_PAYLOAD = {
    "full_name": "Dra. Carolina Mendoza",
    "specialty": "Medicina general",
    "email": "carolina.mendoza@hospital.com",
}


async def create_patient(client: AsyncClient, **overrides: object) -> dict:
    payload = {**PATIENT_PAYLOAD, **overrides}
    response = await client.post("/patients", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert "_id" in data, f"Contrato inesperado en POST /patients: {data}"
    return data


async def create_doctor(client: AsyncClient, **overrides: object) -> dict:
    payload = {**DOCTOR_PAYLOAD, **overrides}
    response = await client.post("/doctors", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert "_id" in data, f"Contrato inesperado en POST /doctors: {data}"
    return data


def appointment_payload(
    patient_id: str,
    doctor_id: str,
    scheduled_at: str = "2026-11-05T09:00:00",
    *,
    duration_minutes: int = 30,
    reason: str = "Consulta general",
) -> dict:
    return {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "scheduled_at": scheduled_at,
        "duration_minutes": duration_minutes,
        "reason": reason,
    }


async def create_appointment(
    client: AsyncClient,
    patient_id: str,
    doctor_id: str,
    scheduled_at: str = "2026-11-05T09:00:00",
    **overrides: object,
) -> dict:
    payload = appointment_payload(patient_id, doctor_id, scheduled_at)
    payload.update(overrides)
    response = await client.post("/appointments", json=payload)
    assert response.status_code == 201, response.text
    return response.json()