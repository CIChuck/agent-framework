"""Real local public registry dispatch and WS-03 startup/cleanup boundaries."""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest
from friday_core.profiles import MemoryProfile
from friday_runtime.config import RuntimeConfig, ToolsConfig
from friday_runtime.kernel import RuntimeKernel
from friday_runtime.tool_loading import ToolProviderLoadError

from tests.integration import test_mcp_runtime_lifecycle as lifecycle
from tests.integration.test_mcp_runtime_lifecycle import server

# Reuse the settled-process fixture; assignments (not imports) allow ordinary
# pytest fixture argument names without unused-import/shadowing suppressions.
processes = lifecycle.processes


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
