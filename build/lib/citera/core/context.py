"""Project context scanning for AI prompts."""

from __future__ import annotations

import os
from pathlib import Path

from .metadata import parse_project_metadata

EXTENSION_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".html": "html",
    ".css": "css",
    ".json": "json",
}

SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules", ".mypy_cache"}
SKIP_FILES = {"project.yaml"}
SNIPPET_LIMIT = 8
SNIPPET_CHARS = 2000


def collect_project_context(project_path: Path) -> dict:
    """Build a shallow context summary without reading full code."""
    files: list[str] = []
    languages: set[str] = set()
    snippets: list[dict[str, str]] = []

    for root, dirnames, filenames in os.walk(project_path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            if len(files) >= 300:
                break
            if filename in SKIP_FILES:
                continue
            path = Path(root) / filename
            relative = str(path.relative_to(project_path))
            files.append(relative)
            ext = path.suffix.lower()
            language = EXTENSION_LANGUAGE.get(ext)
            if language:
                languages.add(language)
            if len(snippets) < SNIPPET_LIMIT and ext in EXTENSION_LANGUAGE:
                snippet = _read_snippet(path)
                if snippet:
                    snippets.append({"path": relative, "snippet": snippet})
        if len(files) >= 300:
            break

    notes = _read_notes(project_path)
    stage = _read_stage(project_path)
    return {
        "files": files,
        "languages": sorted(languages) or ["unknown"],
        "notes": notes,
        "stage": stage,
        "snippets": snippets,
    }


def _read_notes(project_path: Path) -> str | None:
    candidate = project_path / "playground.md"
    if not candidate.exists():
        return None
    content = candidate.read_text(encoding="utf-8", errors="ignore")
    return content.strip()[:1000] if content else None


def _read_snippet(path: Path) -> str | None:
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    if not content.strip():
        return None
    return content.strip()[:SNIPPET_CHARS]


def _read_stage(project_path: Path) -> str:
    project_yaml = project_path / "project.yaml"
    if not project_yaml.exists():
        return "unknown"
    data = parse_project_metadata(project_yaml)
    return str(data.get("stage", "unknown"))
