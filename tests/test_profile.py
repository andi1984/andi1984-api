import pytest
from fastapi.testclient import TestClient


def test_get_me(client: TestClient) -> None:
    response = client.get("/api/v1/me")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Andreas Sander"
    assert body["handle"] == "andi1984"
    assert body["website"] == "https://andi1984.dev"
    assert body["location"] == {
        "city": "Heusweiler",
        "region": "Saarland",
        "country": "DE",
        "label": "South-West Germany",
    }


def test_get_links(client: TestClient) -> None:
    response = client.get("/api/v1/links")
    assert response.status_code == 200
    links = {link["name"]: link["url"] for link in response.json()}
    assert links["github"] == "https://github.com/andi1984"
    assert all(url.startswith("https://") for url in links.values())


def test_get_projects(client: TestClient) -> None:
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    projects = response.json()
    assert projects
    assert {"name", "description", "url", "tech"} <= projects[0].keys()
    assert isinstance(projects[0]["tech"], list)


def test_get_now(client: TestClient) -> None:
    response = client.get("/api/v1/now")
    assert response.status_code == 200
    kinds = [item["kind"] for item in response.json()]
    assert kinds == ["building", "learning", "growing"]


def test_get_hobby(client: TestClient) -> None:
    response = client.get("/api/v1/hobby")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Gardening"}


@pytest.mark.parametrize("path", ["/me", "/links", "/projects", "/now", "/hobby"])
def test_unversioned_aliases(client: TestClient, path: str) -> None:
    assert client.get(path).status_code == 200
