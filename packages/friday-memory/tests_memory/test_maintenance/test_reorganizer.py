"""Tests for MemoryReorganizer orchestrator."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from friday_memory.maintenance.models import LifecycleReport, OptimizationReport
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


class TestLifecycleIntegration:
    """Test lifecycle integration in reorganization (Phase 8)."""

    @pytest.fixture
    def mock_collection_manager(self):
        """Create a mock collection manager."""
        manager = MagicMock()

        # Create mock short_term collection with async get_all method
        # Returns list of dictionaries with "id" and "metadata" keys
        # Include created_at old enough to pass eligibility (>24h ago)
        short_term = MagicMock()
        short_term.get_all = AsyncMock(
            return_value=[
                {
                    "id": "st_1",
                    "text": "Short term memory",
                    "metadata": {
                        "hit_count": 5,
                        "access_count": 5,
                        "confidence": 0.9,
                        "created_at": "2026-01-01T00:00:00",
                    },
                },
                {
                    "id": "st_2",
                    "text": "Another short term",
                    "metadata": {
                        "hit_count": 10,
                        "access_count": 10,
                        "confidence": 0.85,
                        "created_at": "2026-01-01T00:00:00",
                    },
                },
            ]
        )
        manager.short_term = short_term

        # Create mock long_term collection with async get_all method
        long_term = MagicMock()
        long_term.get_all = AsyncMock(
            return_value=[
                {
                    "id": "lt_1",
                    "text": "Long term memory",
                    "metadata": {
                        "decay_score": 0.1,
                        "last_accessed_at": "2025-01-01T00:00:00",
                    },
                },
            ]
        )
        manager.long_term = long_term

        manager.promote_to_long_term = AsyncMock()
        manager.demote_to_decayed = AsyncMock()
        manager.promote_memory = AsyncMock()
        manager.demote_memory = AsyncMock()
        return manager

    @pytest.fixture
    def mock_access_buffer(self):
        """Create a mock access buffer."""
        buffer = MagicMock()
        buffer.get_stats = MagicMock(
            return_value={
                "short_term_memories": 5,
                "long_term_memories": 10,
            }
        )
        buffer.flush_all = AsyncMock(
            return_value=MagicMock(
                short_term_flushed=5,
                long_term_flushed=10,
            )
        )
        return buffer

    @pytest.fixture
    def mock_factor_computer(self):
        """Create a mock factor computer."""
        computer = MagicMock()
        computer.compute_factors = AsyncMock(
            return_value=MagicMock(
                updated=15,
            )
        )
        return computer

    @pytest.fixture
    def mock_promotion_scorer(self):
        """Create a mock promotion scorer."""
        scorer = MagicMock()
        scorer.is_eligible_for_promotion = MagicMock(return_value=True)
        scorer.calculate_promotion_score = MagicMock(
            return_value=0.8
        )  # Above threshold
        return scorer

    @pytest.fixture
    def mock_decay_calculator(self):
        """Create a mock decay calculator."""
        calculator = MagicMock()
        calculator.calculate_decay = MagicMock(return_value=0.1)  # Low score
        calculator.should_decay = MagicMock(return_value=True)  # Below threshold
        return calculator

    def test_has_lifecycle_support_false(self, clean_memory_dir):
        """Test has_lifecycle_support returns False without components."""
        reorganizer = MemoryReorganizer(clean_memory_dir)
        assert not reorganizer.has_lifecycle_support

    def test_has_lifecycle_support_true(
        self, clean_memory_dir, mock_collection_manager
    ):
        """Test has_lifecycle_support returns True with collection manager."""
        reorganizer = MemoryReorganizer(
            clean_memory_dir,
            collection_manager=mock_collection_manager,
        )
        assert reorganizer.has_lifecycle_support

    @pytest.mark.asyncio
    async def test_lifecycle_without_support(self, clean_memory_dir):
        """Test lifecycle step returns error without components."""
        reorganizer = MemoryReorganizer(clean_memory_dir)
        report = await reorganizer.lifecycle(dry_run=True)

        assert len(report.errors) > 0
        assert "not configured" in report.errors[0]

    @pytest.mark.asyncio
    async def test_lifecycle_dry_run(
        self,
        clean_memory_dir,
        mock_collection_manager,
        mock_promotion_scorer,
        mock_decay_calculator,
    ):
        """Test lifecycle step in dry run mode."""
        reorganizer = MemoryReorganizer(
            clean_memory_dir,
            collection_manager=mock_collection_manager,
            promotion_scorer=mock_promotion_scorer,
            decay_calculator=mock_decay_calculator,
        )

        report = await reorganizer.lifecycle(dry_run=True)

        assert report.dry_run
        assert report.promotions_checked == 2  # 2 short-term memories
        assert report.promotions_executed == 2  # Both above threshold
        assert report.decays_checked == 1  # 1 long-term memory
        assert report.decays_executed == 1  # Below threshold

        # Should not actually call promotion/demotion in dry run
        mock_collection_manager.promote_to_long_term.assert_not_called()
        mock_collection_manager.demote_to_decayed.assert_not_called()

    @pytest.mark.asyncio
    async def test_optimize_without_support(self, clean_memory_dir):
        """Test optimize step skips gracefully without components.

        Without lifecycle support or collection_manager, steps 1-3 are
        skipped and the timestamp backfill is also skipped.  No errors
        are appended — only warnings are logged.
        """
        reorganizer = MemoryReorganizer(clean_memory_dir)
        report = await reorganizer.optimize(dry_run=True)

        assert len(report.errors) == 0
        assert not report.access_buffer_flushed
        assert not report.timestamp_backfill_done

    @pytest.mark.asyncio
    async def test_optimize_dry_run(
        self,
        clean_memory_dir,
        mock_collection_manager,
        mock_access_buffer,
        mock_factor_computer,
    ):
        """Test optimize step in dry run mode."""
        reorganizer = MemoryReorganizer(
            clean_memory_dir,
            collection_manager=mock_collection_manager,
            access_buffer=mock_access_buffer,
            factor_computer=mock_factor_computer,
        )

        report = await reorganizer.optimize(dry_run=True)

        assert report.dry_run
        assert report.access_buffer_flushed
        assert report.short_term_accesses_flushed == 5
        assert report.long_term_accesses_flushed == 10

        # Should not actually flush in dry run
        mock_access_buffer.flush_all.assert_not_called()

    @pytest.mark.asyncio
    async def test_reorganize_skip_lifecycle(self, memory_with_issues):
        """Test reorganize with skip_lifecycle option."""
        reorganizer = MemoryReorganizer(memory_with_issues)

        report = await reorganizer.reorganize(
            backup_first=False,
            dry_run=True,
            skip_synthesis=True,
            skip_verify=True,
            skip_lifecycle=True,
        )

        assert report.success
        assert report.lifecycle_report is None
        assert report.optimization_report is None

    @pytest.mark.asyncio
    async def test_reorganize_with_lifecycle(
        self,
        memory_with_issues,
        mock_collection_manager,
        mock_access_buffer,
        mock_factor_computer,
        mock_promotion_scorer,
        mock_decay_calculator,
    ):
        """Test reorganize includes lifecycle steps when configured."""
        reorganizer = MemoryReorganizer(
            memory_with_issues,
            collection_manager=mock_collection_manager,
            access_buffer=mock_access_buffer,
            factor_computer=mock_factor_computer,
            promotion_scorer=mock_promotion_scorer,
            decay_calculator=mock_decay_calculator,
        )

        report = await reorganizer.reorganize(
            backup_first=False,
            dry_run=True,
            skip_synthesis=True,
            skip_verify=True,
            skip_lifecycle=False,
        )

        assert report.success
        assert report.lifecycle_report is not None
        assert report.optimization_report is not None

    @pytest.mark.asyncio
    async def test_report_summary_includes_lifecycle(
        self,
        memory_with_issues,
        mock_collection_manager,
        mock_access_buffer,
        mock_factor_computer,
        mock_promotion_scorer,
        mock_decay_calculator,
    ):
        """Test report summary includes lifecycle sections."""
        reorganizer = MemoryReorganizer(
            memory_with_issues,
            collection_manager=mock_collection_manager,
            access_buffer=mock_access_buffer,
            factor_computer=mock_factor_computer,
            promotion_scorer=mock_promotion_scorer,
            decay_calculator=mock_decay_calculator,
        )

        report = await reorganizer.reorganize(
            backup_first=False,
            dry_run=True,
            skip_synthesis=True,
            skip_verify=True,
            skip_lifecycle=False,
        )

        summary = reorganizer.generate_report_summary(report)

        assert "LIFECYCLE MAINTENANCE" in summary
        assert "LATENCY OPTIMIZATION" in summary
        assert "Promotions:" in summary
        assert "Decays:" in summary


class TestLifecycleReportModel:
    """Test LifecycleReport model."""

    def test_lifecycle_report_defaults(self):
        """Test LifecycleReport has correct defaults."""
        report = LifecycleReport(dry_run=True)

        assert report.dry_run
        assert report.promotions_checked == 0
        assert report.promotions_executed == 0
        assert report.decays_checked == 0
        assert report.decays_executed == 0
        assert report.graph_nodes_decayed == 0
        assert len(report.errors) == 0

    def test_lifecycle_report_with_values(self):
        """Test LifecycleReport with values."""
        report = LifecycleReport(
            dry_run=False,
            promotions_checked=10,
            promotions_executed=5,
            decays_checked=20,
            decays_executed=3,
            graph_nodes_decayed=2,
            promoted_memory_ids=["m1", "m2"],
            decayed_memory_ids=["m3"],
        )

        assert report.promotions_checked == 10
        assert report.promotions_executed == 5
        assert len(report.promoted_memory_ids) == 2


class TestOptimizationReportModel:
    """Test OptimizationReport model."""

    def test_optimization_report_defaults(self):
        """Test OptimizationReport has correct defaults."""
        report = OptimizationReport(dry_run=True)

        assert report.dry_run
        assert report.access_buffer_flushed is False
        assert report.retrieval_factors_computed is False
        assert report.edge_embeddings_backfilled is False
        assert len(report.errors) == 0

    def test_optimization_report_with_values(self):
        """Test OptimizationReport with values."""
        report = OptimizationReport(
            dry_run=False,
            access_buffer_flushed=True,
            short_term_accesses_flushed=10,
            long_term_accesses_flushed=20,
            retrieval_factors_computed=True,
            short_term_factors_updated=15,
            long_term_factors_updated=25,
            access_flush_duration_ms=50.5,
            factor_compute_duration_ms=100.2,
        )

        assert report.access_buffer_flushed
        assert report.short_term_accesses_flushed == 10
        assert report.long_term_accesses_flushed == 20
        assert report.access_flush_duration_ms == 50.5
