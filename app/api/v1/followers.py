from fastapi import APIRouter

from app.api.deps import FollowersServiceDep
from app.schemas.followers import FollowersResponse

router = APIRouter()


@router.get(
    "/followers",
    response_model=FollowersResponse,
    summary="Follower counts across platforms",
    description=(
        "Mastodon, YouTube, dev.to and GitHub followers plus their total. Cached for an hour. "
        "A platform is null when it is not configured or has never been reachable."
    ),
)
async def get_followers(service: FollowersServiceDep) -> FollowersResponse:
    result = await service.get()
    return FollowersResponse(total=result.total, **result.counts)
