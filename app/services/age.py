"""Age calculation service. Pure domain logic, no framework imports."""

from dataclasses import dataclass

from app.services.clock import Clock


@dataclass(frozen=True, slots=True)
class AgeResult:
    birth_year: int
    current_year: int

    @property
    def age(self) -> int:
        return self.current_year - self.birth_year


class AgeService:
    def __init__(self, birth_year: int, clock: Clock) -> None:
        self._birth_year = birth_year
        self._clock = clock

    def calculate(self) -> AgeResult:
        return AgeResult(birth_year=self._birth_year, current_year=self._clock.now().year)
