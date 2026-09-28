"""Runtime-owned MCP lifecycle and bounded, untrusted WS-03 discovery handoff.

Nothing in this module registers tools or exposes peer content to model context.
Raw JSON exists only in the explicitly untrusted, non-repr handoff, not in
diagnostics, logs, memory, or transcript storage.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from friday_core.mcp import (
    MCPDiagnosticCode,
    MCPDiscoveryState,
    MCPProviderDiagnostics,
    MCPServerDiscoveryState,
)
from friday_mcp.client.manager import MCPClientManager
from friday_mcp.config import MCPConfig, MCPServerConfig

from friday_runtime.config import MCPRuntimeServerConfig, MCPToolProviderConfig
from friday_runtime.tool_loading import ToolProviderLoadError

MCPLifecycleOutcome = Literal[
    "disabled",
    "auto_connect_disabled",
    "connected",
    "connection_failed",
    "connection_timeout",
    "discovery_failed",
    "discovery_timeout",
    "cancelled",
    "cleanup_failed",
]


@dataclass(frozen=True)
class MCPServerLifecycleDiagnostic:
    """Safe configured identifier and fixed reason, never peer exception text."""

    server_id: str
    required: bool
    outcome: MCPLifecycleOutcome


@dataclass(frozen=True)
class MCPDiscoveredTool:
    """Size-bounded peer data for WS-03 validation; not an executable tool."""

    server_id: str
    untrusted_definition_json: str = field(repr=False)


@dataclass
class _ServerResult:
    server: MCPRuntimeServerConfig
    outcome: MCPLifecycleOutcome
    # Any is confined to the JSON-RPC boundary; never a diagnostic contract.
    tools: list[dict[str, Any]] = field(default_factory=list, repr=False)


class RuntimeMCPProvider:
    """Explicit lifetime owner, reachable even after failed runtime startup."""

    def __init__(self, config: MCPToolProviderConfig, workspace_root: str) -> None:
        self._config = config
        self._workspace_root = Path(workspace_root).expanduser().resolve()
        self.manager: MCPClientManager | None = None
        self.discovery = MCPDiscoveryState()
        self.diagnostics = MCPProviderDiagnostics()
        self.lifecycle: tuple[MCPServerLifecycleDiagnostic, ...] = ()
        self.prepared_tools: tuple[MCPDiscoveredTool, ...] = ()
        self._started = False

    async def start(self) -> None:
        if self._started or not self._config.enabled:
            return
        config = self._config.config
        # Recheck paths at execution time; do not inherit ambient process cwd.
        try:
            config.validate_workspace(str(self._workspace_root))
        except ValueError:
            raise ToolProviderLoadError("MCP workspace validation failed") from None
        servers = [server for server in config.servers if server.enabled]
        self.manager = MCPClientManager(
            MCPConfig(
                servers=[self._protocol_config(server) for server in servers],
                auto_connect=False,
                tool_name_prefix=config.tool_name_prefix,
            )
        )
        results: dict[str, _ServerResult] = {
            server.name: _ServerResult(server, "disabled")
            for server in config.servers
            if not server.enabled
        }
        try:
            if not config.auto_connect:
                results.update(
                    {
                        server.name: _ServerResult(server, "auto_connect_disabled")
                        for server in servers
                    }
                )
            else:
                # At most the configured number of tasks exist at once. Batch
                # order also makes total-cap admission deterministic.
                width = config.limits.max_parallel_server_connects
                for offset in range(0, len(servers), width):
                    batch = await self._batch(servers[offset : offset + width])
                    results.update({result.server.name: result for result in batch})
            self._publish(results)
            if any(result.outcome == "cleanup_failed" for result in results.values()):
                raise ToolProviderLoadError(
                    "MCP client cleanup incomplete; inspect mcp_provider.lifecycle"
                )
            if any(
                result.server.required and result.outcome != "connected"
                for result in results.values()
            ):
                raise ToolProviderLoadError(
                    "Required MCP server unavailable; inspect mcp_provider.lifecycle"
                )
            self._started = True
        except BaseException:
            # A canceled gather waits for its children to unwind before this
            # owner tears down the remaining successful/partial connections.
            for server in servers:
                results.setdefault(server.name, _ServerResult(server, "cancelled"))
            self._publish(results)
            self.discovery = self.discovery.model_copy(update={"status": "failed"})
            await self.stop()
            raise

    async def _batch(
        self, servers: list[MCPRuntimeServerConfig]
    ) -> list[_ServerResult]:
        tasks = [asyncio.create_task(self._discover(server)) for server in servers]
        try:
            return await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            # The first gather already canceled its children. Do not send a
            # second cancellation while they are unwinding transport cleanup.
            await asyncio.gather(*tasks, return_exceptions=True)
            raise
        except BaseException:
            for task in tasks:
                if not task.done():
                    task.cancel()
            # Drain every child before shutdown, including partial connection
            # cleanup. This gather is bounded to one configured worker batch.
            await asyncio.gather(*tasks, return_exceptions=True)
            raise

    def _protocol_config(self, server: MCPRuntimeServerConfig) -> MCPServerConfig:
        raw_cwd = Path(server.cwd) if server.cwd is not None else self._workspace_root
        cwd = (
            raw_cwd if raw_cwd.is_absolute() else self._workspace_root / raw_cwd
        ).resolve()
        return MCPServerConfig(
            name=server.name,
            enabled=True,
            command=server.command,
            args=list(server.args),
            env=dict(server.env),
            cwd=cwd,
            timeout_seconds=server.timeout_seconds,
            retry_attempts=server.retry_attempts,
        )

    async def _connect(self, server: MCPRuntimeServerConfig) -> None:
        manager = self.manager
        if manager is None:
            raise RuntimeError("MCP manager not initialized")
        for attempt in range(server.retry_attempts + 1):
            try:
                await manager.connect_or_raise(server.name)
                return
            except Exception:
                if attempt == server.retry_attempts:
                    raise

    async def _discover(self, server: MCPRuntimeServerConfig) -> _ServerResult:
        manager = self.manager
        if manager is None:
            raise RuntimeError("MCP manager not initialized")
        timeout = min(
            server.timeout_seconds,
            self._config.config.limits.connection_timeout_seconds,
        )
        outcome: MCPLifecycleOutcome
        try:
            await asyncio.wait_for(self._connect(server), timeout=timeout)
        except asyncio.TimeoutError:
            outcome = "connection_timeout"
        except Exception:
            outcome = "connection_failed"
        else:
            try:
                tools = await asyncio.wait_for(
                    manager.get_client(server.name).list_tools(), timeout=timeout
                )
                if not isinstance(tools, list):
                    raise ValueError("Invalid MCP catalog")
                return _ServerResult(server, "connected", tools)
            except asyncio.TimeoutError:
                outcome = "discovery_timeout"
            except Exception:
                outcome = "discovery_failed"
        try:
            await manager.disconnect(server.name)
        except Exception:
            outcome = "cleanup_failed"
        return _ServerResult(server, outcome)

    def _publish(self, results: dict[str, _ServerResult]) -> None:
        limits = self._config.config.limits
        states: list[MCPServerDiscoveryState] = []
        lifecycle: list[MCPServerLifecycleDiagnostic] = []
        prepared: list[MCPDiscoveredTool] = []
        connected = failed = discovered = rejected = schema_cost = 0
        aggregate_codes: set[MCPDiagnosticCode] = set()
        required_failure = False
        for server in self._config.config.servers:
            result = results[server.name]
            lifecycle.append(
                MCPServerLifecycleDiagnostic(
                    server.name, server.required, result.outcome
                )
            )
            codes: set[MCPDiagnosticCode] = set()
            server_rejected = 0
            if result.outcome == "connected":
                connected += 1
                discovered += len(result.tools)
                for index, tool in enumerate(result.tools):
                    if (
                        index >= limits.max_tools_per_server
                        or len(prepared) >= limits.max_total_tools
                    ):
                        codes.add("tool_limit")
                        server_rejected += 1
                        continue
                    try:
                        if (
                            not isinstance(tool, dict)
                            or not isinstance(tool.get("name"), str)
                            or not tool["name"]
                            or not isinstance(tool.get("inputSchema"), dict)
                            or not isinstance(tool.get("description", ""), str)
                        ):
                            raise ValueError("Invalid MCP tool shape")
                        encoded = json.dumps(
                            tool,
                            ensure_ascii=False,
                            allow_nan=False,
                            separators=(",", ":"),
                        )
                        size = len(encoded.encode("utf-8"))
                    except (ValueError, TypeError, RecursionError, UnicodeError):
                        codes.add("invalid_schema")
                        server_rejected += 1
                        continue
                    # One token per encoded byte is a conservative pre-registry
                    # upper bound. WS-03 owns final schema/token accounting.
                    if (
                        size > limits.max_schema_bytes_per_tool
                        or schema_cost + size > limits.max_schema_tokens
                    ):
                        codes.add("schema_limit")
                        server_rejected += 1
                        continue
                    prepared.append(MCPDiscoveredTool(server.name, encoded))
                    schema_cost += size
                state: Literal["not_started", "connected", "failed"] = "connected"
            elif result.outcome in ("disabled", "auto_connect_disabled"):
                state = "not_started"
            else:
                failed += 1
                state = "failed"
                codes.add("connection_failed")
            if server.required and result.outcome != "connected":
                required_failure = True
                codes.add("required_server_unavailable")
            rejected += server_rejected
            aggregate_codes.update(codes)
            states.append(
                MCPServerDiscoveryState(
                    server_id=server.name,
                    connection_state=state,
                    cache_timestamp=datetime.now(timezone.utc)
                    if state == "connected"
                    else None,
                    rejected_tools=server_rejected,
                    diagnostic_codes=tuple(sorted(codes)),
                )
            )
        self.prepared_tools = tuple(prepared)
        self.lifecycle = tuple(lifecycle)
        self.discovery = MCPDiscoveryState(
            status="failed"
            if required_failure
            else "partial"
            if failed
            else "completed",
            connected_servers=connected,
            failed_servers=failed,
            discovered_tools=discovered,
            selected_tools=0,
            servers=tuple(states),
        )
        self.diagnostics = MCPProviderDiagnostics(
            connected_servers=connected,
            failed_servers=failed,
            rejected_tools=rejected,
            codes=tuple(sorted(aggregate_codes)),
        )

    async def stop(self) -> None:
        """Release clients and untrusted handoff while retaining safe history."""
        if self.manager is not None:
            try:
                await self.manager.disconnect_all()
            except Exception:
                raise ToolProviderLoadError("MCP shutdown incomplete") from None
        self.prepared_tools = ()
        self._started = False
        self.discovery = self.discovery.model_copy(
            update={
                "connected_servers": 0,
                "servers": tuple(
                    state.model_copy(update={"connection_state": "disconnected"})
                    if state.connection_state == "connected"
                    else state
                    for state in self.discovery.servers
                ),
            }
        )
