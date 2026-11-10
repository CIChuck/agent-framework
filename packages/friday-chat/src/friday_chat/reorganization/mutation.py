"""Chat configuration/transport composition over the shared Memory pipeline."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass, field

from friday_llm import LiteLLMEmbeddingService, LiteLLMService, ResilienceConfig
from friday_memory.llm_completion import MemoryLLMClient, complete_memory_request
from friday_memory.maintenance.models import SynthesisConfig
from friday_memory.maintenance.mutation import MemoryMutationParticipant
from friday_memory.maintenance.pipeline import (
    MemoryMaintenanceBoundary,
    MemoryMaintenanceObserver,
    MemoryMaintenancePipeline,
    MemoryMaintenanceRequest,
    MemoryMaintenanceRunResult,
)
from friday_memory.maintenance.provider_contracts import (
    ExplicitMaintenanceProviderRegistry as ExplicitMaintenanceProviderRegistry,
)
from friday_memory.maintenance.provider_contracts import (
    LifecycleMaintenanceRunner as LifecycleMaintenanceRunner,
)
from friday_memory.maintenance.provider_contracts import (
    LifecycleStepReport as LifecycleStepReport,
)
from friday_memory.maintenance.provider_contracts import (
    MaintenanceEmbeddingProvider as MaintenanceEmbeddingProvider,
)
from friday_memory.maintenance.provider_contracts import (
    MaintenanceLlmProvider as MaintenanceLlmProvider,
)
from friday_memory.maintenance.provider_contracts import (
    MaintenanceLlmRole as MaintenanceLlmRole,
)
from friday_memory.maintenance.provider_contracts import (
    MaintenanceProviderConfig as MaintenanceProviderConfig,
)
from friday_memory.maintenance.provider_contracts import (
    MaintenanceResponseError as MaintenanceResponseError,
)
from friday_memory.maintenance.provider_contracts import (
    MaintenanceResponseIncompleteError as MaintenanceResponseIncompleteError,
)
from friday_memory.maintenance.provider_contracts import (
    MaintenanceResponseParseError as MaintenanceResponseParseError,
)
from friday_memory.maintenance.provider_contracts import (
    MaintenanceResponseValidationError as MaintenanceResponseValidationError,
)
from friday_memory.maintenance.provider_contracts import (
    ProviderProbeResponse as ProviderProbeResponse,
)
from friday_memory.maintenance.provider_contracts import (
    ProviderResponseT as ProviderResponseT,
)
from friday_memory.maintenance.provider_contracts import (
    StrictProviderModel as StrictProviderModel,
)
from friday_memory.maintenance.provider_contracts import (
    SynthesisDraft as SynthesisDraft,
)
from friday_memory.maintenance.provider_contracts import (
    SynthesisResponse as SynthesisResponse,
)
from friday_memory.maintenance.provider_contracts import (
    VerificationDecision as VerificationDecision,
)
from friday_memory.maintenance.provider_contracts import (
    VerificationResponse as VerificationResponse,
)
from friday_memory.maintenance.provider_contracts import (
    decode_maintenance_response as decode_maintenance_response,
)
from friday_telemetry import TelemetryInterface
from friday_telemetry.models.llm_events import ServiceRole

from friday_chat.config import FridayChatConfig
from friday_chat.reorganization.contracts import (
    MutationStep,
    MutationStepResult,
    ReorganizationRequest,
)
from friday_chat.reorganization.coordinator import (
    MutationPreflight,
    present_memory_error,
    present_stage_result,
    to_memory_request,
)

_DEFAULT_SYNTHESIS_GUIDANCE = (
    "Identify one useful higher-order observation that is supported by multiple "
    "records and is not explicitly stated by any single record."
)


@dataclass
class LiteLlmMaintenanceProvider:
    """Production provider constructed only from explicit maintenance config."""

    role: MaintenanceLlmRole
    service: MemoryLLMClient
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
        schema = json.dumps(
            response_model.model_json_schema(),
            sort_keys=True,
            separators=(",", ":"),
        )
        structured_system_prompt = (
            f"{system_prompt.rstrip()}\n"
            "Return exactly one JSON object with no Markdown or commentary. "
            "The object must validate against this JSON Schema:\n"
            f"{schema}"
        )
        response = await complete_memory_request(
            self.service,
            messages=[
                {"role": "system", "content": structured_system_prompt},
                {"role": "user", "content": user_payload},
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            timeout=self.config.timeout_seconds,
        )
        return decode_maintenance_response(
            response, response_model, role=self.role, configured_model=self.config.model
        )


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


def _canonical_provider_config(
    config: FridayChatConfig,
    service_name: str,
) -> MaintenanceProviderConfig:
    """Derive non-secret execution controls from one resolved chat service."""
    try:
        spec = config.llm_service_specs[service_name]
    except KeyError as exc:
        raise ValueError(
            f"unknown canonical maintenance LLM service {service_name!r}"
        ) from exc
    sampling = spec.generation_defaults.sampling
    temperature = (
        sampling.temperature
        if sampling is not None and sampling.temperature is not None
        else 0.0
    )
    return MaintenanceProviderConfig(
        model=spec.model,
        timeout_seconds=spec.resilience.timeout_seconds,
        max_retries=spec.resilience.max_retries,
        temperature=temperature,
        max_tokens=spec.generation_defaults.max_tokens or 8_000,
    )


def _required_service_name(raw: object, *, key: str) -> str:
    if not isinstance(raw, Mapping):
        raise ValueError("canonical maintenance role must be a mapping")
    value = raw.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"canonical maintenance role requires {key}")
    return value


def build_explicit_maintenance_provider_registry(
    config: FridayChatConfig,
    *, telemetry: TelemetryInterface | None = None,
) -> ExplicitMaintenanceProviderRegistry:
    """Build providers without consulting primary chat or embedding config."""
    roles: dict[MaintenanceLlmRole, ServiceRole] = {MaintenanceLlmRole.SYNTHESIZER: "maintenance_synthesizer", MaintenanceLlmRole.CLASSIFIER: "maintenance_classifier", MaintenanceLlmRole.RESEARCHER: "maintenance_researcher", MaintenanceLlmRole.JUDGE: "maintenance_judge"}
    llms: dict[MaintenanceLlmRole, MaintenanceLlmProvider] = {}
    errors: dict[str, str] = {}
    for role in MaintenanceLlmRole:
        raw = config.maintenance.llm.get(role.value)
        if raw is None:
            continue
        try:
            if config.llm_pool is not None:
                service_name = _required_service_name(raw, key="llm_service")
                provider_config = _canonical_provider_config(config, service_name)
                service = LiteLLMService.from_spec(
                    config.llm_service_specs[service_name],
                    telemetry=telemetry, service_role=roles[role],
                )
            else:
                provider_config = _provider_config(raw)
                service = LiteLLMService(
                    model_name=provider_config.model,
                    api_key=provider_config.api_key,
                    api_base=provider_config.api_base,
                    resilience=ResilienceConfig(
                        max_retries=provider_config.max_retries,
                        timeout_seconds=provider_config.timeout_seconds,
                    ),
                    telemetry=telemetry, service_role=roles[role],
                )
            llms[role] = LiteLlmMaintenanceProvider(
                role=role,
                service=service,
                config=provider_config,
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors[role.value] = (
                f"maintenance provider configuration is invalid ({type(exc).__name__})"
            )
    embedding: MaintenanceEmbeddingProvider | None = None
    if config.maintenance.embedding is not None:
        try:
            if config.embedding_pool is not None:
                service_name = _required_service_name(
                    config.maintenance.embedding,
                    key="embedding_service",
                )
                try:
                    spec = config.embedding_service_specs[service_name]
                except KeyError as exc:
                    raise ValueError(
                        "unknown canonical maintenance embedding service "
                        f"{service_name!r}"
                    ) from exc
                embedding_config = MaintenanceProviderConfig(
                    model=spec.model,
                    timeout_seconds=spec.resilience.timeout_seconds,
                    max_retries=spec.resilience.max_retries,
                )
                embedding_service = LiteLLMEmbeddingService.from_spec(spec, telemetry=telemetry, service_role="maintenance_embedding")
            else:
                embedding_config = _provider_config(config.maintenance.embedding)
                embedding_service = LiteLLMEmbeddingService(
                    model_name=embedding_config.model,
                    api_key=embedding_config.api_key,
                    api_base=embedding_config.api_base,
                    resilience=ResilienceConfig(
                        max_retries=embedding_config.max_retries,
                        timeout_seconds=embedding_config.timeout_seconds,
                    ),
                    telemetry=telemetry, service_role="maintenance_embedding",
                )
            embedding = LiteLlmMaintenanceEmbeddingProvider(
                service=embedding_service,
                config=embedding_config,
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors["embedding"] = (
                f"maintenance embedding configuration is invalid ({type(exc).__name__})"
            )
    return ExplicitMaintenanceProviderRegistry(
        llms=llms,
        embedding=embedding,
        configuration_errors=errors,
    )


def build_memory_synthesis_config(config: FridayChatConfig) -> SynthesisConfig:
    """Validate the established synthesis configuration at composition time."""
    return SynthesisConfig.model_validate(config.maintenance.synthesis)


def build_synthesis_guidance(config: FridayChatConfig) -> str:
    """Resolve configured semantic guidance without its legacy output schema."""
    raw = config.maintenance.prompts.get("meta_insight")
    if not isinstance(raw, str) or not raw.strip():
        return _DEFAULT_SYNTHESIS_GUIDANCE
    try:
        resolved = raw.format(
            insights="the supplied JSON memory records",
            entities="not supplied",
        )
    except (IndexError, KeyError, ValueError) as exc:
        raise ValueError("maintenance synthesis prompt is invalid") from exc
    semantic_guidance = resolved.partition("Respond with JSON:")[0].strip()
    if not semantic_guidance:
        return _DEFAULT_SYNTHESIS_GUIDANCE
    return semantic_guidance[:16_000]


@dataclass
class FrameworkMaintenanceMutationAdapter:
    """Construct one shared engine; adapt facts, never select domain policy."""

    memory: MemoryMutationParticipant
    providers: ExplicitMaintenanceProviderRegistry
    lifecycle: LifecycleMaintenanceRunner | None
    synthesis_guidance: str = _DEFAULT_SYNTHESIS_GUIDANCE
    _pipeline: MemoryMaintenancePipeline = field(init=False)

    def __post_init__(self) -> None:
        self._pipeline = MemoryMaintenancePipeline(
            self.memory, self.providers, self.lifecycle, self.synthesis_guidance
        )

    @staticmethod
    def memory_request(request: ReorganizationRequest) -> MemoryMaintenanceRequest:
        return to_memory_request(request)

    async def preflight(self, request: ReorganizationRequest) -> MutationPreflight:
        report = await self._pipeline.preflight(self.memory_request(request))
        return MutationPreflight(
            supported=report.supported,
            planned_steps=tuple(MutationStep(s.value) for s in report.stages),
            warnings=report.warnings,
            errors=tuple(
                present_memory_error(e, preflight=True) for e in report.errors
            ),
        )

    async def preview(
        self, request: ReorganizationRequest
    ) -> tuple[MutationStepResult, ...]:
        return tuple(
            present_stage_result(r)
            for r in await self._pipeline.preview(self.memory_request(request))
        )

    async def execute_pipeline(
        self,
        request: MemoryMaintenanceRequest,
        *,
        run_id: str,
        observer: MemoryMaintenanceObserver,
        boundary: MemoryMaintenanceBoundary,
    ) -> MemoryMaintenanceRunResult:
        return await self._pipeline.execute(
            request, operation_id=run_id, observer=observer, boundary=boundary
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
    "MaintenanceResponseError",
    "MaintenanceResponseIncompleteError",
    "MaintenanceResponseParseError",
    "MaintenanceResponseValidationError",
    "ProviderProbeResponse",
    "SynthesisDraft",
    "SynthesisResponse",
    "VerificationDecision",
    "VerificationResponse",
    "build_explicit_maintenance_provider_registry",
    "build_memory_synthesis_config",
    "build_synthesis_guidance",
]
