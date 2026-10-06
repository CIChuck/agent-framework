"""Focused safety tests for durable Friday Chat reorganization foundations."""

from __future__ import annotations

import fcntl
import multiprocessing
import os
import platform
import stat
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import friday_chat.reorganization.durability as durability_module
import friday_chat.reorganization.layout as layout_module
import pytest
from friday_chat.reorganization import (
    AtomicJsonStore,
    DarwinLayoutLeaseRegistry,
    DurableArtifactError,
    FridayChatMaintenanceLayout,
    JournalSafeBoundary,
    JournalState,
    LayoutLeaseContentionError,
    LayoutLeaseError,
    MaintenanceArtifactStore,
    MaintenanceLayoutError,
    MaintenancePlatformError,
    OperationTrigger,
    ParticipantKind,
    ParticipantManifestReference,
    ProgressStep,
    RecoveryBundleManifest,
    RecoveryJournal,
    ReorganizationError,
    ReorganizationErrorCode,
    ReorganizationMode,
    ResultStatus,
    StaleLeaseReconciliationError,
)
from friday_chat.reorganization.contracts import StrictContractModel
from friday_chat.reorganization.durability import ensure_owner_directory
from friday_memory import (
    AccessBufferRecoveryStrategy,
    AccessBufferSnapshotManifest,
    GraphSnapshotManifest,
    MemorySnapshotManifest,
    MemorySnapshotStrategy,
    StoreDiscoveryState,
    VectorSnapshotManifest,
)
from friday_transcript import TranscriptSnapshotManifest
from pydantic import ValidationError

NOW = datetime(2026, 8, 6, 12, 0, tzinfo=UTC)
DARWIN_ONLY = pytest.mark.skipif(
    platform.system() != "Darwin",
    reason="lease execution semantics are verified only on Darwin",
)


class RevisionRecord(StrictContractModel):
    """Small strict model used to exercise the generic atomic store."""

    revision: int
    value: str


def _make_layout(
    root: Path,
    name: str,
    *,
    vector: Path | None = None,
    graph: Path | None = None,
    access_wal: Path | None = None,
    transcript: Path | None = None,
    recovery: Path | None = None,
    logs: Path | None = None,
) -> FridayChatMaintenanceLayout:
    base = root / name
    cwd = base / "cwd"
    cwd.mkdir(parents=True, exist_ok=True)
    vector_path = vector or base / "vector"
    graph_path = graph or base / "graph.json"
    wal_path = access_wal or base / "access.wal"
    transcript_path = transcript or base / "transcript.sqlite3"
    vector_path.mkdir(parents=True, exist_ok=True)
    for path in (graph_path, wal_path, transcript_path):
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(b"fixture")
    return FridayChatMaintenanceLayout.resolve_once(
        captured_process_cwd=cwd,
        vector_directory=vector_path,
        graph_path=graph_path,
        access_buffer_wal_path=wal_path,
        transcript_database_path=transcript_path,
        recovery_root=recovery or base / "recovery",
        log_root=logs or base / "logs",
    )


def _new_persisted_journal(
    layout: FridayChatMaintenanceLayout,
    *,
    trigger: OperationTrigger = OperationTrigger.MANUAL,
    mode: ReorganizationMode | None = ReorganizationMode.BACKUP,
    created_at: datetime = NOW,
) -> tuple[MaintenanceArtifactStore, RecoveryJournal, str]:
    store = MaintenanceArtifactStore(layout)
    journal = store.new_journal(
        application_id="friday-chat",
        application_version="0.1.0",
        trigger=trigger,
        requested_mode=mode,
        created_at=created_at,
    )
    artifact = store.write_initial_journal(journal)
    return store, journal, artifact.sha256


def _persist_transition(
    store: MaintenanceArtifactStore,
    previous: RecoveryJournal,
    current: RecoveryJournal,
    checksum: str,
) -> tuple[RecoveryJournal, str]:
    artifact = store.write_journal_transition(
        previous,
        current,
        expected_current_sha256=checksum,
    )
    return current, artifact.sha256


def _complete_pre_mutation(
    store: MaintenanceArtifactStore,
    journal: RecoveryJournal,
    checksum: str,
) -> tuple[RecoveryJournal, str]:
    current = journal.transition(
        JournalState.COMPLETE,
        updated_at=journal.updated_at + timedelta(microseconds=1),
        safe_boundary=JournalSafeBoundary.LIVE_UNMODIFIED,
        terminal_status=ResultStatus.CANCELLED,
    )
    return _persist_transition(store, journal, current, checksum)


def _advance_to_recovery_required(
    store: MaintenanceArtifactStore,
    journal: RecoveryJournal,
    checksum: str,
) -> tuple[RecoveryJournal, str]:
    timestamp = journal.updated_at
    snapshot_started = journal.transition(
        JournalState.SNAPSHOT_IN_PROGRESS,
        updated_at=timestamp + timedelta(microseconds=1),
        safe_boundary=JournalSafeBoundary.LIVE_UNMODIFIED,
        completed_steps=(ProgressStep.PREFLIGHT,),
    )
    snapshot_started, checksum = _persist_transition(
        store, journal, snapshot_started, checksum
    )
    snapshot_verified = snapshot_started.transition(
        JournalState.SNAPSHOT_VERIFIED,
        updated_at=timestamp + timedelta(microseconds=2),
        safe_boundary=JournalSafeBoundary.SNAPSHOT_VERIFIED_LIVE_UNMODIFIED,
        bundle_manifest_path=store.bundle_path(journal.run_id),
        bundle_manifest_sha256="a" * 64,
        completed_steps=(ProgressStep.PREFLIGHT, ProgressStep.SNAPSHOTTING),
    )
    snapshot_verified, checksum = _persist_transition(
        store, snapshot_started, snapshot_verified, checksum
    )
    mutating = snapshot_verified.transition(
        JournalState.MUTATION_IN_PROGRESS,
        updated_at=timestamp + timedelta(microseconds=3),
        safe_boundary=JournalSafeBoundary.MUTATION_UNCERTAIN,
    )
    mutating, checksum = _persist_transition(
        store, snapshot_verified, mutating, checksum
    )
    rolling_back = mutating.transition(
        JournalState.ROLLBACK_IN_PROGRESS,
        updated_at=timestamp + timedelta(microseconds=4),
        safe_boundary=JournalSafeBoundary.MUTATION_UNCERTAIN,
    )
    rolling_back, checksum = _persist_transition(
        store, mutating, rolling_back, checksum
    )
    recovery = rolling_back.transition(
        JournalState.RECOVERY_REQUIRED,
        updated_at=timestamp + timedelta(microseconds=5),
        safe_boundary=JournalSafeBoundary.RECOVERY_REQUIRED,
    )
    return _persist_transition(store, rolling_back, recovery, checksum)


def _attempt_process_acquire(
    layout_json: str,
    journal_json: str,
    namespace: str,
    result_queue: Any,
) -> None:
    layout = FridayChatMaintenanceLayout.model_validate_json(layout_json)
    journal = RecoveryJournal.model_validate_json(journal_json)
    registry = DarwinLayoutLeaseRegistry(namespace_root=Path(namespace))
    try:
        registry.acquire(layout, journal)
    except LayoutLeaseContentionError:
        result_queue.put("contended")
    except Exception as exc:  # pragma: no cover - reported to the parent assertion
        result_queue.put(type(exc).__name__)
    else:  # pragma: no cover - safety regression signal
        result_queue.put("acquired")


def _simulate_process_exit(handle: Any) -> None:
    fcntl.flock(handle._descriptor, fcntl.LOCK_UN)
    os.close(handle._descriptor)
    handle._released = True


def test_layout_resolution_is_stable_and_cwd_is_not_in_fingerprint(
    tmp_path: Path,
) -> None:
    absolute = _make_layout(tmp_path, "absolute")
    other_cwd = tmp_path / "other-cwd"
    other_cwd.mkdir()
    same_paths = FridayChatMaintenanceLayout.resolve_once(
        captured_process_cwd=other_cwd,
        vector_directory=absolute.vector_directory,
        graph_path=absolute.graph_path,
        access_buffer_wal_path=absolute.access_buffer_wal_path,
        transcript_database_path=absolute.transcript_database_path,
        recovery_root=absolute.recovery_root,
        log_root=absolute.log_root,
    )

    assert same_paths.layout_fingerprint == absolute.layout_fingerprint
    assert same_paths.captured_process_cwd != absolute.captured_process_cwd


def test_layout_rejects_symlink_overlap_hardlink_and_stat_uncertainty(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    layout = _make_layout(tmp_path, "unsafe")
    alias = tmp_path / "hardlink-graph.json"
    os.link(layout.graph_path, alias)
    with pytest.raises(ValidationError, match="alias or overlap"):
        FridayChatMaintenanceLayout.resolve_once(
            captured_process_cwd=layout.captured_process_cwd,
            vector_directory=layout.vector_directory,
            graph_path=layout.graph_path,
            access_buffer_wal_path=layout.access_buffer_wal_path,
            transcript_database_path=alias,
            recovery_root=tmp_path / "hardlink-recovery",
            log_root=tmp_path / "hardlink-logs",
        )

    symlink = tmp_path / "vector-link"
    symlink.symlink_to(layout.vector_directory, target_is_directory=True)
    with pytest.raises(ValidationError, match="symlinks"):
        FridayChatMaintenanceLayout.resolve_once(
            captured_process_cwd=layout.captured_process_cwd,
            vector_directory=symlink,
            graph_path=tmp_path / "symlink-graph",
            access_buffer_wal_path=tmp_path / "symlink-wal",
            transcript_database_path=tmp_path / "symlink-transcript",
            recovery_root=tmp_path / "symlink-recovery",
            log_root=tmp_path / "symlink-logs",
        )

    original_stat = Path.stat

    def uncertain_stat(path: Path, *, follow_symlinks: bool = True) -> os.stat_result:
        if path == layout.graph_path:
            raise PermissionError("injected")
        return original_stat(path, follow_symlinks=follow_symlinks)

    monkeypatch.setattr(Path, "stat", uncertain_stat)
    with pytest.raises(MaintenanceLayoutError, match="cannot be inspected"):
        layout_module._same_existing_inode(
            layout.graph_path,
            layout.transcript_database_path,
        )


def test_declared_path_revalidation_detects_post_resolution_hardlink_alias(
    tmp_path: Path,
) -> None:
    layout = _make_layout(tmp_path, "toctou-hardlink")
    layout.transcript_database_path.unlink()
    os.link(layout.graph_path, layout.transcript_database_path)

    with pytest.raises(MaintenanceLayoutError, match="alias or overlap"):
        layout_module.validate_declared_paths(layout.all_declared_paths)


@DARWIN_ONLY
def test_case_insensitive_component_alias_and_post_resolution_drift_fail_closed(
    tmp_path: Path,
) -> None:
    canonical_root = tmp_path / "CaseRoot"
    lower_root = tmp_path / "caseroot"
    canonical_root.mkdir()
    if not lower_root.exists():
        pytest.skip("test filesystem is genuinely case-sensitive")
    vector = canonical_root / "vector"
    vector.mkdir()
    graph = canonical_root / "graph.json"
    wal = canonical_root / "access.wal"
    transcript = canonical_root / "transcript.sqlite3"
    for path in (graph, wal, transcript):
        path.write_bytes(b"fixture")
    cwd = tmp_path / "cwd"
    cwd.mkdir()

    with pytest.raises(ValidationError, match="spelling is not canonical"):
        FridayChatMaintenanceLayout.resolve_once(
            captured_process_cwd=cwd,
            vector_directory=vector,
            graph_path=graph,
            access_buffer_wal_path=wal,
            transcript_database_path=transcript,
            recovery_root=lower_root / "vector" / "recovery",
            log_root=tmp_path / "alias-logs",
        )

    layout = FridayChatMaintenanceLayout.resolve_once(
        captured_process_cwd=cwd,
        vector_directory=vector,
        graph_path=graph,
        access_buffer_wal_path=wal,
        transcript_database_path=transcript,
        recovery_root=tmp_path / "case-recovery",
        log_root=tmp_path / "case-logs",
    )
    _, journal, _ = _new_persisted_journal(layout)
    canonical_root.rename(lower_root)
    registry = DarwinLayoutLeaseRegistry(namespace_root=tmp_path / "case-registry")
    with pytest.raises(LayoutLeaseError, match="identity is unsafe"):
        registry.acquire(layout, journal)


def test_journal_transition_invariants_are_strict_and_history_aware(
    tmp_path: Path,
) -> None:
    layout = _make_layout(tmp_path, "journal")
    store, journal, checksum = _new_persisted_journal(layout)
    error = ReorganizationError(
        code=ReorganizationErrorCode.SNAPSHOT_FAILED,
        message="content-safe failure",
    )
    started = journal.transition(
        JournalState.SNAPSHOT_IN_PROGRESS,
        updated_at=journal.updated_at + timedelta(microseconds=1),
        safe_boundary=JournalSafeBoundary.LIVE_UNMODIFIED,
        errors=(error,),
    )

    with pytest.raises(ValueError, match="timestamp must increase"):
        started.transition(
            JournalState.SNAPSHOT_VERIFIED,
            updated_at=started.updated_at,
            safe_boundary=JournalSafeBoundary.SNAPSHOT_VERIFIED_LIVE_UNMODIFIED,
            bundle_manifest_path=store.bundle_path(journal.run_id),
            bundle_manifest_sha256="a" * 64,
        )
    with pytest.raises(ValueError, match="errors must be append-only"):
        started.transition(
            JournalState.SNAPSHOT_VERIFIED,
            updated_at=started.updated_at + timedelta(microseconds=1),
            safe_boundary=JournalSafeBoundary.SNAPSHOT_VERIFIED_LIVE_UNMODIFIED,
            bundle_manifest_path=store.bundle_path(journal.run_id),
            bundle_manifest_sha256="a" * 64,
            errors=(),
        )
    with pytest.raises(ValidationError):
        RecoveryJournal.model_validate(
            {**journal.model_dump(mode="python"), "revision": "0"}
        )

    started, checksum = _persist_transition(store, journal, started, checksum)
    verified = started.transition(
        JournalState.SNAPSHOT_VERIFIED,
        updated_at=started.updated_at + timedelta(microseconds=1),
        safe_boundary=JournalSafeBoundary.SNAPSHOT_VERIFIED_LIVE_UNMODIFIED,
        bundle_manifest_path=store.bundle_path(journal.run_id),
        bundle_manifest_sha256="a" * 64,
    )
    mutating = verified.transition(
        JournalState.MUTATION_IN_PROGRESS,
        updated_at=verified.updated_at + timedelta(microseconds=1),
        safe_boundary=JournalSafeBoundary.MUTATION_UNCERTAIN,
    )
    with pytest.raises(ValidationError, match="transition is not legal"):
        mutating.transition(
            JournalState.RECOVERY_REQUIRED,
            updated_at=mutating.updated_at + timedelta(microseconds=1),
            safe_boundary=JournalSafeBoundary.RECOVERY_REQUIRED,
        )
    rollback = mutating.transition(
        JournalState.ROLLBACK_IN_PROGRESS,
        updated_at=mutating.updated_at + timedelta(microseconds=1),
        safe_boundary=JournalSafeBoundary.MUTATION_UNCERTAIN,
    )
    with pytest.raises(ValidationError, match="verified live boundary"):
        rollback.transition(
            JournalState.COMPLETE,
            updated_at=rollback.updated_at + timedelta(microseconds=1),
            safe_boundary=JournalSafeBoundary.SNAPSHOT_VERIFIED_LIVE_UNMODIFIED,
            terminal_status=ResultStatus.FAILED_ROLLED_BACK,
        )


def test_journal_store_rejects_stale_compare_and_swap(tmp_path: Path) -> None:
    layout = _make_layout(tmp_path, "cas")
    store, journal, checksum = _new_persisted_journal(layout)
    first = journal.transition(
        JournalState.SNAPSHOT_IN_PROGRESS,
        updated_at=journal.updated_at + timedelta(microseconds=1),
        safe_boundary=JournalSafeBoundary.LIVE_UNMODIFIED,
    )
    _persist_transition(store, journal, first, checksum)
    stale = journal.transition(
        JournalState.COMPLETE,
        updated_at=journal.updated_at + timedelta(microseconds=2),
        safe_boundary=JournalSafeBoundary.LIVE_UNMODIFIED,
        terminal_status=ResultStatus.CANCELLED,
    )

    with pytest.raises(DurableArtifactError, match="compare-and-swap"):
        store.write_journal_transition(
            journal,
            stale,
            expected_current_sha256=checksum,
        )


def test_atomic_store_rejects_corruption_modes_size_and_traversal(
    tmp_path: Path,
) -> None:
    root = tmp_path / "atomic"
    store = AtomicJsonStore(root, max_json_bytes=128)
    artifact = store.write_model("record.json", RevisionRecord(revision=0, value="ok"))
    assert stat.S_IMODE(root.stat().st_mode) == 0o700
    assert stat.S_IMODE(artifact.path.stat().st_mode) == 0o600

    with pytest.raises(DurableArtifactError, match="escapes"):
        store.read_model("../record.json", RevisionRecord)
    artifact.path.chmod(0o644)
    with pytest.raises(DurableArtifactError, match="owner-only"):
        store.read_model("record.json", RevisionRecord)
    artifact.path.chmod(0o600)
    artifact.path.write_bytes(b"{" + b"x" * 256)
    with pytest.raises(DurableArtifactError, match="size limit"):
        store.read_model("record.json", RevisionRecord)


def test_atomic_read_detects_file_and_parent_identity_substitution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "race-root"
    store = AtomicJsonStore(root)
    artifact = store.write_model("nested/record.json", RevisionRecord(revision=0, value="a"))
    original_open = durability_module.os.open
    swapped = False

    def swap_file_open(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
        nonlocal swapped
        if path == "record.json" and kwargs.get("dir_fd") is not None and not swapped:
            swapped = True
            artifact.path.rename(artifact.path.with_suffix(".old"))
            descriptor = original_open(artifact.path, os.O_WRONLY | os.O_CREAT, 0o600)
            os.write(descriptor, RevisionRecord(revision=0, value="b").model_dump_json().encode())
            os.close(descriptor)
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(durability_module.os, "open", swap_file_open)
    with pytest.raises(DurableArtifactError, match="cannot be read safely"):
        store.read_model("nested/record.json", RevisionRecord)

    monkeypatch.setattr(durability_module.os, "open", original_open)
    parent = root / "nested"
    moved = root / "moved"
    parent_swapped = False

    def swap_parent_open(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
        nonlocal parent_swapped
        if Path(path) == parent and not parent_swapped:
            parent_swapped = True
            parent.rename(moved)
            parent.mkdir(mode=0o700)
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(durability_module.os, "open", swap_parent_open)
    with pytest.raises(DurableArtifactError, match="parent identity is unsafe"):
        store.read_model("nested/record.json", RevisionRecord)


def test_atomic_store_rejects_symlink_components_and_unsafe_root_mode(
    tmp_path: Path,
) -> None:
    actual = tmp_path / "actual"
    store = AtomicJsonStore(actual)
    store.write_model("record.json", RevisionRecord(revision=0, value="ok"))
    alias = tmp_path / "alias"
    alias.symlink_to(actual, target_is_directory=True)
    with pytest.raises(DurableArtifactError, match="symlink"):
        AtomicJsonStore(alias).read_model("record.json", RevisionRecord)

    actual.chmod(0o755)
    with pytest.raises(DurableArtifactError, match="owner-only"):
        store.write_model("other.json", RevisionRecord(revision=0, value="no"))


def _write_bundle_fixture(
    layout: FridayChatMaintenanceLayout,
) -> tuple[MaintenanceArtifactStore, RecoveryBundleManifest]:
    run_id = "1" * 32
    participant_fingerprint = "2" * 64
    memory = MemorySnapshotManifest(
        run_id=run_id,
        created_at=NOW,
        layout_fingerprint=participant_fingerprint,
        vector_source=str(layout.vector_directory),
        graph_source=str(layout.graph_path),
        access_buffer_wal_source=str(layout.access_buffer_wal_path),
        vector=VectorSnapshotManifest(
            state=StoreDiscoveryState.PRESENT,
            strategy=MemorySnapshotStrategy.CHROMA_LOGICAL_EXPORT_REBUILD,
            artifact_filename="vector.json",
            artifact_sha256="3" * 64,
            artifact_size_bytes=1,
            maximum_float32_ulp_drift=2,
            collections=[],
        ),
        graph=GraphSnapshotManifest(
            state=StoreDiscoveryState.PRESENT,
            artifact_filename="graph.json",
            artifact_sha256="4" * 64,
            artifact_size_bytes=1,
            node_count=0,
            edge_count=0,
        ),
        access_buffer=AccessBufferSnapshotManifest(
            state=StoreDiscoveryState.PRESENT,
            strategy=AccessBufferRecoveryStrategy.DRAINED_INTO_VECTOR,
            wal_configured=True,
            buffered_item_count=0,
            wal_size_bytes=0,
        ),
        verified=True,
    )
    transcript = TranscriptSnapshotManifest(
        created_at=NOW,
        source_path=str(layout.transcript_database_path),
        artifact_filename="transcript.sqlite3",
        artifact_sha256="5" * 64,
        artifact_size_bytes=1,
        schema_fingerprint="schema-v1",
        page_count=1,
        verified=True,
    )
    store = MaintenanceArtifactStore(layout)
    atomic = AtomicJsonStore(layout.recovery_root)
    memory_path = store.participant_manifest_path(run_id, ParticipantKind.MEMORY)
    transcript_path = store.participant_manifest_path(
        run_id, ParticipantKind.TRANSCRIPT
    )
    memory_artifact = atomic.write_model(
        memory_path.relative_to(layout.recovery_root), memory
    )
    transcript_artifact = atomic.write_model(
        transcript_path.relative_to(layout.recovery_root), transcript
    )
    bundle = RecoveryBundleManifest(
        bundle_id="6" * 32,
        run_id=run_id,
        created_at=NOW,
        completed_at=NOW + timedelta(seconds=1),
        verification_completed_at=NOW + timedelta(seconds=2),
        layout_fingerprint=layout.layout_fingerprint,
        application_id="friday-chat",
        application_version="0.1.0",
        participant_manifests=(
            ParticipantManifestReference(
                participant=ParticipantKind.MEMORY,
                manifest_path=memory_path,
                manifest_sha256=memory_artifact.sha256,
                participant_layout_fingerprint=participant_fingerprint,
            ),
            ParticipantManifestReference(
                participant=ParticipantKind.TRANSCRIPT,
                manifest_path=transcript_path,
                manifest_sha256=transcript_artifact.sha256,
            ),
        ),
        memory=memory,
        transcript=transcript,
    )
    return store, bundle


def test_bundle_binds_exact_participant_files_checksums_and_live_sources(
    tmp_path: Path,
) -> None:
    layout = _make_layout(tmp_path, "bundle")
    store, bundle = _write_bundle_fixture(layout)
    artifact = store.write_bundle(bundle)
    loaded, _ = store.read_bundle(artifact.path, expected_sha256=artifact.sha256)
    assert loaded == bundle

    bad_reference = bundle.participant_manifests[0].model_copy(
        update={"manifest_sha256": "f" * 64}
    )
    with pytest.raises(DurableArtifactError, match="checksum"):
        store._verify_bundle_participants(
            bundle.model_copy(
                update={
                    "participant_manifests": (
                        bad_reference,
                        bundle.participant_manifests[1],
                    )
                }
            )
        )
    wrong_source = bundle.memory.model_copy(
        update={"vector_source": str(tmp_path / "wrong-vector")}
    )
    with pytest.raises(DurableArtifactError, match="sources"):
        store._validate_bundle_identity(bundle.model_copy(update={"memory": wrong_source}))


@DARWIN_ONLY
def test_lease_contention_disjoint_layouts_and_initial_journal_gate(
    tmp_path: Path,
) -> None:
    namespace = tmp_path / "registry"
    first = _make_layout(tmp_path, "lease-first")
    second = _make_layout(tmp_path, "lease-second")
    first_store, first_journal, first_checksum = _new_persisted_journal(first)
    _, second_journal, _ = _new_persisted_journal(second)
    registry = DarwinLayoutLeaseRegistry(namespace_root=namespace)
    first_handle = registry.acquire(first, first_journal)
    assert stat.S_IMODE(registry.namespace_root.stat().st_mode) == 0o700
    assert stat.S_IMODE(first_handle.path.stat().st_mode) == 0o600
    second_handle = registry.acquire(second, second_journal)

    with pytest.raises(LayoutLeaseContentionError):
        registry.acquire(first, first_journal)

    first_journal, first_checksum = _complete_pre_mutation(
        first_store, first_journal, first_checksum
    )
    first_handle.release()
    second_handle.release()
    historical = first_journal.model_copy()
    with pytest.raises(LayoutLeaseError, match="initial ordinary journal"):
        registry.acquire(first, historical)

    _, recovery_journal, _ = _new_persisted_journal(
        first,
        trigger=OperationTrigger.RECOVERY,
        mode=None,
        created_at=NOW + timedelta(seconds=1),
    )
    with pytest.raises(LayoutLeaseError, match="initial ordinary journal"):
        registry.acquire(first, recovery_journal)


@DARWIN_ONLY
def test_real_second_process_observes_active_contention(tmp_path: Path) -> None:
    layout = _make_layout(tmp_path, "process-contention")
    store, journal, checksum = _new_persisted_journal(layout)
    registry = DarwinLayoutLeaseRegistry(namespace_root=tmp_path / "registry")
    handle = registry.acquire(layout, journal)
    context = multiprocessing.get_context("spawn")
    result_queue = context.Queue()
    process = context.Process(
        target=_attempt_process_acquire,
        args=(
            layout.model_dump_json(),
            journal.model_dump_json(),
            str(registry.namespace_root),
            result_queue,
        ),
    )
    process.start()
    process.join(timeout=10)
    assert process.exitcode == 0
    assert result_queue.get(timeout=2) == "contended"
    _complete_pre_mutation(store, journal, checksum)
    handle.release()


@DARWIN_ONLY
def test_cross_lease_hardlink_alias_contends(tmp_path: Path) -> None:
    first = _make_layout(tmp_path, "hardlink-first")
    alias = tmp_path / "aliased-graph.json"
    os.link(first.graph_path, alias)
    second = _make_layout(tmp_path, "hardlink-second", graph=alias)
    _, first_journal, _ = _new_persisted_journal(first)
    _, second_journal, _ = _new_persisted_journal(second)
    registry = DarwinLayoutLeaseRegistry(namespace_root=tmp_path / "registry")
    first_handle = registry.acquire(first, first_journal)
    with pytest.raises(LayoutLeaseContentionError):
        registry.acquire(second, second_journal)
    first_handle.release()


@DARWIN_ONLY
def test_unfinished_release_blocks_cross_root_and_exact_recovery_resumes(
    tmp_path: Path,
) -> None:
    namespace = tmp_path / "registry"
    layout = _make_layout(tmp_path, "unfinished")
    store, journal, checksum = _new_persisted_journal(layout)
    registry = DarwinLayoutLeaseRegistry(namespace_root=namespace)
    handle = registry.acquire(layout, journal)
    journal, _ = _advance_to_recovery_required(store, journal, checksum)
    handle.release()

    overlap = _make_layout(
        tmp_path,
        "overlap",
        vector=layout.vector_directory,
        graph=layout.graph_path,
        access_wal=layout.access_buffer_wal_path,
        transcript=layout.transcript_database_path,
        recovery=tmp_path / "other-recovery",
        logs=tmp_path / "other-logs",
    )
    _, overlap_journal, _ = _new_persisted_journal(overlap)
    with pytest.raises(LayoutLeaseContentionError, match="retained recovery"):
        registry.acquire(overlap, overlap_journal)

    recovery_handle = registry.reconcile_stale(layout, journal)
    recovery_handle.release()


@DARWIN_ONLY
@pytest.mark.parametrize(
    "failure_phase",
    ["evidence_fsynced", "namespace_fsynced"],
)
def test_unfinished_release_fault_retries_and_preserves_recovery_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_phase: str,
) -> None:
    namespace = tmp_path / "registry"
    layout = _make_layout(tmp_path, f"unfinished-fault-{failure_phase}")
    _, journal, _ = _new_persisted_journal(layout)
    registry = DarwinLayoutLeaseRegistry(namespace_root=namespace)
    handle = registry.acquire(layout, journal)
    injected = False

    def fail_once(phase: str) -> None:
        nonlocal injected
        if phase == failure_phase and not injected:
            injected = True
            raise OSError("injected unfinished release durability failure")

    monkeypatch.setattr(
        registry,
        "_after_unfinished_release_durability",
        fail_once,
    )
    with pytest.raises(LayoutLeaseError, match="release failed closed"):
        handle.release()
    handle.release()

    unfinished_root = namespace / "evidence" / "unfinished"
    evidence = list(unfinished_root.glob("*.lease.json"))
    assert len(evidence) == 1
    assert not registry.lease_path(layout).exists()

    overlap = _make_layout(
        tmp_path,
        f"unfinished-overlap-{failure_phase}",
        vector=layout.vector_directory,
        graph=layout.graph_path,
        access_wal=layout.access_buffer_wal_path,
        transcript=layout.transcript_database_path,
        recovery=tmp_path / f"other-recovery-{failure_phase}",
        logs=tmp_path / f"other-logs-{failure_phase}",
    )
    _, overlap_journal, _ = _new_persisted_journal(overlap)
    with pytest.raises(LayoutLeaseContentionError, match="retained recovery"):
        registry.acquire(overlap, overlap_journal)

    recovery_handle = registry.reconcile_stale(layout, journal)
    recovery_handle.release()
    assert len(list(unfinished_root.glob("*.lease.json"))) == 1


@DARWIN_ONLY
def test_stale_rename_failure_blocks_overlap_and_exact_resume_succeeds(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    namespace = tmp_path / "registry"
    layout = _make_layout(tmp_path, "stale")
    _, journal, _ = _new_persisted_journal(layout)
    registry = DarwinLayoutLeaseRegistry(namespace_root=namespace)
    record = registry._new_record(layout, journal).model_copy(
        update={"process_id": 2_000_000_000}
    )
    with registry._registry_guard() as descriptor:
        held = registry._create_active_lease(
            descriptor,
            registry.lease_path(layout).name,
            record,
        )
        fcntl.flock(held, fcntl.LOCK_UN)
        os.close(held)

    def fail_after_evidence() -> None:
        raise OSError("injected crash boundary")

    monkeypatch.setattr(registry, "_after_evidence_rename", fail_after_evidence)
    with pytest.raises(StaleLeaseReconciliationError):
        registry.reconcile_stale(layout, journal)

    overlap = _make_layout(
        tmp_path,
        "stale-overlap",
        vector=layout.vector_directory,
        graph=layout.graph_path,
        access_wal=layout.access_buffer_wal_path,
        transcript=layout.transcript_database_path,
        recovery=tmp_path / "stale-other-recovery",
        logs=tmp_path / "stale-other-logs",
    )
    _, overlap_journal, _ = _new_persisted_journal(overlap)
    with pytest.raises(LayoutLeaseContentionError):
        registry.acquire(overlap, overlap_journal)

    resumed = registry.reconcile_stale(layout, journal)
    resumed.release()


@DARWIN_ONLY
def test_historical_terminal_evidence_does_not_ambiguous_current_recovery(
    tmp_path: Path,
) -> None:
    layout = _make_layout(tmp_path, "history")
    first_store, first_journal, first_checksum = _new_persisted_journal(layout)
    first_journal, _ = _complete_pre_mutation(
        first_store,
        first_journal,
        first_checksum,
    )
    registry = DarwinLayoutLeaseRegistry(namespace_root=tmp_path / "registry")
    old_record = registry._new_record(layout, first_journal).model_copy(
        update={"process_id": 2_000_000_000}
    )
    with registry._registry_guard() as descriptor:
        held = registry._create_active_lease(
            descriptor,
            registry.lease_path(layout).name,
            old_record,
        )
        fcntl.flock(held, fcntl.LOCK_UN)
        os.close(held)
    registry.retire_terminal_lease(layout, first_journal)

    second_store, second_journal, second_checksum = _new_persisted_journal(
        layout,
        created_at=NOW + timedelta(seconds=1),
    )
    second_handle = registry.acquire(layout, second_journal)
    second_journal, _ = _advance_to_recovery_required(
        second_store,
        second_journal,
        second_checksum,
    )
    second_handle.release()
    recovered = registry.reconcile_stale(layout, second_journal)
    recovered.release()


@DARWIN_ONLY
@pytest.mark.parametrize(
    "failure_phase",
    ["pending_created", "active_unlinked", "pending_unlinked"],
)
def test_terminal_release_fault_phases_are_explicitly_recoverable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_phase: str,
) -> None:
    layout = _make_layout(tmp_path, f"release-{failure_phase}")
    store, journal, checksum = _new_persisted_journal(layout)
    registry = DarwinLayoutLeaseRegistry(namespace_root=tmp_path / "registry")
    handle = registry.acquire(layout, journal)
    journal, _ = _complete_pre_mutation(store, journal, checksum)
    original_fsync = registry._fsync_release_directory

    def fail_phase(descriptor: int, phase: str) -> None:
        if phase == failure_phase:
            raise OSError("injected release fsync failure")
        original_fsync(descriptor, phase)

    monkeypatch.setattr(registry, "_fsync_release_directory", fail_phase)
    with pytest.raises(LayoutLeaseError, match="release failed closed"):
        handle.release()
    handle.release()
    evidence_root = registry.namespace_root / "evidence" / "stale"
    assert not list(evidence_root.glob("*.lease.json"))


@DARWIN_ONLY
@pytest.mark.parametrize(
    "failure_phase",
    ["pending_created", "active_unlinked", "pending_unlinked"],
)
def test_terminal_release_fault_phases_survive_owner_exit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_phase: str,
) -> None:
    layout = _make_layout(tmp_path, f"release-exit-{failure_phase}")
    store, journal, checksum = _new_persisted_journal(layout)
    registry = DarwinLayoutLeaseRegistry(namespace_root=tmp_path / "registry")
    handle = registry.acquire(layout, journal)
    journal, _ = _complete_pre_mutation(store, journal, checksum)
    original_fsync = registry._fsync_release_directory

    def fail_phase(descriptor: int, phase: str) -> None:
        if phase == failure_phase:
            raise OSError("injected release fsync failure")
        original_fsync(descriptor, phase)

    monkeypatch.setattr(registry, "_fsync_release_directory", fail_phase)
    with pytest.raises(LayoutLeaseError, match="release failed closed"):
        handle.release()
    _simulate_process_exit(handle)
    registry.retire_terminal_lease(layout, journal)


@DARWIN_ONLY
def test_partial_active_creation_cleanup_and_fail_closed_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    layout = _make_layout(tmp_path, "partial")
    _, journal, _ = _new_persisted_journal(layout)
    registry = DarwinLayoutLeaseRegistry(namespace_root=tmp_path / "registry")
    original_write = registry._write_all

    def fail_write(descriptor: int, payload: bytes) -> None:
        del descriptor, payload
        raise OSError("injected write failure")

    monkeypatch.setattr(registry, "_write_all", fail_write)
    descriptor_count = len(os.listdir("/dev/fd"))
    with pytest.raises(LayoutLeaseError):
        registry.acquire(layout, journal)
    assert not registry.lease_path(layout).exists()
    assert len(os.listdir("/dev/fd")) == descriptor_count

    def fail_cleanup(descriptor: int) -> None:
        del descriptor
        raise OSError("injected cleanup fsync failure")

    monkeypatch.setattr(registry, "_fsync_partial_cleanup", fail_cleanup)
    with pytest.raises(LayoutLeaseError, match="cleanup failed closed"):
        registry.acquire(layout, journal)
    assert registry.lease_path(layout).exists()
    monkeypatch.setattr(registry, "_write_all", original_write)
    with pytest.raises(LayoutLeaseError, match="metadata is invalid"):
        registry.acquire(layout, journal)


@DARWIN_ONLY
def test_registry_grammar_bounds_platform_refusal_and_stale_link_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    layout = _make_layout(tmp_path, "registry-safety")
    _, journal, _ = _new_persisted_journal(layout)
    unsupported_namespace = tmp_path / "unsupported-registry"
    unsupported = DarwinLayoutLeaseRegistry(
        namespace_root=unsupported_namespace,
        platform_name="Linux",
    )
    with pytest.raises(MaintenancePlatformError):
        unsupported.acquire(layout, journal)
    assert not unsupported_namespace.exists()

    namespace = tmp_path / "strict-registry"
    ensure_owner_directory(namespace)
    unexpected = namespace / "unexpected"
    unexpected.write_bytes(b"x")
    unexpected.chmod(0o600)
    registry = DarwinLayoutLeaseRegistry(namespace_root=namespace)
    with pytest.raises(LayoutLeaseError, match="unexpected state"):
        registry.acquire(layout, journal)
    unexpected.unlink()

    monkeypatch.setattr(
        os,
        "listdir",
        lambda descriptor: ["registry.lock"] * 1025,
    )
    with pytest.raises(LayoutLeaseError, match="too large"):
        registry._bounded_directory_names(0)
    monkeypatch.setattr(os, "listdir", lambda descriptor: ["x" * 256])
    with pytest.raises(LayoutLeaseError, match="filename is too long"):
        registry._bounded_directory_names(0)

    monkeypatch.undo()
    mismatch = registry._new_record(layout, journal).model_copy(
        update={"application_version": "wrong", "process_id": 2_000_000_000}
    )
    with registry._registry_guard() as descriptor:
        held = registry._create_active_lease(
            descriptor,
            registry.lease_path(layout).name,
            mismatch,
        )
        fcntl.flock(held, fcntl.LOCK_UN)
        os.close(held)
    with pytest.raises(
        StaleLeaseReconciliationError,
        match="journal linkage does not match",
    ):
        registry.reconcile_stale(layout, journal)
