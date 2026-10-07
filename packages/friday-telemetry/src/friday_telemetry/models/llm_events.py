"""Closed, content-free version-one LLM events shared across package boundaries."""

from __future__ import annotations

import math
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator,
    model_validator,
)

Scalar = str | int | float | bool
Count = Annotated[int, Field(strict=True, ge=0, le=2**63 - 1)]
Ordinal = Annotated[int, Field(strict=True, ge=1, le=2**63 - 1)]
NonnegativeFloat = Annotated[float, Field(strict=True, ge=0, allow_inf_nan=False)]
Identifier = Annotated[str, Field(strict=True, pattern=r"^[0-9a-f]{32}$")]
Reference = Annotated[str, Field(strict=True, pattern=r"^[0-9a-f]{16}$")]
Operation = Literal["chat", "embedding"]
LLMAPI = Literal[
    "typed_completion", "legacy_completion", "typed_stream", "legacy_stream",
    "embedding_query", "embedding_documents",
]
ServiceRole = Literal[
    "unspecified", "primary", "embedding", "maintenance_default",
    "maintenance_synthesizer", "maintenance_classifier", "maintenance_researcher",
    "maintenance_judge", "extraction", "passage_router", "compaction",
    "smart_file_summarizer", "smart_file_synthesizer", "maintenance_embedding",
]
Outcome = Literal["success", "error", "cancelled", "incomplete", "cache_hit", "empty_input", "blocked"]
DispatchOutcome = Literal["success", "error", "cancelled"]
ErrorCategory = Literal[
    "timeout", "rate_limit", "authentication", "invalid_request", "model",
    "network", "circuit_open", "unknown",
]
UsageState = Literal["reported", "unavailable", "invalid"]
Coverage = Literal["complete", "partial", "none"]
CostState = Literal["estimated", "unavailable", "invalid"]
PriceSource = Literal["builtin_2025", "custom_config", "supplied_table", "fallback"]
PriceMatch = Literal["exact", "provider", "base_model", "prefix", "fallback"]
FinishReason = Literal["stop", "length", "tool_calls", "content_filter", "other"]


class ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, revalidate_instances="always")


class UsageMetrics(ClosedModel):
    """Presence-aware reported counts, independent of application zero defaults."""

    usage_state: UsageState = "unavailable"
    input_tokens: Count | None = None
    output_tokens: Count | None = None
    total_tokens: Count | None = None
    reasoning_tokens: Count | None = None

    @model_validator(mode="after")
    def validate_presence(self) -> Self:
        counts = (self.input_tokens, self.output_tokens, self.total_tokens, self.reasoning_tokens)
        if self.usage_state == "unavailable" and any(n is not None for n in counts):
            raise ValueError("unavailable usage has no counts")
        if self.usage_state == "reported" and all(n is None for n in counts):
            raise ValueError("reported usage requires counts")
        if (self.input_tokens is not None and self.output_tokens is not None
                and self.total_tokens is not None
                and self.input_tokens + self.output_tokens != self.total_tokens):
            raise ValueError("contradictory usage total")
        if (self.reasoning_tokens is not None and self.output_tokens is not None
                and self.reasoning_tokens > self.output_tokens):
            raise ValueError("reasoning is part of reported output")
        if (self.input_tokens is not None and self.total_tokens is not None
                and self.total_tokens < self.input_tokens):
            raise ValueError("total cannot be below input")
        return self


class CostMetrics(ClosedModel):
    cost_state: CostState = "unavailable"
    input_cost_usd: NonnegativeFloat | None = None
    output_cost_usd: NonnegativeFloat | None = None
    total_cost_usd: NonnegativeFloat | None = None
    currency: Literal["USD"] | None = None
    price_source: PriceSource | None = None
    price_match: PriceMatch | None = None
    pricing_ref: Reference | None = None

    @model_validator(mode="after")
    def validate_estimate(self) -> Self:
        fields = (self.input_cost_usd, self.output_cost_usd, self.total_cost_usd,
                  self.currency, self.price_source, self.price_match, self.pricing_ref)
        if self.cost_state == "estimated" and any(v is None for v in fields):
            raise ValueError("estimate requires complete provenance")
        if self.cost_state != "estimated" and any(v is not None for v in fields):
            raise ValueError("unavailable cost has no estimate")
        return self


class RequestIdentity(ClosedModel):
    schema_version: Literal[1] = 1
    request_id: Identifier
    operation: Operation
    api: LLMAPI
    service_role: ServiceRole
    model_ref: Identifier
    session_ref: Reference | None = None

    @field_validator("schema_version", mode="before")
    @classmethod
    def integer_version(cls, value: object) -> object:
        if type(value) is not int:
            raise ValueError("schema version requires an integer")
        return value

    @model_validator(mode="after")
    def operation_matches_api(self) -> Self:
        if self.api.startswith("embedding_") != (self.operation == "embedding"):
            raise ValueError("operation and API disagree")
        return self


class RequestStart(RequestIdentity):
    name: Literal["llm.request_start"] = "llm.request_start"


class AttemptFinish(RequestIdentity):
    name: Literal["llm.attempt_finish"] = "llm.attempt_finish"
    attempt_id: Identifier
    attempt_number: Ordinal
    outcome: DispatchOutcome
    duration_ms: NonnegativeFloat
    batch_id: Identifier | None = None
    batch_number: Ordinal | None = None
    error_category: ErrorCategory | None = None

    @model_validator(mode="after")
    def paired_batch(self) -> Self:
        if (self.batch_id is None) != (self.batch_number is None):
            raise ValueError("batch identity requires both fields")
        return self


class BatchFinish(RequestIdentity, UsageMetrics):
    name: Literal["llm.batch_finish"] = "llm.batch_finish"
    batch_id: Identifier
    batch_number: Ordinal
    outcome: DispatchOutcome
    attempt_count: Count
    item_count: Count
    duration_ms: NonnegativeFloat
    # Embeddings report input/total only; no output or reasoning counts.
    output_tokens: None = None
    reasoning_tokens: None = None
    error_category: ErrorCategory | None = None


class RequestFinish(RequestIdentity, UsageMetrics, CostMetrics):
    name: Literal["llm.request_finish"] = "llm.request_finish"
    outcome: Outcome
    attempt_count: Count
    batch_count: Count
    duration_ms: NonnegativeFloat
    usage_coverage: Coverage
    first_text_ms: NonnegativeFloat | None = None
    chunk_count: Count | None = None
    finish_reason: FinishReason | None = None
    error_category: ErrorCategory | None = None

    @model_validator(mode="after")
    def truthful_outcome(self) -> Self:
        if self.outcome in {"cache_hit", "empty_input", "blocked"} and self.attempt_count:
            raise ValueError("non-dispatch outcome has zero attempts")
        if self.cost_state == "estimated" and (
            self.usage_coverage != "complete" or self.usage_state != "reported"
            or self.outcome != "success" or self.input_tokens is None
            or (self.operation == "chat" and self.output_tokens is None)
        ):
            raise ValueError("estimate requires complete successful reported usage")
        if self.usage_coverage == "complete" and self.usage_state != "reported":
            raise ValueError("complete coverage requires reported usage")
        return self


EventUnion = Annotated[
    RequestStart | AttemptFinish | BatchFinish | RequestFinish,
    Field(discriminator="name"),
]


class LLMEvent(RootModel[EventUnion]):
    """Runtime parser of the closed event union; never a prefix-wide dict pass-through."""

    model_config = ConfigDict(frozen=True)

    def attributes(self) -> dict[str, Scalar]:
        values = self.root.model_dump(exclude={"name"}, exclude_none=True)
        if len(values) > 32:
            raise ValueError("too many LLM attributes")
        result: dict[str, Scalar] = {}
        for key, value in values.items():
            if not isinstance(value, (str, int, float, bool)):
                raise ValueError("non-scalar LLM attribute")
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError("nonfinite LLM attribute")
            result[key] = value
        return result
