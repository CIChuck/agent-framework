"""Real SDK subprocess and dated TLS peers exercise public refresh/adapter paths."""

import json
import sys

import pytest

from friday_mcp.client.adapter import MCPToolAdapter
from friday_mcp.client.base import MCPError, MCPToolExecutionError
from friday_mcp.client.protocol import ProtocolLimits
from friday_mcp.client.stdio import StdioMCPClient
from tests_mcp.client.test_http_interop import (
    FIXTURES,
    fixture_client,
    records,
    tls_material,
)


async def exercise_refresh(client, control, call):
    adapter = MCPToolAdapter(client)
    tools = await adapter.get_tools()
    old = next(tool for tool in tools if tool.original_name == "echo")
    snapshot = client.current_catalog_snapshot
    assert "synthetic" in await call(old)
    control.write_text("fail")
    with pytest.raises(MCPError):
        await adapter.get_tools(refresh=True)
    assert client.current_catalog_snapshot is None
    with pytest.raises(MCPToolExecutionError) as exc:
        await call(old)
    assert exc.value.failure_code == "catalog_unavailable"
    with pytest.raises(MCPError):
        await adapter.get_tools()
    assert adapter._tools_cache is None
    control.write_text("good")
    fresh = await adapter.get_tools(refresh=True)
    new = next(tool for tool in fresh if tool.original_name == "echo")
    assert client.current_catalog_snapshot.generation > snapshot.generation
    assert "synthetic" in await call(new)
    control.write_text("remove")
    assert all(
        tool.original_name != "echo" for tool in await adapter.get_tools(refresh=True)
    )
    with pytest.raises(MCPToolExecutionError):
        await call(new)
    control.write_text("good")
    await client.disconnect()
    await client.connect()
    reconnect = next(
        tool for tool in await adapter.get_tools() if tool.original_name == "echo"
    )
    with pytest.raises(MCPToolExecutionError):
        await call(new)
    assert "synthetic" in await call(reconnect)


@pytest.mark.asyncio
async def test_real_sdk_stdio_failed_removed_and_reconnected_catalog(tmp_path):
    control = tmp_path / "catalog-control"
    counter = tmp_path / "calls.jsonl"
    client = StdioMCPClient(
        "refresh-fixture",
        sys.executable,
        [str(FIXTURES / "modern_sdk_server.py")],
        env={
            "MCP_FIXTURE_CATALOG_CONTROL": str(control),
            "MCP_FIXTURE_COUNTER": str(counter),
        },
        cwd=tmp_path,
        protocol_profile="modern",
        limits=ProtocolLimits(timeout_seconds=3),
    )
    try:
        await client.connect()
        await exercise_refresh(
            client, control, lambda tool: tool.execute(text="synthetic")
        )
    finally:
        await client.disconnect()
    assert records(counter) == [{"tool": "echo"}] * 3
    assert client.outstanding_catalog_owners == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("modern", [True, False])
@pytest.mark.parametrize("mode", ["tls", "tls-sse"])
async def test_real_tls_refresh_failure_removal_reconnect_no_stale_calls(
    tmp_path, monkeypatch, modern, mode
):
    control = tmp_path / "catalog-control"
    context = tls_material(tmp_path)
    monkeypatch.setattr(
        "friday_mcp.client.http.ssl.create_default_context", lambda: context
    )
    monkeypatch.setenv("MCP_FIXTURE_CATALOG_CONTROL", str(control))
    async with fixture_client(tmp_path, modern=modern, mode=mode) as (
        client,
        process,
        counter,
    ):
        await exercise_refresh(
            client, control, lambda tool: tool.execute(text="synthetic")
        )
        assert client.outstanding_catalog_owners == 0
    log = records(counter)
    assert (
        sum(
            row.get("tool") == "echo" if modern else row.get("method") == "tools/call"
            for row in log
        )
        == 3
    )
    assert process.returncode is not None
    assert client.outstanding_http_owners == 0
    assert "secret" not in json.dumps(log)
