"""Explicitly opted-in MCP snapshots, separate from the native tool ingester."""

from __future__ import annotations

import html
from datetime import UTC, datetime
from typing import Literal, Protocol, runtime_checkable
from uuid import uuid4

from friday_core.mcp import MCPIngestionPolicy, MCPToolCallProvenance
from friday_core.security import SanitizationConfig, ToolOutputSanitizer

from friday_memory.models.mcp import (
    MCPMemoryPreparation,
    MCPMemorySnapshot,
    MCPMemoryStorage,
    MCPStoredSnapshot,
)
from friday_memory.retrieval.mcp import snapshot_label


@runtime_checkable
class _OwnedMCPStorage(MCPMemoryStorage, Protocol):
    async def find_mcp_snapshot(
        self, entry_id: str, call_id: str
    ) -> MCPStoredSnapshot | None: ...


class MCPMemoryOwnershipError(RuntimeError):
    def __init__(self) -> None:
        super().__init__("Owned MCP memory record does not match this call.")


class MCPMemoryIngester:
    def __init__(self, storage: MCPMemoryStorage) -> None:
        self._storage = storage

    async def prepare(
        self,
        facts: MCPToolCallProvenance,
        text: str,
        entry_id: str,
        policy: MCPIngestionPolicy,
        *,
        record_id: str | None = None,
        stage_missing: bool = True,
    ) -> MCPMemoryPreparation:
        if not policy.long_term_memory_enabled:
            return MCPMemoryPreparation("disabled")
        if (
            facts.status != "succeeded"
            or facts.call_id is None
            or facts.memory_ingested
            or facts.memory_correlation_id is not None
            or facts.transcript_correlation_id not in {None, entry_id}
            or facts.output_sanitization_state not in {"unchanged", "sanitized"}
        ):
            return MCPMemoryPreparation("ineligible")
        grant: Literal["server", "tool"]
        if facts.tool.server_name in policy.opted_in_servers:
            grant = "server"
        elif facts.tool.canonical_name in policy.opted_in_tools:
            grant = "tool"
        else:
            return MCPMemoryPreparation("unallowlisted")
        try:
            size = len(text.encode("utf-8"))
            if size != facts.model_result_size_bytes:
                return MCPMemoryPreparation("ineligible")
            if size > policy.max_ingested_bytes:
                return MCPMemoryPreparation("oversized")
            capacity = max(1000, policy.max_ingested_bytes * 4)
            sanitizer = ToolOutputSanitizer(
                SanitizationConfig.model_validate(
                    {
                        "enabled": True,
                        "detection": {
                            "enabled": True,
                            "sensitivity": "high",
                            "max_scan_length": capacity,
                        },
                        "normalization": {
                            "enabled": True,
                            "max_normalize_length": capacity,
                        },
                        "wrapping": {"enabled": False},
                        "quarantine": {"action": "block", "log_detections": False},
                        "storage_policy": {
                            "store_raw_on_detection": False,
                            "raw_store_mode": "drop",
                        },
                    }
                )
            )
            checked = sanitizer.sanitize(text, facts.tool.canonical_name, "mcp_memory")
            rejected = bool(checked.detections)
            normalized = checked.sanitized_content
            del checked
            if rejected:
                return MCPMemoryPreparation("unsafe")
            previous: MCPStoredSnapshot | None = None
            if record_id is None and isinstance(self._storage, _OwnedMCPStorage):
                try:
                    previous = await self._storage.find_mcp_snapshot(
                        entry_id, facts.call_id
                    )
                except ValueError:
                    raise MCPMemoryOwnershipError() from None
                except Exception:
                    return MCPMemoryPreparation("storage_failed")
            identifier = record_id or (
                previous.snapshot.record_id
                if previous is not None
                else "mcp-memory-" + uuid4().hex
            )
            correlated = MCPToolCallProvenance.model_validate(
                {
                    **facts.model_dump(),
                    "ingestion_decision": "ingested",
                    "memory_ingested": True,
                    "memory_correlation_id": identifier,
                    "transcript_correlation_id": entry_id,
                }
            )
            # The fixed label can be constructed before the final validated DTO.
            label = (
                f"[MCP snapshot server={facts.tool.server_name} tool={facts.tool.canonical_name} "
                f"trust={facts.tool.trust_level} freshness=snapshot_at_capture revocation=not_implemented]"
            )
            stored = (
                label
                + '\n<untrusted_content source="mcp_memory">\n'
                + html.escape(normalized, quote=False)
                + "\n</untrusted_content>"
            )
            stored_size = len(stored.encode("utf-8"))
            if stored_size > policy.max_ingested_bytes:
                return MCPMemoryPreparation("oversized")
            snapshot = MCPMemorySnapshot(
                record_id=identifier,
                transcript_entry_id=entry_id,
                call=correlated,
                policy=policy,
                matched_grant=grant,
                memory_sanitization="sanitized" if normalized != text else "unchanged",
                stored_size_bytes=stored_size,
                captured_at=datetime.now(UTC),
            )
            snapshot.encoded_provenance()
            if not stored.startswith(snapshot_label(snapshot) + "\n"):
                return MCPMemoryPreparation("ineligible")
        except (ValueError, UnicodeError):
            return MCPMemoryPreparation("ineligible")
        try:
            previous = previous or await self._storage.get_mcp_snapshot(
                snapshot.record_id
            )
            if previous is not None:
                if self._matching(previous, snapshot, stored):
                    return MCPMemoryPreparation("prepared", previous.snapshot)
                if record_id is None:
                    raise MCPMemoryOwnershipError()
                return MCPMemoryPreparation("storage_failed")
            if not stage_missing:
                return MCPMemoryPreparation("storage_failed")
            if not await self._storage.stage_mcp_snapshot(snapshot, stored):
                # A concurrent preparation may have won this ownership. Reuse
                # only its exact durable content; never discard its record.
                if record_id is None and isinstance(self._storage, _OwnedMCPStorage):
                    previous = await self._storage.find_mcp_snapshot(
                        entry_id, facts.call_id
                    )
                    if previous is not None and self._matching(previous, snapshot, stored):
                        return MCPMemoryPreparation("prepared", previous.snapshot)
                    if previous is not None:
                        raise MCPMemoryOwnershipError()
                return MCPMemoryPreparation("storage_failed")
            durable = await self._storage.get_mcp_snapshot(snapshot.record_id)
            if (
                durable is None
                or durable.snapshot != snapshot
                or durable.text != stored
            ):
                return MCPMemoryPreparation("storage_failed")
        except MCPMemoryOwnershipError:
            raise
        except Exception:
            return MCPMemoryPreparation("storage_failed")
        return MCPMemoryPreparation("prepared", snapshot)

    @staticmethod
    def _matching(
        previous: MCPStoredSnapshot, candidate: MCPMemorySnapshot, text: str
    ) -> bool:
        old = previous.snapshot
        return (
            old.transcript_entry_id == candidate.transcript_entry_id
            and old.call == candidate.call.model_copy(
                update={"memory_correlation_id": old.record_id}
            )
            and old.policy == candidate.policy
            and old.matched_grant == candidate.matched_grant
            and old.memory_sanitization == candidate.memory_sanitization
            and old.stored_size_bytes == candidate.stored_size_bytes
            and previous.text == text
        )
