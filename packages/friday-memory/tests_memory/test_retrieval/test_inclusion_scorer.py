# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
# mypy: disallow-untyped-defs=False
"""Tests for LongTermInclusionScorer."""

from datetime import datetime, timedelta, timezone

import pytest
from friday_memory.retrieval.inclusion_scorer import (
    InclusionScorerConfig,
    LongTermInclusionScorer,
)


class TestInclusionScorerConfig:
    """Test InclusionScorerConfig model."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = InclusionScorerConfig()
        assert config.decay_rate == 0.005
        assert config.usage_boost_factor == 0.1
        assert config.inclusion_threshold == 0.6

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = InclusionScorerConfig(
            decay_rate=0.01,
            usage_boost_factor=0.2,
            inclusion_threshold=0.5,
        )
        assert config.decay_rate == 0.01
        assert config.usage_boost_factor == 0.2
        assert config.inclusion_threshold == 0.5


class TestLongTermInclusionScorer:
    """Test LongTermInclusionScorer class."""

    @pytest.fixture
    def scorer(self):
        """Create scorer with default config."""
        return LongTermInclusionScorer()

    @pytest.fixture
    def now(self):
        """Fixed timestamp for testing."""
        return datetime(2024, 1, 15, 12, 0, 0)

    def test_time_factor_fresh_memory(self, scorer, now) -> None:
        """Fresh memory should have time_factor near 1.0."""
        created_at = now - timedelta(hours=1)
        time_factor = scorer.calculate_time_factor(created_at, now)
        # At 1 hour with decay_rate=0.005: exp(-0.005 * 1) ≈ 0.995
        assert 0.99 < time_factor < 1.0

    def test_time_factor_day_old_memory(self, scorer, now) -> None:
        """Day-old memory should have time_factor around 0.89."""
        created_at = now - timedelta(hours=24)
        time_factor = scorer.calculate_time_factor(created_at, now)
        # At 24 hours with decay_rate=0.005: exp(-0.005 * 24) ≈ 0.89
        assert 0.88 < time_factor < 0.90

    def test_time_factor_accepts_aware_timestamp_with_naive_now(
        self,
        scorer,
        now,
    ) -> None:
        aware_now = now.astimezone()
        created_at = (aware_now - timedelta(hours=24)).astimezone(timezone.utc)

        time_factor = scorer.calculate_time_factor(created_at, now)

        assert 0.88 < time_factor < 0.90

    def test_time_factor_week_old_memory(self, scorer, now) -> None:
        """Week-old memory should have time_factor around 0.43."""
        created_at = now - timedelta(hours=168)
        time_factor = scorer.calculate_time_factor(created_at, now)
        # At 168 hours with decay_rate=0.005: exp(-0.005 * 168) ≈ 0.43
        assert 0.42 < time_factor < 0.44

    def test_usage_factor_no_hits(self, scorer) -> None:
        """Memory with no hits should have usage_factor of 1.0."""
        usage_factor = scorer.calculate_usage_factor(0)
        assert usage_factor == 1.0

    def test_usage_factor_low_hits(self, scorer) -> None:
        """Memory with 5 hits should have moderate boost."""
        usage_factor = scorer.calculate_usage_factor(5)
        # 1 + 0.1 * log(6) ≈ 1.18
        assert 1.17 < usage_factor < 1.19

    def test_usage_factor_high_hits(self, scorer) -> None:
        """Memory with 50 hits should have significant boost."""
        usage_factor = scorer.calculate_usage_factor(50)
        # 1 + 0.1 * log(51) ≈ 1.39
        assert 1.38 < usage_factor < 1.40

    def test_inclusion_score_recent_high_similarity(self, scorer, now) -> None:
        """Recent memory with high similarity should score well."""
        created_at = now - timedelta(hours=24)
        score = scorer.calculate_inclusion_score(
            similarity=0.8,
            created_at=created_at,
            hit_count=5,
            now=now,
        )
        # 0.8 * ~0.89 * ~1.18 ≈ 0.84
        assert score > 0.8

    def test_inclusion_score_old_high_similarity(self, scorer, now) -> None:
        """Week-old memory with high similarity should score moderately."""
        created_at = now - timedelta(hours=168)
        score = scorer.calculate_inclusion_score(
            similarity=0.9,
            created_at=created_at,
            hit_count=5,
            now=now,
        )
        # 0.9 * ~0.43 * ~1.18 ≈ 0.46
        assert 0.4 < score < 0.5

    def test_should_include_above_threshold(self, scorer, now) -> None:
        """Memory above threshold should be included."""
        created_at = now - timedelta(hours=24)
        should_include = scorer.should_include(
            similarity=0.8,
            created_at=created_at,
            hit_count=5,
            now=now,
        )
        assert should_include is True

    def test_should_include_below_threshold(self, scorer, now) -> None:
        """Memory below threshold should not be included."""
        created_at = now - timedelta(hours=168)
        should_include = scorer.should_include(
            similarity=0.6,
            created_at=created_at,
            hit_count=0,
            now=now,
        )
        # 0.6 * ~0.43 * 1.0 ≈ 0.26
        assert should_include is False

    def test_score_and_filter_filters_results(self, scorer, now) -> None:
        """score_and_filter should filter results below threshold."""
        results = [
            {
                "id": "mem1",
                "similarity": 0.9,
                "metadata": {
                    "created_at": (now - timedelta(hours=24)).isoformat(),
                    "hit_count": 10,
                },
            },
            {
                "id": "mem2",
                "similarity": 0.4,
                "metadata": {
                    "created_at": (now - timedelta(hours=168)).isoformat(),
                    "hit_count": 0,
                },
            },
            {
                "id": "mem3",
                "similarity": 0.7,
                "metadata": {
                    "created_at": (now - timedelta(hours=48)).isoformat(),
                    "hit_count": 5,
                },
            },
        ]

        filtered = scorer.score_and_filter(results, now)

        # Should filter out mem2 (low similarity + old + no hits)
        assert len(filtered) == 2
        assert all("inclusion_score" in r for r in filtered)
        # Should be sorted by inclusion_score descending
        assert filtered[0]["id"] == "mem1"

    def test_score_and_filter_handles_missing_metadata(self, scorer, now) -> None:
        """score_and_filter should handle missing metadata gracefully."""
        results = [
            {
                "id": "mem1",
                "similarity": 0.9,
                "metadata": {},  # Missing created_at and hit_count
            },
        ]

        filtered = scorer.score_and_filter(results, now)
        assert len(filtered) == 1
        assert "inclusion_score" in filtered[0]
