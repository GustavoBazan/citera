"""Command-line interface for Citera."""

from __future__ import annotations

import argparse
from typing import Iterable

from . import __version__
from .commands.describe import handle_describe
from .commands.new import handle_new
from .commands.promote import handle_promote
from .commands.set import handle_set
from .core.constants import stage_choices, stage_label


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level CLI parser."""
    parser = argparse.ArgumentParser(
        prog="citera",
        description=(
            "Start, promote, and organize projects with a single CLI."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"citera {__version__}",
        help="Show the version and exit.",
    )
    parser.add_argument(
        "--flags",
        action="store_true",
        help="Print supported flags and subcommands.",
    )

    subparsers = parser.add_subparsers(dest="command")
    new_parser = subparsers.add_parser("new", help="Create a new project.")
    new_parser.add_argument(
        "--type",
        choices=stage_choices(include_archive=False, include_roles=True),
        default=stage_label("playground"),
        help="Stage for the new project.",
    )
    new_parser.add_argument(
        "--lang",
        help="Optional language starter (python, js, rust).",
    )
    new_parser.add_argument(
        "--name",
        help="Override the generated project id.",
    )

    promote_parser = subparsers.add_parser("promote", help="Promote a project stage.")
    promote_parser.add_argument(
        "--stage",
        choices=stage_choices(include_archive=False, include_roles=True),
        help="Target stage for promotion.",
    )
    promote_parser.add_argument(
        "--name",
        help="Override AI-generated project name.",
    )
    promote_parser.add_argument(
        "--no-github",
        action="store_true",
        help="Disable GitHub repo creation.",
    )
    promote_parser.add_argument(
        "--git",
        action="store_true",
        help="Initialize git if not already.",
    )
    promote_parser.add_argument(
        "--obsidian",
        action="store_true",
        help="Generate an Obsidian note.",
    )
    promote_parser.add_argument(
        "--archive",
        action="store_true",
        help="Archive the project.",
    )
    promote_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without making changes.",
    )
    promote_parser.add_argument(
        "--path",
        help="Path to the project directory (defaults to cwd).",
    )
    promote_parser.add_argument(
        "--id",
        help="Project id to locate within the projects directory.",
    )

    describe_parser = subparsers.add_parser("describe", help="Generate metadata for a project.")
    describe_parser.add_argument(
        "--path",
        help="Path to the project directory (defaults to cwd).",
    )
    describe_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing metadata fields.",
    )
    describe_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print metadata without writing.",
    )
    set_parser = subparsers.add_parser("set", help="Update config values.")
    set_parser.add_argument("key", help="Config key to set.")
    set_parser.add_argument("value", help="Config value.")

    subparsers.add_parser("list", help="List projects by stage or tag.")
    subparsers.add_parser("archive", help="Archive a project.")
    return parser


def _print_flags(parser: argparse.ArgumentParser) -> None:
    """Print available global flags and commands."""
    print("Global flags:")
    for action in parser._actions:
        if not action.option_strings:
            continue
        options = ", ".join(action.option_strings)
        print(f"  {options:<18} {action.help or ''}")
    print("\nCommands:")
    subparsers = next(
        (a for a in parser._actions if isinstance(a, argparse._SubParsersAction)),
        None,
    )
    if not subparsers:
        return
    for name, subparser in sorted(subparsers.choices.items()):
        print(f"  {name:<10} {subparser.description or subparser.format_help().splitlines()[0]}")


def _handle_command(args: argparse.Namespace) -> int:
    """Dispatch to the selected command handler."""
    if args.command == "new":
        return handle_new(args)
    if args.command == "promote":
        return handle_promote(args)
    if args.command == "describe":
        return handle_describe(args)
    if args.command == "set":
        return handle_set(args)
    if args.command is None:
        return 0
    print(
        "Citera is initialized. Command dispatch is not implemented yet.\n"
        f"Received command: {args.command}"
    )
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    parsed_args = parser.parse_args(argv)

    if parsed_args.flags:
        _print_flags(parser)
        return 0

    if parsed_args.command is None:
        parser.print_help()
        return 0

    return _handle_command(parsed_args)
