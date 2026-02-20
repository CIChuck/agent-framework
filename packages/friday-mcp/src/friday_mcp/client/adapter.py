"""
MCP Tool Adapter.

Adapts MCP tools to Friday's ToolDefinition protocol.
Follows the pattern from friday-tools/adapters/.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from friday_core.interfaces.tools import SchemaFormat

from friday_mcp.protocols import MCPClient, ToolDefinition
from friday_mcp.utils.schema import mcp_to_friday_schema

if TYPE_CHECKING:
    from friday_mcp.client.base import MCPClientBase

logger = logging.getLogger(__name__)


class MCPToolWrapper:
    """
    Wraps an MCP tool as a Friday ToolDefinition.

    Similar to LangChainToolWrapper and AnthropicToolWrapper
    in friday-tools/adapters/.
    """

    def __init__(
        self,
        client: MCPClient,
        tool_def: dict[str, Any],
        name_prefix: str = "",
    ):
        """
        Initialize MCP tool wrapper.

        Args:
            client: Connected MCP client for executing the tool
            tool_def: MCP tool definition from tools/list
            name_prefix: Optional prefix for tool name
        """
        self._client = client
        self._tool_def = tool_def
        self._name_prefix = name_prefix
        self._original_name = tool_def.get("name", "unknown")

    @property
    def name(self) -> str:
        """Tool name with optional prefix."""
        if self._name_prefix:
            return f"{self._name_prefix}{self._original_name}"
        return self._original_name

    @property
    def description(self) -> str:
        """Tool description."""
        return self._tool_def.get("description", f"MCP tool: {self._original_name}")

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """Convert MCP inputSchema to Friday parameters_schema."""
        input_schema = self._tool_def.get("inputSchema", {})
        return mcp_to_friday_schema(input_schema)

    async def execute(self, **kwargs: Any) -> str:
        """Execute the tool via MCP client."""
        return await self._client.call_tool(self._original_name, kwargs)

    def to_schema(self, format: str = "plain") -> dict[str, Any]:
        """
        Convert to JSON schema format for LLM function calling.

        Args:
            format: Output format - "plain" or "openai".

        Returns:
            Dictionary suitable for LLM function calling.
        """
        plain_schema = {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema,
        }

        if format == SchemaFormat.OPENAI or format == "openai":
            return {
                "type": "function",
                "function": plain_schema,
            }

        return plain_schema

    def __repr__(self) -> str:
        return f"MCPToolWrapper(name={self.name!r})"


class MCPToolAdapter:
    """
    Adapts MCP tools to Friday's ToolDefinition protocol.

    Example:
        client = StdioMCPClient(...)
        await client.connect()

        adapter = MCPToolAdapter(client, prefix="mcp_filesystem_")
        tools = await adapter.get_tools()

        # Register with Friday's registry
        for tool in tools:
            registry.register(tool)
    """

    def __init__(
        self,
        client: MCPClientBase,
        prefix: str = "",
    ):
        """
        Initialize adapter.

        Args:
            client: Connected MCP client
            prefix: Prefix to add to tool names (e.g., "mcp_filesystem_")
        """
        self._client = client
        self._prefix = prefix
        self._tools_cache: list[MCPToolWrapper] | None = None

    async def get_tools(self, refresh: bool = False) -> list[ToolDefinition]:
        """
        Get all tools from the MCP server as Friday ToolDefinitions.

        Args:
            refresh: Force refresh of cached tools

        Returns:
            List of wrapped tools implementing ToolDefinition protocol.
        """
        if self._tools_cache is not None and not refresh:
            return list(self._tools_cache)

        mcp_tools = await self._client.list_tools()
        self._tools_cache = [
            MCPToolWrapper(self._client, tool_def, self._prefix)
            for tool_def in mcp_tools
        ]

        logger.debug(f"Adapted {len(self._tools_cache)} tools from {self._client.name}")

        return list(self._tools_cache)

    async def get_tool(self, name: str) -> ToolDefinition | None:
        """
        Get a specific tool by name.

        Args:
            name: Tool name (with or without prefix)

        Returns:
            Wrapped tool or None if not found
        """
        tools = await self.get_tools()

        # Try exact match first
        for tool in tools:
            if tool.name == name:
                return tool

        # Try matching original name (without prefix)
        for tool in tools:
            if isinstance(tool, MCPToolWrapper) and tool._original_name == name:
                return tool

        return None

    def adapt(self, tool_def: dict[str, Any]) -> ToolDefinition:
        """
        Adapt a single tool definition.

        Args:
            tool_def: MCP tool definition

        Returns:
            Wrapped tool
        """
        return MCPToolWrapper(self._client, tool_def, self._prefix)

    def adapt_many(self, tool_defs: list[dict[str, Any]]) -> list[ToolDefinition]:
        """
        Adapt multiple tool definitions.

        Args:
            tool_defs: List of MCP tool definitions

        Returns:
            List of wrapped tools
        """
        return [self.adapt(tool_def) for tool_def in tool_defs]

    @property
    def client_name(self) -> str:
        """Get the name of the underlying client."""
        return self._client.name

    def clear_cache(self) -> None:
        """Clear the tools cache."""
        self._tools_cache = None
