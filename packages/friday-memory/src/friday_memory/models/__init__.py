"""
Data Transfer Objects (DTOs) for the Memory subsystem.

This module exports all Pydantic models used across the friday-memory package:

Graph Models (Batch 1):
- ProvenanceMetadata: Lineage tracking for all data
- GraphNode: Entity/concept representation
- GraphEdge: Relationship between nodes

Session Models (Batch 2a):
- InteractionTurn: Single conversation turn with tool support
- ToolCall, ToolResult: Tool execution records
- SessionState: Session continuity and scoped variables
- ConsolidationReport: Consolidation cycle telemetry

Payload Models (Batch 2):
- ContextPayload: Aggregated retrieval results
"""

from friday_memory.models.graph import GraphEdge, GraphNode, ProvenanceMetadata
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

__all__ = [
    # Graph models
    "ProvenanceMetadata",
    "GraphNode",
    "GraphEdge",
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
]
