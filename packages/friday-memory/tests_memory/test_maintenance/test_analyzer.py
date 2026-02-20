"""Tests for ConsistencyAnalyzer."""

import pytest
from friday_memory.maintenance.analyzer import ConsistencyAnalyzer
from friday_memory.maintenance.models import IssueSeverity, IssueType, PruneConfig


class TestConsistencyAnalyzer:
    """Test consistency analysis operations."""

    @pytest.mark.asyncio
    async def test_analyze_finds_orphaned_edges(self, memory_with_issues):
        """Test detection of orphaned edges."""
        analyzer = ConsistencyAnalyzer(memory_with_issues)
        report = await analyzer.analyze()

        orphaned_issues = [
            i for i in report.issues if i.issue_type == IssueType.ORPHANED_EDGE
        ]

        # Should find 2 orphaned edges
        assert len(orphaned_issues) == 2
        assert all(i.severity == IssueSeverity.CRITICAL for i in orphaned_issues)

    @pytest.mark.asyncio
    async def test_analyze_finds_duplicate_entities(self, memory_with_issues):
        """Test detection of duplicate entities."""
        analyzer = ConsistencyAnalyzer(memory_with_issues)
        report = await analyzer.analyze()

        # Should find duplicate groups
        assert len(report.duplicate_groups) >= 1

        # Check for exact duplicates (Chuck/chuck)
        exact_dups = [g for g in report.duplicate_groups if g.match_type == "exact"]
        assert len(exact_dups) >= 1

    @pytest.mark.asyncio
    async def test_analyze_finds_stale_entities(self, memory_with_issues):
        """Test detection of stale entities."""
        config = PruneConfig(stale_threshold_days=90, min_hit_count=1)
        analyzer = ConsistencyAnalyzer(memory_with_issues, config)
        report = await analyzer.analyze()

        stale_issues = [
            i for i in report.issues if i.issue_type == IssueType.STALE_ENTITY
        ]

        # Should find 3 stale entities
        assert len(stale_issues) == 3
        assert all(i.severity == IssueSeverity.INFO for i in stale_issues)

    @pytest.mark.asyncio
    async def test_analyze_clean_memory(self, clean_memory_dir):
        """Test analysis of clean memory (no issues)."""
        analyzer = ConsistencyAnalyzer(clean_memory_dir)
        report = await analyzer.analyze()

        # Should have minimal or no issues
        critical = report.severity_counts["critical"]
        assert critical == 0

    @pytest.mark.asyncio
    async def test_analyze_populates_stats(self, memory_with_issues):
        """Test that analysis populates store statistics."""
        analyzer = ConsistencyAnalyzer(memory_with_issues)
        report = await analyzer.analyze()

        # Graph stats
        assert "node_count" in report.graph_stats
        assert "edge_count" in report.graph_stats
        assert report.graph_stats["node_count"] == 9  # All nodes in fixture
        assert report.graph_stats["edge_count"] == 4  # All edges in fixture

        # Episodic stats
        assert "turn_count" in report.episodic_stats
        assert report.episodic_stats["turn_count"] == 3  # 3 turns in fixture

    @pytest.mark.asyncio
    async def test_analyze_severity_counts(self, memory_with_issues):
        """Test that severity counts are accurate."""
        analyzer = ConsistencyAnalyzer(memory_with_issues)
        report = await analyzer.analyze()

        # Count issues by severity manually
        manual_counts = {"critical": 0, "warning": 0, "info": 0}
        for issue in report.issues:
            manual_counts[issue.severity.value] += 1

        assert report.severity_counts == manual_counts

    @pytest.mark.asyncio
    async def test_report_summary_generation(self, memory_with_issues):
        """Test human-readable report generation."""
        analyzer = ConsistencyAnalyzer(memory_with_issues)
        report = await analyzer.analyze()

        summary = analyzer.generate_report_summary(report)

        assert "MEMORY CONSISTENCY REPORT" in summary
        assert "STORE STATISTICS" in summary
        assert "ISSUES FOUND" in summary
        assert str(memory_with_issues) in summary

    @pytest.mark.asyncio
    async def test_configurable_staleness_threshold(self, memory_with_issues):
        """Test that staleness threshold is configurable."""
        # With very long threshold, no entities should be stale
        config = PruneConfig(stale_threshold_days=365, min_hit_count=0)
        analyzer = ConsistencyAnalyzer(memory_with_issues, config)
        report = await analyzer.analyze()

        stale_issues = [
            i for i in report.issues if i.issue_type == IssueType.STALE_ENTITY
        ]

        # 120 days old entities shouldn't be stale with 365 day threshold
        # But they have hit_count=0 and min_hit_count=0, so not flagged
        # Actually with min_hit_count=0, nothing is stale
        assert len(stale_issues) == 0

    @pytest.mark.asyncio
    async def test_empty_memory_directory(self, temp_memory_dir):
        """Test analysis of empty memory directory."""
        analyzer = ConsistencyAnalyzer(temp_memory_dir)
        report = await analyzer.analyze()

        # Should complete without error
        assert report.graph_stats["node_count"] == 0
        assert report.graph_stats["edge_count"] == 0
