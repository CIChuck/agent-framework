"""Pinned official Client over real Friday subprocess stdio and verified TLS HTTP."""

import asyncio
import json
import os
import socket
import sys
from contextlib import asynccontextmanager
from importlib.metadata import version
from pathlib import Path

import httpx
import httpx2
import pytest
from mcp.client import Client
from mcp.client.stdio import StdioServerParameters
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.exceptions import MCPError

from friday_mcp.server.protocol import VERSION
from tests_mcp.client.test_http_interop import tls_material
from tests_mcp.server.test_modern_protocol import rpc
from tests_mcp.server.test_streamable_http import headers

FIXTURE = Path(__file__).parents[1] / "fixtures/friday_modern_tools_server.py"


def rows(counter):
    return (
        [json.loads(line) for line in counter.read_text().splitlines()]
        if counter.exists()
        else []
    )


def official_client(transport):
    return Client(
        transport,
        mode=VERSION,
        cache=None,
        sampling_callback=None,
        list_roots_callback=None,
        elicitation_callback=None,
        logging_callback=None,
        log_level=None,
        extensions=None,
        read_timeout_seconds=2,
    )


async def exercise_sdk(client, counter):
    discovery = await client.session.send_discover(VERSION)
    assert discovery["supportedVersions"] == [VERSION] and discovery[
        "capabilities"
    ] == {"tools": {}}
    assert discovery["ttlMs"] == 0 and discovery["cacheScope"] == "private"
    tools = await client.list_tools()
    assert tools.ttl_ms == 0 and tools.cache_scope == "private"
    assert [t.name for t in tools.tools] == ["echo"]
    result = await client.call_tool("echo", {"text": "Hello, 世界"})
    assert (
        result.structured_content == {"text": "Hello, 世界"}
        and result.result_type == "complete"
    )
    failure = await client.call_tool("echo", {"fail": True})
    assert failure.is_error is True and "synthetic-private-exception" not in str(
        failure
    )
    with pytest.raises(MCPError) as invalid:
        await client.session.send_discover("unsupported")
    assert invalid.value.error.code == -32022
    from mcp_types import UnsupportedProtocolVersionErrorData

    decoded_error = UnsupportedProtocolVersionErrorData.model_validate(
        invalid.value.error.data
    )
    assert (
        decoded_error.supported == [VERSION]
        and decoded_error.requested == "unsupported"
    )
    requests = [r for r in rows(counter) if r["event"] == "request"]
    assert any(
        r["method"] == "server/discover" and r["version"] == VERSION for r in requests
    )
    assert all(r["has_capabilities"] for r in requests)
    assert all(r["method"] != "initialize" for r in requests)
    assert sum(r["event"] == "handler_start" for r in rows(counter)) == 2


@pytest.mark.asyncio
async def test_official_client_230_real_stdio(tmp_path):
    assert version("mcp") == version("mcp-types") == "2.3.0"
    counter = tmp_path / "sdk-stdio.jsonl"
    parameters = StdioServerParameters(
        command=sys.executable,
        args=[str(FIXTURE), "stdio", str(counter)],
        env=dict(os.environ),
        cwd=str(tmp_path),
    )
    async with official_client(parameters) as client:
        await exercise_sdk(client, counter)
    for _ in range(100):
        if rows(counter) and rows(counter)[-1]["event"] == "server_stopped":
            break
        await asyncio.sleep(0.01)
    assert rows(counter)[-1] == {"event": "server_stopped", "active": 0}


@asynccontextmanager
async def tls_friday(tmp_path, mode):
    context = tls_material(tmp_path)
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    counter = tmp_path / "sdk-http.jsonl"
    ready = tmp_path / "ready"
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        str(FIXTURE),
        mode,
        str(counter),
        str(port),
        str(tmp_path / "fixture-cert.pem"),
        str(tmp_path / "fixture-key.pem"),
        str(ready),
        cwd=tmp_path,
        env=dict(os.environ),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        for _ in range(300):
            if ready.exists():
                break
            if process.returncode is not None:
                raise RuntimeError("Synthetic Friday TLS child exited")
            await asyncio.sleep(0.01)
        assert ready.exists()
        yield f"https://127.0.0.1:{port}/mcp", context, counter, process
    finally:
        if process.returncode is None:
            process.terminate()
        try:
            await asyncio.wait_for(process.wait(), 2)
        except TimeoutError:
            process.kill()
            await process.wait()
            raise
        stdout, stderr = await process.communicate()
        assert process.returncode == 0, stderr.decode()
        assert stdout == b""
        assert b"synthetic-private-exception" not in stderr


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["json", "sse"])
async def test_official_client_230_real_verified_tls_json_sse(tmp_path, mode):
    async with tls_friday(tmp_path, mode) as (url, context, counter, process):
        async with httpx2.AsyncClient(
            verify=context, trust_env=False, follow_redirects=False
        ) as http:
            transport = streamable_http_client(
                url, http_client=http, terminate_on_close=False
            )
            async with official_client(transport) as client:
                await exercise_sdk(client, counter)
        # Raw negatives bypass SDK's automatic HeaderMismatch relist/retry behavior.
        before = sum(r["event"] == "handler_start" for r in rows(counter))
        async with httpx.AsyncClient(
            verify=context, trust_env=False, follow_redirects=False
        ) as raw:
            response = await raw.post(
                url,
                headers={**headers(), "Mcp-Param-Text": "wrong"},
                content=rpc(
                    "tools/call",
                    params={"name": "echo", "arguments": {"text": "actual"}},
                ),
            )
            assert (
                response.status_code == 400
                and response.json()["error"]["code"] == -32020
            )
        assert sum(r["event"] == "handler_start" for r in rows(counter)) == before
    assert process.returncode == 0
    assert rows(counter)[-1] == {"event": "server_stopped", "active": 0}


@pytest.mark.asyncio
async def test_official_stdio_cancel_owned_call_then_continue(tmp_path):
    counter = tmp_path / "sdk-cancel.jsonl"
    parameters = StdioServerParameters(
        command=sys.executable,
        args=[str(FIXTURE), "stdio", str(counter)],
        env=dict(os.environ),
        cwd=str(tmp_path),
    )
    async with official_client(parameters) as client:
        held = asyncio.create_task(client.call_tool("echo", {"hold": True}))
        for _ in range(100):
            if any(r["event"] == "handler_start" for r in rows(counter)):
                break
            await asyncio.sleep(0.01)
        assert sum(r["event"] == "handler_start" for r in rows(counter)) == 1
        held.cancel()
        await asyncio.gather(held, return_exceptions=True)
        for _ in range(100):
            if any(r["event"] == "handler_terminal" for r in rows(counter)):
                break
            await asyncio.sleep(0.01)
        assert sum(r["event"] == "handler_terminal" for r in rows(counter)) == 1
        assert (
            await client.call_tool("echo", {"text": "continued"})
        ).structured_content == {"text": "continued"}
    assert sum(r["event"] == "handler_start" for r in rows(counter)) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["json", "sse"])
async def test_real_tls_disconnect_cancel_only_owned_call(tmp_path, mode):
    async with tls_friday(tmp_path, mode) as (url, context, counter, process):
        async with httpx.AsyncClient(verify=context, trust_env=False) as client:
            held = asyncio.create_task(
                client.post(
                    url,
                    headers=headers(),
                    content=rpc(
                        "tools/call",
                        params={"name": "echo", "arguments": {"hold": True}},
                    ),
                )
            )
            for _ in range(100):
                if any(r["event"] == "handler_start" for r in rows(counter)):
                    break
                await asyncio.sleep(0.01)
            assert sum(r["event"] == "handler_start" for r in rows(counter)) == 1
            held.cancel()
            await asyncio.gather(held, return_exceptions=True)
            for _ in range(100):
                if any(r["event"] == "handler_terminal" for r in rows(counter)):
                    break
                await asyncio.sleep(0.01)
            assert sum(r["event"] == "handler_terminal" for r in rows(counter)) == 1
            response = await client.post(
                url, headers=headers("server/discover", name=None), content=rpc()
            )
            assert response.status_code == 200
        assert sum(r["event"] == "handler_start" for r in rows(counter)) == 1
    assert process.returncode == 0 and rows(counter)[-1]["active"] == 0


@pytest.mark.asyncio
async def test_real_tls_untrusted_certificate_zero_wire_requests(tmp_path):
    import ssl

    async with tls_friday(tmp_path, "json") as (url, _, counter, process):
        no_trust = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        async with httpx.AsyncClient(verify=no_trust, trust_env=False) as client:
            with pytest.raises(httpx.ConnectError):
                await client.post(
                    url,
                    headers=headers(),
                    content=rpc("tools/call", params={"name": "echo"}),
                )
        assert rows(counter) == []
    assert process.returncode == 0
