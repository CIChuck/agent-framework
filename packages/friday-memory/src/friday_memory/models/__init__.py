"""
Data Transfer Objects (DTOs) for the Memory subsystem.

This module exports all Pydantic models used across the friday-memory package:

Graph Models (Batch 1):
- ProvenanceMetadata: Lineage tracking for all data
- GraphNode: Entity/concept representation with lifecycle fields
- GraphEdge: Relationship between nodes with embedding support
- MemoryStage: Lifecycle stage enum

Session Models (Batch 2a):
- InteractionTurn: Single conversation turn with tool support
- ToolCall, ToolResult: Tool execution records
- SessionState: Session continuity and scoped variables
- ConsolidationReport: Consolidation cycle telemetry

Payload Models (Batch 2):
- ContextPayload: Aggregated retrieval results

Vector Metadata Models (Lifecycle):
- VectorDocumentMetadata: TypedDict for vector store metadata
- InitialVectorMetadata: Pydantic model for new memory creation
- create_initial_metadata: Helper to create initial metadata
"""

from friday_memory.models.graph import (
    GraphEdge,
    GraphNode,
    MemoryStage,
    ProvenanceMetadata,
)
from friday_memory.models.llm_responses import (
    ConflictResolutionResponse,
    SummarizationResponse,
)
from friday_memory.models.payload import ContextPayload
from friday_memory.models.session import (
    ConsolidationReport,
    InteractionTurn,
    SessionState,
    ToolCall,
    ToolResult,
)
from friday_memory.models.vector_metadata import (
    InitialVectorMetadata,
    VectorDocumentMetadata,
    create_initial_metadata,
    create_longterm_metadata,
)

__all__ = [
    # Graph models
    "ProvenanceMetadata",
    "GraphNode",
    "GraphEdge",
    "MemoryStage",
    # Session models
    "ToolCall",
    "ToolResult",
    "InteractionTurn",
    "SessionState",
    "ConsolidationReport",
    # Payload models
    "ContextPayload",
    # LLM response models
    "SummarizationResponse",
    "ConflictResolutionResponse",
    # Vector metadata models
    "VectorDocumentMetadata",
    "InitialVectorMetadata",
    "create_initial_metadata",
    "create_longterm_metadata",
]
