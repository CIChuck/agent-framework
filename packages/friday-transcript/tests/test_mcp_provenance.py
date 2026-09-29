"""Typed additive MCP records and safe JSONL/Markdown/CSV export contracts."""

import csv
import io
import json

import pytest
from friday_core.mcp import (
    MCPToolCallProvenance,
    MCPToolMetadata,
    normalize_mcp_tool_name,
)
from friday_transcript import (
    CSVExporter,
    JSONLExporter,
    MarkdownExporter,
    SQLiteTranscriptStore,
    ToolCall,
    ToolResult,
    TranscriptEntry,
    TranscriptSession,
)
from pydantic import ValidationError


def facts(original="Read.File", server="peer", **changes):
    metadata = MCPToolMetadata(
        canonical_name=normalize_mcp_tool_name(server, original),
        server_name=server,
        original_name=original,
        transport="stdio",
        trust_level="local",
    )
    return MCPToolCallProvenance(
        tool=metadata,
        status="succeeded",
        call_id="call1",
        output_sanitization_state="sanitized",
        result_size_bytes=8,
        model_result_size_bytes=8,
        **changes,
    )


def test_optional_mcp_fields_absent_from_old_native_serialization():
    call = ToolCall(id="native/id", name="echo", arguments={"value": "native"})
    result = ToolResult(tool_call_id="native/id", output={"native": True})
    assert call.model_dump() == {
        "id": "native/id",
        "name": "echo",
        "arguments": {"value": "native"},
    }
    assert result.model_dump() == {
        "tool_call_id": "native/id",
        "output": {"native": True},
        "error": None,
    }
    assert ToolCall.model_validate_json(call.model_dump_json()) == call
    assert ToolResult.model_validate_json(result.model_dump_json()) == result


@pytest.mark.parametrize(
    "kind",
    [
        "raw_arguments",
        "wrong_name",
        "wrong_id",
        "raw_error",
        "raw_output",
        "wrong_size",
        "unchecked",
    ],
)
def test_mcp_models_reject_uncorrelated_or_unchecked_payload_without_error_leak(kind):
    provenance = facts()
    call = dict(
        id="call1",
        name=provenance.tool.canonical_name,
        arguments={},
        mcp_provenance=provenance,
    )
    result = dict(tool_call_id="call1", output="safe-mcp", mcp_provenance=provenance)
    if kind == "raw_arguments":
        call["arguments"] = {"secret": "WS05_SECRET"}
    if kind == "wrong_name":
        call["name"] = "WS05_SECRET"
    if kind == "wrong_id":
        result["tool_call_id"] = "WS05_SECRET"
    if kind == "raw_error":
        result["error"] = "WS05_SECRET"
    if kind == "raw_output":
        result["output"] = {"secret": "WS05_SECRET"}
    if kind == "wrong_size":
        result["output"] = "WS05_SECRET"
    if kind == "unchecked":
        result["mcp_provenance"] = provenance.model_copy(
            update={"output_sanitization_state": "not_checked"}
        )
    with pytest.raises(ValidationError) as caught:
        if kind in ("raw_arguments", "wrong_name"):
            ToolCall(**call)
        else:
            ToolResult(**result)
    assert "WS05_SECRET" not in str(caught.value)


@pytest.mark.asyncio
async def test_typed_sqlite_roundtrip_full_jsonl_flags_and_bounded_safe_human_exports(
    tmp_path,
):
    store = SQLiteTranscriptStore(tmp_path / "transcript.sqlite")
    await store.create_session(
        TranscriptSession(session_id="session1", model_name="fake")
    )
    provenance = facts(original="Read`<File>", server="=Unsafe Server")
    call = ToolCall(
        id="call1",
        name=provenance.tool.canonical_name,
        arguments={},
        mcp_provenance=provenance,
    )
    result = ToolResult(
        tool_call_id="call1", output="safe-mcp", mcp_provenance=provenance
    )
    entry = TranscriptEntry(
        id="entry1",
        session_id="session1",
        turn_number=1,
        tool_calls=[call],
        tool_results=[result],
    )
    assert await store.append_entry(entry)
    restored = (await store.get_entries("session1"))[0]
    assert restored.tool_calls[0].mcp_provenance == provenance
    assert restored.tool_results[0].mcp_provenance == provenance
    full = io.StringIO()
    await JSONLExporter(store).export_session("session1", full)
    parsed = json.loads(full.getvalue().splitlines()[-1])
    assert (
        parsed["tool_calls"][0]["mcp_provenance"]["tool"]["original_name"]
        == "Read`<File>"
    )
    assert parsed["tool_results"][0]["mcp_provenance"]["model_result_size_bytes"] == 8
    reduced = io.StringIO()
    await JSONLExporter(store).export_session(
        "session1", reduced, include_metadata=False
    )
    assert "tool_calls" not in json.loads(reduced.getvalue().splitlines()[-1])
    hidden = io.StringIO()
    await MarkdownExporter(store).export_session("session1", hidden)
    assert "MCP:" not in hidden.getvalue()
    md = io.StringIO()
    await MarkdownExporter(store).export_session(
        "session1", md, include_tool_calls=True
    )
    assert "MCP:" in md.getvalue() and "safe\\-mcp" in md.getvalue()
    assert "Read`<File>" not in md.getvalue() and "=Unsafe Server" not in md.getvalue()
    csv_output = io.StringIO()
    exporter = CSVExporter(store)
    await exporter.export_session("session1", csv_output)
    reader = csv.DictReader(io.StringIO(csv_output.getvalue()))
    assert reader.fieldnames == exporter._entry_fieldnames()
    row = next(reader)
    summary = json.loads(row["tool_calls"])[0]["mcp_provenance"]
    assert summary["status"] == "succeeded" and summary["server"].startswith(
        "mcp-server-"
    )
    assert (
        "original_name" not in row["tool_calls"]
        and "Read`<File>" not in row["tool_calls"]
    )
    assert json.loads(row["tool_results"])[0]["output"] == "safe-mcp"


@pytest.mark.asyncio
async def test_human_mcp_result_previews_escape_markup_control_and_bound_content(
    tmp_path,
):
    store = SQLiteTranscriptStore(tmp_path / "markup.sqlite")
    await store.create_session(
        TranscriptSession(session_id="session1", model_name="fake")
    )
    text = "</x>\x00\n[link](javascript:bad)`=SUM(1) " + "é" * 1000
    provenance = facts().model_copy(
        update={"model_result_size_bytes": len(text.encode())}
    )
    await store.append_entry(
        TranscriptEntry(
            id="entry1",
            session_id="session1",
            turn_number=1,
            tool_calls=[
                ToolCall(
                    id="call1",
                    name=provenance.tool.canonical_name,
                    mcp_provenance=provenance,
                )
            ],
            tool_results=[
                ToolResult(tool_call_id="call1", output=text, mcp_provenance=provenance)
            ],
        )
    )
    output = io.StringIO()
    await MarkdownExporter(store).export_session(
        "session1", output, include_tool_calls=True
    )
    assert (
        "</x>" not in output.getvalue()
        and "[link](" not in output.getvalue()
        and "\x00" not in output.getvalue()
    )
    assert len(output.getvalue()) < 1600
    output = io.StringIO()
    await CSVExporter(store).export_session("session1", output)
    row = next(csv.DictReader(io.StringIO(output.getvalue())))
    assert (
        row["tool_results"].startswith("[")
        and len(json.loads(row["tool_results"])[0]["output"]) <= 203
    )


@pytest.mark.parametrize(
    "invalid", ["entry_id", "correlation", "unpaired", "mismatch", "duplicate_native"]
)
def test_entry_rejects_invalid_mcp_correlations_and_unpaired_facts(invalid):
    provenance = facts(transcript_correlation_id="entry1")
    call = ToolCall(
        id="call1", name=provenance.tool.canonical_name, mcp_provenance=provenance
    )
    result = ToolResult(
        tool_call_id="call1", output="safe-mcp", mcp_provenance=provenance
    )
    entry_id = "entry1"
    calls = [call]
    results = [result]
    if invalid == "entry_id":
        entry_id = "unsafe/WS05_SECRET"
    if invalid == "correlation":
        entry_id = "entry2"
    if invalid == "unpaired":
        results = []
    if invalid == "mismatch":
        results = [
            ToolResult(
                tool_call_id="call1",
                output="safe-mcp",
                mcp_provenance=provenance.model_copy(update={"result_size_bytes": 10}),
            )
        ]
    if invalid == "duplicate_native":
        calls.append(ToolCall(id="call1", name="native"))
    with pytest.raises(ValidationError) as caught:
        TranscriptEntry(
            id=entry_id,
            session_id="session1",
            turn_number=1,
            tool_calls=calls,
            tool_results=results,
        )
    assert "WS05_SECRET" not in str(caught.value)


@pytest.mark.asyncio
async def test_ingested_snapshot_receipt_roundtrips_existing_schema_and_privacy_flags(tmp_path):
    store = SQLiteTranscriptStore(tmp_path / "ingested.sqlite")
    await store.create_session(TranscriptSession(session_id="ingested", model_name="fake"))
    provenance = facts(memory_ingested=True, ingestion_decision="ingested",
                       memory_correlation_id="memory-record", transcript_correlation_id="entry")
    entry = TranscriptEntry(id="entry", session_id="ingested", turn_number=1,
        tool_calls=[ToolCall(id="call1", name=provenance.tool.canonical_name, arguments={}, mcp_provenance=provenance)],
        tool_results=[ToolResult(tool_call_id="call1", output="safe-mcp", mcp_provenance=provenance)])
    assert await store.append_entry(entry)
    loaded = await store.get_entry("entry")
    assert loaded.tool_calls[0].mcp_provenance == loaded.tool_results[0].mcp_provenance == provenance
    for enabled in (True, False):
        output = io.StringIO()
        await JSONLExporter(store).export_session("ingested", output, include_metadata=enabled)
        rows = [json.loads(row) for row in output.getvalue().splitlines()]
        row = next(r for r in rows if r["_type"] == "entry")
        if enabled:
            assert row["tool_calls"][0]["mcp_provenance"]["memory_correlation_id"] == "memory-record"
        else:
            assert "tool_calls" not in row
