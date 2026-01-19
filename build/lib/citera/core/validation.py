"""Validation helpers for AI metadata payloads."""

from __future__ import annotations

from .constants import CATEGORY_CHOICES
from .metadata import normalize_category

SUPPORTED_CATEGORIES = set(CATEGORY_CHOICES.values())


def validate_ai_payload(payload: dict) -> dict | None:
    """Validate the metadata schema and normalize fields."""
    payload = _normalize_keys(payload)
    required = {"name", "description", "tags", "tech", "category"}
    if not required.issubset(payload):
        return None
    if not isinstance(payload["name"], str) or not payload["name"].strip():
        return None
    if not isinstance(payload["description"], str) or not payload["description"].strip():
        return None
    if not isinstance(payload["tags"], list) or not all(
        isinstance(tag, str) for tag in payload["tags"]
    ):
        return None
    if not isinstance(payload["tech"], list) or not all(
        isinstance(item, str) for item in payload["tech"]
    ):
        return None

    normalized_category = normalize_category(payload["category"])
    if not normalized_category or normalized_category not in SUPPORTED_CATEGORIES:
        return None

    payload["tags"] = [tag.strip().lower() for tag in payload["tags"] if tag.strip()]
    payload["tech"] = [item.strip() for item in payload["tech"] if item.strip()]
    payload["category"] = normalized_category
    return payload


def _normalize_keys(payload: dict) -> dict:
    """Accept common alias keys from AI output."""
    normalized = dict(payload)
    if "name" not in normalized and "project_name" in normalized:
        normalized["name"] = normalized["project_name"]
    if "tech" not in normalized and "tech_stack" in normalized:
        normalized["tech"] = normalized["tech_stack"]
    return normalized
