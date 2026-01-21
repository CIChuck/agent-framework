"""
Context Retrieval Payload.
Defines ContextPayload DTO for passing data from Controller to Assembler.
Includes recent_memories (Transparency Loop).

Ref: Batch 2 Specification, Section 1.1
"""

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from friday_memory.models.graph import GraphEdge, GraphNode
from friday_memory.models.session import InteractionTurn

if TYPE_CHECKING:
    from friday_memory.models.tools import ToolRecommendation


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

    # --- Cross-Session History ---
    prior_history: list[InteractionTurn] = Field(
        default_factory=list,
        description=(
            "Conversation turns from previous sessions for continuity. "
            "Merged with history during prompt formatting, ordered chronologically."
        ),
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
    key_facts: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Key facts from vector store insights, sorted by created_at desc. "
            "Each dict contains 'text' and 'metadata' (with created_at timestamp)."
        ),
    )

    # --- Meta-Cognition ---
    debug_info: dict[str, Any] = Field(
        default_factory=dict,
        description="Debug telemetry: {'vector_latency': 0.1, 'graph_nodes_touched': 15}",
    )

    # --- Tool Context ---
    # These fields support intelligent tool selection and context integration.
    # Tool schemas are passed to the LLM API's tools parameter, while
    # recommendations appear in supporting context for the recency effect.
    tool_schemas: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Filtered tool schemas for API tools parameter. "
            "Contains only actively selected tools, not all available tools."
        ),
    )
    recommended_tools: list[Any] = Field(  # list[ToolRecommendation] at runtime
        default_factory=list,
        description=(
            "Tool recommendations with reasons for supporting context. "
            "Placed near user query for recency effect."
        ),
    )
    tool_usage_hints: list[str] = Field(
        default_factory=list,
        description=(
            "Natural language hints about tool usage patterns. "
            "E.g., 'For file operations, read_file is faster than cat for large files.'"
        ),
    )

    def total_items(self) -> int:
        """Return total number of items in the payload."""
        return (
            len(self.history)
            + len(self.prior_history)
            + len(self.passages)
            + len(self.entities)
            + len(self.facts)
            + len(self.insights)
            + len(self.summaries)
            + len(self.key_facts)
            + len(self.tool_schemas)
            + len(self.recommended_tools)
        )

    def is_empty(self) -> bool:
        """Check if payload contains any data."""
        return self.total_items() == 0
