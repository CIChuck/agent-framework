"""Session commands for FridayV2."""

from __future__ import annotations

from friday_chat.commands.contracts import (
    CommandContext,
    CommandMetadata,
    CommandResult,
    CommandUiEffect,
)


async def cls_handler(
    _context: CommandContext,
    _args: tuple[str, ...],
    _metadata: CommandMetadata,
) -> CommandResult:
    """Request terminal clearing through the app-owned display boundary."""
    return CommandResult(output="", ui_effects=(CommandUiEffect.CLEAR_SCREEN,))


__all__ = ["cls_handler"]
