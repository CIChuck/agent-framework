# mypy: ignore-errors
"""
OpenTelemetry Provider.

Production-grade telemetry adapter using OpenTelemetry SDK.

Ref: Batch 3 Specification, Section 1.1
"""

import uuid
from typing import Any

from friday_telemetry.interface import TelemetryInterface


class OpenTelemetryProvider(TelemetryInterface):
    """
    Production-grade telemetry adapter using OpenTelemetry.

    Wraps OpenTelemetry SDK to provide distributed tracing and
    event recording. Supports multiple exporters (OTLP, Console, etc.).

    Example:
        # With OTLP exporter (production)
        telemetry = OpenTelemetryProvider(
            service_name="friday-agent",
            endpoint="http://localhost:4317"
        )

        # Console exporter (development)
        telemetry = OpenTelemetryProvider(
            service_name="friday-agent"
        )

    Ref: Batch 3 Specification, Section 1.1
    """

    def __init__(
        self,
        service_name: str,
        endpoint: str | None = None,
    ) -> None:
        """
        Initialize OpenTelemetry provider.

        Args:
            service_name: Name of the service (e.g., 'friday-agent')
            endpoint: OTLP collector URL. If None, uses console exporter.
        """
        self._service_name = service_name
        self._active_spans: dict[str, Any] = {}

        # Lazy import to avoid requiring OTel when not used
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import (
                BatchSpanProcessor,
                ConsoleSpanExporter,
            )

            # Create resource with service name
            resource = Resource.create({"service.name": service_name})

            # Create tracer provider
            provider = TracerProvider(resource=resource)

            # Add exporter
            if endpoint:
                try:
                    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                        OTLPSpanExporter,
                    )

                    exporter = OTLPSpanExporter(endpoint=endpoint)
                except ImportError:
                    # Fallback to console if OTLP exporter not installed
                    exporter = ConsoleSpanExporter()
            else:
                exporter = ConsoleSpanExporter()

            provider.add_span_processor(BatchSpanProcessor(exporter))
            trace.set_tracer_provider(provider)

            self._tracer = trace.get_tracer(service_name)
            self._trace_module = trace
            self._initialized = True

        except ImportError:
            # OpenTelemetry not installed - use no-op mode
            self._tracer = None
            self._trace_module = None
            self._initialized = False

    def capture_event(self, event_name: str, data: dict[str, Any]) -> None:
        """
        Records a discrete event as a span event on the current context.

        If there's an active span, the event is attached to it.
        Otherwise, the event is logged but not traced.
        """
        if not self._initialized or not self._trace_module:
            return

        current_span = self._trace_module.get_current_span()
        if current_span and current_span.is_recording():
            # Convert data values to strings for OTel attributes
            attributes = {k: str(v) for k, v in data.items()}
            current_span.add_event(event_name, attributes=attributes)

    def start_span(self, name: str, parent_id: str | None = None) -> str:
        """
        Starts a trace span and returns its unique ID.

        Args:
            name: Name of the operation
            parent_id: Optional parent span ID (not used - OTel handles context)

        Returns:
            Unique span ID for ending the span later
        """
        span_id = str(uuid.uuid4())

        if not self._initialized or not self._tracer:
            return span_id

        span = self._tracer.start_span(name)
        self._active_spans[span_id] = span

        return span_id

    def end_span(self, span_id: str, data: dict[str, Any] | None = None) -> None:
        """
        Ends a previously started span.

        Args:
            span_id: The ID returned by start_span()
            data: Optional attributes to attach before ending
        """
        if span_id not in self._active_spans:
            return

        span = self._active_spans.pop(span_id)

        if data:
            for key, value in data.items():
                span.set_attribute(key, str(value))

        span.end()
