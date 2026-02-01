"""
Transcript management commands for Friday Chat.

Commands:
- /sessions - List all stored sessions
- /transcript - Show transcript for a session
- /export - Export session to file
- /replay - Replay a transcript
"""

import asyncio
from typing import TYPE_CHECKING

from friday_cli import arg

if TYPE_CHECKING:
    from ..session import MemoryChatSession


def register_transcript_commands(registry, session: "MemoryChatSession") -> None:
    """Register transcript management commands with the registry."""

    registry.register(
        "sessions",
        lambda ctx: asyncio.create_task(ctx.cmd_sessions()),
        description="List all stored transcript sessions",
        category="transcript",
    )

    registry.register(
        "transcript",
        lambda ctx, session_id=None, **kwargs: asyncio.create_task(ctx.cmd_transcript(session_id)),
        arguments=[
            arg("session_id", required=False, description="Session ID to view (default: current session)"),
        ],
        description="Show transcript for current or specified session. Use 'export' to export DB.",
        category="transcript",
    )

    registry.register(
        "export",
        lambda ctx, format="markdown", **kwargs: asyncio.create_task(ctx.cmd_export(format)),
        arguments=[
            arg("format", required=False, default="markdown",
                description="Export format", choices=["csv", "jsonl", "markdown", "training"]),
        ],
        description="Export current session transcript to ./exports directory",
        category="transcript",
    )

    registry.register(
        "replay",
        lambda ctx, csv_path=None, delay="0", **kwargs: asyncio.create_task(
            ctx.cmd_replay(csv_path, delay)
        ),
        arguments=[
            arg("csv_path", required=True, description="Path to exported CSV transcript file"),
            arg("delay", required=False, default="0", description="Seconds to wait between turns"),
        ],
        description="Replay a transcript CSV through Friday (resets memory first)",
        category="testing",
    )
