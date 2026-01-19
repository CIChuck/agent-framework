"""
Graph Data Models.
Defines GraphNode, GraphEdge, and ProvenanceMetadata with strong typing.

Ref: Batch 1 Specification, Section 2.1
Ref: docs/build-plan/memory-lifecycle-staging-decay.md (lifecycle extensions)
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MemoryStage(str, Enum):
    """
    Memory lifecycle stages for graph nodes.

    Duplicated here to avoid circular imports with lifecycle module.
    The canonical definition is in friday_memory.lifecycle.stages.
    """

    EPISODIC = "episodic"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    DECAYED = "decayed"
    DELETED = "deleted"


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
    They support Hebbian learning through hit_count tracking and lifecycle
    management through decay scoring.
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

    # Hebbian learning fields
    hit_count: int = Field(
        default=0,
        ge=0,
        description="Access frequency for Hebbian learning reinforcement",
    )
    last_accessed: datetime = Field(default_factory=datetime.now)

    # Lifecycle management fields
    stage: MemoryStage = Field(
        default=MemoryStage.SHORT_TERM,
        description="Current lifecycle stage of the node",
    )
    decay_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Current decay score (1.0 = fresh, 0.0 = fully decayed)",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When the node was first created",
    )
    last_decay_at: datetime | None = Field(
        default=None,
        description="When decay was last calculated for this node",
    )
    promoted_at: datetime | None = Field(
        default=None,
        description="When promoted from SHORT_TERM to LONG_TERM",
    )
    decayed_at: datetime | None = Field(
        default=None,
        description="When demoted to DECAYED stage",
    )

    # Graph-vector linkage for coordinated decay
    source_memory_ids: list[str] = Field(
        default_factory=list,
        description="IDs of vector memories that contributed to this node's creation. "
        "Used for coordinated decay: if ALL source memories decay, this node decays too.",
    )

    # Optional embedding for semantic operations
    embedding: list[float] | None = Field(
        default=None,
        description="Optional embedding vector for semantic similarity operations",
    )

    def touch(self) -> None:
        """Increment hit_count and update last_accessed timestamp."""
        self.hit_count += 1
        self.last_accessed = datetime.now()

    def add_source_memory(self, memory_id: str) -> None:
        """Link this node to a source vector memory."""
        if memory_id not in self.source_memory_ids:
            self.source_memory_ids.append(memory_id)

    def mark_promoted(self) -> None:
        """Mark node as promoted to LONG_TERM stage."""
        self.stage = MemoryStage.LONG_TERM
        self.promoted_at = datetime.now()

    def mark_decayed(self) -> None:
        """Mark node as decayed."""
        self.stage = MemoryStage.DECAYED
        self.decayed_at = datetime.now()

    def reactivate(self) -> None:
        """Reactivate a decayed node back to LONG_TERM."""
        self.stage = MemoryStage.LONG_TERM
        self.decay_score = 0.5  # Reset to neutral
        self.decayed_at = None
        self.touch()


class GraphEdge(BaseModel):
    """
    Represents a relationship between two nodes in the knowledge graph.

    Edges connect nodes and carry semantic meaning about their relationship.
    Pre-computed embeddings enable fast path relevancy scoring during retrieval.
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

    # Pre-computed embedding for fast path relevancy scoring
    embedding: list[float] | None = Field(
        default=None,
        description="Pre-computed embedding of the relation for path relevancy scoring. "
        "Should be computed during consolidation to avoid retrieval-time latency.",
    )

    # Hebbian learning fields (for edge staleness tracking)
    hit_count: int = Field(
        default=0,
        ge=0,
        description="Access frequency for Hebbian learning reinforcement",
    )
    last_accessed: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When the edge was first created",
    )

    def touch(self) -> None:
        """Increment hit_count and update last_accessed timestamp."""
        self.hit_count += 1
        self.last_accessed = datetime.now()

    def get_relation_text(self) -> str:
        """
        Get the text representation of the edge for embedding.

        Returns a natural language description of the relationship
        suitable for embedding generation.
        """
        # Convert relation to natural language (e.g., "works_for" -> "works for")
        relation_text = self.relation.replace("_", " ")
        return f"{relation_text}"
