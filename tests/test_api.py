from fastapi.testclient import TestClient

from app import __version__
from app.core.config import Settings
from app.main import create_app


def test_get_age(client: TestClient) -> None:
    response = client.get("/api/v1/age")
    assert response.status_code == 200
    assert response.json() == {"age": 42, "birth_year": 1984, "current_year": 2026}


def test_get_age_unversioned_alias(client: TestClient) -> None:
    response = client.get("/age")
    assert response.status_code == 200
    assert response.json()["age"] == 42


def test_health(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__, "environment": "test"}


def test_request_id_generated(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert len(response.headers["X-Request-ID"]) == 32


def test_request_id_propagated(client: TestClient) -> None:
    response = client.get("/api/v1/health", headers={"X-Request-ID": "abc-123"})
    assert response.headers["X-Request-ID"] == "abc-123"


def test_unknown_route_returns_error_envelope(client: TestClient) -> None:
    response = client.get("/api/v1/nope")
    assert response.status_code == 404


def test_openapi_available(client: TestClient) -> None:
    assert client.get("/openapi.json").status_code == 200
    assert client.get("/docs").status_code == 200


def test_docs_available_in_production() -> None:
    app = create_app(Settings(environment="production", cors_origins=[]))
    with TestClient(app) as production_client:
        assert production_client.get("/docs").status_code == 200
        assert production_client.get("/redoc").status_code == 200
