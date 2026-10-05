"""TELEM-01 contract tests: local inspection, safe injection, and lifecycle truth."""

from __future__ import annotations

import asyncio
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from friday_chat.app import FridayChatApp, ListInputSource, ListOutputSink
from friday_chat.config import (
    FridayChatConfig,
    FridayChatConfigError,
    load_friday_py_config,
)
from friday_chat.runtime import build_runtime
from friday_chat.telemetry import ChatTelemetryObserver
from friday_telemetry import CompositeProvider, DebugTelemetryRecorder
from pydantic import ValidationError

SENTINEL = "PRIVATE_CONTENT_SENTINEL"


def config(enabled: bool = True) -> FridayChatConfig:
    return FridayChatConfig.model_validate(
        {"llm": {"model": "fake/test"}, "telemetry": {"enabled": enabled}}
    )


class FailingRecorder(DebugTelemetryRecorder):
    def capture_event(self, event_name: str, data: dict) -> None:
        raise RuntimeError(SENTINEL)

    def start_span(self, name: str, parent_id: str | None = None) -> str:
        raise RuntimeError(SENTINEL)

    def end_span(self, span_id: str, data: dict | None = None) -> None:
        raise RuntimeError(SENTINEL)


def observer(runtime):
    assert runtime.telemetry is not None
    return runtime.telemetry


def test_default_disabled_and_injected_override() -> None:
    disabled = build_runtime(FridayChatConfig(), session_id=SENTINEL)
    assert observer(disabled).snapshot().state == "disabled"
    assert observer(disabled).snapshot().events == ()
    sink = DebugTelemetryRecorder()
    runtime = build_runtime(config(False), session_id=SENTINEL, telemetry=sink)
    snap = observer(runtime).snapshot()
    assert snap.provider == "injected"
    assert snap.configured is False
    assert snap.state == "active"
    assert sink.event_names == ["chat.runtime_ready"]
    assert SENTINEL not in repr(snap)


@pytest.mark.parametrize(
    "section",
    [
        {"enabled": "true"},
        {"enabled": 1},
        {"provider": "otel"},
        {"provider": 3},
        {"secret": SENTINEL},
        {SENTINEL: SENTINEL},
    ],
)
def test_local_config_is_strict_and_loader_errors_are_safe(
    tmp_path: Path, section: dict
) -> None:
    import yaml

    path = tmp_path / "config.yaml"
    path.write_text(
        yaml.safe_dump({"llm": {"model": "fake/test"}, "telemetry": section})
    )
    with pytest.raises(FridayChatConfigError) as error:
        load_friday_py_config(path)
    assert SENTINEL not in str(error.value)
    with pytest.raises(ValidationError):
        FridayChatConfig.model_validate({"telemetry": section})


def test_yaml_enabled_local_provider(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text(
        "llm:\n  model: fake/test\ntelemetry:\n  enabled: true\n  provider: debug\n"
    )
    runtime = build_runtime(load_friday_py_config(path))
    snapshot = observer(runtime).snapshot()
    assert (snapshot.provider, snapshot.state) == ("debug", "active")
    assert [event.name for event in snapshot.events] == ["chat.runtime_ready"]


def test_bounded_immutable_records_preserve_failure_and_drop_counts() -> None:
    telemetry = ChatTelemetryObserver(enabled=True, session_id=SENTINEL)
    telemetry.capture_event(SENTINEL, {"prompt": SENTINEL})
    for _ in range(300):
        telemetry.emit("runtime_ready")
    snap = telemetry.snapshot()
    assert len(snap.events) == 256
    assert snap.dropped_count == 45
    assert snap.failure_count == snap.rejected_count == 1
    assert snap.state == "failed"
    assert snap.events[0].sequence == 46
    assert snap.events[-1].sequence == 301
    assert SENTINEL not in repr(snap)
    with pytest.raises(FrozenInstanceError):
        snap.events[0].name = SENTINEL
    telemetry.emit("application_start")
    assert len(snap.events) == 256
    assert snap.events[-1].sequence == 301


@pytest.mark.parametrize(
    "name,data",
    [
        ("llm.completion", {"error_message": SENTINEL}),
        (f"mcp.{SENTINEL}", {}),
        ("mcp.tool_call_finish", {"tool_ref": SENTINEL}),
        ("mcp.tool_call_finish", {"reason": SENTINEL}),
        ("mcp.tool_call_finish", {"count": -1}),
        ("mcp.tool_call_finish", {"count": True}),
        ("mcp.tool_call_finish", {"arguments": SENTINEL}),
        ("mcp.tool_call_finish", {"name": "tool_call_start"}),
        ("chat.application_start", {"session_ref": "0" * 16, "prompt": SENTINEL}),
    ],
)
def test_unknown_or_content_events_are_rejected(name: str, data: dict) -> None:
    sink = DebugTelemetryRecorder()
    telemetry = ChatTelemetryObserver(enabled=True, session_id=SENTINEL, provider=sink)
    telemetry.capture_event(name, data)
    assert sink.events == []
    snap = telemetry.snapshot()
    assert snap.failure_count == snap.rejected_count == 1
    assert SENTINEL not in repr(snap)
    assert snap.events[0].name == "chat.telemetry_delivery_failure"


def test_valid_mcp_events_preserve_existing_payload() -> None:
    first, second = DebugTelemetryRecorder(), DebugTelemetryRecorder()
    telemetry = ChatTelemetryObserver(
        enabled=True, session_id=SENTINEL, provider=CompositeProvider([first, second])
    )
    data = {"tool_ref": "a" * 16, "reason": "success", "count": 2, "required": False}
    telemetry.capture_event("mcp.tool_call_finish", data)
    assert first.get_event("mcp.tool_call_finish") == data
    assert second.get_event("mcp.tool_call_finish") == data
    assert dict(telemetry.snapshot().events[0].attributes) == data


def test_failed_sink_is_inspectable_and_does_not_raise() -> None:
    telemetry = ChatTelemetryObserver(
        enabled=True, session_id=SENTINEL, provider=FailingRecorder()
    )
    telemetry.emit("runtime_ready")
    parent = telemetry.start_span("chat.runtime")
    telemetry.end_span(parent)
    snap = telemetry.snapshot()
    assert snap.state == "failed"
    assert snap.failure_count == 2
    assert SENTINEL not in repr(snap)


def test_safe_span_ids_parents_and_invalid_end_data() -> None:
    first, second = DebugTelemetryRecorder(), DebugTelemetryRecorder()
    telemetry = ChatTelemetryObserver(
        enabled=True, session_id=SENTINEL, provider=CompositeProvider([first, second])
    )
    parent = telemetry.start_span("chat.runtime")
    child = telemetry.start_span("chat.application", parent)
    telemetry.end_span(child, {"prompt": SENTINEL})
    telemetry.end_span(parent)
    telemetry.end_span(child)
    for sink in (first, second):
        root = sink.get_span_by_name("chat.runtime")
        nested = sink.get_span_by_name("chat.application")
        assert root is not None and nested is not None
        assert nested.parent_id in sink.spans
        assert nested.data == {"outcome": "failed", "count": 0}
        assert all(span.end_time is not None for span in sink.spans.values())
        assert SENTINEL not in repr(sink.spans)
    assert telemetry.snapshot().rejected_count == 1


def test_unsafe_span_name_and_active_span_cap_are_visible() -> None:
    sink = DebugTelemetryRecorder()
    telemetry = ChatTelemetryObserver(enabled=True, session_id="test", provider=sink)
    telemetry.start_span(SENTINEL)
    for _ in range(129):
        telemetry.start_span("chat.runtime")
    assert len(sink.spans) == 128
    assert telemetry.snapshot().rejected_count == 2
    assert SENTINEL not in repr(sink.spans)


def test_real_path_receives_observer_before_construction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import friday_chat.runtime as module

    built = build_runtime(config(False), session_id="test")
    received = []

    def builder(config, *, session_identity, maintenance_layout, telemetry):
        assert telemetry is not None
        assert telemetry.snapshot().events == ()
        telemetry.capture_event("mcp.connection_start", {"count": 1})
        received.append(telemetry)
        return built

    monkeypatch.setattr(module, "_build_framework_runtime", builder)
    monkeypatch.chdir(tmp_path)
    loaded = config()
    loaded.memory.persist_directory = str(tmp_path / "vector")
    loaded.transcript.export_directory = str(tmp_path / "exports")
    runtime = build_runtime(loaded, fake=False, session_id="test")
    assert observer(runtime) is received[0]
    assert [e.name for e in observer(runtime).snapshot().events] == [
        "mcp.connection_start",
        "chat.runtime_ready",
    ]


def test_failed_runtime_assembly_never_emits_ready(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sink = DebugTelemetryRecorder()

    def failed(*args, **kwargs):
        raise RuntimeError(SENTINEL)

    monkeypatch.setattr("friday_chat.runtime._build_framework_runtime", failed)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(RuntimeError, match=SENTINEL):
        build_runtime(config(), fake=False, telemetry=sink)
    assert sink.events == []


@pytest.mark.asyncio
async def test_app_lifecycle_and_borrowed_provider_ownership(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Borrowed(DebugTelemetryRecorder):
        def close(self):
            raise AssertionError("borrowed provider must not be closed")

    sink = Borrowed()
    runtime = build_runtime(config(), session_id=SENTINEL, telemetry=sink)

    async def close():
        assert "chat.application_stop" not in sink.event_names

    monkeypatch.setattr(runtime.async_clients, "close", close)
    result = await FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource([SENTINEL, "/exit"]),
        output_sink=ListOutputSink(),
    ).run()
    assert result.turns_processed == 1
    assert sink.event_names == [
        "chat.runtime_ready",
        "chat.application_start",
        "chat.application_stop",
    ]
    assert sink.get_event("chat.application_stop")["outcome"] == "succeeded"
    assert SENTINEL not in repr(observer(runtime).snapshot())
    assert SENTINEL not in repr(sink.events)


@pytest.mark.asyncio
@pytest.mark.parametrize("component", ["client", "memory", "transcript", "mcp"])
async def test_failed_cleanup_is_truthful_without_changing_behavior(
    component: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime = build_runtime(config())

    async def failed(*args, **kwargs):
        raise RuntimeError(SENTINEL)

    target, name = {
        "client": (runtime.async_clients, "close"),
        "memory": (runtime.maintenance, "flush_memory"),
        "transcript": (runtime.transcript, "finalize"),
        "mcp": (runtime, "stop_mcp_tools"),
    }[component]
    monkeypatch.setattr(target, name, failed)
    app = FridayChatApp(
        runtime=runtime, input_source=ListInputSource([]), output_sink=ListOutputSink()
    )
    if component == "mcp":
        with pytest.raises(RuntimeError, match=SENTINEL):
            await app.run()
    else:
        assert (await app.run()).exit_reason == "eof"
    stop = observer(runtime).snapshot().events[-1]
    assert stop.name == "chat.application_stop"
    assert dict(stop.attributes)["outcome"] == "failed"
    assert dict(stop.attributes)["reason"] == "shutdown_failed"
    assert SENTINEL not in repr(observer(runtime).snapshot())
    assert app.started is False


@pytest.mark.asyncio
async def test_cancelled_app_finishes_cleanup_then_reports_cancelled() -> None:
    entered = asyncio.Event()

    class BlockingInput:
        async def read(self):
            entered.set()
            await asyncio.Event().wait()

    runtime = build_runtime(config())
    task = asyncio.create_task(
        FridayChatApp(
            runtime=runtime, input_source=BlockingInput(), output_sink=ListOutputSink()
        ).run()
    )
    await entered.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert runtime.async_clients.close_calls == 1
    stop = observer(runtime).snapshot().events[-1]
    assert dict(stop.attributes)["outcome"] == "cancelled"
    assert dict(stop.attributes)["reason"] == "cancelled"


@pytest.mark.asyncio
async def test_keyboard_interrupt_is_categorical_cancellation() -> None:
    class InterruptedInput:
        async def read(self):
            raise KeyboardInterrupt

    runtime = build_runtime(config())
    result = await FridayChatApp(
        runtime=runtime, input_source=InterruptedInput(), output_sink=ListOutputSink()
    ).run()
    assert result.exit_reason == "keyboard_interrupt"
    assert (
        dict(observer(runtime).snapshot().events[-1].attributes)["outcome"]
        == "cancelled"
    )


@pytest.mark.asyncio
async def test_injected_failure_does_not_interrupt_application() -> None:
    runtime = build_runtime(config(), telemetry=FailingRecorder())
    result = await FridayChatApp(
        runtime=runtime, input_source=ListInputSource([]), output_sink=ListOutputSink()
    ).run()
    assert result.exit_reason == "eof"
    assert observer(runtime).snapshot().failure_count == 3


@pytest.mark.asyncio
@pytest.mark.parametrize("during_start", [True, False])
async def test_lifecycle_failure_phase_and_cleanup_are_truthful(
    during_start: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    class FailedInput:
        async def read(self):
            raise RuntimeError(SENTINEL)

    runtime = build_runtime(config())
    app = FridayChatApp(
        runtime=runtime, input_source=FailedInput(), output_sink=ListOutputSink()
    )
    if during_start:

        def failed_start():
            raise RuntimeError(SENTINEL)

        monkeypatch.setattr(app, "start", failed_start)
    with pytest.raises(RuntimeError, match=SENTINEL):
        await app.run()
    stop = observer(runtime).snapshot().events[-1]
    assert dict(stop.attributes)["reason"] == (
        "startup_failed" if during_start else "application_failed"
    )
    assert runtime.async_clients.close_calls == (0 if during_start else 1)
    assert SENTINEL not in repr(observer(runtime).snapshot())
