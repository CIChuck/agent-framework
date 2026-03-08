# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Tests for Orca sanitization helper."""

from friday_speech.adapters.picovoice import _sanitize_for_orca


def test_sanitize_for_orca_filters_invalid_chars() -> None:
    valid = "abc ."
    text = "a*b c…"
    sanitized = _sanitize_for_orca(text, valid)
    assert "*" not in sanitized
    assert "…" not in sanitized
    assert sanitized.replace(" ", "").startswith("abc")
