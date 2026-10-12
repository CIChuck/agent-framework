"""Typed contracts for Friday Memory recovery snapshots."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Final, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    field_validator,
    model_validator,
)

# Chroma 1.4.0 persists embeddings as float32 and its public cosine collection
# add/get round trip can move a coordinate by up to two float32 ULPs.  The
# original exported coordinates remain checksum-protected in the artifact;
# this fixed, persisted policy applies only when comparing a public-API rebuild
# or live restored collection with that artifact.
CHROMA_REBUILD_MAXIMUM_FLOAT32_ULP_DRIFT: Final[Literal[2]] = 2


class StrictRecoveryModel(BaseModel):
    """Reject unknown fields in persisted and externally validated records."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class MemoryStoreKind(str, Enum):
    """Persistent Friday Memory components covered by recovery."""

    VECTOR = "vector"
    GRAPH = "graph"
    ACCESS_BUFFER = "access_buffer"


class StoreDiscoveryState(str, Enum):
    """Closed discovery states used by recovery preflight."""

    PRESENT = "present"
    NOT_CONFIGURED = "not_configured"
    CONFIGURED_ABSENT = "configured_absent"
    UNSUPPORTED = "unsupported"
    INCOMPLETE = "incomplete"
    CORRUPT = "corrupt"


class MemoryRecoveryOperation(str, Enum):
    """Operations requiring an opaque participant quiescence token."""

    SNAPSHOT = "snapshot"
    RESTORE = "restore"


class MemorySnapshotStrategy(str, Enum):
    """Supported vector recovery mechanism."""

    CHROMA_LOGICAL_EXPORT_REBUILD = "chroma_logical_export_rebuild"


class AccessBufferRecoveryStrategy(str, Enum):
    """Supported representation of access-buffer recovery state."""

    NOT_CONFIGURED = "not_configured"
    DRAINED_INTO_VECTOR = "drained_into_vector"


class MemoryOperationStatus(str, Enum):
    """Outcome of a snapshot, verification, restore, or integrity operation."""

    COMPLETED = "completed"
    FAILED = "failed"


class MemoryRecoveryErrorCode(str, Enum):
    """Stable, content-safe error categories for recovery operations."""

    INVALID_LAYOUT = "invalid_layout"
    INVALID_QUIESCENCE = "invalid_quiescence"
    STORE_ABSENT = "store_absent"
    STORE_UNSUPPORTED = "store_unsupported"
    STORE_INCOMPLETE = "store_incomplete"
    STORE_CORRUPT = "store_corrupt"
    SNAPSHOT_INCOMPLETE = "snapshot_incomplete"
    CHECKSUM_MISMATCH = "checksum_mismatch"
    SCHEMA_MISMATCH = "schema_mismatch"
    LAYOUT_MISMATCH = "layout_mismatch"
    RESTORE_FAILED = "restore_failed"
    INTEGRITY_FAILED = "integrity_failed"


class MemoryMaintenanceLayout(StrictRecoveryModel):
    """Explicit normalized paths for all Friday Memory maintenance state."""

    vector_directory: Path
    graph_path: Path
    access_buffer_wal_path: Path | None = None
    recovery_directory: Path
    log_directory: Path

    @field_validator(
        "vector_directory",
        "graph_path",
        "access_buffer_wal_path",
        "recovery_directory",
        "log_directory",
        mode="before",
    )
    @classmethod
    def resolve_from_process_working_directory(
        cls, value: str | Path | None
    ) -> Path | None:
        """Preserve the existing cwd base for relative configuration paths."""
        if value is None:
            return None
        return Path(value).resolve(strict=False)


class LegacySingleRootLayoutAdapter:
    """Explicitly map a legacy root without guessing historical filenames."""

    @staticmethod
    def adapt(
        root: str | Path,
        *,
        vector_path: str | Path,
        graph_path: str | Path,
        access_buffer_wal_path: str | Path | None,
        recovery_path: str | Path,
        log_path: str | Path,
        base_directory: str | Path | None = None,
    ) -> MemoryMaintenanceLayout:
        """Build a layout from caller-declared legacy relative paths."""
        base = (
            Path(base_directory).resolve(strict=False)
            if base_directory is not None
            else Path.cwd().resolve(strict=False)
        )
        root_path = Path(root)
        normalized_root = (
            root_path.resolve(strict=False)
            if root_path.is_absolute()
            else (base / root_path).resolve(strict=False)
        )

        def join(explicit_path: str | Path) -> Path:
            candidate = Path(explicit_path)
            if candidate.is_absolute():
                return candidate.resolve(strict=False)
            return (normalized_root / candidate).resolve(strict=False)

        return MemoryMaintenanceLayout(
            vector_directory=join(vector_path),
            graph_path=join(graph_path),
            access_buffer_wal_path=(
                join(access_buffer_wal_path)
                if access_buffer_wal_path is not None
                else None
            ),
            recovery_directory=join(recovery_path),
            log_directory=join(log_path),
        )


class MemoryRecoveryErrorDetail(StrictRecoveryModel):
    """Typed, content-safe recovery error."""

    code: MemoryRecoveryErrorCode
    store: MemoryStoreKind | None = None
    message: str


class StoreDiscovery(StrictRecoveryModel):
    """Discovery result for one configured persistent component."""

    store: MemoryStoreKind
    state: StoreDiscoveryState
    normalized_path: str | None = None
    item_count: int | None = Field(default=None, ge=0)
    detail: str | None = None


class MemoryDiscoveryReport(StrictRecoveryModel):
    """Aggregate participant discovery and capability report."""

    schema_version: Literal[1] = 1
    layout_fingerprint: str
    stores: list[StoreDiscovery]
    snapshot_supported: bool
    errors: list[MemoryRecoveryErrorDetail] = Field(default_factory=list)


class VectorRecordSnapshot(StrictRecoveryModel):
    """Exact logical Chroma record used for public-API rebuild."""

    id: str
    document: str | None = None
    metadata: dict[str, JsonValue] | None = None
    embedding: list[float]
    uri: str | None = None


class ChromaCollectionSnapshot(StrictRecoveryModel):
    """Complete logical content and public configuration for one collection."""

    name: str
    metadata: dict[str, JsonValue] | None = None
    configuration: dict[str, JsonValue]
    collection_schema: dict[str, JsonValue]
    records: list[VectorRecordSnapshot]


class ChromaLogicalSnapshot(StrictRecoveryModel):
    """Versioned persisted artifact containing every Chroma collection."""

    schema_version: Literal[1] = 1
    strategy: MemorySnapshotStrategy = (
        MemorySnapshotStrategy.CHROMA_LOGICAL_EXPORT_REBUILD
    )
    collections: list[ChromaCollectionSnapshot]


class ChromaCollectionManifest(StrictRecoveryModel):
    """Content-safe collection evidence retained in the memory manifest."""

    name: str
    record_count: int = Field(ge=0)
    logical_digest: str
    query_probe_count: int = Field(ge=0)


class VectorSnapshotManifest(StrictRecoveryModel):
    """Manifest entry for the exact artifact and bounded rebuild equivalence."""

    state: StoreDiscoveryState
    strategy: MemorySnapshotStrategy
    artifact_filename: str
    artifact_sha256: str
    artifact_size_bytes: int = Field(ge=0)
    maximum_float32_ulp_drift: Literal[2]
    collections: list[ChromaCollectionManifest]


class GraphSnapshotManifest(StrictRecoveryModel):
    """Manifest entry for the exact graph persistence artifact."""

    state: StoreDiscoveryState
    artifact_filename: str | None = None
    artifact_sha256: str | None = None
    artifact_size_bytes: int | None = Field(default=None, ge=0)
    node_count: int = Field(ge=0)
    edge_count: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_state_representation(self) -> Self:
        """Represent either a checksummed artifact or exact configured absence."""
        artifacts = (
            self.artifact_filename,
            self.artifact_sha256,
            self.artifact_size_bytes,
        )
        if self.state is StoreDiscoveryState.PRESENT:
            if any(value is None for value in artifacts):
                raise ValueError("present graph state requires a complete artifact")
            return self
        if self.state is StoreDiscoveryState.CONFIGURED_ABSENT:
            if any(value is not None for value in artifacts):
                raise ValueError("absent graph state cannot name an artifact")
            if self.node_count != 0 or self.edge_count != 0:
                raise ValueError("absent graph state must have zero content counts")
            return self
        raise ValueError("graph snapshot state must be present or configured absent")


class AccessBufferSnapshotManifest(StrictRecoveryModel):
    """Evidence that access effects were drained into the vector snapshot."""

    state: StoreDiscoveryState
    strategy: AccessBufferRecoveryStrategy
    wal_configured: bool
    buffered_item_count: int = Field(ge=0)
    wal_size_bytes: int = Field(ge=0)


class MemorySnapshotManifest(StrictRecoveryModel):
    """Versioned Friday Memory recovery manifest."""

    schema_version: Literal[1] = 1
    run_id: str
    created_at: datetime
    layout_fingerprint: str
    vector_source: str
    graph_source: str
    access_buffer_wal_source: str | None = None
    vector: VectorSnapshotManifest
    graph: GraphSnapshotManifest
    access_buffer: AccessBufferSnapshotManifest
    verified: bool


class MemoryOperationResult(StrictRecoveryModel):
    """Typed result for create, verify, restore, and live-integrity operations."""

    status: MemoryOperationStatus
    manifest_path: Path | None = None
    layout_fingerprint: str
    verified: bool
    errors: list[MemoryRecoveryErrorDetail] = Field(default_factory=list)
