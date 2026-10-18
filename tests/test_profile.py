import re

import pytest
from fastapi.testclient import TestClient


def test_get_me(client: TestClient) -> None:
    response = client.get("/api/v1/me")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Andreas Sander"
    assert body["handle"] == "andi1984"
    assert body["website"] == "https://andi1984.dev"
    assert body["location"] == {"city": "Heusweiler", "region": "Saarland", "country": "DE"}


def test_get_links(client: TestClient) -> None:
    response = client.get("/api/v1/links")
    assert response.status_code == 200
    links = {link["name"]: link for link in response.json()}
    assert links["github"] == {
        "name": "github",
        "url": "https://github.com/andi1984",
        "kind": "profile",
        "handle": "andi1984",
    }
    assert links["twitch"]["url"] == "https://www.twitch.tv/andi1984"
    assert links["mastodon"]["handle"] == "@andi1984dev@dibbelabb.es"
    assert all(link["url"].startswith("https://") for link in links.values())


def test_links_have_handles_exactly_when_they_are_profiles(client: TestClient) -> None:
    for link in client.get("/api/v1/links").json():
        assert link["kind"] in {"profile", "site"}
        assert (link["handle"] is not None) == (link["kind"] == "profile"), link["name"]


def test_get_projects_keeps_display_order(client: TestClient) -> None:
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    assert [project["id"] for project in response.json()] == [
        "ferrico",
        "primico",
        "tinypng",
        "mastodon-news-bot",
        "kann-ich-lueften",
    ]


def test_get_projects_shape(client: TestClient) -> None:
    tinypng = next(p for p in client.get("/api/v1/projects").json() if p["id"] == "tinypng")
    assert tinypng["name"] == "TinyPNG for VS Code"
    assert tinypng["ai_assisted"] is False
    assert tinypng["license"] is None
    assert tinypng["languages"] == []
    assert tinypng["facts"] == [
        {"label": "Formats", "value": "PNG, JPG"},
        {"label": "Source", "value": "Open source"},
    ]


def test_project_ids_are_unique_slugs(client: TestClient) -> None:
    ids = [project["id"] for project in client.get("/api/v1/projects").json()]
    assert len(ids) == len(set(ids))
    assert all(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", project_id) for project_id in ids)


def test_project_fact_labels_are_non_empty(client: TestClient) -> None:
    for project in client.get("/api/v1/projects").json():
        assert all(fact["label"].strip() for fact in project["facts"]), project["id"]


def test_get_now(client: TestClient) -> None:
    response = client.get("/api/v1/now")
    assert response.status_code == 200
    assert response.json() == [
        {"kind": "building", "text": "Ferrico — an Android build and smarter duplicate detection."},
        {"kind": "learning", "text": "Enough Rust to stop fighting the borrow checker in public."},
        {"kind": "growing", "text": "Tomatoes, three kinds of mint, and one stubborn fig tree."},
    ]


def test_get_hobby(client: TestClient) -> None:
    response = client.get("/api/v1/hobby")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Gardening"}


@pytest.mark.parametrize("path", ["/me", "/links", "/projects", "/now", "/hobby"])
def test_unversioned_aliases(client: TestClient, path: str) -> None:
    assert client.get(path).status_code == 200
