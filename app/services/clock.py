"""Clock abstraction so time-dependent logic is testable."""

from datetime import datetime
from typing import Protocol
from zoneinfo import ZoneInfo


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def __init__(self, timezone: str = "UTC") -> None:
        self._tz = ZoneInfo(timezone)

    def now(self) -> datetime:
        return datetime.now(self._tz)


class FixedClock:
    """Deterministic clock for tests."""

    def __init__(self, fixed: datetime) -> None:
        self._fixed = fixed

    def now(self) -> datetime:
        return self._fixed
