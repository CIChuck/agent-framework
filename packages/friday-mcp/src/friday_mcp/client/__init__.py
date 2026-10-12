# mypy: ignore-errors
"""
MCP Client implementations.

Provides clients for connecting to external MCP servers:
- StdioMCPClient: Connect via subprocess stdio
- SSEMCPClient: Connect via HTTP Server-Sent Events
- StreamableHTTPMCPClient: Explicit modern or 2025 Streamable HTTP profile
- MCPClientManager: Manage multiple server connections
- MCPToolAdapter: Adapt MCP tools to Friday's ToolDefinition
"""

from friday_mcp.client.adapter import MCPToolAdapter, MCPToolWrapper
from friday_mcp.client.base import MCPClientBase, MCPError
from friday_mcp.client.http import StreamableHTTPMCPClient
from friday_mcp.client.http_policy import HTTPEndpointPolicy
from friday_mcp.client.http_protocol import HTTPLimits
from friday_mcp.client.manager import MCPClientManager
from friday_mcp.client.sse import SSEMCPClient
from friday_mcp.client.stdio import StdioMCPClient

__all__ = [
    "MCPClientBase",
    "MCPError",
    "StdioMCPClient",
    "SSEMCPClient",
    "StreamableHTTPMCPClient",
    "HTTPEndpointPolicy",
    "HTTPLimits",
    "MCPClientManager",
    "MCPToolAdapter",
    "MCPToolWrapper",
]
