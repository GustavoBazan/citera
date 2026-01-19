"""Handler for `citera archive`."""

from __future__ import annotations

from types import SimpleNamespace

from .promote import handle_promote


def handle_archive(args: object) -> int:
    """Archive a project using the promote flow."""
    archive_args = SimpleNamespace(
        archive=True,
        stage=None,
        name=None,
        no_github=True,
        git=False,
        obsidian=False,
        dry_run=getattr(args, "dry_run", False),
        path=getattr(args, "path", None),
        id=getattr(args, "id", None),
    )
    return handle_promote(archive_args)
