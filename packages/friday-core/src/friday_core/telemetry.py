"""
Telemetry Interfaces and Debug Recorders.
Defines TelemetryInterface protocol for white-box testing.

Ref: Batch 0 Specification, Section 4.3
"""

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


class TelemetryInterface(ABC):
    """
    Protocol for telemetry and inspection hooks.

    Allows inspecting internal decision-making during tests without
    breaking encapsulation. Components accept an optional telemetry
    recorder via constructor injection.

    Example:
        recorder = DebugTelemetryRecorder()
        controller = MemoryController(..., telemetry=recorder)
        await controller.recall("test")
        assert "vector_search" in [e["name"] for e in recorder.events]
    """

    @abstractmethod
    def capture_event(self, event_name: str, data: dict[str, Any]) -> None:
        """
        Records a discrete event.

        Args:
            event_name: Identifier for the event type (e.g., 'memory_recall', 'tool_usage')
            data: Arbitrary event data to record
        """
        pass

    @abstractmethod
    def start_span(self, name: str, parent_id: str | None = None) -> str:
        """
        Starts a trace span for duration tracking.

        Args:
            name: Name of the operation being traced
            parent_id: Optional parent span ID for nested traces

        Returns:
            span_id: Unique identifier for this span, used to end it later
        """
        pass

    @abstractmethod
    def end_span(self, span_id: str, data: dict[str, Any] | None = None) -> None:
        """
        Ends a previously started span.

        Args:
            span_id: The ID returned by start_span()
            data: Optional final data to attach (e.g., result, error)
        """
        pass


@dataclass
class SpanRecord:
    """Internal record of a trace span."""

    name: str
    parent_id: str | None
    start_time: float
    end_time: float | None = None
    data: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float | None:
        """Duration in milliseconds, or None if span hasn't ended."""
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000


@dataclass
class EventRecord:
    """Internal record of a discrete event."""

    name: str
    data: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class DebugTelemetryRecorder(TelemetryInterface):
    """
    In-memory telemetry recorder for white-box testing.

    Captures all events and spans in memory for test assertions.
    Not intended for production use.

    Example:
        recorder = DebugTelemetryRecorder()
        controller = MemoryController(..., telemetry=recorder)
        await controller.recall("test query")

        # Assert on captured events
        assert recorder.get_event("vector_search") is not None
        assert recorder.get_event("vector_search")["latency"] < 0.5

        # Assert on spans
        span = recorder.get_span_by_name("recall_operation")
        assert span.duration_ms < 1000
    """

    def __init__(self) -> None:
        self.events: list[EventRecord] = []
        self.spans: dict[str, SpanRecord] = {}

    def capture_event(self, event_name: str, data: dict[str, Any]) -> None:
        """Records a discrete event to the in-memory list."""
        self.events.append(EventRecord(name=event_name, data=data))

    def start_span(self, name: str, parent_id: str | None = None) -> str:
        """Starts a span and returns its unique ID."""
        span_id = str(uuid.uuid4())
        self.spans[span_id] = SpanRecord(
            name=name,
            parent_id=parent_id,
            start_time=time.perf_counter(),
        )
        return span_id

    def end_span(self, span_id: str, data: dict[str, Any] | None = None) -> None:
        """Ends a span, recording the end time and optional data."""
        if span_id in self.spans:
            self.spans[span_id].end_time = time.perf_counter()
            if data:
                self.spans[span_id].data = data

    # --- Test Helper Methods ---

    def get_event(self, event_name: str) -> dict[str, Any] | None:
        """
        Retrieves the data from the first event with the given name.

        Args:
            event_name: The event name to search for

        Returns:
            The event data dict, or None if not found
        """
        for event in self.events:
            if event.name == event_name:
                return event.data
        return None

    def get_all_events(self, event_name: str) -> list[dict[str, Any]]:
        """
        Retrieves data from all events with the given name.

        Args:
            event_name: The event name to search for

        Returns:
            List of event data dicts
        """
        return [event.data for event in self.events if event.name == event_name]

    def get_span_by_name(self, name: str) -> SpanRecord | None:
        """
        Retrieves the first span with the given name.

        Args:
            name: The span name to search for

        Returns:
            The SpanRecord, or None if not found
        """
        for span in self.spans.values():
            if span.name == name:
                return span
        return None

    def get_span(self, span_id: str) -> SpanRecord | None:
        """
        Retrieves a span by its ID.

        Args:
            span_id: The span ID returned by start_span()

        Returns:
            The SpanRecord, or None if not found
        """
        return self.spans.get(span_id)

    def clear(self) -> None:
        """Clears all recorded events and spans."""
        self.events.clear()
        self.spans.clear()

    @property
    def event_names(self) -> list[str]:
        """Returns a list of all captured event names."""
        return [event.name for event in self.events]


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
