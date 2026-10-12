"""Actual HTTP sockets and child ownership, official SDK and independent peer."""

import asyncio
import ipaddress
import json
import os
import socket
import ssl
import sys
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from importlib.metadata import version
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

from friday_mcp.client.base import MCPToolExecutionError
from friday_mcp.client.http import StreamableHTTPMCPClient
from friday_mcp.client.http_policy import HTTPEndpointPolicy
from friday_mcp.client.http_protocol import HTTP_COMPAT_VERSION
from friday_mcp.client.protocol import MODERN_VERSION, ProtocolFailure, ProtocolLimits

FIXTURES = Path(__file__).parents[1] / "fixtures"


def records(path):
    return (
        [json.loads(line) for line in path.read_text().splitlines()]
        if path.exists()
        else []
    )


@asynccontextmanager
async def fixture_client(tmp_path, *, modern=True, mode="json"):
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    counter = tmp_path / "counter.jsonl"
    environment = dict(
        os.environ
    )  # Parent is the already allowlisted guard environment.
    environment["MCP_FIXTURE_COUNTER"] = str(counter)
    if mode.startswith("tls"):
        environment["MCP_FIXTURE_TLS_CERT"] = str(tmp_path / "fixture-cert.pem")
        environment["MCP_FIXTURE_TLS_KEY"] = str(tmp_path / "fixture-key.pem")
    script = FIXTURES / ("http_sdk_server.py" if modern else "http_compat_server.py")
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        str(script),
        str(port),
        mode,
        cwd=tmp_path,
        env=environment,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    client = StreamableHTTPMCPClient(
        f"{'https' if mode.startswith('tls') else 'http'}://127.0.0.1:{port}/mcp",
        protocol_version=MODERN_VERSION if modern else HTTP_COMPAT_VERSION,
        endpoint_policy=HTTPEndpointPolicy(("127.0.0.1",), (port,), True),
        limits=ProtocolLimits(timeout_seconds=2),
    )
    try:
        deadline = asyncio.get_running_loop().time() + 5
        while True:
            try:
                await client.connect()
                break
            except (ProtocolFailure, TimeoutError):
                if (
                    process.returncode is not None
                    or asyncio.get_running_loop().time() >= deadline
                    or mode == "wrong-version"
                    or (
                        mode.startswith("tls")
                        and any(r["method"] == "initialize" for r in records(counter))
                    )
                ):
                    raise
                await asyncio.sleep(0.05)
        yield client, process, counter
    finally:
        try:
            await client.disconnect()
        finally:
            if process.returncode is None:
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), 2)
                except TimeoutError:
                    process.kill()
                    await process.wait()
        assert process.returncode is not None
        assert client._pool is None and client.outstanding_http_owners == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["json", "sse"])
async def test_official_sdk_230_modern_real_http_headers_results_and_owned_cleanup(
    tmp_path, mode
):
    assert version("mcp") == "2.3.0"
    async with fixture_client(tmp_path, mode=mode) as (client, process, counter):
        assert client.negotiated_version == MODERN_VERSION
        assert {t["name"] for t in await client.list_tools()} == {
            "echo",
            "structured",
            "slow",
            "drop",
        }
        for text in ("synthetic-text", "雪\nline", "=?base64?literal?="):
            result = await client.call_tool("echo", {"text": text})
            assert (
                text in result
                or text in json.loads(result)["structuredContent"].values()
            )
        structured = json.loads(await client.call_tool("structured", {"value": 9}))
        assert structured["structuredContent"] == {"value": 9}
        assert client._session_id is None
    assert records(counter) == [{"tool": "echo"}] * 3 + [{"tool": "structured"}]


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["good", "sse", "server-request"])
async def test_independent_2025_http_session_text_and_unsupported_request(
    tmp_path, mode
):
    async with fixture_client(tmp_path, modern=False, mode=mode) as (
        client,
        process,
        counter,
    ):
        assert client.negotiated_version == HTTP_COMPAT_VERSION
        assert {t["name"] for t in await client.list_tools()} == {
            "echo",
            "drop",
            "slow",
        }
        assert (
            await client.call_tool("echo", {"text": "compat-exact"}) == "compat-exact"
        )
    log = records(counter)
    assert log[0] == {"method": "initialize", "verb": "POST", "has_session": False}
    assert all(r["has_session"] for r in log[1:])
    assert log[-1]["verb"] == "DELETE"
    if mode == "server-request":
        assert any(r["method"] == "response" and r["verb"] == "POST" for r in log)


@pytest.mark.asyncio
@pytest.mark.parametrize("modern", [True, False])
async def test_real_http_ambiguous_drop_executes_once_without_retry(tmp_path, modern):
    async with fixture_client(
        tmp_path, modern=modern, mode="json" if modern else "good"
    ) as (client, process, counter):
        await client.list_tools()
        with pytest.raises(MCPToolExecutionError):
            await client.call_tool("drop", {})
    log = records(counter)
    assert (
        sum(
            r.get("tool") == "drop" if modern else r.get("method") == "tools/call"
            for r in log
        )
        == 1
    )


def tls_material(tmp_path, *, valid_name=True):
    key = ec.generate_private_key(ec.SECP256R1())
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "synthetic-loopback")])
    now = datetime.now(UTC)
    san = (
        x509.IPAddress(ipaddress.ip_address("127.0.0.1"))
        if valid_name
        else x509.DNSName("wrong.example")
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(hours=1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(x509.SubjectAlternativeName([san]), critical=False)
        .sign(key, hashes.SHA256())
    )
    cert_path = tmp_path / "fixture-cert.pem"
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    (tmp_path / "fixture-key.pem").write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    context = ssl.create_default_context(cafile=str(cert_path))
    assert context.check_hostname and context.verify_mode == ssl.CERT_REQUIRED
    return context


@pytest.mark.asyncio
async def test_real_verified_tls_hostname_and_owned_cleanup(tmp_path, monkeypatch):
    context = tls_material(tmp_path)
    monkeypatch.setattr(
        "friday_mcp.client.http.ssl.create_default_context", lambda: context
    )
    async with fixture_client(tmp_path, modern=False, mode="tls") as (
        client,
        process,
        counter,
    ):
        await client.list_tools()
        assert (
            await client.call_tool("echo", {"text": "verified-TLS"}) == "verified-TLS"
        )
        assert client._endpoint.scheme == "https"
        assert context.check_hostname and context.verify_mode == ssl.CERT_REQUIRED


@pytest.mark.asyncio
async def test_real_tls_wrong_hostname_fails_with_partial_streams_reaped(
    tmp_path, monkeypatch
):
    context = tls_material(tmp_path, valid_name=False)
    monkeypatch.setattr(
        "friday_mcp.client.http.ssl.create_default_context", lambda: context
    )
    with pytest.raises(ProtocolFailure):
        async with fixture_client(tmp_path, modern=False, mode="tls-wrong-name"):
            pytest.fail("Wrong TLS hostname must not connect")


@pytest.mark.asyncio
async def test_real_2025_session_expiry_reinitializes_but_first_call_still_fails(
    tmp_path,
):
    async with fixture_client(tmp_path, modern=False, mode="session-404") as (
        client,
        process,
        counter,
    ):
        await client.list_tools()
        with pytest.raises(MCPToolExecutionError):
            await client.call_tool("echo", {"text": "first"})
        assert (
            await client.call_tool("echo", {"text": "second explicit"})
            == "second explicit"
        )
    methods = [r["method"] for r in records(counter)]
    assert methods.count("initialize") == 2 and methods.count("tools/call") == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("modern", [True, False])
async def test_real_http_cancel_slow_request_closes_owners_without_replay(
    tmp_path, modern
):
    async with fixture_client(
        tmp_path, modern=modern, mode="sse" if modern else "good"
    ) as (client, process, counter):
        await client.list_tools()
        task = asyncio.create_task(client.call_tool("slow", {}))
        deadline = asyncio.get_running_loop().time() + 1
        while not any(
            r.get("tool") == "slow" if modern else r.get("method") == "tools/call"
            for r in records(counter)
        ):
            if asyncio.get_running_loop().time() > deadline:
                pytest.fail("Synthetic operation did not start")
            await asyncio.sleep(0.01)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    log = records(counter)
    assert (
        sum(
            r.get("tool") == "slow" if modern else r.get("method") == "tools/call"
            for r in log
        )
        == 1
    )
