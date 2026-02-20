"""
Models for additive multi-agent memory mode.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

PRIVATE_VISIBILITY = "private"
SHARED_VISIBILITY = "shared"
SHARED_NAMESPACE = "shared"


class PromotionJournalState(str, Enum):
    PENDING = "pending"
    GRAPH_WRITTEN = "graph_written"
    VECTOR_WRITTEN = "vector_written"
    COMMITTED = "committed"
    FAILED = "failed"
    COMPENSATED = "compensated"


class SharedPromotionProposal(BaseModel):
    proposal_id: str
    session_id: str
    namespace: str
    author_id: str
    fact: str
    metadata: dict = Field(default_factory=dict)
    correlation_id: str | None = None
    transcript_entry_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PromotionJournalEntry(BaseModel):
    proposal_id: str
    state: PromotionJournalState
    session_id: str
    namespace: str
    author_id: str
    correlation_id: str | None = None
    transcript_entry_id: str | None = None
    promotion_id: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PromotionJournalEvent(BaseModel):
    """Immutable replay event for promotion timeline forensics."""

    proposal_id: str
    state: PromotionJournalState
    session_id: str
    namespace: str
    author_id: str
    correlation_id: str | None = None
    transcript_entry_id: str | None = None
    promotion_id: str | None = None
    error: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
