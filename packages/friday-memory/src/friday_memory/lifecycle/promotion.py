# mypy: ignore-errors
"""
Promotion Scoring and Memory Promotion Service.

Implements the promotion logic for SHORT_TERM → LONG_TERM transitions
and the full lifecycle management service.

Ref: docs/build-plan/memory-lifecycle-staging-decay.md, Section "PromotionScorer" and "MemoryPromotionService"
"""  # noqa: E501

from __future__ import annotations

import contextlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from friday_memory.lifecycle.decay import DecayCalculator, DecayConfig
from friday_memory.lifecycle.stages import MemoryStage

if TYPE_CHECKING:
    from friday_memory.retrieval.collection_manager import CollectionManager

logger = logging.getLogger(__name__)


class PromotionScorer:
    """
    Calculates promotion scores for SHORT_TERM → LONG_TERM transitions.

    The promotion score is a weighted combination of four factors:
    - Age: Time spent in short-term (older survivors are valuable)
    - Access: Number of times accessed (frequently used = important)
    - Confidence: Extraction confidence score (high confidence = reliable)
    - Connection: Number of graph relationships (well-connected = valuable)

    Example:
        scorer = PromotionScorer(config)
        score = scorer.calculate_promotion_score(
            created_at=memory_created_at,
            access_count=5,
            confidence=0.85,
            relationship_count=3,
        )
        if score >= config.promotion_threshold:
            promote_memory(memory_id)
    """

    def __init__(self, config: DecayConfig) -> None:
        """
        Initialize the promotion scorer.

        Args:
            config: DecayConfig with promotion weights and thresholds.
        """
        self._config = config
        self._weights = config.get_promotion_weights()

    @property
    def config(self) -> DecayConfig:
        """Get the decay configuration."""
        return self._config

    def calculate_promotion_score(
        self,
        created_at: datetime,
        access_count: int,
        confidence: float,
        relationship_count: int,
        now: datetime | None = None,
    ) -> float:
        """
        Calculate promotion score for a memory in SHORT_TERM.

        The score is a weighted sum of normalized factors:
        - age: min(1.0, hours_in_short_term / 72) - maxes at 3 days
        - access: min(1.0, access_count / 5) - maxes at 5 accesses
        - confidence: raw confidence score (0.0-1.0)
        - connection: min(1.0, relationship_count / 3) - maxes at 3 connections

        Args:
            created_at: When memory was created
            access_count: Number of times accessed
            confidence: Extraction confidence score (0.0-1.0)
            relationship_count: Number of graph relationships
            now: Current time (defaults to now)

        Returns:
            Promotion score (0.0-1.0)
        """
        now = now or datetime.now()
        hours_in_short_term = (now - created_at).total_seconds() / 3600

        # Calculate normalized factors
        factors = {
            "age": min(1.0, hours_in_short_term / 72),  # Max at 3 days
            "access": min(1.0, access_count / 5),  # Max at 5 accesses
            "confidence": max(0.0, min(1.0, confidence)),  # Clamp to valid range
            "connection": min(1.0, relationship_count / 3),  # Max at 3 connections
        }

        # Weighted sum
        score = sum(factors[k] * self._weights[k] for k in factors)

        return score

    def is_eligible_for_promotion(
        self,
        stage: MemoryStage,
        created_at: datetime,
        now: datetime | None = None,
    ) -> bool:
        """
        Check if memory is eligible for promotion consideration.

        A memory is eligible if:
        1. It's in SHORT_TERM stage
        2. It has been in SHORT_TERM for at least `short_term_min_age_hours`

        Args:
            stage: Current memory stage
            created_at: When memory was created
            now: Current time (defaults to now)

        Returns:
            True if eligible for promotion evaluation
        """
        if stage != MemoryStage.SHORT_TERM:
            return False

        now = now or datetime.now()
        hours_in_short_term = (now - created_at).total_seconds() / 3600

        return hours_in_short_term >= self._config.short_term_min_age_hours

    def should_promote(self, score: float) -> bool:
        """
        Check if a promotion score meets the threshold.

        Args:
            score: Calculated promotion score

        Returns:
            True if score meets or exceeds promotion threshold
        """
        return score >= self._config.promotion_threshold

    def get_factor_breakdown(
        self,
        created_at: datetime,
        access_count: int,
        confidence: float,
        relationship_count: int,
        now: datetime | None = None,
    ) -> dict[str, dict[str, float]]:
        """
        Get detailed breakdown of promotion score factors.

        Useful for debugging and observability.

        Returns:
            Dict with 'factors', 'weights', 'contributions', and 'total'
        """
        now = now or datetime.now()
        hours_in_short_term = (now - created_at).total_seconds() / 3600

        factors = {
            "age": min(1.0, hours_in_short_term / 72),
            "access": min(1.0, access_count / 5),
            "confidence": max(0.0, min(1.0, confidence)),
            "connection": min(1.0, relationship_count / 3),
        }

        contributions = {k: factors[k] * self._weights[k] for k in factors}

        return {
            "factors": factors,
            "weights": self._weights,
            "contributions": contributions,
            "total": sum(contributions.values()),
        }


@dataclass
class PromotionResult:
    """Result of a promotion/decay cycle."""

    promoted_to_long_term: int = 0
    decayed_from_long_term: int = 0
    decayed_from_short_term: int = 0
    reactivated: int = 0
    graph_nodes_decayed: int = 0
    errors: list[str] = field(default_factory=list)

    def has_errors(self) -> bool:
        """Check if any errors occurred."""
        return len(self.errors) > 0

    def summary(self) -> str:
        """Get a summary string of the results."""
        parts = []
        if self.promoted_to_long_term > 0:
            parts.append(f"promoted={self.promoted_to_long_term}")
        if self.decayed_from_long_term > 0:
            parts.append(f"decayed_lt={self.decayed_from_long_term}")
        if self.decayed_from_short_term > 0:
            parts.append(f"decayed_st={self.decayed_from_short_term}")
        if self.reactivated > 0:
            parts.append(f"reactivated={self.reactivated}")
        if self.graph_nodes_decayed > 0:
            parts.append(f"graph_decayed={self.graph_nodes_decayed}")
        if self.errors:
            parts.append(f"errors={len(self.errors)}")

        if not parts:
            return "No changes"
        return ", ".join(parts)


class MemoryPromotionService:
    """
    Manages memory lifecycle transitions.

    Responsibilities:
    - Promote SHORT_TERM → LONG_TERM based on promotion score
    - Decay LONG_TERM → DECAYED based on decay score
    - Propagate decay to linked graph nodes
    - Reactivate DECAYED → LONG_TERM on access

    This service is designed to be run periodically (e.g., during reorganization)
    rather than on every memory access.

    Example:
        service = MemoryPromotionService(
            config=DecayConfig(),
            collection_manager=manager,
            graph_store=graph,
        )

        # Dry run to see what would change
        result = await service.run_promotion_cycle(dry_run=True)
        print(f"Would promote: {result.promoted_to_long_term}")

        # Execute changes
        result = await service.run_promotion_cycle(dry_run=False)
    """

    def __init__(
        self,
        config: DecayConfig,
        collection_manager: CollectionManager,
        graph_store: Any | None = None,
    ) -> None:
        """
        Initialize the memory promotion service.

        Args:
            config: DecayConfig with thresholds and weights
            collection_manager: CollectionManager for multi-collection operations
            graph_store: Optional graph store for node decay propagation
        """
        self._config = config
        self._collection_manager = collection_manager
        self._graph_store = graph_store
        self._decay_calculator = DecayCalculator(config)
        self._promotion_scorer = PromotionScorer(config)

    @property
    def config(self) -> DecayConfig:
        """Get the decay configuration."""
        return self._config

    @property
    def collection_manager(self) -> CollectionManager:
        """Get the collection manager."""
        return self._collection_manager

    @property
    def decay_calculator(self) -> DecayCalculator:
        """Get the decay calculator."""
        return self._decay_calculator

    @property
    def promotion_scorer(self) -> PromotionScorer:
        """Get the promotion scorer."""
        return self._promotion_scorer

    async def run_promotion_cycle(
        self,
        dry_run: bool = True,
        now: datetime | None = None,
    ) -> PromotionResult:
        """
        Run a full promotion/decay cycle.

        Steps:
        1. Apply decay to all LONG_TERM memories and demote if below threshold
        2. Check SHORT_TERM memories for promotion eligibility
        3. Propagate decay to linked graph nodes

        Args:
            dry_run: If True, don't make any changes (just count)
            now: Current time (defaults to now)

        Returns:
            PromotionResult with counts and any errors
        """
        result = PromotionResult()
        now = now or datetime.now()

        # Step 1: Decay and demote LONG_TERM memories
        try:
            await self._process_long_term_decay(result, dry_run, now)
        except Exception as e:
            logger.error(f"Long-term decay processing failed: {e}")
            result.errors.append(f"Long-term decay failed: {e}")

        # Step 2: Promote eligible SHORT_TERM memories
        try:
            await self._process_short_term_promotion(result, dry_run, now)
        except Exception as e:
            logger.error(f"Short-term promotion processing failed: {e}")
            result.errors.append(f"Short-term promotion failed: {e}")

        # Step 3: Propagate decay to graph nodes
        if self._graph_store is not None and result.decayed_from_long_term > 0:
            try:
                await self._propagate_decay_to_graph(result, dry_run)
            except Exception as e:
                logger.error(f"Graph decay propagation failed: {e}")
                result.errors.append(f"Graph decay propagation failed: {e}")

        return result

    async def _process_long_term_decay(
        self,
        result: PromotionResult,
        dry_run: bool,
        now: datetime,
    ) -> None:
        """Apply decay to long-term memories and demote if below threshold."""
        # Get all long-term memories
        long_term_docs = await self._collection_manager.long_term.get_all(limit=10000)

        for doc in long_term_docs:
            doc_id = doc.get("id")
            metadata = doc.get("metadata", {})

            # Skip protected memories (e.g., explicitly ingested documents)
            if metadata.get("protected", False):
                logger.debug(f"Skipping decay for protected memory {doc_id}")
                continue

            # Parse timestamps
            last_accessed_str = metadata.get("last_accessed_at")
            if last_accessed_str:
                try:
                    last_accessed = datetime.fromisoformat(last_accessed_str)
                except (ValueError, TypeError):
                    last_accessed = now
            else:
                last_accessed = now

            # Get current decay score
            current_score = float(metadata.get("decay_score", 1.0))

            # Calculate new decay score
            new_score = self._decay_calculator.calculate_decay(
                current_score, last_accessed, now
            )

            # Check if should decay
            if self._decay_calculator.should_decay(new_score):
                result.decayed_from_long_term += 1
                if not dry_run:
                    try:
                        await self._collection_manager.demote_to_decayed(doc_id)
                        logger.info(
                            f"Demoted memory {doc_id} to DECAYED (score={new_score:.3f})"  # noqa: E501
                        )
                    except Exception as e:
                        result.errors.append(f"Failed to demote {doc_id}: {e}")
            elif not dry_run and new_score != current_score:
                # Update decay score
                try:
                    await self._collection_manager.long_term.update_metadata(
                        doc_id,
                        {
                            "decay_score": new_score,
                            "last_decay_at": now.isoformat(),
                        },
                    )
                except Exception as e:
                    result.errors.append(f"Failed to update decay for {doc_id}: {e}")

    async def _process_short_term_promotion(
        self,
        result: PromotionResult,
        dry_run: bool,
        now: datetime,
    ) -> None:
        """Check short-term memories for promotion eligibility."""
        # Get all short-term memories
        short_term_docs = await self._collection_manager.short_term.get_all(limit=10000)

        for doc in short_term_docs:
            doc_id = doc.get("id")
            metadata = doc.get("metadata", {})

            # Parse created_at
            created_at_str = metadata.get("created_at")
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str)
                except (ValueError, TypeError):
                    created_at = now
            else:
                created_at = now

            # Fast-track protected memories (e.g., explicitly ingested documents)
            # These bypass the normal age/access requirements
            is_protected = metadata.get("protected", False)
            if is_protected:
                result.promoted_to_long_term += 1
                if not dry_run:
                    try:
                        await self._collection_manager.promote_memory(doc_id)
                        logger.info(
                            f"Fast-track promoted protected memory {doc_id} to LONG_TERM"  # noqa: E501
                        )
                    except Exception as e:
                        result.errors.append(
                            f"Failed to promote protected {doc_id}: {e}"
                        )
                continue

            # Check eligibility (must be old enough)
            if not self._promotion_scorer.is_eligible_for_promotion(
                MemoryStage.SHORT_TERM, created_at, now
            ):
                continue

            # Get promotion factors
            access_count = int(metadata.get("access_count", 0))
            confidence = float(metadata.get("confidence", 0.5))

            # Count relationships (if graph store available)
            relationship_count = 0
            if self._graph_store is not None:
                with contextlib.suppress(Exception):
                    relationship_count = await self._count_relationships(doc_id)

            # Calculate promotion score
            score = self._promotion_scorer.calculate_promotion_score(
                created_at=created_at,
                access_count=access_count,
                confidence=confidence,
                relationship_count=relationship_count,
                now=now,
            )

            # Check if should promote
            if self._promotion_scorer.should_promote(score):
                result.promoted_to_long_term += 1
                if not dry_run:
                    try:
                        await self._collection_manager.promote_memory(doc_id)
                        logger.info(
                            f"Promoted memory {doc_id} to LONG_TERM (score={score:.3f})"
                        )
                    except Exception as e:
                        result.errors.append(f"Failed to promote {doc_id}: {e}")

    async def _count_relationships(self, memory_id: str) -> int:
        """Count graph relationships for a memory.

        Finds all graph nodes whose source_memory_ids include this
        memory, collects their IDs, then fetches all connected edges
        in a single batch call.

        Args:
            memory_id: The vector memory ID to count relationships for.

        Returns:
            Total number of edges connected to nodes sourced from
            this memory. Returns 0 if graph store is unavailable or
            on error.
        """
        if self._graph_store is None:
            return 0

        try:
            all_nodes = await self._graph_store.get_all_nodes()
            linked_node_ids: set[str] = set()
            for node in all_nodes:
                if (
                    hasattr(node, "source_memory_ids")
                    and memory_id in node.source_memory_ids
                ):
                    linked_node_ids.add(node.id)

            if not linked_node_ids:
                return 0

            edges = await self._graph_store.get_edges_for_nodes(
                linked_node_ids, direction="both"
            )
            return len(edges)
        except Exception as e:
            logger.warning(
                "Failed to count relationships for %s: %s",
                memory_id,
                e,
            )
            return 0

    async def _propagate_decay_to_graph(
        self,
        result: PromotionResult,
        dry_run: bool,
    ) -> None:
        """
        Propagate decay to graph nodes whose source memories have all decayed.

        A graph node decays if ALL of its source_memory_ids are in the DECAYED stage.
        """
        if self._graph_store is None:
            return

        # Get all decayed memory IDs
        decayed_docs = await self._collection_manager.decayed.get_all(limit=10000)
        decayed_ids = {doc.get("id") for doc in decayed_docs}

        # Check each graph node
        all_nodes = await self._graph_store.get_all_nodes()
        for node in all_nodes:
            if not hasattr(node, "source_memory_ids") or not node.source_memory_ids:
                continue

            # Check if all source memories are decayed
            if all(mid in decayed_ids for mid in node.source_memory_ids):  # noqa: SIM102
                if node.stage != MemoryStage.DECAYED:
                    result.graph_nodes_decayed += 1
                    if not dry_run:
                        try:
                            node.mark_decayed()
                            await self._graph_store.update_node(node)
                            logger.info(
                                f"Decayed graph node {node.id} (all sources decayed)"
                            )
                        except Exception as e:
                            result.errors.append(f"Failed to decay node {node.id}: {e}")

    async def on_memory_accessed(self, memory_id: str) -> bool:
        """
        Handle memory access event.

        Boosts decay score and potentially reactivates DECAYED memories.

        Args:
            memory_id: ID of the accessed memory

        Returns:
            True if memory was reactivated, False otherwise
        """
        # Check if memory is in decayed collection
        decayed_doc = await self._collection_manager.decayed.get_by_id(memory_id)
        if decayed_doc:
            # Reactivate from decayed
            success = await self._collection_manager.reactivate_from_decayed(memory_id)
            if success:
                logger.info(f"Reactivated memory {memory_id} from DECAYED to LONG_TERM")
            return success

        # Check long-term collection and boost decay score
        long_term_doc = await self._collection_manager.long_term.get_by_id(memory_id)
        if long_term_doc:
            metadata = long_term_doc.get("metadata", {})
            current_score = float(metadata.get("decay_score", 1.0))
            new_score = self._decay_calculator.apply_access_boost(current_score)
            access_count = int(metadata.get("access_count", 0)) + 1

            await self._collection_manager.long_term.update_metadata(
                memory_id,
                {
                    "decay_score": new_score,
                    "access_count": access_count,
                    "last_accessed_at": datetime.now().isoformat(),
                },
            )
            return False

        # Check short-term collection and boost access count
        short_term_doc = await self._collection_manager.short_term.get_by_id(memory_id)
        if short_term_doc:
            metadata = short_term_doc.get("metadata", {})
            access_count = int(metadata.get("access_count", 0)) + 1

            await self._collection_manager.short_term.update_metadata(
                memory_id,
                {
                    "access_count": access_count,
                    "last_accessed_at": datetime.now().isoformat(),
                },
            )
            return False

        return False
