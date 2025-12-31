"""
Friday Memory Package.
Contains the 'Brain' logic: MemoryController, ContextEngine, and DB Adapters.

Ref: Batch 1 & 2 Specifications

This package provides:
- Models: Data structures for memory operations (Pydantic models)
- Adapters: Concrete implementations of storage interfaces
- Controller: Unified facade for memory operations
- Context: Context engineering components
- Ingestion: Document processing pipeline
"""

# Models
from friday_memory.models import (
    ConsolidationReport,
    ContextPayload,
    GraphEdge,
    GraphNode,
    InteractionTurn,
    ProvenanceMetadata,
    SessionState,
    ToolCall,
    ToolResult,
)

# Adapters
from friday_memory.adapters import (
    ChromaVectorStore,
    ElementXGraphStore,
    InMemoryEpisodicStore,
)

# Controller
from friday_memory.controller import MemoryController

# Context Engineering
from friday_memory.context import (
    ContextAssembler,
    MemoryConsolidator,
    MemoryExtractor,
    PromptArchitect,
)

# Ingestion
from friday_memory.ingestion import DocumentIngestionPipeline

__all__ = [
    # Models
    "ProvenanceMetadata",
    "GraphNode",
    "GraphEdge",
    "ToolCall",
    "ToolResult",
    "InteractionTurn",
    "SessionState",
    "ConsolidationReport",
    "ContextPayload",
    # Adapters
    "InMemoryEpisodicStore",
    "ElementXGraphStore",
    "ChromaVectorStore",
    # Controller
    "MemoryController",
    # Context Engineering
    "PromptArchitect",
    "ContextAssembler",
    "MemoryExtractor",
    "MemoryConsolidator",
    # Ingestion
    "DocumentIngestionPipeline",
]
