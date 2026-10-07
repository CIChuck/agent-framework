"""Bounded request accounting; the only sink operation is a guarded capture_event."""

from __future__ import annotations

import asyncio
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from types import TracebackType
from typing import Literal, Self
from uuid import uuid4

from friday_telemetry.interface import TelemetryInterface
from friday_telemetry.models.llm_events import (
    LLMAPI,
    AttemptFinish,
    BatchFinish,
    CostMetrics,
    Coverage,
    DispatchOutcome,
    ErrorCategory,
    FinishReason,
    LLMEvent,
    Operation,
    Outcome,
    RequestFinish,
    RequestIdentity,
    RequestStart,
    ServiceRole,
    UsageMetrics,
    UsageState,
)

ErrorClassifier = Callable[[BaseException], ErrorCategory]
CostEstimator = Callable[[UsageMetrics], CostMetrics]


@dataclass(frozen=True)
class DeliveryDiagnostic:
    sequence: int
    reason: Literal["sink_failed", "invalid_event"]


@dataclass(frozen=True)
class DeliverySnapshot:
    failure_count: int
    dropped_count: int
    records: tuple[DeliveryDiagnostic, ...]


class SafeLLMTelemetry:
    """One service instance, an opaque model reference, and a borrowed optional sink."""

    def __init__(self, telemetry: TelemetryInterface | None, *, service_role: ServiceRole = "unspecified") -> None:
        self.telemetry = telemetry
        # Enforce even dynamically supplied roles through the closed identity model.
        self.identity = RequestIdentity(request_id=uuid4().hex, operation="chat",
                                        api="legacy_completion", service_role=service_role,
                                        model_ref=uuid4().hex)
        self._failures = 0
        self._dropped = 0
        self._diagnostics: deque[DeliveryDiagnostic] = deque(maxlen=256)

    def snapshot(self) -> DeliverySnapshot:
        return DeliverySnapshot(self._failures, self._dropped, tuple(self._diagnostics))

    def diagnose(self, reason: Literal["sink_failed", "invalid_event"]) -> None:
        self._failures += 1
        if len(self._diagnostics) == self._diagnostics.maxlen:
            self._dropped += 1
        self._diagnostics.append(DeliveryDiagnostic(self._failures, reason))

    def emit(self, event: RequestStart | AttemptFinish | BatchFinish | RequestFinish) -> None:
        if self.telemetry is None:
            return
        try:
            parsed = LLMEvent.model_validate(event)
            attributes = parsed.attributes()
        except Exception:
            self.diagnose("invalid_event")
            return
        try:
            self.telemetry.capture_event(event.name, attributes)
        except Exception:
            self.diagnose("sink_failed")

    def request(self, api: LLMAPI, *, classify: ErrorClassifier,
                estimate: CostEstimator) -> RequestTracker:
        operation: Operation = "embedding" if api.startswith("embedding_") else "chat"
        identity = RequestIdentity(request_id=uuid4().hex, operation=operation, api=api,
                                   service_role=self.identity.service_role,
                                   model_ref=self.identity.model_ref)
        return RequestTracker(self, identity, classify, estimate)


class RequestTracker:
    """Per-invocation state; explicit references keep concurrent requests independent."""

    def __init__(self, helper: SafeLLMTelemetry, identity: RequestIdentity,
                 classify: ErrorClassifier, estimate: CostEstimator) -> None:
        self.helper = helper
        self.identity = identity
        self.classify = classify
        self.estimate = estimate
        self.started = time.monotonic()
        self.attempt_count = 0
        self.batch_count = 0
        self.successful_batches = 0
        self.usage = UsageMetrics()
        self._batch_fields: dict[str, int] | None = None
        self._missing_batch_usage = False
        self._reported_batch_usage = False
        self._invalid_batch_usage = False
        self._invalid_stream_usage = False
        self.chunk_count = 0
        self.first_text_ms: float | None = None
        self.finish_reason: FinishReason | None = None
        self.outcome: Outcome = "success"
        self.finished = False

    def __enter__(self) -> Self:
        try:
            self.helper.emit(RequestStart(**self.identity.model_dump()))
        except BaseException as error:
            self.finish(error)
            raise
        return self

    def __exit__(self, kind: type[BaseException] | None, error: BaseException | None,
                 traceback: TracebackType | None) -> Literal[False]:
        self.finish(error)
        return False

    def category(self, error: BaseException | None) -> ErrorCategory | None:
        if error is None:
            return None
        try:
            return self.classify(error)
        except Exception:
            self.helper.diagnose("invalid_event")
            return "unknown"

    def attempt(self, batch: BatchTracker | None = None) -> AttemptTracker:
        return AttemptTracker(self, batch)

    def batch(self, item_count: int) -> BatchTracker:
        return BatchTracker(self, item_count)

    def record_chunk(self, usage: UsageMetrics | None) -> None:
        self.chunk_count += 1
        if usage is None:
            return
        previous = self.usage
        if usage.usage_state == "invalid" or any(
            (old := getattr(previous, field)) is not None
            and (new := getattr(usage, field)) is not None and new < old
            for field in ("input_tokens", "output_tokens", "total_tokens", "reasoning_tokens")
        ):
            self._invalid_stream_usage = True
        self.usage = UsageMetrics(usage_state="invalid") if self._invalid_stream_usage else usage

    def text_seen(self) -> None:
        if self.first_text_ms is None:
            self.first_text_ms = (time.monotonic() - self.started) * 1000

    def add_batch_usage(self, usage: UsageMetrics) -> None:
        self.successful_batches += 1
        self._reported_batch_usage |= usage.usage_state == "reported"
        self._missing_batch_usage |= usage.usage_state != "reported"
        self._invalid_batch_usage |= usage.usage_state == "invalid"
        fields = {key: value for key in ("input_tokens", "total_tokens")
                  if (value := getattr(usage, key)) is not None}
        if self._batch_fields is None:
            self._batch_fields = fields
        else:
            self._batch_fields = {key: value + fields[key] for key, value in self._batch_fields.items()
                                  if key in fields}
        state: UsageState = "invalid" if self._invalid_batch_usage else "reported" if self._batch_fields else "unavailable"
        try:
            self.usage = UsageMetrics(usage_state=state, **self._batch_fields)
        except Exception:
            self.usage = UsageMetrics(usage_state="invalid")
            self._invalid_batch_usage = True

    def finish(self, error: BaseException | None = None) -> None:
        if self.finished:
            return
        self.finished = True
        category = self.category(error)
        outcome = self.outcome
        if isinstance(error, asyncio.CancelledError):
            outcome = "cancelled"
        elif isinstance(error, GeneratorExit):
            outcome = "incomplete"
        elif error is not None:
            outcome = "blocked" if category == "circuit_open" and not self.attempt_count else "error"
        coverage: Coverage = "none"
        if self.usage.usage_state == "reported":
            coverage = "complete" if outcome == "success" and not self._missing_batch_usage else "partial"
        elif (self._reported_batch_usage and self._missing_batch_usage) or any(
            value is not None for value in (self.usage.input_tokens, self.usage.total_tokens)
        ):
            coverage = "partial"
        cost = CostMetrics()
        if coverage == "complete":
            try:
                cost = self.estimate(self.usage)
            except Exception:
                self.helper.diagnose("invalid_event")
                cost = CostMetrics(cost_state="invalid")
        try:
            event = RequestFinish(
                **self.identity.model_dump(), **self.usage.model_dump(), **cost.model_dump(),
                outcome=outcome, attempt_count=self.attempt_count, batch_count=self.batch_count,
                duration_ms=(time.monotonic() - self.started) * 1000,
                usage_coverage=coverage, error_category=category,
                first_text_ms=self.first_text_ms,
                chunk_count=self.chunk_count if self.identity.api.endswith("stream") else None,
                finish_reason=self.finish_reason,
            )
        except Exception:
            self.helper.diagnose("invalid_event")
            return
        self.helper.emit(event)


class AttemptTracker:
    def __init__(self, request: RequestTracker, batch: BatchTracker | None) -> None:
        self.request = request
        self.batch = batch
        self.started = 0.0
        self.identifier = uuid4().hex

    def __enter__(self) -> Self:
        if self.batch is not None:
            self.batch.dispatch()
        self.request.attempt_count += 1
        self.number = self.request.attempt_count
        self.started = time.monotonic()
        return self

    def __exit__(self, kind: type[BaseException] | None, error: BaseException | None,
                 traceback: TracebackType | None) -> Literal[False]:
        outcome: DispatchOutcome = "cancelled" if isinstance(error, asyncio.CancelledError) else "error" if error else "success"
        try:
            event = AttemptFinish(
                **self.request.identity.model_dump(), attempt_id=self.identifier,
                attempt_number=self.number, outcome=outcome,
                duration_ms=(time.monotonic() - self.started) * 1000,
                batch_id=self.batch.identifier if self.batch else None,
                batch_number=self.batch.number if self.batch else None,
                error_category=self.request.category(error),
            )
        except Exception:
            self.request.helper.diagnose("invalid_event")
        else:
            self.request.helper.emit(event)
        return False


class BatchTracker:
    def __init__(self, request: RequestTracker, item_count: int) -> None:
        self.request = request
        self.item_count = item_count
        self.identifier = uuid4().hex
        self.number: int | None = None
        self.attempts = 0
        self.usage = UsageMetrics()
        self.started = time.monotonic()

    def __enter__(self) -> Self:
        return self

    def dispatch(self) -> None:
        if self.number is None:
            self.request.batch_count += 1
            self.number = self.request.batch_count
        self.attempts += 1

    def __exit__(self, kind: type[BaseException] | None, error: BaseException | None,
                 traceback: TracebackType | None) -> Literal[False]:
        if self.number is None:
            return False
        outcome: DispatchOutcome = "cancelled" if isinstance(error, asyncio.CancelledError) else "error" if error else "success"
        if error is None:
            self.request.add_batch_usage(self.usage)
        try:
            event = BatchFinish(**self.request.identity.model_dump(), **self.usage.model_dump(),
                                batch_id=self.identifier, batch_number=self.number,
                                outcome=outcome, attempt_count=self.attempts,
                                item_count=self.item_count,
                                duration_ms=(time.monotonic() - self.started) * 1000,
                                error_category=self.request.category(error))
        except Exception:
            self.request.helper.diagnose("invalid_event")
        else:
            self.request.helper.emit(event)
        return False
