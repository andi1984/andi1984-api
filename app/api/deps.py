"""FastAPI dependency wiring. Override these in tests via app.dependency_overrides."""

from typing import Annotated

from fastapi import Depends, Request

from app.core.config import Settings, get_settings
from app.services.age import AgeService
from app.services.clock import Clock, SystemClock
from app.services.writing import WritingService

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_clock(settings: SettingsDep) -> Clock:
    return SystemClock(settings.timezone)


ClockDep = Annotated[Clock, Depends(get_clock)]


def get_age_service(settings: SettingsDep, clock: ClockDep) -> AgeService:
    return AgeService(birth_year=settings.birth_year, clock=clock)


AgeServiceDep = Annotated[AgeService, Depends(get_age_service)]


def get_writing_service(request: Request) -> WritingService:
    # One instance per app (created in create_app) so the feed cache survives across requests.
    service: WritingService = request.app.state.writing_service
    return service


WritingServiceDep = Annotated[WritingService, Depends(get_writing_service)]
