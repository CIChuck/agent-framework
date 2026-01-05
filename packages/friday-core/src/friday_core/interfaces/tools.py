"""
Tool Protocols.

Defines unified interfaces for tools across the Friday Framework.
All tool-related protocols are defined here to ensure consistency
between friday-tools, friday-agent, and friday-mcp packages.

Ref: Batch 3 Specification, Section 2.3
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Generic, Protocol, TypeVar, runtime_checkable


class SchemaFormat(str, Enum):
    """Schema output format for LLM function calling."""

    PLAIN = "plain"
    """Plain format: {"name": ..., "description": ..., "parameters": ...}"""

    OPENAI = "openai"
    """OpenAI-wrapped: {"type": "function", "function": {...}}"""


@runtime_checkable
class ToolDefinition(Protocol):
    """
    Abstract representation of a tool capability.

    This protocol defines what a "tool" IS in Friday - the fundamental
    unit of agent capability. All tools must implement this interface.

    Properties:
        name: Unique tool identifier (e.g., "file_read", "web_search").
        description: Human-readable description for the LLM to understand
                    when to use this tool.
        parameters_schema: JSON Schema defining the tool's parameters.
    """

    @property
    def name(self) -> str:
        """Unique tool identifier."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description for the LLM."""
        ...

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """JSON Schema for tool parameters."""
        ...

    async def execute(self, **kwargs: Any) -> str:
        """
        Execute the tool with given arguments.

        Args:
            **kwargs: Tool-specific parameters matching the schema.

        Returns:
            String result of the tool execution.
        """
        ...

    def to_schema(self, format: str = "plain") -> dict[str, Any]:
        """
        Convert tool to JSON schema format for LLM function calling.

        Args:
            format: Output format - "plain" or "openai".
                   "plain": {"name": ..., "description": ..., "parameters": ...}
                   "openai": {"type": "function", "function": {...}}

        Returns:
            Dictionary suitable for LLM function calling.
        """
        ...


T = TypeVar("T")


@runtime_checkable
class ToolAdapter(Protocol, Generic[T]):
    """
    Adapts external framework tools to Friday's ToolDefinition.

    Framework adapters (LangChain, Anthropic, OpenAI, MCP) implement this
    protocol to convert their tool formats into Friday's unified format.
    """

    def adapt(self, external_tool: T) -> ToolDefinition:
        """
        Convert an external tool to Friday's ToolDefinition.

        Args:
            external_tool: Tool from an external framework.

        Returns:
            Friday ToolDefinition instance.
        """
        ...

    def adapt_many(self, tools: list[T]) -> list[ToolDefinition]:
        """
        Convert multiple external tools.

        Args:
            tools: List of tools from an external framework.

        Returns:
            List of Friday ToolDefinition instances.
        """
        ...


@runtime_checkable
class ToolRegistry(Protocol):
    """
    Registry for managing tool collections.

    Provides unified interface for tool registration, retrieval, and
    schema access. Supports both object-based and callable-based access
    patterns for backward compatibility.
    """

    def register(self, tool: ToolDefinition) -> None:
        """
        Register a tool with the registry.

        Args:
            tool: Tool to register (must implement ToolDefinition).

        Raises:
            ValueError: If tool with same name already registered.
        """
        ...

    def get(self, name: str) -> ToolDefinition | None:
        """
        Get a tool by name.

        Args:
            name: The tool's unique identifier.

        Returns:
            The tool if found, None otherwise.
        """
        ...

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
        ...

    def list_tools(self) -> list[ToolDefinition]:
        """
        List all registered tools.

        Returns:
            List of all registered ToolDefinition instances.
        """
        ...

    def list_names(self) -> list[str]:
        """
        List all registered tool names.

        Returns:
            List of tool name strings.
        """
        ...

    def get_schemas(self, format: str = "plain") -> list[dict[str, Any]]:
        """
        Get JSON schemas for all registered tools.

        Args:
            format: Output format - "plain" or "openai".

        Returns:
            List of tool schemas suitable for LLM function calling.
        """
        ...

    def get_schema(self, name: str, format: str = "plain") -> dict[str, Any] | None:
        """
        Get JSON schema for a specific tool.

        Args:
            name: The tool name.
            format: Output format - "plain" or "openai".

        Returns:
            Tool schema if found, None otherwise.
        """
        ...
