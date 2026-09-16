from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_clock
from app.core.config import Settings
from app.main import create_app
from app.services.clock import FixedClock

FROZEN_NOW = datetime(2026, 9, 16, 12, 0, tzinfo=UTC)


@pytest.fixture
def settings() -> Settings:
    return Settings(environment="test", birth_year=1984, cors_origins=[])


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    application = create_app(settings)
    application.dependency_overrides[get_clock] = lambda: FixedClock(FROZEN_NOW)
    return application


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
