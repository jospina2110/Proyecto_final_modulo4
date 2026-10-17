import pytest
from beanie import init_beanie
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.models import Appointment, Doctor, Patient


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    await init_beanie(
        database=client["test_db"],
        document_models=[Patient, Doctor, Appointment],
    )
    yield client


@pytest.fixture
async def client(db):
    """Cliente HTTP contra la app ASGI sin lifespan: `db` inicializa Beanie."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client