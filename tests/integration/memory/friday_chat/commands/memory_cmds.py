"""
Memory inspection commands for Friday Chat.

Commands:
- /history - Show conversation history
- /memory - Show memory statistics
- /context - Show context payload
- /prompt - Show formatted prompt
- /debug - Show debug info
- /debug-retrieval - Debug vector retrieval
- /prime - Load primed context
- /entities - List graph entities
- /facts - List all documents
- /insights - List insights
- /summaries - List summaries
- /meta - List meta insights
- /vars - Show scoped variables
- /set - Set a scoped variable
- /list-ingested - List ingested documents
"""

import asyncio
from typing import TYPE_CHECKING

from friday_cli import arg

if TYPE_CHECKING:
    from ..session import MemoryChatSession


def register_memory_commands(registry, session: "MemoryChatSession") -> None:
    """Register memory inspection commands with the registry."""

    registry.register(
        "history",
        lambda ctx: asyncio.create_task(ctx.cmd_history()),
        description="Show conversation history with timestamps and tool calls",
        category="memory",
    )

    registry.register(
        "memory",
        lambda ctx: ctx.cmd_memory(),
        description="Show memory statistics across all stores",
        category="memory",
    )

    registry.register(
        "context",
        lambda ctx, **kwargs: ctx.cmd_context(debug_mode="--debug" in str(kwargs)),
        arguments=[
            arg(
                "--debug",
                required=False,
                description="Show detailed token counts per section",
            ),
        ],
        description="Show assembled context payload that would be sent to LLM",
        category="memory",
    )

    registry.register(
        "prompt",
        lambda ctx: ctx.cmd_prompt(),
        description="Show full formatted prompt (complete, no truncation)",
        category="memory",
    )

    registry.register(
        "prime",
        lambda ctx: asyncio.create_task(ctx.cmd_prime()),
        description="Load and show primed context (works before first turn)",
        category="memory",
    )

    registry.register(
        "debug",
        lambda ctx: ctx.cmd_debug(),
        description="Show debug info from context assembly",
        category="memory",
    )

    registry.register(
        "entities",
        lambda ctx: asyncio.create_task(ctx.cmd_entities()),
        description="List graph entities and their relationships",
        category="memory",
    )

    registry.register(
        "facts",
        lambda ctx: asyncio.create_task(ctx.cmd_facts()),
        description="List all documents from vector store (insights + summaries)",
        category="memory",
    )

    registry.register(
        "insights",
        lambda ctx: asyncio.create_task(ctx.cmd_insights()),
        description="List only insights (type='insight') with structured metadata",
        category="memory",
    )

    registry.register(
        "summaries",
        lambda ctx: asyncio.create_task(ctx.cmd_summaries()),
        description="List only turn summaries (type='summary')",
        category="memory",
    )

    registry.register(
        "meta",
        lambda ctx: asyncio.create_task(ctx.cmd_meta_insights()),
        description="List meta insights from synthesis operations",
        category="memory",
    )

    registry.register(
        "vars",
        lambda ctx: ctx.cmd_vars(),
        description="Show all scoped variables (user:*, session:*, task:*)",
        category="memory",
    )

    registry.register(
        "set",
        lambda ctx, key="", value="", **kwargs: ctx.cmd_set(key, value),
        arguments=[
            arg(
                "key",
                required=True,
                description="Variable key (e.g., user:name, session:project)",
            ),
            arg("value", required=True, description="Value to set"),
        ],
        description="Set a scoped variable",
        category="memory",
    )
