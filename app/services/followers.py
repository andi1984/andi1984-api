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

    def __init__(self, username: str, token: str | None = None) -> None:
        self._username = username
        self._token = token

    async def count(self) -> int:
        headers = {"X-GitHub-Api-Version": "2022-11-28"}
        if self._token:
            # Unauthenticated calls share a 60/hour limit per IP, which hosting IPs often exhaust.
            headers["Authorization"] = f"Bearer {self._token}"
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"https://api.github.com/users/{self._username}", headers=headers
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
        retry_after: timedelta = timedelta(minutes=1),
        platforms: tuple[str, ...] = ("mastodon", "youtube", "devto", "github"),
    ) -> None:
        self._sources = sources
        self._ttl = ttl
        self._retry_after = retry_after
        self._clock = clock
        self._counts: dict[str, int | None] = dict.fromkeys(platforms)
        self._next_refresh: datetime | None = None
        self._lock = asyncio.Lock()

    async def get(self) -> FollowerCounts:
        async with self._lock:
            if self._next_refresh is None or self._clock.now() >= self._next_refresh:
                await self._refresh()
            return FollowerCounts(counts=dict(self._counts))

    async def _refresh(self) -> None:
        results = await asyncio.gather(
            *(source.count() for source in self._sources), return_exceptions=True
        )
        failed = False
        for source, result in zip(self._sources, results, strict=True):
            if isinstance(result, BaseException):
                # Keep the last known value (if any) rather than dropping the platform.
                logger.warning("follower count failed for %s: %r", source.name, result)
                failed = True
            else:
                self._counts[source.name] = result
        # Retry soon after a failure instead of serving a gap for the whole TTL.
        delay = min(self._retry_after, self._ttl) if failed else self._ttl
        self._next_refresh = self._clock.now() + delay
