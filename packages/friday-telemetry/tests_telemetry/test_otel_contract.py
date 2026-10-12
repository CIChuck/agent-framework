"""Actual SDK semantics through the public managed adapter; synthetic exporters."""

import asyncio
import contextvars
import io
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError

import pytest
from friday_telemetry import (
    OTelConfig,
    TelemetryFactoryConfig,
    TelemetryOperationError,
    create_telemetry,
)
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult


@pytest.fixture
def recorded(monkeypatch):
    from friday_telemetry.providers import _otel_exporter

    spans = []
    lock = threading.Lock()
    initial = set(threading.enumerate())

    class Recording(SpanExporter):
        def __init__(self, stream):
            self.closed = False

        def export(self, batch):
            with lock:
                spans.extend(batch)
            return SpanExportResult.FAILURE if self.closed else SpanExportResult.SUCCESS

        def shutdown(self):
            self.closed = True

    monkeypatch.setattr(_otel_exporter, "SafeConsoleExporter", Recording)
    yield spans
    workers = [
        t
        for t in threading.enumerate()
        if t not in initial and t.name == "FridayTelemetryExporter"
    ]
    assert workers == [], "Owned workers must be explicitly released by each test"


def managed(**settings):
    return create_telemetry(
        TelemetryFactoryConfig(provider="otel", otel=OTelConfig(**settings))
    )


def test_actual_parent_events_scalars_and_global_isolation(recorded, monkeypatch):
    global_before = trace.get_tracer_provider()
    monkeypatch.setattr(
        trace, "set_tracer_provider", lambda *a: pytest.fail("global registration")
    )
    ambient_sdk = TracerProvider(shutdown_on_exit=False)
    ambient = ambient_sdk.get_tracer("synthetic.ambient").start_span("ambient")
    try:
        with trace.use_span(ambient), managed() as handle:
            sink = handle.telemetry
            parent = sink.start_span("root")
            child = sink.start_span("child", parent)
            attributes = {
                "bool": True,
                "min": -(2**63),
                "max": 2**63 - 1,
                "float": 1.25,
                "string": "safe",
            }
            sink.capture_event("current.event", attributes)
            sink.end_span(child, attributes)
            sink.end_span(parent)
            sink.capture_event("standalone.event", attributes)
            assert handle.flush().status == "success"
            assert handle.snapshot().exported_spans == 3
        spans = {s.name: s for s in recorded}
        root, child = spans["root"], spans["child"]
        assert root.parent is None
        assert child.parent.span_id == root.context.span_id
        assert child.context.trace_id == root.context.trace_id
        assert child.context.trace_flags.sampled
        assert dict(child.attributes) == attributes
        assert dict(child.events[0].attributes) == attributes
        assert spans["standalone.event"].parent is None
        assert spans["standalone.event"].events[0].name == "standalone.event"
        assert dict(root.resource.attributes) == {"service.name": "friday"}
        assert not ambient.events
        assert trace.get_tracer_provider() is global_before
    finally:
        ambient.end()
        ambient_sdk.shutdown()


def test_out_of_order_cross_context_foreign_and_duplicate_end(recorded):
    with managed() as first, managed() as second:
        sink = first.telemetry
        parent = sink.start_span("parent")
        child = sink.start_span("child")
        contextvars.Context().run(sink.end_span, parent)
        with pytest.raises(TelemetryOperationError, match="invalid_parent"):
            sink.start_span("ended.parent", parent)
        with pytest.raises(TelemetryOperationError, match="invalid_parent"):
            second.telemetry.start_span("foreign", child)
        sink.end_span(parent)
        sink.end_span("unknown")
        sink.capture_event("still.child", {})
        sink.end_span(child)
        new_root = sink.start_span("new.root")
        sink.end_span(new_root)
        assert first.flush().status == "success"
    by_name = {s.name: s for s in recorded}
    assert by_name["child"].events[0].name == "still.child"
    assert by_name["new.root"].parent is None
    assert len(recorded) == 3


@pytest.mark.asyncio
async def test_task_thread_and_provider_contexts_are_independent(recorded):
    with managed() as first, managed() as second:
        root = first.telemetry.start_span("task.root")

        async def child(name):
            span = first.telemetry.start_span(name)
            await asyncio.sleep(0)
            first.telemetry.capture_event("task.event", {"name": name})
            first.telemetry.end_span(span)

        await asyncio.gather(child("task.one"), child("task.two"))
        second.telemetry.capture_event("provider.two", {})

        def thread_child(name):
            span = first.telemetry.start_span(name)
            first.telemetry.capture_event("thread.event", {})
            first.telemetry.end_span(span)

        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(thread_child, ["thread.one", "thread.two"]))
        first.telemetry.end_span(root)
        assert first.flush().status == second.flush().status == "success"
    by_name = {s.name: s for s in recorded}
    parent = by_name["task.root"]
    for name in ["task.one", "task.two"]:
        assert by_name[name].parent.span_id == parent.context.span_id
        assert by_name[name].events[0].attributes["name"] == name
    for name in ["thread.one", "thread.two", "provider.two"]:
        assert by_name[name].parent is None


@pytest.mark.parametrize(
    "data",
    [
        {"nested": {"SECRET": "PRIVATE"}},
        {"list": [1]},
        {"value": object()},
        {"value": float("nan")},
        {"value": float("inf")},
        {"value": 2**63},
        {"value": -(2**63) - 1},
        {"value": "\ud800"},
        {"value": "é" * 513},
        {"bad key": 1},
        {"κ": 1},
        {"x" * 129: 1},
        {f"a{i}": i for i in range(65)},
    ],
)
def test_unrepresentable_attributes_rejected_before_sdk(recorded, data, caplog):
    with managed() as handle:
        span = handle.telemetry.start_span("safe")
        with pytest.raises(TelemetryOperationError, match="invalid_input"):
            handle.telemetry.capture_event("safe.event", data)
        with pytest.raises(TelemetryOperationError, match="invalid_input"):
            handle.telemetry.end_span(span, data)
        assert handle.snapshot().invalid_inputs == 2
        handle.telemetry.end_span(span)
        assert handle.flush().status == "success"
    assert recorded[0].events == ()
    assert not recorded[0].attributes
    assert not caplog.records


@pytest.mark.parametrize("name", ["", "bad name", "é", "x" * 129, "\ud800"])
def test_names_rejected_without_sdk_warning(recorded, name, caplog):
    with managed() as handle:
        with pytest.raises(TelemetryOperationError, match="invalid_input"):
            handle.telemetry.start_span(name)
        with pytest.raises(TelemetryOperationError, match="invalid_input"):
            handle.telemetry.capture_event(name, {})
    assert recorded == []
    assert not caplog.records


def test_active_limit_cancelled_close_idempotent_and_frozen(recorded):
    handle = managed()
    try:
        for n in range(128):
            handle.telemetry.start_span(f"open.{n}")
        with pytest.raises(TelemetryOperationError, match="active_limit"):
            handle.telemetry.start_span("overflow")
        assert handle.snapshot().active_spans == 128
        result = handle.shutdown()
        assert result.status == "success"
        assert result.snapshot.cancelled_spans == 128
        assert result.snapshot.active_spans == 0
        assert not result.snapshot.worker_alive
        assert handle.shutdown() is result
        assert handle.flush().status == "closed"
        with pytest.raises(FrozenInstanceError):
            result.snapshot.closed = False
        with pytest.raises(TelemetryOperationError, match="closed"):
            handle.telemetry.capture_event("closed", {})
        with pytest.raises(TelemetryOperationError, match="closed"):
            handle.telemetry.start_span("closed")
        assert all(s.status.description == "cancelled" for s in recorded)
    finally:
        handle.shutdown()


def test_actual_console_closed_capture_stream_cleanup(monkeypatch, caplog):
    stream = io.StringIO()
    monkeypatch.setattr("sys.stdout", stream)
    handle = managed()
    try:
        stream.close()
        handle.telemetry.capture_event("closed.stream", {})
        result = handle.flush()
        assert result.status == "failure"
        assert result.snapshot.export_failures == 1
        result = handle.shutdown()
        assert result.status == "failure"
        assert not result.snapshot.worker_alive
        assert not caplog.records
    finally:
        handle.shutdown()


def test_queue_overflow_flush_deadline_failure_recovery_and_cleanup(monkeypatch):
    from friday_telemetry.providers import _otel_exporter

    entered, release = threading.Event(), threading.Event()

    class Controlled(SpanExporter):
        fail = True

        def export(self, spans):
            entered.set()
            release.wait(2)
            return SpanExportResult.FAILURE if self.fail else SpanExportResult.SUCCESS

        def shutdown(self):
            release.set()

    exporter = Controlled()
    monkeypatch.setattr(_otel_exporter, "SafeConsoleExporter", lambda stream: exporter)
    handle = managed(queue_limit=2, batch_limit=1)
    try:
        handle.telemetry.capture_event("one", {})
        assert entered.wait(1)
        for name in ["two", "three", "dropped"]:
            handle.telemetry.capture_event(name, {})
        assert handle.snapshot().dropped_spans == 1
        start = time.monotonic()
        assert handle.flush(20).status == "timeout"
        assert time.monotonic() - start < 0.3
        release.set()
        assert handle.flush().status == "failure"
        assert handle.snapshot().failed_spans == 3
        exporter.fail = False
        handle.telemetry.capture_event("recovered", {})
        assert handle.flush().status == "success"
        assert handle.snapshot().failed_spans == 3
        assert handle.snapshot().exported_spans == 1
    finally:
        release.set()
        result = handle.shutdown()
        assert not result.snapshot.worker_alive


def test_shutdown_cancels_cooperative_in_flight_with_one_deadline(monkeypatch):
    from friday_telemetry.providers import _otel_exporter

    entered, release = threading.Event(), threading.Event()
    initial = set(threading.enumerate())

    class Blocking(SpanExporter):
        def export(self, batch):
            entered.set()
            release.wait(2)
            return SpanExportResult.FAILURE

        def shutdown(self):
            release.set()

    monkeypatch.setattr(
        _otel_exporter, "SafeConsoleExporter", lambda stream: Blocking()
    )
    handle = managed(batch_limit=1)
    try:
        handle.telemetry.capture_event("blocked", {})
        assert entered.wait(1)
        start = time.monotonic()
        result = handle.shutdown(100)
        assert time.monotonic() - start < 0.3
        assert result.status == "timeout"
        assert not result.snapshot.worker_alive
        assert handle.shutdown() is result
    finally:
        release.set()
        handle.shutdown()
        for worker in set(threading.enumerate()) - initial:
            if worker.name == "FridayTelemetryExporter":
                worker.join(1)
                assert not worker.is_alive()


def test_concurrent_shutdown_uses_each_callers_budget_and_retains_completed_result(
    monkeypatch,
):
    from friday_telemetry.providers import _otel_exporter

    entered, release = threading.Event(), threading.Event()

    class Blocking(SpanExporter):
        def export(self, batch):
            entered.set()
            release.wait(2)
            return SpanExportResult.SUCCESS

        def shutdown(self):
            release.set()

    monkeypatch.setattr(
        _otel_exporter, "SafeConsoleExporter", lambda stream: Blocking()
    )
    handle = managed(batch_limit=1)
    try:
        handle.telemetry.capture_event("concurrent", {})
        assert entered.wait(1)
        with ThreadPoolExecutor(max_workers=1) as pool:
            first = pool.submit(handle.shutdown, 500)
            deadline = time.monotonic() + 1
            while not handle.snapshot().closed and time.monotonic() < deadline:
                time.sleep(0.001)
            assert handle.snapshot().closed
            start = time.monotonic()
            second = handle.shutdown(20)
            assert second.status == "timeout"
            assert time.monotonic() - start < 0.15
            release.set()
            completed = first.result(timeout=1)
        assert completed.status == "success"
        assert not completed.snapshot.worker_alive
        assert handle.shutdown() is completed
    finally:
        release.set()
        handle.shutdown()


def test_noncooperative_double_reports_unreaped_then_is_released_in_finally(
    monkeypatch,
):
    from friday_telemetry.providers import _otel_exporter

    entered, release = threading.Event(), threading.Event()
    initial = set(threading.enumerate())

    class Hung(SpanExporter):
        def export(self, batch):
            entered.set()
            release.wait(2)
            return SpanExportResult.FAILURE

        def shutdown(self):
            pass

    monkeypatch.setattr(_otel_exporter, "SafeConsoleExporter", lambda stream: Hung())
    handle = managed(batch_limit=1)
    try:
        handle.telemetry.capture_event("hung.double", {})
        assert entered.wait(1)
        result = handle.shutdown(30)
        assert result.status == "timeout"
        assert result.snapshot.worker_alive
        assert handle.shutdown() is result
    finally:
        release.set()
        for worker in set(threading.enumerate()) - initial:
            if worker.name == "FridayTelemetryExporter":
                worker.join(1)
                assert not worker.is_alive()
        assert not handle.snapshot().worker_alive


def test_scalar_and_name_limits_accept_exact_boundaries_without_repr(recorded):
    class ForbiddenRepresentation:
        def __str__(self):
            pytest.fail("untrusted object representation")

    with managed() as handle:
        name = "a" * 128
        span = handle.telemetry.start_span(name)
        handle.telemetry.capture_event(name, {"utf8": "é" * 512})
        with pytest.raises(TelemetryOperationError, match="invalid_input"):
            handle.telemetry.capture_event(
                "unsafe", {"object": ForbiddenRepresentation()}
            )
        attributes = {f"a{n}": n for n in range(64)}
        handle.telemetry.end_span(span, attributes)
        assert handle.flush().status == "success"
    assert len(recorded[0].attributes) == 64
    assert recorded[0].events[0].attributes["utf8"] == "é" * 512


def test_standalone_event_respects_provider_active_cap_in_another_context(recorded):
    with managed() as handle:
        for n in range(128):
            handle.telemetry.start_span(f"open.{n}")
        with pytest.raises(TelemetryOperationError, match="active_limit"):
            contextvars.Context().run(handle.telemetry.capture_event, "standalone", {})


def test_sparse_queue_exports_on_bounded_interval_without_explicit_flush(recorded):
    with managed(flush_interval_ms=20) as handle:
        handle.telemetry.capture_event("scheduled", {})
        deadline = time.monotonic() + 1
        while not recorded and time.monotonic() < deadline:
            time.sleep(0.005)
        assert len(recorded) == 1
        assert handle.snapshot().exported_spans == 1
