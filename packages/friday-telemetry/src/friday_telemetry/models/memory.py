"""
Telemetry Data Models for Memory Operations.

Provides Pydantic models for structured memory telemetry.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MemoryWriteMetrics(BaseModel):
    """Metrics for memory write operations."""

    request_id: str = Field(description="Unique request identifier")
    operation: Literal[
        "store_fact", "store_insight", "store_document", "ingest_file", "batch_store"
    ] = Field(description="Type of write operation")
    store_type: Literal["vector", "graph", "episodic"] = Field(
        description="Target memory store"
    )

    # Timing
    start_time: datetime = Field(default_factory=datetime.now)
    duration_ms: float = Field(default=0.0, ge=0.0)

    # Volume
    document_count: int = Field(default=1, ge=0, description="Number of documents")
    total_chars: int = Field(default=0, ge=0, description="Total character count")
    chunk_count: int | None = Field(
        default=None, description="Number of chunks (for chunked operations)"
    )

    # Embedding (if applicable)
    embedding_time_ms: float | None = Field(
        default=None, ge=0.0, description="Time spent on embeddings"
    )
    embedding_model: str | None = Field(
        default=None, description="Embedding model used"
    )

    # Result
    success: bool = Field(default=True)
    stored_ids: list[str] = Field(
        default_factory=list, description="IDs of stored items"
    )
    error_type: str | None = Field(default=None)
    error_message: str | None = Field(default=None)

    # Context
    source_file: str | None = Field(
        default=None, description="Source file for file ingestion"
    )
    session_id: str | None = Field(default=None)


class MemoryRecallMetrics(BaseModel):
    """Metrics for memory recall operations."""

    request_id: str = Field(description="Unique request identifier")
    operation: Literal["recall", "prime", "search", "get_context"] = Field(
        description="Type of recall operation"
    )

    # Query info
    query_text: str = Field(description="The query text")
    query_tokens: int = Field(default=0, ge=0, description="Approximate token count")

    # Stores queried
    stores_queried: list[str] = Field(
        default_factory=list, description="Stores that were queried"
    )

    # Timing
    start_time: datetime = Field(default_factory=datetime.now)
    duration_ms: float = Field(default=0.0, ge=0.0)
    vector_search_ms: float | None = Field(
        default=None, ge=0.0, description="Vector store search time"
    )
    graph_traversal_ms: float | None = Field(
        default=None, ge=0.0, description="Graph traversal time"
    )
    reranking_ms: float | None = Field(
        default=None, ge=0.0, description="Reranking time"
    )

    # Results
    results_count: int = Field(default=0, ge=0, description="Total results returned")
    results_by_store: dict[str, int] = Field(
        default_factory=dict, description="Result count per store"
    )

    # Cache
    cache_hit: bool = Field(default=False, description="Whether cache was hit")
    cache_source: str | None = Field(
        default=None, description="Cache source if cache hit"
    )

    # Processing
    reranking_applied: bool = Field(
        default=False, description="Whether reranking was applied"
    )
    filters_applied: list[str] = Field(
        default_factory=list, description="Filters that were applied"
    )

    # Result
    success: bool = Field(default=True)
    error_type: str | None = Field(default=None)
    error_message: str | None = Field(default=None)


class MaintenanceMetrics(BaseModel):
    """Metrics for memory maintenance operations."""

    request_id: str = Field(description="Unique request identifier")
    operation: Literal["prune", "promote", "synthesize", "reorganize", "decay"] = Field(
        description="Type of maintenance operation"
    )

    # Timing
    start_time: datetime = Field(default_factory=datetime.now)
    duration_ms: float = Field(default=0.0, ge=0.0)

    # Volume
    items_processed: int = Field(default=0, ge=0, description="Total items examined")
    items_affected: int = Field(default=0, ge=0, description="Items that were modified")

    # Specifics by operation type
    items_pruned: int = Field(default=0, ge=0, description="Items removed (prune)")
    items_promoted: int = Field(default=0, ge=0, description="Items promoted (promote)")
    items_synthesized: int = Field(
        default=0, ge=0, description="New items created (synthesize)"
    )
    relationships_inferred: int = Field(
        default=0, ge=0, description="New relationships created"
    )

    # Result
    success: bool = Field(default=True)
    error_count: int = Field(default=0, ge=0, description="Number of errors")
    dry_run: bool = Field(default=False, description="Whether this was a dry run")
    error_type: str | None = Field(default=None)
    error_message: str | None = Field(default=None)


class ArbitrationOpsMetrics(BaseModel):
    """Operational metrics for shared-promotion arbitration and recovery."""

    request_id: str = Field(description="Unique request identifier")
    session_id: str | None = Field(default=None)
    correlation_id: str | None = Field(default=None)
    proposal_volume: int = Field(default=0, ge=0)
    promotion_backlog: int = Field(default=0, ge=0)
    recovery_backlog: int = Field(default=0, ge=0)
    promotion_latency_ms: float | None = Field(default=None, ge=0.0)
    conflict_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    recovery_retries: int = Field(default=0, ge=0)
    compensation_events: int = Field(default=0, ge=0)
    degraded_mode: bool = Field(default=False)
