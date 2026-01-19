"""Metadata parsing and AI stub helpers."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from .constants import CATEGORY_CHOICES


def normalize_category(raw: str | None) -> str | None:
    """Normalize AI category to the canonical title-case buckets."""
    if not raw:
        return None
    key = raw.strip().lower()
    if key in CATEGORY_CHOICES:
        return CATEGORY_CHOICES[key]
    candidate = raw.strip().title()
    if candidate.lower() in CATEGORY_CHOICES:
        return CATEGORY_CHOICES[candidate.lower()]
    return None


def project_name_from_id(project_id: str) -> str:
    """Derive a human-ish name from an AdjectiveNoun ID."""
    parts = re.findall(r"[A-Z][a-z]+|[A-Z]+(?![a-z])", project_id)
    if not parts:
        return project_id
    return " ".join(parts)


def generate_ai_metadata_stub(project_id: str) -> dict:
    """Return mock AI metadata until the real model is wired up."""
    name = project_name_from_id(project_id)
    return {
        "name": name,
        "description": f"{name} is ready for its next stage.",
        "tags": ["citera", "project"],
        "category": "Tools",
    }


def parse_project_metadata(project_yaml: Path) -> dict:
    """Parse the project.yaml file into a dict."""
    data: dict[str, object] = {}
    section: str | None = None
    for line in project_yaml.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        if re.match(r"^[a-zA-Z_]+:\s*$", line):
            section = line.strip().rstrip(":")
            data[section] = {}
            continue
        if line.startswith("  ") and section:
            key, value = [part.strip() for part in line.strip().split(":", 1)]
            data[section][key] = _parse_scalar(value)
            continue
        if ":" in line:
            key, value = [part.strip() for part in line.split(":", 1)]
            data[key] = _parse_scalar(value)
    return data


def _parse_scalar(value: str) -> object:
    if value in ("null", ""):
        return None
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip("'\"") for item in inner.split(",")]
    return value


def _serialize_list(values: list[str]) -> str:
    if not values:
        return "[]"
    joined = ", ".join(values)
    return f"[{joined}]"


def write_project_metadata(project_path: Path, project_id: str, stage: str) -> None:
    """Write the initial project.yaml for a new project."""
    created_at = datetime.now(timezone.utc).isoformat()
    content = (
        f"id: {project_id}\n"
        f"stage: {stage}\n"
        "name: null\n"
        "description: null\n"
        "tags: []\n"
        "tech: []\n"
        f"created_at: {created_at}\n"
        "git:\n"
        "  enabled: false\n"
        "obsidian:\n"
        "  enabled: false\n"
    )
    (project_path / "project.yaml").write_text(content, encoding="utf-8")


def write_updated_metadata(project_yaml: Path, metadata: dict) -> None:
    """Write updated metadata after promotion."""
    content = (
        f"id: {metadata['id']}\n"
        f"stage: {metadata['stage']}\n"
        f"name: {metadata['name'] if metadata['name'] is not None else 'null'}\n"
        f"description: {metadata['description'] if metadata['description'] is not None else 'null'}\n"
        f"tags: {_serialize_list(metadata.get('tags', []))}\n"
        f"tech: {_serialize_list(metadata.get('tech', []))}\n"
        f"created_at: {metadata.get('created_at', '')}\n"
        f"category: {metadata.get('category', '')}\n"
        "git:\n"
        f"  enabled: {'true' if metadata.get('git_enabled') else 'false'}\n"
        f"  repo: {metadata.get('git_repo', '')}\n"
        "obsidian:\n"
        f"  enabled: {'true' if metadata.get('obsidian_enabled') else 'false'}\n"
    )
    project_yaml.write_text(content, encoding="utf-8")
