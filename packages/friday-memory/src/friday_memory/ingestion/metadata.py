"""Shared metadata for ingested files, independent of command or UI hosts."""

from __future__ import annotations


def build_ingested_file_metadata(
    source_path: str, description: str | None
) -> dict[str, str]:
    """Omit an absent description while retaining explicit empty descriptions."""
    metadata = {"source": source_path}
    if description is not None:
        metadata["description"] = description
    metadata["type"] = "ingested_file"
    return metadata
