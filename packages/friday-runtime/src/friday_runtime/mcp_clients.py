"""Typed Runtime assembly of accepted MCP clients, without transport duplication."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol

from friday_core.mcp import MCPClientLimits
from friday_mcp.client import (
    MCPClientBase,
    MCPManagedServer,
    ProtocolLimits,
    StdioMCPClient,
    StreamableHTTPMCPClient,
)
from friday_mcp.config import MCPServerConfig

from friday_runtime.config import MCPRuntimeHTTPServerConfig, MCPRuntimeServerConfig


class MCPCredentialResolver(Protocol):
    """Resolve one explicit reference only at enabled connection assembly."""

    def resolve(self, name: str) -> str | None: ...


class EnvironmentMCPCredentialResolver:
    def resolve(self, name: str) -> str | None:
        return os.environ.get(name)


def create_mcp_client(
    server: MCPRuntimeServerConfig | MCPRuntimeHTTPServerConfig,
    limits: MCPClientLimits,
    workspace_root: Path,
    credential_resolver: MCPCredentialResolver,
) -> MCPClientBase:
    """No factory effect occurs for disabled entries or auto_connect false."""
    if not server.enabled:
        raise ValueError("MCP server is disabled")
    protocol_limits = ProtocolLimits(
        result_bytes=min(limits.max_result_bytes, 65536),
        concurrent_requests=min(limits.max_parallel_tool_calls, 4),
        timeout_seconds=float(
            max(
                min(server.timeout_seconds, limits.connection_timeout_seconds, 30),
                min(server.tool_timeout_seconds, limits.tool_timeout_seconds, 30),
            )
        ),
    )
    if isinstance(server, MCPRuntimeHTTPServerConfig):
        token = None
        failed = False
        if server.auth == "bearer_env":
            if server.credential_env is None:
                raise ValueError("MCP credential reference missing")
            try:
                token = credential_resolver.resolve(server.credential_env)
                failed = (
                    not isinstance(token, str)
                    or not 0 < len(token) <= 8192
                    or any(not 0x21 <= ord(c) <= 0x7E for c in token)
                )
            except Exception:
                failed = True
            if failed:
                raise ValueError("MCP credential unavailable")
        client = StreamableHTTPMCPClient(
            server.url,
            protocol_version=server.protocol_version,
            name=server.name,
            endpoint_policy=server.network.endpoint_policy(),
            limits=protocol_limits,
            bearer_token=token,
        )
        client.request_timeout_seconds = float(
            min(server.timeout_seconds, limits.connection_timeout_seconds, 30)
        )
        return client
    raw_cwd = Path(server.cwd) if server.cwd is not None else workspace_root
    cwd = (raw_cwd if raw_cwd.is_absolute() else workspace_root / raw_cwd).resolve()
    server.validate_workspace(str(workspace_root))
    if server.protocol_profile == "legacy":
        return StdioMCPClient.from_config(
            MCPServerConfig(
                name=server.name,
                command=server.command,
                args=list(server.args),
                env=dict(server.env),
                cwd=cwd,
                timeout_seconds=server.timeout_seconds,
                retry_attempts=server.retry_attempts,
            )
        )
    if server.command is None:
        raise ValueError("MCP stdio command missing")
    stdio = StdioMCPClient(
        server.name,
        server.command,
        list(server.args),
        dict(server.env) or None,
        cwd,
        protocol_profile=server.protocol_profile,
        limits=protocol_limits,
    )
    stdio.request_timeout_seconds = float(
        min(server.timeout_seconds, limits.connection_timeout_seconds, 30)
    )
    return stdio


def managed_mcp_server(
    server: MCPRuntimeServerConfig | MCPRuntimeHTTPServerConfig,
    limits: MCPClientLimits,
    workspace_root: Path,
    credential_resolver: MCPCredentialResolver,
) -> MCPManagedServer:
    def factory() -> MCPClientBase:
        return create_mcp_client(server, limits, workspace_root, credential_resolver)

    return MCPManagedServer(server.name, server.enabled, factory)
