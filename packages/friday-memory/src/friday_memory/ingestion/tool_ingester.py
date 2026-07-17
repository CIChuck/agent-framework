# mypy: ignore-errors
"""
Tool Output Ingester.

Automatically ingests tool outputs into vector memory for future
semantic retrieval across sessions.

When an LLM calls a tool (e.g., read_file), the content flows through
context but is eventually summarized and lost. This ingester persists
tool outputs to vector memory, enabling future recall.

Ref: docs/planning/build-plans/copilot-promotion-build-plan.md, Issue 2
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from friday_memory.ingestion.chunker import SemanticChunker, SemanticChunkerConfig

if TYPE_CHECKING:
    from friday_memory.retrieval import CollectionManager

logger = logging.getLogger(__name__)


class ToolIngestionPolicy(str, Enum):
    """Policies for when to ingest tool outputs."""

    ALWAYS = "always"  # Always ingest output
    NEVER = "never"  # Never ingest (e.g., sensitive tools)
    ON_SUCCESS = "on_success"  # Only if tool didn't error
    ON_REQUEST = "on_request"  # Only if user explicitly requests


class ToolOutputIngesterConfig(BaseModel):
    """Configuration for automatic tool output ingestion."""

    enabled: bool = Field(
        default=True,
        description="Enable tool output ingestion",
    )
    min_tokens_for_ingestion: int = Field(
        default=200,
        ge=50,
        description="Only ingest outputs >= this size (in tokens)",
    )
    chunk_size: int = Field(
        default=512,
        ge=100,
        description="Target tokens per chunk",
    )
    chunk_overlap: int = Field(
        default=50,
        ge=0,
        description="Overlap tokens for context preservation",
    )

    # Default policy for unlisted tools
    default_policy: ToolIngestionPolicy = Field(
        default=ToolIngestionPolicy.ON_SUCCESS,
        description="Default ingestion policy for tools not in tool_policies",
    )

    # Per-tool policies
    tool_policies: dict[str, ToolIngestionPolicy] = Field(
        default_factory=lambda: {
            # File reading tools - always ingest
            "read_file": ToolIngestionPolicy.ALWAYS,
            "file_read": ToolIngestionPolicy.ALWAYS,
            # Web tools - on success (may fail)
            "web_reader": ToolIngestionPolicy.ON_SUCCESS,
            "http_get": ToolIngestionPolicy.ON_SUCCESS,
            # Security-sensitive tools - never ingest
            "shell": ToolIngestionPolicy.NEVER,
            "shell_execute": ToolIngestionPolicy.NEVER,
            "code_execution": ToolIngestionPolicy.NEVER,
        },
        description="Per-tool ingestion policies",
    )


@dataclass
class IngestionResult:
    """Result of a tool output ingestion operation."""

    stored: bool = False
    skipped: bool = False
    reason: str = ""
    chunks_created: int = 0
    chunk_ids: list[str] = field(default_factory=list)
    error: str | None = None


class ToolOutputIngester:
    """
    Ingests tool outputs into vector memory for future retrieval.

    Runs asynchronously to avoid blocking the chat loop.
    Chunks large outputs for better retrieval granularity.

    Example:
        ingester = ToolOutputIngester(collection_manager)

        # In tool execution handler:
        asyncio.create_task(ingester.ingest_async(
            tool_call_id="tc_123",
            tool_name="read_file",
            content="File content...",
            turn_id="turn_5",
            source_path="/path/to/file.txt",
        ))
    """

    # Rough token estimation: ~4 chars per token
    CHARS_PER_TOKEN = 4

    def __init__(
        self,
        collection_manager: CollectionManager,
        config: ToolOutputIngesterConfig | None = None,
        chunker: SemanticChunker | None = None,
    ) -> None:
        """
        Initialize the tool output ingester.

        Args:
            collection_manager: CollectionManager for storing chunks
            config: Ingestion configuration
            chunker: Optional custom chunker (created if not provided)
        """
        self._collection_manager = collection_manager
        self._config = config or ToolOutputIngesterConfig()

        # Create chunker with appropriate config
        if chunker:
            self._chunker = chunker
        else:
            self._chunker = SemanticChunker(
                SemanticChunkerConfig(
                    chunk_size=self._config.chunk_size,
                    chunk_overlap=self._config.chunk_overlap,
                )
            )

    @property
    def config(self) -> ToolOutputIngesterConfig:
        """Access the ingestion configuration."""
        return self._config

    def should_ingest(
        self,
        tool_name: str,
        content: str,
        had_error: bool = False,
    ) -> tuple[bool, str]:
        """
        Check if a tool output should be ingested.

        Args:
            tool_name: Name of the tool
            content: Tool output content
            had_error: Whether the tool execution had an error

        Returns:
            Tuple of (should_ingest, reason)
        """
        if not self._config.enabled:
            return False, "ingestion_disabled"

        # Check policy
        policy = self._config.tool_policies.get(tool_name, self._config.default_policy)

        if policy == ToolIngestionPolicy.NEVER:
            return False, "policy:never"

        if policy == ToolIngestionPolicy.ON_SUCCESS and had_error:
            return False, "policy:on_success_but_had_error"

        if policy == ToolIngestionPolicy.ON_REQUEST:
            return False, "policy:on_request_only"

        # Check size threshold
        token_count = len(content) // self.CHARS_PER_TOKEN
        if token_count < self._config.min_tokens_for_ingestion:
            return (
                False,
                f"below_threshold:{token_count}<{self._config.min_tokens_for_ingestion}",
            )

        return True, "eligible"

    def _flatten_security_metadata(
        self, security_metadata: dict[str, Any] | None
    ) -> dict[str, Any]:
        """
        Flatten security metadata to scalar values for vector-store metadata.

        Vector metadata only accepts scalar values, so lists/dicts are
        stringified. All keys are prefixed with "security_".
        """
        if not security_metadata:
            return {}

        flattened: dict[str, Any] = {}
        for key, value in security_metadata.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                flattened[f"security_{key}"] = value
                continue
            if isinstance(value, list):
                flattened[f"security_{key}"] = ", ".join(str(item) for item in value)
                continue
            try:
                flattened[f"security_{key}"] = json.dumps(value, default=str)
            except TypeError:
                flattened[f"security_{key}"] = str(value)

        # Preserve full metadata as JSON for auditing/debugging.
        flattened["security_json"] = json.dumps(security_metadata, default=str)
        return flattened

    async def ingest_async(
        self,
        tool_call_id: str,
        tool_name: str,
        content: str,
        turn_id: str,
        source_path: str | None = None,
        had_error: bool = False,
        security_metadata: dict[str, Any] | None = None,
    ) -> IngestionResult:
        """
        Ingest tool output into vector memory.

        Called fire-and-forget after tool execution.
        Chunks the content and stores in short-term collection.

        Args:
            tool_call_id: Unique ID of the tool call
            tool_name: Name of the tool
            content: Tool output content
            turn_id: ID of the conversation turn
            source_path: Optional source path (for file tools)
            had_error: Whether the tool execution had an error
            security_metadata: Optional security metadata (detections, risk)

        Returns:
            IngestionResult with status and chunk information
        """
        try:
            # Check eligibility
            should_ingest, reason = self.should_ingest(tool_name, content, had_error)
            if not should_ingest:
                return IngestionResult(skipped=True, reason=reason)

            # Chunk the content
            chunks = self._chunker.chunk(content)

            if not chunks:
                return IngestionResult(skipped=True, reason="no_chunks_created")

            # Build metadata and IDs for each chunk
            chunk_ids: list[str] = []
            chunk_texts: list[str] = []
            chunk_metadatas: list[dict[str, Any]] = []

            now = datetime.now().isoformat()

            security_flat = self._flatten_security_metadata(security_metadata)

            for chunk in chunks:
                chunk_id = f"tool_{tool_call_id}_chunk_{chunk.index}"
                chunk_ids.append(chunk_id)
                chunk_texts.append(chunk.text)
                chunk_metadatas.append(
                    {
                        "type": "tool_output",
                        "tool_name": tool_name,
                        "tool_call_id": tool_call_id,
                        "turn_id": turn_id,
                        "chunk_index": chunk.index,
                        "total_chunks": chunk.total,
                        "has_overlap": chunk.has_overlap,
                        "source_path": source_path or "",
                        "ingested_at": now,
                        **security_flat,
                    }
                )

            # Store in short-term collection
            await self._collection_manager.add_to_short_term(
                texts=chunk_texts,
                metadatas=chunk_metadatas,
                ids=chunk_ids,
            )

            logger.debug(f"Ingested tool output: {tool_name} ({len(chunks)} chunks)")

            return IngestionResult(
                stored=True,
                chunks_created=len(chunks),
                chunk_ids=chunk_ids,
            )

        except Exception as e:
            logger.warning(f"Tool output ingestion failed: {e}")
            return IngestionResult(
                stored=False,
                error=str(e),
            )

    def ingest_fire_and_forget(
        self,
        tool_call_id: str,
        tool_name: str,
        content: str,
        turn_id: str,
        source_path: str | None = None,
        had_error: bool = False,
        security_metadata: dict[str, Any] | None = None,
    ) -> asyncio.Task[IngestionResult]:
        """
        Fire-and-forget wrapper for ingest_async.

        Creates a background task for ingestion that doesn't block.
        Errors are logged but don't affect the caller.

        Args:
            Same as ingest_async

        Returns:
            The asyncio Task (can be awaited or ignored)
        """
        return asyncio.create_task(
            self.ingest_async(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                content=content,
                turn_id=turn_id,
                source_path=source_path,
                had_error=had_error,
                security_metadata=security_metadata,
            )
        )
