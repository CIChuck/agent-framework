"""
File commands for Friday Chat.

Commands:
- /read - Read file with smart format detection
- /ingest - Ingest file into vector memory
"""

import asyncio
from typing import TYPE_CHECKING

from friday_cli import arg

if TYPE_CHECKING:
    from ..session import MemoryChatSession


def register_file_commands(registry, session: "MemoryChatSession") -> None:
    """Register file commands with the registry."""

    registry.register(
        "read",
        lambda ctx, path="", **kwargs: asyncio.create_task(ctx.cmd_read_file(path)),
        arguments=[
            arg(
                "path",
                required=True,
                description="Path to file (supports txt, csv, pdf, docx, xlsx)",
            ),
        ],
        description="Read file with smart format detection",
        category="files",
    )

    registry.register(
        "ingest",
        lambda ctx, path="", **kwargs: asyncio.create_task(ctx.cmd_ingest_file(path)),
        arguments=[
            arg(
                "path",
                required=True,
                description="Path to file to ingest into vector memory",
            ),
        ],
        description="Ingest file content into vector memory",
        category="files",
    )
