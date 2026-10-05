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

    The first child ID remains the public ID for caller compatibility. Empty
    composites use an opaque local ID. Failing sinks do not prevent healthy
    sinks from receiving events or closing their own spans.
    """

    def __init__(self, providers: list[TelemetryInterface]) -> None:
        self._providers = list(providers)
        self._spans: dict[str, tuple[_ChildSpan, ...]] = {}

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
        span_id = children[0].span_id if children else uuid4().hex
        self._spans[span_id] = tuple(children)
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
