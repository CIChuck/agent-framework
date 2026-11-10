"""Shared maintenance provider contracts and strict response decoding.

Provider construction/configuration lookup belongs to the caller. All consumers
share these schema, complete-JSON and sanitized diagnostic rules.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, TypeVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from friday_memory.json_response import json_response_text, parse_json_object_from_text
from friday_memory.llm_completion import MemoryCompletion
from friday_memory.maintenance.mutation import (
    MemoryMutationError,
    MemoryVerificationStatus,
)
from friday_memory.response_diagnostics import ResponseDiagnostic, response_diagnostic


class StrictProviderModel(BaseModel):
    """Reject coercion and unknown fields at provider boundaries."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class MaintenanceResponseError(ValueError):
    """A provider failure carrying shared, content-safe diagnostic evidence."""

    def __init__(
        self, message: str, *, diagnostic: ResponseDiagnostic | None = None
    ) -> None:
        self.diagnostic = diagnostic
        detail = f"; {diagnostic.summary()}" if diagnostic is not None else ""
        super().__init__(message + detail)


class MaintenanceResponseParseError(MaintenanceResponseError):
    """A maintenance provider returned no parseable JSON object."""


class MaintenanceResponseIncompleteError(MaintenanceResponseParseError):
    """The provider explicitly reported an output-length termination."""


class MaintenanceResponseValidationError(MaintenanceResponseError):
    """A maintenance provider response violated its typed contract."""


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
    api_key: str | None = Field(
        default=None,
        min_length=1,
        max_length=4096,
        repr=False,
    )
    timeout_seconds: float = Field(default=30.0, gt=0.0, le=600.0)
    max_retries: int = Field(default=0, ge=0, le=10)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=8_000, gt=0, le=100_000)

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
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(min_length=1, max_length=8_000)

    @model_validator(mode="after")
    def validate_draft(self) -> SynthesisDraft:
        if len(self.source_memory_ids) != len(set(self.source_memory_ids)):
            raise ValueError("synthesis source identifiers must be unique")
        if not self.document.strip():
            raise ValueError("synthesis document must contain text")
        return self


class SynthesisResponse(StrictProviderModel):
    """Bounded synthesis provider response."""

    drafts: tuple[SynthesisDraft, ...] = Field(max_length=1)


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
    errors: tuple[MemoryMutationError, ...] = ()

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


def decode_maintenance_response[ResponseT: StrictProviderModel](
    response: MemoryCompletion,
    response_model: type[ResponseT],
    *,
    role: MaintenanceLlmRole,
    configured_model: str,
) -> ResponseT:
    diagnostic = response_diagnostic(
        role=role.value,
        configured_model=configured_model,
        response_model=response_model,
        finish_reason=response.finish_reason,
    )
    if diagnostic.finish_reason in {"length", "max_tokens", "model_length"}:
        raise MaintenanceResponseIncompleteError(
            "maintenance provider reported an incomplete response",
            diagnostic=diagnostic,
        )
    parsed = parse_json_object_from_text(
        json_response_text(response), recover_nested_objects=False
    )
    if parsed is None:
        raise MaintenanceResponseParseError(
            "maintenance provider returned no complete enclosing JSON object",
            diagnostic=diagnostic,
        )
    try:
        canonical_json = json.dumps(
            parsed,
            sort_keys=True,
            separators=(",", ":"),
        )
        return response_model.model_validate_json(canonical_json)
    except ValidationError as exc:
        raise MaintenanceResponseValidationError(
            f"maintenance {response_model.__name__} response failed validation",
            diagnostic=response_diagnostic(
                role=role.value,
                configured_model=configured_model,
                response_model=response_model,
                finish_reason=response.finish_reason,
                error=exc,
            ),
        ) from None
