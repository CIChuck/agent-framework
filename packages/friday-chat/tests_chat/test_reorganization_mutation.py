"""Deterministic provider-matrix and run-scoped mutation adapter tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeVar, cast

import pytest
from friday_chat.config import FridayChatConfig
from friday_chat.reorganization.contracts import (
    MutationStep,
    OperationTrigger,
    ReorganizationMode,
    ReorganizationRequest,
)
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
    build_explicit_maintenance_provider_registry,
)
from friday_memory import (
    MemoryMutationCommand,
    MemoryMutationError,
    MemoryMutationErrorCode,
    MemoryMutationPlan,
    MemoryMutationResult,
    MemoryMutationStep,
    MemoryMutationVerification,
    MemoryVerificationStatus,
    VectorCollectionDimension,
    VectorMemoryRecord,
    VectorMemoryReference,
)

ProviderResponseT = TypeVar("ProviderResponseT", bound=StrictProviderModel)


@dataclass
class DeterministicLlmProvider(MaintenanceLlmProvider):
    role: MaintenanceLlmRole
    fail_probe: bool = False
    probe_calls: int = 0
    completion_calls: int = 0

    async def probe(self) -> None:
        self.probe_calls += 1
        if self.fail_probe:
            raise RuntimeError("secret-provider-response")

    async def complete_model(
        self,
        response_model: type[ProviderResponseT],
        *,
        system_prompt: str,
        user_payload: str,
    ) -> ProviderResponseT:
        del system_prompt, user_payload
        self.completion_calls += 1
        if response_model is ProviderProbeResponse:
            result: StrictProviderModel = ProviderProbeResponse(ready=True)
        elif response_model is SynthesisResponse:
            result = SynthesisResponse(
                drafts=(
                    SynthesisDraft(
                        collection="primary",
                        source_memory_ids=("memory-a", "memory-b"),
                        document="Synthetic synthesized memory",
                    ),
                )
            )
        elif response_model is VerificationResponse:
            result = VerificationResponse(
                decisions=(
                    VerificationDecision(
                        collection="primary",
                        memory_id="memory-a",
                        status=MemoryVerificationStatus.VERIFIED,
                        confidence=0.9,
                    ),
                    VerificationDecision(
                        collection="primary",
                        memory_id="memory-b",
                        status=MemoryVerificationStatus.UNCERTAIN,
                        confidence=0.6,
                    ),
                )
            )
        else:
            raise TypeError("unsupported deterministic response model")
        return cast(ProviderResponseT, result)


@dataclass
class DeterministicEmbeddingProvider(MaintenanceEmbeddingProvider):
    fail_probe: bool = False
    probe_calls: int = 0
    embed_calls: list[tuple[str, ...]] = field(default_factory=list)

    async def probe(self) -> None:
        self.probe_calls += 1
        if self.fail_probe:
            raise TimeoutError("secret-embedding-response")

    async def embed_documents(
        self,
        documents: tuple[str, ...],
    ) -> tuple[tuple[float, ...], ...]:
        self.embed_calls.append(documents)
        return tuple((0.25, 0.75) for _ in documents)


@dataclass
class RecordingMemoryMutation:
    plans: list[MemoryMutationStep] = field(default_factory=list)
    commands: list[MemoryMutationCommand] = field(default_factory=list)
    verification_command_counts: list[int] = field(default_factory=list)

    async def plan(self, step: MemoryMutationStep) -> MemoryMutationPlan:
        self.plans.append(step)
        provider_records = (
            (
                VectorMemoryRecord(
                    collection="primary",
                    memory_id="memory-a",
                    document="Synthetic memory A",
                    metadata={"type": "insight", "topic": "synthetic"},
                ),
                VectorMemoryRecord(
                    collection="primary",
                    memory_id="memory-b",
                    document="Synthetic memory B",
                    metadata={"type": "insight", "topic": "synthetic"},
                ),
            )
            if step
            in {
                MemoryMutationStep.SYNTHESIZE,
                MemoryMutationStep.VERIFY,
                MemoryMutationStep.REEMBED,
            }
            else ()
        )
        candidate_count = (
            1
            if step
            in {
                MemoryMutationStep.DEDUPE,
                MemoryMutationStep.PRUNE,
            }
            else len(provider_records)
        )
        return MemoryMutationPlan(
            plan_id=("a" * 64),
            step=step,
            scanned_count=2,
            candidate_count=candidate_count,
            vector_collection_count=1,
            vector_collection_dimensions=(
                VectorCollectionDimension(collection="primary", dimension=2),
            ),
            provider_records=provider_records,
            all_vector_references=tuple(
                VectorMemoryReference(
                    collection=record.collection,
                    memory_id=record.memory_id,
                )
                for record in provider_records
            ),
            maximum_output_count=(1 if step is MemoryMutationStep.SYNTHESIZE else None),
        )

    async def apply(
        self,
        plan: MemoryMutationPlan,
        command: MemoryMutationCommand,
    ) -> MemoryMutationResult:
        self.commands.append(command)
        return MemoryMutationResult(
            plan_id=plan.plan_id,
            step=plan.step,
            succeeded=True,
            scanned_count=plan.scanned_count,
            changed_count=(
                len(command.vector_additions)
                or len(command.verification_updates)
                or len(command.embedding_updates)
                or 1
            ),
        )

    async def verify_postconditions(
        self,
        commands: tuple[MemoryMutationCommand, ...],
    ) -> MemoryMutationVerification:
        self.verification_command_counts.append(len(commands))
        return MemoryMutationVerification(
            verified=True,
            vector_collection_count=1,
            vector_record_count=2,
            graph_node_count=0,
            graph_edge_count=0,
        )


@dataclass
class DeterministicLifecycle:
    preview_calls: int = 0
    execute_calls: int = 0

    async def preview_reorganization_lifecycle(self) -> LifecycleStepReport:
        self.preview_calls += 1
        return LifecycleStepReport(
            succeeded=True,
            scanned_count=2,
            candidate_count=None,
            changed_count=None,
        )

    async def run_reorganization_lifecycle(self) -> LifecycleStepReport:
        self.execute_calls += 1
        return LifecycleStepReport(
            succeeded=True,
            scanned_count=2,
            candidate_count=None,
            changed_count=1,
        )


def _adapter(
    *,
    fail_role: MaintenanceLlmRole | None = None,
    fail_embedding: bool = False,
) -> tuple[
    FrameworkMaintenanceMutationAdapter,
    dict[MaintenanceLlmRole, DeterministicLlmProvider],
    DeterministicEmbeddingProvider,
    RecordingMemoryMutation,
    DeterministicLifecycle,
]:
    llms = {
        role: DeterministicLlmProvider(role=role, fail_probe=role is fail_role)
        for role in MaintenanceLlmRole
    }
    embedding = DeterministicEmbeddingProvider(fail_probe=fail_embedding)
    memory = RecordingMemoryMutation()
    lifecycle = DeterministicLifecycle()
    adapter = FrameworkMaintenanceMutationAdapter(
        memory=memory,
        providers=ExplicitMaintenanceProviderRegistry(
            llms=llms,
            embedding=embedding,
        ),
        lifecycle=lifecycle,
    )
    return adapter, llms, embedding, memory, lifecycle


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("steps", "expected_roles", "embedding_calls"),
    [
        ((MutationStep.ANALYZE,), (), 0),
        ((MutationStep.DEDUPE,), (), 0),
        ((MutationStep.PRUNE,), (), 0),
        (
            (MutationStep.SYNTHESIZE,),
            (MaintenanceLlmRole.SYNTHESIZER,),
            1,
        ),
        (
            (MutationStep.VERIFY,),
            (
                MaintenanceLlmRole.CLASSIFIER,
                MaintenanceLlmRole.RESEARCHER,
                MaintenanceLlmRole.JUDGE,
            ),
            0,
        ),
        (
            (MutationStep.DEDUPE, MutationStep.PRUNE, MutationStep.LIFECYCLE),
            (),
            0,
        ),
        ((MutationStep.REEMBED,), (), 1),
    ],
)
async def test_preflight_probes_only_selected_mode_capabilities(
    steps: tuple[MutationStep, ...],
    expected_roles: tuple[MaintenanceLlmRole, ...],
    embedding_calls: int,
) -> None:
    adapter, llms, embedding, _memory, _lifecycle = _adapter()
    request = ReorganizationRequest(
        mode=ReorganizationMode.FULL,
        trigger=OperationTrigger.MANUAL,
    )

    result = await adapter.preflight(request, steps)

    assert result.supported
    assert tuple(role for role, provider in llms.items() if provider.probe_calls) == (
        expected_roles
    )
    assert embedding.probe_calls == embedding_calls


@pytest.mark.asyncio
async def test_provider_failures_are_sanitized_and_fail_before_mutation() -> None:
    adapter, _llms, _embedding, memory, _lifecycle = _adapter(
        fail_role=MaintenanceLlmRole.JUDGE
    )
    request = ReorganizationRequest(
        mode=ReorganizationMode.VERIFY,
        trigger=OperationTrigger.MANUAL,
    )

    result = await adapter.preflight(request, (MutationStep.VERIFY,))

    assert not result.supported
    assert memory.commands == []
    rendered = " ".join(error.message for error in result.errors)
    assert "secret-provider-response" not in rendered
    assert "RuntimeError" in rendered


@pytest.mark.asyncio
async def test_missing_selected_providers_fail_preflight_without_mutation() -> None:
    memory = RecordingMemoryMutation()
    adapter = FrameworkMaintenanceMutationAdapter(
        memory=memory,
        providers=ExplicitMaintenanceProviderRegistry(llms={}, embedding=None),
        lifecycle=DeterministicLifecycle(),
    )
    request = ReorganizationRequest(
        mode=ReorganizationMode.SYNTHESIZE,
        trigger=OperationTrigger.MANUAL,
    )

    result = await adapter.preflight(request, (MutationStep.SYNTHESIZE,))

    assert not result.supported
    assert len(result.errors) == 2
    assert all(error.code.value == "capability_unavailable" for error in result.errors)
    assert memory.commands == []


@pytest.mark.asyncio
async def test_embedding_timeout_is_sanitized_before_mutation() -> None:
    adapter, _llms, _embedding, memory, _lifecycle = _adapter(
        fail_embedding=True
    )
    request = ReorganizationRequest(
        mode=ReorganizationMode.SYNTHESIZE,
        trigger=OperationTrigger.MANUAL,
    )

    result = await adapter.preflight(request, (MutationStep.SYNTHESIZE,))

    assert not result.supported
    assert memory.commands == []
    rendered = " ".join(error.message for error in result.errors)
    assert "secret-embedding-response" not in rendered
    assert "TimeoutError" in rendered


@pytest.mark.asyncio
async def test_synthesis_and_verification_dispatch_typed_provider_outputs() -> None:
    adapter, llms, embedding, memory, _lifecycle = _adapter()
    synthesis = ReorganizationRequest(
        mode=ReorganizationMode.SYNTHESIZE,
        trigger=OperationTrigger.MANUAL,
        execute=True,
    )
    adapter.begin_run(synthesis)
    synthesis_result = await adapter.execute_step(synthesis, MutationStep.SYNTHESIZE)
    synthesis_verification = await adapter.verify_postconditions(synthesis)
    adapter.end_run(synthesis)

    assert synthesis_result.changed_count == 1
    assert synthesis_verification.verified
    assert llms[MaintenanceLlmRole.SYNTHESIZER].completion_calls == 1
    assert embedding.embed_calls == [("Synthetic synthesized memory",)]
    assert len(memory.commands[0].vector_additions) == 1

    verification = ReorganizationRequest(
        mode=ReorganizationMode.VERIFY,
        trigger=OperationTrigger.MANUAL,
        execute=True,
    )
    adapter.begin_run(verification)
    verification_result = await adapter.execute_step(verification, MutationStep.VERIFY)
    await adapter.verify_postconditions(verification)
    adapter.end_run(verification)

    assert verification_result.changed_count == 2
    assert all(
        llms[role].completion_calls == 1
        for role in (
            MaintenanceLlmRole.CLASSIFIER,
            MaintenanceLlmRole.RESEARCHER,
            MaintenanceLlmRole.JUDGE,
        )
    )
    assert len(memory.commands[1].verification_updates) == 2


@pytest.mark.asyncio
async def test_command_receipts_are_cleared_between_execute_runs() -> None:
    adapter, _llms, _embedding, memory, _lifecycle = _adapter()
    request = ReorganizationRequest(
        mode=ReorganizationMode.DEDUPE,
        trigger=OperationTrigger.MANUAL,
        execute=True,
    )

    for _ in range(2):
        adapter.begin_run(request)
        await adapter.execute_step(request, MutationStep.DEDUPE)
        await adapter.verify_postconditions(request)
        adapter.end_run(request)

    assert memory.verification_command_counts == [1, 1]


def test_registry_never_inherits_primary_chat_or_embedding_provider() -> None:
    primary_only = FridayChatConfig.model_validate(
        {
            "llm": {
                "model": "primary-chat-model",
                "api_base": "https://primary.invalid/v1",
                "api_key": "primary-secret",
            },
            "embedding": {"model": "primary-embedding-model"},
        }
    )
    registry = build_explicit_maintenance_provider_registry(primary_only)

    assert registry.llms == {}
    assert registry.embedding is None

    unresolved = FridayChatConfig.model_validate(
        {
            "llm": {"model": "primary-chat-model"},
            "maintenance": {
                "llm": {"synthesizer": {"model": "${UNRESOLVED_MAINTENANCE_MODEL}"}}
            },
        }
    )
    unresolved_registry = build_explicit_maintenance_provider_registry(unresolved)
    assert MaintenanceLlmRole.SYNTHESIZER not in unresolved_registry.llms
    assert "synthesizer" in unresolved_registry.configuration_errors


def test_failed_memory_results_retain_typed_errors_without_zero_fabrication() -> None:
    error = MemoryMutationError(
        code=MemoryMutationErrorCode.APPLY_FAILED,
        message="synthetic safe failure",
    )
    result = MemoryMutationResult(
        plan_id="f" * 64,
        step=MemoryMutationStep.DEDUPE,
        succeeded=False,
        scanned_count=None,
        changed_count=None,
        errors=(error,),
    )
    assert result.scanned_count is None
    assert result.changed_count is None
