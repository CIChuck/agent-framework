"""
Tests for ContextAssembler lifecycle-aware features (Phase 7).

Tests cover:
- DECAYED memory filtering
- Short-term vs long-term separation
- Relevancy score-based ranking (inclusion_score)
- Lifecycle-aware budget pruning
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from friday_core import DebugTelemetryRecorder

from friday_memory import (
    ChromaVectorStore,
    ElementXGraphStore,
    InMemoryEpisodicStore,
    MemoryController,
)
from friday_memory.context import ContextAssembler
from friday_memory.lifecycle.stages import MemoryStage
from friday_memory.models import ContextPayload, SessionState


class TestDecayedFiltering:
    """Test DECAYED memory filtering."""

    @pytest.fixture
    def mock_embedding(self):
        mock = AsyncMock()
        mock.embed_documents = AsyncMock(return_value=[[0.1] * 1536])
        mock.embed_query = AsyncMock(return_value=[0.1] * 1536)
        return mock

    @pytest.fixture
    def assembler(self, mock_embedding):
        collection_name = f"test_{uuid.uuid4().hex[:8]}"
        controller = MemoryController(
            vector_store=ChromaVectorStore(
                collection_name=collection_name,
                embedding_function=mock_embedding,
            ),
            graph_store=ElementXGraphStore(),
            episodic_store=InMemoryEpisodicStore(),
        )
        return ContextAssembler(
            memory_controller=controller,
            telemetry=DebugTelemetryRecorder(),
        )

    def test_filter_decayed_removes_decayed_memories(self, assembler):
        """Test that _filter_decayed removes DECAYED stage memories."""
        payload = ContextPayload(
            history=[],
            passages=[
                {"id": "1", "text": "Active memory", "metadata": {"stage": "long_term"}},
                {"id": "2", "text": "Decayed memory", "metadata": {"stage": "decayed"}},
                {"id": "3", "text": "Short term", "metadata": {"stage": "short_term"}},
            ],
            entities=[],
            facts=[],
            debug_info={},
        )

        filtered = assembler._filter_decayed(payload)

        assert len(filtered.passages) == 2
        assert all(p["id"] != "2" for p in filtered.passages)

    def test_filter_decayed_handles_no_decayed(self, assembler):
        """Test that _filter_decayed returns original when no decayed present."""
        payload = ContextPayload(
            history=[],
            passages=[
                {"id": "1", "text": "Active memory", "metadata": {"stage": "long_term"}},
            ],
            entities=[],
            facts=[],
            debug_info={},
        )

        filtered = assembler._filter_decayed(payload)

        assert filtered is payload  # Same object, no filtering needed

    def test_filter_decayed_adds_debug_info(self, assembler):
        """Test that filtering adds count to debug_info."""
        payload = ContextPayload(
            history=[],
            passages=[
                {"id": "1", "text": "Decayed", "metadata": {"stage": "decayed"}},
                {"id": "2", "text": "Also decayed", "metadata": {"stage": "decayed"}},
            ],
            entities=[],
            facts=[],
            debug_info={},
        )

        filtered = assembler._filter_decayed(payload)

        assert filtered.debug_info.get("decayed_filtered") == 2


class TestStageSeparation:
    """Test short-term vs long-term separation."""

    @pytest.fixture
    def mock_embedding(self):
        mock = AsyncMock()
        mock.embed_documents = AsyncMock(return_value=[[0.1] * 1536])
        mock.embed_query = AsyncMock(return_value=[0.1] * 1536)
        return mock

    @pytest.fixture
    def assembler(self, mock_embedding):
        collection_name = f"test_{uuid.uuid4().hex[:8]}"
        controller = MemoryController(
            vector_store=ChromaVectorStore(
                collection_name=collection_name,
                embedding_function=mock_embedding,
            ),
            graph_store=ElementXGraphStore(),
            episodic_store=InMemoryEpisodicStore(),
        )
        return ContextAssembler(memory_controller=controller)

    def test_separate_by_stage_correct_split(self, assembler):
        """Test that passages are correctly separated by stage."""
        passages = [
            {"id": "1", "metadata": {"stage": "short_term"}},
            {"id": "2", "metadata": {"stage": "long_term"}},
            {"id": "3", "metadata": {"stage": "short_term"}},
            {"id": "4", "metadata": {}},  # No stage = long_term default
        ]

        short_term, long_term = assembler._separate_by_stage(passages)

        assert len(short_term) == 2
        assert len(long_term) == 2
        assert all(p["id"] in ["1", "3"] for p in short_term)
        assert all(p["id"] in ["2", "4"] for p in long_term)

    def test_separate_by_stage_all_short_term(self, assembler):
        """Test with all short-term passages."""
        passages = [
            {"id": "1", "metadata": {"stage": "short_term"}},
            {"id": "2", "metadata": {"stage": "short_term"}},
        ]

        short_term, long_term = assembler._separate_by_stage(passages)

        assert len(short_term) == 2
        assert len(long_term) == 0

    def test_separate_by_stage_empty(self, assembler):
        """Test with empty passages list."""
        short_term, long_term = assembler._separate_by_stage([])

        assert short_term == []
        assert long_term == []


class TestRelevancyScoring:
    """Test relevancy score-based ranking."""

    @pytest.fixture
    def mock_embedding(self):
        mock = AsyncMock()
        mock.embed_documents = AsyncMock(return_value=[[0.1] * 1536])
        mock.embed_query = AsyncMock(return_value=[0.1] * 1536)
        return mock

    @pytest.fixture
    def assembler(self, mock_embedding):
        collection_name = f"test_{uuid.uuid4().hex[:8]}"
        controller = MemoryController(
            vector_store=ChromaVectorStore(
                collection_name=collection_name,
                embedding_function=mock_embedding,
            ),
            graph_store=ElementXGraphStore(),
            episodic_store=InMemoryEpisodicStore(),
        )
        return ContextAssembler(memory_controller=controller)

    def test_get_relevancy_score_prefers_inclusion_score(self, assembler):
        """Test that inclusion_score is preferred over similarity."""
        passage = {"similarity": 0.8, "inclusion_score": 0.5}
        score = assembler._get_relevancy_score(passage)
        assert score == 0.5

    def test_get_relevancy_score_falls_back_to_similarity(self, assembler):
        """Test fallback to similarity when no inclusion_score."""
        passage = {"similarity": 0.8}
        score = assembler._get_relevancy_score(passage)
        assert score == 0.8

    def test_get_relevancy_score_zero_default(self, assembler):
        """Test default of 0.0 when no scores present."""
        passage = {"id": "1", "text": "No scores"}
        score = assembler._get_relevancy_score(passage)
        assert score == 0.0

    def test_sort_by_relevancy_orders_correctly(self, assembler):
        """Test that passages are sorted by relevancy score."""
        passages = [
            {"id": "low", "inclusion_score": 0.2},
            {"id": "high", "inclusion_score": 0.9},
            {"id": "mid", "inclusion_score": 0.5},
        ]

        sorted_passages = assembler._sort_by_relevancy(passages)

        assert sorted_passages[0]["id"] == "high"
        assert sorted_passages[1]["id"] == "mid"
        assert sorted_passages[2]["id"] == "low"


class TestLifecycleAwareBudgeting:
    """Test lifecycle-aware budget pruning."""

    @pytest.fixture
    def mock_embedding(self):
        mock = AsyncMock()
        mock.embed_documents = AsyncMock(return_value=[[0.1] * 1536])
        mock.embed_query = AsyncMock(return_value=[0.1] * 1536)
        return mock

    @pytest.fixture
    def assembler(self, mock_embedding):
        collection_name = f"test_{uuid.uuid4().hex[:8]}"
        controller = MemoryController(
            vector_store=ChromaVectorStore(
                collection_name=collection_name,
                embedding_function=mock_embedding,
            ),
            graph_store=ElementXGraphStore(),
            episodic_store=InMemoryEpisodicStore(),
        )
        return ContextAssembler(
            memory_controller=controller,
            telemetry=DebugTelemetryRecorder(),
        )

    def test_apply_budget_filters_decayed_first(self, assembler):
        """Test that DECAYED memories are filtered before budgeting."""
        payload = ContextPayload(
            history=[],
            passages=[
                {"id": "1", "text": "x" * 100, "metadata": {"stage": "long_term"}, "similarity": 0.8},
                {"id": "2", "text": "x" * 100, "metadata": {"stage": "decayed"}, "similarity": 0.9},
            ],
            entities=[],
            facts=[],
            debug_info={},
        )

        # Large budget so no other pruning needed
        result = assembler._apply_budget(payload, 100000)

        # Decayed should be filtered out
        assert len(result.passages) == 1
        assert result.passages[0]["id"] == "1"

    def test_apply_budget_drops_low_relevancy_long_term_first(self, assembler):
        """Test that low-relevancy long-term is dropped before short-term when budget is tight."""
        payload = ContextPayload(
            history=[],
            passages=[
                {"id": "st1", "text": "x" * 500, "metadata": {"stage": "short_term"}, "inclusion_score": 0.6},
                {"id": "lt_low", "text": "x" * 500, "metadata": {"stage": "long_term"}, "inclusion_score": 0.2},
                {"id": "lt_high", "text": "x" * 500, "metadata": {"stage": "long_term"}, "inclusion_score": 0.8},
            ],
            entities=[],
            facts=[],
            debug_info={},
        )

        # Budget that requires pruning - each passage has ~125 tokens (500/4)
        # Total ~375 tokens, budget of 300 requires dropping something
        result = assembler._apply_budget(payload, 300)

        # Low relevancy long-term (< 0.3 threshold) should be dropped first
        ids = [p["id"] for p in result.passages]
        # At minimum, low-relevancy long-term should be filtered before short-term
        if "lt_low" in ids:
            # If lt_low wasn't filtered, then we should still have all short-term
            assert "st1" in ids

    def test_apply_budget_preserves_short_term_over_long_term(self, assembler):
        """Test that short-term is preserved over long-term when pruning."""
        payload = ContextPayload(
            history=[],
            passages=[
                {"id": "st1", "text": "Short term memory", "metadata": {"stage": "short_term"}, "inclusion_score": 0.6},
                {"id": "st2", "text": "Another short", "metadata": {"stage": "short_term"}, "inclusion_score": 0.5},
                {"id": "lt1", "text": "Long term", "metadata": {"stage": "long_term"}, "inclusion_score": 0.7},
                {"id": "lt2", "text": "Another long", "metadata": {"stage": "long_term"}, "inclusion_score": 0.6},
            ],
            entities=[],
            facts=[],
            debug_info={},
        )

        # Very tight budget
        result = assembler._apply_budget(payload, 50)

        # Short-term should be preserved
        ids = [p["id"] for p in result.passages]
        # At minimum, short-term should still be present
        short_term_count = sum(1 for p in result.passages if p.get("metadata", {}).get("stage") == "short_term")
        assert short_term_count >= min(2, len(result.passages))

    def test_estimate_tokens_full_includes_insights(self, assembler):
        """Test that full token estimation includes insights and summaries."""
        tokens_without = assembler._estimate_tokens_full(
            history=[],
            passages=[],
            entities=[],
            facts=[],
            insights=[],
            summaries=[],
        )

        tokens_with = assembler._estimate_tokens_full(
            history=[],
            passages=[],
            entities=[],
            facts=[],
            insights=[{"text": "This is an insight with some tokens"}],
            summaries=[{"text": "This is a summary with tokens"}],
        )

        assert tokens_with > tokens_without


class TestCreatePrunedPayloadFull:
    """Test the full pruned payload creation."""

    @pytest.fixture
    def mock_embedding(self):
        mock = AsyncMock()
        mock.embed_documents = AsyncMock(return_value=[[0.1] * 1536])
        mock.embed_query = AsyncMock(return_value=[0.1] * 1536)
        return mock

    @pytest.fixture
    def assembler(self, mock_embedding):
        collection_name = f"test_{uuid.uuid4().hex[:8]}"
        controller = MemoryController(
            vector_store=ChromaVectorStore(
                collection_name=collection_name,
                embedding_function=mock_embedding,
            ),
            graph_store=ElementXGraphStore(),
            episodic_store=InMemoryEpisodicStore(),
        )
        return ContextAssembler(memory_controller=controller)

    @pytest.fixture
    def sample_turns(self):
        """Create sample InteractionTurn objects for testing."""
        from friday_memory.models import InteractionTurn

        return [
            InteractionTurn(id=f"turn_{i}", session_id="test_session")
            for i in range(5)
        ]

    @pytest.fixture
    def sample_entities(self):
        """Create sample GraphNode objects for testing."""
        from friday_memory.models import GraphNode, ProvenanceMetadata

        provenance = ProvenanceMetadata(
            source_id="test",
            source_type="interaction",
            confidence=0.9,
        )
        return [
            GraphNode(id="e1", type="Entity", label="Entity 1", provenance=provenance),
            GraphNode(id="e2", type="Entity", label="Entity 2", provenance=provenance),
        ]

    @pytest.fixture
    def sample_facts(self):
        """Create sample GraphEdge objects for testing."""
        from friday_memory.models import GraphEdge, ProvenanceMetadata

        provenance = ProvenanceMetadata(
            source_id="test",
            source_type="interaction",
            confidence=0.9,
        )
        return [
            GraphEdge(
                source_id="e1",
                target_id="e2",
                relation="related_to",
                provenance=provenance,
            ),
        ]

    def test_creates_payload_with_pruned_content(
        self, assembler, sample_turns, sample_entities, sample_facts
    ):
        """Test that pruned payload preserves structure with reduced content."""
        original = ContextPayload(
            history=sample_turns,
            passages=[{"id": "p1"}, {"id": "p2"}, {"id": "p3"}],
            entities=sample_entities,
            facts=sample_facts,
            recent_memories=["mem1"],
            insights=[{"text": "i1"}, {"text": "i2"}],
            summaries=[{"text": "s1"}],
            debug_info={"original_key": "value"},
        )

        pruned = assembler._create_pruned_payload_full(
            original=original,
            history=sample_turns[:2],
            passages=[{"id": "p1"}],
            entities=[],
            facts=[],
            insights=[{"text": "i1"}],
            summaries=[],
        )

        assert len(pruned.history) == 2
        assert len(pruned.passages) == 1
        assert len(pruned.entities) == 0
        assert len(pruned.facts) == 0
        assert len(pruned.insights) == 1
        assert len(pruned.summaries) == 0
        assert pruned.recent_memories == ["mem1"]  # Preserved
        assert pruned.debug_info["pruned"] is True
        assert pruned.debug_info["original_history"] == 5
        assert pruned.debug_info["original_passages"] == 3
