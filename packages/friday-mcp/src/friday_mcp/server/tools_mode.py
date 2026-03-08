# mypy: ignore-errors
"""
Tools Mode MCP Server.

Exposes Friday's tool registry as an MCP server.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Protocol, runtime_checkable

from friday_mcp.config import MCPServerSettings
from friday_mcp.server.base import MCPServerBase
from friday_mcp.utils.schema import friday_to_mcp_schema

logger = logging.getLogger(__name__)


@runtime_checkable
class ToolRegistryLike(Protocol):
    """Protocol for tool registry compatibility."""

    def list_tools(self) -> list[Any]:
        """Get list of all tools."""
        ...

    def get(self, name: str) -> Any | None:
        """Get a tool by name."""
        ...


@runtime_checkable
class ToolDefinitionLike(Protocol):
    """Protocol for tool definition compatibility."""

    @property
    def name(self) -> str:
        """Tool name."""
        ...

    @property
    def description(self) -> str:
        """Tool description."""
        ...

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """Tool parameters schema."""
        ...

    async def execute(self, **kwargs: Any) -> str:
        """Execute the tool."""
        ...


def configure_tools_mode(
    server: MCPServerBase,
    registry: ToolRegistryLike,
    settings: MCPServerSettings,
) -> None:
    """
    Configure an MCP server for tools mode.

    Exposes all (or filtered) tools from the registry via MCP.

    Args:
        server: MCP server instance
        registry: Friday tool registry
        settings: Server settings

    Example:
        from friday_mcp import SSEMCPServer, MCPServerSettings, ServerMode
        from friday_tools import DefaultToolRegistry

        registry = DefaultToolRegistry()
        # ... register tools ...

        server = SSEMCPServer(host="0.0.0.0", port=8080)
        configure_tools_mode(
            server,
            registry,
            MCPServerSettings(
                mode=ServerMode.TOOLS,
                tool_filter=["file_read", "file_write", "web_search"]
            )
        )
        await server.start()
    """
    tools = registry.list_tools()
    registered_count = 0
    skipped_count = 0

    for tool in tools:
        # Apply filter if specified
        if settings.tool_filter and tool.name not in settings.tool_filter:
            skipped_count += 1
            continue

        # Create prefixed name for MCP
        mcp_name = f"{settings.tool_prefix}{tool.name}"

        # Create async handler that captures the tool
        async def tool_handler(_tool: ToolDefinitionLike = tool, **kwargs: Any) -> str:
            return await _tool.execute(**kwargs)

        # Convert Friday schema to MCP inputSchema
        input_schema = friday_to_mcp_schema(tool.parameters_schema)

        # Register with MCP server
        server.register_tool(
            name=mcp_name,
            description=tool.description,
            input_schema=input_schema,
            handler=tool_handler,
        )

        registered_count += 1

    logger.info(
        f"Configured tools mode: {registered_count} tools registered, "
        f"{skipped_count} filtered out"
    )

    # Add a tools listing resource
    _register_tools_resource(server, tools, settings)


def _register_tools_resource(
    server: MCPServerBase,
    tools: list[Any],
    settings: MCPServerSettings,
) -> None:
    """Register a resource listing available tools."""

    def list_available_tools() -> dict[str, Any]:
        """Get list of available tools as a resource."""
        tool_list = []
        for tool in tools:
            if settings.tool_filter and tool.name not in settings.tool_filter:
                continue
            tool_list.append(
                {
                    "name": f"{settings.tool_prefix}{tool.name}",
                    "description": tool.description,
                }
            )

        return {
            "contents": [
                {
                    "uri": "friday://tools/list",
                    "mimeType": "application/json",
                    "text": json.dumps(tool_list, indent=2),
                },
            ],
        }

    server.register_resource(
        uri="friday://tools/list",
        name="Available Tools",
        description="List of all available Friday tools",
        mime_type="application/json",
        handler=list_available_tools,
    )


def register_single_tool(
    server: MCPServerBase,
    tool: ToolDefinitionLike,
    prefix: str = "",
) -> None:
    """
    Register a single tool with the MCP server.

    Convenience function for adding individual tools.

    Args:
        server: MCP server instance
        tool: Tool to register
        prefix: Optional name prefix
    """
    mcp_name = f"{prefix}{tool.name}" if prefix else tool.name

    async def tool_handler(**kwargs: Any) -> str:
        return await tool.execute(**kwargs)

    input_schema = friday_to_mcp_schema(tool.parameters_schema)

    server.register_tool(
        name=mcp_name,
        description=tool.description,
        input_schema=input_schema,
        handler=tool_handler,
    )

    logger.debug(f"Registered tool: {mcp_name}")
