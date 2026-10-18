from pydantic import BaseModel, ConfigDict, Field


class FollowersResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"total": 176, "mastodon": 111, "youtube": None, "devto": None, "github": 65}
            ]
        }
    )

    total: int = Field(description="Sum of all platforms that returned a count")
    mastodon: int | None
    youtube: int | None = Field(description="null unless a YouTube API key is configured")
    devto: int | None = Field(description="null unless a dev.to API key is configured")
    github: int | None
