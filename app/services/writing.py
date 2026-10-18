"""Latest writing from the andi1984.dev RSS feed, cached in memory."""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from typing import Protocol

import httpx
from defusedxml import ElementTree

from app.core.exceptions import UpstreamError
from app.services.clock import Clock

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Post:
    title: str
    summary: str
    url: str
    published: datetime
    tags: tuple[str, ...]


class FeedFetcher(Protocol):
    async def fetch(self, url: str) -> str: ...


class HttpFeedFetcher:
    def __init__(self, timeout: float = 5.0) -> None:
        self._timeout = timeout

    async def fetch(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text


def parse_feed(xml: str) -> list[Post]:
    """Parse an RSS 2.0 document. Items without a title, link or date are skipped."""
    root = ElementTree.fromstring(xml)
    posts = []
    for item in root.iterfind("channel/item"):
        title = item.findtext("title")
        url = item.findtext("link")
        pub_date = item.findtext("pubDate")
        if not (title and url and pub_date):
            continue
        posts.append(
            Post(
                title=title.strip(),
                summary=(item.findtext("description") or "").strip(),
                url=url.strip(),
                published=parsedate_to_datetime(pub_date),
                tags=tuple(c.text.strip().lower() for c in item.iterfind("category") if c.text),
            )
        )
    return sorted(posts, key=lambda post: post.published, reverse=True)


class WritingService:
    def __init__(self, feed_url: str, ttl: timedelta, fetcher: FeedFetcher, clock: Clock) -> None:
        self._feed_url = feed_url
        self._ttl = ttl
        self._fetcher = fetcher
        self._clock = clock
        self._posts: list[Post] | None = None
        self._fetched_at: datetime | None = None
        self._lock = asyncio.Lock()

    async def latest(self, limit: int, tag: str | None = None) -> list[Post]:
        posts = await self._get_posts()
        if tag:
            posts = [post for post in posts if tag.lower() in post.tags]
        return posts[:limit]

    async def _get_posts(self) -> list[Post]:
        async with self._lock:
            if self._posts is not None and not self._is_stale():
                return self._posts
            try:
                self._posts = parse_feed(await self._fetcher.fetch(self._feed_url))
                self._fetched_at = self._clock.now()
            except Exception as exc:
                if self._posts is None:
                    raise UpstreamError("Writing feed is unavailable") from exc
                # Serve the stale copy rather than failing; retry on the next request.
                logger.warning("feed refresh failed, serving stale copy", exc_info=True)
            return self._posts

    def _is_stale(self) -> bool:
        return self._fetched_at is None or self._clock.now() - self._fetched_at >= self._ttl
