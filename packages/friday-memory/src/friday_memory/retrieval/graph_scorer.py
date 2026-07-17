# mypy: ignore-errors
"""
Graph Path Relevancy Scorer.

Scores node-edge-node paths for relevancy to the current query,
enabling selective inclusion of graph context in the LLM prompt.

The problem: Graph traversal returns ALL neighbors regardless of relevancy.
Query: "How do I configure logging?"
→ Graph returns: logging → [Python, debugging, files, stdout, JSON, levels, handlers, ...]
→ Without filtering, ALL go into context wasting tokens on irrelevant relationships.

The solution: Score each path and only include paths above the relevancy threshold.

Ref: docs/archive/build-plans/completed/friday-core-legacy/memory-lifecycle-staging-decay.md, Section "Graph Path Relevancy Scoring"
"""  # noqa: E501

from __future__ import annotations

import math
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from friday_memory.models import GraphEdge, GraphNode


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Returns a value between -1 and 1, where 1 means identical direction.
    """
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2, strict=False))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


class GraphPathScorerConfig(BaseModel):
    """Configuration for graph path scoring."""

    edge_weight: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="Weight for edge relevancy in combined score",
    )
    target_weight: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Weight for target node relevancy in combined score",
    )
    hit_count_boost: float = Field(
        default=0.05,
        ge=0.0,
        le=0.5,
        description="Logarithmic boost factor for hit_count",
    )
    inclusion_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum score for path inclusion",
    )


class ScoredPath:
    """A graph path with its relevancy score."""

    def __init__(
        self,
        source_node: GraphNode,
        edge: GraphEdge,
        target_node: GraphNode,
        score: float,
        edge_similarity: float,
        target_similarity: float,
    ) -> None:
        self.source_node = source_node
        self.edge = edge
        self.target_node = target_node
        self.score = score
        self.edge_similarity = edge_similarity
        self.target_similarity = target_similarity

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source_id": self.source_node.id,
            "source_label": self.source_node.label,
            "relation": self.edge.relation,
            "target_id": self.target_node.id,
            "target_label": self.target_node.label,
            "score": self.score,
            "edge_similarity": self.edge_similarity,
            "target_similarity": self.target_similarity,
        }


class GraphPathScorer:
    """
    Score node-edge-node paths for relevancy to current query.

    Only include paths where the combined relevancy exceeds threshold.
    This prevents wasting context tokens on irrelevant graph relationships.

    The scoring formula:
    1. Edge relevancy: cosine_similarity(edge_embedding, query_embedding)
    2. Target relevancy: cosine_similarity(target_embedding, query_embedding)
    3. Combined: (edge_similarity * edge_weight) + (target_similarity * target_weight)
    4. Usage boost: combined * (1 + hit_count_boost * log(1 + min_hits))

    Example usage:
        scorer = GraphPathScorer()

        # Score a single path
        score = await scorer.score_path(
            source_node=source,
            edge=edge,
            target_node=target,
            query_embedding=query_emb,
            embedding_fn=embeddings.embed_query,
        )

        # Filter multiple paths
        relevant_paths = await scorer.filter_paths(
            paths=all_paths,
            query_embedding=query_emb,
            embedding_fn=embeddings.embed_query,
        )
    """

    def __init__(self, config: GraphPathScorerConfig | None = None) -> None:
        """
        Initialize the graph path scorer.

        Args:
            config: Scorer configuration (uses defaults if None)
        """
        self._config = config or GraphPathScorerConfig()

    @property
    def edge_weight(self) -> float:
        """Weight for edge relevancy."""
        return self._config.edge_weight

    @property
    def target_weight(self) -> float:
        """Weight for target node relevancy."""
        return self._config.target_weight

    @property
    def hit_count_boost(self) -> float:
        """Logarithmic boost factor."""
        return self._config.hit_count_boost

    @property
    def inclusion_threshold(self) -> float:
        """Minimum score for inclusion."""
        return self._config.inclusion_threshold

    def _get_edge_text(
        self,
        source_node: GraphNode,
        edge: GraphEdge,
        target_node: GraphNode,
    ) -> str:
        """
        Generate text representation of an edge for embedding.

        Converts the relationship into a natural language phrase.
        """
        # Convert relation to natural language (e.g., "works_for" -> "works for")
        relation_text = edge.relation.replace("_", " ")
        return f"{source_node.label} {relation_text} {target_node.label}"

    def _get_target_text(self, target_node: GraphNode) -> str:
        """
        Generate text representation of target node for embedding.

        Uses description if available, otherwise uses label.
        """
        # Check for description in properties
        description = target_node.properties.get("description", "")
        if description:
            return f"{target_node.label}: {description}"
        return target_node.label

    def calculate_usage_boost(
        self,
        source_hit_count: int,
        target_hit_count: int,
    ) -> float:
        """
        Calculate usage boost factor from hit counts.

        Uses the minimum of source and target hit counts to represent
        the "weakest link" in the path.

        Args:
            source_hit_count: Hit count of source node
            target_hit_count: Hit count of target node

        Returns:
            Boost factor >= 1.0
        """
        min_hits = min(source_hit_count, target_hit_count)
        return 1.0 + (self._config.hit_count_boost * math.log(1 + min_hits))

    async def score_path(
        self,
        source_node: GraphNode,
        edge: GraphEdge,
        target_node: GraphNode,
        query_embedding: list[float],
        embedding_fn: Callable[[str], Awaitable[list[float]]] | None = None,
    ) -> ScoredPath:
        """
        Score a graph path for relevancy to the query.

        Uses pre-computed embeddings when available, falling back to
        computing embeddings on-demand (with latency penalty).

        Args:
            source_node: Starting node (matched from query)
            edge: Relationship connecting nodes
            target_node: Connected node to potentially include
            query_embedding: Embedding of current query
            embedding_fn: Async function to compute embeddings (for fallback)

        Returns:
            ScoredPath with relevancy score and component similarities
        """
        # Get edge embedding (prefer pre-computed)
        edge_embedding = edge.embedding
        if edge_embedding is None and embedding_fn is not None:
            edge_text = self._get_edge_text(source_node, edge, target_node)
            edge_embedding = await embedding_fn(edge_text)

        # Get target node embedding (prefer pre-computed)
        target_embedding = target_node.embedding
        if target_embedding is None and embedding_fn is not None:
            target_text = self._get_target_text(target_node)
            target_embedding = await embedding_fn(target_text)

        # Calculate similarities
        edge_similarity = 0.0
        if edge_embedding:
            edge_similarity = cosine_similarity(edge_embedding, query_embedding)

        target_similarity = 0.0
        if target_embedding:
            target_similarity = cosine_similarity(target_embedding, query_embedding)

        # Weighted combination
        relevancy = (
            edge_similarity * self._config.edge_weight
            + target_similarity * self._config.target_weight
        )

        # Apply usage boost
        usage_factor = self.calculate_usage_boost(
            source_node.hit_count,
            target_node.hit_count,
        )
        final_score = relevancy * usage_factor

        return ScoredPath(
            source_node=source_node,
            edge=edge,
            target_node=target_node,
            score=final_score,
            edge_similarity=edge_similarity,
            target_similarity=target_similarity,
        )

    async def filter_paths(
        self,
        paths: list[tuple[GraphNode, GraphEdge, GraphNode]],
        query_embedding: list[float],
        embedding_fn: Callable[[str], Awaitable[list[float]]] | None = None,
        max_paths: int | None = None,
    ) -> list[ScoredPath]:
        """
        Filter and score paths, returning only relevant ones.

        Args:
            paths: List of (source_node, edge, target_node) tuples
            query_embedding: Embedding of current query
            embedding_fn: Async function to compute embeddings (for fallback)
            max_paths: Maximum number of paths to return (None = no limit)

        Returns:
            List of ScoredPath objects above threshold, sorted by score descending
        """
        scored_paths: list[ScoredPath] = []

        for source, edge, target in paths:
            scored_path = await self.score_path(
                source_node=source,
                edge=edge,
                target_node=target,
                query_embedding=query_embedding,
                embedding_fn=embedding_fn,
            )

            if scored_path.score >= self._config.inclusion_threshold:
                scored_paths.append(scored_path)

        # Sort by score descending
        scored_paths.sort(key=lambda x: x.score, reverse=True)

        # Apply max_paths limit if specified
        if max_paths is not None:
            scored_paths = scored_paths[:max_paths]

        return scored_paths

    def score_path_sync(
        self,
        source_node: GraphNode,
        edge: GraphEdge,
        target_node: GraphNode,
        query_embedding: list[float],
    ) -> ScoredPath:
        """
        Score a graph path synchronously (uses only pre-computed embeddings).

        This is the fast path for retrieval when embeddings are pre-computed.
        If embeddings are missing, the similarity component will be 0.

        Args:
            source_node: Starting node (matched from query)
            edge: Relationship connecting nodes (should have pre-computed embedding)
            target_node: Connected node (should have pre-computed embedding)
            query_embedding: Embedding of current query

        Returns:
            ScoredPath with relevancy score
        """
        # Get pre-computed embeddings (or empty)
        edge_embedding = edge.embedding or []
        target_embedding = target_node.embedding or []

        # Calculate similarities
        edge_similarity = cosine_similarity(edge_embedding, query_embedding)
        target_similarity = cosine_similarity(target_embedding, query_embedding)

        # Weighted combination
        relevancy = (
            edge_similarity * self._config.edge_weight
            + target_similarity * self._config.target_weight
        )

        # Apply usage boost
        usage_factor = self.calculate_usage_boost(
            source_node.hit_count,
            target_node.hit_count,
        )
        final_score = relevancy * usage_factor

        return ScoredPath(
            source_node=source_node,
            edge=edge,
            target_node=target_node,
            score=final_score,
            edge_similarity=edge_similarity,
            target_similarity=target_similarity,
        )

    def filter_paths_sync(
        self,
        paths: list[tuple[GraphNode, GraphEdge, GraphNode]],
        query_embedding: list[float],
        max_paths: int | None = None,
    ) -> list[ScoredPath]:
        """
        Filter paths synchronously (uses only pre-computed embeddings).

        This is the fast path for retrieval. Use this when all edges
        have pre-computed embeddings from the consolidation phase.

        Args:
            paths: List of (source_node, edge, target_node) tuples
            query_embedding: Embedding of current query
            max_paths: Maximum number of paths to return

        Returns:
            List of ScoredPath objects above threshold, sorted by score descending
        """
        scored_paths: list[ScoredPath] = []

        for source, edge, target in paths:
            scored_path = self.score_path_sync(
                source_node=source,
                edge=edge,
                target_node=target,
                query_embedding=query_embedding,
            )

            if scored_path.score >= self._config.inclusion_threshold:
                scored_paths.append(scored_path)

        # Sort by score descending
        scored_paths.sort(key=lambda x: x.score, reverse=True)

        # Apply max_paths limit if specified
        if max_paths is not None:
            scored_paths = scored_paths[:max_paths]

        return scored_paths
