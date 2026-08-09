"""Store-owned Friday Memory snapshot, verification, and restore participant."""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import os
import pickle
import re
import sqlite3
import stat
import struct
from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Protocol, runtime_checkable
from uuid import uuid4

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.collection_configuration import (
    CreateCollectionConfiguration,
    json_to_create_hnsw_configuration,
    json_to_create_spann_configuration,
    load_collection_configuration_from_json,
)
from chromadb.api.models.Collection import Collection
from chromadb.api.types import Metadata, Schema
from chromadb.errors import ChromaError
from pydantic import JsonValue, TypeAdapter, ValidationError

from friday_memory.adapters.graph import ElementXGraphStore
from friday_memory.maintenance.recovery_models import (
    CHROMA_REBUILD_MAXIMUM_FLOAT32_ULP_DRIFT,
    AccessBufferRecoveryStrategy,
    AccessBufferSnapshotManifest,
    ChromaCollectionManifest,
    ChromaCollectionSnapshot,
    ChromaLogicalSnapshot,
    GraphSnapshotManifest,
    MemoryDiscoveryReport,
    MemoryMaintenanceLayout,
    MemoryOperationResult,
    MemoryOperationStatus,
    MemoryRecoveryErrorCode,
    MemoryRecoveryErrorDetail,
    MemoryRecoveryOperation,
    MemorySnapshotManifest,
    MemorySnapshotStrategy,
    MemoryStoreKind,
    StoreDiscovery,
    StoreDiscoveryState,
    VectorRecordSnapshot,
    VectorSnapshotManifest,
)
from friday_memory.retrieval import AccessBufferConfig


class MemoryRecoveryError(RuntimeError):
    """Base exception for memory recovery invariant failures."""


class MemoryLayoutError(MemoryRecoveryError):
    """Raised when source, recovery, or log paths overlap."""


class MemoryQuiescenceError(MemoryRecoveryError):
    """Raised when an operation lacks its participant-issued token."""


class MemoryPreflightError(MemoryRecoveryError):
    """Raised when configured stores are not safely recoverable."""


class MemorySnapshotError(MemoryRecoveryError):
    """Raised when a verified memory snapshot cannot be created or restored."""


@runtime_checkable
class DrainedAccessBuffer(Protocol):
    """Public surface used to prove access effects were drained before snapshot."""

    @property
    def config(self) -> AccessBufferConfig:
        """Return the public access-buffer configuration."""
        ...

    @property
    def total_count(self) -> int:
        """Return the number of buffered memory identifiers."""
        ...

    def get_stats(self) -> dict[str, int]:
        """Return public buffer counts without exposing buffered content."""
        ...


class MemoryQuiescenceToken:
    """Opaque token issued while the participant operation lock is held."""

    __slots__ = ("_issuer_id", "_layout_fingerprint", "_nonce", "_operation")

    def __init__(
        self,
        issuer_id: str,
        layout_fingerprint: str,
        nonce: str,
        operation: MemoryRecoveryOperation,
    ) -> None:
        self._issuer_id = issuer_id
        self._layout_fingerprint = layout_fingerprint
        self._nonce = nonce
        self._operation = operation


@runtime_checkable
class MemoryRecoveryParticipant(Protocol):
    """Narrow public recovery interface for persistent Friday Memory stores."""

    @property
    def layout_fingerprint(self) -> str:
        """Return the participant-owned normalized layout identity."""
        ...

    def maintenance_quiescence(
        self,
        operation: MemoryRecoveryOperation,
    ) -> AbstractAsyncContextManager[MemoryQuiescenceToken]:
        """Acquire participant-owned snapshot or restore quiescence."""
        ...

    async def discover(self) -> MemoryDiscoveryReport:
        """Return typed store capability and integrity discovery."""
        ...

    async def create_snapshot(
        self,
        run_id: str,
        token: MemoryQuiescenceToken,
    ) -> MemoryOperationResult:
        """Create one complete participant-owned snapshot."""
        ...

    async def verify_snapshot(
        self,
        manifest_path: str | Path,
    ) -> MemoryOperationResult:
        """Verify one exact participant manifest and its artifacts."""
        ...

    async def restore_snapshot(
        self,
        manifest_path: str | Path,
        token: MemoryQuiescenceToken,
    ) -> MemoryOperationResult:
        """Restore only under participant-owned quiescence."""
        ...

    async def verify_live(
        self,
        manifest_path: str | Path,
    ) -> MemoryOperationResult:
        """Verify live stores against one exact snapshot."""
        ...


_JSON_MAPPING = TypeAdapter(dict[str, JsonValue])
_RUN_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
_CHROMA_EXPORT_BATCH_SIZE = 128
_CHROMA_INDEX_PROBE_RESULTS = 8
_LEGACY_HNSW_METADATA_KEYS = frozenset(
    {
        "hnsw:space",
        "hnsw:construction_ef",
        "hnsw:M",
        "hnsw:search_ef",
        "hnsw:num_threads",
        "hnsw:batch_size",
        "hnsw:sync_threshold",
        "hnsw:resize_factor",
    }
)


class MemoryMaintenanceParticipant:
    """Own consistent recovery behavior for graph, Chroma, and drained access state.

    The store-owned token serializes participant operations. Gate C must drain
    external Friday writers before entering ``maintenance_quiescence``.
    """

    def __init__(
        self,
        layout: MemoryMaintenanceLayout,
        *,
        graph_store: ElementXGraphStore | None,
        access_buffer: DrainedAccessBuffer | None = None,
    ) -> None:
        self.layout = layout
        self._graph_store = graph_store
        self._access_buffer = access_buffer
        self._issuer_id = uuid4().hex
        self._operation_lock = asyncio.Lock()
        self._active_token: MemoryQuiescenceToken | None = None
        self._layout_fingerprint = self._fingerprint_layout(layout)
        self._validate_layout_paths()

    @property
    def layout_fingerprint(self) -> str:
        """Return the deterministic fingerprint of normalized explicit paths."""
        return self._layout_fingerprint

    @staticmethod
    def _fingerprint_layout(layout: MemoryMaintenanceLayout) -> str:
        payload = {
            "access_buffer_wal_path": (
                str(layout.access_buffer_wal_path)
                if layout.access_buffer_wal_path is not None
                else None
            ),
            "graph_path": str(layout.graph_path),
            "log_directory": str(layout.log_directory),
            "recovery_directory": str(layout.recovery_directory),
            "vector_directory": str(layout.vector_directory),
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _paths_overlap(first: Path, second: Path) -> bool:
        normalized_first = first.resolve(strict=False)
        normalized_second = second.resolve(strict=False)
        return (
            normalized_first == normalized_second
            or normalized_first in normalized_second.parents
            or normalized_second in normalized_first.parents
        )

    def _validate_layout_paths(self) -> None:
        sources = [self.layout.vector_directory, self.layout.graph_path]
        if self.layout.access_buffer_wal_path is not None:
            sources.append(self.layout.access_buffer_wal_path)
        destinations = [self.layout.recovery_directory, self.layout.log_directory]

        for index, source in enumerate(sources):
            for other_source in sources[index + 1 :]:
                if self._paths_overlap(source, other_source):
                    raise MemoryLayoutError("Friday Memory source paths overlap")
            for destination in destinations:
                if self._paths_overlap(source, destination):
                    raise MemoryLayoutError(
                        "Friday Memory recovery or log path overlaps a source store"
                    )
        if self._paths_overlap(*destinations):
            raise MemoryLayoutError("Friday Memory recovery and log paths overlap")

    @asynccontextmanager
    async def maintenance_quiescence(
        self, operation: MemoryRecoveryOperation
    ) -> AsyncIterator[MemoryQuiescenceToken]:
        """Serialize a drained snapshot/restore operation and issue its token."""
        if self._active_token is not None:
            raise MemoryQuiescenceError("Memory maintenance quiescence is active")
        await self._operation_lock.acquire()
        token = MemoryQuiescenceToken(
            self._issuer_id,
            self._layout_fingerprint,
            uuid4().hex,
            operation,
        )
        self._active_token = token
        try:
            yield token
        finally:
            self._active_token = None
            self._operation_lock.release()

    def _validate_token(
        self, token: MemoryQuiescenceToken, operation: MemoryRecoveryOperation
    ) -> None:
        if (
            token is not self._active_token
            or not self._operation_lock.locked()
            or token._operation is not operation
            or token._layout_fingerprint != self._layout_fingerprint
            or token._issuer_id != self._issuer_id
        ):
            raise MemoryQuiescenceError(
                "Operation requires the active participant-issued quiescence token"
            )

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _read_checked_payload(path: Path, expected_sha256: str) -> bytes:
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != expected_sha256:
            raise ValueError("Recovery artifact checksum mismatch")
        return payload

    @staticmethod
    def _canonical_payload(model: ChromaLogicalSnapshot) -> bytes:
        return json.dumps(
            model.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")

    @staticmethod
    def _collection_digest(collection: ChromaCollectionSnapshot) -> str:
        encoded = json.dumps(
            collection.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _write_owner_only(path: Path, payload: bytes) -> None:
        temp_path = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
        descriptor = os.open(
            temp_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_path, path)
            if os.name == "posix":
                path.chmod(0o600)
                MemoryMaintenanceParticipant._fsync_directory(path.parent)
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise

    @staticmethod
    def _fsync_directory(directory: Path) -> None:
        if os.name != "posix":
            return
        descriptor = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    @staticmethod
    def _make_owner_directory(path: Path, *, parents: bool) -> None:
        path.mkdir(parents=parents, exist_ok=False, mode=0o700)
        if os.name == "posix":
            path.chmod(0o700)
            MemoryMaintenanceParticipant._fsync_directory(path.parent)

    @staticmethod
    def _validate_existing_run_directory(path: Path) -> None:
        try:
            info = path.lstat()
        except OSError as exc:
            raise MemoryLayoutError(
                "Recovery run directory cannot be inspected"
            ) from exc
        if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
            raise MemoryLayoutError("Recovery run path is not a safe directory")
        if os.name == "posix" and (
            info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700
        ):
            raise MemoryLayoutError(
                "Recovery run directory is not owner-only"
            )

    def _prepare_bundle_directory(self, run_id: str) -> Path:
        if (
            _RUN_ID_PATTERN.fullmatch(run_id) is None
            or run_id in {".", ".."}
        ):
            raise MemoryLayoutError("Recovery run ID is not a safe path component")

        recovery_root = self.layout.recovery_directory
        if not recovery_root.exists():
            recovery_root.mkdir(parents=True, exist_ok=False, mode=0o700)
            self._fsync_directory(recovery_root.parent)
        if not recovery_root.is_dir():
            raise MemoryLayoutError("Configured recovery path is not a directory")
        if os.name == "posix":
            recovery_root.chmod(0o700)

        run_directory = recovery_root / run_id
        if run_directory.exists() or run_directory.is_symlink():
            self._validate_existing_run_directory(run_directory)
        else:
            self._make_owner_directory(run_directory, parents=False)
        bundle_directory = run_directory / "memory"
        self._make_owner_directory(bundle_directory, parents=False)
        return bundle_directory

    @staticmethod
    def _open_client(vector_directory: Path) -> ClientAPI:
        return chromadb.PersistentClient(path=str(vector_directory))

    @staticmethod
    def _configuration_supported(
        configuration: dict[str, JsonValue],
        schema: dict[str, JsonValue] | None = None,
    ) -> bool:
        try:
            MemoryMaintenanceParticipant._load_create_configuration(configuration)
            if schema is not None:
                MemoryMaintenanceParticipant._load_schema(schema)
        except (ChromaError, KeyError, TypeError, ValueError):
            return False
        return True

    @staticmethod
    def _load_schema(schema: dict[str, JsonValue]) -> Schema:
        return Schema.deserialize_from_json(dict(schema))

    @staticmethod
    def _public_collection_schema(collection: Collection) -> dict[str, JsonValue]:
        schema = collection.schema
        if schema is None:
            raise MemorySnapshotError("Chroma collection schema is unavailable")
        return _JSON_MAPPING.validate_python(schema.serialize_to_json())

    @staticmethod
    def _load_create_configuration(
        configuration: dict[str, JsonValue]
    ) -> CreateCollectionConfiguration:
        if set(configuration) != {"hnsw", "spann", "embedding_function"}:
            raise ValueError("Unsupported Chroma collection configuration fields")
        loaded = load_collection_configuration_from_json(dict(configuration))
        raw_hnsw = configuration["hnsw"]
        raw_spann = configuration["spann"]
        return CreateCollectionConfiguration(
            hnsw=(
                json_to_create_hnsw_configuration(dict(raw_hnsw))
                if isinstance(raw_hnsw, dict)
                else None
            ),
            spann=(
                json_to_create_spann_configuration(dict(raw_spann))
                if isinstance(raw_spann, dict)
                else None
            ),
            embedding_function=loaded["embedding_function"],
        )

    @staticmethod
    def _as_chroma_metadata(
        metadata: dict[str, JsonValue] | None,
    ) -> Metadata | None:
        if metadata is None:
            return None
        validated: dict[str, str | int | float | bool | None] = {}
        for key, value in metadata.items():
            if value is not None and not isinstance(value, (str, int, float, bool)):
                raise MemorySnapshotError(
                    "Chroma record metadata contains an unsupported value"
                )
            validated[key] = value
        return validated

    @staticmethod
    def _canonical_collection_metadata(
        metadata: dict[str, JsonValue] | None,
    ) -> dict[str, JsonValue] | None:
        """Separate legacy Chroma configuration from user metadata."""
        if metadata is None:
            return None
        canonical = {
            key: value
            for key, value in metadata.items()
            if key not in _LEGACY_HNSW_METADATA_KEYS
        }
        return canonical or None

    @staticmethod
    def _collection_from_public_api(collection: Collection) -> ChromaCollectionSnapshot:
        configuration = _JSON_MAPPING.validate_python(collection.configuration_json)
        schema = MemoryMaintenanceParticipant._public_collection_schema(collection)
        if not MemoryMaintenanceParticipant._configuration_supported(
            configuration, schema
        ):
            raise MemorySnapshotError(
                "A Chroma collection uses an unsupported public configuration"
            )
        metadata = MemoryMaintenanceParticipant._canonical_collection_metadata(
            _JSON_MAPPING.validate_python(collection.metadata)
            if collection.metadata is not None
            else None
        )
        records: list[VectorRecordSnapshot] = []
        expected_count = collection.count()
        for offset in range(0, expected_count, _CHROMA_EXPORT_BATCH_SIZE):
            result = collection.get(
                limit=_CHROMA_EXPORT_BATCH_SIZE,
                offset=offset,
                include=["documents", "metadatas", "embeddings", "uris"],
            )
            ids = result["ids"]
            embeddings = result["embeddings"]
            documents = result["documents"]
            metadatas = result["metadatas"]
            uris = result["uris"]
            if embeddings is None or len(embeddings) != len(ids) or not ids:
                raise MemorySnapshotError(
                    "Chroma did not return a complete bounded export batch"
                )
            for index, record_id in enumerate(ids):
                raw_metadata = metadatas[index] if metadatas is not None else None
                record_metadata = (
                    _JSON_MAPPING.validate_python(raw_metadata)
                    if raw_metadata is not None
                    else None
                )
                records.append(
                    VectorRecordSnapshot(
                        id=record_id,
                        document=(
                            documents[index] if documents is not None else None
                        ),
                        metadata=record_metadata,
                        embedding=[float(value) for value in embeddings[index]],
                        uri=uris[index] if uris is not None else None,
                    )
                )
        if len(records) != expected_count or len({record.id for record in records}) != (
            expected_count
        ):
            raise MemorySnapshotError(
                "Chroma bounded export did not produce every unique record"
            )
        records.sort(key=lambda record: record.id)
        return ChromaCollectionSnapshot(
            name=collection.name,
            metadata=metadata,
            configuration=configuration,
            collection_schema=schema,
            records=records,
        )

    @staticmethod
    def _probe_collection_index(
        collection: Collection, snapshot: ChromaCollectionSnapshot
    ) -> int:
        if not snapshot.records:
            return 0
        probe = snapshot.records[0]
        result = collection.query(
            query_embeddings=probe.embedding,
            n_results=min(len(snapshot.records), _CHROMA_INDEX_PROBE_RESULTS),
            include=["distances"],
        )
        result_ids = result["ids"]
        result_distances = result["distances"]
        if not result_ids or not result_ids[0] or result_distances is None:
            raise MemorySnapshotError("Chroma query index returned no probe result")
        distances = [float(value) for value in result_distances[0]]
        minimum_distance = min(distances)
        if not math.isfinite(minimum_distance) or minimum_distance > 1e-5:
            raise MemorySnapshotError(
                "Chroma query index did not return a finite near-exact result"
            )
        return 1

    @classmethod
    def _export_vector_snapshot(
        cls, vector_directory: Path
    ) -> tuple[ChromaLogicalSnapshot, list[ChromaCollectionManifest]]:
        client = cls._open_client(vector_directory)
        collection_snapshots: list[ChromaCollectionSnapshot] = []
        collection_manifests: list[ChromaCollectionManifest] = []
        for collection in sorted(client.list_collections(), key=lambda item: item.name):
            snapshot = cls._collection_from_public_api(collection)
            probe_count = cls._probe_collection_index(collection, snapshot)
            collection_snapshots.append(snapshot)
            collection_manifests.append(
                ChromaCollectionManifest(
                    name=snapshot.name,
                    record_count=len(snapshot.records),
                    logical_digest=cls._collection_digest(snapshot),
                    query_probe_count=probe_count,
                )
            )
        return (
            ChromaLogicalSnapshot(collections=collection_snapshots),
            collection_manifests,
        )

    def _discover_vector(self) -> StoreDiscovery:
        path = self.layout.vector_directory
        try:
            path_absent = not path.exists() or (
                path.is_dir() and not any(path.iterdir())
            )
        except PermissionError:
            return StoreDiscovery(
                store=MemoryStoreKind.VECTOR,
                state=StoreDiscoveryState.UNSUPPORTED,
                normalized_path=str(path),
                detail="Configured Chroma persistence is not accessible",
            )
        if path_absent:
            return StoreDiscovery(
                store=MemoryStoreKind.VECTOR,
                state=StoreDiscoveryState.CONFIGURED_ABSENT,
                normalized_path=str(path),
                detail="Configured Chroma persistence is absent",
            )
        if not path.is_dir():
            return StoreDiscovery(
                store=MemoryStoreKind.VECTOR,
                state=StoreDiscoveryState.CORRUPT,
                normalized_path=str(path),
                detail="Configured Chroma persistence is not a directory",
            )
        try:
            client = self._open_client(path)
            collections = list(client.list_collections())
            total = 0
            for collection in collections:
                configuration = _JSON_MAPPING.validate_python(
                    collection.configuration_json
                )
                schema = self._public_collection_schema(collection)
                if not self._configuration_supported(configuration, schema):
                    return StoreDiscovery(
                        store=MemoryStoreKind.VECTOR,
                        state=StoreDiscoveryState.UNSUPPORTED,
                        normalized_path=str(path),
                        detail="A Chroma collection configuration is unsupported",
                    )
                total += collection.count()
        except PermissionError:
            return StoreDiscovery(
                store=MemoryStoreKind.VECTOR,
                state=StoreDiscoveryState.UNSUPPORTED,
                normalized_path=str(path),
                detail="Configured Chroma persistence is not accessible",
            )
        except (
            ChromaError,
            OSError,
            RuntimeError,
            sqlite3.Error,
            ValidationError,
            ValueError,
        ):
            return StoreDiscovery(
                store=MemoryStoreKind.VECTOR,
                state=StoreDiscoveryState.CORRUPT,
                normalized_path=str(path),
                detail="Configured Chroma persistence cannot be opened",
            )
        return StoreDiscovery(
            store=MemoryStoreKind.VECTOR,
            state=StoreDiscoveryState.PRESENT,
            normalized_path=str(path),
            item_count=total,
            detail="All public Chroma collection configurations are supported",
        )

    async def _discover_graph(self) -> StoreDiscovery:
        path = self.layout.graph_path
        if not path.exists():
            return StoreDiscovery(
                store=MemoryStoreKind.GRAPH,
                state=StoreDiscoveryState.CONFIGURED_ABSENT,
                normalized_path=str(path),
                detail="Configured graph persistence is absent",
            )
        if self._graph_store is None:
            return StoreDiscovery(
                store=MemoryStoreKind.GRAPH,
                state=StoreDiscoveryState.UNSUPPORTED,
                normalized_path=str(path),
                detail="No graph store owns the configured path",
            )
        store_path = self._graph_store.storage_path
        if store_path is None or store_path.resolve(strict=False) != path:
            return StoreDiscovery(
                store=MemoryStoreKind.GRAPH,
                state=StoreDiscoveryState.UNSUPPORTED,
                normalized_path=str(path),
                detail="Graph store and maintenance layout paths differ",
            )
        if not path.is_file():
            return StoreDiscovery(
                store=MemoryStoreKind.GRAPH,
                state=StoreDiscoveryState.CORRUPT,
                normalized_path=str(path),
                detail="Configured graph persistence is not a file",
            )
        try:
            checksum = await asyncio.to_thread(self._sha256, path)
            summary = await self._graph_store.verify_recovery_snapshot(path, checksum)
        except (EOFError, OSError, pickle.UnpicklingError, ValueError, TypeError):
            return StoreDiscovery(
                store=MemoryStoreKind.GRAPH,
                state=StoreDiscoveryState.CORRUPT,
                normalized_path=str(path),
                detail="Configured graph persistence cannot be validated",
            )
        return StoreDiscovery(
            store=MemoryStoreKind.GRAPH,
            state=StoreDiscoveryState.PRESENT,
            normalized_path=str(path),
            item_count=summary.node_count + summary.edge_count,
            detail="Graph persistence is readable",
        )

    def _discover_access_buffer(self) -> StoreDiscovery:
        configured_wal = self.layout.access_buffer_wal_path
        if self._access_buffer is None:
            if configured_wal is None:
                return StoreDiscovery(
                    store=MemoryStoreKind.ACCESS_BUFFER,
                    state=StoreDiscoveryState.NOT_CONFIGURED,
                    detail="Access-buffer WAL is not configured",
                )
            return StoreDiscovery(
                store=MemoryStoreKind.ACCESS_BUFFER,
                state=StoreDiscoveryState.UNSUPPORTED,
                normalized_path=str(configured_wal),
                detail="Configured WAL has no owning public AccessBuffer",
            )

        owner_wal = self._access_buffer.config.wal_path
        normalized_owner_wal = (
            owner_wal.resolve(strict=False) if owner_wal is not None else None
        )
        if configured_wal != normalized_owner_wal:
            return StoreDiscovery(
                store=MemoryStoreKind.ACCESS_BUFFER,
                state=StoreDiscoveryState.UNSUPPORTED,
                normalized_path=(str(configured_wal) if configured_wal else None),
                detail="AccessBuffer and maintenance layout WAL paths differ",
            )

        stats = self._access_buffer.get_stats()
        reported_total = stats.get("short_term_memories", 0) + stats.get(
            "long_term_memories", 0
        )
        total_count = self._access_buffer.total_count
        try:
            wal_size = (
                configured_wal.stat().st_size
                if configured_wal is not None and configured_wal.exists()
                else 0
            )
        except OSError:
            return StoreDiscovery(
                store=MemoryStoreKind.ACCESS_BUFFER,
                state=StoreDiscoveryState.UNSUPPORTED,
                normalized_path=(str(configured_wal) if configured_wal else None),
                detail="Configured access-buffer WAL is not accessible",
            )
        if reported_total != total_count or total_count != 0 or wal_size != 0:
            return StoreDiscovery(
                store=MemoryStoreKind.ACCESS_BUFFER,
                state=StoreDiscoveryState.INCOMPLETE,
                normalized_path=(str(configured_wal) if configured_wal else None),
                item_count=total_count,
                detail="Access effects have not been drained into vector state",
            )
        return StoreDiscovery(
            store=MemoryStoreKind.ACCESS_BUFFER,
            state=(
                StoreDiscoveryState.PRESENT
                if configured_wal is not None
                else StoreDiscoveryState.NOT_CONFIGURED
            ),
            normalized_path=(str(configured_wal) if configured_wal else None),
            item_count=0,
            detail="Access effects are drained into vector state",
        )

    async def discover(self) -> MemoryDiscoveryReport:
        """Inventory explicit stores and distinguish all fail-closed states."""
        stores = [
            self._discover_vector(),
            await self._discover_graph(),
            self._discover_access_buffer(),
        ]
        supported_by_store = {
            MemoryStoreKind.VECTOR: {StoreDiscoveryState.PRESENT},
            MemoryStoreKind.GRAPH: {
                StoreDiscoveryState.PRESENT,
                StoreDiscoveryState.CONFIGURED_ABSENT,
            },
            MemoryStoreKind.ACCESS_BUFFER: {
                StoreDiscoveryState.PRESENT,
                StoreDiscoveryState.NOT_CONFIGURED,
            },
        }
        graph_store_path = (
            self._graph_store.storage_path.resolve(strict=False)
            if self._graph_store is not None
            and self._graph_store.storage_path is not None
            else None
        )
        unsupported = [
            store
            for store in stores
            if store.state not in supported_by_store[store.store]
            or (
                store.store is MemoryStoreKind.GRAPH
                and store.state is StoreDiscoveryState.CONFIGURED_ABSENT
                and graph_store_path != self.layout.graph_path
            )
        ]
        snapshot_supported = not unsupported
        errors = [
            MemoryRecoveryErrorDetail(
                code={
                    StoreDiscoveryState.CONFIGURED_ABSENT: MemoryRecoveryErrorCode.STORE_ABSENT,
                    StoreDiscoveryState.UNSUPPORTED: MemoryRecoveryErrorCode.STORE_UNSUPPORTED,
                    StoreDiscoveryState.INCOMPLETE: MemoryRecoveryErrorCode.STORE_INCOMPLETE,
                    StoreDiscoveryState.CORRUPT: MemoryRecoveryErrorCode.STORE_CORRUPT,
                }[store.state],
                store=store.store,
                message=store.detail or "Memory store preflight failed",
            )
            for store in unsupported
        ]
        return MemoryDiscoveryReport(
            layout_fingerprint=self._layout_fingerprint,
            stores=stores,
            snapshot_supported=snapshot_supported,
            errors=errors,
        )

    def _access_manifest(self) -> AccessBufferSnapshotManifest:
        wal_path = self.layout.access_buffer_wal_path
        return AccessBufferSnapshotManifest(
            state=(
                StoreDiscoveryState.PRESENT
                if wal_path is not None
                else StoreDiscoveryState.NOT_CONFIGURED
            ),
            strategy=(
                AccessBufferRecoveryStrategy.DRAINED_INTO_VECTOR
                if wal_path is not None
                else AccessBufferRecoveryStrategy.NOT_CONFIGURED
            ),
            wal_configured=wal_path is not None,
            buffered_item_count=0,
            wal_size_bytes=(
                wal_path.stat().st_size if wal_path is not None and wal_path.exists() else 0
            ),
        )

    async def create_snapshot(
        self, run_id: str, token: MemoryQuiescenceToken
    ) -> MemoryOperationResult:
        """Create and verify one complete Friday Memory recovery bundle."""
        self._validate_token(token, MemoryRecoveryOperation.SNAPSHOT)
        discovery = await self.discover()
        if not discovery.snapshot_supported:
            raise MemoryPreflightError("Friday Memory recovery preflight failed")
        if self._graph_store is None:
            raise MemoryPreflightError("Configured graph has no owning store")
        graph_discovery = next(
            store
            for store in discovery.stores
            if store.store is MemoryStoreKind.GRAPH
        )

        bundle_directory = self._prepare_bundle_directory(run_id)
        vector_artifact = bundle_directory / "chroma-logical.json"
        graph_suffix = self.layout.graph_path.suffix or ".gpickle"
        graph_artifact = bundle_directory / f"graph{graph_suffix}"
        manifest_path = bundle_directory / "manifest.json"

        try:
            vector_snapshot, collection_manifests = await asyncio.to_thread(
                self._export_vector_snapshot, self.layout.vector_directory
            )
            vector_payload = self._canonical_payload(vector_snapshot)
            await asyncio.to_thread(
                self._write_owner_only, vector_artifact, vector_payload
            )
            vector_checksum = await asyncio.to_thread(self._sha256, vector_artifact)
            if graph_discovery.state is StoreDiscoveryState.PRESENT:
                graph_summary = await self._graph_store.create_recovery_snapshot(
                    graph_artifact
                )
                graph_checksum = await asyncio.to_thread(
                    self._sha256, graph_artifact
                )
                await self._graph_store.verify_recovery_snapshot(
                    graph_artifact, graph_checksum
                )
                graph_manifest = GraphSnapshotManifest(
                    state=StoreDiscoveryState.PRESENT,
                    artifact_filename=graph_artifact.name,
                    artifact_sha256=graph_checksum,
                    artifact_size_bytes=graph_artifact.stat().st_size,
                    node_count=graph_summary.node_count,
                    edge_count=graph_summary.edge_count,
                )
            else:
                graph_manifest = GraphSnapshotManifest(
                    state=StoreDiscoveryState.CONFIGURED_ABSENT,
                    node_count=0,
                    edge_count=0,
                )
            manifest = MemorySnapshotManifest(
                run_id=run_id,
                created_at=datetime.now(),
                layout_fingerprint=self._layout_fingerprint,
                vector_source=str(self.layout.vector_directory),
                graph_source=str(self.layout.graph_path),
                access_buffer_wal_source=(
                    str(self.layout.access_buffer_wal_path)
                    if self.layout.access_buffer_wal_path is not None
                    else None
                ),
                vector=VectorSnapshotManifest(
                    state=StoreDiscoveryState.PRESENT,
                    strategy=MemorySnapshotStrategy.CHROMA_LOGICAL_EXPORT_REBUILD,
                    artifact_filename=vector_artifact.name,
                    artifact_sha256=vector_checksum,
                    artifact_size_bytes=vector_artifact.stat().st_size,
                    maximum_float32_ulp_drift=(
                        CHROMA_REBUILD_MAXIMUM_FLOAT32_ULP_DRIFT
                    ),
                    collections=collection_manifests,
                ),
                graph=graph_manifest,
                access_buffer=self._access_manifest(),
                verified=True,
            )
            await asyncio.to_thread(
                self._write_owner_only,
                manifest_path,
                manifest.model_dump_json(indent=2).encode("utf-8"),
            )
        except (
            ChromaError,
            EOFError,
            OSError,
            pickle.PickleError,
            RuntimeError,
            sqlite3.Error,
            TypeError,
            ValidationError,
            ValueError,
        ) as exc:
            raise MemorySnapshotError(
                f"Friday Memory snapshot failed: {type(exc).__name__}"
            ) from exc

        verification = await self.verify_snapshot(manifest_path)
        if not verification.verified:
            raise MemorySnapshotError("Friday Memory snapshot verification failed")
        return verification

    @staticmethod
    def _artifact_path(manifest_path: Path, filename: str) -> Path | None:
        if Path(filename).name != filename:
            return None
        return manifest_path.parent / filename

    @classmethod
    def _graph_artifact_path(
        cls,
        manifest_path: Path,
        graph: GraphSnapshotManifest,
    ) -> Path | None:
        if graph.state is StoreDiscoveryState.CONFIGURED_ABSENT:
            return None
        if graph.artifact_filename is None:
            return None
        return cls._artifact_path(manifest_path, graph.artifact_filename)

    @staticmethod
    def _failed_result(
        layout_fingerprint: str,
        code: MemoryRecoveryErrorCode,
        message: str,
        *,
        manifest_path: Path | None = None,
        store: MemoryStoreKind | None = None,
    ) -> MemoryOperationResult:
        return MemoryOperationResult(
            status=MemoryOperationStatus.FAILED,
            manifest_path=manifest_path,
            layout_fingerprint=layout_fingerprint,
            verified=False,
            errors=[
                MemoryRecoveryErrorDetail(
                    code=code,
                    store=store,
                    message=message,
                )
            ],
        )

    def _validate_manifest_layout(
        self, manifest: MemorySnapshotManifest
    ) -> MemoryRecoveryErrorDetail | None:
        expected_wal = (
            str(self.layout.access_buffer_wal_path)
            if self.layout.access_buffer_wal_path is not None
            else None
        )
        if (
            manifest.layout_fingerprint != self._layout_fingerprint
            or Path(manifest.vector_source).resolve(strict=False)
            != self.layout.vector_directory
            or Path(manifest.graph_source).resolve(strict=False) != self.layout.graph_path
            or manifest.access_buffer_wal_source != expected_wal
        ):
            return MemoryRecoveryErrorDetail(
                code=MemoryRecoveryErrorCode.LAYOUT_MISMATCH,
                message="Memory snapshot belongs to a different explicit layout",
            )
        return None

    @staticmethod
    def _manifest_store_state_complete(manifest: MemorySnapshotManifest) -> bool:
        """Apply one fail-closed store-state invariant to verify and live use."""
        access = manifest.access_buffer
        return (
            manifest.vector.state is StoreDiscoveryState.PRESENT
            and manifest.graph.state
            in {
                StoreDiscoveryState.PRESENT,
                StoreDiscoveryState.CONFIGURED_ABSENT,
            }
            and manifest.vector.strategy
            is MemorySnapshotStrategy.CHROMA_LOGICAL_EXPORT_REBUILD
            and access.buffered_item_count == 0
            and access.wal_size_bytes == 0
            and access.wal_configured
            == (manifest.access_buffer_wal_source is not None)
            and (
                (
                    access.state is StoreDiscoveryState.PRESENT
                    and access.strategy
                    is AccessBufferRecoveryStrategy.DRAINED_INTO_VECTOR
                )
                if access.wal_configured
                else (
                    access.state is StoreDiscoveryState.NOT_CONFIGURED
                    and access.strategy
                    is AccessBufferRecoveryStrategy.NOT_CONFIGURED
                )
            )
        )

    def _load_manifest_for_apply(self, manifest_path: Path) -> MemorySnapshotManifest:
        """Revalidate the exact manifest instance used to select applied artifacts."""
        try:
            manifest = MemorySnapshotManifest.model_validate_json(
                manifest_path.read_bytes()
            )
        except (OSError, ValidationError, ValueError) as exc:
            raise MemorySnapshotError(
                "Memory snapshot manifest became unavailable or invalid"
            ) from exc
        if (
            self._validate_manifest_layout(manifest) is not None
            or not manifest.verified
            or self._artifact_path(
                manifest_path, manifest.vector.artifact_filename
            )
            is None
            or (
                manifest.graph.state is StoreDiscoveryState.PRESENT
                and self._graph_artifact_path(manifest_path, manifest.graph) is None
            )
            or not self._manifest_store_state_complete(manifest)
        ):
            raise MemorySnapshotError(
                "Memory snapshot manifest is not valid for this layout"
            )
        return manifest

    async def verify_snapshot(self, manifest_path: str | Path) -> MemoryOperationResult:
        """Verify a complete manifest and every package-owned artifact."""
        normalized_manifest = Path(manifest_path).resolve(strict=False)
        try:
            manifest = MemorySnapshotManifest.model_validate_json(
                normalized_manifest.read_text()
            )
        except FileNotFoundError:
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.SNAPSHOT_INCOMPLETE,
                "Memory snapshot manifest is absent",
                manifest_path=normalized_manifest,
            )
        except (OSError, ValidationError, ValueError):
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.SCHEMA_MISMATCH,
                "Memory snapshot manifest is invalid",
                manifest_path=normalized_manifest,
            )
        layout_error = self._validate_manifest_layout(manifest)
        if layout_error is not None:
            return MemoryOperationResult(
                status=MemoryOperationStatus.FAILED,
                manifest_path=normalized_manifest,
                layout_fingerprint=self._layout_fingerprint,
                verified=False,
                errors=[layout_error],
            )
        if not manifest.verified:
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.SNAPSHOT_INCOMPLETE,
                "Memory snapshot manifest is not marked verified",
                manifest_path=normalized_manifest,
            )
        vector_artifact = self._artifact_path(
            normalized_manifest, manifest.vector.artifact_filename
        )
        graph_artifact = self._graph_artifact_path(
            normalized_manifest, manifest.graph
        )
        if (
            vector_artifact is None
            or not vector_artifact.is_file()
            or (
                manifest.graph.state is StoreDiscoveryState.PRESENT
                and (graph_artifact is None or not graph_artifact.is_file())
            )
        ):
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.SNAPSHOT_INCOMPLETE,
                "Memory snapshot artifact is absent or outside its bundle",
                manifest_path=normalized_manifest,
            )
        try:
            vector_payload = await asyncio.to_thread(
                self._read_checked_payload,
                vector_artifact,
                manifest.vector.artifact_sha256,
            )
            graph_checksum = (
                await asyncio.to_thread(self._sha256, graph_artifact)
                if graph_artifact is not None
                else None
            )
        except OSError:
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.SNAPSHOT_INCOMPLETE,
                "Memory snapshot artifact became unavailable",
                manifest_path=normalized_manifest,
            )
        except ValueError:
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.CHECKSUM_MISMATCH,
                "Memory snapshot artifact checksum mismatch",
                manifest_path=normalized_manifest,
            )
        if graph_checksum != manifest.graph.artifact_sha256:
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.CHECKSUM_MISMATCH,
                "Memory snapshot artifact checksum mismatch",
                manifest_path=normalized_manifest,
            )
        try:
            vector_snapshot = ChromaLogicalSnapshot.model_validate_json(
                vector_payload
            )
        except (OSError, ValidationError, ValueError):
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.SCHEMA_MISMATCH,
                "Chroma logical snapshot schema is invalid",
                manifest_path=normalized_manifest,
                store=MemoryStoreKind.VECTOR,
            )
        if any(
            not self._configuration_supported(
                collection.configuration, collection.collection_schema
            )
            for collection in vector_snapshot.collections
        ):
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.STORE_UNSUPPORTED,
                "Chroma logical snapshot contains an unsupported configuration",
                manifest_path=normalized_manifest,
                store=MemoryStoreKind.VECTOR,
            )
        if not self._manifest_store_state_complete(manifest):
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.SNAPSHOT_INCOMPLETE,
                "Memory recovery manifest contains incomplete store state",
                manifest_path=normalized_manifest,
            )
        expected_collections = [
            ChromaCollectionManifest(
                name=collection.name,
                record_count=len(collection.records),
                logical_digest=self._collection_digest(collection),
                query_probe_count=(1 if collection.records else 0),
            )
            for collection in vector_snapshot.collections
        ]
        try:
            vector_size = len(vector_payload)
            graph_size = (
                graph_artifact.stat().st_size
                if graph_artifact is not None
                else None
            )
        except OSError:
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.SNAPSHOT_INCOMPLETE,
                "Memory snapshot artifact became unavailable",
                manifest_path=normalized_manifest,
            )
        if (
            expected_collections != manifest.vector.collections
            or vector_size != manifest.vector.artifact_size_bytes
            or graph_size != manifest.graph.artifact_size_bytes
        ):
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.SNAPSHOT_INCOMPLETE,
                "Memory snapshot manifest does not match artifact contents",
                manifest_path=normalized_manifest,
            )
        if self._graph_store is None:
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.STORE_UNSUPPORTED,
                "No graph store can verify the recovery artifact",
                manifest_path=normalized_manifest,
                store=MemoryStoreKind.GRAPH,
            )
        if manifest.graph.state is StoreDiscoveryState.PRESENT:
            if graph_artifact is None or manifest.graph.artifact_sha256 is None:
                return self._failed_result(
                    self._layout_fingerprint,
                    MemoryRecoveryErrorCode.SNAPSHOT_INCOMPLETE,
                    "Graph recovery artifact metadata is incomplete",
                    manifest_path=normalized_manifest,
                    store=MemoryStoreKind.GRAPH,
                )
            try:
                graph_summary = await self._graph_store.verify_recovery_snapshot(
                    graph_artifact, manifest.graph.artifact_sha256
                )
            except (
                EOFError,
                OSError,
                pickle.PickleError,
                TypeError,
                ValueError,
            ):
                return self._failed_result(
                    self._layout_fingerprint,
                    MemoryRecoveryErrorCode.STORE_CORRUPT,
                    "Graph recovery artifact cannot be validated",
                    manifest_path=normalized_manifest,
                    store=MemoryStoreKind.GRAPH,
                )
            if (
                graph_summary.node_count != manifest.graph.node_count
                or graph_summary.edge_count != manifest.graph.edge_count
            ):
                return self._failed_result(
                    self._layout_fingerprint,
                    MemoryRecoveryErrorCode.SNAPSHOT_INCOMPLETE,
                    "Memory recovery manifest contains incomplete store state",
                    manifest_path=normalized_manifest,
                )
        try:
            await asyncio.to_thread(
                self._verify_vector_snapshot_restorable,
                vector_snapshot,
                manifest.vector.maximum_float32_ulp_drift,
            )
        except (
            ChromaError,
            MemorySnapshotError,
            OSError,
            sqlite3.Error,
            TypeError,
            ValueError,
        ):
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.STORE_UNSUPPORTED,
                "Chroma logical snapshot cannot be restored through public APIs",
                manifest_path=normalized_manifest,
                store=MemoryStoreKind.VECTOR,
            )
        return MemoryOperationResult(
            status=MemoryOperationStatus.COMPLETED,
            manifest_path=normalized_manifest,
            layout_fingerprint=self._layout_fingerprint,
            verified=True,
        )

    @classmethod
    def _prepare_vector_restore(
        cls, snapshot: ChromaLogicalSnapshot
    ) -> list[Schema]:
        names = [collection.name for collection in snapshot.collections]
        if len(names) != len(set(names)):
            raise MemorySnapshotError("Chroma snapshot contains duplicate collections")
        for collection in snapshot.collections:
            record_ids = [record.id for record in collection.records]
            if len(record_ids) != len(set(record_ids)):
                raise MemorySnapshotError("Chroma snapshot contains duplicate record IDs")
            dimensions = {len(record.embedding) for record in collection.records}
            if len(dimensions) > 1 or any(
                not record.embedding
                or any(not math.isfinite(value) for value in record.embedding)
                for record in collection.records
            ):
                raise MemorySnapshotError(
                    "Chroma snapshot contains invalid embedding dimensions or values"
                )
        schemas: list[Schema] = []
        for collection in snapshot.collections:
            cls._load_create_configuration(collection.configuration)
            schemas.append(cls._load_schema(collection.collection_schema))
        return schemas

    @classmethod
    def _populate_vector_client(
        cls,
        client: ClientAPI,
        snapshot: ChromaLogicalSnapshot,
        schemas: list[Schema],
    ) -> None:
        for collection_snapshot, schema in zip(
            snapshot.collections, schemas, strict=True
        ):
            collection = client.create_collection(
                name=collection_snapshot.name,
                metadata=cls._canonical_collection_metadata(
                    collection_snapshot.metadata
                ),
                schema=schema,
            )
            if _JSON_MAPPING.validate_python(
                collection.configuration_json
            ) != collection_snapshot.configuration:
                raise MemorySnapshotError(
                    "Rebuilt Chroma collection configuration changed"
                )
            if cls._public_collection_schema(
                collection
            ) != collection_snapshot.collection_schema:
                raise MemorySnapshotError("Rebuilt Chroma collection schema changed")
            for record in collection_snapshot.records:
                collection.add(
                    ids=record.id,
                    embeddings=record.embedding,
                    metadatas=cls._as_chroma_metadata(record.metadata),
                    documents=record.document,
                    uris=record.uri,
                )
            cls._probe_collection_index(collection, collection_snapshot)

    @staticmethod
    def _float32_ordered_integer(value: float) -> int:
        """Map one finite, exactly represented float32 value to ULP order."""
        if not math.isfinite(value):
            raise MemorySnapshotError("Chroma embedding contains a non-finite value")
        try:
            encoded = struct.pack("!f", value)
        except (OverflowError, struct.error) as exc:
            raise MemorySnapshotError(
                "Chroma embedding is outside the finite float32 range"
            ) from exc
        restored = float(struct.unpack("!f", encoded)[0])
        if restored != value:
            raise MemorySnapshotError(
                "Chroma embedding is not exactly represented as float32"
            )
        bits = int.from_bytes(encoded, byteorder="big")
        if bits & 0x80000000:
            return ~bits & 0xFFFFFFFF
        return bits | 0x80000000

    @classmethod
    def _embedding_within_float32_ulp_bound(
        cls,
        expected: list[float],
        actual: list[float],
        maximum_float32_ulp_drift: int,
    ) -> bool:
        if len(expected) != len(actual):
            return False
        return all(
            abs(
                cls._float32_ordered_integer(expected_value)
                - cls._float32_ordered_integer(actual_value)
            )
            <= maximum_float32_ulp_drift
            for expected_value, actual_value in zip(expected, actual, strict=True)
        )

    @classmethod
    def _vector_snapshots_equivalent(
        cls,
        expected: ChromaLogicalSnapshot,
        actual: ChromaLogicalSnapshot,
        maximum_float32_ulp_drift: int,
    ) -> bool:
        """Compare exact logical state with only declared float32 ULP drift."""
        if (
            maximum_float32_ulp_drift
            != CHROMA_REBUILD_MAXIMUM_FLOAT32_ULP_DRIFT
        ):
            raise MemorySnapshotError(
                "Unsupported Chroma float32 ULP equivalence policy"
            )
        if (
            expected.schema_version != actual.schema_version
            or expected.strategy is not actual.strategy
            or len(expected.collections) != len(actual.collections)
        ):
            return False
        for expected_collection, actual_collection in zip(
            expected.collections, actual.collections, strict=True
        ):
            if (
                expected_collection.name != actual_collection.name
                or cls._canonical_collection_metadata(
                    expected_collection.metadata
                )
                != cls._canonical_collection_metadata(actual_collection.metadata)
                or expected_collection.configuration
                != actual_collection.configuration
                or expected_collection.collection_schema
                != actual_collection.collection_schema
                or len(expected_collection.records)
                != len(actual_collection.records)
            ):
                return False
            for expected_record, actual_record in zip(
                expected_collection.records,
                actual_collection.records,
                strict=True,
            ):
                if (
                    expected_record.id != actual_record.id
                    or expected_record.document != actual_record.document
                    or expected_record.metadata != actual_record.metadata
                    or expected_record.uri != actual_record.uri
                    or not cls._embedding_within_float32_ulp_bound(
                        expected_record.embedding,
                        actual_record.embedding,
                        maximum_float32_ulp_drift,
                    )
                ):
                    return False
        return True

    @staticmethod
    def _live_collection_evidence_matches(
        expected: list[ChromaCollectionManifest],
        actual: list[ChromaCollectionManifest],
    ) -> bool:
        """Compare live evidence while artifact digests retain exact embeddings."""
        if len(expected) != len(actual):
            return False
        return all(
            expected_collection.name == actual_collection.name
            and expected_collection.record_count == actual_collection.record_count
            and expected_collection.query_probe_count
            == actual_collection.query_probe_count
            for expected_collection, actual_collection in zip(
                expected, actual, strict=True
            )
        )

    @classmethod
    def _restore_vector_snapshot(
        cls,
        vector_directory: Path,
        snapshot: ChromaLogicalSnapshot,
        maximum_float32_ulp_drift: int,
    ) -> None:
        cls._verify_vector_snapshot_restorable(
            snapshot, maximum_float32_ulp_drift
        )
        schemas = cls._prepare_vector_restore(snapshot)
        client = cls._open_client(vector_directory)
        for live_collection in list(client.list_collections()):
            client.delete_collection(live_collection.name)
        cls._populate_vector_client(client, snapshot, schemas)

    @classmethod
    def _verify_vector_snapshot_restorable(
        cls,
        snapshot: ChromaLogicalSnapshot,
        maximum_float32_ulp_drift: int,
    ) -> None:
        """Prove a public rebuild meets the persisted ULP policy before mutation."""
        schemas = cls._prepare_vector_restore(snapshot)
        with TemporaryDirectory(prefix="friday-chroma-restore-preflight-") as temp_dir:
            preflight_client = cls._open_client(Path(temp_dir))
            cls._populate_vector_client(
                preflight_client,
                snapshot,
                schemas,
            )
            rebuilt, _ = cls._export_vector_snapshot(Path(temp_dir))
            if not cls._vector_snapshots_equivalent(
                snapshot,
                rebuilt,
                maximum_float32_ulp_drift,
            ):
                raise MemorySnapshotError(
                    "Public Chroma rebuild changed logical snapshot content"
                )

    @classmethod
    def _load_vector_artifact(
        cls, manifest_path: Path, manifest: MemorySnapshotManifest
    ) -> ChromaLogicalSnapshot:
        artifact = manifest_path.parent / manifest.vector.artifact_filename
        payload = cls._read_checked_payload(
            artifact, manifest.vector.artifact_sha256
        )
        return ChromaLogicalSnapshot.model_validate_json(payload)

    async def restore_snapshot(
        self, manifest_path: str | Path, token: MemoryQuiescenceToken
    ) -> MemoryOperationResult:
        """Restore every memory component and verify exact live state."""
        self._validate_token(token, MemoryRecoveryOperation.RESTORE)
        verification = await self.verify_snapshot(manifest_path)
        if not verification.verified or verification.manifest_path is None:
            raise MemorySnapshotError("Memory snapshot verification failed")
        if self._graph_store is None:
            raise MemorySnapshotError("No graph store can restore the snapshot")

        try:
            manifest = self._load_manifest_for_apply(verification.manifest_path)
            vector_snapshot = self._load_vector_artifact(
                verification.manifest_path, manifest
            )
            await asyncio.to_thread(
                self._restore_vector_snapshot,
                self.layout.vector_directory,
                vector_snapshot,
                manifest.vector.maximum_float32_ulp_drift,
            )
            if manifest.graph.state is StoreDiscoveryState.CONFIGURED_ABSENT:
                await self._graph_store.restore_configured_absence()
            else:
                graph_artifact = self._graph_artifact_path(
                    verification.manifest_path, manifest.graph
                )
                if (
                    graph_artifact is None
                    or manifest.graph.artifact_sha256 is None
                ):
                    raise MemorySnapshotError(
                        "Graph recovery artifact metadata is incomplete"
                    )
                await self._graph_store.restore_recovery_snapshot(
                    graph_artifact, manifest.graph.artifact_sha256
                )
        except (
            ChromaError,
            EOFError,
            OSError,
            pickle.PickleError,
            RuntimeError,
            sqlite3.Error,
            TypeError,
            ValidationError,
            ValueError,
        ) as exc:
            raise MemorySnapshotError(
                f"Friday Memory restore failed: {type(exc).__name__}"
            ) from exc

        live_result = await self.verify_live(verification.manifest_path)
        if not live_result.verified:
            raise MemorySnapshotError("Restored Friday Memory failed integrity checks")
        return live_result

    async def verify_live(self, manifest_path: str | Path) -> MemoryOperationResult:
        """Verify live graph/vector/access state against a recovery manifest."""
        snapshot_result = await self.verify_snapshot(manifest_path)
        if not snapshot_result.verified or snapshot_result.manifest_path is None:
            return snapshot_result
        try:
            manifest = self._load_manifest_for_apply(
                snapshot_result.manifest_path
            )
            expected_vector = self._load_vector_artifact(
                snapshot_result.manifest_path, manifest
            )
            live_vector, live_manifests = await asyncio.to_thread(
                self._export_vector_snapshot, self.layout.vector_directory
            )
        except (
            ChromaError,
            OSError,
            RuntimeError,
            sqlite3.Error,
            TypeError,
            ValidationError,
            ValueError,
        ):
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.INTEGRITY_FAILED,
                "Live Chroma state or recovery metadata cannot be validated",
                manifest_path=snapshot_result.manifest_path,
                store=MemoryStoreKind.VECTOR,
            )
        if (
            not self._vector_snapshots_equivalent(
                expected_vector,
                live_vector,
                manifest.vector.maximum_float32_ulp_drift,
            )
            or not self._live_collection_evidence_matches(
                manifest.vector.collections, live_manifests
            )
        ):
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.INTEGRITY_FAILED,
                "Live Chroma logical state differs from the snapshot",
                manifest_path=snapshot_result.manifest_path,
                store=MemoryStoreKind.VECTOR,
            )
        if self._graph_store is None:
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.STORE_UNSUPPORTED,
                "No graph store can validate live state",
                manifest_path=snapshot_result.manifest_path,
                store=MemoryStoreKind.GRAPH,
            )
        if manifest.graph.state is StoreDiscoveryState.CONFIGURED_ABSENT:
            if (
                self.layout.graph_path.exists()
                or await self._graph_store.node_count() != 0
                or await self._graph_store.edge_count() != 0
            ):
                return self._failed_result(
                    self._layout_fingerprint,
                    MemoryRecoveryErrorCode.INTEGRITY_FAILED,
                    "Live graph state differs from configured absence",
                    manifest_path=snapshot_result.manifest_path,
                    store=MemoryStoreKind.GRAPH,
                )
        else:
            try:
                live_graph_checksum = await asyncio.to_thread(
                    self._sha256, self.layout.graph_path
                )
            except OSError:
                return self._failed_result(
                    self._layout_fingerprint,
                    MemoryRecoveryErrorCode.INTEGRITY_FAILED,
                    "Live graph state cannot be read",
                    manifest_path=snapshot_result.manifest_path,
                    store=MemoryStoreKind.GRAPH,
                )
            if live_graph_checksum != manifest.graph.artifact_sha256:
                return self._failed_result(
                    self._layout_fingerprint,
                    MemoryRecoveryErrorCode.INTEGRITY_FAILED,
                    "Live graph state differs from the snapshot",
                    manifest_path=snapshot_result.manifest_path,
                    store=MemoryStoreKind.GRAPH,
                )
        access_discovery = self._discover_access_buffer()
        if access_discovery.state not in {
            StoreDiscoveryState.PRESENT,
            StoreDiscoveryState.NOT_CONFIGURED,
        }:
            return self._failed_result(
                self._layout_fingerprint,
                MemoryRecoveryErrorCode.INTEGRITY_FAILED,
                "Live access effects are not drained into vector state",
                manifest_path=snapshot_result.manifest_path,
                store=MemoryStoreKind.ACCESS_BUFFER,
            )
        return MemoryOperationResult(
            status=MemoryOperationStatus.COMPLETED,
            manifest_path=snapshot_result.manifest_path,
            layout_fingerprint=self._layout_fingerprint,
            verified=True,
        )
