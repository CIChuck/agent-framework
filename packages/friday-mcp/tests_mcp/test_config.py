"""Tests for MCP configuration models."""

from pathlib import Path

import pytest

from friday_mcp.config import (
    MCPConfig,
    MCPServerConfig,
    MCPServerSettings,
    ServerMode,
    TransportType,
)


class TestMCPServerConfig:
    """Tests for MCPServerConfig."""

    def test_stdio_config_valid(self):
        """Test valid stdio configuration."""
        config = MCPServerConfig(
            name="test",
            transport=TransportType.STDIO,
            command="npx",
            args=["-y", "some-server"],
        )
        assert config.name == "test"
        assert config.transport == TransportType.STDIO
        assert config.command == "npx"
        assert config.args == ["-y", "some-server"]

    def test_stdio_config_requires_command(self):
        """Test that stdio transport requires command."""
        with pytest.raises(ValueError, match="stdio transport requires 'command'"):
            MCPServerConfig(
                name="test",
                transport=TransportType.STDIO,
            )

    def test_sse_config_valid(self):
        """Test valid SSE configuration."""
        config = MCPServerConfig(
            name="test",
            transport=TransportType.SSE,
            url="http://localhost:8080/sse",
            headers={"Authorization": "Bearer token"},
        )
        assert config.transport == TransportType.SSE
        assert config.url == "http://localhost:8080/sse"
        assert config.headers == {"Authorization": "Bearer token"}

    def test_sse_config_requires_url(self):
        """Test that SSE transport requires url."""
        with pytest.raises(ValueError, match="sse transport requires 'url'"):
            MCPServerConfig(
                name="test",
                transport=TransportType.SSE,
            )

    def test_config_with_env_and_cwd(self):
        """Test configuration with environment and working directory."""
        config = MCPServerConfig(
            name="test",
            transport=TransportType.STDIO,
            command="python",
            args=["server.py"],
            env={"DEBUG": "1"},
            cwd=Path("/tmp"),
        )
        assert config.env == {"DEBUG": "1"}
        assert config.cwd == Path("/tmp")

    def test_config_defaults(self):
        """Test configuration defaults."""
        config = MCPServerConfig(
            name="test",
            transport=TransportType.STDIO,
            command="echo",
        )
        assert config.enabled is True
        assert config.args == []
        assert config.env == {}
        assert config.timeout_seconds == 30
        assert config.retry_attempts == 3


class TestMCPServerSettings:
    """Tests for MCPServerSettings."""

    def test_agent_mode_defaults(self):
        """Test agent mode defaults."""
        settings = MCPServerSettings(mode=ServerMode.AGENT)
        assert settings.mode == ServerMode.AGENT
        assert settings.agent_tool_name == "friday_agent"
        assert settings.expose_prompts is True
        assert settings.expose_resources is True

    def test_tools_mode_with_filter(self):
        """Test tools mode with filter."""
        settings = MCPServerSettings(
            mode=ServerMode.TOOLS,
            tool_filter=["file_read", "file_write"],
            tool_prefix="my_",
        )
        assert settings.mode == ServerMode.TOOLS
        assert settings.tool_filter == ["file_read", "file_write"]
        assert settings.tool_prefix == "my_"

    def test_sse_server_options(self):
        """Test SSE server options."""
        settings = MCPServerSettings(
            transport=TransportType.SSE,
            host="0.0.0.0",
            port=9000,
            path="/api/mcp",
        )
        assert settings.host == "0.0.0.0"
        assert settings.port == 9000
        assert settings.path == "/api/mcp"


class TestMCPConfig:
    """Tests for MCPConfig."""

    def test_empty_config(self):
        """Test empty configuration."""
        config = MCPConfig()
        assert config.servers == []
        assert config.server is None
        assert config.auto_connect is True
        assert config.tool_name_prefix == "mcp_"

    def test_config_with_servers(self):
        """Test configuration with multiple servers."""
        config = MCPConfig(
            servers=[
                MCPServerConfig(
                    name="server1",
                    transport=TransportType.STDIO,
                    command="cmd1",
                ),
                MCPServerConfig(
                    name="server2",
                    transport=TransportType.SSE,
                    url="http://localhost:8080",
                    enabled=False,
                ),
            ]
        )
        assert len(config.servers) == 2
        enabled = config.get_enabled_servers()
        assert len(enabled) == 1
        assert enabled[0].name == "server1"

    def test_config_with_server_settings(self):
        """Test configuration with server settings."""
        config = MCPConfig(
            server=MCPServerSettings(
                mode=ServerMode.AGENT,
                transport=TransportType.STDIO,
            )
        )
        assert config.server is not None
        assert config.server.mode == ServerMode.AGENT
