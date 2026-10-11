import pytest
from friday_chat.commands.contracts import CommandContext, CommandMetadata
from friday_chat.commands.registry import _debug_handler, _timing_handler
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import build_runtime
from friday_chat.telemetry import ChatTelemetryObserver
from friday_chat.turns.processor import TurnCircuitBreakerOpenError, TurnProcessor
from friday_chat.turns.telemetry import operation_scope, turn_scope
from friday_telemetry import DebugTelemetryRecorder, TelemetryInterface
from friday_telemetry.models.execution import OperationFinish


class FailedSink(TelemetryInterface):
    def capture_event(self, event_name, data):
        raise RuntimeError("PRIVATE_ERROR")
    def start_span(self, name, parent_id=None):
        raise RuntimeError("PRIVATE_ERROR")
    def end_span(self, span_id, data=None):
        raise RuntimeError("PRIVATE_ERROR")


def test_failures_bounds_counter_ownership_and_replay():
    o = ChatTelemetryObserver(enabled=True, session_id="private", provider=FailedSink())
    for _ in range(40):
        with turn_scope(o, "completion"), operation_scope(o, "native_tool"):
            frame = o.correlation.current()
            event = OperationFinish(**frame.context.identity().model_dump(), operation_kind="native_tool", outcome="succeeded", duration_ms=0.0)
            o.execution(event)
            o.execution(event)  # Duplicate terminal cannot increment metrics twice.
    snapshot = o.snapshot()
    assert len(snapshot.events) == 256 and snapshot.dropped_count > 0
    assert snapshot.failure_count > 0 and "PRIVATE_ERROR" not in repr(snapshot)
    metrics = o.execution_snapshot()
    assert len(metrics.turns) == 32 and ("native_tool", "succeeded", 40) in metrics.counters
    assert sum(v for kind, outcome, bucket, v in metrics.histograms if kind == "native_tool") == 40
    assert not o._spans
    o.execution(event)  # Closed scope cannot replay a terminal.
    assert o.execution_snapshot().counters == metrics.counters


@pytest.mark.asyncio
async def test_failed_turn_visible_without_result():
    r = build_runtime(FridayChatConfig.model_validate({"llm": {"model": "fake/test"}, "telemetry": {"enabled": True}}))
    with pytest.raises(TurnCircuitBreakerOpenError):
        await TurnProcessor(r, circuit_breaker_open=True).process("private")
    context = CommandContext(runtime=r)
    metadata = CommandMetadata("debug", "safe", "session", "/debug")
    debug = await _debug_handler(context, (), metadata)
    timing = await _timing_handler(context, (), metadata)
    assert "blocked" in debug.output and "not_started" in debug.output
    assert "observed_turn" in timing.output


def test_end_failure_capacity_saturation_and_invalid_link():
    class EndFailure(DebugTelemetryRecorder):
        def end_span(self, span_id, data=None):
            raise RuntimeError("PRIVATE_END")
    o = ChatTelemetryObserver(enabled=True, session_id="private", provider=EndFailure())
    with turn_scope(o, "completion"), operation_scope(o, "native_tool"):
        o._counters[("native_tool", "succeeded")] = 2**63 - 1
        o.capture_event("mcp.tool_call_start", {"tool_ref": "RAW_TOOL"})
    assert not o._spans and o.snapshot().failure_count >= 3
    assert ("native_tool", "succeeded", 2**63 - 1) in o.execution_snapshot().counters
    assert not any(e.name == "execution.mcp_link" for e in o.snapshot().events)
    for _ in range(129):
        o.start_span("chat.operation")
    assert len(o._spans) == 128
    for span in tuple(o._spans):
        o.end_span(span)
    assert not o._spans and "PRIVATE_END" not in repr(o.snapshot())


@pytest.mark.parametrize("version", [True, False, 1.0, "1", 0, 2])
@pytest.mark.parametrize("entry", ["dictionary", "forged", "forged_root"])
def test_invalid_versions_rejected_before_record_delivery_and_metrics(version, entry):
    from friday_telemetry.models.execution import ExecutionEvent
    sink = DebugTelemetryRecorder()
    o = ChatTelemetryObserver(enabled=True, session_id="private", provider=sink)
    with operation_scope(o, "native_tool"):
        frame = o.correlation.current()
        data = {**frame.context.identity().model_dump(), "schema_version": version,
                "operation_kind": "native_tool", "outcome": "succeeded", "duration_ms": 0.0}
        before = o.execution_snapshot()
        delivered = len(sink.events)
        if entry == "dictionary":
            o.capture_event("execution.operation_finish", data)
        else:
            forged = OperationFinish.model_construct(**data)
            o.execution(forged if entry == "forged" else ExecutionEvent.model_construct(root=forged))
        assert o.execution_snapshot() == before
        assert len(sink.events) == delivered
        assert not frame.terminal
        assert o.snapshot().rejected_count == 1
        assert not any(e.name == "execution.operation_finish" for e in o.snapshot().events)
    assert o.execution_snapshot().counters == (("native_tool", "succeeded", 1),)
