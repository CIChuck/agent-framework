"""
Shared Protocol Definitions.

This module exports all abstract base classes (protocols) that define
the contracts for swappable components in the Friday Framework.

Storage Adapters (Batch 1):
- EpisodicStoreAdapter: Short-term conversation history
- VectorStoreAdapter: Semantic search storage
- GraphStoreAdapter: Relationship graph storage

Context Engineering (Batch 2a):
- ContextEngineeringInterface: Context strategy lifecycle

LLM Interfaces (Batch 3):
- LLMClient: Chat completion protocol
- EmbeddingModel: Text embedding protocol
- ChatCompletionResponse: Structured LLM response
- ToolCall: Tool call representation

Tool Management (Batch 3):
- ToolRegistry: Tool registration and resolution

Transcript Integration:
- TranscriptBackedEpisodicStore: Bridge adapter for persistent transcripts
"""

from friday_core.interfaces.context import ContextEngineeringInterface
from friday_core.interfaces.llm import (
    ChatCompletionResponse,
    EmbeddingModel,
    LLMClient,
    ToolCall,
)
from friday_core.interfaces.memory import (
    EpisodicStoreAdapter,
    GraphStoreAdapter,
    VectorStoreAdapter,
)
from friday_core.interfaces.tools import (
    SchemaFormat,
    ToolAdapter,
    ToolDefinition,
    ToolRegistry,
)
from friday_core.interfaces.transcript import (
    TranscriptBackedEpisodicStore,
    TranscriptStoreProtocol,
)

__all__ = [
    # Storage Adapters
    "EpisodicStoreAdapter",
    "VectorStoreAdapter",
    "GraphStoreAdapter",
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
    # Transcript Integration
    "TranscriptBackedEpisodicStore",
    "TranscriptStoreProtocol",
]
