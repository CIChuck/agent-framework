"""Public YAML/Kernel assembly against named synthetic verified-TLS counterparts."""

import asyncio
import base64
import importlib.util
import ipaddress
import json
import os
import socket
import ssl
import sys
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
import yaml
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID
from friday_agent import DefaultToolRegistry
from friday_core.mcp import MCPClientLimits
from friday_core.profiles import MemoryProfile
from friday_mcp.client import StdioMCPClient, StreamableHTTPMCPClient
from friday_mcp.client.base import MCPToolExecutionError
from friday_runtime.config import (
    MCPRuntimeHTTPServerConfig,
    MCPRuntimeServerConfig,
    MCPToolProviderConfig,
    RuntimeConfig,
)
from friday_runtime.kernel import RuntimeKernel
from friday_runtime.mcp_clients import create_mcp_client
from friday_runtime.mcp_loading import RuntimeMCPProvider
from friday_runtime.tool_loading import ToolProviderLoadError
from friday_telemetry import DebugTelemetryRecorder

FIXTURES = Path(__file__).resolve().parents[2] / "friday-mcp/tests_mcp/fixtures"


def records(path):
    return (
        [json.loads(line) for line in path.read_text().splitlines()]
        if path.exists()
        else []
    )


def tls_material(tmp_path, valid_name=True):
    key = ec.generate_private_key(ec.SECP256R1())
    subject = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, "synthetic-private-CA")]
    )
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
    key_path = tmp_path / "fixture-key.pem"
    key_path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    context = ssl.create_default_context(cafile=str(cert_path))
    assert context.check_hostname and context.verify_mode == ssl.CERT_REQUIRED
    return context


@asynccontextmanager
async def tls_peer(
    tmp_path, monkeypatch, version, mode="tls", bearer=None, valid_name=True
):
    context = tls_material(tmp_path, valid_name)
    monkeypatch.setattr(
        "friday_mcp.client.http.ssl.create_default_context", lambda: context
    )
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    counter = tmp_path / "counter.jsonl"
    wire = tmp_path / "wire.jsonl"
    # The parent verification environment is already the frozen credential-free allowlist.
    environment = dict(os.environ)
    environment.update(
        MCP_FIXTURE_COUNTER=str(counter),
        MCP_FIXTURE_WIRE_COUNTER=str(wire),
        MCP_FIXTURE_TLS_CERT=str(tmp_path / "fixture-cert.pem"),
        MCP_FIXTURE_TLS_KEY=str(tmp_path / "fixture-key.pem"),
    )
    if bearer is not None:
        environment["MCP_FIXTURE_EXPECT_BEARER"] = bearer
    script = FIXTURES / (
        "http_sdk_server.py" if version == "2026-07-28" else "http_compat_server.py"
    )
    child = await asyncio.create_subprocess_exec(
        sys.executable,
        str(script),
        str(port),
        mode,
        cwd=tmp_path,
        env=environment,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    try:
        # Readiness is a literal-loopback socket probe, not an MCP request/retry.
        for _ in range(150):
            if child.returncode is not None:
                raise RuntimeError("Synthetic TLS peer exited before readiness")
            try:
                reader, writer = await asyncio.open_connection("127.0.0.1", port)
                writer.close()
                await writer.wait_closed()
                break
            except ConnectionError:
                await asyncio.sleep(0.02)
        else:
            raise RuntimeError("Synthetic TLS peer did not start")
        entry = {
            "name": "remote",
            "transport": "streamable_http",
            "protocol_version": version,
            "trust_level": "remote",
            "url": f"https://127.0.0.1:{port}/mcp",
            "network": {"allowed_addresses": ["127.0.0.1"], "allowed_ports": [port]},
            "timeout_seconds": 2,
            "tool_timeout_seconds": 1,
            "required": True,
        }
        if bearer is not None:
            entry.update(auth="bearer_env", credential_env="SYNTHETIC_REMOTE_REFERENCE")
        yield entry, child, counter, wire, context
    finally:
        if child.returncode is None:
            child.terminate()
            try:
                await asyncio.wait_for(child.wait(), 2)
            except TimeoutError:
                child.kill()
                await child.wait()
        assert child.returncode is not None


def stanza(servers, **changes):
    return {
        "enabled": True,
        "mode": "all",
        "config": {
            "security": {
                "integrated_transport": "stdio_and_streamable_http",
                "trust_posture": "explicit_remote",
            },
            "servers": servers,
            **changes,
        },
    }


def kernel_from_yaml(tmp_path, monkeypatch, mcp):
    (tmp_path / "workspace").mkdir(exist_ok=True)
    path = tmp_path / "runtime.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "runtime_paths": {
                    "install_root": str(tmp_path),
                    "runtime_data_root": str(tmp_path / "state"),
                    "workspace_root": str(tmp_path / "workspace"),
                },
                "agents": {"dir": str(tmp_path / "agents")},
                "tools": {"providers": {"mcp": mcp}},
            }
        )
    )
    config = RuntimeConfig.from_sources(yaml_path=path, env={})
    kernel = RuntimeKernel(config, memory_profile=MemoryProfile.TESTING)
    for method in (
        "_create_telemetry",
        "_create_llm_services",
        "_create_memory_controller",
        "_create_multi_agent_stack",
        "_create_context_engine",
    ):
        monkeypatch.setattr(kernel._di, method, lambda: None)
    monkeypatch.setattr(kernel._di, "_create_storage_adapters", AsyncMock())
    return kernel


class Credentials:
    def __init__(self, token=None):
        self.token = token
        self.lookups = []

    def resolve(self, name):
        self.lookups.append(name)
        return self.token


@pytest.mark.asyncio
@pytest.mark.parametrize("version", ["2026-07-28", "2025-11-25"])
async def test_real_yaml_kernel_tls_discovery_call_stop(
    version, tmp_path, monkeypatch, caplog
):
    token = "SYNTHETIC_CREDENTIAL_SENTINEL"
    monkeypatch.setenv("SYNTHETIC_REMOTE_REFERENCE", token)
    baseline_tasks = set(asyncio.all_tasks())
    async with tls_peer(tmp_path, monkeypatch, version, bearer=token) as (
        entry,
        child,
        counter,
        wire,
        context,
    ):
        kernel = kernel_from_yaml(tmp_path, monkeypatch, stanza([entry]))
        recorder = DebugTelemetryRecorder()
        # Borrow a recorder before public start; retain the real MCP owner assembly.
        monkeypatch.setattr(
            kernel._di,
            "_create_telemetry",
            lambda: setattr(kernel._di, "telemetry", recorder),
        )
        try:
            await kernel.start()
            provider = kernel.mcp_provider
            registry = kernel.tool_registry
            assert provider is not None and registry is not None
            assert (
                provider.tool_metadata["mcp_remote_echo"].transport == "streamable_http"
            )
            assert provider.tool_metadata["mcp_remote_echo"].trust_level == "remote"
            client = provider.manager.get_client("remote")
            catalog = client.current_catalog_snapshot.tools()
            original = json.dumps(catalog, ensure_ascii=False)
            exported = registry.get("mcp_remote_echo").parameters_schema
            assert "x-mcp-header" not in json.dumps(exported)
            assert await registry.get_callable("mcp_remote_echo")(text="雪\nline")
            assert (
                json.dumps(client.current_catalog_snapshot.tools(), ensure_ascii=False)
                == original
            )
            assert (
                client.request_timeout_seconds == 1
                and client.limits.concurrent_requests <= 4
            )
            calls = [
                r
                for r in records(wire)
                if r.get("mcp-method", r.get("method")) == "tools/call"
            ]
            assert (
                len(calls) == 1
                and calls[0]["auth_matches"]
                and not calls[0]["trace_present"]
            )
            if version == "2026-07-28":
                assert (
                    calls[0]["mcp-param-text"]
                    == "=?base64?"
                    + base64.b64encode("雪\nline".encode()).decode()
                    + "?="
                )
            assert context.check_hostname and context.verify_mode == ssl.CERT_REQUIRED
            assert token not in repr(provider.operational_diagnostics) + repr(
                recorder.events
            ) + caplog.text + repr(client)
            await kernel.stop()
            await kernel.stop()
            assert (
                provider.owned_tool_names == ()
                and provider.manager.connected_servers == []
            )
            assert client.outstanding_http_owners == 0 and client._pool is None
        finally:
            await kernel.stop()
    assert child.returncode is not None
    assert not [
        task for task in asyncio.all_tasks() - baseline_tasks if not task.done()
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", ["provider_off", "entry_off", "auto_off"])
async def test_disabled_http_never_resolves_or_constructs(tmp_path, monkeypatch, case):
    entry = {
        "name": "remote",
        "transport": "streamable_http",
        "protocol_version": "2026-07-28",
        "trust_level": "remote",
        "url": "https://example.com/mcp",
        "auth": "bearer_env",
        "credential_env": "SYNTHETIC_REMOTE_REFERENCE",
    }
    values = stanza([entry])
    values["enabled"] = case != "provider_off"
    entry["enabled"] = case != "entry_off"
    values["config"]["auto_connect"] = case != "auto_off"
    credentials = Credentials()
    monkeypatch.setattr(
        "friday_runtime.mcp_clients.create_mcp_client",
        lambda *args: pytest.fail("Disabled factory invoked"),
    )
    provider = RuntimeMCPProvider(
        MCPToolProviderConfig.from_dict(values),
        str(tmp_path),
        credential_resolver=credentials,
    )
    await provider.start()
    await provider.stop()
    assert credentials.lookups == []


@pytest.mark.parametrize("token", [None, "", "bad\nSENTINEL_TOKEN", "x" * 8193])
def test_bad_credential_has_no_chain_or_content(token, tmp_path):
    entry = MCPRuntimeHTTPServerConfig(
        name="remote",
        transport="streamable_http",
        protocol_version="2026-07-28",
        trust_level="remote",
        url="https://example.com/mcp",
        auth="bearer_env",
        credential_env="SYNTHETIC_REMOTE_REFERENCE",
    )
    resolver = Credentials(token)
    with pytest.raises(ValueError) as failure:
        create_mcp_client(entry, MCPClientLimits(), tmp_path, resolver)
    assert str(failure.value) == "MCP credential unavailable"
    assert failure.value.__cause__ is None and failure.value.__context__ is None
    assert resolver.lookups == ["SYNTHETIC_REMOTE_REFERENCE"]


@pytest.mark.parametrize("profile", ["legacy", "modern", "auto"])
def test_public_stdio_profile_factory_preserves_defaults_and_lower_limits(
    tmp_path, profile
):
    entry = MCPRuntimeServerConfig(
        name="local",
        command="fake",
        protocol_profile=profile,
        timeout_seconds=7,
        tool_timeout_seconds=2,
    )
    credentials = Credentials()
    client = create_mcp_client(
        entry,
        MCPClientLimits(max_parallel_tool_calls=2, max_result_bytes=512),
        tmp_path,
        credentials,
    )
    assert isinstance(client, StdioMCPClient) and client.protocol_profile == profile
    assert client.request_timeout_seconds == 7
    if profile != "legacy":
        assert (
            client.limits.concurrent_requests == 2 and client.limits.result_bytes == 512
        )
    assert credentials.lookups == []


@pytest.mark.asyncio
@pytest.mark.parametrize("version", ["2026-07-28", "2025-11-25"])
async def test_real_tls_hostname_rejection_required_optional_and_no_outer_retry(
    version, tmp_path, monkeypatch
):
    async with tls_peer(tmp_path, monkeypatch, version, valid_name=False) as (
        entry,
        child,
        counter,
        wire,
        context,
    ):
        provider = RuntimeMCPProvider(
            MCPToolProviderConfig.from_dict(stanza([entry])), str(tmp_path)
        )
        with pytest.raises(
            ToolProviderLoadError, match="Required MCP server unavailable"
        ):
            await provider.start()
        assert (
            provider.manager.connected_servers == [] and provider.prepared_tools == ()
        )
        assert not records(counter)
        await provider.stop()
        entry["required"] = False
        optional = RuntimeMCPProvider(
            MCPToolProviderConfig.from_dict(stanza([entry])), str(tmp_path)
        )
        await optional.start()
        assert optional.discovery.status == "partial"
        await optional.stop()
        assert context.check_hostname and context.verify_mode == ssl.CERT_REQUIRED


@pytest.mark.asyncio
@pytest.mark.parametrize("version", ["2026-07-28", "2025-11-25"])
@pytest.mark.parametrize("name", ["drop", "slow"])
async def test_runtime_no_call_replay_on_real_ambiguous_drop_and_timeout(
    version, name, tmp_path, monkeypatch
):
    async with tls_peer(tmp_path, monkeypatch, version) as (
        entry,
        child,
        counter,
        wire,
        context,
    ):
        provider = RuntimeMCPProvider(
            MCPToolProviderConfig.from_dict(stanza([entry])), str(tmp_path)
        )
        registry = DefaultToolRegistry()
        try:
            await provider.start()
            await provider.register_tools(registry)
            with pytest.raises((MCPToolExecutionError, TimeoutError)):
                await registry.get_callable("mcp_remote_" + name)()
            assert (
                sum(r.get("tool") == name for r in records(counter)) == 1
                if version == "2026-07-28"
                else sum(r.get("method") == "tools/call" for r in records(counter)) == 1
            )
        finally:
            await provider.stop()
        assert provider.manager.connected_servers == []


@pytest.mark.asyncio
async def test_2025_runtime_recovery_is_read_only_and_observed_once(
    tmp_path, monkeypatch
):
    async with tls_peer(tmp_path, monkeypatch, "2025-11-25", mode="session-404") as (
        entry,
        child,
        counter,
        wire,
        context,
    ):
        recorder = DebugTelemetryRecorder()
        provider = RuntimeMCPProvider(
            MCPToolProviderConfig.from_dict(stanza([entry])), str(tmp_path), recorder
        )
        registry = DefaultToolRegistry()
        try:
            await provider.start()
            await provider.register_tools(registry)
            with pytest.raises(MCPToolExecutionError):
                await registry.get_callable("mcp_remote_echo")(text="first")
            with pytest.raises(MCPToolExecutionError) as stale:
                await registry.get_callable("mcp_remote_echo")(text="stale")
            assert stale.value.failure_code == "catalog_unavailable"
            assert sum(r["method"] == "tools/call" for r in records(counter)) == 1
            await provider.stop()
            await provider.start()
            await provider.register_tools(registry)
            assert (
                await registry.get_callable("mcp_remote_echo")(text="explicit second")
                == "explicit second"
            )
            methods = [r["method"] for r in records(counter)]
            assert methods.count("initialize") == 3 and methods.count("tools/call") == 2
            names = [r.name for r in recorder.events]
            assert (
                names.count("mcp.tool_call_start") == 3
                and names.count("mcp.tool_call_failure") == 2
                and names.count("mcp.tool_call_finish") == 1
            )
        finally:
            await provider.stop()


def wire_helpers():
    name = "up03_frozen_wire_helpers"
    if name not in sys.modules:
        path = FIXTURES.parent / "client/test_http_lifecycle.py"
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def controlled_factory(monkeypatch, peer, resolver):
    original = StreamableHTTPMCPClient

    def construct(endpoint, **kwargs):
        return original(endpoint, **kwargs, connector=peer, resolver=resolver)

    monkeypatch.setattr("friday_runtime.mcp_clients.StreamableHTTPMCPClient", construct)


def public_remote_entry(version="2026-07-28", **changes):
    return {
        "name": "remote",
        "transport": "streamable_http",
        "protocol_version": version,
        "trust_level": "remote",
        "url": "https://example.test/mcp",
        "required": True,
        "retry_attempts": 0,
        **changes,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("version", ["2026-07-28", "2025-11-25"])
async def test_runtime_actual_connect_policy_rechecks_dns_and_preserves_hostname(
    version, tmp_path, monkeypatch
):
    helpers = wire_helpers()
    peer = helpers.Peer(version)
    if version == "2025-11-25":
        peer.tools[0]["inputSchema"]["properties"]["text"].pop("x-mcp-header")
    resolver = helpers.Resolver()
    controlled_factory(monkeypatch, peer, resolver)
    provider = RuntimeMCPProvider(
        MCPToolProviderConfig.from_dict(stanza([public_remote_entry(version)])),
        str(tmp_path),
    )
    registry = DefaultToolRegistry()
    try:
        await provider.start()
        await provider.register_tools(registry)
        assert peer.connections and all(
            host == "93.184.216.34" for host, port in peer.connections
        )
        assert all(tls == (True, ssl.CERT_REQUIRED, "example.test") for tls in peer.tls)
        before = len(peer.connections)
        resolver.answers = ("93.184.216.34", "127.0.0.1")
        with pytest.raises(MCPToolExecutionError):
            await registry.get_callable("mcp_remote_echo")(text="blocked")
        assert len(peer.connections) == before and "tools/call" not in peer.methods()
        assert resolver.calls > 1
    finally:
        await provider.stop()
    assert all(stream.closed for stream in peer.streams)


@pytest.mark.asyncio
async def test_runtime_modern_schema_additions_and_exact_original_header_catalog(
    tmp_path, monkeypatch
):
    helpers = wire_helpers()
    peer = helpers.Peer()
    resolver = helpers.Resolver()
    peer.tools = [
        {
            "name": "Exact.Name",
            "inputSchema": {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "properties": {
                    "text": {"type": "string", "x-mcp-header": "Exact-Text"},
                    "opaque": {
                        "type": "object",
                        "const": {"x-mcp-header": "application value"},
                    },
                },
            },
        },
        {
            "name": "reject_ref",
            "inputSchema": {
                "type": "object",
                "properties": {"x": {"$ref": "https://example.invalid/schema"}},
            },
        },
        {
            "name": "reject_nested",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "string",
                        "$schema": "https://json-schema.org/draft/2020-12/schema",
                    }
                },
            },
        },
        {
            "name": "reject_header",
            "inputSchema": {
                "type": "object",
                "properties": {"x": {"type": "string", "x-mcp-header": "Bad\nName"}},
            },
        },
        {
            "name": "reject_unreachable",
            "inputSchema": {
                "type": "object",
                "additionalProperties": {"type": "string", "x-mcp-header": "Hidden"},
            },
        },
    ]
    controlled_factory(monkeypatch, peer, resolver)
    provider = RuntimeMCPProvider(
        MCPToolProviderConfig.from_dict(stanza([public_remote_entry()])), str(tmp_path)
    )
    registry = DefaultToolRegistry()
    try:
        await provider.start()
        await provider.register_tools(registry)
        assert provider.owned_tool_names == ("mcp_remote_exact_name",)
        schema = registry.get("mcp_remote_exact_name").parameters_schema
        assert (
            "$schema" not in schema
            and "x-mcp-header" not in schema["properties"]["text"]
        )
        assert schema["properties"]["opaque"]["const"] == {
            "x-mcp-header": "application value"
        }
        assert await registry.get_callable("mcp_remote_exact_name")(text="雪") == "雪"
        headers, request = peer.requests[-1][1:]
        assert (
            request["params"]["name"] == "Exact.Name"
            and headers[b"mcp-param-exact-text"] == b"=?base64?6Zuq?="
        )
        catalog = await provider.manager.get_client("remote").list_tools()
        assert (
            catalog[0]["inputSchema"]["properties"]["text"]["x-mcp-header"]
            == "Exact-Text"
        )
        assert (
            catalog[0]["inputSchema"]["$schema"]
            == "https://json-schema.org/draft/2020-12/schema"
        )
    finally:
        await provider.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "setting", ["exclude", "native_collision", "cap", "bytes", "tokens"]
)
async def test_http_admission_filters_collision_and_raw_export_budgets(
    tmp_path, monkeypatch, setting
):
    helpers = wire_helpers()
    peer = helpers.Peer()
    resolver = helpers.Resolver()
    peer.tools = [
        {"name": "echo", "inputSchema": {"type": "object"}},
        {"name": "second", "inputSchema": {"type": "object"}},
    ]
    controlled_factory(monkeypatch, peer, resolver)
    values = stanza([public_remote_entry()])
    registry = DefaultToolRegistry()
    if setting == "exclude":
        values["exclude_tools"] = ["mcp_remote_echo"]
    if setting == "native_collision":
        registry.register(
            name="mcp_remote_echo", func=lambda: "native", category="native"
        )
    if setting == "cap":
        values["config"]["limits"] = {"max_total_tools": 1}
    if setting == "bytes":
        values["config"]["limits"] = {"max_schema_bytes_per_tool": 64}
    if setting == "tokens":
        values["config"]["limits"] = {"max_schema_tokens": 1}
    provider = RuntimeMCPProvider(
        MCPToolProviderConfig.from_dict(values), str(tmp_path)
    )
    try:
        await provider.start()
        if setting == "native_collision":
            with pytest.raises(ToolProviderLoadError, match="name_collision"):
                await provider.register_tools(registry)
            assert (
                registry.get_callable("mcp_remote_echo")() == "native"
                and provider.owned_tool_names == ()
            )
        else:
            await provider.register_tools(registry)
            expected = (
                ("mcp_remote_second",)
                if setting == "exclude"
                else ("mcp_remote_echo",)
                if setting == "cap"
                else ()
            )
            assert provider.owned_tool_names == expected
    finally:
        await provider.stop()


@pytest.mark.asyncio
async def test_runtime_new_profile_one_deadline_across_handshake_and_discovery(
    tmp_path, monkeypatch
):
    from friday_mcp.client import MCPClientBase

    class Delayed(MCPClientBase):
        def __init__(self):
            super().__init__("remote")
            self.cleaned = False

        async def _create_transport(self):
            return None

        async def connect(self):
            await asyncio.sleep(0.6)
            self._connected = True

        async def list_tools(self):
            await asyncio.sleep(0.6)
            return []

        async def disconnect(self):
            self.cleaned = True
            self._connected = False

    client = Delayed()
    monkeypatch.setattr(
        "friday_runtime.mcp_clients.create_mcp_client", lambda *args: client
    )
    provider = RuntimeMCPProvider(
        MCPToolProviderConfig.from_dict(
            stanza([public_remote_entry(timeout_seconds=1, required=False)])
        ),
        str(tmp_path),
    )
    began = asyncio.get_running_loop().time()
    await provider.start()
    assert (
        provider.lifecycle[0].outcome == "discovery_timeout"
        and asyncio.get_running_loop().time() - began < 1.18
    )
    assert client.cleaned and not provider.prepared_tools
    await provider.stop()


@pytest.mark.asyncio
async def test_runtime_late_2025_404_preserves_healthy_recovered_session(
    tmp_path, monkeypatch
):
    helpers = wire_helpers()
    peer = helpers.OrderedExpiryPeer()
    peer.tools[0]["inputSchema"]["properties"]["text"].pop("x-mcp-header")
    resolver = helpers.Resolver()
    controlled_factory(monkeypatch, peer, resolver)
    provider = RuntimeMCPProvider(
        MCPToolProviderConfig.from_dict(stanza([public_remote_entry("2025-11-25")])),
        str(tmp_path),
    )
    registry = DefaultToolRegistry()
    late = None
    try:
        await provider.start()
        await provider.register_tools(registry)
        peer.hook = (
            lambda verb, headers, request: helpers.Reply(status=404)
            if request.get("method") == "tools/call"
            else None
        )
        late = asyncio.create_task(
            registry.get_callable("mcp_remote_echo")(text="late")
        )
        await asyncio.wait_for(peer.late_issued.wait(), 1)
        with pytest.raises(MCPToolExecutionError):
            await registry.get_callable("mcp_remote_echo")(text="fast")
        client = provider.manager.get_client("remote")
        generation = client._generation
        peer.hook = None
        peer.late_release.set()
        with pytest.raises(MCPToolExecutionError):
            await late
        assert (
            client.is_connected
            and client._generation == generation
            and peer.methods().count("initialize") == 2
        )
        with pytest.raises(MCPToolExecutionError) as stale:
            await registry.get_callable("mcp_remote_echo")(text="stale")
        assert stale.value.failure_code == "catalog_unavailable"
        assert peer.methods().count("tools/call") == 2
        await provider.stop()
        await provider.start()
        await provider.register_tools(registry)
        assert (
            await registry.get_callable("mcp_remote_echo")(text="healthy") == "healthy"
        )
        assert peer.methods().count("tools/call") == 3
    finally:
        peer.late_release.set()
        if late is not None:
            await asyncio.gather(late, return_exceptions=True)
        await provider.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "profile,modern",
    [("legacy", False), ("modern", True), ("auto", True), ("auto", False)],
)
async def test_real_public_kernel_stdio_profiles_and_child_cleanup(
    tmp_path, monkeypatch, profile, modern
):
    entry = {
        "name": "local",
        "command": sys.executable,
        "args": [
            str(
                FIXTURES
                / ("modern_sdk_server.py" if modern else "legacy_protocol_server.py")
            )
        ],
        "protocol_profile": profile,
        "required": True,
        "timeout_seconds": 3,
        "retry_attempts": 0,
        "env": {"MCP_FIXTURE_COUNTER": str(tmp_path / "stdio-counter.jsonl")},
    }
    kernel = kernel_from_yaml(
        tmp_path,
        monkeypatch,
        {"enabled": True, "mode": "all", "config": {"servers": [entry]}},
    )
    started_at = asyncio.get_running_loop().time()
    try:
        try:
            await kernel.start()
        except Exception as exc:
            provider = kernel.mcp_provider
            manager = provider.manager if provider is not None else None
            clients = manager.connected_servers if manager is not None else []
            client = manager.get_client("local") if "local" in clients else None
            transport = getattr(client, "_transport", None)
            process = getattr(transport, "_process", None)
            counter_path = tmp_path / "stdio-counter.jsonl"
            print(
                "synthetic MCP startup diagnostic: "
                f"profile={profile} modern={modern} "
                f"elapsed_seconds={asyncio.get_running_loop().time() - started_at:.3f} "
                f"exception_type={type(exc).__name__} "
                f"lifecycle={provider.lifecycle if provider is not None else None} "
                f"retained_clients={clients} "
                f"child_returncode={getattr(process, 'returncode', None)} "
                f"tool_record_count={len(records(counter_path))}"
            )
            raise
        client = kernel.mcp_provider.manager.get_client("local")
        transport = client._transport
        process = transport._process
        assert client.protocol_profile == profile
        assert client.negotiated_version == ("2026-07-28" if modern else "2024-11-05")
        assert await kernel.tool_registry.get_callable("mcp_local_echo")(
            text="synthetic"
        )
        await kernel.stop()
        assert process.returncode is not None and transport._process is None
        assert transport._stderr_task is None and client._receive_task is None
        assert not client._exchange_tasks and not client._pending_requests
    finally:
        await kernel.stop()


@pytest.mark.asyncio
async def test_credential_resolver_only_named_reference_reconnect_and_safe_resolver_failure(
    tmp_path, monkeypatch
):
    helpers = wire_helpers()
    peer = helpers.Peer()
    controlled_factory(monkeypatch, peer, helpers.Resolver())
    credentials = Credentials("synthetic-first")
    entry = public_remote_entry(
        auth="bearer_env", credential_env="SYNTHETIC_REMOTE_REFERENCE"
    )
    provider = RuntimeMCPProvider(
        MCPToolProviderConfig.from_dict(stanza([entry])),
        str(tmp_path),
        credential_resolver=credentials,
    )
    try:
        await provider.start()
        assert peer.requests[0][1][b"authorization"] == b"Bearer synthetic-first"
        await provider.stop()
        credentials.token = "synthetic-second"
        await provider.start()
        assert credentials.lookups == ["SYNTHETIC_REMOTE_REFERENCE"] * 2
        assert peer.requests[-1][1][b"authorization"] == b"Bearer synthetic-second"
    finally:
        await provider.stop()

    class Failing:
        def resolve(self, name):
            raise RuntimeError("SENTINEL_RESOLVER_SECRET")

    server = MCPRuntimeHTTPServerConfig.model_validate(entry)
    with pytest.raises(ValueError) as failure:
        create_mcp_client(server, MCPClientLimits(), tmp_path, Failing())
    assert failure.value.__cause__ is failure.value.__context__ is None
    assert "SENTINEL" not in str(failure.value)


@pytest.mark.asyncio
async def test_http_runtime_retains_resistant_cleanup_and_never_replaces_owner(
    tmp_path, monkeypatch
):
    helpers = wire_helpers()
    peer = helpers.Peer()
    peer.aclose = AsyncMock()
    controlled_factory(monkeypatch, peer, helpers.Resolver())
    provider = RuntimeMCPProvider(
        MCPToolProviderConfig.from_dict(stanza([public_remote_entry()])), str(tmp_path)
    )
    registry = DefaultToolRegistry()
    release = asyncio.Event()
    try:
        await provider.start()
        await provider.register_tools(registry)
        manager = provider.manager
        client = manager.get_client("remote")
        peer.hook = (
            lambda verb, headers, request: peer.rpc(
                request,
                {"content": [{"type": "text", "text": "safe"}]},
                close_release=release,
            )
            if request.get("method") == "tools/call"
            else None
        )
        with pytest.raises(MCPToolExecutionError):
            await registry.get_callable("mcp_remote_echo")(text="one")
        assert client.outstanding_http_owners == 1
        with pytest.raises(ToolProviderLoadError, match="shutdown incomplete"):
            await provider.stop()
        assert (
            provider.owned_tool_names == () and manager.get_client("remote") is client
        )
        with pytest.raises(ToolProviderLoadError):
            await provider.start()
        assert provider.manager is manager and peer.methods().count("tools/call") == 1
        release.set()
        await asyncio.sleep(0.03)
        await provider.stop()
        await provider.stop()
        assert client.outstanding_http_owners == 0 and manager.connected_servers == []
        peer.aclose.assert_not_awaited()
    finally:
        release.set()
        await asyncio.sleep(0.03)
        await provider.stop()


@pytest.mark.asyncio
async def test_http_registration_primary_safe_failure_and_retained_registry_owner(
    tmp_path, monkeypatch
):
    helpers = wire_helpers()
    peer = helpers.Peer()
    controlled_factory(monkeypatch, peer, helpers.Resolver())

    class Registry(DefaultToolRegistry):
        blocked = True

        def register(self, *args, **kwargs):
            result = super().register(*args, **kwargs)
            if args and args[0].name.startswith("mcp_"):
                raise RuntimeError("SENTINEL_REGISTRY_FAILURE")
            return result

        def unregister(self, name):
            return (
                False
                if self.blocked and name.startswith("mcp_")
                else super().unregister(name)
            )

    registry = Registry()
    registry.register(name="native", func=lambda: "native", category="native")
    provider = RuntimeMCPProvider(
        MCPToolProviderConfig.from_dict(stanza([public_remote_entry()])), str(tmp_path)
    )
    try:
        await provider.start()
        with pytest.raises(
            ToolProviderLoadError, match="registration failed"
        ) as failure:
            await provider.register_tools(registry)
        assert failure.value.__cause__ is failure.value.__context__ is None
        assert (
            provider.registration_registry is registry
            and provider.owned_tool_names == ("mcp_remote_echo",)
        )
        manager = provider.manager
        with pytest.raises(ToolProviderLoadError):
            await provider.start()
        assert (
            provider.manager is manager
            and registry.get_callable("native")() == "native"
        )
        registry.blocked = False
        await provider.stop()
        assert registry.list_names() == ["native"]
        assert provider.manager.connected_servers == []
    finally:
        registry.blocked = False
        await provider.stop()


@pytest.mark.asyncio
async def test_http_complete_catalog_default_per_server_total_caps_and_mixed_peers(
    tmp_path, monkeypatch
):
    helper = wire_helpers()
    peers = {name: helper.Peer() for name in ("one", "two", "three")}
    created = []
    for peer in peers.values():
        peer.tools = [
            {"name": f"tool_{n}", "inputSchema": {"type": "object"}} for n in range(30)
        ]
    original = StreamableHTTPMCPClient

    def construct(endpoint, **kwargs):
        name = kwargs["name"]
        created.append(name)
        return original(
            endpoint, **kwargs, resolver=helper.Resolver(), connector=peers[name]
        )

    monkeypatch.setattr("friday_runtime.mcp_clients.StreamableHTTPMCPClient", construct)
    servers = [
        public_remote_entry(name=name, url=f"https://{name}.example.test/mcp")
        for name in peers
    ]
    provider = RuntimeMCPProvider(
        MCPToolProviderConfig.from_dict(
            stanza(servers, limits={"max_schema_tokens": 30000})
        ),
        str(tmp_path),
    )
    registry = DefaultToolRegistry()
    try:
        await provider.start()
        await provider.register_tools(registry)
        assert set(created) == set(peers) and len(created) == 3
        assert (
            provider.discovery.discovered_tools == 90
            and len(provider.owned_tool_names) == 50
        )
        assert (
            sum(name.startswith("mcp_one_") for name in provider.owned_tool_names) == 25
        )
        assert (
            sum(name.startswith("mcp_two_") for name in provider.owned_tool_names) == 25
        )
        assert not any(
            name.startswith("mcp_three_") for name in provider.owned_tool_names
        )
        assert await registry.get_callable("mcp_two_tool_0")() == "ok"
        assert (
            peers["two"].methods().count("tools/call") == 1
            and peers["one"].methods().count("tools/call") == 0
        )
    finally:
        await provider.stop()
    assert all(stream.closed for peer in peers.values() for stream in peer.streams)
