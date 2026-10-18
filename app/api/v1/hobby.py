from fastapi import APIRouter

from app.schemas.hobby import HobbyResponse
from app.services.profile import HOBBY

router = APIRouter()


@router.get("/hobby", response_model=HobbyResponse, summary="My hobby")
async def get_hobby() -> HobbyResponse:
    return HobbyResponse(id=HOBBY.id, name=HOBBY.name)
