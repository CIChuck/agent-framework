"""Validated source labels, exclusion and retrieval eligibility for MCP memory."""

from __future__ import annotations

from collections.abc import Mapping

from friday_memory.models.mcp import (
    MAX_PROVENANCE_BYTES,
    MCPMemorySnapshot,
    MCPStoredSnapshot,
)


def is_mcp_memory(metadata: Mapping[str, object]) -> bool:
    return (
        metadata.get("source_type") == "mcp_tool"
        or metadata.get("type") == "mcp_tool_snapshot"
        or "mcp_provenance" in metadata
        or "mcp_state" in metadata
    )


def snapshot_label(snapshot: MCPMemorySnapshot) -> str:
    return (
        f"[MCP snapshot server={snapshot.call.tool.server_name} "
        f"tool={snapshot.call.tool.canonical_name} trust={snapshot.call.tool.trust_level} "
        f"freshness={snapshot.freshness} revocation={snapshot.revocation}]"
    )


def decode_mcp_snapshot(record: Mapping[str, object]) -> MCPStoredSnapshot | None:
    metadata = record.get("metadata")
    if not isinstance(metadata, Mapping) or not is_mcp_memory(metadata):
        return None
    encoded = metadata.get("mcp_provenance")
    state = metadata.get("mcp_state")
    text = record.get("text")
    if (
        not isinstance(encoded, str)
        or state not in ("pending", "committed")
        or not isinstance(text, str)
        or metadata.get("source_type") != "mcp_tool"
        or metadata.get("type") != "mcp_tool_snapshot"
    ):
        return None
    try:
        if len(encoded.encode("utf-8")) > MAX_PROVENANCE_BYTES:
            return None
        snapshot = MCPMemorySnapshot.model_validate_json(encoded)
        if (
            record.get("id") != snapshot.record_id
            or len(text.encode("utf-8")) != snapshot.stored_size_bytes
            or not text.startswith(
                snapshot_label(snapshot) + '\n<untrusted_content source="mcp_memory">\n'
            )
            or not text.endswith("\n</untrusted_content>")
        ):
            return None
    except (ValueError, UnicodeError):
        return None
    if state == "pending":
        return MCPStoredSnapshot(snapshot, text, "pending")
    return MCPStoredSnapshot(snapshot, text, "committed")


def mcp_retrieval_eligible(record: Mapping[str, object]) -> bool:
    metadata = record.get("metadata")
    if not isinstance(metadata, Mapping) or not is_mcp_memory(metadata):
        return True
    decoded = decode_mcp_snapshot(record)
    return decoded is not None and decoded.state == "committed"


def mcp_memory_snippet(
    record: Mapping[str, object], *, include_mcp: bool = True
) -> str | None:
    """Return a whole labeled untrusted snapshot, never an unlabeled prefix."""
    if not include_mcp:
        return None
    decoded = decode_mcp_snapshot(record)
    return (
        decoded.text if decoded is not None and decoded.state == "committed" else None
    )


def estimated_snippet_tokens(text: str) -> int:
    """Conservative UTF-8 byte/4 estimate, including every label and wrapper."""
    return (len(text.encode("utf-8")) + 3) // 4
