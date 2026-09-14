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

# Config classes
# Advanced - circuit breaker for direct use
from friday_llm.capabilities import (  # noqa: E402
    CapabilityEntry,
    CapabilityState,
    ControlCapability,
    OperatorCapabilityDeclaration,
    ProviderCapabilities,
)
from friday_llm.circuit_breaker import CircuitBreaker  # noqa: E402
from friday_llm.config import CircuitBreakerConfig, ResilienceConfig  # noqa: E402

# Service classes
from friday_llm.embeddings import LiteLLMEmbeddingService  # noqa: E402

# Exception classes
from friday_llm.exceptions import (  # noqa: E402
    CapabilityConflictError,
    CircuitBreakerOpenError,
    CredentialResolutionError,
    LLMConfigurationError,
    LLMRetryExhaustedError,
    LLMServiceError,
    LLMTimeoutError,
    ModelLibraryError,
    ProviderOptionsError,
    TargetIdentityError,
    TranslationConflictError,
    UnsupportedControlError,
)
from friday_llm.generation import (  # noqa: E402
    GenerationConfig,
    GenerationOverrides,
    ReasoningConfig,
    ReasoningMode,
    SamplingConfig,
)

# LangFuse observability
from friday_llm.langfuse_integration import configure_langfuse  # noqa: E402
from friday_llm.lifecycle import close_litellm_async_clients  # noqa: E402
from friday_llm.model_library import (  # noqa: E402
    MODEL_LIBRARY_SCHEMA,
    ChatModelProfile,
    ChatServiceBinding,
    CircuitBreakerOverrides,
    CredentialDefinition,
    EmbeddingModelProfile,
    EmbeddingOptions,
    EmbeddingServiceBinding,
    EmbeddingServiceSpec,
    EndpointDefinition,
    LLMServiceSpec,
    ModelLibrary,
    ResilienceOverrides,
    resolve_chat_service,
    resolve_embedding_service,
)

# Pricing and cost calculation
from friday_llm.pricing import CostCalculator, PricingConfig  # noqa: E402
from friday_llm.protocols import TypedLLMClient  # noqa: E402
from friday_llm.provider_options import LMStudioQwenOptions  # noqa: E402
from friday_llm.requests import (  # noqa: E402
    ChatCompletionRequest,
    CompletionAssurance,
    CompletionToolCall,
    CompletionUsage,
    NamedToolChoice,
    NamedToolChoiceFunction,
    ToolChoice,
    TypedChatCompletionResponse,
)

# Service classes
from friday_llm.service import LiteLLMService  # noqa: E402
from friday_llm.streaming import (  # noqa: E402
    FinishEvent,
    ReasoningDeltaEvent,
    StreamErrorEvent,
    StreamEvent,
    TextDeltaEvent,
    ToolCallCompleteEvent,
    ToolCallDeltaEvent,
    UsageEvent,
)
from friday_llm.targets import (  # noqa: E402
    ExecutionTarget,
    ModelTarget,
    TransportTarget,
)

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
    "close_litellm_async_clients",
    # Config
    "ResilienceConfig",
    "CircuitBreakerConfig",
    "ReasoningMode",
    "ReasoningConfig",
    "SamplingConfig",
    "GenerationConfig",
    "GenerationOverrides",
    "TransportTarget",
    "ModelTarget",
    "ExecutionTarget",
    "MODEL_LIBRARY_SCHEMA",
    "CredentialDefinition",
    "EndpointDefinition",
    "ChatModelProfile",
    "EmbeddingModelProfile",
    "EmbeddingOptions",
    "ModelLibrary",
    "CircuitBreakerOverrides",
    "ResilienceOverrides",
    "ChatServiceBinding",
    "EmbeddingServiceBinding",
    "LLMServiceSpec",
    "EmbeddingServiceSpec",
    "resolve_chat_service",
    "resolve_embedding_service",
    "LMStudioQwenOptions",
    "CapabilityState",
    "ControlCapability",
    "CapabilityEntry",
    "ProviderCapabilities",
    "OperatorCapabilityDeclaration",
    "ChatCompletionRequest",
    "TypedChatCompletionResponse",
    "TypedLLMClient",
    "CompletionToolCall",
    "CompletionUsage",
    "CompletionAssurance",
    "ToolChoice",
    "NamedToolChoice",
    "NamedToolChoiceFunction",
    "StreamEvent",
    "TextDeltaEvent",
    "ReasoningDeltaEvent",
    "ToolCallDeltaEvent",
    "ToolCallCompleteEvent",
    "StreamErrorEvent",
    "UsageEvent",
    "FinishEvent",
    # Exceptions
    "LLMServiceError",
    "LLMTimeoutError",
    "LLMRetryExhaustedError",
    "CircuitBreakerOpenError",
    "LLMConfigurationError",
    "ModelLibraryError",
    "CredentialResolutionError",
    "UnsupportedControlError",
    "CapabilityConflictError",
    "ProviderOptionsError",
    "TranslationConflictError",
    "TargetIdentityError",
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
