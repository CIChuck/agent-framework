"""Fan-out telemetry with child span ownership and isolated payloads."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from friday_telemetry.interface import TelemetryInterface


class CompositeDeliveryError(RuntimeError):
    """Content-free aggregate failure after every sink was attempted."""

    def __init__(self, failure_count: int) -> None:
        self.failure_count = failure_count
        super().__init__("Composite telemetry delivery failed")


@dataclass(frozen=True)
class _ChildSpan:
    provider: TelemetryInterface
    span_id: str


class CompositeProvider(TelemetryInterface):
    """Map each child's span and parent IDs and snapshot span membership.

    A never-published first child ID remains public for caller compatibility.
    Reused child IDs and empty composites use opaque local IDs. Published IDs
    stay reserved for this instance's lifetime so stale ends cannot alias later
    spans. Failing sinks do not prevent delivery to healthy sinks.
    """

    def __init__(self, providers: list[TelemetryInterface]) -> None:
        self._providers = list(providers)
        self._spans: dict[str, tuple[_ChildSpan, ...]] = {}
        self._issued_span_ids: set[str] = set()
        self._span_namespace = uuid4().hex
        self._next_span_id = 0

    def add_provider(self, provider: TelemetryInterface) -> None:
        self._providers.append(provider)

    def remove_provider(self, provider: TelemetryInterface) -> None:
        self._providers.remove(provider)

    def capture_event(self, event_name: str, data: dict[str, Any]) -> None:
        failures = 0
        for provider in tuple(self._providers):
            try:
                provider.capture_event(event_name, deepcopy(data))
            except Exception:
                failures += 1
        if failures:
            raise CompositeDeliveryError(failures)

    def start_span(self, name: str, parent_id: str | None = None) -> str:
        parents = self._spans.get(parent_id, ()) if parent_id is not None else ()
        children: list[_ChildSpan] = []
        failures = 0
        for provider in tuple(self._providers):
            child_parent = next(
                (parent.span_id for parent in parents if parent.provider is provider),
                None,
            )
            try:
                children.append(
                    _ChildSpan(provider, provider.start_span(name, child_parent))
                )
            except Exception:
                failures += 1
        if failures:
            # A failed start cannot return an ID: close opened child resources.
            for child in children:
                try:
                    child.provider.end_span(child.span_id)
                except Exception:
                    failures += 1
            raise CompositeDeliveryError(failures)
        span_id = children[0].span_id if children else self._new_span_id()
        if span_id in self._issued_span_ids:
            span_id = self._new_span_id()
        self._issued_span_ids.add(span_id)
        self._spans[span_id] = tuple(children)
        return span_id

    def _new_span_id(self) -> str:
        """Allocate without assuming random IDs cannot collide with child IDs."""
        while True:
            self._next_span_id += 1
            span_id = f"{self._span_namespace}:{self._next_span_id}"
            if span_id not in self._issued_span_ids:
                return span_id

    def end_span(self, span_id: str, data: dict[str, Any] | None = None) -> None:
        failures = 0
        for child in self._spans.pop(span_id, ()):
            try:
                child.provider.end_span(child.span_id, deepcopy(data))
            except Exception:
                failures += 1
        if failures:
            raise CompositeDeliveryError(failures)

    @property
    def providers(self) -> list[TelemetryInterface]:
        """Return a membership snapshot; mutation uses add/remove_provider."""
        return list(self._providers)
