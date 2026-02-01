"""
Maintenance commands for Friday Chat.

Commands:
- /reset - Clear all memory stores
- /reorganize - Run memory reorganization
- /lifecycle - Run lifecycle cycle
- /migrate - Migrate memories to lifecycle metadata
"""

import asyncio
from typing import TYPE_CHECKING

from friday_cli import arg

if TYPE_CHECKING:
    from ..session import MemoryChatSession


def register_maintenance_commands(registry, session: "MemoryChatSession") -> None:
    """Register maintenance commands with the registry."""

    registry.register(
        "reset",
        lambda ctx, **kwargs: asyncio.create_task(ctx.cmd_reset()),
        description="Clear all memory stores and archive ALL transcript sessions (clean slate)",
        category="maintenance",
    )

    registry.register(
        "reorganize",
        lambda ctx, opts="", **kwargs: asyncio.create_task(ctx.cmd_reorganize(opts)),
        arguments=[
            arg("--execute", required=False, description="Run for real (default is dry-run)"),
            arg("--no-backup", required=False, description="Skip backup before modifications"),
            arg("--skip-synthesis", required=False, description="Skip LLM-based memory synthesis"),
            arg("--skip-verify", required=False, description="Skip LLM-based fact verification"),
            arg("--skip-lifecycle", required=False, description="Skip lifecycle and optimization steps"),
            arg("--analyze", required=False, description="Just run analysis (read-only)"),
            arg("--prune", required=False, description="Just run pruning"),
            arg("--synthesize", required=False, description="Just run synthesis (meta-insights, relationships)"),
            arg("--verify", required=False, description="Just run fact verification"),
            arg("--backup", required=False, description="Just create a backup"),
            arg("--dedupe", required=False, description="Just run insight deduplication"),
        ],
        description="Run memory reorganization (analyze, prune, synthesize, verify)",
        category="maintenance",
    )

    registry.register(
        "lifecycle",
        lambda ctx, opts="", **kwargs: asyncio.create_task(ctx.cmd_lifecycle(opts)),
        arguments=[
            arg("--execute", required=False, description="Run for real (default is dry-run)"),
            arg("--stats", required=False, description="Show lifecycle statistics only"),
            arg("--optimize", required=False, description="Flush access buffer and recompute retrieval factors"),
            arg("--flush", required=False, description="Flush access buffer only"),
        ],
        description="Run memory lifecycle cycle (promotion, decay, reactivation)",
        category="maintenance",
    )

    registry.register(
        "migrate",
        lambda ctx, opts="", **kwargs: asyncio.create_task(ctx.cmd_migrate(opts)),
        arguments=[
            arg("--execute", required=False, description="Run for real (default is dry-run)"),
            arg("--stats", required=False, description="Show migration statistics only"),
        ],
        description="Migrate existing memories to lifecycle metadata",
        category="maintenance",
    )
