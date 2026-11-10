"""Memory and context commands for FridayV2."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from friday_chat.commands.contracts import (
    CommandContext,
    CommandMetadata,
    CommandResult,
)


async def memory_handler(
    context: CommandContext,
    _args: tuple[str, ...],
    _metadata: CommandMetadata,
) -> CommandResult:
    from friday_chat.commands.memory_queries import invoke_memory_query

    return await invoke_memory_query("memory", _args, context)


async def insights_handler(
    context: CommandContext,
    _args: tuple[str, ...],
    _metadata: CommandMetadata,
) -> CommandResult:
    from friday_chat.commands.memory_queries import invoke_memory_query

    return await invoke_memory_query("insights", _args, context)


async def summaries_handler(
    context: CommandContext,
    _args: tuple[str, ...],
    _metadata: CommandMetadata,
) -> CommandResult:
    from friday_chat.commands.memory_queries import invoke_memory_query

    return await invoke_memory_query("summaries", _args, context)


async def meta_handler(
    context: CommandContext,
    _args: tuple[str, ...],
    _metadata: CommandMetadata,
) -> CommandResult:
    from friday_chat.commands.memory_queries import invoke_memory_query

    return await invoke_memory_query("meta", _args, context)


def record_value(record: Mapping[str, Any], *keys: str) -> str:
    """Return the first non-null record value for shared legacy formatting."""
    for key in keys:
        value = record.get(key)
        if value is not None:
            return str(value)
    return ""


def preview_text(text: str, *, limit: int = 160) -> str:
    """Normalize and bound record text for shared legacy formatting."""
    normalized = " ".join(
        "".join(character if character.isprintable() else " " for character in text)
        .split()
    )
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."


__all__ = [
    "insights_handler",
    "memory_handler",
    "meta_handler",
    "preview_text",
    "record_value",
    "summaries_handler",
]
