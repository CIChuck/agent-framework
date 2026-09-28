"""Runtime-owned MCP lifecycle, bounded discovery and transactional registration.

Raw JSON exists only in the explicitly untrusted, non-repr handoff, not in
diagnostics, logs, memory, or transcript storage.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Protocol

from friday_core.interfaces import ToolDefinition
from friday_core.mcp import (
    MCPDiagnosticCode,
    MCPDiscoveryState,
    MCPProviderDiagnostics,
    MCPServerDiscoveryState,
    MCPToolMetadata,
    build_mcp_metadata_index,
)
from friday_mcp.client.manager import MCPClientManager
from friday_mcp.config import MCPConfig, MCPServerConfig
from friday_mcp.protocols import MCPClient

from friday_runtime.config import MCPRuntimeServerConfig, MCPToolProviderConfig
from friday_runtime.mcp_registration import (
    MCPBindingContext,
    MCPRegistrationDecision,
    MCPRegistrationError,
    prepare_registration,
)
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


class MCPRegistrationRegistry(Protocol):
    """Public registry operations used by the explicit registration owner."""

    def register(self, tool: ToolDefinition) -> None: ...
    def list_names(self) -> list[str]: ...
    def get(self, name: str) -> ToolDefinition | None: ...
    def unregister(self, name: str) -> bool: ...


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
        self._registry: MCPRegistrationRegistry | None = None
        self._owned: dict[str, ToolDefinition] = {}
        self._tool_metadata: Mapping[str, MCPToolMetadata] = build_mcp_metadata_index(
            ()
        )
        self.registration_decisions: tuple[MCPRegistrationDecision, ...] = ()

    @property
    def tool_metadata(self) -> Mapping[str, MCPToolMetadata]:
        return self._tool_metadata

    @property
    def registration_registry(self) -> MCPRegistrationRegistry | None:
        """Inspectable retained owner when rollback/shutdown is incomplete."""
        return self._registry

    @property
    def owned_tool_names(self) -> tuple[str, ...]:
        return tuple(self._owned)

    @property
    def binding_context(self) -> MCPBindingContext:
        return MCPBindingContext(
            self.registration_decisions,
            self._config.config.tool_name_prefix,
            tuple(
                state.server_id
                for state in self.discovery.servers
                if state.connection_state == "failed"
            ),
        )

    async def register_tools(self, registry: MCPRegistrationRegistry) -> None:
        """Publish once after discovery, rolling back only this owner's entries."""
        if self._registry is registry:
            return
        if self._registry is not None or self._owned:
            raise ToolProviderLoadError(
                "MCP registrations still owned; stop before retry"
            )
        manager = self.manager
        clients: dict[str, MCPClient] = {}
        if manager is not None:
            for state in self.discovery.servers:
                if state.connection_state == "connected":
                    clients[state.server_id] = manager.get_client(state.server_id)
        try:
            plan = prepare_registration(
                self._config, self.prepared_tools, clients, registry.list_names()
            )
        except MCPRegistrationError as exc:
            self.registration_decisions = exc.decisions
            self._publish_registration_counts(exc.decisions, exc.code, committed=False)
            await self.stop()
            raise ToolProviderLoadError(str(exc)) from None
        self.registration_decisions = plan.decisions
        self._registry = registry
        try:
            for wrapper, metadata in zip(plan.wrappers, plan.metadata, strict=True):
                try:
                    registry.register(wrapper)
                except BaseException:
                    # Public register can insert then raise: retain any newly
                    # inserted object before unwinding, without private access.
                    inserted = registry.get(wrapper.name)
                    if inserted is not None:
                        self._owned[wrapper.name] = inserted
                    raise
                inserted = registry.get(wrapper.name)
                if inserted is None:
                    raise RuntimeError("MCP registration not visible")
                self._owned[wrapper.name] = inserted
                # Recheck the actual native-rewrapped export, not just input.
                actual_size = max(
                    len(
                        json.dumps(
                            inserted.to_schema(format),
                            ensure_ascii=False,
                            allow_nan=False,
                            separators=(",", ":"),
                        ).encode("utf-8")
                    )
                    for format in ("plain", "openai")
                )
                if actual_size != metadata.schema_byte_size or any(
                    inserted.to_schema(format) != wrapper.to_schema(format)
                    for format in ("plain", "openai")
                ):
                    raise RuntimeError("MCP registered export mismatch")
            self._tool_metadata = build_mcp_metadata_index(plan.metadata)
            self.registration_decisions = tuple(
                replace(decision, reason="registered")
                if decision.reason == "selected"
                else decision
                for decision in plan.decisions
            )
            self._publish_registration_counts(plan.decisions, committed=True)
        except BaseException as exc:
            self._tool_metadata = build_mcp_metadata_index(
                item for item in plan.metadata if item.canonical_name in self._owned
            )
            self._publish_registration_counts(
                plan.decisions, "registration_failed", committed=False
            )
            await self.stop()
            if isinstance(exc, asyncio.CancelledError):
                raise
            raise ToolProviderLoadError(
                "MCP registration failed; inspect mcp_provider.diagnostics"
            ) from None

    def _publish_registration_counts(
        self,
        decisions: tuple[MCPRegistrationDecision, ...],
        code: MCPDiagnosticCode | None = None,
        *,
        committed: bool,
    ) -> None:
        rejected = sum(
            decision.reason in {"rejected", "capped"} for decision in decisions
        )
        filtered = sum(decision.reason == "filtered" for decision in decisions)
        selected = sum(
            decision.reason in {"selected", "registered"} for decision in decisions
        )
        codes = set(self.diagnostics.codes)
        codes.update(
            decision.code for decision in decisions if decision.code is not None
        )
        if code is not None:
            codes.add(code)
        self.diagnostics = self.diagnostics.model_copy(
            update={
                "registered_tools": selected if committed else 0,
                "rejected_tools": self.diagnostics.rejected_tools + rejected,
                "filtered_tools": filtered,
                "codes": tuple(sorted(codes)),
            }
        )
        self.discovery = self.discovery.model_copy(
            update={
                "selected_tools": selected,
                "servers": tuple(
                    state.model_copy(
                        update={
                            "rejected_tools": state.rejected_tools
                            + sum(
                                d.server_id == state.server_id
                                and d.reason in {"rejected", "capped"}
                                for d in decisions
                            ),
                            "filtered_tools": sum(
                                d.server_id == state.server_id
                                and d.reason == "filtered"
                                for d in decisions
                            ),
                            "diagnostic_codes": tuple(
                                sorted(
                                    set(state.diagnostic_codes)
                                    | {
                                        d.code
                                        for d in decisions
                                        if d.server_id == state.server_id
                                        and d.code is not None
                                    }
                                )
                            ),
                        }
                    )
                    for state in self.discovery.servers
                ),
            }
        )

    def _remove_registrations(self) -> None:
        registry = self._registry
        incomplete = False
        if registry is not None:
            for name, owned in tuple(self._owned.items()):
                try:
                    current = registry.get(name)
                    if current is owned:
                        registry.unregister(name)
                        if registry.get(name) is owned:
                            incomplete = True
                            continue
                    self._owned.pop(name)
                except Exception:
                    incomplete = True
        self._tool_metadata = build_mcp_metadata_index(
            value for name, value in self._tool_metadata.items() if name in self._owned
        )
        self.diagnostics = self.diagnostics.model_copy(
            update={"registered_tools": len(self._owned)}
        )
        self.registration_decisions = tuple(
            replace(decision, reason="unavailable")
            if decision.reason == "registered"
            and decision.canonical_name not in self._owned
            else decision
            for decision in self.registration_decisions
        )
        if incomplete:
            raise ToolProviderLoadError(
                "MCP registry cleanup incomplete; inspect mcp_provider.owned_tool_names"
            ) from None
        self._registry = None

    async def start(self) -> None:
        if self._started or not self._config.enabled:
            return
        if self.manager is not None or self._registry is not None:
            # Failed startup can retain transports even with false lifecycle
            # flags. Release them through their owner before replacing it.
            await self.stop()
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
        """Remove owned model-accessible tools before clients; retain safe history."""
        # A failed or canceled cleanup must not leave a startup handoff usable.
        self.prepared_tools = ()
        self._started = False
        self._remove_registrations()
        if self.manager is not None:
            try:
                await self.manager.disconnect_all()
            except Exception:
                raise ToolProviderLoadError("MCP shutdown incomplete") from None
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
