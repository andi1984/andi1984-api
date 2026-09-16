from fastapi import APIRouter

from app.api.v1 import age, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(age.router, tags=["age"])
