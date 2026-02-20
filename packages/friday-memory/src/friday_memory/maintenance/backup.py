"""
Backup Manager for Friday Memory.

Handles creating and restoring backups of all memory stores:
- Graph store (graph.json)
- Vector store (chroma.sqlite3, data_level0.bin, etc.)
- Episodic store (transcript.db)
"""

import hashlib
import json
import logging
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from friday_memory.maintenance.models import BackupManifest

logger = logging.getLogger(__name__)


class BackupManager:
    """
    Manages backup and restore operations for memory stores.

    Creates timestamped backups with checksums for integrity verification.
    Supports atomic restore operations.

    Example:
        manager = BackupManager(memory_dir="./memory")
        manifest = manager.create_backup()
        # ... do dangerous operations ...
        manager.restore_backup(manifest)  # Revert if needed
    """

    # Files to back up (relative to memory_dir)
    MEMORY_FILES = [
        "graph.json",
        "transcript.db",
        # ChromaDB files
        "chroma.sqlite3",
        "data_level0.bin",
        "header.bin",
        "index_metadata.json",
        "length.bin",
        "link_lists.bin",
    ]

    # ChromaDB subdirectory pattern (may have UUID-named folders)
    CHROMA_SUBDIRS = ["vector"]

    def __init__(
        self,
        memory_dir: str | Path,
        backup_root: str | Path | None = None,
    ) -> None:
        """
        Initialize the backup manager.

        Args:
            memory_dir: Directory containing memory stores
            backup_root: Where to store backups (default: memory_dir/backups)
        """
        self._memory_dir = Path(memory_dir)
        self._backup_root = (
            Path(backup_root) if backup_root else self._memory_dir / "backups"
        )

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _get_store_stats(self) -> dict[str, Any]:
        """Gather statistics about the current memory stores."""
        stats: dict[str, Any] = {
            "graph": {"exists": False},
            "vector": {"exists": False},
            "episodic": {"exists": False},
        }

        # Graph stats
        graph_path = self._memory_dir / "graph.json"
        if graph_path.exists():
            try:
                with open(graph_path) as f:
                    data = json.load(f)
                stats["graph"] = {
                    "exists": True,
                    "node_count": len(data.get("nodes", {})),
                    "edge_count": len(data.get("edges", [])),
                    "file_size": graph_path.stat().st_size,
                }
            except Exception as e:
                stats["graph"]["error"] = str(e)

        # Vector store stats (ChromaDB)
        # Try both possible locations
        for vector_dir in [self._memory_dir, self._memory_dir / "vector"]:
            chroma_db = vector_dir / "chroma.sqlite3"
            if chroma_db.exists():
                stats["vector"] = {
                    "exists": True,
                    "file_size": chroma_db.stat().st_size,
                }
                # Count ChromaDB files in this dir
                chroma_files = [
                    "chroma.sqlite3",
                    "data_level0.bin",
                    "header.bin",
                    "index_metadata.json",
                    "length.bin",
                    "link_lists.bin",
                ]
                file_count = sum(1 for f in chroma_files if (vector_dir / f).exists())
                stats["vector"]["file_count"] = file_count
                break

        # Episodic stats
        transcript_path = self._memory_dir / "vector" / "transcript.db"
        if not transcript_path.exists():
            transcript_path = self._memory_dir / "transcript.db"
        if transcript_path.exists():
            stats["episodic"] = {
                "exists": True,
                "file_size": transcript_path.stat().st_size,
            }

        return stats

    def _find_files_to_backup(self) -> list[Path]:
        """Find all memory files that should be backed up."""
        files: list[Path] = []

        # Check root-level files
        for filename in self.MEMORY_FILES:
            file_path = self._memory_dir / filename
            if file_path.exists():
                files.append(file_path)

        # Check ChromaDB subdirectories
        for subdir_name in self.CHROMA_SUBDIRS:
            subdir = self._memory_dir / subdir_name
            if subdir.exists() and subdir.is_dir():
                # Add all files recursively
                for file_path in subdir.rglob("*"):
                    if file_path.is_file():
                        files.append(file_path)

        return files

    def create_backup(self, backup_dir: str | Path | None = None) -> BackupManifest:
        """
        Create a backup of all memory stores.

        Args:
            backup_dir: Optional specific backup directory.
                       If None, creates timestamped directory.

        Returns:
            BackupManifest with backup details

        Raises:
            FileNotFoundError: If memory directory doesn't exist
            IOError: If backup fails
        """
        if not self._memory_dir.exists():
            raise FileNotFoundError(f"Memory directory not found: {self._memory_dir}")

        # Create backup directory
        if backup_dir:
            backup_path = Path(backup_dir)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_id = str(uuid.uuid4())[:8]
            backup_path = self._backup_root / f"{timestamp}_{backup_id}"

        backup_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating backup at: {backup_path}")

        # Find files to backup
        files_to_backup = self._find_files_to_backup()

        if not files_to_backup:
            logger.warning("No memory files found to backup")

        # Copy files and calculate checksums
        file_mapping: dict[str, str] = {}
        checksums: dict[str, str] = {}

        for source_file in files_to_backup:
            # Preserve directory structure relative to memory_dir
            relative_path = source_file.relative_to(self._memory_dir)
            dest_file = backup_path / relative_path

            # Create parent directories
            dest_file.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(source_file, dest_file)

            # Store mapping and checksum
            file_mapping[str(source_file)] = str(dest_file)
            checksums[str(relative_path)] = self._calculate_checksum(dest_file)

            logger.debug(f"Backed up: {relative_path}")

        # Gather stats
        store_stats = self._get_store_stats()

        # Create manifest
        manifest = BackupManifest(
            backup_id=str(uuid.uuid4()),
            created_at=datetime.now(),
            source_dir=str(self._memory_dir),
            backup_dir=str(backup_path),
            files=file_mapping,
            checksums=checksums,
            store_stats=store_stats,
        )

        # Write manifest to backup directory
        manifest_path = backup_path / "manifest.json"
        manifest_path.write_text(manifest.model_dump_json(indent=2))

        logger.info(
            f"Backup complete: {len(file_mapping)} files, "
            f"backup_id={manifest.backup_id[:8]}"
        )

        return manifest

    def verify_backup(self, manifest: BackupManifest) -> tuple[bool, list[str]]:
        """
        Verify backup integrity using checksums.

        Args:
            manifest: The backup manifest to verify

        Returns:
            Tuple of (success, list of error messages)
        """
        errors: list[str] = []
        backup_path = Path(manifest.backup_dir)

        if not backup_path.exists():
            return False, [f"Backup directory not found: {backup_path}"]

        for relative_path, expected_checksum in manifest.checksums.items():
            file_path = backup_path / relative_path

            if not file_path.exists():
                errors.append(f"Missing file: {relative_path}")
                continue

            actual_checksum = self._calculate_checksum(file_path)
            if actual_checksum != expected_checksum:
                errors.append(
                    f"Checksum mismatch for {relative_path}: "
                    f"expected {expected_checksum[:8]}..., "
                    f"got {actual_checksum[:8]}..."
                )

        return len(errors) == 0, errors

    def restore_backup(
        self,
        manifest: BackupManifest,
        verify_first: bool = True,
    ) -> bool:
        """
        Restore memory stores from a backup.

        Args:
            manifest: The backup manifest to restore from
            verify_first: Whether to verify checksums before restore

        Returns:
            True if restore successful

        Raises:
            ValueError: If backup verification fails
            IOError: If restore fails
        """
        backup_path = Path(manifest.backup_dir)

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup directory not found: {backup_path}")

        # Verify backup integrity
        if verify_first:
            valid, errors = self.verify_backup(manifest)
            if not valid:
                raise ValueError(f"Backup verification failed: {errors}")

        logger.info(f"Restoring from backup: {manifest.backup_id[:8]}")

        # Restore files
        restored_count = 0
        for relative_path in manifest.checksums:
            source_file = backup_path / relative_path
            dest_file = self._memory_dir / relative_path

            if not source_file.exists():
                logger.warning(f"Backup file missing: {relative_path}")
                continue

            # Create parent directories
            dest_file.parent.mkdir(parents=True, exist_ok=True)

            # Copy file back
            shutil.copy2(source_file, dest_file)
            restored_count += 1

            logger.debug(f"Restored: {relative_path}")

        logger.info(f"Restore complete: {restored_count} files restored")

        return True

    def list_backups(self) -> list[BackupManifest]:
        """
        List all available backups.

        Returns:
            List of BackupManifest objects, sorted by creation time (newest first)
        """
        backups: list[BackupManifest] = []

        if not self._backup_root.exists():
            return backups

        for backup_dir in self._backup_root.iterdir():
            if not backup_dir.is_dir():
                continue

            manifest_path = backup_dir / "manifest.json"
            if not manifest_path.exists():
                continue

            try:
                manifest_data = json.loads(manifest_path.read_text())
                manifest = BackupManifest.model_validate(manifest_data)
                backups.append(manifest)
            except Exception as e:
                logger.warning(f"Failed to load manifest from {backup_dir}: {e}")

        # Sort by creation time, newest first
        backups.sort(key=lambda m: m.created_at, reverse=True)

        return backups

    def delete_backup(self, manifest: BackupManifest) -> bool:
        """
        Delete a backup.

        Args:
            manifest: The backup to delete

        Returns:
            True if deleted successfully
        """
        backup_path = Path(manifest.backup_dir)

        if not backup_path.exists():
            logger.warning(f"Backup directory not found: {backup_path}")
            return False

        shutil.rmtree(backup_path)
        logger.info(f"Deleted backup: {manifest.backup_id[:8]}")

        return True

    def cleanup_old_backups(self, keep_count: int = 5) -> int:
        """
        Remove old backups, keeping only the most recent ones.

        Args:
            keep_count: Number of backups to keep

        Returns:
            Number of backups deleted
        """
        backups = self.list_backups()

        if len(backups) <= keep_count:
            return 0

        deleted_count = 0
        for backup in backups[keep_count:]:
            if self.delete_backup(backup):
                deleted_count += 1

        logger.info(f"Cleaned up {deleted_count} old backups")
        return deleted_count
