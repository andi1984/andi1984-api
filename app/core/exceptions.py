"""Domain exceptions and their HTTP mapping."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base class for domain errors that map to an HTTP response."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "app_error"

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"


class UpstreamError(AppError):
    status_code = status.HTTP_502_BAD_GATEWAY
    code = "upstream_unavailable"


def _error_response(status_code: int, code: str, detail: object) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content={"error": {"code": code, "detail": detail}}
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError) -> JSONResponse:
        return _error_response(exc.status_code, exc.code, exc.detail)

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "validation_error", exc.errors()
        )

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception")
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "internal_error", "Internal server error"
        )
