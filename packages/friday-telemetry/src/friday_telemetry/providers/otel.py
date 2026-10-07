"""Instance-owned OpenTelemetry adapter; no ambient or global SDK ownership."""

from __future__ import annotations

import math
import os
import sys
import threading
import time
import uuid
from contextvars import ContextVar
from dataclasses import replace
from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING, Any

from friday_telemetry.config import _SAFE_NAME, OTelConfig
from friday_telemetry.interface import TelemetryInterface
from friday_telemetry.lifecycle import (
    LifecycleResult,
    TelemetryInitializationError,
    TelemetryOperationError,
    TelemetrySnapshot,
    _timeout_seconds,
)

if TYPE_CHECKING:
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.trace import Span, Tracer

    from friday_telemetry.providers._otel_processor import OwnedSpanProcessor

_MAX_COUNT = 2**63 - 1
_CERTIFICATE_KEYS = {
    "SSL_CERT_FILE",
    "SSL_CERT_DIR",
    "REQUESTS_CA_BUNDLE",
    "CURL_CA_BUNDLE",
}
_PROXY_KEYS = {"HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY"}


def _environment_keys() -> tuple[str, ...]:
    """Only enumerate names: never read, export or rewrite environment values."""
    return tuple(os.environ)


def _check_environment() -> None:
    for name in _environment_keys():
        key = name.upper()
        if key.startswith(("OTEL_", "GRPC_")) or key in _CERTIFICATE_KEYS | _PROXY_KEYS:
            raise TelemetryInitializationError()


def _name(value: object) -> str:
    if type(value) is not str or not _SAFE_NAME.fullmatch(value):
        raise TelemetryOperationError("invalid_input")
    return value


def _attributes(data: object) -> dict[str, bool | int | float | str]:
    """Validate the deliberately dynamic TelemetryInterface dictionary boundary."""
    if type(data) is not dict or len(data) > 64:
        raise TelemetryOperationError("invalid_input")
    result: dict[str, bool | int | float | str] = {}
    for key, value in data.items():
        safe_key = _name(key)
        if (
            type(value) is bool
            or type(value) is int
            and -(2**63) <= value <= 2**63 - 1
            or type(value) is float
            and math.isfinite(value)
        ):
            result[safe_key] = value
        elif type(value) is str:
            try:
                length = len(value.encode("utf-8"))
            except UnicodeError:
                raise TelemetryOperationError("invalid_input") from None
            if length > 1024:
                raise TelemetryOperationError("invalid_input")
            result[safe_key] = value
        else:
            raise TelemetryOperationError("invalid_input")
    return result


class OpenTelemetryProvider(TelemetryInterface):
    """Keep the legacy constructor; factory creation requires optional SDK support."""

    def __init__(self, service_name: str, endpoint: str | None = None) -> None:
        try:
            settings = OTelConfig(
                service_name=service_name,
                exporter="otlp_grpc" if endpoint is not None else "console",
                endpoint=endpoint,
            )
        except Exception:
            raise TelemetryInitializationError() from None
        self._initialize(settings, required=endpoint is not None)

    @classmethod
    def _from_settings(cls, settings: OTelConfig) -> OpenTelemetryProvider:
        provider = cls.__new__(cls)
        provider._initialize(settings, required=True)
        return provider

    def _initialize(self, settings: OTelConfig, *, required: bool) -> None:
        _check_environment()
        self._lock = threading.RLock()
        self._shutdown_lock = threading.Lock()
        self._stack: ContextVar[tuple[str, ...]] = ContextVar(
            "friday_telemetry_spans", default=()
        )
        self._active_spans: dict[str, Span] = {}
        self._processor: OwnedSpanProcessor | None = None
        self._provider: TracerProvider | None = None
        self._tracer: Tracer | None = None
        self._closed = False
        self._cancelled = 0
        self._invalid = 0
        self._shutdown_result: LifecycleResult | None = None
        try:
            distributions = ["opentelemetry-api", "opentelemetry-sdk"]
            if settings.exporter == "otlp_grpc":
                distributions.extend(
                    [
                        "opentelemetry-exporter-otlp-proto-common",
                        "opentelemetry-exporter-otlp-proto-grpc",
                        "opentelemetry-proto",
                    ]
                )
            for distribution in distributions:
                if version(distribution) != "1.39.1":
                    raise TelemetryInitializationError()
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace import SpanLimits, TracerProvider
            from opentelemetry.sdk.trace.sampling import ALWAYS_ON

            from friday_telemetry.providers._otel_exporter import (
                OwnedGrpcExporter,
                SafeConsoleExporter,
            )
            from friday_telemetry.providers._otel_processor import OwnedSpanProcessor

            exporter = (
                OwnedGrpcExporter(settings)
                if settings.exporter == "otlp_grpc"
                else SafeConsoleExporter(sys.stdout)
            )
            try:
                limits = SpanLimits(
                    max_attributes=64,
                    max_span_attributes=64,
                    max_event_attributes=64,
                    max_link_attributes=64,
                    max_events=128,
                    max_links=0,
                    max_attribute_length=1024,
                    max_span_attribute_length=1024,
                )
                self._provider = TracerProvider(
                    resource=Resource({"service.name": settings.service_name}),
                    sampler=ALWAYS_ON,
                    span_limits=limits,
                    shutdown_on_exit=False,
                )
                self._tracer = self._provider.get_tracer(settings.service_name)
                self._processor = OwnedSpanProcessor(exporter, settings)
                self._provider.add_span_processor(self._processor)
            except Exception:
                exporter.shutdown()
                raise
        except (ImportError, PackageNotFoundError):
            if self._processor is not None:
                self._processor.shutdown_result()
            self._tracer = None
            self._provider = None
            self._processor = None
            if required:
                raise TelemetryInitializationError() from None
        except Exception:
            if self._processor is not None:
                self._processor.shutdown_result()
            raise TelemetryInitializationError() from None

    def _live_stack(self) -> tuple[str, ...]:
        stack = tuple(s for s in self._stack.get() if s in self._active_spans)
        self._stack.set(stack)
        return stack

    def _check_open(self) -> None:
        if self._closed:
            raise TelemetryOperationError("closed")

    def _invalid_input(self) -> None:
        self._invalid = min(_MAX_COUNT, self._invalid + 1)

    def start_span(self, name: str, parent_id: str | None = None) -> str:
        with self._lock:
            self._check_open()
            try:
                safe_name = _name(name)
                if self._tracer is None:
                    return str(uuid.uuid4())
                if parent_id is not None and (
                    type(parent_id) is not str or parent_id not in self._active_spans
                ):
                    raise TelemetryOperationError("invalid_parent")
                if len(self._active_spans) >= 128:
                    raise TelemetryOperationError("active_limit")
            except TelemetryOperationError:
                self._invalid_input()
                raise
            span_id = str(uuid.uuid4())
            from opentelemetry.context import Context
            from opentelemetry.trace import set_span_in_context

            stack = self._live_stack()
            resolved = (
                parent_id if parent_id is not None else (stack[-1] if stack else None)
            )
            context = Context()
            if resolved is not None:
                context = set_span_in_context(self._active_spans[resolved], context)
            self._active_spans[span_id] = self._tracer.start_span(
                safe_name, context=context
            )
            self._stack.set(stack + (span_id,))
            return span_id

    def capture_event(self, event_name: str, data: dict[str, Any]) -> None:
        with self._lock:
            self._check_open()
            try:
                name, attributes = _name(event_name), _attributes(data)
            except TelemetryOperationError:
                self._invalid_input()
                raise
            if self._tracer is None:
                return
            stack = self._live_stack()
            if stack:
                self._active_spans[stack[-1]].add_event(name, attributes=attributes)
            else:
                if len(self._active_spans) >= 128:
                    self._invalid_input()
                    raise TelemetryOperationError("active_limit")
                from opentelemetry.context import Context

                span = self._tracer.start_span(name, context=Context())
                span.add_event(name, attributes=attributes)
                span.end()

    def end_span(self, span_id: str, data: dict[str, Any] | None = None) -> None:
        with self._lock:
            if type(span_id) is not str or span_id not in self._active_spans:
                return
            try:
                attributes = _attributes(data) if data is not None else {}
            except TelemetryOperationError:
                self._invalid_input()
                raise
            span = self._active_spans.pop(span_id)
            for key, value in attributes.items():
                span.set_attribute(key, value)
            span.end()
            self._live_stack()

    def snapshot(self) -> TelemetrySnapshot:
        with self._lock:
            snap = (
                self._processor.snapshot()
                if self._processor
                else TelemetrySnapshot(available=False)
            )
            return replace(
                snap,
                closed=self._closed,
                active_spans=len(self._active_spans),
                cancelled_spans=self._cancelled,
                invalid_inputs=self._invalid,
            )

    def flush(self, timeout_millis: int = 5000) -> LifecycleResult:
        _timeout_seconds(timeout_millis)
        if self._closed:
            return LifecycleResult("closed", self.snapshot())
        if self._processor is None:
            return LifecycleResult("failure", self.snapshot())
        result = self._processor.flush_result(timeout_millis)
        return LifecycleResult(result.status, self.snapshot())

    def shutdown(self, timeout_millis: int = 5000) -> LifecycleResult:
        deadline = time.monotonic() + _timeout_seconds(timeout_millis)
        if not self._shutdown_lock.acquire(timeout=max(0, deadline - time.monotonic())):
            return LifecycleResult("timeout", self.snapshot())
        try:
            if self._shutdown_result is not None:
                return self._shutdown_result
            with self._lock:
                self._closed = True
                if self._active_spans:
                    from opentelemetry.trace import Status, StatusCode

                    for span in self._active_spans.values():
                        span.set_status(Status(StatusCode.ERROR, "cancelled"))
                        span.end()
                    self._cancelled = min(
                        _MAX_COUNT, self._cancelled + len(self._active_spans)
                    )
                    self._active_spans.clear()
                    self._stack.set(())
            status = (
                self._processor.shutdown_until(deadline).status
                if self._processor is not None
                else "failure"
            )
            self._shutdown_result = LifecycleResult(status, self.snapshot())
            return self._shutdown_result
        finally:
            self._shutdown_lock.release()
