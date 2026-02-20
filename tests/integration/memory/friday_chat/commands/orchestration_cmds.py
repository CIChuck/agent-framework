"""
Agent orchestration commands for Friday Chat.

Commands:
- /switch - Switch to agent or show status
- /agents - List available agents
- /agent - Show agent info
- /delegate - Delegate task to agent
- /status - Show orchestrator status
"""

import asyncio
from typing import TYPE_CHECKING

from friday_cli import arg

if TYPE_CHECKING:
    from ..session import MemoryChatSession


def register_orchestration_commands(registry, session: "MemoryChatSession") -> None:
    """Register orchestration commands with the registry."""

    registry.register(
        "switch",
        lambda ctx, agent="", **kwargs: asyncio.create_task(ctx.cmd_switch(agent)),
        arguments=[
            arg(
                "agent",
                required=False,
                description="Agent name to switch to (omit to show status)",
            ),
        ],
        description="Switch to a different agent or show current agent status",
        category="orchestration",
    )

    registry.register(
        "agents",
        lambda ctx: ctx.cmd_agents(),
        description="List all available agents with their capabilities",
        category="orchestration",
    )

    registry.register(
        "agent",
        lambda ctx, name="", **kwargs: ctx.cmd_agent_info(name),
        arguments=[
            arg(
                "name",
                required=False,
                description="Agent name to get info for (omit for active agent)",
            ),
        ],
        description="Show detailed information about an agent",
        category="orchestration",
    )

    registry.register(
        "delegate",
        lambda ctx, agent="", task="", **kwargs: asyncio.create_task(
            ctx.cmd_delegate(agent, task)
        ),
        arguments=[
            arg("agent", required=True, description="Agent name to delegate to"),
            arg("task", required=True, description="Task description to delegate"),
        ],
        description="Delegate a task to another agent and return to current",
        category="orchestration",
    )

    registry.register(
        "status",
        lambda ctx: ctx.cmd_orchestrator_status(),
        description="Show orchestrator status (active agent, cache, message count)",
        category="orchestration",
    )
