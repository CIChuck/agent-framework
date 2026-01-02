"""
Intermediate Example: Telemetry with Events and Spans

This example demonstrates:
- TelemetryInterface protocol for instrumentation
- DebugTelemetryRecorder for white-box testing
- Capturing discrete events with data
- Tracking operation timing with spans
- Parent-child span relationships
- Using helper methods for test assertions

Run with: uv run python packages/friday-core/examples/02_intermediate.py
"""

import time

from friday_core import DebugTelemetryRecorder, EventRecord, SpanRecord, TelemetryInterface


def main():
    # DebugTelemetryRecorder is an in-memory implementation
    # Perfect for testing and development
    recorder = DebugTelemetryRecorder()

    print("=== Capturing Events ===\n")

    # Events are discrete occurrences with associated data
    recorder.capture_event("user_login", {"user_id": "user_123", "method": "oauth"})

    recorder.capture_event(
        "memory_recall",
        {
            "query": "What did we discuss about the API?",
            "results_count": 5,
            "latency_ms": 45,
        },
    )

    recorder.capture_event(
        "tool_execution",
        {"tool_name": "web_search", "status": "success", "tokens_used": 150},
    )

    # View all captured events
    print(f"Captured {len(recorder.events)} events:")
    for event in recorder.events:
        print(f"  - {event.name}: {event.data}")

    print("\n=== Working with Spans ===\n")

    # Spans track the duration of operations
    # start_span returns a span_id for later reference
    span_id = recorder.start_span("database_query")

    # Simulate some work
    time.sleep(0.05)  # 50ms

    # End the span with optional result data
    recorder.end_span(span_id, {"rows_returned": 42, "cache_hit": False})

    # Retrieve and inspect the span
    span = recorder.get_span(span_id)
    print(f"Span '{span.name}':")
    print(f"  Duration: {span.duration_ms:.2f}ms")
    print(f"  Data: {span.data}")

    print("\n=== Parent-Child Span Relationships ===\n")

    # Spans can have parent-child relationships for tracing
    parent_id = recorder.start_span("handle_request")

    # Child spans reference their parent
    child1_id = recorder.start_span("validate_input", parent_id=parent_id)
    time.sleep(0.01)
    recorder.end_span(child1_id, {"valid": True})

    child2_id = recorder.start_span("process_query", parent_id=parent_id)
    time.sleep(0.02)
    recorder.end_span(child2_id, {"tokens": 500})

    child3_id = recorder.start_span("format_response", parent_id=parent_id)
    time.sleep(0.01)
    recorder.end_span(child3_id, {"format": "json"})

    recorder.end_span(parent_id, {"status": 200})

    # Display the span hierarchy
    parent_span = recorder.get_span(parent_id)
    print(f"Parent: {parent_span.name} ({parent_span.duration_ms:.2f}ms)")

    for span_id, span in recorder.spans.items():
        if span.parent_id == parent_id:
            print(f"  Child: {span.name} ({span.duration_ms:.2f}ms)")

    print("\n=== Helper Methods for Testing ===\n")

    # get_event retrieves the first event with a given name
    login_data = recorder.get_event("user_login")
    print(f"User login data: {login_data}")

    # get_all_events retrieves all events with a given name
    recorder.capture_event("api_call", {"endpoint": "/v1/chat"})
    recorder.capture_event("api_call", {"endpoint": "/v1/embeddings"})
    all_api_calls = recorder.get_all_events("api_call")
    print(f"All API calls ({len(all_api_calls)}): {all_api_calls}")

    # get_span_by_name finds a span by its name
    query_span = recorder.get_span_by_name("database_query")
    print(f"Database query span duration: {query_span.duration_ms:.2f}ms")

    # event_names lists all event names in order
    print(f"Event names: {recorder.event_names}")

    print("\n=== Using Telemetry for Test Assertions ===\n")

    # Clear previous data for a fresh test
    recorder.clear()

    # Simulate a component that uses telemetry
    def memory_search(query: str, telemetry: TelemetryInterface):
        span_id = telemetry.start_span("memory_search")

        telemetry.capture_event("search_started", {"query": query})

        # Simulate search
        time.sleep(0.02)
        results = ["result1", "result2", "result3"]

        telemetry.capture_event(
            "search_completed", {"query": query, "count": len(results)}
        )

        telemetry.end_span(span_id, {"results": len(results)})
        return results

    # Execute the function
    results = memory_search("API design patterns", recorder)

    # Now assert on the telemetry data
    assert recorder.get_event("search_started")["query"] == "API design patterns"
    assert recorder.get_event("search_completed")["count"] == 3

    search_span = recorder.get_span_by_name("memory_search")
    assert search_span is not None
    assert search_span.duration_ms >= 20
    assert search_span.data["results"] == 3

    print("All assertions passed!")
    print(f"Search completed in {search_span.duration_ms:.2f}ms")


if __name__ == "__main__":
    main()
