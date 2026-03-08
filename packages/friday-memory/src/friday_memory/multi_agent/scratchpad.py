# mypy: ignore-errors
"""
Ephemeral scratch pad memory for workflow/task execution tracking.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ScratchPlanItemStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WAITING_APPROVAL = "waiting_approval"


class ScratchPlanItem(BaseModel):
    item_id: str
    task_id: str
    title: str
    status: ScratchPlanItemStatus
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class ScratchEvent(BaseModel):
    event_id: str
    event_type: str
    workflow_id: str
    execution_id: str
    task_id: str | None = None
    correlation_id: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ScratchPad(BaseModel):
    scope_id: str
    created_at: datetime
    expires_at: datetime
    plan_items: dict[str, ScratchPlanItem] = Field(default_factory=dict)
    events: list[ScratchEvent] = Field(default_factory=list)


class ScratchPadStore:
    """In-memory scratch pad store with TTL and quota controls."""

    def __init__(self, ttl_seconds: int = 86400, max_entries: int = 2000) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        if max_entries <= 0:
            raise ValueError("max_entries must be positive")
        self._ttl_seconds = ttl_seconds
        self._max_entries = max_entries
        self._pads: dict[str, ScratchPad] = {}

    def ensure_pad(self, scope_id: str) -> ScratchPad:
        now = datetime.now(timezone.utc)
        self.purge_expired(now=now)
        pad = self._pads.get(scope_id)
        if pad is not None:
            return pad
        pad = ScratchPad(
            scope_id=scope_id,
            created_at=now,
            expires_at=now + timedelta(seconds=self._ttl_seconds),
        )
        self._pads[scope_id] = pad
        return pad

    def upsert_plan_item(
        self,
        scope_id: str,
        task_id: str,
        title: str,
        status: ScratchPlanItemStatus,
        metadata: dict[str, Any] | None = None,
    ) -> ScratchPlanItem:
        pad = self.ensure_pad(scope_id)
        item = pad.plan_items.get(task_id)
        if item is None:
            item = ScratchPlanItem(
                item_id=f"item_{uuid.uuid4().hex[:10]}",
                task_id=task_id,
                title=title,
                status=status,
                metadata=metadata or {},
            )
        else:
            item = item.model_copy(
                update={
                    "title": title,
                    "status": status,
                    "updated_at": datetime.now(timezone.utc),
                    "metadata": {**item.metadata, **(metadata or {})},
                }
            )
        pad.plan_items[task_id] = item
        return item

    def update_plan_item_status(
        self,
        scope_id: str,
        task_id: str,
        status: ScratchPlanItemStatus,
        metadata: dict[str, Any] | None = None,
    ) -> ScratchPlanItem:
        pad = self.ensure_pad(scope_id)
        if task_id not in pad.plan_items:
            raise KeyError(f"unknown scratch task_id: {task_id}")
        item = pad.plan_items[task_id]
        updated = item.model_copy(
            update={
                "status": status,
                "updated_at": datetime.now(timezone.utc),
                "metadata": {**item.metadata, **(metadata or {})},
            }
        )
        pad.plan_items[task_id] = updated
        return updated

    def append_event(
        self,
        scope_id: str,
        event_type: str,
        workflow_id: str,
        execution_id: str,
        *,
        task_id: str | None = None,
        correlation_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> ScratchEvent:
        pad = self.ensure_pad(scope_id)
        if len(pad.events) >= self._max_entries:
            raise RuntimeError("scratchpad quota exceeded")
        event = ScratchEvent(
            event_id=f"evt_{uuid.uuid4().hex[:10]}",
            event_type=event_type,
            workflow_id=workflow_id,
            execution_id=execution_id,
            task_id=task_id,
            correlation_id=correlation_id,
            details=details or {},
        )
        pad.events.append(event)
        return event

    def get_pad(self, scope_id: str) -> ScratchPad | None:
        self.purge_expired()
        return self._pads.get(scope_id)

    def purge_expired(self, now: datetime | None = None) -> int:
        current = now or datetime.now(timezone.utc)
        expired = [
            scope_id
            for scope_id, pad in self._pads.items()
            if pad.expires_at <= current
        ]
        for scope_id in expired:
            del self._pads[scope_id]
        return len(expired)
