"""Instance-owned task-local execution scopes; no provider/global context lookup."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field, replace
from uuid import uuid4

from friday_telemetry.models.execution import ExecutionIdentity, PersistenceState


@dataclass(frozen=True)
class ExecutionContext:
    """Validated opaque lineage and a non-exported owner capability."""

    session_ref: str
    turn_ref: str | None
    owner: object = field(repr=False, compare=False)
    operation_ref: str | None = None
    parent_operation_ref: str | None = None

    def __post_init__(self) -> None:
        self.identity()

    def identity(self) -> ExecutionIdentity:
        return ExecutionIdentity(session_ref=self.session_ref, turn_ref=self.turn_ref,
                                 operation_ref=self.operation_ref, parent_operation_ref=self.parent_operation_ref)

    def child(self) -> ExecutionContext:
        return replace(self, operation_ref=uuid4().hex, parent_operation_ref=self.operation_ref)

    def origin(self) -> ExecutionContext:
        return replace(self, operation_ref=None, parent_operation_ref=None)


@dataclass
class TurnAccounting:
    persistence: PersistenceState = "not_started"
    completed_tools: int = 0
    failed_tools: int = 0


@dataclass
class CorrelationFrame:
    context: ExecutionContext
    span_id: str | None
    accounting: TurnAccounting | None = None
    active: bool = True
    terminal: bool = False


class CorrelationScope:
    def __init__(self, session_ref: str) -> None:
        ExecutionIdentity(session_ref=session_ref)
        self.session_ref = session_ref
        self._owner = object()
        self._current: ContextVar[CorrelationFrame | None] = ContextVar("execution_scope", default=None)

    def current(self) -> CorrelationFrame | None:
        frame = self._current.get()
        return frame if frame is not None and frame.active else None

    def context(self, *, turn: bool = False) -> ExecutionContext:
        return ExecutionContext(self.session_ref, uuid4().hex if turn else None, self._owner)

    def accepts(self, context: ExecutionContext) -> bool:
        if not isinstance(context, ExecutionContext):
            return False
        try:
            context.identity()
        except (ValueError, TypeError):
            return False
        return context.owner is self._owner and context.session_ref == self.session_ref

    @contextmanager
    def bind(self, context: ExecutionContext, *, span_id: str | None = None,
             accounting: TurnAccounting | None = None) -> Iterator[CorrelationFrame]:
        if not self.accepts(context):
            raise ValueError("foreign or invalid execution context")
        frame = CorrelationFrame(context, span_id, accounting)
        token = self._current.set(frame)
        try:
            yield frame
        finally:
            frame.active = False
            self._current.reset(token)

    @contextmanager
    def clear(self) -> Iterator[None]:
        token = self._current.set(None)
        try:
            yield
        finally:
            self._current.reset(token)
