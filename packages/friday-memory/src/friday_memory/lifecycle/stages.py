"""
Memory Lifecycle Stages and Metadata.

Defines the lifecycle stages for memory management and the metadata
model for tracking memory state through its lifecycle.

Ref: docs/build-plan/memory-lifecycle-staging-decay.md, Section "Core Components"
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class MemoryStage(str, Enum):
    """
    Memory lifecycle stages.

    Memories progress through these stages based on access patterns,
    age, and relevancy scoring:

    EPISODIC -> SHORT_TERM -> LONG_TERM -> DECAYED -> DELETED

    With potential reactivation path:
    DECAYED -> LONG_TERM (on access)
    """

    EPISODIC = "episodic"
    """Raw conversation data, not yet consolidated."""

    SHORT_TERM = "short_term"
    """Consolidated insights awaiting promotion evaluation."""

    LONG_TERM = "long_term"
    """Proven, frequently-accessed memories with high value."""

    DECAYED = "decayed"
    """Low-value memories excluded from retrieval but recoverable."""

    DELETED = "deleted"
    """Soft-deleted memories pending hard delete after retention period."""


class PromotionState(str, Enum):
    """
    Tracks promotion progress for crash recovery.

    When promoting a memory from short-term to long-term, we use this
    state to ensure atomicity across the add-then-delete operation.
    """

    NONE = "none"
    """No promotion in progress."""

    PENDING = "pending"
    """Added to long-term collection, not yet deleted from short-term."""

    COMPLETE = "complete"
    """Promotion fully completed."""


class MemoryLifecycleMetadata(BaseModel):
    """
    Lifecycle metadata attached to vector store documents and graph nodes.

    This model tracks the temporal state of a memory through its lifecycle,
    enabling decay calculations, promotion decisions, and access tracking.
    """

    stage: MemoryStage = Field(
        default=MemoryStage.SHORT_TERM,
        description="Current lifecycle stage of the memory",
    )
    decay_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Current decay score (1.0 = fresh, 0.0 = fully decayed)",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When the memory was first created",
    )
    last_accessed_at: datetime = Field(
        default_factory=datetime.now,
        description="Last time the memory was accessed/retrieved",
    )
    last_decay_at: datetime | None = Field(
        default=None,
        description="When decay was last calculated for this memory",
    )
    promoted_at: datetime | None = Field(
        default=None,
        description="When promoted from SHORT_TERM to LONG_TERM",
    )
    decayed_at: datetime | None = Field(
        default=None,
        description="When demoted to DECAYED stage",
    )
    access_count: int = Field(
        default=0,
        ge=0,
        description="Number of times this memory has been accessed",
    )
    promotion_state: PromotionState = Field(
        default=PromotionState.NONE,
        description="State of any in-progress promotion (for crash recovery)",
    )
    protected: bool = Field(
        default=False,
        description="If True, memory is exempt from decay and eligible for immediate promotion. "
        "Used for explicitly ingested documents that represent intentional knowledge preservation.",
    )

    def to_metadata_dict(self) -> dict[str, str | float | int | bool | None]:
        """
        Convert to a flat dictionary suitable for vector store metadata.

        ChromaDB and similar stores require flat key-value metadata,
        so we serialize datetime fields to ISO format strings.
        """
        return {
            "stage": self.stage.value,
            "decay_score": self.decay_score,
            "created_at": self.created_at.isoformat(),
            "last_accessed_at": self.last_accessed_at.isoformat(),
            "last_decay_at": self.last_decay_at.isoformat() if self.last_decay_at else None,
            "promoted_at": self.promoted_at.isoformat() if self.promoted_at else None,
            "decayed_at": self.decayed_at.isoformat() if self.decayed_at else None,
            "access_count": self.access_count,
            "promotion_state": self.promotion_state.value,
            "protected": self.protected,
        }

    @classmethod
    def from_metadata_dict(cls, data: dict) -> "MemoryLifecycleMetadata":
        """
        Reconstruct from a flat metadata dictionary.

        Handles ISO format datetime strings and enum value strings.
        """
        return cls(
            stage=MemoryStage(data.get("stage", MemoryStage.SHORT_TERM.value)),
            decay_score=float(data.get("decay_score", 1.0)),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else datetime.now()
            ),
            last_accessed_at=(
                datetime.fromisoformat(data["last_accessed_at"])
                if data.get("last_accessed_at")
                else datetime.now()
            ),
            last_decay_at=(
                datetime.fromisoformat(data["last_decay_at"])
                if data.get("last_decay_at")
                else None
            ),
            promoted_at=(
                datetime.fromisoformat(data["promoted_at"])
                if data.get("promoted_at")
                else None
            ),
            decayed_at=(
                datetime.fromisoformat(data["decayed_at"])
                if data.get("decayed_at")
                else None
            ),
            access_count=int(data.get("access_count", 0)),
            promotion_state=PromotionState(
                data.get("promotion_state", PromotionState.NONE.value)
            ),
            protected=bool(data.get("protected", False)),
        )

    def record_access(self) -> None:
        """Record an access event, updating timestamps and counts."""
        self.access_count += 1
        self.last_accessed_at = datetime.now()

    def mark_promoted(self) -> None:
        """Mark memory as promoted to LONG_TERM."""
        self.stage = MemoryStage.LONG_TERM
        self.promoted_at = datetime.now()
        self.promotion_state = PromotionState.COMPLETE

    def mark_decayed(self) -> None:
        """Mark memory as decayed."""
        self.stage = MemoryStage.DECAYED
        self.decayed_at = datetime.now()

    def mark_deleted(self) -> None:
        """Mark memory as soft-deleted."""
        self.stage = MemoryStage.DELETED

    def reactivate(self) -> None:
        """Reactivate a decayed memory back to LONG_TERM."""
        self.stage = MemoryStage.LONG_TERM
        self.decay_score = 0.5  # Reset to neutral
        self.decayed_at = None
        self.record_access()
