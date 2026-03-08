# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
# mypy: disallow-untyped-defs=False
"""Tests for BackupManager."""

import json
from pathlib import Path

from friday_memory.maintenance.backup import BackupManager


class TestBackupManager:
    """Test backup and restore operations."""

    def test_create_backup(self, clean_memory_dir) -> None:
        """Test creating a backup."""
        manager = BackupManager(clean_memory_dir)
        manifest = manager.create_backup()

        assert manifest.backup_id
        assert manifest.source_dir == str(clean_memory_dir)
        assert Path(manifest.backup_dir).exists()
        assert len(manifest.files) > 0
        assert len(manifest.checksums) > 0

        # Verify manifest file was written
        manifest_path = Path(manifest.backup_dir) / "manifest.json"
        assert manifest_path.exists()

    def test_backup_creates_checksums(self, clean_memory_dir) -> None:
        """Test that checksums are created for all files."""
        manager = BackupManager(clean_memory_dir)
        manifest = manager.create_backup()

        for relative_path, checksum in manifest.checksums.items():
            assert len(checksum) == 64  # SHA256 hex digest length
            # Verify file exists in backup
            backup_file = Path(manifest.backup_dir) / relative_path
            assert backup_file.exists()

    def test_verify_backup(self, clean_memory_dir) -> None:
        """Test backup verification."""
        manager = BackupManager(clean_memory_dir)
        manifest = manager.create_backup()

        valid, errors = manager.verify_backup(manifest)
        assert valid
        assert len(errors) == 0

    def test_verify_corrupted_backup(self, clean_memory_dir) -> None:
        """Test that verification fails for corrupted backup."""
        manager = BackupManager(clean_memory_dir)
        manifest = manager.create_backup()

        # Corrupt a file
        backup_graph = Path(manifest.backup_dir) / "graph.json"
        if backup_graph.exists():
            backup_graph.write_text("corrupted data")

            valid, errors = manager.verify_backup(manifest)
            assert not valid
            assert len(errors) > 0

    def test_restore_backup(self, clean_memory_dir) -> None:
        """Test restoring from backup."""
        manager = BackupManager(clean_memory_dir)

        # Create backup
        manifest = manager.create_backup()

        # Modify original file
        graph_path = clean_memory_dir / "graph.json"
        original_data = json.loads(graph_path.read_text())
        graph_path.write_text('{"nodes": {}, "edges": []}')

        # Restore
        result = manager.restore_backup(manifest)
        assert result

        # Verify restoration
        restored_data = json.loads(graph_path.read_text())
        assert restored_data == original_data

    def test_list_backups(self, clean_memory_dir) -> None:
        """Test listing available backups."""
        manager = BackupManager(clean_memory_dir)

        # Initially no backups
        backups = manager.list_backups()
        assert len(backups) == 0

        # Create backups
        manager.create_backup()
        manifest2 = manager.create_backup()

        backups = manager.list_backups()
        assert len(backups) == 2

        # Should be sorted newest first
        assert backups[0].backup_id == manifest2.backup_id

    def test_delete_backup(self, clean_memory_dir) -> None:
        """Test deleting a backup."""
        manager = BackupManager(clean_memory_dir)
        manifest = manager.create_backup()

        backup_path = Path(manifest.backup_dir)
        assert backup_path.exists()

        result = manager.delete_backup(manifest)
        assert result
        assert not backup_path.exists()

    def test_cleanup_old_backups(self, clean_memory_dir) -> None:
        """Test cleaning up old backups."""
        manager = BackupManager(clean_memory_dir)

        # Create 5 backups
        for _ in range(5):
            manager.create_backup()

        assert len(manager.list_backups()) == 5

        # Keep only 2
        deleted = manager.cleanup_old_backups(keep_count=2)
        assert deleted == 3
        assert len(manager.list_backups()) == 2

    def test_backup_empty_directory(self, temp_memory_dir) -> None:
        """Test backup of directory with no memory files."""
        manager = BackupManager(temp_memory_dir)
        manifest = manager.create_backup()

        # Should succeed but with no files
        assert manifest.backup_id
        assert len(manifest.files) == 0

    def test_backup_preserves_directory_structure(self, memory_with_issues) -> None:
        """Test that backup preserves subdirectory structure."""
        manager = BackupManager(memory_with_issues)
        manifest = manager.create_backup()

        # Check that vector subdirectory structure is preserved
        backup_path = Path(manifest.backup_dir)
        backup_path / "vector"

        # transcript.db should be in vector/
        for rel_path in manifest.checksums:
            if "transcript.db" in rel_path:
                assert "vector" in rel_path
