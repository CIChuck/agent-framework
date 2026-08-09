"""Deterministic provider-matrix and run-scoped mutation adapter tests."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, TypeVar, cast

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
    LiteLlmMaintenanceProvider,
    MaintenanceEmbeddingProvider,
    MaintenanceLlmProvider,
    MaintenanceLlmRole,
    MaintenanceProviderConfig,
    MaintenanceResponseValidationError,
    ProviderProbeResponse,
    StrictProviderModel,
    SynthesisDraft,
    SynthesisResponse,
    VerificationDecision,
    VerificationResponse,
    build_explicit_maintenance_provider_registry,
    build_memory_synthesis_config,
    build_synthesis_guidance,
)
from friday_core.interfaces.llm import ChatCompletionResponse
from friday_memory import (
    MemoryMutationCommand,
    MemoryMutationError,
    MemoryMutationErrorCode,
    MemoryMutationPlan,
    MemoryMutationResult,
    MemoryMutationStep,
    MemoryMutationVerification,
    MemoryVerificationStatus,
    SynthesisCandidateGroup,
    VectorCollectionDimension,
    VectorMemoryRecord,
    VectorMemoryReference,
)

ProviderResponseT = TypeVar("ProviderResponseT", bound=StrictProviderModel)


@dataclass
class DeterministicLlmProvider(MaintenanceLlmProvider):
    role: MaintenanceLlmRole
    fail_probe: bool = False
    invalid_synthesis_sources: bool = False
    empty_synthesis: bool = False
    synthesis_confidence: float = 0.9
    probe_calls: int = 0
    completion_calls: int = 0
    system_prompts: list[str] = field(default_factory=list)
    user_payloads: list[str] = field(default_factory=list)

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
        self.completion_calls += 1
        self.system_prompts.append(system_prompt)
        self.user_payloads.append(user_payload)
        if response_model is ProviderProbeResponse:
            result: StrictProviderModel = ProviderProbeResponse(ready=True)
        elif response_model is SynthesisResponse:
            if self.empty_synthesis:
                return cast(ProviderResponseT, SynthesisResponse(drafts=()))
            source_memory_ids = (
                ("unknown-a", "unknown-b")
                if self.invalid_synthesis_sources
                else ("memory-a", "memory-b")
            )
            result = SynthesisResponse(
                drafts=(
                    SynthesisDraft(
                        collection="primary",
                        source_memory_ids=source_memory_ids,
                        document="Synthetic synthesized memory",
                        confidence=self.synthesis_confidence,
                        reasoning="The supplied records support the synthesis",
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
class RecordingChatService:
    response: ChatCompletionResponse
    messages: list[list[dict[str, Any]]] = field(default_factory=list)

    async def chat_completion(
        self,
        messages: list[dict[str, Any]],
        *,
        temperature: float,
        max_tokens: int,
        timeout: float,
    ) -> ChatCompletionResponse:
        del temperature, max_tokens, timeout
        self.messages.append(messages)
        return self.response


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
    existing_document_hashes: tuple[str, ...] = ()

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
        synthesis_groups = (
            (
                SynthesisCandidateGroup(
                    collection="primary",
                    topic="synthetic",
                    fingerprint="b" * 64,
                    source_memory_ids=("memory-a", "memory-b"),
                ),
            )
            if step is MemoryMutationStep.SYNTHESIZE
            else ()
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
            synthesis_groups=synthesis_groups,
            existing_document_hashes=self.existing_document_hashes,
            all_vector_references=tuple(
                VectorMemoryReference(
                    collection=record.collection,
                    memory_id=record.memory_id,
                )
                for record in provider_records
            ),
            maximum_output_count=(1 if step is MemoryMutationStep.SYNTHESIZE else None),
            minimum_synthesis_confidence=(
                0.65 if step is MemoryMutationStep.SYNTHESIZE else None
            ),
        )

    async def apply(
        self,
        plan: MemoryMutationPlan,
        command: MemoryMutationCommand,
    ) -> MemoryMutationResult:
        self.commands.append(command)
        changed_count = (
            1
            if plan.step in {MemoryMutationStep.DEDUPE, MemoryMutationStep.PRUNE}
            else len(command.vector_additions)
            + len(command.synthesis_metadata_migrations)
            + len(command.verification_updates)
            + len(command.embedding_updates)
            + len(command.graph_embedding_updates)
        )
        return MemoryMutationResult(
            plan_id=plan.plan_id,
            step=plan.step,
            succeeded=True,
            scanned_count=plan.scanned_count,
            changed_count=changed_count,
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
    invalid_synthesis_sources: bool = False,
    empty_synthesis: bool = False,
    synthesis_confidence: float = 0.9,
) -> tuple[
    FrameworkMaintenanceMutationAdapter,
    dict[MaintenanceLlmRole, DeterministicLlmProvider],
    DeterministicEmbeddingProvider,
    RecordingMemoryMutation,
    DeterministicLifecycle,
]:
    llms = {
        role: DeterministicLlmProvider(
            role=role,
            fail_probe=role is fail_role,
            invalid_synthesis_sources=(
                invalid_synthesis_sources
                and role is MaintenanceLlmRole.SYNTHESIZER
            ),
            empty_synthesis=(
                empty_synthesis and role is MaintenanceLlmRole.SYNTHESIZER
            ),
            synthesis_confidence=synthesis_confidence,
        )
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
async def test_litellm_provider_supplies_schema_and_parses_noisy_json() -> None:
    service = RecordingChatService(
        ChatCompletionResponse(
            content=(
                "Structured result follows.\n```json\n"
                '{"drafts":[{"collection":"primary",'
                '"source_memory_ids":["memory-a","memory-b"],'
                '"document":"Synthesized memory",'
                '"confidence":0.9,"reasoning":"Supported synthesis"}]}\n```'
            )
        )
    )
    provider = LiteLlmMaintenanceProvider(
        role=MaintenanceLlmRole.SYNTHESIZER,
        service=service,
        config=MaintenanceProviderConfig(model="test-synthesizer"),
    )

    response = await provider.complete_model(
        SynthesisResponse,
        system_prompt="Create bounded synthesis.",
        user_payload='{"records":[]}',
    )

    assert response.drafts[0].source_memory_ids == ("memory-a", "memory-b")
    system_prompt = service.messages[0][0]["content"]
    assert "JSON Schema" in system_prompt
    assert '"drafts"' in system_prompt
    assert '"additionalProperties":false' in system_prompt


@pytest.mark.asyncio
async def test_litellm_provider_uses_reasoning_json_and_sanitizes_validation() -> None:
    reasoning_service = RecordingChatService(
        ChatCompletionResponse(
            content=None,
            reasoning_content='{"ready":true}',
        )
    )
    provider = LiteLlmMaintenanceProvider(
        role=MaintenanceLlmRole.SYNTHESIZER,
        service=reasoning_service,
        config=MaintenanceProviderConfig(model="test-synthesizer"),
    )

    probe_response = await provider.complete_model(
        ProviderProbeResponse,
        system_prompt="Return readiness.",
        user_payload='{"ready":true}',
    )

    assert probe_response.ready

    invalid_service = RecordingChatService(
        ChatCompletionResponse(
            content=(
                '{"drafts":[{"collection":"primary",'
                '"source_memory_ids":["only-one"],'
                '"document":"secret-provider-content",'
                '"confidence":0.9,"reasoning":"secret-reasoning"}]}'
            )
        )
    )
    invalid_provider = LiteLlmMaintenanceProvider(
        role=MaintenanceLlmRole.SYNTHESIZER,
        service=invalid_service,
        config=MaintenanceProviderConfig(model="test-synthesizer"),
    )

    with pytest.raises(MaintenanceResponseValidationError) as captured:
        await invalid_provider.complete_model(
            SynthesisResponse,
            system_prompt="Create bounded synthesis.",
            user_payload='{"records":[]}',
        )

    assert "secret-provider-content" not in str(captured.value)


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
    synthesis_provider = llms[MaintenanceLlmRole.SYNTHESIZER]
    assert "untrusted data" in synthesis_provider.system_prompts[0]
    synthesis_payload = json.loads(synthesis_provider.user_payloads[0])
    assert synthesis_payload["group"]["topic"] == "synthetic"
    assert {record["memory_id"] for record in synthesis_payload["records"]} == {
        "memory-a",
        "memory-b",
    }

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
@pytest.mark.parametrize(
    ("empty_synthesis", "confidence"),
    ((True, 0.9), (False, 0.5)),
)
async def test_synthesis_can_abstain_without_embedding_or_mutation(
    empty_synthesis: bool,
    confidence: float,
) -> None:
    adapter, _llms, embedding, memory, _lifecycle = _adapter(
        empty_synthesis=empty_synthesis,
        synthesis_confidence=confidence,
    )
    request = ReorganizationRequest(
        mode=ReorganizationMode.SYNTHESIZE,
        trigger=OperationTrigger.MANUAL,
        execute=True,
    )
    adapter.begin_run(request)

    result = await adapter.execute_step(request, MutationStep.SYNTHESIZE)

    adapter.end_run(request)
    assert result.status.value == "completed"
    assert result.changed_count == 0
    assert embedding.embed_calls == []
    assert memory.commands[0].vector_additions == ()


@pytest.mark.asyncio
async def test_synthesis_skips_exact_existing_document_without_embedding() -> None:
    adapter, _llms, embedding, memory, _lifecycle = _adapter()
    normalized = "synthetic synthesized memory"
    memory.existing_document_hashes = (
        hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
    )
    request = ReorganizationRequest(
        mode=ReorganizationMode.SYNTHESIZE,
        trigger=OperationTrigger.MANUAL,
        execute=True,
    )
    adapter.begin_run(request)

    result = await adapter.execute_step(request, MutationStep.SYNTHESIZE)

    adapter.end_run(request)
    assert result.status.value == "completed"
    assert result.changed_count == 0
    assert embedding.embed_calls == []
    assert memory.commands[0].vector_additions == ()


def test_synthesis_configuration_and_semantic_prompt_are_honored() -> None:
    config = FridayChatConfig.model_validate(
        {
            "llm": {},
            "maintenance": {
                "synthesis": {
                    "cluster_min_size": 4,
                    "meta_insight_confidence": 0.83,
                },
                "prompts": {
                    "meta_insight": (
                        "Find a cross-record pattern in {insights}.\n"
                        "Respond with JSON:\n{{\"legacy\": true}}"
                    )
                },
            }
        }
    )

    synthesis_config = build_memory_synthesis_config(config)
    guidance = build_synthesis_guidance(config)

    assert synthesis_config.cluster_min_size == 4
    assert synthesis_config.meta_insight_confidence == 0.83
    assert "supplied JSON memory records" in guidance
    assert "Respond with JSON" not in guidance


def test_synthesis_provider_payload_is_topic_scoped_and_bounded() -> None:
    records = tuple(
        VectorMemoryRecord(
            collection="primary",
            memory_id=f"memory-{index:03d}",
            document="x" * 10_000,
            metadata={
                "type": "insight",
                "topic": "synthetic",
                "verification_status": "verified",
            },
        )
        for index in range(70)
    )
    group = SynthesisCandidateGroup(
        collection="primary",
        topic="synthetic",
        fingerprint="c" * 64,
        source_memory_ids=tuple(record.memory_id for record in records),
    )
    plan = MemoryMutationPlan(
        plan_id="d" * 64,
        step=MemoryMutationStep.SYNTHESIZE,
        candidate_count=len(records),
        provider_records=records,
        synthesis_groups=(group,),
        maximum_output_count=1,
        minimum_synthesis_confidence=0.65,
    )

    payload, visible_source_ids = (
        FrameworkMaintenanceMutationAdapter._synthesis_provider_payload(plan, group)
    )
    decoded = json.loads(payload)

    assert len(payload) <= 120_000
    assert 2 <= len(decoded["records"]) <= 64
    assert all(len(record["document"]) <= 6_000 for record in decoded["records"])
    assert visible_source_ids == {
        record["memory_id"] for record in decoded["records"]
    }


@pytest.mark.asyncio
async def test_synthesis_rejects_sources_outside_plan_before_embedding() -> None:
    adapter, _llms, embedding, memory, _lifecycle = _adapter(
        invalid_synthesis_sources=True
    )
    request = ReorganizationRequest(
        mode=ReorganizationMode.SYNTHESIZE,
        trigger=OperationTrigger.MANUAL,
        execute=True,
    )
    adapter.begin_run(request)

    result = await adapter.execute_step(request, MutationStep.SYNTHESIZE)

    adapter.end_run(request)
    assert result.status.value == "failed"
    assert result.errors[0].message == (
        "maintenance step failed (MaintenanceResponseValidationError)"
    )
    assert embedding.embed_calls == []
    assert memory.commands == []


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
