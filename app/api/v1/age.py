from fastapi import APIRouter

from app.api.deps import AgeServiceDep
from app.schemas.age import AgeResponse

router = APIRouter()


@router.get(
    "/age",
    response_model=AgeResponse,
    summary="Current age in years",
    description="Returns the age computed as `current_year - birth_year`.",
)
async def get_age(service: AgeServiceDep) -> AgeResponse:
    result = service.calculate()
    return AgeResponse(
        age=result.age, birth_year=result.birth_year, current_year=result.current_year
    )
