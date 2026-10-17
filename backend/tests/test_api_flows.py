"""Pruebas E2E del contrato HTTP de citas: ciclo de vida, filtros e idempotencia."""

import pytest
from httpx import AsyncClient

from helpers import (
    appointment_payload,
    create_appointment,
    create_doctor,
    create_patient,
)

# ObjectId valido (formato hex de 24) que nunca se inserta en la base.
NONEXISTENT_ID = "6a1f1a1a1a1a1a1a1a1a1a1a"

# Pasos para dejar una cita en cada estado antes de probar una transicion.
_SETUP_STEPS = {
    "pendiente": (),
    "confirmada": (("patch", "confirmada"),),
    "completada": (("patch", "confirmada"), ("patch", "completada")),
    "cancelada": (("delete", None),),
}


async def _advance(
    client: AsyncClient, appointment_id: str, method: str, target: str | None
) -> None:
    if method == "delete":
        response = await client.delete(f"/appointments/{appointment_id}")
    else:
        response = await client.patch(
            f"/appointments/{appointment_id}/status", json={"status": target}
        )
    assert response.status_code == 200, response.text


async def test_full_flow_confirm_complete_then_cancel_is_rejected(client: AsyncClient) -> None:
    patient = await create_patient(client)
    doctor = await create_doctor(client)

    created = await create_appointment(client, patient["_id"], doctor["_id"], "2026-11-05T09:00:00")
    appointment_id = created["id"]
    assert created["status"] == "pendiente"
    assert created["patient"] == {"id": patient["_id"], "full_name": patient["full_name"]}
    assert created["doctor"]["specialty"] == doctor["specialty"]
    assert created["duration_minutes"] == 30
    assert created["scheduled_at"].startswith("2026-11-05T09:00:00")

    listed = await client.get(
        "/appointments",
        params={
            "status": "pendiente",
            "date": "2026-11-05",
            "patient_id": patient["_id"],
            "doctor_id": doctor["_id"],
        },
    )
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [appointment_id]

    confirmed = await client.patch(
        f"/appointments/{appointment_id}/status", json={"status": "confirmada"}
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "confirmada"

    completed = await client.patch(
        f"/appointments/{appointment_id}/status", json={"status": "completada"}
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completada"

    rejected = await client.delete(f"/appointments/{appointment_id}")
    assert rejected.status_code == 409
    assert "detail" in rejected.json()

    stored = await client.get(f"/appointments/{appointment_id}")
    assert stored.status_code == 200
    assert stored.json()["status"] == "completada"


async def test_cancellation_is_logical_keeps_history_and_frees_slot(client: AsyncClient) -> None:
    patient = await create_patient(client)
    doctor = await create_doctor(client)
    created = await create_appointment(client, patient["_id"], doctor["_id"], "2026-11-05T09:00:00")
    appointment_id = created["id"]

    cancelled = await client.delete(f"/appointments/{appointment_id}")
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelada"

    stored = await client.get(f"/appointments/{appointment_id}")
    assert stored.status_code == 200
    assert stored.json()["id"] == appointment_id
    assert stored.json()["status"] == "cancelada"

    listed = await client.get("/appointments", params={"status": "cancelada"})
    assert [item["id"] for item in listed.json()] == [appointment_id]

    rebooked = await client.post(
        "/appointments",
        json=appointment_payload(patient["_id"], doctor["_id"], "2026-11-05T09:15:00"),
    )
    assert rebooked.status_code == 201
    assert rebooked.json()["status"] == "pendiente"


async def test_confirmed_appointment_can_be_cancelled(client: AsyncClient) -> None:
    patient = await create_patient(client)
    doctor = await create_doctor(client)
    appointment_id = (await create_appointment(client, patient["_id"], doctor["_id"]))["id"]

    confirmed = await client.patch(
        f"/appointments/{appointment_id}/status", json={"status": "confirmada"}
    )
    assert confirmed.status_code == 200

    cancelled = await client.delete(f"/appointments/{appointment_id}")
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelada"


async def test_filters_by_status_date_patient_and_doctor(client: AsyncClient) -> None:
    assert (await client.get("/appointments")).json() == []

    patient_a = await create_patient(client)
    patient_b = await create_patient(
        client,
        full_name="Bruno Diaz",
        document_id="CC-2002",
        email="bruno.diaz@example.com",
        phone="+57 300 222 0002",
    )
    doctor_a = await create_doctor(client)
    doctor_b = await create_doctor(
        client,
        full_name="Dr. Jorge Rivas",
        specialty="Cardiologia",
        email="jorge.rivas@hospital.com",
    )

    first = await create_appointment(client, patient_a["_id"], doctor_a["_id"], "2026-11-05T09:00:00")
    second = await create_appointment(client, patient_b["_id"], doctor_b["_id"], "2026-11-06T10:00:00")
    await client.patch(f"/appointments/{second['id']}/status", json={"status": "confirmada"})

    async def ids_for(params: dict) -> list[str]:
        response = await client.get("/appointments", params=params)
        assert response.status_code == 200, response.text
        return [item["id"] for item in response.json()]

    assert await ids_for({"status": "pendiente"}) == [first["id"]]
    assert await ids_for({"status": "confirmada"}) == [second["id"]]
    assert await ids_for({"date": "2026-11-05"}) == [first["id"]]
    assert await ids_for({"date": "2026-11-06"}) == [second["id"]]
    assert await ids_for({"patient_id": patient_a["_id"]}) == [first["id"]]
    assert await ids_for({"doctor_id": doctor_b["_id"]}) == [second["id"]]
    assert await ids_for(
        {
            "status": "pendiente",
            "date": "2026-11-05",
            "patient_id": patient_a["_id"],
            "doctor_id": doctor_a["_id"],
        }
    ) == [first["id"]]
    assert await ids_for({"status": "completada"}) == []


async def test_large_list_filters_return_only_matching_appointments(client: AsyncClient) -> None:
    patient = await create_patient(client)
    doctor_a = await create_doctor(client)
    doctor_b = await create_doctor(
        client,
        full_name="Dr. Jorge Rivas",
        specialty="Cardiologia",
        email="jorge.rivas@hospital.com",
    )
    days = [f"2026-11-0{day}" for day in range(2, 8)]
    for day in days:
        for doctor in (doctor_a, doctor_b):
            await create_appointment(client, patient["_id"], doctor["_id"], f"{day}T09:00:00")
            await create_appointment(client, patient["_id"], doctor["_id"], f"{day}T10:00:00")

    target_day = days[0]
    day_appointments = (await client.get("/appointments", params={"date": target_day})).json()
    assert len(day_appointments) == 4
    to_confirm = [item for item in day_appointments if item["doctor"]["id"] == doctor_b["_id"]]
    assert len(to_confirm) == 2
    for item in to_confirm:
        response = await client.patch(
            f"/appointments/{item['id']}/status", json={"status": "confirmada"}
        )
        assert response.status_code == 200

    everything = await client.get("/appointments")
    assert everything.status_code == 200
    assert len(everything.json()) == len(days) * 4

    by_doctor = await client.get("/appointments", params={"doctor_id": doctor_a["_id"]})
    assert len(by_doctor.json()) == len(days) * 2

    by_date = await client.get("/appointments", params={"date": days[-1]})
    assert len(by_date.json()) == 4

    by_status = await client.get("/appointments", params={"status": "confirmada"})
    assert len(by_status.json()) == 2

    combined = await client.get(
        "/appointments",
        params={"doctor_id": doctor_b["_id"], "date": target_day, "status": "confirmada"},
    )
    assert len(combined.json()) == 2


async def test_patch_same_status_twice_is_idempotent(client: AsyncClient) -> None:
    patient = await create_patient(client)
    doctor = await create_doctor(client)
    appointment_id = (await create_appointment(client, patient["_id"], doctor["_id"]))["id"]

    for _ in range(2):
        response = await client.patch(
            f"/appointments/{appointment_id}/status", json={"status": "confirmada"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "confirmada"

    for _ in range(2):
        response = await client.patch(
            f"/appointments/{appointment_id}/status", json={"status": "completada"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "completada"


async def test_delete_twice_is_idempotent_and_keeps_record(client: AsyncClient) -> None:
    patient = await create_patient(client)
    doctor = await create_doctor(client)
    appointment_id = (await create_appointment(client, patient["_id"], doctor["_id"]))["id"]

    for _ in range(2):
        response = await client.delete(f"/appointments/{appointment_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "cancelada"

    stored = await client.get(f"/appointments/{appointment_id}")
    assert stored.status_code == 200
    assert stored.json()["status"] == "cancelada"


@pytest.mark.parametrize(
    ("setup_status", "target"),
    [
        ("pendiente", "completada"),
        ("confirmada", "pendiente"),
        ("completada", "cancelada"),
        ("cancelada", "confirmada"),
        ("cancelada", "completada"),
    ],
)
async def test_rejects_invalid_status_transitions(
    client: AsyncClient, setup_status: str, target: str
) -> None:
    patient = await create_patient(client)
    doctor = await create_doctor(client)
    appointment_id = (await create_appointment(client, patient["_id"], doctor["_id"]))["id"]
    for method, step_target in _SETUP_STEPS[setup_status]:
        await _advance(client, appointment_id, method, step_target)

    response = await client.patch(
        f"/appointments/{appointment_id}/status", json={"status": target}
    )

    assert response.status_code == 409
    assert setup_status in response.json()["detail"]
    assert target in response.json()["detail"]

    stored = await client.get(f"/appointments/{appointment_id}")
    assert stored.json()["status"] == setup_status


async def test_rejects_overlapping_appointment_for_same_doctor(client: AsyncClient) -> None:
    patient = await create_patient(client)
    doctor = await create_doctor(client)
    await create_appointment(client, patient["_id"], doctor["_id"], "2026-11-05T09:00:00")

    overlap = await client.post(
        "/appointments",
        json=appointment_payload(patient["_id"], doctor["_id"], "2026-11-05T09:15:00"),
    )
    assert overlap.status_code == 409
    assert "detail" in overlap.json()
    assert "Traceback" not in overlap.text

    before = await client.post(
        "/appointments",
        json=appointment_payload(patient["_id"], doctor["_id"], "2026-11-05T08:45:00"),
    )
    assert before.status_code == 409


async def test_allows_adjacent_slot_and_another_doctor_at_same_time(client: AsyncClient) -> None:
    patient = await create_patient(client)
    doctor = await create_doctor(client)
    other_doctor = await create_doctor(
        client,
        full_name="Dr. Jorge Rivas",
        specialty="Cardiologia",
        email="jorge.rivas@hospital.com",
    )
    await create_appointment(client, patient["_id"], doctor["_id"], "2026-11-05T09:00:00")

    adjacent = await client.post(
        "/appointments",
        json=appointment_payload(patient["_id"], doctor["_id"], "2026-11-05T09:30:00"),
    )
    assert adjacent.status_code == 201

    other = await client.post(
        "/appointments",
        json=appointment_payload(patient["_id"], other_doctor["_id"], "2026-11-05T09:00:00"),
    )
    assert other.status_code == 201