"""Fair in-process admission gate for conflicting Friday Chat work."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass


class MaintenanceAdmissionError(RuntimeError):
    """Raised when maintenance admission would violate gate invariants."""


@dataclass(frozen=True)
class MaintenanceGateSnapshot:
    """Content-safe observable state for diagnostics and tests."""

    active_shared: int
    exclusive_active: bool
    exclusive_waiters: int
    accepting_shared: bool


class MaintenanceAdmissionGate:
    """Drain shared writers before one exclusive maintenance operation."""

    def __init__(self) -> None:
        self._condition = asyncio.Condition()
        self._shared_by_task: dict[asyncio.Task[object], int] = {}
        self._active_shared = 0
        self._exclusive_owner: asyncio.Task[object] | None = None
        self._exclusive_depth = 0
        self._exclusive_waiters = 0
        self._shared_admission_closed = False

    @property
    def snapshot(self) -> MaintenanceGateSnapshot:
        """Return current admission state without exposing task identities."""
        return MaintenanceGateSnapshot(
            active_shared=self._active_shared,
            exclusive_active=self._exclusive_owner is not None,
            exclusive_waiters=self._exclusive_waiters,
            accepting_shared=(
                not self._shared_admission_closed
                and self._exclusive_owner is None
                and self._exclusive_waiters == 0
            ),
        )

    async def close_shared_admission(self) -> None:
        """Reject future external shared work during shutdown."""
        async with self._condition:
            self._shared_admission_closed = True
            self._condition.notify_all()

    @asynccontextmanager
    async def shared(self, operation: str) -> AsyncIterator[None]:
        """Admit one conflicting writer unless exclusive work is pending."""
        del operation
        task = self._current_task()
        if task is self._exclusive_owner:
            yield
            return

        async with self._condition:
            existing_depth = self._shared_by_task.get(task, 0)
            if existing_depth > 0:
                self._shared_by_task[task] = existing_depth + 1
            else:
                if self._shared_admission_closed:
                    raise MaintenanceAdmissionError(
                        "maintenance admission is closed"
                    )
                await self._condition.wait_for(
                    lambda: self._shared_admission_closed
                    or (
                        self._exclusive_owner is None
                        and self._exclusive_waiters == 0
                    )
                )
                if self._shared_admission_closed:
                    raise MaintenanceAdmissionError(
                        "maintenance admission is closed"
                    )
                self._shared_by_task[task] = 1
                self._active_shared += 1
        try:
            yield
        finally:
            async with self._condition:
                depth = self._shared_by_task.get(task)
                if depth is None:
                    raise MaintenanceAdmissionError(
                        "shared maintenance admission ownership was lost"
                    )
                if depth == 1:
                    del self._shared_by_task[task]
                    self._active_shared -= 1
                    self._condition.notify_all()
                else:
                    self._shared_by_task[task] = depth - 1

    @asynccontextmanager
    async def exclusive(self, operation: str) -> AsyncIterator[None]:
        """Close new shared admission and wait for active writers to drain."""
        del operation
        task = self._current_task()
        if task is self._exclusive_owner:
            self._exclusive_depth += 1
            try:
                yield
            finally:
                self._exclusive_depth -= 1
            return
        if task in self._shared_by_task:
            raise MaintenanceAdmissionError(
                "shared admission cannot be upgraded to exclusive"
            )

        async with self._condition:
            self._exclusive_waiters += 1
            try:
                await self._condition.wait_for(
                    lambda: self._exclusive_owner is None
                    and self._active_shared == 0
                )
                self._exclusive_owner = task
                self._exclusive_depth = 1
            finally:
                self._exclusive_waiters -= 1
                self._condition.notify_all()
        try:
            yield
        finally:
            async with self._condition:
                if self._exclusive_owner is not task or self._exclusive_depth != 1:
                    raise MaintenanceAdmissionError(
                        "exclusive maintenance admission ownership was lost"
                    )
                self._exclusive_owner = None
                self._exclusive_depth = 0
                self._condition.notify_all()

    @staticmethod
    def _current_task() -> asyncio.Task[object]:
        task = asyncio.current_task()
        if task is None:
            raise MaintenanceAdmissionError(
                "maintenance admission requires an asyncio task"
            )
        return task


__all__ = [
    "MaintenanceAdmissionError",
    "MaintenanceAdmissionGate",
    "MaintenanceGateSnapshot",
]
