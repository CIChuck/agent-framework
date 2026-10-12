"""Closed content-free execution events; accepted LLM/MCP schemas stay unchanged."""

from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    StrictBool,
    field_validator,
    model_validator,
)

from friday_telemetry.models.llm_events import (
    Count,
    Identifier,
    NonnegativeFloat,
    Reference,
)
from friday_telemetry.models.mcp import MCPEventName, MCPEventReason

OperationKind = Literal[
    "model_call", "native_tool", "mcp_tool", "memory_retrieve", "memory_store_turn",
    "memory_ingest_document", "memory_extract", "transcript_record_turn",
    "transcript_context_log", "transcript_interaction", "persistence",
]
ExecutionOutcome = Literal["succeeded", "failed", "cancelled", "incomplete", "blocked", "skipped", "pending"]
PersistenceState = Literal["not_started", "partial", "completed", "failed", "cancelled"]
ExecutionReason = Literal[
    "timeout", "retry_exhausted", "circuit_open", "selection_rejected", "unknown_tool",
    "tool_error", "invalid_result", "execution_error", "output_rejected",
    "persistence_failed", "extraction_failed", "cancelled", "unavailable", "unknown",
]
SelectionReason = Literal[
    "unknown_tool", "count_limit", "token_limit", "tools_disabled", "mcp_count_limit",
    "memory_floor", "missing_metadata", "unsafe_schema", "schema_limit",
    "not_registered", "not_relevant", "not_requested",
]
CountKind = Literal["items", "chunks", "turns", "calls"]
Scalar = str | int | float | bool


class ExecutionIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, revalidate_instances="always")
    schema_version: Literal[1] = 1
    session_ref: Reference
    turn_ref: Identifier | None = None
    operation_ref: Identifier | None = None
    parent_operation_ref: Identifier | None = None

    @field_validator("schema_version", mode="before")
    @classmethod
    def integer_version(cls, value: object) -> object:
        if type(value) is not int:
            raise ValueError("schema version requires an integer")
        return value

    @model_validator(mode="after")
    def validate_parent(self) -> Self:
        if self.operation_ref is not None and self.operation_ref == self.parent_operation_ref:
            raise ValueError("operation cannot be its own parent")
        if isinstance(self, (TurnStart, TurnFinish)) and (self.operation_ref is not None or self.parent_operation_ref is not None):
            raise ValueError("turn event has no operation identity")
        return self

    def attributes(self) -> dict[str, Scalar]:
        values = self.model_dump(exclude={"name"}, exclude_none=True)
        if len(values) > 32:
            raise ValueError("execution scalar capacity exceeded")
        return values


class TurnStart(ExecutionIdentity):
    name: Literal["execution.turn_start"] = "execution.turn_start"
    turn_ref: Identifier
    mode: Literal["completion", "streaming"]


class TurnFinish(ExecutionIdentity):
    name: Literal["execution.turn_finish"] = "execution.turn_finish"
    turn_ref: Identifier
    outcome: ExecutionOutcome
    reason: ExecutionReason | None = None
    duration_ms: NonnegativeFloat
    persistence: PersistenceState
    completed_tools: Count = 0
    failed_tools: Count = 0


class OperationStart(ExecutionIdentity):
    name: Literal["execution.operation_start"] = "execution.operation_start"
    operation_ref: Identifier
    operation_kind: OperationKind


class OperationFinish(ExecutionIdentity):
    name: Literal["execution.operation_finish"] = "execution.operation_finish"
    operation_ref: Identifier
    operation_kind: OperationKind
    outcome: ExecutionOutcome
    reason: ExecutionReason | None = None
    duration_ms: NonnegativeFloat
    count: Count | None = None
    count_kind: CountKind | None = None
    persistence_state: PersistenceState | None = None

    @model_validator(mode="after")
    def validate_count(self) -> Self:
        if (self.count is None) != (self.count_kind is None):
            raise ValueError("count and count kind must be supplied together")
        return self


class Selection(ExecutionIdentity):
    name: Literal["execution.selection"] = "execution.selection"
    toolset_ref: Identifier
    selected_native: Count
    selected_mcp: Count
    rejected_native: Count
    rejected_mcp: Count
    schema_tokens: Count
    context_budget_tokens: Count
    rejection_reason: SelectionReason | None = None
    rejection_count: Count | None = None


class ReasoningHistory(ExecutionIdentity):
    name: Literal["execution.reasoning_history"] = "execution.reasoning_history"
    iteration: Count
    present: StrictBool
    preserved: StrictBool
    eligible: StrictBool
    required: StrictBool | None = None
    message_count: Count


class LLMLink(ExecutionIdentity):
    name: Literal["execution.llm_link"] = "execution.llm_link"
    request_id: Identifier


class MCPLink(ExecutionIdentity):
    name: Literal["execution.mcp_link"] = "execution.mcp_link"
    source_event: MCPEventName
    source_sequence: Count
    server_ref: Reference | None = None
    tool_ref: Reference | None = None
    reason: MCPEventReason | None = None
    count: Count | None = None
    required: StrictBool | None = None


class ExecutionEvent(RootModel[Annotated[
    TurnStart | TurnFinish | OperationStart | OperationFinish | Selection | ReasoningHistory | LLMLink | MCPLink,
    Field(discriminator="name"),
]]):
    model_config = ConfigDict(frozen=True, strict=True, revalidate_instances="always")

    def attributes(self) -> dict[str, Scalar]:
        return self.root.attributes()
