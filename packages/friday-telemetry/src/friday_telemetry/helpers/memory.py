"""
Memory Telemetry Helper.

Provides context managers and utilities for capturing memory operation
telemetry with consistent attribute naming.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal

from friday_telemetry.attributes import FridayMemoryAttributes
from friday_telemetry.models.memory import (
    MaintenanceMetrics,
    MemoryRecallMetrics,
    MemoryWriteMetrics,
)

if TYPE_CHECKING:
    from friday_telemetry.interface import TelemetryInterface


class MemoryWriteTracker:
    """Tracks a single memory write operation."""

    def __init__(
        self,
        helper: MemoryTelemetryHelper,
        operation: Literal[
            "store_fact",
            "store_insight",
            "store_document",
            "ingest_file",
            "batch_store",
        ],
        store_type: Literal["vector", "graph", "episodic"],
    ) -> None:
        self.helper = helper
        self.operation = operation
        self.store_type = store_type

        self.request_id = str(uuid.uuid4())
        self.span_id: str | None = None
        self._start_time: float = 0
        self._end_time: float = 0

        # Volume
        self.document_count = 1
        self.total_chars = 0
        self.chunk_count: int | None = None

        # Embedding
        self.embedding_time_ms: float | None = None
        self.embedding_model: str | None = None

        # Result
        self.stored_ids: list[str] = []
        self.source_file: str | None = None
        self.session_id: str | None = None

        # Error
        self.success = True
        self.error: Exception | None = None

    def start(self) -> None:
        """Start tracking."""
        self._start_time = time.perf_counter()
        if self.helper.telemetry:
            span_name = f"memory_write {self.operation}"
            self.span_id = self.helper.telemetry.start_span(span_name)

    def set_volume(
        self,
        document_count: int = 1,
        total_chars: int = 0,
        chunk_count: int | None = None,
    ) -> None:
        """Record volume metrics."""
        self.document_count = document_count
        self.total_chars = total_chars
        self.chunk_count = chunk_count

    def set_embedding_info(
        self,
        embedding_time_ms: float,
        embedding_model: str | None = None,
    ) -> None:
        """Record embedding operation details."""
        self.embedding_time_ms = embedding_time_ms
        self.embedding_model = embedding_model

    def set_result(
        self,
        stored_ids: list[str],
        source_file: str | None = None,
        session_id: str | None = None,
    ) -> None:
        """Record write result."""
        self.stored_ids = stored_ids
        self.source_file = source_file
        self.session_id = session_id

    def set_error(self, error: Exception) -> None:
        """Record an error."""
        self.success = False
        self.error = error

    def finish(self) -> None:
        """Finish tracking and close span."""
        self._end_time = time.perf_counter()
        if self.span_id and self.helper.telemetry:
            self.helper.telemetry.end_span(self.span_id, {"success": str(self.success)})

    def to_metrics(self) -> MemoryWriteMetrics:
        """Convert to MemoryWriteMetrics."""
        duration_ms = (self._end_time - self._start_time) * 1000

        error_type = None
        error_message = None
        if self.error:
            error_type = type(self.error).__name__
            error_message = str(self.error)[:500]

        return MemoryWriteMetrics(
            request_id=self.request_id,
            operation=self.operation,
            store_type=self.store_type,
            start_time=datetime.now(),
            duration_ms=duration_ms,
            document_count=self.document_count,
            total_chars=self.total_chars,
            chunk_count=self.chunk_count,
            embedding_time_ms=self.embedding_time_ms,
            embedding_model=self.embedding_model,
            success=self.success,
            stored_ids=self.stored_ids,
            error_type=error_type,
            error_message=error_message,
            source_file=self.source_file,
            session_id=self.session_id,
        )


class MemoryRecallTracker:
    """Tracks a single memory recall operation."""

    def __init__(
        self,
        helper: MemoryTelemetryHelper,
        operation: Literal["recall", "prime", "search", "get_context"],
        query_text: str,
    ) -> None:
        self.helper = helper
        self.operation = operation
        self.query_text = query_text

        self.request_id = str(uuid.uuid4())
        self.span_id: str | None = None
        self._start_time: float = 0
        self._end_time: float = 0

        # Query
        self.query_tokens = 0
        self.stores_queried: list[str] = []

        # Timing breakdown
        self.vector_search_ms: float | None = None
        self.graph_traversal_ms: float | None = None
        self.reranking_ms: float | None = None

        # Results
        self.results_count = 0
        self.results_by_store: dict[str, int] = {}

        # Cache
        self.cache_hit = False
        self.cache_source: str | None = None

        # Processing
        self.reranking_applied = False
        self.filters_applied: list[str] = []

        # Error
        self.success = True
        self.error: Exception | None = None

    def start(self) -> None:
        """Start tracking."""
        self._start_time = time.perf_counter()
        if self.helper.telemetry:
            span_name = f"memory_recall {self.operation}"
            self.span_id = self.helper.telemetry.start_span(span_name)

    def set_query_info(self, query_tokens: int) -> None:
        """Record query information."""
        self.query_tokens = query_tokens

    def set_stores_queried(self, stores: list[str]) -> None:
        """Record which stores were queried."""
        self.stores_queried = stores

    def set_timing(
        self,
        vector_search_ms: float | None = None,
        graph_traversal_ms: float | None = None,
        reranking_ms: float | None = None,
    ) -> None:
        """Record timing breakdown."""
        self.vector_search_ms = vector_search_ms
        self.graph_traversal_ms = graph_traversal_ms
        self.reranking_ms = reranking_ms

    def set_results(
        self,
        results_count: int,
        results_by_store: dict[str, int] | None = None,
    ) -> None:
        """Record result counts."""
        self.results_count = results_count
        if results_by_store:
            self.results_by_store = results_by_store

    def set_cache_info(self, cache_hit: bool, cache_source: str | None = None) -> None:
        """Record cache information."""
        self.cache_hit = cache_hit
        self.cache_source = cache_source

    def set_processing(
        self,
        reranking_applied: bool = False,
        filters_applied: list[str] | None = None,
    ) -> None:
        """Record processing information."""
        self.reranking_applied = reranking_applied
        if filters_applied:
            self.filters_applied = filters_applied

    def set_error(self, error: Exception) -> None:
        """Record an error."""
        self.success = False
        self.error = error

    def finish(self) -> None:
        """Finish tracking and close span."""
        self._end_time = time.perf_counter()
        if self.span_id and self.helper.telemetry:
            self.helper.telemetry.end_span(self.span_id, {"success": str(self.success)})

    def to_metrics(self) -> MemoryRecallMetrics:
        """Convert to MemoryRecallMetrics."""
        duration_ms = (self._end_time - self._start_time) * 1000

        error_type = None
        error_message = None
        if self.error:
            error_type = type(self.error).__name__
            error_message = str(self.error)[:500]

        return MemoryRecallMetrics(
            request_id=self.request_id,
            operation=self.operation,
            query_text=self.query_text,
            query_tokens=self.query_tokens,
            stores_queried=self.stores_queried,
            start_time=datetime.now(),
            duration_ms=duration_ms,
            vector_search_ms=self.vector_search_ms,
            graph_traversal_ms=self.graph_traversal_ms,
            reranking_ms=self.reranking_ms,
            results_count=self.results_count,
            results_by_store=self.results_by_store,
            cache_hit=self.cache_hit,
            cache_source=self.cache_source,
            reranking_applied=self.reranking_applied,
            filters_applied=self.filters_applied,
            success=self.success,
            error_type=error_type,
            error_message=error_message,
        )


class MaintenanceTracker:
    """Tracks a single memory maintenance operation."""

    def __init__(
        self,
        helper: MemoryTelemetryHelper,
        operation: Literal["prune", "promote", "synthesize", "reorganize", "decay"],
        dry_run: bool = False,
    ) -> None:
        self.helper = helper
        self.operation = operation
        self.dry_run = dry_run

        self.request_id = str(uuid.uuid4())
        self.span_id: str | None = None
        self._start_time: float = 0
        self._end_time: float = 0

        # Volume
        self.items_processed = 0
        self.items_affected = 0

        # Operation-specific
        self.items_pruned = 0
        self.items_promoted = 0
        self.items_synthesized = 0
        self.relationships_inferred = 0

        # Error
        self.success = True
        self.error_count = 0
        self.error: Exception | None = None

    def start(self) -> None:
        """Start tracking."""
        self._start_time = time.perf_counter()
        if self.helper.telemetry:
            span_name = f"memory_maintenance {self.operation}"
            self.span_id = self.helper.telemetry.start_span(span_name)

    def set_volume(self, items_processed: int, items_affected: int) -> None:
        """Record volume metrics."""
        self.items_processed = items_processed
        self.items_affected = items_affected

    def set_operation_results(
        self,
        items_pruned: int = 0,
        items_promoted: int = 0,
        items_synthesized: int = 0,
        relationships_inferred: int = 0,
    ) -> None:
        """Record operation-specific results."""
        self.items_pruned = items_pruned
        self.items_promoted = items_promoted
        self.items_synthesized = items_synthesized
        self.relationships_inferred = relationships_inferred

    def set_error(self, error: Exception) -> None:
        """Record an error."""
        self.success = False
        self.error = error

    def increment_error_count(self) -> None:
        """Increment the error count for non-fatal errors."""
        self.error_count += 1

    def finish(self) -> None:
        """Finish tracking and close span."""
        self._end_time = time.perf_counter()
        if self.span_id and self.helper.telemetry:
            self.helper.telemetry.end_span(self.span_id, {"success": str(self.success)})

    def to_metrics(self) -> MaintenanceMetrics:
        """Convert to MaintenanceMetrics."""
        duration_ms = (self._end_time - self._start_time) * 1000

        error_type = None
        error_message = None
        if self.error:
            error_type = type(self.error).__name__
            error_message = str(self.error)[:500]

        return MaintenanceMetrics(
            request_id=self.request_id,
            operation=self.operation,
            start_time=datetime.now(),
            duration_ms=duration_ms,
            items_processed=self.items_processed,
            items_affected=self.items_affected,
            items_pruned=self.items_pruned,
            items_promoted=self.items_promoted,
            items_synthesized=self.items_synthesized,
            relationships_inferred=self.relationships_inferred,
            success=self.success,
            error_count=self.error_count,
            dry_run=self.dry_run,
            error_type=error_type,
            error_message=error_message,
        )


class MemoryTelemetryHelper:
    """
    Helper class for capturing memory telemetry.

    Provides context managers for tracking memory write, recall, and
    maintenance operations with consistent attribute naming.

    Example:
        helper = MemoryTelemetryHelper(telemetry)

        with helper.track_write(
            operation="store_fact",
            store_type="vector",
        ) as tracker:
            result = await memory.store(fact)
            tracker.set_volume(document_count=1, total_chars=len(fact))
            tracker.set_result(stored_ids=[result.id])

        # Metrics automatically emitted on context exit
    """

    def __init__(
        self,
        telemetry: TelemetryInterface | None = None,
    ) -> None:
        """
        Initialize telemetry helper.

        Args:
            telemetry: TelemetryInterface for capturing events and spans
        """
        self.telemetry = telemetry

    @contextmanager
    def track_write(
        self,
        operation: Literal[
            "store_fact",
            "store_insight",
            "store_document",
            "ingest_file",
            "batch_store",
        ],
        store_type: Literal["vector", "graph", "episodic"],
    ) -> Generator[MemoryWriteTracker]:
        """
        Context manager for tracking a memory write operation.

        Args:
            operation: Type of write operation
            store_type: Target memory store

        Yields:
            MemoryWriteTracker for recording operation details
        """
        tracker = MemoryWriteTracker(
            helper=self,
            operation=operation,
            store_type=store_type,
        )
        tracker.start()

        try:
            yield tracker
        except Exception as e:
            tracker.set_error(e)
            raise
        finally:
            tracker.finish()
            self._emit_write_metrics(tracker)

    @contextmanager
    def track_recall(
        self,
        operation: Literal["recall", "prime", "search", "get_context"],
        query_text: str,
    ) -> Generator[MemoryRecallTracker]:
        """
        Context manager for tracking a memory recall operation.

        Args:
            operation: Type of recall operation
            query_text: The query being performed

        Yields:
            MemoryRecallTracker for recording operation details
        """
        tracker = MemoryRecallTracker(
            helper=self,
            operation=operation,
            query_text=query_text,
        )
        tracker.start()

        try:
            yield tracker
        except Exception as e:
            tracker.set_error(e)
            raise
        finally:
            tracker.finish()
            self._emit_recall_metrics(tracker)

    @contextmanager
    def track_maintenance(
        self,
        operation: Literal["prune", "promote", "synthesize", "reorganize", "decay"],
        dry_run: bool = False,
    ) -> Generator[MaintenanceTracker]:
        """
        Context manager for tracking a memory maintenance operation.

        Args:
            operation: Type of maintenance operation
            dry_run: Whether this is a dry run

        Yields:
            MaintenanceTracker for recording operation details
        """
        tracker = MaintenanceTracker(
            helper=self,
            operation=operation,
            dry_run=dry_run,
        )
        tracker.start()

        try:
            yield tracker
        except Exception as e:
            tracker.set_error(e)
            raise
        finally:
            tracker.finish()
            self._emit_maintenance_metrics(tracker)

    def _emit_write_metrics(self, tracker: MemoryWriteTracker) -> None:
        """Emit telemetry for a completed write operation."""
        if not self.telemetry:
            return

        metrics = tracker.to_metrics()

        attributes: dict[str, Any] = {
            FridayMemoryAttributes.MEMORY_OPERATION: metrics.operation,
            FridayMemoryAttributes.MEMORY_STORE_TYPE: metrics.store_type,
            FridayMemoryAttributes.MEMORY_DOCUMENT_COUNT: metrics.document_count,
            FridayMemoryAttributes.MEMORY_TOTAL_CHARS: metrics.total_chars,
            "duration_ms": metrics.duration_ms,
            "success": metrics.success,
            "request_id": metrics.request_id,
        }

        if metrics.chunk_count is not None:
            attributes["chunk_count"] = metrics.chunk_count
        if metrics.embedding_time_ms is not None:
            attributes[FridayMemoryAttributes.MEMORY_EMBEDDING_MS] = (
                metrics.embedding_time_ms
            )
        if metrics.embedding_model:
            attributes["embedding_model"] = metrics.embedding_model
        if metrics.source_file:
            attributes["source_file"] = metrics.source_file
        if metrics.session_id:
            attributes["session_id"] = metrics.session_id
        if metrics.stored_ids:
            attributes["stored_count"] = len(metrics.stored_ids)

        if not metrics.success:
            if metrics.error_type:
                attributes["error_type"] = metrics.error_type
            if metrics.error_message:
                attributes["error_message"] = metrics.error_message

        event_name = "memory_write_success" if metrics.success else "memory_write_error"
        self.telemetry.capture_event(event_name, attributes)

    def _emit_recall_metrics(self, tracker: MemoryRecallTracker) -> None:
        """Emit telemetry for a completed recall operation."""
        if not self.telemetry:
            return

        metrics = tracker.to_metrics()

        attributes: dict[str, Any] = {
            FridayMemoryAttributes.MEMORY_OPERATION: metrics.operation,
            FridayMemoryAttributes.MEMORY_QUERY_TOKENS: metrics.query_tokens,
            FridayMemoryAttributes.MEMORY_RESULTS_COUNT: metrics.results_count,
            FridayMemoryAttributes.MEMORY_CACHE_HIT: metrics.cache_hit,
            FridayMemoryAttributes.MEMORY_RERANKING_APPLIED: metrics.reranking_applied,
            "duration_ms": metrics.duration_ms,
            "success": metrics.success,
            "request_id": metrics.request_id,
        }

        if metrics.stores_queried:
            attributes["stores_queried"] = ",".join(metrics.stores_queried)
        if metrics.vector_search_ms is not None:
            attributes[FridayMemoryAttributes.MEMORY_VECTOR_SEARCH_MS] = (
                metrics.vector_search_ms
            )
        if metrics.graph_traversal_ms is not None:
            attributes[FridayMemoryAttributes.MEMORY_GRAPH_TRAVERSAL_MS] = (
                metrics.graph_traversal_ms
            )
        if metrics.reranking_ms is not None:
            attributes["reranking_ms"] = metrics.reranking_ms
        if metrics.cache_source:
            attributes["cache_source"] = metrics.cache_source
        if metrics.filters_applied:
            attributes["filters_applied"] = ",".join(metrics.filters_applied)
        if metrics.results_by_store:
            for store, count in metrics.results_by_store.items():
                attributes[f"results_{store}"] = count

        if not metrics.success:
            if metrics.error_type:
                attributes["error_type"] = metrics.error_type
            if metrics.error_message:
                attributes["error_message"] = metrics.error_message

        event_name = (
            "memory_recall_success" if metrics.success else "memory_recall_error"
        )
        self.telemetry.capture_event(event_name, attributes)

    def _emit_maintenance_metrics(self, tracker: MaintenanceTracker) -> None:
        """Emit telemetry for a completed maintenance operation."""
        if not self.telemetry:
            return

        metrics = tracker.to_metrics()

        attributes: dict[str, Any] = {
            FridayMemoryAttributes.MEMORY_OPERATION: metrics.operation,
            FridayMemoryAttributes.MEMORY_ITEMS_PROCESSED: metrics.items_processed,
            FridayMemoryAttributes.MEMORY_ITEMS_AFFECTED: metrics.items_affected,
            "duration_ms": metrics.duration_ms,
            "success": metrics.success,
            "request_id": metrics.request_id,
            "dry_run": metrics.dry_run,
        }

        if metrics.items_pruned > 0:
            attributes["items_pruned"] = metrics.items_pruned
        if metrics.items_promoted > 0:
            attributes["items_promoted"] = metrics.items_promoted
        if metrics.items_synthesized > 0:
            attributes["items_synthesized"] = metrics.items_synthesized
        if metrics.relationships_inferred > 0:
            attributes["relationships_inferred"] = metrics.relationships_inferred
        if metrics.error_count > 0:
            attributes["error_count"] = metrics.error_count

        if not metrics.success:
            if metrics.error_type:
                attributes["error_type"] = metrics.error_type
            if metrics.error_message:
                attributes["error_message"] = metrics.error_message

        event_name = (
            "memory_maintenance_success"
            if metrics.success
            else "memory_maintenance_error"
        )
        self.telemetry.capture_event(event_name, attributes)
