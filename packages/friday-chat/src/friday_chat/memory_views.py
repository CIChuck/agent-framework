"""Typed memory diagnostics and record-query views owned by Friday Chat."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar("T")


class MemoryMetricState(str, Enum):
    """Availability state for one diagnostic value."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    NOT_CONFIGURED = "not_configured"


class MemoryDiagnosticReason(str, Enum):
    """Content-safe reason categories for missing memory diagnostics."""

    RUNTIME_NOT_INITIALIZED = "runtime not initialized"
    SESSION_STATE_UNAVAILABLE = "session state unavailable"
    NO_COMPLETED_TURN = "no completed turn"
    STORE_READ_FAILED = "store read failed"
    COMPONENT_NOT_CONFIGURED = "component not configured"
    COMPONENT_INITIALIZATION_FAILED = "component initialization failed"
    CONFIG_VALUE_INVALID = "config value invalid"


@dataclass(frozen=True)
class MemoryMetric(Generic[T]):
    """One typed value that never conflates absence with numeric zero."""

    state: MemoryMetricState
    value: T | None = None
    reason: MemoryDiagnosticReason | None = None

    def __post_init__(self) -> None:
        if self.state is MemoryMetricState.AVAILABLE:
            if self.value is None or self.reason is not None:
                raise ValueError("available memory metric requires only a value")
            return
        if self.value is not None or self.reason is None:
            raise ValueError("missing memory metric requires only a reason")

    @classmethod
    def available(cls, value: T) -> MemoryMetric[T]:
        """Build an available metric, including valid zero and false values."""
        return cls(state=MemoryMetricState.AVAILABLE, value=value)

    @classmethod
    def unavailable(
        cls,
        reason: MemoryDiagnosticReason,
    ) -> MemoryMetric[T]:
        """Build a metric whose configured source could not be read."""
        return cls(state=MemoryMetricState.UNAVAILABLE, reason=reason)

    @classmethod
    def not_configured(cls) -> MemoryMetric[T]:
        """Build a metric for an intentionally absent component."""
        return cls(
            state=MemoryMetricState.NOT_CONFIGURED,
            reason=MemoryDiagnosticReason.COMPONENT_NOT_CONFIGURED,
        )


class MemoryStoreComponent(str, Enum):
    """Bounded component names safe to expose in terminal warnings."""

    EPISODIC = "episodic"
    VECTOR_SHORT_TERM = "vector short-term"
    VECTOR_LONG_TERM = "vector long-term"
    VECTOR_DECAYED = "vector decayed"
    GRAPH = "graph"
    TRANSCRIPT = "transcript"
    ACCESS_BUFFER = "access buffer"
    PRIMING = "priming"
    MEMORY_RECORD = "memory record"


@dataclass(frozen=True)
class MemoryDiagnosticWarning:
    """Sanitized partial-read warning with no store exception content."""

    component: MemoryStoreComponent
    reason: MemoryDiagnosticReason = MemoryDiagnosticReason.STORE_READ_FAILED


@dataclass(frozen=True)
class MemoryStoreStatistics:
    """Statistics read by a memory adapter from configured store APIs."""

    episodic_turns: MemoryMetric[int]
    vector_short_term: MemoryMetric[int]
    vector_long_term: MemoryMetric[int]
    vector_decayed: MemoryMetric[int]
    vector_active_total: MemoryMetric[int]
    vector_total: MemoryMetric[int]
    graph_nodes: MemoryMetric[int]
    graph_relationships: MemoryMetric[int]
    lifecycle_enabled: MemoryMetric[bool]
    access_buffer_entries: MemoryMetric[int]
    access_buffer_accesses: MemoryMetric[int]
    priming_enabled: MemoryMetric[bool]
    priming_previous_sessions: MemoryMetric[int]
    warnings: tuple[MemoryDiagnosticWarning, ...] = ()


@dataclass(frozen=True)
class MemoryStatisticsSnapshot:
    """Complete command snapshot assembled from typed app and store state."""

    session_id: MemoryMetric[str]
    in_process_turns: MemoryMetric[int]
    tracked_turn_ids: MemoryMetric[int]
    scoped_variables: MemoryMetric[int]
    transcript_entries: MemoryMetric[int]
    store: MemoryStoreStatistics
    last_context_total_tokens: MemoryMetric[int]
    last_context_message_tokens: MemoryMetric[int]
    last_context_tool_schema_tokens: MemoryMetric[int]
    last_context_available_budget: MemoryMetric[int]
    last_context_utilization: MemoryMetric[float]
    last_context_severity: MemoryMetric[str]
    warnings: tuple[MemoryDiagnosticWarning, ...] = ()


class MemoryRecordKind(str, Enum):
    """Closed record kinds exposed by memory commands."""

    INSIGHT = "insight"
    SUMMARY = "summary"
    META_INSIGHT = "meta_insight"


class MemoryCollection(str, Enum):
    """Lifecycle collections queried by active-memory commands."""

    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"


@dataclass(frozen=True)
class MemoryRecordView:
    """Typed, bounded view of one vector memory record."""

    record_id: str
    kind: MemoryRecordKind
    text: str
    collection: MemoryCollection
    lifecycle_stage: str | None = None
    created_at: datetime | None = None
    confidence: float | None = None
    source_count: int | None = None
    provenance_source_type: str | None = None
    source_memory_ids: tuple[str, ...] = ()
    provenance_truncated: bool = False
    verification_status: str | None = None
    verification_confidence: float | None = None


@dataclass(frozen=True)
class MemoryRecordQueryResult:
    """Records plus honest partial-read evidence for one typed query."""

    kind: MemoryRecordKind
    records: tuple[MemoryRecordView, ...]
    warnings: tuple[MemoryDiagnosticWarning, ...] = ()
    decayed_records_excluded: bool = True

    @property
    def complete(self) -> bool:
        """Return whether every active collection was read successfully."""
        return not self.warnings


__all__ = [
    "MemoryCollection",
    "MemoryDiagnosticReason",
    "MemoryDiagnosticWarning",
    "MemoryMetric",
    "MemoryMetricState",
    "MemoryRecordKind",
    "MemoryRecordQueryResult",
    "MemoryRecordView",
    "MemoryStatisticsSnapshot",
    "MemoryStoreComponent",
    "MemoryStoreStatistics",
]
