"""Friday Chat transcript query compatibility and export contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from friday_runtime.transcript_views import (
    TranscriptContextLogView,
    TranscriptEntryView,
    TranscriptQueryStore,
    TranscriptSessionView,
)


@dataclass(frozen=True)
class TranscriptExportResult:
    """Files and exact record counts produced by one transcript export."""

    files: tuple[Path, ...]
    session_count: int = 0
    entry_count: int = 0
    context_log_count: int = 0


__all__ = [
    "TranscriptContextLogView",
    "TranscriptEntryView",
    "TranscriptExportResult",
    "TranscriptQueryStore",
    "TranscriptSessionView",
]
