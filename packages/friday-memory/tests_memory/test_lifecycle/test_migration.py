"""
Tests for MemoryMigrator and lifecycle migration (Phase 9).

Tests cover:
- MigrationReport model
- MemoryMigrator initialization
- Vector store migration (adding lifecycle metadata)
- Graph store migration (adding stage metadata)
- Idempotent migration (safe to run multiple times)
- Migration detection (check_migration_needed)
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from friday_memory.lifecycle import MemoryMigrator, MemoryStage, MigrationReport


class TestMigrationReport:
    """Test MigrationReport model."""

    def test_report_defaults(self):
        """Test MigrationReport has correct defaults."""
        report = MigrationReport(dry_run=True)

        assert report.dry_run
        assert report.vectors_scanned == 0
        assert report.vectors_migrated == 0
        assert report.vectors_skipped == 0
        assert report.nodes_scanned == 0
        assert report.nodes_migrated == 0
        assert report.nodes_skipped == 0
        assert report.edges_scanned == 0
        assert report.edges_migrated == 0
        assert report.edges_skipped == 0
        assert len(report.errors) == 0

    def test_total_migrated(self):
        """Test total_migrated property."""
        report = MigrationReport(
            dry_run=False,
            vectors_migrated=10,
            nodes_migrated=5,
            edges_migrated=3,
        )

        assert report.total_migrated == 18

    def test_success_with_no_errors(self):
        """Test success property with no errors."""
        report = MigrationReport(dry_run=False)
        assert report.success

    def test_success_with_errors(self):
        """Test success property with errors."""
        report = MigrationReport(dry_run=False, errors=["Some error"])
        assert not report.success

    def test_needs_migration(self):
        """Test needs_migration property."""
        # No migration needed
        report = MigrationReport(dry_run=True)
        assert not report.needs_migration

        # Vectors need migration
        report = MigrationReport(dry_run=True, vectors_migrated=1)
        assert report.needs_migration

        # Nodes need migration
        report = MigrationReport(dry_run=True, nodes_migrated=1)
        assert report.needs_migration


class TestMemoryMigrator:
    """Test MemoryMigrator class."""

    @pytest.fixture
    def mock_vector_store(self):
        """Create a mock vector store."""
        store = MagicMock()
        store.get_all = AsyncMock(
            return_value=[
                {"id": "v1", "metadata": {"type": "insight"}},
                {"id": "v2", "metadata": {"type": "summary", "stage": "long_term"}},
                {"id": "v3", "metadata": {"type": "insight"}},
            ]
        )
        store.update_metadata = AsyncMock()
        return store

    @pytest.fixture
    def mock_graph_store(self):
        """Create a mock graph store."""
        # Create mock nodes
        node1 = MagicMock()
        node1.id = "n1"
        node1.stage = None  # Needs migration

        node2 = MagicMock()
        node2.id = "n2"
        node2.stage = MemoryStage.LONG_TERM  # Already migrated

        node3 = MagicMock()
        node3.id = "n3"
        node3.stage = None  # Needs migration

        store = MagicMock()
        store.get_all_nodes = AsyncMock(return_value=[node1, node2, node3])
        store.get_neighbors = AsyncMock(return_value=[])
        store.remove_node = AsyncMock()
        store.add_node = AsyncMock()

        return store

    def test_init_with_stores(self, mock_vector_store, mock_graph_store):
        """Test migrator initialization with stores."""
        migrator = MemoryMigrator(
            vector_store=mock_vector_store,
            graph_store=mock_graph_store,
        )

        assert migrator._vector_store is mock_vector_store
        assert migrator._graph_store is mock_graph_store

    def test_init_without_stores(self):
        """Test migrator initialization without stores."""
        migrator = MemoryMigrator()

        assert migrator._vector_store is None
        assert migrator._graph_store is None

    @pytest.mark.asyncio
    async def test_migrate_dry_run(self, mock_vector_store, mock_graph_store):
        """Test migration in dry run mode."""
        migrator = MemoryMigrator(
            vector_store=mock_vector_store,
            graph_store=mock_graph_store,
        )

        report = await migrator.migrate(dry_run=True)

        assert report.dry_run
        # Vectors: 3 scanned, 2 need migration (v1, v3), 1 already has stage (v2)
        assert report.vectors_scanned == 3
        assert report.vectors_migrated == 2
        assert report.vectors_skipped == 1

        # Nodes: 3 scanned, 2 need migration (n1, n3), 1 already migrated (n2)
        assert report.nodes_scanned == 3
        assert report.nodes_migrated == 2
        assert report.nodes_skipped == 1

        # Should NOT actually update anything in dry run
        mock_vector_store.update_metadata.assert_not_called()
        mock_graph_store.remove_node.assert_not_called()

    @pytest.mark.asyncio
    async def test_migrate_execute(self, mock_vector_store, mock_graph_store):
        """Test migration in execute mode."""
        migrator = MemoryMigrator(
            vector_store=mock_vector_store,
            graph_store=mock_graph_store,
        )

        report = await migrator.migrate(dry_run=False)

        assert not report.dry_run
        assert report.vectors_migrated == 2
        assert report.nodes_migrated == 2

        # Should have updated vectors
        assert mock_vector_store.update_metadata.call_count == 2

        # Should have updated nodes (remove + add for each)
        assert mock_graph_store.remove_node.call_count == 2
        assert mock_graph_store.add_node.call_count == 2

    @pytest.mark.asyncio
    async def test_migrate_without_vector_store(self, mock_graph_store):
        """Test migration without vector store."""
        migrator = MemoryMigrator(graph_store=mock_graph_store)

        report = await migrator.migrate(dry_run=True)

        # Should only migrate graph nodes
        assert report.vectors_scanned == 0
        assert report.nodes_scanned == 3
        assert report.nodes_migrated == 2

    @pytest.mark.asyncio
    async def test_migrate_without_graph_store(self, mock_vector_store):
        """Test migration without graph store."""
        migrator = MemoryMigrator(vector_store=mock_vector_store)

        report = await migrator.migrate(dry_run=True)

        # Should only migrate vectors
        assert report.vectors_scanned == 3
        assert report.vectors_migrated == 2
        assert report.nodes_scanned == 0

    @pytest.mark.asyncio
    async def test_check_migration_needed_true(
        self, mock_vector_store, mock_graph_store
    ):
        """Test check_migration_needed returns True when migration needed."""
        migrator = MemoryMigrator(
            vector_store=mock_vector_store,
            graph_store=mock_graph_store,
        )

        needs_migration = await migrator.check_migration_needed()
        assert needs_migration

    @pytest.mark.asyncio
    async def test_check_migration_needed_false(self):
        """Test check_migration_needed returns False when all migrated."""
        # Create store where all items have lifecycle metadata
        vector_store = MagicMock()
        vector_store.get_all = AsyncMock(
            return_value=[
                {"id": "v1", "metadata": {"stage": "long_term"}},
                {"id": "v2", "metadata": {"stage": "short_term"}},
            ]
        )

        node1 = MagicMock()
        node1.id = "n1"
        node1.stage = MemoryStage.LONG_TERM

        graph_store = MagicMock()
        graph_store.get_all_nodes = AsyncMock(return_value=[node1])
        graph_store.get_neighbors = AsyncMock(return_value=[])

        migrator = MemoryMigrator(
            vector_store=vector_store,
            graph_store=graph_store,
        )

        needs_migration = await migrator.check_migration_needed()
        assert not needs_migration

    def test_has_lifecycle_metadata(self):
        """Test _has_lifecycle_metadata detection."""
        migrator = MemoryMigrator()

        # No stage = needs migration
        assert not migrator._has_lifecycle_metadata({})
        assert not migrator._has_lifecycle_metadata({"type": "insight"})

        # Has stage = already migrated
        assert migrator._has_lifecycle_metadata({"stage": "long_term"})
        assert migrator._has_lifecycle_metadata(
            {"stage": "short_term", "type": "insight"}
        )

    def test_add_lifecycle_metadata(self):
        """Test _add_lifecycle_metadata adds correct fields."""
        migrator = MemoryMigrator()

        original = {"type": "insight", "confidence": 0.8}
        updated = migrator._add_lifecycle_metadata(original)

        # Should preserve original fields
        assert updated["type"] == "insight"
        assert updated["confidence"] == 0.8

        # Should add lifecycle fields
        assert updated["stage"] == MemoryStage.LONG_TERM.value
        assert updated["hit_count"] == 0
        assert updated["decay_score"] == 1.0
        assert updated["retrieval_factor"] == 1.0
        assert "migrated_at" in updated

    def test_add_lifecycle_metadata_preserves_hit_count(self):
        """Test _add_lifecycle_metadata preserves existing hit_count."""
        migrator = MemoryMigrator()

        original = {"type": "insight", "hit_count": 5}
        updated = migrator._add_lifecycle_metadata(original)

        # Should preserve existing hit_count
        assert updated["hit_count"] == 5


class TestIdempotentMigration:
    """Test that migration is idempotent (safe to run multiple times)."""

    @pytest.mark.asyncio
    async def test_second_migration_does_nothing(self):
        """Test that running migration twice doesn't double-migrate."""
        # First run: documents without stage
        vector_store = MagicMock()
        vector_store.get_all = AsyncMock(
            return_value=[
                {"id": "v1", "metadata": {"type": "insight"}},
            ]
        )
        vector_store.update_metadata = AsyncMock()

        migrator = MemoryMigrator(vector_store=vector_store)

        # First migration
        report1 = await migrator.migrate(dry_run=False)
        assert report1.vectors_migrated == 1

        # Simulate that vector now has stage after first migration
        vector_store.get_all = AsyncMock(
            return_value=[
                {"id": "v1", "metadata": {"type": "insight", "stage": "long_term"}},
            ]
        )

        # Second migration - should skip already migrated
        report2 = await migrator.migrate(dry_run=False)
        assert report2.vectors_migrated == 0
        assert report2.vectors_skipped == 1

    @pytest.mark.asyncio
    async def test_partial_migration_continues(self):
        """Test that partial migration can be continued."""
        # Simulate some migrated, some not
        vector_store = MagicMock()
        vector_store.get_all = AsyncMock(
            return_value=[
                {"id": "v1", "metadata": {"stage": "long_term"}},  # Already migrated
                {"id": "v2", "metadata": {"type": "insight"}},  # Needs migration
            ]
        )
        vector_store.update_metadata = AsyncMock()

        migrator = MemoryMigrator(vector_store=vector_store)

        report = await migrator.migrate(dry_run=False)

        # Should only migrate the unmigrated one
        assert report.vectors_scanned == 2
        assert report.vectors_migrated == 1
        assert report.vectors_skipped == 1


class TestMigrationErrorHandling:
    """Test error handling in migration."""

    @pytest.mark.asyncio
    async def test_vector_update_error_recorded(self):
        """Test that vector update errors are recorded in report."""
        vector_store = MagicMock()
        vector_store.get_all = AsyncMock(
            return_value=[
                {"id": "v1", "metadata": {}},
            ]
        )
        vector_store.update_metadata = AsyncMock(side_effect=Exception("Update failed"))

        migrator = MemoryMigrator(vector_store=vector_store)

        report = await migrator.migrate(dry_run=False)

        assert len(report.errors) == 1
        assert "v1" in report.errors[0]
        assert "Update failed" in report.errors[0]

    @pytest.mark.asyncio
    async def test_graph_node_error_recorded(self):
        """Test that graph node errors are recorded in report."""
        node = MagicMock()
        node.id = "n1"
        node.stage = None

        graph_store = MagicMock()
        graph_store.get_all_nodes = AsyncMock(return_value=[node])
        graph_store.get_neighbors = AsyncMock(
            return_value=[]
        )  # Empty list of neighbors
        graph_store.remove_node = AsyncMock(side_effect=Exception("Remove failed"))

        migrator = MemoryMigrator(graph_store=graph_store)

        report = await migrator.migrate(dry_run=False)

        assert len(report.errors) == 1
        assert "n1" in report.errors[0]
        assert "Remove failed" in report.errors[0]
