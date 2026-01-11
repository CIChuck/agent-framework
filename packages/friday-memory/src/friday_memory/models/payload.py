"""
Context Retrieval Payload.
Defines ContextPayload DTO for passing data from Controller to Assembler.
Includes recent_memories (Transparency Loop).

Ref: Batch 2 Specification, Section 1.1
"""

from typing import Any

from pydantic import BaseModel, Field

from friday_memory.models.graph import GraphEdge, GraphNode
from friday_memory.models.session import InteractionTurn


class ContextPayload(BaseModel):
    """
    Standardized container for retrieved information.

    Aggregates data from all memory stores (Episodic, Vector, Graph)
    into a single payload for context assembly. Aligns with Batch 2a's
    Provenance requirements.
    """

    # --- Episodic Memory ---
    history: list[InteractionTurn] = Field(
        default_factory=list,
        description="The immediate narrative thread - recent conversation turns",
    )

    # --- Semantic Memory (Vector) ---
    passages: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Relevant text chunks from vector search with provenance",
    )

    # --- Associative Memory (Graph) ---
    entities: list[GraphNode] = Field(
        default_factory=list,
        description="Hydrated nodes representing entities/concepts",
    )
    facts: list[GraphEdge] = Field(
        default_factory=list,
        description="Relationships explaining why entities were retrieved",
    )

    # --- Transparency Layer (Anthropic Parity) ---
    recent_memories: list[str] = Field(
        default_factory=list,
        description=(
            "Relationship summaries for top entities. "
            "e.g., ['Chuck: creates→Friday, works_with→Python']"
        ),
    )

    # --- Dynamic Context (fetched on every recall) ---
    insights: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Recent insights from vector store, sorted by created_at desc. "
            "Most recent first for recency effect."
        ),
    )
    summaries: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Recent turn summaries from vector store, sorted by created_at desc. "
            "Most recent first for recency effect."
        ),
    )

    # --- Meta-Cognition ---
    debug_info: dict[str, Any] = Field(
        default_factory=dict,
        description="Debug telemetry: {'vector_latency': 0.1, 'graph_nodes_touched': 15}",
    )

    def total_items(self) -> int:
        """Return total number of items in the payload."""
        return (
            len(self.history)
            + len(self.passages)
            + len(self.entities)
            + len(self.facts)
            + len(self.insights)
            + len(self.summaries)
        )

    def is_empty(self) -> bool:
        """Check if payload contains any data."""
        return self.total_items() == 0
