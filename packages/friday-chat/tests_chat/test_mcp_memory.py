"""Public Chat turns with real local MCP, Chroma, MemoryController and SQLite."""

from __future__ import annotations

import asyncio
import io
import json
from types import SimpleNamespace

import pytest
import test_mcp_execution_security as execution
from friday_chat.adapters import (
    FrameworkMemoryAdapter,
    FrameworkTranscriptAdapter,
    _context_payload_to_snippets,
)
from friday_chat.config import FridayChatConfig
from friday_chat.memory_mcp import persist_mcp_interaction
from friday_chat.runtime import FakeChatModel, MCPTranscriptReceipt, build_runtime
from friday_chat.tools.output import MCPOutputPolicy
from friday_chat.tools.schemas import ToolCallRecord
from friday_chat.turns.models import (
    ChatModelResponse,
    InteractionTurn,
    ToolCallRequest,
    TurnMetrics,
)
from friday_chat.turns.processor import TurnProcessor
from friday_memory import (
    CollectionManager,
    InMemoryEpisodicStore,
    MemoryController,
    NullGraphStore,
)
from friday_memory.retrieval.mcp import estimated_snippet_tokens
from friday_transcript import (
    CSVExporter,
    JSONLExporter,
    MarkdownExporter,
    SQLiteTranscriptStore,
)

processes = execution.processes


class Embeddings:
    async def embed_documents(self, texts):
        return [[1.0, 0.0, 0.0, 0.0] for _ in texts]

    async def embed_query(self, text):
        return [1.0, 0.0, 0.0, 0.0]


def setup(tmp_path, *, enabled=True, servers=("peer",), tools=(), cap=65536):
    values = execution.config().model_dump()
    values["tools"]["providers"]["mcp"]["config"]["ingestion"] = {
        "long_term_memory_enabled": enabled,
        "opted_in_servers": servers,
        "opted_in_tools": tools,
        "max_ingested_bytes": cap,
    }
    cfg = FridayChatConfig.model_validate(values)
    runtime = build_runtime(cfg)
    manager = CollectionManager(Embeddings(), path=str(tmp_path / "vectors"))
    episodic = InMemoryEpisodicStore()
    controller = MemoryController(
        manager.short_term, NullGraphStore(), episodic, manager
    )
    memory = FrameworkMemoryAdapter(
        controller, manager, cfg, "memory-session", episodic, controller.graph
    )
    runtime.memory = memory
    store = SQLiteTranscriptStore(tmp_path / "transcript.sqlite")
    runtime.transcript = FrameworkTranscriptAdapter(store, cfg, "memory-session")
    return runtime, memory, manager, store


def make_turn(identifier, *, calls):
    return InteractionTurn(
        identifier,
        "user",
        "answer",
        "",
        "",
        (),
        TurnMetrics(0, 0, 0, 0),
        tool_calls=calls,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize("enabled", [False, True])
async def test_real_peer_default_or_optin_truthful_receipts_and_exports(
    tmp_path, processes, streaming, enabled, caplog
):
    runtime, memory, manager, store = setup(tmp_path, enabled=enabled)
    bridge = execution.install(runtime, tmp_path)
    runtime.chat_llm = FakeChatModel(
        "fake",
        responses=[
            ChatModelResponse(
                tool_calls=(
                    ToolCallRequest(
                        "mcp_peer_read_file",
                        {"case": "success", "secret": execution.ARGUMENT},
                        "call-1",
                    ),
                    ToolCallRequest(
                        "mcp_peer_read_file", {"case": "success"}, "call-2"
                    ),
                )
            ),
            ChatModelResponse.from_text("Done"),
        ],
    )

    async def chunk(text):
        pass

    try:
        await runtime.start_mcp_tools()
        runtime.tool_selection.inject_manual(("mcp_peer_read_file",))
        processor = TurnProcessor(runtime)
        result = (
            await processor.process_streaming("synthetic", on_chunk=chunk)
            if streaming
            else await processor.process("synthetic")
        )
        entries = await store.get_entries("memory-session")
        assert len(entries) == 1 and len(entries[0].tool_calls) == 2
        entry = entries[0]
        assert await manager.short_term.count() == (2 if enabled else 0)
        assert len(await memory.episodic_store.get_turns("memory-session")) == 1
        for returned, call, response in zip(
            result.tool_calls, entry.tool_calls, entry.tool_results, strict=True
        ):
            assert call.mcp_provenance == response.mcp_provenance
            assert call.mcp_provenance.memory_ingested is enabled
            assert call.mcp_provenance.transcript_correlation_id == entry.id
            if enabled:
                assert returned.mcp_provenance == call.mcp_provenance
                durable = await manager.get_mcp_snapshot(
                    call.mcp_provenance.memory_correlation_id
                )
                assert (
                    durable.snapshot.call == call.mcp_provenance
                    and durable.state == "committed"
                )
                assert durable.snapshot.transcript_entry_id == entry.id
                assert (
                    execution.ARGUMENT
                    not in durable.text + durable.snapshot.encoded_provenance()
                )
            else:
                assert call.mcp_provenance.memory_correlation_id is None
        outputs = []
        for exporter, flags in (
            (JSONLExporter(store), {"include_metadata": True}),
            (JSONLExporter(store), {"include_metadata": False}),
            (MarkdownExporter(store), {"include_tool_calls": True}),
            (CSVExporter(store), {}),
        ):
            out = io.StringIO()
            await exporter.export_session("memory-session", out, **flags)
            outputs.append(out.getvalue())
        if enabled:
            exported = next(
                json.loads(line)
                for line in outputs[0].splitlines()
                if json.loads(line).get("_type") == "entry"
            )
            assert (
                exported["tool_calls"][0]["mcp_provenance"]["memory_ingested"] is True
            )
            assert "MCP snapshot" in "\n".join(
                await memory.retrieve("result", token_limit=4096)
            )
            assert "MCP snapshot" not in "\n".join(
                await memory.retrieve("result", token_limit=4096, include_mcp=False)
            )
            assert "MCP snapshot" not in "\n".join(
                await memory.retrieve("result", token_limit=0)
            )
        assert (
            execution.ARGUMENT
            not in repr(result) + repr(entries) + "".join(outputs) + caplog.text
        )
    finally:
        await bridge.stop()
    execution.assert_stopped(bridge, processes)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "servers,tools,case,cap",
    [
        (("other",), (), "success", 65536),
        ((), ("read_file",), "success", 65536),
        (("peer",), (), "unsafe", 65536),
        (("peer",), (), "error", 65536),
        (("peer",), (), "success", 100),
    ],
)
async def test_unlisted_failed_and_oversized_outputs_stay_transcript_only(
    tmp_path, processes, servers, tools, case, cap
):
    runtime, memory, manager, store = setup(
        tmp_path, servers=servers, tools=tools, cap=cap
    )
    bridge = execution.install(runtime, tmp_path)
    runtime.chat_llm = FakeChatModel(
        "fake",
        responses=[
            ChatModelResponse(
                tool_calls=(
                    ToolCallRequest("mcp_peer_read_file", {"case": case}, "call"),
                )
            ),
            ChatModelResponse.from_text("Done"),
        ],
    )
    try:
        await runtime.start_mcp_tools()
        runtime.tool_selection.inject_manual(("mcp_peer_read_file",))
        result = await TurnProcessor(runtime).process("synthetic")
        entry = (await store.get_entries("memory-session"))[0]
        assert await manager.short_term.count() == 0
        assert not result.tool_calls[0].mcp_provenance.memory_ingested
        assert entry.tool_calls[0].mcp_provenance.ingestion_decision == "skipped"
        assert execution.UNSAFE not in repr(entry)
    finally:
        await bridge.stop()
    execution.assert_stopped(bridge, processes)


@pytest.mark.asyncio
async def test_missing_optional_capability_preserves_old_adapters(tmp_path):
    runtime, memory, manager, store = setup(tmp_path)
    # The existing fake transcript deliberately has only its old mandatory API.
    legacy = build_runtime(runtime.config).transcript
    record = MCPOutputPolicy(256).checked_record(
        execution.metadata(), "call", "benign", {}
    )
    turn = make_turn("entry", calls=(record, ToolCallRecord("native", {}, "native")))
    calls = await persist_mcp_interaction(
        memory, legacy, runtime.config.tools.mcp_provider.config.ingestion, turn
    )
    assert calls[0].mcp_provenance.ingestion_decision == "skipped"
    assert calls[1] == turn.tool_calls[1] and await manager.short_term.count() == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["append", "readback", "cancel", "publish"])
async def test_partial_persistence_cannot_publish_uncorrelated_memory(
    tmp_path, monkeypatch, failure
):
    runtime, memory, manager, store = setup(tmp_path)
    record = MCPOutputPolicy(256).checked_record(
        execution.metadata(), "call", "benign", {}
    )
    turn = make_turn("entry", calls=(record,))
    original = runtime.transcript.record_mcp_interaction
    if failure == "append":

        async def append(entry):
            return False

        monkeypatch.setattr(store, "append_entry", append)
    elif failure == "readback":

        async def wrong(turn):
            await original(turn)
            return MCPTranscriptReceipt("wrong", ())

        monkeypatch.setattr(runtime.transcript, "record_mcp_interaction", wrong)
    elif failure == "cancel":

        async def interrupted(turn):
            await original(turn)
            raise asyncio.CancelledError()

        monkeypatch.setattr(runtime.transcript, "record_mcp_interaction", interrupted)
    else:

        async def false(snapshot):
            return False

        monkeypatch.setattr(memory, "publish_mcp_memory", false)
    if failure == "publish":
        calls = await persist_mcp_interaction(
            memory,
            runtime.transcript,
            runtime.config.tools.mcp_provider.config.ingestion,
            turn,
        )
        assert calls[0].mcp_provenance.memory_ingested
    else:
        with pytest.raises((RuntimeError, asyncio.CancelledError)):
            await persist_mcp_interaction(
                memory,
                runtime.transcript,
                runtime.config.tools.mcp_provider.config.ingestion,
                turn,
            )
    records = await manager.get_all()
    assert len(records) == 1 and records[0]["metadata"]["mcp_state"] == "pending"
    assert not (await manager.query("result"))["short_term"]
    if failure != "append":
        entry = await store.get_entry("entry")
        assert (
            entry.tool_calls[0].mcp_provenance.memory_correlation_id == records[0]["id"]
        )


@pytest.mark.asyncio
async def test_concurrent_turns_and_budget_forwarding(tmp_path, monkeypatch):
    runtime, memory, manager, store = setup(tmp_path)
    record = MCPOutputPolicy(256).checked_record(
        execution.metadata(), "call", "benign", {}
    )
    # Different owned turn IDs may share call names and call IDs without sharing storage.
    turns = [make_turn(f"entry-{i}", calls=(record,)) for i in range(2)]
    await asyncio.gather(
        *(
            persist_mcp_interaction(
                memory,
                runtime.transcript,
                runtime.config.tools.mcp_provider.config.ingestion,
                t,
            )
            for t in turns
        )
    )
    rows = await manager.get_all()
    assert len(rows) == 2 and len({r["id"] for r in rows}) == 2
    calls = []
    original = memory.controller.recall

    async def spy(*args, **kwargs):
        calls.append(kwargs["token_limit"])
        return await original(*args, **kwargs)

    monkeypatch.setattr(memory.controller, "recall", spy)
    await memory.retrieve("result", token_limit=777)
    await memory.retrieve("result", token_limit=0)
    assert calls == [777, 0]
    assert {r["metadata"]["mcp_state"] for r in rows} == {"committed"}


@pytest.mark.asyncio
async def test_labels_fit_residual_budget_and_cannot_be_lost(tmp_path):
    runtime, memory, manager, store = setup(tmp_path)
    call = MCPOutputPolicy(256).checked_record(
        execution.metadata(), "call", "benign", {}
    )
    prepared = await memory.prepare_mcp_memory(
        call, "entry", runtime.config.tools.mcp_provider.config.ingestion
    )
    await memory.publish_mcp_memory(prepared.snapshot)
    record = await manager.short_term.get_by_id(prepared.snapshot.record_id)
    payload = SimpleNamespace(
        passages=[{"text": "native", "metadata": {}}, record],
        insights=[],
        summaries=[],
        history=[],
        recent_memories=[],
    )
    cost = estimated_snippet_tokens("native") + estimated_snippet_tokens(record["text"])
    assert _context_payload_to_snippets(payload, token_limit=cost) == [
        "native",
        record["text"],
    ]
    assert _context_payload_to_snippets(payload, token_limit=cost - 1) == ["native"]
    assert _context_payload_to_snippets(payload, include_mcp=False) == ["native"]
    assert _context_payload_to_snippets(payload, token_limit=0) == ["native"]
