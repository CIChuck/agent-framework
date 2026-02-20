"""Pytest configuration and fixtures for friday-mcp tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from friday_mcp.config import (
    MCPConfig,
    MCPServerConfig,
    MCPServerSettings,
    ServerMode,
    TransportType,
)


@pytest.fixture
def stdio_server_config():
    """Create a test stdio server configuration."""
    return MCPServerConfig(
        name="test-server",
        transport=TransportType.STDIO,
        command="echo",
        args=["test"],
    )


@pytest.fixture
def sse_server_config():
    """Create a test SSE server configuration."""
    return MCPServerConfig(
        name="test-sse-server",
        transport=TransportType.SSE,
        url="http://localhost:8080/sse",
    )


@pytest.fixture
def mcp_config(stdio_server_config):
    """Create a test MCP configuration."""
    return MCPConfig(
        servers=[stdio_server_config],
        tool_name_prefix="mcp_",
    )


@pytest.fixture
def agent_server_settings():
    """Create agent mode server settings."""
    return MCPServerSettings(
        mode=ServerMode.AGENT,
        transport=TransportType.STDIO,
        agent_tool_name="friday_agent",
        expose_prompts=True,
        expose_resources=True,
    )


@pytest.fixture
def tools_server_settings():
    """Create tools mode server settings."""
    return MCPServerSettings(
        mode=ServerMode.TOOLS,
        transport=TransportType.SSE,
        host="127.0.0.1",
        port=8080,
        tool_prefix="friday_",
    )


@pytest.fixture
def mock_mcp_client():
    """Create a mock MCP client for testing adapters."""
    client = AsyncMock()
    client.name = "mock-server"
    client.list_tools = AsyncMock(
        return_value=[
            {
                "name": "test_tool",
                "description": "A test tool",
                "inputSchema": {
                    "type": "object",
                    "properties": {"arg": {"type": "string"}},
                    "required": ["arg"],
                },
            },
            {
                "name": "another_tool",
                "description": "Another test tool",
                "inputSchema": {
                    "type": "object",
                    "properties": {"value": {"type": "integer"}},
                },
            },
        ]
    )
    client.call_tool = AsyncMock(return_value="test result")
    return client


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing agent mode."""
    agent = AsyncMock()
    agent.run = AsyncMock(return_value="Agent response")
    return agent


@pytest.fixture
def mock_profile():
    """Create a mock agent profile for testing."""
    profile = MagicMock()
    profile.name = "TestAgent"
    profile.role = "Test Role"
    profile.goal = "Test Goal"
    profile.render_system_prompt = MagicMock(
        return_value="You are TestAgent, a Test Role."
    )
    return profile


@pytest.fixture
def mock_tool():
    """Create a mock tool for testing."""
    tool = MagicMock()
    tool.name = "mock_tool"
    tool.description = "A mock tool for testing"
    tool.parameters_schema = {
        "type": "object",
        "properties": {"input": {"type": "string"}},
        "required": ["input"],
    }
    tool.execute = AsyncMock(return_value="mock result")
    return tool


@pytest.fixture
def mock_registry(mock_tool):
    """Create a mock tool registry for testing tools mode."""
    registry = MagicMock()
    registry.list_tools = MagicMock(return_value=[mock_tool])
    registry.get = MagicMock(return_value=mock_tool)
    return registry
