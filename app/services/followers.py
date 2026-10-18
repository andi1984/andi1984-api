"""Follower counts across platforms, cached in memory. Port of andi1984/some-influence."""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

import httpx

from app.services.clock import Clock

logger = logging.getLogger(__name__)

TIMEOUT = 5.0


class FollowerSource(Protocol):
    name: str

    async def count(self) -> int: ...


class GitHubSource:
    name = "github"

    def __init__(self, username: str) -> None:
        self._username = username

    async def count(self) -> int:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"https://api.github.com/users/{self._username}",
                headers={"X-GitHub-Api-Version": "2022-11-28"},
            )
            response.raise_for_status()
            return int(response.json()["followers"])


class MastodonSource:
    name = "mastodon"

    def __init__(self, instance_url: str, account: str) -> None:
        self._instance_url = instance_url.rstrip("/")
        self._account = account

    async def count(self) -> int:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{self._instance_url}/api/v1/accounts/lookup", params={"acct": self._account}
            )
            response.raise_for_status()
            return int(response.json()["followers_count"])


class YouTubeSource:
    name = "youtube"

    def __init__(self, api_key: str, handle: str) -> None:
        self._api_key = api_key
        self._handle = handle

    async def count(self) -> int:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Key goes in a header, not the query string, so it never shows up in request logs.
            response = await client.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={"part": "statistics", "forHandle": self._handle},
                headers={"X-goog-api-key": self._api_key},
            )
            response.raise_for_status()
            return int(response.json()["items"][0]["statistics"]["subscriberCount"])


class DevToSource:
    """dev.to has no public follower count, so page through the authenticated list."""

    name = "devto"
    PAGE_SIZE = 1000
    MAX_PAGES = 50

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def count(self) -> int:
        total = 0
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            for page in range(1, self.MAX_PAGES + 1):
                response = await client.get(
                    "https://dev.to/api/followers/users",
                    headers={"api-key": self._api_key},
                    params={"per_page": self.PAGE_SIZE, "page": page},
                )
                response.raise_for_status()
                followers = response.json()
                total += len(followers)
                if len(followers) < self.PAGE_SIZE:
                    break
        return total


@dataclass(frozen=True, slots=True)
class FollowerCounts:
    counts: dict[str, int | None]

    @property
    def total(self) -> int:
        return sum(count for count in self.counts.values() if count is not None)


class FollowersService:
    def __init__(
        self,
        sources: list[FollowerSource],
        ttl: timedelta,
        clock: Clock,
        platforms: tuple[str, ...] = ("mastodon", "youtube", "devto", "github"),
    ) -> None:
        self._sources = sources
        self._ttl = ttl
        self._clock = clock
        self._platforms = platforms
        self._counts: dict[str, int | None] = dict.fromkeys(platforms)
        self._fetched_at: datetime | None = None
        self._lock = asyncio.Lock()

    async def get(self) -> FollowerCounts:
        async with self._lock:
            if self._is_stale():
                await self._refresh()
            return FollowerCounts(counts=dict(self._counts))

    async def _refresh(self) -> None:
        results = await asyncio.gather(
            *(source.count() for source in self._sources), return_exceptions=True
        )
        for source, result in zip(self._sources, results, strict=True):
            if isinstance(result, BaseException):
                # Keep the last known value (if any) rather than dropping the platform.
                logger.warning("follower count failed for %s: %r", source.name, result)
            else:
                self._counts[source.name] = result
        self._fetched_at = self._clock.now()

    def _is_stale(self) -> bool:
        return self._fetched_at is None or self._clock.now() - self._fetched_at >= self._ttl
