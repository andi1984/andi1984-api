from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import WritingServiceDep
from app.schemas.writing import PostResponse

router = APIRouter()


@router.get(
    "/writing",
    response_model=list[PostResponse],
    summary="Latest articles and notes",
    description="Newest first, from the andi1984.dev RSS feed. Cached for an hour.",
)
async def get_writing(
    service: WritingServiceDep,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    tag: Annotated[str | None, Query(max_length=50, description="e.g. python")] = None,
) -> list[PostResponse]:
    posts = await service.latest(limit=limit, tag=tag)
    return [PostResponse.model_validate(post) for post in posts]
