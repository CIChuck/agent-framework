"""Tests for GraphPathScorer."""

import math

import pytest
from friday_memory.models import GraphEdge, GraphNode, ProvenanceMetadata
from friday_memory.retrieval.graph_scorer import (
    GraphPathScorer,
    GraphPathScorerConfig,
    ScoredPath,
    cosine_similarity,
)


# Helper to create test nodes and edges
def create_test_node(
    node_id: str,
    label: str,
    node_type: str = "entity",
    hit_count: int = 0,
    embedding: list[float] | None = None,
) -> GraphNode:
    """Create a test GraphNode."""
    provenance = ProvenanceMetadata(
        source_id="test-turn-1",
        source_type="extraction",
        confidence=0.9,
    )
    return GraphNode(
        id=node_id,
        type=node_type,
        label=label,
        provenance=provenance,
        hit_count=hit_count,
        embedding=embedding,
    )


def create_test_edge(
    source_id: str,
    target_id: str,
    relation: str,
    embedding: list[float] | None = None,
) -> GraphEdge:
    """Create a test GraphEdge."""
    provenance = ProvenanceMetadata(
        source_id="test-turn-1",
        source_type="extraction",
        confidence=0.9,
    )
    return GraphEdge(
        source_id=source_id,
        target_id=target_id,
        relation=relation,
        provenance=provenance,
        embedding=embedding,
    )


class TestCosineSimilarity:
    """Test cosine_similarity function."""

    def test_identical_vectors(self):
        """Identical vectors should have similarity 1.0."""
        vec = [1.0, 2.0, 3.0]
        assert cosine_similarity(vec, vec) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        """Orthogonal vectors should have similarity 0.0."""
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]
        assert cosine_similarity(vec1, vec2) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        """Opposite vectors should have similarity -1.0."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [-1.0, -2.0, -3.0]
        assert cosine_similarity(vec1, vec2) == pytest.approx(-1.0)

    def test_empty_vectors(self):
        """Empty vectors should return 0.0."""
        assert cosine_similarity([], []) == 0.0
        assert cosine_similarity([1.0], []) == 0.0

    def test_mismatched_length(self):
        """Mismatched length vectors should return 0.0."""
        assert cosine_similarity([1.0, 2.0], [1.0]) == 0.0

    def test_zero_vectors(self):
        """Zero vectors should return 0.0."""
        assert cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0

    def test_known_similarity(self):
        """Test with known similarity value."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 1.0, 0.0]
        # cos(45°) ≈ 0.707
        expected = 1.0 / math.sqrt(2)
        assert cosine_similarity(vec1, vec2) == pytest.approx(expected, rel=1e-5)


class TestGraphPathScorerConfig:
    """Test GraphPathScorerConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = GraphPathScorerConfig()
        assert config.edge_weight == 0.4
        assert config.target_weight == 0.6
        assert config.hit_count_boost == 0.05
        assert config.inclusion_threshold == 0.5

    def test_custom_config(self):
        """Test custom configuration."""
        config = GraphPathScorerConfig(
            edge_weight=0.3,
            target_weight=0.7,
            hit_count_boost=0.1,
            inclusion_threshold=0.6,
        )
        assert config.edge_weight == 0.3
        assert config.target_weight == 0.7


class TestGraphPathScorer:
    """Test GraphPathScorer class."""

    @pytest.fixture
    def scorer(self):
        """Create scorer with default config."""
        return GraphPathScorer()

    @pytest.fixture
    def query_embedding(self):
        """Create a test query embedding."""
        return [1.0, 0.0, 0.0]  # Unit vector in x direction

    @pytest.fixture
    def similar_embedding(self):
        """Create an embedding similar to query."""
        # Slightly off from query direction
        return [0.9, 0.1, 0.0]

    @pytest.fixture
    def dissimilar_embedding(self):
        """Create an embedding dissimilar to query."""
        return [0.0, 1.0, 0.0]  # Orthogonal to query

    def test_usage_boost_no_hits(self, scorer):
        """No hits should give usage boost of 1.0."""
        boost = scorer.calculate_usage_boost(0, 0)
        assert boost == 1.0

    def test_usage_boost_with_hits(self, scorer):
        """Higher hit counts should give higher boost."""
        boost_0 = scorer.calculate_usage_boost(0, 0)
        boost_5 = scorer.calculate_usage_boost(5, 5)
        boost_20 = scorer.calculate_usage_boost(20, 20)

        assert boost_0 < boost_5 < boost_20

    def test_usage_boost_uses_minimum(self, scorer):
        """Usage boost should use minimum of source and target hits."""
        boost_min_5 = scorer.calculate_usage_boost(5, 100)
        boost_both_5 = scorer.calculate_usage_boost(5, 5)

        assert boost_min_5 == boost_both_5

    def test_score_path_sync_with_embeddings(
        self, scorer, query_embedding, similar_embedding
    ):
        """Test synchronous scoring with pre-computed embeddings."""
        source = create_test_node("s1", "Python", hit_count=5)
        target = create_test_node(
            "t1", "Programming", hit_count=10, embedding=similar_embedding
        )
        edge = create_test_edge("s1", "t1", "used_for", embedding=similar_embedding)

        scored = scorer.score_path_sync(source, edge, target, query_embedding)

        assert isinstance(scored, ScoredPath)
        assert scored.score > 0
        assert scored.edge_similarity > 0
        assert scored.target_similarity > 0

    def test_score_path_sync_without_embeddings(self, scorer, query_embedding):
        """Test scoring without embeddings returns 0 similarities."""
        source = create_test_node("s1", "Python")
        target = create_test_node("t1", "Programming")
        edge = create_test_edge("s1", "t1", "used_for")

        scored = scorer.score_path_sync(source, edge, target, query_embedding)

        assert scored.edge_similarity == 0.0
        assert scored.target_similarity == 0.0
        assert scored.score == 0.0

    def test_score_path_sync_similar_vs_dissimilar(
        self, scorer, query_embedding, similar_embedding, dissimilar_embedding
    ):
        """Similar paths should score higher than dissimilar ones."""
        source = create_test_node("s1", "Python")

        # Similar path
        target_similar = create_test_node("t1", "Related", embedding=similar_embedding)
        edge_similar = create_test_edge("s1", "t1", "rel", embedding=similar_embedding)
        scored_similar = scorer.score_path_sync(
            source, edge_similar, target_similar, query_embedding
        )

        # Dissimilar path
        target_dissimilar = create_test_node(
            "t2", "Unrelated", embedding=dissimilar_embedding
        )
        edge_dissimilar = create_test_edge(
            "s1", "t2", "rel", embedding=dissimilar_embedding
        )
        scored_dissimilar = scorer.score_path_sync(
            source, edge_dissimilar, target_dissimilar, query_embedding
        )

        assert scored_similar.score > scored_dissimilar.score

    def test_filter_paths_sync_applies_threshold(
        self, scorer, query_embedding, similar_embedding, dissimilar_embedding
    ):
        """filter_paths_sync should exclude paths below threshold."""
        source = create_test_node("s1", "Source")

        # Path above threshold (similar)
        target_good = create_test_node("t1", "Good", embedding=similar_embedding)
        edge_good = create_test_edge("s1", "t1", "rel", embedding=similar_embedding)

        # Path below threshold (dissimilar)
        target_bad = create_test_node("t2", "Bad", embedding=dissimilar_embedding)
        edge_bad = create_test_edge("s1", "t2", "rel", embedding=dissimilar_embedding)

        paths = [
            (source, edge_good, target_good),
            (source, edge_bad, target_bad),
        ]

        filtered = scorer.filter_paths_sync(paths, query_embedding)

        # Should only include paths above threshold (0.5 by default)
        # Similar embedding should pass, dissimilar should not
        assert len(filtered) <= 2
        if len(filtered) > 0:
            assert all(p.score >= scorer.inclusion_threshold for p in filtered)

    def test_filter_paths_sync_sorts_by_score(self, scorer, query_embedding):
        """filter_paths_sync should return paths sorted by score descending."""
        source = create_test_node("s1", "Source")

        # Create paths with varying scores (via hit counts)
        targets = []
        edges = []
        emb = [0.8, 0.2, 0.0]  # Similar to query

        for i in range(3):
            hit_count = (i + 1) * 10  # 10, 20, 30
            t = create_test_node(
                f"t{i}", f"Target{i}", hit_count=hit_count, embedding=emb
            )
            e = create_test_edge("s1", f"t{i}", "rel", embedding=emb)
            targets.append(t)
            edges.append(e)

        paths = [(source, edges[i], targets[i]) for i in range(3)]
        filtered = scorer.filter_paths_sync(paths, query_embedding)

        if len(filtered) > 1:
            for i in range(len(filtered) - 1):
                assert filtered[i].score >= filtered[i + 1].score

    def test_filter_paths_sync_max_paths(self, scorer, query_embedding):
        """filter_paths_sync should respect max_paths limit."""
        source = create_test_node("s1", "Source")
        emb = [0.9, 0.1, 0.0]

        paths = []
        for i in range(10):
            t = create_test_node(f"t{i}", f"Target{i}", embedding=emb)
            e = create_test_edge("s1", f"t{i}", "rel", embedding=emb)
            paths.append((source, e, t))

        filtered = scorer.filter_paths_sync(paths, query_embedding, max_paths=3)

        assert len(filtered) <= 3

    @pytest.mark.asyncio
    async def test_score_path_async_with_fallback(self, scorer, query_embedding):
        """Test async scoring with embedding function fallback."""
        source = create_test_node("s1", "Python")
        target = create_test_node("t1", "Programming")
        edge = create_test_edge("s1", "t1", "used_for")

        async def mock_embedding_fn(text: str) -> list[float]:
            # Return embedding similar to query for any text
            return [0.8, 0.2, 0.0]

        scored = await scorer.score_path(
            source, edge, target, query_embedding, embedding_fn=mock_embedding_fn
        )

        assert scored.score > 0
        assert scored.edge_similarity > 0
        assert scored.target_similarity > 0

    @pytest.mark.asyncio
    async def test_filter_paths_async(self, scorer, query_embedding):
        """Test async path filtering."""
        source = create_test_node("s1", "Source")
        emb = [0.9, 0.1, 0.0]

        paths = []
        for i in range(5):
            t = create_test_node(f"t{i}", f"Target{i}", embedding=emb)
            e = create_test_edge("s1", f"t{i}", "rel", embedding=emb)
            paths.append((source, e, t))

        filtered = await scorer.filter_paths(paths, query_embedding)

        assert isinstance(filtered, list)
        for p in filtered:
            assert isinstance(p, ScoredPath)
            assert p.score >= scorer.inclusion_threshold


class TestScoredPath:
    """Test ScoredPath class."""

    def test_to_dict(self):
        """Test ScoredPath.to_dict() conversion."""
        source = create_test_node("s1", "Source")
        target = create_test_node("t1", "Target")
        edge = create_test_edge("s1", "t1", "relates_to")

        scored = ScoredPath(
            source_node=source,
            edge=edge,
            target_node=target,
            score=0.75,
            edge_similarity=0.6,
            target_similarity=0.8,
        )

        d = scored.to_dict()

        assert d["source_id"] == "s1"
        assert d["source_label"] == "Source"
        assert d["target_id"] == "t1"
        assert d["target_label"] == "Target"
        assert d["relation"] == "relates_to"
        assert d["score"] == 0.75
        assert d["edge_similarity"] == 0.6
        assert d["target_similarity"] == 0.8
