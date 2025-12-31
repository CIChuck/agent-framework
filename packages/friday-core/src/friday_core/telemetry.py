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
