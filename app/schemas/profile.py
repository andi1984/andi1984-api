from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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
        json_schema_extra={
            "examples": [
                {
                    "name": "mastodon",
                    "url": "https://dibbelabb.es/@andi1984dev",
                    "kind": "profile",
                    "handle": "@andi1984dev@dibbelabb.es",
                }
            ]
        },
    )

    name: str = Field(description="Stable identifier of the link, e.g. github or rss")
    url: str
    kind: Literal["profile", "site"] = Field(
        description="profile: an account on another platform; site: a page of andi1984.dev "
        "or a related document"
    )
    handle: str | None = Field(
        description="Account name in the platform's own notation; null for site links"
    )


class FactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    label: str = Field(min_length=1)
    value: str


class ProjectResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "ferrico",
                    "name": "Ferrico",
                    "tagline": "A home for the links I want to keep.",
                    "description": "A local-first bookmark manager for collecting, "
                    "organising and finding links again.",
                    "homepage": "https://viberfasend.github.io/ferrico_dot_app/",
                    "repository": "https://github.com/viberfasend/ferrico_dot_app",
                    "ai_assisted": True,
                    "category": "ProductivityApplication",
                    "tech": ["Rust", "Tauri", "React", "TypeScript"],
                    "platforms": ["macOS", "Linux", "Windows"],
                    "license": "GPL-3.0-or-later",
                    "languages": [],
                    "facts": [{"label": "Storage", "value": "Local SQLite database"}],
                }
            ]
        },
    )

    id: str = Field(
        pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$",
        description="Stable lowercase slug; never changes once published",
    )
    name: str
    tagline: str = Field(description="One line")
    description: str = Field(description="A paragraph")
    homepage: str | None = Field(
        description="Where people use the project: demo, store page or live bot"
    )
    repository: str | None = Field(description="Source code repository")
    ai_assisted: bool = Field(description="Built or maintained substantially with AI coding tools")
    category: str = Field(
        description="schema.org applicationCategory value, e.g. ProductivityApplication"
    )
    tech: list[str] = Field(description="Languages, frameworks and services it is built with")
    platforms: list[str] = Field(description="Where it runs, e.g. Android, macOS, Web")
    license: str | None = Field(
        description="SPDX license identifier; null when the repository has no license file"
    )
    languages: list[str] = Field(
        description="Human languages of the product, not programming languages"
    )
    facts: list[FactResponse] = Field(description="Ordered one-off facts")


class NowItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"examples": [{"kind": "learning", "text": "Rust"}]},
    )

    kind: str
    text: str
