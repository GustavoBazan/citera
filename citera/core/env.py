"""Load .env configuration for Citera."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from ..config import load_config


def _candidate_env_paths() -> list[Path]:
    paths: list[Path] = []
    # Lowest precedence defaults first; later entries override earlier ones.
    package_root = Path(__file__).resolve().parents[2]
    paths.append(package_root / ".env")
    paths.append(Path.home() / ".config" / "citera" / ".env")
    config_root = str(load_config().get("root", "")).strip()
    if config_root:
        paths.append(Path(config_root).expanduser() / ".env")
    cwd = Path.cwd().resolve()
    # Load from nearest .env up the tree so project-local settings apply when run inside subfolders.
    parent_chain = list(reversed(cwd.parents)) + [cwd]
    for parent in parent_chain:
        paths.append(parent / ".env")
    override = os.environ.get("CITERA_ENV_PATH")
    if override:
        # Keep explicit override last so it wins over other sources.
        paths.append(Path(override).expanduser())
    return paths


def _load_env_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if key:
            data[key] = value
    return data


@lru_cache
def load_env() -> dict[str, str]:
    data: dict[str, str] = {}
    for path in _candidate_env_paths():
        if path.exists():
            data.update(_load_env_file(path))
    return data


def get_env_value(key: str) -> str | None:
    env_value = os.environ.get(key)
    if env_value is not None:
        return env_value
    return load_env().get(key)
