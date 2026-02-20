"""
Long-Term Memory Inclusion Scorer.

Calculates whether a long-term memory should be included in context
based on a multi-factor scoring system:
- Similarity: Semantic relevancy to current query
- Age: Older memories need higher similarity to qualify
- Usage: Frequently-used memories get a boost (hit_count)

Ref: docs/build-plan/memory-lifecycle-staging-decay.md, Section "Long-Term Memory Inclusion Scoring"
"""  # noqa: E501

from __future__ import annotations

import math
from datetime import datetime

from pydantic import BaseModel, Field


class InclusionScorerConfig(BaseModel):
    """Configuration for long-term inclusion scoring."""

    decay_rate: float = Field(
        default=0.005,
        ge=0.0001,
        le=0.1,
        description="Per-hour decay rate for inclusion scoring (separate from lifecycle decay)",  # noqa: E501
    )
    usage_boost_factor: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Logarithmic boost factor for hit_count",
    )
    inclusion_threshold: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Minimum inclusion score to include memory in context",
    )


class LongTermInclusionScorer:
    """
    Calculate whether a long-term memory should be included in context.

    Inclusion = f(similarity, age, usage)

    - similarity: Semantic relevancy to current query (0.0-1.0)
    - age: Older memories need higher similarity to qualify
    - usage: Frequently-used memories get a boost (hit_count)

    This scorer is separate from lifecycle decay. While lifecycle decay
    determines when memories transition between stages (e.g., LONG_TERM -> DECAYED),
    inclusion scoring determines which memories are included in any given retrieval.

    Example usage:
        scorer = LongTermInclusionScorer()

        # Score a retrieved memory
        score = scorer.calculate_inclusion_score(
            similarity=0.8,
            created_at=datetime.fromisoformat("2024-01-10T10:00:00"),
            hit_count=5,
        )

        # Check if it should be included
        if scorer.should_include(similarity=0.8, created_at=..., hit_count=5):
            include_in_context(memory)
    """

    def __init__(self, config: InclusionScorerConfig | None = None) -> None:
        """
        Initialize the inclusion scorer.

        Args:
            config: Scorer configuration (uses defaults if None)
        """
        self._config = config or InclusionScorerConfig()

    @property
    def decay_rate(self) -> float:
        """Per-hour decay rate for age penalty."""
        return self._config.decay_rate

    @property
    def usage_boost_factor(self) -> float:
        """Factor for logarithmic hit_count boost."""
        return self._config.usage_boost_factor

    @property
    def inclusion_threshold(self) -> float:
        """Minimum score for inclusion."""
        return self._config.inclusion_threshold

    def calculate_time_factor(
        self,
        created_at: datetime,
        now: datetime | None = None,
    ) -> float:
        """
        Calculate the time-based decay factor.

        Uses exponential decay: factor = exp(-decay_rate * hours)

        Examples (with default decay_rate=0.005):
        - At 24h: ~0.89
        - At 72h (3 days): ~0.70
        - At 168h (1 week): ~0.43
        - At 336h (2 weeks): ~0.19

        Args:
            created_at: When the memory was created
            now: Current time (defaults to now)

        Returns:
            Decay factor between 0.0 and 1.0
        """
        now = now or datetime.now()
        age_hours = (now - created_at).total_seconds() / 3600

        # Ensure non-negative age
        age_hours = max(0, age_hours)

        return math.exp(-self._config.decay_rate * age_hours)

    def calculate_usage_factor(self, hit_count: int) -> float:
        """
        Calculate the usage-based boost factor.

        Uses logarithmic scaling (diminishing returns):
        - hit_count=0: 1.0
        - hit_count=1: ~1.07
        - hit_count=5: ~1.18
        - hit_count=20: ~1.30
        - hit_count=50: ~1.39

        Args:
            hit_count: Number of times memory was included in context

        Returns:
            Boost factor >= 1.0
        """
        return 1.0 + (self._config.usage_boost_factor * math.log(1 + hit_count))

    def calculate_inclusion_score(
        self,
        similarity: float,
        created_at: datetime,
        hit_count: int,
        now: datetime | None = None,
    ) -> float:
        """
        Calculate inclusion score for a long-term memory.

        Score = similarity * time_factor * usage_factor

        Args:
            similarity: Semantic similarity to query (0.0-1.0)
            created_at: When the memory was created
            hit_count: Number of times included in context
            now: Current time (defaults to now)

        Returns:
            Score between 0.0 and ~1.5 (with usage boost)
        """
        time_factor = self.calculate_time_factor(created_at, now)
        usage_factor = self.calculate_usage_factor(hit_count)

        return similarity * time_factor * usage_factor

    def should_include(
        self,
        similarity: float,
        created_at: datetime,
        hit_count: int,
        now: datetime | None = None,
    ) -> bool:
        """
        Check if memory meets inclusion threshold.

        Args:
            similarity: Semantic similarity to query (0.0-1.0)
            created_at: When the memory was created
            hit_count: Number of times included in context
            now: Current time (defaults to now)

        Returns:
            True if memory should be included in context
        """
        score = self.calculate_inclusion_score(similarity, created_at, hit_count, now)
        return score >= self._config.inclusion_threshold

    def score_and_filter(
        self,
        results: list[dict],
        now: datetime | None = None,
    ) -> list[dict]:
        """
        Score a list of retrieval results and filter by threshold.

        Adds 'inclusion_score' to each result and filters out those
        below the threshold.

        Args:
            results: List of retrieval results with 'similarity', 'metadata'
            now: Current time (defaults to now)

        Returns:
            Filtered list sorted by inclusion_score descending
        """
        now = now or datetime.now()
        scored_results = []

        for result in results:
            similarity = result.get("similarity", 0.0)
            metadata = result.get("metadata", {})

            # Parse created_at from metadata
            created_at_str = metadata.get("created_at")
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str)
                except (ValueError, TypeError):
                    created_at = now  # Fallback to now if parse fails
            else:
                created_at = now

            hit_count = int(metadata.get("hit_count", 0))

            # Calculate inclusion score
            inclusion_score = self.calculate_inclusion_score(
                similarity=similarity,
                created_at=created_at,
                hit_count=hit_count,
                now=now,
            )

            # Add score to result
            result_with_score = {**result, "inclusion_score": inclusion_score}

            # Filter by threshold
            if inclusion_score >= self._config.inclusion_threshold:
                scored_results.append(result_with_score)

        # Sort by inclusion score descending
        return sorted(scored_results, key=lambda x: x["inclusion_score"], reverse=True)
