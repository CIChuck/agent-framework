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
"""  # noqa: E501

# Configuration
# Security
from friday_core import security
from friday_core.config import FridayBaseSettings

# Exceptions
from friday_core.exceptions import (
    ContextOverflowError,
    FridayError,
    MemoryError,
    ProviderAPIError,
)

# Interfaces
from friday_core.interfaces import (
    AgentInterface,
    ArbitrationDecision,
    ArbitrationInterface,
    ChatCompletionResponse,
    ContextEngineeringInterface,
    EmbeddingModel,
    EpisodicStoreAdapter,
    GraphStoreAdapter,
    LabHarnessInterface,
    LLMClient,
    MemoryPromotionProposal,
    MultiAgentMemoryInterface,
    NamespacePolicyInterface,
    RegistryInterface,
    SchemaFormat,
    SharedWriteCapability,
    SystemRuntime,
    ToolAdapter,
    ToolCall,
    ToolDefinition,
    ToolRegistry,
    TranscriptBackedEpisodicStore,
    TranscriptStoreProtocol,
    VectorStoreAdapter,
)

# Logging
from friday_core.logging import LoggerProtocol, get_logger

# Memory Profiles
from friday_core.profiles import (
    MemoryProfile,
    create_graph_store,
    create_vector_store,
)

# Telemetry
from friday_core.telemetry import (
    DebugTelemetryRecorder,
    EventRecord,
    SpanRecord,
    TelemetryInterface,
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
    "NamespacePolicyInterface",
    "MultiAgentMemoryInterface",
    "ArbitrationInterface",
    "ArbitrationDecision",
    "SharedWriteCapability",
    "MemoryPromotionProposal",
    # Context Engineering
    "ContextEngineeringInterface",
    # LLM Interfaces
    "LLMClient",
    "EmbeddingModel",
    "ChatCompletionResponse",
    "ToolCall",
    # Tool Management
    "SchemaFormat",
    "ToolDefinition",
    "ToolAdapter",
    "ToolRegistry",
    # Runtime Interfaces
    "SystemRuntime",
    "AgentInterface",
    "RegistryInterface",
    "LabHarnessInterface",
    # Memory Profiles
    "MemoryProfile",
    "create_vector_store",
    "create_graph_store",
    # Transcript Integration
    "TranscriptBackedEpisodicStore",
    "TranscriptStoreProtocol",
    # Security
    "security",
]

__version__ = "0.1.0"
