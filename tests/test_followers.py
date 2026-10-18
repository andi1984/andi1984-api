from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_followers_service
from app.core.config import Settings
from app.main import _follower_sources
from app.services.followers import (
    DevToSource,
    FollowersService,
    GitHubSource,
    MastodonSource,
    YouTubeSource,
)

START = datetime(2026, 10, 18, 12, 0, tzinfo=UTC)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class MutableClock:
    def __init__(self, now: datetime) -> None:
        self.current = now

    def now(self) -> datetime:
        return self.current


class StubSource:
    def __init__(self, name: str, value: int) -> None:
        self.name = name
        self.value = value
        self.calls = 0
        self.fail = False

    async def count(self) -> int:
        self.calls += 1
        if self.fail:
            raise ConnectionError("boom")
        return self.value


def mock_http(monkeypatch: pytest.MonkeyPatch, handler: Callable[[httpx.Request], Any]) -> None:
    real_client = httpx.AsyncClient
    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kwargs: real_client(transport=transport, **kwargs)
    )


@pytest.mark.anyio
async def test_totals_configured_sources_and_nulls_the_rest() -> None:
    service = FollowersService(
        sources=[StubSource("github", 65), StubSource("mastodon", 111)],
        ttl=timedelta(hours=1),
        clock=MutableClock(START),
    )
    result = await service.get()
    assert result.counts == {"mastodon": 111, "youtube": None, "devto": None, "github": 65}
    assert result.total == 176


@pytest.mark.anyio
async def test_caches_and_keeps_last_value_when_a_source_fails() -> None:
    github, clock = StubSource("github", 65), MutableClock(START)
    service = FollowersService(sources=[github], ttl=timedelta(hours=1), clock=clock)

    await service.get()
    await service.get()
    assert github.calls == 1

    github.fail = True
    clock.current = START + timedelta(hours=1)
    result = await service.get()
    assert github.calls == 2
    assert result.counts["github"] == 65


@pytest.mark.anyio
async def test_github_source(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/users/andi1984"
        return httpx.Response(200, json={"followers": 65})

    mock_http(monkeypatch, handler)
    assert await GitHubSource("andi1984").count() == 65


@pytest.mark.anyio
async def test_mastodon_source(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == ("https://dibbelabb.es/api/v1/accounts/lookup?acct=andi1984dev")
        return httpx.Response(200, json={"followers_count": 111})

    mock_http(monkeypatch, handler)
    assert await MastodonSource("https://dibbelabb.es/", "andi1984dev").count() == 111


@pytest.mark.anyio
async def test_youtube_source(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["forHandle"] == "@andi1984dev"
        assert "key" not in request.url.params
        assert request.headers["X-goog-api-key"] == "yt-key"
        return httpx.Response(200, json={"items": [{"statistics": {"subscriberCount": "42"}}]})

    mock_http(monkeypatch, handler)
    assert await YouTubeSource("yt-key", "@andi1984dev").count() == 42


@pytest.mark.anyio
async def test_devto_source_pages_until_short_page(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(DevToSource, "PAGE_SIZE", 2)
    pages: dict[str, list[dict[str, str]]] = {"1": [{}, {}], "2": [{}]}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["api-key"] == "devto-key"
        return httpx.Response(200, json=pages[request.url.params["page"]])

    mock_http(monkeypatch, handler)
    assert await DevToSource("devto-key").count() == 3


def test_keyed_sources_only_enabled_with_keys() -> None:
    without_keys = _follower_sources(Settings(_env_file=None))
    assert [source.name for source in without_keys] == ["github", "mastodon"]

    with_keys = _follower_sources(
        Settings(_env_file=None, youtube_api_key="yt", devto_api_key="dt")
    )
    assert [source.name for source in with_keys] == ["github", "mastodon", "youtube", "devto"]


def test_api_key_not_leaked_in_settings_repr() -> None:
    assert "secret-value" not in repr(Settings(_env_file=None, devto_api_key="secret-value"))


@pytest.fixture
def stub_github(app: FastAPI) -> StubSource:
    github = StubSource("github", 65)
    service = FollowersService(
        sources=[github, StubSource("mastodon", 111)],
        ttl=timedelta(hours=1),
        clock=MutableClock(START),
    )
    app.dependency_overrides[get_followers_service] = lambda: service
    return github


def test_get_followers(client: TestClient, stub_github: StubSource) -> None:
    response = client.get("/api/v1/followers")
    assert response.status_code == 200
    assert response.json() == {
        "total": 176,
        "mastodon": 111,
        "youtube": None,
        "devto": None,
        "github": 65,
    }
