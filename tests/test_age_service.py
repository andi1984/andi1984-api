from datetime import UTC, datetime

import pytest

from app.services.age import AgeService
from app.services.clock import FixedClock


@pytest.mark.parametrize(
    ("year", "expected"),
    [(1984, 0), (2000, 16), (2026, 42), (2050, 66)],
)
def test_age_is_current_year_minus_birth_year(year: int, expected: int) -> None:
    service = AgeService(birth_year=1984, clock=FixedClock(datetime(year, 6, 1, tzinfo=UTC)))
    result = service.calculate()
    assert result.age == expected
    assert result.current_year == year
    assert result.birth_year == 1984
