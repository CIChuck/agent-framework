"""Tool commands for FridayV2."""

from __future__ import annotations

from friday_chat.commands.contracts import (
    CommandContext,
)
from friday_chat.tools.schemas import ToolDefinition


def list_runtime_tools(context: CommandContext) -> list[ToolDefinition]:
    """Return the currently registered runtime tool definitions."""
    if context.runtime is None:
        return []
    return list(context.runtime.tools.list_tools())


__all__ = ["list_runtime_tools"]
