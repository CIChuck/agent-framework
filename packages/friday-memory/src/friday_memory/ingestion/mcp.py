"""Explicitly opted-in MCP snapshots, separate from the native tool ingester."""

from __future__ import annotations

import asyncio
import html
from contextlib import suppress
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from friday_core.mcp import MCPIngestionPolicy, MCPToolCallProvenance
from friday_core.security import SanitizationConfig, ToolOutputSanitizer

from friday_memory.models.mcp import (
    MCPMemoryPreparation,
    MCPMemorySnapshot,
    MCPMemoryStorage,
)
from friday_memory.retrieval.mcp import snapshot_label


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
            identifier = (
                record_id if record_id is not None else "mcp-memory-" + uuid4().hex
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
                captured_at=datetime.now(timezone.utc),
            )
            snapshot.encoded_provenance()
            if not stored.startswith(snapshot_label(snapshot) + "\n"):
                return MCPMemoryPreparation("ineligible")
        except (ValueError, UnicodeError):
            return MCPMemoryPreparation("ineligible")
        try:
            previous = await self._storage.get_mcp_snapshot(snapshot.record_id)
            if previous is not None:
                if (
                    previous.snapshot.call == snapshot.call
                    and previous.snapshot.policy == snapshot.policy
                    and previous.snapshot.matched_grant == snapshot.matched_grant
                    and previous.text == stored
                ):
                    return MCPMemoryPreparation("prepared", previous.snapshot)
                return MCPMemoryPreparation("storage_failed")
            if not await self._storage.stage_mcp_snapshot(snapshot, stored):
                await self._discard(snapshot)
                return MCPMemoryPreparation("storage_failed")
            durable = await self._storage.get_mcp_snapshot(snapshot.record_id)
            if (
                durable is None
                or durable.snapshot != snapshot
                or durable.text != stored
            ):
                await self._discard(snapshot)
                return MCPMemoryPreparation("storage_failed")
        except asyncio.CancelledError:
            await self._discard(snapshot)
            raise
        except Exception:
            await self._discard(snapshot)
            return MCPMemoryPreparation("storage_failed")
        return MCPMemoryPreparation("prepared", snapshot)

    async def _discard(self, snapshot: MCPMemorySnapshot) -> None:
        # An incomplete cleanup remains pending and cannot enter retrieval.
        with suppress(Exception):
            await self._storage.discard_mcp_snapshot(snapshot)
