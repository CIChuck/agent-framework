"""Real owned stdio children: official SDK and independent legacy peer."""

import asyncio
import json
import sys
from importlib.metadata import version
from pathlib import Path

import pytest

from friday_mcp.client.base import MCPError
from friday_mcp.client.protocol import (
    LEGACY_VERSION,
    MODERN_VERSION,
    ProtocolFailure,
    ProtocolLimits,
)
from friday_mcp.client.stdio import StdioMCPClient

FIXTURES = Path(__file__).parents[1] / "fixtures"

DELAYED_MODERN_PEER = r"""
import json
import os
import sys
import time
from pathlib import Path

mode = sys.argv[1]
delay = float(sys.argv[2])
modern_version = sys.argv[3]
counter = Path(os.environ["MCP_FIXTURE_COUNTER"])
discoveries = 0

for line in sys.stdin:
    request = json.loads(line)
    method = request.get("method")
    with counter.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"method": method}) + "\n")
    if "id" not in request:
        continue
    if method == "server/discover":
        discoveries += 1
        if mode in {"unavailable", "other-legacy-error"}:
            continue
        if mode == "rejected-modern":
            response = {"error": {"code": -32601, "message": "No discovery"}}
        else:
            if discoveries == 1:
                time.sleep(delay)
            response = {
                "result": {
                    "resultType": "complete",
                    "supportedVersions": [modern_version],
                    "capabilities": {"tools": {}},
                    "ttlMs": 0,
                    "cacheScope": "private",
                }
            }
    elif method == "initialize":
        code = -32021 if mode == "other-legacy-error" else -32022
        response = {"error": {"code": code, "message": "Synthetic handshake error"}}
    else:
        response = {"error": {"code": -32601, "message": "Unknown method"}}
    print(json.dumps({"jsonrpc": "2.0", "id": request["id"], **response}), flush=True)
"""


def client_for(tmp_path, *, modern=True, profile=None, mode="good", timeout=3):
    fixture = FIXTURES / (
        "modern_sdk_server.py" if modern else "legacy_protocol_server.py"
    )
    return StdioMCPClient(
        "synthetic",
        sys.executable,
        [str(fixture)] + ([] if modern else [mode]),
        env={"MCP_FIXTURE_COUNTER": str(tmp_path / "counter.jsonl")},
        cwd=tmp_path,
        protocol_profile=profile or ("modern" if modern else "legacy"),
        limits=ProtocolLimits(timeout_seconds=timeout),
    )


def records(tmp_path):
    path = tmp_path / "counter.jsonl"
    return (
        [json.loads(line) for line in path.read_text().splitlines()]
        if path.exists()
        else []
    )


async def disconnect_owned(client, transport, process):
    await client.disconnect()
    assert process.returncode is not None
    assert transport._process is None
    assert transport._stderr_task is None
    assert transport._stdout_read_task is None
    assert transport._stdout_drain_task is None
    assert transport._process_wait_task is None
    assert transport._cleanup_task is None
    assert client._receive_task is None
    assert not client._pending_requests
    assert not client._control_tasks
    assert not client._exchange_tasks


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode,timeout,delay",
    [
        ("late-modern", 4.0, 2.3),
        ("unavailable", 2.0, 0.0),
        ("rejected-modern", 2.0, 0.0),
        ("other-legacy-error", 2.0, 0.0),
    ],
)
async def test_auto_timeout_then_legacy_version_rejection_retries_only_modern(
    tmp_path, mode, timeout, delay
):
    client = StdioMCPClient(
        "synthetic-delayed-modern",
        sys.executable,
        ["-u", "-c", DELAYED_MODERN_PEER, mode, str(delay), MODERN_VERSION],
        env={"MCP_FIXTURE_COUNTER": str(tmp_path / "counter.jsonl")},
        cwd=tmp_path,
        protocol_profile="auto",
        limits=ProtocolLimits(timeout_seconds=timeout),
    )
    original_request = client._request
    outcomes = []
    owned = []

    async def observe_request(method, params, timeout=None):
        if not owned:
            transport = client._transport
            owned.extend((transport, transport._process))
        try:
            result = await original_request(method, params, timeout=timeout)
        except TimeoutError:
            outcomes.append((method, "timeout"))
            raise
        except MCPError as exc:
            outcomes.append((method, exc.code))
            raise
        outcomes.append((method, "success"))
        return result

    client._request = observe_request
    try:
        if mode == "unavailable":
            with pytest.raises(TimeoutError):
                await client.connect()
        elif mode in {"rejected-modern", "other-legacy-error"}:
            with pytest.raises(MCPError) as caught:
                await client.connect()
            assert caught.value.code == (
                -32021 if mode == "other-legacy-error" else -32022
            )
        else:
            await client.connect()
            assert client.negotiated_version == MODERN_VERSION
    finally:
        await client.disconnect()
        await disconnect_owned(client, *owned)
        assert "tools/call" not in [r["method"] for r in records(tmp_path)]
    if mode == "rejected-modern":
        assert outcomes == [("server/discover", -32601), ("initialize", -32022)]
    elif mode == "other-legacy-error":
        assert outcomes == [("server/discover", "timeout"), ("initialize", -32021)]
    elif mode == "unavailable":
        assert outcomes[:2] == [
            ("server/discover", "timeout"),
            ("initialize", -32022),
        ]
        # The outer connection deadline may cancel the retry before its
        # request-scoped timeout reports its own outcome.
        assert outcomes[2:] in ([], [("server/discover", "timeout")])
    else:
        assert outcomes == [
            ("server/discover", "timeout"),
            ("initialize", -32022),
            ("server/discover", "success"),
        ]
    methods = [r["method"] for r in records(tmp_path)]
    assert methods.count("server/discover") == (
        2 if mode in {"late-modern", "unavailable"} else 1
    )
    assert methods.count("initialize") == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("profile", ["modern", "auto"])
async def test_official_sdk_230_real_stdio_catalog_text_structured_and_reaping(
    tmp_path, profile
):
    assert version("mcp") == "2.3.0"
    client = client_for(tmp_path, profile=profile)
    try:
        await client.connect()
        transport = client._transport
        process = transport._process
        assert client.negotiated_version == MODERN_VERSION
        assert {t["name"] for t in await client.list_tools()} == {
            "echo",
            "structured",
            "slow",
            "drop",
        }
        result = await client.call_tool("echo", {"text": "synthetic-text"})
        # SDK may accompany text with structured output; both must survive.
        assert "synthetic-text" in result
        result = json.loads(await client.call_tool("structured", {"value": 9}))
        assert result["structuredContent"] == {"value": 9}
        assert result["content"]
    finally:
        await client.disconnect()
    await disconnect_owned(client, transport, process)
    assert records(tmp_path) == [{"tool": "echo"}, {"tool": "structured"}]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "profile,mode",
    [
        ("legacy", "good"),
        ("auto", "good"),
        ("auto", "ignore-probe"),
        ("auto", "late-probe"),
    ],
)
async def test_exact_legacy_revision_text_api_and_bounded_auto_fallback(
    tmp_path, profile, mode
):
    client = client_for(tmp_path, modern=False, profile=profile, mode=mode, timeout=0.3)
    try:
        await client.connect()
        transport = client._transport
        process = transport._process
        assert client.negotiated_version == LEGACY_VERSION
        assert await client.list_tools() == [
            {"name": "echo", "inputSchema": {"type": "object"}}
        ]
        assert (
            await client.call_tool("echo", {"text": "legacy-exact"}) == "legacy-exact"
        )
    finally:
        await client.disconnect()
    await disconnect_owned(client, transport, process)
    methods = [r["method"] for r in records(tmp_path)]
    assert methods.count("initialize") == 1
    assert methods.count("server/discover") == (1 if profile == "auto" else 0)


@pytest.mark.asyncio
@pytest.mark.parametrize("modern", [True, False])
async def test_ambiguous_call_executes_once_with_no_mutation_replay(tmp_path, modern):
    client = client_for(tmp_path, modern=modern)
    try:
        await client.connect()
        transport = client._transport
        process = transport._process
        with pytest.raises(ConnectionError, match="MCP transport closed"):
            await client.call_tool("drop", {})
    finally:
        await client.disconnect()
    await disconnect_owned(client, transport, process)
    count = sum(
        r.get("tool") == "drop" if modern else r.get("method") == "tools/call"
        for r in records(tmp_path)
    )
    assert count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel", [True, False])
async def test_issued_stdio_call_cancel_or_timeout_notifies_and_reaps(tmp_path, cancel):
    client = client_for(tmp_path, modern=False, timeout=0.12)
    try:
        await client.connect()
        transport = client._transport
        process = transport._process
        task = asyncio.create_task(client.call_tool("slow", {}))
        if cancel:
            await asyncio.sleep(0.03)
            task.cancel()
        with pytest.raises(asyncio.CancelledError if cancel else TimeoutError):
            await task
        await asyncio.sleep(0.02)
        methods = [r["method"] for r in records(tmp_path)]
        assert methods.count("tools/call") == 1
        assert methods.count("notifications/cancelled") == 1
    finally:
        await client.disconnect()
    await disconnect_owned(client, transport, process)


@pytest.mark.asyncio
async def test_oversized_frame_rejected_before_json_decode_then_reaped(tmp_path):
    client = client_for(tmp_path, modern=False, mode="oversized")
    client.limits = ProtocolLimits(frame_bytes=65536)
    try:
        await client.connect()
        transport = client._transport
        process = transport._process
        with pytest.raises(ConnectionError):
            await client.call_tool("echo", {})
    finally:
        await client.disconnect()
    await disconnect_owned(client, transport, process)


@pytest.mark.asyncio
async def test_bad_legacy_version_partial_connection_is_released(tmp_path):
    client = client_for(tmp_path, modern=False, mode="bad-version")
    with pytest.raises(ProtocolFailure, match="Unsupported"):
        await client.connect()
    assert client._transport is None
    assert client._receive_task is None
    assert not client._pending_requests
    assert "notifications/initialized" not in [r["method"] for r in records(tmp_path)]
