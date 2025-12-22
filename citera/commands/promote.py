"""Handler for `citera promote`."""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from ..ai.client import build_client
from ..config import load_config
from ..core.actions import create_obsidian_note, run_command, slugify_repo_name
from ..core.context import collect_project_context
from ..core.constants import ARCHIVE_DIR, STAGE_DIRS
from ..core.metadata import (
    normalize_category,
    parse_project_metadata,
    write_updated_metadata,
)
from ..core.paths import base_projects_path, ensure_base_structure, resolve_project_path
from ..core.validation import validate_ai_payload


def _validate_stage_transition(current: str, target: str, archive: bool) -> None:
    if archive:
        return
    if current == "playground" and target != "incubator":
        raise RuntimeError("playground projects can only be promoted to incubator.")
    if current == "incubator" and target not in ("product", "tool"):
        raise RuntimeError("incubator projects can only be promoted to product or tool.")
    if current in ("product", "tool") and target != "archive":
        raise RuntimeError("product/tool projects can only be archived.")
    if current == "archive":
        raise RuntimeError("archive projects cannot be promoted.")


def _write_readme(
    project_path: Path,
    name: str | None,
    description: str | None,
    tags: list[str],
    tech: list[str],
    category: str | None,
    dry_run: bool,
) -> bool:
    """Create a simple README if one does not exist."""
    readme_path = project_path / "README.md"
    if readme_path.exists():
        return False
    title = name or project_path.name
    lines = [f"# {title}", ""]
    if description:
        lines.extend([description, ""])
    if category:
        lines.extend(["## Category", category, ""])
    if tags:
        lines.append("## Tags")
        lines.extend([f"- {tag}" for tag in tags])
        lines.append("")
    if tech:
        lines.append("## Tech")
        lines.extend([f"- {item}" for item in tech])
        lines.append("")
    content = "\n".join(lines).strip() + "\n"
    if dry_run:
        return True
    readme_path.write_text(content, encoding="utf-8")
    return True


def _git_has_commits(project_path: Path) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=project_path,
        capture_output=True,
    )
    return result.returncode == 0


def _git_has_changes(project_path: Path) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=project_path,
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def handle_promote(args: object) -> int:
    """Promote a project and update metadata."""
    if not args.archive and not args.stage:
        print("Missing required --stage (or use --archive).", file=sys.stderr)
        return 2

    try:
        project_path = resolve_project_path(getattr(args, "path", None), getattr(args, "id", None))
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    project_yaml = project_path / "project.yaml"
    if not project_yaml.exists():
        print(f"Missing project.yaml in {project_path}", file=sys.stderr)
        return 1

    existing = parse_project_metadata(project_yaml)
    project_id = str(existing.get("id", project_path.name))
    current_stage = str(existing.get("stage", "playground"))

    target_stage = "archive" if args.archive else args.stage
    try:
        _validate_stage_transition(current_stage, target_stage, args.archive)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    base_path = base_projects_path(None)
    ensure_base_structure(base_path)

    ai_metadata: dict | None = None
    category: str | None = None
    new_project_id = project_id

    if current_stage == "playground" and target_stage == "incubator":
        context = collect_project_context(project_path)
        config = load_config()
        try:
            client = build_client(config, context)
            ai_metadata = client.generate_metadata(context)
        except Exception as exc:
            print(f"AI request failed: {exc}", file=sys.stderr)
            return 1

        validated = validate_ai_payload(ai_metadata)
        if not validated:
            print("AI response missing required fields or types.", file=sys.stderr)
            return 1
        ai_metadata = validated
        category = ai_metadata["category"]
        name_source = args.name or ai_metadata["name"]
        new_project_id = slugify_repo_name(name_source)
    else:
        category = normalize_category(existing.get("category"))
        if not category:
            print("Missing category for promotion; run describe first.", file=sys.stderr)
            return 1

    if target_stage == "archive":
        stage_dir = base_path / ARCHIVE_DIR
    else:
        stage_dir = base_path / STAGE_DIRS[target_stage]

    destination = stage_dir / category / new_project_id
    if destination.exists():
        print(f"Destination already exists: {destination}", file=sys.stderr)
        return 1

    if ai_metadata:
        use_name = args.name or ai_metadata["name"]
        use_description = ai_metadata["description"]
        use_tags = ai_metadata["tags"]
        use_tech = ai_metadata["tech"]
        use_category = ai_metadata["category"]
    else:
        use_name = args.name or existing.get("name")
        use_description = existing.get("description")
        use_tags = existing.get("tags", [])
        use_tech = existing.get("tech", [])
        use_category = category

    git_enabled = not args.no_github or args.git
    github_enabled = not args.no_github
    repo_url = ""
    readme_created = False
    commit_created = False
    pushed = False

    if args.dry_run:
        print(f"Old path: {project_path}")
        print(f"New path: {destination}")
        print(f"Metadata changes: stage={target_stage}, name={use_name}, category={use_category}")
        print(f"Git: {'init' if git_enabled else 'skip'}")
        print(f"GitHub: {'create' if github_enabled else 'skip'}")
        if git_enabled:
            print("README: create if missing")
            print("Git commit: create initial commit")
        if github_enabled:
            print("Git push: push to origin")
        print(f"Obsidian: {'enabled' if args.obsidian else 'skip'}")
        return 0

    if git_enabled and not shutil.which("git"):
        print("git not found on PATH; cannot initialize git.", file=sys.stderr)
        return 1
    if github_enabled and not shutil.which("gh"):
        print(
            "GitHub CLI (gh) not found; re-run with --no-github or install gh.",
            file=sys.stderr,
        )
        return 1

    destination.parent.mkdir(parents=True, exist_ok=True)
    project_path.rename(destination)

    if git_enabled and not (destination / ".git").exists():
        run_command(["git", "init", "-b", "main"], cwd=destination, dry_run=args.dry_run)

    if github_enabled:
        repo_name = slugify_repo_name(use_name)
        run_command(
            [
                "gh",
                "repo",
                "create",
                repo_name,
                "--private",
                "--source",
                ".",
                "--remote",
                "origin",
                "--confirm",
            ],
            cwd=destination,
            dry_run=args.dry_run,
        )
        try:
            result = subprocess.run(
                ["gh", "repo", "view", "--json", "url", "-q", ".url"],
                cwd=destination,
                check=True,
                capture_output=True,
                text=True,
            )
            repo_url = result.stdout.strip()
        except subprocess.CalledProcessError:
            repo_url = ""

    updated = {
        "id": new_project_id,
        "stage": target_stage,
        "name": use_name,
        "description": use_description,
        "tags": use_tags,
        "tech": use_tech,
        "created_at": existing.get("created_at", datetime.now(timezone.utc).isoformat()),
        "category": use_category,
        "git_enabled": git_enabled,
        "git_repo": repo_url,
        "obsidian_enabled": args.obsidian,
    }
    write_updated_metadata(destination / "project.yaml", updated)

    readme_created = _write_readme(
        destination,
        use_name,
        use_description,
        use_tags or [],
        use_tech or [],
        use_category,
        args.dry_run,
    )

    if args.obsidian:
        create_obsidian_note(destination, new_project_id, args.dry_run)

    if git_enabled and _git_has_changes(destination):
        try:
            run_command(["git", "add", "-A"], cwd=destination, dry_run=args.dry_run)
            run_command(
                ["git", "commit", "-m", "Initial commit"],
                cwd=destination,
                dry_run=args.dry_run,
            )
            commit_created = True
        except subprocess.CalledProcessError:
            print(
                "Git commit failed. Configure user.name and user.email.",
                file=sys.stderr,
            )
            return 1

    if github_enabled and _git_has_commits(destination):
        try:
            run_command(["git", "push", "-u", "origin", "HEAD"], cwd=destination, dry_run=args.dry_run)
            pushed = True
        except subprocess.CalledProcessError:
            print("Git push failed. Check your credentials or remote.", file=sys.stderr)
            return 1

    print(f"✓ Project promoted to: {target_stage}")
    print(f"✓ Category: {use_category}")
    print(f"✓ New path: {destination}")
    if git_enabled:
        print("✓ Git initialized")
    if github_enabled:
        if repo_url:
            print(f"✓ GitHub repo created: {repo_url}")
        else:
            print("✓ GitHub repo created")
    if readme_created:
        print("✓ README.md created")
    if commit_created:
        print("✓ Initial commit created")
    if pushed:
        print("✓ Pushed to GitHub")
    if args.obsidian:
        print("✓ Obsidian note created")

    return 0
