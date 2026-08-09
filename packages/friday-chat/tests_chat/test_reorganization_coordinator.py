"""Coordinator, admission, rollback, and recovery behavior."""

from __future__ import annotations

import asyncio
import stat
from collections.abc import Sequence
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import cast

import chromadb
import pytest
from friday_chat.reorganization.contracts import (
    JournalSafeBoundary,
    JournalState,
    MutationStepStatus,
    OperationTrigger,
    ProgressStep,
    RecoveryRequest,
    ReorganizationError,
    ReorganizationErrorCode,
    ReorganizationMode,
    ReorganizationRequest,
    ResultStatus,
    StoreCapabilityState,
    StoreOperationStatus,
)
from friday_chat.reorganization.coordinator import (
    CoordinatorFaultPoint,
    ManualMaintenanceDrainResult,
    ManualMaintenanceResumeResult,
    MutationPreflight,
    MutationStep,
    MutationStepResult,
    MutationVerification,
    ReorganizationCoordinator,
)
from friday_chat.reorganization.durability import DurableArtifactError
from friday_chat.reorganization.gate import (
    MaintenanceAdmissionError,
    MaintenanceAdmissionGate,
)
from friday_chat.reorganization.layout import FridayChatMaintenanceLayout
from friday_chat.reorganization.lease import DarwinLayoutLeaseRegistry
from friday_chat.reorganization.preflight import MaintenanceEnvironmentPreflight
from friday_memory import (
    ElementXGraphStore,
    GraphNode,
    MemoryDiscoveryReport,
    MemoryMaintenanceLayout,
    MemoryMaintenanceParticipant,
    MemoryOperationResult,
    MemoryQuiescenceToken,
    MemoryRecoveryOperation,
    ProvenanceMetadata,
)
from friday_memory.maintenance.recovery import MemoryRecoveryParticipant
from friday_transcript import (
    SQLiteTranscriptStore,
    TranscriptEntry,
    TranscriptRestoreQuiescenceToken,
    TranscriptSession,
    TranscriptSnapshotParticipant,
    TranscriptSnapshotResult,
)


@dataclass
class RecordingHooks:
    calls: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    buffered_extraction_count: int = 0
    extraction_preempted: bool = False
    resume_calls: int = 0
    resume_scheduled: bool = True
    gate: MaintenanceAdmissionGate | None = None
    resume_observed_exclusive_active: bool | None = None

    async def prepare_for_manual_maintenance(self) -> None:
        return None

    async def drain_for_manual_maintenance(self) -> ManualMaintenanceDrainResult:
        self.calls.append("drain")
        self.events.append("access_buffer_drain")
        return ManualMaintenanceDrainResult(
            buffered_extraction_count=self.buffered_extraction_count,
            extraction_preempted=self.extraction_preempted,
        )

    def resume_after_manual_maintenance(self) -> ManualMaintenanceResumeResult:
        self.resume_calls += 1
        if self.gate is not None:
            self.resume_observed_exclusive_active = self.gate.snapshot.exclusive_active
        return ManualMaintenanceResumeResult(
            required=self.extraction_preempted,
            scheduled=(
                self.extraction_preempted
                and self.buffered_extraction_count > 0
                and self.resume_scheduled
            ),
            pending_count=self.buffered_extraction_count,
        )

    async def close_for_shutdown(self, *, snapshot_requested: bool) -> None:
        assert snapshot_requested
        self.calls.append("shutdown_close")
        self.events.append("access_buffer_drain")

    async def finalize_transcript(self) -> None:
        self.calls.append("finalize")
        self.events.append("transcript_finalize")


@dataclass
class OrderingMemoryParticipant:
    delegate: MemoryRecoveryParticipant
    events: list[str]
    pending_state: list[str] | None = None

    @property
    def layout_fingerprint(self) -> str:
        return cast(str, self.delegate.layout_fingerprint)

    def maintenance_quiescence(
        self,
        operation: MemoryRecoveryOperation,
    ) -> AbstractAsyncContextManager[MemoryQuiescenceToken]:
        return cast(
            AbstractAsyncContextManager[MemoryQuiescenceToken],
            self.delegate.maintenance_quiescence(operation),
        )

    async def discover(self) -> MemoryDiscoveryReport:
        return await self.delegate.discover()

    async def create_snapshot(
        self,
        run_id: str,
        token: MemoryQuiescenceToken,
    ) -> MemoryOperationResult:
        self.events.append("memory_snapshot")
        return await self.delegate.create_snapshot(run_id, token)

    async def verify_snapshot(
        self,
        manifest_path: str | Path,
    ) -> MemoryOperationResult:
        return await self.delegate.verify_snapshot(manifest_path)

    async def restore_snapshot(
        self,
        manifest_path: str | Path,
        token: MemoryQuiescenceToken,
    ) -> MemoryOperationResult:
        self.events.append("memory_restore")
        if self.pending_state is not None:
            assert self.pending_state == []
        return await self.delegate.restore_snapshot(manifest_path, token)

    async def verify_live(
        self,
        manifest_path: str | Path,
    ) -> MemoryOperationResult:
        return await self.delegate.verify_live(manifest_path)


@dataclass
class OrderingTranscriptParticipant:
    delegate: TranscriptSnapshotParticipant
    events: list[str]

    async def inspect_live(self) -> TranscriptSnapshotResult:
        return await self.delegate.inspect_live()

    async def create_snapshot(
        self,
        destination_directory: str | Path,
    ) -> TranscriptSnapshotResult:
        self.events.append("transcript_snapshot")
        return await self.delegate.create_snapshot(destination_directory)

    async def verify_snapshot(
        self,
        manifest_path: str | Path,
    ) -> TranscriptSnapshotResult:
        return await self.delegate.verify_snapshot(manifest_path)

    def restore_quiescence(
        self,
    ) -> AbstractAsyncContextManager[TranscriptRestoreQuiescenceToken]:
        return cast(
            AbstractAsyncContextManager[TranscriptRestoreQuiescenceToken],
            self.delegate.restore_quiescence(),
        )

    async def restore_snapshot(
        self,
        manifest_path: str | Path,
        token: TranscriptRestoreQuiescenceToken,
    ) -> TranscriptSnapshotResult:
        return await self.delegate.restore_snapshot(manifest_path, token)

    async def verify_live(
        self,
        manifest_path: str | Path,
    ) -> TranscriptSnapshotResult:
        return await self.delegate.verify_live(manifest_path)


@dataclass
class SyntheticGraphMutation:
    graph: ElementXGraphStore
    calls: list[str] = field(default_factory=list)
    preflight_errors: tuple[ReorganizationError, ...] = ()

    def begin_run(self, request: ReorganizationRequest) -> None:
        self.calls.append(f"begin:{request.mode.value}")

    def end_run(self, request: ReorganizationRequest) -> None:
        self.calls.append(f"end:{request.mode.value}")

    async def preview(
        self,
        request: ReorganizationRequest,
        planned_steps: tuple[MutationStep, ...],
    ) -> tuple[MutationStepResult, ...]:
        self.calls.append(f"preview:{request.mode.value}")
        return tuple(
            MutationStepResult(
                step=step,
                status=MutationStepStatus.PREVIEWED,
                scanned_count=1,
                candidate_count=1,
            )
            for step in planned_steps
        )

    async def preflight(
        self,
        request: ReorganizationRequest,
        planned_steps: tuple[MutationStep, ...],
    ) -> MutationPreflight:
        self.calls.append(f"preflight:{request.mode.value}")
        return MutationPreflight(
            supported=not self.preflight_errors,
            planned_steps=planned_steps,
            errors=self.preflight_errors,
        )

    async def execute_step(
        self,
        request: ReorganizationRequest,
        step: MutationStep,
    ) -> MutationStepResult:
        del request
        self.calls.append(f"execute:{step.value}")
        if step is MutationStep.DEDUPE:
            await self.graph.add_node(
                GraphNode(
                    id="mutation-node",
                    type="Entity",
                    label="Mutation node",
                    provenance=ProvenanceMetadata(
                        source_id="synthetic-mutation",
                        source_type="test",
                    ),
                )
            )
        return MutationStepResult(
            step=step,
            status=MutationStepStatus.COMPLETED,
            scanned_count=1,
            candidate_count=1,
            changed_count=1,
        )

    async def verify_postconditions(
        self,
        request: ReorganizationRequest,
    ) -> MutationVerification:
        del request
        self.calls.append("verify")
        return MutationVerification(verified=True)


@dataclass
class ProductionCoordinatorFixture:
    coordinator: ReorganizationCoordinator
    memory: MemoryMaintenanceParticipant
    graph: ElementXGraphStore
    transcript: SQLiteTranscriptStore
    hooks: RecordingHooks
    mutation: SyntheticGraphMutation
    layout: FridayChatMaintenanceLayout
    fault_calls: list[tuple[CoordinatorFaultPoint, MutationStep | None]]


@dataclass(frozen=True)
class SyntheticDiskUsage:
    total: int
    used: int
    free: int


@dataclass
class PendingStateHooks:
    pending_state: list[str]
    events: list[str]
    calls: list[str] = field(default_factory=list)

    async def prepare_for_manual_maintenance(self) -> None:
        return None

    async def drain_for_manual_maintenance(self) -> ManualMaintenanceDrainResult:
        self.calls.append("drain")
        self.events.append("runtime_pending_drain")
        self.pending_state.clear()
        return ManualMaintenanceDrainResult()

    def resume_after_manual_maintenance(self) -> ManualMaintenanceResumeResult:
        return ManualMaintenanceResumeResult()

    async def close_for_shutdown(self, *, snapshot_requested: bool) -> None:
        del snapshot_requested
        raise AssertionError("recovery must not use shutdown close")

    async def finalize_transcript(self) -> None:
        raise AssertionError("manual recovery must not finalize the transcript")


@dataclass
class FailingShutdownHooks:
    failure_stage: str
    events: list[str]
    calls: list[str] = field(default_factory=list)

    async def prepare_for_manual_maintenance(self) -> None:
        return None

    async def drain_for_manual_maintenance(self) -> ManualMaintenanceDrainResult:
        raise AssertionError("shutdown must not use the manual drain")

    def resume_after_manual_maintenance(self) -> ManualMaintenanceResumeResult:
        raise AssertionError("shutdown must not resume preempted extraction")

    async def close_for_shutdown(self, *, snapshot_requested: bool) -> None:
        assert snapshot_requested
        self.calls.append("shutdown_close")
        self.events.append("access_buffer_drain")
        if self.failure_stage == "close":
            raise RuntimeError("synthetic shutdown close failure")

    async def finalize_transcript(self) -> None:
        self.calls.append("finalize")
        self.events.append("transcript_finalize")
        if self.failure_stage == "finalize":
            raise RuntimeError("synthetic transcript finalize failure")


async def _production_coordinator(
    root: Path,
    *,
    graph_absent: bool = False,
    cancel_at_fault: bool = False,
    fault_point: CoordinatorFaultPoint | None = None,
    fault_points: set[CoordinatorFaultPoint] | None = None,
    fault_after_step: MutationStep | None = None,
) -> ProductionCoordinatorFixture:
    vector_path = root / "live" / "vector"
    graph_path = root / "live" / "graph.gpickle"
    transcript_path = root / "transcript" / "friday.sqlite"
    recovery_root = root / "recovery"
    log_root = root / "logs"

    client = chromadb.PersistentClient(path=str(vector_path))
    collection = client.create_collection("coordinator-test")
    embeddings: list[Sequence[float] | Sequence[int]] = [[1.0, 0.0]]
    collection.add(
        ids=["memory-1"],
        documents=["synthetic memory"],
        embeddings=embeddings,
    )
    graph = ElementXGraphStore(str(graph_path))
    if not graph_absent:
        await graph.add_node(
            GraphNode(
                id="baseline-node",
                type="Entity",
                label="Baseline node",
                provenance=ProvenanceMetadata(
                    source_id="synthetic-baseline",
                    source_type="test",
                ),
            )
        )
    transcript = SQLiteTranscriptStore(transcript_path)
    assert await transcript.create_session(
        TranscriptSession(session_id="session-1", model_name="test-model")
    )
    assert await transcript.append_entry(
        TranscriptEntry(
            id="entry-1",
            session_id="session-1",
            turn_number=1,
            user_message="synthetic",
            assistant_message="response",
        )
    )
    layout = FridayChatMaintenanceLayout.resolve_once(
        captured_process_cwd=root,
        vector_directory=vector_path,
        graph_path=graph_path,
        access_buffer_wal_path=None,
        transcript_database_path=transcript_path,
        recovery_root=recovery_root,
        log_root=log_root,
    )
    memory = MemoryMaintenanceParticipant(
        MemoryMaintenanceLayout(
            vector_directory=layout.vector_directory,
            graph_path=layout.graph_path,
            access_buffer_wal_path=layout.access_buffer_wal_path,
            recovery_directory=layout.recovery_root,
            log_directory=layout.log_root,
        ),
        graph_store=graph,
    )
    hooks = RecordingHooks()
    mutation = SyntheticGraphMutation(graph)
    fault_calls: list[tuple[CoordinatorFaultPoint, MutationStep | None]] = []

    async def inject(
        point: CoordinatorFaultPoint,
        step: MutationStep | None,
    ) -> None:
        fault_calls.append((point, step))
        selected_faults = fault_points or ({fault_point} if fault_point else set())
        if point in selected_faults and (
            fault_after_step is None or step is fault_after_step
        ):
            if cancel_at_fault:
                raise asyncio.CancelledError
            raise RuntimeError("synthetic coordinator fault")

    coordinator = ReorganizationCoordinator(
        layout=layout,
        gate=MaintenanceAdmissionGate(),
        memory_participant=memory,
        transcript_participant=transcript,
        runtime_hooks=hooks,
        mutation_adapter=mutation,
        lease_registry=DarwinLayoutLeaseRegistry(
            namespace_root=root / "leases",
            platform_name="Darwin",
            host_id="coordinator-test",
        ),
        application_version="test",
        fault_injector=inject,
    )
    hooks.gate = coordinator.gate
    return ProductionCoordinatorFixture(
        coordinator=coordinator,
        memory=memory,
        graph=graph,
        transcript=transcript,
        hooks=hooks,
        mutation=mutation,
        layout=layout,
        fault_calls=fault_calls,
    )


def _restarted_coordinator(
    fixture: ProductionCoordinatorFixture,
) -> tuple[ReorganizationCoordinator, ElementXGraphStore, SQLiteTranscriptStore]:
    layout = fixture.layout
    graph = ElementXGraphStore(str(layout.graph_path))
    memory = MemoryMaintenanceParticipant(
        MemoryMaintenanceLayout(
            vector_directory=layout.vector_directory,
            graph_path=layout.graph_path,
            access_buffer_wal_path=layout.access_buffer_wal_path,
            recovery_directory=layout.recovery_root,
            log_directory=layout.log_root,
        ),
        graph_store=graph,
    )
    transcript = SQLiteTranscriptStore(layout.transcript_database_path)
    coordinator = ReorganizationCoordinator(
        layout=layout,
        gate=MaintenanceAdmissionGate(),
        memory_participant=memory,
        transcript_participant=transcript,
        runtime_hooks=RecordingHooks(),
        lease_registry=DarwinLayoutLeaseRegistry(
            namespace_root=layout.captured_process_cwd / "leases",
            platform_name="Darwin",
            host_id="coordinator-test",
        ),
        application_version="test",
    )
    return coordinator, graph, transcript


@pytest.mark.asyncio
async def test_gate_closure_wakes_and_rejects_queued_shared_waiter() -> None:
    gate = MaintenanceAdmissionGate()
    exclusive_entered = asyncio.Event()
    release_exclusive = asyncio.Event()

    async def hold_exclusive() -> None:
        async with gate.exclusive("test-exclusive"):
            exclusive_entered.set()
            await release_exclusive.wait()

    async def wait_shared() -> None:
        async with gate.shared("queued-shared"):
            raise AssertionError("closed shared waiter was admitted")

    exclusive = asyncio.create_task(hold_exclusive())
    await exclusive_entered.wait()
    shared = asyncio.create_task(wait_shared())
    await asyncio.sleep(0)
    assert not shared.done()

    await gate.close_shared_admission()
    with pytest.raises(MaintenanceAdmissionError, match="closed"):
        await shared
    release_exclusive.set()
    await exclusive


@pytest.mark.asyncio
async def test_exclusive_preparation_can_cancel_an_active_shared_writer() -> None:
    gate = MaintenanceAdmissionGate()
    writer_started = asyncio.Event()

    async def active_writer() -> None:
        async with gate.shared("background-extraction"):
            writer_started.set()
            await asyncio.Event().wait()

    writer = asyncio.create_task(active_writer())
    await writer_started.wait()

    async def prepare() -> None:
        snapshot = gate.snapshot
        assert snapshot.active_shared == 1
        assert snapshot.exclusive_waiters == 1
        assert snapshot.accepting_shared is False
        writer.cancel()
        await asyncio.gather(writer, return_exceptions=True)

    async with gate.exclusive("manual-reorganization", prepare=prepare):
        snapshot = gate.snapshot
        assert snapshot.active_shared == 0
        assert snapshot.exclusive_active is True

    assert writer.cancelled()
    assert gate.snapshot.accepting_shared is True


@pytest.mark.asyncio
async def test_dry_run_has_no_durable_or_runtime_side_effects(
    tmp_path: Path,
) -> None:
    layout = FridayChatMaintenanceLayout.resolve_once(
        captured_process_cwd=tmp_path,
        vector_directory="live/vector",
        graph_path="live/graph.json",
        access_buffer_wal_path=None,
        transcript_database_path="transcript/live.sqlite",
        recovery_root="operator/recovery",
        log_root="operator/logs",
    )
    lease_root = tmp_path / "leases"
    coordinator = ReorganizationCoordinator(
        layout=layout,
        gate=MaintenanceAdmissionGate(),
        memory_participant=None,
        transcript_participant=None,
        runtime_hooks=None,
        lease_registry=DarwinLayoutLeaseRegistry(
            namespace_root=lease_root,
            platform_name="Darwin",
            host_id="dry-run-test",
        ),
    )

    result = await coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.FULL,
        )
    )

    assert result.status is ResultStatus.PREFLIGHT_FAILED
    assert not layout.recovery_root.exists()
    assert not layout.log_root.exists()
    assert not lease_root.exists()


@pytest.mark.asyncio
async def test_dry_run_reports_provider_readiness_failure_without_artifacts(
    tmp_path: Path,
) -> None:
    fixture = await _production_coordinator(tmp_path)
    fixture.mutation.preflight_errors = (
        ReorganizationError(
            code=ReorganizationErrorCode.CAPABILITY_UNAVAILABLE,
            message="maintenance judge provider readiness failed (TimeoutError)",
        ),
    )

    result = await fixture.coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.VERIFY,
        )
    )

    assert result.status is ResultStatus.PREFLIGHT_FAILED
    assert result.errors == list(fixture.mutation.preflight_errors)
    assert fixture.mutation.calls == ["preflight:verify", "preview:verify"]
    assert not fixture.layout.recovery_root.exists()
    assert not fixture.layout.log_root.exists()


@pytest.mark.asyncio
@pytest.mark.parametrize("failure_kind", ["capacity", "permission"])
async def test_environment_preflight_failure_prevents_snapshot_and_mutation(
    tmp_path: Path,
    failure_kind: str,
) -> None:
    fixture = await _production_coordinator(tmp_path)
    fixture.hooks.buffered_extraction_count = 1
    fixture.hooks.extraction_preempted = True
    if failure_kind == "permission":
        fixture.layout.log_root.mkdir(mode=0o700)
        fixture.layout.log_root.chmod(0o755)
    environment = (
        MaintenanceEnvironmentPreflight(
            disk_usage=lambda _path: SyntheticDiskUsage(
                total=1024,
                used=1024,
                free=0,
            )
        )
        if failure_kind == "capacity"
        else MaintenanceEnvironmentPreflight()
    )
    coordinator = ReorganizationCoordinator(
        layout=fixture.layout,
        gate=MaintenanceAdmissionGate(),
        memory_participant=fixture.memory,
        transcript_participant=fixture.transcript,
        runtime_hooks=fixture.hooks,
        mutation_adapter=fixture.mutation,
        lease_registry=DarwinLayoutLeaseRegistry(
            namespace_root=tmp_path / f"{failure_kind}-leases",
            platform_name="Darwin",
            host_id="environment-preflight-test",
        ),
        application_version="test",
        environment_preflight=environment,
    )
    fixture.hooks.gate = coordinator.gate

    result = await coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.DEDUPE,
            execute=True,
        )
    )

    assert result.status is ResultStatus.PREFLIGHT_FAILED
    assert result.journal_path is not None and result.journal_path.exists()
    assert result.recovery_manifest_path is None
    assert "execute:dedupe" not in fixture.mutation.calls
    assert await fixture.graph.get_node("mutation-node") is None
    assert fixture.hooks.resume_calls == 1
    assert fixture.hooks.resume_observed_exclusive_active is False


@pytest.mark.asyncio
async def test_atomic_section_finishes_under_repeated_cancellation() -> None:
    started = asyncio.Event()
    release = asyncio.Event()
    completed = asyncio.Event()
    cancellation_messages: list[str] = []

    async def report_pending() -> None:
        cancellation_messages.append("cancellation pending")

    async def inner() -> str:
        started.set()
        await release.wait()
        completed.set()
        return "finished"

    task = asyncio.create_task(
        ReorganizationCoordinator._atomic(
            inner(),
            cancellation_callback=report_pending,
        )
    )
    await started.wait()
    task.cancel()
    await asyncio.sleep(0)
    task.cancel()
    await asyncio.sleep(0)
    assert not completed.is_set()
    assert cancellation_messages == ["cancellation pending"]

    release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert completed.is_set()


@pytest.mark.asyncio
async def test_production_participants_create_verified_bundle_before_mutation(
    tmp_path: Path,
) -> None:
    fixture = await _production_coordinator(tmp_path)

    result = await fixture.coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.DEDUPE,
            execute=True,
        )
    )

    assert result.status is ResultStatus.COMPLETED
    assert result.recovery_manifest_path is not None
    assert result.recovery_manifest_path.is_file()
    assert await fixture.graph.get_node("mutation-node") is not None
    assert fixture.hooks.calls == ["drain"]
    assert result.journal_path is not None
    assert result.reorganization_log_path is not None
    assert result.reorganization_log_path.is_file()
    assert stat.S_IMODE(result.reorganization_log_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(result.reorganization_log_path.parent.stat().st_mode) == 0o700
    log_payload = result.reorganization_log_path.read_text()
    assert "synthetic memory" not in log_payload
    assert "synthetic-baseline" not in log_payload
    assert '"content_policy":"categorical_only"' in log_payload
    journal, _ = fixture.coordinator._artifacts.read_journal(result.journal_path)
    assert journal.state is JournalState.COMPLETE
    assert journal.state_history.index(JournalState.SNAPSHOT_VERIFIED) < (
        journal.state_history.index(JournalState.MUTATION_IN_PROGRESS)
    )


@pytest.mark.asyncio
async def test_execute_defers_pending_extraction_without_blocking_mutation(
    tmp_path: Path,
) -> None:
    fixture = await _production_coordinator(tmp_path)
    fixture.hooks.buffered_extraction_count = 1

    result = await fixture.coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.DEDUPE,
            execute=True,
        )
    )

    assert result.status is ResultStatus.COMPLETED_WITH_WARNINGS
    assert result.warnings == [
        "1 extraction turn is buffered for the next configured trigger; "
        "no extraction task was running"
    ]
    assert fixture.hooks.resume_calls == 1
    assert fixture.hooks.resume_observed_exclusive_active is False
    assert result.recovery_manifest_path is not None
    assert await fixture.graph.get_node("mutation-node") is not None


@pytest.mark.asyncio
async def test_execute_resumes_only_preempted_extraction_after_gate_release(
    tmp_path: Path,
) -> None:
    fixture = await _production_coordinator(tmp_path)
    fixture.hooks.buffered_extraction_count = 2
    fixture.hooks.extraction_preempted = True

    result = await fixture.coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.DEDUPE,
            execute=True,
        )
    )

    assert result.status is ResultStatus.COMPLETED_WITH_WARNINGS
    assert result.warnings == [
        "Running extraction was preempted safely; 2 unfinished turns were "
        "preserved for post-maintenance resumption"
    ]
    assert fixture.hooks.resume_calls == 1
    assert fixture.hooks.resume_observed_exclusive_active is False


@pytest.mark.asyncio
async def test_execute_reports_unscheduled_post_maintenance_resume(
    tmp_path: Path,
) -> None:
    fixture = await _production_coordinator(tmp_path)
    fixture.hooks.buffered_extraction_count = 1
    fixture.hooks.extraction_preempted = True
    fixture.hooks.resume_scheduled = False

    result = await fixture.coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.DEDUPE,
            execute=True,
        )
    )

    assert result.status is ResultStatus.COMPLETED_WITH_WARNINGS
    assert result.warnings[-1] == (
        "1 preempted extraction turn remains preserved, but post-maintenance "
        "resumption could not be scheduled"
    )
    assert fixture.hooks.resume_calls == 1
    assert fixture.hooks.resume_observed_exclusive_active is False


@pytest.mark.asyncio
async def test_post_mutation_fault_rolls_back_production_participants(
    tmp_path: Path,
) -> None:
    fixture = await _production_coordinator(
        tmp_path,
        fault_point=CoordinatorFaultPoint.AFTER_MUTATION_STEP,
    )
    fixture.hooks.buffered_extraction_count = 1
    fixture.hooks.extraction_preempted = True

    result = await fixture.coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.DEDUPE,
            execute=True,
        )
    )

    assert result.status is ResultStatus.FAILED_ROLLED_BACK
    assert fixture.hooks.resume_calls == 1
    assert await fixture.graph.get_node("mutation-node") is None
    assert await fixture.graph.get_node("baseline-node") is not None
    assert await fixture.transcript.count_entries("session-1") == 1


@pytest.mark.asyncio
async def test_post_mutation_cancellation_triggers_verified_rollback(
    tmp_path: Path,
) -> None:
    fixture = await _production_coordinator(
        tmp_path,
        cancel_at_fault=True,
        fault_point=CoordinatorFaultPoint.AFTER_MUTATION_STEP,
    )
    fixture.hooks.buffered_extraction_count = 1
    fixture.hooks.extraction_preempted = True

    result = await fixture.coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.DEDUPE,
            execute=True,
        )
    )

    assert result.status is ResultStatus.FAILED_ROLLED_BACK
    assert fixture.hooks.resume_calls == 1
    assert any(
        error.code is ReorganizationErrorCode.CANCELLED for error in result.errors
    )
    assert await fixture.graph.get_node("mutation-node") is None
    assert await fixture.graph.get_node("baseline-node") is not None
    assert await fixture.transcript.count_entries("session-1") == 1


@pytest.mark.asyncio
async def test_configured_absent_graph_is_supported_and_rollback_restores_absence(
    tmp_path: Path,
) -> None:
    fixture = await _production_coordinator(
        tmp_path,
        graph_absent=True,
        fault_point=CoordinatorFaultPoint.AFTER_MUTATION_STEP,
    )

    result = await fixture.coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.DEDUPE,
            execute=True,
        )
    )

    graph_result = next(store for store in result.stores if store.store == "graph")
    assert graph_result.capability_state is StoreCapabilityState.CONFIGURED_ABSENT
    assert graph_result.status is StoreOperationStatus.COMPLETED
    assert graph_result.verified
    assert result.status is ResultStatus.FAILED_ROLLED_BACK
    assert not fixture.layout.graph_path.exists()
    assert await fixture.graph.get_node("mutation-node") is None


@pytest.mark.asyncio
@pytest.mark.parametrize("failure_kind", ["error", "cancel"])
async def test_progress_failure_cannot_prevent_post_mutation_rollback(
    tmp_path: Path,
    failure_kind: str,
) -> None:
    fixture = await _production_coordinator(
        tmp_path,
        fault_point=CoordinatorFaultPoint.AFTER_MUTATION_STEP,
    )

    async def failing_progress(step: ProgressStep, message: str) -> None:
        del message
        if step is ProgressStep.ROLLING_BACK:
            if failure_kind == "cancel":
                raise asyncio.CancelledError
            raise RuntimeError("synthetic progress failure")

    result = await fixture.coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.DEDUPE,
            execute=True,
        ),
        progress=failing_progress,
    )

    assert result.status is ResultStatus.FAILED_ROLLED_BACK
    assert await fixture.graph.get_node("mutation-node") is None
    assert len(result.errors) >= 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("faults", "expected_status", "mutation_remains"),
    [
        (
            {CoordinatorFaultPoint.BEFORE_MUTATION_STEP},
            ResultStatus.FAILED_ROLLED_BACK,
            False,
        ),
        (
            {CoordinatorFaultPoint.AFTER_MUTATION_STEP},
            ResultStatus.FAILED_ROLLED_BACK,
            False,
        ),
        (
            {CoordinatorFaultPoint.BEFORE_LIVE_VERIFICATION},
            ResultStatus.FAILED_ROLLED_BACK,
            False,
        ),
        (
            {
                CoordinatorFaultPoint.AFTER_MUTATION_STEP,
                CoordinatorFaultPoint.BEFORE_ROLLBACK,
            },
            ResultStatus.RECOVERY_REQUIRED,
            True,
        ),
        (
            {
                CoordinatorFaultPoint.AFTER_MUTATION_STEP,
                CoordinatorFaultPoint.AFTER_ROLLBACK,
            },
            ResultStatus.RECOVERY_REQUIRED,
            False,
        ),
    ],
)
async def test_mutation_and_rollback_fault_boundaries_are_fail_safe(
    tmp_path: Path,
    faults: set[CoordinatorFaultPoint],
    expected_status: ResultStatus,
    mutation_remains: bool,
) -> None:
    fixture = await _production_coordinator(tmp_path, fault_points=faults)

    result = await fixture.coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.DEDUPE,
            execute=True,
        )
    )

    assert result.status is expected_status
    assert (await fixture.graph.get_node("mutation-node") is not None) is (
        mutation_remains
    )
    assert result.journal_path is not None
    journal, _ = fixture.coordinator._artifacts.read_journal(result.journal_path)
    assert journal.state is (
        JournalState.RECOVERY_REQUIRED
        if expected_status is ResultStatus.RECOVERY_REQUIRED
        else JournalState.COMPLETE
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "fault_step",
    [
        MutationStep.REEMBED,
        MutationStep.DEDUPE,
        MutationStep.PRUNE,
        MutationStep.SYNTHESIZE,
        MutationStep.VERIFY,
        MutationStep.LIFECYCLE,
    ],
)
async def test_full_pipeline_rolls_back_after_each_step_boundary(
    tmp_path: Path,
    fault_step: MutationStep,
) -> None:
    fixture = await _production_coordinator(
        tmp_path,
        fault_point=CoordinatorFaultPoint.AFTER_MUTATION_STEP,
        fault_after_step=fault_step,
    )

    result = await fixture.coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.FULL,
            execute=True,
            force_reembed=True,
        )
    )

    assert result.status is ResultStatus.FAILED_ROLLED_BACK
    assert (
        CoordinatorFaultPoint.AFTER_MUTATION_STEP,
        fault_step,
    ) in fixture.fault_calls
    assert f"execute:{fault_step.value}" in fixture.mutation.calls
    assert await fixture.graph.get_node("mutation-node") is None
    assert await fixture.graph.get_node("baseline-node") is not None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "fault_point",
    [
        CoordinatorFaultPoint.AFTER_JOURNAL,
        CoordinatorFaultPoint.AFTER_LEASE,
        CoordinatorFaultPoint.AFTER_PREFLIGHT,
        CoordinatorFaultPoint.AFTER_SNAPSHOT,
        CoordinatorFaultPoint.AFTER_BUNDLE_VERIFIED,
    ],
)
async def test_pre_mutation_faults_terminalize_without_changing_live_state(
    tmp_path: Path,
    fault_point: CoordinatorFaultPoint,
) -> None:
    fixture = await _production_coordinator(tmp_path, fault_point=fault_point)

    result = await fixture.coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.DEDUPE,
            execute=True,
        )
    )

    assert result.status is ResultStatus.FAILED
    assert await fixture.graph.get_node("mutation-node") is None
    assert await fixture.graph.get_node("baseline-node") is not None
    assert await fixture.transcript.count_entries("session-1") == 1
    assert result.journal_path is not None
    journal, _ = fixture.coordinator._artifacts.read_journal(result.journal_path)
    assert journal.state is JournalState.COMPLETE
    assert JournalState.MUTATION_IN_PROGRESS not in journal.state_history
    assert fixture.coordinator.startup_recovery_warnings() == ()


@pytest.mark.asyncio
async def test_rollback_failure_retains_exact_bundle_for_explicit_recovery(
    tmp_path: Path,
) -> None:
    fixture = await _production_coordinator(
        tmp_path,
        fault_points={
            CoordinatorFaultPoint.AFTER_MUTATION_STEP,
            CoordinatorFaultPoint.BEFORE_ROLLBACK,
        },
    )
    failed = await fixture.coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.DEDUPE,
            execute=True,
        )
    )

    assert failed.status is ResultStatus.RECOVERY_REQUIRED
    assert failed.run_id is not None
    assert await fixture.graph.get_node("mutation-node") is not None
    assert fixture.coordinator.startup_recovery_warnings()

    restarted, restarted_graph, restarted_transcript = _restarted_coordinator(fixture)
    assert restarted is not fixture.coordinator
    assert restarted_graph is not fixture.graph
    assert restarted_transcript is not fixture.transcript

    inspected = await restarted.recover(RecoveryRequest(run_id=failed.run_id))
    recovered = await restarted.recover(
        RecoveryRequest(run_id=failed.run_id, execute=True)
    )

    assert inspected.status is ResultStatus.RECOVERY_REQUIRED
    assert recovered.status is ResultStatus.COMPLETED_WITH_WARNINGS
    assert recovered.recovery_manifest_path == failed.recovery_manifest_path
    assert await restarted_graph.get_node("mutation-node") is None
    assert await restarted_transcript.count_entries("session-1") == 1
    assert restarted.startup_recovery_warnings() == ()


@pytest.mark.asyncio
async def test_no_error_pre_mutation_journal_inspects_and_terminalizes(
    tmp_path: Path,
) -> None:
    fixture = await _production_coordinator(tmp_path)
    journal = fixture.coordinator._artifacts.new_journal(
        application_id="friday-chat",
        application_version="test",
        trigger=OperationTrigger.MANUAL,
        requested_mode=ReorganizationMode.DEDUPE,
    )
    fixture.coordinator._artifacts.write_initial_journal(journal)
    fixture.coordinator._write_initial_log(journal)
    restarted, _graph, _transcript = _restarted_coordinator(fixture)

    inspected = await restarted.recover(RecoveryRequest(run_id=journal.run_id))
    terminalized = await restarted.recover(
        RecoveryRequest(run_id=journal.run_id, execute=True)
    )

    assert inspected.status is ResultStatus.RECOVERY_REQUIRED
    assert inspected.errors == [
        ReorganizationError(
            code=ReorganizationErrorCode.RECOVERY_REQUIRED,
            message="unfinished durable journal requires explicit recovery",
        )
    ]
    assert "live stores are unmodified" in inspected.warnings[0]
    assert terminalized.status is ResultStatus.CANCELLED
    assert any(
        error.code is ReorganizationErrorCode.CANCELLED
        for error in terminalized.errors
    )
    retained, _ = restarted._artifacts.read_journal(journal.journal_path)
    assert retained.state is JournalState.COMPLETE
    assert retained.safe_boundary is JournalSafeBoundary.LIVE_UNMODIFIED
    assert restarted.startup_recovery_warnings() == ()


@pytest.mark.asyncio
async def test_no_error_snapshot_verified_journal_terminalizes_without_restore(
    tmp_path: Path,
) -> None:
    fixture = await _production_coordinator(tmp_path)
    journal = fixture.coordinator._artifacts.new_journal(
        application_id="friday-chat",
        application_version="test",
        trigger=OperationTrigger.MANUAL,
        requested_mode=ReorganizationMode.BACKUP,
    )
    initial = fixture.coordinator._artifacts.write_initial_journal(journal)
    fixture.coordinator._write_initial_log(journal)
    snapshot_in_progress = journal.transition(
        JournalState.SNAPSHOT_IN_PROGRESS,
        updated_at=journal.updated_at + timedelta(microseconds=1),
        safe_boundary=JournalSafeBoundary.LIVE_UNMODIFIED,
    )
    snapshot_artifact = fixture.coordinator._artifacts.write_journal_transition(
        journal,
        snapshot_in_progress,
        expected_current_sha256=initial.sha256,
    )
    evidence = await fixture.coordinator._create_verified_bundle(
        snapshot_in_progress
    )
    snapshot_verified = snapshot_in_progress.transition(
        JournalState.SNAPSHOT_VERIFIED,
        updated_at=snapshot_in_progress.updated_at + timedelta(microseconds=1),
        safe_boundary=JournalSafeBoundary.SNAPSHOT_VERIFIED_LIVE_UNMODIFIED,
        bundle_manifest_path=evidence.bundle_path,
        bundle_manifest_sha256=evidence.bundle_sha256,
    )
    fixture.coordinator._artifacts.write_journal_transition(
        snapshot_in_progress,
        snapshot_verified,
        expected_current_sha256=snapshot_artifact.sha256,
    )
    restarted, restarted_graph, restarted_transcript = _restarted_coordinator(fixture)

    inspected = await restarted.recover(
        RecoveryRequest(run_id=snapshot_verified.run_id)
    )
    terminalized = await restarted.recover(
        RecoveryRequest(run_id=snapshot_verified.run_id, execute=True)
    )

    assert inspected.status is ResultStatus.RECOVERY_REQUIRED
    assert inspected.errors[0].code is ReorganizationErrorCode.RECOVERY_REQUIRED
    assert terminalized.status is ResultStatus.CANCELLED
    assert await restarted_graph.get_node("baseline-node") is not None
    assert await restarted_transcript.count_entries("session-1") == 1
    retained, _ = restarted._artifacts.read_journal(snapshot_verified.journal_path)
    assert retained.state is JournalState.COMPLETE
    assert (
        retained.safe_boundary
        is JournalSafeBoundary.SNAPSHOT_VERIFIED_LIVE_UNMODIFIED
    )


@pytest.mark.asyncio
async def test_explicit_recovery_drains_pending_runtime_state_before_restore(
    tmp_path: Path,
) -> None:
    fixture = await _production_coordinator(
        tmp_path,
        fault_points={
            CoordinatorFaultPoint.AFTER_MUTATION_STEP,
            CoordinatorFaultPoint.BEFORE_ROLLBACK,
        },
    )
    failed = await fixture.coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.DEDUPE,
            execute=True,
        )
    )
    assert failed.status is ResultStatus.RECOVERY_REQUIRED
    assert failed.run_id is not None

    restarted_graph = ElementXGraphStore(str(fixture.layout.graph_path))
    restarted_memory = MemoryMaintenanceParticipant(
        MemoryMaintenanceLayout(
            vector_directory=fixture.layout.vector_directory,
            graph_path=fixture.layout.graph_path,
            access_buffer_wal_path=fixture.layout.access_buffer_wal_path,
            recovery_directory=fixture.layout.recovery_root,
            log_directory=fixture.layout.log_root,
        ),
        graph_store=restarted_graph,
    )
    events: list[str] = []
    pending_state = ["queued-extraction", "buffered-access"]
    hooks = PendingStateHooks(pending_state, events)
    coordinator = ReorganizationCoordinator(
        layout=fixture.layout,
        gate=MaintenanceAdmissionGate(),
        memory_participant=OrderingMemoryParticipant(
            restarted_memory,
            events,
            pending_state,
        ),
        transcript_participant=fixture.transcript,
        runtime_hooks=hooks,
        lease_registry=DarwinLayoutLeaseRegistry(
            namespace_root=tmp_path / "leases",
            platform_name="Darwin",
            host_id="coordinator-test",
        ),
        application_version="test",
    )

    recovered = await coordinator.recover(
        RecoveryRequest(run_id=failed.run_id, execute=True)
    )

    assert recovered.status is ResultStatus.COMPLETED_WITH_WARNINGS
    assert hooks.calls == ["drain"]
    assert pending_state == []
    assert events.index("runtime_pending_drain") < events.index("memory_restore")


@pytest.mark.asyncio
async def test_execute_refuses_corrupt_live_transcript_before_mutation(
    tmp_path: Path,
) -> None:
    fixture = await _production_coordinator(tmp_path)
    fixture.layout.transcript_database_path.with_name(
        f"{fixture.layout.transcript_database_path.name}-wal"
    ).unlink(missing_ok=True)
    fixture.layout.transcript_database_path.with_name(
        f"{fixture.layout.transcript_database_path.name}-shm"
    ).unlink(missing_ok=True)
    fixture.layout.transcript_database_path.write_bytes(b"not-a-sqlite-database")

    result = await fixture.coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.DEDUPE,
            execute=True,
        )
    )

    assert result.status is ResultStatus.PREFLIGHT_FAILED
    transcript = next(store for store in result.stores if store.store == "transcript")
    assert transcript.status is StoreOperationStatus.FAILED
    assert transcript.capability_state is StoreCapabilityState.CORRUPT
    assert not transcript.verified
    assert not any(call.startswith("execute:") for call in fixture.mutation.calls)
    assert "memory_snapshot" not in fixture.hooks.events
    assert "transcript_snapshot" not in fixture.hooks.events
    assert await fixture.graph.get_node("mutation-node") is None


@pytest.mark.asyncio
async def test_shutdown_orders_drain_finalize_then_snapshot(
    tmp_path: Path,
) -> None:
    fixture = await _production_coordinator(tmp_path)
    coordinator = ReorganizationCoordinator(
        layout=fixture.layout,
        gate=MaintenanceAdmissionGate(),
        memory_participant=OrderingMemoryParticipant(
            fixture.memory,
            fixture.hooks.events,
        ),
        transcript_participant=OrderingTranscriptParticipant(
            fixture.transcript,
            fixture.hooks.events,
        ),
        runtime_hooks=fixture.hooks,
        mutation_adapter=fixture.mutation,
        lease_registry=DarwinLayoutLeaseRegistry(
            namespace_root=tmp_path / "ordered-leases",
            platform_name="Darwin",
            host_id="coordinator-test",
        ),
        application_version="test",
    )

    result = await coordinator.shutdown(
        ReorganizationRequest(
            trigger=OperationTrigger.SHUTDOWN,
            mode=ReorganizationMode.BACKUP,
            execute=True,
        )
    )

    assert result is not None
    assert result.status is ResultStatus.COMPLETED
    assert fixture.hooks.calls == ["shutdown_close", "finalize"]
    assert fixture.hooks.events.index("access_buffer_drain") < (
        fixture.hooks.events.index("memory_snapshot")
    )
    assert fixture.hooks.events.index("transcript_finalize") < (
        fixture.hooks.events.index("transcript_snapshot")
    )
    assert coordinator.gate.snapshot.accepting_shared is False


@pytest.mark.asyncio
@pytest.mark.parametrize("failure_stage", ["close", "finalize"])
async def test_shutdown_failure_still_finalizes_and_refuses_snapshot(
    tmp_path: Path,
    failure_stage: str,
) -> None:
    fixture = await _production_coordinator(tmp_path)
    events: list[str] = []
    hooks = FailingShutdownHooks(failure_stage, events)
    coordinator = ReorganizationCoordinator(
        layout=fixture.layout,
        gate=MaintenanceAdmissionGate(),
        memory_participant=OrderingMemoryParticipant(fixture.memory, events),
        transcript_participant=OrderingTranscriptParticipant(
            fixture.transcript,
            events,
        ),
        runtime_hooks=hooks,
        mutation_adapter=fixture.mutation,
        lease_registry=DarwinLayoutLeaseRegistry(
            namespace_root=tmp_path / "failure-leases",
            platform_name="Darwin",
            host_id="coordinator-test",
        ),
        application_version="test",
    )

    with pytest.raises(DurableArtifactError, match="shutdown quiescence"):
        await coordinator.shutdown(
            ReorganizationRequest(
                trigger=OperationTrigger.SHUTDOWN,
                mode=ReorganizationMode.BACKUP,
                execute=True,
            )
        )

    assert hooks.calls == ["shutdown_close", "finalize"]
    assert events.index("access_buffer_drain") < events.index("transcript_finalize")
    assert "memory_snapshot" not in events
    assert "transcript_snapshot" not in events
    assert coordinator.gate.snapshot.accepting_shared is False
