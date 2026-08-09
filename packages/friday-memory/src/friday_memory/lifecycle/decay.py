# mypy: ignore-errors
"""
Decay Configuration and Calculator.

Implements exponential temporal decay for memory lifecycle management.
The decay formula: score(t) = score_0 * exp(-lambda * hours_since_last_access)

Ref: docs/archive/build-plans/completed/friday-core-legacy/memory-lifecycle-staging-decay.md, Section "Core Components"
"""

import math
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from friday_memory.temporal import elapsed_hours


class DecayConfig(BaseModel):
    """
    Configuration for temporal decay mechanism.

    Two Decay Rates:
    - `decay_rate` (lifecycle decay): Controls stage transitions
      (SHORT_TERM -> LONG_TERM -> DECAYED). Default: 0.01/hour.
    - Inclusion decay (in LongTermInclusionScorer): Affects retrieval
      priority within a stage. Default: 0.005/hour. (Separate config)

    These serve different purposes: lifecycle decay determines whether
    a memory is worth keeping, while inclusion decay determines whether
    it's worth retrieving for a specific query.
    """

    enabled: bool = Field(
        default=True,
        description="Enable decay calculations",
    )

    # Decay parameters
    decay_rate: float = Field(
        default=0.01,  # Softer curve: ~79% after 24h, ~37% after 1 week
        ge=0.001,
        le=0.5,
        description="Lambda for exponential decay (higher = faster decay). "
        "At 0.01: 24h->79%, 72h->49%, 168h->19%",
    )
    access_boost: float = Field(
        default=0.2,
        ge=0.0,
        le=0.5,
        description="Score boost on each access (capped at 1.0)",
    )

    # Thresholds
    promotion_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum promotion score for SHORT_TERM -> LONG_TERM promotion",
    )
    decay_threshold: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Score below which memory transitions to DECAYED stage",
    )

    # Timing
    short_term_min_age_hours: int = Field(
        default=24,
        ge=1,
        description="Minimum hours in SHORT_TERM before eligible for promotion",
    )
    decay_check_interval_hours: int = Field(
        default=24,
        ge=1,
        description="How often to run decay calculations",
    )

    # Cleanup
    decayed_retention_days: int = Field(
        default=30,
        ge=1,
        description="Days to retain DECAYED memories before hard deletion",
    )

    # Promotion scoring weights (must sum to 1.0)
    promotion_weight_age: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Weight for time spent in short-term stage",
    )
    promotion_weight_access: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="Weight for access frequency (most important)",
    )
    promotion_weight_confidence: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Weight for extraction confidence score",
    )
    promotion_weight_connection: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Weight for graph connection count",
    )

    @model_validator(mode="after")
    def validate_weights_sum(self) -> "DecayConfig":
        """Ensure promotion weights sum to 1.0."""
        total = (
            self.promotion_weight_age
            + self.promotion_weight_access
            + self.promotion_weight_confidence
            + self.promotion_weight_connection
        )
        if not (0.99 <= total <= 1.01):  # Allow small float tolerance
            raise ValueError(f"Promotion weights must sum to 1.0, got {total:.3f}")
        return self

    def get_promotion_weights(self) -> dict[str, float]:
        """Get promotion weights as a dictionary."""
        return {
            "age": self.promotion_weight_age,
            "access": self.promotion_weight_access,
            "confidence": self.promotion_weight_confidence,
            "connection": self.promotion_weight_connection,
        }


class DecayCalculator:
    """
    Calculates temporal decay for memory lifecycle management.

    Uses exponential decay formula:
        score(t) = score_0 * exp(-lambda * hours_since_last_access)

    where lambda is the decay_rate from DecayConfig.
    """

    def __init__(self, config: DecayConfig):
        """
        Initialize the decay calculator.

        Args:
            config: Decay configuration with rate and thresholds.
        """
        self._config = config

    @property
    def config(self) -> DecayConfig:
        """Get the decay configuration."""
        return self._config

    def calculate_decay(
        self,
        current_score: float,
        last_accessed_at: datetime,
        now: datetime | None = None,
    ) -> float:
        """
        Calculate the decayed score based on time since last access.

        Args:
            current_score: The current decay score (0.0 to 1.0).
            last_accessed_at: When the memory was last accessed.
            now: Current time (defaults to datetime.now()).

        Returns:
            New decay score after applying exponential decay.
        """
        if not self._config.enabled:
            return current_score

        hours_since_access = elapsed_hours(last_accessed_at, now)

        # Apply exponential decay
        decay_factor = math.exp(-self._config.decay_rate * hours_since_access)
        new_score = current_score * decay_factor

        # Ensure score stays in valid range
        return max(0.0, min(1.0, new_score))

    def apply_access_boost(self, current_score: float) -> float:
        """
        Apply a boost to the decay score when memory is accessed.

        Args:
            current_score: The current decay score.

        Returns:
            New score after applying access boost (capped at 1.0).
        """
        if not self._config.enabled:
            return current_score

        new_score = current_score + self._config.access_boost
        return min(1.0, new_score)

    def should_promote(self, score: float) -> bool:
        """
        Check if a memory's promotion score meets the promotion threshold.

        Args:
            score: The calculated promotion score (not decay score).

        Returns:
            True if the score meets or exceeds the promotion threshold.
        """
        return score >= self._config.promotion_threshold

    def should_decay(self, score: float) -> bool:
        """
        Check if a memory's decay score is below the decay threshold.

        Args:
            score: The current decay score.

        Returns:
            True if the score is below the decay threshold.
        """
        return score < self._config.decay_threshold

    def is_eligible_for_promotion_check(
        self,
        created_at: datetime,
        now: datetime | None = None,
    ) -> bool:
        """
        Check if a memory has been in SHORT_TERM long enough for promotion.

        Args:
            created_at: When the memory was created.
            now: Current time (defaults to datetime.now()).

        Returns:
            True if the memory has met the minimum age requirement.
        """
        hours_in_short_term = elapsed_hours(created_at, now)
        return hours_in_short_term >= self._config.short_term_min_age_hours

    def calculate_hours_until_decay(
        self,
        current_score: float,
        last_accessed_at: datetime,
        now: datetime | None = None,
    ) -> float | None:
        """
        Estimate hours until the memory would decay below threshold.

        Useful for debugging and observability.

        Args:
            current_score: The current decay score.
            last_accessed_at: When the memory was last accessed.
            now: Current time (defaults to datetime.now()).

        Returns:
            Estimated hours until decay threshold, or None if already decayed.
        """
        if not self._config.enabled:
            return None

        now = now or datetime.now()

        # Calculate current effective score
        effective_score = self.calculate_decay(current_score, last_accessed_at, now)

        if effective_score <= self._config.decay_threshold:
            return None  # Already below threshold

        # Solve for t where: score * exp(-lambda * t) = threshold
        # t = -ln(threshold / score) / lambda
        try:
            hours = (
                -math.log(self._config.decay_threshold / effective_score)
                / self._config.decay_rate
            )
            return max(0.0, hours)
        except (ValueError, ZeroDivisionError):
            return None
