"""Exact export bytes from the neutral transcript view contract."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from datetime import UTC, datetime

from friday_runtime.transcript_export_format import (
    serialize_context_logs_json,
    serialize_entries_csv,
    serialize_entries_jsonl,
    serialize_sessions_csv,
    serialize_training_jsonl,
    serialize_transcript_markdown,
)
from friday_runtime.transcript_views import (
    TranscriptContextLogView,
    TranscriptEntryView,
    TranscriptSessionView,
)

STAMP = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)


def _session() -> TranscriptSessionView:
    return TranscriptSessionView("s-α", None, STAMP, None, "m", 1, 0)


def _entry() -> TranscriptEntryView:
    return TranscriptEntryView("e-1", "s-α", 1, 'Hi, "Friday"\nagain', "Voilà", STAMP)


def _context_log() -> TranscriptContextLogView:
    return TranscriptContextLogView("l-1", "s-α", 1, "e-1", "raw\nπ", None, STAMP)


def test_frozen_before_code_export_bytes() -> None:
    """All seven former Chat files retain their exact content after extraction."""
    session = _session()
    entry = _entry()
    actual = {
        "sessions.csv": serialize_sessions_csv((session,)),
        "entries.csv": serialize_entries_csv((entry,)),
        "friday_current_session.csv": serialize_entries_csv((entry,)),
        "friday_current_session.jsonl": serialize_entries_jsonl((entry,)),
        "friday_current_session_training.jsonl": serialize_training_jsonl((entry,)),
        "friday_current_session.md": serialize_transcript_markdown(
            session, (entry,), user_name="Chuck", assistant_name="FridayX"
        ),
        "friday_prompts.json": serialize_context_logs_json(session, (_context_log(),)),
    }
    expected = {
        "sessions.csv": (
            '"session_id","user_id","started_at","ended_at","model_name",'
            '"total_turns","total_tokens","archived"\n'
            '"s-α","","2026-01-02T03:04:05+00:00","","m","1","0","False"\n'
        ),
        "entries.csv": (
            '"session_id","turn_number","timestamp","user_message",'
            '"assistant_message","model_name","total_tokens","latency_ms"\n'
            '"s-α","1","2026-01-02T03:04:05+00:00",'
            '"Hi, ""Friday""\nagain","Voilà","","",""\n'
        ),
        "friday_current_session.jsonl": (
            '{"assistant_message": "Voilà", "entry_id": "e-1", '
            '"latency_ms": null, "model_name": null, "session_id": "s-α", '
            '"timestamp": "2026-01-02T03:04:05+00:00", "total_tokens": null, '
            '"turn_number": 1, "user_message": "Hi, \\"Friday\\"\\nagain"}'
        ),
        "friday_current_session_training.jsonl": (
            '{"messages": [{"content": "Hi, \\"Friday\\"\\nagain", '
            '"role": "user"}, {"content": "Voilà", "role": "assistant"}]}'
        ),
        "friday_current_session.md": (
            '# Transcript: s-α\n\n## Turn 1\n\n**Chuck:** Hi, "Friday"\n'
            "again\n\n**FridayX:** Voilà\n"
        ),
        "friday_prompts.json": (
            '[\n  {\n    "captured_at": "2026-01-02T03:04:05+00:00",\n'
            '    "entry_id": "e-1",\n    "prompt": "raw\\nπ",\n'
            '    "raw_response": null,\n    "session_id": "s-α",\n'
            '    "turn_number": 1\n  }\n]'
        ),
    }
    expected["friday_current_session.csv"] = expected["entries.csv"]
    assert actual == expected
    assert {
        name: hashlib.sha256(content.encode("utf-8")).hexdigest()
        for name, content in actual.items()
    } == {
        "sessions.csv": "f259ccf80cb97232e5afaefbba5832a72c997351e82a16084300dc65e42134b2",
        "entries.csv": "4d918ce79fb4525be47f83b65b8fca830614e9a88131736a7bb9bf0e1288cd0c",
        "friday_current_session.csv": "4d918ce79fb4525be47f83b65b8fca830614e9a88131736a7bb9bf0e1288cd0c",
        "friday_current_session.jsonl": "243026aa856dffcb3bcdd700c391f0c1cda1dfc4ed3a40e8970f1c5b707fdb8c",
        "friday_current_session_training.jsonl": "998ffb447b36d5b5e4b0b6e8698447c84fa1c4da48925acb2a2dcd1bb746a09d",
        "friday_current_session.md": "515f2f3516ae6ea8ac8aa70ca19e4a4142939645afa07544d7c9bdf7e36f6c5c",
        "friday_prompts.json": "5b267f343e4fd44207121f0f7142cf4d673459ce91134fb86277c75610b675bf",
    }


def test_empty_exports_preserve_headers_and_newline_rules() -> None:
    assert serialize_sessions_csv(()) == (
        '"session_id","user_id","started_at","ended_at","model_name",'
        '"total_turns","total_tokens","archived"\n'
    )
    assert serialize_entries_csv(()) == (
        '"session_id","turn_number","timestamp","user_message",'
        '"assistant_message","model_name","total_tokens","latency_ms"\n'
    )
    assert serialize_entries_jsonl(()) == ""
    assert serialize_training_jsonl(()) == ""
    assert (
        serialize_transcript_markdown(
            replace(_session(), session_id="empty"),
            (),
            user_name="Chuck",
            assistant_name="FridayX",
        )
        == "# Transcript: empty\n"
    )
    assert serialize_context_logs_json(_session(), ()) == "[]"


def test_multiple_records_keep_caller_order_and_iso_spelling() -> None:
    archived = replace(
        _session(),
        session_id="archived",
        user_id="u,π",
        started_at=datetime(2026, 1, 3, 4, 5, 6),
        ended_at=STAMP,
        total_turns=2,
        total_tokens=7,
        archived=True,
    )
    assert serialize_sessions_csv((archived, _session())) == (
        '"session_id","user_id","started_at","ended_at","model_name",'
        '"total_turns","total_tokens","archived"\n'
        '"archived","u,π","2026-01-03T04:05:06",'
        '"2026-01-02T03:04:05+00:00","m","2","7","True"\n'
        '"s-α","","2026-01-02T03:04:05+00:00","","m","1","0","False"\n'
    )
    second = replace(
        _entry(),
        entry_id="e-2",
        turn_number=2,
        user_message=None,
        assistant_message=None,
        timestamp=datetime(2026, 1, 3, 4, 5, 6),
        model_name="m2",
        total_tokens=0,
        latency_ms=0.0,
    )
    assert serialize_entries_csv((second, _entry())) == (
        '"session_id","turn_number","timestamp","user_message",'
        '"assistant_message","model_name","total_tokens","latency_ms"\n'
        '"s-α","2","2026-01-03T04:05:06","","","m2","0","0.0"\n'
        '"s-α","1","2026-01-02T03:04:05+00:00",'
        '"Hi, ""Friday""\nagain","Voilà","","",""\n'
    )
    assert serialize_training_jsonl((second,)) == (
        '{"messages": [{"content": "", "role": "user"}, '
        '{"content": "", "role": "assistant"}]}'
    )
    assert serialize_entries_jsonl((second, _entry())) == (
        '{"assistant_message": null, "entry_id": "e-2", "latency_ms": 0.0, '
        '"model_name": "m2", "session_id": "s-α", '
        '"timestamp": "2026-01-03T04:05:06", "total_tokens": 0, '
        '"turn_number": 2, "user_message": null}\n'
        '{"assistant_message": "Voilà", "entry_id": "e-1", '
        '"latency_ms": null, "model_name": null, "session_id": "s-α", '
        '"timestamp": "2026-01-02T03:04:05+00:00", "total_tokens": null, '
        '"turn_number": 1, "user_message": "Hi, \\"Friday\\"\\nagain"}'
    )
    assert serialize_transcript_markdown(
        _session(),
        (second,),
        user_name="Visitor",
        assistant_name="Agent",
    ) == ("# Transcript: s-α\n\n## Turn 2\n\n**Visitor:** \n\n**Agent:**\n")


def test_context_log_order_and_nonnullable_response() -> None:
    later = replace(
        _context_log(),
        log_id="l-2",
        turn_number=2,
        entry_id=None,
        raw_prompt="next",
        raw_response="reply",
        captured_at=datetime(2026, 1, 3, 4, 5, 6),
    )
    assert serialize_context_logs_json(_session(), (later, _context_log())) == (
        '[\n  {\n    "captured_at": "2026-01-03T04:05:06",\n'
        '    "entry_id": null,\n    "prompt": "next",\n'
        '    "raw_response": "reply",\n    "session_id": "s-α",\n'
        '    "turn_number": 2\n  },\n  {\n'
        '    "captured_at": "2026-01-02T03:04:05+00:00",\n'
        '    "entry_id": "e-1",\n    "prompt": "raw\\nπ",\n'
        '    "raw_response": null,\n    "session_id": "s-α",\n'
        '    "turn_number": 1\n  }\n]'
    )
