"""Production/fake transcript and real model-continuation safety through Chat."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import replace

import pytest
import test_mcp_execution_security as execution_security
from friday_chat.adapters import FrameworkTranscriptAdapter
from friday_chat.runtime import FakeChatModel, build_runtime
from friday_chat.tools.output import MCPOutputPolicy
from friday_chat.tools.schemas import ToolCallRecord
from friday_chat.turns.models import (
    ChatModelResponse,
    InteractionTurn,
    ToolCallRequest,
    TurnMetrics,
)
from friday_chat.turns.processor import TurnProcessor
from friday_transcript import (
    CSVExporter,
    JSONLExporter,
    MarkdownExporter,
    SQLiteTranscriptStore,
)
from test_mcp_execution_security import (
    ARGUMENT,
    ERROR,
    UNSAFE,
    assert_stopped,
    config,
    install,
    metadata,
)

processes = execution_security.processes


@pytest.mark.asyncio
@pytest.mark.parametrize("production", [False, True])
@pytest.mark.parametrize("streaming", [False, True])
async def test_mixed_repeated_calls_safe_continuation_ids_and_storage(
    tmp_path, processes, production, streaming
):
    runtime = build_runtime(config())
    bridge = install(runtime, tmp_path)
    store = SQLiteTranscriptStore(tmp_path / "transcript.sqlite")
    if production:
        runtime.transcript = FrameworkTranscriptAdapter(
            store, runtime.config, "session1"
        )
    try:
        await runtime.start_mcp_tools()
        runtime.tool_selection.inject_manual(
            ("echo", "mcp_peer_read_file", "mcp_peer_other_tool")
        )
        model = FakeChatModel(
            "fake",
            responses=[
                ChatModelResponse(
                    content=ARGUMENT,
                    reasoning_content=ARGUMENT,
                    raw_response={"unsafe": ARGUMENT},
                    tool_calls=(
                        ToolCallRequest(
                            "mcp_peer_read_file",
                            {"case": "echo", "value": ARGUMENT},
                            "shared",
                        ),
                        ToolCallRequest("echo", {"text": "native literal"}, "shared"),
                        ToolCallRequest(
                            "mcp_peer_other_tool",
                            {"case": "error", "value": ARGUMENT},
                            "shared",
                        ),
                        ToolCallRequest(
                            "mcp_peer_read_file",
                            {"case": "large", "value": ARGUMENT},
                            None,
                        ),
                    ),
                ),
                ChatModelResponse.from_text("done"),
            ],
        )
        runtime.chat_llm = model
        chunks = []

        async def capture(text):
            chunks.append(text)

        processor = TurnProcessor(runtime)
        result = (
            await processor.process_streaming("fixture", on_chunk=capture)
            if streaming
            else await processor.process("fixture")
        )
        mcp = [c for c in result.tool_calls if c.mcp_provenance is not None]
        native = [c for c in result.tool_calls if c.mcp_provenance is None]
        assert len(mcp) == 3 and len(native) == 1
        assert len({c.call_id for c in result.tool_calls}) == 4
        assert native[0].call_id == "shared" and native[0].arguments == {
            "text": "native literal"
        }
        assert native[0].result == "native literal"
        assert [c.mcp_provenance.status for c in mcp] == [
            "succeeded",
            "failed",
            "succeeded",
        ]
        assert mcp[-1].mcp_provenance.result_truncated
        continuation = model.calls[1]
        assistant = continuation[2]
        assert assistant["content"] == "" and "reasoning_content" not in assistant
        assert [c["id"] for c in assistant["tool_calls"]] == [
            c.call_id for c in result.tool_calls
        ]
        assert [m["tool_call_id"] for m in continuation[3:]] == [
            c.call_id for c in result.tool_calls
        ]
        all_capture = repr(result) + repr(model.calls)
        if production:
            entries = await store.get_entries("session1")
            assert len(entries) == 1 and len(entries[0].tool_calls) == 4
            entry = entries[0]
            for call, output in zip(entry.tool_calls, entry.tool_results, strict=True):
                if call.mcp_provenance is not None:
                    assert (
                        call.arguments == {}
                        and output.mcp_provenance == call.mcp_provenance
                    )
                    assert call.mcp_provenance.transcript_correlation_id == entry.id
            logs = await store.get_context_log_for_session("session1")
            assert len(logs) == 1 and logs[0].entry_id == entry.id
            for exporter in [
                JSONLExporter(store),
                MarkdownExporter(store),
                CSVExporter(store),
            ]:
                output = io.StringIO()
                await exporter.export_session("session1", output)
                all_capture += output.getvalue()
            all_capture += repr(logs) + repr(entry)
        else:
            all_capture += repr(runtime.transcript.interactions) + repr(
                runtime.transcript.context_logs
            )
            assert runtime.transcript.interactions[0].tool_calls == result.tool_calls
        assert all(s not in all_capture for s in (ARGUMENT, ERROR, UNSAFE))
        assert all(
            c.arguments == {} and c.mcp_provenance.ingestion_decision == "disabled"
            for c in mcp
        )
        assert all(c.mcp_provenance.transcript_correlation_id is None for c in mcp)
        assert chunks == ["done"] if streaming else chunks == []
        await bridge.stop()
        assert_stopped(bridge, processes)
    finally:
        await bridge.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize("text_call", [False, True])
async def test_exhausted_pending_and_text_parsed_requests_cannot_leak(
    tmp_path, processes, streaming, text_call
):
    values = config().model_dump()
    values["tools"]["loop"] = {"max_iterations": 1}
    from friday_chat.config import FridayChatConfig

    runtime = build_runtime(FridayChatConfig.model_validate(values))
    bridge = install(runtime, tmp_path)
    try:
        await runtime.start_mcp_tools()
        runtime.tool_selection.inject_manual(("mcp_peer_read_file",))
        first = (
            ChatModelResponse.from_text(f'mcp_peer_read_file(value="{ARGUMENT}")')
            if text_call
            else ChatModelResponse(
                content=ARGUMENT,
                tool_calls=(
                    ToolCallRequest("mcp_peer_read_file", {"value": ARGUMENT}, "call1"),
                ),
            )
        )
        # Last response is still a pending request, never executed a second time.
        runtime.chat_llm = FakeChatModel(
            "fake",
            responses=[
                first,
                ChatModelResponse(
                    content=ARGUMENT,
                    tool_calls=(
                        ToolCallRequest(
                            "mcp_peer_read_file", {"value": ARGUMENT}, "bad/" + ARGUMENT
                        ),
                    ),
                ),
            ],
        )
        chunks = []

        async def capture(text):
            chunks.append(text)

        processor = TurnProcessor(runtime)
        result = (
            await processor.process_streaming("fixture", on_chunk=capture)
            if streaming
            else await processor.process("fixture")
        )
        assert len(result.tool_calls) == 1
        assert result.assistant_message.startswith("Tool results:")
        assert ARGUMENT not in repr(result) + repr(runtime.chat_llm.calls) + repr(
            runtime.transcript.interactions
        ) + repr(chunks)
        raw = json.loads(result.raw_response)
        assert raw["content"] == "" and raw["tool_calls"][0]["arguments"] == {}
    finally:
        await bridge.stop()
    assert_stopped(bridge, processes)


@pytest.mark.asyncio
async def test_ids_remain_unique_across_tool_loop_iterations(tmp_path, processes):
    runtime = build_runtime(config())
    bridge = install(runtime, tmp_path)
    try:
        await runtime.start_mcp_tools()
        runtime.tool_selection.inject_manual(("mcp_peer_read_file",))
        response = ChatModelResponse(
            tool_calls=(ToolCallRequest("mcp_peer_read_file", {}, "repeated"),)
        )
        runtime.chat_llm = FakeChatModel(
            "fake", responses=[response, response, ChatModelResponse.from_text("done")]
        )
        result = await TurnProcessor(runtime).process("fixture")
        assert (
            len(result.tool_calls) == 2
            and len({c.call_id for c in result.tool_calls}) == 2
        )
        assert result.tool_calls[0].call_id == "repeated"
    finally:
        await bridge.stop()
    assert_stopped(bridge, processes)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "change",
    [
        "raw_arguments",
        "bad_id",
        "unchecked",
        "wrong_size",
        "wrong_correlation",
        "bad_entry",
    ],
)
async def test_production_adapter_rejects_unsafe_facts_before_store(tmp_path, change):
    store = SQLiteTranscriptStore(tmp_path / "reject.sqlite")
    adapter = FrameworkTranscriptAdapter(store, config(), "session1")
    record = MCPOutputPolicy(256).checked_record(metadata(), "call1", "benign", {})
    turn_id = "entry1"
    if change == "raw_arguments":
        record = replace(record, arguments={"secret": ARGUMENT})
    if change == "bad_id":
        record = replace(record, call_id="other")
    if change == "unchecked":
        record = replace(
            record,
            mcp_provenance=record.mcp_provenance.model_copy(
                update={"output_sanitization_state": "not_checked"}
            ),
        )
    if change == "wrong_size":
        record = replace(
            record,
            mcp_provenance=record.mcp_provenance.model_copy(
                update={"model_result_size_bytes": 1}
            ),
        )
    if change == "wrong_correlation":
        record = replace(
            record,
            mcp_provenance=record.mcp_provenance.model_copy(
                update={"transcript_correlation_id": "other"}
            ),
        )
    if change == "bad_entry":
        turn_id = "invalid/" + ARGUMENT
    turn = InteractionTurn(
        turn_id,
        "fixture",
        "done",
        "fixture",
        "",
        (),
        TurnMetrics(0, 0, 0, 0),
        tool_calls=(record,),
    )
    with pytest.raises(ValueError) as caught:
        await adapter.record_interaction(turn)
    assert ARGUMENT not in str(caught.value)
    assert await store.get_entries("session1") == []


@pytest.mark.asyncio
async def test_native_legacy_adapter_shape_and_export_controls(tmp_path):
    store = SQLiteTranscriptStore(tmp_path / "native.sqlite")
    adapter = FrameworkTranscriptAdapter(store, config(), "session1")
    call = ToolCallRecord(
        "echo", {"text": "native input"}, "native result", "legacy/native-id"
    )
    await adapter.record_interaction(
        InteractionTurn(
            "legacy/entry",
            "user",
            "assistant",
            "p",
            "c",
            (),
            TurnMetrics(0, 0, 0, 0),
            tool_calls=(call,),
        )
    )
    entry = (await store.get_entries("session1"))[0]
    assert entry.tool_calls[0].model_dump() == {
        "id": "legacy/native-id",
        "name": "echo",
        "arguments": {"text": "native input"},
    }
    assert entry.tool_results[0].model_dump() == {
        "tool_call_id": "legacy/native-id",
        "output": "native result",
        "error": None,
    }
    out = io.StringIO()
    await JSONLExporter(store).export_session("session1", out, include_metadata=False)
    payload = json.loads(out.getvalue().splitlines()[-1])
    assert "tool_calls" not in payload
    out = io.StringIO()
    await MarkdownExporter(store).export_session(
        "session1", out, include_tool_calls=True
    )
    assert "native input" in out.getvalue() and "native result" in out.getvalue()
    out = io.StringIO()
    await CSVExporter(store).export_session("session1", out)
    row = list(csv.DictReader(io.StringIO(out.getvalue())))[0]
    assert json.loads(row["tool_calls"]) == [entry.tool_calls[0].model_dump()]


@pytest.mark.asyncio
async def test_mcp_capture_policy_survives_public_stop_during_memory_await(
    tmp_path, processes, monkeypatch
):
    runtime = build_runtime(config())
    bridge = install(runtime, tmp_path)
    await runtime.start_mcp_tools()
    runtime.tool_selection.inject_manual(("mcp_peer_read_file",))
    original = runtime.memory.retrieve

    async def stop_before_model(query, *, token_limit):
        await bridge.stop()
        return await original(query, token_limit=token_limit)

    monkeypatch.setattr(runtime.memory, "retrieve", stop_before_model)
    runtime.chat_llm = FakeChatModel(
        "fake",
        responses=[
            ChatModelResponse(
                content=ARGUMENT,
                tool_calls=(
                    ToolCallRequest(
                        "mcp_peer_read_file", {"value": ARGUMENT}, "bad/" + ARGUMENT
                    ),
                ),
            )
        ],
    )
    try:
        result = await TurnProcessor(runtime).process("fixture")
        assert result.tool_calls == ()  # Nothing executed after the public stop.
        assert ARGUMENT not in repr(result) + repr(
            runtime.transcript.context_logs
        ) + repr(runtime.transcript.interactions)
        assert json.loads(result.raw_response)["tool_calls"][0]["arguments"] == {}
    finally:
        await bridge.stop()
    assert_stopped(bridge, processes)


@pytest.mark.asyncio
async def test_tiny_result_limit_is_safe_turn_error_before_execution_or_persistence(
    tmp_path, processes, monkeypatch
):
    from friday_chat.turns.processor import TurnProcessingError

    runtime = build_runtime(config(1))
    bridge = install(runtime, tmp_path)
    requests = []
    try:
        await runtime.start_mcp_tools()
        runtime.tool_selection.inject_manual(("mcp_peer_read_file",))
        original = bridge.registry.get_callable

        def track(name):
            requests.append(name)
            return original(name)

        monkeypatch.setattr(bridge.registry, "get_callable", track)
        runtime.chat_llm = FakeChatModel(
            "fake",
            responses=[
                ChatModelResponse(
                    content=ARGUMENT,
                    tool_calls=(
                        ToolCallRequest(
                            "mcp_peer_read_file", {"value": ARGUMENT}, "call1"
                        ),
                    ),
                )
            ],
        )
        with pytest.raises(TurnProcessingError, match="too small") as caught:
            await TurnProcessor(runtime).process("fixture")
        assert ARGUMENT not in str(caught.value) and requests == []
        assert (
            runtime.transcript.interactions == []
            and runtime.transcript.context_logs == []
        )
        assert runtime.memory.stored_turns == []
    finally:
        await bridge.stop()
    assert_stopped(bridge, processes)
