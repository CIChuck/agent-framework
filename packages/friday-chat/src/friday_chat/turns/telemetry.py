"""Best-effort observation at existing Chat boundaries, without content retention."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from friday_telemetry import ExecutionContext
from friday_telemetry.helpers.correlation import TurnAccounting
from friday_telemetry.models.execution import (
    CountKind,
    ExecutionOutcome,
    ExecutionReason,
    OperationFinish,
    OperationKind,
    OperationStart,
    PersistenceState,
    TurnFinish,
    TurnStart,
)

if TYPE_CHECKING:
    from friday_chat.telemetry import ChatTelemetryObserver


@dataclass
class OperationObservation:
    outcome: ExecutionOutcome = "succeeded"
    reason: ExecutionReason | None = None
    count: int | None = None
    count_kind: CountKind | None = None
    persistence_state: PersistenceState | None = None


def error_category(error: BaseException) -> tuple[ExecutionOutcome, ExecutionReason]:
    from friday_chat.turns.processor import (
        TurnBudgetError,
        TurnCircuitBreakerOpenError,
        TurnPersistenceError,
        TurnRetryExhaustedError,
        TurnTimeoutError,
    )
    if isinstance(error, (asyncio.CancelledError, GeneratorExit)):
        return ("cancelled", "cancelled") if isinstance(error, asyncio.CancelledError) else ("incomplete", "cancelled")
    if isinstance(error, (TimeoutError, TurnTimeoutError)):
        return "failed", "timeout"
    if isinstance(error, TurnCircuitBreakerOpenError):
        return "blocked", "circuit_open"
    if isinstance(error, TurnBudgetError):
        return "blocked", "selection_rejected"
    if isinstance(error, TurnRetryExhaustedError):
        return "failed", "retry_exhausted"
    if isinstance(error, TurnPersistenceError):
        return "failed", "persistence_failed"
    if isinstance(error, KeyError):
        return "failed", "unknown_tool"
    return "failed", "unknown"


@contextmanager
def turn_scope(observer: ChatTelemetryObserver | None, mode: Literal["completion", "streaming"]) -> Iterator[ExecutionContext | None]:
    if observer is None or not observer.enabled:
        yield None
        return
    context = observer.correlation.context(turn=True)
    started = time.monotonic()
    accounting = TurnAccounting()
    span = observer.start_span("chat.turn")
    outcome: ExecutionOutcome = "succeeded"
    reason: ExecutionReason | None = None
    with observer.correlation.bind(context, span_id=span, accounting=accounting):
        observer.execution(TurnStart(**context.identity().model_dump(), mode=mode))
        try:
            yield context.origin()
        except BaseException as error:
            outcome, reason = error_category(error)
            raise
        finally:
            try:
                observer.execution(TurnFinish(**context.identity().model_dump(), outcome=outcome, reason=reason,
                                              duration_ms=(time.monotonic()-started)*1000,
                                              persistence=accounting.persistence,
                                              completed_tools=accounting.completed_tools, failed_tools=accounting.failed_tools))
            except Exception:
                observer.report_failure()
            finally:
                observer.end_span(span, {"outcome": "succeeded" if outcome == "succeeded" else "cancelled" if outcome == "cancelled" else "failed"})


@contextmanager
def operation_scope(observer: ChatTelemetryObserver | None, kind: OperationKind,
                    *, origin: ExecutionContext | None = None) -> Iterator[OperationObservation]:
    observation = OperationObservation()
    if observer is None or not observer.enabled:
        yield observation
        return
    parent = observer.correlation.current()
    if origin is not None and not observer.correlation.accepts(origin):
        observer.report_failure()
        origin = None
        parent = None
    context = (origin or (parent.context if parent else observer.correlation.context())).child()
    started = time.monotonic()
    span = observer.start_span("chat.operation", parent.span_id if parent and origin is None else None)
    accounting = parent.accounting if parent and origin is None else None
    with observer.correlation.bind(context, span_id=span, accounting=accounting):
        observer.execution(OperationStart(**context.identity().model_dump(), operation_kind=kind))
        try:
            yield observation
        except BaseException as error:
            observation.outcome, observation.reason = error_category(error)
            if observation.persistence_state != "completed" and kind in {"memory_extract", "persistence"}:
                observation.persistence_state = "cancelled" if observation.outcome == "cancelled" else "failed"
            raise
        finally:
            try:
                observer.execution(OperationFinish(**context.identity().model_dump(), operation_kind=kind,
                                                   outcome=observation.outcome, reason=observation.reason,
                                                   duration_ms=(time.monotonic()-started)*1000,
                                                   count=observation.count, count_kind=observation.count_kind,
                                                   persistence_state=observation.persistence_state))
            except Exception:
                observer.report_failure()
            finally:
                observer.end_span(span, {"outcome": "succeeded" if observation.outcome in {"succeeded", "skipped", "pending"} else "cancelled" if observation.outcome == "cancelled" else "failed"})


@contextmanager
def detached_scope(observer: ChatTelemetryObserver | None) -> Iterator[None]:
    if observer is None:
        yield
    else:
        with observer.correlation.clear():
            yield
