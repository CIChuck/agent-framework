"""Only two approved native tests: synthetic literal-loopback ephemeral collector."""

import json
import threading
from concurrent.futures import ThreadPoolExecutor

import grpc
import pytest
from friday_telemetry import OTelConfig, TelemetryFactoryConfig, create_telemetry
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
    ExportTraceServiceResponse,
)
from opentelemetry.proto.collector.trace.v1.trace_service_pb2_grpc import (
    TraceServiceServicer,
    add_TraceServiceServicer_to_server,
)


@pytest.fixture
def collector(request, monkeypatch):
    """No external process, fixed port, TLS, proxy or nonsynthetic request."""
    from friday_telemetry.providers._otel_exporter import CHANNEL_OPTIONS

    assert CHANNEL_OPTIONS == (
        ("grpc.enable_http_proxy", 0),
        ("grpc.enable_retries", 0),
        ("grpc.max_send_message_length", 4 * 1024 * 1024),
        ("grpc.max_receive_message_length", 4 * 1024 * 1024),
    )

    received = []
    unavailable = request.node.name == "test_grpc_unavailable_reports_export_failure"
    lock = threading.Lock()

    class Collector(TraceServiceServicer):
        def Export(self, message, context):
            with lock:
                received.append(message)
            if unavailable:
                context.abort(grpc.StatusCode.UNAVAILABLE, "synthetic unavailable")
            return ExportTraceServiceResponse()

    executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="SyntheticOTLP")
    server = grpc.server(executor, maximum_concurrent_rpcs=2)
    add_TraceServiceServicer_to_server(Collector(), server)
    port = server.add_insecure_port("127.0.0.1:0")
    assert 1 <= port <= 65535
    target = f"127.0.0.1:{port}"
    actual_channel = grpc.insecure_channel
    channels = []

    def intercepted(destination, **kwargs):
        assert destination == target
        assert kwargs == {
            "options": CHANNEL_OPTIONS,
            "compression": grpc.Compression.NoCompression,
        }
        channel = actual_channel(destination, **kwargs)
        state = {"closed": False}
        actual_close = channel.close

        def close():
            actual_close()
            state["closed"] = True

        monkeypatch.setattr(channel, "close", close)
        channels.append((channel, state))
        return channel

    monkeypatch.setattr(grpc, "insecure_channel", intercepted)
    monkeypatch.setattr(
        grpc, "secure_channel", lambda *a, **k: pytest.fail("TLS forbidden")
    )
    monkeypatch.setattr(
        grpc,
        "ssl_channel_credentials",
        lambda *a, **k: pytest.fail("credentials forbidden"),
    )
    server.start()
    try:
        yield f"http://{target}", received
    finally:
        closed_by_owner = all(state["closed"] for _, state in channels)
        for channel, _ in channels:
            channel.close()
        stopped = server.stop(0).wait(1)
        assert stopped, "bounded server stop failed"
        executor.shutdown(wait=True, cancel_futures=True)
        assert not any(
            t.name.startswith("SyntheticOTLP") for t in threading.enumerate()
        )
        print(
            json.dumps(
                {
                    "node": request.node.nodeid,
                    "bind": "127.0.0.1:0",
                    "target": target,
                    "options": CHANNEL_OPTIONS,
                    "request_count": len(received),
                    "channel_count": len(channels),
                    "channels_closed_by_owner": closed_by_owner,
                    "server_stopped": bool(stopped),
                    "executor_workers_remaining": False,
                    "native_guard_covers_all_io": False,
                }
            )
        )
        assert closed_by_owner


def test_grpc_roundtrip_preserves_spans_and_events(collector):
    endpoint, requests = collector
    config = TelemetryFactoryConfig(
        provider="otel", otel=OTelConfig(exporter="otlp_grpc", endpoint=endpoint)
    )
    with create_telemetry(config) as handle:
        sink = handle.telemetry
        parent = sink.start_span("synthetic.root")
        child = sink.start_span("synthetic.child", parent)
        attributes = {
            "boolean": True,
            "min": -(2**63),
            "max": 2**63 - 1,
            "float": 1.25,
            "string": "synthetic",
        }
        sink.capture_event("synthetic.current", attributes)
        sink.end_span(child, attributes)
        sink.end_span(parent)
        sink.capture_event("synthetic.standalone", {"count": 1})
        assert handle.flush().status == "success"
        assert handle.snapshot().exported_spans == 3
    assert not handle.snapshot().worker_alive
    decoded = [
        s
        for r in requests
        for rs in r.resource_spans
        for scope in rs.scope_spans
        for s in scope.spans
    ]
    by_name = {s.name: s for s in decoded}
    root, child = by_name["synthetic.root"], by_name["synthetic.child"]
    assert not root.parent_span_id
    assert root.span_id == child.parent_span_id
    assert root.trace_id == child.trace_id
    event = child.events[0]
    assert event.name == "synthetic.current"
    assert {a.key: a.value.WhichOneof("value") for a in event.attributes} == {
        "boolean": "bool_value",
        "min": "int_value",
        "max": "int_value",
        "float": "double_value",
        "string": "string_value",
    }
    assert {
        a.key: a.value.int_value for a in event.attributes if a.key in {"min", "max"}
    } == {"min": -(2**63), "max": 2**63 - 1}
    assert by_name["synthetic.standalone"].events[0].name == "synthetic.standalone"
    assert dict(
        (a.key, a.value.string_value)
        for a in requests[0].resource_spans[0].resource.attributes
    ) == {"service.name": "friday"}


def test_grpc_unavailable_reports_export_failure(collector):
    endpoint, requests = collector
    config = TelemetryFactoryConfig(
        provider="otel", otel=OTelConfig(exporter="otlp_grpc", endpoint=endpoint)
    )
    with create_telemetry(config) as handle:
        handle.telemetry.capture_event("synthetic.unavailable", {"count": 1})
        result = handle.flush()
        assert result.status == "failure"
        assert result.snapshot.export_failures == 1
        assert result.snapshot.failed_spans == 1
        assert "127.0.0.1" not in repr(result)
        assert len(requests) == 1
    assert not handle.snapshot().worker_alive
