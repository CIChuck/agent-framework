"""Resolved, immutable maintenance layout identity for Friday Chat."""

from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path
from typing import Literal

from pydantic import model_validator

from friday_chat.reorganization.contracts import (
    LeaseTarget,
    LiveTargetKind,
    StrictContractModel,
)


class MaintenanceLayoutError(ValueError):
    """Raised when configured maintenance paths are unsafe or ambiguous."""


def _normalize_path(value: str | Path, captured_cwd: Path) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = captured_cwd / candidate
    return Path(os.path.abspath(os.path.normpath(os.fspath(candidate))))


def _reject_symlink_traversal(path: Path) -> None:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        parent = current
        current = parent / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            return
        except OSError as exc:
            raise MaintenanceLayoutError(
                "maintenance path identity cannot be inspected"
            ) from exc
        if stat.S_ISLNK(info.st_mode):
            raise MaintenanceLayoutError("maintenance paths cannot traverse symlinks")
        try:
            with os.scandir(parent) as entries:
                if not any(entry.name == part for entry in entries):
                    raise MaintenanceLayoutError(
                        "maintenance path component spelling is not canonical"
                    )
        except MaintenanceLayoutError:
            raise
        except OSError as exc:
            raise MaintenanceLayoutError(
                "maintenance path identity cannot be inspected"
            ) from exc


def _paths_overlap(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def _same_existing_inode(left: Path, right: Path) -> bool:
    try:
        left_info = left.stat(follow_symlinks=False)
        right_info = right.stat(follow_symlinks=False)
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise MaintenanceLayoutError(
            "maintenance path identity cannot be inspected"
        ) from exc
    return (left_info.st_dev, left_info.st_ino) == (
        right_info.st_dev,
        right_info.st_ino,
    )


class FridayChatMaintenanceLayout(StrictContractModel):
    """All live and external maintenance paths resolved against one cwd."""

    schema_version: Literal[1] = 1
    captured_process_cwd: Path
    vector_directory: Path
    graph_path: Path
    access_buffer_wal_path: Path | None = None
    transcript_database_path: Path
    recovery_root: Path
    log_root: Path
    layout_fingerprint: str

    @classmethod
    def resolve_once(
        cls,
        *,
        captured_process_cwd: str | Path,
        vector_directory: str | Path,
        graph_path: str | Path,
        access_buffer_wal_path: str | Path | None,
        transcript_database_path: str | Path,
        recovery_root: str | Path,
        log_root: str | Path,
    ) -> FridayChatMaintenanceLayout:
        """Resolve every relative path against the same captured process cwd."""
        captured = Path(captured_process_cwd)
        if not captured.is_absolute():
            raise MaintenanceLayoutError("captured process cwd must be absolute")
        captured = Path(os.path.abspath(os.path.normpath(os.fspath(captured))))
        vector = _normalize_path(vector_directory, captured)
        graph = _normalize_path(graph_path, captured)
        access_wal = (
            _normalize_path(access_buffer_wal_path, captured)
            if access_buffer_wal_path is not None
            else None
        )
        transcript = _normalize_path(transcript_database_path, captured)
        recovery = _normalize_path(recovery_root, captured)
        logs = _normalize_path(log_root, captured)
        values = {
            "captured_process_cwd": captured,
            "vector_directory": vector,
            "graph_path": graph,
            "access_buffer_wal_path": access_wal,
            "transcript_database_path": transcript,
            "recovery_root": recovery,
            "log_root": logs,
        }
        fingerprint = cls._fingerprint_for(values)
        return cls(
            captured_process_cwd=captured,
            vector_directory=vector,
            graph_path=graph,
            access_buffer_wal_path=access_wal,
            transcript_database_path=transcript,
            recovery_root=recovery,
            log_root=logs,
            layout_fingerprint=fingerprint,
        )

    @property
    def live_targets(self) -> tuple[LeaseTarget, ...]:
        """Return the deterministic target set used for overlap locking."""
        targets = [
            LeaseTarget(kind=LiveTargetKind.VECTOR, path=self.vector_directory),
            LeaseTarget(kind=LiveTargetKind.GRAPH, path=self.graph_path),
            LeaseTarget(
                kind=LiveTargetKind.TRANSCRIPT,
                path=self.transcript_database_path,
            ),
        ]
        if self.access_buffer_wal_path is not None:
            targets.append(
                LeaseTarget(
                    kind=LiveTargetKind.ACCESS_WAL,
                    path=self.access_buffer_wal_path,
                )
            )
        return tuple(sorted(targets, key=lambda target: target.kind.value))

    @property
    def all_declared_paths(self) -> tuple[Path, ...]:
        """Return live targets plus roots bound into layout identity."""
        return (
            *(target.path for target in self.live_targets),
            self.recovery_root,
            self.log_root,
        )

    @model_validator(mode="after")
    def validate_layout_identity(self) -> FridayChatMaintenanceLayout:
        """Reject path traversal, aliasing, overlap, and fingerprint drift."""
        if not self.captured_process_cwd.is_absolute():
            raise ValueError("captured process cwd must be absolute")
        for path in (self.captured_process_cwd, *self.all_declared_paths):
            if not path.is_absolute() or path == Path(path.anchor):
                raise ValueError("maintenance paths must be absolute and bounded")
            _reject_symlink_traversal(path)
        paths = self.all_declared_paths
        for index, left in enumerate(paths):
            for right in paths[index + 1 :]:
                if _paths_overlap(left, right) or _same_existing_inode(left, right):
                    raise ValueError("maintenance paths alias or overlap")
        values = {
            "captured_process_cwd": self.captured_process_cwd,
            "vector_directory": self.vector_directory,
            "graph_path": self.graph_path,
            "access_buffer_wal_path": self.access_buffer_wal_path,
            "transcript_database_path": self.transcript_database_path,
            "recovery_root": self.recovery_root,
            "log_root": self.log_root,
        }
        if self.layout_fingerprint != self._fingerprint_for(values):
            raise ValueError("maintenance layout fingerprint does not match paths")
        return self

    @staticmethod
    def _fingerprint_for(values: dict[str, Path | None]) -> str:
        payload = {
            "schema_version": 1,
            **{
                key: os.fspath(value) if value is not None else None
                for key, value in sorted(values.items())
                if key != "captured_process_cwd"
            },
        }
        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()


def live_targets_overlap(
    left: tuple[LeaseTarget, ...],
    right: tuple[LeaseTarget, ...],
) -> bool:
    """Return whether two declared layouts share or nest any live target."""
    return any(
        _paths_overlap(left_target.path, right_target.path)
        or _same_existing_inode(left_target.path, right_target.path)
        for left_target in left
        for right_target in right
    )


def validate_live_target_identities(targets: tuple[LeaseTarget, ...]) -> None:
    """Revalidate symlink and within-layout alias state at lease boundaries."""
    for target in targets:
        _reject_symlink_traversal(target.path)
    for index, left in enumerate(targets):
        for right in targets[index + 1 :]:
            if _paths_overlap(left.path, right.path) or _same_existing_inode(
                left.path,
                right.path,
            ):
                raise MaintenanceLayoutError("live maintenance targets alias or overlap")


def validate_declared_paths(paths: tuple[Path, ...]) -> None:
    """Revalidate traversal, overlap, and inode identity before an operation."""
    for path in paths:
        _reject_symlink_traversal(path)
    for index, left in enumerate(paths):
        for right in paths[index + 1 :]:
            if _paths_overlap(left, right) or _same_existing_inode(left, right):
                raise MaintenanceLayoutError(
                    "maintenance paths alias or overlap"
                )
