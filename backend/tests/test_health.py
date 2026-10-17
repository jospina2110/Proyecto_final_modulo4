from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_declara_servidor_api() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    servers = response.json()["servers"]
    assert [server["url"] for server in servers] == ["/api"]
