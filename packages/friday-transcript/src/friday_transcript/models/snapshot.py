"""Typed contracts for WAL-safe transcript recovery snapshots."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictSnapshotModel(BaseModel):
    """Reject unknown fields in persisted and externally validated records."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class TranscriptSnapshotStrategy(str, Enum):
    """Supported transcript snapshot implementation."""

    SQLITE_ONLINE_BACKUP = "sqlite_online_backup"


class TranscriptSnapshotStatus(str, Enum):
    """Outcome of a transcript recovery operation."""

    COMPLETED = "completed"
    FAILED = "failed"


class TranscriptRecoveryErrorCode(str, Enum):
    """Stable, content-safe transcript recovery error categories."""

    INVALID_PATH = "invalid_path"
    INVALID_QUIESCENCE = "invalid_quiescence"
    SOURCE_ABSENT = "source_absent"
    SNAPSHOT_INCOMPLETE = "snapshot_incomplete"
    CHECKSUM_MISMATCH = "checksum_mismatch"
    SCHEMA_MISMATCH = "schema_mismatch"
    INTEGRITY_FAILED = "integrity_failed"
    RESTORE_FAILED = "restore_failed"


class TranscriptRecoveryErrorDetail(StrictSnapshotModel):
    """Typed error without transcript content."""

    code: TranscriptRecoveryErrorCode
    message: str


class TranscriptIntegrityResult(StrictSnapshotModel):
    """SQLite integrity and schema verification evidence."""

    integrity_ok: bool
    foreign_keys_ok: bool
    schema_fingerprint: str
    page_count: int = Field(ge=0)

    @property
    def verified(self) -> bool:
        """Return whether all integrity requirements passed."""
        return self.integrity_ok and self.foreign_keys_ok


class TranscriptSnapshotManifest(StrictSnapshotModel):
    """Versioned persisted manifest for one online SQLite backup."""

    schema_version: Literal[1] = 1
    created_at: datetime
    strategy: TranscriptSnapshotStrategy = (
        TranscriptSnapshotStrategy.SQLITE_ONLINE_BACKUP
    )
    source_path: str
    artifact_filename: str
    artifact_sha256: str
    artifact_size_bytes: int = Field(ge=0)
    schema_fingerprint: str
    page_count: int = Field(ge=0)
    verified: bool


class TranscriptSnapshotResult(StrictSnapshotModel):
    """Typed result for transcript snapshot, verify, restore, and live checks."""

    status: TranscriptSnapshotStatus
    manifest_path: Path | None = None
    integrity: TranscriptIntegrityResult | None = None
    verified: bool
    errors: list[TranscriptRecoveryErrorDetail] = Field(default_factory=list)


class TranscriptRestoreQuiescenceToken:
    """Opaque token proving the issuing transcript store holds its write gate."""

    __slots__ = ("_issuer_id", "_source_fingerprint", "_nonce")

    def __init__(self, issuer_id: str, source_fingerprint: str, nonce: str) -> None:
        self._issuer_id = issuer_id
        self._source_fingerprint = source_fingerprint
        self._nonce = nonce
