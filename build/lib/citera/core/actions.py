"""Side-effect helpers (git, obsidian, process)."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


def slugify_repo_name(name: str) -> str:
    """Convert a human name into a URL-safe repo slug."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or "citera-project"


def run_command(cmd: list[str], cwd: Path | None, dry_run: bool) -> None:
    """Run a command unless dry-run is enabled."""
    if dry_run:
        return
    subprocess.run(cmd, cwd=cwd, check=True)


def create_obsidian_note(project_path: Path, project_id: str, dry_run: bool) -> None:
    """Create a minimal Obsidian note in the project folder."""
    note_path = project_path / "obsidian.md"
    if dry_run:
        return
    note_path.write_text(
        f"---\nproject: {project_id}\n---\n\n# {project_id}\n",
        encoding="utf-8",
    )
