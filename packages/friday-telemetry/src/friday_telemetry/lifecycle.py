"""Optional owned lifecycle; borrowed TelemetryInterface implementations stay valid."""

from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable

LifecycleStatus = Literal["success", "failure", "timeout", "closed"]


class TelemetryInitializationError(RuntimeError):
    """Content-free construction failure."""

    def __init__(self) -> None:
        super().__init__("telemetry_initialization_failed")


class TelemetryOperationError(RuntimeError):
    """Closed categorical operation error, never a caller payload."""

    def __init__(
        self,
        reason: Literal["closed", "invalid_input", "invalid_parent", "active_limit"],
    ) -> None:
        super().__init__(reason)


@dataclass(frozen=True)
class TelemetrySnapshot:
    available: bool = True
    closed: bool = False
    active_spans: int = 0
    queued_spans: int = 0
    in_flight_spans: int = 0
    exported_spans: int = 0
    failed_spans: int = 0
    dropped_spans: int = 0
    export_failures: int = 0
    cancelled_spans: int = 0
    invalid_inputs: int = 0
    worker_alive: bool = False


@dataclass(frozen=True)
class LifecycleResult:
    status: LifecycleStatus
    snapshot: TelemetrySnapshot


@runtime_checkable
class TelemetryLifecycle(Protocol):
    def snapshot(self) -> TelemetrySnapshot: ...

    def flush(self, timeout_millis: int = 5000) -> LifecycleResult: ...

    def shutdown(self, timeout_millis: int = 5000) -> LifecycleResult: ...


def _timeout_seconds(timeout_millis: int) -> float:
    if type(timeout_millis) is not int or timeout_millis <= 0:
        raise TelemetryOperationError("invalid_input")
    return min(timeout_millis, 5000) / 1000
