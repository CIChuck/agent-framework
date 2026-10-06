"""Durable coordinator journal and aggregate recovery-bundle storage."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from friday_memory import MemorySnapshotManifest
from friday_transcript import TranscriptSnapshotManifest

from friday_chat.reorganization.contracts import (
    JournalSafeBoundary,
    JournalState,
    OperationTrigger,
    ParticipantKind,
    RecoveryBundleManifest,
    RecoveryJournal,
    ReorganizationMode,
)
from friday_chat.reorganization.durability import (
    AtomicJsonStore,
    DurableArtifact,
    DurableArtifactError,
)
from friday_chat.reorganization.layout import FridayChatMaintenanceLayout


class MaintenanceArtifactStore:
    """Persist retained run artifacts inside one resolved recovery root."""

    def __init__(self, layout: FridayChatMaintenanceLayout) -> None:
        self._layout = layout
        self._store = AtomicJsonStore(layout.recovery_root)

    @property
    def layout(self) -> FridayChatMaintenanceLayout:
        return self._layout

    def new_journal(
        self,
        *,
        application_id: str,
        application_version: str,
        trigger: OperationTrigger,
        requested_mode: ReorganizationMode | None,
        run_id: str | None = None,
        journal_id: str | None = None,
        lease_id: str | None = None,
        lease_nonce: str | None = None,
        created_at: datetime | None = None,
    ) -> RecoveryJournal:
        """Create, but do not persist, an initial journal bound to this layout."""
        effective_run_id = run_id or uuid4().hex
        timestamp = created_at or datetime.now(UTC)
        return RecoveryJournal(
            journal_id=journal_id or uuid4().hex,
            lease_id=lease_id or uuid4().hex,
            lease_nonce=lease_nonce or uuid4().hex,
            run_id=effective_run_id,
            application_id=application_id,
            application_version=application_version,
            layout_fingerprint=self._layout.layout_fingerprint,
            trigger=trigger,
            requested_mode=requested_mode,
            safe_boundary=JournalSafeBoundary.LIVE_UNMODIFIED,
            recovery_root=self._layout.recovery_root,
            journal_path=self.journal_path(effective_run_id),
            created_at=timestamp,
            updated_at=timestamp,
            revision=0,
            state=JournalState.CREATED,
        )

    def journal_path(self, run_id: str) -> Path:
        return self._layout.recovery_root / run_id / "journal.json"

    def bundle_path(self, run_id: str) -> Path:
        return self._layout.recovery_root / run_id / "bundle" / "manifest.json"

    def participant_manifest_path(
        self,
        run_id: str,
        participant: ParticipantKind,
    ) -> Path:
        return self._layout.recovery_root / run_id / participant.value / "manifest.json"

    def write_initial_journal(self, journal: RecoveryJournal) -> DurableArtifact:
        """Create revision zero without overwriting any existing run journal."""
        self._validate_journal_identity(journal)
        if journal.revision != 0 or journal.state is not JournalState.CREATED:
            raise DurableArtifactError("initial journal is not at revision zero")
        return self._store.write_model(
            self._relative(journal.journal_path),
            journal,
            require_absent=True,
        )

    def write_journal_transition(
        self,
        previous: RecoveryJournal,
        current: RecoveryJournal,
        *,
        expected_current_sha256: str,
    ) -> DurableArtifact:
        """CAS-persist one validated, append-only journal transition."""
        self._validate_journal_identity(previous)
        self._validate_journal_identity(current)
        immutable_fields = (
            "journal_id",
            "lease_id",
            "lease_nonce",
            "run_id",
            "application_id",
            "application_version",
            "layout_fingerprint",
            "trigger",
            "requested_mode",
            "recovery_root",
            "journal_path",
            "created_at",
        )
        if any(
            getattr(previous, field) != getattr(current, field)
            for field in immutable_fields
        ):
            raise DurableArtifactError("journal immutable identity changed")
        if current.state_history[:-1] != previous.state_history:
            raise DurableArtifactError("journal transition history is not append-only")
        return self._store.write_model(
            self._relative(current.journal_path),
            current,
            expected_current_sha256=expected_current_sha256,
            expected_revision=previous.revision,
        )

    def read_journal(
        self,
        journal_path: Path,
        *,
        expected_sha256: str | None = None,
    ) -> tuple[RecoveryJournal, DurableArtifact]:
        """Read one exact confined journal and validate its layout identity."""
        journal, artifact = self._store.read_model(
            self._relative(journal_path),
            RecoveryJournal,
            expected_sha256=expected_sha256,
        )
        self._validate_journal_identity(journal)
        if journal.journal_path != journal_path:
            raise DurableArtifactError("journal path binding does not match")
        return journal, artifact

    def write_bundle(self, bundle: RecoveryBundleManifest) -> DurableArtifact:
        """Verify exact participant files before persisting the aggregate bundle."""
        self._validate_bundle_identity(bundle)
        self._verify_bundle_participants(bundle)
        return self._store.write_model(
            self._relative(self.bundle_path(bundle.run_id)),
            bundle,
            require_absent=True,
        )

    def read_bundle(
        self,
        bundle_path: Path,
        *,
        expected_sha256: str,
    ) -> tuple[RecoveryBundleManifest, DurableArtifact]:
        """Read and reverify a checksum-bound aggregate bundle."""
        bundle, artifact = self._store.read_model(
            self._relative(bundle_path),
            RecoveryBundleManifest,
            expected_sha256=expected_sha256,
        )
        self._validate_bundle_identity(bundle)
        if bundle_path != self.bundle_path(bundle.run_id):
            raise DurableArtifactError("bundle path binding does not match")
        self._verify_bundle_participants(bundle)
        return bundle, artifact

    def _verify_bundle_participants(self, bundle: RecoveryBundleManifest) -> None:
        references = {
            reference.participant: reference
            for reference in bundle.participant_manifests
        }
        memory_reference = references[ParticipantKind.MEMORY]
        transcript_reference = references[ParticipantKind.TRANSCRIPT]
        expected_memory_path = self.participant_manifest_path(
            bundle.run_id,
            ParticipantKind.MEMORY,
        )
        expected_transcript_path = self.participant_manifest_path(
            bundle.run_id,
            ParticipantKind.TRANSCRIPT,
        )
        if (
            memory_reference.manifest_path != expected_memory_path
            or transcript_reference.manifest_path != expected_transcript_path
        ):
            raise DurableArtifactError("bundle participant path binding does not match")
        parsed_memory, _ = self._store.read_model(
            self._relative(expected_memory_path),
            MemorySnapshotManifest,
            expected_sha256=memory_reference.manifest_sha256,
        )
        parsed_transcript, _ = self._store.read_model(
            self._relative(expected_transcript_path),
            TranscriptSnapshotManifest,
            expected_sha256=transcript_reference.manifest_sha256,
        )
        if parsed_memory != bundle.memory or parsed_transcript != bundle.transcript:
            raise DurableArtifactError(
                "bundle embedded participant payload does not match exact manifest"
            )

    def _validate_journal_identity(self, journal: RecoveryJournal) -> None:
        if (
            journal.layout_fingerprint != self._layout.layout_fingerprint
            or journal.recovery_root != self._layout.recovery_root
            or journal.journal_path != self.journal_path(journal.run_id)
        ):
            raise DurableArtifactError("journal does not match maintenance layout")

    def _validate_bundle_identity(self, bundle: RecoveryBundleManifest) -> None:
        if bundle.layout_fingerprint != self._layout.layout_fingerprint:
            raise DurableArtifactError("bundle does not match maintenance layout")
        if (
            Path(bundle.memory.vector_source) != self._layout.vector_directory
            or Path(bundle.memory.graph_source) != self._layout.graph_path
            or (
                Path(bundle.memory.access_buffer_wal_source)
                if bundle.memory.access_buffer_wal_source is not None
                else None
            )
            != self._layout.access_buffer_wal_path
            or Path(bundle.transcript.source_path)
            != self._layout.transcript_database_path
        ):
            raise DurableArtifactError(
                "bundle participant sources do not match maintenance layout"
            )

    def _relative(self, path: Path) -> Path:
        try:
            return path.relative_to(self._layout.recovery_root)
        except ValueError as exc:
            raise DurableArtifactError("artifact path is outside recovery root") from exc
