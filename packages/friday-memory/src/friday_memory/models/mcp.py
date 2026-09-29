"""Typed, bounded MCP semantic snapshots and durable storage receipts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Protocol

from friday_core.mcp import MCPIngestionPolicy, MCPSafeIdentifier, MCPToolCallProvenance
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

MAX_PROVENANCE_BYTES = 65536
_SAFE_ID = TypeAdapter(MCPSafeIdentifier)


class MCPMemorySnapshot(BaseModel):
    """A captured untrusted result; persistence does not imply current truth."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    source_type: Literal["mcp_tool"] = "mcp_tool"
    record_id: MCPSafeIdentifier
    transcript_entry_id: MCPSafeIdentifier
    call: MCPToolCallProvenance
    policy: MCPIngestionPolicy
    matched_grant: Literal["server", "tool"]
    memory_sanitization: Literal["unchanged", "sanitized"]
    stored_size_bytes: int = Field(gt=0)
    captured_at: datetime
    freshness: Literal["snapshot_at_capture", "stale", "unknown"] = (
        "snapshot_at_capture"
    )
    revocation: Literal["not_implemented"] = "not_implemented"

    @model_validator(mode="after")
    def _validate_snapshot(self) -> MCPMemorySnapshot:
        facts = self.call
        if (
            facts.status != "succeeded"
            or facts.call_id is None
            or facts.output_sanitization_state not in {"unchanged", "sanitized"}
            or facts.model_result_size_bytes is None
            or not facts.memory_ingested
            or facts.ingestion_decision != "ingested"
            or facts.memory_correlation_id != self.record_id
            or facts.transcript_correlation_id != self.transcript_entry_id
            or not self.policy.long_term_memory_enabled
            or self.captured_at.utcoffset() is None
            or self.stored_size_bytes > self.policy.max_ingested_bytes
        ):
            raise ValueError("Invalid MCP memory snapshot")
        _SAFE_ID.validate_python(facts.tool.server_name)
        granted = (
            facts.tool.server_name in self.policy.opted_in_servers
            if self.matched_grant == "server"
            else facts.tool.canonical_name in self.policy.opted_in_tools
        )
        if not granted:
            raise ValueError("Invalid MCP memory grant")
        return self

    def encoded_provenance(self) -> str:
        """Encode only the validated DTO, with an independent metadata cap."""
        value = self.model_dump_json()
        if len(value.encode("utf-8")) > MAX_PROVENANCE_BYTES:
            raise ValueError("MCP memory provenance exceeds its limit")
        return value


@dataclass(frozen=True)
class MCPStoredSnapshot:
    snapshot: MCPMemorySnapshot
    text: str
    state: Literal["pending", "committed"]


@dataclass(frozen=True)
class MCPMemoryPreparation:
    decision: Literal[
        "disabled",
        "ineligible",
        "unallowlisted",
        "unsafe",
        "oversized",
        "storage_failed",
        "prepared",
    ]
    snapshot: MCPMemorySnapshot | None = None


class MCPMemoryStorage(Protocol):
    """Memory-owned durable operations; no transcript implementation coupling."""

    async def stage_mcp_snapshot(
        self, snapshot: MCPMemorySnapshot, text: str
    ) -> bool: ...
    async def get_mcp_snapshot(self, record_id: str) -> MCPStoredSnapshot | None: ...
    async def publish_mcp_snapshot(self, snapshot: MCPMemorySnapshot) -> bool: ...
    async def discard_mcp_snapshot(self, snapshot: MCPMemorySnapshot) -> bool: ...
