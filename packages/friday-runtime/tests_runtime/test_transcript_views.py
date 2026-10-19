"""Frontend-independent transcript query contract tests."""

from __future__ import annotations

import inspect
import subprocess
import sys
from dataclasses import MISSING, FrozenInstanceError, astuple, fields
from datetime import UTC, datetime
from typing import get_type_hints

import pytest
from friday_runtime import transcript_views as views


def test_session_view_fields_defaults_and_immutability() -> None:
    started = datetime(2026, 1, 2, tzinfo=UTC)
    view = views.TranscriptSessionView(
        "session-1", "user-1", started, None, "model-1", 2, 11
    )

    assert astuple(view) == (
        "session-1",
        "user-1",
        started,
        None,
        "model-1",
        2,
        11,
        False,
    )
    assert tuple(field.name for field in fields(view)) == (
        "session_id",
        "user_id",
        "started_at",
        "ended_at",
        "model_name",
        "total_turns",
        "total_tokens",
        "archived",
    )
    assert [field.default for field in fields(view)] == [MISSING] * 7 + [False]
    assert views.TranscriptSessionView(
        "session-1", "user-1", started, None, "model-1", 2, 11, True
    ).archived
    assert view == views.TranscriptSessionView(
        "session-1", "user-1", started, None, "model-1", 2, 11
    )
    assert "__slots__" not in vars(type(view))
    attribute = "total_turns"
    with pytest.raises(FrozenInstanceError):
        setattr(view, attribute, 3)
    with pytest.raises(TypeError):
        views.TranscriptSessionView()  # type: ignore[call-arg]


def test_entry_view_fields_defaults_and_immutability() -> None:
    timestamp = datetime(2026, 1, 3, tzinfo=UTC)
    view = views.TranscriptEntryView(
        "entry-1", "session-1", 2, "user prompt", "answer", timestamp
    )

    assert astuple(view) == (
        "entry-1",
        "session-1",
        2,
        "user prompt",
        "answer",
        timestamp,
        None,
        None,
        None,
    )
    assert tuple(field.name for field in fields(view)) == (
        "entry_id",
        "session_id",
        "turn_number",
        "user_message",
        "assistant_message",
        "timestamp",
        "model_name",
        "total_tokens",
        "latency_ms",
    )
    assert [field.default for field in fields(view)] == [MISSING] * 6 + [None] * 3
    assert (
        views.TranscriptEntryView(
            "entry-1",
            "session-1",
            2,
            "user prompt",
            "answer",
            timestamp,
            "model-1",
            7,
            12.5,
        ).latency_ms
        == 12.5
    )
    assert "__slots__" not in vars(type(view))
    attribute = "assistant_message"
    with pytest.raises(FrozenInstanceError):
        setattr(view, attribute, "changed")
    with pytest.raises(TypeError):
        views.TranscriptEntryView()  # type: ignore[call-arg]


def test_context_log_view_fields_and_immutability() -> None:
    captured = datetime(2026, 1, 4, tzinfo=UTC)
    view = views.TranscriptContextLogView(
        "log-1", "session-1", 2, None, "raw prompt", None, captured
    )

    assert astuple(view) == (
        "log-1",
        "session-1",
        2,
        None,
        "raw prompt",
        None,
        captured,
    )
    assert tuple(field.name for field in fields(view)) == (
        "log_id",
        "session_id",
        "turn_number",
        "entry_id",
        "raw_prompt",
        "raw_response",
        "captured_at",
    )
    assert all(field.default is MISSING for field in fields(view))
    assert "__slots__" not in vars(type(view))
    attribute = "raw_response"
    with pytest.raises(FrozenInstanceError):
        setattr(view, attribute, "changed")
    with pytest.raises(TypeError):
        views.TranscriptContextLogView()  # type: ignore[call-arg]


def test_query_protocol_preserves_async_signatures_and_return_types() -> None:
    assert views.__all__ == [
        "TranscriptContextLogView",
        "TranscriptEntryView",
        "TranscriptQueryStore",
        "TranscriptSessionView",
    ]
    assert views.TranscriptQueryStore.__module__ == "friday_runtime.transcript_views"
    expected = {
        "query_sessions": (
            "(self, *, limit: 'int' = 1000, include_archived: 'bool' = False) "
            "-> 'tuple[TranscriptSessionView, ...]'",
            tuple[views.TranscriptSessionView, ...],
        ),
        "query_session": (
            "(self, session_id: 'str') -> 'TranscriptSessionView | None'",
            views.TranscriptSessionView | None,
        ),
        "query_entries": (
            "(self, session_id: 'str') -> 'tuple[TranscriptEntryView, ...]'",
            tuple[views.TranscriptEntryView, ...],
        ),
        "query_context_logs": (
            "(self, session_id: 'str') -> 'tuple[TranscriptContextLogView, ...]'",
            tuple[views.TranscriptContextLogView, ...],
        ),
    }
    for name, (signature, return_type) in expected.items():
        method = getattr(views.TranscriptQueryStore, name)
        assert inspect.iscoroutinefunction(method)
        assert str(inspect.signature(method)) == signature
        assert get_type_hints(method)["return"] == return_type


def test_neutral_import_does_not_load_frontends() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import friday_runtime.transcript_views, sys; "
            "raise SystemExit(any(name.split('.')[0] in {'friday_chat', 'friday_cli'} "
            "for name in sys.modules))",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
