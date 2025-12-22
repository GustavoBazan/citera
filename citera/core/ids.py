"""Project id helpers."""

from __future__ import annotations

from pathlib import Path
from secrets import choice, randbelow

from .constants import ADJECTIVES, NOUNS


def generate_project_id(stage_dir: Path) -> str:
    """Create a unique adjective-noun ID for the stage directory."""
    for _ in range(1000):
        adjective = choice(ADJECTIVES)
        noun = choice(NOUNS)
        number = randbelow(9000) + 1000
        candidate = f"{adjective}{noun}{number}"
        if not (stage_dir / candidate).exists():
            return candidate
    raise RuntimeError("Unable to generate unique project id.")
