"""Public-SDK processor with owned queue, observed exports and bounded waits."""

import threading
import time
from collections import deque

from opentelemetry.context import Context
from opentelemetry.sdk.trace import ReadableSpan, Span, SpanProcessor
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

from friday_telemetry.config import OTelConfig
from friday_telemetry.lifecycle import (
    LifecycleResult,
    TelemetrySnapshot,
    _timeout_seconds,
)

_MAX_COUNT = 2**63 - 1


class OwnedSpanProcessor(SpanProcessor):
    """Exports on one cooperative worker; never delegates deadlines to SDK BSP."""

    def __init__(self, exporter: SpanExporter, settings: OTelConfig) -> None:
        self._exporter = exporter
        self._settings = settings
        self._condition = threading.Condition()
        self._queue: deque[ReadableSpan] = deque()
        self._closing = False
        self._stop = False
        self._flush_requested = False
        self._in_flight = 0
        self._accepted = 0
        self._completed = 0
        self._exported = 0
        self._failed = 0
        self._dropped = 0
        self._failures = 0
        self._reported_failures = 0
        self._shutdown_result: LifecycleResult | None = None
        self._shutdown_lock = threading.Lock()
        self._worker = threading.Thread(
            target=self._work, name="FridayTelemetryExporter", daemon=True
        )
        try:
            self._worker.start()
        except Exception:
            exporter.shutdown()
            raise

    def on_start(self, span: Span, parent_context: Context | None = None) -> None:
        pass

    def on_end(self, span: ReadableSpan) -> None:
        with self._condition:
            if self._closing or len(self._queue) >= self._settings.queue_limit:
                self._dropped = min(_MAX_COUNT, self._dropped + 1)
                return
            self._queue.append(span)
            self._accepted += 1
            self._condition.notify_all()

    def _work(self) -> None:
        next_export = time.monotonic() + self._settings.flush_interval_ms / 1000
        while True:
            with self._condition:
                while not self._stop and (
                    not self._queue
                    or (
                        not self._flush_requested
                        and not self._closing
                        and len(self._queue) < self._settings.batch_limit
                        and time.monotonic() < next_export
                    )
                ):
                    delay = (
                        max(0, next_export - time.monotonic()) if self._queue else None
                    )
                    self._condition.wait(delay)
                if self._stop:
                    return
                batch = tuple(
                    self._queue.popleft()
                    for _ in range(min(len(self._queue), self._settings.batch_limit))
                )
                self._in_flight = len(batch)
            try:
                succeeded = self._exporter.export(batch) is SpanExportResult.SUCCESS
            except Exception:
                succeeded = False
            with self._condition:
                self._completed += len(batch)
                if succeeded:
                    self._exported = min(_MAX_COUNT, self._exported + len(batch))
                else:
                    self._failed = min(_MAX_COUNT, self._failed + len(batch))
                    self._failures = min(_MAX_COUNT, self._failures + 1)
                self._in_flight = 0
                if not self._queue:
                    self._flush_requested = False
                next_export = time.monotonic() + self._settings.flush_interval_ms / 1000
                self._condition.notify_all()

    def snapshot(self) -> TelemetrySnapshot:
        with self._condition:
            return TelemetrySnapshot(
                closed=self._closing,
                queued_spans=len(self._queue),
                in_flight_spans=self._in_flight,
                exported_spans=self._exported,
                failed_spans=self._failed,
                dropped_spans=self._dropped,
                export_failures=self._failures,
                worker_alive=self._worker.is_alive(),
            )

    def flush_result(self, timeout_millis: int = 5000) -> LifecycleResult:
        deadline = time.monotonic() + _timeout_seconds(timeout_millis)
        with self._condition:
            if self._closing:
                return LifecycleResult("closed", self.snapshot())
            return self._drain(deadline)

    def _drain(self, deadline: float) -> LifecycleResult:
        target = self._accepted
        self._flush_requested = True
        self._condition.notify_all()
        while self._completed < target:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return LifecycleResult("timeout", self.snapshot())
            self._condition.wait(remaining)
        failed = self._failures > self._reported_failures
        self._reported_failures = self._failures
        return LifecycleResult("failure" if failed else "success", self.snapshot())

    def shutdown_result(self, timeout_millis: int = 5000) -> LifecycleResult:
        return self.shutdown_until(time.monotonic() + _timeout_seconds(timeout_millis))

    def shutdown_until(self, deadline: float) -> LifecycleResult:
        """Share the caller's absolute deadline, including concurrent-close waits."""
        if not self._shutdown_lock.acquire(timeout=max(0, deadline - time.monotonic())):
            return LifecycleResult("timeout", self.snapshot())
        try:
            if self._shutdown_result is not None:
                return self._shutdown_result
            with self._condition:
                self._closing = True
                # Reserve part of the same budget for cooperative I/O cancellation/join.
                remaining = max(0, deadline - time.monotonic())
                drained = self._drain(deadline - min(0.02, remaining / 5))
                self._stop = True
                self._dropped = min(_MAX_COUNT, self._dropped + len(self._queue))
                self._queue.clear()
                self._condition.notify_all()
            try:
                self._exporter.shutdown()
            except Exception:
                with self._condition:
                    self._failures = min(_MAX_COUNT, self._failures + 1)
            self._worker.join(max(0, deadline - time.monotonic()))
            snap = self.snapshot()
            status = drained.status
            if snap.worker_alive or time.monotonic() > deadline:
                status = "timeout"
            elif snap.export_failures and status == "success":
                status = "failure"
            self._shutdown_result = LifecycleResult(status, snap)
            return self._shutdown_result
        finally:
            self._shutdown_lock.release()

    def force_flush(self, timeout_millis: int = 5000) -> bool:
        return self.flush_result(timeout_millis).status == "success"

    def shutdown(self) -> None:
        self.shutdown_result()
