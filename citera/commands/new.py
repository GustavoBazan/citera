"""Handler for `citera new`."""

from __future__ import annotations

import sys
from pathlib import Path

from ..core.constants import LANG_STARTERS, STAGE_DIRS
from ..core.ids import generate_project_id
from ..core.metadata import write_project_metadata
from ..core.paths import base_projects_path, ensure_base_structure


def _create_starter_file(project_path: Path, lang: str | None) -> None:
    if not lang:
        return
    starter = LANG_STARTERS.get(lang.lower())
    if not starter:
        return
    filename, content = starter
    (project_path / filename).write_text(content, encoding="utf-8")


def handle_new(args: object) -> int:
    """Create a new project folder and metadata."""
    base_path = base_projects_path(getattr(args, "path", None))
    ensure_base_structure(base_path)
    stage_dir = base_path / STAGE_DIRS[args.type]

    project_id = args.name or generate_project_id(stage_dir)
    project_path = stage_dir / project_id
    if project_path.exists():
        print(
            f"Refusing to overwrite existing folder: {project_path}",
            file=sys.stderr,
        )
        return 1

    project_path.mkdir(parents=False)
    write_project_metadata(project_path, project_id, args.type)
    _create_starter_file(project_path, args.lang)
    print(project_path.resolve())
    return 0
