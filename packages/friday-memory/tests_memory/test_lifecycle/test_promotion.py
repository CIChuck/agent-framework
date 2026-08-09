# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
# mypy: disallow-untyped-defs=False
"""Tests for PromotionScorer and MemoryPromotionService."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from friday_memory.lifecycle.decay import DecayConfig
from friday_memory.lifecycle.promotion import (
    MemoryPromotionService,
    PromotionResult,
    PromotionScorer,
)
from friday_memory.lifecycle.stages import MemoryStage
from friday_memory.retrieval.collection_manager import (
    CollectionConfig,
    CollectionManager,
)


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


class TestPromotionScorer:
    """Test PromotionScorer class."""

    @pytest.fixture
    def config(self):
        """Create default decay config."""
        return DecayConfig()

    @pytest.fixture
    def scorer(self, config):
        """Create scorer with default config."""
        return PromotionScorer(config)

    @pytest.fixture
    def now(self):
        """Fixed timestamp for testing."""
        return datetime(2024, 1, 15, 12, 0, 0)

    def test_calculate_promotion_score_new_memory(self, scorer, now) -> None:
        """Brand new memory should have low promotion score."""
        created_at = now - timedelta(hours=1)  # 1 hour old
        score = scorer.calculate_promotion_score(
            created_at=created_at,
            access_count=0,
            confidence=0.5,
            relationship_count=0,
            now=now,
        )
        # age: 1/72 ≈ 0.014 * 0.2 = 0.003
        # access: 0/5 = 0 * 0.4 = 0
        # confidence: 0.5 * 0.2 = 0.1
        # connection: 0/3 = 0 * 0.2 = 0
        # Total ≈ 0.103
        assert 0.1 < score < 0.15

    def test_calculate_promotion_score_mature_memory(self, scorer, now) -> None:
        """Well-established memory should have high promotion score."""
        created_at = now - timedelta(hours=72)  # 3 days old (max age factor)
        score = scorer.calculate_promotion_score(
            created_at=created_at,
            access_count=5,  # Max access factor
            confidence=0.9,
            relationship_count=3,  # Max connection factor
            now=now,
        )
        # age: 72/72 = 1.0 * 0.2 = 0.2
        # access: 5/5 = 1.0 * 0.4 = 0.4
        # confidence: 0.9 * 0.2 = 0.18
        # connection: 3/3 = 1.0 * 0.2 = 0.2
        # Total = 0.98
        assert score > 0.9

    def test_calculate_promotion_score_factors_capped(self, scorer, now) -> None:
        """Factors should be capped at 1.0."""
        created_at = now - timedelta(hours=200)  # Way over 72h
        score = scorer.calculate_promotion_score(
            created_at=created_at,
            access_count=100,  # Way over 5
            confidence=1.0,
            relationship_count=100,  # Way over 3
            now=now,
        )
        # All factors should be capped at 1.0
        # Total should equal sum of weights = 1.0
        assert 0.99 <= score <= 1.01

    def test_is_eligible_wrong_stage(self, scorer, now) -> None:
        """Only SHORT_TERM memories are eligible for promotion."""
        created_at = now - timedelta(hours=48)

        assert not scorer.is_eligible_for_promotion(
            MemoryStage.LONG_TERM, created_at, now
        )
        assert not scorer.is_eligible_for_promotion(
            MemoryStage.DECAYED, created_at, now
        )
        assert not scorer.is_eligible_for_promotion(
            MemoryStage.EPISODIC, created_at, now
        )

    def test_is_eligible_too_young(self, scorer, now) -> None:
        """Memory must be at least 24h old (default) to be eligible."""
        created_at = now - timedelta(hours=12)  # Only 12 hours old

        assert not scorer.is_eligible_for_promotion(
            MemoryStage.SHORT_TERM, created_at, now
        )

    def test_is_eligible_old_enough(self, scorer, now) -> None:
        """Memory 24h+ old should be eligible."""
        created_at = now - timedelta(hours=25)  # 25 hours old

        assert scorer.is_eligible_for_promotion(MemoryStage.SHORT_TERM, created_at, now)

    def test_aware_synthesis_timestamp_is_eligible_with_naive_now(
        self,
        scorer,
        now,
    ) -> None:
        aware_now = now.astimezone()
        created_at = (aware_now - timedelta(hours=25)).astimezone(timezone.utc)

        assert scorer.is_eligible_for_promotion(
            MemoryStage.SHORT_TERM,
            created_at,
            now,
        )

    def test_should_promote_above_threshold(self, scorer) -> None:
        """Score >= 0.7 (default threshold) should promote."""
        assert scorer.should_promote(0.7)
        assert scorer.should_promote(0.8)
        assert scorer.should_promote(1.0)

    def test_should_promote_below_threshold(self, scorer) -> None:
        """Score < 0.7 should not promote."""
        assert not scorer.should_promote(0.69)
        assert not scorer.should_promote(0.5)
        assert not scorer.should_promote(0.0)

    def test_custom_weights(self, now) -> None:
        """Test with custom promotion weights."""
        config = DecayConfig(
            promotion_weight_age=0.0,
            promotion_weight_access=1.0,  # Only access matters
            promotion_weight_confidence=0.0,
            promotion_weight_connection=0.0,
        )
        scorer = PromotionScorer(config)

        created_at = now - timedelta(hours=72)

        # With only access mattering
        score_no_access = scorer.calculate_promotion_score(
            created_at=created_at,
            access_count=0,
            confidence=1.0,
            relationship_count=10,
            now=now,
        )
        assert score_no_access == 0.0

        score_max_access = scorer.calculate_promotion_score(
            created_at=created_at,
            access_count=5,
            confidence=0.0,
            relationship_count=0,
            now=now,
        )
        assert score_max_access == 1.0

    def test_get_factor_breakdown(self, scorer, now) -> None:
        """Test factor breakdown for debugging."""
        created_at = now - timedelta(hours=36)
        breakdown = scorer.get_factor_breakdown(
            created_at=created_at,
            access_count=2,
            confidence=0.8,
            relationship_count=1,
            now=now,
        )

        assert "factors" in breakdown
        assert "weights" in breakdown
        assert "contributions" in breakdown
        assert "total" in breakdown

        # Check factors are calculated correctly
        assert 0.49 < breakdown["factors"]["age"] < 0.51  # 36/72 = 0.5
        assert breakdown["factors"]["access"] == 0.4  # 2/5
        assert breakdown["factors"]["confidence"] == 0.8
        assert 0.32 < breakdown["factors"]["connection"] < 0.34  # 1/3


class TestPromotionResult:
    """Test PromotionResult dataclass."""

    def test_default_values(self) -> None:
        """Test default initialization."""
        result = PromotionResult()
        assert result.promoted_to_long_term == 0
        assert result.decayed_from_long_term == 0
        assert result.reactivated == 0
        assert result.errors == []
        assert not result.has_errors()

    def test_has_errors(self) -> None:
        """Test error detection."""
        result = PromotionResult(errors=["Something went wrong"])
        assert result.has_errors()

    def test_summary_no_changes(self) -> None:
        """Test summary with no changes."""
        result = PromotionResult()
        assert result.summary() == "No changes"

    def test_summary_with_changes(self) -> None:
        """Test summary with various changes."""
        result = PromotionResult(
            promoted_to_long_term=5,
            decayed_from_long_term=2,
            reactivated=1,
        )
        summary = result.summary()
        assert "promoted=5" in summary
        assert "decayed_lt=2" in summary
        assert "reactivated=1" in summary


class TestMemoryPromotionService:
    """Test MemoryPromotionService class."""

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
    def config(self):
        """Create decay config with short min age for testing."""
        return DecayConfig(
            short_term_min_age_hours=1,  # 1 hour for faster testing
            promotion_threshold=0.5,  # Lower threshold for testing
            decay_threshold=0.2,
        )

    @pytest.fixture
    def service(self, config, collection_manager):
        """Create promotion service."""
        return MemoryPromotionService(
            config=config,
            collection_manager=collection_manager,
            graph_store=None,
        )

    @pytest.mark.asyncio
    async def test_run_promotion_cycle_empty(self, service) -> None:
        """Test promotion cycle with no memories."""
        result = await service.run_promotion_cycle(dry_run=True)

        assert result.promoted_to_long_term == 0
        assert result.decayed_from_long_term == 0
        assert not result.has_errors()

    @pytest.mark.asyncio
    async def test_run_promotion_cycle_promotes_eligible(
        self, service, collection_manager
    ) -> None:
        """Test that eligible short-term memories get promoted."""
        now = datetime.now()
        old_time = (now - timedelta(hours=48)).isoformat()  # 48h old

        # Add eligible memory to short-term
        await collection_manager.add_to_short_term(
            texts=["Memory ready for promotion"],
            metadatas=[
                {
                    "type": "insight",
                    "created_at": old_time,
                    "access_count": 5,
                    "confidence": 0.9,
                }
            ],
            ids=["mem_promote"],
        )

        # Dry run first
        result = await service.run_promotion_cycle(dry_run=True, now=now)
        assert result.promoted_to_long_term == 1

        # Verify not actually promoted
        stats = await collection_manager.get_stats()
        assert stats["short_term"] == 1
        assert stats["long_term"] == 0

        # Execute promotion
        result = await service.run_promotion_cycle(dry_run=False, now=now)
        assert result.promoted_to_long_term == 1

        # Verify promoted
        stats = await collection_manager.get_stats()
        assert stats["short_term"] == 0
        assert stats["long_term"] == 1

    @pytest.mark.asyncio
    async def test_run_promotion_cycle_does_not_promote_young(
        self, service, collection_manager
    ) -> None:
        """Test that young memories are not promoted."""
        now = datetime.now()
        recent_time = (now - timedelta(minutes=30)).isoformat()  # 30min old

        await collection_manager.add_to_short_term(
            texts=["Too young memory"],
            metadatas=[
                {
                    "type": "insight",
                    "created_at": recent_time,
                    "access_count": 5,
                    "confidence": 0.9,
                }
            ],
            ids=["mem_young"],
        )

        result = await service.run_promotion_cycle(dry_run=True, now=now)
        assert result.promoted_to_long_term == 0

    @pytest.mark.asyncio
    async def test_run_promotion_cycle_accepts_aware_synthesis_created_at(
        self,
        service,
        collection_manager,
    ) -> None:
        now = datetime(2024, 1, 15, 12, 0, 0)
        created_at = (now.astimezone() - timedelta(hours=48)).astimezone(timezone.utc)
        await collection_manager.add_to_short_term(
            texts=["Timezone-aware synthesized memory"],
            metadatas=[
                {
                    "type": "meta_insight",
                    "created_at": created_at.isoformat(),
                    "access_count": 5,
                    "confidence": 0.9,
                    "maintenance_generated": True,
                    "verification_status": "verified",
                }
            ],
            ids=["aware-synthesis"],
        )

        result = await service.run_promotion_cycle(dry_run=True, now=now)

        assert result.errors == []
        assert result.promoted_to_long_term == 1

    @pytest.mark.asyncio
    async def test_run_promotion_cycle_decays_long_term(
        self, service, collection_manager
    ) -> None:
        """Test that low-score long-term memories get decayed."""
        now = datetime.now()
        old_access = (now - timedelta(days=30)).isoformat()  # Very old access

        # Add directly to long-term with low decay score
        await collection_manager.long_term.add_documents(
            texts=["Decaying memory"],
            metadatas=[
                {
                    "type": "insight",
                    "stage": "long_term",
                    "decay_score": 0.1,  # Below threshold (0.2)
                    "last_accessed_at": old_access,
                }
            ],
            ids=["mem_decay"],
        )

        # Dry run
        result = await service.run_promotion_cycle(dry_run=True, now=now)
        assert result.decayed_from_long_term == 1

        # Execute
        result = await service.run_promotion_cycle(dry_run=False, now=now)
        assert result.decayed_from_long_term == 1

        # Verify moved to decayed
        stats = await collection_manager.get_stats()
        assert stats["long_term"] == 0
        assert stats["decayed"] == 1

    @pytest.mark.asyncio
    async def test_on_memory_accessed_reactivates_decayed(
        self, service, collection_manager
    ) -> None:
        """Test that accessing a decayed memory reactivates it."""
        # Add memory to decayed collection (sync operation)
        collection_manager.decayed._collection.add(
            ids=["mem_decayed"],
            documents=["Decayed memory"],
            embeddings=[[0.5] * 768],
            metadatas=[
                {
                    "type": "insight",
                    "stage": "decayed",
                    "decay_score": 0.1,
                }
            ],
        )

        # Verify in decayed
        stats_before = await collection_manager.get_stats()
        assert stats_before["decayed"] == 1
        assert stats_before["long_term"] == 0

        # Access the memory
        reactivated = await service.on_memory_accessed("mem_decayed")
        assert reactivated is True

        # Verify reactivated to long-term
        stats_after = await collection_manager.get_stats()
        assert stats_after["decayed"] == 0
        assert stats_after["long_term"] == 1

    @pytest.mark.asyncio
    async def test_on_memory_accessed_boosts_long_term(
        self, service, collection_manager
    ) -> None:
        """Test that accessing long-term memory boosts decay score."""
        # Add memory to long-term (sync operation)
        collection_manager.long_term._collection.add(
            ids=["mem_lt"],
            documents=["Long-term memory"],
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

        # Access the memory
        reactivated = await service.on_memory_accessed("mem_lt")
        assert reactivated is False  # Not reactivated, just boosted

        # Verify score boosted
        doc = await collection_manager.long_term.get_by_id("mem_lt")
        metadata = doc.get("metadata", {})
        assert metadata.get("decay_score") > 0.5  # Boosted from 0.5
        assert metadata.get("access_count") == 2  # Incremented
