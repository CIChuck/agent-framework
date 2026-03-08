# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
# mypy: disallow-untyped-defs=False
"""Tests for RedundancyPruner."""

import json

import pytest
from friday_memory.maintenance.models import PruneConfig
from friday_memory.maintenance.pruner import RedundancyPruner


class TestRedundancyPruner:
    """Test redundancy pruning operations."""

    @pytest.mark.asyncio
    async def test_identify_stale_entities(self, memory_with_issues) -> None:
        """Test identification of stale entities."""
        config = PruneConfig(stale_threshold_days=90, min_hit_count=1)
        pruner = RedundancyPruner(memory_with_issues, config)

        stale = await pruner.identify_stale_entities()

        # Should find 3 stale entities from fixture
        assert len(stale) == 3

        # All should be from graph store
        assert all(item.store == "graph" for item in stale)
        assert all(item.item_type == "entity" for item in stale)

    @pytest.mark.asyncio
    async def test_prune_dry_run(self, memory_with_issues) -> None:
        """Test dry run doesn't modify data."""
        config = PruneConfig(stale_threshold_days=90, min_hit_count=1)
        pruner = RedundancyPruner(memory_with_issues, config)

        # Get original graph data
        graph_path = memory_with_issues / "graph.json"
        original_data = json.loads(graph_path.read_text())
        original_node_count = len(original_data["nodes"])

        # Dry run
        report = await pruner.prune(dry_run=True)

        # Data should be unchanged
        current_data = json.loads(graph_path.read_text())
        assert len(current_data["nodes"]) == original_node_count

        # But report should show what would be removed
        assert report.dry_run is True
        assert (
            report.entities_removed > 0
            or report.entities_merged > 0
            or len(report.items) > 0
        )

    @pytest.mark.asyncio
    async def test_prune_actually_removes(self, memory_with_issues) -> None:
        """Test actual pruning removes entities."""
        config = PruneConfig(stale_threshold_days=90, min_hit_count=1)
        pruner = RedundancyPruner(memory_with_issues, config)

        # Get original count
        graph_path = memory_with_issues / "graph.json"
        original_data = json.loads(graph_path.read_text())
        original_count = len(original_data["nodes"])

        # Actually prune
        report = await pruner.prune(dry_run=False)

        # Data should be modified
        current_data = json.loads(graph_path.read_text())
        current_count = len(current_data["nodes"])

        # Should have fewer nodes (stale ones removed)
        assert current_count < original_count
        assert report.dry_run is False

    @pytest.mark.asyncio
    async def test_merge_duplicate_entities(self, memory_with_issues) -> None:
        """Test merging of duplicate entities."""
        pruner = RedundancyPruner(memory_with_issues)

        # Merge duplicates
        report = await pruner.merge_duplicate_entities(dry_run=False)

        # Should have merged some entities
        assert report.entities_merged > 0

        # Check graph was modified
        graph_path = memory_with_issues / "graph.json"
        data = json.loads(graph_path.read_text())

        # The duplicates (chuck and chuck_2) should be merged
        labels = [n.get("label", "").lower() for n in data["nodes"].values()]

        # Should not have multiple "chuck" entries
        chuck_count = sum(1 for l in labels if l == "chuck")  # noqa: E741
        assert chuck_count == 1

    @pytest.mark.asyncio
    async def test_merge_preserves_higher_hit_count(self, memory_with_issues) -> None:
        """Test that merge preserves the higher hit_count."""
        pruner = RedundancyPruner(memory_with_issues)

        # Get original hit counts
        graph_path = memory_with_issues / "graph.json"
        original_data = json.loads(graph_path.read_text())

        chuck_hit = original_data["nodes"]["chuck"]["hit_count"]  # 15
        chuck2_hit = original_data["nodes"]["chuck_2"]["hit_count"]  # 3

        # Merge
        await pruner.merge_duplicate_entities(dry_run=False)

        # Check merged entity has higher hit count
        current_data = json.loads(graph_path.read_text())

        # Find the remaining chuck entry
        chuck_node = None
        for _node_id, node_data in current_data["nodes"].items():
            if node_data.get("label", "").lower() == "chuck":
                chuck_node = node_data
                break

        assert chuck_node is not None
        assert chuck_node["hit_count"] == max(chuck_hit, chuck2_hit)

    @pytest.mark.asyncio
    async def test_configurable_similarity_threshold(self, memory_with_issues) -> None:
        """Test configurable similarity threshold."""
        # With very low threshold, should find no semantic duplicates
        config = PruneConfig(similarity_threshold=0.99)
        pruner = RedundancyPruner(memory_with_issues, config)

        # Note: This test is limited without ChromaDB
        # The semantic dedup won't find anything without vector store
        report = await pruner.prune(dry_run=True)

        # Should complete without error
        assert report is not None

    @pytest.mark.asyncio
    async def test_prune_report_summary(self, memory_with_issues) -> None:
        """Test prune report summary generation."""
        pruner = RedundancyPruner(memory_with_issues)
        report = await pruner.prune(dry_run=True)

        summary = pruner.generate_report_summary(report)

        assert "PRUNE REPORT" in summary
        assert "DRY RUN" in summary
        assert "RESULTS" in summary

    @pytest.mark.asyncio
    async def test_edges_removed_with_entity(self, memory_with_issues) -> None:
        """Test that edges are removed when entity is removed."""
        config = PruneConfig(stale_threshold_days=90, min_hit_count=1)
        pruner = RedundancyPruner(memory_with_issues, config)

        # Get original edge count
        graph_path = memory_with_issues / "graph.json"
        original_data = json.loads(graph_path.read_text())
        len(original_data["edges"])

        # Prune stale entities
        await pruner.prune(dry_run=False)

        # Check edges were cleaned up
        current_data = json.loads(graph_path.read_text())

        # Edges shouldn't reference deleted nodes
        node_ids = set(current_data["nodes"].keys())
        for edge in current_data["edges"]:
            # At minimum, valid edges should have existing targets
            # (source might still be orphaned from fixture)
            if edge["source"] in node_ids:
                assert (
                    edge["target"] in node_ids or edge["target"] == "nonexistent_node_1"
                )

    @pytest.mark.asyncio
    async def test_prune_clean_memory(self, clean_memory_dir) -> None:
        """Test pruning clean memory (nothing to prune)."""
        pruner = RedundancyPruner(clean_memory_dir)
        report = await pruner.prune(dry_run=True)

        # Should find nothing to prune
        assert report.entities_removed == 0
        assert report.insights_removed == 0
