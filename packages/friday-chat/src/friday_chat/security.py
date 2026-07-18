"""Security command and sanitization integration for FridayV2."""

from __future__ import annotations

from dataclasses import dataclass

SECURITY_PATTERNS: dict[str, tuple[str, ...]] = {
    "instruction": ("ignore previous", "system prompt", "developer message"),
    "delimiter": ("</instructions>", "```system", "<!--"),
    "jailbreak": ("jailbreak", "do anything now", "dan mode"),
    "exfil": ("api key", "secret", "token"),
}


@dataclass(frozen=True)
class SanitizationResult:
    """Result of one deterministic sanitization pass."""

    detected: bool
    patterns_seen: tuple[str, ...]
    sanitized: str


def sanitize_payload(
    payload: str,
    *,
    wrapping_enabled: bool = True,
    marker_style: str = "xml",
) -> SanitizationResult:
    """Detect and sanitize simple prompt-injection payloads."""
    lowered = payload.lower()
    patterns_seen = tuple(
        name
        for name, needles in SECURITY_PATTERNS.items()
        if any(needle in lowered for needle in needles)
    )
    sanitized = payload.replace("<", "&lt;").replace(">", "&gt;")
    if wrapping_enabled and patterns_seen:
        if marker_style == "markdown":
            sanitized = f"```untrusted\n{sanitized}\n```"
        else:
            sanitized = f"<untrusted>{sanitized}</untrusted>"
    return SanitizationResult(
        detected=bool(patterns_seen),
        patterns_seen=patterns_seen,
        sanitized=sanitized,
    )


def validate_security_update(kind: str, value: str) -> None:
    """Validate runtime security config update values."""
    if kind == "sensitivity" and value not in {"low", "medium", "high"}:
        raise ValueError("Sensitivity must be low, medium, or high.")
    if kind == "action" and value not in {"allow", "sanitize", "block"}:
        raise ValueError("Action must be allow, sanitize, or block.")
    if kind == "wrapping" and value not in {"xml", "markdown", "off"}:
        raise ValueError("Wrapping must be xml, markdown, or off.")
