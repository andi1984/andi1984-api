from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PostResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "title": "QueuePool Limit Reached",
                    "summary": "Reproducing SQLAlchemy's QueuePool error in FastAPI.",
                    "url": "https://andi1984.dev/posts/python/fastapi-queuepool-limit",
                    "published": "2026-10-05T12:00:00Z",
                    "tags": ["article", "python"],
                }
            ]
        },
    )

    title: str
    summary: str
    url: str
    published: datetime
    tags: list[str]
