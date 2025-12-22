"""Handler for `citera set`."""

from __future__ import annotations

import sys

from ..config import set_config_value

VALID_KEYS = {"llm", "llm_key", "llm_model"}
VALID_LLMS = {"openai", "gemini"}


def handle_set(args: object) -> int:
    """Persist a config key/value pair."""
    raw_key = str(getattr(args, "key", "")).strip()
    key = raw_key.lower().replace("-", "_")
    value = str(getattr(args, "value", "")).strip()
    if key not in VALID_KEYS:
        print(f"Unsupported config key: {key}", file=sys.stderr)
        return 1
    if key == "llm":
        value = value.lower()
        if value not in VALID_LLMS:
            print("Invalid llm provider. Use: openai or gemini.", file=sys.stderr)
            return 1
    if key == "llm_key" and not value:
        print("llm_key cannot be empty.", file=sys.stderr)
        return 1
    set_config_value(key, value)
    print(f"✓ {key} updated.")
    return 0
