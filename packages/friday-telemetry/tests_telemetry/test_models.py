# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Tests for telemetry models."""

from friday_telemetry import (
    # LLM models
    ArbitrationOpsMetrics,
    ConversationContext,
    ErrorCategory,
    GenAIOperationType,
    LLMCallMetrics,
    # Memory models
    MaintenanceMetrics,
    MemoryRecallMetrics,
    MemoryWriteMetrics,
    # Common models
    RequestContext,
    StreamingMetrics,
    TokenUsage,
)


class TestTokenUsage:
    """Tests for TokenUsage model."""

    def test_default_values(self):
        """Test default values."""
        usage = TokenUsage()
        assert usage.input_tokens == 0
        assert usage.output_tokens == 0
        assert usage.total_tokens == 0

    def test_from_response(self):
        """Test creating from response dict."""
        response = {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        }
        usage = TokenUsage.from_response(response)
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
        assert usage.total_tokens == 150

    def test_from_response_none(self):
        """Test creating from None response."""
        usage = TokenUsage.from_response(None)
        assert usage.input_tokens == 0
        assert usage.output_tokens == 0


class TestStreamingMetrics:
    """Tests for StreamingMetrics model."""

    def test_streaming_metrics(self):
        """Test streaming metrics creation."""
        metrics = StreamingMetrics(
            time_to_first_token_ms=150.5,
            chunk_count=42,
            tokens_per_second=25.0,
            inter_token_latency_ms=40.0,
            total_stream_duration_ms=1680.0,
        )
        assert metrics.time_to_first_token_ms == 150.5
        assert metrics.chunk_count == 42
        assert metrics.tokens_per_second == 25.0


class TestLLMCallMetrics:
    """Tests for LLMCallMetrics model."""

    def test_minimal_creation(self):
        """Test creating with minimal required fields."""
        metrics = LLMCallMetrics(
            request_id="req-123",
            request_model="gpt-4",
        )
        assert metrics.request_id == "req-123"
        assert metrics.request_model == "gpt-4"
        assert metrics.success is True
        assert metrics.operation_name == GenAIOperationType.CHAT

    def test_full_creation(self):
        """Test creating with all fields."""
        metrics = LLMCallMetrics(
            request_id="req-123",
            conversation_id="conv-456",
            turn_id="turn-1",
            workflow_id="wf-1",
            execution_id="exec-1",
            pipeline_id="pl-1",
            task_id="task-1",
            assignment_id="assign-1",
            agent_id="agent-1",
            llm_service="fast_openai",
            operation_name=GenAIOperationType.CHAT,
            provider_name="openai",
            request_model="gpt-4",
            response_model="gpt-4-0613",
            temperature=0.7,
            max_tokens=1000,
            tool_count=3,
            duration_ms=500.0,
            usage=TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150),
            response_id="resp-789",
            finish_reasons=["stop"],
            tool_calls_count=1,
            success=True,
            attempt_number=1,
            total_attempts=1,
        )
        assert metrics.conversation_id == "conv-456"
        assert metrics.workflow_id == "wf-1"
        assert metrics.llm_service == "fast_openai"
        assert metrics.usage.total_tokens == 150


class TestConversationContext:
    """Tests for ConversationContext model."""

    def test_conversation_context(self):
        """Test conversation context creation."""
        context = ConversationContext(
            session_id="session-123",
            conversation_id="conv-456",
            turn_id="turn-1",
            turn_number=3,
            message_count=7,
            workflow_id="wf-1",
            execution_id="exec-1",
            pipeline_id="pl-1",
            task_id="task-1",
            assignment_id="assign-1",
            agent_id="agent-1",
            llm_service="reasoning",
        )
        assert context.session_id == "session-123"
        assert context.turn_number == 3
        assert context.workflow_id == "wf-1"
        assert context.llm_service == "reasoning"


class TestMemoryWriteMetrics:
    """Tests for MemoryWriteMetrics model."""

    def test_minimal_creation(self):
        """Test creating with minimal fields."""
        metrics = MemoryWriteMetrics(
            request_id="req-123",
            operation="store_fact",
            store_type="vector",
        )
        assert metrics.request_id == "req-123"
        assert metrics.operation == "store_fact"
        assert metrics.store_type == "vector"
        assert metrics.success is True

    def test_full_creation(self):
        """Test creating with all fields."""
        metrics = MemoryWriteMetrics(
            request_id="req-123",
            operation="ingest_file",
            store_type="vector",
            duration_ms=250.0,
            document_count=5,
            total_chars=10000,
            chunk_count=20,
            embedding_time_ms=100.0,
            embedding_model="text-embedding-3-small",
            success=True,
            stored_ids=["id1", "id2", "id3"],
            source_file="/path/to/file.txt",
            session_id="session-123",
        )
        assert metrics.chunk_count == 20
        assert len(metrics.stored_ids) == 3


class TestMemoryRecallMetrics:
    """Tests for MemoryRecallMetrics model."""

    def test_minimal_creation(self):
        """Test creating with minimal fields."""
        metrics = MemoryRecallMetrics(
            request_id="req-123",
            operation="recall",
            query_text="test query",
        )
        assert metrics.request_id == "req-123"
        assert metrics.operation == "recall"
        assert metrics.query_text == "test query"

    def test_full_creation(self):
        """Test creating with all fields."""
        metrics = MemoryRecallMetrics(
            request_id="req-123",
            operation="search",
            query_text="what is the capital",
            query_tokens=5,
            stores_queried=["vector", "graph"],
            duration_ms=50.0,
            vector_search_ms=30.0,
            graph_traversal_ms=15.0,
            reranking_ms=5.0,
            results_count=10,
            results_by_store={"vector": 7, "graph": 3},
            cache_hit=False,
            reranking_applied=True,
            filters_applied=["recency", "relevance"],
            success=True,
        )
        assert metrics.stores_queried == ["vector", "graph"]
        assert metrics.results_by_store["vector"] == 7


class TestMaintenanceMetrics:
    """Tests for MaintenanceMetrics model."""

    def test_minimal_creation(self):
        """Test creating with minimal fields."""
        metrics = MaintenanceMetrics(
            request_id="req-123",
            operation="prune",
        )
        assert metrics.request_id == "req-123"
        assert metrics.operation == "prune"

    def test_prune_operation(self):
        """Test prune operation metrics."""
        metrics = MaintenanceMetrics(
            request_id="req-123",
            operation="prune",
            duration_ms=1000.0,
            items_processed=500,
            items_affected=50,
            items_pruned=50,
            success=True,
            dry_run=False,
        )
        assert metrics.items_pruned == 50
        assert not metrics.dry_run

    def test_promote_operation(self):
        """Test promote operation metrics."""
        metrics = MaintenanceMetrics(
            request_id="req-123",
            operation="promote",
            items_processed=100,
            items_affected=15,
            items_promoted=15,
        )
        assert metrics.items_promoted == 15

    def test_synthesize_operation(self):
        """Test synthesize operation metrics."""
        metrics = MaintenanceMetrics(
            request_id="req-123",
            operation="synthesize",
            items_processed=50,
            items_affected=5,
            items_synthesized=5,
            relationships_inferred=10,
        )
        assert metrics.items_synthesized == 5
        assert metrics.relationships_inferred == 10


class TestArbitrationOpsMetrics:
    """Tests for arbitration/recovery ops metrics."""

    def test_minimal_creation(self):
        metrics = ArbitrationOpsMetrics(request_id="req-123")
        assert metrics.request_id == "req-123"
        assert metrics.proposal_volume == 0
        assert metrics.degraded_mode is False

    def test_full_creation(self):
        metrics = ArbitrationOpsMetrics(
            request_id="req-123",
            session_id="session-1",
            correlation_id="corr-1",
            proposal_volume=42,
            promotion_backlog=4,
            recovery_backlog=2,
            promotion_latency_ms=125.5,
            conflict_rate=0.15,
            recovery_retries=3,
            compensation_events=1,
            degraded_mode=True,
        )
        assert metrics.proposal_volume == 42
        assert metrics.conflict_rate == 0.15
        assert metrics.degraded_mode is True


class TestErrorCategory:
    """Tests for ErrorCategory enum."""

    def test_error_categories(self):
        """Test error category values."""
        assert ErrorCategory.TIMEOUT.value == "timeout"
        assert ErrorCategory.RATE_LIMIT.value == "rate_limit"
        assert ErrorCategory.AUTH_ERROR.value == "auth_error"
        assert ErrorCategory.NETWORK_ERROR.value == "network_error"


class TestRequestContext:
    """Tests for RequestContext model."""

    def test_request_context(self):
        """Test request context creation."""
        context = RequestContext(
            request_id="req-123",
            session_id="session-456",
            conversation_id="conv-789",
            turn_id="turn-1",
            parent_span_id="span-abc",
        )
        assert context.request_id == "req-123"
        assert context.parent_span_id == "span-abc"
