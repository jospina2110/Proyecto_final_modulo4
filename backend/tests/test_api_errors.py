"""Pruebas del contrato de errores HTTP: 404, 409 y 422."""

import pytest
from httpx import AsyncClient

from helpers import appointment_payload, create_appointment, create_doctor, create_patient

# ObjectIds validos (24 hex) que nunca se insertan en la base.
NONEXISTENT_ID = "6a1f1a1a1a1a1a1a1a1a1a1a"
OTHER_ID = "6a1f1a1a1a1a1a1a1a1a1a1b"

VALID_APPOINTMENT_PAYLOAD = {
    "patient_id": NONEXISTENT_ID,
    "doctor_id": OTHER_ID,
    "scheduled_at": "2026-11-05T09:00:00",
    "duration_minutes": 30,
    "reason": "Consulta general",
}

VALID_PATIENT_PAYLOAD = {
    "full_name": "Paciente Valido",
    "document_id": "CC-7777",
    "email": "paciente.valido@example.com",
    "phone": "+57 300 777 0007",
}

VALID_DOCTOR_PAYLOAD = {
    "full_name": "Doctor Valido",
    "specialty": "Pediatria",
    "email": "doctor.valido@example.com",
}


async def test_get_unknown_appointment_returns_404(client: AsyncClient) -> None:
    response = await client.get(f"/appointments/{NONEXISTENT_ID}")

    assert response.status_code == 404
    assert set(response.json()) == {"detail"}
    assert "Cita" in response.json()["detail"]
    assert NONEXISTENT_ID in response.json()["detail"]
    assert "Traceback" not in response.text


@pytest.mark.parametrize("method", ["patch", "delete"])
async def test_modify_unknown_appointment_returns_404(client: AsyncClient, method: str) -> None:
    if method == "patch":
        response = await client.patch(
            f"/appointments/{NONEXISTENT_ID}/status", json={"status": "confirmada"}
        )
    else:
        response = await client.delete(f"/appointments/{NONEXISTENT_ID}")

    assert response.status_code == 404
    assert set(response.json()) == {"detail"}
    assert "Traceback" not in response.text


async def test_schedule_with_unknown_patient_returns_404(client: AsyncClient) -> None:
    doctor = await create_doctor(client)

    response = await client.post(
        "/appointments", json=appointment_payload(NONEXISTENT_ID, doctor["_id"])
    )

    assert response.status_code == 404
    assert "Paciente" in response.json()["detail"]
    assert "Traceback" not in response.text


async def test_schedule_with_unknown_doctor_returns_404(client: AsyncClient) -> None:
    patient = await create_patient(client)

    response = await client.post(
        "/appointments", json=appointment_payload(patient["_id"], NONEXISTENT_ID)
    )

    assert response.status_code == 404
    assert "M\u00e9dico" in response.json()["detail"]
    assert "Traceback" not in response.text


async def test_duplicate_patient_email_returns_409(client: AsyncClient) -> None:
    await create_patient(client)

    response = await client.post(
        "/patients",
        json={
            "full_name": "Otra Persona",
            "document_id": "CC-9999",
            "email": "ana.lopez@example.com",
            "phone": "+57 300 999 0009",
        },
    )

    assert response.status_code == 409
    assert set(response.json()) == {"detail"}
    assert "correo" in response.json()["detail"]
    assert "Traceback" not in response.text


async def test_duplicate_patient_document_returns_409(client: AsyncClient) -> None:
    await create_patient(client)

    response = await client.post(
        "/patients",
        json={
            "full_name": "Otra Persona",
            "document_id": "CC-1001",
            "email": "otra.persona@example.com",
            "phone": "+57 300 999 0009",
        },
    )

    assert response.status_code == 409
    assert set(response.json()) == {"detail"}
    assert "documento" in response.json()["detail"]
    assert "Traceback" not in response.text


@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param({"duration_minutes": 0}, id="duracion-cero"),
        pytest.param({"duration_minutes": 4}, id="duracion-bajo-minimo"),
        pytest.param({"duration_minutes": 241}, id="duracion-sobre-maximo"),
        pytest.param({"duration_minutes": "treinta"}, id="duracion-no-numerica"),
        pytest.param({"scheduled_at": None}, id="fecha-nula"),
        pytest.param({"scheduled_at": "no-es-una-fecha"}, id="fecha-invalida"),
        pytest.param({"reason": ""}, id="motivo-vacio"),
        pytest.param({"reason": None}, id="motivo-nulo"),
        pytest.param({"patient_id": "abc"}, id="paciente-malformado"),
        pytest.param({"doctor_id": "abc"}, id="medico-malformado"),
    ],
)
async def test_rejects_invalid_appointment_payload(
    client: AsyncClient, overrides: dict
) -> None:
    payload = {**VALID_APPOINTMENT_PAYLOAD, **overrides}

    response = await client.post("/appointments", json=payload)

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
    assert "Traceback" not in response.text


async def test_rejects_empty_appointment_body(client: AsyncClient) -> None:
    response = await client.post("/appointments", json={})

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param({"full_name": ""}, id="nombre-vacio"),
        pytest.param({"full_name": None}, id="nombre-nulo"),
        pytest.param({"document_id": ""}, id="documento-vacio"),
        pytest.param({"email": ""}, id="correo-vacio"),
        pytest.param({"email": "no-es-un-correo"}, id="correo-invalido"),
        pytest.param({"phone": ""}, id="telefono-vacio"),
    ],
)
async def test_rejects_invalid_patient_payload(client: AsyncClient, overrides: dict) -> None:
    response = await client.post("/patients", json={**VALID_PATIENT_PAYLOAD, **overrides})

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param({"full_name": ""}, id="nombre-vacio"),
        pytest.param({"specialty": ""}, id="especialidad-vacia"),
        pytest.param({"email": "sin-arroba"}, id="correo-invalido"),
    ],
)
async def test_rejects_invalid_doctor_payload(client: AsyncClient, overrides: dict) -> None:
    response = await client.post("/doctors", json={**VALID_DOCTOR_PAYLOAD, **overrides})

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


async def test_rejects_empty_patient_and_doctor_bodies(client: AsyncClient) -> None:
    assert (await client.post("/patients", json={})).status_code == 422
    assert (await client.post("/doctors", json={})).status_code == 422


async def test_rejects_unknown_status_on_patch_and_keeps_state(client: AsyncClient) -> None:
    patient = await create_patient(client)
    doctor = await create_doctor(client)
    appointment_id = (await create_appointment(client, patient["_id"], doctor["_id"]))["id"]

    response = await client.patch(
        f"/appointments/{appointment_id}/status", json={"status": "en-curso"}
    )

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)

    stored = await client.get(f"/appointments/{appointment_id}")
    assert stored.json()["status"] == "pendiente"


@pytest.mark.parametrize(
    "bad_id",
    ["abc", "123", "no-es-object-id", "6a1f1a1a1a1a1a1a1a1a1a1a1a"],
)
async def test_rejects_malformed_appointment_id_in_path(
    client: AsyncClient, bad_id: str
) -> None:
    assert (await client.get(f"/appointments/{bad_id}")).status_code == 422
    patch_response = await client.patch(
        f"/appointments/{bad_id}/status", json={"status": "confirmada"}
    )
    assert patch_response.status_code == 422
    assert (await client.delete(f"/appointments/{bad_id}")).status_code == 422


@pytest.mark.parametrize(
    "params",
    [{"patient_id": "abc"}, {"doctor_id": "abc"}, {"patient_id": "123"}],
)
async def test_rejects_malformed_id_in_query(client: AsyncClient, params: dict) -> None:
    response = await client.get("/appointments", params=params)

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


@pytest.mark.parametrize(
    "params",
    [
        {"status": "en-curso"},
        {"status": ""},
        {"status": "PENDIENTE"},
        {"date": "05-11-2026"},
        {"date": "2026-13-01"},
        {"date": "ayer"},
        {"date": ""},
    ],
)
async def test_rejects_invalid_filters(client: AsyncClient, params: dict) -> None:
    response = await client.get("/appointments", params=params)

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)