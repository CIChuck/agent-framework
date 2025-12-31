"""
Friday Core Package
Foundation interfaces and shared utilities.

This package provides the foundational "glue" for the Friday Framework:
- Configuration management (FridayBaseSettings)
- Exception hierarchy (FridayError and subclasses)
- Logging utilities (get_logger, LoggerProtocol)
- Telemetry interfaces (TelemetryInterface, DebugTelemetryRecorder)
- Storage adapter protocols (EpisodicStoreAdapter, VectorStoreAdapter, GraphStoreAdapter)
- Context engineering protocol (ContextEngineeringInterface)

Ref: Batch 0 Specification
"""

# Configuration
from friday_core.config import FridayBaseSettings

# Exceptions
from friday_core.exceptions import (
    ContextOverflowError,
    FridayError,
    MemoryError,
    ProviderAPIError,
)

# Logging
from friday_core.logging import LoggerProtocol, get_logger

# Telemetry
from friday_core.telemetry import (
    DebugTelemetryRecorder,
    EventRecord,
    SpanRecord,
    TelemetryInterface,
)

# Interfaces
from friday_core.interfaces import (
    ContextEngineeringInterface,
    EpisodicStoreAdapter,
    GraphStoreAdapter,
    VectorStoreAdapter,
)

__all__ = [
    # Configuration
    "FridayBaseSettings",
    # Exceptions
    "FridayError",
    "MemoryError",
    "ContextOverflowError",
    "ProviderAPIError",
    # Logging
    "LoggerProtocol",
    "get_logger",
    # Telemetry
    "TelemetryInterface",
    "DebugTelemetryRecorder",
    "SpanRecord",
    "EventRecord",
    # Storage Adapters
    "EpisodicStoreAdapter",
    "VectorStoreAdapter",
    "GraphStoreAdapter",
    # Context Engineering
    "ContextEngineeringInterface",
]

__version__ = "0.1.0"
