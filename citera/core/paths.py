"""Filesystem helpers for locating projects."""

from __future__ import annotations

import os
from pathlib import Path

from .constants import stage_dirs
from ..config import load_config


def base_projects_path() -> Path:
    """Resolve the projects root from config/env/default."""
    config = load_config()
    config_root = str(config.get("root", "")).strip()
    if config_root:
        return Path(config_root).expanduser()
    env_path = os.environ.get("PROJECTS_DIRECTORY")
    if env_path:
        return Path(env_path).expanduser()
    return Path("~/Documents/Projects/").expanduser()


def ensure_base_structure(base_path: Path) -> None:
    """Create the base folder structure if missing."""
    base_path.mkdir(parents=True, exist_ok=True)
    for folder in stage_dirs().values():
        (base_path / folder).mkdir(parents=True, exist_ok=True)


def find_project_by_id(base_path: Path, project_id: str) -> Path | None:
    """Locate a project by ID across stages and categories."""
    candidates: list[Path] = []
    for folder in stage_dirs().values():
        stage_dir = base_path / folder
        direct = stage_dir / project_id
        if direct.exists():
            candidates.append(direct)
        if stage_dir.exists():
            for child in stage_dir.iterdir():
                if child.is_dir():
                    candidate = child / project_id
                    if candidate.exists():
                        candidates.append(candidate)
    if not candidates:
        return None
    if len(candidates) > 1:
        raise RuntimeError(f"Multiple projects found for id {project_id}.")
    return candidates[0]


def resolve_project_path(path: str | None, project_id: str | None) -> Path:
    """Resolve the current project path using path, id, or cwd."""
    if path:
        return Path(path).expanduser().resolve()
    if project_id:
        base_path = base_projects_path()
        ensure_base_structure(base_path)
        found = find_project_by_id(base_path, project_id)
        if not found:
            raise RuntimeError(f"Project id not found: {project_id}")
        return found.resolve()
    return Path.cwd().resolve()
