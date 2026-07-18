"""Supervised background task management for FridayV2."""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from dataclasses import dataclass
from typing import Any, TypeVar

from friday_chat.runtime import FridayRuntime

T = TypeVar("T")


class BackgroundTaskManager:
    """Track and close FridayV2 background tasks."""

    def __init__(self) -> None:
        self._closed = False
        self._tasks: set[asyncio.Task[Any]] = set()
        self.failures: list[BaseException] = []

    @property
    def closed(self) -> bool:
        """Return whether the manager has been closed."""
        return self._closed

    @property
    def pending_count(self) -> int:
        """Return the number of currently pending tasks."""
        return sum(1 for task in self._tasks if not task.done())

    def create_task(self, coroutine: Coroutine[Any, Any, T]) -> asyncio.Task[T]:
        """Create and track one supervised background task."""
        if self._closed:
            raise RuntimeError("Cannot create background task after close.")

        task = asyncio.create_task(coroutine)
        self._tasks.add(task)
        task.add_done_callback(self._record_completion)
        return task

    async def wait_for_all(self) -> None:
        """Await all currently tracked tasks without cancelling them."""
        pending = [task for task in self._tasks if not task.done()]
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)

    async def close(self) -> None:
        """Cancel and await all pending background tasks."""
        pending = [task for task in self._tasks if not task.done()]
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)
        self._tasks.clear()
        self._closed = True

    def _record_completion(self, task: asyncio.Task[Any]) -> None:
        self._tasks.discard(task)
        if task.cancelled():
            return
        exception = task.exception()
        if exception is not None:
            self.failures.append(exception)


@dataclass
class BackgroundWorkCoordinator:
    """Route FridayV2 background work through the supervised manager."""

    runtime: FridayRuntime
    manager: BackgroundTaskManager

    def schedule_after_turn(
        self,
        *,
        turn_count: int,
        user_message: str,
        assistant_message: str,
        budget_status: Any | None = None,
    ) -> None:
        """Schedule background work due after a persisted turn."""
        self.runtime.maintenance.pending_extraction.append(
            (user_message, assistant_message)
        )
        if self._should_extract(turn_count):
            self.manager.create_task(
                self.runtime.maintenance.extract_buffered_turns(
                    trigger_reason="background_interval"
                )
            )

        if self.runtime.config.tools.enabled:
            self.manager.create_task(self.runtime.maintenance.run_tool_decay())

        if self.runtime.config.lifecycle.factor_computer.get("enabled") is True:
            self.manager.create_task(
                self.runtime.maintenance.run_incremental_graph_maintenance()
            )

        self._schedule_budget_compaction(budget_status)

    async def wait_for_inflight_compaction(self) -> None:
        """Await any compaction task before processing the next chat prompt."""
        task = self.runtime.compaction_task
        if task is not None and not task.done():
            await task

    def _should_extract(self, turn_count: int) -> bool:
        interval = self.runtime.config.extraction.interval
        if interval == -1:
            return False
        if interval == 0:
            return True
        return interval > 0 and turn_count % interval == 0

    def _schedule_budget_compaction(self, budget_status: Any | None) -> None:
        monitor = self.runtime.budget_monitor
        if monitor is None or self.runtime.compactor is None or budget_status is None:
            return
        monitor.record_turn(budget_status)
        if not monitor.should_compact():
            return
        monitor.mark_compaction_started()
        self.runtime.compaction_task = self.manager.create_task(
            self._run_budget_compaction()
        )

    async def _run_budget_compaction(self) -> None:
        monitor = self.runtime.budget_monitor
        if monitor is None:
            return
        try:
            await self.runtime.maintenance.flush_pending_extraction()
            budget_context = monitor.get_budget_context()
            await self.runtime.maintenance.compact(
                trigger_reason="budget_threshold_exceeded",
                time_budget_ms=monitor.get_time_budget_ms(),
                current_tokens=int(budget_context["current_tokens"]),
                available_budget=int(budget_context["available_budget"]),
                target_utilization=float(budget_context["target_utilization"]),
            )
        finally:
            monitor.mark_compaction_complete()
            self.runtime.compaction_task = None
