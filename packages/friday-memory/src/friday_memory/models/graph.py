"""
Graph Data Models.
Defines GraphNode, GraphEdge, and ProvenanceMetadata with strong typing.

Ref: Batch 1 Specification, Section 2.1
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProvenanceMetadata(BaseModel):
    """
    Tracks the lineage and origin of all stored data.

    Every GraphNode and GraphEdge MUST include provenance metadata
    to ensure explainability and auditability of the knowledge graph.
    """

    source_id: str = Field(..., description="UUID of the originating Turn or Document")
    source_type: str = Field(
        ...,
        description="Origin type: 'interaction', 'document', or 'inference'",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score from 0.0 to 1.0",
    )
    created_at: datetime = Field(default_factory=datetime.now)
    author_id: str | None = Field(
        default=None,
        description="Creator identifier: 'user_123' or 'agent_friday'",
    )


class GraphNode(BaseModel):
    """
    Represents an entity, concept, or event in the knowledge graph.

    Nodes are the primary knowledge units stored in the GraphStoreAdapter.
    They support Hebbian learning through hit_count tracking.
    """

    id: str = Field(..., description="Unique node identifier")
    type: str = Field(
        ...,
        description="Node classification: 'Entity', 'Concept', or 'Event'",
    )
    label: str = Field(..., description="Human-readable name for the node")
    properties: dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible attribute storage",
    )
    provenance: ProvenanceMetadata = Field(
        ...,
        description="Required lineage metadata - validates data origin",
    )
    hit_count: int = Field(
        default=0,
        ge=0,
        description="Access frequency for Hebbian learning reinforcement",
    )
    last_accessed: datetime = Field(default_factory=datetime.now)

    def touch(self) -> None:
        """Increment hit_count and update last_accessed timestamp."""
        self.hit_count += 1
        self.last_accessed = datetime.now()


class GraphEdge(BaseModel):
    """
    Represents a relationship between two nodes in the knowledge graph.

    Edges connect nodes and carry semantic meaning about their relationship.
    """

    source_id: str = Field(..., description="ID of the source node")
    target_id: str = Field(..., description="ID of the target node")
    relation: str = Field(
        ...,
        description="Relationship type/label (e.g., 'works_for', 'located_in')",
    )
    properties: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional edge attributes",
    )
    provenance: ProvenanceMetadata = Field(
        ...,
        description="Required lineage metadata - validates relationship origin",
    )
    weight: float = Field(
        default=1.0,
        ge=0.0,
        description="Edge weight for graph algorithms",
    )
