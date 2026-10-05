# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Tests for telemetry providers."""

from friday_telemetry import (
    CompositeProvider,
    DebugTelemetryRecorder,
    OpenTelemetryProvider,
)


class TestDebugTelemetryRecorder:
    """Tests for DebugTelemetryRecorder."""

    def test_capture_event(self):
        """Test capturing discrete events."""
        recorder = DebugTelemetryRecorder()

        recorder.capture_event("test_event", {"key": "value", "count": 42})

        assert len(recorder.events) == 1
        assert recorder.events[0].name == "test_event"
        assert recorder.events[0].data == {"key": "value", "count": 42}

    def test_get_event(self):
        """Test retrieving event data by name."""
        recorder = DebugTelemetryRecorder()

        recorder.capture_event("event_a", {"value": 1})
        recorder.capture_event("event_b", {"value": 2})

        assert recorder.get_event("event_a") == {"value": 1}
        assert recorder.get_event("event_b") == {"value": 2}
        assert recorder.get_event("nonexistent") is None

    def test_get_all_events(self):
        """Test retrieving all events with a given name."""
        recorder = DebugTelemetryRecorder()

        recorder.capture_event("repeat", {"n": 1})
        recorder.capture_event("other", {"n": 99})
        recorder.capture_event("repeat", {"n": 2})
        recorder.capture_event("repeat", {"n": 3})

        events = recorder.get_all_events("repeat")
        assert len(events) == 3
        assert events == [{"n": 1}, {"n": 2}, {"n": 3}]

    def test_start_and_end_span(self):
        """Test starting and ending spans."""
        recorder = DebugTelemetryRecorder()

        span_id = recorder.start_span("test_operation")
        assert span_id is not None
        assert span_id in recorder.spans

        span = recorder.spans[span_id]
        assert span.name == "test_operation"
        assert span.end_time is None

        recorder.end_span(span_id, {"result": "success"})
        assert span.end_time is not None
        assert span.data == {"result": "success"}
        assert span.duration_ms is not None
        assert span.duration_ms >= 0

    def test_get_span_by_name(self):
        """Test retrieving span by name."""
        recorder = DebugTelemetryRecorder()

        recorder.start_span("operation_a")
        recorder.start_span("operation_b")

        span_a = recorder.get_span_by_name("operation_a")
        span_b = recorder.get_span_by_name("operation_b")
        span_c = recorder.get_span_by_name("nonexistent")

        assert span_a is not None
        assert span_a.name == "operation_a"
        assert span_b is not None
        assert span_b.name == "operation_b"
        assert span_c is None

    def test_nested_spans(self):
        """Test spans with parent IDs."""
        recorder = DebugTelemetryRecorder()

        parent_id = recorder.start_span("parent_operation")
        child_id = recorder.start_span("child_operation", parent_id=parent_id)

        parent = recorder.get_span(parent_id)
        child = recorder.get_span(child_id)

        assert parent.parent_id is None
        assert child.parent_id == parent_id

    def test_clear(self):
        """Test clearing all recorded data."""
        recorder = DebugTelemetryRecorder()

        recorder.capture_event("event", {})
        recorder.start_span("span")

        assert len(recorder.events) == 1
        assert len(recorder.spans) == 1

        recorder.clear()

        assert len(recorder.events) == 0
        assert len(recorder.spans) == 0

    def test_event_names(self):
        """Test event_names property."""
        recorder = DebugTelemetryRecorder()

        recorder.capture_event("a", {})
        recorder.capture_event("b", {})
        recorder.capture_event("a", {})

        assert recorder.event_names == ["a", "b", "a"]


class TestOpenTelemetryProvider:
    """Tests for OpenTelemetryProvider."""

    def test_no_op_without_otel(self):
        """Test that provider works in no-op mode without OpenTelemetry."""
        # This test verifies the provider handles missing OTel gracefully
        provider = OpenTelemetryProvider(service_name="test-service")

        # Should not raise even without OTel installed
        provider.capture_event("test", {"key": "value"})
        span_id = provider.start_span("test_span")
        provider.end_span(span_id, {"result": "ok"})

        # span_id should still be valid (for correlation)
        assert span_id is not None


class TestCompositeProvider:
    """Tests for CompositeProvider."""

    def test_fan_out_events(self):
        """Test that events are sent to all providers."""
        recorder1 = DebugTelemetryRecorder()
        recorder2 = DebugTelemetryRecorder()
        composite = CompositeProvider([recorder1, recorder2])

        composite.capture_event("test_event", {"value": 42})

        assert len(recorder1.events) == 1
        assert len(recorder2.events) == 1
        assert recorder1.get_event("test_event") == {"value": 42}
        assert recorder2.get_event("test_event") == {"value": 42}

    def test_fan_out_spans(self):
        """Test that spans are created on all providers."""
        recorder1 = DebugTelemetryRecorder()
        recorder2 = DebugTelemetryRecorder()
        composite = CompositeProvider([recorder1, recorder2])

        span_id = composite.start_span("test_span")
        composite.end_span(span_id, {"result": "ok"})

        # Both recorders should have spans
        assert len(recorder1.spans) == 1
        assert len(recorder2.spans) == 1

        # First recorder should have the same span_id for correlation
        span1 = recorder1.get_span(span_id)
        assert span1 is not None
        assert span1.name == "test_span"

    def test_add_provider(self):
        """Test adding a provider dynamically."""
        recorder1 = DebugTelemetryRecorder()
        composite = CompositeProvider([recorder1])

        recorder2 = DebugTelemetryRecorder()
        composite.add_provider(recorder2)

        composite.capture_event("event", {})

        assert len(recorder1.events) == 1
        assert len(recorder2.events) == 1

    def test_remove_provider(self):
        """Test removing a provider."""
        recorder1 = DebugTelemetryRecorder()
        recorder2 = DebugTelemetryRecorder()
        composite = CompositeProvider([recorder1, recorder2])

        composite.remove_provider(recorder1)
        composite.capture_event("event", {})

        assert len(recorder1.events) == 0
        assert len(recorder2.events) == 1

    def test_providers_property(self):
        """Test providers property."""
        recorder1 = DebugTelemetryRecorder()
        recorder2 = DebugTelemetryRecorder()
        composite = CompositeProvider([recorder1, recorder2])

        assert composite.providers == [recorder1, recorder2]


class TestCompositeSpanOwnership:
    def test_nested_spans_end_in_each_sink(self):
        first, second = DebugTelemetryRecorder(), DebugTelemetryRecorder()
        composite = CompositeProvider([first, second])
        parent = composite.start_span("parent")
        child = composite.start_span("child", parent)
        composite.end_span(child, {"outcome": "success"})
        composite.end_span(parent)
        for sink in (first, second):
            root = sink.get_span_by_name("parent")
            nested = sink.get_span_by_name("child")
            assert root.end_time is not None
            assert nested.end_time is not None
            assert nested.parent_id in sink.spans
            assert sink.spans[nested.parent_id] is root
            assert nested.data == {"outcome": "success"}
        assert first.get_span(parent) is not None
        assert first.get_span(child) is not None

    def test_membership_is_pinned_and_new_child_has_no_foreign_parent(self):
        first, second, added = (DebugTelemetryRecorder() for _ in range(3))
        composite = CompositeProvider([first, second])
        parent = composite.start_span("parent")
        composite.remove_provider(first)
        composite.add_provider(added)
        child = composite.start_span("child", parent)
        assert added.get_span_by_name("child").parent_id is None
        assert second.get_span_by_name("child").parent_id in second.spans
        composite.end_span(parent)
        composite.end_span(child)
        assert len(first.spans) == 1
        assert all(
            span.end_time is not None
            for sink in (first, second, added)
            for span in sink.spans.values()
        )

    def test_empty_and_duplicate_end(self):
        empty = CompositeProvider([])
        assert empty.start_span("empty")
        empty.end_span("unknown")

        class Counting(DebugTelemetryRecorder):
            ends = 0

            def end_span(self, span_id, data=None):
                self.ends += 1
                super().end_span(span_id, data)

        sink = Counting()
        composite = CompositeProvider([sink])
        span = composite.start_span("test")
        composite.end_span(span)
        composite.end_span(span)
        composite.end_span("unknown")
        assert sink.ends == 1

    def test_payload_mutation_is_isolated(self):
        class Mutating(DebugTelemetryRecorder):
            def capture_event(self, event_name, data):
                data["nested"]["value"] = "changed"

            def end_span(self, span_id, data=None):
                data["nested"]["value"] = "changed"
                super().end_span(span_id, data)

        mutating, normal = Mutating(), DebugTelemetryRecorder()
        composite = CompositeProvider([mutating, normal])
        data = {"nested": {"value": "original"}}
        composite.capture_event("event", data)
        span = composite.start_span("span")
        composite.end_span(span, data)
        assert data["nested"]["value"] == "original"
        assert normal.get_event("event")["nested"]["value"] == "original"
        assert normal.get_span_by_name("span").data["nested"]["value"] == "original"

    def test_failures_attempt_all_sinks_and_rollback_opened_spans(self):
        import pytest
        from friday_telemetry.providers.composite import CompositeDeliveryError

        class Failing(DebugTelemetryRecorder):
            def capture_event(self, event_name, data):
                raise RuntimeError("PRIVATE_EXCEPTION")

            def start_span(self, name, parent_id=None):
                raise RuntimeError("PRIVATE_EXCEPTION")

        healthy = DebugTelemetryRecorder()
        composite = CompositeProvider([Failing(), healthy])
        with pytest.raises(CompositeDeliveryError) as error:
            composite.capture_event("event", {"count": 1})
        assert "PRIVATE_EXCEPTION" not in str(error.value)
        assert error.value.failure_count == 1
        assert healthy.get_event("event") == {"count": 1}
        with pytest.raises(CompositeDeliveryError):
            composite.start_span("span")
        assert healthy.get_span_by_name("span").end_time is not None

    def test_failed_end_still_closes_other_sink_once(self):
        import pytest
        from friday_telemetry.providers.composite import CompositeDeliveryError

        class FailingEnd(DebugTelemetryRecorder):
            def end_span(self, span_id, data=None):
                raise RuntimeError("PRIVATE_EXCEPTION")

        failing, healthy = FailingEnd(), DebugTelemetryRecorder()
        composite = CompositeProvider([failing, healthy])
        span = composite.start_span("span")
        with pytest.raises(CompositeDeliveryError) as error:
            composite.end_span(span)
        assert error.value.failure_count == 1
        assert healthy.get_span_by_name("span").end_time is not None
        composite.end_span(span)
