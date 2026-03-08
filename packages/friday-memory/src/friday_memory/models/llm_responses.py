# mypy: ignore-errors
"""
LLM Response Models for Memory Consolidation.

Pydantic models for structured LLM output during memory operations.

Ref: Batch 2a Specification, Section 4
"""

from pydantic import BaseModel


class SummarizationResponse(BaseModel):
    """
    Structured response from LLM summarization.

    Used by MemoryConsolidator to compress conversation history.
    """

    summary: str
    key_topics: list[str]
    decisions: list[str]
    tokens_original: int
    tokens_compressed: int


class ConflictResolutionResponse(BaseModel):
    """
    Structured response from LLM conflict resolution.

    Used by MemoryConsolidator to resolve contradictory facts.
    """

    has_conflict: bool
    resolution: str
    current_value: str
    historical_note: str | None = None
