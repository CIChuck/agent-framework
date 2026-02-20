from __future__ import annotations

from typing import Literal

from friday_memory import MemoryController
from friday_memory.maintenance import MemoryReorganizer
from pydantic import BaseModel, Field

from friday_tools.base import FridayTool, ToolResult


class MemoryMaintenanceTool(FridayTool):
    """
    Perform maintenance tasks on the memory system: Pruning, Synthesis, and Verification.

    This tool wraps the MemoryReorganizer. It is a "heavy" operation that should
    typically be run during 'Night Mode'.
    """  # noqa: E501

    name = "memory_maintain"
    description = "Prune redundancies, synthesize insights, and verify facts in memory."

    class Input(BaseModel):
        operation: Literal["prune", "synthesize", "verify", "full"] = Field(
            ..., description="The maintenance operation to perform."
        )
        dry_run: bool = Field(
            True, description="If True, only report what would be changed."
        )
        backup_first: bool = Field(
            True, description="If True, create a backup before modifying."
        )

    def __init__(self, reorganizer: MemoryReorganizer):
        # Strict DI: We accept the configured Reorganizer, not just the Controller
        self.reorganizer = reorganizer

    async def run(self, args: Input) -> ToolResult:
        report = None

        # Ensure backup if executing and requested
        if not args.dry_run and args.backup_first:
            await self.reorganizer.backup()

        if args.operation == "prune":
            report = await self.reorganizer.prune(
                dry_run=args.dry_run, backup_first=False
            )

        elif args.operation == "synthesize":
            report = await self.reorganizer.synthesize(dry_run=args.dry_run)

        elif args.operation == "verify":
            report = await self.reorganizer.verify(dry_run=args.dry_run)

        elif args.operation == "full":
            report = await self.reorganizer.reorganize(
                dry_run=args.dry_run,
                backup_first=False,  # Handled above
                skip_synthesis=False,
                skip_verify=False,
            )

        # Convert report to dict/string
        # Note: Report objects in friday-memory might not be Pydantic models yet,
        # so we assume they are dataclasses or have a summary method.
        # Ideally, we would inspect the report object.

        summary = f"Maintenance ({args.operation}) complete. Dry Run: {args.dry_run}"

        # Serialize report safely
        report_data = {}
        if hasattr(report, "model_dump"):
            report_data = report.model_dump()
        elif hasattr(report, "dict"):
            report_data = report.dict()
        elif hasattr(report, "__dict__"):
            report_data = report.__dict__

        return ToolResult(
            content=summary,
            data=report_data,
            metadata={"operation": args.operation, "dry_run": args.dry_run},
        )


class MemoryResetTool(FridayTool):
    """
    Reset (Clear) all memory stores. Dangerous operation.
    """

    name = "memory_reset"
    description = "Permanently clear all Graph, Vector, and Episodic memory."

    class Input(BaseModel):
        confirm: bool = Field(..., description="Must be True to execute.")
        session_id: str = Field(..., description="The session ID to clear.")

    def __init__(self, controller: MemoryController):
        self.controller = controller

    async def run(self, args: Input) -> ToolResult:
        if not args.confirm:
            return ToolResult(
                content="Operation cancelled. Confirmation required.",
                error="Confirmation required",
            )

        # Execute Reset
        graph_res = await self.controller.graph.clear()
        vector_res = await self.controller.vector.clear()
        await self.controller.episodic.clear_session(args.session_id)

        return ToolResult(
            content="Memory reset complete.",
            data={
                "graph_deleted": graph_res,
                "vector_deleted": vector_res,
                "session_cleared": args.session_id,
            },
        )
