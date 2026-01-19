"""Handler for `citera describe`."""

from __future__ import annotations

import sys
from ..ai.client import build_client
from ..core.context import collect_project_context
from ..core.metadata import parse_project_metadata, write_updated_metadata
from ..core.paths import resolve_project_path
from ..core.validation import validate_ai_payload
from ..config import load_config


def _merge_metadata(existing: dict, incoming: dict, force: bool) -> dict:
    def pick(key: str, default):
        current = existing.get(key, default)
        if force:
            return incoming.get(key, current)
        if current in (None, "", []):
            return incoming.get(key, current)
        return current

    git_section = existing.get("git", {}) if isinstance(existing.get("git"), dict) else {}
    obsidian_section = (
        existing.get("obsidian", {}) if isinstance(existing.get("obsidian"), dict) else {}
    )

    return {
        "id": existing.get("id", ""),
        "stage": existing.get("stage", ""),
        "name": pick("name", None),
        "description": pick("description", None),
        "tags": pick("tags", []),
        "tech": pick("tech", []),
        "created_at": existing.get("created_at", ""),
        "category": pick("category", ""),
        "git_enabled": _truthy(git_section.get("enabled")),
        "git_repo": git_section.get("repo", ""),
        "obsidian_enabled": _truthy(obsidian_section.get("enabled")),
    }


def _truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return False


def handle_describe(args: object) -> int:
    """Generate AI metadata for an existing project."""
    try:
        project_path = resolve_project_path(getattr(args, "path", None), None)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    project_yaml = project_path / "project.yaml"
    if not project_yaml.exists():
        print(f"Missing project.yaml in {project_path}", file=sys.stderr)
        return 1

    existing = parse_project_metadata(project_yaml)
    context = collect_project_context(project_path)
    config = load_config()
    try:
        client = build_client(config, context)
        payload = client.generate_metadata(context)
    except Exception as exc:
        print(f"AI request failed: {exc}", file=sys.stderr)
        return 1

    validated = validate_ai_payload(payload)
    if not validated:
        print("AI response missing required fields or types.", file=sys.stderr)
        return 1

    merged = _merge_metadata(existing, validated, getattr(args, "force", False))

    if getattr(args, "dry_run", False):
        print("✓ AI metadata generated.")
        print(f"✓ name: {merged['name']}")
        print(f"✓ tags: {merged['tags']}")
        print(f"✓ category: {merged['category']}")
        print("✓ project.yaml unchanged (dry-run).")
        return 0

    write_updated_metadata(project_yaml, merged)
    print("✓ AI metadata generated.")
    print(f"✓ name: {merged['name']}")
    print(f"✓ tags: {merged['tags']}")
    print(f"✓ category: {merged['category']}")
    print("✓ project.yaml updated.")
    return 0
