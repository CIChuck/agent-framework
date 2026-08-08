"""Explicit maintenance-provider and Friday Memory mutation composition."""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, TypeVar, cast

from friday_core.interfaces.llm import ChatCompletionResponse
from friday_llm import LiteLLMEmbeddingService, LiteLLMService, ResilienceConfig
from friday_memory import (
    GraphEmbeddingUpdate,
    MemoryEmbeddingUpdate,
    MemoryMutationCommand,
    MemoryMutationParticipant,
    MemoryMutationPlan,
    MemoryMutationStep,
    MemoryVectorAddition,
    MemoryVerificationStatus,
    MemoryVerificationUpdate,
)
from pydantic import BaseModel, ConfigDict, Field, model_validator

from friday_chat.config import FridayChatConfig
from friday_chat.reorganization.contracts import (
    MutationStep,
    MutationStepResult,
    MutationStepStatus,
    ReorganizationError,
    ReorganizationErrorCode,
    ReorganizationRequest,
)
from friday_chat.reorganization.coordinator import (
    MaintenanceMutationAdapter,
    MutationPreflight,
    MutationVerification,
)


class StrictProviderModel(BaseModel):
    """Reject coercion and unknown fields at provider boundaries."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class MaintenanceLlmRole(str, Enum):
    """Explicit provider roles used by the selected pipeline."""

    SYNTHESIZER = "synthesizer"
    CLASSIFIER = "classifier"
    RESEARCHER = "researcher"
    JUDGE = "judge"


class MaintenanceProviderConfig(StrictProviderModel):
    """Explicit provider configuration with no primary-provider fallback."""

    model: str = Field(min_length=1, max_length=256)
    api_base: str | None = Field(default=None, min_length=1, max_length=2048)
    api_key: str | None = Field(default=None, min_length=1, max_length=4096)
    timeout_seconds: float = Field(default=30.0, gt=0.0, le=600.0)
    max_retries: int = Field(default=0, ge=0, le=10)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)

    @model_validator(mode="after")
    def reject_unresolved_values(self) -> MaintenanceProviderConfig:
        for value in (self.model, self.api_base, self.api_key):
            if value is not None and ("${" in value or "{{" in value):
                raise ValueError("maintenance provider configuration is unresolved")
        return self


class ProviderProbeResponse(StrictProviderModel):
    """Minimal provider-readiness response."""

    ready: bool


class SynthesisDraft(StrictProviderModel):
    """LLM-produced text before explicit maintenance embedding."""

    collection: str = Field(min_length=1, max_length=512)
    source_memory_ids: tuple[str, ...] = Field(min_length=2, max_length=256)
    document: str = Field(min_length=1, max_length=32_000)


class SynthesisResponse(StrictProviderModel):
    """Bounded synthesis provider response."""

    drafts: tuple[SynthesisDraft, ...] = Field(max_length=128)


class VerificationDecision(StrictProviderModel):
    """One provider verdict bound to one collection record."""

    collection: str = Field(min_length=1, max_length=512)
    memory_id: str = Field(min_length=1, max_length=1024)
    status: MemoryVerificationStatus
    confidence: float = Field(ge=0.0, le=1.0)


class VerificationResponse(StrictProviderModel):
    """Bounded verification provider response."""

    decisions: tuple[VerificationDecision, ...] = Field(max_length=512)


class LifecycleStepReport(StrictProviderModel):
    """Honest deterministic lifecycle result without embedding backfill."""

    succeeded: bool
    scanned_count: int | None = Field(default=None, ge=0)
    candidate_count: int | None = Field(default=None, ge=0)
    changed_count: int | None = Field(default=None, ge=0)
    warnings: tuple[str, ...] = ()
    errors: tuple[ReorganizationError, ...] = ()

    @model_validator(mode="after")
    def validate_outcome(self) -> LifecycleStepReport:
        if self.succeeded and self.errors:
            raise ValueError("successful lifecycle report cannot contain errors")
        if not self.succeeded and not self.errors:
            raise ValueError("failed lifecycle report requires typed errors")
        return self


ProviderResponseT = TypeVar("ProviderResponseT", bound=StrictProviderModel)


class MaintenanceLlmProvider(Protocol):
    """Narrow deterministic/testable maintenance LLM boundary."""

    role: MaintenanceLlmRole

    async def probe(self) -> None: ...

    async def complete_model(
        self,
        response_model: type[ProviderResponseT],
        *,
        system_prompt: str,
        user_payload: str,
    ) -> ProviderResponseT: ...


class MaintenanceEmbeddingProvider(Protocol):
    """Narrow explicit maintenance embedding boundary."""

    async def probe(self) -> None: ...

    async def embed_documents(
        self, documents: tuple[str, ...]
    ) -> tuple[tuple[float, ...], ...]: ...


class LifecycleMaintenanceRunner(Protocol):
    """Promotion/decay lifecycle only; no edge-embedding backfill."""

    async def preview_reorganization_lifecycle(self) -> LifecycleStepReport: ...

    async def run_reorganization_lifecycle(self) -> LifecycleStepReport: ...


@dataclass(frozen=True)
class ExplicitMaintenanceProviderRegistry:
    """Only explicitly configured maintenance providers and their safe errors."""

    llms: Mapping[MaintenanceLlmRole, MaintenanceLlmProvider]
    embedding: MaintenanceEmbeddingProvider | None
    configuration_errors: Mapping[str, str] = field(default_factory=dict)


@dataclass
class LiteLlmMaintenanceProvider:
    """Production provider constructed only from explicit maintenance config."""

    role: MaintenanceLlmRole
    service: LiteLLMService
    config: MaintenanceProviderConfig

    async def probe(self) -> None:
        response = await self.complete_model(
            ProviderProbeResponse,
            system_prompt="Return the requested readiness JSON only.",
            user_payload='{"ready":true}',
        )
        if not response.ready:
            raise RuntimeError("maintenance provider readiness was not confirmed")

    async def complete_model(
        self,
        response_model: type[ProviderResponseT],
        *,
        system_prompt: str,
        user_payload: str,
    ) -> ProviderResponseT:
        response: ChatCompletionResponse = await self.service.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_payload},
            ],
            temperature=self.config.temperature,
            max_tokens=8_000,
            timeout=self.config.timeout_seconds,
        )
        if response.content is None:
            raise ValueError("maintenance provider returned no structured content")
        raw = re.sub(r"^```(?:json)?\s*\n?", "", response.content.strip())
        raw = re.sub(r"\n?```\s*$", "", raw)
        return response_model.model_validate_json(raw)


@dataclass
class LiteLlmMaintenanceEmbeddingProvider:
    """Production embedding provider from maintenance.embedding only."""

    service: LiteLLMEmbeddingService
    config: MaintenanceProviderConfig

    async def probe(self) -> None:
        embeddings = await self.embed_documents(("maintenance readiness probe",))
        if len(embeddings) != 1:
            raise RuntimeError("maintenance embedding readiness was not confirmed")

    async def embed_documents(
        self,
        documents: tuple[str, ...],
    ) -> tuple[tuple[float, ...], ...]:
        vectors = await self.service.embed_documents(
            list(documents), timeout=self.config.timeout_seconds
        )
        result = tuple(tuple(float(value) for value in vector) for vector in vectors)
        if len(result) != len(documents) or any(
            not vector or not all(math.isfinite(value) for value in vector)
            for vector in result
        ):
            raise ValueError("maintenance embedding response is invalid")
        return result


def _provider_config(
    raw: object,
) -> MaintenanceProviderConfig:
    if not isinstance(raw, Mapping):
        raise ValueError("maintenance provider configuration must be a mapping")
    return MaintenanceProviderConfig.model_validate(dict(raw))


def build_explicit_maintenance_provider_registry(
    config: FridayChatConfig,
) -> ExplicitMaintenanceProviderRegistry:
    """Build providers without consulting primary chat or embedding config."""
    llms: dict[MaintenanceLlmRole, MaintenanceLlmProvider] = {}
    errors: dict[str, str] = {}
    for role in MaintenanceLlmRole:
        raw = config.maintenance.llm.get(role.value)
        if raw is None:
            continue
        try:
            provider_config = _provider_config(raw)
            llms[role] = LiteLlmMaintenanceProvider(
                role=role,
                service=LiteLLMService(
                    model_name=provider_config.model,
                    api_key=provider_config.api_key,
                    api_base=provider_config.api_base,
                    resilience=ResilienceConfig(
                        max_retries=provider_config.max_retries,
                        timeout_seconds=provider_config.timeout_seconds,
                    ),
                ),
                config=provider_config,
            )
        except (TypeError, ValueError) as exc:
            errors[role.value] = (
                f"maintenance provider configuration is invalid ({type(exc).__name__})"
            )
    embedding: MaintenanceEmbeddingProvider | None = None
    if config.maintenance.embedding is not None:
        try:
            embedding_config = _provider_config(config.maintenance.embedding)
            embedding = LiteLlmMaintenanceEmbeddingProvider(
                service=LiteLLMEmbeddingService(
                    model_name=embedding_config.model,
                    api_key=embedding_config.api_key,
                    api_base=embedding_config.api_base,
                    resilience=ResilienceConfig(
                        max_retries=embedding_config.max_retries,
                        timeout_seconds=embedding_config.timeout_seconds,
                    ),
                ),
                config=embedding_config,
            )
        except (TypeError, ValueError) as exc:
            errors["embedding"] = (
                f"maintenance embedding configuration is invalid ({type(exc).__name__})"
            )
    return ExplicitMaintenanceProviderRegistry(
        llms=llms,
        embedding=embedding,
        configuration_errors=errors,
    )


_MEMORY_STEP_BY_CHAT_STEP = {
    MutationStep.ANALYZE: MemoryMutationStep.ANALYZE,
    MutationStep.REEMBED: MemoryMutationStep.REEMBED,
    MutationStep.DEDUPE: MemoryMutationStep.DEDUPE,
    MutationStep.PRUNE: MemoryMutationStep.PRUNE,
    MutationStep.SYNTHESIZE: MemoryMutationStep.SYNTHESIZE,
    MutationStep.VERIFY: MemoryMutationStep.VERIFY,
}

_MAX_PROVIDER_RECORDS = 512


@dataclass
class FrameworkMaintenanceMutationAdapter(MaintenanceMutationAdapter):
    """Production composition over explicit Memory and provider contracts."""

    memory: MemoryMutationParticipant
    providers: ExplicitMaintenanceProviderRegistry
    lifecycle: LifecycleMaintenanceRunner | None
    _commands: list[MemoryMutationCommand] = field(default_factory=list)
    _active_request: ReorganizationRequest | None = None

    def begin_run(self, request: ReorganizationRequest) -> None:
        """Create empty command-receipt state for exactly one execute run."""
        if self._active_request is not None:
            raise RuntimeError("maintenance mutation adapter run is already active")
        self._commands.clear()
        self._active_request = request

    def end_run(self, request: ReorganizationRequest) -> None:
        """Clear all command receipts on every coordinator terminal path."""
        if self._active_request != request:
            raise RuntimeError("maintenance mutation adapter run identity differs")
        self._commands.clear()
        self._active_request = None

    def _require_active_run(self, request: ReorganizationRequest) -> None:
        if self._active_request is None or self._active_request != request:
            raise RuntimeError("maintenance mutation adapter run is not active")

    @staticmethod
    def _error(
        code: ReorganizationErrorCode,
        message: str,
        *,
        store: str | None = None,
    ) -> ReorganizationError:
        return ReorganizationError(code=code, message=message, store=store)

    @classmethod
    def _plan_result(
        cls,
        step: MutationStep,
        plan: MemoryMutationPlan,
    ) -> MutationStepResult:
        errors = tuple(
            cls._error(
                ReorganizationErrorCode.PREFLIGHT_FAILED,
                error.message,
                store=error.store or "memory",
            )
            for error in plan.errors
        )
        return MutationStepResult(
            step=step,
            status=(
                MutationStepStatus.FAILED if errors else MutationStepStatus.PREVIEWED
            ),
            scanned_count=plan.scanned_count,
            candidate_count=plan.candidate_count,
            warnings=plan.warnings,
            errors=errors,
        )

    async def preview(
        self,
        request: ReorganizationRequest,
        planned_steps: tuple[MutationStep, ...],
    ) -> tuple[MutationStepResult, ...]:
        del request
        results: list[MutationStepResult] = []
        for step in planned_steps:
            if step is MutationStep.LIFECYCLE:
                if self.lifecycle is None:
                    results.append(
                        MutationStepResult(
                            step=step,
                            status=MutationStepStatus.FAILED,
                            errors=(
                                self._error(
                                    ReorganizationErrorCode.CAPABILITY_UNAVAILABLE,
                                    "deterministic lifecycle maintenance is unavailable",
                                ),
                            ),
                        )
                    )
                else:
                    report = await self.lifecycle.preview_reorganization_lifecycle()
                    results.append(self._lifecycle_result(report, preview=True))
                continue
            plan = await self.memory.plan(_MEMORY_STEP_BY_CHAT_STEP[step])
            results.append(self._plan_result(step, plan))
        return tuple(results)

    @staticmethod
    def _required_roles(
        planned_steps: tuple[MutationStep, ...],
    ) -> tuple[MaintenanceLlmRole, ...]:
        roles: list[MaintenanceLlmRole] = []
        if MutationStep.SYNTHESIZE in planned_steps:
            roles.append(MaintenanceLlmRole.SYNTHESIZER)
        if MutationStep.VERIFY in planned_steps:
            roles.extend(
                (
                    MaintenanceLlmRole.CLASSIFIER,
                    MaintenanceLlmRole.RESEARCHER,
                    MaintenanceLlmRole.JUDGE,
                )
            )
        return tuple(roles)

    async def preflight(
        self,
        request: ReorganizationRequest,
        planned_steps: tuple[MutationStep, ...],
    ) -> MutationPreflight:
        del request
        errors: list[ReorganizationError] = []
        for step in planned_steps:
            if step is MutationStep.LIFECYCLE:
                if self.lifecycle is None:
                    errors.append(
                        self._error(
                            ReorganizationErrorCode.CAPABILITY_UNAVAILABLE,
                            "deterministic lifecycle maintenance is unavailable",
                        )
                    )
                continue
            plan = await self.memory.plan(_MEMORY_STEP_BY_CHAT_STEP[step])
            errors.extend(self._plan_result(step, plan).errors)
            if len(plan.provider_records) > _MAX_PROVIDER_RECORDS:
                errors.append(
                    self._error(
                        ReorganizationErrorCode.PREFLIGHT_FAILED,
                        "maintenance provider input exceeds the bounded record limit",
                    )
                )
        for role in self._required_roles(planned_steps):
            provider = self.providers.llms.get(role)
            if provider is None:
                detail = self.providers.configuration_errors.get(role.value)
                errors.append(
                    self._error(
                        ReorganizationErrorCode.CAPABILITY_UNAVAILABLE,
                        detail
                        or f"explicit maintenance {role.value} provider is missing",
                    )
                )
                continue
            try:
                await provider.probe()
            except BaseException as exc:
                if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                    raise
                errors.append(
                    self._error(
                        ReorganizationErrorCode.CAPABILITY_UNAVAILABLE,
                        f"maintenance {role.value} provider readiness failed ({type(exc).__name__})",
                    )
                )
        needs_embedding = any(
            step in {MutationStep.REEMBED, MutationStep.SYNTHESIZE}
            for step in planned_steps
        )
        if needs_embedding:
            embedding = self.providers.embedding
            if embedding is None:
                detail = self.providers.configuration_errors.get("embedding")
                errors.append(
                    self._error(
                        ReorganizationErrorCode.CAPABILITY_UNAVAILABLE,
                        detail or "explicit maintenance embedding provider is missing",
                    )
                )
            else:
                try:
                    await embedding.probe()
                except BaseException as exc:
                    if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                        raise
                    errors.append(
                        self._error(
                            ReorganizationErrorCode.CAPABILITY_UNAVAILABLE,
                            f"maintenance embedding readiness failed ({type(exc).__name__})",
                        )
                    )
        return MutationPreflight(
            supported=not errors,
            planned_steps=planned_steps,
            errors=tuple(errors),
        )

    async def execute_step(
        self,
        request: ReorganizationRequest,
        step: MutationStep,
    ) -> MutationStepResult:
        self._require_active_run(request)
        if step is MutationStep.LIFECYCLE:
            if self.lifecycle is None:
                return MutationStepResult(
                    step=step,
                    status=MutationStepStatus.FAILED,
                    errors=(
                        self._error(
                            ReorganizationErrorCode.CAPABILITY_UNAVAILABLE,
                            "deterministic lifecycle maintenance is unavailable",
                        ),
                    ),
                )
            return self._lifecycle_result(
                await self.lifecycle.run_reorganization_lifecycle(),
                preview=False,
            )
        memory_step = _MEMORY_STEP_BY_CHAT_STEP[step]
        plan = await self.memory.plan(memory_step)
        if plan.errors:
            preview = self._plan_result(step, plan)
            return preview.model_copy(update={"status": MutationStepStatus.FAILED})
        try:
            command = await self._command_for_plan(step, plan)
            result = await self.memory.apply(plan, command)
        except BaseException as exc:
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            return MutationStepResult(
                step=step,
                status=MutationStepStatus.FAILED,
                scanned_count=plan.scanned_count,
                candidate_count=plan.candidate_count,
                errors=(
                    self._error(
                        ReorganizationErrorCode.MUTATION_FAILED,
                        f"maintenance step failed ({type(exc).__name__})",
                    ),
                ),
            )
        errors = tuple(
            self._error(
                ReorganizationErrorCode.MUTATION_FAILED,
                error.message,
                store=error.store or "memory",
            )
            for error in result.errors
        )
        if result.succeeded:
            self._commands.append(command)
        return MutationStepResult(
            step=step,
            status=(
                MutationStepStatus.COMPLETED
                if result.succeeded
                else MutationStepStatus.FAILED
            ),
            scanned_count=result.scanned_count,
            candidate_count=plan.candidate_count,
            changed_count=result.changed_count,
            warnings=result.warnings,
            errors=errors,
        )

    async def _command_for_plan(
        self,
        step: MutationStep,
        plan: MemoryMutationPlan,
    ) -> MemoryMutationCommand:
        if plan.candidate_count == 0 or step in {
            MutationStep.DEDUPE,
            MutationStep.PRUNE,
        }:
            return MemoryMutationCommand(plan_id=plan.plan_id, step=plan.step)
        if step is MutationStep.SYNTHESIZE:
            synthesis_provider = self.providers.llms[MaintenanceLlmRole.SYNTHESIZER]
            embedding = cast(MaintenanceEmbeddingProvider, self.providers.embedding)
            synthesis_response = await synthesis_provider.complete_model(
                SynthesisResponse,
                system_prompt=(
                    "Create bounded synthesized insights from only the supplied "
                    "records. Return strict JSON matching the response schema."
                ),
                user_payload=self._provider_payload(plan),
            )
            vectors = await embedding.embed_documents(
                tuple(draft.document for draft in synthesis_response.drafts)
            )
            additions = tuple(
                MemoryVectorAddition(
                    collection=draft.collection,
                    memory_id=f"reorg-{plan.plan_id[:12]}-{index:04d}",
                    document=draft.document,
                    embedding=vector,
                    source_memory_ids=draft.source_memory_ids,
                )
                for index, (draft, vector) in enumerate(
                    zip(synthesis_response.drafts, vectors, strict=True), start=1
                )
            )
            return MemoryMutationCommand(
                plan_id=plan.plan_id,
                step=plan.step,
                vector_additions=additions,
            )
        if step is MutationStep.VERIFY:
            responses: list[VerificationResponse] = []
            payload = self._provider_payload(plan)
            for role in (
                MaintenanceLlmRole.CLASSIFIER,
                MaintenanceLlmRole.RESEARCHER,
                MaintenanceLlmRole.JUDGE,
            ):
                verification_provider = self.providers.llms[role]
                verification_response = await verification_provider.complete_model(
                    VerificationResponse,
                    system_prompt=(
                        f"Act as the maintenance {role.value}. Return one bounded "
                        "verdict for every supplied record as strict JSON."
                    ),
                    user_payload=payload,
                )
                self._validate_verification_coverage(plan, verification_response)
                responses.append(verification_response)
                payload = json.dumps(
                    {
                        "records": json.loads(self._provider_payload(plan))["records"],
                        "prior_decisions": [
                            item.model_dump(mode="json")
                            for prior in responses
                            for item in prior.decisions
                        ],
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
            final = responses[-1]
            return MemoryMutationCommand(
                plan_id=plan.plan_id,
                step=plan.step,
                verification_updates=tuple(
                    MemoryVerificationUpdate(
                        collection=decision.collection,
                        memory_id=decision.memory_id,
                        status=decision.status,
                        confidence=decision.confidence,
                    )
                    for decision in final.decisions
                ),
            )
        if step is MutationStep.REEMBED:
            embedding = cast(MaintenanceEmbeddingProvider, self.providers.embedding)
            records = plan.provider_records
            vector_embeddings = await embedding.embed_documents(
                tuple(record.document or "" for record in records)
            )
            edge_embeddings = await embedding.embed_documents(
                tuple(edge.relation for edge in plan.graph_edge_targets)
            )
            return MemoryMutationCommand(
                plan_id=plan.plan_id,
                step=plan.step,
                embedding_updates=tuple(
                    MemoryEmbeddingUpdate(
                        collection=record.collection,
                        memory_id=record.memory_id,
                        embedding=vector,
                    )
                    for record, vector in zip(records, vector_embeddings, strict=True)
                ),
                graph_embedding_updates=tuple(
                    GraphEmbeddingUpdate(
                        source_id=edge.source_id,
                        target_id=edge.target_id,
                        relation=edge.relation,
                        embedding=vector,
                    )
                    for edge, vector in zip(
                        plan.graph_edge_targets,
                        edge_embeddings,
                        strict=True,
                    )
                ),
            )
        raise ValueError("unsupported maintenance step")

    @staticmethod
    def _provider_payload(plan: MemoryMutationPlan) -> str:
        return json.dumps(
            {
                "records": [
                    {
                        "collection": record.collection,
                        "memory_id": record.memory_id,
                        "document": record.document,
                    }
                    for record in plan.provider_records
                ]
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    @staticmethod
    def _validate_verification_coverage(
        plan: MemoryMutationPlan,
        response: VerificationResponse,
    ) -> None:
        planned = {
            (record.collection, record.memory_id) for record in plan.provider_records
        }
        returned = {
            (decision.collection, decision.memory_id) for decision in response.decisions
        }
        if returned != planned or len(returned) != len(response.decisions):
            raise ValueError("maintenance verification response changed the plan")

    @staticmethod
    def _lifecycle_result(
        report: LifecycleStepReport,
        *,
        preview: bool,
    ) -> MutationStepResult:
        return MutationStepResult(
            step=MutationStep.LIFECYCLE,
            status=(
                MutationStepStatus.PREVIEWED
                if preview and report.succeeded
                else MutationStepStatus.COMPLETED
                if report.succeeded
                else MutationStepStatus.FAILED
            ),
            scanned_count=report.scanned_count,
            candidate_count=report.candidate_count,
            changed_count=(None if preview else report.changed_count),
            warnings=report.warnings,
            errors=report.errors,
        )

    async def verify_postconditions(
        self,
        request: ReorganizationRequest,
    ) -> MutationVerification:
        self._require_active_run(request)
        verification = await self.memory.verify_postconditions(tuple(self._commands))
        errors = tuple(
            self._error(
                ReorganizationErrorCode.INTEGRITY_FAILED,
                error.message,
                store=error.store or "memory",
            )
            for error in verification.errors
        )
        return MutationVerification(
            verified=verification.verified,
            vector_collection_count=verification.vector_collection_count,
            vector_record_count=verification.vector_record_count,
            graph_node_count=verification.graph_node_count,
            graph_edge_count=verification.graph_edge_count,
            warnings=verification.warnings,
            errors=errors,
        )


__all__ = [
    "ExplicitMaintenanceProviderRegistry",
    "FrameworkMaintenanceMutationAdapter",
    "LifecycleMaintenanceRunner",
    "LifecycleStepReport",
    "LiteLlmMaintenanceEmbeddingProvider",
    "LiteLlmMaintenanceProvider",
    "MaintenanceEmbeddingProvider",
    "MaintenanceLlmProvider",
    "MaintenanceLlmRole",
    "MaintenanceProviderConfig",
    "ProviderProbeResponse",
    "SynthesisDraft",
    "SynthesisResponse",
    "VerificationDecision",
    "VerificationResponse",
    "build_explicit_maintenance_provider_registry",
]
