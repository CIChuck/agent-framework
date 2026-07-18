"""Adapters from FridayV2 runtime protocols to framework packages."""

from __future__ import annotations

import importlib
import json
import os
from collections.abc import AsyncIterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

from friday_llm import LiteLLMEmbeddingService, LiteLLMService, ResilienceConfig
from friday_memory import (
    AccessBuffer,
    AccessBufferConfig,
    CollectionConfig,
    CollectionManager,
    DecayConfig,
    ElementXGraphStore,
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
from friday_transcript import (
    ContextLogEntry,
    SQLiteTranscriptStore,
    TranscriptEntry,
    TranscriptSession,
)

from friday_chat.config import FridayChatConfig
from friday_chat.tools.schemas import ToolDefinition
from friday_chat.turns.models import (
    ChatModelResponse,
    ToolCallRequest,
)
from friday_chat.turns.models import (
    InteractionTurn as ChatInteractionTurn,
)


@dataclass
class FrameworkChatModel:
    """Chat adapter backed by ``friday-llm`` LiteLLMService."""

    service: LiteLLMService
    config: FridayChatConfig

    async def complete(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ChatModelResponse:
        response = await self.service.chat_completion(
            messages=[dict(message) for message in messages],
            tools=[_to_openai_tool_schema(tool) for tool in tools] or None,
            temperature=self.config.llm.temperature,
            max_tokens=self.config.llm.max_tokens,
            timeout=self.config.llm.timeout_seconds,
        )
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
            usage=dict(response.usage),
            reasoning_content=response.reasoning_content,
            raw_response=response,
        )

    async def stream_complete(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> AsyncIterator[str]:
        async for chunk in self.service.chat_completion_stream(
            messages=[dict(message) for message in messages],
            tools=[_to_openai_tool_schema(tool) for tool in tools] or None,
            temperature=self.config.llm.temperature,
            max_tokens=self.config.llm.max_tokens,
            timeout=self.config.llm.timeout_seconds,
        ):
            yield chunk


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
    passage_router: PassageRouter | None = None

    async def retrieve(
        self,
        query: str,
        *,
        token_limit: int | None = None,
    ) -> list[str]:
        resolved_token_limit = token_limit or _dynamic_context_budget(self.config)
        payload = await self._recall(
            query,
            token_limit=resolved_token_limit,
        )
        return _context_payload_to_snippets(payload)

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

    async def ingest_document(
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
        graph = cast(Any, self.controller.graph)
        if name:
            found = await graph.find_by_label(name)
            return [found.model_dump(mode="json")] if found is not None else []
        nodes = await graph.get_all_nodes()
        return [node.model_dump(mode="json") for node in nodes]

    async def list_relationships(self, name: str | None = None) -> list[dict[str, Any]]:
        graph = cast(Any, self.controller.graph)
        nodes = await graph.get_all_nodes()
        node_by_id = {str(node.id): node for node in nodes}
        edges = await graph.get_all_edges()
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

    async def list_insights(self) -> list[dict[str, Any]]:
        return cast(
            list[dict[str, Any]],
            await self.collection_manager.get_all(
                limit=100,
                where={"type": "insight"},
            ),
        )

    async def list_summaries(self) -> list[dict[str, Any]]:
        return cast(
            list[dict[str, Any]],
            await self.collection_manager.get_all(
                limit=100,
                where={"type": "summary"},
            ),
        )

    async def list_meta_insights(self) -> list[dict[str, Any]]:
        return cast(
            list[dict[str, Any]],
            await self.collection_manager.get_all(
                limit=100,
                where={"type": "meta_insight"},
            ),
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
    pending_extraction: list[tuple[str, str]] = field(default_factory=list)
    flush_pending_error: BaseException | None = None
    background_actions: list[str] = field(default_factory=list)
    compaction_running: bool = False
    compaction_calls: list[dict[str, Any]] = field(default_factory=list)
    errors: list[BaseException] = field(default_factory=list)
    migration_needed: bool = False

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
            await self.promotion_service.run_promotion_cycle(dry_run=False)
        self.actions.append("run_lifecycle")

    async def reorganize_memory(self, mode: str) -> None:
        """Run full framework memory reorganization."""
        self._raise_next_error()
        persist_directory = self.config.memory.persist_directory
        if not persist_directory:
            self.actions.append("reorganize_skipped:no_persist_directory")
            return
        memory_dir = Path(persist_directory)
        if not memory_dir.exists():
            self.actions.append("reorganize_skipped:no_persist_directory")
            return

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
            self.actions.append("flush_pending_extraction")
            return 0
        pending = list(self.pending_extraction)
        self.pending_extraction.clear()
        try:
            await self._extract_turns(pending)
        except Exception:
            self.pending_extraction[:0] = pending
            raise
        self.actions.append("flush_pending_extraction")
        return len(pending)

    async def extract_buffered_turns(self, *, trigger_reason: str) -> int:
        """Extract all currently buffered turns."""
        self._raise_next_error()
        if self.flush_pending_error is not None:
            raise self.flush_pending_error
        if not self.pending_extraction:
            self.background_actions.append(f"extract:{trigger_reason}:0")
            return 0
        pending = list(self.pending_extraction)
        self.pending_extraction.clear()
        try:
            await self._extract_turns(pending)
        except Exception:
            self.pending_extraction[:0] = pending
            raise
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
                flushed = flush_result.short_term_flushed + flush_result.long_term_flushed
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
        self._raise_next_error()
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

    async def _extract_turns(self, turns: list[tuple[str, str]]) -> None:
        if self.extractor is None:
            return
        for user_message, assistant_message in turns:
            result = await self.extractor.extract(
                InteractionTurn(
                    id=str(uuid4()),
                    session_id=self.session_id,
                    user_message=user_message,
                    assistant_message=assistant_message,
                    model_name=self.config.llm.model,
                    temperature=self.config.llm.temperature,
                )
            )
            if isinstance(result, Mapping) and result.get("error"):
                raise RuntimeError(f"Memory extraction failed: {result['error']}")


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
        await self._ensure_session()
        turn_number = await self._next_turn_number()
        entry = TranscriptEntry(
            id=turn.turn_id,
            session_id=self.session_id,
            turn_number=turn_number,
            user_message=turn.user_message,
            assistant_message=turn.assistant_message,
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

    async def record_context_log(self, prompt: str, raw_response: str) -> None:
        self._pending_context_log = (prompt, raw_response)

    async def finalize(self) -> None:
        await self.store.end_session(self.session_id)

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
                config_snapshot=self.config.model_dump(mode="json"),
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


def build_framework_chat_model(config: FridayChatConfig) -> FrameworkChatModel:
    service = LiteLLMService(
        model_name=config.llm.model or "unknown",
        api_key=config.llm.api_key,
        api_base=config.llm.api_base,
        resilience=ResilienceConfig(
            max_retries=config.llm.max_retries,
            timeout_seconds=config.llm.timeout_seconds or 30.0,
        ),
        thinking_enabled=config.llm.thinking,
    )
    return FrameworkChatModel(service=service, config=config)


def build_framework_embedding_service(
    config: FridayChatConfig,
) -> FrameworkEmbeddingService:
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
    )
    return FrameworkEmbeddingService(service=service)


def build_framework_memory_adapter(
    config: FridayChatConfig,
    embedding: FrameworkEmbeddingService,
    *,
    session_id: str,
) -> FrameworkMemoryAdapter:
    persist_directory = config.memory.persist_directory or ".friday/vector"
    graph_path = str(Path(persist_directory).with_name("graph.json"))
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
    controller = MemoryController(
        vector_store=vector_store,
        graph_store=graph_store,
        episodic_store=InMemoryEpisodicStore(),
        collection_manager=collection_manager,
        priming_config=config.memory.priming,
        recalc_interval=config.extraction.interval,
    )
    return FrameworkMemoryAdapter(
        controller=controller,
        collection_manager=collection_manager,
        config=config,
        session_id=session_id,
        passage_router=_build_passage_router(config),
    )


def build_framework_transcript_adapter(
    config: FridayChatConfig,
    *,
    session_id: str,
) -> FrameworkTranscriptAdapter:
    export_directory = Path(config.transcript.export_directory or "./exports")
    db_path = export_directory / "friday_transcripts.sqlite"
    return FrameworkTranscriptAdapter(
        store=SQLiteTranscriptStore(db_path),
        config=config,
        session_id=session_id,
    )


def build_framework_tool_registry(
    config: FridayChatConfig,
) -> FrameworkToolRegistryAdapter:
    tool_specs = _configured_tool_specs(config.tools.registry)
    loaded: dict[str, Any] = {}
    definitions: list[ToolDefinition] = []
    for spec in tool_specs:
        try:
            tool = _instantiate_tool(spec, config)
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
    chat_llm: FrameworkChatModel,
    llm_models: dict[str, str],
    diagnostics: Any,
) -> FrameworkMaintenanceAdapter:
    """Build real framework maintenance services for FridayV2."""
    llm_services = {
        role: _build_role_llm_service(config, role, model)
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
                wal_path = access_config.get("wal_path")
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
                        wal_path=Path(wal_path) if isinstance(wal_path, str) else None,
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
            compaction_config = CompactionConfig(**compaction_config_data)
            budget_monitor = ContextBudgetMonitor(config=compaction_config)
            compactor = InSessionCompactor(
                memory_controller=memory.controller,
                collection_manager=memory.collection_manager,
                llm_client=llm_services.get("researcher", chat_llm.service),
                config=compaction_config,
                token_estimator_config=config.memory.token_estimator,
                model_name=config.llm.model or "gpt-4",
            )
        except Exception as exc:
            diagnostics.framework_upgrade_gaps.append(
                f"Unable to initialize framework compaction: {exc}"
            )

    extractor = None
    try:
        extractor = MemoryExtractor(
            memory_controller=memory.controller,
            llm=_build_extraction_llm_service(config, chat_llm.service),
            prompt_template=(
                config.extraction.prompt
                if isinstance(config.extraction.prompt, str)
                else None
            ),
            user_name=config.chat.user_name,
            assistant_name=config.chat.assistant_name,
            embedding_model=embedding,
            max_tokens=config.extraction.max_tokens,
            rejection_log_path=config.extraction.rejection_log,
        )
    except Exception as exc:
        diagnostics.framework_upgrade_gaps.append(
            f"Unable to initialize framework extraction: {exc}"
        )

    return FrameworkMaintenanceAdapter(
        config=config,
        session_id=session_id,
        memory=memory,
        embedding=embedding,
        llm_service=chat_llm.service,
        llm_models=llm_models,
        llm_services=llm_services,
        promotion_service=promotion_service,
        access_buffer=access_buffer,
        factor_computer=factor_computer,
        incremental_maintainer=incremental_maintainer,
        budget_monitor=budget_monitor,
        compactor=compactor,
        extractor=extractor,
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


def _build_passage_router(config: FridayChatConfig) -> PassageRouter | None:
    router_config = config.memory.passage_router
    if router_config.get("enabled") is not True:
        return None
    router_model = (
        router_config.get("model")
        or config.extraction.model
        or config.llm.model
        or "unknown"
    )
    router_llm = LiteLLMService(
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
    router_kwargs = {
        key: router_config[key]
        for key in fields
        if key in router_config
    }
    router_kwargs["enabled"] = True
    return PassageRouter(
        llm=router_llm,
        config=PassageRouterConfig(**router_kwargs),
    )


def _build_role_llm_service(
    config: FridayChatConfig,
    role: str,
    model: str,
) -> LiteLLMService:
    role_config = config.maintenance.llm.get(role)
    role_data = role_config if isinstance(role_config, Mapping) else {}
    return LiteLLMService(
        model_name=model,
        api_key=_optional_string(role_data.get("api_key")) or config.llm.api_key,
        api_base=_optional_string(role_data.get("api_base")) or config.llm.api_base,
        resilience=ResilienceConfig(
            max_retries=_int_from_mapping(role_data, "max_retries", config.llm.max_retries),
            timeout_seconds=float(
                role_data.get("timeout_seconds")
                or config.llm.timeout_seconds
                or 30.0
            ),
        ),
    )


def _build_extraction_llm_service(
    config: FridayChatConfig,
    default_service: LiteLLMService,
) -> LiteLLMService:
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
    )


def _framework_maintenance_config(config: FridayChatConfig) -> FrameworkMaintenanceConfig:
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


def _instantiate_tool(spec: Mapping[str, Any], config: FridayChatConfig) -> Any:
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
        kwargs.setdefault("fallback_llm", _build_smart_file_llm_service(config))
        kwargs.setdefault("config", _build_smart_file_processor_config(config))
    return tool_class(**kwargs)


def _build_smart_file_llm_service(config: FridayChatConfig) -> LiteLLMService:
    llm_config = config.smart_file.llm
    summarizer = llm_config.get("summarizer") if isinstance(llm_config, Mapping) else {}
    summarizer_data = summarizer if isinstance(summarizer, Mapping) else {}
    return LiteLLMService(
        model_name=_optional_string(summarizer_data.get("model"))
        or config.llm.model
        or "unknown",
        api_key=_optional_string(summarizer_data.get("api_key")) or config.llm.api_key,
        api_base=_optional_string(summarizer_data.get("api_base")) or config.llm.api_base,
        resilience=ResilienceConfig(
            max_retries=_int_from_mapping(
                summarizer_data,
                "max_retries",
                config.llm.max_retries,
            ),
            timeout_seconds=float(
                summarizer_data.get("timeout_seconds")
                or config.llm.timeout_seconds
                or 30.0
            ),
        ),
    )


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


def _context_payload_to_snippets(payload: Any) -> list[str]:
    snippets: list[str] = []
    for turn in getattr(payload, "history", []) or []:
        user = getattr(turn, "user_message", None)
        assistant = getattr(turn, "assistant_message", None)
        if user:
            snippets.append(f"User: {user}")
        if assistant:
            snippets.append(f"Assistant: {assistant}")
    for item in getattr(payload, "passages", []) or []:
        text = item.get("text") if isinstance(item, dict) else None
        if isinstance(text, str) and text:
            snippets.append(text)
    for item in getattr(payload, "insights", []) or []:
        snippets.append(_metadata_text(item))
    for item in getattr(payload, "summaries", []) or []:
        snippets.append(_metadata_text(item))
    for fact in getattr(payload, "recent_memories", []) or []:
        if isinstance(fact, str) and fact:
            snippets.append(fact)
    return [snippet for snippet in snippets if snippet]


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


def _dynamic_context_budget(config: FridayChatConfig) -> int:
    context_window = config.memory.context_window or 8192
    output_buffer = config.memory.output_buffer or 1024
    return max(512, context_window - output_buffer)


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
