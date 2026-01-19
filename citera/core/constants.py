"""Shared constants for Citera."""

from __future__ import annotations

from functools import lru_cache

CORE_STAGE_ROLES = ("sandbox", "develop", "product")
SPECIAL_STAGE_ROLES = ("resources", "archived")
STAGE_ROLES = CORE_STAGE_ROLES + SPECIAL_STAGE_ROLES

STAGE_NAMES = {
    "sandbox": "Sandbox",
    "develop": "Develop",
    "product": "Product",
    "resources": "Resources",
    "archived": "Archived",
}

STAGE_DIRS = {
    "sandbox": "1- Sandbox",
    "develop": "2- Develop",
    "product": "3- Products",
    "resources": "Resources",
    "archived": "Archived",
}

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
    return dict(STAGE_NAMES)


@lru_cache
def stage_dirs() -> dict[str, str]:
    """Return configured stage directories by role."""
    return dict(STAGE_DIRS)


def stage_label(role: str) -> str:
    return stage_names()[role]


def stage_dir(role: str) -> str:
    return stage_dirs()[role]


def stage_roles(include_archive: bool = False) -> list[str]:
    if include_archive:
        return list(STAGE_ROLES)
    return list(CORE_STAGE_ROLES)


def stage_role_from_label(label: str) -> str | None:
    if not label:
        return None
    normalized = label.strip().lower()
    if normalized in STAGE_ROLES:
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
