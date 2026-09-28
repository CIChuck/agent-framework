"""Local-only WS-04 Chat startup, commands, callable routing and owner cleanup."""

from __future__ import annotations

import asyncio
import contextlib
import sys
from pathlib import Path

import pytest
from friday_chat.app import FridayChatApp, ListInputSource, ListOutputSink
from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.config import FridayChatConfig, load_friday_py_config
from friday_chat.runtime import FakeChatModel, build_runtime
from friday_chat.tools.mcp import MCPChatRegistry
from friday_chat.turns.models import ChatModelResponse, ToolCallRequest
from friday_chat.turns.processor import TurnProcessor

PEER = Path(__file__).resolve().parents[3] / "tests/integration/mcp_fake_server.py"


def cfg(
    *, mode: str = "registry_a", enabled: bool = True, required: bool = True
) -> FridayChatConfig:
    return FridayChatConfig.model_validate(
        {
            "tools": {
                "providers": {
                    "mcp": {
                        "enabled": enabled,
                        "mode": "all",
                        "config": {
                            "servers": [
                                {
                                    "name": "peer",
                                    "command": sys.executable,
                                    "args": [str(PEER), mode],
                                    "required": required,
                                }
                            ],
                            "limits": {
                                "min_memory_retrieval_tokens": 100,
                                "reserved_tool_result_tokens": 100,
                            },
                        },
                    }
                },
                "context": {"max_budget_ratio": 1.0},
            }
        }
    )


@pytest.fixture
async def processes(monkeypatch: pytest.MonkeyPatch):
    seen = []
    original = asyncio.create_subprocess_exec

    async def spawn(*args, **kwargs):
        process = await original(*args, **kwargs)
        seen.append(process)
        return process

    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
    try:
        yield seen
    finally:
        # Defensive settlement is after assertions of public owner cleanup.
        async def drain(stream):
            if stream is not None:
                while await stream.read(4096):
                    pass

        for process in seen:
            if process.returncode is None:
                with contextlib.suppress(ProcessLookupError):
                    process.kill()
            await asyncio.wait_for(
                asyncio.gather(drain(process.stdout), drain(process.stderr)), 2
            )
            await asyncio.wait_for(process.wait(), 2)


def install(runtime, tmp_path: Path) -> MCPChatRegistry:
    bridge = MCPChatRegistry(
        runtime.tools, runtime.config.tools.mcp_provider, str(tmp_path)
    )
    runtime.tools = bridge
    runtime.mcp_tools = bridge
    return bridge


async def test_real_stdio_chat_turn_routes_exact_name_and_stops(
    tmp_path: Path, processes, caplog
) -> None:
    runtime = build_runtime(cfg())
    bridge = install(runtime, tmp_path)
    native = tuple(bridge.native.list_tools())
    baseline_tasks = set(asyncio.all_tasks())
    try:
        await runtime.start_mcp_tools()
        assert tuple(bridge.native.list_tools()) == native
        assert bridge.tool_metadata["mcp_peer_read_file"].original_name == "Read.File"
        await runtime.start_mcp_tools()
        assert len(processes) == 1
        runtime.tool_selection.inject_manual(("mcp_peer_read_file",))
        runtime.chat_llm = FakeChatModel(
            "fake",
            responses=[
                ChatModelResponse(
                    tool_calls=(
                        ToolCallRequest("mcp_peer_read_file", {"path": "a/b"}, "call1"),
                    )
                ),
                ChatModelResponse.from_text("done"),
            ],
        )
        client = bridge.provider.manager.get_client("peer")
        original = client.call_tool
        routed = []

        async def record_route(name, arguments):
            routed.append((name, arguments))
            return await original(name, arguments)

        client.call_tool = record_route
        result = await TurnProcessor(runtime).process("read fixture")
        assert routed == [("Read.File", {"path": "a/b"})]
        call = result.tool_calls[0]
        assert call.arguments == {} and "a/b" not in call.result
        assert call.mcp_provenance.status == "succeeded"
        assert call.mcp_provenance.tool.original_name == "Read.File"
        assert call.mcp_provenance.failure_code is None
        registry = build_default_registry()
        context = RegistryCommandContext(runtime=runtime, registry=registry)
        for command in ("/tools", "/tool-budget", "/recommend-tools read fixture"):
            handled, output = await registry.execute(command, context)
            assert handled and output is not None
            assert "SENTINEL-STDERR-SECRET" not in output.output
        await runtime.stop_mcp_tools()
        assert (
            bridge.provider.manager is not None
            and bridge.provider.manager.connected_servers == []
        )
        assert bridge.provider.owned_tool_names == ()
        assert bridge.tool_metadata == {}
        assert bridge.list_tools() == native
        assert all(
            p.returncode is not None and p.stdout.at_eof() and p.stderr.at_eof()
            for p in processes
        )
        assert not [t for t in asyncio.all_tasks() - baseline_tasks if not t.done()]
        assert "SENTINEL-STDERR-SECRET" not in caplog.text
    finally:
        await runtime.stop_mcp_tools()


@pytest.mark.parametrize(
    "mode,required", [("registry_a", True), ("list_fail", False), ("list_fail", True)]
)
async def test_app_eof_or_start_failure_cleans_public_owner(
    tmp_path: Path, processes, mode: str, required: bool
) -> None:
    runtime = build_runtime(cfg(mode=mode, required=required))
    bridge = install(runtime, tmp_path)
    app = FridayChatApp(
        runtime=runtime, input_source=ListInputSource([]), output_sink=ListOutputSink()
    )
    try:
        if mode == "list_fail" and required:
            with pytest.raises(RuntimeError):
                await app.run()
        else:
            result = await app.run()
            assert result.turns_processed == 0
        assert (
            bridge.provider.manager is not None
            and bridge.provider.manager.connected_servers == []
            and bridge.tool_metadata == {}
        )
        assert all(
            p.returncode is not None and p.stdout.at_eof() and p.stderr.at_eof()
            for p in processes
        )
        assert not app.started
    finally:
        await runtime.stop_mcp_tools()


async def test_fake_construction_never_connects_configured_peers(processes) -> None:
    runtime = build_runtime(cfg())
    assert runtime.mcp_tools is None
    await runtime.start_mcp_tools()
    assert processes == []


async def test_owner_identity_survives_obstructed_cleanup_and_public_retry(
    tmp_path: Path, processes, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime = build_runtime(cfg())
    bridge = install(runtime, tmp_path)
    try:
        await runtime.start_mcp_tools()
        original = bridge.provider.stop

        async def obstructed():
            raise RuntimeError("fixed cleanup obstruction")

        monkeypatch.setattr(bridge.provider, "stop", obstructed)
        with pytest.raises(RuntimeError):
            await runtime.stop_mcp_tools()
        assert runtime.mcp_tools is bridge
        assert bridge.provider.manager is not None
        monkeypatch.setattr(bridge.provider, "stop", original)
        await runtime.stop_mcp_tools()
        assert all(p.returncode is not None for p in processes)
        await runtime.start_mcp_tools()
        assert runtime.mcp_tools is bridge and len(processes) == 2
    finally:
        await bridge.stop()


def test_invalid_canonical_config_diagnostics_hide_input(tmp_path: Path) -> None:
    path = tmp_path / "chat.yaml"
    path.write_text(
        "llm:\n  model: fake/test\ntools:\n  providers:\n    mcp:\n      enabled: false\n      config:\n        limits:\n          max_servers: 0\n        servers:\n          - name: peer\n            command: SENTINEL_COMMAND_SECRET\n"
    )
    with pytest.raises(ValueError) as error:
        load_friday_py_config(path, env={})
    assert "SENTINEL_COMMAND_SECRET" not in str(error.value)
    assert "max_servers" in str(error.value)


async def test_real_factory_installs_inert_public_bridge(
    tmp_path: Path, processes
) -> None:
    values = cfg().model_dump()
    values.update(
        {
            "llm": {"model": "openai/test-chat-model"},
            "embedding": {"model": "openai/test-embedding-model"},
            "memory": {"persist_directory": str(tmp_path / "vector")},
            "maintenance": {"backup_directory": str(tmp_path / "recovery")},
            "transcript": {"export_directory": str(tmp_path / "exports")},
        }
    )
    values["tools"]["registry"] = []
    runtime = build_runtime(
        FridayChatConfig.model_validate(values),
        fake=False,
        session_id="mcp-real-factory-test",
    )
    try:
        assert isinstance(runtime.tools, MCPChatRegistry)
        assert runtime.mcp_tools is runtime.tools
        assert runtime.mcp_tools.provider.manager is None and processes == []
    finally:
        await runtime.stop_mcp_tools()
        await runtime.async_clients.close()


async def test_app_cancellation_settles_peer_before_return(
    tmp_path: Path, processes
) -> None:
    ready = asyncio.Event()

    class Input:
        async def read(self) -> str:
            ready.set()
            await asyncio.Event().wait()
            return "unused"

    runtime = build_runtime(cfg())
    bridge = install(runtime, tmp_path)
    app = FridayChatApp(
        runtime=runtime, input_source=Input(), output_sink=ListOutputSink()
    )
    task = asyncio.create_task(app.run())
    try:
        await asyncio.wait_for(ready.wait(), 3)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(task, 13)
        assert bridge.tool_metadata == {} and bridge.provider.owned_tool_names == ()
        assert all(
            p.returncode is not None and p.stdout.at_eof() and p.stderr.at_eof()
            for p in processes
        )
        assert not app.started
    finally:
        if not task.done():
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        await runtime.stop_mcp_tools()


async def test_chat_native_collision_fails_without_losing_native_owner(
    tmp_path: Path, processes
) -> None:
    from friday_chat.runtime import FakeToolRegistry
    from friday_chat.tools.schemas import ToolDefinition

    runtime = build_runtime(cfg())
    native = ToolDefinition(
        "mcp_peer_read_file", "Native fixture", {"type": "object"}, "utility"
    )
    runtime.tools = FakeToolRegistry((native,))
    bridge = install(runtime, tmp_path)
    try:
        with pytest.raises(RuntimeError, match="name_collision"):
            await runtime.start_mcp_tools()
        assert bridge.native.list_tools()[0] is native
        assert bridge.tool_metadata == {} and bridge.provider.owned_tool_names == ()
        collision = bridge.provider.registration_decisions[-1].collision
        assert collision is not None and collision.first.provider == "native"
        assert all(p.returncode is not None for p in processes)
    finally:
        await runtime.stop_mcp_tools()
