"""
Friday Transcript - Persistent conversation logging.

Provides immutable, append-only transcript storage for:
- Debugging/development
- Audit/compliance
- Training data collection
- Analytics
- Persistent episodic memory backend
"""

from friday_transcript.models.transcript import (
    TranscriptEntry,
    TranscriptSession,
    ToolCall,
    ToolResult,
)
from friday_transcript.stores.protocol import TranscriptStore
from friday_transcript.stores.sqlite import SQLiteTranscriptStore
from friday_transcript.stores.jsonl import JSONLTranscriptStore
from friday_transcript.exporters.jsonl import JSONLExporter
from friday_transcript.exporters.markdown import MarkdownExporter

__all__ = [
    # Models
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
    "JSONLExporter",
    "MarkdownExporter",
]
