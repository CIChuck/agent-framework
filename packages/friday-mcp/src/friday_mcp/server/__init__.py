# mypy: ignore-errors
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
from friday_mcp.server.sse import SSEMCPServer
from friday_mcp.server.stdio import StdioMCPServer
from friday_mcp.server.tools_mode import configure_tools_mode

__all__ = [
    "MCPServerBase",
    "StdioMCPServer",
    "SSEMCPServer",
    "configure_agent_mode",
    "configure_tools_mode",
]
