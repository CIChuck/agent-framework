"""
Tests for telemetry interfaces and debug recorder.

Tests cover:
- TelemetryInterface protocol
- DebugTelemetryRecorder implementation
- Event capture and retrieval
- Span lifecycle (start/end)
- Test helper methods

Ref: Batch 0 Specification, Section 4.3
Ref: Batch 0 Acceptance Criteria #6
"""

import time

import pytest

from friday_core import (
    DebugTelemetryRecorder,
    EventRecord,
    SpanRecord,
    TelemetryInterface,
)


class TestTelemetryInterface:
    """Tests for the TelemetryInterface protocol."""

    def test_interface_is_abstract(self):
        """Test that TelemetryInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            TelemetryInterface()

    def test_interface_defines_capture_event(self):
        """Test that interface defines capture_event method."""
        assert hasattr(TelemetryInterface, "capture_event")

    def test_interface_defines_start_span(self):
        """Test that interface defines start_span method."""
        assert hasattr(TelemetryInterface, "start_span")

    def test_interface_defines_end_span(self):
        """Test that interface defines end_span method."""
        assert hasattr(TelemetryInterface, "end_span")


class TestDebugTelemetryRecorder:
    """Tests for the DebugTelemetryRecorder implementation."""

    def test_implements_interface(self):
        """Test that DebugTelemetryRecorder implements TelemetryInterface."""
        recorder = DebugTelemetryRecorder()
        assert isinstance(recorder, TelemetryInterface)

    def test_initial_state_empty(self):
        """Test that recorder starts with empty events and spans."""
        recorder = DebugTelemetryRecorder()

        assert recorder.events == []
        assert recorder.spans == {}

    def test_capture_event(self):
        """Test capturing a simple event."""
        recorder = DebugTelemetryRecorder()

        recorder.capture_event("test_event", {"key": "value"})

        assert len(recorder.events) == 1
        assert recorder.events[0].name == "test_event"
        assert recorder.events[0].data == {"key": "value"}

    def test_capture_multiple_events(self):
        """Test capturing multiple events."""
        recorder = DebugTelemetryRecorder()

        recorder.capture_event("event_1", {"index": 1})
        recorder.capture_event("event_2", {"index": 2})
        recorder.capture_event("event_3", {"index": 3})

        assert len(recorder.events) == 3
        assert recorder.events[0].name == "event_1"
        assert recorder.events[1].name == "event_2"
        assert recorder.events[2].name == "event_3"

    def test_event_has_timestamp(self):
        """Test that events have timestamp."""
        recorder = DebugTelemetryRecorder()

        recorder.capture_event("timed_event", {})

        assert recorder.events[0].timestamp is not None


class TestSpanLifecycle:
    """Tests for span start/end lifecycle."""

    def test_start_span_returns_id(self):
        """Test that start_span returns a unique span ID."""
        recorder = DebugTelemetryRecorder()

        span_id = recorder.start_span("test_span")

        assert span_id is not None
        assert isinstance(span_id, str)
        assert len(span_id) > 0

    def test_start_span_creates_record(self):
        """Test that start_span creates a SpanRecord."""
        recorder = DebugTelemetryRecorder()

        span_id = recorder.start_span("my_span")

        assert span_id in recorder.spans
        span = recorder.spans[span_id]
        assert span.name == "my_span"
        assert span.start_time is not None
        assert span.end_time is None  # Not ended yet

    def test_start_span_with_parent(self):
        """Test starting a span with a parent ID."""
        recorder = DebugTelemetryRecorder()

        parent_id = recorder.start_span("parent_span")
        child_id = recorder.start_span("child_span", parent_id=parent_id)

        child_span = recorder.spans[child_id]
        assert child_span.parent_id == parent_id

    def test_end_span(self):
        """Test ending a span."""
        recorder = DebugTelemetryRecorder()

        span_id = recorder.start_span("ending_span")
        recorder.end_span(span_id)

        span = recorder.spans[span_id]
        assert span.end_time is not None

    def test_end_span_with_data(self):
        """Test ending a span with additional data."""
        recorder = DebugTelemetryRecorder()

        span_id = recorder.start_span("data_span")
        recorder.end_span(span_id, data={"result": "success", "count": 42})

        span = recorder.spans[span_id]
        assert span.data == {"result": "success", "count": 42}

    def test_span_duration(self):
        """Test that span duration is calculated correctly."""
        recorder = DebugTelemetryRecorder()

        span_id = recorder.start_span("duration_span")
        time.sleep(0.01)  # 10ms delay
        recorder.end_span(span_id)

        span = recorder.spans[span_id]
        assert span.duration_ms is not None
        assert span.duration_ms >= 10  # At least 10ms

    def test_span_duration_none_before_end(self):
        """Test that duration is None before span ends."""
        recorder = DebugTelemetryRecorder()

        span_id = recorder.start_span("unended_span")

        span = recorder.spans[span_id]
        assert span.duration_ms is None

    def test_end_nonexistent_span(self):
        """Test that ending a nonexistent span doesn't raise."""
        recorder = DebugTelemetryRecorder()

        # Should not raise
        recorder.end_span("nonexistent_id")


class TestHelperMethods:
    """Tests for test helper methods on DebugTelemetryRecorder."""

    def test_get_event(self):
        """Test get_event retrieves event data."""
        recorder = DebugTelemetryRecorder()

        recorder.capture_event("target_event", {"found": True})
        recorder.capture_event("other_event", {"found": False})

        data = recorder.get_event("target_event")

        assert data == {"found": True}

    def test_get_event_not_found(self):
        """Test get_event returns None for missing event."""
        recorder = DebugTelemetryRecorder()

        recorder.capture_event("existing_event", {})

        data = recorder.get_event("missing_event")

        assert data is None

    def test_get_event_returns_first_match(self):
        """Test that get_event returns the first matching event."""
        recorder = DebugTelemetryRecorder()

        recorder.capture_event("duplicate", {"version": 1})
        recorder.capture_event("duplicate", {"version": 2})

        data = recorder.get_event("duplicate")

        assert data == {"version": 1}

    def test_get_all_events(self):
        """Test get_all_events retrieves all matching events."""
        recorder = DebugTelemetryRecorder()

        recorder.capture_event("multi", {"index": 1})
        recorder.capture_event("other", {"index": 99})
        recorder.capture_event("multi", {"index": 2})
        recorder.capture_event("multi", {"index": 3})

        events = recorder.get_all_events("multi")

        assert len(events) == 3
        assert events[0] == {"index": 1}
        assert events[1] == {"index": 2}
        assert events[2] == {"index": 3}

    def test_get_span_by_name(self):
        """Test get_span_by_name retrieves a span."""
        recorder = DebugTelemetryRecorder()

        recorder.start_span("target_span")
        recorder.start_span("other_span")

        span = recorder.get_span_by_name("target_span")

        assert span is not None
        assert span.name == "target_span"

    def test_get_span_by_name_not_found(self):
        """Test get_span_by_name returns None for missing span."""
        recorder = DebugTelemetryRecorder()

        span = recorder.get_span_by_name("missing_span")

        assert span is None

    def test_get_span_by_id(self):
        """Test get_span retrieves span by ID."""
        recorder = DebugTelemetryRecorder()

        span_id = recorder.start_span("id_span")

        span = recorder.get_span(span_id)

        assert span is not None
        assert span.name == "id_span"

    def test_get_span_by_id_not_found(self):
        """Test get_span returns None for missing ID."""
        recorder = DebugTelemetryRecorder()

        span = recorder.get_span("missing_id")

        assert span is None

    def test_event_names_property(self):
        """Test event_names property returns all event names."""
        recorder = DebugTelemetryRecorder()

        recorder.capture_event("event_a", {})
        recorder.capture_event("event_b", {})
        recorder.capture_event("event_a", {})

        names = recorder.event_names

        assert names == ["event_a", "event_b", "event_a"]

    def test_clear(self):
        """Test clear removes all events and spans."""
        recorder = DebugTelemetryRecorder()

        recorder.capture_event("event", {})
        recorder.start_span("span")

        recorder.clear()

        assert recorder.events == []
        assert recorder.spans == {}


class TestDataClasses:
    """Tests for SpanRecord and EventRecord data classes."""

    def test_span_record_fields(self):
        """Test SpanRecord has expected fields."""
        span = SpanRecord(
            name="test",
            parent_id="parent",
            start_time=1000.0,
            end_time=1005.0,
            data={"key": "value"},
        )

        assert span.name == "test"
        assert span.parent_id == "parent"
        assert span.start_time == 1000.0
        assert span.end_time == 1005.0
        assert span.data == {"key": "value"}

    def test_span_record_duration_calculation(self):
        """Test SpanRecord duration_ms property."""
        span = SpanRecord(
            name="test",
            parent_id=None,
            start_time=1.0,
            end_time=1.5,
        )

        assert span.duration_ms == 500.0  # 0.5 seconds = 500ms

    def test_event_record_fields(self):
        """Test EventRecord has expected fields."""
        event = EventRecord(name="test_event", data={"key": "value"})

        assert event.name == "test_event"
        assert event.data == {"key": "value"}
        assert event.timestamp is not None


class TestTelemetryInjection:
    """Tests demonstrating telemetry injection pattern (Batch 0 requirement)."""

    def test_component_with_telemetry(self):
        """Test that components can accept telemetry via constructor."""

        # Example component using telemetry injection
        class MockComponent:
            def __init__(self, telemetry: TelemetryInterface | None = None):
                self._telemetry = telemetry

            def do_work(self):
                if self._telemetry:
                    self._telemetry.capture_event("work_done", {"status": "success"})
                return "completed"

        # Test without telemetry
        component_no_telemetry = MockComponent()
        result = component_no_telemetry.do_work()
        assert result == "completed"

        # Test with telemetry
        recorder = DebugTelemetryRecorder()
        component_with_telemetry = MockComponent(telemetry=recorder)
        result = component_with_telemetry.do_work()

        assert result == "completed"
        assert recorder.get_event("work_done") == {"status": "success"}

    def test_component_emits_span(self):
        """Test that components can emit spans for timing."""

        class TimedComponent:
            def __init__(self, telemetry: TelemetryInterface | None = None):
                self._telemetry = telemetry

            def expensive_operation(self):
                span_id = None
                if self._telemetry:
                    span_id = self._telemetry.start_span("expensive_op")

                # Simulate work
                time.sleep(0.01)
                result = "done"

                if self._telemetry and span_id:
                    self._telemetry.end_span(span_id, {"result": result})

                return result

        recorder = DebugTelemetryRecorder()
        component = TimedComponent(telemetry=recorder)
        result = component.expensive_operation()

        assert result == "done"
        span = recorder.get_span_by_name("expensive_op")
        assert span is not None
        assert span.duration_ms >= 10
        assert span.data["result"] == "done"
