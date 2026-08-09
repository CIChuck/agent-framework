"""Recovery tests for WAL-safe SQLite transcript snapshots."""

import asyncio
import json
import os
import sqlite3
from pathlib import Path

import pytest
from friday_transcript import (
    SQLiteTranscriptStore,
    TranscriptEntry,
    TranscriptRecoveryError,
    TranscriptRecoveryErrorCode,
    TranscriptRestoreQuiescenceToken,
    TranscriptSession,
    TranscriptSnapshotManifest,
    TranscriptSnapshotResult,
)
from friday_transcript.stores.sqlite import (
    TranscriptPathError,
    TranscriptQuiescenceError,
)
from pydantic import ValidationError


async def _populated_store(database_path: Path) -> SQLiteTranscriptStore:
    store = SQLiteTranscriptStore(database_path)
    assert await store.create_session(
        TranscriptSession(session_id="session-1", model_name="test-model")
    )
    assert await store.append_entry(
        TranscriptEntry(
            id="entry-1",
            session_id="session-1",
            turn_number=1,
            user_message="first",
            assistant_message="response",
        )
    )
    return store


@pytest.mark.asyncio
async def test_live_inspection_is_typed_and_read_only(tmp_path: Path) -> None:
    store = await _populated_store(tmp_path / "live" / "transcript.db")

    result = await store.inspect_live()

    assert result.verified
    assert result.manifest_path is None
    assert result.integrity is not None
    assert result.integrity.page_count > 0


@pytest.mark.asyncio
async def test_live_inspection_does_not_initialize_absent_database(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "missing.db"
    store = SQLiteTranscriptStore(database_path)

    result = await store.inspect_live()

    assert not result.verified
    assert result.errors[0].code is TranscriptRecoveryErrorCode.SOURCE_ABSENT
    assert not database_path.exists()


@pytest.mark.asyncio
async def test_online_snapshot_captures_committed_wal_state(tmp_path: Path) -> None:
    database_path = tmp_path / "live" / "transcript.db"
    store = await _populated_store(database_path)

    writer = sqlite3.connect(database_path)
    try:
        writer.execute("PRAGMA wal_autocheckpoint=0")
        writer.execute(
            "UPDATE sessions SET metadata = ? WHERE session_id = ?",
            (json.dumps({"committed_in_wal": True}), "session-1"),
        )
        writer.commit()
        wal_path = database_path.with_name(f"{database_path.name}-wal")
        assert wal_path.is_file()
        assert wal_path.stat().st_size > 0

        result = await store.create_snapshot(tmp_path / "recovery" / "snapshot-1")
    finally:
        writer.close()

    assert result.verified
    assert result.manifest_path is not None
    manifest = TranscriptSnapshotManifest.model_validate_json(
        result.manifest_path.read_text()
    )
    artifact = result.manifest_path.parent / manifest.artifact_filename
    with sqlite3.connect(artifact) as snapshot_db:
        row = snapshot_db.execute(
            "SELECT metadata FROM sessions WHERE session_id = ?", ("session-1",)
        ).fetchone()
    assert row is not None
    assert json.loads(row[0]) == {"committed_in_wal": True}


@pytest.mark.asyncio
async def test_snapshot_verify_detects_corruption_and_missing_artifact(
    tmp_path: Path,
) -> None:
    store = await _populated_store(tmp_path / "live" / "transcript.db")
    result = await store.create_snapshot(tmp_path / "recovery" / "snapshot-1")
    assert result.manifest_path is not None
    manifest = TranscriptSnapshotManifest.model_validate_json(
        result.manifest_path.read_text()
    )
    artifact = result.manifest_path.parent / manifest.artifact_filename

    incomplete_payload = manifest.model_dump(mode="json")
    incomplete_payload["verified"] = False
    result.manifest_path.write_text(json.dumps(incomplete_payload))
    incomplete = await store.verify_snapshot(result.manifest_path)
    assert not incomplete.verified
    assert incomplete.errors[0].code is TranscriptRecoveryErrorCode.SNAPSHOT_INCOMPLETE
    result.manifest_path.write_text(manifest.model_dump_json(indent=2))

    with artifact.open("r+b") as stream:
        stream.seek(0)
        stream.write(b"corrupt")
    corrupt = await store.verify_snapshot(result.manifest_path)
    assert not corrupt.verified
    assert corrupt.errors[0].code is TranscriptRecoveryErrorCode.CHECKSUM_MISMATCH

    artifact.unlink()
    missing = await store.verify_snapshot(result.manifest_path)
    assert not missing.verified
    assert missing.errors[0].code is TranscriptRecoveryErrorCode.SNAPSHOT_INCOMPLETE


@pytest.mark.asyncio
async def test_restore_requires_active_store_token_and_blocks_writers(
    tmp_path: Path,
) -> None:
    store = await _populated_store(tmp_path / "live" / "transcript.db")
    snapshot = await store.create_snapshot(tmp_path / "recovery" / "snapshot-1")
    assert snapshot.manifest_path is not None
    assert await store.append_entry(
        TranscriptEntry(
            id="entry-2",
            session_id="session-1",
            turn_number=2,
            user_message="later",
        )
    )
    if os.name == "posix":
        store.database_path.chmod(0o640)

    fabricated = TranscriptRestoreQuiescenceToken("other", "other", "other")
    with pytest.raises(TranscriptQuiescenceError):
        await store.restore_snapshot(snapshot.manifest_path, fabricated)

    async with store.restore_quiescence() as token:
        pending_write = asyncio.create_task(
            store.append_entry(
                TranscriptEntry(
                    id="entry-after-restore",
                    session_id="session-1",
                    turn_number=2,
                )
            )
        )
        await asyncio.sleep(0)
        assert not pending_write.done()
        restored = await store.restore_snapshot(snapshot.manifest_path, token)
        assert restored.verified
        assert await store.count_entries("session-1") == 1
        if os.name == "posix":
            assert store.database_path.stat().st_mode & 0o777 == 0o640

    assert await pending_write
    assert await store.count_entries("session-1") == 2

    with pytest.raises(TranscriptQuiescenceError):
        await store.restore_snapshot(snapshot.manifest_path, token)


@pytest.mark.asyncio
async def test_verify_live_rejects_schema_drift(tmp_path: Path) -> None:
    database_path = tmp_path / "live" / "transcript.db"
    store = await _populated_store(database_path)
    snapshot = await store.create_snapshot(tmp_path / "recovery" / "snapshot-1")
    assert snapshot.manifest_path is not None

    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE unexpected_schema (id TEXT PRIMARY KEY)")
        connection.commit()

    result = await store.verify_live(snapshot.manifest_path)
    assert not result.verified
    assert result.errors[0].code is TranscriptRecoveryErrorCode.SCHEMA_MISMATCH


@pytest.mark.asyncio
async def test_snapshot_rejects_overlap_and_symlink_alias(tmp_path: Path) -> None:
    database_path = tmp_path / "live" / "transcript.db"
    store = await _populated_store(database_path)

    with pytest.raises(TranscriptPathError):
        await store.create_snapshot(database_path.parent)

    alias = tmp_path / "live-alias"
    try:
        alias.symlink_to(database_path.parent, target_is_directory=True)
    except OSError:
        pytest.skip("Directory symlinks are not available")
    with pytest.raises(TranscriptPathError):
        await store.create_snapshot(alias)


@pytest.mark.asyncio
async def test_snapshot_artifacts_are_owner_only_on_posix(tmp_path: Path) -> None:
    if os.name != "posix":
        pytest.skip("POSIX mode assertion")
    store = await _populated_store(tmp_path / "live" / "transcript.db")
    destination = tmp_path / "recovery" / "snapshot-1"
    result = await store.create_snapshot(destination)
    assert result.manifest_path is not None
    manifest = TranscriptSnapshotManifest.model_validate_json(
        result.manifest_path.read_text()
    )

    assert destination.stat().st_mode & 0o777 == 0o700
    assert result.manifest_path.stat().st_mode & 0o777 == 0o600
    artifact = destination / manifest.artifact_filename
    assert artifact.stat().st_mode & 0o777 == 0o600


@pytest.mark.asyncio
async def test_snapshot_fsyncs_artifact_and_manifest_directory_entries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX durability assertion")
    store = await _populated_store(tmp_path / "live" / "transcript.db")
    calls: list[Path] = []
    original_fsync = SQLiteTranscriptStore._fsync_directory

    def recording_fsync(path: Path) -> None:
        calls.append(path)
        original_fsync(path)

    monkeypatch.setattr(
        SQLiteTranscriptStore,
        "_fsync_directory",
        staticmethod(recording_fsync),
    )
    destination = tmp_path / "recovery" / "snapshot-1"
    result = await store.create_snapshot(destination)
    assert result.verified
    assert calls.count(destination) >= 2


@pytest.mark.asyncio
async def test_verify_normalizes_artifact_permission_race(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = await _populated_store(tmp_path / "live" / "transcript.db")
    snapshot = await store.create_snapshot(tmp_path / "recovery" / "snapshot-1")
    assert snapshot.manifest_path is not None

    def inaccessible(_path: Path) -> str:
        raise PermissionError("synthetic permission race")

    monkeypatch.setattr(
        SQLiteTranscriptStore,
        "_sha256",
        staticmethod(inaccessible),
    )
    result = await store.verify_snapshot(snapshot.manifest_path)
    assert not result.verified
    assert result.errors[0].code is TranscriptRecoveryErrorCode.SNAPSHOT_INCOMPLETE


@pytest.mark.asyncio
async def test_verify_inspects_owner_only_staged_checksummed_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = await _populated_store(tmp_path / "live" / "transcript.db")
    snapshot = await store.create_snapshot(tmp_path / "recovery" / "snapshot-1")
    assert snapshot.manifest_path is not None
    manifest = TranscriptSnapshotManifest.model_validate_json(
        snapshot.manifest_path.read_text()
    )
    artifact = snapshot.manifest_path.parent / manifest.artifact_filename
    staged_paths: list[Path] = []
    staged_modes: list[tuple[int, int]] = []
    original_copy = SQLiteTranscriptStore._copy_owner_only

    def copy_then_swap(source: Path, destination: Path) -> None:
        original_copy(source, destination)
        staged_paths.append(destination)
        staged_modes.append(
            (
                destination.stat().st_mode & 0o777,
                destination.parent.stat().st_mode & 0o777,
            )
        )
        if source == artifact:
            source.write_bytes(b"changed after the staged copy")

    monkeypatch.setattr(
        SQLiteTranscriptStore,
        "_copy_owner_only",
        staticmethod(copy_then_swap),
    )
    result = await store.verify_snapshot(snapshot.manifest_path)
    assert result.verified
    assert staged_paths
    if os.name == "posix":
        assert staged_modes[0] == (0o600, 0o700)
    staged_parent = staged_paths[0].parent
    assert not staged_parent.exists()


@pytest.mark.asyncio
async def test_restore_rechecks_staged_checksum_before_live_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "live" / "transcript.db"
    store = await _populated_store(database_path)
    snapshot = await store.create_snapshot(tmp_path / "recovery" / "snapshot-1")
    assert snapshot.manifest_path is not None
    manifest = TranscriptSnapshotManifest.model_validate_json(
        snapshot.manifest_path.read_text()
    )
    artifact = snapshot.manifest_path.parent / manifest.artifact_filename
    assert await store.append_entry(
        TranscriptEntry(
            id="entry-2",
            session_id="session-1",
            turn_number=2,
        )
    )
    original_verify = store.verify_snapshot

    async def verify_then_swap(path: str | Path) -> TranscriptSnapshotResult:
        result = await original_verify(path)
        if result.verified:
            replacement = artifact.with_name("same-schema-replacement.sqlite3")
            replacement.write_bytes(artifact.read_bytes())
            with sqlite3.connect(replacement) as connection:
                connection.execute("PRAGMA journal_mode=DELETE")
                connection.execute(
                    "UPDATE sessions SET metadata = ? WHERE session_id = ?",
                    (json.dumps({"changed": True}), "session-1"),
                )
                connection.commit()
            os.replace(replacement, artifact)
        return result

    monkeypatch.setattr(store, "verify_snapshot", verify_then_swap)
    async with store.restore_quiescence() as token:
        with pytest.raises(
            TranscriptRecoveryError,
            match="checksum mismatch",
        ):
            await store.restore_snapshot(snapshot.manifest_path, token)
        assert await store.count_entries("session-1") == 2


@pytest.mark.asyncio
async def test_transcript_restore_revalidates_apply_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = await _populated_store(tmp_path / "live" / "transcript.db")
    snapshot = await store.create_snapshot(tmp_path / "recovery" / "snapshot-1")
    assert snapshot.manifest_path is not None
    manifest_path = snapshot.manifest_path
    assert await store.append_entry(
        TranscriptEntry(
            id="entry-2",
            session_id="session-1",
            turn_number=2,
        )
    )
    original_verify = store.verify_snapshot

    async def verify_then_change_manifest(
        path: str | Path,
    ) -> TranscriptSnapshotResult:
        result = await original_verify(path)
        if result.verified:
            payload = json.loads(manifest_path.read_text())
            payload["artifact_filename"] = "../outside.sqlite3"
            manifest_path.write_text(json.dumps(payload))
        return result

    monkeypatch.setattr(store, "verify_snapshot", verify_then_change_manifest)
    async with store.restore_quiescence() as token:
        with pytest.raises(TranscriptRecoveryError):
            await store.restore_snapshot(manifest_path, token)
        assert await store.count_entries("session-1") == 2


@pytest.mark.asyncio
async def test_transcript_verify_live_revalidates_apply_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = await _populated_store(tmp_path / "live" / "transcript.db")
    snapshot = await store.create_snapshot(tmp_path / "recovery" / "snapshot-1")
    assert snapshot.manifest_path is not None
    manifest_path = snapshot.manifest_path
    original_verify = store.verify_snapshot

    async def verify_then_change_manifest(
        path: str | Path,
    ) -> TranscriptSnapshotResult:
        result = await original_verify(path)
        if result.verified:
            payload = json.loads(manifest_path.read_text())
            payload["artifact_filename"] = "../outside.sqlite3"
            manifest_path.write_text(json.dumps(payload))
        return result

    monkeypatch.setattr(store, "verify_snapshot", verify_then_change_manifest)
    result = await store.verify_live(manifest_path)
    assert not result.verified
    assert result.errors[0].code is TranscriptRecoveryErrorCode.INVALID_PATH


def test_snapshot_manifest_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        TranscriptSnapshotManifest.model_validate(
            {
                "created_at": "2026-01-01T00:00:00",
                "source_path": "/tmp/transcript.db",
                "artifact_filename": "transcript.sqlite3",
                "artifact_sha256": "0" * 64,
                "artifact_size_bytes": 1,
                "schema_fingerprint": "1" * 64,
                "page_count": 1,
                "verified": True,
                "unexpected": "drift",
            }
        )
