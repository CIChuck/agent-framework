"""Production coordination for Friday Chat reorganization and recovery."""

from __future__ import annotations

import asyncio
import re
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Protocol, TypeVar
from uuid import uuid4

from friday_memory import (
    MemoryOperationResult,
    MemoryRecoveryOperation,
    MemoryRecoveryParticipant,
    MemorySnapshotManifest,
    MemoryStoreKind,
    StoreDiscoveryState,
)
from friday_transcript import (
    TranscriptSnapshotManifest,
    TranscriptSnapshotParticipant,
    TranscriptSnapshotResult,
)
from pydantic import Field

from friday_chat.reorganization.artifacts import MaintenanceArtifactStore
from friday_chat.reorganization.contracts import (
    JournalSafeBoundary,
    JournalState,
    MutationStep,
    MutationStepResult,
    MutationStepStatus,
    OperationTrigger,
    ParticipantKind,
    ParticipantManifestReference,
    ProgressStep,
    RecoveryBundleManifest,
    RecoveryJournal,
    RecoveryRequest,
    ReorganizationError,
    ReorganizationErrorCode,
    ReorganizationLogRecord,
    ReorganizationMode,
    ReorganizationRequest,
    ReorganizationResult,
    ResultStatus,
    StoreCapabilityState,
    StoreOperationResult,
    StoreOperationStatus,
    StrictContractModel,
)
from friday_chat.reorganization.durability import (
    AtomicJsonStore,
    DurableArtifactError,
)
from friday_chat.reorganization.gate import MaintenanceAdmissionGate
from friday_chat.reorganization.layout import FridayChatMaintenanceLayout
from friday_chat.reorganization.lease import (
    DarwinLayoutLeaseRegistry,
    LayoutLeaseError,
    LayoutLeaseHandle,
)
from friday_chat.reorganization.preflight import MaintenanceEnvironmentPreflight


class CoordinatorFaultPoint(str, Enum):
    """Deterministic safe-boundary fault points for coordinator tests."""

    AFTER_JOURNAL = "after_journal"
    AFTER_LEASE = "after_lease"
    AFTER_PREFLIGHT = "after_preflight"
    AFTER_SNAPSHOT = "after_snapshot"
    AFTER_BUNDLE_VERIFIED = "after_bundle_verified"
    BEFORE_MUTATION_STEP = "before_mutation_step"
    AFTER_MUTATION_STEP = "after_mutation_step"
    BEFORE_LIVE_VERIFICATION = "before_live_verification"
    BEFORE_ROLLBACK = "before_rollback"
    AFTER_ROLLBACK = "after_rollback"


class MutationPreflight(StrictContractModel):
    """Provider and operation capability evidence before mutation."""

    supported: bool
    planned_steps: tuple[MutationStep, ...]
    warnings: tuple[str, ...] = ()
    errors: tuple[ReorganizationError, ...] = ()


class MutationVerification(StrictContractModel):
    """Postcondition evidence for the selected mutation pipeline."""

    verified: bool
    vector_collection_count: int | None = Field(default=None, ge=0)
    vector_record_count: int | None = Field(default=None, ge=0)
    graph_node_count: int | None = Field(default=None, ge=0)
    graph_edge_count: int | None = Field(default=None, ge=0)
    warnings: tuple[str, ...] = ()
    errors: tuple[ReorganizationError, ...] = ()


@dataclass(frozen=True)
class ReorganizationExecutionCapability:
    """Operation-specific structural authorization for Chat execute paths."""

    memory_participant: bool
    transcript_participant: bool
    runtime_hooks: bool
    mutation_adapter: bool

    @property
    def mutation_available(self) -> bool:
        """Return whether coordinated reorganization mutation is assembled."""
        return not self.mutation_missing_components

    @property
    def recovery_available(self) -> bool:
        """Return whether explicit restore/terminalization is assembled."""
        return not self.recovery_missing_components

    @property
    def mutation_missing_components(self) -> tuple[str, ...]:
        """Name missing ordinary-mutation dependencies without provider I/O."""
        components = (
            ("Friday Memory recovery participant", self.memory_participant),
            ("Friday Transcript recovery participant", self.transcript_participant),
            ("runtime quiescence hooks", self.runtime_hooks),
            ("maintenance mutation adapter", self.mutation_adapter),
        )
        return tuple(name for name, configured in components if not configured)

    @property
    def recovery_missing_components(self) -> tuple[str, ...]:
        """Name missing recovery dependencies without requiring mutation."""
        components = (
            ("Friday Memory recovery participant", self.memory_participant),
            ("Friday Transcript recovery participant", self.transcript_participant),
            ("runtime quiescence hooks", self.runtime_hooks),
        )
        return tuple(name for name, configured in components if not configured)

    @property
    def mutation_reason(self) -> str:
        """Return content-safe ordinary-mutation capability evidence."""
        if self.mutation_available:
            return "coordinator ordinary execute dependencies are assembled"
        return "coordinator ordinary execute dependencies are missing: " + ", ".join(
            self.mutation_missing_components
        )

    @property
    def recovery_reason(self) -> str:
        """Return content-safe recovery capability evidence."""
        if self.recovery_available:
            return "coordinator recovery execute dependencies are assembled"
        return "coordinator recovery execute dependencies are missing: " + ", ".join(
            self.recovery_missing_components
        )

    def available_for(
        self,
        request: ReorganizationRequest | RecoveryRequest,
    ) -> bool:
        """Authorize from the actual typed request and its required structure."""
        if isinstance(request, RecoveryRequest):
            return self.recovery_available
        if request.mode is ReorganizationMode.BACKUP:
            return self.recovery_available
        return self.mutation_available

    def reason_for(
        self,
        request: ReorganizationRequest | RecoveryRequest,
    ) -> str:
        """Explain the structural decision for one typed request."""
        if isinstance(request, RecoveryRequest):
            return self.recovery_reason
        if request.mode is ReorganizationMode.BACKUP:
            return self.recovery_reason
        return self.mutation_reason


@dataclass(frozen=True)
class ManualMaintenanceDrainResult:
    """Content-safe evidence from quiescing the interactive runtime."""

    buffered_extraction_count: int = 0
    extraction_preempted: bool = False

    def __post_init__(self) -> None:
        if self.buffered_extraction_count < 0:
            raise ValueError("buffered extraction count cannot be negative")

    @property
    def warnings(self) -> tuple[str, ...]:
        """Render bounded warnings without exposing pending turn content."""
        if self.buffered_extraction_count == 0:
            return ()
        label = "turn" if self.buffered_extraction_count == 1 else "turns"
        if self.extraction_preempted:
            return (
                "Running extraction was preempted safely; "
                f"{self.buffered_extraction_count} unfinished {label} were preserved "
                "for post-maintenance resumption",
            )
        verb = "is" if self.buffered_extraction_count == 1 else "are"
        return (
            f"{self.buffered_extraction_count} extraction {label} {verb} buffered for "
            "the next configured trigger; no extraction task was running",
        )


@dataclass(frozen=True)
class ManualMaintenanceResumeResult:
    """Content-safe evidence from post-maintenance extraction resumption."""

    required: bool = False
    scheduled: bool = False
    pending_count: int = 0
    error_type: str | None = None

    def __post_init__(self) -> None:
        if self.pending_count < 0:
            raise ValueError("pending extraction count cannot be negative")
        if self.scheduled and not self.required:
            raise ValueError("unrequired extraction resumption cannot be scheduled")
        if self.scheduled and self.error_type is not None:
            raise ValueError("scheduled extraction resumption cannot contain an error")

    @property
    def warnings(self) -> tuple[str, ...]:
        if self.error_type is not None:
            return (
                "Post-maintenance extraction resumption failed "
                f"({self.error_type}); preserved turns remain queued",
            )
        if not self.required or self.scheduled or self.pending_count == 0:
            return ()
        label = "turn" if self.pending_count == 1 else "turns"
        verb = "remains" if self.pending_count == 1 else "remain"
        return (
            f"{self.pending_count} preempted extraction {label} {verb} preserved, "
            "but post-maintenance resumption could not be scheduled",
        )


class MaintenanceMutationAdapter(Protocol):
    """Constructor-injected mutation boundary; never selected by a CLI flag."""

    def begin_run(self, request: ReorganizationRequest) -> None: ...

    def end_run(self, request: ReorganizationRequest) -> None: ...

    async def preview(
        self,
        request: ReorganizationRequest,
        planned_steps: tuple[MutationStep, ...],
    ) -> tuple[MutationStepResult, ...]: ...

    async def preflight(
        self,
        request: ReorganizationRequest,
        planned_steps: tuple[MutationStep, ...],
    ) -> MutationPreflight: ...

    async def execute_step(
        self,
        request: ReorganizationRequest,
        step: MutationStep,
    ) -> MutationStepResult: ...

    async def verify_postconditions(
        self,
        request: ReorganizationRequest,
    ) -> MutationVerification: ...


class MaintenanceRuntimeHooks(Protocol):
    """Runtime hooks for exclusive-intent preparation and maintenance."""

    async def prepare_for_manual_maintenance(self) -> None: ...

    async def drain_for_manual_maintenance(self) -> ManualMaintenanceDrainResult: ...

    def resume_after_manual_maintenance(self) -> ManualMaintenanceResumeResult: ...

    async def close_for_shutdown(self, *, snapshot_requested: bool) -> None: ...

    async def finalize_transcript(self) -> None: ...


class MaintenanceProgressCallback(Protocol):
    """Framework-neutral bounded progress callback."""

    async def __call__(self, step: ProgressStep, message: str) -> None: ...


FaultInjector = Callable[[CoordinatorFaultPoint, MutationStep | None], Awaitable[None]]


@dataclass
class _JournalCursor:
    journal: RecoveryJournal
    sha256: str


@dataclass(frozen=True)
class _SnapshotEvidence:
    bundle: RecoveryBundleManifest
    bundle_path: Path
    bundle_sha256: str
    memory_manifest_path: Path
    transcript_manifest_path: Path


_RUN_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")
_MAX_RUN_DIRECTORIES = 1024
_AtomicResultT = TypeVar("_AtomicResultT")


class ReorganizationCoordinator:
    """Single FridayChatApp-owned coordinator for maintenance and recovery."""

    def __init__(
        self,
        *,
        layout: FridayChatMaintenanceLayout,
        gate: MaintenanceAdmissionGate,
        memory_participant: MemoryRecoveryParticipant | None,
        transcript_participant: TranscriptSnapshotParticipant | None,
        runtime_hooks: MaintenanceRuntimeHooks | None,
        mutation_adapter: MaintenanceMutationAdapter | None = None,
        lease_registry: DarwinLayoutLeaseRegistry | None = None,
        application_id: str = "friday-chat",
        application_version: str = "0.1.0a4",
        fault_injector: FaultInjector | None = None,
        environment_preflight: MaintenanceEnvironmentPreflight | None = None,
    ) -> None:
        self.layout = layout
        self.gate = gate
        self._memory = memory_participant
        self._transcript = transcript_participant
        self._runtime_hooks = runtime_hooks
        self._mutation = mutation_adapter
        self._artifacts = MaintenanceArtifactStore(layout)
        self._json = AtomicJsonStore(layout.recovery_root)
        self._logs = AtomicJsonStore(layout.log_root)
        self._leases = lease_registry or DarwinLayoutLeaseRegistry()
        self._application_id = application_id
        self._application_version = application_version
        self._fault_injector = fault_injector
        self._environment = environment_preflight or MaintenanceEnvironmentPreflight()

    @property
    def execution_capability(self) -> ReorganizationExecutionCapability:
        """Return the structural authorization used by all execute entry points."""
        return ReorganizationExecutionCapability(
            memory_participant=self._memory is not None,
            transcript_participant=self._transcript is not None,
            runtime_hooks=self._runtime_hooks is not None,
            mutation_adapter=self._mutation is not None,
        )

    @property
    def execution_configured(self) -> bool:
        """Compatibility view of the typed structural execute capability."""
        return self.execution_capability.mutation_available

    @property
    def recovery_inspection_configured(self) -> bool:
        """Return whether package-owned recovery participants were assembled."""
        return self._memory is not None and self._transcript is not None

    async def run(
        self,
        request: ReorganizationRequest,
        *,
        progress: MaintenanceProgressCallback | None = None,
    ) -> ReorganizationResult:
        """Run one ordinary request through the shared production boundary."""
        if not request.execute:
            async with self.gate.shared("reorganization-dry-run"):
                return await self._dry_run(request, progress=progress)
        prepare = (
            self._runtime_hooks.prepare_for_manual_maintenance
            if self._runtime_hooks is not None
            else None
        )
        try:
            async with self.gate.exclusive(
                "reorganization-execute",
                prepare=prepare,
            ):
                result = await self._execute_locked(request, progress=progress)
        except BaseException:
            self._resume_manual_maintenance()
            raise
        return self._with_resume_evidence(
            result,
            self._resume_manual_maintenance(),
        )

    async def shutdown(
        self,
        request: ReorganizationRequest | None,
        *,
        progress: MaintenanceProgressCallback | None = None,
    ) -> ReorganizationResult | None:
        """Close admission, drain writers, finalize, then optionally snapshot."""
        hooks = self._require_runtime_hooks()
        await self.gate.close_shared_admission()
        async with self.gate.exclusive(
            "shutdown",
            prepare=hooks.prepare_for_manual_maintenance,
        ):
            shutdown_error: BaseException | None = None
            try:
                await hooks.close_for_shutdown(
                    snapshot_requested=(request is not None and request.execute)
                )
            except BaseException as exc:
                if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                    raise
                shutdown_error = exc
            try:
                await hooks.finalize_transcript()
            except BaseException as exc:
                if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                    raise
                if shutdown_error is None:
                    shutdown_error = exc
            if shutdown_error is not None:
                raise DurableArtifactError(
                    "shutdown quiescence or transcript finalization failed"
                ) from shutdown_error
            if request is None:
                return None
            if not request.execute:
                return await self._dry_run(request, progress=progress)
            return await self._execute_locked(
                request,
                progress=progress,
                state_already_drained=True,
            )

    async def recover(
        self,
        request: RecoveryRequest,
        *,
        progress: MaintenanceProgressCallback | None = None,
    ) -> ReorganizationResult:
        """Inspect or explicitly restore the exact bundle named by a journal."""
        if not request.execute:
            async with self.gate.shared("reorganization-recovery-inspection"):
                return self._inspect_recovery(request)
        prepare = (
            self._runtime_hooks.prepare_for_manual_maintenance
            if self._runtime_hooks is not None
            else None
        )
        try:
            async with self.gate.exclusive(
                "reorganization-recovery-execute",
                prepare=prepare,
            ):
                result = await self._recover_locked(request, progress=progress)
        except BaseException:
            self._resume_manual_maintenance()
            raise
        return self._with_resume_evidence(
            result,
            self._resume_manual_maintenance(),
        )

    def startup_recovery_warnings(self) -> tuple[str, ...]:
        """Read unfinished journals without creating or mutating any artifact."""
        journals = self._unfinished_journals()
        return tuple(
            f"reorganization recovery required for run {journal.run_id} "
            f"({journal.state.value})"
            for journal in journals
        )

    async def _dry_run(
        self,
        request: ReorganizationRequest,
        *,
        progress: MaintenanceProgressCallback | None,
    ) -> ReorganizationResult:
        attempted: list[ProgressStep] = []
        completed: list[ProgressStep] = []
        warnings: list[str] = []
        errors: list[ReorganizationError] = []
        mutation_steps = list(self._skipped_mutation_steps(request))
        await self._progress(
            ProgressStep.PREFLIGHT,
            "Inspecting reorganization capabilities",
            progress,
            attempted,
        )
        stores = await self._discover_store_results()
        try:
            unfinished = self._unfinished_journals()
        except DurableArtifactError as exc:
            errors.append(self._exception_error(exc, preflight=True))
        else:
            if unfinished:
                errors.append(
                    self._error(
                        ReorganizationErrorCode.PREFLIGHT_FAILED,
                        "unfinished reorganization journal blocks maintenance",
                    )
                )
        environment = self._environment.inspect(self.layout, self._leases)
        errors.extend(environment.errors)
        errors.extend(self._store_preflight_errors(stores))
        planned_steps = self._planned_steps(request)
        if planned_steps:
            if self._mutation is None:
                errors.append(
                    self._error(
                        ReorganizationErrorCode.CAPABILITY_UNAVAILABLE,
                        "maintenance mutation adapter is unavailable",
                    )
                )
            else:
                preflight = await self._mutation.preflight(request, planned_steps)
                warnings.extend(preflight.warnings)
                errors.extend(preflight.errors)
                if preflight.planned_steps != planned_steps:
                    errors.append(
                        self._error(
                            ReorganizationErrorCode.PREFLIGHT_FAILED,
                            "maintenance adapter changed the coordinator plan",
                        )
                    )
                if not preflight.supported and not preflight.errors:
                    errors.append(
                        self._error(
                            ReorganizationErrorCode.CAPABILITY_UNAVAILABLE,
                            "maintenance capabilities are unavailable",
                        )
                    )
                previews = await self._mutation.preview(request, planned_steps)
                if tuple(preview.step for preview in previews) != planned_steps:
                    errors.append(
                        self._error(
                            ReorganizationErrorCode.PREFLIGHT_FAILED,
                            "maintenance preview changed the coordinator plan",
                        )
                    )
                mutation_steps.extend(previews)
                for preview in previews:
                    warnings.extend(preview.warnings)
                    errors.extend(preview.errors)
        completed.append(ProgressStep.PREFLIGHT)
        await self._progress(
            ProgressStep.COMPLETE,
            "Dry-run inspection complete",
            progress,
            attempted,
        )
        completed.append(ProgressStep.COMPLETE)
        status = (
            ResultStatus.PREFLIGHT_FAILED if errors else ResultStatus.DRY_RUN_COMPLETE
        )
        return ReorganizationResult(
            status=status,
            trigger=request.trigger,
            mode=request.mode,
            attempted_steps=attempted,
            completed_steps=completed,
            stores=stores,
            mutation_steps=mutation_steps,
            warnings=warnings,
            errors=errors,
        )

    async def _execute_locked(
        self,
        request: ReorganizationRequest,
        *,
        progress: MaintenanceProgressCallback | None,
        state_already_drained: bool = False,
    ) -> ReorganizationResult:
        unfinished = self._unfinished_journals()
        if unfinished:
            retained = unfinished[0]
            return ReorganizationResult(
                status=ResultStatus.RECOVERY_REQUIRED,
                trigger=request.trigger,
                mode=request.mode,
                run_id=retained.run_id,
                recovery_manifest_path=retained.bundle_manifest_path,
                journal_path=retained.journal_path,
                reorganization_log_path=self._log_path(retained.run_id),
                errors=[
                    self._error(
                        ReorganizationErrorCode.RESTORE_FAILED,
                        "unfinished reorganization journal blocks mutation",
                    )
                ],
                warnings=[
                    "inspect the retained run with /reorganize --recover <run-id>"
                ],
            )

        journal = self._artifacts.new_journal(
            application_id=self._application_id,
            application_version=self._application_version,
            trigger=request.trigger,
            requested_mode=request.mode,
        )
        artifact = self._artifacts.write_initial_journal(journal)
        cursor = _JournalCursor(journal=journal, sha256=artifact.sha256)
        attempted: list[ProgressStep] = []
        completed: list[ProgressStep] = []
        warnings: list[str] = []
        errors: list[ReorganizationError] = []
        stores: list[StoreOperationResult] = []
        mutation_steps = list(self._skipped_mutation_steps(request))
        lease: LayoutLeaseHandle | None = None
        mutation_started = False
        mutation_run_started = False

        environment = self._environment.inspect(self.layout, self._leases)
        if environment.errors:
            errors.extend(environment.errors)
            self._complete_pre_mutation(
                cursor,
                status=ResultStatus.PREFLIGHT_FAILED,
                errors=errors,
                completed_steps=(),
            )
            return ReorganizationResult(
                status=ResultStatus.PREFLIGHT_FAILED,
                trigger=request.trigger,
                mode=request.mode,
                run_id=cursor.journal.run_id,
                journal_path=cursor.journal.journal_path,
                errors=errors,
            )
        try:
            self._write_initial_log(cursor.journal)
        except DurableArtifactError as exc:
            errors.append(self._exception_error(exc, preflight=True))
            self._complete_pre_mutation(
                cursor,
                status=ResultStatus.PREFLIGHT_FAILED,
                errors=errors,
                completed_steps=(),
            )
            return ReorganizationResult(
                status=ResultStatus.PREFLIGHT_FAILED,
                trigger=request.trigger,
                mode=request.mode,
                run_id=cursor.journal.run_id,
                journal_path=cursor.journal.journal_path,
                errors=errors,
            )

        try:
            await self._fault(CoordinatorFaultPoint.AFTER_JOURNAL)
            try:
                lease = self._leases.acquire(self.layout, cursor.journal)
            except LayoutLeaseError as exc:
                errors.append(self._exception_error(exc, preflight=True))
                self._complete_pre_mutation(
                    cursor,
                    status=ResultStatus.PREFLIGHT_FAILED,
                    errors=errors,
                    completed_steps=tuple(completed),
                )
                return self._result(
                    request,
                    cursor,
                    ResultStatus.PREFLIGHT_FAILED,
                    attempted,
                    completed,
                    stores,
                    mutation_steps,
                    warnings,
                    errors,
                )
            await self._fault(CoordinatorFaultPoint.AFTER_LEASE)

            await self._progress(
                ProgressStep.QUIESCING,
                "Draining conflicting writers",
                progress,
                attempted,
            )
            hooks = self._require_runtime_hooks()
            if not state_already_drained:
                drain_result = await hooks.drain_for_manual_maintenance()
                warnings.extend(drain_result.warnings)
            completed.append(ProgressStep.QUIESCING)

            await self._progress(
                ProgressStep.PREFLIGHT,
                "Validating stores and maintenance capabilities",
                progress,
                attempted,
            )
            stores = await self._discover_store_results()
            errors.extend(self._store_preflight_errors(stores))
            planned_steps = self._planned_steps(request)
            if planned_steps:
                self._require_mutation_adapter().begin_run(request)
                mutation_run_started = True
            preflight_errors, preflight_warnings = await self._preflight_mutation(
                request
            )
            errors.extend(preflight_errors)
            warnings.extend(preflight_warnings)
            if errors:
                completed.append(ProgressStep.PREFLIGHT)
                self._complete_pre_mutation(
                    cursor,
                    status=ResultStatus.PREFLIGHT_FAILED,
                    errors=errors,
                    completed_steps=tuple(completed),
                )
                return self._result(
                    request,
                    cursor,
                    ResultStatus.PREFLIGHT_FAILED,
                    attempted,
                    completed,
                    stores,
                    mutation_steps,
                    warnings,
                    errors,
                )
            completed.append(ProgressStep.PREFLIGHT)
            await self._fault(CoordinatorFaultPoint.AFTER_PREFLIGHT)

            cursor = self._transition(
                cursor,
                JournalState.SNAPSHOT_IN_PROGRESS,
                safe_boundary=JournalSafeBoundary.LIVE_UNMODIFIED,
                completed_steps=tuple(completed),
            )
            await self._progress(
                ProgressStep.SNAPSHOTTING,
                "Creating memory and transcript recovery snapshots",
                progress,
                attempted,
            )
            evidence = await self._atomic(
                self._create_verified_bundle(cursor.journal),
                cancellation_callback=self._cancellation_reporter(
                    progress,
                    ProgressStep.SNAPSHOTTING,
                ),
            )
            completed.append(ProgressStep.SNAPSHOTTING)
            await self._fault(CoordinatorFaultPoint.AFTER_SNAPSHOT)

            await self._progress(
                ProgressStep.VERIFYING_SNAPSHOT,
                "Verifying aggregate recovery evidence",
                progress,
                attempted,
            )
            completed.append(ProgressStep.VERIFYING_SNAPSHOT)
            cursor = self._transition(
                cursor,
                JournalState.SNAPSHOT_VERIFIED,
                safe_boundary=(JournalSafeBoundary.SNAPSHOT_VERIFIED_LIVE_UNMODIFIED),
                bundle_manifest_path=evidence.bundle_path,
                bundle_manifest_sha256=evidence.bundle_sha256,
                completed_steps=tuple(completed),
            )
            await self._fault(CoordinatorFaultPoint.AFTER_BUNDLE_VERIFIED)

            if request.mode is ReorganizationMode.BACKUP:
                await self._progress(
                    ProgressStep.COMPLETE,
                    "Reorganization backup completed",
                    progress,
                    attempted,
                )
                completed.append(ProgressStep.COMPLETE)
                cursor = self._transition(
                    cursor,
                    JournalState.COMPLETE,
                    safe_boundary=(
                        JournalSafeBoundary.SNAPSHOT_VERIFIED_LIVE_UNMODIFIED
                    ),
                    completed_steps=tuple(completed),
                    terminal_status=ResultStatus.COMPLETED,
                )
                return self._result(
                    request,
                    cursor,
                    ResultStatus.COMPLETED,
                    attempted,
                    completed,
                    stores,
                    mutation_steps,
                    warnings,
                    errors,
                )

            cursor = self._transition(
                cursor,
                JournalState.MUTATION_IN_PROGRESS,
                safe_boundary=JournalSafeBoundary.MUTATION_UNCERTAIN,
                completed_steps=tuple(completed),
            )
            mutation_started = True
            mutation = self._require_mutation_adapter()
            for step in self._planned_steps(request):
                await self._progress(
                    ProgressStep.MUTATING,
                    f"Applying maintenance step: {step.value}",
                    progress,
                    attempted,
                )
                await self._fault(
                    CoordinatorFaultPoint.BEFORE_MUTATION_STEP,
                    step,
                )
                step_result = await self._atomic(
                    mutation.execute_step(request, step),
                    cancellation_callback=self._cancellation_reporter(
                        progress,
                        ProgressStep.MUTATING,
                    ),
                )
                mutation_steps.append(step_result)
                warnings.extend(step_result.warnings)
                errors.extend(step_result.errors)
                if (
                    step_result.step is not step
                    or step_result.status is not MutationStepStatus.COMPLETED
                ):
                    if not step_result.errors:
                        errors.append(
                            self._error(
                                ReorganizationErrorCode.MUTATION_FAILED,
                                f"maintenance step {step.value} failed",
                            )
                        )
                    raise RuntimeError("maintenance mutation step failed")
                await self._fault(
                    CoordinatorFaultPoint.AFTER_MUTATION_STEP,
                    step,
                )
            completed.append(ProgressStep.MUTATING)

            await self._fault(CoordinatorFaultPoint.BEFORE_LIVE_VERIFICATION)
            await self._progress(
                ProgressStep.VERIFYING_LIVE,
                "Verifying live memory postconditions",
                progress,
                attempted,
            )
            verification = await self._atomic(
                mutation.verify_postconditions(request),
                cancellation_callback=self._cancellation_reporter(
                    progress,
                    ProgressStep.VERIFYING_LIVE,
                ),
            )
            warnings.extend(verification.warnings)
            errors.extend(verification.errors)
            if not verification.verified:
                if not verification.errors:
                    errors.append(
                        self._error(
                            ReorganizationErrorCode.INTEGRITY_FAILED,
                            "maintenance postcondition verification failed",
                        )
                    )
                raise RuntimeError("maintenance postconditions failed")
            await self._progress(
                ProgressStep.COMPLETE,
                "Reorganization completed with verified live state",
                progress,
                attempted,
            )
            completed.extend((ProgressStep.VERIFYING_LIVE, ProgressStep.COMPLETE))
            status = (
                ResultStatus.COMPLETED_WITH_WARNINGS
                if warnings
                else ResultStatus.COMPLETED
            )
            cursor = self._transition(
                cursor,
                JournalState.COMPLETE,
                safe_boundary=JournalSafeBoundary.LIVE_VERIFIED,
                completed_steps=tuple(completed),
                terminal_status=status,
                errors=tuple(errors),
            )
            return self._result(
                request,
                cursor,
                status,
                attempted,
                completed,
                stores,
                mutation_steps,
                warnings,
                errors,
            )
        except BaseException as exc:
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            error = self._exception_error(
                exc,
                cancelled=isinstance(exc, asyncio.CancelledError),
            )
            if error not in errors:
                errors.append(error)
            if mutation_started:
                return await self._rollback_after_failure(
                    request,
                    cursor,
                    attempted,
                    completed,
                    stores,
                    mutation_steps,
                    warnings,
                    errors,
                    progress=progress,
                )
            self._complete_pre_mutation(
                cursor,
                status=(
                    ResultStatus.CANCELLED
                    if isinstance(exc, asyncio.CancelledError)
                    else ResultStatus.FAILED
                ),
                errors=errors,
                completed_steps=tuple(completed),
            )
            return self._result(
                request,
                cursor,
                (
                    ResultStatus.CANCELLED
                    if isinstance(exc, asyncio.CancelledError)
                    else ResultStatus.FAILED
                ),
                attempted,
                completed,
                stores,
                mutation_steps,
                warnings,
                errors,
            )
        finally:
            if mutation_run_started and self._mutation is not None:
                self._mutation.end_run(request)
            if lease is not None:
                lease.release()

    async def _rollback_after_failure(
        self,
        request: ReorganizationRequest,
        cursor: _JournalCursor,
        attempted: list[ProgressStep],
        completed: list[ProgressStep],
        stores: list[StoreOperationResult],
        mutation_steps: list[MutationStepResult],
        warnings: list[str],
        errors: list[ReorganizationError],
        *,
        progress: MaintenanceProgressCallback | None,
    ) -> ReorganizationResult:
        """Always attempt exact-bundle rollback after mutation was crossed."""
        try:
            cursor = self._transition(
                cursor,
                JournalState.ROLLBACK_IN_PROGRESS,
                safe_boundary=JournalSafeBoundary.MUTATION_UNCERTAIN,
                errors=tuple(errors),
            )
        except BaseException as transition_exc:
            if isinstance(transition_exc, (KeyboardInterrupt, SystemExit)):
                raise
            errors.append(self._exception_error(transition_exc, restore=True))
        await self._rollback_progress_safely(
            progress=progress,
            attempted=attempted,
            errors=errors,
        )
        try:
            await self._fault(CoordinatorFaultPoint.BEFORE_ROLLBACK)
            evidence = self._read_bound_bundle(cursor.journal)
            await self._atomic(
                self._restore_and_verify(evidence),
                cancellation_callback=self._cancellation_reporter(
                    progress,
                    ProgressStep.ROLLING_BACK,
                ),
            )
            await self._fault(CoordinatorFaultPoint.AFTER_ROLLBACK)
            await self._progress(
                ProgressStep.COMPLETE,
                "Reorganization failed and verified rollback completed",
                progress,
                attempted,
            )
            completed.extend((ProgressStep.ROLLING_BACK, ProgressStep.COMPLETE))
            cursor = self._transition(
                cursor,
                JournalState.COMPLETE,
                safe_boundary=JournalSafeBoundary.LIVE_VERIFIED,
                completed_steps=tuple(completed),
                terminal_status=ResultStatus.FAILED_ROLLED_BACK,
                errors=tuple(errors),
            )
            return self._result(
                request,
                cursor,
                ResultStatus.FAILED_ROLLED_BACK,
                attempted,
                completed,
                stores,
                mutation_steps,
                warnings,
                errors,
            )
        except BaseException as rollback_exc:
            if isinstance(rollback_exc, (KeyboardInterrupt, SystemExit)):
                raise
            rollback_error = self._exception_error(
                rollback_exc,
                restore=True,
                cancelled=isinstance(rollback_exc, asyncio.CancelledError),
            )
            errors.append(rollback_error)
            if cursor.journal.state is JournalState.MUTATION_IN_PROGRESS:
                cursor = self._transition(
                    cursor,
                    JournalState.ROLLBACK_IN_PROGRESS,
                    safe_boundary=JournalSafeBoundary.MUTATION_UNCERTAIN,
                    errors=tuple(errors),
                )
            if cursor.journal.state is JournalState.ROLLBACK_IN_PROGRESS:
                cursor = self._transition(
                    cursor,
                    JournalState.RECOVERY_REQUIRED,
                    safe_boundary=JournalSafeBoundary.RECOVERY_REQUIRED,
                    errors=tuple(errors),
                )
            return self._result(
                request,
                cursor,
                ResultStatus.RECOVERY_REQUIRED,
                attempted,
                completed,
                stores,
                mutation_steps,
                warnings,
                errors,
            )

    def _inspect_recovery(self, request: RecoveryRequest) -> ReorganizationResult:
        try:
            journal, _ = self._artifacts.read_journal(
                self._artifacts.journal_path(request.run_id)
            )
            self._logs.read_model(
                f"{request.run_id}.json",
                ReorganizationLogRecord,
            )
            if journal.bundle_manifest_path is not None:
                self._read_bound_bundle(journal)
        except (DurableArtifactError, ValueError) as exc:
            return ReorganizationResult(
                status=ResultStatus.PREFLIGHT_FAILED,
                trigger=OperationTrigger.RECOVERY,
                run_id=request.run_id,
                errors=[self._exception_error(exc, preflight=True)],
            )
        if journal.state is JournalState.COMPLETE:
            terminal_status = journal.terminal_status or ResultStatus.COMPLETED
            retained_errors = list(journal.errors)
            warnings = ["the named reorganization run is already terminal"]
            if (
                terminal_status
                in {
                    ResultStatus.COMPLETED,
                    ResultStatus.COMPLETED_WITH_WARNINGS,
                }
                and retained_errors
            ):
                terminal_status = ResultStatus.COMPLETED_WITH_WARNINGS
                retained_errors = []
                warnings.append(
                    "prior run errors remain available in the retained journal"
                )
            return ReorganizationResult(
                status=terminal_status,
                trigger=OperationTrigger.RECOVERY,
                mode=journal.requested_mode,
                run_id=journal.run_id,
                completed_steps=list(journal.completed_steps),
                recovery_manifest_path=journal.bundle_manifest_path,
                journal_path=journal.journal_path,
                reorganization_log_path=self._log_path(journal.run_id),
                errors=retained_errors,
                warnings=warnings,
            )
        retained_errors = list(journal.errors)
        if not retained_errors:
            retained_errors.append(
                self._error(
                    ReorganizationErrorCode.RECOVERY_REQUIRED,
                    "unfinished durable journal requires explicit recovery",
                )
            )
        return ReorganizationResult(
            status=ResultStatus.RECOVERY_REQUIRED,
            trigger=OperationTrigger.RECOVERY,
            mode=journal.requested_mode,
            run_id=journal.run_id,
            completed_steps=list(journal.completed_steps),
            recovery_manifest_path=journal.bundle_manifest_path,
            journal_path=journal.journal_path,
            reorganization_log_path=self._log_path(journal.run_id),
            errors=retained_errors,
            warnings=[
                (
                    "the live stores are unmodified; execute recovery to "
                    "terminalize this run"
                    if not self._crossed_mutation(journal)
                    else "execute recovery to restore the exact retained bundle"
                )
            ],
        )

    async def _recover_locked(
        self,
        request: RecoveryRequest,
        *,
        progress: MaintenanceProgressCallback | None,
    ) -> ReorganizationResult:
        inspected = self._inspect_recovery(
            RecoveryRequest(run_id=request.run_id, execute=False)
        )
        if inspected.status is not ResultStatus.RECOVERY_REQUIRED:
            return inspected
        journal, artifact = self._artifacts.read_journal(
            self._artifacts.journal_path(request.run_id)
        )
        cursor = _JournalCursor(journal=journal, sha256=artifact.sha256)
        attempted: list[ProgressStep] = []
        completed = list(journal.completed_steps)
        errors = list(journal.errors)
        warnings: list[str] = []
        lease: LayoutLeaseHandle | None = None

        if not self._crossed_mutation(journal):
            if self._leases.lease_path(self.layout).exists():
                try:
                    lease = self._leases.reconcile_stale(self.layout, journal)
                except LayoutLeaseError as exc:
                    errors.append(self._exception_error(exc, restore=True))
                    return ReorganizationResult(
                        status=ResultStatus.RECOVERY_REQUIRED,
                        trigger=OperationTrigger.RECOVERY,
                        mode=journal.requested_mode,
                        run_id=journal.run_id,
                        completed_steps=completed,
                        recovery_manifest_path=journal.bundle_manifest_path,
                        journal_path=journal.journal_path,
                        reorganization_log_path=self._log_path(journal.run_id),
                        errors=errors,
                    )
            try:
                if ProgressStep.COMPLETE not in completed:
                    completed.append(ProgressStep.COMPLETE)
                cancellation_error = self._error(
                    ReorganizationErrorCode.CANCELLED,
                    "safe pre-mutation run was terminalized explicitly",
                )
                if cancellation_error not in errors:
                    errors.append(cancellation_error)
                cursor = self._transition(
                    cursor,
                    JournalState.COMPLETE,
                    safe_boundary=(
                        JournalSafeBoundary.SNAPSHOT_VERIFIED_LIVE_UNMODIFIED
                        if JournalState.SNAPSHOT_VERIFIED in journal.state_history
                        else JournalSafeBoundary.LIVE_UNMODIFIED
                    ),
                    completed_steps=tuple(completed),
                    terminal_status=ResultStatus.CANCELLED,
                    errors=tuple(errors),
                )
                return ReorganizationResult(
                    status=ResultStatus.CANCELLED,
                    trigger=OperationTrigger.RECOVERY,
                    mode=journal.requested_mode,
                    run_id=journal.run_id,
                    completed_steps=completed,
                    recovery_manifest_path=journal.bundle_manifest_path,
                    journal_path=journal.journal_path,
                    reorganization_log_path=self._log_path(journal.run_id),
                    errors=errors,
                    warnings=["safe pre-mutation run was terminalized explicitly"],
                )
            finally:
                if lease is not None:
                    lease.release()

        evidence = self._read_bound_bundle(journal)
        try:
            lease = self._leases.reconcile_stale(self.layout, journal)
            await self._progress(
                ProgressStep.QUIESCING,
                "Draining conflicting writers before recovery",
                progress,
                attempted,
            )
            drain_result = (
                await self._require_runtime_hooks().drain_for_manual_maintenance()
            )
            warnings.extend(drain_result.warnings)
            if ProgressStep.QUIESCING not in completed:
                completed.append(ProgressStep.QUIESCING)
            await self._progress(
                ProgressStep.RECOVERING,
                "Restoring the exact retained recovery bundle",
                progress,
                attempted,
            )
            cursor = self._advance_to_recovery_in_progress(cursor, errors)
            await self._atomic(
                self._restore_and_verify(evidence),
                cancellation_callback=self._cancellation_reporter(
                    progress,
                    ProgressStep.RECOVERING,
                ),
            )
            if ProgressStep.RECOVERING not in completed:
                completed.append(ProgressStep.RECOVERING)
            if ProgressStep.COMPLETE not in completed:
                completed.append(ProgressStep.COMPLETE)
            terminal_status = (
                ResultStatus.COMPLETED_WITH_WARNINGS
                if errors or warnings
                else ResultStatus.COMPLETED
            )
            cursor = self._transition(
                cursor,
                JournalState.COMPLETE,
                safe_boundary=JournalSafeBoundary.LIVE_VERIFIED,
                completed_steps=tuple(completed),
                terminal_status=terminal_status,
                errors=tuple(errors),
            )
            return ReorganizationResult(
                status=terminal_status,
                trigger=OperationTrigger.RECOVERY,
                mode=journal.requested_mode,
                run_id=journal.run_id,
                attempted_steps=attempted,
                completed_steps=completed,
                recovery_manifest_path=evidence.bundle_path,
                journal_path=journal.journal_path,
                reorganization_log_path=self._log_path(journal.run_id),
                warnings=(
                    ["prior run errors remain available in the retained journal"]
                    if errors
                    else []
                )
                + warnings,
            )
        except BaseException as exc:
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            errors.append(
                self._exception_error(
                    exc,
                    restore=True,
                    cancelled=isinstance(exc, asyncio.CancelledError),
                )
            )
            if cursor.journal.state is JournalState.RECOVERY_IN_PROGRESS:
                cursor = self._transition(
                    cursor,
                    JournalState.RECOVERY_REQUIRED,
                    safe_boundary=JournalSafeBoundary.RECOVERY_REQUIRED,
                    errors=tuple(errors),
                )
            return ReorganizationResult(
                status=ResultStatus.RECOVERY_REQUIRED,
                trigger=OperationTrigger.RECOVERY,
                mode=journal.requested_mode,
                run_id=journal.run_id,
                attempted_steps=attempted,
                completed_steps=completed,
                recovery_manifest_path=evidence.bundle_path,
                journal_path=journal.journal_path,
                reorganization_log_path=self._log_path(journal.run_id),
                errors=errors,
            )
        finally:
            if lease is not None:
                lease.release()

    async def _create_verified_bundle(
        self,
        journal: RecoveryJournal,
    ) -> _SnapshotEvidence:
        memory = self._require_memory_participant()
        transcript = self._require_transcript_participant()
        async with memory.maintenance_quiescence(
            MemoryRecoveryOperation.SNAPSHOT
        ) as token:
            memory_result = await memory.create_snapshot(journal.run_id, token)
        memory_manifest_path = self._verified_memory_path(memory_result)
        transcript_result = await transcript.create_snapshot(
            self.layout.recovery_root / journal.run_id / "transcript"
        )
        transcript_manifest_path = self._verified_transcript_path(transcript_result)

        memory_verification = await memory.verify_snapshot(memory_manifest_path)
        transcript_verification = await transcript.verify_snapshot(
            transcript_manifest_path
        )
        self._require_verified_memory(memory_verification)
        self._require_verified_transcript(transcript_verification)

        memory_manifest, memory_artifact = self._json.read_model(
            memory_manifest_path.relative_to(self.layout.recovery_root),
            MemorySnapshotManifest,
        )
        transcript_manifest, transcript_artifact = self._json.read_model(
            transcript_manifest_path.relative_to(self.layout.recovery_root),
            TranscriptSnapshotManifest,
        )
        created_at = datetime.now(UTC)
        completed_at = created_at + timedelta(microseconds=1)
        verification_completed_at = completed_at + timedelta(microseconds=1)
        bundle = RecoveryBundleManifest(
            bundle_id=uuid4().hex,
            run_id=journal.run_id,
            created_at=created_at,
            completed_at=completed_at,
            verification_completed_at=verification_completed_at,
            layout_fingerprint=self.layout.layout_fingerprint,
            application_id=self._application_id,
            application_version=self._application_version,
            participant_manifests=(
                ParticipantManifestReference(
                    participant=ParticipantKind.MEMORY,
                    manifest_path=memory_artifact.path,
                    manifest_sha256=memory_artifact.sha256,
                    participant_layout_fingerprint=(memory_manifest.layout_fingerprint),
                ),
                ParticipantManifestReference(
                    participant=ParticipantKind.TRANSCRIPT,
                    manifest_path=transcript_artifact.path,
                    manifest_sha256=transcript_artifact.sha256,
                ),
            ),
            memory=memory_manifest,
            transcript=transcript_manifest,
        )
        bundle_artifact = self._artifacts.write_bundle(bundle)
        verified_bundle, verified_artifact = self._artifacts.read_bundle(
            bundle_artifact.path,
            expected_sha256=bundle_artifact.sha256,
        )
        if verified_bundle != bundle:
            raise DurableArtifactError("aggregate recovery bundle changed after write")
        return _SnapshotEvidence(
            bundle=bundle,
            bundle_path=verified_artifact.path,
            bundle_sha256=verified_artifact.sha256,
            memory_manifest_path=memory_artifact.path,
            transcript_manifest_path=transcript_artifact.path,
        )

    def _read_bound_bundle(self, journal: RecoveryJournal) -> _SnapshotEvidence:
        if (
            journal.bundle_manifest_path is None
            or journal.bundle_manifest_sha256 is None
        ):
            raise DurableArtifactError("journal has no verified recovery bundle")
        bundle, artifact = self._artifacts.read_bundle(
            journal.bundle_manifest_path,
            expected_sha256=journal.bundle_manifest_sha256,
        )
        references = {
            reference.participant: reference
            for reference in bundle.participant_manifests
        }
        return _SnapshotEvidence(
            bundle=bundle,
            bundle_path=artifact.path,
            bundle_sha256=artifact.sha256,
            memory_manifest_path=references[ParticipantKind.MEMORY].manifest_path,
            transcript_manifest_path=(
                references[ParticipantKind.TRANSCRIPT].manifest_path
            ),
        )

    async def _restore_and_verify(self, evidence: _SnapshotEvidence) -> None:
        memory = self._require_memory_participant()
        transcript = self._require_transcript_participant()
        async with memory.maintenance_quiescence(
            MemoryRecoveryOperation.RESTORE
        ) as memory_token:
            memory_result = await memory.restore_snapshot(
                evidence.memory_manifest_path,
                memory_token,
            )
        self._require_verified_memory(memory_result)
        async with transcript.restore_quiescence() as transcript_token:
            transcript_result = await transcript.restore_snapshot(
                evidence.transcript_manifest_path,
                transcript_token,
            )
        self._require_verified_transcript(transcript_result)
        self._require_verified_memory(
            await memory.verify_live(evidence.memory_manifest_path)
        )
        self._require_verified_transcript(
            await transcript.verify_live(evidence.transcript_manifest_path)
        )

    async def _discover_store_results(self) -> list[StoreOperationResult]:
        results: list[StoreOperationResult] = []
        if self._memory is None:
            results.append(
                StoreOperationResult(
                    store="memory",
                    capability_state=StoreCapabilityState.NOT_CONFIGURED,
                    status=StoreOperationStatus.FAILED,
                    verified=False,
                    errors=[
                        self._error(
                            ReorganizationErrorCode.PREFLIGHT_FAILED,
                            "Friday Memory recovery participant is unavailable",
                            store="memory",
                        )
                    ],
                )
            )
        else:
            discovery = await self._memory.discover()
            state_mapping = {
                StoreDiscoveryState.PRESENT: StoreCapabilityState.PRESENT,
                StoreDiscoveryState.NOT_CONFIGURED: (
                    StoreCapabilityState.NOT_CONFIGURED
                ),
                StoreDiscoveryState.CONFIGURED_ABSENT: (
                    StoreCapabilityState.CONFIGURED_ABSENT
                ),
                StoreDiscoveryState.UNSUPPORTED: StoreCapabilityState.UNSUPPORTED,
                StoreDiscoveryState.INCOMPLETE: StoreCapabilityState.INCOMPLETE,
                StoreDiscoveryState.CORRUPT: StoreCapabilityState.CORRUPT,
            }
            for store in discovery.stores:
                supported = store.state in {
                    StoreDiscoveryState.PRESENT,
                    StoreDiscoveryState.NOT_CONFIGURED,
                } or (
                    store.store is MemoryStoreKind.GRAPH
                    and store.state is StoreDiscoveryState.CONFIGURED_ABSENT
                )
                results.append(
                    StoreOperationResult(
                        store=store.store.value,
                        capability_state=state_mapping[store.state],
                        status=(
                            StoreOperationStatus.COMPLETED
                            if supported
                            else StoreOperationStatus.FAILED
                        ),
                        verified=supported,
                        item_count=store.item_count,
                        errors=(
                            []
                            if supported
                            else [
                                self._error(
                                    ReorganizationErrorCode.PREFLIGHT_FAILED,
                                    "memory store discovery failed",
                                    store=store.store.value,
                                )
                            ]
                        ),
                    )
                )
        if self._transcript is None:
            results.append(
                StoreOperationResult(
                    store="transcript",
                    capability_state=StoreCapabilityState.NOT_CONFIGURED,
                    status=StoreOperationStatus.FAILED,
                    verified=False,
                    errors=[
                        self._error(
                            ReorganizationErrorCode.PREFLIGHT_FAILED,
                            "Friday Transcript recovery participant is unavailable",
                            store="transcript",
                        )
                    ],
                )
            )
        else:
            inspection = await self._transcript.inspect_live()
            results.append(
                StoreOperationResult(
                    store="transcript",
                    capability_state=(
                        StoreCapabilityState.PRESENT
                        if inspection.verified
                        else StoreCapabilityState.CORRUPT
                    ),
                    status=(
                        StoreOperationStatus.COMPLETED
                        if inspection.verified
                        else StoreOperationStatus.FAILED
                    ),
                    verified=inspection.verified,
                    item_count=(
                        inspection.integrity.page_count
                        if inspection.integrity is not None
                        else None
                    ),
                    errors=(
                        []
                        if inspection.verified
                        else [
                            self._error(
                                ReorganizationErrorCode.PREFLIGHT_FAILED,
                                "transcript live integrity inspection failed",
                                store="transcript",
                            )
                        ]
                    ),
                )
            )
        return results

    def _store_preflight_errors(
        self,
        stores: Sequence[StoreOperationResult],
    ) -> list[ReorganizationError]:
        errors: list[ReorganizationError] = []
        for store in stores:
            if store.status is not StoreOperationStatus.FAILED:
                continue
            if store.errors:
                errors.extend(store.errors)
            else:
                errors.append(
                    self._error(
                        ReorganizationErrorCode.PREFLIGHT_FAILED,
                        "persistent store discovery failed",
                        store=store.store,
                    )
                )
        return errors

    async def _preflight_mutation(
        self,
        request: ReorganizationRequest,
    ) -> tuple[list[ReorganizationError], list[str]]:
        errors: list[ReorganizationError] = []
        warnings: list[str] = []
        environment = self._environment.inspect(self.layout, self._leases)
        errors.extend(environment.errors)
        if self._memory is None:
            errors.append(
                self._error(
                    ReorganizationErrorCode.CAPABILITY_UNAVAILABLE,
                    "Friday Memory recovery participant is unavailable",
                    store="memory",
                )
            )
        else:
            discovery = await self._memory.discover()
            if not discovery.snapshot_supported:
                errors.extend(
                    self._error(
                        ReorganizationErrorCode.PREFLIGHT_FAILED,
                        detail.message,
                        store=(detail.store.value if detail.store else "memory"),
                    )
                    for detail in discovery.errors
                )
        if self._transcript is None:
            errors.append(
                self._error(
                    ReorganizationErrorCode.CAPABILITY_UNAVAILABLE,
                    "Friday Transcript recovery participant is unavailable",
                    store="transcript",
                )
            )
        if self._runtime_hooks is None:
            errors.append(
                self._error(
                    ReorganizationErrorCode.CAPABILITY_UNAVAILABLE,
                    "runtime quiescence hooks are unavailable",
                )
            )
        planned_steps = self._planned_steps(request)
        if planned_steps:
            if self._mutation is None:
                errors.append(
                    self._error(
                        ReorganizationErrorCode.CAPABILITY_UNAVAILABLE,
                        "maintenance mutation adapter is unavailable",
                    )
                )
            else:
                preflight = await self._mutation.preflight(request, planned_steps)
                warnings.extend(preflight.warnings)
                errors.extend(preflight.errors)
                if preflight.planned_steps != planned_steps:
                    errors.append(
                        self._error(
                            ReorganizationErrorCode.PREFLIGHT_FAILED,
                            "maintenance adapter changed the coordinator plan",
                        )
                    )
                if not preflight.supported and not preflight.errors:
                    errors.append(
                        self._error(
                            ReorganizationErrorCode.CAPABILITY_UNAVAILABLE,
                            "maintenance capabilities are unavailable",
                        )
                    )
        return errors, warnings

    @staticmethod
    def _planned_steps(
        request: ReorganizationRequest,
    ) -> tuple[MutationStep, ...]:
        if request.mode is ReorganizationMode.BACKUP:
            return ()
        if request.mode is ReorganizationMode.ANALYZE:
            return (MutationStep.ANALYZE,)
        if request.mode is ReorganizationMode.DEDUPE:
            return (MutationStep.DEDUPE,)
        if request.mode is ReorganizationMode.PRUNE:
            return (MutationStep.PRUNE,)
        if request.mode is ReorganizationMode.SYNTHESIZE:
            return (MutationStep.SYNTHESIZE,)
        if request.mode is ReorganizationMode.VERIFY:
            return (MutationStep.VERIFY,)
        steps: list[MutationStep] = []
        if request.force_reembed:
            steps.append(MutationStep.REEMBED)
        steps.extend((MutationStep.DEDUPE, MutationStep.PRUNE))
        if not request.skip_synthesis:
            steps.append(MutationStep.SYNTHESIZE)
        if not request.skip_verify:
            steps.append(MutationStep.VERIFY)
        if not request.skip_lifecycle:
            steps.append(MutationStep.LIFECYCLE)
        return tuple(steps)

    @staticmethod
    def _skipped_mutation_steps(
        request: ReorganizationRequest,
    ) -> tuple[MutationStepResult, ...]:
        if request.mode is not ReorganizationMode.FULL:
            return ()
        skipped: list[MutationStepResult] = []
        for selected, step in (
            (request.skip_synthesis, MutationStep.SYNTHESIZE),
            (request.skip_verify, MutationStep.VERIFY),
            (request.skip_lifecycle, MutationStep.LIFECYCLE),
        ):
            if selected:
                skipped.append(
                    MutationStepResult(
                        step=step,
                        status=MutationStepStatus.SKIPPED,
                        changed_count=0,
                    )
                )
        return tuple(skipped)

    def _unfinished_journals(self) -> tuple[RecoveryJournal, ...]:
        root = self.layout.recovery_root
        try:
            entries = list(root.iterdir())
        except FileNotFoundError:
            return ()
        except OSError as exc:
            raise DurableArtifactError(
                "recovery root cannot be inspected safely"
            ) from exc
        if len(entries) > _MAX_RUN_DIRECTORIES:
            raise DurableArtifactError("recovery root exceeds its bounded run limit")
        journals: list[RecoveryJournal] = []
        for entry in sorted(entries, key=lambda path: path.name):
            if _RUN_ID_PATTERN.fullmatch(entry.name) is None:
                continue
            journal_path = self._artifacts.journal_path(entry.name)
            try:
                journal, _ = self._artifacts.read_journal(journal_path)
            except DurableArtifactError as exc:
                raise DurableArtifactError(
                    "recovery root contains unverifiable run evidence"
                ) from exc
            if journal.state is not JournalState.COMPLETE:
                journals.append(journal)
        return tuple(journals)

    def _advance_to_recovery_in_progress(
        self,
        cursor: _JournalCursor,
        errors: list[ReorganizationError],
    ) -> _JournalCursor:
        state = cursor.journal.state
        if state is JournalState.MUTATION_IN_PROGRESS:
            cursor = self._transition(
                cursor,
                JournalState.ROLLBACK_IN_PROGRESS,
                safe_boundary=JournalSafeBoundary.MUTATION_UNCERTAIN,
                errors=tuple(errors),
            )
            state = cursor.journal.state
        if state is JournalState.ROLLBACK_IN_PROGRESS:
            cursor = self._transition(
                cursor,
                JournalState.RECOVERY_REQUIRED,
                safe_boundary=JournalSafeBoundary.RECOVERY_REQUIRED,
                errors=tuple(errors),
            )
            state = cursor.journal.state
        if state is JournalState.RECOVERY_IN_PROGRESS:
            cursor = self._transition(
                cursor,
                JournalState.RECOVERY_REQUIRED,
                safe_boundary=JournalSafeBoundary.RECOVERY_REQUIRED,
                errors=tuple(errors),
            )
            state = cursor.journal.state
        if state is not JournalState.RECOVERY_REQUIRED:
            raise DurableArtifactError("journal state cannot enter explicit recovery")
        return self._transition(
            cursor,
            JournalState.RECOVERY_IN_PROGRESS,
            safe_boundary=JournalSafeBoundary.RECOVERY_REQUIRED,
            errors=tuple(errors),
        )

    def _complete_pre_mutation(
        self,
        cursor: _JournalCursor,
        *,
        status: ResultStatus,
        errors: list[ReorganizationError],
        completed_steps: tuple[ProgressStep, ...],
    ) -> None:
        if cursor.journal.state not in {
            JournalState.CREATED,
            JournalState.SNAPSHOT_IN_PROGRESS,
            JournalState.SNAPSHOT_VERIFIED,
        }:
            raise DurableArtifactError(
                "unsafe journal cannot use pre-mutation terminalization"
            )
        boundary = (
            JournalSafeBoundary.SNAPSHOT_VERIFIED_LIVE_UNMODIFIED
            if cursor.journal.state is JournalState.SNAPSHOT_VERIFIED
            else JournalSafeBoundary.LIVE_UNMODIFIED
        )
        next_cursor = self._transition(
            cursor,
            JournalState.COMPLETE,
            safe_boundary=boundary,
            completed_steps=completed_steps,
            terminal_status=status,
            errors=tuple(errors),
        )
        cursor.journal = next_cursor.journal
        cursor.sha256 = next_cursor.sha256

    def _transition(
        self,
        cursor: _JournalCursor,
        state: JournalState,
        *,
        safe_boundary: JournalSafeBoundary,
        bundle_manifest_path: Path | None = None,
        bundle_manifest_sha256: str | None = None,
        completed_steps: tuple[ProgressStep, ...] | None = None,
        terminal_status: ResultStatus | None = None,
        errors: tuple[ReorganizationError, ...] | None = None,
    ) -> _JournalCursor:
        now = datetime.now(UTC)
        if now <= cursor.journal.updated_at:
            now = cursor.journal.updated_at + timedelta(microseconds=1)
        current = cursor.journal.transition(
            state,
            updated_at=now,
            safe_boundary=safe_boundary,
            bundle_manifest_path=bundle_manifest_path,
            bundle_manifest_sha256=bundle_manifest_sha256,
            completed_steps=completed_steps,
            terminal_status=terminal_status,
            errors=errors,
        )
        artifact = self._artifacts.write_journal_transition(
            cursor.journal,
            current,
            expected_current_sha256=cursor.sha256,
        )
        return _JournalCursor(journal=current, sha256=artifact.sha256)

    async def _progress(
        self,
        step: ProgressStep,
        message: str,
        callback: MaintenanceProgressCallback | None,
        attempted: list[ProgressStep],
    ) -> None:
        if step not in attempted:
            attempted.append(step)
        if callback is not None:
            await callback(step, message)

    async def _rollback_progress_safely(
        self,
        *,
        progress: MaintenanceProgressCallback | None,
        attempted: list[ProgressStep],
        errors: list[ReorganizationError],
    ) -> None:
        try:
            await self._progress(
                ProgressStep.ROLLING_BACK,
                "Restoring the verified pre-mutation bundle",
                progress,
                attempted,
            )
        except BaseException as exc:
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            errors.append(
                self._exception_error(
                    exc,
                    restore=True,
                    cancelled=isinstance(exc, asyncio.CancelledError),
                )
            )

    async def _fault(
        self,
        point: CoordinatorFaultPoint,
        step: MutationStep | None = None,
    ) -> None:
        if self._fault_injector is not None:
            await self._fault_injector(point, step)

    @staticmethod
    async def _atomic(
        operation: Awaitable[_AtomicResultT],
        *,
        cancellation_callback: Callable[[], Awaitable[None]] | None = None,
    ) -> _AtomicResultT:
        task = asyncio.ensure_future(operation)
        cancellation_pending = False
        while not task.done():
            try:
                await asyncio.shield(task)
            except asyncio.CancelledError:
                if not cancellation_pending and cancellation_callback is not None:
                    try:
                        await cancellation_callback()
                    except BaseException as callback_exc:
                        if isinstance(callback_exc, (KeyboardInterrupt, SystemExit)):
                            raise
                cancellation_pending = True
                continue
        if task.cancelled():
            raise asyncio.CancelledError
        result = task.result()
        if cancellation_pending:
            raise asyncio.CancelledError
        return result

    @staticmethod
    def _cancellation_reporter(
        progress: MaintenanceProgressCallback | None,
        step: ProgressStep,
    ) -> Callable[[], Awaitable[None]] | None:
        if progress is None:
            return None

        async def report() -> None:
            await progress(
                step,
                "Cancellation pending; waiting for the current atomic section",
            )

        return report

    @staticmethod
    def _verified_memory_path(result: MemoryOperationResult) -> Path:
        ReorganizationCoordinator._require_verified_memory(result)
        if result.manifest_path is None:
            raise DurableArtifactError("memory snapshot omitted its manifest path")
        return Path(result.manifest_path)

    @staticmethod
    def _verified_transcript_path(result: TranscriptSnapshotResult) -> Path:
        ReorganizationCoordinator._require_verified_transcript(result)
        if result.manifest_path is None:
            raise DurableArtifactError("transcript snapshot omitted its manifest path")
        return Path(result.manifest_path)

    @staticmethod
    def _require_verified_memory(result: MemoryOperationResult) -> None:
        if not result.verified:
            raise DurableArtifactError("Friday Memory recovery verification failed")

    @staticmethod
    def _require_verified_transcript(result: TranscriptSnapshotResult) -> None:
        if not result.verified:
            raise DurableArtifactError("Friday Transcript recovery verification failed")

    def _require_memory_participant(self) -> MemoryRecoveryParticipant:
        if self._memory is None:
            raise DurableArtifactError(
                "Friday Memory recovery participant is unavailable"
            )
        return self._memory

    def _require_transcript_participant(self) -> TranscriptSnapshotParticipant:
        if self._transcript is None:
            raise DurableArtifactError(
                "Friday Transcript recovery participant is unavailable"
            )
        return self._transcript

    def _require_runtime_hooks(self) -> MaintenanceRuntimeHooks:
        if self._runtime_hooks is None:
            raise DurableArtifactError("runtime quiescence hooks are unavailable")
        return self._runtime_hooks

    def _resume_manual_maintenance(self) -> ManualMaintenanceResumeResult:
        """Resume preempted work after exclusive admission has been released."""
        if self._runtime_hooks is None:
            return ManualMaintenanceResumeResult()
        try:
            return self._runtime_hooks.resume_after_manual_maintenance()
        except Exception as exc:
            return ManualMaintenanceResumeResult(
                required=True,
                error_type=type(exc).__name__,
            )

    @staticmethod
    def _with_resume_evidence(
        result: ReorganizationResult,
        resume: ManualMaintenanceResumeResult,
    ) -> ReorganizationResult:
        """Attach categorical resumption failures without hiding terminal state."""
        if not resume.warnings:
            return result
        warnings = [*result.warnings, *resume.warnings]
        status = result.status
        if status is ResultStatus.COMPLETED:
            status = ResultStatus.COMPLETED_WITH_WARNINGS
        payload = result.model_dump(mode="python")
        payload.update(status=status, warnings=warnings)
        return ReorganizationResult.model_validate(payload)

    def _require_mutation_adapter(self) -> MaintenanceMutationAdapter:
        if self._mutation is None:
            raise DurableArtifactError("maintenance mutation adapter is unavailable")
        return self._mutation

    @staticmethod
    def _crossed_mutation(journal: RecoveryJournal) -> bool:
        return JournalState.MUTATION_IN_PROGRESS in journal.state_history

    @staticmethod
    def _error(
        code: ReorganizationErrorCode,
        message: str,
        *,
        store: str | None = None,
    ) -> ReorganizationError:
        return ReorganizationError(code=code, message=message, store=store)

    @classmethod
    def _exception_error(
        cls,
        exc: BaseException,
        *,
        preflight: bool = False,
        restore: bool = False,
        cancelled: bool = False,
    ) -> ReorganizationError:
        if cancelled:
            code = ReorganizationErrorCode.CANCELLED
        elif restore:
            code = ReorganizationErrorCode.RESTORE_FAILED
        elif preflight:
            code = ReorganizationErrorCode.PREFLIGHT_FAILED
        else:
            code = ReorganizationErrorCode.MUTATION_FAILED
        return cls._error(
            code,
            f"reorganization operation failed ({type(exc).__name__})",
        )

    def _result(
        self,
        request: ReorganizationRequest,
        cursor: _JournalCursor,
        status: ResultStatus,
        attempted: list[ProgressStep],
        completed: list[ProgressStep],
        stores: list[StoreOperationResult],
        mutation_steps: list[MutationStepResult],
        warnings: list[str],
        errors: list[ReorganizationError],
    ) -> ReorganizationResult:
        return ReorganizationResult(
            status=status,
            trigger=request.trigger,
            mode=request.mode,
            run_id=cursor.journal.run_id,
            attempted_steps=attempted,
            completed_steps=completed,
            stores=stores,
            mutation_steps=mutation_steps,
            recovery_manifest_path=cursor.journal.bundle_manifest_path,
            journal_path=cursor.journal.journal_path,
            reorganization_log_path=self._log_path(cursor.journal.run_id),
            warnings=warnings,
            errors=errors,
        )

    def _log_path(self, run_id: str) -> Path:
        return self._logs.confined_path(f"{run_id}.json")

    def _write_initial_log(self, journal: RecoveryJournal) -> None:
        if journal.requested_mode is None:
            raise DurableArtifactError(
                "ordinary reorganization log requires a requested mode"
            )
        self._logs.write_model(
            f"{journal.run_id}.json",
            ReorganizationLogRecord(
                run_id=journal.run_id,
                created_at=journal.created_at,
                trigger=journal.trigger,
                mode=journal.requested_mode,
                layout_fingerprint=journal.layout_fingerprint,
                journal_path=journal.journal_path,
            ),
            require_absent=True,
        )


__all__ = [
    "CoordinatorFaultPoint",
    "ManualMaintenanceDrainResult",
    "ManualMaintenanceResumeResult",
    "MaintenanceMutationAdapter",
    "MaintenanceProgressCallback",
    "MaintenanceRuntimeHooks",
    "MutationPreflight",
    "MutationStep",
    "MutationStepResult",
    "MutationVerification",
    "ReorganizationCoordinator",
    "ReorganizationExecutionCapability",
]
