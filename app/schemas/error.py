from typing import Any

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    detail: Any


class ErrorResponse(BaseModel):
    error: ErrorDetail
