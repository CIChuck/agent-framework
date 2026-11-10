"""Typed Chat memory-query capabilities, detached projections and pure rendering."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

import friday_commands.memory_queries as shared_memory_queries
from friday_commands import (
    CommandExecution,
    CommandOutcome,
    CommandRequest,
    GraphData,
    GraphEntityData,
    GraphRelationshipData,
    IngestedDocumentData,
    IngestedDocumentsData,
    MemoryMetricData,
    MemoryQueryFailedData,
    MemoryRecordData,
    MemoryRecordsData,
    MemorySectionData,
    MemoryStatisticsData,
    MemoryUnavailableData,
    MemoryWarningData,
)
from friday_commands.contracts import MemoryRecordKindName

from friday_chat.commands.contracts import (
    CommandArgument,
    CommandContext,
    CommandMetadata,
    CommandResult,
)
from friday_chat.commands.memory import preview_text, record_value
from friday_chat.memory_views import (
    MemoryDiagnosticReason,
    MemoryDiagnosticWarning,
    MemoryMetric,
    MemoryMetricState,
    MemoryRecordKind,
    MemoryRecordQueryResult,
    MemoryRecordView,
    MemoryStatisticsSnapshot,
    MemoryStoreComponent,
    MemoryStoreStatistics,
)

if TYPE_CHECKING:
    from friday_chat.runtime import FridayRuntime

_MEMORY_QUERY_BY_NAME = MappingProxyType(
    {s.name: s for s in shared_memory_queries.MEMORY_QUERY_SPECS}
)


def _plain(value: object, spec: str = "") -> str:
    return "".join((format(value, spec),))


def _runtime(context: CommandContext, member: str) -> FridayRuntime:
    runtime = context.runtime
    if runtime is None:
        raise AttributeError(f"'NoneType' object has no attribute '{member}'")
    return runtime


class ChatMemoryQueryPort:
    """Keep context by reference; read services only after shared validation."""

    def __init__(self, context: CommandContext) -> None:
        self.context = context

    def memory_available(self) -> bool:
        return self.context.runtime is not None

    async def memory_statistics(self) -> MemoryStatisticsData:
        context = self.context
        try:
            store = await _runtime(context, "memory").memory.query_memory_statistics()
        except Exception:
            store = _unavailable_store_statistics()

        warnings = list(store.warnings)
        try:
            transcript_entries = MemoryMetric.available(
                len(
                    await _runtime(context, "transcript").transcript.query_entries(
                        _runtime(context, "session_identity").session_identity.value
                    )
                )
            )
        except Exception:
            transcript_entries = MemoryMetric.unavailable(
                MemoryDiagnosticReason.STORE_READ_FAILED
            )
            warnings.append(MemoryDiagnosticWarning(MemoryStoreComponent.TRANSCRIPT))

        last_budget = context.last_budget_status
        if last_budget is None:
            no_turn: MemoryMetric[int] = MemoryMetric.unavailable(
                MemoryDiagnosticReason.NO_COMPLETED_TURN
            )
            no_turn_float: MemoryMetric[float] = MemoryMetric.unavailable(
                MemoryDiagnosticReason.NO_COMPLETED_TURN
            )
            no_turn_text: MemoryMetric[str] = MemoryMetric.unavailable(
                MemoryDiagnosticReason.NO_COMPLETED_TURN
            )
            total_tokens = no_turn
            message_tokens = no_turn
            tool_schema_tokens = no_turn
            available_budget = no_turn
            utilization = no_turn_float
            severity = no_turn_text
        else:
            total_tokens = MemoryMetric.available(last_budget.total_tokens)
            message_tokens = MemoryMetric.available(last_budget.message_tokens)
            tool_schema_tokens = MemoryMetric.available(last_budget.tool_tokens)
            available_budget = MemoryMetric.available(last_budget.available_budget)
            utilization = MemoryMetric.available(last_budget.utilization_pct)
            severity = MemoryMetric.available(last_budget.severity.value)

        tracked_turn_ids = (
            MemoryMetric.available(len(context.session.turn_ids))
            if context.session is not None
            else MemoryMetric.unavailable(
                MemoryDiagnosticReason.SESSION_STATE_UNAVAILABLE
            )
        )
        snapshot = MemoryStatisticsSnapshot(
            session_id=MemoryMetric.available(
                _runtime(context, "session_identity").session_identity.value
            ),
            in_process_turns=MemoryMetric.available(len(context.history)),
            tracked_turn_ids=tracked_turn_ids,
            scoped_variables=MemoryMetric.available(len(context.variables)),
            transcript_entries=transcript_entries,
            store=store,
            last_context_total_tokens=total_tokens,
            last_context_message_tokens=message_tokens,
            last_context_tool_schema_tokens=tool_schema_tokens,
            last_context_available_budget=available_budget,
            last_context_utilization=utilization,
            last_context_severity=severity,
            warnings=tuple(warnings),
        )
        return _project_statistics(snapshot)

    async def memory_records(
        self, kind: MemoryRecordKindName
    ) -> MemoryRecordsData | MemoryQueryFailedData:
        try:
            result = await _runtime(self.context, "memory").memory.query_memory_records(
                MemoryRecordKind(kind)
            )
        except Exception:
            return MemoryQueryFailedData(kind)
        return _project_records(result)

    async def graph_snapshot(
        self, name: str | None, include_relationships: bool
    ) -> GraphData:
        records = await _runtime(self.context, "memory").memory.list_entities(name)
        relationships = []
        if include_relationships:
            relationships = await _runtime(
                self.context, "memory"
            ).memory.list_relationships(name)
        if not records and not relationships:
            return GraphData()
        entities = (
            tuple(
                GraphEntityData(
                    record_value(record, "label", "id"),
                    record_value(record, "type"),
                    record_value(record, "hit_count"),
                )
                for record in records[:100]
            )
            if records
            else ()
        )
        edges = (
            tuple(
                GraphRelationshipData(
                    record_value(record, "source_label", "source_id"),
                    record_value(record, "relation", "type"),
                    record_value(record, "target_label", "target_id"),
                    record_value(record, "hit_count"),
                )
                for record in relationships[:100]
            )
            if relationships
            else ()
        )
        return GraphData(entities, edges)

    async def ingested_documents(self) -> IngestedDocumentsData:
        result = await _runtime(
            self.context, "memory"
        ).memory.query_ingested_documents()
        documents = tuple(
            IngestedDocumentData(
                _plain(d.source_path),
                _plain(d.chunk_count),
                _plain(d.description or ""),
            )
            for d in result.documents
        )
        return IngestedDocumentsData(documents, _project_warnings(result.warnings))


def memory_query_metadata(name: str) -> CommandMetadata:
    spec = _MEMORY_QUERY_BY_NAME[name]
    return CommandMetadata(
        spec.name,
        spec.description,
        spec.category,
        spec.usage,
        spec.aliases,
        tuple(
            CommandArgument(a.name, a.description, a.required, a.default, a.choices)
            for a in spec.arguments
        ),
        spec.detail,
    )


def _project_warnings(
    warnings: tuple[MemoryDiagnosticWarning, ...],
) -> tuple[MemoryWarningData, ...]:
    if not warnings:
        return ()
    unique = sorted({(w.component.value, w.reason.value) for w in warnings})
    return tuple(MemoryWarningData(component, reason) for component, reason in unique)


def _project_metric[T](
    key: str, metric: MemoryMetric[T], *, suffix: str = ""
) -> MemoryMetricData:
    if metric.state is MemoryMetricState.AVAILABLE:
        # Preserve the old value reads and formatting branches, including bool
        # before float and the suffix behavior for each kind.
        if isinstance(metric.value, bool):
            text = "true" if metric.value else "false"
        elif isinstance(metric.value, float):
            text = f"{metric.value:.1f}{suffix}"
        elif isinstance(metric.value, str):
            text = f"{preview_text(metric.value, limit=256)}{suffix}"
        else:
            text = f"{metric.value}{suffix}"
        return MemoryMetricData(key, "available", value="".join((text,)))
    if metric.state is MemoryMetricState.NOT_CONFIGURED:
        reason = metric.reason.value if metric.reason is not None else "unknown"
        return MemoryMetricData(key, "not_configured", reason=reason)
    reason = metric.reason.value if metric.reason is not None else "unknown"
    return MemoryMetricData(key, "unavailable", reason=reason)


def _project_statistics(snapshot: MemoryStatisticsSnapshot) -> MemoryStatisticsData:
    store = snapshot.store
    sections = (
        MemorySectionData(
            "Session",
            (
                _project_metric("session_id", snapshot.session_id),
                _project_metric("in_process_turns", snapshot.in_process_turns),
                _project_metric("tracked_turn_ids", snapshot.tracked_turn_ids),
                _project_metric("scoped_variables", snapshot.scoped_variables),
            ),
        ),
        MemorySectionData(
            "Episodic",
            (_project_metric("episodic_current_session_turns", store.episodic_turns),),
        ),
        MemorySectionData(
            "Vector",
            (
                _project_metric("short_term", store.vector_short_term),
                _project_metric("long_term", store.vector_long_term),
                _project_metric("decayed", store.vector_decayed),
                _project_metric("active_total", store.vector_active_total),
                _project_metric("total", store.vector_total),
            ),
        ),
        MemorySectionData(
            "Graph",
            (
                _project_metric("nodes", store.graph_nodes),
                _project_metric("relationships", store.graph_relationships),
            ),
        ),
        MemorySectionData(
            "Transcript",
            (_project_metric("current_session_entries", snapshot.transcript_entries),),
        ),
        MemorySectionData(
            "Lifecycle",
            (
                _project_metric("enabled", store.lifecycle_enabled),
                _project_metric("access_buffer_entries", store.access_buffer_entries),
                _project_metric("access_buffer_accesses", store.access_buffer_accesses),
            ),
        ),
        MemorySectionData(
            "Priming",
            (
                _project_metric("enabled", store.priming_enabled),
                _project_metric("previous_sessions", store.priming_previous_sessions),
            ),
        ),
        MemorySectionData(
            "Last context",
            (
                _project_metric("total_tokens", snapshot.last_context_total_tokens),
                _project_metric("message_tokens", snapshot.last_context_message_tokens),
                _project_metric(
                    "tool_schema_tokens", snapshot.last_context_tool_schema_tokens
                ),
                _project_metric(
                    "available_budget", snapshot.last_context_available_budget
                ),
                _project_metric(
                    "utilization", snapshot.last_context_utilization, suffix="%"
                ),
                _project_metric("severity", snapshot.last_context_severity),
            ),
        ),
    )
    return MemoryStatisticsData(sections, _project_warnings(snapshot.warnings))


def _project_meta_record(record: MemoryRecordView) -> MemoryRecordData:
    ids = tuple(record.source_memory_ids)
    source_ids = ", ".join(ids) or "unavailable"
    truncated = bool(record.provenance_truncated)
    if truncated:
        source_ids += ", ..."
    verification = record.verification_status or "unavailable"
    if record.verification_confidence is not None:
        verification += f" ({record.verification_confidence:.3f})"
    text = "".join((preview_text(record.text),))
    record_id = "".join((preview_text(record.record_id, limit=80),))
    collection = _plain(record.collection.value)
    stage = record.lifecycle_stage or None
    lifecycle_stage = _plain(stage) if stage is not None else None
    created_at = _plain(record.created_at.isoformat()) if record.created_at else None
    confidence_value = record.confidence
    confidence = (
        _plain(confidence_value, ".3f") if confidence_value is not None else None
    )
    source_count = (
        _plain(record.source_count) if record.source_count is not None else None
    )
    provenance = record.provenance_source_type or None
    provenance_source_type = _plain(provenance) if provenance is not None else None
    # This was the last formatted field in the old list expression. Keep its
    # formatting after confidence/provenance, while concatenation stays first.
    verification_text = _plain(verification)
    return MemoryRecordData(
        record_id,
        text,
        collection,
        lifecycle_stage,
        created_at,
        confidence,
        source_count,
        provenance_source_type,
        ids,
        truncated,
        verification_text,
    )


def _project_records(result: MemoryRecordQueryResult) -> MemoryRecordsData:
    complete = True
    records: tuple[MemoryRecordData, ...]
    if not result.records:
        kind = result.kind
        if kind is MemoryRecordKind.META_INSIGHT:
            complete = bool(result.complete)
        records = ()
    else:
        visible = result.records[:100]
        kind = result.kind
        if kind is MemoryRecordKind.META_INSIGHT:
            records = tuple(_project_meta_record(record) for record in visible)
        else:
            records = tuple(
                MemoryRecordData(None, "".join((preview_text(record.text),)), None)
                for record in visible
            )
    warnings = _project_warnings(result.warnings)
    return MemoryRecordsData(kind.value, records, warnings, complete)


def _warning_lines(warnings: tuple[MemoryWarningData, ...]) -> list[str]:
    if not warnings:
        return []
    return ["Warnings:", *(f"- {w.component}: {w.reason}" for w in warnings)]


def _render_statistics(data: MemoryStatisticsData) -> str:
    lines = ["Memory statistics:"]
    for section in data.sections:
        lines.append(section.title + ":")
        for metric in section.metrics:
            value = (
                metric.value
                if metric.state == "available"
                else "not configured"
                if metric.state == "not_configured"
                else f"unavailable ({metric.reason})"
            )
            lines.append(f"- {metric.key}: {value}")
    lines.extend(_warning_lines(data.warnings))
    return "\n".join(lines)


def _fallback(value: str | None) -> str:
    return "unavailable" if value is None else value


def _render_records(data: MemoryRecordsData) -> str:
    title = {
        "insight": "Insights",
        "summary": "Summaries",
        "meta_insight": "Meta insights",
    }[data.kind]
    if not data.records:
        if data.kind == "meta_insight":
            if data.complete:
                lines = [
                    "No meta insights found. Run /reorganize --full --execute with synthesis enabled,",
                    "or use /help reorganize to inspect available modes.",
                ]
            else:
                lines = [
                    "Meta insight query incomplete; no records were returned from available stores.",
                    "Run /reorganize --full --execute only after resolving store warnings,",
                    "or use /help reorganize to inspect available modes.",
                ]
            lines.append(_decayed_policy_line())
        else:
            lines = [f"No {title.lower()} found."]
    else:
        lines = [title + ":"]
        for record in data.records:
            lines.append(f"- {record.text}")
            if data.kind == "meta_insight":
                source_ids = ", ".join(record.source_memory_ids) or "unavailable"
                if record.provenance_truncated:
                    source_ids += ", ..."
                lines.extend(
                    (
                        f"  id={record.record_id}; collection={record.collection}; stage={_fallback(record.lifecycle_stage)}; created={_fallback(record.created_at)}",
                        f"  confidence={_fallback(record.confidence)}; source_count={_fallback(record.source_count)}; provenance={_fallback(record.provenance_source_type)}; source_ids={source_ids}",
                        f"  verification={_fallback(record.verification)}",
                    )
                )
        if data.kind == "meta_insight":
            lines.append(_decayed_policy_line())
    lines.extend(_warning_lines(data.warnings))
    return "\n".join(lines)


def _decayed_policy_line() -> str:
    return "Decayed records: excluded from active insight, summary, and meta queries."


def _render_graph(data: GraphData) -> str:
    if not data.entities and not data.relationships:
        return "No entities found."
    lines = []
    if data.entities:
        lines.append("Entities:")
        for record in data.entities:
            suffix = f" ({record.node_type})" if record.node_type else ""
            if record.hit_count:
                suffix = f"{suffix}, hits={record.hit_count}"
            lines.append(f"- {record.label}{suffix}")
    if data.relationships:
        if lines:
            lines.append("")
        lines.append("Relationships:")
        for relationship in data.relationships:
            suffix = (
                f", hits={relationship.hit_count}" if relationship.hit_count else ""
            )
            lines.append(
                f"- {relationship.source} -[{relationship.relation}]-> {relationship.target}{suffix}"
            )
    return "\n".join(lines)


def _render_ingested(data: IngestedDocumentsData) -> str:
    lines = ["Ingested documents:"] if data.documents else ["No ingested documents."]
    lines.extend(
        f"- {d.source_path} ({d.chunk_count} chunks): {d.description}"
        for d in data.documents
    )
    lines.extend(_warning_lines(data.warnings))
    return "\n".join(lines)


def adapt_memory_query_outcome(outcome: CommandOutcome) -> CommandResult:
    if (
        type(outcome) is not CommandOutcome
        or outcome.error is not None
        or outcome.ui_effects
    ):
        raise ValueError("Unsupported memory query outcome")
    data = outcome.data
    if type(data) is MemoryUnavailableData:
        text = "Memory runtime is not initialized."
    elif type(data) is MemoryStatisticsData:
        text = _render_statistics(data)
    elif type(data) is MemoryRecordsData:
        text = _render_records(data)
    elif type(data) is MemoryQueryFailedData:
        title = {
            "insight": "insights",
            "summary": "summaries",
            "meta_insight": "meta insights",
        }[data.kind]
        text = f"Unable to query {title}: store read failed."
    elif type(data) is GraphData:
        text = _render_graph(data)
    elif type(data) is IngestedDocumentsData:
        text = _render_ingested(data)
    else:
        raise ValueError("Unsupported memory query data")
    return CommandResult(output=text)


async def invoke_memory_query(
    name: str, args: tuple[str, ...], context: CommandContext
) -> CommandResult:
    spec = _MEMORY_QUERY_BY_NAME[name]
    request = CommandRequest(spec.name, args, spec)
    port = ChatMemoryQueryPort(context)
    handler = shared_memory_queries.build_memory_query_handlers(port)[name]
    return adapt_memory_query_outcome(await handler(request, CommandExecution()))


def _unavailable_store_statistics() -> MemoryStoreStatistics:
    unavailable_int: MemoryMetric[int] = MemoryMetric.unavailable(
        MemoryDiagnosticReason.STORE_READ_FAILED
    )
    unavailable_bool: MemoryMetric[bool] = MemoryMetric.unavailable(
        MemoryDiagnosticReason.STORE_READ_FAILED
    )
    return MemoryStoreStatistics(
        episodic_turns=unavailable_int,
        vector_short_term=unavailable_int,
        vector_long_term=unavailable_int,
        vector_decayed=unavailable_int,
        vector_active_total=unavailable_int,
        vector_total=unavailable_int,
        graph_nodes=unavailable_int,
        graph_relationships=unavailable_int,
        lifecycle_enabled=unavailable_bool,
        access_buffer_entries=unavailable_int,
        access_buffer_accesses=unavailable_int,
        priming_enabled=unavailable_bool,
        priming_previous_sessions=unavailable_int,
        warnings=(MemoryDiagnosticWarning(MemoryStoreComponent.EPISODIC),),
    )
