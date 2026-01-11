"""Tests for MemoryReorganizer orchestrator."""

import pytest

from friday_memory.maintenance.reorganizer import MemoryReorganizer


class TestMemoryReorganizer:
    """Test full reorganization pipeline."""

    @pytest.mark.asyncio
    async def test_reorganize_dry_run(self, memory_with_issues):
        """Test dry run reorganization."""
        reorganizer = MemoryReorganizer(memory_with_issues)

        report = await reorganizer.reorganize(
            backup_first=False,
            dry_run=True,
            skip_synthesis=True,  # No LLM
            skip_verify=True,  # No LLM
        )

        assert report.success
        assert report.consistency_report is not None
        assert report.prune_report is not None
        assert report.prune_report.dry_run is True

    @pytest.mark.asyncio
    async def test_reorganize_with_backup(self, memory_with_issues):
        """Test reorganization creates backup first."""
        reorganizer = MemoryReorganizer(memory_with_issues)

        report = await reorganizer.reorganize(
            backup_first=True,
            dry_run=False,
            skip_synthesis=True,
            skip_verify=True,
        )

        assert report.success
        assert report.backup_manifest is not None
        assert report.backup_manifest.backup_id

    @pytest.mark.asyncio
    async def test_analyze_only(self, memory_with_issues):
        """Test standalone analysis."""
        reorganizer = MemoryReorganizer(memory_with_issues)
        report = await reorganizer.analyze()

        assert report.graph_stats["node_count"] > 0
        assert len(report.issues) > 0

    @pytest.mark.asyncio
    async def test_prune_only(self, memory_with_issues):
        """Test standalone pruning."""
        reorganizer = MemoryReorganizer(memory_with_issues)
        report = await reorganizer.prune(dry_run=True)

        assert report.dry_run
        assert report is not None

    @pytest.mark.asyncio
    async def test_backup_only(self, clean_memory_dir):
        """Test standalone backup."""
        reorganizer = MemoryReorganizer(clean_memory_dir)
        manifest = await reorganizer.backup()

        assert manifest.backup_id
        assert len(manifest.files) > 0

    @pytest.mark.asyncio
    async def test_report_summary_generation(self, memory_with_issues):
        """Test full report summary."""
        reorganizer = MemoryReorganizer(memory_with_issues)

        report = await reorganizer.reorganize(
            backup_first=False,
            dry_run=True,
            skip_synthesis=True,
            skip_verify=True,
        )

        summary = reorganizer.generate_report_summary(report)

        assert "MEMORY REORGANIZATION REPORT" in summary
        assert "CONSISTENCY ANALYSIS" in summary
        assert "PRUNING" in summary

    @pytest.mark.asyncio
    async def test_component_access(self, clean_memory_dir):
        """Test access to individual components."""
        reorganizer = MemoryReorganizer(clean_memory_dir)

        # Should have all components
        assert reorganizer.backup_manager is not None
        assert reorganizer.analyzer is not None
        assert reorganizer.pruner is not None
        assert reorganizer.synthesizer is not None
        assert reorganizer.fact_checker is not None

    @pytest.mark.asyncio
    async def test_reorganize_handles_errors_gracefully(self, temp_memory_dir):
        """Test reorganization handles missing files gracefully."""
        reorganizer = MemoryReorganizer(temp_memory_dir)

        # Should complete without crashing even with empty directory
        report = await reorganizer.reorganize(
            backup_first=False,
            dry_run=True,
            skip_synthesis=True,
            skip_verify=True,
        )

        # May or may not succeed depending on implementation
        # But should not raise exception
        assert report is not None
