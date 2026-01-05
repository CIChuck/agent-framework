"""
Friday LLM - Inference Layer.

Provides concrete implementations of LLM interfaces using LiteLLM.
Supports multiple providers (OpenAI, Anthropic, Ollama, etc.) through
a unified API.

Components:
- LiteLLMService: Chat completion with tool calling support
- LiteLLMEmbeddingService: Text embeddings for vector search
- ResilienceConfig: Configuration for retry, timeout, circuit breaker

Ref: Batch 3 Specification, Section 3
"""

import litellm

# Suppress LiteLLM's verbose debug output (e.g., "Give Feedback" messages)
# Users can re-enable if needed via litellm.suppress_debug_info = False
litellm.suppress_debug_info = True

# Config classes
# Advanced - circuit breaker for direct use
from friday_llm.circuit_breaker import CircuitBreaker
from friday_llm.config import CircuitBreakerConfig, ResilienceConfig

# Service classes
from friday_llm.embeddings import LiteLLMEmbeddingService

# Exception classes
from friday_llm.exceptions import (
    CircuitBreakerOpenError,
    LLMRetryExhaustedError,
    LLMServiceError,
    LLMTimeoutError,
)

# Pricing and cost calculation
from friday_llm.pricing import CostCalculator, PricingConfig

# Service classes
from friday_llm.service import LiteLLMService

# Telemetry
from friday_llm.telemetry_helper import LLMTelemetryHelper
from friday_llm.telemetry_models import (
    ConversationContext,
    CostEstimate,
    EmbeddingMetrics,
    LLMCallMetrics,
    StreamingMetrics,
    TokenUsage,
)

__all__ = [
    # Services
    "LiteLLMService",
    "LiteLLMEmbeddingService",
    # Config
    "ResilienceConfig",
    "CircuitBreakerConfig",
    # Exceptions
    "LLMServiceError",
    "LLMTimeoutError",
    "LLMRetryExhaustedError",
    "CircuitBreakerOpenError",
    # Pricing
    "PricingConfig",
    "CostCalculator",
    # Telemetry
    "LLMTelemetryHelper",
    "ConversationContext",
    "LLMCallMetrics",
    "EmbeddingMetrics",
    "StreamingMetrics",
    "TokenUsage",
    "CostEstimate",
    # Advanced
    "CircuitBreaker",
]
