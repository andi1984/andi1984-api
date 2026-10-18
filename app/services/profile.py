"""Static profile content. Pure data, no framework imports.

Everything here is already self-published on github.com/andi1984 and andi1984.dev.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Location:
    city: str
    region: str
    country: str


@dataclass(frozen=True, slots=True)
class Profile:
    name: str
    handle: str
    role: str
    employer: str
    location: Location
    bio: str
    website: str
    avatar_url: str
    coding_since: int


@dataclass(frozen=True, slots=True)
class Link:
    name: str
    url: str


@dataclass(frozen=True, slots=True)
class Project:
    name: str
    description: str
    url: str
    tech: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NowItem:
    kind: str
    text: str


@dataclass(frozen=True, slots=True)
class Hobby:
    id: int
    name: str


PROFILE = Profile(
    name="Andreas Sander",
    handle="andi1984",
    role="Senior Product Engineer",
    employer="Digital Science (Dimensions)",
    location=Location(city="Heusweiler", region="Saarland", country="DE"),
    bio=(
        "Building for the web since 2012. React and TypeScript at the core, "
        "Python and FastAPI behind them, and LLM features that are useful in practice."
    ),
    website="https://andi1984.dev",
    avatar_url="https://andi1984.dev/ava.jpg",
    coding_since=2012,
)

LINKS: tuple[Link, ...] = (
    Link(name="website", url="https://andi1984.dev"),
    Link(name="writing", url="https://andi1984.dev/writing"),
    Link(name="rss", url="https://andi1984.dev/rss.xml"),
    Link(name="cv", url="https://andi1984.github.io/CV/"),
    Link(name="github", url="https://github.com/andi1984"),
    Link(name="linkedin", url="https://www.linkedin.com/in/andi1984"),
    Link(name="mastodon", url="https://dibbelabb.es/@andi1984dev"),
    Link(name="devto", url="https://dev.to/andi1984"),
    Link(name="youtube", url="https://www.youtube.com/@andi1984dev"),
)

PROJECTS: tuple[Project, ...] = (
    Project(
        name="Ferrico",
        description="Local-first bookmark manager",
        url="https://github.com/viberfasend/ferrico_dot_app",
        tech=("Rust", "Tauri"),
    ),
    Project(
        name="Primico",
        description="Importance-first todo app",
        url="https://github.com/viberfasend/primico",
        tech=("Kotlin Multiplatform",),
    ),
    Project(
        name="VSCode TinyPNG",
        description="Image compression extension for VS Code",
        url="https://github.com/andi1984/vscode-tinypng",
        tech=("TypeScript",),
    ),
    Project(
        name="Mastodon News Bot",
        description="Regional news aggregator for the fediverse",
        url="https://github.com/andi1984/mastodon-news-bot",
        tech=("TypeScript",),
    ),
    Project(
        name="Kann ich lüften?",
        description="Offline PWA that tells you whether airing out dries or dampens your flat",
        url="https://viberfasend.github.io/kann-ich-lueften/",
        tech=("PWA",),
    ),
)

NOW: tuple[NowItem, ...] = (
    NowItem(kind="building", text="An Android build of Ferrico and smarter duplicate detection"),
    NowItem(kind="learning", text="Enough Rust to stop fighting the borrow checker in public"),
    NowItem(kind="growing", text="Tomatoes, three kinds of mint and one stubborn fig tree"),
)

HOBBY = Hobby(id=1, name="Gardening")
