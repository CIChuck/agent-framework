"""
MCP Server implementations.

Provides servers for exposing Friday capabilities via MCP:
- StdioMCPServer: Expose via stdin/stdout (CLI integration)
- SSEMCPServer: Expose via HTTP Server-Sent Events
- configure_agent_mode: Set up agent exposure
- configure_tools_mode: Set up tool registry exposure
"""

from friday_mcp.server.agent_mode import configure_agent_mode
from friday_mcp.server.base import MCPServerBase
from friday_mcp.server.http import StreamableHTTPMCPServer
from friday_mcp.server.http_policy import HTTPServerPolicy
from friday_mcp.server.modern import ModernToolsMCPServer
from friday_mcp.server.modern_stdio import ModernStdioMCPServer
from friday_mcp.server.protocol import (
    RegisteredTool,
    ServerLimits,
    ServerWireError,
    ToolCallResult,
)
from friday_mcp.server.registry import configure_modern_tools_mode
from friday_mcp.server.sse import SSEMCPServer
from friday_mcp.server.stdio import StdioMCPServer
from friday_mcp.server.tools_mode import configure_tools_mode

__all__ = [
    "ModernToolsMCPServer",
    "ModernStdioMCPServer",
    "StreamableHTTPMCPServer",
    "HTTPServerPolicy",
    "RegisteredTool",
    "ServerLimits",
    "ServerWireError",
    "ToolCallResult",
    "configure_modern_tools_mode",
    "MCPServerBase",
    "StdioMCPServer",
    "SSEMCPServer",
    "configure_agent_mode",
    "configure_tools_mode",
]
