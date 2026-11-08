"""Session commands for FridayV2."""

from __future__ import annotations

from friday_chat.commands.contracts import (
    CommandContext,
    CommandMetadata,
    CommandResult,
)
from friday_chat.commands.pilot import invoke_pilot


async def cls_handler(
    _context: CommandContext,
    _args: tuple[str, ...],
    _metadata: CommandMetadata,
) -> CommandResult:
    """Request terminal clearing through the app-owned display boundary."""
    return await invoke_pilot("cls", _args)


__all__ = ["cls_handler"]
