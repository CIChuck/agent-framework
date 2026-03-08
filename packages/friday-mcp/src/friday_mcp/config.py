# mypy: ignore-errors
"""
MCP Configuration Models.

Pydantic models for configuring MCP clients and servers.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, model_validator


class TransportType(str, Enum):
    """Supported MCP transport types."""

    STDIO = "stdio"
    SSE = "sse"


class MCPServerConfig(BaseModel):
    """
    Configuration for connecting to an external MCP server.

    Example (stdio):
        MCPServerConfig(
            name="filesystem",
            transport="stdio",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
        )

    Example (SSE):
        MCPServerConfig(
            name="remote-api",
            transport="sse",
            url="https://mcp.example.com/sse"
        )
    """

    # Server identification
    name: str = Field(..., description="Unique server name for reference")
    enabled: bool = Field(default=True, description="Whether to connect to this server")

    # Transport configuration
    transport: TransportType = Field(default=TransportType.STDIO)

    # Stdio transport options
    command: str | None = Field(default=None, description="Command to run for stdio")
    args: list[str] = Field(default_factory=list, description="Command arguments")
    env: dict[str, str] = Field(
        default_factory=dict, description="Environment variables"
    )
    cwd: Path | None = Field(default=None, description="Working directory")

    # SSE transport options
    url: str | None = Field(default=None, description="SSE endpoint URL")
    headers: dict[str, str] = Field(default_factory=dict, description="HTTP headers")

    # Connection options
    timeout_seconds: int = Field(default=30, description="Connection timeout")
    retry_attempts: int = Field(default=3, description="Retry attempts on failure")

    @model_validator(mode="after")
    def validate_transport_requirements(self) -> MCPServerConfig:
        """Validate that required fields are present for transport type."""
        if self.transport == TransportType.STDIO and not self.command:
            raise ValueError("stdio transport requires 'command'")
        if self.transport == TransportType.SSE and not self.url:
            raise ValueError("sse transport requires 'url'")
        return self


class ServerMode(str, Enum):
    """MCP server operation modes."""

    AGENT = "agent"  # Expose agent.run() as a tool
    TOOLS = "tools"  # Expose tool registry


class MCPServerSettings(BaseModel):
    """
    Configuration for running Friday as an MCP server.

    Example (agent mode):
        MCPServerSettings(
            mode="agent",
            transport="stdio",
            expose_prompts=True
        )

    Example (tools mode with SSE):
        MCPServerSettings(
            mode="tools",
            transport="sse",
            host="0.0.0.0",
            port=8080,
            tool_filter=["file_read", "file_write", "web_search"]
        )
    """

    # Server mode
    mode: ServerMode = Field(default=ServerMode.AGENT)

    # Transport configuration
    transport: TransportType = Field(default=TransportType.STDIO)

    # SSE server options
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8765)
    path: str = Field(default="/mcp")

    # Tool exposure options (for tools mode)
    tool_filter: list[str] | None = Field(
        default=None,
        description="Whitelist of tools to expose (None = all)",
    )
    tool_prefix: str = Field(
        default="friday_",
        description="Prefix for exposed tool names",
    )

    # Agent mode options
    agent_tool_name: str = Field(
        default="friday_agent",
        description="Name of the agent tool",
    )
    agent_tool_description: str = Field(
        default="Execute a task using the Friday AI agent",
        description="Description for the agent tool",
    )
    expose_prompts: bool = Field(
        default=True,
        description="Expose agent system prompts",
    )
    expose_resources: bool = Field(
        default=True,
        description="Expose memory/context as resources",
    )


class MCPConfig(BaseModel):
    """
    Complete MCP configuration.

    Combines client and server settings for full MCP integration.
    """

    # Client configuration (connect to external servers)
    servers: list[MCPServerConfig] = Field(
        default_factory=list,
        description="External MCP servers to connect to",
    )

    # Server configuration (expose Friday via MCP)
    server: MCPServerSettings | None = Field(
        default=None,
        description="Settings for running Friday as MCP server",
    )

    # General options
    auto_connect: bool = Field(
        default=True,
        description="Auto-connect to servers on startup",
    )
    tool_name_prefix: str = Field(
        default="mcp_",
        description="Prefix for tools from MCP servers",
    )

    def get_enabled_servers(self) -> list[MCPServerConfig]:
        """Get list of enabled server configurations."""
        return [s for s in self.servers if s.enabled]
