# mypy: ignore-errors
"""
Retrieval Factor Computer.

Pre-computes retrieval factors for long-term memories during reorganization,
enabling fast O(1) multiplication at retrieval time instead of expensive
exponential calculations.

The retrieval_factor is stored in memory metadata and used for fast
inclusion scoring: inclusion_score = similarity * retrieval_factor

Ref: docs/archive/build-plans/completed/friday-core-legacy/memory-lifecycle-staging-decay.md - Optimization A
"""

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from friday_memory.temporal import elapsed_hours

if TYPE_CHECKING:
    from friday_memory.retrieval.collection_manager import ManagedCollection

logger = logging.getLogger(__name__)


class FactorComputerConfig(BaseModel):
    """Configuration for RetrievalFactorComputer."""

    decay_rate: float = Field(
        default=0.005,
        ge=0.0001,
        le=0.1,
        description="Per-hour decay rate for time factor calculation",
    )
    usage_boost_factor: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Logarithmic boost factor for hit_count",
    )
    min_factor: float = Field(
        default=0.01,
        ge=0.0,
        le=1.0,
        description="Minimum retrieval factor (floor for very old memories)",
    )


@dataclass
class FactorComputeResult:
    """Result from computing retrieval factors."""

    updated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def summary(self) -> str:
        parts = [f"updated={self.updated}"]
        if self.skipped > 0:
            parts.append(f"skipped={self.skipped}")
        if self.errors:
            parts.append(f"errors={len(self.errors)}")
        return ", ".join(parts)


class RetrievalFactorComputer:
    """
    Pre-compute retrieval factors for long-term memories.

    The retrieval factor combines time-based decay and usage-based boost
    into a single pre-computed value:

        retrieval_factor = time_factor * usage_factor

    Where:
        - time_factor = exp(-decay_rate * age_hours)
        - usage_factor = 1.0 + (usage_boost * log(1 + hit_count))

    At retrieval time, inclusion scoring becomes a simple multiplication:

        inclusion_score = similarity * retrieval_factor

    This saves ~4ms per query by eliminating exponential calculations.

    Example usage:
        computer = RetrievalFactorComputer()

        # During reorganization, update all long-term memories:
        result = await computer.compute_factors(long_term_collection)
        print(f"Updated {result.updated} memories")

        # At retrieval time, use pre-computed factor:
        score = similarity * metadata.get("retrieval_factor", 0.5)
    """

    def __init__(self, config: FactorComputerConfig | None = None) -> None:
        """
        Initialize the factor computer.

        Args:
            config: Computer configuration (uses defaults if None)
        """
        self._config = config or FactorComputerConfig()

    @property
    def config(self) -> FactorComputerConfig:
        return self._config

    def compute_time_factor(
        self,
        created_at: datetime,
        now: datetime | None = None,
    ) -> float:
        """
        Calculate time-based decay factor.

        Uses exponential decay: factor = exp(-decay_rate * hours)

        Args:
            created_at: When the memory was created.
            now: Current time (defaults to now).

        Returns:
            Decay factor between min_factor and 1.0.
        """
        age_hours = elapsed_hours(created_at, now)
        age_hours = max(0, age_hours)

        factor = math.exp(-self._config.decay_rate * age_hours)
        return max(self._config.min_factor, factor)

    def compute_usage_factor(self, hit_count: int) -> float:
        """
        Calculate usage-based boost factor.

        Uses logarithmic scaling (diminishing returns).

        Args:
            hit_count: Number of times memory was accessed.

        Returns:
            Boost factor >= 1.0.
        """
        return 1.0 + (self._config.usage_boost_factor * math.log(1 + max(0, hit_count)))

    def compute_retrieval_factor(
        self,
        created_at: datetime,
        hit_count: int,
        now: datetime | None = None,
    ) -> float:
        """
        Compute the combined retrieval factor.

        retrieval_factor = time_factor * usage_factor

        Args:
            created_at: When the memory was created.
            hit_count: Number of times memory was accessed.
            now: Current time (defaults to now).

        Returns:
            Combined factor for fast inclusion scoring.
        """
        time_factor = self.compute_time_factor(created_at, now)
        usage_factor = self.compute_usage_factor(hit_count)
        return time_factor * usage_factor

    async def compute_factors(
        self,
        collection: "ManagedCollection",
        now: datetime | None = None,
        force_update: bool = False,
    ) -> FactorComputeResult:
        """
        Update retrieval_factor for all memories in a collection.

        Called during reorganization to pre-compute factors.

        Args:
            collection: The collection to process.
            now: Current time (defaults to now).
            force_update: If True, update even if recently computed.

        Returns:
            Result with counts of updated/skipped memories.
        """
        now = now or datetime.now()
        result = FactorComputeResult()

        try:
            # Get all documents from collection
            all_docs = await collection.get_all(limit=100000)

            for doc in all_docs:
                memory_id = doc.get("id")
                metadata = doc.get("metadata", {})

                if not memory_id:
                    continue

                # Skip if recently computed (within last hour) unless forced
                if not force_update:
                    last_computed = metadata.get("factor_computed_at")
                    if last_computed:
                        try:
                            computed_at = datetime.fromisoformat(last_computed)
                            age_hours = elapsed_hours(computed_at, now)
                            if age_hours < 1.0:
                                result.skipped += 1
                                continue
                        except (ValueError, TypeError):
                            pass  # Compute if parse fails

                # Parse created_at
                created_at_str = metadata.get("created_at")
                if created_at_str:
                    try:
                        created_at = datetime.fromisoformat(created_at_str)
                    except (ValueError, TypeError):
                        created_at = now
                else:
                    created_at = now

                hit_count = int(metadata.get("hit_count", 0))

                # Compute retrieval factor
                retrieval_factor = self.compute_retrieval_factor(
                    created_at=created_at,
                    hit_count=hit_count,
                    now=now,
                )

                try:
                    await collection.update_metadata(
                        memory_id,
                        {
                            "retrieval_factor": retrieval_factor,
                            "factor_computed_at": now.isoformat(),
                        },
                    )
                    result.updated += 1
                except Exception as e:
                    result.errors.append(f"Failed to update {memory_id}: {e}")

        except Exception as e:
            result.errors.append(f"Failed to process collection: {e}")
            logger.exception("Error computing retrieval factors")

        if result.updated > 0:
            logger.info(f"Computed retrieval factors: {result.summary()}")

        return result


def calculate_inclusion_score_fast(similarity: float, metadata: dict) -> float:
    """
    Fast inclusion scoring using pre-computed retrieval_factor.

    Use this at retrieval time instead of full calculation.

    Args:
        similarity: Semantic similarity from vector search (0.0-1.0).
        metadata: Memory metadata containing retrieval_factor.

    Returns:
        Inclusion score.
    """
    retrieval_factor = metadata.get("retrieval_factor", 0.5)
    return similarity * retrieval_factor
