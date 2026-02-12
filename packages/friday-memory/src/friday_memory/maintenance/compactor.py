"""
In-Session Memory Compactor.

Performs background compaction of memory data to reduce context size
for subsequent turns.  Designed to run as a fire-and-forget
``asyncio.create_task()`` without blocking the chat loop.

Operations (in priority order):

1. **Turn summarization** — compress older conversation turns into
   summaries, reusing the ``SUMMARIZATION_PROMPT`` from
   ``MemoryConsolidator``.
2. **Insight deduplication** — group insights by overlapping entity
   mentions and mark older duplicates as ``superseded_by`` the most
   recent version.
3. **Memory promotion** — promote frequently-accessed short-term
   memories to long-term so they occupy a stable, lower-priority
   retrieval slot.

All phases are time-bounded via the same ``_start_budget`` /
``_time_budget_exhausted`` pattern used by
``IncrementalGraphMaintainer``.

Ref: Proactive In-Session Context Budget Management
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import TYPE_CHECKING, Any

from friday_memory.context.token_estimator import (
    build_token_estimator,
)
from friday_memory.models.budget import (
    CompactionConfig,
    CompactionResult,
)

if TYPE_CHECKING:
    from friday_core import TelemetryInterface
    from friday_core.interfaces import LLMClient

    from friday_memory.controller import MemoryController
    from friday_memory.retrieval import CollectionManager

logger = logging.getLogger(__name__)


class InSessionCompactor:
    """Background compaction engine for in-session memory management.

    Runs time-bounded compaction operations to *persistently* reduce
    the volume of data that context assembly retrieves on subsequent
    turns.  Unlike ``_apply_budget()`` (which only trims the
    in-memory payload), ``InSessionCompactor`` writes back to the
    memory stores so that the reduction is durable.

    Example::

        compactor = InSessionCompactor(
            memory_controller=controller,
            collection_manager=cm,
            llm_client=llm,
        )

        # Fire-and-forget from process_turn()
        asyncio.create_task(
            compactor.run_compaction(
                session_id="sess_123",
                time_budget_ms=2000,
                trigger_reason="budget_warning",
            )
        )

    Args:
        memory_controller: MemoryController for episodic /
            vector access.
        collection_manager: CollectionManager for lifecycle
            collection operations.
        llm_client: LLMClient for summarization calls.
        config: Compaction configuration.
        telemetry: Optional telemetry interface.
        token_estimator_config: Token estimator settings.
        model_name: Model name for token estimation.
    """

    def __init__(
        self,
        memory_controller: MemoryController,
        collection_manager: CollectionManager,
        llm_client: LLMClient,
        config: CompactionConfig | None = None,
        telemetry: TelemetryInterface | None = None,
        token_estimator_config: dict[str, Any] | None = None,
        model_name: str = "gpt-4",
    ) -> None:
        """Initialize the in-session compactor.

        Args:
            memory_controller: MemoryController for episodic /
                vector access.
            collection_manager: CollectionManager for lifecycle
                collection operations.
            llm_client: LLMClient for summarization calls.
            config: Compaction configuration.
            telemetry: Optional telemetry interface.
            token_estimator_config: Token estimator settings.
            model_name: Model name for token estimation.
        """
        self._memory = memory_controller
        self._collection_manager = collection_manager
        self._llm_client = llm_client
        self._config = config or CompactionConfig()
        self._telemetry = telemetry
        self._token_estimator = build_token_estimator(
            token_estimator_config, model_name
        )

        # Time budget tracking
        self._budget_start: float = 0.0
        self._budget_max_ms: float = 0.0

    def _emit_event(
        self,
        event_name: str,
        data: dict[str, Any],
    ) -> None:
        """Emit telemetry event if configured.

        Args:
            event_name: The event name.
            data: Event data payload.
        """
        if self._telemetry:
            self._telemetry.capture_event(event_name, data)

    def _count_tokens(self, text: str) -> int:
        """Count tokens in a text string.

        Args:
            text: The text to count.

        Returns:
            Estimated token count.
        """
        return self._token_estimator.count(text)

    def _start_budget(self, max_ms: float) -> None:
        """Start the time budget timer.

        Args:
            max_ms: Maximum time budget in milliseconds.
        """
        self._budget_start = time.time()
        self._budget_max_ms = max_ms

    def _time_budget_exhausted(self) -> bool:
        """Check if time budget has been exhausted.

        Returns:
            True if elapsed time exceeds the budget.
        """
        elapsed_ms = (time.time() - self._budget_start) * 1000
        return elapsed_ms >= self._budget_max_ms

    async def run_compaction(
        self,
        session_id: str,
        time_budget_ms: int = 15000,
        trigger_reason: str = "threshold_exceeded",
        current_tokens: int = 0,
        available_budget: int = 0,
        target_utilization: float = 0.70,
    ) -> CompactionResult:
        """Run a goal-driven compaction cycle.

        Calculates how many tokens need to be freed to bring
        utilization down to ``target_utilization``, then runs
        compaction phases until the goal is met. Time budgets
        serve as safety nets, not primary stopping conditions.

        Phases (in priority order):

        1. Summarize old conversation turns (loops until goal
           met or no more unconsolidated turns).
        2. Deduplicate insights in vector store.
        3. Promote frequently-accessed short-term memories.

        Args:
            session_id: The session triggering compaction.
            time_budget_ms: Maximum time for this run (ms).
                Acts as a safety net; primary stop is goal.
            trigger_reason: Why compaction was triggered.
            current_tokens: Total tokens in the current prompt.
            available_budget: Max tokens minus output buffer.
            target_utilization: Desired post-compaction
                utilization level (0.0-1.0).

        Returns:
            CompactionResult with statistics and goal tracking.
        """
        result = CompactionResult(
            trigger_reason=trigger_reason,
        )
        self._start_budget(time_budget_ms)

        # Calculate goal: how many tokens to free
        target_tokens = int(
            available_budget * target_utilization
        )
        tokens_to_free = max(
            0, current_tokens - target_tokens
        )
        result.tokens_target = tokens_to_free

        logger.info(
            "Compaction goal for session %s: "
            "current=%d, target=%d (%.0f%% of %d), "
            "need_to_free=%d tokens",
            session_id,
            current_tokens,
            target_tokens,
            target_utilization * 100,
            available_budget,
            tokens_to_free,
        )

        self._emit_event(
            "compaction_started",
            {
                "session_id": session_id,
                "time_budget_ms": time_budget_ms,
                "trigger_reason": trigger_reason,
                "current_tokens": current_tokens,
                "target_tokens": target_tokens,
                "tokens_to_free": tokens_to_free,
                "target_utilization": target_utilization,
            },
        )

        try:
            # Phase 1: Turn summarization (highest priority)
            if not self._time_budget_exhausted():
                await self._summarize_old_turns(
                    session_id, result, tokens_to_free
                )

            # Phase 2: Insight deduplication
            if (
                self._config.insight_dedup_enabled
                and not self._time_budget_exhausted()
            ):
                await self._deduplicate_insights(result)

            # Phase 3: Memory promotion
            if not self._time_budget_exhausted():
                await self._promote_hot_memories(result)

        except Exception as e:
            result.errors.append(str(e))
            logger.error(
                "Compaction error for session %s: %s",
                session_id,
                e,
            )

        result.time_budget_exhausted = (
            self._time_budget_exhausted()
        )
        result.target_met = (
            result.tokens_saved_from_summarization
            >= tokens_to_free
        )
        result.complete()

        self._emit_event(
            "compaction_complete",
            {
                "session_id": session_id,
                "duration_ms": result.duration_ms,
                "turns_summarized": result.turns_summarized,
                "tokens_saved": (
                    result.tokens_saved_from_summarization
                ),
                "tokens_target": tokens_to_free,
                "target_met": result.target_met,
                "insights_deduplicated": (
                    result.insights_deduplicated
                ),
                "memories_promoted": result.memories_promoted,
                "time_budget_exhausted": (
                    result.time_budget_exhausted
                ),
                "errors": len(result.errors),
            },
        )

        logger.info(
            "Compaction complete for session %s: "
            "summarized=%d turns, deduped=%d insights, "
            "promoted=%d memories, saved=%d/%d tokens "
            "(target_met=%s, %.0fms, budget_exhausted=%s)",
            session_id,
            result.turns_summarized,
            result.insights_deduplicated,
            result.memories_promoted,
            result.tokens_saved_from_summarization,
            tokens_to_free,
            result.target_met,
            result.duration_ms,
            result.time_budget_exhausted,
        )

        return result

    async def _summarize_old_turns(
        self,
        session_id: str,
        result: CompactionResult,
        tokens_to_free: int = 0,
    ) -> None:
        """Summarize older conversation turns to reduce history.

        Fetches ALL non-compacted turns and compresses older ones
        into summaries via LLM, protecting the most recent turns
        (``compaction_recency_window``) for conversational
        continuity.  Reuses the ``SUMMARIZATION_PROMPT`` from
        ``MemoryConsolidator`` for consistency.

        Uses a **goal-driven loop**: continues summarizing
        batches until token savings meet the target, or there
        are no more compactable turns. The time budget acts
        as a safety net, not the primary stopping condition.

        After summarization, turns are marked ``compacted=True``
        so ``get_turns()`` excludes them from prompt assembly.

        Args:
            session_id: Session to summarize turns for.
            result: CompactionResult to update.
            tokens_to_free: Target number of tokens to free.
                The loop continues until savings meet this
                target, or materials are exhausted, or the
                time budget expires.
        """
        try:
            # Fetch ALL non-compacted turns (get_turns
            # already filters out compacted turns)
            all_turns = (
                await self._memory.episodic.get_turns(
                    session_id, limit=1000
                )
            )

            # Protect recent turns from compaction
            recency = (
                self._config.compaction_recency_window
            )
            if len(all_turns) <= recency:
                logger.debug(
                    "All %d turns within recency window "
                    "(%d), skipping summarization",
                    len(all_turns),
                    recency,
                )
                return

            # Turns eligible for compaction: everything
            # EXCEPT the most recent N
            compactable = all_turns[:-recency]

            if (
                len(compactable)
                < self._config.min_turns_to_summarize
            ):
                logger.debug(
                    "Not enough compactable turns: "
                    "%d < %d (total=%d, protected=%d)",
                    len(compactable),
                    self._config.min_turns_to_summarize,
                    len(all_turns),
                    recency,
                )
                return

            # Import here to avoid circular dependency
            from friday_memory.context.consolidator import (
                SUMMARIZATION_PROMPT,
            )
            from friday_memory.models import (
                ProvenanceMetadata,
                SummarizationResponse,
            )

            max_per = self._config.max_turns_per_summary
            for i in range(0, len(compactable), max_per):
                # Primary goal: stop when target is met
                if (
                    tokens_to_free > 0
                    and (
                        result.tokens_saved_from_summarization
                        >= tokens_to_free
                    )
                ):
                    logger.info(
                        "Token savings target met: "
                        "saved=%d >= target=%d",
                        result.tokens_saved_from_summarization,
                        tokens_to_free,
                    )
                    break

                # Safety net: stop if time budget exhausted
                if self._time_budget_exhausted():
                    result.time_budget_exhausted = True
                    logger.warning(
                        "Time budget exhausted during "
                        "summarization: saved=%d / "
                        "target=%d",
                        result.tokens_saved_from_summarization,
                        tokens_to_free,
                    )
                    break

                batch = compactable[i : i + max_per]
                if len(batch) < 2:
                    continue

                turns_text = self._format_turns(batch)
                original_tokens = self._count_tokens(
                    turns_text
                )

                response = (
                    await self._llm_client.chat_completion(
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are a precise "
                                    "conversation summarizer."
                                ),
                            },
                            {
                                "role": "user",
                                "content": (
                                    SUMMARIZATION_PROMPT
                                    .format(turns=turns_text)
                                ),
                            },
                        ],
                        response_model=SummarizationResponse,
                        temperature=0.0,
                    )
                )

                parsed = response._parsed_model
                if parsed is None:
                    logger.warning(
                        "Failed to parse summarization "
                        "response for batch %d",
                        i,
                    )
                    continue

                summary_tokens = self._count_tokens(
                    parsed.summary
                )

                provenance = ProvenanceMetadata(
                    source_id=session_id,
                    source_type="in_session_compaction",
                    confidence=0.85,
                    author_id="compactor",
                )

                await self._memory.store_insight(
                    f"[Session Summary] {parsed.summary}",
                    provenance,
                    {"type": "summary"},
                )

                # Mark turns as COMPACTED so get_turns()
                # excludes them from prompt assembly
                turn_ids = [t.id for t in batch]
                await self._memory.mark_turns_compacted(
                    turn_ids
                )

                result.turns_summarized += len(batch)
                result.tokens_saved_from_summarization += (
                    max(0, original_tokens - summary_tokens)
                )

                logger.info(
                    "Compacted %d turns (batch %d), "
                    "saved %d tokens "
                    "(cumulative: %d / %d target)",
                    len(batch),
                    i // max_per,
                    max(0, original_tokens - summary_tokens),
                    result.tokens_saved_from_summarization,
                    tokens_to_free,
                )

        except Exception as e:
            result.errors.append(
                f"Turn summarization failed: {e}"
            )
            logger.error(
                "Turn summarization failed: %s", e
            )

    def _format_turns(self, turns: list) -> str:
        """Format turns for the summarization prompt.

        Args:
            turns: List of InteractionTurn objects.

        Returns:
            Formatted text block for the LLM prompt.
        """
        formatted = []
        for i, turn in enumerate(turns, 1):
            user_msg = (
                getattr(turn, "user_message", "") or ""
            )
            assistant_msg = (
                getattr(turn, "assistant_response", "")
                or getattr(turn, "assistant_message", "")
                or ""
            )
            ts = getattr(turn, "timestamp", None)
            ts_str = ts.isoformat() if ts else "unknown"

            formatted.append(f"Turn {i} ({ts_str}):")
            if user_msg:
                formatted.append(
                    f"  User: {user_msg[:500]}"
                )
            if assistant_msg:
                formatted.append(
                    f"  Assistant: {assistant_msg[:500]}"
                )
            formatted.append("")

        return "\n".join(formatted)

    async def _deduplicate_insights(
        self,
        result: CompactionResult,
    ) -> None:
        """Find and mark duplicate/near-duplicate insights.

        Groups insights by overlapping ``entities_mentioned``
        metadata.  For groups with more than one member, keeps
        the most recent and marks older entries with a
        ``superseded_by`` metadata field.

        Args:
            result: CompactionResult to update.
        """
        try:
            insights = await self._collection_manager.get_all(
                limit=self._config.max_insights_to_check,
                where={"type": "insight"},
            )

            if len(insights) < 2:
                return

            # Group by entity mentions for dedup candidates
            entity_groups: dict[
                frozenset[str], list[dict[str, Any]]
            ] = defaultdict(list)

            for insight in insights:
                if self._time_budget_exhausted():
                    result.time_budget_exhausted = True
                    return

                meta = insight.get("metadata", {})
                entities_str = meta.get(
                    "entities_mentioned", ""
                )
                if entities_str:
                    entities = frozenset(
                        e.strip().lower()
                        for e in entities_str.split(";")
                        if e.strip()
                    )
                    if entities:
                        entity_groups[entities].append(
                            insight
                        )

            # For each group with duplicates, keep most recent
            for _entities, group in entity_groups.items():
                if len(group) < 2:
                    continue

                if self._time_budget_exhausted():
                    result.time_budget_exhausted = True
                    return

                # Sort by created_at desc (most recent first)
                group.sort(
                    key=lambda x: x.get(
                        "metadata", {}
                    ).get("created_at", ""),
                    reverse=True,
                )

                keeper = group[0]
                keeper_id = keeper.get("id", "")

                for duplicate in group[1:]:
                    dup_id = duplicate.get("id")
                    if not dup_id:
                        continue

                    try:
                        # Try short-term first, then long-term
                        updated = False
                        for store in (
                            self._collection_manager._short_term,
                            self._collection_manager._long_term,
                        ):
                            try:
                                await store.update_metadata(
                                    dup_id,
                                    {
                                        "superseded_by":
                                            keeper_id,
                                    },
                                )
                                updated = True
                                break
                            except Exception:
                                continue

                        if updated:
                            result.insights_deduplicated += 1
                        else:
                            result.errors.append(
                                f"Could not update "
                                f"metadata for {dup_id}"
                            )
                    except Exception as e:
                        result.errors.append(
                            f"Dedup failed for "
                            f"{dup_id}: {e}"
                        )

        except Exception as e:
            result.errors.append(
                f"Insight dedup failed: {e}"
            )
            logger.error(
                "Insight deduplication failed: %s", e
            )

    async def _promote_hot_memories(
        self,
        result: CompactionResult,
    ) -> None:
        """Promote frequently-accessed short-term memories.

        Memories with ``hit_count >= 3`` in the short-term
        collection are promoted to long-term via
        ``CollectionManager.promote_memory()``, reducing
        re-retrieval overhead on subsequent turns.

        Args:
            result: CompactionResult to update.
        """
        try:
            short_term_docs = (
                await self._collection_manager._short_term
                .get_all(limit=20)
            )

            for doc in short_term_docs:
                if self._time_budget_exhausted():
                    result.time_budget_exhausted = True
                    return

                meta = doc.get("metadata", {})
                hit_count = meta.get("hit_count", 0)

                # Promote memories accessed 3+ times
                if hit_count >= 3:
                    doc_id = doc.get("id")
                    if doc_id:
                        try:
                            promoted = (
                                await self._collection_manager
                                .promote_memory(doc_id)
                            )
                            if promoted:
                                result.memories_promoted += 1
                                logger.debug(
                                    "Promoted memory %s "
                                    "(hit_count=%d)",
                                    doc_id,
                                    hit_count,
                                )
                        except Exception as e:
                            result.errors.append(
                                f"Promotion failed for "
                                f"{doc_id}: {e}"
                            )

        except Exception as e:
            result.errors.append(
                f"Memory promotion failed: {e}"
            )
            logger.error(
                "Memory promotion failed: %s", e
            )
