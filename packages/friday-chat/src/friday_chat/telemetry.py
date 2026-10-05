"""Bounded local diagnostics and a content-free boundary for injected telemetry."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Literal
from uuid import uuid4

from friday_telemetry import MCPEvent, TelemetryInterface
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
Scalar = str | int | bool


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


class ChatTelemetryObserver(TelemetryInterface):
    """Local provider or safe wrapper around a borrowed custom provider.

    The interface's dynamic dictionaries are validated at entry. Only lifecycle
    models and existing MCP models cross the sink boundary. Legacy hooks are
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
        try:
            if "name" in data:
                raise ValueError("reserved event field")
            if event_name.startswith("mcp."):
                model = MCPEvent.model_validate({**data, "name": event_name[4:]})
                attributes = model.attributes()
            elif event_name.startswith("chat."):
                lifecycle = LifecycleEvent.model_validate(
                    {**data, "name": event_name[5:]}
                )
                if lifecycle.session_ref != self._session_ref:
                    raise ValueError("foreign session")
                attributes = lifecycle.model_dump(exclude={"name"}, exclude_none=True)
            else:
                raise ValueError("unknown event")
        except (ValidationError, ValueError, TypeError):
            self._rejected += 1
            self._record_failure("invalid_event")
            return
        self._record(event_name, attributes)
        if self._sink is not None:
            try:
                self._sink.capture_event(event_name, dict(attributes))
            except Exception:
                self._record_failure("sink_failed")

    def _record(self, name: str, attributes: dict[str, Scalar]) -> None:
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
        if name not in {"chat.runtime", "chat.application"} or len(self._spans) >= 128:
            self._rejected += 1
            self._record_failure("invalid_event")
            return span_id
        sink_id = None
        if self._sink is not None:
            try:
                sink_id = self._sink.start_span(
                    name, self._spans.get(parent_id) if parent_id else None
                )
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
                self._sink.end_span(sink_id, attributes)
            except Exception:
                self._record_failure("sink_failed")
