"""Versioned typed cross-package contracts for memory reorganization."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal

from friday_memory import MemorySnapshotManifest
from friday_transcript import TranscriptSnapshotManifest
from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictContractModel(BaseModel):
    """Reject unknown fields in persisted and externally validated contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class OperationTrigger(str, Enum):
    """Origin of a reorganization request."""

    MANUAL = "manual"
    SHUTDOWN = "shutdown"
    RECOVERY = "recovery"


class ReorganizationMode(str, Enum):
    """Advertised reorganization modes."""

    FULL = "full"
    BACKUP = "backup"
    ANALYZE = "analyze"
    DEDUPE = "dedupe"
    PRUNE = "prune"
    SYNTHESIZE = "synthesize"
    VERIFY = "verify"


class StoreCapabilityState(str, Enum):
    """Aggregate discovery and capability state."""

    PRESENT = "present"
    NOT_CONFIGURED = "not_configured"
    CONFIGURED_ABSENT = "configured_absent"
    UNSUPPORTED = "unsupported"
    INCOMPLETE = "incomplete"
    CORRUPT = "corrupt"


class StoreOperationStatus(str, Enum):
    """Snapshot, restore, or integrity outcome for one store."""

    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


class ProgressStep(str, Enum):
    """Bounded framework-neutral coordinator progress steps."""

    QUIESCING = "quiescing"
    PREFLIGHT = "preflight"
    SNAPSHOTTING = "snapshotting"
    VERIFYING_SNAPSHOT = "verifying_snapshot"
    MUTATING = "mutating"
    VERIFYING_LIVE = "verifying_live"
    ROLLING_BACK = "rolling_back"
    RECOVERING = "recovering"
    COMPLETE = "complete"


class MutationStep(str, Enum):
    """Closed graph/vector and lifecycle maintenance operation steps."""

    ANALYZE = "analyze"
    REEMBED = "reembed"
    DEDUPE = "dedupe"
    PRUNE = "prune"
    SYNTHESIZE = "synthesize"
    VERIFY = "verify"
    LIFECYCLE = "lifecycle"


class MutationStepStatus(str, Enum):
    """Honest terminal state for one previewed or executed operation."""

    PREVIEWED = "previewed"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


class ResultStatus(str, Enum):
    """Terminal reorganization result states."""

    DRY_RUN_COMPLETE = "dry_run_complete"
    COMPLETED = "completed"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"
    PREFLIGHT_FAILED = "preflight_failed"
    FAILED = "failed"
    FAILED_ROLLED_BACK = "failed_rolled_back"
    CANCELLED = "cancelled"
    RECOVERY_REQUIRED = "recovery_required"


class ReorganizationErrorCode(str, Enum):
    """Stable coordinator error categories."""

    INVALID_REQUEST = "invalid_request"
    CAPABILITY_UNAVAILABLE = "capability_unavailable"
    PREFLIGHT_FAILED = "preflight_failed"
    SNAPSHOT_FAILED = "snapshot_failed"
    MUTATION_FAILED = "mutation_failed"
    RESTORE_FAILED = "restore_failed"
    INTEGRITY_FAILED = "integrity_failed"
    CANCELLED = "cancelled"
    RECOVERY_REQUIRED = "recovery_required"


class JournalState(str, Enum):
    """Durable recovery journal states."""

    CREATED = "created"
    SNAPSHOT_IN_PROGRESS = "snapshot_in_progress"
    SNAPSHOT_VERIFIED = "snapshot_verified"
    MUTATION_IN_PROGRESS = "mutation_in_progress"
    ROLLBACK_IN_PROGRESS = "rollback_in_progress"
    RECOVERY_REQUIRED = "recovery_required"
    RECOVERY_IN_PROGRESS = "recovery_in_progress"
    COMPLETE = "complete"


class JournalSafeBoundary(str, Enum):
    """Last durable boundary known safe for the live stores."""

    LIVE_UNMODIFIED = "live_unmodified"
    SNAPSHOT_VERIFIED_LIVE_UNMODIFIED = "snapshot_verified_live_unmodified"
    MUTATION_UNCERTAIN = "mutation_uncertain"
    RECOVERY_REQUIRED = "recovery_required"
    LIVE_VERIFIED = "live_verified"


class LiveTargetKind(str, Enum):
    """Live mutation targets protected by the layout lease registry."""

    VECTOR = "vector"
    GRAPH = "graph"
    ACCESS_WAL = "access_wal"
    TRANSCRIPT = "transcript"


class ParticipantKind(str, Enum):
    """Package-owned manifests bound into an aggregate recovery bundle."""

    MEMORY = "memory"
    TRANSCRIPT = "transcript"


LEGAL_JOURNAL_TRANSITIONS: dict[JournalState, frozenset[JournalState]] = {
    JournalState.CREATED: frozenset(
        {JournalState.SNAPSHOT_IN_PROGRESS, JournalState.COMPLETE}
    ),
    JournalState.SNAPSHOT_IN_PROGRESS: frozenset(
        {JournalState.SNAPSHOT_VERIFIED, JournalState.COMPLETE}
    ),
    JournalState.SNAPSHOT_VERIFIED: frozenset(
        {JournalState.MUTATION_IN_PROGRESS, JournalState.COMPLETE}
    ),
    JournalState.MUTATION_IN_PROGRESS: frozenset(
        {
            JournalState.ROLLBACK_IN_PROGRESS,
            JournalState.COMPLETE,
        }
    ),
    JournalState.ROLLBACK_IN_PROGRESS: frozenset(
        {JournalState.RECOVERY_REQUIRED, JournalState.COMPLETE}
    ),
    JournalState.RECOVERY_REQUIRED: frozenset({JournalState.RECOVERY_IN_PROGRESS}),
    JournalState.RECOVERY_IN_PROGRESS: frozenset(
        {JournalState.RECOVERY_REQUIRED, JournalState.COMPLETE}
    ),
    JournalState.COMPLETE: frozenset(),
}


class ReorganizationError(StrictContractModel):
    """Typed, content-safe coordinator error."""

    code: ReorganizationErrorCode
    message: str
    store: str | None = None


class ReorganizationRequest(StrictContractModel):
    """Ordinary dry-run or execute request, distinct from recovery."""

    trigger: OperationTrigger
    mode: ReorganizationMode
    execute: bool = False
    skip_synthesis: bool = False
    skip_verify: bool = False
    skip_lifecycle: bool = False
    force_reembed: bool = False

    @model_validator(mode="after")
    def reject_meaningless_analyze_execution(self) -> "ReorganizationRequest":
        """Analyze has no mutating execute form."""
        if self.mode is ReorganizationMode.ANALYZE and self.execute:
            raise ValueError("analyze mode does not support execute")
        if self.mode is not ReorganizationMode.FULL and any(
            (
                self.skip_synthesis,
                self.skip_verify,
                self.skip_lifecycle,
                self.force_reembed,
            )
        ):
            raise ValueError("single-step modes do not accept full-only flags")
        return self


class RecoveryRequest(StrictContractModel):
    """Explicit recovery request; never inferred from an ordinary request."""

    trigger: Literal[OperationTrigger.RECOVERY] = OperationTrigger.RECOVERY
    run_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    execute: bool = False


class ReorganizationLogRecord(StrictContractModel):
    """Content-free durable audit envelope for one execute-capable run."""

    schema_version: Literal[1] = 1
    run_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    created_at: datetime
    trigger: OperationTrigger
    mode: ReorganizationMode
    layout_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    journal_path: Path
    content_policy: Literal["categorical_only"] = "categorical_only"

    @model_validator(mode="after")
    def validate_log_identity(self) -> "ReorganizationLogRecord":
        if not self.journal_path.is_absolute():
            raise ValueError("reorganization log journal path must be absolute")
        if self.journal_path.name != "journal.json":
            raise ValueError("reorganization log must reference a journal")
        if self.journal_path.parent.name != self.run_id:
            raise ValueError("reorganization log run identity does not match journal")
        return self


class StoreOperationResult(StrictContractModel):
    """Typed aggregate result for one persistent participant."""

    store: str
    capability_state: StoreCapabilityState
    status: StoreOperationStatus
    verified: bool
    item_count: int | None = Field(default=None, ge=0)
    errors: list[ReorganizationError] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_store_outcome(self) -> "StoreOperationResult":
        if self.status is StoreOperationStatus.COMPLETED:
            if not self.verified or self.errors:
                raise ValueError(
                    "completed store result requires verified error-free evidence"
                )
        elif self.status is StoreOperationStatus.FAILED:
            if self.verified or not self.errors:
                raise ValueError(
                    "failed store result requires unverified typed errors"
                )
        elif self.verified or self.errors:
            raise ValueError("skipped store result cannot be verified or contain errors")
        return self


class MutationStepResult(StrictContractModel):
    """Content-safe evidence retained for one selected maintenance step."""

    step: MutationStep
    status: MutationStepStatus
    scanned_count: int | None = Field(default=None, ge=0)
    candidate_count: int | None = Field(default=None, ge=0)
    changed_count: int | None = Field(default=None, ge=0)
    warnings: tuple[str, ...] = ()
    errors: tuple[ReorganizationError, ...] = ()

    @model_validator(mode="after")
    def validate_step_outcome(self) -> "MutationStepResult":
        if self.status is MutationStepStatus.FAILED and not self.errors:
            raise ValueError("failed mutation step requires typed errors")
        if self.status is not MutationStepStatus.FAILED and self.errors:
            raise ValueError("non-failed mutation step cannot contain errors")
        if (
            self.status is MutationStepStatus.PREVIEWED
            and self.changed_count is not None
        ):
            raise ValueError("previewed mutation step cannot report changes")
        if self.status is MutationStepStatus.SKIPPED and self.changed_count not in {
            None,
            0,
        }:
            raise ValueError("skipped mutation step cannot report changes")
        return self


class ParticipantManifestReference(StrictContractModel):
    """Exact path and digest for one package-owned participant manifest."""

    participant: ParticipantKind
    manifest_path: Path
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    participant_layout_fingerprint: str | None = Field(
        default=None,
        pattern=r"^[0-9a-f]{64}$",
    )
    complete: Literal[True] = True
    verified: Literal[True] = True


class RecoveryBundleManifest(StrictContractModel):
    """Versioned aggregate of package-owned recovery manifests."""

    schema_version: Literal[1] = 1
    bundle_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    run_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    created_at: datetime
    completed_at: datetime
    verification_completed_at: datetime
    layout_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    application_id: str = Field(pattern=r"^[A-Za-z0-9_.-]+$")
    application_version: str = Field(min_length=1)
    participant_manifests: tuple[ParticipantManifestReference, ...]
    memory: MemorySnapshotManifest
    transcript: TranscriptSnapshotManifest
    complete: Literal[True] = True
    verified: Literal[True] = True

    @model_validator(mode="after")
    def validate_complete_bundle_evidence(self) -> "RecoveryBundleManifest":
        """Bind exact verified participant manifests to this run and layout."""
        participants = {
            reference.participant for reference in self.participant_manifests
        }
        if participants != {ParticipantKind.MEMORY, ParticipantKind.TRANSCRIPT}:
            raise ValueError("bundle must bind exactly memory and transcript manifests")
        if len(self.participant_manifests) != 2:
            raise ValueError("bundle participant manifest references must be unique")
        if any(
            not reference.manifest_path.is_absolute()
            for reference in self.participant_manifests
        ):
            raise ValueError("bundle participant manifest paths must be absolute")
        if self.memory.run_id != self.run_id:
            raise ValueError("memory manifest run identity does not match bundle")
        if not self.memory.verified or not self.transcript.verified:
            raise ValueError("bundle participants must be verified")
        references = {
            reference.participant: reference for reference in self.participant_manifests
        }
        if (
            references[ParticipantKind.MEMORY].participant_layout_fingerprint
            != self.memory.layout_fingerprint
        ):
            raise ValueError("memory participant layout identity does not match")
        if (
            references[ParticipantKind.TRANSCRIPT].participant_layout_fingerprint
            is not None
        ):
            raise ValueError(
                "transcript participant does not expose a layout fingerprint"
            )
        if not (self.created_at <= self.completed_at <= self.verification_completed_at):
            raise ValueError("bundle completion evidence is not monotonic")
        return self


class RecoveryJournal(StrictContractModel):
    """Versioned durable coordinator journal contract."""

    schema_version: Literal[1] = 1
    journal_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    lease_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    lease_nonce: str = Field(pattern=r"^[0-9a-f]{32}$")
    run_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    application_id: str = Field(pattern=r"^[A-Za-z0-9_.-]+$")
    application_version: str = Field(min_length=1)
    layout_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    trigger: OperationTrigger
    requested_mode: ReorganizationMode | None
    safe_boundary: JournalSafeBoundary
    recovery_root: Path
    journal_path: Path
    created_at: datetime
    updated_at: datetime
    revision: int = Field(ge=0)
    state: JournalState
    state_history: tuple[JournalState, ...] = (JournalState.CREATED,)
    bundle_manifest_path: Path | None = None
    bundle_manifest_sha256: str | None = Field(
        default=None,
        pattern=r"^[0-9a-f]{64}$",
    )
    completed_steps: tuple[ProgressStep, ...] = ()
    terminal_status: ResultStatus | None = None
    errors: tuple[ReorganizationError, ...] = ()

    @model_validator(mode="after")
    def validate_durable_transition_history(self) -> "RecoveryJournal":
        """Reject skipped, regressed, or incompletely bound journal states."""
        if not self.recovery_root.is_absolute() or not self.journal_path.is_absolute():
            raise ValueError("journal paths must be absolute")
        try:
            self.journal_path.relative_to(self.recovery_root)
        except ValueError as exc:
            raise ValueError("journal path must be confined to recovery root") from exc
        expected_path = self.recovery_root / self.run_id / "journal.json"
        if self.journal_path != expected_path:
            raise ValueError("journal path does not match its run identity")
        if not self.state_history or self.state_history[0] is not JournalState.CREATED:
            raise ValueError("journal history must begin at created")
        if self.state_history[-1] is not self.state:
            raise ValueError("journal state must match the final history entry")
        if self.revision != len(self.state_history) - 1:
            raise ValueError("journal revision must match transition history")
        for previous, current in zip(
            self.state_history,
            self.state_history[1:],
            strict=False,
        ):
            if current not in LEGAL_JOURNAL_TRANSITIONS[previous]:
                raise ValueError("journal transition is not legal or monotonic")
        bundle_fields = (
            self.bundle_manifest_path,
            self.bundle_manifest_sha256,
        )
        if (bundle_fields[0] is None) != (bundle_fields[1] is None):
            raise ValueError("journal bundle path and checksum must be bound together")
        crossed_snapshot_boundary = JournalState.SNAPSHOT_VERIFIED in self.state_history
        crossed_mutation_boundary = (
            JournalState.MUTATION_IN_PROGRESS in self.state_history
        )
        if crossed_snapshot_boundary and bundle_fields[0] is None:
            raise ValueError("journal must bind a verified bundle at snapshot boundary")
        if not crossed_snapshot_boundary and bundle_fields[0] is not None:
            raise ValueError("pre-snapshot journal cannot bind a recovery bundle")
        if self.bundle_manifest_path is not None:
            if not self.bundle_manifest_path.is_absolute():
                raise ValueError("journal bundle path must be absolute")
            try:
                self.bundle_manifest_path.relative_to(self.recovery_root)
            except ValueError as exc:
                raise ValueError(
                    "journal bundle path must be confined to recovery root"
                ) from exc
        if self.updated_at < self.created_at:
            raise ValueError("journal timestamps must be monotonic")
        if len(self.completed_steps) != len(set(self.completed_steps)):
            raise ValueError("journal completed steps cannot contain duplicates")
        if self.trigger is OperationTrigger.RECOVERY:
            if self.requested_mode is not None:
                raise ValueError("recovery journal cannot bind an ordinary mode")
        elif self.requested_mode is None:
            raise ValueError("ordinary journal must bind its requested mode")
        unsafe_states = {
            JournalState.MUTATION_IN_PROGRESS,
            JournalState.ROLLBACK_IN_PROGRESS,
        }
        if (
            self.state in unsafe_states
            and self.safe_boundary is not JournalSafeBoundary.MUTATION_UNCERTAIN
        ):
            raise ValueError("mutating journal must record an uncertain live boundary")
        if (
            self.state
            in {
                JournalState.RECOVERY_REQUIRED,
                JournalState.RECOVERY_IN_PROGRESS,
            }
            and self.safe_boundary is not JournalSafeBoundary.RECOVERY_REQUIRED
        ):
            raise ValueError("recovery journal must record recovery-required boundary")
        if (
            self.state is JournalState.SNAPSHOT_VERIFIED
            and self.safe_boundary
            is not JournalSafeBoundary.SNAPSHOT_VERIFIED_LIVE_UNMODIFIED
        ):
            raise ValueError(
                "verified snapshot must retain an unmodified live boundary"
            )
        if (
            not crossed_snapshot_boundary
            and self.safe_boundary is not JournalSafeBoundary.LIVE_UNMODIFIED
        ):
            raise ValueError(
                "pre-snapshot journal must retain an unmodified live boundary"
            )
        if self.state is JournalState.COMPLETE and crossed_mutation_boundary:
            if self.safe_boundary is not JournalSafeBoundary.LIVE_VERIFIED:
                raise ValueError(
                    "complete mutated journal must identify a verified live boundary"
                )
        elif self.state is JournalState.COMPLETE and crossed_snapshot_boundary:
            allowed_boundaries = {
                JournalSafeBoundary.SNAPSHOT_VERIFIED_LIVE_UNMODIFIED,
                JournalSafeBoundary.LIVE_VERIFIED,
            }
            if self.safe_boundary not in allowed_boundaries:
                raise ValueError(
                    "complete journal must identify its verified safe boundary"
                )
        if self.state is JournalState.COMPLETE and self.terminal_status is None:
            raise ValueError("complete journal requires a terminal status")
        if self.state is not JournalState.COMPLETE and self.terminal_status is not None:
            raise ValueError("unfinished journal cannot have a terminal status")
        return self

    def transition(
        self,
        state: JournalState,
        *,
        updated_at: datetime,
        safe_boundary: JournalSafeBoundary,
        bundle_manifest_path: Path | None = None,
        bundle_manifest_sha256: str | None = None,
        completed_steps: tuple[ProgressStep, ...] | None = None,
        terminal_status: ResultStatus | None = None,
        errors: tuple[ReorganizationError, ...] | None = None,
    ) -> "RecoveryJournal":
        """Return a validated next journal state without mutating this record."""
        if updated_at <= self.updated_at:
            raise ValueError("journal transition timestamp must increase")
        next_completed_steps = (
            completed_steps if completed_steps is not None else self.completed_steps
        )
        if next_completed_steps[: len(self.completed_steps)] != self.completed_steps:
            raise ValueError("journal completed steps must be append-only")
        if len(next_completed_steps) != len(set(next_completed_steps)):
            raise ValueError("journal completed steps cannot contain duplicates")
        next_errors = errors if errors is not None else self.errors
        if next_errors[: len(self.errors)] != self.errors:
            raise ValueError("journal errors must be append-only")
        data = self.model_dump(mode="python")
        data.update(
            {
                "updated_at": updated_at,
                "revision": self.revision + 1,
                "state": state,
                "state_history": (*self.state_history, state),
                "safe_boundary": safe_boundary,
                "bundle_manifest_path": (
                    bundle_manifest_path
                    if bundle_manifest_path is not None
                    else self.bundle_manifest_path
                ),
                "bundle_manifest_sha256": (
                    bundle_manifest_sha256
                    if bundle_manifest_sha256 is not None
                    else self.bundle_manifest_sha256
                ),
                "completed_steps": next_completed_steps,
                "terminal_status": terminal_status,
                "errors": next_errors,
            }
        )
        return RecoveryJournal.model_validate(data)


class LeaseTarget(StrictContractModel):
    """One canonical live target included in overlap detection."""

    kind: LiveTargetKind
    path: Path


class LayoutLeaseRecord(StrictContractModel):
    """Durable owner and journal identity for one active maintenance layout."""

    schema_version: Literal[1] = 1
    lease_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    ownership_nonce: str = Field(pattern=r"^[0-9a-f]{32}$")
    journal_lease_nonce: str = Field(pattern=r"^[0-9a-f]{32}$")
    run_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    process_id: int = Field(gt=0)
    user_id: int = Field(ge=0)
    host_id: str = Field(min_length=1)
    application_id: str = Field(pattern=r"^[A-Za-z0-9_.-]+$")
    application_version: str = Field(min_length=1)
    layout_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    live_targets: tuple[LeaseTarget, ...]
    recovery_root: Path
    log_root: Path
    journal_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    journal_path: Path
    created_at: datetime

    @model_validator(mode="after")
    def validate_lease_bindings(self) -> "LayoutLeaseRecord":
        """Keep active lease metadata complete and path identities canonical."""
        if len(self.live_targets) not in {3, 4}:
            raise ValueError("lease must bind every configured live target")
        kinds = [target.kind for target in self.live_targets]
        required = {
            LiveTargetKind.VECTOR,
            LiveTargetKind.GRAPH,
            LiveTargetKind.TRANSCRIPT,
        }
        if not required.issubset(kinds) or len(kinds) != len(set(kinds)):
            raise ValueError("lease live target kinds are incomplete or duplicated")
        paths = [target.path for target in self.live_targets]
        expected_targets = tuple(
            sorted(
                self.live_targets,
                key=lambda target: (target.kind.value, str(target.path)),
            )
        )
        if self.live_targets != expected_targets or len(paths) != len(set(paths)):
            raise ValueError("lease live targets must be unique and deterministic")
        if any(not path.is_absolute() for path in paths):
            raise ValueError("lease live target paths must be absolute")
        if any(
            not path.is_absolute()
            for path in (self.recovery_root, self.log_root, self.journal_path)
        ):
            raise ValueError("lease recovery, log, and journal paths must be absolute")
        try:
            self.journal_path.relative_to(self.recovery_root)
        except ValueError as exc:
            raise ValueError("lease journal path must be confined") from exc
        return self


class ReorganizationResult(StrictContractModel):
    """Honest typed terminal result for ordinary and recovery operations."""

    status: ResultStatus
    trigger: OperationTrigger
    mode: ReorganizationMode | None = None
    run_id: str | None = None
    attempted_steps: list[ProgressStep] = Field(default_factory=list)
    completed_steps: list[ProgressStep] = Field(default_factory=list)
    skipped_steps: list[ProgressStep] = Field(default_factory=list)
    stores: list[StoreOperationResult] = Field(default_factory=list)
    mutation_steps: list[MutationStepResult] = Field(default_factory=list)
    recovery_manifest_path: Path | None = None
    journal_path: Path | None = None
    reorganization_log_path: Path | None = None
    warnings: list[str] = Field(default_factory=list)
    errors: list[ReorganizationError] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_terminal_outcome(self) -> "ReorganizationResult":
        success_statuses = {
            ResultStatus.DRY_RUN_COMPLETE,
            ResultStatus.COMPLETED,
            ResultStatus.COMPLETED_WITH_WARNINGS,
        }
        failed_store = any(
            store.status is StoreOperationStatus.FAILED or store.errors
            for store in self.stores
        )
        failed_step = any(
            step.status is MutationStepStatus.FAILED or step.errors
            for step in self.mutation_steps
        )
        if self.status in success_statuses and (
            self.errors or failed_store or failed_step
        ):
            raise ValueError("successful result cannot contain failure evidence")
        if self.status is ResultStatus.COMPLETED and self.warnings:
            raise ValueError("completed result with warnings requires warning status")
        if self.status is ResultStatus.COMPLETED_WITH_WARNINGS and not self.warnings:
            raise ValueError("warning status requires at least one warning")
        if (
            self.status
            in {
                ResultStatus.PREFLIGHT_FAILED,
                ResultStatus.FAILED,
                ResultStatus.FAILED_ROLLED_BACK,
                ResultStatus.RECOVERY_REQUIRED,
            }
            and not self.errors
        ):
            raise ValueError("failed result requires typed errors")
        if self.status is ResultStatus.CANCELLED and not any(
            error.code is ReorganizationErrorCode.CANCELLED for error in self.errors
        ):
            raise ValueError("cancelled result requires cancellation evidence")
        if len(self.attempted_steps) != len(set(self.attempted_steps)):
            raise ValueError("attempted progress steps cannot repeat")
        if len(self.completed_steps) != len(set(self.completed_steps)):
            raise ValueError("completed progress steps cannot repeat")
        if len(self.skipped_steps) != len(set(self.skipped_steps)):
            raise ValueError("skipped progress steps cannot repeat")
        completed = set(self.completed_steps)
        skipped = set(self.skipped_steps)
        attempted = set(self.attempted_steps)
        if completed & skipped or attempted & skipped:
            raise ValueError("skipped progress steps must be disjoint")
        if self.trigger is not OperationTrigger.RECOVERY and not completed.issubset(
            attempted
        ):
            raise ValueError("ordinary completed progress must have been attempted")
        if self.status is ResultStatus.DRY_RUN_COMPLETE:
            if any(
                path is not None
                for path in (
                    self.recovery_manifest_path,
                    self.journal_path,
                    self.reorganization_log_path,
                )
            ) or self.run_id is not None:
                raise ValueError("dry-run completion cannot contain execute artifacts")
            if any(
                step.status is MutationStepStatus.COMPLETED
                or step.changed_count not in {None, 0}
                for step in self.mutation_steps
            ):
                raise ValueError("dry-run completion cannot claim completed mutation")
        return self
