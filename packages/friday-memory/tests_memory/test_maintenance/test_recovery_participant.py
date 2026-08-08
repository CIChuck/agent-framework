"""Recovery tests for graph, Chroma, and drained access-buffer state."""

import hashlib
import json
import os
import pickle
import struct
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

import chromadb
import pytest
from chromadb.api.models.Collection import Collection
from chromadb.errors import InvalidArgumentError
from friday_memory import (
    CHROMA_REBUILD_MAXIMUM_FLOAT32_ULP_DRIFT,
    AccessBuffer,
    AccessBufferConfig,
    AccessBufferRecoveryStrategy,
    ChromaCollectionManifest,
    ChromaLogicalSnapshot,
    ElementXGraphStore,
    GraphNode,
    LegacySingleRootLayoutAdapter,
    MemoryLayoutError,
    MemoryMaintenanceLayout,
    MemoryMaintenanceParticipant,
    MemoryOperationResult,
    MemoryQuiescenceError,
    MemoryQuiescenceToken,
    MemoryRecoveryErrorCode,
    MemoryRecoveryOperation,
    MemorySnapshotError,
    MemorySnapshotManifest,
    ProvenanceMetadata,
    StoreDiscoveryState,
)
from pydantic import ValidationError


@dataclass
class RecoveryFixture:
    root: Path
    layout: MemoryMaintenanceLayout
    graph: ElementXGraphStore
    access_buffer: AccessBuffer
    participant: MemoryMaintenanceParticipant


async def _recovery_fixture(root: Path) -> RecoveryFixture:
    vector_path = root / "vector"
    graph_path = root / "graph.gpickle"
    wal_path = root / "access.wal"
    client = chromadb.PersistentClient(path=str(vector_path))
    primary = client.create_collection(
        "primary",
        metadata={"purpose": "primary"},
        configuration={"hnsw": {"space": "cosine"}},
    )
    primary_embeddings: list[Sequence[float] | Sequence[int]] = [
        [1.0, 0.0],
        [0.0, 1.0],
    ]
    primary.add(
        ids=["p-1", "p-2"],
        documents=["first", "second"],
        metadatas=[{"rank": 1}, {"rank": 2}],
        embeddings=primary_embeddings,
    )
    secondary = client.create_collection(
        "secondary",
        metadata={"purpose": "secondary"},
        configuration={"hnsw": {"space": "l2"}},
    )
    secondary.add(
        ids="s-1",
        documents="third",
        metadatas={"rank": 3},
        embeddings=[0.5, 0.5],
    )

    graph = ElementXGraphStore(str(graph_path))
    await graph.add_node(
        GraphNode(
            id="node-1",
            type="Entity",
            label="Test node",
            provenance=ProvenanceMetadata(
                source_id="source-1",
                source_type="test",
            ),
        )
    )
    access_buffer = AccessBuffer(AccessBufferConfig(wal_path=wal_path))
    layout = MemoryMaintenanceLayout(
        vector_directory=vector_path,
        graph_path=graph_path,
        access_buffer_wal_path=wal_path,
        recovery_directory=root / "recovery",
        log_directory=root / "logs",
    )
    participant = MemoryMaintenanceParticipant(
        layout,
        graph_store=graph,
        access_buffer=access_buffer,
    )
    return RecoveryFixture(root, layout, graph, access_buffer, participant)


async def _create_snapshot(
    fixture: RecoveryFixture, run_id: str = "run-1"
) -> Path:
    async with fixture.participant.maintenance_quiescence(
        MemoryRecoveryOperation.SNAPSHOT
    ) as token:
        result = await fixture.participant.create_snapshot(run_id, token)
    assert result.verified
    assert result.manifest_path is not None
    return result.manifest_path


@pytest.mark.asyncio
async def test_snapshot_accepts_journal_owned_run_directory(tmp_path: Path) -> None:
    fixture = await _recovery_fixture(tmp_path)
    run_directory = fixture.layout.recovery_directory / "journal-run"
    run_directory.mkdir(parents=True, mode=0o700)
    if os.name == "posix":
        run_directory.chmod(0o700)
    journal = run_directory / "journal.json"
    journal.write_text("{}")
    if os.name == "posix":
        journal.chmod(0o600)

    manifest_path = await _create_snapshot(fixture, "journal-run")

    assert manifest_path == run_directory / "memory" / "manifest.json"


@pytest.mark.asyncio
@pytest.mark.parametrize("unsafe_kind", ["mode", "symlink", "memory_exists"])
async def test_snapshot_rejects_unsafe_existing_run_directory(
    tmp_path: Path,
    unsafe_kind: str,
) -> None:
    fixture = await _recovery_fixture(tmp_path)
    recovery_root = fixture.layout.recovery_directory
    recovery_root.mkdir(parents=True)
    run_directory = recovery_root / "unsafe-run"
    if unsafe_kind == "symlink":
        target = tmp_path / "run-target"
        target.mkdir()
        try:
            run_directory.symlink_to(target, target_is_directory=True)
        except OSError:
            pytest.skip("Directory symlinks are not available")
    else:
        run_directory.mkdir(mode=0o700)
        if os.name == "posix":
            run_directory.chmod(0o700)
        if unsafe_kind == "mode":
            if os.name != "posix":
                pytest.skip("POSIX directory modes are unavailable")
            run_directory.chmod(0o755)
        else:
            (run_directory / "memory").mkdir()

    async with fixture.participant.maintenance_quiescence(
        MemoryRecoveryOperation.SNAPSHOT
    ) as token:
        with pytest.raises((FileExistsError, MemoryLayoutError)):
            await fixture.participant.create_snapshot("unsafe-run", token)


@pytest.mark.asyncio
async def test_snapshot_rejects_existing_run_directory_owned_by_other_user(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX ownership is unavailable")
    fixture = await _recovery_fixture(tmp_path)
    run_directory = fixture.layout.recovery_directory / "owner-run"
    run_directory.mkdir(parents=True, mode=0o700)
    run_directory.chmod(0o700)
    actual_user_id = os.getuid()
    monkeypatch.setattr(os, "getuid", lambda: actual_user_id + 1)

    async with fixture.participant.maintenance_quiescence(
        MemoryRecoveryOperation.SNAPSHOT
    ) as token:
        with pytest.raises(MemoryLayoutError, match="owner-only"):
            await fixture.participant.create_snapshot("owner-run", token)


def _canonical_json(payload: object) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _shift_positive_float32(value: float, ulps: int) -> float:
    bits = int.from_bytes(struct.pack("!f", value), byteorder="big")
    assert bits & 0x80000000 == 0
    return float(struct.unpack("!f", (bits + ulps).to_bytes(4, byteorder="big"))[0])


@pytest.mark.asyncio
async def test_multicollection_snapshot_restore_and_query_index_integrity(
    tmp_path: Path,
) -> None:
    fixture = await _recovery_fixture(tmp_path)
    discovery = await fixture.participant.discover()
    assert discovery.snapshot_supported
    assert [store.state for store in discovery.stores] == [
        StoreDiscoveryState.PRESENT,
        StoreDiscoveryState.PRESENT,
        StoreDiscoveryState.PRESENT,
    ]

    manifest_path = await _create_snapshot(fixture)
    manifest = MemorySnapshotManifest.model_validate_json(manifest_path.read_text())
    assert manifest.vector.strategy.value == "chroma_logical_export_rebuild"
    assert manifest.access_buffer.strategy is AccessBufferRecoveryStrategy.DRAINED_INTO_VECTOR
    assert [collection.name for collection in manifest.vector.collections] == [
        "primary",
        "secondary",
    ]
    assert [collection.query_probe_count for collection in manifest.vector.collections] == [
        1,
        1,
    ]

    vector_artifact = manifest_path.parent / manifest.vector.artifact_filename
    logical_snapshot = ChromaLogicalSnapshot.model_validate_json(
        vector_artifact.read_text()
    )
    primary_snapshot = logical_snapshot.collections[0]
    assert [record.id for record in primary_snapshot.records] == ["p-1", "p-2"]
    assert [record.document for record in primary_snapshot.records] == [
        "first",
        "second",
    ]
    assert [record.metadata for record in primary_snapshot.records] == [
        {"rank": 1},
        {"rank": 2},
    ]
    assert [record.embedding for record in primary_snapshot.records] == [
        [1.0, 0.0],
        [0.0, 1.0],
    ]
    assert primary_snapshot.metadata == {"purpose": "primary"}
    hnsw_configuration = primary_snapshot.configuration["hnsw"]
    assert isinstance(hnsw_configuration, dict)
    assert hnsw_configuration["space"] == "cosine"

    client = chromadb.PersistentClient(path=str(fixture.layout.vector_directory))
    client.get_collection("primary").delete(ids=["p-1"])
    extra = client.create_collection("extra")
    extra.add(ids="extra-1", documents="extra", embeddings=[1.0, 1.0])
    await fixture.graph.clear()

    if os.name == "posix":
        fixture.layout.graph_path.parent.chmod(0o750)
        fixture.layout.graph_path.chmod(0o640)
    async with fixture.participant.maintenance_quiescence(
        MemoryRecoveryOperation.RESTORE
    ) as token:
        restored = await fixture.participant.restore_snapshot(manifest_path, token)
    assert restored.verified

    assert sorted(collection.name for collection in client.list_collections()) == [
        "primary",
        "secondary",
    ]
    restored_primary = client.get_collection("primary")
    restored_records = restored_primary.get(
        include=["documents", "metadatas", "embeddings"]
    )
    assert restored_records["ids"] == ["p-1", "p-2"]
    query = restored_primary.query(
        query_embeddings=[1.0, 0.0], n_results=2, include=["distances"]
    )
    assert query["ids"][0][0] == "p-1"
    assert restored_primary.configuration_json == primary_snapshot.configuration
    assert await fixture.graph.node_count() == 1
    assert await fixture.graph.edge_count() == 0
    if os.name == "posix":
        assert fixture.layout.graph_path.parent.stat().st_mode & 0o777 == 0o750
        assert fixture.layout.graph_path.stat().st_mode & 0o777 == 0o640
        assert manifest_path.parent.stat().st_mode & 0o777 == 0o700
        assert manifest_path.stat().st_mode & 0o777 == 0o600
        assert vector_artifact.stat().st_mode & 0o777 == 0o600


@pytest.mark.asyncio
async def test_discovery_distinguishes_absent_unsupported_incomplete_and_corrupt(
    tmp_path: Path,
) -> None:
    absent_layout = MemoryMaintenanceLayout(
        vector_directory=tmp_path / "absent" / "vector",
        graph_path=tmp_path / "absent" / "graph.gpickle",
        recovery_directory=tmp_path / "absent" / "recovery",
        log_directory=tmp_path / "absent" / "logs",
    )
    absent = await MemoryMaintenanceParticipant(
        absent_layout, graph_store=None
    ).discover()
    assert [store.state for store in absent.stores] == [
        StoreDiscoveryState.CONFIGURED_ABSENT,
        StoreDiscoveryState.CONFIGURED_ABSENT,
        StoreDiscoveryState.NOT_CONFIGURED,
    ]

    fixture = await _recovery_fixture(tmp_path / "configured")
    unsupported = await MemoryMaintenanceParticipant(
        fixture.layout,
        graph_store=fixture.graph,
        access_buffer=None,
    ).discover()
    assert unsupported.stores[2].state is StoreDiscoveryState.UNSUPPORTED

    await fixture.access_buffer.record_access("p-1", "long_term")
    incomplete = await fixture.participant.discover()
    assert incomplete.stores[2].state is StoreDiscoveryState.INCOMPLETE
    assert not incomplete.snapshot_supported

    fixture.layout.graph_path.write_bytes(b"not a graph")
    corrupt = await fixture.participant.discover()
    assert corrupt.stores[1].state is StoreDiscoveryState.CORRUPT


@pytest.mark.asyncio
async def test_configured_absent_graph_is_snapshotted_and_restored_exactly(
    tmp_path: Path,
) -> None:
    fixture = await _recovery_fixture(tmp_path)
    fixture.layout.graph_path.unlink()
    graph = ElementXGraphStore(str(fixture.layout.graph_path))
    participant = MemoryMaintenanceParticipant(
        fixture.layout,
        graph_store=graph,
        access_buffer=fixture.access_buffer,
    )
    absent_fixture = RecoveryFixture(
        fixture.root,
        fixture.layout,
        graph,
        fixture.access_buffer,
        participant,
    )

    discovery = await participant.discover()
    assert discovery.snapshot_supported
    assert discovery.stores[1].state is StoreDiscoveryState.CONFIGURED_ABSENT

    manifest_path = await _create_snapshot(absent_fixture, "absent-graph")
    manifest = MemorySnapshotManifest.model_validate_json(manifest_path.read_text())
    assert manifest.graph.state is StoreDiscoveryState.CONFIGURED_ABSENT
    assert manifest.graph.artifact_filename is None
    assert manifest.graph.artifact_sha256 is None
    assert manifest.graph.artifact_size_bytes is None
    assert not fixture.layout.graph_path.exists()

    await graph.add_node(
        GraphNode(
            id="post-snapshot-node",
            type="Entity",
            label="Post snapshot node",
            provenance=ProvenanceMetadata(
                source_id="post-snapshot",
                source_type="test",
            ),
        )
    )
    assert fixture.layout.graph_path.exists()

    async with participant.maintenance_quiescence(
        MemoryRecoveryOperation.RESTORE
    ) as token:
        restored = await participant.restore_snapshot(manifest_path, token)

    assert restored.verified
    assert not fixture.layout.graph_path.exists()
    assert await graph.node_count() == 0
    assert (await participant.verify_live(manifest_path)).verified


@pytest.mark.asyncio
async def test_snapshot_detects_missing_corrupt_and_unverified_artifacts_before_pickle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = await _recovery_fixture(tmp_path)
    manifest_path = await _create_snapshot(fixture)
    manifest = MemorySnapshotManifest.model_validate_json(manifest_path.read_text())
    graph_artifact = manifest_path.parent / manifest.graph.artifact_filename

    original_graph = graph_artifact.read_bytes()
    graph_artifact.write_bytes(pickle.dumps({"unexpected": True}))
    monkeypatch.setattr(
        "friday_memory.adapters.graph.pickle.loads",
        lambda _stream: pytest.fail("checksum mismatch must precede pickle load"),
    )
    corrupt = await fixture.participant.verify_snapshot(manifest_path)
    assert not corrupt.verified
    assert corrupt.errors[0].code is MemoryRecoveryErrorCode.CHECKSUM_MISMATCH

    graph_artifact.write_bytes(original_graph)
    graph_artifact.unlink()
    missing = await fixture.participant.verify_snapshot(manifest_path)
    assert not missing.verified
    assert missing.errors[0].code is MemoryRecoveryErrorCode.SNAPSHOT_INCOMPLETE

    payload = manifest.model_dump(mode="json")
    payload["verified"] = False
    manifest_path.write_text(json.dumps(payload))
    incomplete = await fixture.participant.verify_snapshot(manifest_path)
    assert not incomplete.verified
    assert incomplete.errors[0].code is MemoryRecoveryErrorCode.SNAPSHOT_INCOMPLETE


@pytest.mark.asyncio
async def test_graph_backend_corruption_returns_typed_failure(tmp_path: Path) -> None:
    fixture = await _recovery_fixture(tmp_path)
    manifest_path = await _create_snapshot(fixture)
    manifest = MemorySnapshotManifest.model_validate_json(manifest_path.read_text())
    artifact = manifest_path.parent / manifest.graph.artifact_filename
    corrupt_payload = b"not a valid graph pickle"
    artifact.write_bytes(corrupt_payload)
    manifest_payload = manifest.model_dump(mode="json")
    manifest_payload["graph"]["artifact_sha256"] = hashlib.sha256(
        corrupt_payload
    ).hexdigest()
    manifest_payload["graph"]["artifact_size_bytes"] = len(corrupt_payload)
    manifest_path.write_text(json.dumps(manifest_payload))

    result = await fixture.participant.verify_snapshot(manifest_path)
    assert not result.verified
    assert result.errors[0].code is MemoryRecoveryErrorCode.STORE_CORRUPT


@pytest.mark.asyncio
async def test_expected_io_and_chroma_failures_are_package_owned(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = await _recovery_fixture(tmp_path)
    manifest_path = await _create_snapshot(fixture)

    def inaccessible(_path: Path) -> str:
        raise PermissionError("synthetic permission race")

    monkeypatch.setattr(
        MemoryMaintenanceParticipant,
        "_sha256",
        staticmethod(inaccessible),
    )
    inaccessible_result = await fixture.participant.verify_snapshot(manifest_path)
    assert not inaccessible_result.verified
    assert (
        inaccessible_result.errors[0].code
        is MemoryRecoveryErrorCode.SNAPSHOT_INCOMPLETE
    )
    monkeypatch.undo()

    def backend_failure(
        _vector_directory: Path, _snapshot: ChromaLogicalSnapshot
    ) -> None:
        raise InvalidArgumentError("synthetic backend failure")

    monkeypatch.setattr(
        MemoryMaintenanceParticipant,
        "_restore_vector_snapshot",
        staticmethod(backend_failure),
    )
    async with fixture.participant.maintenance_quiescence(
        MemoryRecoveryOperation.RESTORE
    ) as token:
        with pytest.raises(MemorySnapshotError, match="Friday Memory restore failed"):
            await fixture.participant.restore_snapshot(manifest_path, token)


@pytest.mark.asyncio
async def test_vector_verify_parses_the_exact_checksummed_payload(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = await _recovery_fixture(tmp_path)
    manifest_path = await _create_snapshot(fixture)
    manifest = MemorySnapshotManifest.model_validate_json(manifest_path.read_text())
    artifact = manifest_path.parent / manifest.vector.artifact_filename
    original_read = MemoryMaintenanceParticipant._read_checked_payload

    def replace_after_checksum(path: Path, expected: str) -> bytes:
        payload = original_read(path, expected)
        if path == artifact:
            path.write_bytes(b"different bytes after checksum")
        return payload

    monkeypatch.setattr(
        MemoryMaintenanceParticipant,
        "_read_checked_payload",
        staticmethod(replace_after_checksum),
    )
    result = await fixture.participant.verify_snapshot(manifest_path)
    assert result.verified


@pytest.mark.asyncio
async def test_vector_restore_rechecks_artifact_before_live_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = await _recovery_fixture(tmp_path)
    manifest_path = await _create_snapshot(fixture)
    manifest = MemorySnapshotManifest.model_validate_json(manifest_path.read_text())
    artifact = manifest_path.parent / manifest.vector.artifact_filename
    original_verify = fixture.participant.verify_snapshot

    async def verify_then_tamper(path: str | Path) -> MemoryOperationResult:
        result = await original_verify(path)
        if result.verified:
            artifact.write_bytes(b"tampered after verification")
        return result

    monkeypatch.setattr(fixture.participant, "verify_snapshot", verify_then_tamper)
    client = chromadb.PersistentClient(path=str(fixture.layout.vector_directory))
    before = {collection.name: collection.count() for collection in client.list_collections()}
    async with fixture.participant.maintenance_quiescence(
        MemoryRecoveryOperation.RESTORE
    ) as token:
        with pytest.raises(MemorySnapshotError):
            await fixture.participant.restore_snapshot(manifest_path, token)
    after = {collection.name: collection.count() for collection in client.list_collections()}
    assert after == before


@pytest.mark.asyncio
async def test_memory_restore_revalidates_apply_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = await _recovery_fixture(tmp_path)
    manifest_path = await _create_snapshot(fixture)
    original_verify = fixture.participant.verify_snapshot

    async def verify_then_change_manifest(
        path: str | Path,
    ) -> MemoryOperationResult:
        result = await original_verify(path)
        if result.verified:
            payload = json.loads(manifest_path.read_text())
            payload["vector"]["artifact_filename"] = "../outside.json"
            manifest_path.write_text(json.dumps(payload))
        return result

    monkeypatch.setattr(
        fixture.participant,
        "verify_snapshot",
        verify_then_change_manifest,
    )
    client = chromadb.PersistentClient(path=str(fixture.layout.vector_directory))
    before = {collection.name: collection.count() for collection in client.list_collections()}
    async with fixture.participant.maintenance_quiescence(
        MemoryRecoveryOperation.RESTORE
    ) as token:
        with pytest.raises(MemorySnapshotError):
            await fixture.participant.restore_snapshot(manifest_path, token)
    after = {collection.name: collection.count() for collection in client.list_collections()}
    assert after == before


@pytest.mark.asyncio
async def test_unknown_chroma_configuration_fails_closed(tmp_path: Path) -> None:
    fixture = await _recovery_fixture(tmp_path)
    manifest_path = await _create_snapshot(fixture)
    manifest = MemorySnapshotManifest.model_validate_json(manifest_path.read_text())
    vector_artifact = manifest_path.parent / manifest.vector.artifact_filename
    snapshot_payload = json.loads(vector_artifact.read_text())
    snapshot_payload["collections"][0]["configuration"]["embedding_function"][
        "name"
    ] = "unsupported-recovery-function"
    artifact_payload = _canonical_json(snapshot_payload)
    vector_artifact.write_bytes(artifact_payload)

    manifest_payload = manifest.model_dump(mode="json")
    manifest_payload["vector"]["artifact_sha256"] = hashlib.sha256(
        artifact_payload
    ).hexdigest()
    manifest_payload["vector"]["artifact_size_bytes"] = len(artifact_payload)
    manifest_path.write_text(json.dumps(manifest_payload))

    verification = await fixture.participant.verify_snapshot(manifest_path)
    assert not verification.verified
    assert verification.errors[0].code is MemoryRecoveryErrorCode.STORE_UNSUPPORTED


@pytest.mark.asyncio
async def test_restore_preflights_all_records_before_live_collection_deletion(
    tmp_path: Path,
) -> None:
    fixture = await _recovery_fixture(tmp_path)
    manifest_path = await _create_snapshot(fixture)
    manifest = MemorySnapshotManifest.model_validate_json(manifest_path.read_text())
    vector_artifact = manifest_path.parent / manifest.vector.artifact_filename
    snapshot_payload = json.loads(vector_artifact.read_text())
    snapshot_payload["collections"][0]["records"][1]["metadata"] = {
        "unsupported_nested_value": {"nested": True}
    }
    artifact_payload = _canonical_json(snapshot_payload)
    vector_artifact.write_bytes(artifact_payload)

    manifest_payload = manifest.model_dump(mode="json")
    manifest_payload["vector"]["artifact_sha256"] = hashlib.sha256(
        artifact_payload
    ).hexdigest()
    manifest_payload["vector"]["artifact_size_bytes"] = len(artifact_payload)
    changed_collection = snapshot_payload["collections"][0]
    manifest_payload["vector"]["collections"][0]["logical_digest"] = hashlib.sha256(
        _canonical_json(changed_collection)
    ).hexdigest()
    manifest_path.write_text(json.dumps(manifest_payload))
    verification = await fixture.participant.verify_snapshot(manifest_path)
    assert not verification.verified
    assert verification.errors[0].code is MemoryRecoveryErrorCode.STORE_UNSUPPORTED

    client = chromadb.PersistentClient(path=str(fixture.layout.vector_directory))
    before = {collection.name: collection.count() for collection in client.list_collections()}
    async with fixture.participant.maintenance_quiescence(
        MemoryRecoveryOperation.RESTORE
    ) as token:
        with pytest.raises(MemorySnapshotError):
            await fixture.participant.restore_snapshot(manifest_path, token)
    after = {collection.name: collection.count() for collection in client.list_collections()}
    assert after == before


@pytest.mark.asyncio
async def test_bounded_pagination_has_stable_order_independent_digest(
    tmp_path: Path,
) -> None:
    fixture = await _recovery_fixture(tmp_path)
    collection = chromadb.PersistentClient(
        path=str(fixture.layout.vector_directory)
    ).get_collection("primary")
    extra_count = 137
    bulk_embeddings: list[Sequence[float] | Sequence[int]] = [
        [float(index + 1), float(extra_count - index)]
        for index in reversed(range(extra_count))
    ]
    collection.add(
        ids=[f"bulk-{index:03d}" for index in reversed(range(extra_count))],
        documents=[f"bulk document {index}" for index in reversed(range(extra_count))],
        metadatas=[{"bulk": index} for index in reversed(range(extra_count))],
        embeddings=bulk_embeddings,
    )

    first_manifest_path = await _create_snapshot(fixture, "paged-1")
    second_manifest_path = await _create_snapshot(fixture, "paged-2")
    first_manifest = MemorySnapshotManifest.model_validate_json(
        first_manifest_path.read_text()
    )
    second_manifest = MemorySnapshotManifest.model_validate_json(
        second_manifest_path.read_text()
    )
    first_primary = first_manifest.vector.collections[0]
    second_primary = second_manifest.vector.collections[0]
    assert (
        first_manifest.vector.maximum_float32_ulp_drift
        == CHROMA_REBUILD_MAXIMUM_FLOAT32_ULP_DRIFT
    )
    assert first_primary.record_count == extra_count + 2
    assert first_primary.logical_digest == second_primary.logical_digest

    first_artifact = ChromaLogicalSnapshot.model_validate_json(
        (first_manifest_path.parent / first_manifest.vector.artifact_filename).read_text()
    )
    record_ids = [record.id for record in first_artifact.collections[0].records]
    assert record_ids == sorted(record_ids)

    schemas = fixture.participant._prepare_vector_restore(first_artifact)
    with TemporaryDirectory(prefix="friday-chroma-ulp-regression-") as temp_dir:
        rebuilt_client = fixture.participant._open_client(Path(temp_dir))
        fixture.participant._populate_vector_client(
            rebuilt_client,
            first_artifact,
            schemas,
        )
        rebuilt_artifact, _ = fixture.participant._export_vector_snapshot(
            Path(temp_dir)
        )
    observed_drifts = [
        abs(
            fixture.participant._float32_ordered_integer(expected_value)
            - fixture.participant._float32_ordered_integer(actual_value)
        )
        for expected_collection, actual_collection in zip(
            first_artifact.collections,
            rebuilt_artifact.collections,
            strict=True,
        )
        for expected_record, actual_record in zip(
            expected_collection.records,
            actual_collection.records,
            strict=True,
        )
        for expected_value, actual_value in zip(
            expected_record.embedding,
            actual_record.embedding,
            strict=True,
        )
    ]
    assert max(observed_drifts) <= CHROMA_REBUILD_MAXIMUM_FLOAT32_ULP_DRIFT

    expected_record = first_artifact.collections[0].records[0]
    two_ulp_embedding = list(expected_record.embedding)
    two_ulp_embedding[0] = _shift_positive_float32(two_ulp_embedding[0], 2)
    two_ulp_record = expected_record.model_copy(
        update={"embedding": two_ulp_embedding}
    )
    two_ulp_collection = first_artifact.collections[0].model_copy(
        update={
            "records": [
                two_ulp_record,
                *first_artifact.collections[0].records[1:],
            ]
        }
    )
    two_ulp_snapshot = first_artifact.model_copy(
        update={
            "collections": [
                two_ulp_collection,
                *first_artifact.collections[1:],
            ]
        }
    )
    assert MemoryMaintenanceParticipant._vector_snapshots_equivalent(
        first_artifact,
        two_ulp_snapshot,
        CHROMA_REBUILD_MAXIMUM_FLOAT32_ULP_DRIFT,
    )

    three_ulp_embedding = list(expected_record.embedding)
    three_ulp_embedding[0] = _shift_positive_float32(three_ulp_embedding[0], 3)
    three_ulp_record = expected_record.model_copy(
        update={"embedding": three_ulp_embedding}
    )
    three_ulp_collection = first_artifact.collections[0].model_copy(
        update={
            "records": [
                three_ulp_record,
                *first_artifact.collections[0].records[1:],
            ]
        }
    )
    three_ulp_snapshot = first_artifact.model_copy(
        update={
            "collections": [
                three_ulp_collection,
                *first_artifact.collections[1:],
            ]
        }
    )
    assert not MemoryMaintenanceParticipant._vector_snapshots_equivalent(
        first_artifact,
        three_ulp_snapshot,
        CHROMA_REBUILD_MAXIMUM_FLOAT32_ULP_DRIFT,
    )

    changed_document_record = expected_record.model_copy(
        update={"document": "changed"}
    )
    changed_document_collection = first_artifact.collections[0].model_copy(
        update={
            "records": [
                changed_document_record,
                *first_artifact.collections[0].records[1:],
            ]
        }
    )
    changed_document_snapshot = first_artifact.model_copy(
        update={
            "collections": [
                changed_document_collection,
                *first_artifact.collections[1:],
            ]
        }
    )
    assert not MemoryMaintenanceParticipant._vector_snapshots_equivalent(
        first_artifact,
        changed_document_snapshot,
        CHROMA_REBUILD_MAXIMUM_FLOAT32_ULP_DRIFT,
    )

    invalid_policy = first_manifest.model_dump(mode="json")
    invalid_policy["vector"]["maximum_float32_ulp_drift"] = 3
    with pytest.raises(ValidationError):
        MemorySnapshotManifest.model_validate(invalid_policy)

    for _ in range(2):
        async with fixture.participant.maintenance_quiescence(
            MemoryRecoveryOperation.RESTORE
        ) as token:
            restored = await fixture.participant.restore_snapshot(
                first_manifest_path, token
            )
        assert restored.verified


@pytest.mark.asyncio
async def test_bounded_index_probe_accepts_duplicate_embedding_ties(
    tmp_path: Path,
) -> None:
    fixture = await _recovery_fixture(tmp_path)
    collection = chromadb.PersistentClient(
        path=str(fixture.layout.vector_directory)
    ).get_collection("primary")
    collection.add(
        ids="duplicate-vector",
        documents="duplicate",
        metadatas={"rank": 4},
        embeddings=[1.0, 0.0],
    )

    manifest_path = await _create_snapshot(fixture)
    manifest = MemorySnapshotManifest.model_validate_json(manifest_path.read_text())
    assert manifest.vector.collections[0].record_count == 3
    assert manifest.vector.collections[0].query_probe_count == 1


@pytest.mark.asyncio
async def test_graph_verification_deserializes_the_checksummed_payload(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = await _recovery_fixture(tmp_path)
    manifest_path = await _create_snapshot(fixture)
    manifest = MemorySnapshotManifest.model_validate_json(manifest_path.read_text())
    artifact = manifest_path.parent / manifest.graph.artifact_filename
    original_require = ElementXGraphStore._require_checksum

    def replace_after_checksum(path: Path, expected: str) -> bytes:
        payload = original_require(path, expected)
        path.write_bytes(b"different bytes after checksum")
        return payload

    monkeypatch.setattr(
        ElementXGraphStore,
        "_require_checksum",
        staticmethod(replace_after_checksum),
    )
    summary = await fixture.graph.verify_recovery_snapshot(
        artifact, manifest.graph.artifact_sha256
    )
    assert summary.node_count == 1


@pytest.mark.asyncio
async def test_memory_snapshot_fsyncs_bundle_directory_entries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX durability assertion")
    fixture = await _recovery_fixture(tmp_path)
    calls: list[Path] = []
    original_fsync = MemoryMaintenanceParticipant._fsync_directory

    def recording_fsync(path: Path) -> None:
        calls.append(path)
        original_fsync(path)

    monkeypatch.setattr(
        MemoryMaintenanceParticipant,
        "_fsync_directory",
        staticmethod(recording_fsync),
    )
    manifest_path = await _create_snapshot(fixture)
    assert calls.count(manifest_path.parent) >= 2


@pytest.mark.asyncio
async def test_live_query_index_failure_is_reported(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = await _recovery_fixture(tmp_path)
    manifest_path = await _create_snapshot(fixture)

    def broken_query(self: Collection, *args: object, **kwargs: object) -> dict[str, object]:
        return {"ids": [[]], "distances": [[]]}

    original_export = fixture.participant._export_vector_snapshot

    def broken_live_export(
        vector_directory: Path,
    ) -> tuple[ChromaLogicalSnapshot, list[ChromaCollectionManifest]]:
        with monkeypatch.context() as live_query_patch:
            live_query_patch.setattr(Collection, "query", broken_query)
            snapshot, manifests = original_export(vector_directory)
        return snapshot, manifests

    monkeypatch.setattr(
        fixture.participant,
        "_export_vector_snapshot",
        broken_live_export,
    )
    result = await fixture.participant.verify_live(manifest_path)
    assert not result.verified
    assert result.errors[0].code is MemoryRecoveryErrorCode.INTEGRITY_FAILED


@pytest.mark.asyncio
async def test_memory_verify_live_revalidates_apply_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = await _recovery_fixture(tmp_path)
    manifest_path = await _create_snapshot(fixture)
    original_verify = fixture.participant.verify_snapshot

    async def verify_then_change_manifest(
        path: str | Path,
    ) -> MemoryOperationResult:
        result = await original_verify(path)
        if result.verified:
            payload = json.loads(manifest_path.read_text())
            payload["vector"]["artifact_filename"] = "../outside.json"
            manifest_path.write_text(json.dumps(payload))
        return result

    monkeypatch.setattr(
        fixture.participant,
        "verify_snapshot",
        verify_then_change_manifest,
    )
    result = await fixture.participant.verify_live(manifest_path)
    assert not result.verified
    assert result.errors[0].code is MemoryRecoveryErrorCode.INTEGRITY_FAILED


@pytest.mark.asyncio
async def test_quiescence_token_is_operation_and_issuer_bound(tmp_path: Path) -> None:
    fixture = await _recovery_fixture(tmp_path)
    fabricated = MemoryQuiescenceToken(
        "other",
        fixture.participant.layout_fingerprint,
        "other",
        MemoryRecoveryOperation.SNAPSHOT,
    )
    with pytest.raises(MemoryQuiescenceError):
        await fixture.participant.create_snapshot("run-1", fabricated)

    async with fixture.participant.maintenance_quiescence(
        MemoryRecoveryOperation.RESTORE
    ) as wrong_operation:
        with pytest.raises(MemoryQuiescenceError):
            await fixture.participant.create_snapshot("run-1", wrong_operation)

    async with fixture.participant.maintenance_quiescence(
        MemoryRecoveryOperation.SNAPSHOT
    ) as token:
        result = await fixture.participant.create_snapshot("run-1", token)
    assert result.verified
    with pytest.raises(MemoryQuiescenceError):
        await fixture.participant.create_snapshot("run-2", token)


def test_layout_uses_cwd_and_explicit_legacy_mapping(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    layout = MemoryMaintenanceLayout(
        vector_directory=Path("vector"),
        graph_path=Path("graph.gpickle"),
        recovery_directory=Path("recovery"),
        log_directory=Path("logs"),
    )
    assert layout.vector_directory == tmp_path / "vector"

    legacy = LegacySingleRootLayoutAdapter.adapt(
        "legacy",
        vector_path="declared-vector",
        graph_path="declared-graph.gpickle",
        access_buffer_wal_path="declared-access.wal",
        recovery_path="declared-recovery",
        log_path="declared-logs",
    )
    assert legacy.vector_directory == tmp_path / "legacy" / "declared-vector"
    assert legacy.graph_path == tmp_path / "legacy" / "declared-graph.gpickle"


def test_layout_rejects_overlap_recursive_and_symlink_alias(tmp_path: Path) -> None:
    vector_path = tmp_path / "state" / "vector"
    vector_path.mkdir(parents=True)
    graph_path = tmp_path / "state" / "graph.gpickle"

    overlapping = MemoryMaintenanceLayout(
        vector_directory=vector_path,
        graph_path=graph_path,
        recovery_directory=tmp_path / "state",
        log_directory=tmp_path / "logs",
    )
    with pytest.raises(MemoryLayoutError):
        MemoryMaintenanceParticipant(overlapping, graph_store=None)

    alias = tmp_path / "vector-alias"
    try:
        alias.symlink_to(vector_path, target_is_directory=True)
    except OSError:
        pytest.skip("Directory symlinks are not available")
    aliased = MemoryMaintenanceLayout(
        vector_directory=vector_path,
        graph_path=graph_path,
        recovery_directory=alias,
        log_directory=tmp_path / "logs",
    )
    with pytest.raises(MemoryLayoutError):
        MemoryMaintenanceParticipant(aliased, graph_store=None)


def test_memory_manifest_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        MemorySnapshotManifest.model_validate({"unexpected": "schema drift"})
