from fastapi import APIRouter

from app.schemas.profile import LinkResponse, NowItemResponse, ProfileResponse, ProjectResponse
from app.services.profile import LINKS, NOW, PROFILE, PROJECTS

router = APIRouter()


@router.get("/me", response_model=ProfileResponse, summary="Who I am")
async def get_me() -> ProfileResponse:
    return ProfileResponse.model_validate(PROFILE)


@router.get("/links", response_model=list[LinkResponse], summary="Where to find me")
async def get_links() -> list[LinkResponse]:
    return [LinkResponse.model_validate(link) for link in LINKS]


@router.get("/projects", response_model=list[ProjectResponse], summary="Things I've built")
async def get_projects() -> list[ProjectResponse]:
    return [ProjectResponse.model_validate(project) for project in PROJECTS]


@router.get("/now", response_model=list[NowItemResponse], summary="What I'm doing right now")
async def get_now() -> list[NowItemResponse]:
    return [NowItemResponse.model_validate(item) for item in NOW]
