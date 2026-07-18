"""Tool registry loading for FridayV2."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import datetime
from typing import Any

from friday_chat.tools.schemas import ToolCallRecord, ToolDefinition

DEFAULT_FAKE_TOOLS: tuple[ToolDefinition, ...] = (
    ToolDefinition(
        name="echo",
        description="Return the provided text.",
        input_schema={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
        category="utility",
    ),
    ToolDefinition(
        name="get_current_datetime",
        description="Get the current date and time.",
        input_schema={
            "type": "object",
            "properties": {
                "timezone_name": {"type": "string"},
                "format": {"type": "string"},
            },
        },
        category="utility",
    ),
    ToolDefinition(
        name="remember",
        description="Record a short memory note for the active session.",
        input_schema={
            "type": "object",
            "properties": {"note": {"type": "string"}},
            "required": ["note"],
        },
        category="memory",
    ),
)


class FakeToolRegistry:
    """Deterministic registry used for FridayV2 tests and runtime wiring."""

    def __init__(self, tools: Iterable[ToolDefinition] = DEFAULT_FAKE_TOOLS) -> None:
        self._tools = tuple(tools)
        self.calls: list[ToolCallRecord] = []

    def list_tools(self) -> tuple[ToolDefinition, ...]:
        """Return all registered fake tools."""
        return self._tools

    def get_context_block(self) -> str:
        """Return the tool schema context injected into prompts when configured."""
        lines = ["Available tools:"]
        for tool in self._tools:
            lines.append(f"- {tool.name}: {tool.description}")
        return "\n".join(lines)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Execute a deterministic fake tool call."""
        if name == "echo":
            result = str(arguments.get("text", ""))
        elif name == "get_current_datetime":
            current = datetime.now().astimezone()
            if arguments.get("format") == "iso":
                result = current.isoformat()
            else:
                result = (
                    f"Current time ({current.tzname()}): "
                    f"{current:%A, %B %d, %Y at %I:%M:%S %p %Z}\n"
                    f"Date: {current:%Y-%m-%d}\n"
                    f"Time: {current:%H:%M:%S}\n"
                    f"Day: {current:%A}"
                )
        elif name == "remember":
            result = f"remembered: {arguments.get('note', '')}"
        else:
            raise KeyError(f"Unknown tool: {name}")

        self.calls.append(ToolCallRecord(name=name, arguments=arguments, result=result))
        return result

    @classmethod
    def from_enabled_categories(
        cls,
        enabled_categories: Sequence[str] | None,
    ) -> FakeToolRegistry:
        """Create a registry filtered by configured categories."""
        if not enabled_categories:
            return cls()

        allowed = set(enabled_categories)
        return cls(tool for tool in DEFAULT_FAKE_TOOLS if tool.category in allowed)
