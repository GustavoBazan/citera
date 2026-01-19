"""Prompt templates for AI metadata generation."""

from __future__ import annotations

import json

SYSTEM_PROMPT = (
    "You are an assistant that generates structured metadata for software projects. "
    "Your output must be valid JSON. Do not guess or hallucinate technologies. "
    "Use file names and code snippets to infer purpose and behavior. "
    "Avoid generic descriptions and avoid mentioning project stage. "
    "Tags must be lowercase. Category must be one of: "
    "Games, CLIs, Libraries, AI, Web, Tools, Other."
)

USER_PROMPT_TEMPLATE = (
    "Context:\n{context}\n\n"
    "Generate:\n"
    "* project name (kebab-case)\n"
    "* 1-paragraph description focused on functionality and purpose\n"
    "* tags (3-6)\n"
    "* tech stack\n"
    "* category\n"
    "Return as JSON only with keys: name, description, tags, tech, category."
)


def build_prompts(context: dict) -> tuple[str, str]:
    """Create system and user prompts from context."""
    serialized = json.dumps(context, indent=2)
    return SYSTEM_PROMPT, USER_PROMPT_TEMPLATE.format(context=serialized)
