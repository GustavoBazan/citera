"""Shared constants for Citera."""

from __future__ import annotations

from functools import lru_cache

from .env import get_env_value

DEFAULT_STAGE_ROLES = ("playground", "incubator", "product", "tool", "archive")

DEFAULT_STAGE_NAMES = {
    "playground": "playground",
    "incubator": "incubator",
    "product": "product",
    "tool": "tool",
    "archive": "archive",
}

DEFAULT_STAGE_DIRS = {
    "playground": "playground",
    "incubator": "incubator",
    "product": "products",
    "tool": "tools",
    "archive": "archives",
}

STAGE_DIRS = dict(DEFAULT_STAGE_DIRS)

CATEGORY_CHOICES = {
    "games": "Games",
    "libraries": "Libraries",
    "clis": "CLIs",
    "cli": "CLIs",
    "web": "Web",
    "ai": "AI",
    "tools": "Tools",
    "tool": "Tools",
    "other": "Other",
}

ADJECTIVES = [
    "Agile",
    "Bright",
    "Calm",
    "Daring",
    "Eager",
    "Fuzzy",
    "Gentle",
    "Happy",
    "Jolly",
    "Lively",
    "Mighty",
    "Nimble",
    "Quick",
    "Radiant",
    "Sunny",
    "Swift",
    "Witty",
]

NOUNS = [
    "Fox",
    "Llama",
    "Otter",
    "Panda",
    "Rocket",
    "River",
    "Comet",
    "Harbor",
    "Maple",
    "Nimbus",
    "Quartz",
    "Signal",
    "Sprout",
    "Summit",
    "Vector",
]

LANG_STARTERS = {
    "python": ("main.py", "print(\"Hello from citera\")\n"),
    "js": ("main.js", "console.log(\"Hello from citera\");\n"),
    "javascript": ("main.js", "console.log(\"Hello from citera\");\n"),
    "rust": ("main.rs", "fn main() {\n    println!(\"Hello from citera\");\n}\n"),
}


@lru_cache
def stage_names() -> dict[str, str]:
    """Return configured stage labels by role."""
    names = dict(DEFAULT_STAGE_NAMES)
    for role in DEFAULT_STAGE_ROLES:
        value = get_env_value(f"CITERA_STAGE_{role.upper()}")
        if value:
            names[role] = value.strip()
    return names


@lru_cache
def stage_dirs() -> dict[str, str]:
    """Return configured stage directories by role."""
    dirs = dict(DEFAULT_STAGE_DIRS)
    for role in DEFAULT_STAGE_ROLES:
        value = get_env_value(f"CITERA_STAGE_DIR_{role.upper()}")
        if value:
            dirs[role] = value.strip()
    return dirs


def stage_label(role: str) -> str:
    return stage_names()[role]


def stage_dir(role: str) -> str:
    return stage_dirs()[role]


def stage_roles(include_archive: bool = False) -> list[str]:
    roles = list(DEFAULT_STAGE_ROLES)
    if not include_archive:
        roles = [role for role in roles if role != "archive"]
    return roles


def stage_role_from_label(label: str) -> str | None:
    if not label:
        return None
    normalized = label.strip().lower()
    if normalized in DEFAULT_STAGE_ROLES:
        return normalized
    for role, name in stage_names().items():
        if normalized == name.strip().lower():
            return role
    return None


def stage_choices(include_archive: bool = False, include_roles: bool = True) -> list[str]:
    roles = stage_roles(include_archive=include_archive)
    names = stage_names()
    choices = [names[role] for role in roles]
    if include_roles:
        choices.extend(roles)
    seen: set[str] = set()
    unique: list[str] = []
    for choice in choices:
        if choice not in seen:
            unique.append(choice)
            seen.add(choice)
    return unique
