"""Handler for `citera new`."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from ..core.constants import LANG_STARTERS, stage_dir, stage_label, stage_role_from_label
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


def _open_in_vscode(project_path: Path) -> None:
    code_path = shutil.which("code")
    if not code_path:
        print("VS Code 'code' command not found on PATH; skipping open.", file=sys.stderr)
        return
    try:
        subprocess.Popen([code_path, "."], cwd=project_path)
    except OSError as exc:
        print(f"Failed to launch VS Code: {exc}", file=sys.stderr)


def handle_new(args: object) -> int:
    """Create a new project folder and metadata."""
    base_path = base_projects_path()
    ensure_base_structure(base_path)
    stage_role = stage_role_from_label(str(args.type))
    if not stage_role or stage_role == "archive":
        print(f"Unsupported stage: {args.type}", file=sys.stderr)
        return 2
    stage_dir_path = base_path / stage_dir(stage_role)

    project_id = args.name or generate_project_id(stage_dir_path)
    project_path = stage_dir_path / project_id
    if project_path.exists():
        print(
            f"Refusing to overwrite existing folder: {project_path}",
            file=sys.stderr,
        )
        return 1

    project_path.mkdir(parents=False)
    write_project_metadata(project_path, project_id, stage_label(stage_role))
    _create_starter_file(project_path, args.lang)
    print(project_path.resolve())
    _open_in_vscode(project_path)
    return 0
