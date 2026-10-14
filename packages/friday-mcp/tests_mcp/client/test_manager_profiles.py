"""Public managed factories, compatibility and retained cleanup ownership."""

import asyncio
from unittest.mock import AsyncMock

import pytest

from friday_mcp.client import (
    MCPClientBase,
    MCPClientManager,
    MCPManagedServer,
    SSEMCPClient,
    StdioMCPClient,
)
from friday_mcp.config import MCPConfig, MCPServerConfig, TransportType


class OwnedClient(MCPClientBase):
    def __init__(self, name):
        super().__init__(name)
        self.failure = None
        self.cleanup_failure = False
        self.at_connect = None
        self.disconnects = 0

    async def _create_transport(self):
        return None

    async def connect(self):
        if self.at_connect:
            self.at_connect()
        if self.failure:
            raise self.failure
        self._connected = True

    async def disconnect(self):
        self.disconnects += 1
        if self.cleanup_failure:
            raise RuntimeError("synthetic cleanup failure")
        self._connected = False

    async def list_tools(self):
        return [
            {
                "name": "Exact.Name",
                "description": "synthetic",
                "inputSchema": {"type": "object"},
            }
        ]


@pytest.mark.asyncio
async def test_ordered_distinct_public_factories_and_exact_adapter_routing():
    first, second = OwnedClient("one"), OwnedClient("two")
    def off():
        pytest.fail("Disabled factory invoked")
    manager = MCPClientManager(
        MCPConfig(servers=[]),
        managed_servers=[
            MCPManagedServer("one", True, lambda: first),
            MCPManagedServer("off", False, off),
            MCPManagedServer("two", True, lambda: second),
        ],
    )
    first.at_connect = lambda: manager.get_client("one") is first or pytest.fail(
        "Adoption was late"
    )
    first.call_tool = AsyncMock(return_value="safe")
    assert await manager.connect_all() == {"one": True, "off": False, "two": True}
    assert manager.connected_servers == ["one", "two"]
    assert await manager.call_tool("mcp_one_Exact.Name", {}) == "safe"
    first.call_tool.assert_awaited_once_with("Exact.Name", {})
    await manager.disconnect_all()
    await manager.disconnect_all()
    assert first.disconnects == second.disconnects == 1
    assert manager.connected_servers == []


@pytest.mark.parametrize(
    "entries,legacy",
    [
        ([MCPManagedServer("same", True, lambda: None)] * 2, False),
        ([object()], False),
        ([MCPManagedServer("one", True, lambda: None)], True),
    ],
)
def test_ambiguous_duplicate_malformed_entries_reject_before_invocation(
    entries, legacy
):
    config = MCPConfig(
        servers=[MCPServerConfig(name="local", command="fake")] if legacy else []
    )
    with pytest.raises(ValueError):
        MCPClientManager(config, managed_servers=entries)


@pytest.mark.parametrize(
    "values", [("", True, lambda: None), ("one", 1, lambda: None), ("one", True, None)]
)
def test_managed_record_validates_shape(values):
    with pytest.raises(ValueError):
        MCPManagedServer(*values)


@pytest.mark.asyncio
@pytest.mark.parametrize("cancelled", [False, True])
async def test_partial_adoption_preserves_primary_and_retains_incomplete_owner(
    cancelled,
):
    client = OwnedClient("one")
    client.failure = asyncio.CancelledError() if cancelled else ValueError("primary")
    client.cleanup_failure = True
    manager = MCPClientManager(
        MCPConfig(), managed_servers=[MCPManagedServer("one", True, lambda: client)]
    )
    with pytest.raises(type(client.failure)) as failure:
        await manager.connect_or_raise("one")
    assert failure.value is client.failure and manager.get_client("one") is client
    with pytest.raises(RuntimeError):
        await manager.disconnect_all()
    client.cleanup_failure = False
    await manager.disconnect_all()
    assert not manager.connected_servers


def test_default_manager_keeps_legacy_stdio_and_sse_public_api():
    manager = MCPClientManager(MCPConfig())
    assert isinstance(
        manager._create_client(MCPServerConfig(name="local", command="fake")),
        StdioMCPClient,
    )
    assert isinstance(
        manager._create_client(
            MCPServerConfig(
                name="remote",
                transport=TransportType.SSE,
                url="https://example.com/sse",
            )
        ),
        SSEMCPClient,
    )
