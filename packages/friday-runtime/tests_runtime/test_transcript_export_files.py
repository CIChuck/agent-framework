"""Direct file effects for UI-neutral transcript exports."""

from __future__ import annotations

import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
from friday_runtime.transcript_export_files import (
    write_context_log_file,
    write_current_session_file,
)
from friday_runtime.transcript_views import (
    TranscriptContextLogView,
    TranscriptEntryView,
    TranscriptSessionView,
)

STAMP = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
SESSION = TranscriptSessionView("s-α", None, STAMP, None, "m", 1, 0)
ENTRY = TranscriptEntryView("e-1", "s-α", 1, 'Hi, "Friday"\nagain', "Voilà", STAMP)
LOG = TranscriptContextLogView("l-1", "s-α", 1, "e-1", "raw\nπ", None, STAMP)


@pytest.mark.parametrize(
    ("export_format", "expected"),
    [
        (
            "csv",
            '"session_id","turn_number","timestamp","user_message",'
            '"assistant_message","model_name","total_tokens","latency_ms"\n'
            '"s-α","1","2026-01-02T03:04:05+00:00",'
            '"Hi, ""Friday""\nagain","Voilà","","",""\n',
        ),
        (
            "jsonl",
            '{"assistant_message": "Voilà", "entry_id": "e-1", '
            '"latency_ms": null, "model_name": null, "session_id": "s-α", '
            '"timestamp": "2026-01-02T03:04:05+00:00", "total_tokens": null, '
            '"turn_number": 1, "user_message": "Hi, \\"Friday\\"\\nagain"}',
        ),
        (
            "training",
            '{"messages": [{"content": "Hi, \\"Friday\\"\\nagain", '
            '"role": "user"}, {"content": "Voilà", "role": "assistant"}]}',
        ),
        (
            "markdown",
            '# Transcript: s-α\n\n## Turn 1\n\n**Chuck:** Hi, "Friday"\n'
            "again\n\n**FridayX:** Voilà\n",
        ),
    ],
)
def test_current_session_writes_exact_utf8_bytes(
    tmp_path: Path,
    export_format: str,
    expected: str,
) -> None:
    destination = tmp_path / "export"
    write_current_session_file(
        destination,
        SESSION,
        (ENTRY,),
        export_format=export_format,
        user_name="Chuck",
        assistant_name="FridayX",
    )
    assert destination.read_bytes() == expected.encode("utf-8")


def test_context_log_writes_exact_utf8_bytes(tmp_path: Path) -> None:
    destination = tmp_path / "friday_prompts.json"
    write_context_log_file(destination, SESSION, (LOG,))
    assert (
        destination.read_bytes()
        == (
            '[\n  {\n    "captured_at": "2026-01-02T03:04:05+00:00",\n'
            '    "entry_id": "e-1",\n    "prompt": "raw\\nπ",\n'
            '    "raw_response": null,\n    "session_id": "s-α",\n'
            '    "turn_number": 1\n  }\n]'
        ).encode()
    )


def test_empty_exports_and_overwrite_existing_file(tmp_path: Path) -> None:
    destination = tmp_path / "export"
    destination.write_text("stale longer text", encoding="utf-8")
    write_current_session_file(destination, SESSION, (), export_format="jsonl")
    assert destination.read_bytes() == b""
    write_current_session_file(destination, SESSION, (), export_format="csv")
    assert destination.read_bytes() == (
        b'"session_id","turn_number","timestamp","user_message",'
        b'"assistant_message","model_name","total_tokens","latency_ms"\n'
    )
    write_current_session_file(
        destination,
        SESSION,
        (),
        export_format="markdown",
        user_name="User",
        assistant_name="Friday",
    )
    assert destination.read_bytes() == "# Transcript: s-α\n".encode()
    write_context_log_file(destination, SESSION, ())
    assert destination.read_bytes() == b"[]"


def test_writer_does_not_create_parent_or_accept_unsupported_format(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing"
    destination = missing / "export"
    with pytest.raises(FileNotFoundError):
        write_current_session_file(destination, SESSION, (), export_format="csv")
    with pytest.raises(FileNotFoundError):
        write_context_log_file(destination, SESSION, ())
    assert not missing.exists()
    with pytest.raises(ValueError, match="Unsupported transcript export format"):
        write_current_session_file(
            tmp_path / "unsupported",
            SESSION,
            (),
            export_format="md",
        )
    assert not (tmp_path / "unsupported").exists()


@pytest.mark.parametrize(
    ("user_name", "assistant_name"),
    [(None, "Friday"), ("User", None), (None, None)],
)
def test_markdown_requires_both_names(
    tmp_path: Path,
    user_name: str | None,
    assistant_name: str | None,
) -> None:
    destination = tmp_path / "export"
    with pytest.raises(ValueError, match="requires user and assistant names"):
        write_current_session_file(
            destination,
            SESSION,
            (),
            export_format="markdown",
            user_name=user_name,
            assistant_name=assistant_name,
        )
    assert not destination.exists()


def test_write_text_errors_propagate_with_one_utf8_call(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "export"
    calls: list[tuple[Path, str, str | None]] = []

    def fail_write(path: Path, text: str, *, encoding: str | None = None) -> int:
        calls.append((path, text, encoding))
        raise PermissionError("denied")

    monkeypatch.setattr(Path, "write_text", fail_write)
    with pytest.raises(PermissionError, match="denied"):
        write_current_session_file(destination, SESSION, (), export_format="jsonl")
    assert calls == [(destination, "", "utf-8")]
    calls.clear()
    with pytest.raises(PermissionError, match="denied"):
        write_context_log_file(destination, SESSION, ())
    assert calls == [(destination, "[]", "utf-8")]


def test_neutral_module_imports_without_chat_or_cli() -> None:
    script = (
        "import sys\n"
        "from friday_runtime import transcript_export_files\n"
        "assert not any(name.startswith(('friday_chat', 'friday_cli')) "
        "for name in sys.modules)\n"
        "assert callable(transcript_export_files.write_current_session_file)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
