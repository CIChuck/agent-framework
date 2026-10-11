"""Bounded local diagnostics and a content-free boundary for injected telemetry."""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Literal
from uuid import uuid4

from friday_telemetry import (
    CorrelationScope,
    ExecutionEvent,
    LLMEvent,
    MCPEvent,
    TelemetryInterface,
)
from friday_telemetry.models.execution import (
    ExecutionIdentity,
    LLMLink,
    MCPLink,
    OperationFinish,
    TurnFinish,
)
from pydantic import BaseModel, ConfigDict, Field, ValidationError

LifecycleName = Literal["runtime_ready", "application_start", "application_stop"]
Outcome = Literal["succeeded", "failed", "cancelled"]
Reason = Literal[
    "startup_failed",
    "application_failed",
    "shutdown_failed",
    "cancelled",
    "sink_failed",
    "invalid_event",
]
Scalar = str | int | float | bool


class LifecycleEvent(BaseModel):
    """Closed runtime lifecycle payload; no application content is accepted."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    name: LifecycleName
    session_ref: str = Field(pattern=r"^[0-9a-f]{16}$")
    outcome: Outcome = "succeeded"
    reason: Reason | None = None
    count: int = Field(default=0, ge=0, le=1_000_000)


class SpanOutcome(BaseModel):
    """The only attributes accepted for a first-slice lifecycle span."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    outcome: Outcome = "succeeded"
    count: int = Field(default=0, ge=0, le=1_000_000)


@dataclass(frozen=True)
class DiagnosticEvent:
    """An immutable serialized safe event, retained only in process memory."""

    name: str
    sequence: int
    attributes: tuple[tuple[str, Scalar], ...]


@dataclass(frozen=True)
class TelemetrySnapshot:
    """Safe public inspection, independent of the health of an injected sink."""

    configured: bool
    provider: Literal["disabled", "debug", "injected"]
    state: Literal["disabled", "active", "failed"]
    events: tuple[DiagnosticEvent, ...]
    dropped_count: int
    failure_count: int
    rejected_count: int


@dataclass(frozen=True)
class ExecutionDiagnostics:
    turns: tuple[TurnFinish, ...]
    counters: tuple[tuple[str, str, int], ...]
    histograms: tuple[tuple[str, str, str, int], ...]


class ChatTelemetryObserver(TelemetryInterface):
    """Local provider or safe wrapper around a borrowed custom provider.

    The interface's dynamic dictionaries are validated at entry. Only closed lifecycle, MCP and LLM event
    models cross the sink boundary. Raw legacy hooks are
    deliberately not connected in this slice. Borrowed providers are never closed.
    """

    def __init__(
        self,
        *,
        enabled: bool,
        session_id: str,
        provider: TelemetryInterface | None = None,
    ) -> None:
        self._configured = enabled
        self._provider_kind: Literal["disabled", "debug", "injected"] = (
            "injected" if provider is not None else "debug" if enabled else "disabled"
        )
        self._sink = provider
        self._session_ref = sha256(
            session_id.encode("utf-8", errors="surrogatepass")
        ).hexdigest()[:16]
        self._events: deque[DiagnosticEvent] = deque(maxlen=256)
        self._sequence = 0
        self._dropped = 0
        self._failures = 0
        self._rejected = 0
        self._spans: dict[str, str | None] = {}
        self.correlation = CorrelationScope(self._session_ref)
        self._turn_summaries: deque[TurnFinish] = deque(maxlen=32)
        self._counters: dict[tuple[str, str], int] = {}
        self._histograms: dict[tuple[str, str, str], int] = {}

    def execution_snapshot(self) -> ExecutionDiagnostics:
        return ExecutionDiagnostics(tuple(self._turn_summaries),
                                    tuple((*key, value) for key, value in sorted(self._counters.items())),
                                    tuple((*key, value) for key, value in sorted(self._histograms.items())))

    def report_failure(self) -> None:
        self._rejected += 1
        self._record_failure("invalid_event")

    def execution(self, event: ExecutionIdentity) -> None:
        if not self.enabled:
            return
        try:
            parsed = ExecutionEvent.model_validate(event)
            attributes = parsed.attributes()
        except (ValidationError, ValueError, TypeError):
            self.report_failure()
            return
        self.capture_event(parsed.root.name, attributes)

    def _aggregate(self, event: OperationFinish | TurnFinish) -> None:
        frame = self.correlation.current()
        if frame is None or frame.terminal:
            raise ValueError("unowned or duplicate terminal event")
        frame.terminal = True
        kind = event.operation_kind if isinstance(event, OperationFinish) else "turn"
        key = (kind, event.outcome)
        self._counters[key] = min(2**63-1, self._counters.get(key, 0)+1)
        bucket = next((f"le_{limit}" for limit in (1, 5, 10, 25, 50, 100, 250, 500, 1000, 5000)
                       if event.duration_ms <= limit), "gt_5000")
        hist_key = (*key, bucket)
        self._histograms[hist_key] = min(2**63-1, self._histograms.get(hist_key, 0)+1)
        if isinstance(event, TurnFinish):
            self._turn_summaries.append(event)
        elif frame.accounting is not None:
            if event.operation_kind in {"native_tool", "mcp_tool"}:
                if event.outcome == "succeeded":
                    frame.accounting.completed_tools = min(2**63-1, frame.accounting.completed_tools+1)
                elif event.outcome != "skipped":
                    frame.accounting.failed_tools = min(2**63-1, frame.accounting.failed_tools+1)
            if event.operation_kind == "memory_store_turn" and event.outcome == "succeeded":
                frame.accounting.persistence = "partial"
            if event.operation_kind == "persistence":
                frame.accounting.persistence = "completed" if event.outcome == "succeeded" else "cancelled" if event.outcome == "cancelled" else "failed"

    @property
    def enabled(self) -> bool:
        return self._provider_kind != "disabled"

    def snapshot(self) -> TelemetrySnapshot:
        return TelemetrySnapshot(
            configured=self._configured,
            provider=self._provider_kind,
            state="disabled"
            if not self.enabled
            else "failed"
            if self._failures
            else "active",
            events=tuple(self._events),
            dropped_count=self._dropped,
            failure_count=self._failures,
            rejected_count=self._rejected,
        )

    def emit(
        self,
        name: LifecycleName,
        *,
        outcome: Outcome = "succeeded",
        reason: Reason | None = None,
        count: int = 0,
    ) -> None:
        self.capture_event(
            f"chat.{name}",
            {
                "session_ref": self._session_ref,
                "outcome": outcome,
                "reason": reason,
                "count": count,
            },
        )

    def capture_event(self, event_name: str, data: dict[str, Any]) -> None:
        if not self.enabled:
            return
        attributes: dict[str, Scalar] = {}
        try:
            if "name" in data:
                raise ValueError("reserved event field")
            if event_name.startswith("mcp."):
                model = MCPEvent.model_validate({**data, "name": event_name[4:]})
                attributes.update(model.attributes())
            elif event_name.startswith("llm."):
                llm = LLMEvent.model_validate({**data, "name": event_name})
                if llm.root.session_ref not in (None, self._session_ref):
                    raise ValueError("foreign session")
                attributes = llm.attributes()
                attributes["session_ref"] = self._session_ref
            elif event_name.startswith("chat."):
                lifecycle = LifecycleEvent.model_validate(
                    {**data, "name": event_name[5:]}
                )
                if lifecycle.session_ref != self._session_ref:
                    raise ValueError("foreign session")
                attributes = lifecycle.model_dump(exclude={"name"}, exclude_none=True)
            elif event_name.startswith("execution."):
                execution = ExecutionEvent.model_validate({**data, "name": event_name})
                frame = self.correlation.current()
                if frame is None or execution.root.session_ref != self._session_ref or (
                    execution.root.turn_ref, execution.root.operation_ref, execution.root.parent_operation_ref
                ) != (frame.context.turn_ref, frame.context.operation_ref, frame.context.parent_operation_ref):
                    raise ValueError("foreign or inactive execution scope")
                attributes = execution.attributes()
                if isinstance(execution.root, (OperationFinish, TurnFinish)):
                    self._aggregate(execution.root)
            else:
                raise ValueError("unknown event")
        except (ValidationError, ValueError, TypeError):
            self._rejected += 1
            self._record_failure("invalid_event")
            return
        self._record(event_name, attributes)
        source_sequence = self._sequence
        if self._sink is not None:
            try:
                frame = self.correlation.current()
                if frame is None:
                    self._sink.capture_event(event_name, dict(attributes))
                else:
                    frame.delivery_context.run(self._sink.capture_event, event_name, dict(attributes))
            except Exception:
                self._record_failure("sink_failed")
        frame = self.correlation.current()
        if frame is not None and frame.context.turn_ref is not None:
            try:
                identity = frame.context.identity().model_dump()
                if event_name == "llm.request_start":
                    self.execution(LLMLink.model_validate({**identity, "request_id": attributes["request_id"]}))
                elif event_name.startswith("mcp."):
                    self.execution(MCPLink.model_validate({**identity, **attributes,
                                                          "source_event": event_name[4:], "source_sequence": source_sequence}))
            except (ValidationError, ValueError, TypeError, KeyError):
                self.report_failure()

    def _record(self, name: str, attributes: Mapping[str, Scalar]) -> None:
        self._sequence += 1
        if len(self._events) == self._events.maxlen:
            self._dropped += 1
        self._events.append(
            DiagnosticEvent(name, self._sequence, tuple(sorted(attributes.items())))
        )

    def _record_failure(self, reason: Reason) -> None:
        self._failures += 1
        # Local only: do not recursively deliver failure events to a failed sink.
        self._record(
            "chat.telemetry_delivery_failure",
            {"reason": reason, "session_ref": self._session_ref},
        )

    def start_span(self, name: str, parent_id: str | None = None) -> str:
        span_id = uuid4().hex
        if not self.enabled:
            return span_id
        if name not in {"chat.runtime", "chat.application", "chat.turn", "chat.operation"} or len(self._spans) >= 128:
            self._rejected += 1
            self._record_failure("invalid_event")
            return span_id
        sink_id = None
        if self._sink is not None:
            try:
                sink_parent = self._spans.get(parent_id) if parent_id else None
                frame = self.correlation.current()
                sink_id = (self._sink.start_span(name, sink_parent) if frame is None else
                           frame.delivery_context.run(self._sink.start_span, name, sink_parent))
            except Exception:
                self._record_failure("sink_failed")
        self._spans[span_id] = sink_id
        return span_id

    def end_span(self, span_id: str, data: dict[str, Any] | None = None) -> None:
        if span_id not in self._spans:
            return
        sink_id = self._spans.pop(span_id)
        try:
            attributes = SpanOutcome.model_validate(data or {}).model_dump()
        except (ValidationError, ValueError, TypeError):
            self._rejected += 1
            self._record_failure("invalid_event")
            attributes = {"outcome": "failed", "count": 0}
        if self._sink is not None and sink_id is not None:
            try:
                frame = self.correlation.current()
                if frame is None:
                    self._sink.end_span(sink_id, attributes)
                else:
                    frame.delivery_context.run(self._sink.end_span, sink_id, attributes)
            except Exception:
                self._record_failure("sink_failed")
