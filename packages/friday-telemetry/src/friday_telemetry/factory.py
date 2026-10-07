"""Provider-neutral programmatic assembly with explicit caller ownership."""

from types import TracebackType
from typing import Any
from uuid import uuid4

from friday_telemetry.config import TelemetryFactoryConfig
from friday_telemetry.interface import TelemetryInterface
from friday_telemetry.lifecycle import (
    LifecycleResult,
    TelemetryLifecycle,
    TelemetrySnapshot,
    _timeout_seconds,
)
from friday_telemetry.providers.debug import DebugTelemetryRecorder


class _DisabledTelemetry(TelemetryInterface):
    """Zero-effect interface for disabled factory handles."""

    def capture_event(self, event_name: str, data: dict[str, Any]) -> None:
        pass

    def start_span(self, name: str, parent_id: str | None = None) -> str:
        return str(uuid4())

    def end_span(self, span_id: str, data: dict[str, Any] | None = None) -> None:
        pass


class ManagedTelemetry:
    """Owns only factory-created resources; callers explicitly close this handle."""

    def __init__(
        self,
        telemetry: TelemetryInterface,
        lifecycle: TelemetryLifecycle | None = None,
        *,
        available: bool = True,
    ) -> None:
        self.telemetry = telemetry
        self._lifecycle = lifecycle
        self._available = available
        self._closed_result: LifecycleResult | None = None

    def snapshot(self) -> TelemetrySnapshot:
        if self._lifecycle is not None:
            return self._lifecycle.snapshot()
        return TelemetrySnapshot(
            available=self._available, closed=self._closed_result is not None
        )

    def flush(self, timeout_millis: int = 5000) -> LifecycleResult:
        _timeout_seconds(timeout_millis)
        if self._lifecycle is not None:
            return self._lifecycle.flush(timeout_millis)
        if self._closed_result is not None:
            return LifecycleResult("closed", self.snapshot())
        return LifecycleResult("success", self.snapshot())

    def shutdown(self, timeout_millis: int = 5000) -> LifecycleResult:
        _timeout_seconds(timeout_millis)
        if self._lifecycle is not None:
            return self._lifecycle.shutdown(timeout_millis)
        if self._closed_result is None:
            self._closed_result = LifecycleResult(
                "success", TelemetrySnapshot(available=self._available, closed=True)
            )
        return self._closed_result

    def __enter__(self) -> "ManagedTelemetry":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.shutdown()


def create_telemetry(config: TelemetryFactoryConfig | None = None) -> ManagedTelemetry:
    """Create disabled/debug without importing or activating optional SDK modules."""
    settings = config if config is not None else TelemetryFactoryConfig()
    if settings.provider == "disabled":
        return ManagedTelemetry(_DisabledTelemetry(), available=False)
    if settings.provider == "debug":
        return ManagedTelemetry(DebugTelemetryRecorder())
    from friday_telemetry.providers.otel import OpenTelemetryProvider

    provider = OpenTelemetryProvider._from_settings(settings.otel)
    return ManagedTelemetry(provider, provider)
