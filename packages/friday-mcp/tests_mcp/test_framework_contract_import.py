"""The existing MCP package can consume the shared WS-00 contracts."""

from friday_core.mcp import MCPClientLimits, MCPToolMetadata, normalize_mcp_tool_name

from friday_mcp.client.manager import MCPClientManager
from friday_mcp.config import MCPConfig


def test_shared_contract_import_does_not_cycle_through_friday_mcp() -> None:
    assert MCPClientManager(MCPConfig()).config.servers == []
    assert MCPClientLimits().max_servers == 8
    assert normalize_mcp_tool_name("filesystem", "read_file") == (
        "mcp_filesystem_read_file"
    )
    assert (
        MCPToolMetadata(
            canonical_name="mcp_filesystem_read_file",
            server_name="filesystem",
            original_name="read_file",
            transport="stdio",
            trust_level="local",
        ).provider
        == "mcp"
    )
