# andi1984-api

Personal API built with [FastAPI](https://fastapi.tiangolo.com/).

## Endpoints

| Method | Path               | Description                                         |
|--------|--------------------|-----------------------------------------------------|
| GET    | `/api/v1/me`       | Profile: name, role, location, bio                  |
| GET    | `/api/v1/links`    | Site links and social profiles with handles         |
| GET    | `/api/v1/projects` | Projects shown on andi1984.dev/portfolio            |
| GET    | `/api/v1/now`      | What I'm building, learning, growing                |
| GET    | `/api/v1/writing`  | Latest posts from the RSS feed (`?limit=`, `?tag=`) |
| GET    | `/api/v1/followers`| Mastodon, YouTube, dev.to and GitHub follower counts|
| GET    | `/api/v1/hobby`    | My hobby                                            |
| GET    | `/api/v1/age`      | Age in years (`current_year - 1984`)                |
| GET    | `/api/v1/health`   | Liveness probe                                      |
| GET    | `/docs`            | Swagger UI (also `/redoc`, `/openapi.json`)         |

All endpoints also work without the version prefix (e.g. `/me`).

```json
GET /api/v1/age
{"age": 42, "birth_year": 1984, "current_year": 2026}
```

## Quickstart

```bash
uv sync
cp .env.example .env
make dev          # http://127.0.0.1:8000/docs
```

## Development

```bash
make test         # pytest + coverage
make lint         # ruff
make typecheck    # mypy --strict
make check        # all of the above
make format       # auto-format
```

## Configuration

All settings are read from environment variables (prefix `APP_`) or `.env`. See `.env.example`.

| Variable           | Default       | Notes                                     |
|--------------------|---------------|-------------------------------------------|
| `APP_ENVIRONMENT`  | `development` | `development` \| `test` \| `production`   |
| `APP_LOG_LEVEL`    | `INFO`        |                                           |
| `APP_BIRTH_YEAR`   | `1984`        |                                           |
| `APP_TIMEZONE`     | `UTC`         | IANA zone used to determine current year  |
| `APP_CORS_ORIGINS` | *(empty)*     | Comma-separated; empty disables CORS      |
| `APP_WRITING_FEED_URL` | `https://andi1984.dev/rss.xml` | Source for `/writing`        |
| `APP_WRITING_CACHE_TTL_SECONDS` | `3600` |                                     |
| `APP_FOLLOWERS_CACHE_TTL_SECONDS` | `3600` |                                   |
| `APP_GITHUB_TOKEN`    | *(unset)*  | Secret, no scopes. Avoids GitHub's 60/h anonymous limit |
| `APP_YOUTUBE_API_KEY` | *(unset)*  | Secret. Without it `youtube` is `null`    |
| `APP_DEVTO_API_KEY`   | *(unset)*  | Secret. Without it `devto` is `null`      |

`/followers` also reads `APP_GITHUB_USERNAME`, `APP_MASTODON_INSTANCE_URL`,
`APP_MASTODON_ACCOUNT` and `APP_YOUTUBE_HANDLE`; the defaults point at my accounts.

## Project layout

```
app/
  main.py              # create_app() factory, lifespan, middleware wiring
  core/
    config.py          # pydantic-settings Settings
    logging.py         # JSON logging with request-id correlation
    exceptions.py      # domain errors + handlers -> {"error": {"code", "detail"}}
  api/
    deps.py            # dependency injection wiring
    router.py          # aggregates versioned routers
    v1/                # route handlers (thin: parse -> service -> schema)
  schemas/             # pydantic request/response models
  services/            # pure domain logic (framework-free, injectable clock)
  middleware/          # request-id + access logging
tests/                 # pytest, TestClient, FixedClock override
```

## Docker

```bash
make docker
docker run -p 8000:8000 andi1984-api
```
