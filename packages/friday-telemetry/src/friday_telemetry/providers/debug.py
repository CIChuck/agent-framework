"""
Debug Telemetry Recorder.

In-memory recorder for white-box testing.

Ref: Batch 0 Specification, Section 4.3
"""

import time
import uuid
from typing import Any

from friday_telemetry.interface import TelemetryInterface
from friday_telemetry.records import EventRecord, SpanRecord


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
