"""
Telemetry Data Models for LLM Operations.

This module re-exports from friday-telemetry for backwards compatibility.

Ref: https://opentelemetry.io/docs/specs/semconv/gen-ai/
"""

# Re-export from friday-telemetry for backwards compatibility
from friday_telemetry import (
    ConversationContext,
    CostEstimate,
    EmbeddingMetrics,
    ErrorCategory,
    GenAIOperationType,
    LLMCallMetrics,
    StreamingMetrics,
    TokenUsage,
)

__all__ = [
    "GenAIOperationType",
    "ErrorCategory",
    "TokenUsage",
    "CostEstimate",
    "StreamingMetrics",
    "ConversationContext",
    "LLMCallMetrics",
    "EmbeddingMetrics",
]
