"""
Echo utility tool.

A simple tool that echoes back the user's input - useful for testing
tool calling pipelines.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from friday_tools.base import FridayTool, ToolResult


class EchoTool(FridayTool):
    """
    Echo back the user's message.

    A simple utility tool that returns exactly what was passed to it.
    Useful for testing tool calling pipelines and verifying LLM
    function calling is working correctly.
    """

    name = "echo"
    description = "Echo back the provided message. Use this to repeat or confirm text."
    category = "utility"
    tags = ["echo", "test", "utility", "debug"]

    class Input(BaseModel):
        message: str = Field(
            description="The message to echo back"
        )

    async def run(self, args: Input) -> ToolResult:
        """Execute the echo tool."""
        # Format output showing arguments received then the echo
        content = f"Arguments received: {args.model_dump()}\nEcho: {args.message}"

        return ToolResult(
            content=content,
            data={"echoed": args.message, "args": args.model_dump()},
            metadata={"tool": "echo"},
        )
