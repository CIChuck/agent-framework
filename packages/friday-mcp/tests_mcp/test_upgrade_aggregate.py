"""Published configuration and real Friday client/server aggregate boundaries."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import pytest

from friday_mcp.client import StdioMCPClient, StreamableHTTPMCPClient
from friday_mcp.client.base import MCPToolExecutionError
from friday_mcp.client.http_policy import HTTPEndpointPolicy
from friday_mcp.client.protocol import ProtocolLimits
from tests_mcp.server.test_server_interop import rows, tls_friday

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = Path(__file__).parent / "fixtures/friday_modern_tools_server.py"
VERSION = "2026-07-28"


async def wait_event(counter, name, count):
    async with asyncio.timeout(3):
        while sum(row["event"] == name for row in rows(counter)) < count:
            await asyncio.sleep(0.01)


@asynccontextmanager
async def friday_client(tmp_path, monkeypatch, transport):
    if transport.startswith("stdio"):
        counter = tmp_path / "friday-stdio.jsonl"
        client = StdioMCPClient(
            "friday",
            sys.executable,
            [str(FIXTURE), "stdio", str(counter)],
            env=dict(os.environ),
            cwd=tmp_path,
            protocol_profile="auto" if transport == "stdio-auto" else "modern",
            limits=ProtocolLimits(timeout_seconds=2, concurrent_requests=2),
        )
        process = None
        try:
            await client.connect()
            process = client._transport._process
            yield client, counter, process
        finally:
            await client.disconnect()
        assert process is not None and process.returncode == 0
    else:
        async with tls_friday(tmp_path, transport) as (url, context, counter, process):
            monkeypatch.setattr(
                "friday_mcp.client.http.ssl.create_default_context", lambda: context
            )
            port = int(url.split(":")[2].split("/")[0])
            client = StreamableHTTPMCPClient(
                url,
                protocol_version=VERSION,
                endpoint_policy=HTTPEndpointPolicy(("127.0.0.1",), (port,)),
                limits=ProtocolLimits(timeout_seconds=2, concurrent_requests=2),
            )
            try:
                await client.connect()
                yield client, counter, process
            finally:
                await client.disconnect()
            assert client.outstanding_http_owners == 0
        assert process.returncode == 0
    await wait_event(counter, "server_stopped", 1)
    assert rows(counter)[-1] == {"event": "server_stopped", "active": 0}


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ["stdio-modern", "stdio-auto", "json", "sse"])
async def test_friday_client_to_friday_server(tmp_path, monkeypatch, transport):
    before = set(asyncio.all_tasks())
    async with friday_client(tmp_path, monkeypatch, transport) as (client, counter, _):
        assert client.negotiated_version == VERSION
        tools = await client.list_tools()
        assert [tool["name"] for tool in tools] == ["echo"]
        text_schema = tools[0]["inputSchema"]["properties"]["text"]
        if transport.startswith("stdio"):
            assert "x-mcp-header" not in text_schema
        else:
            assert text_schema["x-mcp-header"] == "Text"
        for text in ("雪\nline", "=?base64?literal?="):
            result = json.loads(await client.call_tool("echo", {"text": text}))
            assert result["structuredContent"] == {"text": text}
            assert json.loads(result["content"][0]["text"]) == {"text": text}
        with pytest.raises(MCPToolExecutionError) as failed:
            await client.call_tool("echo", {"fail": True})
        assert failed.value.failure_code == "tool_error"
        assert "synthetic-private-exception" not in str(failed.value)
        assert sum(row["event"] == "handler_start" for row in rows(counter)) == 3
    requests = [row for row in rows(counter) if row["event"] == "request"]
    assert requests and all(row["version"] == VERSION for row in requests)
    assert all(row["has_capabilities"] for row in requests)
    assert all(row["method"] != "initialize" for row in requests)
    assert sum(row["event"] == "handler_terminal" for row in rows(counter)) == 3
    assert not [task for task in asyncio.all_tasks() - before if not task.done()]


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ["stdio-modern", "json", "sse"])
@pytest.mark.parametrize("end", ["cancel", "timeout"])
async def test_cross_transport_cancel_and_parallel_call(
    tmp_path, monkeypatch, transport, end
):
    before = set(asyncio.all_tasks())
    async with friday_client(tmp_path, monkeypatch, transport) as (client, counter, _):
        await client.list_tools()
        if end == "timeout":
            client.request_timeout_seconds = 0.5
        held = asyncio.create_task(client.call_tool("echo", {"hold": True}))
        try:
            await wait_event(counter, "handler_start", 1)
            result = json.loads(await client.call_tool("echo", {"text": "parallel"}))
            assert result["structuredContent"] == {"text": "parallel"}
            await wait_event(counter, "handler_terminal", 1)
            assert not held.done()
            if end == "cancel":
                held.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await held
            else:
                with pytest.raises(TimeoutError):
                    await held
            await wait_event(counter, "handler_terminal", 2)
            assert sum(row["event"] == "handler_start" for row in rows(counter)) == 2
            assert sum(row["event"] == "handler_terminal" for row in rows(counter)) == 2
        finally:
            if not held.done():
                held.cancel()
            await asyncio.gather(held, return_exceptions=True)
    assert not [task for task in asyncio.all_tasks() - before if not task.done()]


def runtime_helpers():
    import importlib.util

    name = "up06_runtime_integration_helpers"
    if name not in sys.modules:
        path = (
            ROOT / "packages/friday-runtime/tests_runtime/test_mcp_http_integration.py"
        )
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


@asynccontextmanager
async def friday_entry(tmp_path, monkeypatch, transport):
    if transport == "stdio":
        counter = tmp_path / "assembly-stdio.jsonl"
        entry = {
            "name": "friday",
            "transport": "stdio",
            "command": sys.executable,
            "args": [str(FIXTURE), "stdio", str(counter)],
            "protocol_profile": "modern",
            "required": True,
            "retry_attempts": 0,
        }
        yield entry, counter
    else:
        async with tls_friday(tmp_path, transport) as (url, context, counter, _):
            monkeypatch.setattr(
                "friday_mcp.client.http.ssl.create_default_context", lambda: context
            )
            port = int(url.split(":")[2].split("/")[0])
            yield (
                {
                    "name": "friday",
                    "transport": "streamable_http",
                    "protocol_version": VERSION,
                    "trust_level": "remote",
                    "url": url,
                    "network": {
                        "allowed_addresses": ["127.0.0.1"],
                        "allowed_ports": [port],
                    },
                    "required": True,
                    "retry_attempts": 0,
                },
                counter,
            )
    await wait_event(counter, "server_stopped", 1)
    assert rows(counter)[-1] == {"event": "server_stopped", "active": 0}


def selected_stanza(entry):
    return {
        "enabled": True,
        "mode": "selected",
        "include_tools": ["mcp_friday_echo"],
        "config": {
            "security": {
                "integrated_transport": "stdio_and_streamable_http",
                "trust_posture": "explicit_remote",
            },
            "servers": [entry],
        },
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ["stdio", "json", "sse"])
async def test_runtime_yaml_to_friday_peer(tmp_path, monkeypatch, transport, caplog):
    from friday_telemetry import DebugTelemetryRecorder

    before = set(asyncio.all_tasks())
    async with friday_entry(tmp_path, monkeypatch, transport) as (entry, counter):
        kernel = runtime_helpers().kernel_from_yaml(
            tmp_path, monkeypatch, selected_stanza(entry)
        )
        recorder = DebugTelemetryRecorder()
        monkeypatch.setattr(
            kernel._di,
            "_create_telemetry",
            lambda: setattr(kernel._di, "telemetry", recorder),
        )
        try:
            await kernel.start()
            provider = kernel.mcp_provider
            tool = kernel.tool_registry.get("mcp_friday_echo")
            assert provider is not None and tool is not None
            assert list(provider.tool_metadata) == ["mcp_friday_echo"]
            assert "x-mcp-header" not in json.dumps(tool.parameters_schema)
            sentinel = "SYNTHETIC_AGGREGATE_雪"
            result = await kernel.tool_registry.get_callable("mcp_friday_echo")(
                text=sentinel
            )
            assert json.loads(result)["structuredContent"] == {"text": sentinel}
            ingestion = kernel.config.tools.providers.mcp.config.ingestion
            assert not ingestion.long_term_memory_enabled
            assert (
                sentinel
                not in repr(provider.operational_diagnostics)
                + repr(recorder.events)
                + caplog.text
            )
            names = [event.name for event in recorder.events]
            assert names.count("mcp.tool_call_start") == 1
            assert names.count("mcp.tool_call_finish") == 1
            await kernel.stop()
            await kernel.stop()
            assert provider.owned_tool_names == ()
            assert provider.manager.connected_servers == []
            recorder.capture_event("up06.borrowed_observer", {})
            assert recorder.events[-1].name == "up06.borrowed_observer"
        finally:
            await kernel.stop()
    assert sum(row["event"] == "handler_start" for row in rows(counter)) == 1
    assert sum(row["event"] == "handler_terminal" for row in rows(counter)) == 1
    assert not [task for task in asyncio.all_tasks() - before if not task.done()]


def chat_from_yaml(tmp_path, monkeypatch, stanza):
    import yaml
    from friday_chat.config import load_friday_py_config
    from friday_chat.runtime import (
        FakeChatModel,
        FakeEmbeddingService,
        FakeMaintenanceService,
        FakeMemoryController,
        FakeTranscriptStore,
        build_runtime,
    )
    from friday_telemetry import DebugTelemetryRecorder

    values = {
        "llm": {"model": "openai/test-chat-model"},
        "embedding": {"model": "openai/test-embedding-model"},
        "memory": {"persist_directory": str(tmp_path / "vectors")},
        "maintenance": {"backup_directory": str(tmp_path / "recovery")},
        "transcript": {"export_directory": str(tmp_path / "exports")},
        "lifecycle": {"enabled": False},
        "telemetry": {"enabled": True, "provider": "debug"},
        "tools": {
            "registry": [],
            "context": {"max_budget_ratio": 1.0, "max_mcp_tools": 1},
            "providers": {"mcp": stanza},
        },
    }
    path = tmp_path / "chat.yaml"
    path.write_text(yaml.safe_dump(values))
    config = load_friday_py_config(path, env={})
    model = FakeChatModel("controlled")
    memory = FakeMemoryController()
    memory.recovery_graph_store = None
    transcript = FakeTranscriptStore()
    transcript.store = None
    maintenance = FakeMaintenanceService({})
    maintenance.access_buffer = None
    maintenance.budget_monitor = None
    maintenance.compactor = None
    # Only non-MCP services are inert. YAML, real assembly, registry and selection run.
    factories = {
        "build_framework_chat_model": model,
        "build_framework_embedding_service": FakeEmbeddingService("controlled"),
        "build_framework_memory_adapter": memory,
        "build_framework_transcript_adapter": transcript,
        "build_framework_maintenance_adapter": maintenance,
    }
    for name, service in factories.items():
        monkeypatch.setattr(
            "friday_chat.adapters." + name,
            lambda *args, value=service, **kwargs: value,
        )
    monkeypatch.chdir(tmp_path)
    recorder = DebugTelemetryRecorder()
    runtime = build_runtime(config, fake=False, telemetry=recorder)
    return runtime, model, memory, recorder


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ["stdio", "json", "sse"])
async def test_chat_real_yaml_factory_to_friday_peer(
    tmp_path, monkeypatch, transport, caplog
):
    from friday_chat.tools.mcp import MCPChatRegistry

    before = set(asyncio.all_tasks())
    async with friday_entry(tmp_path, monkeypatch, transport) as (entry, counter):
        runtime, model, memory, recorder = chat_from_yaml(
            tmp_path, monkeypatch, selected_stanza(entry)
        )
        assert isinstance(runtime.tools, MCPChatRegistry)
        assert runtime.tools is runtime.mcp_tools
        try:
            await runtime.start_mcp_tools()
            runtime.tool_selection.inject_manual(("mcp_friday_echo",))
            selection = runtime.tool_selection.select_for_turn("synthetic")
            assert [tool.name for tool in selection.definitions] == ["mcp_friday_echo"]
            assert selection.budget.selected_mcp_count == 1
            assert (
                selection.budget.schema_tokens <= selection.budget.maximum_schema_tokens
            )
            assert "x-mcp-header" not in selection.budget.schema_bytes.decode()
            sentinel = "SYNTHETIC_CHAT_雪"
            record = await runtime.mcp_tools.call_tool_record(
                "mcp_friday_echo", {"text": sentinel}
            )
            assert record.arguments == {}
            assert record.mcp_provenance.status == "succeeded"
            assert not record.mcp_provenance.memory_ingested
            assert sentinel not in record.result
            assert "[REDACTED]" in record.result
            assert "structuredContent" in record.result
            assert record.mcp_provenance.output_sanitization_state == "sanitized"
            assert "<untrusted_content" in record.result
            assert memory.ingested_documents == [] and model.calls == []
            assert (
                sentinel
                not in repr(recorder.events)
                + repr(runtime.mcp_tools.provider.operational_diagnostics)
                + caplog.text
            )
            names = [event.name for event in recorder.events]
            assert names.count("mcp.tool_call_start") == 1
            assert names.count("mcp.tool_call_finish") == 1
            await runtime.stop_mcp_tools()
            await runtime.stop_mcp_tools()
            assert runtime.mcp_tools.provider.owned_tool_names == ()
            assert runtime.mcp_tools.provider.manager.connected_servers == []
            recorder.capture_event("up06.borrowed_observer", {})
            assert recorder.events[-1].name == "up06.borrowed_observer"
        finally:
            await runtime.stop_mcp_tools()
            await runtime.async_clients.close()
    assert sum(row["event"] == "handler_start" for row in rows(counter)) == 1
    assert sum(row["event"] == "handler_terminal" for row in rows(counter)) == 1
    assert not [task for task in asyncio.all_tasks() - before if not task.done()]


DOCUMENTS = (
    "docs/guides/17-mcp-client.md",
    "docs/guides/18-mcp-server.md",
    "docs/guides/19-mcp-migration.md",
    "packages/friday-mcp/README.md",
)


def published_fences(language):
    import re

    entries = []
    for document in DOCUMENTS:
        text = (ROOT / document).read_text()
        for match in re.finditer(
            r"^```" + language + r"\n(.*?)^```", text, re.M | re.S
        ):
            line = text[: match.start(1)].count("\n") + 1
            entries.append((document, line, match.group(1)))
    return entries


@pytest.mark.parametrize(
    "document,line,excerpt",
    published_fences("yaml"),
    ids=lambda value: str(value)[:70],
)
def test_documented_yaml_loads_both_public_schemas(
    document, line, excerpt, tmp_path, monkeypatch
):
    import copy
    import socket

    import yaml
    from friday_chat.config import load_friday_py_config
    from friday_runtime.config import RuntimeConfig

    def forbidden(*args, **kwargs):
        raise AssertionError(f"Loader attempted I/O for {document}:{line}")

    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr("friday_runtime.mcp_clients.create_mcp_client", forbidden)
    values = yaml.safe_load(excerpt)
    assert "mcp" in values["tools"]["providers"]
    original = copy.deepcopy(values["tools"]["providers"]["mcp"])
    # Only the documented local env placeholder is resolved for the headless caller.
    for entry in values["tools"]["providers"]["mcp"]["config"]["servers"]:
        if "env" in entry:
            assert entry["env"] == {"EXAMPLE_API_KEY": "${EXAMPLE_API_KEY}"}
            entry["env"]["EXAMPLE_API_KEY"] = "SYNTHETIC_LOCAL_VALUE"
    values["runtime_paths"] = private_roots(tmp_path)
    runtime_path = tmp_path / "runtime.yaml"
    runtime_path.write_text(yaml.safe_dump(values))
    runtime = RuntimeConfig.from_sources(yaml_path=runtime_path, env={})
    chat_values = yaml.safe_load(excerpt)
    chat_values["llm"] = {"model": "openai/test-chat-model"}
    chat_path = tmp_path / "chat.yaml"
    chat_path.write_text(yaml.safe_dump(chat_values))
    chat = load_friday_py_config(
        chat_path, env={"EXAMPLE_API_KEY": "SYNTHETIC_LOCAL_VALUE"}
    )
    assert runtime.tools.providers.mcp == chat.tools.mcp_provider
    assert original == yaml.safe_load(excerpt)["tools"]["providers"]["mcp"]
    for entry in runtime.tools.providers.mcp.config.servers:
        if entry.transport == "stdio":
            assert entry.protocol_profile in {"legacy", "modern", "auto"}
            if "protocol_profile" not in next(
                item
                for item in original["config"]["servers"]
                if item["name"] == entry.name
            ):
                assert entry.protocol_profile == "legacy"
        else:
            assert entry.protocol_version in {VERSION, "2025-11-25"}
            assert entry.credential_env == "FRIDAY_REMOTE_MCP_TOKEN"
            assert "SYNTHETIC_LOCAL_VALUE" not in repr(entry)
    assert "FRIDAY_REMOTE_MCP_TOKEN" not in os.environ


@pytest.mark.parametrize("document,line,excerpt", published_fences("python"))
def test_documented_python_compiles_public_exports_and_keywords(
    document, line, excerpt
):
    import ast
    import importlib
    import inspect

    tree = ast.parse(excerpt, filename=f"{document}:{line}")
    compile(tree, f"{document}:{line}", "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    exports = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module.startswith("friday_"):
            module = importlib.import_module(node.module)
            for item in node.names:
                exports[item.asname or item.name] = getattr(module, item.name)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            factory = exports.get(node.func.id)
            if factory is not None and callable(factory):
                signature = inspect.signature(factory)
                signature.bind(
                    *[None for _ in node.args],
                    **{item.arg: None for item in node.keywords},
                )


@pytest.mark.parametrize(
    "invalid", ["mixed", "unknown", "interpolated_reference", "disabled_required"]
)
def test_documented_invalid_config_rejected_without_io(invalid, tmp_path, monkeypatch):
    import copy
    import socket

    import yaml
    from friday_chat.config import load_friday_py_config
    from friday_runtime.config import RuntimeConfig

    def forbidden(*args, **kwargs):
        raise AssertionError("Invalid config attempted I/O")

    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr("friday_runtime.mcp_clients.create_mcp_client", forbidden)
    examples = published_fences("yaml")
    stanza = next(
        yaml.safe_load(excerpt)
        for document, _, excerpt in examples
        if document.endswith("19-mcp-migration.md") and "'2026-07-28'" in excerpt
    )
    values = copy.deepcopy(stanza)
    entry = values["tools"]["providers"]["mcp"]["config"]["servers"][0]
    if invalid == "mixed":
        entry["command"] = "/absolute/path/to/trusted-server"
    elif invalid == "unknown":
        entry["unknown_transport_option"] = True
    elif invalid == "interpolated_reference":
        entry["credential_env"] = "${FRIDAY_REMOTE_MCP_TOKEN}"
    else:
        entry["enabled"] = False
    # Also disabled providers must validate the complete strict transport union.
    values["tools"]["providers"]["mcp"]["enabled"] = False
    values["runtime_paths"] = private_roots(tmp_path)
    path = tmp_path / "invalid.yaml"
    path.write_text(yaml.safe_dump(values))
    with pytest.raises(ValueError):
        RuntimeConfig.from_sources(yaml_path=path, env={})
    values["llm"] = {"model": "openai/test-chat-model"}
    path.write_text(yaml.safe_dump(values))
    with pytest.raises(ValueError):
        load_friday_py_config(path, env={})


@pytest.mark.asyncio
async def test_documented_disabled_real_assemblies_do_not_connect(
    tmp_path, monkeypatch
):
    import yaml

    excerpt = next(
        text
        for doc, _, text in published_fences("yaml")
        if doc.endswith("19-mcp-migration.md") and "enabled: false" in text
    )
    stanza = yaml.safe_load(excerpt)["tools"]["providers"]["mcp"]

    def forbidden(*args, **kwargs):
        raise AssertionError("Disabled provider attempted client construction")

    monkeypatch.setattr("friday_runtime.mcp_clients.create_mcp_client", forbidden)
    kernel = runtime_helpers().kernel_from_yaml(tmp_path, monkeypatch, stanza)
    runtime, model, memory, _ = chat_from_yaml(tmp_path, monkeypatch, stanza)
    try:
        await kernel.start()
        await runtime.start_mcp_tools()
        assert runtime.mcp_tools is None
        assert model.calls == [] and memory.ingested_documents == []
    finally:
        await kernel.stop()
        await runtime.stop_mcp_tools()
        await runtime.async_clients.close()


def private_roots(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir(exist_ok=True)
    return {
        "install_root": str(tmp_path),
        "runtime_data_root": str(tmp_path / "state"),
        "workspace_root": str(workspace),
    }


@asynccontextmanager
async def documented_peer(tmp_path, monkeypatch, excerpt):
    import yaml

    values = yaml.safe_load(excerpt)
    stanza = values["tools"]["providers"]["mcp"]
    entry = stanza["config"]["servers"][0]
    if entry["transport"] == "stdio":
        entry["command"] = sys.executable
        if "protocol_profile" in entry:
            counter = tmp_path / "published-stdio.jsonl"
            entry["args"] = [str(FIXTURE), "stdio", str(counter)]
            yield stanza, "mcp_owned_echo", counter
            await wait_event(counter, "server_stopped", 1)
            assert rows(counter)[-1] == {"event": "server_stopped", "active": 0}
        else:
            entry["args"] = [str(ROOT / "tests/integration/mcp_fake_server.py"), "good"]
            yield stanza, "mcp_owned_probe", None
    else:
        import signal

        async with runtime_helpers().tls_peer(
            tmp_path,
            monkeypatch,
            entry["protocol_version"],
            bearer="SYNTHETIC_DOCUMENT_TOKEN",
        ) as (private, child, counter, _, _):
            entry["url"] = private["url"]
            entry["network"] = private["network"]
            monkeypatch.setenv("FRIDAY_REMOTE_MCP_TOKEN", "SYNTHETIC_DOCUMENT_TOKEN")
            yield stanza, "mcp_owned_echo", None
            assert len(runtime_helpers().records(counter)) > 0
        # Retained SDK/2025 fixture helper explicitly terminates its listener.
        assert child.returncode in (0, -signal.SIGTERM)


@pytest.mark.asyncio
@pytest.mark.parametrize("assembly", ["runtime", "chat"])
@pytest.mark.parametrize(
    "document,line,excerpt",
    [
        (doc, line, text)
        for doc, line, text in published_fences("yaml")
        if doc.endswith("19-mcp-migration.md") and "enabled: true" in text
    ],
)
async def test_documented_profiles_execute_named_peers(
    assembly, document, line, excerpt, tmp_path, monkeypatch
):
    before = set(asyncio.all_tasks())
    async with documented_peer(tmp_path, monkeypatch, excerpt) as (
        stanza,
        name,
        counter,
    ):
        if assembly == "runtime":
            runtime = runtime_helpers().kernel_from_yaml(tmp_path, monkeypatch, stanza)
            try:
                await runtime.start()
                provider = runtime.mcp_provider
                result = await runtime.tool_registry.get_callable(name)(
                    **({"text": "雪"} if name.endswith("echo") else {})
                )
                assert (
                    "雪" in result
                    if name.endswith("echo")
                    else '"peer": "good"' in result
                )
            finally:
                await runtime.stop()
                await runtime.stop()
        else:
            runtime, model, memory, _ = chat_from_yaml(tmp_path, monkeypatch, stanza)
            try:
                await runtime.start_mcp_tools()
                provider = runtime.mcp_tools.provider
                runtime.tool_selection.inject_manual((name,))
                assert runtime.tool_selection.select_for_turn(
                    "synthetic"
                ).budget.selected_names == (name,)
                record = await runtime.mcp_tools.call_tool_record(
                    name, {"text": "雪"} if name.endswith("echo") else {}
                )
                assert record.mcp_provenance.status == "succeeded"
                assert not record.mcp_provenance.memory_ingested
                assert record.arguments == {}
                assert memory.ingested_documents == [] and model.calls == []
            finally:
                await runtime.stop_mcp_tools()
                await runtime.stop_mcp_tools()
                await runtime.async_clients.close()
        assert provider.owned_tool_names == ()
        assert provider.manager.connected_servers == []
    if counter is not None:
        assert sum(row["event"] == "handler_start" for row in rows(counter)) == 1
        assert sum(row["event"] == "handler_terminal" for row in rows(counter)) == 1
    assert not [task for task in asyncio.all_tasks() - before if not task.done()]
