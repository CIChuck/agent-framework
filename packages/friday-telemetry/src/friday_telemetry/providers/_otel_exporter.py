"""Owned exporters without SDK endpoint/env loaders or exception logging."""

import threading
from collections.abc import Sequence
from typing import TextIO

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

from friday_telemetry.config import OTelConfig, _endpoint_target

CHANNEL_OPTIONS = (
    ("grpc.enable_http_proxy", 0),
    ("grpc.enable_retries", 0),
    ("grpc.max_send_message_length", 4 * 1024 * 1024),
    ("grpc.max_receive_message_length", 4 * 1024 * 1024),
)


class OwnedGrpcExporter(SpanExporter):
    """One explicit channel, finite RPC deadlines and fixed native retry disable."""

    def __init__(self, settings: OTelConfig) -> None:
        import grpc
        from opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans
        from opentelemetry.proto.collector.trace.v1.trace_service_pb2_grpc import (
            TraceServiceStub,
        )

        if settings.endpoint is None:
            raise ValueError("missing_telemetry_destination")
        secure, target = _endpoint_target(settings.endpoint)
        self._timeout = settings.request_timeout_ms / 1000
        self._lock = threading.Lock()
        self._closed = False
        self._encode = encode_spans
        self._compression = grpc.Compression.NoCompression
        if secure:
            credentials = grpc.ssl_channel_credentials(
                root_certificates=None, private_key=None, certificate_chain=None
            )
            self._channel = grpc.secure_channel(
                target,
                credentials,
                options=CHANNEL_OPTIONS,
                compression=grpc.Compression.NoCompression,
            )
        else:
            self._channel = grpc.insecure_channel(
                target,
                options=CHANNEL_OPTIONS,
                compression=grpc.Compression.NoCompression,
            )
        try:
            self._stub = TraceServiceStub(self._channel)
        except Exception:
            self._channel.close()
            raise

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        with self._lock:
            if self._closed:
                return SpanExportResult.FAILURE
        try:
            response = self._stub.Export(
                self._encode(spans),
                timeout=self._timeout,
                compression=self._compression,
                wait_for_ready=False,
            )
            if response.partial_success.rejected_spans:
                return SpanExportResult.FAILURE
            return SpanExportResult.SUCCESS
        except Exception:
            return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
        self._channel.close()

    def force_flush(self, timeout_millis: int = 5000) -> bool:
        with self._lock:
            return not self._closed


class SafeConsoleExporter(SpanExporter):
    """Uses a caller stream without closing it or logging writer exceptions."""

    def __init__(self, stream: TextIO) -> None:
        self._stream = stream
        self._closed = False
        self._lock = threading.Lock()

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        with self._lock:
            if self._closed:
                return SpanExportResult.FAILURE
        try:
            for span in spans:
                self._stream.write(span.to_json() + "\n")
            self._stream.flush()
            return SpanExportResult.SUCCESS
        except Exception:
            return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        with self._lock:
            self._closed = True

    def force_flush(self, timeout_millis: int = 5000) -> bool:
        with self._lock:
            return not self._closed
