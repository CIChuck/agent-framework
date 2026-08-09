"""Read-only environment preflight for complete reorganization recovery."""

from __future__ import annotations

import os
import shutil
import stat
from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from pydantic import Field

from friday_chat.reorganization.contracts import (
    ReorganizationError,
    ReorganizationErrorCode,
    StrictContractModel,
)
from friday_chat.reorganization.layout import (
    FridayChatMaintenanceLayout,
    validate_declared_paths,
)
from friday_chat.reorganization.lease import (
    DarwinLayoutLeaseRegistry,
    LayoutLeaseError,
)

_MINIMUM_RECOVERY_CAPACITY_BYTES = 64 * 1024 * 1024
_RECOVERY_FIXED_OVERHEAD_BYTES = 16 * 1024 * 1024
_RECOVERY_SOURCE_EXPANSION_AND_STAGING_FACTOR = 12
_MINIMUM_LOG_CAPACITY_BYTES = 1024 * 1024
_MAX_SOURCE_ENTRIES = 100_000


class DiskUsageResult(Protocol):
    """Public structural portion of a filesystem capacity result."""

    @property
    def free(self) -> int: ...


class EnvironmentPreflightReport(StrictContractModel):
    """Content-safe capacity, permission, and platform evidence."""

    supported: bool
    source_size_bytes: int | None = Field(default=None, ge=0)
    required_recovery_bytes: int | None = Field(default=None, ge=0)
    available_recovery_bytes: int | None = Field(default=None, ge=0)
    available_log_bytes: int | None = Field(default=None, ge=0)
    errors: tuple[ReorganizationError, ...] = ()


class MaintenanceEnvironmentPreflight:
    """Fail-closed read-only checks before snapshot or store mutation."""

    def __init__(
        self,
        *,
        disk_usage: Callable[[Path], DiskUsageResult] = shutil.disk_usage,
    ) -> None:
        self._disk_usage = disk_usage

    @staticmethod
    def _error(message: str, *, store: str | None = None) -> ReorganizationError:
        return ReorganizationError(
            code=ReorganizationErrorCode.PREFLIGHT_FAILED,
            message=message,
            store=store,
        )

    @staticmethod
    def _nearest_existing_directory(path: Path) -> Path:
        current = path
        while True:
            try:
                info = current.lstat()
            except FileNotFoundError:
                parent = current.parent
                if parent == current:
                    raise OSError("maintenance path has no existing anchor") from None
                current = parent
                continue
            if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
                raise OSError("maintenance path anchor is not a safe directory")
            return current

    @staticmethod
    def _validate_destination(path: Path) -> None:
        try:
            info = path.lstat()
        except FileNotFoundError:
            anchor = MaintenanceEnvironmentPreflight._nearest_existing_directory(
                path.parent
            )
            if not os.access(anchor, os.W_OK | os.X_OK):
                raise PermissionError(
                    "maintenance destination is not writable"
                ) from None
            return
        if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
            raise OSError("maintenance destination is not a safe directory")
        if not os.access(path, os.W_OK | os.X_OK):
            raise PermissionError("maintenance destination is not writable")
        if os.name == "posix":
            if info.st_uid != os.getuid():
                raise PermissionError("maintenance destination owner differs")
            if stat.S_IMODE(info.st_mode) != 0o700:
                raise PermissionError("maintenance destination is not owner-only")

    @staticmethod
    def _file_size(path: Path, *, optional: bool) -> tuple[int, int]:
        try:
            info = path.lstat()
        except FileNotFoundError:
            if optional:
                return 0, 0
            raise
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
            raise OSError("maintenance source is not a regular file")
        if not os.access(path, os.R_OK):
            raise PermissionError("maintenance source is not readable")
        return info.st_size, 1

    @classmethod
    def _directory_size(cls, path: Path) -> tuple[int, int]:
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise OSError("maintenance source is not a safe directory")
        if not os.access(path, os.R_OK | os.X_OK):
            raise PermissionError("maintenance source directory is not readable")
        total = 0
        entries = 1
        stack = [path]
        while stack:
            directory = stack.pop()
            with os.scandir(directory) as children:
                for child in children:
                    entries += 1
                    if entries > _MAX_SOURCE_ENTRIES:
                        raise OSError("maintenance source exceeds bounded inventory")
                    child_info = child.stat(follow_symlinks=False)
                    if stat.S_ISLNK(child_info.st_mode):
                        raise OSError("maintenance source traverses a symlink")
                    child_path = Path(child.path)
                    if stat.S_ISDIR(child_info.st_mode):
                        if not os.access(child_path, os.R_OK | os.X_OK):
                            raise PermissionError(
                                "maintenance source directory is not readable"
                            )
                        stack.append(child_path)
                    elif stat.S_ISREG(child_info.st_mode):
                        if not os.access(child_path, os.R_OK):
                            raise PermissionError(
                                "maintenance source file is not readable"
                            )
                        total += child_info.st_size
                    else:
                        raise OSError("maintenance source contains a special file")
        return total, entries

    @classmethod
    def _source_size(cls, layout: FridayChatMaintenanceLayout) -> int:
        total, entries = cls._directory_size(layout.vector_directory)
        size, count = cls._file_size(layout.graph_path, optional=True)
        total += size
        entries += count
        for transcript_path in (
            layout.transcript_database_path,
            Path(f"{layout.transcript_database_path}-wal"),
            Path(f"{layout.transcript_database_path}-shm"),
        ):
            size, count = cls._file_size(
                transcript_path,
                optional=transcript_path != layout.transcript_database_path,
            )
            total += size
            entries += count
        if layout.access_buffer_wal_path is not None:
            size, count = cls._file_size(
                layout.access_buffer_wal_path,
                optional=True,
            )
            total += size
            entries += count
        if entries > _MAX_SOURCE_ENTRIES:
            raise OSError("maintenance source exceeds bounded inventory")
        return total

    def inspect(
        self,
        layout: FridayChatMaintenanceLayout,
        lease_registry: DarwinLayoutLeaseRegistry,
    ) -> EnvironmentPreflightReport:
        """Inspect without creating any destination, lease, journal, or log."""
        errors: list[ReorganizationError] = []
        source_size: int | None = None
        required: int | None = None
        recovery_free: int | None = None
        log_free: int | None = None
        try:
            validate_declared_paths(layout.all_declared_paths)
            lease_registry.validate_capability(layout)
        except (LayoutLeaseError, OSError, ValueError) as exc:
            errors.append(
                self._error(
                    f"maintenance layout or platform preflight failed ({type(exc).__name__})"
                )
            )
        for destination, label in (
            (layout.recovery_root, "recovery"),
            (layout.log_root, "log"),
        ):
            try:
                self._validate_destination(destination)
            except (OSError, ValueError) as exc:
                errors.append(
                    self._error(
                        f"maintenance {label} destination preflight failed ({type(exc).__name__})"
                    )
                )
        try:
            source_size = self._source_size(layout)
            required = max(
                _MINIMUM_RECOVERY_CAPACITY_BYTES,
                source_size * _RECOVERY_SOURCE_EXPANSION_AND_STAGING_FACTOR
                + _RECOVERY_FIXED_OVERHEAD_BYTES,
            )
        except (OSError, ValueError) as exc:
            errors.append(
                self._error(
                    f"maintenance source permission or inventory preflight failed ({type(exc).__name__})"
                )
            )
        try:
            recovery_anchor = self._nearest_existing_directory(layout.recovery_root)
            recovery_free = self._disk_usage(recovery_anchor).free
            if required is not None and recovery_free < required:
                errors.append(
                    self._error(
                        "insufficient capacity for complete recovery and staging"
                    )
                )
        except OSError as exc:
            errors.append(
                self._error(
                    f"recovery capacity preflight failed ({type(exc).__name__})"
                )
            )
        try:
            log_anchor = self._nearest_existing_directory(layout.log_root)
            log_free = self._disk_usage(log_anchor).free
            if log_free < _MINIMUM_LOG_CAPACITY_BYTES:
                errors.append(self._error("insufficient capacity for maintenance log"))
        except OSError as exc:
            errors.append(
                self._error(f"log capacity preflight failed ({type(exc).__name__})")
            )
        return EnvironmentPreflightReport(
            supported=not errors,
            source_size_bytes=source_size,
            required_recovery_bytes=required,
            available_recovery_bytes=recovery_free,
            available_log_bytes=log_free,
            errors=tuple(errors),
        )


__all__ = [
    "EnvironmentPreflightReport",
    "MaintenanceEnvironmentPreflight",
]
