"""Tests for MCP tool adapter."""

import pytest

from friday_mcp.client.adapter import MCPToolAdapter, MCPToolWrapper


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
