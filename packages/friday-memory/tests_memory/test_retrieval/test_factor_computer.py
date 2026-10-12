# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
# mypy: disallow-untyped-defs=False
"""Tests for RetrievalFactorComputer."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from friday_memory.retrieval.collection_manager import (
    CollectionConfig,
    CollectionManager,
)
from friday_memory.retrieval.factor_computer import (
    FactorComputerConfig,
    FactorComputeResult,
    RetrievalFactorComputer,
    calculate_inclusion_score_fast,
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


class TestFactorComputerConfig:
    """Test FactorComputerConfig defaults and customization."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = FactorComputerConfig()
        assert config.decay_rate == 0.005
        assert config.usage_boost_factor == 0.1
        assert config.min_factor == 0.01

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = FactorComputerConfig(
            decay_rate=0.01,
            usage_boost_factor=0.2,
            min_factor=0.05,
        )
        assert config.decay_rate == 0.01
        assert config.usage_boost_factor == 0.2
        assert config.min_factor == 0.05


class TestFactorComputeResult:
    """Test FactorComputeResult dataclass."""

    def test_default_values(self) -> None:
        """Test default initialization."""
        result = FactorComputeResult()
        assert result.updated == 0
        assert result.skipped == 0
        assert result.errors == []
        assert not result.has_errors()

    def test_has_errors(self) -> None:
        """Test error detection."""
        result = FactorComputeResult(errors=["Something went wrong"])
        assert result.has_errors()

    def test_summary(self) -> None:
        """Test summary generation."""
        result = FactorComputeResult(updated=10, skipped=5)
        summary = result.summary()
        assert "updated=10" in summary
        assert "skipped=5" in summary


class TestRetrievalFactorComputer:
    """Test RetrievalFactorComputer class."""

    @pytest.fixture
    def config(self):
        """Create default config."""
        return FactorComputerConfig()

    @pytest.fixture
    def computer(self, config):
        """Create computer with default config."""
        return RetrievalFactorComputer(config)

    @pytest.fixture
    def now(self):
        """Fixed timestamp for testing."""
        return datetime(2024, 1, 15, 12, 0, 0)

    def test_compute_time_factor_fresh_memory(self, computer, now) -> None:
        """Fresh memory should have time factor close to 1.0."""
        created_at = now - timedelta(hours=1)
        factor = computer.compute_time_factor(created_at, now)

        # exp(-0.005 * 1) ≈ 0.995
        assert 0.99 < factor <= 1.0

    def test_compute_time_factor_day_old_memory(self, computer, now) -> None:
        """24-hour old memory should have reduced time factor."""
        created_at = now - timedelta(hours=24)
        factor = computer.compute_time_factor(created_at, now)

        # exp(-0.005 * 24) ≈ 0.887
        assert 0.88 < factor < 0.90

    def test_compute_time_factor_accepts_aware_timestamp_with_naive_now(
        self,
        computer,
        now,
    ) -> None:
        aware_now = now.astimezone()
        created_at = (aware_now - timedelta(hours=24)).astimezone(UTC)

        factor = computer.compute_time_factor(created_at, now)

        assert 0.88 < factor < 0.90

    def test_compute_time_factor_week_old_memory(self, computer, now) -> None:
        """Week-old memory should have significantly reduced time factor."""
        created_at = now - timedelta(hours=168)
        factor = computer.compute_time_factor(created_at, now)

        # exp(-0.005 * 168) ≈ 0.43
        assert 0.42 < factor < 0.44

    def test_compute_time_factor_very_old_memory(self, computer, now) -> None:
        """Very old memory should hit min_factor floor."""
        config = FactorComputerConfig(min_factor=0.1)
        computer = RetrievalFactorComputer(config)

        created_at = now - timedelta(days=365)  # Year old
        factor = computer.compute_time_factor(created_at, now)

        # Should be floored at min_factor
        assert factor >= 0.1

    def test_compute_usage_factor_no_hits(self, computer) -> None:
        """Memory with no hits should have usage factor of 1.0."""
        factor = computer.compute_usage_factor(0)
        assert factor == 1.0

    def test_compute_usage_factor_low_hits(self, computer) -> None:
        """Memory with low hits should have slightly boosted factor."""
        factor = computer.compute_usage_factor(1)
        # 1.0 + (0.1 * log(2)) ≈ 1.069
        assert 1.06 < factor < 1.08

    def test_compute_usage_factor_high_hits(self, computer) -> None:
        """Memory with high hits should have significant boost."""
        factor = computer.compute_usage_factor(20)
        # 1.0 + (0.1 * log(21)) ≈ 1.30
        assert 1.29 < factor < 1.31

    def test_compute_usage_factor_very_high_hits(self, computer) -> None:
        """Usage factor has diminishing returns."""
        factor_50 = computer.compute_usage_factor(50)
        factor_100 = computer.compute_usage_factor(100)

        # High hit counts should still boost but with diminishing returns
        assert factor_50 < factor_100
        # Difference should be small due to log scaling
        assert factor_100 - factor_50 < 0.1

    def test_compute_retrieval_factor_fresh_unused(self, computer, now) -> None:
        """Fresh unused memory should have factor close to 1.0."""
        created_at = now - timedelta(hours=1)
        factor = computer.compute_retrieval_factor(created_at, hit_count=0, now=now)

        # time_factor ≈ 0.995, usage_factor = 1.0
        assert 0.99 < factor <= 1.0

    def test_compute_retrieval_factor_old_popular(self, computer, now) -> None:
        """Old but popular memory should maintain decent factor."""
        created_at = now - timedelta(hours=168)  # Week old
        factor = computer.compute_retrieval_factor(created_at, hit_count=20, now=now)

        # time_factor ≈ 0.43, usage_factor ≈ 1.30
        # Combined ≈ 0.56
        assert 0.5 < factor < 0.6

    def test_compute_retrieval_factor_combines_factors(self, computer, now) -> None:
        """Retrieval factor should be product of time and usage factors."""
        created_at = now - timedelta(hours=24)

        time_factor = computer.compute_time_factor(created_at, now)
        usage_factor = computer.compute_usage_factor(5)
        combined = computer.compute_retrieval_factor(created_at, hit_count=5, now=now)

        # Should be approximately equal to product
        expected = time_factor * usage_factor
        assert abs(combined - expected) < 0.001


class TestRetrievalFactorComputerWithCollection:
    """Test RetrievalFactorComputer with actual collections."""

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
    def computer(self):
        """Create factor computer."""
        return RetrievalFactorComputer()

    @pytest.mark.asyncio
    async def test_compute_factors_empty_collection(self, computer, collection_manager) -> None:
        """Test computing factors on empty collection."""
        result = await computer.compute_factors(collection_manager.long_term)

        assert result.updated == 0
        assert result.skipped == 0
        assert not result.has_errors()

    @pytest.mark.asyncio
    async def test_compute_factors_updates_metadata(self, computer, collection_manager) -> None:
        """Test that compute_factors updates retrieval_factor in metadata."""
        now = datetime.now()
        old_time = (now - timedelta(hours=24)).isoformat()

        # Add memory to long-term collection
        collection_manager.long_term._collection.add(
            ids=["mem1"],
            documents=["Test memory"],
            embeddings=[[0.5] * 768],
            metadatas=[
                {
                    "type": "insight",
                    "stage": "long_term",
                    "created_at": old_time,
                    "hit_count": 5,
                }
            ],
        )

        # Compute factors
        result = await computer.compute_factors(
            collection_manager.long_term,
            now=now,
            force_update=True,
        )

        assert result.updated == 1
        assert not result.has_errors()

        # Verify metadata was updated
        doc = await collection_manager.long_term.get_by_id("mem1")
        metadata = doc.get("metadata", {})

        assert "retrieval_factor" in metadata
        assert "factor_computed_at" in metadata
        assert 0.0 < metadata["retrieval_factor"] < 2.0  # Reasonable range

    @pytest.mark.asyncio
    async def test_compute_factors_skips_recently_computed(
        self, computer, collection_manager
    ) -> None:
        """Test that recently computed factors are skipped."""
        now = datetime.now()

        # Add memory with recently computed factor
        collection_manager.long_term._collection.add(
            ids=["mem1"],
            documents=["Test memory"],
            embeddings=[[0.5] * 768],
            metadatas=[
                {
                    "type": "insight",
                    "stage": "long_term",
                    "created_at": now.isoformat(),
                    "hit_count": 0,
                    "retrieval_factor": 1.0,
                    "factor_computed_at": now.isoformat(),  # Just computed
                }
            ],
        )

        # Compute factors without force
        result = await computer.compute_factors(
            collection_manager.long_term,
            now=now,
            force_update=False,
        )

        assert result.skipped == 1
        assert result.updated == 0

    @pytest.mark.asyncio
    async def test_compute_factors_force_update(self, computer, collection_manager) -> None:
        """Test that force_update recomputes all factors."""
        now = datetime.now()

        # Add memory with recently computed factor
        collection_manager.long_term._collection.add(
            ids=["mem1"],
            documents=["Test memory"],
            embeddings=[[0.5] * 768],
            metadatas=[
                {
                    "type": "insight",
                    "stage": "long_term",
                    "created_at": now.isoformat(),
                    "hit_count": 10,
                    "retrieval_factor": 0.5,  # Old value
                    "factor_computed_at": now.isoformat(),
                }
            ],
        )

        # Compute factors with force
        result = await computer.compute_factors(
            collection_manager.long_term,
            now=now,
            force_update=True,
        )

        assert result.updated == 1
        assert result.skipped == 0


class TestCalculateInclusionScoreFast:
    """Test the fast inclusion score helper function."""

    def test_with_retrieval_factor(self) -> None:
        """Test score calculation with pre-computed factor."""
        score = calculate_inclusion_score_fast(
            similarity=0.8,
            metadata={"retrieval_factor": 1.2},
        )
        assert abs(score - 0.96) < 0.001  # 0.8 * 1.2

    def test_with_missing_factor(self) -> None:
        """Test fallback when retrieval_factor is missing."""
        score = calculate_inclusion_score_fast(
            similarity=0.8,
            metadata={},  # No retrieval_factor
        )
        assert abs(score - 0.4) < 0.001  # 0.8 * 0.5 (default)

    def test_with_low_similarity(self) -> None:
        """Test with low similarity score."""
        score = calculate_inclusion_score_fast(
            similarity=0.3,
            metadata={"retrieval_factor": 1.5},
        )
        assert abs(score - 0.45) < 0.001  # 0.3 * 1.5

    def test_performance_vs_full_calculation(self) -> None:
        """Verify fast calculation matches expected formula."""
        # This is more of a documentation test
        similarity = 0.75
        retrieval_factor = 1.1

        fast_score = calculate_inclusion_score_fast(
            similarity=similarity,
            metadata={"retrieval_factor": retrieval_factor},
        )

        expected = similarity * retrieval_factor
        assert fast_score == expected
