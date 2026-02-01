"""
Telemetry Interfaces and Debug Recorders.

This module re-exports from friday-telemetry for backwards compatibility.

Ref: Batch 0 Specification, Section 4.3
"""

# Re-export everything from friday-telemetry for backwards compatibility
from friday_telemetry import (
    DebugTelemetryRecorder,
    EventRecord,
    OpenTelemetryProvider,
    SpanRecord,
    TelemetryInterface,
)

__all__ = [
    "TelemetryInterface",
    "SpanRecord",
    "EventRecord",
    "DebugTelemetryRecorder",
    "OpenTelemetryProvider",
]
