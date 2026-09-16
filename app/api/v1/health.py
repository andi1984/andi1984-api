from fastapi import APIRouter

from app import __version__
from app.api.deps import SettingsDep
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
async def health(settings: SettingsDep) -> HealthResponse:
    return HealthResponse(status="ok", version=__version__, environment=settings.environment)
