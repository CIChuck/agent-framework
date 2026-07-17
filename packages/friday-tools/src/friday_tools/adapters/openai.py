# mypy: ignore-errors
"""
OpenAI tool adapter.

Ref: docs/reference/specs/tool_specification.md - Section 6.3: OpenAI Adapter

Converts OpenAI function calling format to Friday's ToolDefinition.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from ..definition import BaseTool
from ..protocols import ToolDefinition

logger = logging.getLogger(__name__)


class OpenAIToolWrapper(BaseTool):
    """Wraps an OpenAI function definition as a Friday tool."""

    def __init__(
        self,
        tool_def: dict[str, Any],
        handler: Callable[..., Any] | None = None,
    ):
        """
        Initialize wrapper.

        Args:
            tool_def: OpenAI function/tool definition dict.
            handler: Optional function to execute the tool.
        """
        # Handle both formats: {"type": "function", "function": {...}} and direct function def  # noqa: E501
        self._func_def = tool_def.get("function", tool_def)
        self._handler = handler

    @property
    def name(self) -> str:
        return self._func_def["name"]

    @property
    def description(self) -> str:
        return self._func_def.get("description", f"Execute {self.name}")

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """Get parameters from OpenAI format."""
        return self._func_def.get(
            "parameters",
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
                "OpenAI tools require a handler function."
            )

        import asyncio
        import inspect

        if inspect.iscoroutinefunction(self._handler):
            result = await self._handler(**kwargs)
        else:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: self._handler(**kwargs))

        return str(result) if result is not None else ""


class OpenAIToolAdapter:
    """
    Adapts OpenAI function calling format to Friday ToolDefinition.

    OpenAI tools can be defined in two formats:

    1. Function format (older):
    ```python
    {
        "name": "get_weather",
        "description": "Get the current weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    }
    ```

    2. Tool format (newer):
    ```python
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather",
            "parameters": {...}
        }
    }
    ```

    Both formats are supported.

    Example:
        ```python
        adapter = OpenAIToolAdapter()

        openai_tool = {
            "type": "function",
            "function": {
                "name": "search",
                "description": "Search the web",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    },
                    "required": ["query"]
                }
            }
        }

        def search_handler(query: str) -> str:
            return f"Results for: {query}"

        friday_tool = adapter.adapt(openai_tool, handler=search_handler)
        ```
    """

    def adapt(
        self,
        external_tool: dict[str, Any],
        handler: Callable[..., Any] | None = None,
    ) -> ToolDefinition:
        """
        Convert an OpenAI tool definition to Friday's ToolDefinition.

        Args:
            external_tool: OpenAI function/tool definition dict.
            handler: Function to execute when the tool is called.

        Returns:
            Friday ToolDefinition (actually an OpenAIToolWrapper).
        """
        self._validate_openai_tool(external_tool)
        return OpenAIToolWrapper(external_tool, handler=handler)

    def adapt_many(
        self,
        tools: list[dict[str, Any]],
        handlers: dict[str, Callable[..., Any]] | None = None,
    ) -> list[ToolDefinition]:
        """
        Convert multiple OpenAI tool definitions.

        Args:
            tools: List of OpenAI function/tool definition dicts.
            handlers: Optional dict mapping tool names to handler functions.

        Returns:
            List of Friday ToolDefinition instances.
        """
        handlers = handlers or {}
        result = []
        for tool in tools:
            # Extract name for handler lookup
            name = tool["function"]["name"] if "function" in tool else tool["name"]
            result.append(self.adapt(tool, handler=handlers.get(name)))
        return result

    def _validate_openai_tool(self, tool: dict[str, Any]) -> None:
        """Validate that the dict is a valid OpenAI tool definition."""
        if not isinstance(tool, dict):
            raise TypeError(f"Expected dict for OpenAI tool, got {type(tool).__name__}")

        # Check for tool format
        if "function" in tool:
            func_def = tool["function"]
            if "name" not in func_def:
                raise ValueError("OpenAI function must have 'name' field")
        elif "name" not in tool:
            raise ValueError("OpenAI tool must have 'name' field")

    @staticmethod
    def to_openai_format(tool: ToolDefinition) -> dict[str, Any]:
        """
        Convert a Friday tool to OpenAI format.

        Args:
            tool: Friday ToolDefinition instance.

        Returns:
            Dict in OpenAI tool format.
        """
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters_schema,
            },
        }

    @staticmethod
    def to_openai_format_many(tools: list[ToolDefinition]) -> list[dict[str, Any]]:
        """
        Convert multiple Friday tools to OpenAI format.

        Args:
            tools: List of Friday ToolDefinition instances.

        Returns:
            List of dicts in OpenAI tool format.
        """
        return [OpenAIToolAdapter.to_openai_format(t) for t in tools]
