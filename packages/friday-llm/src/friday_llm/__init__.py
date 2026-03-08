# mypy: ignore-errors
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

# Allow LiteLLM to normalize parameters for provider-specific quirks.
# Notably, Moonshot thinking models require reasoning_content in assistant
# tool-call messages; when it's missing LiteLLM drops the thinking param
# for that turn instead of letting the API reject the request.
litellm.modify_params = True

# Silently drop parameters that a provider doesn't support (e.g.
# 'thinking' on providers that lack reasoning mode) instead of
# raising UnsupportedParamsError.
litellm.drop_params = True

# Config classes
# Advanced - circuit breaker for direct use
from friday_llm.circuit_breaker import CircuitBreaker  # noqa: E402
from friday_llm.config import CircuitBreakerConfig, ResilienceConfig  # noqa: E402

# Service classes
from friday_llm.embeddings import LiteLLMEmbeddingService  # noqa: E402

# Exception classes
from friday_llm.exceptions import (  # noqa: E402
    CircuitBreakerOpenError,
    LLMRetryExhaustedError,
    LLMServiceError,
    LLMTimeoutError,
)

# LangFuse observability
from friday_llm.langfuse_integration import configure_langfuse  # noqa: E402

# Pricing and cost calculation
from friday_llm.pricing import CostCalculator, PricingConfig  # noqa: E402

# Service classes
from friday_llm.service import LiteLLMService  # noqa: E402

# Telemetry
from friday_llm.telemetry_helper import LLMTelemetryHelper  # noqa: E402
from friday_llm.telemetry_models import (  # noqa: E402
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
    # Observability
    "configure_langfuse",
]
