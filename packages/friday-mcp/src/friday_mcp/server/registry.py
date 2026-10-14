"""Explicit modern bridge through the public Core registry/tool contracts."""

from __future__ import annotations

import inspect
from collections.abc import Collection

from friday_core.interfaces.tools import ToolDefinition, ToolRegistry

from friday_mcp.client.protocol import JSONValue
from friday_mcp.server.modern import ModernToolsMCPServer
from friday_mcp.server.protocol import (
    RegisteredTool,
    ServerLimits,
    ToolCallResult,
    ToolHandler,
)


def _handler(tool: ToolDefinition, limits: ServerLimits) -> ToolHandler:
    method = tool.execute
    if not inspect.iscoroutinefunction(method):
        raise ValueError("MCP registry tool must be async")

    async def execute(arguments: dict[str, JSONValue]) -> ToolCallResult:
        result = await method(**arguments)
        if not isinstance(result, str):
            raise ValueError("MCP registry tool returned invalid result")
        return ToolCallResult.text(result, limits=limits)

    return execute


def configure_modern_tools_mode(
    server: ModernToolsMCPServer,
    registry: ToolRegistry,
    *,
    tool_filter: Collection[str] | None = None,
    prefix: str = "",
) -> None:
    """Publish a validated explicit snapshot atomically, without auto refresh."""
    if not isinstance(prefix, str) or len(prefix.encode("utf-8")) > 128:
        raise ValueError("Invalid MCP registry prefix")
    if tool_filter is not None and (
        len(tool_filter) > server.limits.catalog_tools
        or any(not isinstance(n, str) for n in tool_filter)
    ):
        raise ValueError("Invalid MCP registry filter")
    tools = registry.list_tools()
    if len(tools) > server.limits.catalog_tools:
        raise ValueError("MCP registry limit exceeded")
    staged: list[RegisteredTool] = []
    for tool in tools:
        if tool_filter is not None and tool.name not in tool_filter:
            continue
        # parameters_schema is the declared dynamic JSON boundary. Preserve all fields.
        definition = {
            "name": prefix + tool.name,
            "description": tool.description,
            "inputSchema": tool.parameters_schema,
        }
        staged.append(
            RegisteredTool.from_definition(
                definition, _handler(tool, server.limits), limits=server.limits
            )
        )
    server.replace_tools(staged)
