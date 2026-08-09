"""Memory and context commands for FridayV2."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from friday_chat.commands.contracts import (
    CommandContext,
    CommandMetadata,
    CommandResult,
)
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

T = TypeVar("T")

_MAX_MEMORY_COMMAND_RECORDS = 100


async def memory_handler(
    context: CommandContext,
    _args: tuple[str, ...],
    _metadata: CommandMetadata,
) -> CommandResult:
    """Render real memory diagnostics without fabricated zero values."""
    if context.runtime is None:
        return CommandResult(output="Memory runtime is not initialized.")

    try:
        store = await context.runtime.memory.query_memory_statistics()
    except Exception:
        store = _unavailable_store_statistics()

    warnings = list(store.warnings)
    try:
        transcript_entries = MemoryMetric.available(
            len(
                await context.runtime.transcript.query_entries(
                    context.runtime.session_identity.value
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
        session_id=MemoryMetric.available(context.runtime.session_identity.value),
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
    return CommandResult(output=_format_memory_statistics(snapshot))


async def insights_handler(
    context: CommandContext,
    _args: tuple[str, ...],
    _metadata: CommandMetadata,
) -> CommandResult:
    """List typed active-memory insight records."""
    return await _query_memory_record_result(
        context,
        kind=MemoryRecordKind.INSIGHT,
        title="Insights",
    )


async def summaries_handler(
    context: CommandContext,
    _args: tuple[str, ...],
    _metadata: CommandMetadata,
) -> CommandResult:
    """List typed active-memory summary records."""
    return await _query_memory_record_result(
        context,
        kind=MemoryRecordKind.SUMMARY,
        title="Summaries",
    )


async def meta_handler(
    context: CommandContext,
    _args: tuple[str, ...],
    _metadata: CommandMetadata,
) -> CommandResult:
    """List existing meta insights without synthesis or provider execution."""
    return await _query_memory_record_result(
        context,
        kind=MemoryRecordKind.META_INSIGHT,
        title="Meta insights",
    )


async def _query_memory_record_result(
    context: CommandContext,
    *,
    kind: MemoryRecordKind,
    title: str,
) -> CommandResult:
    if context.runtime is None:
        return CommandResult(output="Memory runtime is not initialized.")
    try:
        result = await context.runtime.memory.query_memory_records(kind)
    except Exception:
        return CommandResult(output=f"Unable to query {title.lower()}: store read failed.")
    return _memory_record_result(title, result)


def _memory_record_result(
    title: str,
    result: MemoryRecordQueryResult,
) -> CommandResult:
    if not result.records:
        if result.kind is MemoryRecordKind.META_INSIGHT:
            if result.complete:
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
            lines.extend(_warning_lines(result.warnings))
            return CommandResult(output="\n".join(lines))
        lines = [f"No {title.lower()} found."]
        lines.extend(_warning_lines(result.warnings))
        return CommandResult(output="\n".join(lines))

    visible_records = result.records[:_MAX_MEMORY_COMMAND_RECORDS]
    lines = [f"{title}:"]
    if result.kind is MemoryRecordKind.META_INSIGHT:
        for record in visible_records:
            lines.extend(_meta_record_lines(record))
        lines.append(_decayed_policy_line())
    else:
        lines.extend(f"- {preview_text(record.text)}" for record in visible_records)
    lines.extend(_warning_lines(result.warnings))
    return CommandResult(output="\n".join(lines))


def _meta_record_lines(record: MemoryRecordView) -> list[str]:
    source_ids = ", ".join(record.source_memory_ids) or "unavailable"
    if record.provenance_truncated:
        source_ids += ", ..."
    verification = record.verification_status or "unavailable"
    if record.verification_confidence is not None:
        verification += f" ({record.verification_confidence:.3f})"
    return [
        f"- {preview_text(record.text)}",
        (
            f"  id={preview_text(record.record_id, limit=80)}; "
            f"collection={record.collection.value}; "
            f"stage={record.lifecycle_stage or 'unavailable'}; "
            f"created={record.created_at.isoformat() if record.created_at else 'unavailable'}"
        ),
        (
            f"  confidence={_optional_float(record.confidence)}; "
            f"source_count={record.source_count if record.source_count is not None else 'unavailable'}; "
            f"provenance={record.provenance_source_type or 'unavailable'}; "
            f"source_ids={source_ids}"
        ),
        f"  verification={verification}",
    ]


def _decayed_policy_line() -> str:
    return "Decayed records: excluded from active insight, summary, and meta queries."


def _warning_lines(
    warnings: tuple[MemoryDiagnosticWarning, ...],
) -> list[str]:
    if not warnings:
        return []
    unique = sorted(
        {(warning.component.value, warning.reason.value) for warning in warnings}
    )
    return ["Warnings:", *(f"- {component}: {reason}" for component, reason in unique)]


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


def _format_memory_statistics(snapshot: MemoryStatisticsSnapshot) -> str:
    store = snapshot.store
    lines = [
        "Memory statistics:",
        "Session:",
        f"- session_id: {_metric_text(snapshot.session_id)}",
        f"- in_process_turns: {_metric_text(snapshot.in_process_turns)}",
        f"- tracked_turn_ids: {_metric_text(snapshot.tracked_turn_ids)}",
        f"- scoped_variables: {_metric_text(snapshot.scoped_variables)}",
        "Episodic:",
        f"- episodic_current_session_turns: {_metric_text(store.episodic_turns)}",
        "Vector:",
        f"- short_term: {_metric_text(store.vector_short_term)}",
        f"- long_term: {_metric_text(store.vector_long_term)}",
        f"- decayed: {_metric_text(store.vector_decayed)}",
        f"- active_total: {_metric_text(store.vector_active_total)}",
        f"- total: {_metric_text(store.vector_total)}",
        "Graph:",
        f"- nodes: {_metric_text(store.graph_nodes)}",
        f"- relationships: {_metric_text(store.graph_relationships)}",
        "Transcript:",
        f"- current_session_entries: {_metric_text(snapshot.transcript_entries)}",
        "Lifecycle:",
        f"- enabled: {_metric_text(store.lifecycle_enabled)}",
        f"- access_buffer_entries: {_metric_text(store.access_buffer_entries)}",
        f"- access_buffer_accesses: {_metric_text(store.access_buffer_accesses)}",
        "Priming:",
        f"- enabled: {_metric_text(store.priming_enabled)}",
        f"- previous_sessions: {_metric_text(store.priming_previous_sessions)}",
        "Last context:",
        f"- total_tokens: {_metric_text(snapshot.last_context_total_tokens)}",
        f"- message_tokens: {_metric_text(snapshot.last_context_message_tokens)}",
        f"- tool_schema_tokens: {_metric_text(snapshot.last_context_tool_schema_tokens)}",
        f"- available_budget: {_metric_text(snapshot.last_context_available_budget)}",
        f"- utilization: {_metric_text(snapshot.last_context_utilization, suffix='%')}",
        f"- severity: {_metric_text(snapshot.last_context_severity)}",
    ]
    lines.extend(_warning_lines(snapshot.warnings))
    return "\n".join(lines)


def _metric_text(metric: MemoryMetric[T], *, suffix: str = "") -> str:
    if metric.state is MemoryMetricState.AVAILABLE:
        if isinstance(metric.value, bool):
            return "true" if metric.value else "false"
        if isinstance(metric.value, float):
            return f"{metric.value:.1f}{suffix}"
        if isinstance(metric.value, str):
            return f"{preview_text(metric.value, limit=256)}{suffix}"
        return f"{metric.value}{suffix}"
    if metric.state is MemoryMetricState.NOT_CONFIGURED:
        return "not configured"
    reason = metric.reason.value if metric.reason is not None else "unknown"
    return f"unavailable ({reason})"


def _optional_float(value: float | None) -> str:
    return "unavailable" if value is None else f"{value:.3f}"


def record_value(record: Mapping[str, Any], *keys: str) -> str:
    """Return the first non-null record value for shared legacy formatting."""
    for key in keys:
        value = record.get(key)
        if value is not None:
            return str(value)
    return ""


def preview_text(text: str, *, limit: int = 160) -> str:
    """Normalize and bound record text for shared legacy formatting."""
    normalized = " ".join(
        "".join(character if character.isprintable() else " " for character in text)
        .split()
    )
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."


__all__ = [
    "insights_handler",
    "memory_handler",
    "meta_handler",
    "preview_text",
    "record_value",
    "summaries_handler",
]
