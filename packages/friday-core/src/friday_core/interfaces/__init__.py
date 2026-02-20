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

Runtime Interfaces (Phase 1):
- SystemRuntime: Headless runtime kernel contract
- AgentInterface: Agent execution contract
- RegistryInterface: Agent registry contract
- LabHarnessInterface: Integration test harness contract

Transcript Integration:
- TranscriptBackedEpisodicStore: Bridge adapter for persistent transcripts
"""

from friday_core.interfaces.agent import AgentInterface
from friday_core.interfaces.context import ContextEngineeringInterface
from friday_core.interfaces.lab import LabHarnessInterface
from friday_core.interfaces.llm import (
    ChatCompletionResponse,
    EmbeddingModel,
    LLMClient,
    ToolCall,
)
from friday_core.interfaces.memory import (
    ArbitrationDecision,
    ArbitrationInterface,
    EpisodicStoreAdapter,
    GraphStoreAdapter,
    MemoryPromotionProposal,
    MultiAgentMemoryInterface,
    NamespacePolicyInterface,
    SharedWriteCapability,
    VectorStoreAdapter,
)
from friday_core.interfaces.registry import RegistryInterface
from friday_core.interfaces.runtime import SystemRuntime
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
    # Transcript Integration
    "TranscriptBackedEpisodicStore",
    "TranscriptStoreProtocol",
]
