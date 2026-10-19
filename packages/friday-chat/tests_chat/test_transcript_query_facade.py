"""Chat compatibility for neutral transcript query contracts."""

from __future__ import annotations

import pickle
from dataclasses import astuple
from datetime import UTC, datetime
from pathlib import Path

import friday_chat.transcripts as chat
import friday_runtime.transcript_views as neutral


def test_chat_reexports_neutral_query_contracts_by_identity() -> None:
    assert chat.__all__ == [
        "TranscriptContextLogView",
        "TranscriptEntryView",
        "TranscriptExportResult",
        "TranscriptQueryStore",
        "TranscriptSessionView",
    ]
    for name in (
        "TranscriptContextLogView",
        "TranscriptEntryView",
        "TranscriptQueryStore",
        "TranscriptSessionView",
    ):
        contract = getattr(neutral, name)
        assert getattr(chat, name) is contract
        assert contract.__module__ == "friday_runtime.transcript_views"

    session = chat.TranscriptSessionView(
        "session-1",
        None,
        datetime(2026, 1, 1, tzinfo=UTC),
        None,
        "model-1",
        1,
        5,
    )
    assert type(session) is neutral.TranscriptSessionView
    assert astuple(session)[-1] is False


def test_legacy_chat_pickle_globals_resolve_to_neutral_objects() -> None:
    for name in (
        "TranscriptContextLogView",
        "TranscriptEntryView",
        "TranscriptQueryStore",
        "TranscriptSessionView",
    ):
        old_global = f"cfriday_chat.transcripts\n{name}\n.".encode()
        assert pickle.loads(old_global) is getattr(neutral, name)


def test_export_result_remains_chat_owned_with_existing_defaults() -> None:
    result = chat.TranscriptExportResult(files=(Path("transcript.json"),))
    assert result.files == (Path("transcript.json"),)
    assert result.session_count == 0
    assert result.entry_count == 0
    assert result.context_log_count == 0
    assert chat.TranscriptExportResult.__module__ == "friday_chat.transcripts"
    assert not hasattr(neutral, "TranscriptExportResult")
