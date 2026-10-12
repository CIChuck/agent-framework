"""Supervised background task management for FridayV2."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any, TypeVar
from uuid import uuid4

from friday_telemetry import ExecutionContext

from friday_chat.reorganization.gate import (
    MaintenanceAdmissionError,
    MaintenanceAdmissionGate,
)
from friday_chat.runtime import FridayRuntime, PendingExtractionTurn
from friday_chat.turns.telemetry import detached_scope

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
        await self.cancel_pending()
        self._closed = True

    async def cancel_pending(self) -> None:
        """Cancel and drain pending work without closing future admission."""
        pending = [task for task in self._tasks if not task.done()]
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)
        self._tasks.clear()

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
    gate: MaintenanceAdmissionGate = field(
        default_factory=MaintenanceAdmissionGate
    )
    _extraction_tasks: set[asyncio.Task[None]] = field(
        default_factory=set,
        init=False,
        repr=False,
    )

    def schedule_after_turn(
        self,
        *,
        turn_count: int,
        user_message: str,
        assistant_message: str,
        budget_status: Any | None = None,
        correlation_context: ExecutionContext | None = None,
    ) -> None:
        """Schedule background work due after a persisted turn."""
        self.runtime.maintenance.pending_extraction.append(
            PendingExtractionTurn(
                turn_id=str(uuid4()),
                user_message=user_message,
                assistant_message=assistant_message,
                correlation_context=correlation_context,
            )
        )
        if self._should_extract(turn_count):
            self._schedule_extraction(trigger_reason="background_interval")

        if self.runtime.config.tools.enabled:
            self.manager.create_task(
                self._run_shared(
                    "background-tool-decay",
                    self.runtime.maintenance.run_tool_decay,
                )
            )

        if self.runtime.config.lifecycle.factor_computer.get("enabled") is True:
            self.manager.create_task(
                self._run_shared(
                    "background-graph-maintenance",
                    self.runtime.maintenance.run_incremental_graph_maintenance,
                )
            )

        self._schedule_budget_compaction(budget_status)

    async def wait_for_inflight_compaction(self) -> None:
        """Await any compaction task before processing the next chat prompt."""
        task = self.runtime.compaction_task
        if task is not None and not task.done():
            await task

    async def preempt_extraction_for_foreground_turn(self) -> bool:
        """Cancel in-flight extraction before foreground inference begins."""
        pending = [task for task in self._extraction_tasks if not task.done()]
        cancellation_requested = False
        for task in pending:
            cancellation_requested = task.cancel() or cancellation_requested
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)
        return cancellation_requested

    @property
    def extraction_running(self) -> bool:
        """Return whether an extraction task is active or awaiting admission."""
        return any(not task.done() for task in self._extraction_tasks)

    def resume_preempted_extraction(
        self,
        *,
        trigger_reason: str = "foreground_resume",
    ) -> bool:
        """Resume deferred extraction after foreground inference completes."""
        if not self.runtime.maintenance.pending_extraction:
            return False
        if self.extraction_running:
            return False
        self._schedule_extraction(trigger_reason=trigger_reason)
        return True

    def _should_extract(self, turn_count: int) -> bool:
        interval = self.runtime.config.extraction.interval
        if interval == -1:
            return False
        if interval == 0:
            return True
        return interval > 0 and turn_count % interval == 0

    def _schedule_extraction(self, *, trigger_reason: str) -> None:
        task = self.manager.create_task(
            self._run_shared(
                "background-extraction",
                lambda: self.runtime.maintenance.extract_buffered_turns(
                    trigger_reason=trigger_reason,
                ),
            )
        )
        self._extraction_tasks.add(task)
        task.add_done_callback(self._extraction_tasks.discard)

    def _schedule_budget_compaction(self, budget_status: Any | None) -> None:
        monitor = self.runtime.budget_monitor
        if monitor is None or self.runtime.compactor is None or budget_status is None:
            return
        monitor.record_turn(budget_status)
        if not monitor.should_compact():
            return
        monitor.mark_compaction_started()
        self.runtime.compaction_task = self.manager.create_task(
            self._run_shared(
                "background-compaction",
                self._run_budget_compaction,
            )
        )

    async def _run_shared(
        self,
        operation_name: str,
        operation_factory: Callable[[], Coroutine[Any, Any, object]],
    ) -> None:
        try:
            with detached_scope(self.runtime.telemetry):
                async with self.gate.shared(operation_name):
                    await operation_factory()
        except MaintenanceAdmissionError:
            return

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
