from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import AppError, NotFoundError


def _install_routes(app: FastAPI) -> None:
    @app.get("/_boom/not-found")
    async def _not_found() -> None:
        raise NotFoundError("thing missing")

    @app.get("/_boom/app-error")
    async def _app_error() -> None:
        raise AppError("bad input")

    @app.get("/_boom/crash")
    async def _crash() -> None:
        raise RuntimeError("kaboom")

    @app.get("/_boom/validate")
    async def _validate(n: int) -> int:
        return n


def test_domain_error_envelope(app: FastAPI, client: TestClient) -> None:
    _install_routes(app)
    response = client.get("/_boom/not-found")
    assert response.status_code == 404
    assert response.json() == {"error": {"code": "not_found", "detail": "thing missing"}}

    response = client.get("/_boom/app-error")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "app_error"


def test_validation_error_envelope(app: FastAPI, client: TestClient) -> None:
    _install_routes(app)
    response = client.get("/_boom/validate", params={"n": "notanumber"})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["detail"][0]["loc"] == ["query", "n"]


def test_unhandled_error_is_masked(app: FastAPI) -> None:
    _install_routes(app)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/_boom/crash")
    assert response.status_code == 500
    assert response.json() == {
        "error": {"code": "internal_error", "detail": "Internal server error"}
    }
    assert "kaboom" not in response.text
