"""Static profile content. Pure data, no framework imports.

Everything here is already self-published on github.com/andi1984 and andi1984.dev.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class Profile:
    name: str
    handle: str
    role: str
    employer: str
    location: str
    bio: str
    website: str
    avatar_url: str
    coding_since: int


@dataclass(frozen=True, slots=True)
class Link:
    name: str
    url: str
    kind: Literal["profile", "site"]
    handle: str | None = None


@dataclass(frozen=True, slots=True)
class Fact:
    label: str
    value: str


@dataclass(frozen=True, slots=True)
class Project:
    id: str
    name: str
    tagline: str
    description: str
    homepage: str | None
    repository: str | None
    ai_assisted: bool
    category: str
    tech: tuple[str, ...]
    platforms: tuple[str, ...]
    license: str | None
    languages: tuple[str, ...]
    facts: tuple[Fact, ...]


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
    location="Saarbrücken, Germany",
    bio=(
        "Building for the web since 2012. React and TypeScript at the core, "
        "Python and FastAPI behind them, and LLM features that are useful in practice."
    ),
    website="https://andi1984.dev",
    avatar_url="https://andi1984.dev/ava.jpg",
    coding_since=2012,
)

LINKS: tuple[Link, ...] = (
    Link(name="website", url="https://andi1984.dev", kind="site"),
    Link(name="writing", url="https://andi1984.dev/writing", kind="site"),
    Link(name="rss", url="https://andi1984.dev/rss.xml", kind="site"),
    Link(name="cv", url="https://andi1984.github.io/CV/", kind="site"),
    Link(name="github", url="https://github.com/andi1984", kind="profile", handle="andi1984"),
    Link(
        name="linkedin",
        url="https://www.linkedin.com/in/andi1984",
        kind="profile",
        handle="andi1984",
    ),
    Link(
        name="mastodon",
        url="https://dibbelabb.es/@andi1984dev",
        kind="profile",
        handle="@andi1984dev@dibbelabb.es",
    ),
    Link(name="devto", url="https://dev.to/andi1984", kind="profile", handle="@andi1984"),
    Link(
        name="youtube",
        url="https://www.youtube.com/@andi1984dev",
        kind="profile",
        handle="@andi1984dev",
    ),
    Link(name="twitch", url="https://www.twitch.tv/andi1984", kind="profile", handle="andi1984"),
)

# List order is display order; every listed project is shown on andi1984.dev/portfolio.
PROJECTS: tuple[Project, ...] = (
    Project(
        id="ferrico",
        name="Ferrico",
        tagline="A home for the links I want to keep.",
        description=(
            "A local-first bookmark manager for collecting, organising and finding links "
            "again. Your library lives in a SQLite file on your machine, with folders, tags "
            "and fuzzy search. No account required; syncing through your own Google Drive "
            "is optional."
        ),
        homepage="https://viberfasend.github.io/ferrico_dot_app/",
        repository="https://github.com/viberfasend/ferrico_dot_app",
        ai_assisted=True,
        category="ProductivityApplication",
        tech=("Rust", "Tauri", "React", "TypeScript"),
        platforms=("macOS", "Linux", "Windows"),
        license="GPL-3.0-or-later",
        languages=(),
        facts=(
            Fact(label="Android", value="Read-only companion"),
            Fact(label="Storage", value="Local SQLite database"),
        ),
    ),
    Project(
        id="primico",
        name="Primico",
        tagline="Importance first, due date breaks ties.",
        description=(
            "A local-first todo app for Android and the desktop. Every list is ordered by "
            "importance, with due date only breaking ties, and every task is stored in a "
            "SQLite file on your device — no account, no analytics, no cloud unless you "
            "point sync at your own database. Quick-add parses a single line into priority, "
            "project, tags, dates and recurrence, in English and German."
        ),
        homepage="https://viberfasend.github.io/primico/",
        repository="https://github.com/viberfasend/primico",
        ai_assisted=True,
        category="ProductivityApplication",
        tech=("Kotlin", "Compose Multiplatform", "SQLDelight"),
        platforms=("Android", "Linux", "macOS", "Windows"),
        license="GPL-3.0-or-later",
        languages=("English", "German"),
        facts=(Fact(label="Sync", value="Optional, self-hosted (Neon)"),),
    ),
    Project(
        id="tinypng",
        name="TinyPNG for VS Code",
        tagline="Smaller images, without leaving the editor.",
        description=(
            "A VS Code extension I built before working with AI coding tools. Compress PNG "
            "and JPG assets through TinyPNG, right from the editor — one less interruption "
            "when preparing images for the web."
        ),
        homepage="https://marketplace.visualstudio.com/items?itemName=andi1984.tinypng",
        repository="https://github.com/andi1984/vscode-tinypng",
        ai_assisted=False,
        category="DeveloperApplication",
        tech=("TypeScript", "VS Code API"),
        platforms=("VS Code",),
        license=None,
        languages=(),
        facts=(
            Fact(label="Formats", value="PNG, JPG"),
            Fact(label="Source", value="Open source"),
        ),
    ),
    Project(
        id="mastodon-news-bot",
        name="Mastodon News Bot",
        tagline="Saarland's regional news, gathered into stories.",
        description=(
            "A Mastodon bot that collects news from more than 15 regional RSS feeds, groups "
            "articles about the same event into one story and posts follow-ups as replies. "
            "It spots breaking news when several sources report at once, and answers "
            "questions sent to it as mentions."
        ),
        homepage="https://dibbelabb.es/@saarlandnews",
        repository="https://github.com/andi1984/mastodon-news-bot",
        ai_assisted=True,
        category="SocialNetworkingApplication",
        tech=("TypeScript", "Node.js", "PostgreSQL (Supabase)", "Claude API"),
        platforms=("Mastodon",),
        license="GPL-3.0",
        languages=("German",),
        facts=(
            Fact(label="Live at", value="@saarlandnews@dibbelabb.es"),
            Fact(label="AI features", value="Story matching, polls, hashtags (optional)"),
        ),
    ),
    Project(
        id="kann-ich-lueften",
        name="Kann ich lüften?",
        tagline="Will opening the window actually help?",
        description=(
            "A small German-language web app for an everyday question. Enter the "
            "temperature and humidity indoors and outside to estimate whether airing the "
            "room will remove moisture. It compares absolute humidity and works offline "
            "once loaded."
        ),
        homepage="https://viberfasend.github.io/kann-ich-lueften/",
        repository="https://github.com/viberfasend/kann-ich-lueften",
        ai_assisted=True,
        category="UtilitiesApplication",
        tech=("TypeScript", "Lit", "Vite"),
        platforms=("Web",),
        license=None,
        languages=("German",),
        facts=(Fact(label="Runs in", value="Your browser, also offline"),),
    ),
)

NOW: tuple[NowItem, ...] = (
    NowItem(kind="building", text="Ferrico — an Android build and smarter duplicate detection."),
    NowItem(kind="learning", text="Enough Rust to stop fighting the borrow checker in public."),
    NowItem(kind="growing", text="Tomatoes, three kinds of mint, and one stubborn fig tree."),
)

HOBBY = Hobby(id=1, name="Gardening")
