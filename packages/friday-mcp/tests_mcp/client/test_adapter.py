# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Tests for MCP tool adapter."""

import pytest
from friday_core.interfaces.tools import ToolDefinition
from friday_core.mcp import MCPToolMetadata

from friday_mcp.client.adapter import (
    MCPToolAdapter,
    MCPToolWrapper,
    MCPValidatedDefinition,
)


@pytest.mark.asyncio
async def test_validated_wrapper_full_protocol_snapshot_and_exact_route(
    mock_mcp_client,
):
    metadata = MCPToolMetadata(
        canonical_name="mcp_peer_read_file",
        server_name="peer",
        original_name="Read.File",
        transport="stdio",
        trust_level="local",
        discovery_state="discovered",
        schema_sanitization_state="sanitized",
        filter_state="included",
    )
    definition = MCPValidatedDefinition(
        "Safe description", '{"type":"object","properties":{"path":{"type":"string"}}}'
    )
    wrapper = MCPToolWrapper.from_validated(mock_mcp_client, metadata, definition)
    assert isinstance(wrapper, ToolDefinition)
    assert wrapper.name == "mcp_peer_read_file"
    assert wrapper.category == "mcp"
    tags = wrapper.tags
    tags.append("unsafe")
    exported = wrapper.to_schema("openai")
    exported["function"]["parameters"]["properties"]["path"]["type"] = "number"
    assert wrapper.parameters_schema["properties"]["path"]["type"] == "string"
    assert wrapper.tags == ["mcp"]
    await wrapper.execute(path="safe.txt")
    mock_mcp_client.call_tool.assert_awaited_once_with(
        "Read.File", {"path": "safe.txt"}
    )
    assert "Read.File" not in repr(wrapper)


def test_legacy_wrapper_snapshots_input_and_each_export(mock_mcp_client):
    source = {
        "name": "probe",
        "inputSchema": {"type": "object", "properties": {"x": {"type": "string"}}},
    }
    wrapper = MCPToolWrapper(mock_mcp_client, source, "prefix_")
    source["name"] = "rerouted"
    source["inputSchema"]["properties"]["x"]["type"] = "number"
    wrapper.parameters_schema["properties"]["x"]["type"] = "boolean"
    assert wrapper.name == "prefix_probe"
    assert wrapper.parameters_schema["properties"]["x"]["type"] == "string"


def test_unchecked_metadata_cannot_use_validated_path(mock_mcp_client):
    metadata = MCPToolMetadata(
        canonical_name="mcp_peer_probe",
        server_name="peer",
        original_name="probe",
        transport="stdio",
        trust_level="local",
    )
    with pytest.raises(ValueError, match="checked metadata"):
        MCPToolWrapper.from_validated(
            mock_mcp_client,
            metadata,
            MCPValidatedDefinition("Safe", '{"type":"object"}'),
        )


class TestMCPToolWrapper:
    """Tests for MCPToolWrapper."""

    def test_wrapper_name_no_prefix(self, mock_mcp_client):
        """Test tool name without prefix."""
        tool_def = {
            "name": "read_file",
            "description": "Read a file",
            "inputSchema": {"type": "object", "properties": {}},
        }
        wrapper = MCPToolWrapper(mock_mcp_client, tool_def)
        assert wrapper.name == "read_file"

    def test_wrapper_name_with_prefix(self, mock_mcp_client):
        """Test tool name with prefix."""
        tool_def = {
            "name": "read_file",
            "description": "Read a file",
            "inputSchema": {"type": "object", "properties": {}},
        }
        wrapper = MCPToolWrapper(mock_mcp_client, tool_def, name_prefix="mcp_fs_")
        assert wrapper.name == "mcp_fs_read_file"

    def test_wrapper_description(self, mock_mcp_client):
        """Test tool description."""
        tool_def = {
            "name": "test",
            "description": "A test tool",
            "inputSchema": {"type": "object"},
        }
        wrapper = MCPToolWrapper(mock_mcp_client, tool_def)
        assert wrapper.description == "A test tool"

    def test_wrapper_description_fallback(self, mock_mcp_client):
        """Test tool description fallback."""
        tool_def = {"name": "test", "inputSchema": {"type": "object"}}
        wrapper = MCPToolWrapper(mock_mcp_client, tool_def)
        assert "MCP tool:" in wrapper.description

    def test_wrapper_parameters_schema(self, mock_mcp_client):
        """Test parameters schema conversion."""
        tool_def = {
            "name": "test",
            "description": "Test",
            "inputSchema": {
                "type": "object",
                "properties": {"arg": {"type": "string"}},
                "required": ["arg"],
            },
        }
        wrapper = MCPToolWrapper(mock_mcp_client, tool_def)
        schema = wrapper.parameters_schema
        assert schema["type"] == "object"
        assert "arg" in schema["properties"]
        assert schema["required"] == ["arg"]

    @pytest.mark.asyncio
    async def test_wrapper_execute(self, mock_mcp_client):
        """Test tool execution."""
        tool_def = {
            "name": "test_tool",
            "description": "Test",
            "inputSchema": {"type": "object"},
        }
        wrapper = MCPToolWrapper(mock_mcp_client, tool_def)
        result = await wrapper.execute(arg="value")

        mock_mcp_client.call_tool.assert_called_once_with("test_tool", {"arg": "value"})
        assert result == "test result"

    def test_wrapper_to_schema(self, mock_mcp_client):
        """Test to_schema method."""
        tool_def = {
            "name": "test",
            "description": "A test",
            "inputSchema": {"type": "object", "properties": {}},
        }
        wrapper = MCPToolWrapper(mock_mcp_client, tool_def, name_prefix="pre_")
        schema = wrapper.to_schema()

        assert schema["name"] == "pre_test"
        assert schema["description"] == "A test"
        assert "parameters" in schema


class TestMCPToolAdapter:
    """Tests for MCPToolAdapter."""

    @pytest.mark.asyncio
    async def test_get_tools(self, mock_mcp_client):
        """Test getting tools from adapter."""
        adapter = MCPToolAdapter(mock_mcp_client, prefix="mcp_")
        tools = await adapter.get_tools()

        assert len(tools) == 2
        assert tools[0].name == "mcp_test_tool"
        assert tools[1].name == "mcp_another_tool"

    @pytest.mark.asyncio
    async def test_get_tools_caching(self, mock_mcp_client):
        """Test that tools are cached."""
        adapter = MCPToolAdapter(mock_mcp_client)

        await adapter.get_tools()
        await adapter.get_tools()

        # Should only call list_tools once due to caching
        assert mock_mcp_client.list_tools.call_count == 1

    @pytest.mark.asyncio
    async def test_get_tools_refresh(self, mock_mcp_client):
        """Test refreshing tools cache."""
        adapter = MCPToolAdapter(mock_mcp_client)

        await adapter.get_tools()
        await adapter.get_tools(refresh=True)

        assert mock_mcp_client.list_tools.call_count == 2

    @pytest.mark.asyncio
    async def test_get_tool_by_name(self, mock_mcp_client):
        """Test getting a specific tool by name."""
        adapter = MCPToolAdapter(mock_mcp_client, prefix="mcp_")
        tool = await adapter.get_tool("mcp_test_tool")

        assert tool is not None
        assert tool.name == "mcp_test_tool"

    @pytest.mark.asyncio
    async def test_get_tool_not_found(self, mock_mcp_client):
        """Test getting non-existent tool."""
        adapter = MCPToolAdapter(mock_mcp_client)
        tool = await adapter.get_tool("nonexistent")

        assert tool is None

    def test_adapt_single(self, mock_mcp_client):
        """Test adapting a single tool definition."""
        adapter = MCPToolAdapter(mock_mcp_client, prefix="test_")
        tool_def = {
            "name": "my_tool",
            "description": "My tool",
            "inputSchema": {"type": "object"},
        }
        tool = adapter.adapt(tool_def)

        assert tool.name == "test_my_tool"

    def test_adapt_many(self, mock_mcp_client):
        """Test adapting multiple tool definitions."""
        adapter = MCPToolAdapter(mock_mcp_client)
        tool_defs = [
            {"name": "tool1", "description": "Tool 1", "inputSchema": {}},
            {"name": "tool2", "description": "Tool 2", "inputSchema": {}},
        ]
        tools = adapter.adapt_many(tool_defs)

        assert len(tools) == 2

    def test_clear_cache(self, mock_mcp_client):
        """Test clearing the tools cache."""
        adapter = MCPToolAdapter(mock_mcp_client)
        adapter._tools_cache = []  # Simulate cached tools

        adapter.clear_cache()

        assert adapter._tools_cache is None
