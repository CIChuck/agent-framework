"""
Workflow commands for Friday Chat.

Commands:
- /workflow list - List available workflows
- /workflow run - Execute a workflow
- /workflow status - Show workflow status
- /workflow approve - Approve pending task
- /workflow skip - Skip pending task
"""

import asyncio
from typing import TYPE_CHECKING

from friday_cli import arg

if TYPE_CHECKING:
    from ..session import MemoryChatSession


def register_workflow_commands(registry, session: "MemoryChatSession") -> None:
    """Register workflow commands with the registry."""

    registry.register(
        "workflow",
        lambda ctx, subcommand="", args="", **kwargs: asyncio.create_task(
            ctx.cmd_workflow(subcommand, args)
        ),
        arguments=[
            arg(
                "subcommand", required=False, description="list|run|status|approve|skip"
            ),
            arg(
                "args",
                required=False,
                description="Additional arguments for subcommand",
            ),
        ],
        description="Manage workflows (list, run, status, approve, skip)",
        category="workflows",
    )
