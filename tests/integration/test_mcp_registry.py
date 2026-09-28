"""Real local public registry dispatch and WS-03 startup/cleanup boundaries."""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from hashlib import sha256
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest
from friday_core.profiles import MemoryProfile
from friday_runtime.config import RuntimeConfig, ToolsConfig
from friday_runtime.kernel import RuntimeKernel
from friday_runtime.mcp_loading import RuntimeMCPProvider
from friday_runtime.tool_loading import ToolProviderLoadError

from tests.integration import test_mcp_runtime_lifecycle as lifecycle
from tests.integration.test_mcp_runtime_lifecycle import server

# Reuse the settled-process fixture; assignments (not imports) allow ordinary
# pytest fixture argument names without unused-import/shadowing suppressions.
processes = lifecycle.processes


def assert_collision_public_cleanup(
    provider: RuntimeMCPProvider, observed: Any
) -> None:
    """Public cleanup must succeed before any defensive fixture intervention."""
    assert not provider.prepared_tools and not provider.tool_metadata
    assert not provider.owned_tool_names and provider.registration_registry is None
    assert provider.manager is not None and not provider.manager.connected_servers
    assert observed
    for process in observed:
        assert process.returncode is not None
        assert process.stdout is not None and process.stdout.at_eof()
        assert process.stderr is not None and process.stderr.at_eof()
        assert process.stdin is not None and process.stdin.is_closing()


async def settle_collision_fixture(
    kernel: RuntimeKernel, initial_tasks: set[asyncio.Task[Any]]
) -> None:
    try:
        await asyncio.wait_for(kernel.stop(), lifecycle.CLEANUP_TEST_BOUND)
    finally:
        # Includes failed assertions; fixture then kills/drains/reaps tracked peers.
        tasks = [task for task in asyncio.all_tasks() - initial_tasks if not task.done()]
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


def kernel_for(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    servers: list[dict[str, Any]],
    **options: Any,
) -> RuntimeKernel:
    workspace = tmp_path / "workspace"
    workspace.mkdir(exist_ok=True)
    install = tmp_path / "install"
    install.mkdir(exist_ok=True)
    kernel = RuntimeKernel(
        RuntimeConfig(
            install_root=str(install),
            runtime_data_root=str(tmp_path / "state"),
            workspace_root=str(workspace),
            agents_dir=str(workspace / "agents"),
            tools_config=ToolsConfig.from_dict(
                {
                    "providers": {
                        "builtin": {"enabled": True, "mode": "all"},
                        "mcp": {
                            "enabled": True,
                            "mode": "all",
                            "config": {"servers": servers},
                            **options,
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
    original_registry_bootstrap = kernel._di._create_tool_registry

    def bootstrap_native() -> None:
        original_registry_bootstrap()
        registry = kernel._di.tool_registry
        if registry is None:
            raise RuntimeError("Test registry missing")
        # Other registry tests clear the process-global decorator catalog.
        # Explicit native registration keeps this fixture order-independent.
        registry.register(
            name="fixture_native", func=lambda: "native", category="native"
        )

    monkeypatch.setattr(kernel._di, "_create_tool_registry", bootstrap_native)
    return kernel


@pytest.mark.asyncio
async def test_real_registry_routes_exact_names_arguments_peers_without_rediscovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, processes: Any
) -> None:
    kernel = kernel_for(
        tmp_path,
        monkeypatch,
        [server("first", "registry_a"), server("second", "registry_b")],
    )
    try:
        await kernel.start()
        provider = kernel.mcp_provider
        assert provider is not None
        registry = kernel.tool_registry
        assert set(provider.tool_metadata) == {
            "mcp_first_read_file",
            "mcp_second_read_file",
        }
        assert provider.tool_metadata.get("recall_memory") is None
        for peer, mode in (("first", "registry_a"), ("second", "registry_b")):
            name = f"mcp_{peer}_read_file"
            result = json.loads(await registry.get_callable(name)(path="fixture.txt"))
            assert result == {
                "peer": mode,
                "name": "Read.File",
                "arguments": {"path": "fixture.txt"},
                "list_calls": 1,
            }
            exported = registry.get_schema(name, "openai")
            assert exported is not None
            assert exported["function"]["category"] == "mcp"
            assert exported["function"]["tags"] == ["mcp"]
            size = max(
                len(
                    json.dumps(
                        registry.get_schema(name, fmt),
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ).encode()
                )
                for fmt in ("plain", "openai")
            )
            assert provider.tool_metadata[name].schema_byte_size == size
        await kernel.stop()
        assert not provider.tool_metadata
        assert not any(name.startswith("mcp_") for name in registry.list_names())
        assert "fixture_native" in registry.list_names()
        assert processes and all(
            process.returncode is not None for process in processes
        )
        await kernel.stop()
        await kernel.start()
        assert set(provider.tool_metadata) == {
            "mcp_first_read_file",
            "mcp_second_read_file",
        }
    finally:
        await kernel.stop()


@pytest.mark.asyncio
async def test_registered_noisy_peer_cancelled_stop_unpublishes_before_public_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, processes: Any
) -> None:
    kernel = kernel_for(tmp_path, monkeypatch, [server("peer", "noisy_success")])
    shutdown: asyncio.Task[None] | None = None
    try:
        await kernel.start()
        provider = kernel.mcp_provider
        assert provider is not None
        registry = kernel.tool_registry
        assert "mcp_peer_probe" in provider.tool_metadata
        shutdown = asyncio.create_task(kernel.stop())
        await asyncio.sleep(0.05)
        assert not provider.tool_metadata
        assert "mcp_peer_probe" not in registry.list_names()
        assert "fixture_native" in registry.list_names()
        shutdown.cancel()
        with pytest.raises(asyncio.CancelledError):
            await shutdown
        await asyncio.wait_for(kernel.stop(), 13)
        assert not provider.owned_tool_names
        assert provider.manager is not None and not provider.manager.connected_servers
        assert processes and all(
            process.returncode is not None for process in processes
        )
    finally:
        if shutdown is not None and not shutdown.done():
            shutdown.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await shutdown
        await asyncio.wait_for(kernel.stop(), 13)


@pytest.mark.asyncio
async def test_real_schema_rejection_redaction_safe_diagnostics_and_partial_counts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    processes: Any,
    caplog: pytest.LogCaptureFixture,
) -> None:
    kernel = kernel_for(
        tmp_path,
        monkeypatch,
        [server("peer", "registry_unsafe"), server("bad", "list_fail")],
    )
    try:
        with caplog.at_level(logging.DEBUG):
            await kernel.start()
            provider = kernel.mcp_provider
            assert provider is not None
            assert set(provider.tool_metadata) == {"mcp_peer_safe"}
            assert provider.diagnostics.rejected_tools == 1
            assert provider.diagnostics.failed_servers == 1
            assert provider.discovery.discovered_tools == 2
            assert provider.discovery.selected_tools == 1
            assert (
                provider.tool_metadata["mcp_peer_safe"].schema_sanitization_state
                == "sanitized"
            )
            assert "SENTINEL" not in json.dumps(kernel.tool_registry.get_schemas())
            assert "SENTINEL" not in repr(provider.registration_decisions)
            assert "SENTINEL" not in repr(provider.tool_metadata)
            await kernel.stop()
        assert "SENTINEL" not in caplog.text
        assert all(process.returncode is not None for process in processes)
    finally:
        await kernel.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "options,expected",
    [
        ({"mode": "selected"}, set()),
        (
            {"mode": "selected", "include_categories": ["mcp"]},
            {"mcp_peer_first", "mcp_peer_second", "mcp_peer_third"},
        ),
        (
            {"mode": "selected", "include_tools": ["mcp_peer_second"]},
            {"mcp_peer_second"},
        ),
        ({"exclude_tools": ["mcp_peer_second"]}, {"mcp_peer_first", "mcp_peer_third"}),
    ],
)
async def test_real_filters_and_default_selection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    processes: Any,
    options: dict[str, Any],
    expected: set[str],
) -> None:
    kernel = kernel_for(
        tmp_path, monkeypatch, [server("peer", "registry_catalog")], **options
    )
    try:
        await kernel.start()
        provider = kernel.mcp_provider
        assert provider is not None
        assert set(provider.tool_metadata) == expected
        assert provider.diagnostics.registered_tools == len(expected)
        assert provider.diagnostics.filtered_tools == 3 - len(expected)
        for name in expected:
            result = json.loads(await kernel.tool_registry.get_callable(name)())
            assert result["list_calls"] == 1
        await kernel.stop()
        assert all(process.returncode is not None for process in processes)
    finally:
        await kernel.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode,options,code",
    [
        ("registry_collision", {"mode": "selected"}, "name_collision"),
        ("registry_unsafe", {"include_tools": ["mcp_peer_bad"]}, "missing_include"),
        ("list_fail", {"include_tools": ["mcp_peer_probe"]}, "missing_include"),
        (
            "registry_catalog",
            {
                "config": {
                    "servers": [server("peer", "registry_catalog")],
                    "limits": {"max_tools_per_server": 2},
                },
                "include_tools": ["mcp_peer_third"],
            },
            "missing_include",
        ),
    ],
)
async def test_real_failure_no_partial_registration_and_public_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    processes: Any,
    mode: str,
    options: dict[str, Any],
    code: str,
) -> None:
    kernel = kernel_for(tmp_path, monkeypatch, [server("peer", mode)], **options)
    try:
        with pytest.raises(ToolProviderLoadError, match=code):
            await kernel.start()
        provider = kernel.mcp_provider
        assert provider is not None
        assert code in provider.diagnostics.codes
        assert not provider.tool_metadata
        assert not provider.owned_tool_names
        assert provider.registration_registry is None
        assert provider.manager is not None and not provider.manager.connected_servers
        assert processes and all(
            process.returncode is not None for process in processes
        )
    finally:
        await kernel.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("selected", [True, False])
async def test_real_profile_binding_after_publication_or_safe_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, processes: Any, selected: bool
) -> None:
    kernel = kernel_for(
        tmp_path,
        monkeypatch,
        [server("peer", "registry_a")],
        mode="all" if selected else "selected",
    )
    agents = tmp_path / "workspace" / "agents"
    agents.mkdir()
    (agents / "reader.yaml").write_text(
        "name: reader\nrole: reader\ngoal: reader\nsystem_prompt: reader\ntools: [mcp_peer_read_file]\n",
        encoding="utf-8",
    )
    try:
        if selected:
            await kernel.start()
            assert kernel.mcp_provider is not None
            assert "mcp_peer_read_file" in kernel.mcp_provider.tool_metadata
        else:
            with pytest.raises(ValueError, match="MCP reasons:.*filtered"):
                await kernel.start()
            assert kernel.mcp_provider is not None
            assert not kernel.mcp_provider.tool_metadata
            assert kernel.mcp_provider.registration_registry is None
        await kernel.stop()
        assert all(process.returncode is not None for process in processes)
    finally:
        await kernel.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("native", [False, True])
@pytest.mark.parametrize(
    "options",
    [
        {"mode": "selected"},
        {"mode": "selected", "include_categories": ["mcp"]},
        {"mode": "all", "exclude_tools": ["mcp_peer_read_file"]},
        {"mode": "selected", "exclude_categories": ["mcp"]},
    ],
)
async def test_public_collision_both_sources_retained_native_identity_and_retry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    processes: Any,
    caplog: pytest.LogCaptureFixture,
    native: bool,
    options: dict[str, Any],
) -> None:
    kernel = kernel_for(tmp_path, monkeypatch, [server(
        "peer", "registry_a" if native else "registry_collision"
    )], **options)
    bootstrap = kernel._di._create_tool_registry
    snapshots = []

    def capture_native_registry() -> None:
        bootstrap()
        registry = kernel._di.tool_registry
        if registry is None:
            raise RuntimeError("Test registry missing")
        if native:
            registry.register(name="mcp_peer_read_file", func=lambda: "native", category="native")
        snapshots.append((registry, {name: registry.get(name) for name in registry.list_names()}))

    monkeypatch.setattr(kernel._di, "_create_tool_registry", capture_native_registry)
    initial_tasks = asyncio.all_tasks()
    try:
        with caplog.at_level(logging.DEBUG):
            for attempt in range(2):
                with pytest.raises(ToolProviderLoadError, match="name_collision") as failure:
                    await kernel.start()
                provider = kernel.mcp_provider
                assert provider is not None
                collision = provider.registration_decisions[-1].collision
                assert collision is not None
                assert collision.canonical_name == "mcp_peer_read_file"
                assert collision.first.provider == ("native" if native else "mcp")
                assert collision.first.server_id == (None if native else "peer")
                assert collision.second.provider == "mcp" and collision.second.server_id == "peer"
                summary = collision.second.original_name_summary
                assert summary is not None
                assert summary.fingerprint == sha256(
                    ("Read.File" if native else "Read-File").encode()
                ).hexdigest()[:12]
                if native:
                    assert collision.first.original_name_summary is None
                else:
                    assert collision.first.original_name_summary is not None
                    assert collision.first.original_name_summary != summary
                assert provider.diagnostics.rejected_tools == 1
                assert provider.discovery.discovered_tools == (1 if native else 2)
                assert provider.discovery.selected_tools == 0
                assert provider.diagnostics.registered_tools == provider.diagnostics.filtered_tools == 0
                registry, snapshot = snapshots[attempt]
                assert registry.list_names() == list(snapshot)
                assert all(registry.get(name) is tool for name, tool in snapshot.items())
                assert_collision_public_cleanup(provider, processes)
                retained = provider.registration_decisions
                await kernel.stop()
                await kernel.stop()
                assert kernel.mcp_provider is provider
                assert provider.registration_decisions == retained
                await asyncio.sleep(0)
                assert not (asyncio.all_tasks() - initial_tasks)
                evidence = str(failure.value) + repr(retained)
                assert "Read.File" not in evidence and "Read-File" not in evidence
                assert "SENTINEL" not in evidence
        assert "SENTINEL" not in caplog.text
        assert "Read.File" not in caplog.text and "Read-File" not in caplog.text
    finally:
        await settle_collision_fixture(kernel, initial_tasks)


@pytest.mark.asyncio
async def test_public_cross_peer_normalization_ambiguity_retains_both_safe_ids(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, processes: Any,
    caplog: pytest.LogCaptureFixture,
) -> None:
    kernel = kernel_for(tmp_path, monkeypatch, [
        server("peer_one", "registry_a"), server("peer", "registry_collision_cross")
    ], mode="selected")
    initial_tasks = asyncio.all_tasks()
    try:
        with caplog.at_level(logging.DEBUG):
            with pytest.raises(ToolProviderLoadError, match="name_collision"):
                await kernel.start()
            provider = kernel.mcp_provider
            assert provider is not None
            collision = provider.registration_decisions[-1].collision
            assert collision is not None
            assert collision.canonical_name == "mcp_peer_one_read_file"
            assert (collision.first.provider, collision.second.provider) == ("mcp", "mcp")
            assert (collision.first.server_id, collision.second.server_id) == ("peer_one", "peer")
            assert collision.first.original_name_summary != collision.second.original_name_summary
            assert_collision_public_cleanup(provider, processes)
            assert "Read.File" not in repr(collision) and "one.Read-File" not in repr(collision)
            await asyncio.sleep(0)
            assert not (asyncio.all_tasks() - initial_tasks)
        assert "SENTINEL" not in caplog.text
        assert "Read.File" not in caplog.text and "one.Read-File" not in caplog.text
    finally:
        await settle_collision_fixture(kernel, initial_tasks)


@pytest.mark.asyncio
@pytest.mark.parametrize("mode,length,shape", [
    ("registry_collision_long", "9999+", "-" * 24),
    ("registry_collision_control", "11", "aaaa.??aaaa"),
    ("registry_collision_encoded", "5", "??00?"),
])
async def test_public_hostile_name_collision_evidence_is_bounded_and_private(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, processes: Any,
    caplog: pytest.LogCaptureFixture, mode: str, length: str, shape: str,
) -> None:
    peers = [server("peer", mode)]
    kernel = kernel_for(tmp_path, monkeypatch, peers, mode="selected", config={
        "servers": peers,
        "limits": {"max_schema_bytes_per_tool": 30000, "max_schema_tokens": 80000},
    })
    initial_tasks = asyncio.all_tasks()
    try:
        with caplog.at_level(logging.DEBUG):
            with pytest.raises(ToolProviderLoadError, match="name_collision") as failure:
                await kernel.start()
            provider = kernel.mcp_provider
            assert provider is not None
            collision = provider.registration_decisions[-1].collision
            assert collision is not None
            summary = collision.first.original_name_summary
            assert summary is not None
            assert (summary.length, summary.shape) == (length, shape)
            assert summary != collision.second.original_name_summary
            evidence = str(failure.value) + repr(provider.registration_decisions)
            assert len(evidence) < 1100
            assert "SENTINEL" not in evidence and "Read.File" not in evidence
            assert "&#83;" not in evidence and "\x00" not in evidence and "\u200b" not in evidence
            assert_collision_public_cleanup(provider, processes)
            await asyncio.sleep(0)
            assert not (asyncio.all_tasks() - initial_tasks)
        assert "SENTINEL" not in caplog.text
        assert "Read.File" not in caplog.text and "&#83;" not in caplog.text
    finally:
        await settle_collision_fixture(kernel, initial_tasks)
