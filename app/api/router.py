from fastapi import APIRouter

from app.api.v1 import age, followers, health, hobby, profile, writing

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(age.router, tags=["age"])
api_router.include_router(hobby.router, tags=["hobby"])
api_router.include_router(profile.router, tags=["profile"])
api_router.include_router(writing.router, tags=["writing"])
api_router.include_router(followers.router, tags=["followers"])
