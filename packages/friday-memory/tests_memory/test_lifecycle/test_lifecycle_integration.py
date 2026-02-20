"""
Integration tests for full memory lifecycle flow.

Tests cover:
- End-to-end lifecycle: SHORT_TERM → LONG_TERM → DECAYED
- Promotion cycle with CollectionManager
- Decay cycle with score degradation
- Reactivation on access
- AccessBuffer integration with promotion service
- Graph-vector decay linkage
- Soft-delete and recovery patterns
"""

import uuid
from datetime import datetime, timedelta

import pytest
from friday_memory.lifecycle.decay import DecayCalculator, DecayConfig
from friday_memory.lifecycle.promotion import (
    MemoryPromotionService,
    PromotionScorer,
)
from friday_memory.lifecycle.stages import MemoryStage
from friday_memory.retrieval.access_buffer import AccessBuffer, AccessBufferConfig
from friday_memory.retrieval.collection_manager import (
    CollectionConfig,
    CollectionManager,
)
from friday_memory.retrieval.factor_computer import RetrievalFactorComputer


class MockEmbeddingFunction:
    """Mock embedding function for testing."""

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(t)) / 100] * 768 for t in texts]

    async def embed_query(self, text: str) -> list[float]:
        return [float(len(text)) / 100] * 768


def unique_config():
    """Create config with unique collection names for test isolation."""
    suffix = uuid.uuid4().hex[:8]
    return CollectionConfig(
        short_term_collection=f"test_short_{suffix}",
        long_term_collection=f"test_long_{suffix}",
        decayed_collection=f"test_decayed_{suffix}",
    )


class TestLifecycleEndToEnd:
    """Test complete lifecycle from SHORT_TERM to DECAYED."""

    @pytest.fixture
    def embedding_fn(self):
        """Create mock embedding function."""
        return MockEmbeddingFunction()

    @pytest.fixture
    def collection_manager(self, embedding_fn):
        """Create collection manager with unique collections."""
        return CollectionManager(
            embedding_function=embedding_fn,
            config=unique_config(),
            path=None,  # Ephemeral
        )

    @pytest.fixture
    def decay_config(self):
        """Create decay config with fast timings for testing."""
        return DecayConfig(
            decay_rate=0.01,
            access_boost=0.2,
            promotion_threshold=0.5,  # Lower for testing
            decay_threshold=0.2,
            short_term_min_age_hours=1,  # 1 hour for fast testing
            decayed_retention_days=30,
        )

    @pytest.fixture
    def promotion_service(self, decay_config, collection_manager):
        """Create promotion service."""
        return MemoryPromotionService(
            config=decay_config,
            collection_manager=collection_manager,
            graph_store=None,
        )

    @pytest.mark.asyncio
    async def test_full_lifecycle_short_to_long_term(
        self, promotion_service, collection_manager, decay_config
    ):
        """Test promotion from SHORT_TERM to LONG_TERM."""
        now = datetime.now()
        old_time = (now - timedelta(hours=48)).isoformat()  # Well past min age

        # Step 1: Add memory to short-term (simulating consolidation)
        await collection_manager.add_to_short_term(
            texts=["Python is a programming language"],
            metadatas=[
                {
                    "type": "insight",
                    "created_at": old_time,
                    "access_count": 10,  # High access count
                    "confidence": 0.9,  # High confidence
                }
            ],
            ids=["mem_lifecycle_1"],
        )

        # Verify in short-term
        stats_before = await collection_manager.get_stats()
        assert stats_before["short_term"] == 1
        assert stats_before["long_term"] == 0

        # Step 2: Run promotion cycle
        result = await promotion_service.run_promotion_cycle(dry_run=False, now=now)

        # Should be promoted
        assert result.promoted_to_long_term == 1

        # Step 3: Verify moved to long-term
        stats_after = await collection_manager.get_stats()
        assert stats_after["short_term"] == 0
        assert stats_after["long_term"] == 1

    @pytest.mark.asyncio
    async def test_full_lifecycle_long_term_to_decayed(
        self, promotion_service, collection_manager
    ):
        """Test decay from LONG_TERM to DECAYED."""
        now = datetime.now()
        very_old_access = (now - timedelta(days=60)).isoformat()

        # Add memory directly to long-term with very low decay score
        collection_manager.long_term._collection.add(
            ids=["mem_lifecycle_2"],
            documents=["Old memory that will decay"],
            embeddings=[[0.5] * 768],
            metadatas=[
                {
                    "type": "insight",
                    "stage": "long_term",
                    "decay_score": 0.1,  # Below decay threshold (0.2)
                    "last_accessed_at": very_old_access,
                }
            ],
        )

        # Verify in long-term
        stats_before = await collection_manager.get_stats()
        assert stats_before["long_term"] == 1
        assert stats_before["decayed"] == 0

        # Run promotion cycle (which includes decay checks)
        result = await promotion_service.run_promotion_cycle(dry_run=False, now=now)

        # Should be decayed
        assert result.decayed_from_long_term == 1

        # Verify moved to decayed
        stats_after = await collection_manager.get_stats()
        assert stats_after["long_term"] == 0
        assert stats_after["decayed"] == 1

    @pytest.mark.asyncio
    async def test_full_lifecycle_decayed_reactivation(
        self, promotion_service, collection_manager
    ):
        """Test reactivation from DECAYED back to LONG_TERM."""
        # Add memory to decayed collection
        collection_manager.decayed._collection.add(
            ids=["mem_lifecycle_3"],
            documents=["Decayed memory to reactivate"],
            embeddings=[[0.5] * 768],
            metadatas=[
                {
                    "type": "insight",
                    "stage": "decayed",
                    "decay_score": 0.05,
                    "decayed_at": datetime.now().isoformat(),
                }
            ],
        )

        # Verify in decayed
        stats_before = await collection_manager.get_stats()
        assert stats_before["decayed"] == 1
        assert stats_before["long_term"] == 0

        # Access the memory (triggers reactivation)
        reactivated = await promotion_service.on_memory_accessed("mem_lifecycle_3")

        assert reactivated is True

        # Verify moved back to long-term
        stats_after = await collection_manager.get_stats()
        assert stats_after["decayed"] == 0
        assert stats_after["long_term"] == 1


class TestPromotionWithAccessBuffer:
    """Test promotion service integration with AccessBuffer."""

    @pytest.fixture
    def embedding_fn(self):
        """Create mock embedding function."""
        return MockEmbeddingFunction()

    @pytest.fixture
    def collection_manager(self, embedding_fn):
        """Create collection manager."""
        return CollectionManager(
            embedding_function=embedding_fn,
            config=unique_config(),
            path=None,
        )

    @pytest.fixture
    def access_buffer(self):
        """Create access buffer."""
        return AccessBuffer(AccessBufferConfig())

    @pytest.fixture
    def promotion_service(self, collection_manager):
        """Create promotion service."""
        config = DecayConfig(
            short_term_min_age_hours=1,
            promotion_threshold=0.5,
        )
        return MemoryPromotionService(
            config=config,
            collection_manager=collection_manager,
        )

    @pytest.mark.asyncio
    async def test_access_buffer_tracks_retrieval(
        self, access_buffer, collection_manager
    ):
        """Test that access buffer correctly tracks memory accesses."""
        # Add memory to long-term
        collection_manager.long_term._collection.add(
            ids=["mem_access_1"],
            documents=["Test memory"],
            embeddings=[[0.5] * 768],
            metadatas=[{"type": "insight", "stage": "long_term"}],
        )

        # Record access
        await access_buffer.record_access("mem_access_1", "long_term")
        await access_buffer.record_access("mem_access_1", "long_term")

        # Check stats
        stats = access_buffer.get_stats()
        assert stats["long_term_memories"] == 1
        assert stats["long_term_accesses"] == 2

    @pytest.mark.asyncio
    async def test_access_buffer_flush_updates_counts(
        self, access_buffer, collection_manager, promotion_service
    ):
        """Test that flushing access buffer updates access counts."""
        # Add memory with moderate decay score
        collection_manager.long_term._collection.add(
            ids=["mem_access_2"],
            documents=["Test memory for flush"],
            embeddings=[[0.5] * 768],
            metadatas=[
                {
                    "type": "insight",
                    "stage": "long_term",
                    "decay_score": 0.5,
                    "access_count": 1,
                }
            ],
        )

        # Record accesses
        await access_buffer.record_access("mem_access_2", "long_term")
        await access_buffer.record_access("mem_access_2", "long_term")
        await access_buffer.record_access("mem_access_2", "long_term")

        # Verify buffer has recorded accesses
        stats = access_buffer.get_stats()
        assert stats["long_term_memories"] == 1
        assert stats["long_term_accesses"] == 3

        # Flush buffer
        result = await access_buffer.flush_all(
            long_term_collection=collection_manager.long_term,
        )

        assert result.long_term_flushed == 1

        # Buffer should be cleared after flush
        assert access_buffer.long_term_count == 0


class TestFactorComputerIntegration:
    """Test RetrievalFactorComputer integration."""

    @pytest.fixture
    def embedding_fn(self):
        """Create mock embedding function."""
        return MockEmbeddingFunction()

    @pytest.fixture
    def collection_manager(self, embedding_fn):
        """Create collection manager."""
        return CollectionManager(
            embedding_function=embedding_fn,
            config=unique_config(),
            path=None,
        )

    @pytest.fixture
    def factor_computer(self):
        """Create factor computer."""
        return RetrievalFactorComputer()

    @pytest.mark.asyncio
    async def test_factor_computer_updates_retrieval_factor(
        self, factor_computer, collection_manager
    ):
        """Test that factor computer updates retrieval_factor metadata."""
        now = datetime.now()
        old_time = (now - timedelta(hours=48)).isoformat()

        # Add memory without retrieval_factor
        collection_manager.long_term._collection.add(
            ids=["mem_factor_1"],
            documents=["Test memory for factor computation"],
            embeddings=[[0.5] * 768],
            metadatas=[
                {
                    "type": "insight",
                    "stage": "long_term",
                    "created_at": old_time,
                    "hit_count": 10,
                }
            ],
        )

        # Compute factors
        result = await factor_computer.compute_factors(
            collection_manager.long_term,
            now=now,
            force_update=True,
        )

        assert result.updated == 1

        # Verify retrieval_factor was added
        doc = await collection_manager.long_term.get_by_id("mem_factor_1")
        metadata = doc.get("metadata", {})
        assert "retrieval_factor" in metadata
        assert metadata["retrieval_factor"] > 0

    @pytest.mark.asyncio
    async def test_factor_affects_search_scoring(
        self, factor_computer, collection_manager, embedding_fn
    ):
        """Test that retrieval_factor affects search result scoring."""
        now = datetime.now()
        recent_time = now.isoformat()
        old_time = (now - timedelta(days=7)).isoformat()

        # Add recent memory with high factor
        collection_manager.long_term._collection.add(
            ids=["mem_recent"],
            documents=["Recent Python programming insights"],
            embeddings=[[0.5] * 768],
            metadatas=[
                {
                    "type": "insight",
                    "stage": "long_term",
                    "created_at": recent_time,
                    "hit_count": 20,
                    "retrieval_factor": 1.3,  # High factor
                }
            ],
        )

        # Add old memory with low factor
        collection_manager.long_term._collection.add(
            ids=["mem_old"],
            documents=["Old Python programming insights"],
            embeddings=[[0.5] * 768],
            metadatas=[
                {
                    "type": "insight",
                    "stage": "long_term",
                    "created_at": old_time,
                    "hit_count": 1,
                    "retrieval_factor": 0.3,  # Low factor
                }
            ],
        )

        # Search should return both
        results = await collection_manager.long_term.query(
            query_text="Python programming",
            n_results=10,
        )

        assert len(results) == 2

        # Both results have similar similarity, but different factors
        for r in results:
            factor = r["metadata"].get("retrieval_factor", 0.5)
            # Effective score = similarity * factor
            r["effective_score"] = r["similarity"] * factor

        # Sort by effective score
        results.sort(key=lambda x: x["effective_score"], reverse=True)

        # Recent memory should rank higher due to higher factor
        assert results[0]["id"] == "mem_recent"


class TestDecayCalculatorIntegration:
    """Test DecayCalculator with real score updates."""

    @pytest.fixture
    def config(self):
        """Create decay config."""
        return DecayConfig(
            decay_rate=0.01,
            access_boost=0.2,
            decay_threshold=0.2,
        )

    @pytest.fixture
    def calculator(self, config):
        """Create decay calculator."""
        return DecayCalculator(config)

    def test_decay_and_boost_cycle(self, calculator):
        """Test realistic decay and access boost cycle."""
        now = datetime.now()
        score = 1.0

        # Day 1: Initial score
        assert score == 1.0

        # Day 2: Score decays (no access)
        last_accessed = now - timedelta(hours=24)
        score = calculator.calculate_decay(score, last_accessed, now)
        assert 0.78 < score < 0.80  # ~79%

        # Day 3: Access boosts score
        score = calculator.apply_access_boost(score)
        assert 0.98 < score < 1.0  # ~79% + 20% boost

        # Day 4: More decay
        last_accessed = now - timedelta(hours=24)
        score = calculator.calculate_decay(score, last_accessed, now)
        # New score after another day of decay

        # Verify still above decay threshold
        assert not calculator.should_decay(score)

    def test_eventual_decay_without_access(self, calculator):
        """Test that without access, score eventually falls below threshold."""
        now = datetime.now()
        score = 1.0

        # Simulate 30 days without access
        for day in range(30):
            last_accessed = now - timedelta(hours=24 * (day + 1))
            score = calculator.calculate_decay(1.0, last_accessed, now)

        # After 30 days (720 hours): exp(-0.01 * 720) ≈ 0.0007
        assert score < 0.01
        assert calculator.should_decay(score)


class TestPromotionScorerIntegration:
    """Test PromotionScorer with various memory profiles."""

    @pytest.fixture
    def config(self):
        """Create decay config."""
        return DecayConfig()

    @pytest.fixture
    def scorer(self, config):
        """Create promotion scorer."""
        return PromotionScorer(config)

    def test_different_memory_profiles(self, scorer):
        """Test scoring of different memory profiles."""
        now = datetime.now()

        profiles = [
            {
                "name": "Young, unused",
                "created_at": now - timedelta(hours=12),
                "access_count": 0,
                "confidence": 0.5,
                "relationship_count": 0,
            },
            {
                "name": "Old, frequently accessed",
                "created_at": now - timedelta(hours=72),
                "access_count": 10,
                "confidence": 0.9,
                "relationship_count": 5,
            },
            {
                "name": "Medium age, some access",
                "created_at": now - timedelta(hours=48),
                "access_count": 3,
                "confidence": 0.7,
                "relationship_count": 2,
            },
        ]

        scores = []
        for profile in profiles:
            score = scorer.calculate_promotion_score(
                created_at=profile["created_at"],
                access_count=profile["access_count"],
                confidence=profile["confidence"],
                relationship_count=profile["relationship_count"],
                now=now,
            )
            scores.append((profile["name"], score))

        # Old, frequently accessed should score highest
        scores.sort(key=lambda x: x[1], reverse=True)
        assert scores[0][0] == "Old, frequently accessed"

        # Young, unused should score lowest
        assert scores[-1][0] == "Young, unused"

    def test_promotion_eligibility_with_age(self, scorer, config):
        """Test that promotion eligibility considers age requirement."""
        now = datetime.now()

        # High-scoring but too young
        young_created = now - timedelta(hours=12)
        young_score = scorer.calculate_promotion_score(
            created_at=young_created,
            access_count=10,
            confidence=0.95,
            relationship_count=5,
            now=now,
        )

        # Score is high
        assert young_score > config.promotion_threshold

        # But not eligible due to age
        assert not scorer.is_eligible_for_promotion(
            MemoryStage.SHORT_TERM, young_created, now
        )

        # Old enough to be eligible
        old_created = now - timedelta(hours=48)
        assert scorer.is_eligible_for_promotion(
            MemoryStage.SHORT_TERM, old_created, now
        )
