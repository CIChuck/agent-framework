# mypy: ignore-errors
"""
LLM Telemetry Helper.

This module re-exports from friday-telemetry for backwards compatibility.

Ref: https://opentelemetry.io/docs/specs/semconv/gen-ai/
"""

# Re-export from friday-telemetry for backwards compatibility
from friday_telemetry import (
    CompletionTracker,
    EmbeddingTracker,
    LLMTelemetryHelper,
    OTelAttributes,
    StreamingTracker,
    classify_error,
)

__all__ = [
    "OTelAttributes",
    "classify_error",
    "StreamingTracker",
    "CompletionTracker",
    "EmbeddingTracker",
    "LLMTelemetryHelper",
]
