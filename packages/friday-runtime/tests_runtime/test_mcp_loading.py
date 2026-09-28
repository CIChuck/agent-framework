# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Runtime MCP lifecycle, deterministic caps and owned registry publication."""

import asyncio
import logging
from unittest.mock import AsyncMock

import pytest
from friday_agent import DefaultToolRegistry
from friday_core.profiles import MemoryProfile
from friday_mcp.client.base import MCPClientBase
from friday_mcp.client.manager import MCPClientManager
from friday_runtime.config import MCPToolProviderConfig, RuntimeConfig, ToolsConfig
from friday_runtime.kernel import RuntimeKernel
from friday_runtime.mcp_loading import RuntimeMCPProvider
from friday_runtime.tool_loading import ToolProviderLoadError


class TestTransport:
    __test__ = False

    def __init__(self):
        self.is_connected = False
        self.disconnect_calls = 0
        self.fail_cleanup = False
        self.pause_cleanup = False
        self.cleanup_entered = asyncio.Event()

    async def connect(self):
        self.is_connected = True

    async def disconnect(self):
        self.disconnect_calls += 1
        self.cleanup_entered.set()
        if self.pause_cleanup:
            await asyncio.Future()
        if self.fail_cleanup:
            raise RuntimeError("SENTINEL-CLEANUP-SECRET")
        self.is_connected = False

    async def send(self, message):
        pass

    async def receive(self):
        await asyncio.Future()


class TestClient(MCPClientBase):
    __test__ = False

    def __init__(self, name, mode, tracker, tools):
        super().__init__(name)
        self.transport = TestTransport()
        self.transport.fail_cleanup = mode == "discovery_cleanup_failed"
        self.mode = mode
        self.tracker = tracker
        self.tools = tools
        self.entered = asyncio.Event()

    async def _create_transport(self):
        return self.transport

    async def _initialize(self):
        self.entered.set()
        self.tracker["active"] += 1
        self.tracker["peak"] = max(self.tracker["peak"], self.tracker["active"])
        try:
            await asyncio.sleep(0.01)
            if self.mode == "connection_failed":
                raise ValueError("SENTINEL-SECRET")
            if self.mode == "connection_timeout":
                await asyncio.Future()
        finally:
            self.tracker["active"] -= 1

    async def list_tools(self):
        self.tracker["list_calls"] = self.tracker.get("list_calls", 0) + 1
        self.tracker["discovery_active"] += 1
        self.tracker["discovery_peak"] = max(
            self.tracker["discovery_peak"], self.tracker["discovery_active"]
        )
        try:
            if self.mode in ("discovery_failed", "discovery_cleanup_failed"):
                raise ValueError("SENTINEL-SECRET")
            if self.mode == "discovery_timeout":
                await asyncio.Future()
            await asyncio.sleep(0.01)
            return self.tools
        finally:
            self.tracker["discovery_active"] -= 1


def provider_config(servers=(), **config):
    return MCPToolProviderConfig.from_dict(
        {
            "enabled": True,
            "config": {"servers": list(servers), **config},
        }
    )


def server(name="fake", **values):
    return {"name": name, "command": "fake", "retry_attempts": 0, **values}


@pytest.fixture
async def fake_clients(monkeypatch):
    clients = []
    modes = {}
    catalogs = {}
    tracker = {"active": 0, "peak": 0, "discovery_active": 0, "discovery_peak": 0}

    def create(self, config):
        mode = modes.get(config.name, "good")
        if isinstance(mode, list):
            mode = mode.pop(0)
        client = TestClient(
            config.name,
            mode,
            tracker,
            catalogs.get(
                config.name, [{"name": "probe", "inputSchema": {"type": "object"}}]
            ),
        )
        clients.append(client)
        return client

    monkeypatch.setattr(MCPClientManager, "_create_client", create)
    try:
        yield clients, modes, catalogs, tracker
    finally:
        # Release synthetic transports even when a regression assertion fails.
        for client in clients:
            client.transport.fail_cleanup = False
            client.transport.pause_cleanup = False
            await client.disconnect()


@pytest.mark.asyncio
@pytest.mark.parametrize("enabled", [False, True])
async def test_no_servers_and_disabled_are_lightweight(tmp_path, fake_clients, enabled):
    config = MCPToolProviderConfig.from_dict({"enabled": enabled})
    provider = RuntimeMCPProvider(config, str(tmp_path))
    await provider.start()
    assert not fake_clients[0]
    assert provider.discovery.status == ("completed" if enabled else "not_started")
    assert (provider.manager is not None) == enabled
    await provider.stop()
    await provider.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "outcome",
    [
        "connection_failed",
        "discovery_failed",
        "connection_timeout",
        "discovery_timeout",
    ],
)
@pytest.mark.parametrize("required", [False, True])
async def test_optional_and_required_failure_semantics(
    tmp_path, fake_clients, caplog, outcome, required
):
    clients, modes, _, _ = fake_clients
    modes["fake"] = outcome
    provider = RuntimeMCPProvider(
        provider_config([server(required=required, timeout_seconds=1)]), str(tmp_path)
    )
    with caplog.at_level(logging.DEBUG):
        if required:
            with pytest.raises(
                ToolProviderLoadError, match="Required MCP server unavailable"
            ):
                await provider.start()
        else:
            await provider.start()
    assert provider.lifecycle[0].outcome == outcome
    assert provider.lifecycle[0].required == required
    assert provider.discovery.status == ("failed" if required else "partial")
    assert provider.discovery.failed_servers == 1
    assert not provider.prepared_tools
    assert not provider.manager.connected_servers
    assert all(not client.transport.is_connected for client in clients)
    assert "SENTINEL" not in caplog.text
    assert "SENTINEL" not in str(provider.discovery.model_dump())
    await provider.stop()


@pytest.mark.asyncio
async def test_partial_success_disabled_server_and_idempotent_shutdown(
    tmp_path, fake_clients
):
    clients, modes, _, _ = fake_clients
    modes["bad"] = "discovery_failed"
    provider = RuntimeMCPProvider(
        provider_config(
            [
                server("good"),
                server("bad"),
                {"name": "off", "enabled": False},
            ]
        ),
        str(tmp_path),
    )
    await provider.start()
    manager = provider.manager
    await provider.start()
    assert provider.manager is manager
    assert manager.connected_servers == ["good"]
    assert [event.outcome for event in provider.lifecycle] == [
        "connected",
        "discovery_failed",
        "disabled",
    ]
    assert provider.discovery.status == "partial"
    assert [tool.server_id for tool in provider.prepared_tools] == ["good"]
    assert provider.diagnostics.registered_tools == 0
    assert provider.discovery.selected_tools == 0
    await provider.stop()
    await provider.stop()
    assert not provider.prepared_tools
    assert all(not client.transport.is_connected for client in clients)
    assert all(client.transport.disconnect_calls == 1 for client in clients)
    assert provider.discovery.connected_servers == 0
    assert provider.discovery.servers[0].connection_state == "disconnected"


@pytest.mark.asyncio
async def test_required_failure_cleans_successful_peer(tmp_path, fake_clients):
    clients, modes, _, _ = fake_clients
    modes["bad"] = "connection_failed"
    provider = RuntimeMCPProvider(
        provider_config([server("good"), server("bad", required=True)]), str(tmp_path)
    )
    with pytest.raises(ToolProviderLoadError):
        await provider.start()
    assert not provider.manager.connected_servers
    assert not provider.prepared_tools
    assert all(client.transport.disconnect_calls == 1 for client in clients)


@pytest.mark.asyncio
async def test_bounded_connect_and_discovery_concurrency(tmp_path, fake_clients):
    _, _, _, tracker = fake_clients
    provider = RuntimeMCPProvider(
        provider_config(
            [server(f"s{index}") for index in range(7)],
            limits={"max_parallel_server_connects": 2},
        ),
        str(tmp_path),
    )
    await provider.start()
    assert tracker["peak"] == 2
    assert tracker["discovery_peak"] == 2
    assert provider.discovery.connected_servers == 7
    assert [tool.server_id for tool in provider.prepared_tools] == [
        f"s{index}" for index in range(7)
    ]
    await provider.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "limits,expected,reason",
    [
        ({"max_tools_per_server": 1}, 2, "tool_limit"),
        ({"max_total_tools": 1}, 1, "tool_limit"),
        ({"max_schema_bytes_per_tool": 1}, 0, "schema_limit"),
        ({"max_schema_tokens": 1}, 0, "schema_limit"),
    ],
)
async def test_discovery_caps_are_deterministic(
    tmp_path, fake_clients, limits, expected, reason
):
    _, _, catalogs, _ = fake_clients
    catalogs["a"] = catalogs["b"] = [
        {"name": f"t{index}", "inputSchema": {}} for index in range(3)
    ]
    provider = RuntimeMCPProvider(
        provider_config([server("a"), server("b")], limits=limits), str(tmp_path)
    )
    await provider.start()
    assert len(provider.prepared_tools) == expected
    assert provider.discovery.discovered_tools == 6
    assert provider.diagnostics.rejected_tools == 6 - expected
    assert reason in provider.diagnostics.codes
    if expected == 1:
        assert provider.prepared_tools[0].server_id == "a"
    await provider.stop()


@pytest.mark.asyncio
async def test_untrusted_catalog_never_becomes_diagnostics_or_executable_registry(
    tmp_path, fake_clients
):
    _, _, catalogs, _ = fake_clients
    catalogs["fake"] = [
        {"name": "probe", "description": "SENTINEL-SECRET", "inputSchema": {}},
        {"name": 12, "inputSchema": {}},
        {"name": "bad", "inputSchema": None},
        {"name": "nan", "inputSchema": {"bad": float("nan")}},
    ]
    provider = RuntimeMCPProvider(provider_config([server()]), str(tmp_path))
    await provider.start()
    assert len(provider.prepared_tools) == 1
    assert "SENTINEL" not in repr(provider.prepared_tools)
    assert "SENTINEL" not in str(provider.discovery.model_dump())
    assert provider.diagnostics.rejected_tools == 3
    assert "invalid_schema" in provider.diagnostics.codes
    await provider.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("required", [False, True])
async def test_auto_connect_false_is_explicit_and_required_fails(
    tmp_path, fake_clients, required
):
    provider = RuntimeMCPProvider(
        provider_config([server(required=required)], auto_connect=False), str(tmp_path)
    )
    if required:
        with pytest.raises(ToolProviderLoadError):
            await provider.start()
    else:
        await provider.start()
    assert not fake_clients[0]
    assert provider.lifecycle[0].outcome == "auto_connect_disabled"
    await provider.stop()


@pytest.mark.asyncio
async def test_cancel_boot_drains_all_workers_and_cleans_clients(
    tmp_path, fake_clients
):
    clients, modes, _, _ = fake_clients
    modes.update({"a": "connection_timeout", "b": "connection_timeout"})
    provider = RuntimeMCPProvider(
        provider_config([server("a"), server("b")]), str(tmp_path)
    )
    task = asyncio.create_task(provider.start())
    while len(clients) < 2:
        await asyncio.sleep(0)
    await asyncio.gather(*(client.entered.wait() for client in clients))
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert all(not client.transport.is_connected for client in clients)
    assert all(client._receive_task is None for client in clients)
    assert not provider.manager.connected_servers
    assert not provider.prepared_tools


@pytest.mark.asyncio
async def test_revalidate_workspace_before_connect(tmp_path, fake_clients):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    target = workspace / "server"
    target.mkdir()
    provider = RuntimeMCPProvider(
        provider_config([server(cwd="server")]), str(workspace)
    )
    target.rmdir()
    target.symlink_to(tmp_path)
    with pytest.raises(ToolProviderLoadError, match="workspace validation failed"):
        await provider.start()
    assert not fake_clients[0]


def lightweight_kernel(tmp_path, monkeypatch, mcp):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (tmp_path / "install").mkdir()
    config = RuntimeConfig(
        install_root=str(tmp_path / "install"),
        runtime_data_root=str(tmp_path / "state"),
        workspace_root=str(workspace),
        agents_dir=str(workspace / "agents"),
        tools_config=ToolsConfig.from_dict(
            {
                "providers": {
                    "builtin": {"enabled": True, "mode": "all"},
                    "mcp": mcp,
                }
            }
        ),
    )
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


@pytest.mark.asyncio
@pytest.mark.parametrize("enabled", [False, True])
async def test_kernel_disabled_or_empty_mcp_preserves_native_tools(
    tmp_path, monkeypatch, fake_clients, enabled
):
    kernel = lightweight_kernel(tmp_path, monkeypatch, {"enabled": enabled})
    await kernel.start()
    owner = kernel.mcp_provider
    await kernel._di.boot()
    assert kernel.mcp_provider is owner
    assert "recall_memory" in kernel.tool_registry.list_names()
    assert (kernel.mcp_provider is not None) == enabled
    await kernel.stop()
    await kernel.stop()


@pytest.mark.asyncio
async def test_real_agent_binding_validation_runs_after_discovery_and_cleans_on_failure(
    tmp_path, monkeypatch, fake_clients
):
    kernel = lightweight_kernel(
        tmp_path,
        monkeypatch,
        {
            "enabled": True,
            "config": {"servers": [server()]},
        },
    )
    agents = tmp_path / "workspace" / "agents"
    agents.mkdir()
    (agents / "probe.yaml").write_text(
        "name: probe\nrole: probe\ngoal: probe\nsystem_prompt: probe\n"
        "tools: [mcp_fake_probe]\n",
        encoding="utf-8",
    )
    original = kernel._validate_agent_profiles

    def validate(profiles):
        assert kernel.mcp_provider.discovery.status == "completed"
        assert len(kernel.mcp_provider.prepared_tools) == 1
        original(profiles)

    monkeypatch.setattr(kernel, "_validate_agent_profiles", validate)
    with pytest.raises(ValueError, match="unavailable tool"):
        await kernel.start()
    assert kernel.mcp_provider.discovery.servers[0].connection_state == "disconnected"
    assert not kernel.mcp_provider.manager.connected_servers
    assert not kernel._initialized


@pytest.mark.asyncio
async def test_registry_metadata_public_cleanup_and_restart(tmp_path, fake_clients):
    _, _, _, tracker = fake_clients
    config = MCPToolProviderConfig.from_dict(
        {"enabled": True, "mode": "all", "config": {"servers": [server()]}}
    )
    provider = RuntimeMCPProvider(config, str(tmp_path))
    registry = DefaultToolRegistry()
    registry.register(name="native", func=lambda: "native", category="native")
    try:
        await provider.start()
        await provider.register_tools(registry)
        await provider.register_tools(registry)
        assert tracker["list_calls"] == 1
        assert set(provider.tool_metadata) == {"mcp_fake_probe"}
        assert provider.tool_metadata.get("native") is None
        assert provider.diagnostics.registered_tools == 1
        assert provider.discovery.selected_tools == 1
        assert provider.owned_tool_names == ("mcp_fake_probe",)
        with pytest.raises(TypeError):
            provider.tool_metadata["new"] = provider.tool_metadata["mcp_fake_probe"]
        await provider.stop()
        assert registry.list_names() == ["native"]
        assert not provider.tool_metadata
        assert provider.registration_registry is None
        await provider.stop()
        await provider.start()
        await provider.register_tools(registry)
        assert tracker["list_calls"] == 2
        assert registry.list_names() == ["native", "mcp_fake_probe"]
    finally:
        await provider.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("insert_then_raise", [False, True])
async def test_transactional_insert_failure_removes_only_owned_tools(
    tmp_path, fake_clients, insert_then_raise
):
    _, _, catalogs, _ = fake_clients
    catalogs["fake"] = [
        {"name": name, "inputSchema": {"type": "object"}}
        for name in ("first", "second")
    ]

    class FailingRegistry(DefaultToolRegistry):
        def register(self, tool=None, **kwargs):
            if tool is not None and tool.name == "mcp_fake_second":
                if insert_then_raise:
                    super().register(tool)
                raise RuntimeError("SENTINEL-INSERT-SECRET")
            super().register(tool, **kwargs)

    registry = FailingRegistry()
    registry.register(name="native", func=lambda: "native", category="native")
    provider = RuntimeMCPProvider(
        MCPToolProviderConfig.from_dict(
            {"enabled": True, "mode": "all", "config": {"servers": [server()]}}
        ),
        str(tmp_path),
    )
    try:
        await provider.start()
        with pytest.raises(
            ToolProviderLoadError, match="MCP registration failed"
        ) as failure:
            await provider.register_tools(registry)
        assert registry.list_names() == ["native"]
        assert not provider.tool_metadata
        assert not provider.owned_tool_names
        assert not provider.manager.connected_servers
        assert "registration_failed" in provider.diagnostics.codes
        assert "SENTINEL" not in str(failure.value)
    finally:
        await provider.stop()


@pytest.mark.asyncio
async def test_registry_rollback_failure_retains_public_owner_for_retry(
    tmp_path, fake_clients
):
    class RefusingRegistry(DefaultToolRegistry):
        refusing = True

        def unregister(self, name):
            if self.refusing:
                raise RuntimeError("SENTINEL-REMOVE-SECRET")
            return super().unregister(name)

    registry = RefusingRegistry()
    provider = RuntimeMCPProvider(
        MCPToolProviderConfig.from_dict(
            {"enabled": True, "mode": "all", "config": {"servers": [server()]}}
        ),
        str(tmp_path),
    )
    try:
        await provider.start()
        await provider.register_tools(registry)
        with pytest.raises(ToolProviderLoadError, match="registry cleanup incomplete"):
            await provider.stop()
        assert provider.registration_registry is registry
        assert provider.owned_tool_names == ("mcp_fake_probe",)
        assert set(provider.tool_metadata) == set(registry.list_names())
        registry.refusing = False
        await provider.stop()
        assert not registry.list_names()
        assert not provider.tool_metadata
        assert not provider.manager.connected_servers
        assert provider.registration_registry is None
    finally:
        registry.refusing = False
        await provider.stop()


@pytest.mark.asyncio
async def test_public_stop_unpublishes_before_failed_client_cleanup(
    tmp_path, fake_clients
):
    clients, _, _, _ = fake_clients
    provider = RuntimeMCPProvider(
        MCPToolProviderConfig.from_dict(
            {"enabled": True, "mode": "all", "config": {"servers": [server()]}}
        ),
        str(tmp_path),
    )
    registry = DefaultToolRegistry()
    try:
        await provider.start()
        await provider.register_tools(registry)
        clients[0].transport.fail_cleanup = True
        with pytest.raises(ToolProviderLoadError, match="shutdown incomplete"):
            await provider.stop()
        assert not registry.list_names()
        assert not provider.tool_metadata
        assert provider.diagnostics.registered_tools == 0
        assert provider.manager.connected_servers
        clients[0].transport.fail_cleanup = False
        await provider.start()
        await provider.register_tools(registry)
        assert registry.list_names() == ["mcp_fake_probe"]
    finally:
        for client in clients:
            client.transport.fail_cleanup = False
        await provider.stop()


@pytest.mark.asyncio
async def test_connection_retries_do_not_leak_failed_attempt(tmp_path, fake_clients):
    clients, modes, _, _ = fake_clients
    modes["fake"] = ["connection_failed", "good"]
    provider = RuntimeMCPProvider(
        provider_config([server(retry_attempts=1)]), str(tmp_path)
    )
    await provider.start()
    assert len(clients) == 2
    assert clients[0].transport.disconnect_calls == 1
    assert provider.lifecycle[0].outcome == "connected"
    await provider.stop()
    assert clients[1].transport.disconnect_calls == 1


@pytest.mark.asyncio
async def test_global_connection_timeout_caps_server_timeout(tmp_path, fake_clients):
    _, modes, _, _ = fake_clients
    modes["fake"] = "connection_timeout"
    provider = RuntimeMCPProvider(
        provider_config(
            [server(timeout_seconds=30)], limits={"connection_timeout_seconds": 1}
        ),
        str(tmp_path),
    )
    await asyncio.wait_for(provider.start(), timeout=2)
    assert provider.lifecycle[0].outcome == "connection_timeout"
    await provider.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("with_peer", [False, True])
async def test_provider_retry_retains_manager_until_cleanup_and_recovers(
    tmp_path, fake_clients, caplog, with_peer
):
    clients, modes, _, _ = fake_clients
    modes["bad"] = "discovery_cleanup_failed"
    servers = [server("good"), server("bad")] if with_peer else [server("bad")]
    provider = RuntimeMCPProvider(provider_config(servers), str(tmp_path))
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(ToolProviderLoadError, match="MCP shutdown incomplete"):
            await provider.start()
        manager = provider.manager
        original_clients = tuple(clients)
        with pytest.raises(ToolProviderLoadError, match="MCP shutdown incomplete"):
            await provider.start()
    assert provider.manager is manager
    assert tuple(clients) == original_clients
    assert manager.connected_servers == ["bad"]
    assert not manager.get_client("bad").is_connected
    assert manager.get_client("bad").transport.is_connected
    assert not provider.prepared_tools
    assert provider.discovery.status == "failed"
    assert provider.lifecycle[-1].outcome == "cleanup_failed"
    assert provider.diagnostics.registered_tools == 0
    assert "SENTINEL" not in caplog.text
    assert "SENTINEL" not in repr(provider.lifecycle)
    assert "SENTINEL" not in str(provider.discovery.model_dump())
    assert "SENTINEL" not in str(provider.diagnostics.model_dump())
    if with_peer:
        good = next(client for client in clients if client.name == "good")
        assert not good.transport.is_connected
        assert good.transport.disconnect_calls == 1
        assert provider.lifecycle[0].outcome == "connected"
    for client in clients:
        client.transport.fail_cleanup = False
    modes["bad"] = "good"
    await provider.start()
    assert all(not client.transport.is_connected for client in original_clients)
    assert not manager.connected_servers
    assert provider.manager is not manager
    assert provider.discovery.status == "completed"
    assert len(provider.prepared_tools) == len(servers)
    recovered_manager = provider.manager
    await provider.start()
    assert provider.manager is recovered_manager
    assert len(clients) == 2 * len(servers)
    await provider.stop()
    await provider.stop()
    assert not provider.manager.connected_servers
    assert not provider.prepared_tools
    assert all(not client.transport.is_connected for client in clients)


@pytest.mark.asyncio
@pytest.mark.parametrize("with_peer", [False, True])
async def test_public_kernel_retry_retains_provider_and_stop_releases_every_client(
    tmp_path, monkeypatch, fake_clients, with_peer
):
    clients, modes, _, _ = fake_clients
    modes["bad"] = "discovery_cleanup_failed"
    servers = [server("good"), server("bad")] if with_peer else [server("bad")]
    kernel = lightweight_kernel(
        tmp_path, monkeypatch, {"enabled": True, "config": {"servers": servers}}
    )
    with pytest.raises(ToolProviderLoadError, match="MCP shutdown incomplete"):
        await kernel.start()
    owner = kernel.mcp_provider
    manager = owner.manager
    original_clients = tuple(clients)
    with pytest.raises(ToolProviderLoadError, match="MCP shutdown incomplete"):
        await kernel.start()
    assert kernel.mcp_provider is owner
    assert kernel.mcp_provider.manager is manager
    assert tuple(clients) == original_clients
    assert manager.connected_servers == ["bad"]
    assert not owner.prepared_tools
    assert owner.lifecycle[-1].outcome == "cleanup_failed"
    registry = kernel._di.tool_registry
    assert "recall_memory" in registry.list_names()
    assert not any(name.startswith("mcp_") for name in registry.list_names())
    if with_peer:
        assert not next(
            client for client in clients if client.name == "good"
        ).transport.is_connected
    for client in clients:
        client.transport.fail_cleanup = False
    # Cleanup is reached solely through the current public kernel owner.
    await kernel.stop()
    await kernel.stop()
    assert all(not client.transport.is_connected for client in clients)
    assert not kernel.mcp_provider.manager.connected_servers
    assert not kernel.mcp_provider.prepared_tools
    modes["bad"] = "good"
    await kernel.start()
    assert kernel.mcp_provider is owner
    assert kernel.mcp_provider.discovery.status == "completed"
    assert len(kernel.mcp_provider.prepared_tools) == len(servers)
    recovered_manager = kernel.mcp_provider.manager
    await kernel.start()
    await kernel._di.boot()
    assert kernel.mcp_provider is owner
    assert kernel.mcp_provider.manager is recovered_manager
    assert len(clients) == 2 * len(servers)
    assert not any(
        name.startswith("mcp_") for name in kernel.tool_registry.list_names()
    )
    await kernel.stop()
    await kernel.stop()
    assert all(not client.transport.is_connected for client in clients)


@pytest.mark.asyncio
async def test_cancellation_during_retry_cleanup_preserves_owner_for_public_stop(
    tmp_path, fake_clients
):
    clients, modes, _, _ = fake_clients
    modes["fake"] = "discovery_cleanup_failed"
    provider = RuntimeMCPProvider(provider_config([server()]), str(tmp_path))
    with pytest.raises(ToolProviderLoadError, match="MCP shutdown incomplete"):
        await provider.start()
    manager = provider.manager
    client = manager.get_client("fake")
    client.transport.fail_cleanup = False
    client.transport.pause_cleanup = True
    client.transport.cleanup_entered.clear()
    task = asyncio.create_task(provider.start())
    try:
        await asyncio.wait_for(client.transport.cleanup_entered.wait(), timeout=2)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(task, timeout=2)
        assert provider.manager is manager
        assert clients == [client]
        assert manager.connected_servers == ["fake"]
        assert client.transport.is_connected
        assert not provider.prepared_tools
    finally:
        if not task.done():
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        client.transport.pause_cleanup = False
        await provider.stop()
    assert not client.transport.is_connected
    assert not manager.connected_servers


@pytest.mark.asyncio
async def test_failed_commit_with_failed_rollback_retains_exact_public_owner(
    tmp_path, fake_clients
):
    _, _, catalogs, _ = fake_clients
    catalogs["fake"] = [
        {"name": name, "inputSchema": {"type": "object"}}
        for name in ("first", "second")
    ]

    class RefusingRegistry(DefaultToolRegistry):
        refusing = True

        def register(self, tool=None, **kwargs):
            if tool is not None and tool.name == "mcp_fake_second":
                raise RuntimeError("SENTINEL-INSERT")
            super().register(tool, **kwargs)

        def unregister(self, name):
            if self.refusing:
                raise RuntimeError("SENTINEL-ROLLBACK")
            return super().unregister(name)

    registry = RefusingRegistry()
    registry.register(name="native", func=lambda: "native", category="native")
    provider = RuntimeMCPProvider(
        MCPToolProviderConfig.from_dict(
            {"enabled": True, "mode": "all", "config": {"servers": [server()]}}
        ),
        str(tmp_path),
    )
    try:
        await provider.start()
        with pytest.raises(ToolProviderLoadError, match="registry cleanup incomplete"):
            await provider.register_tools(registry)
        assert provider.registration_registry is registry
        assert provider.owned_tool_names == ("mcp_fake_first",)
        assert set(provider.tool_metadata) == {"mcp_fake_first"}
        assert provider.diagnostics.registered_tools == 1
        assert registry.list_names() == ["native", "mcp_fake_first"]
        registry.refusing = False
        await provider.stop()
        assert registry.list_names() == ["native"]
        assert not provider.tool_metadata
        assert not provider.manager.connected_servers
    finally:
        registry.refusing = False
        await provider.stop()


@pytest.mark.asyncio
async def test_discovery_and_registration_rejections_count_once(tmp_path, fake_clients):
    _, _, catalogs, _ = fake_clients
    catalogs["fake"] = [
        {"name": "good", "inputSchema": {"type": "object"}},
        {"name": False, "inputSchema": {"type": "object"}},
        {"name": "unsafe", "inputSchema": {"type": "object", "$ref": "SENTINEL"}},
        {"name": "excluded", "inputSchema": {"type": "object"}},
    ]
    config = MCPToolProviderConfig.from_dict(
        {
            "enabled": True,
            "mode": "all",
            "exclude_tools": ["mcp_fake_excluded"],
            "config": {"servers": [server()]},
        }
    )
    provider = RuntimeMCPProvider(config, str(tmp_path))
    try:
        await provider.start()
        assert provider.diagnostics.rejected_tools == 1
        await provider.register_tools(DefaultToolRegistry())
        assert provider.discovery.discovered_tools == 4
        assert provider.discovery.selected_tools == 1
        assert provider.diagnostics.registered_tools == 1
        assert provider.diagnostics.rejected_tools == 2
        assert provider.diagnostics.filtered_tools == 1
        assert provider.discovery.servers[0].rejected_tools == 2
        assert provider.discovery.servers[0].filtered_tools == 1
    finally:
        await provider.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("native", [False, True])
async def test_collision_evidence_retained_until_new_discovery_and_retry(
    tmp_path, fake_clients, native, caplog
):
    clients, modes, catalogs, tracker = fake_clients
    catalogs["fake"] = [
        {"name": name, "inputSchema": {"type": "object"}}
        for name in (["Read.File"] if native else ["Read.File", "Read-File"])
    ]
    provider = RuntimeMCPProvider(provider_config([server()]), str(tmp_path))
    registry = DefaultToolRegistry()
    registry.register(name="native", func=lambda: "native", category="native")
    if native:
        registry.register(name="mcp_fake_read_file", func=lambda: "native", category="native")
    snapshot = {name: registry.get(name) for name in registry.list_names()}
    try:
        with caplog.at_level(logging.DEBUG):
            await provider.start()
            with pytest.raises(ToolProviderLoadError, match="name_collision"):
                await provider.register_tools(registry)
            retained = provider.registration_decisions
            collision = retained[-1].collision
            assert collision is not None
            assert collision.first.provider == ("native" if native else "mcp")
            assert collision.second.provider == "mcp"
            assert provider.diagnostics.rejected_tools == 1
            assert provider.discovery.discovered_tools == (1 if native else 2)
            assert provider.discovery.selected_tools == 0
            assert provider.diagnostics.registered_tools == provider.diagnostics.filtered_tools == 0
            assert {name: registry.get(name) for name in snapshot} == snapshot
            assert all(registry.get(name) is value for name, value in snapshot.items())
            assert registry.list_names() == list(snapshot)
            assert not provider.prepared_tools and not provider.tool_metadata
            assert provider.registration_registry is None and not provider.owned_tool_names
            assert provider.manager is not None and not provider.manager.connected_servers
            assert all(not client.transport.is_connected for client in clients)
            await provider.stop()
            await provider.stop()
            assert provider.registration_decisions == retained

            # Obstructed prior cleanup does not erase history or replace its owner.
            manager = provider.manager
            disconnect = manager.disconnect_all
            manager.disconnect_all = AsyncMock(side_effect=RuntimeError("SENTINEL-RETRY"))
            try:
                with pytest.raises(ToolProviderLoadError, match="shutdown incomplete"):
                    await provider.start()
                assert provider.manager is manager
                assert provider.registration_decisions == retained
            finally:
                manager.disconnect_all = disconnect

            # A new optional discovery failure clears the old collision history.
            modes["fake"] = "connection_failed"
            await provider.start()
            assert not provider.registration_decisions
            assert provider.diagnostics.failed_servers == 1
            await provider.stop()
            modes["fake"] = "good"
            catalogs["fake"] = [{"name": "probe", "inputSchema": {"type": "object"}}]
            await provider.start()
            await provider.register_tools(registry)
            assert all(decision.collision is None for decision in provider.registration_decisions)
            assert provider.diagnostics.registered_tools == 0  # default selected mode
            assert tracker["list_calls"] == 2
            await provider.stop()
            assert all(not client.transport.is_connected for client in clients)
        assert "SENTINEL" not in caplog.text + repr(provider.registration_decisions)
    finally:
        # Public assertions precede this defensive synthetic-client settlement.
        for client in clients:
            client.transport.fail_cleanup = client.transport.pause_cleanup = False
        await provider.stop()
