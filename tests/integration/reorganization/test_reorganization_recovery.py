"""Disposable cross-package rollback-failure and restart recovery drill."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeVar, cast

import chromadb
import pytest
from friday_chat.reorganization.contracts import (
    MutationStepStatus,
    OperationTrigger,
    RecoveryRequest,
    ReorganizationMode,
    ReorganizationRequest,
    ResultStatus,
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
from friday_chat.reorganization.gate import MaintenanceAdmissionGate
from friday_chat.reorganization.layout import FridayChatMaintenanceLayout
from friday_chat.reorganization.lease import DarwinLayoutLeaseRegistry
from friday_chat.reorganization.mutation import (
    ExplicitMaintenanceProviderRegistry,
    FrameworkMaintenanceMutationAdapter,
    LifecycleStepReport,
    MaintenanceEmbeddingProvider,
    MaintenanceLlmProvider,
    MaintenanceLlmRole,
    ProviderProbeResponse,
    StrictProviderModel,
    SynthesisDraft,
    SynthesisResponse,
    VerificationDecision,
    VerificationResponse,
)
from friday_memory import (
    ElementXGraphStore,
    ExplicitMemoryMutationParticipant,
    GraphNode,
    MemoryMaintenanceLayout,
    MemoryMaintenanceParticipant,
    MemoryVerificationStatus,
    ProvenanceMetadata,
    SynthesisConfig,
)
from friday_transcript import (
    SQLiteTranscriptStore,
    TranscriptEntry,
    TranscriptSession,
)

ProviderResponseT = TypeVar("ProviderResponseT", bound=StrictProviderModel)


@dataclass
class DeterministicIntegrationLlm(MaintenanceLlmProvider):
    role: MaintenanceLlmRole
    probe_calls: int = 0
    completion_calls: int = 0

    async def probe(self) -> None:
        self.probe_calls += 1

    async def complete_model(
        self,
        response_model: type[ProviderResponseT],
        *,
        system_prompt: str,
        user_payload: str,
    ) -> ProviderResponseT:
        del system_prompt
        self.completion_calls += 1
        records = json.loads(user_payload)["records"]
        if response_model is ProviderProbeResponse:
            result: StrictProviderModel = ProviderProbeResponse(ready=True)
        elif response_model is SynthesisResponse:
            result = SynthesisResponse(
                drafts=(
                    SynthesisDraft(
                        collection=records[0]["collection"],
                        source_memory_ids=(
                            records[0]["memory_id"],
                            records[1]["memory_id"],
                        ),
                        document="Synthetic provider-composed insight",
                        confidence=0.9,
                        reasoning="The topic records support this synthesis",
                    ),
                )
            )
        elif response_model is VerificationResponse:
            result = VerificationResponse(
                decisions=tuple(
                    VerificationDecision(
                        collection=record["collection"],
                        memory_id=record["memory_id"],
                        status=MemoryVerificationStatus.VERIFIED,
                        confidence=0.9,
                    )
                    for record in records
                )
            )
        else:
            raise TypeError("unsupported deterministic integration response")
        return cast(ProviderResponseT, result)


@dataclass
class DeterministicIntegrationEmbedding(MaintenanceEmbeddingProvider):
    probe_calls: int = 0
    embed_calls: int = 0

    async def probe(self) -> None:
        self.probe_calls += 1

    async def embed_documents(
        self,
        documents: tuple[str, ...],
    ) -> tuple[tuple[float, ...], ...]:
        self.embed_calls += 1
        return tuple((0.25, 0.75) for _document in documents)


@dataclass
class DeterministicIntegrationLifecycle:
    preview_calls: int = 0
    execute_calls: int = 0

    async def preview_reorganization_lifecycle(self) -> LifecycleStepReport:
        self.preview_calls += 1
        return LifecycleStepReport(
            succeeded=True,
            scanned_count=0,
            candidate_count=0,
            changed_count=None,
        )

    async def run_reorganization_lifecycle(self) -> LifecycleStepReport:
        self.execute_calls += 1
        return LifecycleStepReport(
            succeeded=True,
            scanned_count=0,
            candidate_count=0,
            changed_count=0,
        )


@dataclass
class RecoveryHooks:
    calls: list[str] = field(default_factory=list)

    async def prepare_for_manual_maintenance(self) -> None:
        return None

    async def drain_for_manual_maintenance(self) -> ManualMaintenanceDrainResult:
        self.calls.append("drain")
        return ManualMaintenanceDrainResult()

    def resume_after_manual_maintenance(self) -> ManualMaintenanceResumeResult:
        return ManualMaintenanceResumeResult()

    async def close_for_shutdown(self, *, snapshot_requested: bool) -> None:
        del snapshot_requested
        self.calls.append("shutdown_close")

    async def finalize_transcript(self) -> None:
        self.calls.append("finalize")


@dataclass
class GraphMutation:
    graph: ElementXGraphStore

    def begin_run(self, request: ReorganizationRequest) -> None:
        del request

    def end_run(self, request: ReorganizationRequest) -> None:
        del request

    async def preview(
        self,
        request: ReorganizationRequest,
        planned_steps: tuple[MutationStep, ...],
    ) -> tuple[MutationStepResult, ...]:
        del request
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
        del request
        return MutationPreflight(supported=True, planned_steps=planned_steps)

    async def execute_step(
        self,
        request: ReorganizationRequest,
        step: MutationStep,
    ) -> MutationStepResult:
        del request
        if step is MutationStep.DEDUPE:
            await self.graph.add_node(
                GraphNode(
                    id="mutation-node",
                    type="Entity",
                    label="Synthetic mutation",
                    provenance=ProvenanceMetadata(
                        source_id="integration-mutation",
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
        return MutationVerification(verified=True)


def _memory_participant(
    layout: FridayChatMaintenanceLayout,
    graph: ElementXGraphStore,
) -> MemoryMaintenanceParticipant:
    return MemoryMaintenanceParticipant(
        MemoryMaintenanceLayout(
            vector_directory=layout.vector_directory,
            graph_path=layout.graph_path,
            access_buffer_wal_path=None,
            recovery_directory=layout.recovery_root,
            log_directory=layout.log_root,
        ),
        graph_store=graph,
    )


@pytest.mark.asyncio
async def test_full_execute_uses_production_mutation_and_deterministic_providers(
    tmp_path: Path,
) -> None:
    vector_path = tmp_path / "live" / "vector"
    graph_path = tmp_path / "live" / "graph.gpickle"
    transcript_path = tmp_path / "transcript" / "live.sqlite"
    client = chromadb.PersistentClient(path=str(vector_path))
    collection = client.create_collection("integration-full")
    embeddings: list[Sequence[float] | Sequence[int]] = [
        [1.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
    ]
    collection.add(
        ids=["memory-a", "memory-b", "memory-c"],
        documents=[
            "Duplicate synthetic insight",
            "Duplicate synthetic insight",
            "Distinct synthetic insight",
        ],
        metadatas=[
            {
                "type": "insight",
                "topic": "synthetic",
                "verification_status": "verified",
            },
            {
                "type": "insight",
                "topic": "synthetic",
                "verification_status": "verified",
            },
            {
                "type": "insight",
                "topic": "synthetic",
                "verification_status": "verified",
            },
        ],
        embeddings=embeddings,
    )
    graph = ElementXGraphStore(str(graph_path))
    await graph.add_node(
        GraphNode(
            id="baseline-node",
            type="Entity",
            label="Synthetic baseline",
            provenance=ProvenanceMetadata(
                source_id="integration-full-baseline",
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
            user_message="synthetic user",
            assistant_message="synthetic assistant",
        )
    )
    layout = FridayChatMaintenanceLayout.resolve_once(
        captured_process_cwd=tmp_path,
        vector_directory=vector_path,
        graph_path=graph_path,
        access_buffer_wal_path=None,
        transcript_database_path=transcript_path,
        recovery_root=tmp_path / "recovery",
        log_root=tmp_path / "logs",
    )
    memory_layout = MemoryMaintenanceLayout(
        vector_directory=layout.vector_directory,
        graph_path=layout.graph_path,
        access_buffer_wal_path=None,
        recovery_directory=layout.recovery_root,
        log_directory=layout.log_root,
    )
    providers = {
        role: DeterministicIntegrationLlm(role=role)
        for role in MaintenanceLlmRole
    }
    embedding = DeterministicIntegrationEmbedding()
    lifecycle = DeterministicIntegrationLifecycle()
    mutation = FrameworkMaintenanceMutationAdapter(
        memory=ExplicitMemoryMutationParticipant(
            memory_layout,
            graph_store=graph,
            synthesis_config=SynthesisConfig(cluster_min_size=2),
        ),
        providers=ExplicitMaintenanceProviderRegistry(
            llms=providers,
            embedding=embedding,
        ),
        lifecycle=lifecycle,
    )
    coordinator = ReorganizationCoordinator(
        layout=layout,
        gate=MaintenanceAdmissionGate(),
        memory_participant=MemoryMaintenanceParticipant(
            memory_layout,
            graph_store=graph,
        ),
        transcript_participant=transcript,
        runtime_hooks=RecoveryHooks(),
        mutation_adapter=mutation,
        lease_registry=DarwinLayoutLeaseRegistry(
            namespace_root=tmp_path / "leases",
            platform_name="Darwin",
            host_id="integration-full",
        ),
        application_version="integration-test",
    )

    result = await coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.FULL,
            execute=True,
        )
    )

    assert result.status is ResultStatus.COMPLETED
    assert [step.step for step in result.mutation_steps] == [
        MutationStep.DEDUPE,
        MutationStep.PRUNE,
        MutationStep.SYNTHESIZE,
        MutationStep.VERIFY,
        MutationStep.LIFECYCLE,
    ]
    assert all(
        step.status is MutationStepStatus.COMPLETED
        for step in result.mutation_steps
    )
    assert result.recovery_manifest_path is not None
    assert result.recovery_manifest_path.is_file()
    assert result.journal_path is not None and result.journal_path.is_file()
    assert result.reorganization_log_path is not None
    assert result.reorganization_log_path.is_file()
    live = collection.get(include=["documents", "metadatas"])
    assert "memory-b" not in live["ids"]
    assert len(live["ids"]) == 3
    assert any(memory_id.startswith("reorg-") for memory_id in live["ids"])
    assert all(
        metadata is not None
        and metadata.get("verification_status") == "verified"
        for metadata in live["metadatas"] or []
    )
    assert await transcript.count_entries("session-1") == 1
    assert providers[MaintenanceLlmRole.SYNTHESIZER].completion_calls == 1
    assert all(
        providers[role].completion_calls == 1
        for role in (
            MaintenanceLlmRole.CLASSIFIER,
            MaintenanceLlmRole.RESEARCHER,
            MaintenanceLlmRole.JUDGE,
        )
    )
    assert embedding.probe_calls == 1
    assert embedding.embed_calls == 1
    assert lifecycle.execute_calls == 1

    vector_count_after_first_run = collection.count()
    repeated = await coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.FULL,
            execute=True,
        )
    )

    assert repeated.status is ResultStatus.COMPLETED
    repeated_synthesis = next(
        step
        for step in repeated.mutation_steps
        if step.step is MutationStep.SYNTHESIZE
    )
    assert repeated_synthesis.changed_count == 0
    assert collection.count() == vector_count_after_first_run
    assert providers[MaintenanceLlmRole.SYNTHESIZER].completion_calls == 1
    assert embedding.embed_calls == 1


@pytest.mark.asyncio
async def test_disposable_restart_recovers_exact_cross_package_bundle(
    tmp_path: Path,
) -> None:
    vector_path = tmp_path / "live" / "vector"
    graph_path = tmp_path / "live" / "graph.gpickle"
    transcript_path = tmp_path / "transcript" / "live.sqlite"
    client = chromadb.PersistentClient(path=str(vector_path))
    collection = client.create_collection("integration-recovery")
    embeddings: list[Sequence[float] | Sequence[int]] = [[1.0, 0.0]]
    collection.add(
        ids=["memory-1"],
        documents=["synthetic memory"],
        embeddings=embeddings,
    )
    graph = ElementXGraphStore(str(graph_path))
    await graph.add_node(
        GraphNode(
            id="baseline-node",
            type="Entity",
            label="Synthetic baseline",
            provenance=ProvenanceMetadata(
                source_id="integration-baseline",
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
            user_message="synthetic user",
            assistant_message="synthetic assistant",
        )
    )
    layout = FridayChatMaintenanceLayout.resolve_once(
        captured_process_cwd=tmp_path,
        vector_directory=vector_path,
        graph_path=graph_path,
        access_buffer_wal_path=None,
        transcript_database_path=transcript_path,
        recovery_root=tmp_path / "recovery",
        log_root=tmp_path / "logs",
    )
    lease_root = tmp_path / "leases"

    async def fail_rollback(
        point: CoordinatorFaultPoint,
        step: MutationStep | None,
    ) -> None:
        del step
        if point in {
            CoordinatorFaultPoint.AFTER_MUTATION_STEP,
            CoordinatorFaultPoint.BEFORE_ROLLBACK,
        }:
            raise RuntimeError("synthetic recovery drill fault")

    coordinator = ReorganizationCoordinator(
        layout=layout,
        gate=MaintenanceAdmissionGate(),
        memory_participant=_memory_participant(layout, graph),
        transcript_participant=transcript,
        runtime_hooks=RecoveryHooks(),
        mutation_adapter=GraphMutation(graph),
        lease_registry=DarwinLayoutLeaseRegistry(
            namespace_root=lease_root,
            platform_name="Darwin",
            host_id="integration-recovery",
        ),
        application_version="integration-test",
        fault_injector=fail_rollback,
    )
    failed = await coordinator.run(
        ReorganizationRequest(
            trigger=OperationTrigger.MANUAL,
            mode=ReorganizationMode.DEDUPE,
            execute=True,
        )
    )

    assert failed.status is ResultStatus.RECOVERY_REQUIRED
    assert failed.run_id is not None
    assert await graph.get_node("mutation-node") is not None

    restarted_graph = ElementXGraphStore(str(graph_path))
    restarted_transcript = SQLiteTranscriptStore(transcript_path)
    recovery_hooks = RecoveryHooks()
    restarted = ReorganizationCoordinator(
        layout=layout,
        gate=MaintenanceAdmissionGate(),
        memory_participant=_memory_participant(layout, restarted_graph),
        transcript_participant=restarted_transcript,
        runtime_hooks=recovery_hooks,
        lease_registry=DarwinLayoutLeaseRegistry(
            namespace_root=lease_root,
            platform_name="Darwin",
            host_id="integration-recovery",
        ),
        application_version="integration-test",
    )

    inspected = await restarted.recover(RecoveryRequest(run_id=failed.run_id))
    recovered = await restarted.recover(
        RecoveryRequest(run_id=failed.run_id, execute=True)
    )

    assert inspected.status is ResultStatus.RECOVERY_REQUIRED
    assert recovered.status is ResultStatus.COMPLETED_WITH_WARNINGS
    assert recovered.recovery_manifest_path == failed.recovery_manifest_path
    assert await restarted_graph.get_node("mutation-node") is None
    assert await restarted_graph.get_node("baseline-node") is not None
    assert await restarted_transcript.count_entries("session-1") == 1
    assert recovery_hooks.calls == ["drain"]
    assert restarted.startup_recovery_warnings() == ()
