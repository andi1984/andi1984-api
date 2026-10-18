"""Application factory."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.middleware.request_context import RequestContextMiddleware
from app.schemas.error import ErrorResponse
from app.services.clock import SystemClock
from app.services.followers import (
    DevToSource,
    FollowerSource,
    FollowersService,
    GitHubSource,
    MastodonSource,
    YouTubeSource,
)
from app.services.writing import HttpFeedFetcher, WritingService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    logger.info("starting %s (%s)", settings.app_name, settings.environment)
    yield
    logger.info("shutting down")


def _follower_sources(settings: Settings) -> list[FollowerSource]:
    sources: list[FollowerSource] = [
        GitHubSource(settings.github_username),
        MastodonSource(settings.mastodon_instance_url, settings.mastodon_account),
    ]
    if settings.youtube_api_key:
        sources.append(
            YouTubeSource(settings.youtube_api_key.get_secret_value(), settings.youtube_handle)
        )
    if settings.devto_api_key:
        sources.append(DevToSource(settings.devto_api_key.get_secret_value()))
    return sources


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        debug=settings.debug,
        lifespan=lifespan,
        responses={
            422: {"model": ErrorResponse, "description": "Validation error"},
            500: {"model": ErrorResponse, "description": "Internal server error"},
        },
    )
    app.state.settings = settings
    # Route dependencies resolve settings through get_settings(); bind them to *this* instance
    # so create_app(custom_settings) is honoured (important for tests).
    app.dependency_overrides[get_settings] = lambda: settings
    app.state.writing_service = WritingService(
        feed_url=settings.writing_feed_url,
        ttl=timedelta(seconds=settings.writing_cache_ttl_seconds),
        fetcher=HttpFeedFetcher(),
        clock=SystemClock(settings.timezone),
    )
    app.state.followers_service = FollowersService(
        sources=_follower_sources(settings),
        ttl=timedelta(seconds=settings.followers_cache_ttl_seconds),
        clock=SystemClock(settings.timezone),
    )

    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_methods=["GET"],
            allow_headers=["*"],
        )
    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    # Unversioned alias so GET /age works too
    app.include_router(api_router, include_in_schema=False)

    return app


app = create_app()
