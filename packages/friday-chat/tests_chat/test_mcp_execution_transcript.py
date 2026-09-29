"""Production/fake transcript and real model-continuation safety through Chat."""

from __future__ import annotations

import csv
import io
import json
import sys
from dataclasses import replace

import pytest
import test_mcp_execution_security as execution_security
from friday_chat.adapters import FrameworkTranscriptAdapter
from friday_chat.config import FridayChatConfig
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

ENVIRONMENT = "REM006_ENV_SENTINEL"
HEADER = "REM006_HEADER_SENTINEL"
LAUNCH = "REM006_LAUNCH_SENTINEL"


@pytest.mark.asyncio
@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize("fallback", [False, True])
async def test_new_session_omits_mcp_launch_material_from_every_export(
    tmp_path, processes, caplog, streaming, fallback
):
    # Headers are forbidden by the accepted stdio config. Exercise header/URL
    # copies in supported launch arguments without introducing HTTP authority.
    peer = tmp_path / (LAUNCH + ".py")
    audit = tmp_path / "launch-audit.json"
    peer.write_text(
        "import json, os, runpy, sys\n"
        f"with open(sys.argv[1], 'w') as out: json.dump({{"
        f"'env_exact': os.environ.get('REM006_ENV') == {ENVIRONMENT!r}, "
        f"'args_exact': sys.argv[2:] == {[LAUNCH, 'Authorization: ' + HEADER, 'https://synthetic.invalid/?token=' + HEADER]!r}"
        "}, out)\n"
        f"runpy.run_path({str(execution_security.PEER.resolve())!r}, run_name='__main__')\n"
    )
    values = config().model_dump()
    server = values["tools"]["providers"]["mcp"]["config"]["servers"][0]
    server.update(
        command=sys.executable,
        args=[
            str(peer),
            str(audit),
            LAUNCH,
            "Authorization: " + HEADER,
            "https://synthetic.invalid/?token=" + HEADER,
        ],
        env={"REM006_ENV": ENVIRONMENT},
    )
    values["tools"]["providers"]["native_example"] = {"shape": "preserved"}
    if fallback:
        values["tools"]["loop"] = {"max_iterations": 1}
    configuration = FridayChatConfig.model_validate(values)
    original = configuration.model_dump(mode="json")
    runtime = build_runtime(configuration)
    bridge = install(runtime, tmp_path)
    store = SQLiteTranscriptStore(tmp_path / "private.sqlite")
    runtime.transcript = FrameworkTranscriptAdapter(store, configuration, "private")
    runtime.chat_llm = FakeChatModel(
        "fake",
        responses=[
            ChatModelResponse(
                tool_calls=(
                    ToolCallRequest("mcp_peer_read_file", {"case": "success"}, "call1"),
                )
            ),
            ChatModelResponse(
                tool_calls=(ToolCallRequest("mcp_peer_read_file", {}, "pending"),)
            )
            if fallback
            else ChatModelResponse.from_text("done"),
        ],
    )
    chunks = []

    async def capture(text):
        chunks.append(text)

    try:
        await runtime.start_mcp_tools()
        runtime.tool_selection.inject_manual(("mcp_peer_read_file",))
        processor = TurnProcessor(runtime)
        result = (
            await processor.process_streaming("synthetic", on_chunk=capture)
            if streaming
            else await processor.process("synthetic")
        )
        assert json.loads(audit.read_text()) == {
            "env_exact": True,
            "args_exact": True,
        }
        assert configuration.model_dump(mode="json") == original
        assert "Read.File" in result.tool_calls[0].result
        assert result.tool_calls[0].mcp_provenance.tool.original_name == "Read.File"
        session = await store.get_session("private")
        expected = configuration.model_dump(
            mode="json", exclude={"tools": {"providers": {"mcp"}}}
        )
        assert session.config_snapshot == expected
        assert session.config_snapshot["tools"]["providers"] == {
            "native_example": {"shape": "preserved"}
        }
        entry = (await store.get_entries("private"))[0]
        assert entry.tool_calls[0].mcp_provenance.transcript_correlation_id == entry.id
        captured = repr(session) + repr(entry) + repr(result) + repr(chunks)
        captured += repr(runtime.chat_llm.calls) + caplog.text
        captured += repr(await store.get_context_log_for_session("private"))
        for exporter, options in [
            (JSONLExporter(store), {"include_metadata": True}),
            (JSONLExporter(store), {"include_metadata": False}),
            (MarkdownExporter(store), {}),
            (MarkdownExporter(store), {"include_tool_calls": True}),
            (CSVExporter(store), {}),
        ]:
            output = io.StringIO()
            await exporter.export_session("private", output, **options)
            captured += output.getvalue()
            if isinstance(exporter, JSONLExporter):
                payloads = [json.loads(line) for line in output.getvalue().splitlines()]
                assert payloads[0]["config_snapshot"] == expected
                assert ("tool_calls" in payloads[-1]) == options["include_metadata"]
        folder = tmp_path / "all-csv"
        assert await CSVExporter(store).export_all_sessions(folder) == {
            "sessions": 1,
            "entries": 1,
        }
        for path in folder.glob("*.csv"):
            captured += path.read_text()
        session_row = next(
            csv.DictReader(io.StringIO((folder / "sessions.csv").read_text()))
        )
        assert json.loads(session_row["config_snapshot"]) == expected
        assert all(s not in captured for s in (ENVIRONMENT, HEADER, LAUNCH))
        assert (
            result.assistant_message.startswith("Tool results:")
            if fallback
            else (result.assistant_message == "done")
        )
        await bridge.stop()
        assert_stopped(bridge, processes)
    finally:
        await bridge.stop()


@pytest.mark.asyncio
async def test_native_session_snapshot_shape_and_historical_snapshot_are_preserved(
    tmp_path,
):
    from friday_transcript import TranscriptSession

    configuration = FridayChatConfig.model_validate(
        {"tools": {"providers": {"native_example": {"shape": "preserved"}}}}
    )
    store = SQLiteTranscriptStore(tmp_path / "native-session.sqlite")
    adapter = FrameworkTranscriptAdapter(store, configuration, "new-native")
    turn = InteractionTurn(
        "entry1", "user", "assistant", "p", "c", (), TurnMetrics(0, 0, 0, 0)
    )
    await adapter.record_interaction(turn)
    assert (
        await store.get_session("new-native")
    ).config_snapshot == configuration.model_dump(mode="json")
    historical = TranscriptSession(
        session_id="historical",
        model_name="fake",
        config_snapshot={"tools": {"providers": {"mcp": {"env": ENVIRONMENT}}}},
    )
    await store.create_session(historical)
    await FrameworkTranscriptAdapter(
        store, configuration, "historical"
    ).record_interaction(replace(turn, turn_id="entry2"))
    assert (
        await store.get_session("historical")
    ).config_snapshot == historical.config_snapshot


@pytest.mark.asyncio
@pytest.mark.parametrize("production", [False, True])
@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize("fallback", [False, True])
async def test_later_native_claims_rebind_complete_mcp_pairs_across_iterations(
    tmp_path, processes, production, streaming, fallback
):
    runtime = build_runtime(config())
    runtime.config.tools.loop["max_iterations"] = 3
    bridge = install(runtime, tmp_path)
    store = SQLiteTranscriptStore(tmp_path / "collision.sqlite")
    if production:
        runtime.transcript = FrameworkTranscriptAdapter(store, runtime.config, "pairs")

    class LaterNativeModel(FakeChatModel):
        async def complete(self, messages, *, tools=()):
            number = len(self.calls)
            if number == 0:
                response = ChatModelResponse(
                    tool_calls=(
                        ToolCallRequest("mcp_peer_read_file", {}, "shared"),
                        ToolCallRequest("mcp_peer_read_file", {}, "stable"),
                    )
                )
            elif number == 1:
                response = ChatModelResponse(
                    tool_calls=(
                        ToolCallRequest("echo", {"text": "native one"}, "shared"),
                        ToolCallRequest("mcp_peer_read_file", {}, "shared"),
                        ToolCallRequest("mcp_peer_read_file", {}, None),
                        ToolCallRequest("mcp_peer_other_tool", {}, "bad/" + ARGUMENT),
                    )
                )
            elif number == 2:
                # Claim the replacement itself, exercising a second rebind of
                # the same completed call and repeated tool names by identity.
                identifier = messages[2]["tool_calls"][0]["id"]
                self.claimed_id = identifier
                response = ChatModelResponse(
                    tool_calls=(
                        ToolCallRequest("echo", {"text": "native two"}, identifier),
                        ToolCallRequest("mcp_peer_read_file", {}, "stable"),
                    )
                )
            elif fallback:
                response = ChatModelResponse(
                    tool_calls=(
                        ToolCallRequest("echo", {"text": "unexecuted"}, "stable"),
                        ToolCallRequest(
                            "mcp_peer_read_file", {"value": ARGUMENT}, "shared"
                        ),
                    )
                )
            else:
                response = ChatModelResponse.from_text("done")
            self.responses = [response]
            return await super().complete(messages, tools=tools)

    model = LaterNativeModel("fake")
    runtime.chat_llm = model
    chunks = []

    async def capture(text):
        chunks.append(text)

    try:
        await runtime.start_mcp_tools()
        runtime.tool_selection.inject_manual(
            ("echo", "mcp_peer_read_file", "mcp_peer_other_tool")
        )
        processor = TurnProcessor(runtime)
        result = (
            await processor.process_streaming("synthetic", on_chunk=capture)
            if streaming
            else await processor.process("synthetic")
        )
        records = result.tool_calls
        assert len(records) == 8 and len({r.call_id for r in records}) == 8
        native = [r for r in records if r.mcp_provenance is None]
        assert native[0].call_id == "shared" and native[0].result == "native one"
        assert native[1].call_id == model.claimed_id and native[1].call_id != "shared"
        assert native[1].result == "native two"
        assert (
            records[1].call_id != "stable"
            if fallback
            else records[1].call_id == "stable"
        )
        retained = model.calls[-1]
        requests = [
            c
            for m in retained
            if m.get("role") == "assistant"
            for c in m.get("tool_calls", [])
        ]
        outputs = [m for m in retained if m.get("role") == "tool"]
        assert [c["id"] for c in requests] == [r.call_id for r in records]
        assert [m["tool_call_id"] for m in outputs] == [r.call_id for r in records]
        assert [m["content"] for m in outputs] == [r.result for r in records]
        for r in records:
            if r.mcp_provenance is not None:
                assert r.call_id == r.mcp_provenance.call_id
                assert r.arguments == {} and r.mcp_provenance.status == "succeeded"
        assert ARGUMENT not in repr(result) + repr(model.calls) + repr(chunks)
        if production:
            entry = (await store.get_entries("pairs"))[0]
            assert [c.id for c in entry.tool_calls] == [r.call_id for r in records]
            for call, output in zip(entry.tool_calls, entry.tool_results, strict=True):
                if call.mcp_provenance is not None:
                    assert call.mcp_provenance == output.mcp_provenance
                    assert call.mcp_provenance.transcript_correlation_id == entry.id
            output = io.StringIO()
            await JSONLExporter(store).export_session("pairs", output)
            exported = json.loads(output.getvalue().splitlines()[-1])
            assert exported["tool_calls"] == [
                c.model_dump(mode="json") for c in entry.tool_calls
            ]
        else:
            assert runtime.transcript.interactions[0].tool_calls == records
        if fallback:
            assert result.assistant_message.startswith("Tool results:")
            assert json.loads(result.raw_response)["tool_calls"][0]["id"] == "stable"
        else:
            assert result.assistant_message == "done"
        await bridge.stop()
        assert_stopped(bridge, processes)
    finally:
        await bridge.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("production", [False, True])
@pytest.mark.parametrize("streaming", [False, True])
async def test_pending_mcp_reuse_gets_distinct_capture_id_without_execution(
    tmp_path, processes, production, streaming
):
    runtime = build_runtime(config())
    runtime.config.tools.loop["max_iterations"] = 1
    bridge = install(runtime, tmp_path)
    store = SQLiteTranscriptStore(tmp_path / "pending.sqlite")
    if production:
        runtime.transcript = FrameworkTranscriptAdapter(
            store, runtime.config, "pending"
        )
    runtime.chat_llm = FakeChatModel(
        "fake",
        responses=[
            ChatModelResponse(
                tool_calls=(ToolCallRequest("mcp_peer_read_file", {}, "shared"),)
            ),
            ChatModelResponse(
                content=ARGUMENT,
                tool_calls=(
                    ToolCallRequest(
                        "mcp_peer_read_file", {"value": ARGUMENT}, "shared"
                    ),
                    ToolCallRequest(
                        "mcp_peer_read_file", {"value": ARGUMENT}, "shared"
                    ),
                    ToolCallRequest("mcp_peer_read_file", {}, "valid-pending"),
                ),
            ),
        ],
    )
    chunks = []

    async def capture(text):
        chunks.append(text)

    try:
        await runtime.start_mcp_tools()
        runtime.tool_selection.inject_manual(("mcp_peer_read_file",))
        processor = TurnProcessor(runtime)
        result = (
            await processor.process_streaming("synthetic", on_chunk=capture)
            if streaming
            else await processor.process("synthetic")
        )
        assert len(result.tool_calls) == 1 and result.tool_calls[0].call_id == "shared"
        captured = json.loads(result.raw_response)["tool_calls"]
        assert len({c["id"] for c in captured} | {"shared"}) == 4
        assert captured[-1]["id"] == "valid-pending"
        assert all(c["arguments"] == {} for c in captured)
        assert len(runtime.chat_llm.calls) == 2
        assert result.assistant_message.startswith("Tool results:")
        assert ARGUMENT not in repr(result) + repr(chunks) + repr(
            runtime.chat_llm.calls
        )
        if production:
            entry = (await store.get_entries("pending"))[0]
            assert len(entry.tool_calls) == 1 and entry.tool_calls[0].id == "shared"
        else:
            assert runtime.transcript.interactions[0].tool_calls == result.tool_calls
        await bridge.stop()
        assert_stopped(bridge, processes)
    finally:
        await bridge.stop()


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


@pytest.mark.asyncio
async def test_optional_mcp_receipt_rejects_actual_paired_fact_readback_mismatch(tmp_path, monkeypatch):
    from friday_chat.runtime import MCPTranscriptReceipt
    cfg = config()
    store = SQLiteTranscriptStore(tmp_path / "receipt.sqlite")
    adapter = FrameworkTranscriptAdapter(store, cfg, "receipt")
    record = MCPOutputPolicy(256).checked_record(metadata(), "call", "benign", {})
    correlated = record.mcp_provenance.model_copy(update={"transcript_correlation_id": "entry"})
    turn = InteractionTurn("entry", "user", "answer", "", "", (), TurnMetrics(0,0,0,0),
                           tool_calls=(replace(record, mcp_provenance=correlated),))
    receipt = await adapter.record_mcp_interaction(turn)
    assert receipt == MCPTranscriptReceipt("entry", (correlated,))
    original = store.get_entry
    async def mismatched(entry_id):
        entry = await original(entry_id)
        changed = correlated.model_copy(update={"transcript_correlation_id": "wrong"})
        # Bypass constructor validation only to simulate corrupted persisted facts.
        entry.tool_results[0] = entry.tool_results[0].model_copy(update={"mcp_provenance": changed})
        return entry
    monkeypatch.setattr(store, "get_entry", mismatched)
    monkeypatch.setattr(adapter, "record_interaction", _receipt_noop)
    with pytest.raises(RuntimeError, match="inconsistent"):
        await adapter.record_mcp_interaction(turn)


async def _receipt_noop(turn):
    pass
