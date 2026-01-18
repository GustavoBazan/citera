"""Load .env configuration for Citera."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


def _candidate_env_paths() -> list[Path]:
    paths: list[Path] = []
    override = os.environ.get("CITERA_ENV_PATH")
    if override:
        paths.append(Path(override).expanduser())
    paths.append(Path.home() / ".config" / "citera" / ".env")
    paths.append(Path.cwd() / ".env")
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
