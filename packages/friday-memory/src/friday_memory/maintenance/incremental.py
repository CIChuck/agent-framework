"""
Incremental Graph Maintenance.

Lightweight, time-bounded maintenance triggered every N turns during
active sessions. Prevents graph clutter from accumulating by running
deduplication and cleanup incrementally.

Operations:
- Entity deduplication (merge near-duplicates)
- Orphan edge cleanup (remove dangling references)
- Hebbian consolidation (batch flush access events)

Ref: docs/build-plan/copilot-promotion-build-plan.md, Issue 4
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from friday_core import GraphStoreAdapter, TelemetryInterface

logger = logging.getLogger(__name__)


class IncrementalMaintenanceConfig(BaseModel):
    """Configuration for incremental graph maintenance."""

    enabled: bool = Field(
        default=True,
        description="Enable incremental maintenance",
    )
    interval: int = Field(
        default=5,
        ge=0,
        description="Run maintenance every N turns (0 = disabled)",
    )
    mode: str = Field(
        default="lightweight",
        description="Maintenance mode: 'lightweight' or 'full'",
    )
    max_duration_ms: int = Field(
        default=200,
        ge=50,
        le=5000,
        description="Maximum time budget per maintenance run (ms)",
    )

    # Entity deduplication settings
    dedup_enabled: bool = Field(
        default=True,
        description="Enable entity deduplication",
    )
    fuzzy_threshold: float = Field(
        default=0.85,
        ge=0.5,
        le=1.0,
        description="Similarity threshold for fuzzy entity matching",
    )
    max_entities_per_run: int = Field(
        default=50,
        ge=10,
        description="Maximum entities to check per run",
    )

    # Orphan edge cleanup settings
    orphan_cleanup_enabled: bool = Field(
        default=True,
        description="Enable orphan edge cleanup",
    )
    max_orphans_per_run: int = Field(
        default=20,
        ge=5,
        description="Maximum orphan edges to clean per run",
    )

    # Hebbian consolidation (full mode only)
    hebbian_batch_size: int = Field(
        default=100,
        ge=10,
        description="Batch size for Hebbian access flush",
    )


@dataclass
class MaintenanceResult:
    """Result of an incremental maintenance run."""

    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    duration_ms: float = 0.0

    # Entity deduplication
    entities_checked: int = 0
    entities_merged: int = 0
    merge_details: list[dict[str, Any]] = field(default_factory=list)

    # Orphan cleanup
    orphans_checked: int = 0
    orphans_removed: int = 0
    orphan_details: list[dict[str, Any]] = field(default_factory=list)

    # Hebbian consolidation
    accesses_flushed: int = 0

    # Errors
    errors: list[str] = field(default_factory=list)

    # Time budget
    time_budget_exhausted: bool = False

    def complete(self) -> None:
        """Mark maintenance as complete."""
        self.completed_at = datetime.now()
        self.duration_ms = (self.completed_at - self.started_at).total_seconds() * 1000


class IncrementalGraphMaintainer:
    """
    Lightweight, time-bounded graph maintenance.

    Runs every N turns via the MemoryController.add_turn() hook.
    Operations are time-bounded to avoid blocking the chat loop.

    Example:
        maintainer = IncrementalGraphMaintainer(graph_store)

        # Register with memory controller
        async def on_turn_complete(session_id: str, turn_count: int):
            if turn_count % maintainer.config.interval == 0:
                asyncio.create_task(maintainer.run_maintenance(session_id))

        controller.set_maintenance_callback(on_turn_complete)
    """

    def __init__(
        self,
        graph_store: GraphStoreAdapter,
        config: IncrementalMaintenanceConfig | None = None,
        telemetry: TelemetryInterface | None = None,
    ) -> None:
        """
        Initialize the incremental maintainer.

        Args:
            graph_store: GraphStoreAdapter for graph operations
            config: Maintenance configuration
            telemetry: Optional telemetry interface
        """
        self._graph = graph_store
        self._config = config or IncrementalMaintenanceConfig()
        self._telemetry = telemetry

        # Track maintenance runs per session
        self._run_counts: dict[str, int] = {}
        self._last_run: dict[str, datetime] = {}

        # Time budget tracking
        self._budget_start: float = 0.0
        self._budget_max_ms: float = 0.0

    @property
    def config(self) -> IncrementalMaintenanceConfig:
        """Access the maintenance configuration."""
        return self._config

    def _emit_event(self, event_name: str, data: dict[str, Any]) -> None:
        """Emit telemetry event if configured."""
        if self._telemetry:
            self._telemetry.capture_event(event_name, data)

    def _start_budget(self) -> None:
        """Start the time budget timer."""
        self._budget_start = time.time()
        self._budget_max_ms = self._config.max_duration_ms

    def _time_budget_exhausted(self) -> bool:
        """Check if time budget has been exhausted."""
        elapsed_ms = (time.time() - self._budget_start) * 1000
        return elapsed_ms >= self._budget_max_ms

    def _time_remaining_ms(self) -> float:
        """Get remaining time budget in milliseconds."""
        elapsed_ms = (time.time() - self._budget_start) * 1000
        return max(0, self._budget_max_ms - elapsed_ms)

    async def run_maintenance(self, session_id: str) -> MaintenanceResult:
        """
        Run incremental maintenance for a session.

        Non-blocking, time-bounded maintenance that:
        1. Deduplicates recently accessed entities
        2. Cleans up orphan edges
        3. (Full mode) Consolidates Hebbian accesses

        Args:
            session_id: The session triggering maintenance

        Returns:
            MaintenanceResult with statistics
        """
        result = MaintenanceResult()

        if not self._config.enabled:
            result.complete()
            return result

        self._emit_event(
            "incremental_maintenance_started",
            {
                "session_id": session_id,
                "mode": self._config.mode,
            },
        )

        self._start_budget()

        try:
            # Phase 1: Entity deduplication
            if self._config.dedup_enabled and not self._time_budget_exhausted():
                await self._dedupe_recent_entities(result)

            # Phase 2: Orphan edge cleanup
            if (
                self._config.orphan_cleanup_enabled
                and not self._time_budget_exhausted()
            ):
                await self._cleanup_orphan_edges(result)

            # Phase 3: Hebbian consolidation (full mode only)
            if self._config.mode == "full" and not self._time_budget_exhausted():
                await self._consolidate_hebbian(result)

            # Track run
            self._run_counts[session_id] = self._run_counts.get(session_id, 0) + 1
            self._last_run[session_id] = datetime.now()

        except Exception as e:
            result.errors.append(str(e))
            logger.warning(f"Incremental maintenance error: {e}")

        result.time_budget_exhausted = self._time_budget_exhausted()
        result.complete()

        self._emit_event(
            "incremental_maintenance_complete",
            {
                "session_id": session_id,
                "duration_ms": result.duration_ms,
                "entities_merged": result.entities_merged,
                "orphans_removed": result.orphans_removed,
                "accesses_flushed": result.accesses_flushed,
                "time_budget_exhausted": result.time_budget_exhausted,
                "errors": len(result.errors),
            },
        )

        return result

    async def _dedupe_recent_entities(self, result: MaintenanceResult) -> None:
        """
        Deduplicate recently accessed entities.

        Finds entities with similar labels and merges them,
        keeping the one with higher hit_count.

        Args:
            result: MaintenanceResult to update
        """
        try:
            # Get recently accessed entities (most likely to have fresh duplicates)
            recent_entities = await self._graph.get_top_nodes(
                self._config.max_entities_per_run,
                sort_by="last_accessed",
            )

            if not recent_entities:
                return

            # Track entities we've already processed to avoid double-checking
            processed_ids: set[str] = set()
            merged_ids: set[str] = set()

            for entity in recent_entities:
                if self._time_budget_exhausted():
                    result.time_budget_exhausted = True
                    break

                if entity.id in processed_ids or entity.id in merged_ids:
                    continue

                result.entities_checked += 1
                processed_ids.add(entity.id)

                # Find similar entities using fuzzy search
                try:
                    matches = await self._graph.fuzzy_search(
                        entity.label,
                        threshold=self._config.fuzzy_threshold,
                    )
                except Exception as e:
                    # fuzzy_search may not be implemented
                    logger.debug(f"Fuzzy search not available: {e}")
                    continue

                # Filter to actual duplicates (different ID, similar label)
                duplicates = [
                    m for m in matches if m.id != entity.id and m.id not in merged_ids
                ]

                if not duplicates:
                    continue

                # Determine primary (highest hit_count)
                all_candidates = [entity] + duplicates
                primary = max(all_candidates, key=lambda n: n.hit_count)

                # Merge duplicates into primary
                for dup in duplicates:
                    if dup.id == primary.id:
                        continue

                    try:
                        await self._graph.merge_nodes(primary.id, dup.id)
                        merged_ids.add(dup.id)
                        result.entities_merged += 1
                        result.merge_details.append(
                            {
                                "primary_id": primary.id,
                                "merged_id": dup.id,
                                "primary_label": primary.label,
                                "merged_label": dup.label,
                            }
                        )

                        self._emit_event(
                            "incremental_entity_merged",
                            {
                                "primary_id": primary.id,
                                "secondary_id": dup.id,
                                "similarity": self._config.fuzzy_threshold,
                            },
                        )
                    except Exception as e:
                        result.errors.append(
                            f"Merge failed: {primary.id} <- {dup.id}: {e}"
                        )

        except Exception as e:
            result.errors.append(f"Dedup phase failed: {e}")

    async def _cleanup_orphan_edges(self, result: MaintenanceResult) -> None:
        """
        Remove edges pointing to non-existent nodes.

        Args:
            result: MaintenanceResult to update
        """
        try:
            # Get all edges
            all_edges = await self._graph.get_all_edges()
            if not all_edges:
                return

            # Get all node IDs for existence check
            all_nodes = await self._graph.get_all_nodes()
            node_ids = {n.id for n in all_nodes}

            # Check edges for orphans (bounded by config)
            orphans_found = 0
            for edge in all_edges[: self._config.max_orphans_per_run * 3]:
                if self._time_budget_exhausted():
                    result.time_budget_exhausted = True
                    break

                result.orphans_checked += 1

                # Check if source or target is missing
                source_missing = edge.source_id not in node_ids
                target_missing = edge.target_id not in node_ids

                if source_missing or target_missing:
                    orphans_found += 1

                    if orphans_found > self._config.max_orphans_per_run:
                        break

                    try:
                        await self._graph.remove_edge(edge.source_id, edge.target_id)
                        result.orphans_removed += 1
                        result.orphan_details.append(
                            {
                                "source_id": edge.source_id,
                                "target_id": edge.target_id,
                                "relation": edge.relation,
                                "source_missing": source_missing,
                                "target_missing": target_missing,
                            }
                        )

                        self._emit_event(
                            "incremental_orphan_removed",
                            {
                                "source_id": edge.source_id,
                                "target_id": edge.target_id,
                                "relation": edge.relation,
                            },
                        )
                    except Exception as e:
                        result.errors.append(
                            f"Orphan removal failed: {edge.source_id}->{edge.target_id}: {e}"  # noqa: E501
                        )

        except Exception as e:
            result.errors.append(f"Orphan cleanup phase failed: {e}")

    async def _consolidate_hebbian(self, result: MaintenanceResult) -> None:
        """
        Batch flush pending Hebbian access events.

        Only runs in 'full' mode. Flushes accumulated access events
        to update hit_counts in a single batch operation.

        Args:
            result: MaintenanceResult to update
        """
        # This is a placeholder - actual implementation depends on
        # whether the graph store has an access buffer to flush.
        # The current ElementXGraphStore handles this directly.
        try:
            # If the graph store has a flush method, call it
            if hasattr(self._graph, "flush_access_buffer"):
                flushed = await self._graph.flush_access_buffer()
                result.accesses_flushed = flushed
        except Exception as e:
            result.errors.append(f"Hebbian consolidation failed: {e}")

    def get_stats(self, session_id: str | None = None) -> dict[str, Any]:
        """
        Get maintenance statistics.

        Args:
            session_id: Specific session or None for all

        Returns:
            Dict with run counts and last run times
        """
        if session_id:
            return {
                "session_id": session_id,
                "run_count": self._run_counts.get(session_id, 0),
                "last_run": self._last_run.get(session_id),
            }
        return {
            "total_runs": sum(self._run_counts.values()),
            "sessions": list(self._run_counts.keys()),
            "run_counts": dict(self._run_counts),
        }

    def should_run(self, turn_count: int) -> bool:
        """
        Check if maintenance should run at this turn count.

        Args:
            turn_count: Current turn number

        Returns:
            True if maintenance should run
        """
        if not self._config.enabled:
            return False
        if self._config.interval <= 0:
            return False
        return turn_count > 0 and turn_count % self._config.interval == 0
