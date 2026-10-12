"""Strict configuration, optional dependencies and caller-owned Chat injection."""

import atexit
import builtins
import inspect
import io
import threading

import pytest
from friday_chat.config import ChatTelemetryConfig, FridayChatConfig
from friday_chat.runtime import build_runtime
from friday_telemetry import (
    CompositeProvider,
    OpenTelemetryProvider,
    OTelConfig,
    TelemetryConfig,
    TelemetryFactoryConfig,
    TelemetryInitializationError,
    TelemetryInterface,
    TelemetryOperationError,
    create_telemetry,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from pydantic import ValidationError

from .test_otel_contract import managed
from .test_otel_contract import recorded as recording_fixture


@pytest.fixture
def recorded(monkeypatch):
    yield from recording_fixture.__wrapped__(monkeypatch)


def test_defaults_api_and_lazy_disabled_debug(monkeypatch):
    original_import = builtins.__import__
    initial = set(threading.enumerate())

    def forbidden_sdk(name, *args, **kwargs):
        if name.startswith(("opentelemetry", "grpc")):
            pytest.fail("disabled/debug imported optional dependencies")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", forbidden_sdk)
    with create_telemetry() as disabled:
        assert isinstance(disabled.telemetry, TelemetryInterface)
        parent = disabled.telemetry.start_span("disabled")
        child = disabled.telemetry.start_span("disabled.child", parent)
        disabled.telemetry.capture_event("disabled.event", {"count": 1})
        disabled.telemetry.end_span(child)
        disabled.telemetry.end_span(parent)
        assert not disabled.snapshot().available
    with create_telemetry(TelemetryFactoryConfig(provider="debug")) as debug:
        debug.telemetry.capture_event("synthetic", {"count": 1})
        assert debug.flush().status == "success"
    assert set(threading.enumerate()) == initial
    assert TelemetryConfig().enabled is True
    assert TelemetryConfig().otel_enabled is False
    assert ChatTelemetryConfig().enabled is False
    assert ChatTelemetryConfig().provider == "debug"
    assert TelemetryInterface.__abstractmethods__ == {
        "capture_event",
        "start_span",
        "end_span",
    }
    signature = inspect.signature(OpenTelemetryProvider)
    assert list(signature.parameters) == ["service_name", "endpoint"]
    assert signature.parameters["endpoint"].default is None


@pytest.mark.parametrize(
    "settings",
    [
        {"provider": "langfuse"},
        {"provider": 1},
        {"enabled": True},
        {"otel": {"headers": {"secret": "PRIVATE"}}},
        {"otel": {"queue_limit": "2"}},
        {"otel": {"queue_limit": True}},
        {"otel": {"queue_limit": 513}},
        {"otel": {"batch_limit": 129}},
        {"otel": {"queue_limit": 1, "batch_limit": 2}},
        {"otel": {"request_timeout_ms": float("inf")}},
        {"otel": {"service_name": "unsafe name"}},
        {"otel": {"exporter": "otlp_http"}},
        {"otel": {"endpoint": "http://127.0.0.1:1"}},
        {"otel": {"exporter": "otlp_grpc"}},
    ],
)
def test_strict_additive_models_reject_invalid_settings(settings):
    with pytest.raises(ValidationError):
        TelemetryFactoryConfig.model_validate(settings)


@pytest.mark.parametrize(
    "endpoint",
    [
        "http://remote.test:4317",
        "http://localhost:4317",
        "http://127.0.0.1",
        "ftp://127.0.0.1:1",
        "http://user:PRIVATE@127.0.0.1:1",
        "http://127.0.0.1:1/path",
        "http://127.0.0.1:1?secret=PRIVATE",
        "http://127.0.0.1:1#PRIVATE",
        "http://127.0.0.1:0",
        "http://127.0.0.1:65536",
        "https://remote.test",
        "http://[::1]:1/path",
        "http://127.0.0.1:1?",
        "http://127.0.0.1:1#",
        "http://127.0.0.1:1\n",
    ],
)
def test_destination_validation_precedes_channel(endpoint, monkeypatch):
    import grpc

    monkeypatch.setattr(
        grpc,
        "insecure_channel",
        lambda *a, **k: pytest.fail("channel before validation"),
    )
    monkeypatch.setattr(
        grpc, "secure_channel", lambda *a, **k: pytest.fail("channel before validation")
    )
    with pytest.raises(ValidationError):
        OTelConfig(exporter="otlp_grpc", endpoint=endpoint)
    with pytest.raises(TelemetryInitializationError) as caught:
        OpenTelemetryProvider("safe", endpoint)
    assert str(caught.value) == "telemetry_initialization_failed"


@pytest.mark.parametrize(
    "key",
    [
        "OTEL_EXPORTER_OTLP_HEADERS",
        "otel_python_context",
        "GRPC_DEFAULT_SSL_ROOTS_FILE_PATH",
        "grpc_ssl_cipher_suites",
        "HTTP_PROXY",
        "https_proxy",
        "ALL_PROXY",
        "no_proxy",
        "SSL_CERT_FILE",
        "ssl_cert_dir",
        "REQUESTS_CA_BUNDLE",
        "curl_ca_bundle",
    ],
)
def test_conflicting_environment_names_rejected_without_reading_values(
    key, monkeypatch
):
    from friday_telemetry.providers import otel

    monkeypatch.setattr(otel, "_environment_keys", lambda: (key,))
    monkeypatch.setattr(
        otel, "version", lambda *a: pytest.fail("SDK before environment check")
    )
    with pytest.raises(TelemetryInitializationError) as caught:
        create_telemetry(TelemetryFactoryConfig(provider="otel"))
    assert str(caught.value) == "telemetry_initialization_failed"
    assert key not in str(caught.value)


def test_missing_sdk_legacy_noop_and_explicit_factory_safe_failure(monkeypatch):
    original_import = builtins.__import__

    def missing(name, *a, **k):
        if name.startswith("opentelemetry"):
            raise ImportError("PRIVATE")
        return original_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", missing)
    legacy = OpenTelemetryProvider("safe")
    try:
        span = legacy.start_span("safe")
        child = legacy.start_span("safe.child", span)
        legacy.capture_event("safe.event", {})
        legacy.end_span(child)
        legacy.end_span(span)
        assert not legacy.snapshot().available
    finally:
        legacy.shutdown()
    with pytest.raises(TelemetryInitializationError) as caught:
        create_telemetry(TelemetryFactoryConfig(provider="otel"))
    assert str(caught.value) == "telemetry_initialization_failed"


def test_incompatible_sdk_rejected(monkeypatch):
    from friday_telemetry.providers import otel

    monkeypatch.setattr(otel, "version", lambda name: "1.20.0")
    with pytest.raises(
        TelemetryInitializationError, match="telemetry_initialization_failed"
    ):
        create_telemetry(TelemetryFactoryConfig(provider="otel"))


def test_missing_explicit_exporter_never_falls_back(monkeypatch):
    from friday_telemetry.providers import _otel_exporter

    original_import = builtins.__import__

    def missing(name, *a, **k):
        if name.startswith("opentelemetry.exporter"):
            raise ImportError("PRIVATE exporter exception")
        return original_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", missing)
    monkeypatch.setattr(
        _otel_exporter,
        "SafeConsoleExporter",
        lambda *a: pytest.fail("silent console fallback"),
    )
    settings = TelemetryFactoryConfig(
        provider="otel",
        otel=OTelConfig(exporter="otlp_grpc", endpoint="http://127.0.0.1:4317"),
    )
    with pytest.raises(TelemetryInitializationError) as caught:
        create_telemetry(settings)
    assert "PRIVATE" not in str(caught.value)


@pytest.mark.parametrize("secure", [False, True])
def test_public_grpc_transport_arguments_encoder_and_no_loaders(secure, monkeypatch):
    import grpc
    from friday_telemetry.providers._otel_exporter import CHANNEL_OPTIONS
    from opentelemetry.exporter.otlp.proto.grpc import exporter as sdk_exporter
    from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
        ExportTraceServiceResponse,
    )

    calls, requests = [], []
    assert CHANNEL_OPTIONS == (
        ("grpc.enable_http_proxy", 0),
        ("grpc.enable_retries", 0),
        ("grpc.max_send_message_length", 4 * 1024 * 1024),
        ("grpc.max_receive_message_length", 4 * 1024 * 1024),
    )

    class Channel:
        closed = False

        def unary_unary(self, method, **kwargs):
            assert (
                method == "/opentelemetry.proto.collector.trace.v1.TraceService/Export"
            )

            def rpc(request, **options):
                requests.append(request)
                assert options["timeout"] == 1
                assert options["compression"] == grpc.Compression.NoCompression
                assert options["wait_for_ready"] is False
                return ExportTraceServiceResponse()

            return rpc

        def close(self):
            self.closed = True

    channel = Channel()

    def credentials(**kwargs):
        assert kwargs == {
            "root_certificates": None,
            "private_key": None,
            "certificate_chain": None,
        }
        calls.append("native-default-public-root-policy-mocked")
        return "synthetic-credentials"

    def transport(target, *args, **kwargs):
        assert target == ("example.test:443" if secure else "127.0.0.1:4317")
        assert kwargs == {
            "options": CHANNEL_OPTIONS,
            "compression": grpc.Compression.NoCompression,
        }
        assert args == (("synthetic-credentials",) if secure else ())
        calls.append(target)
        return channel

    monkeypatch.setattr(
        grpc,
        "ssl_channel_credentials",
        credentials
        if secure
        else lambda **k: pytest.fail("insecure branch credentials"),
    )
    monkeypatch.setattr(
        grpc,
        "secure_channel",
        transport if secure else lambda *a, **k: pytest.fail("wrong secure branch"),
    )
    monkeypatch.setattr(
        grpc,
        "insecure_channel",
        transport if not secure else lambda *a, **k: pytest.fail("plaintext fallback"),
    )
    monkeypatch.setattr(
        Resource, "create", lambda *a, **k: pytest.fail("resource detector")
    )
    for loader in ["_get_credentials", "_load_credentials", "_read_file"]:
        monkeypatch.setattr(
            sdk_exporter,
            loader,
            lambda *a, **k: pytest.fail("forbidden credential/file loader"),
        )
    monkeypatch.setattr(
        atexit, "register", lambda *a, **k: pytest.fail("SDK atexit ownership")
    )
    endpoint = "https://example.test:443" if secure else "http://127.0.0.1:4317"
    with managed(exporter="otlp_grpc", endpoint=endpoint) as handle:
        handle.telemetry.capture_event(
            "scalar", {"min": -(2**63), "max": 2**63 - 1, "boolean": True}
        )
        assert handle.flush().status == "success"
    assert channel.closed
    assert len(requests) == 1
    attributes = (
        requests[0].resource_spans[0].scope_spans[0].spans[0].events[0].attributes
    )
    assert {a.key: a.value.WhichOneof("value") for a in attributes} == {
        "min": "int_value",
        "max": "int_value",
        "boolean": "bool_value",
    }


def test_mocked_tls_failure_no_plaintext_fallback_or_exception_content(monkeypatch):
    import grpc

    def unavailable(**kwargs):
        raise RuntimeError("PRIVATE root exception")

    monkeypatch.setattr(grpc, "ssl_channel_credentials", unavailable)
    monkeypatch.setattr(
        grpc, "insecure_channel", lambda *a, **k: pytest.fail("plaintext fallback")
    )
    with pytest.raises(TelemetryInitializationError) as caught:
        managed(exporter="otlp_grpc", endpoint="https://example.test:443")
    assert str(caught.value) == "telemetry_initialization_failed"


def test_constructor_failure_releases_partial_owned_state(monkeypatch):
    from friday_telemetry.providers import _otel_exporter

    closed = []

    class Exporter:
        def shutdown(self):
            closed.append(True)

    monkeypatch.setattr(
        _otel_exporter, "SafeConsoleExporter", lambda stream: Exporter()
    )
    monkeypatch.setattr(
        TracerProvider,
        "get_tracer",
        lambda *a: (_ for _ in ()).throw(RuntimeError("PRIVATE")),
    )
    with pytest.raises(TelemetryInitializationError) as caught:
        managed()
    assert closed == [True]
    assert "PRIVATE" not in str(caught.value)


def test_real_chat_observer_two_providers_borrowed_ownership_and_privacy(recorded):
    secret = "PRIVATE_PROMPT_REASONING_ARGUMENT_RESULT_EXCEPTION"
    with managed() as first, managed() as second:
        composite = CompositeProvider([first.telemetry, second.telemetry])
        runtime = build_runtime(
            FridayChatConfig(), session_id=secret, telemetry=composite
        )
        observer = runtime.telemetry
        parent = observer.start_span("chat.runtime")
        child = observer.start_span("chat.application", parent)
        observer.emit("application_start")
        observer.capture_event(
            "unknown",
            {
                "prompt": secret,
                "reasoning": secret,
                "arguments": {"key": secret},
                "result": secret,
            },
        )
        observer.end_span(child, {"outcome": "succeeded", "count": 1})
        observer.end_span(parent, {"outcome": "succeeded"})
        assert first.flush().status == second.flush().status == "success"
        assert not first.snapshot().closed and not second.snapshot().closed
        assert secret not in repr(observer.snapshot())
        assert observer.snapshot().rejected_count == 1
        first.shutdown()
        observer.emit("application_stop")
        assert observer.snapshot().state == "failed"
        assert observer.snapshot().failure_count >= 1
        assert secret not in repr(first.snapshot()) + repr(second.snapshot())
    assert secret not in "".join(s.to_json() for s in recorded)
    spans = [s for s in recorded if s.name == "chat.application"]
    parents = [s for s in recorded if s.name == "chat.runtime"]
    assert len(spans) == len(parents) == 2
    assert {s.parent.span_id for s in spans} == {s.context.span_id for s in parents}


@pytest.mark.parametrize("timeout", [0, -1, True, 1.5])
def test_invalid_lifecycle_budget_rejected(recorded, timeout):
    with managed() as handle:
        with pytest.raises(TelemetryOperationError, match="invalid_input"):
            handle.flush(timeout)
        with pytest.raises(TelemetryOperationError, match="invalid_input"):
            handle.shutdown(timeout)


def test_owned_context_manager_keeps_console_stream_open(monkeypatch):
    stream = io.StringIO()
    monkeypatch.setattr("sys.stdout", stream)
    with managed() as handle:
        handle.telemetry.capture_event("safe", {})
    assert not stream.closed
    assert not handle.snapshot().worker_alive
