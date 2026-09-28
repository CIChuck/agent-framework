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
    original = asyncio.create_subprocess_exec

    async def spawn(*args, **kwargs):
        process = await original(*args, **kwargs)
        observed.append(process)
        return process

    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
    yield observed
    # Reap only processes created by this fixture even if an assertion fails.
    for process in observed:
        if process.returncode is None:
            with contextlib.suppress(ProcessLookupError):
                process.terminate()
            await asyncio.wait_for(process.wait(), timeout=5)


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
async def test_real_process_already_exited_disconnect_is_idempotent():
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
