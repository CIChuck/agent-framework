# mypy: ignore-errors
"""
Graph Data Models.
Defines GraphNode, GraphEdge, and ProvenanceMetadata with strong typing.

Ref: Batch 1 Specification, Section 2.1
Ref: docs/build-plan/memory-lifecycle-staging-decay.md (lifecycle extensions)
Ref: docs/build-plan/shared-memory-provenance-build-plan.md (provenance tracking)
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


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

    In multi-agent scenarios, author_id tracks which agent created the data,
    enabling provenance queries and trust verification.

    Attributes:
        source_id: UUID of the originating Turn or Document
        source_type: Origin type ('interaction', 'document', 'inference', 'agent', 'user')
        confidence: Confidence score (0.0 = uncertain, 1.0 = certain)
        created_at: Timestamp of creation
        author_id: Creator identifier (agent name or user ID)
        parent_ids: IDs of parent data this was derived from (for lineage chains)
    """  # noqa: E501

    source_id: str = Field(..., description="UUID of the originating Turn or Document")
    source_type: str = Field(
        ...,
        description="Origin type: 'interaction', 'document', 'inference', 'agent', 'user'",  # noqa: E501
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score from 0.0 to 1.0",
    )
    created_at: datetime = Field(default_factory=datetime.now)
    author_id: str | None = Field(
        default=None,
        description="Creator identifier: 'researcher', 'coder', 'user_123'",
    )
    parent_ids: list[str] = Field(
        default_factory=list,
        description="IDs of parent data this was derived from (for lineage chains)",
    )

    @field_validator("author_id")
    @classmethod
    def validate_author_id(cls, v: str | None) -> str | None:
        """Normalize author_id if provided."""
        if v is not None:
            v = v.strip().lower()
            if not v:
                raise ValueError("author_id cannot be empty string")
        return v

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v: str) -> str:
        """Normalize source_type."""
        return v.strip().lower()

    def with_parent(self, parent_id: str) -> "ProvenanceMetadata":
        """
        Create a new ProvenanceMetadata with an additional parent.

        Useful for tracking data lineage when deriving new data.

        Args:
            parent_id: ID of the parent data

        Returns:
            New ProvenanceMetadata with parent added
        """
        return ProvenanceMetadata(
            source_id=self.source_id,
            source_type=self.source_type,
            author_id=self.author_id,
            confidence=self.confidence,
            created_at=self.created_at,
            parent_ids=[*self.parent_ids, parent_id],
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "author_id": self.author_id,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "parent_ids": self.parent_ids,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProvenanceMetadata":
        """Deserialize from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        return cls(
            source_id=data["source_id"],
            source_type=data["source_type"],
            author_id=data.get("author_id"),
            confidence=data.get("confidence", 1.0),
            created_at=created_at or datetime.now(),
            parent_ids=data.get("parent_ids", []),
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
        "Used for coordinated decay: if ALL source memories decay, this node decays too.",  # noqa: E501
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
        description="Pre-computed embedding of the relation for path relevancy scoring. "  # noqa: E501
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

    def get_relation_text(
        self,
        source_label: str | None = None,
        target_label: str | None = None,
    ) -> str:
        """
        Get the text representation of the edge for embedding.

        Returns a natural language description of the relationship
        suitable for embedding generation. When source and target labels
        are provided, produces a richer triple like "Chuck married to Tara"
        instead of just "married to".

        Args:
            source_label: Optional label of the source node.
            target_label: Optional label of the target node.

        Returns:
            Natural language relation text for embedding.
        """
        relation_text = self.relation.replace("_", " ")
        if source_label and target_label:
            return f"{source_label} {relation_text} {target_label}"
        return relation_text


# =============================================================================
# Provenance Factory Functions
# =============================================================================


def create_agent_provenance(
    author_id: str,
    source_id: str = "manual",
    confidence: float = 1.0,
) -> ProvenanceMetadata:
    """
    Create provenance for agent-generated data.

    Args:
        author_id: Agent name (e.g., "researcher", "coder")
        source_id: ID of the source (e.g., turn_id)
        confidence: Confidence score (0.0-1.0)

    Returns:
        ProvenanceMetadata configured for agent authorship
    """
    return ProvenanceMetadata(
        source_id=source_id,
        source_type="agent",
        author_id=author_id,
        confidence=confidence,
    )


def create_user_provenance(
    user_id: str,
    source_id: str = "user_input",
) -> ProvenanceMetadata:
    """
    Create provenance for user-provided data.

    Args:
        user_id: User identifier
        source_id: ID of the source

    Returns:
        ProvenanceMetadata configured for user authorship
    """
    return ProvenanceMetadata(
        source_id=source_id,
        source_type="user",
        author_id=user_id,
        confidence=1.0,  # User input is always trusted
    )


def create_extraction_provenance(
    author_id: str,
    source_id: str,
    parent_ids: list[str] | None = None,
    confidence: float = 0.9,
) -> ProvenanceMetadata:
    """
    Create provenance for extracted/derived data.

    Args:
        author_id: Agent that performed extraction
        source_id: ID of the extraction source
        parent_ids: IDs of source data this was derived from
        confidence: Confidence score (typically lower for derived data)

    Returns:
        ProvenanceMetadata configured for extraction
    """
    return ProvenanceMetadata(
        source_id=source_id,
        source_type="extraction",
        author_id=author_id,
        confidence=confidence,
        parent_ids=parent_ids or [],
    )
