"""
Tool management commands for Friday Chat.

Commands:
- /tools - List available tools
- /run-tool - Execute a tool
- /inject-tools - Inject tools into context
- /clear-tools - Clear injected tools
- /recommend-tools - Test tool recommendations
- /tool-budget - Show tool token budget
"""

import asyncio
from typing import TYPE_CHECKING

from friday_cli import arg

if TYPE_CHECKING:
    from ..session import MemoryChatSession


def register_tools_commands(registry, session: "MemoryChatSession") -> None:
    """Register tool management commands with the registry."""

    registry.register(
        "tools",
        lambda ctx, category=None, **kwargs: ctx.cmd_tools(category),
        arguments=[
            arg(
                "category",
                required=False,
                description="Filter by tool category (e.g., utility, filesystem)",
            ),
        ],
        description="List available tools, optionally filtered by category",
        category="tools",
    )

    registry.register(
        "run-tool",
        lambda ctx, name="", json="", **kwargs: asyncio.create_task(
            ctx.cmd_run_tool(f"{name} {json}".strip())
        ),
        arguments=[
            arg("name", required=True, description="Name of the tool to execute"),
            arg("json", required=False, description="JSON parameters for the tool"),
        ],
        description="Execute a tool with optional JSON parameters",
        category="tools",
    )

    registry.register(
        "inject-tools",
        lambda ctx, names="", **kwargs: ctx.cmd_inject_tools(names),
        arguments=[
            arg(
                "names",
                required=True,
                description="Comma-separated list of tool names to inject",
            ),
        ],
        description="Inject tools into context for testing",
        category="tools",
    )

    registry.register(
        "clear-tools",
        lambda ctx: ctx.cmd_clear_tools(),
        description="Clear all injected tools from context",
        category="tools",
    )

    registry.register(
        "recommend-tools",
        lambda ctx, query="", **kwargs: ctx.cmd_recommend_tools(query),
        arguments=[
            arg(
                "query",
                required=True,
                description="Query to get tool recommendations for",
            ),
        ],
        description="Test tool recommendations for a query",
        category="tools",
    )

    registry.register(
        "tool-budget",
        lambda ctx: ctx.cmd_tool_budget(),
        description="Show tool token budget information",
        category="tools",
    )
