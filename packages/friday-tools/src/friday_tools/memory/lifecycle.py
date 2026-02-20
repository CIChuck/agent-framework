from __future__ import annotations

from friday_memory import MemoryPromotionService
from pydantic import BaseModel, Field

from friday_tools.base import FridayTool, ToolResult


class LifecycleTool(FridayTool):
    """
    Manage the Memory Lifecycle (Short-term -> Long-term promotion).
    """

    name = "memory_lifecycle"
    description = "Trigger memory promotion/decay cycles or view lifecycle statistics."

    class Input(BaseModel):
        action: str = Field(
            ..., description="Action to perform: 'run_cycle' or 'stats'"
        )
        dry_run: bool = Field(
            True, description="If True, only report potential changes."
        )

    def __init__(self, promotion_service: MemoryPromotionService):
        self.promotion_service = promotion_service

    async def run(self, args: Input) -> ToolResult:
        if args.action == "stats":
            stats = await self.promotion_service.collection_manager.get_stats()
            return ToolResult(content=f"Lifecycle Stats: {stats}", data=stats)

        elif args.action == "run_cycle":
            result = await self.promotion_service.run_promotion_cycle(
                dry_run=args.dry_run
            )

            content = (
                f"Promotion Cycle (Dry Run: {args.dry_run})\n"
                f"Promoted: {result.promoted_to_long_term}\n"
                f"Decayed: {result.decayed_from_long_term}\n"
                f"Reactivated: {result.reactivated}"
            )

            return ToolResult(
                content=content,
                data={
                    "promoted": result.promoted_to_long_term,
                    "decayed": result.decayed_from_long_term,
                    "reactivated": result.reactivated,
                    "errors": [str(e) for e in result.errors],
                },
                metadata={"dry_run": args.dry_run},
            )

        return ToolResult(content="Invalid action.", error="Invalid action")
