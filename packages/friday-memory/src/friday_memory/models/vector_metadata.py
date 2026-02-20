"""
Vector Store Metadata Schema.

Defines the metadata fields used for vector store documents,
including lifecycle management fields.

Ref: docs/build-plan/memory-lifecycle-staging-decay.md
"""

from datetime import datetime
from typing import Any, TypedDict

from pydantic import BaseModel, Field


class VectorDocumentMetadata(TypedDict, total=False):
    """
    TypedDict defining the expected metadata fields for vector documents.

    This schema documents what fields are expected in vector store metadata.
    ChromaDB stores these as flat key-value pairs.
    """

    # Existing consolidation fields
    consolidated: bool
    source_type: str  # 'consolidation', 'document', 'inference'
    confidence: float
    type: str  # 'insight', 'summary', 'meta_insight'

    # Lifecycle management fields (NEW)
    stage: str  # MemoryStage value: 'episodic', 'short_term', 'long_term', 'decayed', 'deleted'  # noqa: E501
    decay_score: float  # 0.0 to 1.0
    created_at: str  # ISO datetime
    created_at_ts: int  # Unix epoch seconds — used for ChromaDB date-range filtering
    last_accessed_at: str  # ISO datetime
    last_decay_at: str | None  # ISO datetime or None
    promoted_at: str | None  # ISO datetime or None
    decayed_at: str | None  # ISO datetime or None
    access_count: int
    promotion_state: str  # PromotionState value: 'none', 'pending', 'complete'

    # Long-term memory fields
    hit_count: int  # Number of times included in context (for long-term memories)
    retrieval_factor: float  # Pre-computed relevancy factor for optimization


class InitialVectorMetadata(BaseModel):
    """
    Initial metadata for a newly consolidated memory.

    Use this model when creating new memories to ensure all lifecycle
    fields are properly initialized.
    """

    # Required consolidation fields
    consolidated: bool = True
    source_type: str = Field(default="consolidation")
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    type: str = Field(default="insight")

    # Lifecycle fields (initialized for SHORT_TERM stage)
    stage: str = Field(default="short_term")
    decay_score: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)
    created_at_ts: int = Field(
        default=0,
        description="Unix epoch seconds for ChromaDB date-range filtering",
    )
    last_accessed_at: datetime = Field(default_factory=datetime.now)
    last_decay_at: datetime | None = None
    promoted_at: datetime | None = None
    decayed_at: datetime | None = None
    access_count: int = 0
    promotion_state: str = Field(default="none")

    # Long-term fields (initialized to zero)
    hit_count: int = 0
    retrieval_factor: float = Field(default=1.0, ge=0.0)

    def to_chromadb_metadata(self) -> dict[str, Any]:
        """
        Convert to a flat dict suitable for ChromaDB metadata.

        Datetime fields are converted to ISO format strings.
        None values are excluded (ChromaDB doesn't support None).
        """
        metadata: dict[str, Any] = {
            "consolidated": self.consolidated,
            "source_type": self.source_type,
            "confidence": self.confidence,
            "type": self.type,
            "stage": self.stage,
            "decay_score": self.decay_score,
            "created_at": self.created_at.isoformat(),
            "created_at_ts": self.created_at_ts or int(self.created_at.timestamp()),
            "last_accessed_at": self.last_accessed_at.isoformat(),
            "access_count": self.access_count,
            "promotion_state": self.promotion_state,
            "hit_count": self.hit_count,
            "retrieval_factor": self.retrieval_factor,
        }

        # Add optional datetime fields only if set
        if self.last_decay_at:
            metadata["last_decay_at"] = self.last_decay_at.isoformat()
        if self.promoted_at:
            metadata["promoted_at"] = self.promoted_at.isoformat()
        if self.decayed_at:
            metadata["decayed_at"] = self.decayed_at.isoformat()

        return metadata


def create_initial_metadata(
    source_type: str = "consolidation",
    confidence: float = 0.7,
    doc_type: str = "insight",
) -> dict[str, Any]:
    """
    Create initial metadata for a new memory in SHORT_TERM stage.

    Args:
        source_type: Origin of the memory ('consolidation', 'document', 'inference')
        confidence: Extraction confidence score (0.0-1.0)
        doc_type: Document type ('insight', 'summary', 'meta_insight')

    Returns:
        Flat dict suitable for ChromaDB metadata
    """
    metadata = InitialVectorMetadata(
        source_type=source_type,
        confidence=confidence,
        type=doc_type,
    )
    return metadata.to_chromadb_metadata()


def create_longterm_metadata(
    existing_metadata: dict[str, Any],
    promoted_at: datetime | None = None,
) -> dict[str, Any]:
    """
    Create metadata for a memory being promoted to LONG_TERM.

    Updates the stage and sets promotion timestamp.

    Args:
        existing_metadata: Current metadata dict
        promoted_at: Promotion timestamp (defaults to now)

    Returns:
        Updated metadata dict for LONG_TERM stage
    """
    now = promoted_at or datetime.now()
    updated = existing_metadata.copy()
    updated.update(
        {
            "stage": "long_term",
            "promoted_at": now.isoformat(),
            "promotion_state": "complete",
            "hit_count": 0,  # Reset for long-term tracking
        }
    )
    return updated
