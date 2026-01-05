"""
Tool registry implementation.

Ref: docs/specs/tool_specification.md - Section 4: Registry

Provides DefaultToolRegistry for managing tool collections and the
@tool decorator for easy tool registration.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from friday_core.interfaces.tools import SchemaFormat, ToolDefinition

from .definition import FunctionTool

logger = logging.getLogger(__name__)


class DefaultToolRegistry:
    """
    Default implementation of ToolRegistry.

    Manages a collection of tools with thread-safe registration
    and retrieval operations.

    Example:
        ```python
        registry = DefaultToolRegistry()

        @registry.tool
        async def my_tool(input: str) -> str:
            return f"Processed: {input}"

        # Or register manually
        registry.register(SomeToolClass())

        # Get tools for LLM
        schemas = registry.get_schemas()
        ```
    """

    def __init__(self):
        """Initialize empty registry."""
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """
        Register a tool with the registry.

        Args:
            tool: Tool to register.

        Raises:
            ValueError: If tool with same name already registered.
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")

        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def unregister(self, name: str) -> bool:
        """
        Remove a tool from the registry.

        Args:
            name: The tool name to remove.

        Returns:
            True if tool was removed, False if not found.
        """
        if name in self._tools:
            del self._tools[name]
            logger.debug(f"Unregistered tool: {name}")
            return True
        return False

    def get(self, name: str) -> ToolDefinition | None:
        """
        Get a tool by name.

        Args:
            name: The tool's unique identifier.

        Returns:
            The tool if found, None otherwise.
        """
        return self._tools.get(name)

    def list_tools(self) -> list[ToolDefinition]:
        """
        List all registered tools.

        Returns:
            List of all registered tools.
        """
        return list(self._tools.values())

    def list_names(self) -> list[str]:
        """
        List all registered tool names.

        Returns:
            List of tool names.
        """
        return list(self._tools.keys())

    def get_callable(self, name: str) -> Callable[..., Any]:
        """
        Get the executable callable for a tool.

        Args:
            name: The tool's unique identifier.

        Returns:
            Callable that can be invoked with tool arguments.

        Raises:
            KeyError: If tool not found.
        """
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"Tool '{name}' not found in registry")
        return tool.execute

    def get_schemas(self, format: str = "plain") -> list[dict[str, Any]]:
        """
        Get JSON schemas for all registered tools.

        Args:
            format: Output format - "plain" or "openai".

        Returns:
            List of tool schemas suitable for LLM function calling.
        """
        return [tool.to_schema(format) for tool in self._tools.values()]

    def get_schema(self, name: str, format: str = "plain") -> dict[str, Any] | None:
        """
        Get JSON schema for a specific tool.

        Args:
            name: The tool name.
            format: Output format - "plain" or "openai".

        Returns:
            Tool schema if found, None otherwise.
        """
        tool = self.get(name)
        if tool is None:
            return None
        return tool.to_schema(format)

    def tool(
        self,
        name: str | None = None,
        description: str | None = None,
    ) -> Callable[[Callable], FunctionTool]:
        """
        Decorator to register a function as a tool.

        Example:
            ```python
            registry = DefaultToolRegistry()

            @registry.tool(name="greet", description="Greet someone")
            async def greet(name: str) -> str:
                return f"Hello, {name}!"
            ```
        """
        def decorator(func: Callable) -> FunctionTool:
            tool = FunctionTool(func, name=name, description=description)
            self.register(tool)
            return tool
        return decorator

    def clear(self) -> None:
        """Remove all registered tools."""
        self._tools.clear()
        logger.debug("Cleared all tools from registry")

    def __len__(self) -> int:
        """Return number of registered tools."""
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools


# Global default registry instance
_default_registry = DefaultToolRegistry()


def get_default_registry() -> DefaultToolRegistry:
    """Get the default global registry instance."""
    return _default_registry


def tool(
    name: str | None = None,
    description: str | None = None,
) -> Callable[[Callable], FunctionTool]:
    """
    Decorator to register a function as a tool in the default registry.

    Example:
        ```python
        @tool(name="my_tool")
        async def my_tool(input: str) -> str:
            return f"Processed: {input}"
        ```
    """
    return _default_registry.tool(name=name, description=description)
