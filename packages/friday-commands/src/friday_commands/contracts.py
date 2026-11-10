"""Immutable, runtime-validated foundation models without host dependencies."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Literal


def _string(value: object, *, optional: bool = False) -> None:
    if optional and value is None:
        return
    if not isinstance(value, str):
        raise TypeError("Expected a string")


def _boolean(value: object) -> None:
    if type(value) is not bool:
        raise TypeError("Expected a boolean")


def _snapshot[T](
    value: Iterable[object], member_type: type[T], *, exact: bool = False
) -> tuple[T, ...]:
    if isinstance(value, (str, bytes, bytearray, Mapping)):
        raise TypeError("Expected a finite iterable collection")
    items: list[T] = []
    for item in value:
        if not isinstance(item, member_type) or (
            exact and type(item) is not member_type
        ):
            raise TypeError("Invalid collection member type")
        items.append(item)
    return tuple(items)


@dataclass(frozen=True, slots=True)
class CommandArgument:
    name: str
    description: str
    required: bool = False
    default: str | None = None
    choices: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _string(self.name)
        _string(self.description)
        _boolean(self.required)
        _string(self.default, optional=True)
        object.__setattr__(self, "choices", _snapshot(self.choices, str))


@dataclass(frozen=True, slots=True)
class CommandSpec:
    name: str
    description: str
    category: str
    usage: str
    aliases: tuple[str, ...] = ()
    arguments: tuple[CommandArgument, ...] = ()
    detail: str | None = None

    def __post_init__(self) -> None:
        _string(self.name)
        _string(self.description)
        _string(self.category)
        _string(self.usage)
        object.__setattr__(self, "aliases", _snapshot(self.aliases, str))
        object.__setattr__(
            self, "arguments", _snapshot(self.arguments, CommandArgument, exact=True)
        )
        _string(self.detail, optional=True)


@dataclass(frozen=True, slots=True)
class CommandRequest:
    name: str
    args: tuple[str, ...]
    spec: CommandSpec

    def __post_init__(self) -> None:
        _string(self.name)
        object.__setattr__(self, "args", _snapshot(self.args, str))
        if type(self.spec) is not CommandSpec:
            raise TypeError("Expected a CommandSpec")
        if self.name != self.spec.name:
            raise ValueError("Request and spec names must match")


@dataclass(frozen=True, slots=True)
class CommandExecution:
    session_id: str | None = None

    def __post_init__(self) -> None:
        _string(self.session_id, optional=True)


@dataclass(frozen=True, slots=True)
class NoData:
    """A typed successful result with no data fields."""


@dataclass(frozen=True, slots=True)
class HelpData:
    commands: tuple[CommandSpec, ...]
    focused_name: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "commands", _snapshot(self.commands, CommandSpec, exact=True)
        )
        _string(self.focused_name, optional=True)


@dataclass(frozen=True, slots=True)
class ExitData:
    requested: bool = True

    def __post_init__(self) -> None:
        _boolean(self.requested)


@dataclass(frozen=True, slots=True)
class HistoryTurn:
    user_message: str
    assistant_message: str

    def __post_init__(self) -> None:
        _string(self.user_message)
        _string(self.assistant_message)


@dataclass(frozen=True, slots=True)
class HistoryData:
    turns: tuple[HistoryTurn, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "turns", _snapshot(self.turns, HistoryTurn, exact=True)
        )


@dataclass(frozen=True, slots=True)
class SessionClearedData:
    """The host's existing history/session-clear procedure completed."""


@dataclass(frozen=True, slots=True)
class DiagnosticField:
    key: str
    value: str

    def __post_init__(self) -> None:
        _string(self.key)
        _string(self.value)


@dataclass(frozen=True, slots=True)
class ContextData:
    text: str
    character_count: int | None = None
    export_path: str | None = None

    def __post_init__(self) -> None:
        _string(self.text)
        if self.character_count is not None:
            if type(self.character_count) is not int:
                raise TypeError("Expected an integer character count")
            if self.character_count < 0:
                raise ValueError("Character count must be nonnegative")
        _string(self.export_path, optional=True)


@dataclass(frozen=True, slots=True)
class PromptData:
    text: str
    export_path: str | None = None

    def __post_init__(self) -> None:
        _string(self.text)
        _string(self.export_path, optional=True)


@dataclass(frozen=True, slots=True)
class DebugTurnData:
    turn_ref: str
    outcome: str
    persistence: str
    completed_tools: str
    failed_tools: str

    def __post_init__(self) -> None:
        _string(self.turn_ref)
        _string(self.outcome)
        _string(self.persistence)
        _string(self.completed_tools)
        _string(self.failed_tools)


@dataclass(frozen=True, slots=True)
class DebugData:
    recorded: bool
    fields: tuple[DiagnosticField, ...] = ()
    turn: DebugTurnData | None = None

    def __post_init__(self) -> None:
        _boolean(self.recorded)
        object.__setattr__(
            self, "fields", _snapshot(self.fields, DiagnosticField, exact=True)
        )
        if self.turn is not None and type(self.turn) is not DebugTurnData:
            raise TypeError("Expected a DebugTurnData")
        if not self.recorded and (self.fields or self.turn is not None):
            raise ValueError("Unrecorded debug data must be empty")


@dataclass(frozen=True, slots=True)
class BudgetData:
    context_window: str | None
    output_buffer: str | None

    def __post_init__(self) -> None:
        _string(self.context_window, optional=True)
        _string(self.output_buffer, optional=True)


@dataclass(frozen=True, slots=True)
class TimingCounter:
    kind: str
    outcome: str
    count: str

    def __post_init__(self) -> None:
        _string(self.kind)
        _string(self.outcome)
        _string(self.count)


@dataclass(frozen=True, slots=True)
class TimingTurnData:
    seconds: str
    outcome: str
    persistence: str
    counters: tuple[TimingCounter, ...] = ()

    def __post_init__(self) -> None:
        _string(self.seconds)
        _string(self.outcome)
        _string(self.persistence)
        object.__setattr__(
            self, "counters", _snapshot(self.counters, TimingCounter, exact=True)
        )


@dataclass(frozen=True, slots=True)
class TimingData:
    recorded: bool
    fields: tuple[DiagnosticField, ...] = ()
    turn: TimingTurnData | None = None

    def __post_init__(self) -> None:
        _boolean(self.recorded)
        object.__setattr__(
            self, "fields", _snapshot(self.fields, DiagnosticField, exact=True)
        )
        if self.turn is not None and type(self.turn) is not TimingTurnData:
            raise TypeError("Expected a TimingTurnData")
        if not self.recorded and (self.fields or self.turn is not None):
            raise ValueError("Unrecorded timing data must be empty")


@dataclass(frozen=True, slots=True)
class RetrievalData:
    query: str
    result_count: int
    fields: tuple[DiagnosticField, ...] = ()
    previews: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _string(self.query)
        if type(self.result_count) is not int:
            raise TypeError("Expected an integer result count")
        if self.result_count < 0:
            raise ValueError("Result count must be nonnegative")
        object.__setattr__(
            self, "fields", _snapshot(self.fields, DiagnosticField, exact=True)
        )
        object.__setattr__(self, "previews", _snapshot(self.previews, str))
        if len(self.previews) > 10:
            raise ValueError("At most ten retrieval previews are permitted")


@dataclass(frozen=True, slots=True)
class RetrievalUnavailableData:
    reason: Literal["runtime_missing", "query_missing"]

    def __post_init__(self) -> None:
        _string(self.reason)
        if self.reason not in ("runtime_missing", "query_missing"):
            raise ValueError("Unknown retrieval unavailability reason")


MemoryRecordKindName = Literal["insight", "summary", "meta_insight"]


@dataclass(frozen=True, slots=True)
class MemoryWarningData:
    component: str
    reason: str

    def __post_init__(self) -> None:
        _string(self.component)
        _string(self.reason)


@dataclass(frozen=True, slots=True)
class MemoryMetricData:
    key: str
    state: Literal["available", "unavailable", "not_configured"]
    value: str | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        _string(self.key)
        _string(self.state)
        if self.state not in ("available", "unavailable", "not_configured"):
            raise ValueError("Unknown memory metric state")
        _string(self.value, optional=True)
        _string(self.reason, optional=True)
        if self.state == "available":
            if self.value is None or self.reason is not None:
                raise ValueError("Available metrics require only a value")
        elif self.value is not None or self.reason is None:
            raise ValueError("Unavailable metrics require only a reason")


@dataclass(frozen=True, slots=True)
class MemorySectionData:
    title: str
    metrics: tuple[MemoryMetricData, ...] = ()

    def __post_init__(self) -> None:
        _string(self.title)
        object.__setattr__(
            self, "metrics", _snapshot(self.metrics, MemoryMetricData, exact=True)
        )


@dataclass(frozen=True, slots=True)
class MemoryStatisticsData:
    sections: tuple[MemorySectionData, ...] = ()
    warnings: tuple[MemoryWarningData, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "sections", _snapshot(self.sections, MemorySectionData, exact=True)
        )
        object.__setattr__(
            self, "warnings", _snapshot(self.warnings, MemoryWarningData, exact=True)
        )


@dataclass(frozen=True, slots=True)
class MemoryRecordData:
    record_id: str | None
    text: str
    collection: str | None
    lifecycle_stage: str | None = None
    created_at: str | None = None
    confidence: str | None = None
    source_count: str | None = None
    provenance_source_type: str | None = None
    source_memory_ids: tuple[str, ...] = ()
    provenance_truncated: bool = False
    verification: str | None = None

    def __post_init__(self) -> None:
        _string(self.record_id, optional=True)
        _string(self.text)
        _string(self.collection, optional=True)
        _string(self.lifecycle_stage, optional=True)
        _string(self.created_at, optional=True)
        _string(self.confidence, optional=True)
        _string(self.source_count, optional=True)
        _string(self.provenance_source_type, optional=True)
        object.__setattr__(
            self, "source_memory_ids", _snapshot(self.source_memory_ids, str)
        )
        _boolean(self.provenance_truncated)
        _string(self.verification, optional=True)


@dataclass(frozen=True, slots=True)
class MemoryRecordsData:
    kind: MemoryRecordKindName
    records: tuple[MemoryRecordData, ...] = ()
    warnings: tuple[MemoryWarningData, ...] = ()
    complete: bool = True

    def __post_init__(self) -> None:
        _string(self.kind)
        if self.kind not in ("insight", "summary", "meta_insight"):
            raise ValueError("Unknown memory record kind")
        object.__setattr__(
            self, "records", _snapshot(self.records, MemoryRecordData, exact=True)
        )
        if len(self.records) > 100:
            raise ValueError("At most 100 memory records are permitted")
        object.__setattr__(
            self, "warnings", _snapshot(self.warnings, MemoryWarningData, exact=True)
        )
        _boolean(self.complete)
        for record in self.records:
            if self.kind == "meta_insight":
                if record.record_id is None or record.collection is None:
                    raise ValueError("Meta records require an id and collection")
            elif (
                record.record_id is not None
                or record.collection is not None
                or record.lifecycle_stage is not None
                or record.created_at is not None
                or record.confidence is not None
                or record.source_count is not None
                or record.provenance_source_type is not None
                or record.source_memory_ids
                or record.provenance_truncated
                or record.verification is not None
            ):
                raise ValueError("Plain records must not carry meta fields")


@dataclass(frozen=True, slots=True)
class MemoryQueryFailedData:
    kind: MemoryRecordKindName

    def __post_init__(self) -> None:
        _string(self.kind)
        if self.kind not in ("insight", "summary", "meta_insight"):
            raise ValueError("Unknown memory record kind")


@dataclass(frozen=True, slots=True)
class MemoryUnavailableData:
    reason: Literal["runtime_missing"]

    def __post_init__(self) -> None:
        _string(self.reason)
        if self.reason != "runtime_missing":
            raise ValueError("Unknown memory unavailability reason")


@dataclass(frozen=True, slots=True)
class GraphEntityData:
    label: str
    node_type: str
    hit_count: str

    def __post_init__(self) -> None:
        _string(self.label)
        _string(self.node_type)
        _string(self.hit_count)


@dataclass(frozen=True, slots=True)
class GraphRelationshipData:
    source: str
    relation: str
    target: str
    hit_count: str

    def __post_init__(self) -> None:
        _string(self.source)
        _string(self.relation)
        _string(self.target)
        _string(self.hit_count)


@dataclass(frozen=True, slots=True)
class GraphData:
    entities: tuple[GraphEntityData, ...] = ()
    relationships: tuple[GraphRelationshipData, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "entities", _snapshot(self.entities, GraphEntityData, exact=True)
        )
        if len(self.entities) > 100:
            raise ValueError("At most 100 graph entities are permitted")
        object.__setattr__(
            self,
            "relationships",
            _snapshot(self.relationships, GraphRelationshipData, exact=True),
        )
        if len(self.relationships) > 100:
            raise ValueError("At most 100 graph relationships are permitted")


@dataclass(frozen=True, slots=True)
class IngestedDocumentData:
    source_path: str
    chunk_count: str
    description: str

    def __post_init__(self) -> None:
        _string(self.source_path)
        _string(self.chunk_count)
        _string(self.description)


@dataclass(frozen=True, slots=True)
class IngestedDocumentsData:
    documents: tuple[IngestedDocumentData, ...] = ()
    warnings: tuple[MemoryWarningData, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "documents",
            _snapshot(self.documents, IngestedDocumentData, exact=True),
        )
        object.__setattr__(
            self, "warnings", _snapshot(self.warnings, MemoryWarningData, exact=True)
        )


type FoundationData = (
    NoData
    | HelpData
    | ExitData
    | HistoryData
    | SessionClearedData
    | ContextData
    | PromptData
    | DebugData
    | BudgetData
    | TimingData
    | RetrievalData
    | RetrievalUnavailableData
    | MemoryUnavailableData
    | MemoryStatisticsData
    | MemoryRecordsData
    | MemoryQueryFailedData
    | GraphData
    | IngestedDocumentsData
)


@dataclass(frozen=True, slots=True)
class CommandError:
    code: Literal["unknown_command", "invalid_arguments", "unavailable", "failed"]
    command_name: str
    usage: str | None = None

    def __post_init__(self) -> None:
        _string(self.code)
        _string(self.command_name)
        _string(self.usage, optional=True)
        if self.code not in (
            "unknown_command",
            "invalid_arguments",
            "unavailable",
            "failed",
        ):
            raise ValueError("Unknown foundation error code")


class UiEffect(Enum):
    CLEAR_SCREEN = "clear_screen"


@dataclass(frozen=True, slots=True)
class CommandOutcome:
    data: FoundationData | None = None
    error: CommandError | None = None
    ui_effects: tuple[UiEffect, ...] = ()

    def __post_init__(self) -> None:
        if self.data is not None and not any(
            type(self.data) is variant
            for variant in (
                NoData,
                HelpData,
                ExitData,
                HistoryData,
                SessionClearedData,
                ContextData,
                PromptData,
                DebugData,
                BudgetData,
                TimingData,
                RetrievalData,
                RetrievalUnavailableData,
                MemoryUnavailableData,
                MemoryStatisticsData,
                MemoryRecordsData,
                MemoryQueryFailedData,
                GraphData,
                IngestedDocumentsData,
            )
        ):
            raise TypeError("Expected a closed foundation data variant")
        if self.error is not None and type(self.error) is not CommandError:
            raise TypeError("Expected a CommandError")
        object.__setattr__(
            self, "ui_effects", _snapshot(self.ui_effects, UiEffect, exact=True)
        )
        if (self.data is None) == (self.error is None):
            raise ValueError("Exactly one of data or error is required")
        if self.error is not None and self.ui_effects:
            raise ValueError("Error outcomes cannot request UI effects")


@dataclass(frozen=True, slots=True)
class DispatchResult:
    handled: bool
    outcome: CommandOutcome | None

    def __post_init__(self) -> None:
        _boolean(self.handled)
        if self.outcome is not None and type(self.outcome) is not CommandOutcome:
            raise TypeError("Expected a CommandOutcome")
        if self.handled != (self.outcome is not None):
            raise ValueError("Handled and outcome must agree")
