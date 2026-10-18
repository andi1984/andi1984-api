from datetime import UTC, datetime, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_writing_service
from app.core.exceptions import UpstreamError
from app.services.writing import WritingService, parse_feed

FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>andi1984.dev</title>
<item>
  <title><![CDATA[Older post]]></title>
  <description><![CDATA[Older summary]]></description>
  <link>https://andi1984.dev/posts/older</link>
  <category><![CDATA[Article]]></category>
  <category><![CDATA[Python]]></category>
  <pubDate>Mon, 05 Oct 2026 12:00:00 GMT</pubDate>
</item>
<item>
  <title><![CDATA[Newer note]]></title>
  <description><![CDATA[Newer summary]]></description>
  <link>https://andi1984.dev/notes/newer</link>
  <category><![CDATA[Note]]></category>
  <pubDate>Fri, 09 Oct 2026 12:00:00 GMT</pubDate>
</item>
<item>
  <title>Missing link and date</title>
</item>
</channel></rss>"""


class MutableClock:
    def __init__(self, now: datetime) -> None:
        self.current = now

    def now(self) -> datetime:
        return self.current


class StubFetcher:
    def __init__(self, body: str = FEED) -> None:
        self.body = body
        self.calls = 0
        self.fail = False

    async def fetch(self, url: str) -> str:
        self.calls += 1
        if self.fail:
            raise ConnectionError("boom")
        return self.body


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


START = datetime(2026, 10, 18, 12, 0, tzinfo=UTC)


def make_service(fetcher: StubFetcher, clock: MutableClock) -> WritingService:
    return WritingService(
        feed_url="https://example.test/rss.xml",
        ttl=timedelta(hours=1),
        fetcher=fetcher,
        clock=clock,
    )


def test_parse_feed_sorts_newest_first_and_skips_incomplete_items() -> None:
    posts = parse_feed(FEED)
    assert [post.title for post in posts] == ["Newer note", "Older post"]
    assert posts[1].tags == ("article", "python")
    assert posts[1].published == datetime(2026, 10, 5, 12, 0, tzinfo=UTC)


@pytest.mark.anyio
async def test_caches_until_ttl_expires() -> None:
    fetcher, clock = StubFetcher(), MutableClock(START)
    service = make_service(fetcher, clock)

    await service.latest(limit=10)
    clock.current = START + timedelta(minutes=59)
    await service.latest(limit=10)
    assert fetcher.calls == 1

    clock.current = START + timedelta(hours=1)
    await service.latest(limit=10)
    assert fetcher.calls == 2


@pytest.mark.anyio
async def test_serves_stale_copy_when_refresh_fails() -> None:
    fetcher, clock = StubFetcher(), MutableClock(START)
    service = make_service(fetcher, clock)
    await service.latest(limit=10)

    fetcher.fail = True
    clock.current = START + timedelta(hours=2)
    posts = await service.latest(limit=10)
    assert len(posts) == 2


@pytest.mark.anyio
async def test_raises_upstream_error_without_cached_copy() -> None:
    fetcher = StubFetcher()
    fetcher.fail = True
    service = make_service(fetcher, MutableClock(START))
    with pytest.raises(UpstreamError):
        await service.latest(limit=10)


@pytest.mark.anyio
async def test_filters_by_tag_and_limits() -> None:
    service = make_service(StubFetcher(), MutableClock(START))
    assert [p.title for p in await service.latest(limit=10, tag="Python")] == ["Older post"]
    assert len(await service.latest(limit=1)) == 1


@pytest.fixture
def stub_fetcher(app: FastAPI) -> StubFetcher:
    fetcher = StubFetcher()
    service = make_service(fetcher, MutableClock(START))
    app.dependency_overrides[get_writing_service] = lambda: service
    return fetcher


def test_get_writing(client: TestClient, stub_fetcher: StubFetcher) -> None:
    response = client.get("/api/v1/writing", params={"limit": 1})
    assert response.status_code == 200
    assert response.json() == [
        {
            "title": "Newer note",
            "summary": "Newer summary",
            "url": "https://andi1984.dev/notes/newer",
            "published": "2026-10-09T12:00:00Z",
            "tags": ["note"],
        }
    ]


def test_get_writing_rejects_bad_limit(client: TestClient, stub_fetcher: StubFetcher) -> None:
    response = client.get("/api/v1/writing", params={"limit": 0})
    assert response.status_code == 422


def test_get_writing_upstream_down(client: TestClient, stub_fetcher: StubFetcher) -> None:
    stub_fetcher.fail = True
    response = client.get("/api/v1/writing")
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "upstream_unavailable"
