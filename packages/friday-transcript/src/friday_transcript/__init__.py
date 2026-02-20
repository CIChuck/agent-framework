"""
Friday Transcript - Persistent conversation logging.

Provides immutable, append-only transcript storage for:
- Debugging/development
- Audit/compliance
- Training data collection
- Analytics
- Persistent episodic memory backend
"""

from friday_transcript.correlation import (
    build_correlation_index,
    correlate_promotion_entries,
    filter_entries_by_metadata,
    summarize_correlation_slice,
)
from friday_transcript.exporters.csv import CSVExporter
from friday_transcript.exporters.jsonl import JSONLExporter
from friday_transcript.exporters.markdown import MarkdownExporter
from friday_transcript.models.transcript import (
    ContextLogEntry,
    ToolCall,
    ToolResult,
    TranscriptEntry,
    TranscriptSession,
)
from friday_transcript.stores.jsonl import JSONLTranscriptStore
from friday_transcript.stores.protocol import TranscriptStore
from friday_transcript.stores.sqlite import SQLiteTranscriptStore

__all__ = [
    # Models
    "ContextLogEntry",
    "TranscriptEntry",
    "TranscriptSession",
    "ToolCall",
    "ToolResult",
    # Protocol
    "TranscriptStore",
    # Store Implementations
    "SQLiteTranscriptStore",
    "JSONLTranscriptStore",
    # Exporters
    "CSVExporter",
    "JSONLExporter",
    "MarkdownExporter",
    # Correlation helpers
    "build_correlation_index",
    "correlate_promotion_entries",
    "filter_entries_by_metadata",
    "summarize_correlation_slice",
]
