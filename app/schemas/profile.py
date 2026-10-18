from pydantic import BaseModel, ConfigDict


class ProfileResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "Andreas Sander",
                    "handle": "andi1984",
                    "role": "Senior Product Engineer",
                    "employer": "Digital Science (Dimensions)",
                    "location": "Saarbrücken, Germany",
                    "bio": "Building for the web since 2012.",
                    "website": "https://andi1984.dev",
                    "avatar_url": "https://andi1984.dev/ava.jpg",
                    "coding_since": 2012,
                }
            ]
        },
    )

    name: str
    handle: str
    role: str
    employer: str
    location: str
    bio: str
    website: str
    avatar_url: str
    coding_since: int


class LinkResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"examples": [{"name": "github", "url": "https://github.com/andi1984"}]},
    )

    name: str
    url: str


class ProjectResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "Ferrico",
                    "description": "Local-first bookmark manager",
                    "url": "https://github.com/viberfasend/ferrico_dot_app",
                    "tech": ["Rust", "Tauri"],
                }
            ]
        },
    )

    name: str
    description: str
    url: str
    tech: list[str]


class NowItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"examples": [{"kind": "learning", "text": "Rust"}]},
    )

    kind: str
    text: str
