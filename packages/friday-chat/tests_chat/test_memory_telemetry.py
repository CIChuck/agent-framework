import asyncio
from contextlib import suppress
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from friday_chat.adapters import FrameworkMaintenanceAdapter, FrameworkMemoryAdapter
from friday_chat.background import BackgroundTaskManager, BackgroundWorkCoordinator
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import (
    FakeMemoryController,
    FakeTranscriptStore,
    MCPTranscriptReceipt,
    PendingExtractionTurn,
    build_runtime,
)
from friday_chat.telemetry import ChatTelemetryObserver
from friday_chat.tools.output import MCPOutputPolicy
from friday_chat.turns.processor import TurnProcessor
from friday_chat.turns.telemetry import turn_scope
from friday_core.mcp import MCPIngestionPolicy, MCPToolCallProvenance, MCPToolMetadata
from friday_memory import ExtractionCommitCompletedUnderCancellation
from friday_memory.models.mcp import MCPMemoryPreparation, MCPMemorySnapshot


def config():
    return FridayChatConfig.model_validate({"llm": {"model": "fake/test"}, "tools": {"enabled": False},
        "telemetry": {"enabled": True}, "extraction": {"interval": -1}})


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["success", "failure", "cancel", "committed_cancel", "none"])
async def test_mixed_origins_and_existing_requeue_truth(mode):
    o = ChatTelemetryObserver(enabled=True, session_id="private")
    origins = [o.correlation.context(turn=True), o.correlation.context(turn=True)]
    seen = []
    class Extractor:
        async def extract(self, turn):
            seen.append(o.correlation.current().context.turn_ref)
            if len(seen) == 1:
                if mode == "failure":
                    raise RuntimeError("PRIVATE_FAILURE")
                if mode == "cancel":
                    raise asyncio.CancelledError()
                if mode == "committed_cancel":
                    raise ExtractionCommitCompletedUnderCancellation()
            return {}
    adapter = FrameworkMaintenanceAdapter(config(), "private", None, None, None, {}, {},
        extractor=None if mode == "none" else Extractor(), observer=o)
    adapter.pending_extraction = [PendingExtractionTurn(str(i), "PRIVATE_U", "PRIVATE_A", origin) for i, origin in enumerate(origins)]
    with suppress(RuntimeError, asyncio.CancelledError):
        await adapter.extract_buffered_turns(trigger_reason="safe")
    if mode in {"success", "none"}:
        assert not adapter.pending_extraction
    else:
        assert [t.turn_id for t in adapter.pending_extraction] == (["1"] if mode == "committed_cancel" else ["0", "1"])
    finishes = [dict(e.attributes) for e in o.snapshot().events if e.name == "execution.operation_finish"]
    assert finishes[0]["turn_ref"] == origins[0].turn_ref
    if mode == "committed_cancel":
        assert finishes[0]["outcome"] == "cancelled" and finishes[0]["persistence_state"] == "completed"
    elif mode == "none":
        assert all(e["outcome"] == "skipped" and e["count"] == 0 for e in finishes)
    elif mode == "success":
        assert [e["turn_ref"] for e in finishes] == [c.turn_ref for c in origins]
    assert o.correlation.current() is None and not o._spans
    assert "PRIVATE_U" not in repr(o.snapshot())


@pytest.mark.asyncio
async def test_ingestion_count_and_background_handoff():
    r = build_runtime(config())
    result = await TurnProcessor(r).process("safe")
    manager = BackgroundTaskManager()
    coordinator = BackgroundWorkCoordinator(r, manager)
    coordinator.schedule_after_turn(turn_count=1, user_message="private", assistant_message="private", correlation_context=result.correlation_context)
    assert r.maintenance.pending_extraction[0].correlation_context is result.correlation_context
    observed = []
    async def background():
        observed.append(r.telemetry.correlation.current())
    with turn_scope(r.telemetry, "completion"):
        await coordinator._run_shared("synthetic", background)
        assert r.telemetry.correlation.current() is not None
    assert observed == [None]
    await manager.close()
    class Controller:
        async def store_document(self, *args, **kwargs):
            return None
    a = FrameworkMemoryAdapter(Controller(), None, config(), "private", None, None, observer=r.telemetry)
    assert await a.ingest_document(source_path="PRIVATE_PATH", description="PRIVATE", content="PRIVATE_DOC") == 1
    finish = next(dict(e.attributes) for e in reversed(r.telemetry.snapshot().events)
                  if e.name == "execution.operation_finish")
    assert finish["count"] == 1 and "turn_ref" not in finish
    assert "PRIVATE_PATH" not in repr(r.telemetry.snapshot())


@pytest.mark.asyncio
@pytest.mark.parametrize("published", [False, True])
async def test_actual_mcp_receipt_is_distinct_from_publication(published):
    values = config().model_dump()
    values["tools"]["providers"] = {"mcp": {"enabled": False, "config": {"ingestion": {
        "long_term_memory_enabled": True, "opted_in_servers": ["peer"]}}}}
    r = build_runtime(FridayChatConfig.model_validate(values))
    policy = MCPIngestionPolicy(long_term_memory_enabled=True, opted_in_servers=("peer",))
    class Memory(FakeMemoryController):
        async def prepare_mcp_memory(self, call, entry, supplied_policy):
            facts = MCPToolCallProvenance.model_validate({**call.mcp_provenance.model_dump(),
                "memory_ingested": True, "ingestion_decision": "ingested", "memory_correlation_id": "record",
                "transcript_correlation_id": entry})
            snapshot = MCPMemorySnapshot(record_id="record", transcript_entry_id=entry, call=facts,
                policy=policy, matched_grant="server", memory_sanitization="unchanged",
                stored_size_bytes=4, captured_at=datetime.now(UTC))
            return MCPMemoryPreparation("prepared", snapshot)
        async def publish_mcp_memory(self, snapshot):
            return published
        async def discard_mcp_memory(self, snapshot):
            return True
    class Transcript(FakeTranscriptStore):
        async def record_mcp_interaction(self, turn):
            return MCPTranscriptReceipt(turn.turn_id, tuple(c.mcp_provenance for c in turn.tool_calls))
    r.memory = Memory()
    r.transcript = Transcript()
    def emit(kind, *, tool_name, reason):
        r.telemetry.capture_event("mcp." + kind, {"tool_ref": "a" * 16, "reason": reason})
    r.mcp_tools = SimpleNamespace(provider=SimpleNamespace(emit_event=emit))
    metadata = MCPToolMetadata(canonical_name="mcp_peer_private", server_name="peer", original_name="private", transport="stdio", trust_level="local")
    call = MCPOutputPolicy(4096).checked_record(metadata, "call", "safe", {})
    with turn_scope(r.telemetry, "completion"):
        _, calls = await TurnProcessor(r)._persist_turn(user_message="private", assistant_message="private", prompt_text="private",
            context_text="private", memories=[], tool_calls=(call,), retrieval_seconds=0.0, llm_seconds=0.0, total_start=0.0, raw_response="private")
    assert calls[0].mcp_provenance.transcript_correlation_id is not None
    links = [dict(e.attributes) for e in r.telemetry.snapshot().events if e.name == "execution.mcp_link"]
    assert links[-1]["reason"] == ("published" if published else "pending")
    assert r.telemetry.execution_snapshot().turns[-1].persistence == "completed"


@pytest.mark.asyncio
async def test_empty_extraction_is_skipped():
    observer = ChatTelemetryObserver(enabled=True, session_id="private")
    adapter = FrameworkMaintenanceAdapter(config(), "private", None, None, None, {}, {}, observer=observer)
    assert await adapter.extract_buffered_turns(trigger_reason="private") == 0
    assert await adapter.flush_pending_extraction() == 0
    finishes = [dict(e.attributes) for e in observer.snapshot().events if e.name == "execution.operation_finish"]
    assert len(finishes) == 2
    assert all(e["outcome"] == "skipped" and e["count"] == 0 and "persistence_state" not in e for e in finishes)
    assert not observer.execution_snapshot().turns


class ContextSink:
    """Fake sink models the accepted immutable task-local logical span stack."""
    def __init__(self):
        from contextvars import ContextVar
        self.stack = ContextVar("fake_sink_stack", default=())
        self.spans = {}
        self.events = []
    def start_span(self, name, parent_id=None):
        stack = tuple(x for x in self.stack.get() if not self.spans[x]["closed"])
        key = str(len(self.spans))
        self.spans[key] = {"name": name, "parent": parent_id if parent_id is not None else stack[-1] if stack else None,
                           "closed": False, "events": []}
        self.stack.set((*stack, key))
        return key
    def capture_event(self, name, data):
        stack = tuple(x for x in self.stack.get() if not self.spans[x]["closed"])
        self.events.append((name, data, stack[-1] if stack else None))
        if stack:
            self.spans[stack[-1]]["events"].append((name, data))
    def end_span(self, key, data=None):
        self.spans[key]["closed"] = True
        self.stack.set(tuple(x for x in self.stack.get() if x != key and not self.spans[x]["closed"]))


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["success", "retry", "none"])
async def test_explicit_none_mixed_origins_isolate_active_foreground_and_accounting(mode):
    from friday_telemetry import CompositeProvider
    sinks = [ContextSink(), ContextSink()]
    o = ChatTelemetryObserver(enabled=True, session_id="private", provider=CompositeProvider(sinks))
    origins = [o.correlation.context(turn=True), None, o.correlation.context(turn=True)]
    seen = []
    attempts = 0
    class Extractor:
        async def extract(self, turn):
            nonlocal attempts
            attempts += 1
            seen.append(o.correlation.current().context.turn_ref)
            if mode == "retry" and attempts == 2:
                raise RuntimeError("PRIVATE_PRIMARY")
            return {}
    adapter = FrameworkMaintenanceAdapter(config(), "private", None, None, None, {}, {},
        extractor=None if mode == "none" else Extractor(), observer=o)
    items = [PendingExtractionTurn(str(i), "PRIVATE_U", "PRIVATE_A", origin) for i, origin in enumerate(origins)]
    adapter.pending_extraction = items.copy()
    with turn_scope(o, "completion"):
        foreground = o.correlation.current()
        with suppress(RuntimeError):
            await adapter.flush_pending_extraction()
        assert o.correlation.current() is foreground
        assert foreground.accounting.completed_tools == foreground.accounting.failed_tools == 0
        assert foreground.accounting.persistence == "not_started"
        if mode == "retry":
            assert adapter.pending_extraction == items[1:]
            assert adapter.pending_extraction[0] is items[1]
            await adapter.flush_pending_extraction()
        assert not adapter.pending_extraction
        assert all(s.stack.get() == () for s in sinks)
    finishes = [dict(e.attributes) for e in o.snapshot().events if e.name == "execution.operation_finish"]
    expected = [origins[0].turn_ref, None, None, origins[2].turn_ref] if mode == "retry" else [origins[0].turn_ref, None, origins[2].turn_ref]
    assert [e.get("turn_ref") for e in finishes] == expected
    assert not o._spans and o.correlation.current() is None
    for sink in sinks:
        extraction = [s for s in sink.spans.values() if any(n == "execution.operation_start" for n, d in s["events"])]
        assert len(extraction) == len(expected) and all(s["parent"] is None and s["closed"] for s in extraction)
        assert "PRIVATE" not in repr(sink.events)


@pytest.mark.asyncio
async def test_context_sink_active_background_preemption_resume_shutdown_and_nested_siblings():
    from friday_chat.turns.telemetry import operation_scope
    from friday_telemetry import CompositeProvider
    sinks = [ContextSink(), ContextSink()]
    o = ChatTelemetryObserver(enabled=True, session_id="private", provider=CompositeProvider(sinks))
    r = build_runtime(config())
    r.telemetry = o
    entered = asyncio.Event()
    attempt = 0
    class Extractor:
        async def extract(self, turn):
            nonlocal attempt
            attempt += 1
            entered.set()
            if attempt == 1:
                await asyncio.Event().wait()
            return {}
    values = config().model_dump()
    values["extraction"]["interval"] = 0
    adapter = FrameworkMaintenanceAdapter(FridayChatConfig.model_validate(values), "private", None, None, None, {}, {},
        extractor=Extractor(), observer=o)
    r.maintenance = adapter
    r.config = adapter.config
    manager = BackgroundTaskManager()
    coordinator = BackgroundWorkCoordinator(r, manager)
    try:
        with turn_scope(o, "completion") as origin:
            parent = o.correlation.current()
            coordinator.schedule_after_turn(turn_count=1, user_message="PRIVATE_U", assistant_message="PRIVATE_A", correlation_context=origin)
            await asyncio.wait_for(entered.wait(), timeout=2)
            assert await coordinator.preempt_extraction_for_foreground_turn()
            assert adapter.pending_extraction[0].correlation_context is origin
            assert coordinator.resume_preempted_extraction()
            await manager.wait_for_all()
            async def sibling():
                with operation_scope(o, "native_tool"):
                    await asyncio.sleep(0)
            await asyncio.gather(sibling(), sibling())
            with turn_scope(o, "completion"), operation_scope(o, "model_call"):
                pass
            assert o.correlation.current() is parent
            assert all(s.stack.get() == () for s in sinks)
        coordinator.schedule_after_turn(turn_count=2, user_message="PRIVATE_U", assistant_message="PRIVATE_A", correlation_context=origin)
        await manager.wait_for_all()
        adapter.pending_extraction.append(PendingExtractionTurn("private", "PRIVATE_U", "PRIVATE_A", None))
        assert await adapter.flush_pending_extraction() == 1
    finally:
        await manager.close()
    assert manager.closed and not o._spans and o.correlation.current() is None
    for sink in sinks:
        assert all(s["closed"] for s in sink.spans.values())
        for name, data, key in sink.events:
            if name == "execution.operation_start":
                span = sink.spans[key]
                if data["operation_kind"] == "memory_extract":
                    assert span["parent"] is None
                else:
                    assert span["parent"] is not None
            if name in {"execution.operation_start", "execution.operation_finish"}:
                assert sink.spans[key]["name"] == "chat.operation"


@pytest.mark.parametrize("invalid_origin", [object(), True, "PRIVATE_ORIGIN", {"PRIVATE": "PRIVATE"}])
def test_malformed_explicit_origin_is_diagnosed_without_borrowing_foreground(invalid_origin):
    from friday_chat.turns.telemetry import operation_scope
    from friday_telemetry import DebugTelemetryRecorder
    sink = DebugTelemetryRecorder()
    o = ChatTelemetryObserver(enabled=True, session_id="private", provider=sink)
    with turn_scope(o, "completion"):
        parent = o.correlation.current()
        before = o.snapshot().rejected_count
        with operation_scope(o, "memory_extract", origin=invalid_origin):
            child = o.correlation.current()
            assert child.context.turn_ref is None and child.context.parent_operation_ref is None
            assert child.accounting is None
        assert o.correlation.current() is parent
        assert o.snapshot().rejected_count == before + 1
        assert parent.accounting.persistence == "not_started"
    assert not o._spans and o.correlation.current() is None
    assert "PRIVATE" not in repr(o.snapshot()) and "PRIVATE" not in repr(sink.events)
