# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Tests for quarantine storage."""

from friday_core.security import QuarantineStore


def test_quarantine_store_appends_jsonl(tmp_path):
    path = tmp_path / "quarantine.jsonl"
    store = QuarantineStore(path)

    store.append(
        content="raw content",
        tool_name="web_reader",
        tool_category="web",
        risk_level="critical",
        detected_patterns=["ignore_instructions"],
        metadata={"session_id": "test"},
    )

    lines = path.read_text().splitlines()
    assert len(lines) == 1
    assert "web_reader" in lines[0]
