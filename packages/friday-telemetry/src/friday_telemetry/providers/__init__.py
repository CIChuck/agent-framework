"""
Telemetry Providers.

Concrete implementations of TelemetryInterface.
"""

from friday_telemetry.providers.composite import CompositeProvider
from friday_telemetry.providers.debug import DebugTelemetryRecorder
from friday_telemetry.providers.otel import OpenTelemetryProvider

__all__ = [
    "DebugTelemetryRecorder",
    "OpenTelemetryProvider",
    "CompositeProvider",
]
