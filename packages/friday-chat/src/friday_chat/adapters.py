"""Adapters from FridayV2 runtime protocols to framework packages."""

from __future__ import annotations

import asyncio
import importlib
import json
import math
import os
import warnings
from collections.abc import AsyncIterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol, TypeGuard, cast
from uuid import uuid4

from friday_core.interfaces.llm import ChatCompletionResponse
from friday_core.mcp import MCPIngestionPolicy, MCPToolCallProvenance
from friday_llm import (
    ChatCompletionRequest,
    FinishEvent,
    LiteLLMEmbeddingService,
    LiteLLMService,
    ReasoningDeltaEvent,
    ResilienceConfig,
    StreamErrorEvent,
    TextDeltaEvent,
    ToolCallCompleteEvent,
    ToolCallDeltaEvent,
    TypedChatCompletionResponse,
    UsageEvent,
    close_litellm_async_clients,
)
from friday_memory import (
    AccessBuffer,
    AccessBufferConfig,
    CollectionConfig,
    CollectionManager,
    DecayConfig,
    ElementXGraphStore,
    ExtractionCommitCompletedUnderCancellation,
    FactorComputerConfig,
    InMemoryEpisodicStore,
    InteractionTurn,
    MemoryController,
    MemoryExtractor,
    MemoryPromotionService,
    NullGraphStore,
    PassageRouter,
    PassageRouterConfig,
    RetrievalFactorComputer,
    SimpleVectorStore,
)
from friday_memory.context.budget_monitor import ContextBudgetMonitor
from friday_memory.ingestion.mcp import MCPMemoryIngester
from friday_memory.maintenance import (
    IncrementalGraphMaintainer,
    IncrementalMaintenanceConfig,
    InSessionCompactor,
    MemoryReorganizer,
)
from friday_memory.maintenance.models import (
    MaintenanceConfig as FrameworkMaintenanceConfig,
)
from friday_memory.models.budget import CompactionConfig
from friday_memory.models.mcp import MCPMemoryPreparation, MCPMemorySnapshot
from friday_memory.retrieval.mcp import (
    estimated_snippet_tokens,
    is_mcp_memory,
    mcp_memory_snippet,
)
from friday_runtime.transcript_queries import TranscriptQueryAdapter
from friday_runtime.transcript_tool_records import (
    build_transcript_tool_records,
    validate_transcript_tool_provenance,
)
from friday_telemetry import TelemetryInterface
from friday_telemetry.models.llm_events import ServiceRole
from friday_transcript import (
    ContextLogEntry,
    SQLiteTranscriptStore,
    TranscriptEntry,
    TranscriptSession,
)

from friday_chat.config import (
    FridayChatConfig,
    LegacyLLMExecutionConfig,
    PrimaryLLMExecutionConfig,
    TypedLLMExecutionConfig,
)
from friday_chat.memory_views import (
    MemoryCollection,
    MemoryDiagnosticReason,
    MemoryDiagnosticWarning,
    MemoryMetric,
    MemoryRecordKind,
    MemoryRecordQueryResult,
    MemoryRecordView,
    MemoryStoreComponent,
    MemoryStoreStatistics,
)
from friday_chat.reorganization.contracts import (
    ReorganizationError,
    ReorganizationErrorCode,
)
from friday_chat.reorganization.layout import FridayChatMaintenanceLayout
from friday_chat.reorganization.mutation import LifecycleStepReport
from friday_chat.runtime import (
    REORGANIZATION_EXECUTE_DISABLED_REASON,
    MCPTranscriptReceipt,
    PendingExtractionTurn,
)
from friday_chat.telemetry import ChatTelemetryObserver
from friday_chat.tools.schemas import ToolCallRecord, ToolDefinition
from friday_chat.tools.selection import ToolBudgetCalculator
from friday_chat.transcripts import (
    TranscriptContextLogView,
    TranscriptEntryView,
    TranscriptSessionView,
)
from friday_chat.turns.models import (
    ChatModelResponse,
    ToolCallRequest,
)
from friday_chat.turns.models import (
    InteractionTurn as ChatInteractionTurn,
)
from friday_chat.turns.telemetry import closing_stream, detached_scope, operation_scope

_MAX_SOURCE_PROVENANCE_CHARS = 32_000
_MAX_SOURCE_PROVENANCE_BYTES = 32_000
_MAX_VISIBLE_SOURCE_IDS = 8


class FridayChatStreamProtocolError(RuntimeError):
    """Raised when a typed stream cannot fit Chat's text-only boundary."""


class MCPSnapshotPublisher(Protocol):
    async def publish_mcp_snapshot(self, snapshot: MCPMemorySnapshot) -> bool: ...
    async def discard_mcp_snapshot(self, snapshot: MCPMemorySnapshot) -> bool: ...


@dataclass(frozen=True)
class FrameworkAsyncClientLifecycle:
    """Friday Chat adapter for Friday LLM's process-client lifecycle."""

    async def close(self) -> None:
        """Close process-scoped LiteLLM clients after runtime quiescence."""
        await close_litellm_async_clients()


@dataclass
class FrameworkChatModel:
    """Chat adapter backed by ``friday-llm`` LiteLLMService."""

    service: LiteLLMService
    config: FridayChatConfig
    execution: PrimaryLLMExecutionConfig

    async def complete(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ChatModelResponse:
        message_values = [dict(message) for message in messages]
        tool_values = [_to_openai_tool_schema(tool) for tool in tools] or None
        response: ChatCompletionResponse | TypedChatCompletionResponse
        if isinstance(self.execution, LegacyLLMExecutionConfig):
            response = await self.service.chat_completion(
                messages=message_values,
                tools=tool_values,
                temperature=self.execution.temperature,
                max_tokens=self.execution.max_tokens,
                timeout=self.config.llm.timeout_seconds,
            )
            usage = dict(response.usage)
        else:
            response = await self.service.chat_completion_request(
                ChatCompletionRequest(
                    messages=tuple(message_values),
                    tools=tuple(tool_values) if tool_values is not None else None,
                    tool_choice="auto" if tool_values else None,
                    provider_options=self.execution.provider_options,
                    timeout=self.config.llm.timeout_seconds,
                )
            )
            usage = {
                key: value
                for key, value in response.usage.model_dump().items()
                if value is not None
            }
        return ChatModelResponse(
            content=response.content or "",
            tool_calls=tuple(
                ToolCallRequest(
                    name=call.name,
                    arguments=dict(call.arguments),
                    call_id=call.id,
                )
                for call in response.tool_calls
            ),
            model=response.model,
            usage=usage,
            reasoning_content=response.reasoning_content,
            raw_response=response,
        )

    async def stream_complete(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> AsyncIterator[str]:
        message_values = [dict(message) for message in messages]
        tool_values = [_to_openai_tool_schema(tool) for tool in tools] or None
        if isinstance(self.execution, LegacyLLMExecutionConfig):
            legacy_iterator = aiter(self.service.chat_completion_stream(
                messages=message_values,
                tools=tool_values,
                temperature=self.execution.temperature,
                max_tokens=self.execution.max_tokens,
                timeout=self.config.llm.timeout_seconds,
            ))
            async with closing_stream(legacy_iterator):
                async for chunk in legacy_iterator:
                    yield chunk
            return

        request = ChatCompletionRequest(
            messages=tuple(message_values),
            tools=tuple(tool_values) if tool_values is not None else None,
            tool_choice="auto" if tool_values else None,
            provider_options=self.execution.provider_options,
            timeout=self.config.llm.timeout_seconds,
        )
        event_iterator = aiter(self.service.chat_completion_events(request))
        async with closing_stream(event_iterator):
            async for event in event_iterator:
                if isinstance(event, TextDeltaEvent):
                    yield event.text
                elif isinstance(event, (ReasoningDeltaEvent, UsageEvent, FinishEvent)):
                    continue
                elif isinstance(
                    event,
                    (ToolCallDeltaEvent, ToolCallCompleteEvent, StreamErrorEvent),
                ):
                    raise FridayChatStreamProtocolError(
                        "Friday Chat's text-only stream received a non-text tool event"
                    )
                else:
                    raise FridayChatStreamProtocolError(
                        "Friday Chat received an unknown typed stream event"
                    )


@dataclass
class FrameworkEmbeddingService:
    """Embedding adapter backed by ``friday-llm`` LiteLLMEmbeddingService."""

    service: LiteLLMEmbeddingService

    async def embed_text(self, text: str) -> list[float]:
        return cast(list[float], await self.service.embed_query(text))

    async def embed_query(self, text: str) -> list[float]:
        return cast(list[float], await self.service.embed_query(text))

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return cast(list[list[float]], await self.service.embed_documents(texts))


@dataclass
class FrameworkMemoryAdapter:
    """FridayV2 memory protocol adapter over ``friday-memory`` MemoryController."""

    controller: MemoryController
    collection_manager: CollectionManager
    config: FridayChatConfig
    session_id: str
    episodic_store: InMemoryEpisodicStore
    graph_store: ElementXGraphStore | NullGraphStore
    recovery_graph_store: ElementXGraphStore | None = None
    passage_router: PassageRouter | None = None
    access_buffer: AccessBuffer | None = None
    access_buffer_configured: bool = False
    observer: ChatTelemetryObserver | None = None

    async def retrieve(
        self,
        query: str,
        *,
        token_limit: int | None = None,
        include_mcp: bool = True,
    ) -> list[str]:
        resolved_token_limit = (
            token_limit
            if token_limit is not None
            else _dynamic_context_budget(self.config)
        )
        payload = await self._recall(
            query,
            token_limit=resolved_token_limit,
        )
        return _context_payload_to_snippets(
            payload, token_limit=resolved_token_limit, include_mcp=include_mcp
        )

    async def prepare_mcp_memory(
        self, call: ToolCallRecord, entry_id: str, policy: MCPIngestionPolicy
    ) -> MCPMemoryPreparation:
        facts = call.mcp_provenance
        if (facts is None or call.arguments or call.call_id != facts.call_id
                or call.name != facts.tool.canonical_name):
            return MCPMemoryPreparation("ineligible")
        return await MCPMemoryIngester(self.collection_manager).prepare(
            facts, call.result, entry_id, policy
        )

    async def verify_mcp_memory(
        self,
        call: ToolCallRecord,
        entry_id: str,
        policy: MCPIngestionPolicy,
        record_id: str,
    ) -> MCPMemoryPreparation:
        facts = call.mcp_provenance
        if (
            facts is None or call.arguments or call.call_id != facts.call_id
            or call.name != facts.tool.canonical_name
        ):
            return MCPMemoryPreparation("ineligible")
        return await MCPMemoryIngester(self.collection_manager).prepare(
            facts, call.result, entry_id, policy,
            record_id=record_id, stage_missing=False,
        )

    async def publish_mcp_memory(self, snapshot: MCPMemorySnapshot) -> bool:
        publisher: MCPSnapshotPublisher = self.collection_manager
        return await publisher.publish_mcp_snapshot(snapshot)

    async def discard_mcp_memory(self, snapshot: MCPMemorySnapshot) -> bool:
        publisher: MCPSnapshotPublisher = self.collection_manager
        return await publisher.discard_mcp_snapshot(snapshot)

    async def store_turn(self, user_message: str, assistant_message: str) -> None:
        await self.controller.add_turn(
            self.session_id,
            InteractionTurn(
                id=str(uuid4()),
                session_id=self.session_id,
                user_message=user_message,
                assistant_message=assistant_message,
                model_name=self.config.llm.model,
                temperature=self.config.llm.temperature,
            ),
        )

    async def clear_session_memory(self) -> bool:
        """Clear current-session episodic state through its public API."""
        return bool(await self.episodic_store.clear_session(self.session_id))

    async def ingest_document(
        self,
        *,
        source_path: str,
        description: str | None,
        content: str,
    ) -> int:
        with operation_scope(self.observer, "memory_ingest_document") as observation:
            count = await self._ingest_document(source_path=source_path, description=description, content=content)
            observation.count = count
            observation.count_kind = "chunks"
            return count

    async def _ingest_document(
        self,
        *,
        source_path: str,
        description: str | None,
        content: str,
    ) -> int:
        chunks = _chunk_text(
            content,
            chunk_size=self.config.smart_file.chunk_size or 2048,
            chunk_overlap=self.config.smart_file.chunk_overlap or 0,
        )
        if len(chunks) == 1:
            await self.controller.store_document(
                chunks[0],
                {
                    "source": source_path,
                    "description": description,
                    "type": "ingested_file",
                },
                protected=True,
            )
            return 1
        metadatas = [
            {
                "source": source_path,
                "description": description,
                "type": "ingested_file",
                "chunk_index": index,
                "chunk_count": len(chunks),
            }
            for index, _chunk in enumerate(chunks)
        ]
        await self.controller.store_documents_batch(chunks, metadatas, protected=True)
        return len(chunks)

    async def debug_retrieval(self, query: str) -> dict[str, Any]:
        payload = await self._recall(
            query,
            token_limit=_dynamic_context_budget(self.config),
        )
        return {
            "query": query,
            "snippets": _context_payload_to_snippets(payload),
            "debug_info": getattr(payload, "debug_info", {}),
        }

    async def list_entities(self, name: str | None = None) -> list[dict[str, Any]]:
        if name:
            found = await self.graph_store.find_by_label(name)
            return [found.model_dump(mode="json")] if found is not None else []
        nodes = await self.graph_store.get_all_nodes()
        return [node.model_dump(mode="json") for node in nodes]

    async def list_relationships(self, name: str | None = None) -> list[dict[str, Any]]:
        nodes = await self.graph_store.get_all_nodes()
        node_by_id = {str(node.id): node for node in nodes}
        edges = await self.graph_store.get_all_edges()
        records: list[dict[str, Any]] = []
        for edge in edges:
            source = node_by_id.get(str(edge.source_id))
            target = node_by_id.get(str(edge.target_id))
            source_label = str(getattr(source, "label", edge.source_id))
            target_label = str(getattr(target, "label", edge.target_id))
            relation = str(getattr(edge, "relation", ""))
            if name and not _relationship_matches_name(
                name,
                source_label,
                relation,
                target_label,
            ):
                continue
            record = edge.model_dump(mode="json")
            record["source_label"] = source_label
            record["target_label"] = target_label
            records.append(record)
        return records

    async def query_memory_statistics(self) -> MemoryStoreStatistics:
        """Aggregate honest store statistics through public component APIs."""
        warnings: list[MemoryDiagnosticWarning] = []

        try:
            episodic_turns = MemoryMetric.available(
                await self.episodic_store.get_turn_count(self.session_id)
            )
        except Exception:
            episodic_turns = MemoryMetric.unavailable(
                MemoryDiagnosticReason.STORE_READ_FAILED
            )
            warnings.append(MemoryDiagnosticWarning(MemoryStoreComponent.EPISODIC))

        vector_results = await asyncio.gather(
            self.collection_manager.short_term.count(),
            self.collection_manager.long_term.count(),
            self.collection_manager.decayed.count(),
            return_exceptions=True,
        )
        vector_components = (
            MemoryStoreComponent.VECTOR_SHORT_TERM,
            MemoryStoreComponent.VECTOR_LONG_TERM,
            MemoryStoreComponent.VECTOR_DECAYED,
        )
        vector_metrics: list[MemoryMetric[int]] = []
        for component, value in zip(vector_components, vector_results, strict=True):
            if isinstance(value, asyncio.CancelledError):
                raise value
            if isinstance(value, Exception) or not _is_nonnegative_int(value):
                vector_metrics.append(
                    MemoryMetric.unavailable(MemoryDiagnosticReason.STORE_READ_FAILED)
                )
                warnings.append(MemoryDiagnosticWarning(component))
            else:
                vector_metrics.append(MemoryMetric.available(value))
        short_term, long_term, decayed = vector_metrics
        vector_active_total = _sum_available_metrics(short_term, long_term)
        vector_total = _sum_available_metrics(short_term, long_term, decayed)

        if self.config.lifecycle.enabled:
            graph_results = await asyncio.gather(
                self.graph_store.get_all_nodes(),
                self.graph_store.get_all_edges(),
                return_exceptions=True,
            )
            for graph_value in graph_results:
                if isinstance(graph_value, asyncio.CancelledError):
                    raise graph_value
            graph_nodes = _length_metric(graph_results[0])
            graph_relationships = _length_metric(graph_results[1])
            if any(isinstance(value, Exception) for value in graph_results):
                warnings.append(MemoryDiagnosticWarning(MemoryStoreComponent.GRAPH))
        else:
            graph_nodes = MemoryMetric.not_configured()
            graph_relationships = MemoryMetric.not_configured()

        access_buffer_entries: MemoryMetric[int]
        access_buffer_accesses: MemoryMetric[int]
        if not self.access_buffer_configured:
            access_buffer_entries = MemoryMetric.not_configured()
            access_buffer_accesses = MemoryMetric.not_configured()
        elif self.access_buffer is None:
            access_buffer_entries = MemoryMetric.unavailable(
                MemoryDiagnosticReason.COMPONENT_INITIALIZATION_FAILED
            )
            access_buffer_accesses = MemoryMetric.unavailable(
                MemoryDiagnosticReason.COMPONENT_INITIALIZATION_FAILED
            )
            warnings.append(MemoryDiagnosticWarning(MemoryStoreComponent.ACCESS_BUFFER))
        else:
            try:
                access_stats = self.access_buffer.get_stats()
                access_buffer_entries = MemoryMetric.available(
                    access_stats["short_term_memories"]
                    + access_stats["long_term_memories"]
                )
                access_buffer_accesses = MemoryMetric.available(
                    access_stats["short_term_accesses"]
                    + access_stats["long_term_accesses"]
                )
            except Exception:
                access_buffer_entries = MemoryMetric.unavailable(
                    MemoryDiagnosticReason.STORE_READ_FAILED
                )
                access_buffer_accesses = MemoryMetric.unavailable(
                    MemoryDiagnosticReason.STORE_READ_FAILED
                )
                warnings.append(
                    MemoryDiagnosticWarning(MemoryStoreComponent.ACCESS_BUFFER)
                )

        try:
            priming_info = self.controller.get_priming_info(self.session_id)
            priming_enabled_value = priming_info.get("enabled")
            if not isinstance(priming_enabled_value, bool):
                raise TypeError("priming enabled state is malformed")
            priming_enabled = MemoryMetric.available(priming_enabled_value)
        except Exception:
            priming_enabled = MemoryMetric.unavailable(
                MemoryDiagnosticReason.STORE_READ_FAILED
            )
            warnings.append(MemoryDiagnosticWarning(MemoryStoreComponent.PRIMING))
        configured_previous_sessions = _nonnegative_mapping_int(
            self.config.memory.priming,
            "previous_sessions",
            0,
        )
        priming_previous_sessions: MemoryMetric[int]
        if configured_previous_sessions is None:
            priming_previous_sessions = MemoryMetric.unavailable(
                MemoryDiagnosticReason.CONFIG_VALUE_INVALID
            )
            if not any(
                warning.component is MemoryStoreComponent.PRIMING
                for warning in warnings
            ):
                warnings.append(
                    MemoryDiagnosticWarning(
                        MemoryStoreComponent.PRIMING,
                        MemoryDiagnosticReason.CONFIG_VALUE_INVALID,
                    )
                )
        else:
            priming_previous_sessions = MemoryMetric.available(
                configured_previous_sessions
            )

        return MemoryStoreStatistics(
            episodic_turns=episodic_turns,
            vector_short_term=short_term,
            vector_long_term=long_term,
            vector_decayed=decayed,
            vector_active_total=vector_active_total,
            vector_total=vector_total,
            graph_nodes=graph_nodes,
            graph_relationships=graph_relationships,
            lifecycle_enabled=MemoryMetric.available(self.config.lifecycle.enabled),
            access_buffer_entries=access_buffer_entries,
            access_buffer_accesses=access_buffer_accesses,
            priming_enabled=priming_enabled,
            priming_previous_sessions=priming_previous_sessions,
            warnings=tuple(warnings),
        )

    async def query_memory_records(
        self,
        kind: MemoryRecordKind,
    ) -> MemoryRecordQueryResult:
        """Query active lifecycle collections without including decayed records."""
        results = await asyncio.gather(
            self.collection_manager.short_term.get_all(
                limit=None,
                where={"type": kind.value},
            ),
            self.collection_manager.long_term.get_all(
                limit=None,
                where={"type": kind.value},
            ),
            return_exceptions=True,
        )
        warnings: list[MemoryDiagnosticWarning] = []
        records: list[MemoryRecordView] = []
        collections = (MemoryCollection.SHORT_TERM, MemoryCollection.LONG_TERM)
        for collection, result in zip(collections, results, strict=True):
            if isinstance(result, BaseException):
                if isinstance(result, asyncio.CancelledError) or not isinstance(
                    result, Exception
                ):
                    raise result
                warnings.append(
                    MemoryDiagnosticWarning(
                        MemoryStoreComponent.VECTOR_SHORT_TERM
                        if collection is MemoryCollection.SHORT_TERM
                        else MemoryStoreComponent.VECTOR_LONG_TERM
                    )
                )
                continue
            malformed = False
            for record in result:
                view = _memory_record_view(record, kind=kind, collection=collection)
                if view is None:
                    malformed = True
                else:
                    records.append(view)
            if malformed:
                warnings.append(
                    MemoryDiagnosticWarning(MemoryStoreComponent.MEMORY_RECORD)
                )
        records.sort(key=_memory_record_sort_key, reverse=True)
        return MemoryRecordQueryResult(
            kind=kind,
            records=tuple(records[:100]),
            warnings=tuple(warnings),
            decayed_records_excluded=True,
        )

    async def _recall(self, query: str, *, token_limit: int) -> Any:
        payload = await self.controller.recall(
            query,
            session_id=self.session_id,
            token_limit=token_limit,
            include_history=True,
            history_limit=self.config.memory.max_history_turns or 10,
            vector_results=_int_from_mapping(
                self.config.memory.retrieval,
                "default_n_results",
                5,
            ),
            semantic_retrieval=True,
        )
        if self.passage_router is None:
            return payload
        return await _apply_passage_routing(payload, query, self.passage_router)


@dataclass
class FrameworkMaintenanceAdapter:
    """Maintenance adapter backed by ``friday-memory`` runtime services."""

    config: FridayChatConfig
    session_id: str
    memory: FrameworkMemoryAdapter
    embedding: FrameworkEmbeddingService
    llm_service: LiteLLMService
    llm_models: dict[str, str]
    llm_services: Mapping[str, LiteLLMService]
    promotion_service: MemoryPromotionService | None = None
    access_buffer: AccessBuffer | None = None
    factor_computer: RetrievalFactorComputer | None = None
    incremental_maintainer: IncrementalGraphMaintainer | None = None
    budget_monitor: ContextBudgetMonitor | None = None
    compactor: InSessionCompactor | None = None
    extractor: MemoryExtractor | None = None
    actions: list[str] = field(default_factory=list)
    reset_calls: list[str] = field(default_factory=list)
    archived_transcripts: bool = False
    pending_extraction: list[PendingExtractionTurn] = field(default_factory=list)
    flush_pending_error: BaseException | None = None
    background_actions: list[str] = field(default_factory=list)
    compaction_running: bool = False
    compaction_calls: list[dict[str, Any]] = field(default_factory=list)
    errors: list[BaseException] = field(default_factory=list)
    migration_needed: bool = False
    observer: ChatTelemetryObserver | None = None

    async def flush_memory(self) -> None:
        """Flush memory buffers."""
        self._raise_next_error()
        if self.access_buffer is not None and self.promotion_service is not None:
            await self.access_buffer.flush_all(
                short_term_collection=self.promotion_service.collection_manager.short_term,
                long_term_collection=self.promotion_service.collection_manager.long_term,
            )
        self.actions.append("flush_memory")

    async def run_lifecycle(self) -> None:
        """Run lifecycle maintenance."""
        self._raise_next_error()
        if self.promotion_service is not None:
            result = await self.promotion_service.run_promotion_cycle(dry_run=False)
            if result.errors:
                raise RuntimeError("lifecycle promotion reported errors")
        self.actions.append("run_lifecycle")

    async def preview_reorganization_lifecycle(self) -> LifecycleStepReport:
        """Report promotion/decay scope without mutation or embedding backfill."""
        if self.promotion_service is None:
            return LifecycleStepReport(
                succeeded=False,
                errors=(
                    ReorganizationError(
                        code=ReorganizationErrorCode.CAPABILITY_UNAVAILABLE,
                        message="deterministic lifecycle promotion is unavailable",
                    ),
                ),
            )
        stats = await self.promotion_service.collection_manager.get_stats()
        return LifecycleStepReport(
            succeeded=True,
            scanned_count=sum(
                int(value) for value in stats.values() if isinstance(value, int)
            ),
            candidate_count=None,
            changed_count=None,
            warnings=(
                "lifecycle candidate and change counts are unavailable before execution",
            ),
        )

    async def run_reorganization_lifecycle(self) -> LifecycleStepReport:
        """Run promotion/decay only; never backfill graph edge embeddings."""
        self._raise_next_error()
        if self.promotion_service is None:
            return LifecycleStepReport(
                succeeded=False,
                errors=(
                    ReorganizationError(
                        code=ReorganizationErrorCode.CAPABILITY_UNAVAILABLE,
                        message="deterministic lifecycle promotion is unavailable",
                    ),
                ),
            )
        stats = await self.promotion_service.collection_manager.get_stats()
        result = await self.promotion_service.run_promotion_cycle(dry_run=False)
        if result.errors:
            return LifecycleStepReport(
                succeeded=False,
                scanned_count=sum(
                    int(value) for value in stats.values() if isinstance(value, int)
                ),
                errors=(
                    ReorganizationError(
                        code=ReorganizationErrorCode.MUTATION_FAILED,
                        message="deterministic lifecycle promotion reported errors",
                    ),
                ),
            )
        changed_count = (
            result.promoted_to_long_term
            + result.decayed_from_long_term
            + result.reactivated
        )
        self.actions.append("run_reorganization_lifecycle")
        return LifecycleStepReport(
            succeeded=True,
            scanned_count=sum(
                int(value) for value in stats.values() if isinstance(value, int)
            ),
            candidate_count=None,
            changed_count=changed_count,
        )

    def reorganization_execute_status(self) -> tuple[bool, str]:
        """Keep legacy direct mutation outside the Chat coordinator disabled."""
        return False, REORGANIZATION_EXECUTE_DISABLED_REASON

    async def reorganize_memory(self, mode: str) -> None:
        """Run full framework memory reorganization."""
        persist_directory = self.config.memory.persist_directory
        if not persist_directory:
            self.actions.append("reorganize_skipped:no_persist_directory")
            return
        memory_dir = Path(persist_directory)
        if not memory_dir.exists():
            self.actions.append("reorganize_skipped:no_persist_directory")
            return

        allowed, reason = self.reorganization_execute_status()
        if not allowed:
            self.actions.append("reorganize_skipped:execute_disabled")
            self.background_actions.append(f"reorganize_execute_disabled:{reason}")
            return

        self._raise_next_error()

        skip_llm_work = mode == "fast"
        reorganizer = MemoryReorganizer(
            memory_dir=memory_dir,
            config=_framework_maintenance_config(self.config),
            llm_service=self.llm_services.get("synthesizer", self.llm_service),
            classifier_llm=self.llm_services.get("classifier", self.llm_service),
            researcher_llm=self.llm_services.get("researcher", self.llm_service),
            judge_llm=self.llm_services.get("judge", self.llm_service),
            embedding_function=self.embedding,
            collection_name=self.config.memory.collection_name,
            collection_manager=self.memory.collection_manager,
            access_buffer=self.access_buffer,
            factor_computer=self.factor_computer,
            promotion_scorer=(
                self.promotion_service.promotion_scorer
                if self.promotion_service is not None
                else None
            ),
            decay_calculator=(
                self.promotion_service.decay_calculator
                if self.promotion_service is not None
                else None
            ),
            graph_store=self.memory.controller.graph,
        )
        report = await reorganizer.reorganize(
            backup_first=True,
            dry_run=False,
            skip_synthesis=skip_llm_work,
            skip_verify=skip_llm_work,
            skip_lifecycle=True,
        )
        self.actions.append(f"reorganize_memory:{mode}")
        self.background_actions.append(f"reorganize_report:{type(report).__name__}")

    async def flush_pending_extraction(self) -> int:
        """Flush buffered extraction turns before compaction or shutdown."""
        self._raise_next_error()
        if self.flush_pending_error is not None:
            raise self.flush_pending_error
        if not self.pending_extraction:
            with operation_scope(self.observer, "memory_extract") as observation:
                observation.outcome = "skipped"
                observation.count = 0
                observation.count_kind = "turns"
            self.actions.append("flush_pending_extraction")
            return 0
        pending = list(self.pending_extraction)
        self.pending_extraction.clear()
        await self._extract_turns(pending)
        self.actions.append("flush_pending_extraction")
        return len(pending)

    async def extract_buffered_turns(self, *, trigger_reason: str) -> int:
        """Extract all currently buffered turns."""
        self._raise_next_error()
        if self.flush_pending_error is not None:
            raise self.flush_pending_error
        if not self.pending_extraction:
            with operation_scope(self.observer, "memory_extract") as observation:
                observation.outcome = "skipped"
                observation.count = 0
                observation.count_kind = "turns"
            self.background_actions.append(f"extract:{trigger_reason}:0")
            return 0
        pending = list(self.pending_extraction)
        self.pending_extraction.clear()
        await self._extract_turns(pending)
        self.background_actions.append(f"extract:{trigger_reason}:{len(pending)}")
        return len(pending)

    async def run_tool_decay(self) -> None:
        """Run tool-content lifecycle decay if available."""
        self.background_actions.append("tool_decay")

    async def run_incremental_graph_maintenance(self) -> None:
        """Run incremental graph maintenance if available."""
        if self.incremental_maintainer is not None:
            result = await self.incremental_maintainer.run_maintenance(self.session_id)
            self.background_actions.append(
                "incremental_graph_maintenance:"
                f"merged={result.entities_merged}:orphans={result.orphans_removed}"
            )
            return
        self.background_actions.append("incremental_graph_maintenance")

    async def compact(
        self,
        *,
        trigger_reason: str,
        time_budget_ms: int | None = None,
        current_tokens: int | None = None,
        available_budget: int | None = None,
        target_utilization: float | None = None,
    ) -> dict[str, Any]:
        """Run real in-session compaction."""
        self._raise_next_error()
        if self.compactor is None:
            raise RuntimeError("Compaction service is not configured.")
        resolved_time_budget = time_budget_ms or 15000
        resolved_current_tokens = current_tokens or 0
        resolved_available_budget = available_budget or 0
        resolved_target = target_utilization or 0.70
        self.compaction_running = True
        try:
            result = await self.compactor.run_compaction(
                session_id=self.session_id,
                time_budget_ms=resolved_time_budget,
                trigger_reason=trigger_reason,
                current_tokens=resolved_current_tokens,
                available_budget=resolved_available_budget,
                target_utilization=resolved_target,
            )
            self.actions.append("compact")
            payload = _compaction_result_to_dict(
                result,
                trigger_reason=trigger_reason,
                time_budget_ms=resolved_time_budget,
                current_tokens=resolved_current_tokens,
                available_budget=resolved_available_budget,
                target_utilization=resolved_target,
            )
            self.compaction_calls.append(payload)
            return payload
        finally:
            self.compaction_running = False

    async def reset_store(self, store: str) -> str:
        """Reset hook retained for command compatibility."""
        self._raise_next_error()
        self.reset_calls.append(store)
        return f"reset {store}"

    async def archive_transcripts(self) -> None:
        """Archive transcript hook retained for command compatibility."""
        self._raise_next_error()
        self.archived_transcripts = True
        self.actions.append("archive_transcripts")

    async def lifecycle(self, *, mode: str, dry_run: bool) -> dict[str, Any]:
        """Run the framework lifecycle command surface."""
        self._raise_next_error()
        if self.promotion_service is None:
            raise RuntimeError("Lifecycle service is not configured.")

        if mode == "stats":
            stats = await self.promotion_service.collection_manager.get_stats()
            return {
                "mode": mode,
                "dry_run": dry_run,
                "promoted": 0,
                "decayed": 0,
                "reactivated": 0,
                "short_term": int(stats.get("short_term", 0)),
                "long_term": int(stats.get("long_term", 0)),
                "decayed_count": int(stats.get("decayed", 0)),
                "access_buffer": _access_buffer_count(self.access_buffer),
                "errors": [],
            }

        if mode == "flush":
            if self.access_buffer is None:
                raise RuntimeError("Lifecycle access buffer is not configured.")
            flush_result = await self.access_buffer.flush_all(
                short_term_collection=self.promotion_service.collection_manager.short_term,
                long_term_collection=self.promotion_service.collection_manager.long_term,
            )
            self.actions.append(f"lifecycle:{mode}")
            return {
                "mode": mode,
                "dry_run": dry_run,
                "promoted": 0,
                "decayed": 0,
                "reactivated": 0,
                "short_term": 0,
                "long_term": 0,
                "decayed_count": 0,
                "access_buffer": (
                    flush_result.short_term_flushed + flush_result.long_term_flushed
                ),
                "errors": list(flush_result.errors),
            }

        if mode == "optimize":
            flushed = 0
            errors: list[str] = []
            if self.access_buffer is not None:
                flush_result = await self.access_buffer.flush_all(
                    short_term_collection=(
                        self.promotion_service.collection_manager.short_term
                    ),
                    long_term_collection=self.promotion_service.collection_manager.long_term,
                )
                flushed = (
                    flush_result.short_term_flushed + flush_result.long_term_flushed
                )
                errors.extend(flush_result.errors)
            if self.factor_computer is not None:
                factor_result = await self.factor_computer.compute_factors(
                    self.promotion_service.collection_manager.long_term,
                    force_update=True,
                )
                errors.extend(factor_result.errors)
            stats = await self.promotion_service.collection_manager.get_stats()
            self.actions.append(f"lifecycle:{mode}")
            return {
                "mode": mode,
                "dry_run": dry_run,
                "promoted": 0,
                "decayed": 0,
                "reactivated": 0,
                "short_term": int(stats.get("short_term", 0)),
                "long_term": int(stats.get("long_term", 0)),
                "decayed_count": int(stats.get("decayed", 0)),
                "access_buffer": flushed,
                "errors": errors,
            }

        result = await self.promotion_service.run_promotion_cycle(dry_run=dry_run)
        stats = await self.promotion_service.collection_manager.get_stats()
        self.actions.append(f"lifecycle:{mode}")
        return {
            "mode": mode,
            "dry_run": dry_run,
            "promoted": result.promoted_to_long_term,
            "decayed": result.decayed_from_long_term,
            "reactivated": result.reactivated,
            "short_term": int(stats.get("short_term", 0)),
            "long_term": int(stats.get("long_term", 0)),
            "decayed_count": int(stats.get("decayed", 0)),
            "access_buffer": _access_buffer_count(self.access_buffer),
            "errors": list(result.errors),
        }

    async def reorganize(
        self,
        *,
        mode: str,
        dry_run: bool,
        backup_first: bool,
        skip_synthesis: bool = False,
        skip_verify: bool = False,
        skip_lifecycle: bool = False,
        force_reembed: bool = False,
    ) -> dict[str, Any]:
        """Manual reorganization command hook."""
        persist_directory = self.config.memory.persist_directory
        if not persist_directory:
            return {
                "mode": mode,
                "dry_run": dry_run,
                "backup_first": backup_first,
                "skip_synthesis": skip_synthesis,
                "skip_verify": skip_verify,
                "skip_lifecycle": skip_lifecycle,
                "force_reembed": force_reembed,
                "scanned": 0,
                "changed": 0,
                "errors": ["No persistence directory configured."],
            }
        if not dry_run:
            allowed, reason = self.reorganization_execute_status()
            if not allowed:
                self.actions.append(f"reorganize:{mode}:execute_disabled")
                return {
                    "mode": mode,
                    "dry_run": dry_run,
                    "backup_first": backup_first,
                    "skip_synthesis": skip_synthesis,
                    "skip_verify": skip_verify,
                    "skip_lifecycle": skip_lifecycle,
                    "force_reembed": force_reembed,
                    "scanned": 0,
                    "changed": 0,
                    "errors": [f"Execute disabled: {reason}"],
                }
        self._raise_next_error()
        memory_dir = Path(persist_directory)
        reorganizer = MemoryReorganizer(
            memory_dir=memory_dir,
            config=_framework_maintenance_config(self.config),
            llm_service=self.llm_services.get("synthesizer", self.llm_service),
            classifier_llm=self.llm_services.get("classifier", self.llm_service),
            researcher_llm=self.llm_services.get("researcher", self.llm_service),
            judge_llm=self.llm_services.get("judge", self.llm_service),
            embedding_function=self.embedding,
            collection_name=self.config.memory.collection_name,
            collection_manager=self.memory.collection_manager,
            access_buffer=self.access_buffer,
            factor_computer=self.factor_computer,
            promotion_scorer=(
                self.promotion_service.promotion_scorer
                if self.promotion_service is not None
                else None
            ),
            decay_calculator=(
                self.promotion_service.decay_calculator
                if self.promotion_service is not None
                else None
            ),
            graph_store=self.memory.controller.graph,
        )
        report = await reorganizer.reorganize(
            backup_first=backup_first,
            dry_run=dry_run,
            skip_synthesis=skip_synthesis,
            skip_verify=skip_verify,
            skip_lifecycle=skip_lifecycle,
            force_reembed=force_reembed,
        )
        self.actions.append(f"reorganize:{mode}")
        return {
            "mode": mode,
            "dry_run": dry_run,
            "backup_first": backup_first,
            "skip_synthesis": skip_synthesis,
            "skip_verify": skip_verify,
            "skip_lifecycle": skip_lifecycle,
            "force_reembed": force_reembed,
            "scanned": getattr(report, "total_items_scanned", 0),
            "changed": getattr(report, "total_items_changed", 0),
            "errors": list(getattr(report, "errors", []) or []),
        }

    async def migrate(self, *, execute: bool) -> dict[str, Any]:
        """Migration command hook retained for command compatibility."""
        self._raise_next_error()
        self.actions.append(f"migrate:{'execute' if execute else 'dry-run'}")
        return {
            "needed": False,
            "vector_scanned": 0,
            "graph_nodes_scanned": 0,
            "graph_edges_scanned": 0,
            "migrated": 0,
            "skipped": 0,
            "errors": [],
        }

    def _raise_next_error(self) -> None:
        if self.errors:
            raise self.errors.pop(0)

    async def _extract_turns(self, turns: list[PendingExtractionTurn]) -> None:
        if self.extractor is None:
            for turn in turns:
                with detached_scope(self.observer), operation_scope(self.observer, "memory_extract", origin=turn.correlation_context) as observation:
                    observation.outcome = "skipped"
                    observation.reason = "unavailable"
                    observation.count = 0
                    observation.count_kind = "turns"
            return
        for index, pending_turn in enumerate(turns):
            try:
                with detached_scope(self.observer), operation_scope(self.observer, "memory_extract", origin=pending_turn.correlation_context) as observation:
                    try:
                        result = await self.extractor.extract(
                            InteractionTurn(
                                id=pending_turn.turn_id,
                                session_id=self.session_id,
                                user_message=pending_turn.user_message,
                                assistant_message=pending_turn.assistant_message,
                                model_name=self.config.llm.model,
                                temperature=self.config.llm.temperature,
                            )
                        )
                        if isinstance(result, Mapping) and result.get("error"):
                            raise RuntimeError(
                                f"Memory extraction failed: {result['error']}"
                            )
                    except ExtractionCommitCompletedUnderCancellation:
                        observation.persistence_state = "completed"
                        raise
                    observation.count = 1
                    observation.count_kind = "turns"
                    observation.persistence_state = "completed"
            except ExtractionCommitCompletedUnderCancellation:
                self.pending_extraction[:0] = turns[index + 1 :]
                raise asyncio.CancelledError from None
            except asyncio.CancelledError:
                self.pending_extraction[:0] = turns[index:]
                raise
            except Exception:
                self.pending_extraction[:0] = turns[index:]
                raise


@dataclass
class FrameworkTranscriptAdapter:
    """FridayV2 transcript protocol adapter over SQLiteTranscriptStore."""

    store: SQLiteTranscriptStore
    config: FridayChatConfig
    session_id: str
    _turn_number: int | None = None
    _pending_context_log: tuple[str, str] | None = None

    async def record_turn(self, user_message: str, assistant_message: str) -> None:
        """Keep protocol compatibility; rich interaction write owns persistence."""
        return None

    async def record_interaction(self, turn: ChatInteractionTurn) -> None:
        provenance = validate_transcript_tool_provenance(
            turn.turn_id,
            turn.tool_calls,
            self.config.tools.mcp_provider.config.limits.max_result_bytes,
        )
        await self._ensure_session()
        turn_number = await self._next_turn_number()
        tool_calls, tool_results = build_transcript_tool_records(
            turn.turn_id, turn.tool_calls, provenance
        )
        entry = TranscriptEntry(
            id=turn.turn_id,
            session_id=self.session_id,
            turn_number=turn_number,
            user_message=turn.user_message,
            assistant_message=turn.assistant_message,
            tool_calls=tool_calls,
            tool_results=tool_results,
            timestamp=datetime.now(),
            model_name=self.config.llm.model,
            temperature=self.config.llm.temperature,
            latency_ms=(
                turn.metrics.total_seconds * 1000 if turn.metrics is not None else None
            ),
            metadata={
                "raw_prompt_captured": turn.raw_prompt_captured,
                "memory_snippets": list(turn.memory_snippets),
            },
        )
        if not await self.store.append_entry(entry):
            raise RuntimeError("Failed to append transcript entry.")
        if self._pending_context_log is not None:
            prompt, raw_response = self._pending_context_log
            await self.store.store_context_log(
                ContextLogEntry(
                    session_id=self.session_id,
                    turn_number=turn_number,
                    entry_id=turn.turn_id,
                    raw_prompt=prompt,
                    raw_response=raw_response,
                )
            )
            self._pending_context_log = None
        self._turn_number = turn_number

    async def record_mcp_interaction(self, turn: ChatInteractionTurn) -> MCPTranscriptReceipt:
        """Confirm the real append and matching per-call result facts by readback."""
        await self.record_interaction(turn)
        receipt = await self.read_mcp_interaction(turn)
        expected = tuple(c.mcp_provenance for c in turn.tool_calls if c.mcp_provenance is not None)
        if receipt is None or receipt.calls != expected:
            raise RuntimeError("MCP transcript receipt is inconsistent.")
        return receipt

    async def read_mcp_interaction(
        self, turn: ChatInteractionTurn
    ) -> MCPTranscriptReceipt | None:
        """Match the complete safe interaction against an immutable public entry."""
        entry = await self.store.get_entry(turn.turn_id)
        if entry is None:
            return None
        if (
            entry.session_id != self.session_id
            or entry.user_message != turn.user_message
            or entry.assistant_message != turn.assistant_message
            or entry.model_name != self.config.llm.model
            or entry.temperature != self.config.llm.temperature
            or entry.latency_ms != turn.metrics.total_seconds * 1000
            or entry.metadata != {
                "raw_prompt_captured": turn.raw_prompt_captured,
                "memory_snippets": list(turn.memory_snippets),
            }
            or len(entry.tool_calls) != len(turn.tool_calls)
            or len(entry.tool_results) != len(turn.tool_calls)
        ):
            raise RuntimeError("MCP transcript receipt is inconsistent.")
        actual: list[MCPToolCallProvenance] = []
        for index, (supplied, call, result) in enumerate(
            zip(turn.tool_calls, entry.tool_calls, entry.tool_results, strict=True)
        ):
            expected_id = supplied.call_id or f"{turn.turn_id}:{index}:{supplied.name}"
            facts = call.mcp_provenance
            supplied_facts = supplied.mcp_provenance
            if (
                call.id != expected_id
                or call.name != supplied.name
                or call.arguments != supplied.arguments
                or result.tool_call_id != call.id
                or result.output != supplied.result
                or (facts is None) != (supplied_facts is None)
                or result.mcp_provenance != facts
                or result.error != (facts.failure_code if facts is not None else None)
            ):
                raise RuntimeError("MCP transcript receipt is inconsistent.")
            if facts is None or supplied_facts is None:
                continue
            excluded = {
                "ingestion_decision", "memory_ingested", "memory_correlation_id",
                "transcript_correlation_id",
            }
            if (
                facts.transcript_correlation_id != entry.id
                or facts.model_dump(exclude=excluded)
                != supplied_facts.model_dump(exclude=excluded)
            ):
                raise RuntimeError("MCP transcript receipt is inconsistent.")
            actual.append(facts)
        return MCPTranscriptReceipt(entry.id, tuple(actual))

    async def record_context_log(self, prompt: str, raw_response: str) -> None:
        self._pending_context_log = (prompt, raw_response)

    async def finalize(self) -> None:
        await self.store.end_session(self.session_id)

    async def query_sessions(
        self,
        *,
        limit: int = 1000,
        include_archived: bool = False,
    ) -> tuple[TranscriptSessionView, ...]:
        return await TranscriptQueryAdapter(self.store).query_sessions(
            limit=limit,
            include_archived=include_archived,
        )

    async def query_session(self, session_id: str) -> TranscriptSessionView | None:
        return await TranscriptQueryAdapter(self.store).query_session(session_id)

    async def query_entries(
        self,
        session_id: str,
    ) -> tuple[TranscriptEntryView, ...]:
        return await TranscriptQueryAdapter(self.store).query_entries(session_id)

    async def query_context_logs(
        self,
        session_id: str,
    ) -> tuple[TranscriptContextLogView, ...]:
        return await TranscriptQueryAdapter(self.store).query_context_logs(session_id)

    async def _ensure_session(self) -> None:
        session = await self.store.get_session(self.session_id)
        if session is not None:
            return
        await self.store.create_session(
            TranscriptSession(
                session_id=self.session_id,
                user_id=self.config.chat.user_name,
                model_name=self.config.llm.model or "unknown",
                system_prompt=self.config.chat.system_prompt,
                # MCP launch/connection material is runtime-only. Exclude the
                # whole stanza from this new diagnostic copy, preserving the
                # original config and all native provider snapshot behavior.
                config_snapshot=self.config.model_dump(
                    mode="json", exclude={"tools": {"providers": {"mcp"}}}
                ),
            )
        )

    async def _next_turn_number(self) -> int:
        if self._turn_number is None:
            self._turn_number = await self.store.count_entries(self.session_id)
        return self._turn_number + 1


@dataclass
class FrameworkToolRegistryAdapter:
    """Tool registry adapter for configured ``friday-tools`` classes."""

    tools: Mapping[str, Any]
    definitions: tuple[ToolDefinition, ...]
    calls: list[tuple[str, dict[str, Any], str]] = field(default_factory=list)

    def list_tools(self) -> tuple[ToolDefinition, ...]:
        return self.definitions

    def get_context_block(self) -> str:
        lines = ["Available tools:"]
        for tool in self.definitions:
            lines.append(f"- {tool.name}: {tool.description}")
        return "\n".join(lines)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        tool = self.tools.get(name)
        if tool is None:
            raise KeyError(f"Unknown tool: {name}")
        result = await tool.execute(**arguments)
        text = str(result)
        self.calls.append((name, arguments, text))
        return text


@dataclass
class FrameworkWorkflowAdapter:
    """Workflow command adapter over ``friday-agent`` legacy workflow APIs."""

    loader: Any
    engine: Any
    active_workflow: Any | None = None
    active_execution: Any | None = None

    def list_workflows(self) -> dict[str, str]:
        descriptions: dict[str, str] = {}
        for name in self.loader.list_workflows():
            descriptions[name] = self._describe_workflow(name)
        return descriptions

    async def run_workflow(self, name: str, arguments: Mapping[str, Any]) -> str:
        workflow = self.loader.load(name)
        execution = await self.engine.execute(workflow, dict(arguments))
        self.active_workflow = workflow
        self.active_execution = execution
        return _format_workflow_execution(workflow, execution)

    def status(self) -> str:
        if self.active_workflow is None or self.active_execution is None:
            return "No active workflow. Use /workflow run <name> to start one."
        status = self.engine.get_workflow_status(
            self.active_workflow,
            self.active_execution,
        )
        return _format_workflow_status(status)

    async def approve(self, approval_id: str | None = None) -> str:
        if self.active_workflow is None or self.active_execution is None:
            return "No active workflow. Use /workflow run <name> to start one."
        task_id = approval_id or self.active_execution.pending_approval
        if not task_id:
            return "No pending approval."
        self.active_execution = await self.engine.approve_task(
            self.active_workflow,
            self.active_execution,
            task_id,
        )
        return f"Approved {task_id}.\n{self.status()}"

    async def skip(self, approval_id: str | None = None) -> str:
        if self.active_workflow is None or self.active_execution is None:
            return "No active workflow. Use /workflow run <name> to start one."
        task_id = approval_id or self.active_execution.pending_approval
        if not task_id:
            return "No pending approval."
        self.active_execution = await self.engine.skip_task(
            self.active_workflow,
            self.active_execution,
            task_id,
        )
        return f"Skipped {task_id}.\n{self.status()}"

    def _describe_workflow(self, name: str) -> str:
        try:
            workflow = self.loader.load(name)
            description = getattr(workflow, "description", "")
            return str(description or "No description.")
        except Exception:
            try:
                bundle = self.loader.load_canonical(name)
                goal = getattr(bundle.workflow, "goal", "")
                return str(goal or "No description.")
            except Exception as exc:
                return f"Unable to load workflow metadata: {exc}"


def build_framework_chat_model(config: FridayChatConfig, *, telemetry: TelemetryInterface | None = None) -> FrameworkChatModel:
    if config.llm_pool is not None:
        spec = config.llm_service_specs[config.llm_pool.default_service]
        service = LiteLLMService.from_spec(spec, telemetry=telemetry, service_role="primary")
        canonical_execution = TypedLLMExecutionConfig(
            generation=spec.generation_defaults,
            transport_target=spec.execution_target.transport,
            model_target=spec.execution_target.model,
            provider_options=spec.provider_options_defaults,
        )
        return FrameworkChatModel(
            service=service,
            config=config,
            execution=canonical_execution,
        )

    execution = config.llm.resolve_execution()
    resilience = ResilienceConfig(
        max_retries=config.llm.max_retries,
        timeout_seconds=config.llm.timeout_seconds or 30.0,
    )
    if isinstance(execution, TypedLLMExecutionConfig):
        service = LiteLLMService(
            model_name=config.llm.model or "unknown",
            api_key=config.llm.api_key,
            api_base=config.llm.api_base,
            resilience=resilience,
            transport_target=execution.transport_target,
            model_target=execution.model_target,
            generation_defaults=execution.generation,
            telemetry=telemetry, service_role="primary",
        )
    else:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=(
                    "thinking_enabled is deprecated; use "
                    "generation_defaults.reasoning"
                ),
                category=DeprecationWarning,
            )
            service = LiteLLMService(
                model_name=config.llm.model or "unknown",
                api_key=config.llm.api_key,
                api_base=config.llm.api_base,
                resilience=resilience,
                thinking_enabled=execution.thinking_enabled,
                telemetry=telemetry, service_role="primary",
            )
    return FrameworkChatModel(service=service, config=config, execution=execution)


def build_framework_async_client_lifecycle() -> FrameworkAsyncClientLifecycle:
    """Build the real process-client lifecycle adapter."""
    return FrameworkAsyncClientLifecycle()


def _build_legacy_primary_llm_service(config: FridayChatConfig, *, telemetry: TelemetryInterface | None = None) -> LiteLLMService:
    """Build the unchanged fallback used by non-primary Chat consumers."""
    if config.llm_pool is not None:
        return LiteLLMService.from_spec(
            config.llm_service_specs[config.llm_pool.default_service],
            telemetry=telemetry, service_role="maintenance_default",
        )
    thinking_enabled = (
        config.llm.thinking if "thinking" in config.llm.model_fields_set else None
    )
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=(
                "thinking_enabled is deprecated; use generation_defaults.reasoning"
            ),
            category=DeprecationWarning,
        )
        return LiteLLMService(
            model_name=config.llm.model or "unknown",
            api_key=config.llm.api_key,
            api_base=config.llm.api_base,
            resilience=ResilienceConfig(
                max_retries=config.llm.max_retries,
                timeout_seconds=config.llm.timeout_seconds or 30.0,
            ),
            thinking_enabled=thinking_enabled,
            telemetry=telemetry, service_role="maintenance_default",
        )


def build_framework_embedding_service(
    config: FridayChatConfig,
    *,
    telemetry: TelemetryInterface | None = None,
) -> FrameworkEmbeddingService:
    if config.embedding_pool is not None:
        spec = config.embedding_service_specs[
            config.embedding_pool.default_service
        ]
        return FrameworkEmbeddingService(
            service=LiteLLMEmbeddingService.from_spec(spec, telemetry=telemetry, service_role="embedding")
        )

    service = LiteLLMEmbeddingService(
        model_name=config.embedding.model or "text-embedding-3-small",
        api_key=config.embedding.api_key or config.llm.api_key,
        api_base=config.embedding.api_base or config.llm.api_base,
        resilience=ResilienceConfig(
            max_retries=config.llm.max_retries,
            timeout_seconds=config.embedding.timeout_seconds
            or config.llm.timeout_seconds
            or 30.0,
        ),
        telemetry=telemetry, service_role="embedding",
    )
    return FrameworkEmbeddingService(service=service)


def build_framework_memory_adapter(
    config: FridayChatConfig,
    embedding: FrameworkEmbeddingService,
    *,
    session_id: str,
    maintenance_layout: FridayChatMaintenanceLayout,
    telemetry: TelemetryInterface | None = None,
) -> FrameworkMemoryAdapter:
    persist_directory = str(maintenance_layout.vector_directory)
    graph_path = str(maintenance_layout.graph_path)
    collection_config = CollectionConfig(
        short_term_collection=str(
            config.memory.retrieval.get("short_term_collection", "memories_short_term")
        ),
        long_term_collection=str(
            config.memory.retrieval.get("long_term_collection", "memories_long_term")
        ),
        decayed_collection=str(
            config.memory.retrieval.get("decayed_collection", "memories_decayed")
        ),
        short_term_min_similarity=float(
            config.memory.retrieval.get("short_term_min_similarity", 0.5)
        ),
        long_term_min_similarity=float(
            config.memory.retrieval.get("long_term_min_similarity", 0.7)
        ),
        default_n_results=_int_from_mapping(
            config.memory.retrieval,
            "default_n_results",
            5,
        ),
    )
    collection_manager = CollectionManager(
        embedding_function=embedding,
        config=collection_config,
        path=persist_directory,
    )
    vector_store = SimpleVectorStore(embedding_function=embedding)
    graph_store = (
        ElementXGraphStore(
            storage_path=graph_path,
            schema_config=config.extraction.ontology,
        )
        if config.lifecycle.enabled
        else NullGraphStore()
    )
    episodic_store = InMemoryEpisodicStore()
    controller = MemoryController(
        vector_store=vector_store,
        graph_store=graph_store,
        episodic_store=episodic_store,
        collection_manager=collection_manager,
        priming_config=config.memory.priming,
        recalc_interval=config.extraction.interval,
    )
    return FrameworkMemoryAdapter(
        controller=controller,
        collection_manager=collection_manager,
        config=config,
        session_id=session_id,
        episodic_store=episodic_store,
        graph_store=graph_store,
        recovery_graph_store=(
            graph_store if isinstance(graph_store, ElementXGraphStore) else None
        ),
        passage_router=_build_passage_router(config, telemetry=telemetry),
        observer=telemetry if isinstance(telemetry, ChatTelemetryObserver) else None,
        access_buffer_configured=(
            config.lifecycle.enabled
            and config.lifecycle.access_buffer.get("enabled", True) is not False
        ),
    )


def build_framework_transcript_adapter(
    config: FridayChatConfig,
    *,
    session_id: str,
    maintenance_layout: FridayChatMaintenanceLayout,
) -> FrameworkTranscriptAdapter:
    return FrameworkTranscriptAdapter(
        store=SQLiteTranscriptStore(maintenance_layout.transcript_database_path),
        config=config,
        session_id=session_id,
    )


def build_framework_tool_registry(
    config: FridayChatConfig,
    *,
    telemetry: TelemetryInterface | None = None,
) -> FrameworkToolRegistryAdapter:
    tool_specs = _configured_tool_specs(config.tools.registry)
    loaded: dict[str, Any] = {}
    definitions: list[ToolDefinition] = []
    for spec in tool_specs:
        try:
            tool = _instantiate_tool(spec, config, telemetry=telemetry)
        except Exception:
            continue
        configured_name = spec.get("name")
        name = (
            configured_name
            if isinstance(configured_name, str)
            else getattr(tool, "name", "unknown")
        )
        if not isinstance(name, str) or not name:
            continue
        loaded[name] = tool
        definitions.append(_definition_from_framework_tool(tool, name=name))
    return FrameworkToolRegistryAdapter(tools=loaded, definitions=tuple(definitions))


def build_framework_maintenance_adapter(
    config: FridayChatConfig,
    *,
    session_id: str,
    memory: FrameworkMemoryAdapter,
    embedding: FrameworkEmbeddingService,
    llm_models: dict[str, str],
    diagnostics: Any,
    maintenance_layout: FridayChatMaintenanceLayout,
    telemetry: TelemetryInterface | None = None,
) -> FrameworkMaintenanceAdapter:
    """Build real framework maintenance services for FridayV2."""
    legacy_primary_llm = _build_legacy_primary_llm_service(config, telemetry=telemetry)
    llm_services = {
        role: _build_role_llm_service(config, role, model, telemetry=telemetry)
        for role, model in llm_models.items()
    }
    promotion_service = None
    access_buffer = None
    factor_computer = None
    incremental_maintainer = None
    lifecycle_config = config.lifecycle.model_dump(mode="python")
    if config.lifecycle.enabled:
        try:
            decay_config = DecayConfig(
                decay_rate=float(lifecycle_config.get("decay_rate", 0.01)),
                access_boost=float(lifecycle_config.get("access_boost", 0.2)),
                promotion_threshold=float(
                    lifecycle_config.get("promotion_threshold", 0.7)
                ),
                decay_threshold=float(lifecycle_config.get("decay_threshold", 0.2)),
                short_term_min_age_hours=int(
                    lifecycle_config.get("short_term_min_age_hours", 24)
                ),
                decayed_retention_days=int(
                    lifecycle_config.get("decayed_retention_days", 30)
                ),
                promotion_weight_age=float(
                    lifecycle_config.get("promotion_weight_age", 0.2)
                ),
                promotion_weight_access=float(
                    lifecycle_config.get("promotion_weight_access", 0.4)
                ),
                promotion_weight_confidence=float(
                    lifecycle_config.get("promotion_weight_confidence", 0.2)
                ),
                promotion_weight_connection=float(
                    lifecycle_config.get("promotion_weight_connection", 0.2)
                ),
            )
            promotion_service = MemoryPromotionService(
                config=decay_config,
                collection_manager=memory.collection_manager,
                graph_store=memory.controller.graph,
            )
        except Exception as exc:
            diagnostics.framework_upgrade_gaps.append(
                f"Unable to initialize framework lifecycle promotion: {exc}"
            )

        access_config = config.lifecycle.access_buffer
        if access_config.get("enabled", True) is not False:
            try:
                access_buffer = AccessBuffer(
                    AccessBufferConfig(
                        max_buffer_size=int(
                            access_config.get(
                                "max_buffer_size",
                                lifecycle_config.get("access_buffer_size", 1000),
                            )
                        ),
                        max_buffer_age_seconds=int(
                            access_config.get(
                                "max_buffer_age_seconds",
                                lifecycle_config.get("access_buffer_age_seconds", 300),
                            )
                        ),
                        wal_path=maintenance_layout.access_buffer_wal_path,
                        decay_score_boost=float(
                            access_config.get(
                                "decay_score_boost",
                                lifecycle_config.get("decay_score_boost", 0.1),
                            )
                        ),
                    )
                )
            except Exception as exc:
                diagnostics.framework_upgrade_gaps.append(
                    f"Unable to initialize framework access buffer: {exc}"
                )

        factor_config = config.lifecycle.factor_computer
        if factor_config.get("enabled", True) is not False:
            try:
                factor_computer = RetrievalFactorComputer(
                    FactorComputerConfig(
                        decay_rate=float(
                            factor_config.get(
                                "decay_rate",
                                lifecycle_config.get("factor_decay_rate", 0.005),
                            )
                        ),
                        usage_boost_factor=float(
                            factor_config.get(
                                "usage_boost_factor",
                                lifecycle_config.get("usage_boost_factor", 0.1),
                            )
                        ),
                        min_factor=float(factor_config.get("min_factor", 0.01)),
                    )
                )
            except Exception as exc:
                diagnostics.framework_upgrade_gaps.append(
                    f"Unable to initialize framework factor computer: {exc}"
                )

        incremental_config = lifecycle_config.get("incremental_maintenance", {})
        if isinstance(incremental_config, Mapping):
            incremental_enabled = incremental_config.get("enabled", True) is not False
        else:
            incremental_config = {}
            incremental_enabled = True
        if incremental_enabled:
            try:
                incremental_maintainer = IncrementalGraphMaintainer(
                    graph_store=memory.controller.graph,
                    config=IncrementalMaintenanceConfig(
                        enabled=True,
                        interval=int(incremental_config.get("interval", 5)),
                        mode=str(incremental_config.get("mode", "lightweight")),
                        max_duration_ms=int(
                            incremental_config.get("max_duration_ms", 200)
                        ),
                        fuzzy_threshold=float(
                            incremental_config.get("fuzzy_threshold", 0.85)
                        ),
                    ),
                )
            except Exception as exc:
                diagnostics.framework_upgrade_gaps.append(
                    f"Unable to initialize framework incremental maintenance: {exc}"
                )

    budget_monitor = None
    compactor = None
    compaction_config_data = config.memory.compaction
    if compaction_config_data.get("enabled") is True:
        try:
            compaction_config = CompactionConfig(
                **{
                    key: value
                    for key, value in compaction_config_data.items()
                    if key != "llm_service"
                }
            )
            budget_monitor = ContextBudgetMonitor(config=compaction_config)
            if config.llm_pool is not None:
                compaction_service_name = _optional_string(
                    compaction_config_data.get("llm_service")
                ) or "compaction"
                compaction_llm = _canonical_chat_service(
                    config,
                    compaction_service_name,
                    telemetry=telemetry, service_role="compaction",
                )
                compaction_model_name = config.llm_service_specs[
                    compaction_service_name
                ].model
            else:
                compaction_llm = llm_services.get(
                    "researcher",
                    legacy_primary_llm,
                )
                compaction_model_name = config.llm.model or "gpt-4"
            compactor = InSessionCompactor(
                memory_controller=memory.controller,
                collection_manager=memory.collection_manager,
                llm_client=compaction_llm,
                config=compaction_config,
                token_estimator_config=config.memory.token_estimator,
                model_name=compaction_model_name,
            )
        except Exception as exc:
            diagnostics.framework_upgrade_gaps.append(
                f"Unable to initialize framework compaction: {exc}"
            )

    extractor = None
    try:
        extractor = MemoryExtractor(
            memory_controller=memory.controller,
            llm=_build_extraction_llm_service(config, legacy_primary_llm, telemetry=telemetry),
            prompt_template=(
                config.extraction.prompt
                if isinstance(config.extraction.prompt, str)
                else None
            ),
            user_name=config.chat.user_name,
            assistant_name=config.chat.assistant_name,
            embedding_model=embedding,
            temperature=(
                None
                if config.llm_pool is not None
                else config.extraction.temperature
            ),
            max_tokens=(
                None
                if config.llm_pool is not None
                else config.extraction.max_tokens
            ),
            rejection_log_path=config.extraction.rejection_log,
        )
    except Exception as exc:
        diagnostics.framework_upgrade_gaps.append(
            f"Unable to initialize framework extraction: {exc}"
        )

    memory.access_buffer = access_buffer
    return FrameworkMaintenanceAdapter(
        config=config,
        session_id=session_id,
        memory=memory,
        embedding=embedding,
        llm_service=legacy_primary_llm,
        llm_models=llm_models,
        llm_services=llm_services,
        promotion_service=promotion_service,
        access_buffer=access_buffer,
        factor_computer=factor_computer,
        incremental_maintainer=incremental_maintainer,
        budget_monitor=budget_monitor,
        compactor=compactor,
        extractor=extractor,
        observer=telemetry if isinstance(telemetry, ChatTelemetryObserver) else None,
    )


def build_framework_workflow_adapter(
    config: FridayChatConfig,
    *,
    orchestrator: Any,
) -> FrameworkWorkflowAdapter:
    from friday_agent.workflows import WorkflowEngine, WorkflowLoader
    from friday_memory import ScratchPadStore

    return FrameworkWorkflowAdapter(
        loader=WorkflowLoader(_resolve_workflows_dir(config)),
        engine=WorkflowEngine(
            orchestrator=orchestrator,
            scratchpad=ScratchPadStore(),
        ),
    )


def _build_passage_router(config: FridayChatConfig, *, telemetry: TelemetryInterface | None = None) -> PassageRouter | None:
    router_config = config.memory.passage_router
    if router_config.get("enabled") is not True:
        return None
    canonical_service = _canonical_chat_service_from_mapping(
        config,
        router_config,
        default_name="passage_router",
        telemetry=telemetry, service_role="passage_router",
    )
    router_model = (
        router_config.get("model")
        or config.extraction.model
        or config.llm.model
        or "unknown"
    )
    router_llm = canonical_service or LiteLLMService(
        model_name=str(router_model),
        api_key=(
            _optional_string(router_config.get("api_key"))
            or config.extraction.api_key
            or config.llm.api_key
        ),
        api_base=(
            _optional_string(router_config.get("api_base"))
            or config.extraction.api_base
            or config.llm.api_base
        ),
        resilience=ResilienceConfig(
            max_retries=_int_from_mapping(router_config, "max_retries", 1),
            timeout_seconds=float(router_config.get("timeout_seconds", 6.0) or 6.0),
        ),
        telemetry=telemetry, service_role="passage_router",
    )
    fields = (
        "temperature",
        "max_tokens",
        "timeout_seconds",
        "min_confidence",
        "include_on_empty_query",
        "fallback_mode",
        "heuristic_keywords",
        "system_prompt",
        "min_similarity",
        "min_similarity_tool_output",
        "min_keep_on_empty",
    )
    router_kwargs = {key: router_config[key] for key in fields if key in router_config}
    if canonical_service is not None:
        router_kwargs.update(
            temperature=None,
            max_tokens=None,
            timeout_seconds=None,
        )
    router_kwargs["enabled"] = True
    return PassageRouter(
        llm=router_llm,
        config=PassageRouterConfig(**router_kwargs),
    )


def _build_role_llm_service(
    config: FridayChatConfig,
    role: str,
    model: str,
    *,
    telemetry: TelemetryInterface | None = None,
) -> LiteLLMService:
    roles: dict[str, ServiceRole] = {"synthesizer": "maintenance_synthesizer", "classifier": "maintenance_classifier", "researcher": "maintenance_researcher", "judge": "maintenance_judge"}
    service_role = roles.get(role, "unspecified")
    role_config = config.maintenance.llm.get(role)
    role_data = role_config if isinstance(role_config, Mapping) else {}
    canonical_service = _canonical_chat_service_from_mapping(
        config,
        role_data,
        default_name=role,
        telemetry=telemetry, service_role=service_role,
    )
    if canonical_service is not None:
        return canonical_service
    return LiteLLMService(
        model_name=model,
        api_key=_optional_string(role_data.get("api_key")) or config.llm.api_key,
        api_base=_optional_string(role_data.get("api_base")) or config.llm.api_base,
        resilience=ResilienceConfig(
            max_retries=_int_from_mapping(
                role_data, "max_retries", config.llm.max_retries
            ),
            timeout_seconds=float(
                role_data.get("timeout_seconds") or config.llm.timeout_seconds or 30.0
            ),
        ),
        telemetry=telemetry, service_role=service_role,
    )


def _build_extraction_llm_service(
    config: FridayChatConfig,
    default_service: LiteLLMService,
    *,
    telemetry: TelemetryInterface | None = None,
) -> LiteLLMService:
    if config.llm_pool is not None:
        service_name = config.extraction.llm_service or "extraction"
        return _canonical_chat_service(config, service_name, telemetry=telemetry, service_role="extraction")
    if not config.extraction.model:
        return default_service
    return LiteLLMService(
        model_name=config.extraction.model,
        api_key=config.extraction.api_key or config.llm.api_key,
        api_base=config.extraction.api_base or config.llm.api_base,
        resilience=ResilienceConfig(
            max_retries=config.extraction.max_retries,
            timeout_seconds=config.extraction.timeout_seconds
            or config.llm.timeout_seconds
            or 30.0,
        ),
        telemetry=telemetry, service_role="extraction",
    )


def _framework_maintenance_config(
    config: FridayChatConfig,
) -> FrameworkMaintenanceConfig:
    payload = config.maintenance.model_dump(mode="python")
    payload["collection_name"] = config.memory.collection_name
    return FrameworkMaintenanceConfig.model_validate(payload)


def _compaction_result_to_dict(
    result: Any,
    *,
    trigger_reason: str,
    time_budget_ms: int,
    current_tokens: int,
    available_budget: int,
    target_utilization: float,
) -> dict[str, Any]:
    return {
        "trigger_reason": getattr(result, "trigger_reason", trigger_reason),
        "turns_summarized": getattr(result, "turns_summarized", 0),
        "tokens_saved": getattr(result, "tokens_saved_from_summarization", 0),
        "tokens_target": getattr(result, "tokens_target", 0),
        "target_met": getattr(result, "target_met", False),
        "insights_deduplicated": getattr(result, "insights_deduplicated", 0),
        "memories_promoted": getattr(result, "memories_promoted", 0),
        "duration_ms": getattr(result, "duration_ms", 0.0),
        "time_budget_exhausted": getattr(result, "time_budget_exhausted", False),
        "errors": list(getattr(result, "errors", []) or []),
        "time_budget_ms": time_budget_ms,
        "current_tokens": current_tokens,
        "available_budget": available_budget,
        "target_utilization": target_utilization,
    }


def _access_buffer_count(access_buffer: AccessBuffer | None) -> int:
    if access_buffer is None:
        return 0
    stats = access_buffer.get_stats()
    return int(stats.get("short_term_accesses", 0)) + int(
        stats.get("long_term_accesses", 0)
    )


def _configured_tool_specs(registry_config: Any) -> list[dict[str, Any]]:
    if isinstance(registry_config, list):
        return [dict(item) for item in registry_config if isinstance(item, Mapping)]
    return []


async def _apply_passage_routing(
    payload: Any,
    query: str,
    passage_router: PassageRouter,
) -> Any:
    passages = getattr(payload, "passages", []) or []
    if not passages:
        return payload

    decision = await passage_router.decide(query)
    original_count = len(passages)
    if decision.include_passages:
        filtered_passages, excluded = passage_router.filter_passages(passages)
        included = len(filtered_passages)
    else:
        filtered_passages = []
        excluded = original_count
        included = 0

    debug_info = {
        **(getattr(payload, "debug_info", {}) or {}),
        "passage_router_enabled": True,
        "passage_router_include": decision.include_passages,
        "passage_router_confidence": decision.confidence,
        "passage_router_reason": decision.reason,
        "passage_router_original": original_count,
        "passage_router_included": included,
        "passage_router_excluded": excluded,
    }
    return payload.model_copy(
        update={"passages": filtered_passages, "debug_info": debug_info}
    )


def _resolve_workflows_dir(config: FridayChatConfig) -> Path:
    chat_extra = config.chat.model_extra or {}
    configured = (
        chat_extra.get("workflows_dir")
        or chat_extra.get("workflow_directory")
        or os.environ.get("FRIDAY_WORKFLOWS_DIR")
    )
    if isinstance(configured, str) and configured:
        return Path(configured).expanduser()
    return Path.cwd() / "workflows"


def _optional_string(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _instantiate_tool(spec: Mapping[str, Any], config: FridayChatConfig, *, telemetry: TelemetryInterface | None = None) -> Any:
    module_name = spec.get("module")
    class_name = spec.get("class")
    if not isinstance(module_name, str) or not isinstance(class_name, str):
        raise ValueError("Tool spec requires module and class.")
    module = importlib.import_module(module_name)
    tool_class = getattr(module, class_name)
    constructor_args = spec.get("constructor_args", {})
    if not isinstance(constructor_args, Mapping):
        constructor_args = {}
    kwargs = dict(constructor_args)
    if module_name == "friday_tools.web":
        kwargs.setdefault("config", config.web.model_dump(mode="python"))
    if class_name == "SmartFileReadTool":
        summarizer_llm = _build_smart_file_llm_service(
            config,
            role="summarizer",
            default_name="smart_file_summarizer",
            telemetry=telemetry,
        )
        synthesizer_llm = _build_smart_file_llm_service(
            config,
            role="synthesizer",
            default_name="smart_file_synthesizer",
            telemetry=telemetry,
        )
        kwargs.setdefault("fallback_llm", summarizer_llm)
        kwargs.setdefault("summarizer_llm", summarizer_llm)
        kwargs.setdefault("synthesizer_llm", synthesizer_llm)
        kwargs.setdefault("config", _build_smart_file_processor_config(config))
    return tool_class(**kwargs)


def _build_smart_file_llm_service(
    config: FridayChatConfig,
    *,
    role: str = "summarizer",
    default_name: str = "smart_file_summarizer",
    telemetry: TelemetryInterface | None = None,
) -> LiteLLMService:
    service_role: ServiceRole = "smart_file_summarizer" if role == "summarizer" else "smart_file_synthesizer" if role == "synthesizer" else "unspecified"
    llm_config = config.smart_file.llm
    role_config = llm_config.get(role) if isinstance(llm_config, Mapping) else {}
    role_data = role_config if isinstance(role_config, Mapping) else {}
    canonical_service = _canonical_chat_service_from_mapping(
        config,
        role_data,
        default_name=default_name,
        telemetry=telemetry, service_role=service_role,
    )
    if canonical_service is not None:
        return canonical_service
    return LiteLLMService(
        model_name=_optional_string(role_data.get("model"))
        or config.llm.model
        or "unknown",
        api_key=_optional_string(role_data.get("api_key")) or config.llm.api_key,
        api_base=_optional_string(role_data.get("api_base"))
        or config.llm.api_base,
        resilience=ResilienceConfig(
            max_retries=_int_from_mapping(
                role_data,
                "max_retries",
                config.llm.max_retries,
            ),
            timeout_seconds=float(
                role_data.get("timeout_seconds")
                or config.llm.timeout_seconds
                or 30.0
            ),
        ),
        telemetry=telemetry, service_role=service_role,
    )


def _canonical_chat_service(
    config: FridayChatConfig,
    service_name: str,
    *,
    telemetry: TelemetryInterface | None = None,
    service_role: ServiceRole = "unspecified",
) -> LiteLLMService:
    try:
        spec = config.llm_service_specs[service_name]
    except KeyError as error:
        raise ValueError(
            f"Unknown canonical LLM service {service_name!r}"
        ) from error
    return LiteLLMService.from_spec(spec, telemetry=telemetry, service_role=service_role)


def _canonical_chat_service_from_mapping(
    config: FridayChatConfig,
    role_data: Mapping[str, Any],
    *,
    default_name: str,
    telemetry: TelemetryInterface | None = None,
    service_role: ServiceRole = "unspecified",
) -> LiteLLMService | None:
    if config.llm_pool is None:
        return None
    configured_name = _optional_string(role_data.get("llm_service"))
    service_name = configured_name or default_name
    return _canonical_chat_service(config, service_name, telemetry=telemetry, service_role=service_role)


def _build_smart_file_processor_config(config: FridayChatConfig) -> Any:
    from friday_memory.ingestion.large_file_processor import LargeFileProcessorConfig

    return LargeFileProcessorConfig(
        auto_chunk_threshold_chars=config.smart_file.auto_chunk_threshold or 50000,
        chunk_size=config.smart_file.chunk_size or 2048,
        chunk_overlap=config.smart_file.chunk_overlap or 25,
    )


def _definition_from_framework_tool(
    tool: Any,
    *,
    name: str | None = None,
) -> ToolDefinition:
    schema = getattr(tool, "parameters_schema", None)
    if not isinstance(schema, dict):
        schema = tool.to_schema().get("parameters", {})
    return ToolDefinition(
        name=str(name or tool.name),
        description=str(getattr(tool, "description", "")),
        input_schema=schema,
        category=str(getattr(tool, "category", "uncategorized")),
    )


def _format_workflow_execution(workflow: Any, execution: Any) -> str:
    lines = [
        f"Workflow: {getattr(workflow, 'name', getattr(workflow, 'id', 'unknown'))}",
        f"Status: {getattr(execution.status, 'value', str(execution.status))}",
        f"Execution: {execution.execution_id}",
    ]
    pending = getattr(execution, "pending_approval", None)
    if pending:
        lines.append(f"Pending approval: {pending}")
        lines.append("Use /workflow approve to continue or /workflow skip to skip.")
    return "\n".join(lines)


def _format_workflow_status(status: Mapping[str, Any]) -> str:
    lines = [
        f"Workflow: {status.get('workflow_id', 'unknown')}",
        f"Execution: {status.get('execution_id', 'unknown')}",
        f"Status: {status.get('status', 'unknown')}",
        f"Pending approval: {status.get('pending_approval') or 'none'}",
    ]
    tasks = status.get("tasks", {})
    if isinstance(tasks, Mapping) and tasks:
        lines.append("Tasks:")
        for task_id, task in tasks.items():
            if not isinstance(task, Mapping):
                continue
            lines.append(
                f"- {task_id}: {task.get('status', 'unknown')} "
                f"({task.get('agent', 'unknown')})"
            )
    return "\n".join(lines)


def _to_openai_tool_schema(tool: ToolDefinition) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.input_schema,
        },
    }


def _context_payload_to_snippets(
    payload: Any, *, token_limit: int | None = None, include_mcp: bool = True
) -> list[str]:
    # Dynamic legacy payload decoding stays at the existing adapter boundary.
    parts: list[tuple[bool, str]] = []
    for turn in getattr(payload, "history", []) or []:
        user = getattr(turn, "user_message", None)
        assistant = getattr(turn, "assistant_message", None)
        if user:
            parts.append((False, f"User: {user}"))
        if assistant:
            parts.append((False, f"Assistant: {assistant}"))
    for field_name in ("passages", "insights", "summaries"):
        for item in getattr(payload, field_name, []) or []:
            if not isinstance(item, dict):
                continue
            metadata = item.get("metadata")
            if isinstance(metadata, Mapping) and is_mcp_memory(metadata):
                snippet = mcp_memory_snippet(item, include_mcp=include_mcp)
                if snippet is not None:
                    parts.append((True, snippet))
            else:
                text = item.get("text") if field_name == "passages" else _metadata_text(item)
                if isinstance(text, str) and text:
                    parts.append((False, text))
    for fact in getattr(payload, "recent_memories", []) or []:
        if isinstance(fact, str) and fact:
            parts.append((False, fact))
    remaining = None if token_limit is None else max(
        0, token_limit - sum(estimated_snippet_tokens(text) for mcp, text in parts if not mcp)
    )
    snippets: list[str] = []
    seen_mcp: set[str] = set()
    for mcp, text in parts:
        if mcp:
            cost = estimated_snippet_tokens(text)
            if text in seen_mcp or (remaining is not None and cost > remaining):
                continue
            seen_mcp.add(text)
            if remaining is not None:
                remaining -= cost
        snippets.append(text)
    return snippets


def _relationship_matches_name(
    name: str,
    source_label: str,
    relation: str,
    target_label: str,
) -> bool:
    lowered = name.lower()
    return lowered in f"{source_label} {relation} {target_label}".lower()


def _metadata_text(item: Mapping[str, Any]) -> str:
    for key in ("text", "content", "summary", "document"):
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    metadata = item.get("metadata")
    if isinstance(metadata, Mapping):
        for key in ("text", "content", "summary"):
            value = metadata.get(key)
            if isinstance(value, str) and value:
                return value
    return json.dumps(item, default=str)


def _sum_available_metrics(
    *metrics: MemoryMetric[int],
) -> MemoryMetric[int]:
    """Sum only fully available metrics; never replace a failed read with zero."""
    if any(metric.value is None for metric in metrics):
        return MemoryMetric.unavailable(MemoryDiagnosticReason.STORE_READ_FAILED)
    return MemoryMetric.available(
        sum(metric.value for metric in metrics if metric.value is not None)
    )


def _length_metric(value: object) -> MemoryMetric[int]:
    """Map one gathered collection result to an honest count metric."""
    if isinstance(value, Exception):
        return MemoryMetric.unavailable(MemoryDiagnosticReason.STORE_READ_FAILED)
    if not isinstance(value, list):
        return MemoryMetric.unavailable(MemoryDiagnosticReason.STORE_READ_FAILED)
    return MemoryMetric.available(len(value))


def _memory_record_view(
    record: object,
    *,
    kind: MemoryRecordKind,
    collection: MemoryCollection,
) -> MemoryRecordView | None:
    """Validate and bound one framework vector record at the adapter boundary."""
    if not isinstance(record, Mapping):
        return None
    record_id = _bounded_memory_text(record.get("id"), limit=256)
    text_value = record.get("text")
    if text_value is None:
        text_value = record.get("document")
    text = _bounded_memory_text(text_value, limit=4096)
    if not record_id or not text:
        return None
    metadata_value = record.get("metadata")
    metadata = metadata_value if isinstance(metadata_value, Mapping) else {}
    source_memory_ids, provenance_truncated = _source_memory_ids(
        metadata.get("source_memories")
    )
    source_count = _optional_nonnegative_int(metadata.get("source_count"))
    verification_status = _bounded_memory_text(
        metadata.get("verification_status"),
        limit=64,
    )
    if verification_status is None and isinstance(metadata.get("verified"), bool):
        verification_status = (
            "verified" if metadata["verified"] is True else "unverified"
        )
    return MemoryRecordView(
        record_id=record_id,
        kind=kind,
        text=text,
        collection=collection,
        lifecycle_stage=_bounded_memory_text(metadata.get("stage"), limit=64),
        created_at=_optional_datetime(metadata.get("created_at")),
        confidence=_optional_confidence(metadata.get("confidence")),
        source_count=source_count,
        provenance_source_type=_bounded_memory_text(
            metadata.get("provenance_source_type") or metadata.get("source_type"),
            limit=64,
        ),
        source_memory_ids=source_memory_ids,
        provenance_truncated=provenance_truncated,
        verification_status=verification_status,
        verification_confidence=_optional_confidence(
            metadata.get("verification_confidence")
        ),
    )


def _bounded_memory_text(value: object, *, limit: int) -> str | None:
    """Normalize untrusted scalar text and remove terminal control characters."""
    if not isinstance(value, str):
        return None
    normalized = " ".join(
        "".join(
            character if character.isprintable() else " " for character in value
        ).split()
    )
    if not normalized:
        return None
    return normalized[:limit]


def _source_memory_ids(value: object) -> tuple[tuple[str, ...], bool]:
    """Decode scalar-safe synthesis lineage into a bounded typed tuple."""
    decoded = value
    if isinstance(value, str):
        if len(value) > _MAX_SOURCE_PROVENANCE_CHARS:
            return (), False
        try:
            encoded_size = len(value.encode("utf-8", errors="strict"))
        except UnicodeEncodeError:
            return (), False
        if encoded_size > _MAX_SOURCE_PROVENANCE_BYTES:
            return (), False
        try:
            decoded = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return (), False
    if not isinstance(decoded, list):
        return (), False
    visible: list[str] = []
    truncated = len(decoded) > _MAX_VISIBLE_SOURCE_IDS
    for candidate in decoded[: _MAX_VISIBLE_SOURCE_IDS + 1]:
        item = _bounded_memory_text(candidate, limit=128)
        if item is None:
            continue
        if len(visible) == _MAX_VISIBLE_SOURCE_IDS:
            truncated = True
            break
        visible.append(item)
    return tuple(visible), truncated


def _optional_nonnegative_int(value: object) -> int | None:
    if _is_nonnegative_int(value):
        return value
    return None


def _is_nonnegative_int(value: object) -> TypeGuard[int]:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _optional_confidence(value: object) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        result = float(value)
        return result if math.isfinite(result) and 0.0 <= result <= 1.0 else None
    return None


def _optional_datetime(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _memory_record_sort_key(record: MemoryRecordView) -> tuple[float, str]:
    created = record.created_at
    if created is None:
        return (float("-inf"), record.record_id)
    try:
        return (created.timestamp(), record.record_id)
    except (OSError, OverflowError, ValueError):
        return (float("-inf"), record.record_id)


def _nonnegative_mapping_int(
    data: Mapping[str, Any],
    key: str,
    default: int,
) -> int | None:
    value = data.get(key, default)
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return None


def _dynamic_context_budget(config: FridayChatConfig) -> int:
    return ToolBudgetCalculator.from_config(
        config,
        registered_count=0,
    ).available_context_tokens


def _int_from_mapping(data: Mapping[str, Any], key: str, default: int) -> int:
    value = data.get(key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _chunk_text(text: str, *, chunk_size: int, chunk_overlap: int) -> list[str]:
    if chunk_size <= 0 or len(text) <= chunk_size:
        return [text]
    overlap = max(0, min(chunk_overlap, chunk_size - 1))
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks


__all__ = [
    "FrameworkChatModel",
    "FrameworkEmbeddingService",
    "FrameworkMaintenanceAdapter",
    "FrameworkMemoryAdapter",
    "FrameworkToolRegistryAdapter",
    "FrameworkTranscriptAdapter",
    "FrameworkWorkflowAdapter",
    "build_framework_chat_model",
    "build_framework_embedding_service",
    "build_framework_maintenance_adapter",
    "build_framework_memory_adapter",
    "build_framework_tool_registry",
    "build_framework_transcript_adapter",
    "build_framework_workflow_adapter",
]
