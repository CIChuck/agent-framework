# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Real local subprocess integration, with unrelated LLM/storage services stubbed."""

import asyncio
import contextlib
import logging
import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from friday_core.profiles import MemoryProfile
from friday_mcp.client.stdio import StdioMCPClient, StdioTransport
from friday_runtime.config import RuntimeConfig, ToolsConfig
from friday_runtime.kernel import RuntimeKernel
from friday_runtime.tool_loading import ToolProviderLoadError

FAKE_SERVER = Path(__file__).with_name("mcp_fake_server.py").resolve()
# Production attempt budget is 11 seconds (including failed task settlement).
# Two seconds of scheduling slack, not a replacement RPC or shutdown SLA.
CLEANUP_TEST_BOUND = 13


def kernel_for(tmp_path, monkeypatch, servers, enabled=True):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (tmp_path / "install").mkdir()
    kernel = RuntimeKernel(
        RuntimeConfig(
            install_root=str(tmp_path / "install"),
            runtime_data_root=str(tmp_path / "state"),
            workspace_root=str(workspace),
            agents_dir=str(workspace / "agents"),
            tools_config=ToolsConfig.from_dict(
                {
                    "providers": {
                        "builtin": {"enabled": True, "mode": "all"},
                        "mcp": {
                            "enabled": enabled,
                            "config": {"servers": servers},
                        },
                    }
                }
            ),
        ),
        MemoryProfile.TESTING,
    )
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


def server(name, mode="good", required=False):
    return {
        "name": name,
        "command": sys.executable,
        "args": ["-u", str(FAKE_SERVER), mode, "SENTINEL-ARG-SECRET"],
        "env": {"FAKE_KEY": "SENTINEL-ENV-SECRET"},
        "timeout_seconds": 1,
        "retry_attempts": 0,
        "required": required,
    }


@pytest.fixture
async def processes(monkeypatch):
    observed = []
    transports = []
    original = asyncio.create_subprocess_exec
    connect = StdioTransport.connect

    async def spawn(*args, **kwargs):
        process = await original(*args, **kwargs)
        observed.append(process)
        return process

    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)

    async def track_connect(transport):
        transports.append(transport)
        await connect(transport)

    async def discard(stream):
        if stream is not None:
            while await stream.read(4096):
                pass

    monkeypatch.setattr(StdioTransport, "connect", track_connect)
    try:
        yield observed
    finally:
        # Defensive fixture work occurs AFTER public-cleanup assertions. It
        # cannot make those assertions pass, including when an assertion fails.
        for transport in transports:
            with contextlib.suppress(Exception):
                await asyncio.wait_for(transport.disconnect(), CLEANUP_TEST_BOUND)
        for process in observed:
            if process.returncode is None:
                with contextlib.suppress(ProcessLookupError):
                    process.kill()
            await asyncio.wait_for(
                asyncio.gather(discard(process.stdout), discard(process.stderr)), 2
            )
            await asyncio.wait_for(process.wait(), 2)


@pytest.mark.asyncio
async def test_real_runtime_success_native_tools_and_local_stdio_shutdown(
    tmp_path, monkeypatch, processes, caplog
):
    kernel = kernel_for(tmp_path, monkeypatch, [server("fake")])
    with caplog.at_level(logging.DEBUG):
        await kernel.start()
        provider = kernel.mcp_provider
        assert provider.discovery.status == "completed"
        assert len(provider.prepared_tools) == 1
        assert "recall_memory" in kernel.tool_registry.list_names()
        assert "mcp_fake_probe" not in kernel.tool_registry.list_names()
        assert provider.diagnostics.registered_tools == 0
        client = provider.manager.get_client("fake")
        assert isinstance(client, StdioMCPClient)
        assert client.cwd == tmp_path / "workspace"
        await kernel.stop()
        await kernel.stop()
    assert processes and all(process.returncode is not None for process in processes)
    assert "SENTINEL" not in caplog.text
    assert provider.discovery.servers[0].connection_state == "disconnected"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode,outcome",
    [
        ("handshake_fail", "connection_failed"),
        ("handshake_timeout", "connection_timeout"),
        ("list_fail", "discovery_failed"),
        ("list_timeout", "discovery_timeout"),
        ("exit", "connection_failed"),
    ],
)
@pytest.mark.parametrize("required", [False, True])
async def test_real_optional_and_required_failure_cleanup(
    tmp_path, monkeypatch, processes, caplog, mode, outcome, required
):
    kernel = kernel_for(tmp_path, monkeypatch, [server("fake", mode, required)])
    with caplog.at_level(logging.DEBUG):
        if required:
            with pytest.raises(
                ToolProviderLoadError, match="Required MCP server unavailable"
            ):
                await kernel.start()
            assert not kernel._initialized
        else:
            await kernel.start()
            assert kernel._initialized
            assert not any(
                name.startswith("mcp_") for name in kernel.tool_registry.list_names()
            )
        assert kernel.mcp_provider.lifecycle[0].outcome == outcome
        assert not kernel.mcp_provider.manager.connected_servers
        await kernel.stop()
    assert processes and all(process.returncode is not None for process in processes)
    assert "SENTINEL" not in caplog.text


@pytest.mark.asyncio
async def test_real_partial_success_and_disabled_provider(
    tmp_path, monkeypatch, processes
):
    kernel = kernel_for(
        tmp_path, monkeypatch, [server("good"), server("bad", "list_fail")]
    )
    await kernel.start()
    assert kernel.mcp_provider.discovery.status == "partial"
    assert kernel.mcp_provider.manager.connected_servers == ["good"]
    assert [tool.server_id for tool in kernel.mcp_provider.prepared_tools] == ["good"]
    await kernel.stop()
    assert all(process.returncode is not None for process in processes)
    other = tmp_path / "disabled"
    other.mkdir()
    disabled = kernel_for(other, monkeypatch, [server("off")], enabled=False)
    count = len(processes)
    await disabled.start()
    await disabled.stop()
    assert disabled.mcp_provider is None
    assert len(processes) == count


@pytest.mark.asyncio
async def test_real_process_already_exited_disconnect_is_idempotent(processes):
    transport = StdioTransport(sys.executable, ["-c", "pass"])
    await transport.connect()
    process = transport._process
    await process.wait()
    await transport.disconnect()
    await transport.disconnect()
    assert transport._process is None
    assert not transport.is_connected


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["handshake_timeout", "list_timeout"])
async def test_real_cancel_startup_reaps_child(tmp_path, monkeypatch, processes, mode):
    kernel = kernel_for(tmp_path, monkeypatch, [server("fake", mode)])
    task = asyncio.create_task(kernel.start())

    async def wait_for_child():
        while not processes:
            await asyncio.sleep(0)

    await asyncio.wait_for(wait_for_child(), timeout=2)
    await asyncio.sleep(0.03)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert not kernel._initialized
    assert not kernel.mcp_provider.manager.connected_servers
    assert kernel.mcp_provider.discovery.status == "failed"
    assert all(process.returncode is not None for process in processes)
    await kernel.stop()


def assert_public_resources_released(processes):
    assert processes
    for process in processes:
        assert process.returncode is not None
        assert process.stdout.at_eof()
        assert process.stderr.at_eof()
        assert process.stdin.is_closing()
    assert not any(
        task.get_name().startswith("mcp-stdio-")
        or task.get_coro().__qualname__ == "MCPClientBase._receive_loop"
        or task.get_coro().__qualname__ == "RuntimeMCPProvider._discover"
        for task in asyncio.all_tasks()
        if task is not asyncio.current_task()
    )


async def receiver_failure_seen(caplog):
    while "MCP receive failed" not in caplog.text:
        await asyncio.sleep(0)


@pytest.mark.asyncio
async def test_real_direct_transport_noisy_forced_kill_is_bounded(processes, caplog):
    transport = StdioTransport(
        sys.executable,
        ["-u", str(FAKE_SERVER), "noisy_success", "SENTINEL-ARG"],
        {"KEY": "SENTINEL-ENV"},
    )
    with caplog.at_level(logging.DEBUG):
        await transport.connect()
        await transport.send({"id": 1, "method": "initialize"})
        assert (await transport.receive())["id"] == 1
        await transport.send({"id": 2, "method": "tools/list"})
        assert (await transport.receive())["id"] == 2
        # Observed oversized unterminated line proves the protocol reader has
        # stopped, rather than assuming that a sleep means the peer is ready.
        with pytest.raises(ValueError):
            await asyncio.wait_for(transport.receive(), 2)
        await asyncio.wait_for(transport.disconnect(), CLEANUP_TEST_BOUND)
        await transport.disconnect()
    assert processes[0].returncode == -9
    assert not transport.is_connected
    assert_public_resources_released(processes)
    assert "SENTINEL" not in caplog.text


@pytest.mark.asyncio
async def test_real_public_kernel_noisy_success_stop_and_restart(
    tmp_path, monkeypatch, processes, caplog
):
    kernel = kernel_for(tmp_path, monkeypatch, [server("fake", "noisy_success")])
    with caplog.at_level(logging.DEBUG):
        for _ in range(2):
            caplog.clear()
            await kernel.start()
            assert kernel.mcp_provider.discovery.status == "completed"
            assert len(kernel.mcp_provider.prepared_tools) == 1
            assert "SENTINEL" not in repr(kernel.mcp_provider.discovery)
            assert "SENTINEL" not in repr(kernel.mcp_provider.lifecycle)
            await asyncio.wait_for(receiver_failure_seen(caplog), 2)
            await asyncio.wait_for(kernel.stop(), CLEANUP_TEST_BOUND)
            await kernel.stop()
            assert not kernel.mcp_provider.manager.connected_servers
            assert not kernel.mcp_provider.prepared_tools
            assert_public_resources_released(processes)
            assert "SENTINEL" not in caplog.text
    assert all(process.returncode == -9 for process in processes)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode,outcome",
    [
        ("noisy_handshake", "connection_timeout"),
        ("noisy_list_fail", "discovery_failed"),
    ],
)
@pytest.mark.parametrize("required", [False, True])
async def test_real_public_kernel_noisy_partial_start_cleanup(
    tmp_path, monkeypatch, processes, caplog, mode, outcome, required
):
    kernel = kernel_for(
        tmp_path, monkeypatch, [server("fake", mode, required), server("good")]
    )
    with caplog.at_level(logging.DEBUG):
        if required:
            with pytest.raises(
                ToolProviderLoadError, match="Required MCP server unavailable"
            ):
                await asyncio.wait_for(kernel.start(), CLEANUP_TEST_BOUND + 2)
            assert not kernel.mcp_provider.manager.connected_servers
            assert not kernel.mcp_provider.prepared_tools
        else:
            await asyncio.wait_for(kernel.start(), CLEANUP_TEST_BOUND + 2)
            assert kernel.mcp_provider.manager.connected_servers == ["good"]
            assert [tool.server_id for tool in kernel.mcp_provider.prepared_tools] == [
                "good"
            ]
            assert not any(
                name.startswith("mcp_") for name in kernel.tool_registry.list_names()
            )
        assert kernel.mcp_provider.lifecycle[0].outcome == outcome
        assert kernel.mcp_provider.diagnostics.registered_tools == 0
        assert "SENTINEL" not in repr(kernel.mcp_provider.discovery)
        assert "SENTINEL" not in repr(kernel.mcp_provider.lifecycle)
        await asyncio.wait_for(kernel.stop(), CLEANUP_TEST_BOUND)
    assert not kernel.mcp_provider.manager.connected_servers
    assert not kernel.mcp_provider.prepared_tools
    assert any(process.returncode == -9 for process in processes)
    assert_public_resources_released(processes)
    assert "SENTINEL" not in caplog.text
