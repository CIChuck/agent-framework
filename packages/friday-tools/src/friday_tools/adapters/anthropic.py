# mypy: ignore-errors
"""
Anthropic tool adapter.

Ref: docs/specs/tool_specification.md - Section 6.2: Anthropic Adapter

Converts Anthropic tool definitions (dict format) to Friday's ToolDefinition.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from ..definition import BaseTool
from ..protocols import ToolDefinition

logger = logging.getLogger(__name__)


class AnthropicToolWrapper(BaseTool):
    """Wraps an Anthropic tool definition as a Friday tool."""

    def __init__(
        self,
        tool_def: dict[str, Any],
        handler: Callable[..., Any] | None = None,
    ):
        """
        Initialize wrapper.

        Args:
            tool_def: Anthropic tool definition dict.
            handler: Optional function to execute the tool.
        """
        self._tool_def = tool_def
        self._handler = handler

    @property
    def name(self) -> str:
        return self._tool_def["name"]

    @property
    def description(self) -> str:
        return self._tool_def.get("description", f"Execute {self.name}")

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """Get input schema from Anthropic format."""
        return self._tool_def.get(
            "input_schema",
            {
                "type": "object",
                "properties": {},
            },
        )

    async def execute(self, **kwargs: Any) -> str:
        """Execute the tool using the provided handler."""
        if self._handler is None:
            raise RuntimeError(
                f"No handler provided for tool '{self.name}'. "
                "Anthropic tools require a handler function."
            )

        import asyncio
        import inspect

        if inspect.iscoroutinefunction(self._handler):
            result = await self._handler(**kwargs)
        else:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: self._handler(**kwargs))

        return str(result) if result is not None else ""


class AnthropicToolAdapter:
    """
    Adapts Anthropic tool definitions to Friday ToolDefinition.

    Anthropic tools are defined as dictionaries with the following format:
    ```python
    {
        "name": "get_weather",
        "description": "Get the current weather",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
        }
    }
    ```

    Example:
        ```python
        adapter = AnthropicToolAdapter()

        anthropic_tool = {
            "name": "calculator",
            "description": "Evaluate math expressions",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                },
                "required": ["expression"]
            }
        }

        def calc_handler(expression: str) -> str:
            return str(eval(expression))

        friday_tool = adapter.adapt(anthropic_tool, handler=calc_handler)
        ```
    """

    def adapt(
        self,
        external_tool: dict[str, Any],
        handler: Callable[..., Any] | None = None,
    ) -> ToolDefinition:
        """
        Convert an Anthropic tool definition to Friday's ToolDefinition.

        Args:
            external_tool: Anthropic tool definition dict.
            handler: Function to execute when the tool is called.

        Returns:
            Friday ToolDefinition (actually an AnthropicToolWrapper).
        """
        self._validate_anthropic_tool(external_tool)
        return AnthropicToolWrapper(external_tool, handler=handler)

    def adapt_many(
        self,
        tools: list[dict[str, Any]],
        handlers: dict[str, Callable[..., Any]] | None = None,
    ) -> list[ToolDefinition]:
        """
        Convert multiple Anthropic tool definitions.

        Args:
            tools: List of Anthropic tool definition dicts.
            handlers: Optional dict mapping tool names to handler functions.

        Returns:
            List of Friday ToolDefinition instances.
        """
        handlers = handlers or {}
        return [self.adapt(tool, handler=handlers.get(tool["name"])) for tool in tools]

    def _validate_anthropic_tool(self, tool: dict[str, Any]) -> None:
        """Validate that the dict is a valid Anthropic tool definition."""
        if not isinstance(tool, dict):
            raise TypeError(
                f"Expected dict for Anthropic tool, got {type(tool).__name__}"
            )

        if "name" not in tool:
            raise ValueError("Anthropic tool must have 'name' field")

    @staticmethod
    def from_anthropic_response(
        response_tools: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Extract tool definitions from an Anthropic API response.

        This is useful when you want to re-use tools defined by
        an Anthropic API response.

        Args:
            response_tools: List of tool dicts from Anthropic API.

        Returns:
            List of tool definitions in Anthropic format.
        """
        return [
            {
                "name": t["name"],
                "description": t.get("description", ""),
                "input_schema": t.get("input_schema", {}),
            }
            for t in response_tools
        ]
