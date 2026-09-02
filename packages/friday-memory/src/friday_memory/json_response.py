"""Helpers for parsing structured JSON returned by LLMs."""

from __future__ import annotations

import json
import re
from typing import Any

_REASONING_BLOCK_PATTERN = re.compile(
    r"(?is)<(think|thinking|reasoning|analysis)\b[^>]*>.*?</\1>"
)


def strip_llm_reasoning(content: str) -> str:
    """Remove common inline reasoning blocks before structured-output parsing."""
    stripped = _REASONING_BLOCK_PATTERN.sub("", content)
    stripped = re.sub(
        r"(?is)^\s*(?:thinking|reasoning|analysis)\s*:\s*.*?(?=\{)",
        "",
        stripped,
    )
    return stripped.strip()


def parse_json_object_from_text(content: str | None) -> dict[str, Any] | None:
    """Parse the first valid JSON object from noisy LLM response text."""
    if not content:
        return None

    candidates = _json_text_candidates(strip_llm_reasoning(content))
    for candidate in candidates:
        parsed = _parse_json_object(candidate)
        if parsed is not None:
            return parsed
    return None


def json_response_text(response: Any) -> str:
    """Return final response text without exposing model reasoning."""
    content = getattr(response, "content", None) or ""
    return content


def json_parse_warning_detail(
    source: str,
    content: str | None,
    *,
    reasoning_content: str | None = None,
) -> str:
    """Return a concise warning payload for failed LLM JSON parsing."""
    raw = content or ""
    reasoning = reasoning_content or ""
    parse_source = raw if raw.strip() else reasoning
    sanitized = strip_llm_reasoning(parse_source)
    preview = (
        "<content empty; reasoning_content present>"
        if not raw.strip() and reasoning
        else _preview_text(sanitized or raw)
    )
    return (
        f"Could not parse JSON from {source} response "
        f"(raw_chars={len(raw)}, reasoning_chars={len(reasoning)}, "
        f"sanitized_chars={len(sanitized)}, "
        f"preview={preview})"
    )


def _json_text_candidates(content: str) -> list[str]:
    candidates = [content]
    candidates.extend(
        match.group(1)
        for match in re.finditer(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
    )
    candidates.extend(_raw_json_object_candidates(content))
    fixed = re.sub(r",\s*([}\]])", r"\1", content)
    if fixed != content:
        candidates.append(fixed)
        candidates.extend(_raw_json_object_candidates(fixed))
    return candidates


def _raw_json_object_candidates(content: str) -> list[str]:
    decoder = json.JSONDecoder()
    candidates: list[str] = []
    for index, char in enumerate(content):
        if char != "{":
            continue
        try:
            value, end = decoder.raw_decode(content[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            candidates.append(content[index : index + end])
    return candidates


def _parse_json_object(content: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _preview_text(content: str, limit: int = 200) -> str:
    preview = " ".join(content.split())
    if len(preview) > limit:
        preview = f"{preview[: limit - 3]}..."
    return repr(preview)
