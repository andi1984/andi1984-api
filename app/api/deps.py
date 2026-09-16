"""FastAPI dependency wiring. Override these in tests via app.dependency_overrides."""

from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.services.age import AgeService
from app.services.clock import Clock, SystemClock

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_clock(settings: SettingsDep) -> Clock:
    return SystemClock(settings.timezone)


ClockDep = Annotated[Clock, Depends(get_clock)]


def get_age_service(settings: SettingsDep, clock: ClockDep) -> AgeService:
    return AgeService(birth_year=settings.birth_year, clock=clock)


AgeServiceDep = Annotated[AgeService, Depends(get_age_service)]
