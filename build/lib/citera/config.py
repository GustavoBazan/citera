"""Configuration helpers for Citera."""

from __future__ import annotations

from pathlib import Path


def default_config_path() -> Path:
    return Path.home() / ".config" / "citera" / "config.yaml"


def load_config() -> dict:
    """Load a simple key/value config from disk."""
    path = default_config_path()
    if not path.exists():
        return {}
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        key, value = [part.strip() for part in stripped.split(":", 1)]
        data[key] = value
    return data


def save_config(data: dict) -> None:
    """Persist config to disk in a simple YAML format."""
    path = default_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}: {value}" for key, value in sorted(data.items())]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def set_config_value(key: str, value: str) -> None:
    """Update a single config key."""
    data = load_config()
    data[key] = value
    save_config(data)
