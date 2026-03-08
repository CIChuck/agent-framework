# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Tests for telemetry helpers."""

import pytest
from friday_telemetry import (
    ConversationContext,
    DebugTelemetryRecorder,
    ErrorCategory,
    LLMTelemetryHelper,
    MemoryTelemetryHelper,
    StreamingTracker,
    TokenUsage,
    classify_error,
)


class TestClassifyError:
    """Tests for error classification."""

    def test_timeout_error(self):
        """Test classifying timeout errors."""

        class TimeoutError(Exception):
            pass

        assert (
            classify_error(TimeoutError("request timed out")) == ErrorCategory.TIMEOUT
        )

    def test_rate_limit_error(self):
        """Test classifying rate limit errors."""
        error = Exception("Rate limit exceeded")
        assert classify_error(error) == ErrorCategory.RATE_LIMIT

    def test_auth_error(self):
        """Test classifying auth errors."""
        error = Exception("Invalid API key")
        assert classify_error(error) == ErrorCategory.AUTH_ERROR

    def test_network_error(self):
        """Test classifying network errors."""
        error = Exception("Connection refused")
        assert classify_error(error) == ErrorCategory.NETWORK_ERROR

    def test_unknown_error(self):
        """Test classifying unknown errors."""
        error = Exception("Something went wrong")
        assert classify_error(error) == ErrorCategory.UNKNOWN


class TestStreamingTracker:
    """Tests for StreamingTracker."""

    def test_basic_tracking(self):
        """Test basic streaming metrics tracking."""
        tracker = StreamingTracker()
        tracker.start()

        # Simulate receiving chunks
        for _ in range(10):
            tracker.record_chunk(token_count=5)

        metrics = tracker.finish()

        assert metrics.chunk_count == 10
        assert metrics.time_to_first_token_ms is not None
        assert metrics.total_stream_duration_ms > 0

    def test_tokens_per_second(self):
        """Test tokens per second calculation."""
        tracker = StreamingTracker()
        tracker.start()

        for _ in range(100):
            tracker.record_chunk(token_count=1)

        metrics = tracker.finish()

        assert metrics.tokens_per_second is not None
        assert metrics.tokens_per_second > 0


class TestLLMTelemetryHelper:
    """Tests for LLMTelemetryHelper."""

    def test_track_completion_success(self):
        """Test tracking a successful completion."""
        recorder = DebugTelemetryRecorder()
        helper = LLMTelemetryHelper(telemetry=recorder, provider_name="test")
        context = ConversationContext(
            session_id="session-1",
            workflow_id="wf-1",
            execution_id="exec-1",
            pipeline_id="pl-1",
            task_id="task-1",
            assignment_id="assign-1",
            agent_id="agent-1",
            llm_service="reasoning",
        )

        with helper.track_completion(
            model="gpt-4",
            context=context,
            temperature=0.7,
            max_tokens=1000,
            tool_count=2,
        ) as tracker:
            tracker.set_response(
                response_model="gpt-4-0613",
                response_id="resp-123",
                usage=TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150),
                finish_reasons=["stop"],
                tool_calls_count=1,
            )

        # Check event was captured
        assert len(recorder.events) == 1
        event = recorder.events[0]
        assert event.name == "llm_completion_success"
        assert event.data["gen_ai.request.model"] == "gpt-4"
        assert event.data["success"] is True
        assert event.data["friday.workflow.id"] == "wf-1"
        assert event.data["friday.execution.id"] == "exec-1"
        assert event.data["friday.pipeline.id"] == "pl-1"
        assert event.data["friday.task.id"] == "task-1"
        assert event.data["friday.assignment.id"] == "assign-1"
        assert event.data["friday.agent.id"] == "agent-1"
        assert event.data["friday.llm.service"] == "reasoning"

    def test_track_completion_error(self):
        """Test tracking a failed completion."""
        recorder = DebugTelemetryRecorder()
        helper = LLMTelemetryHelper(telemetry=recorder)

        with pytest.raises(ValueError), helper.track_completion(model="gpt-4"):
            raise ValueError("Test error")

        # Check error event was captured
        assert len(recorder.events) == 1
        event = recorder.events[0]
        assert event.name == "llm_completion_error"
        assert event.data["success"] is False
        assert "error.type" in event.data  # OTel convention uses dot notation

    def test_track_embedding_success(self):
        """Test tracking a successful embedding."""
        recorder = DebugTelemetryRecorder()
        helper = LLMTelemetryHelper(telemetry=recorder)
        context = ConversationContext(
            session_id="session-1",
            workflow_id="wf-embed",
            execution_id="exec-embed",
            llm_service="embedding-default",
        )

        with helper.track_embedding(
            model="text-embedding-3-small",
            text_count=5,
            total_characters=1000,
            context=context,
        ) as tracker:
            tracker.set_response(
                embedding_dimensions=1536,
                batch_count=1,
                usage=TokenUsage(input_tokens=200),
            )

        # Check event was captured
        assert len(recorder.events) == 1
        event = recorder.events[0]
        assert event.name == "embeddings_generated"
        assert event.data["text_count"] == 5
        assert event.data["friday.workflow.id"] == "wf-embed"
        assert event.data["friday.execution.id"] == "exec-embed"
        assert event.data["friday.llm.service"] == "embedding-default"

    def test_span_creation(self):
        """Test that spans are created for operations."""
        recorder = DebugTelemetryRecorder()
        helper = LLMTelemetryHelper(telemetry=recorder)

        with helper.track_completion(model="gpt-4"):
            pass

        # Check span was created
        assert len(recorder.spans) == 1
        span = recorder.get_span_by_name("chat gpt-4")
        assert span is not None
        assert span.duration_ms is not None

    def test_no_telemetry(self):
        """Test helper works without telemetry (no-op mode)."""
        helper = LLMTelemetryHelper(telemetry=None)

        # Should not raise
        with helper.track_completion(model="gpt-4") as tracker:
            tracker.set_response(usage=TokenUsage(input_tokens=100))


class TestMemoryTelemetryHelper:
    """Tests for MemoryTelemetryHelper."""

    def test_track_write_success(self):
        """Test tracking a successful write."""
        recorder = DebugTelemetryRecorder()
        helper = MemoryTelemetryHelper(telemetry=recorder)

        with helper.track_write(
            operation="store_fact",
            store_type="vector",
        ) as tracker:
            tracker.set_volume(document_count=1, total_chars=500)
            tracker.set_result(stored_ids=["id-123"])

        # Check event was captured
        assert len(recorder.events) == 1
        event = recorder.events[0]
        assert event.name == "memory_write_success"
        assert event.data["friday.memory.operation"] == "store_fact"
        assert event.data["friday.memory.store_type"] == "vector"

    def test_track_write_with_embedding(self):
        """Test tracking write with embedding info."""
        recorder = DebugTelemetryRecorder()
        helper = MemoryTelemetryHelper(telemetry=recorder)

        with helper.track_write(
            operation="ingest_file",
            store_type="vector",
        ) as tracker:
            tracker.set_volume(document_count=5, total_chars=10000, chunk_count=20)
            tracker.set_embedding_info(
                embedding_time_ms=150.0,
                embedding_model="text-embedding-3-small",
            )
            tracker.set_result(
                stored_ids=["id1", "id2"],
                source_file="/path/to/file.txt",
            )

        event = recorder.events[0]
        assert event.data["friday.memory.embedding_ms"] == 150.0
        assert event.data["embedding_model"] == "text-embedding-3-small"

    def test_track_recall_success(self):
        """Test tracking a successful recall."""
        recorder = DebugTelemetryRecorder()
        helper = MemoryTelemetryHelper(telemetry=recorder)

        with helper.track_recall(
            operation="recall",
            query_text="test query",
        ) as tracker:
            tracker.set_query_info(query_tokens=5)
            tracker.set_stores_queried(["vector", "graph"])
            tracker.set_timing(vector_search_ms=30.0, graph_traversal_ms=20.0)
            tracker.set_results(
                results_count=10, results_by_store={"vector": 7, "graph": 3}
            )

        # Check event was captured
        assert len(recorder.events) == 1
        event = recorder.events[0]
        assert event.name == "memory_recall_success"
        assert event.data["friday.memory.results_count"] == 10

    def test_track_recall_with_cache(self):
        """Test tracking recall with cache hit."""
        recorder = DebugTelemetryRecorder()
        helper = MemoryTelemetryHelper(telemetry=recorder)

        with helper.track_recall(
            operation="prime",
            query_text="cached query",
        ) as tracker:
            tracker.set_cache_info(cache_hit=True, cache_source="lru_cache")
            tracker.set_results(results_count=5)

        event = recorder.events[0]
        assert event.data["friday.memory.cache_hit"] is True
        assert event.data["cache_source"] == "lru_cache"

    def test_track_maintenance_prune(self):
        """Test tracking a prune operation."""
        recorder = DebugTelemetryRecorder()
        helper = MemoryTelemetryHelper(telemetry=recorder)

        with helper.track_maintenance(
            operation="prune",
            dry_run=False,
        ) as tracker:
            tracker.set_volume(items_processed=500, items_affected=50)
            tracker.set_operation_results(items_pruned=50)

        # Check event was captured
        assert len(recorder.events) == 1
        event = recorder.events[0]
        assert event.name == "memory_maintenance_success"
        assert event.data["items_pruned"] == 50
        assert event.data["dry_run"] is False

    def test_track_maintenance_dry_run(self):
        """Test tracking a dry run maintenance operation."""
        recorder = DebugTelemetryRecorder()
        helper = MemoryTelemetryHelper(telemetry=recorder)

        with helper.track_maintenance(
            operation="reorganize",
            dry_run=True,
        ) as tracker:
            tracker.set_volume(items_processed=100, items_affected=0)

        event = recorder.events[0]
        assert event.data["dry_run"] is True

    def test_track_maintenance_error(self):
        """Test tracking a failed maintenance operation."""
        recorder = DebugTelemetryRecorder()
        helper = MemoryTelemetryHelper(telemetry=recorder)

        with pytest.raises(RuntimeError):  # noqa: SIM117
            with helper.track_maintenance(operation="synthesize"):
                raise RuntimeError("Synthesis failed")

        event = recorder.events[0]
        assert event.name == "memory_maintenance_error"
        assert event.data["success"] is False

    def test_no_telemetry(self):
        """Test helper works without telemetry (no-op mode)."""
        helper = MemoryTelemetryHelper(telemetry=None)

        # Should not raise
        with helper.track_write(operation="store_fact", store_type="vector") as tracker:
            tracker.set_result(stored_ids=["id-123"])

        with helper.track_recall(operation="recall", query_text="test") as tracker:
            tracker.set_results(results_count=5)

        with helper.track_maintenance(operation="prune") as tracker:
            tracker.set_volume(items_processed=100, items_affected=10)
