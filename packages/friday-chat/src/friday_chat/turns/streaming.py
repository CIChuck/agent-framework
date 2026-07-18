"""Streaming response helpers for FridayV2."""

from __future__ import annotations

from collections.abc import AsyncIterator


async def stream_text(text: str, *, chunk_size: int = 24) -> AsyncIterator[str]:
    """Yield deterministic text chunks for fake streaming tests."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")
    for index in range(0, len(text), chunk_size):
        yield text[index : index + chunk_size]
