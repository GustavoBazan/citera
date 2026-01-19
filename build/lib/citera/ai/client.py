"""LLM client interface and stub implementation."""

from __future__ import annotations

import sys

import json
from dataclasses import dataclass
from typing import Protocol


class LLMClient(Protocol):
    """Abstract interface for AI metadata generation."""

    def generate_metadata(self, context: dict) -> dict:
        raise NotImplementedError


@dataclass
class StubLLMClient:
    """Mock AI client that returns deterministic JSON."""

    def generate_metadata(self, context: dict) -> dict:
        base_name = context.get("languages", ["project"])[0].lower()
        payload = {
            "name": f"{base_name}-prototype",
            "description": "Auto-generated project description.",
            "tags": ["prototype", "citera", base_name],
            "tech": [lang.title() for lang in context.get("languages", [])],
            "category": "Tools",
        }
        return payload


@dataclass
class OpenAIClient:
    """OpenAI client using the official SDK."""

    api_key: str
    model: str = "gpt-4o-mini"
    max_retries: int = 1

    def generate_metadata(self, context: dict) -> dict:
        from .prompts import build_prompts

        system_prompt, user_prompt = build_prompts(context)
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Missing openai package. Install with: pip install openai") from exc

        def _request() -> dict:
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content or ""
            return _parse_json_payload(content)

        return _retry_request(_request, self.max_retries, "OpenAI")


@dataclass
class GeminiClient:
    """Gemini client using the official SDK."""

    api_key: str
    model: str = "gemini-1.5-flash"
    max_retries: int = 1

    def generate_metadata(self, context: dict) -> dict:
        from .prompts import build_prompts

        system_prompt, user_prompt = build_prompts(context)
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError(
                "Missing google-genai package. Install with: pip install google-genai"
            ) from exc

        def _request() -> dict:
            client = genai.Client(api_key=self.api_key)
            prompt = f"{system_prompt}\n\n{user_prompt}"
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            content = _extract_gemini_text(response)
            return _parse_json_payload(content)

        return _retry_request(_request, self.max_retries, "Gemini")


def _extract_gemini_text(response: object) -> str:
    text = getattr(response, "text", "") or ""
    if text:
        return text
    try:
        return response.candidates[0].content.parts[0].text
    except Exception:
        return ""


def _parse_json_payload(content: str) -> dict:
    cleaned = _strip_code_fence(content)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        snippet = content if len(content) <= 1000 else content[:1000] + "..."
        print("🌐 AI response (truncated):", file=sys.stderr)
        print(snippet, file=sys.stderr)
        raise RuntimeError("AI response was not valid JSON.") from exc


def _strip_code_fence(content: str) -> str:
    """Remove Markdown code fences if the model wraps JSON."""
    if "```" not in content:
        return content.strip()
    lines = content.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _retry_request(func, max_retries: int, label: str) -> dict:
    last_error: Exception | None = None
    for _ in range(max_retries + 1):
        try:
            return func()
        except Exception as exc:  # pragma: no cover - network errors are environment-specific
            last_error = exc
    raise RuntimeError(f"{label} request failed: {last_error}")


def build_client(config: dict, context: dict) -> LLMClient:
    """Return a configured LLM client based on config."""
    provider = str(config.get("llm", "")).lower()
    key = str(config.get("llm_key", "")).strip()
    if provider == "openai":
        if not key:
            raise RuntimeError("Missing llm_key for OpenAI.")
        model = str(config.get("openai_model") or config.get("llm_model") or "gpt-4o-mini")
        return OpenAIClient(api_key=key, model=model)
    if provider == "gemini":
        if not key:
            raise RuntimeError("Missing llm_key for Gemini.")
        model = str(config.get("gemini_model") or config.get("llm_model") or "gemini-1.5-flash")
        return GeminiClient(api_key=key, model=model)
    return StubLLMClient()
