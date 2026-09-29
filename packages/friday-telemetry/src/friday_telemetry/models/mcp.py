"""Closed, content-free MCP telemetry contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MCPEventName = Literal[
    "connection_start",
    "connection_finish",
    "connection_failure",
    "list_tools_start",
    "list_tools_finish",
    "list_tools_failure",
    "tool_skipped",
    "tool_registered",
    "tool_call_start",
    "tool_call_finish",
    "tool_call_failure",
    "tool_output_decision",
    "budget_skip",
    "ingestion_decision",
    "disconnect",
]

MCPEventReason = Literal[
    "connected",
    "success",
    "disabled",
    "auto_connect_disabled",
    "connection_failed",
    "connection_timeout",
    "discovery_failed",
    "discovery_timeout",
    "cancelled",
    "cleanup_failed",
    "required_server_unavailable",
    "tool_limit",
    "schema_limit",
    "invalid_schema",
    "name_collision",
    "filter_excluded",
    "missing_include",
    "registration_failed",
    "registered",
    "selected",
    "filtered",
    "rejected",
    "capped",
    "unavailable",
    "unknown",
    "timeout",
    "tool_error",
    "invalid_result",
    "execution_error",
    "output_rejected",
    "succeeded",
    "blocked",
    "truncated",
    "checked",
    "unknown_tool",
    "count_limit",
    "token_limit",
    "tools_disabled",
    "mcp_count_limit",
    "memory_floor",
    "missing_metadata",
    "unsafe_schema",
    "not_registered",
    "not_relevant",
    "not_requested",
    "skipped",
    "pending",
    "published",
    "receipt_committed",
    "ingestion_disabled",
    "ingestion_denied",
]


class MCPEvent(BaseModel):
    """An allowlisted event. Refs are opaque hashes, never source identifiers."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    name: MCPEventName
    server_ref: str | None = Field(default=None, pattern=r"^[0-9a-f]{16}$")
    tool_ref: str | None = Field(default=None, pattern=r"^[0-9a-f]{16}$")
    reason: MCPEventReason | None = None
    count: int | None = Field(default=None, ge=0, le=1_000_000)
    required: bool | None = None

    def attributes(self) -> dict[str, str | int | bool]:
        """Return only declared exporter-safe scalar fields."""
        return self.model_dump(exclude={"name"}, exclude_none=True)
