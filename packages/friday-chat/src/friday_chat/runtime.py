"""Runtime service construction for FridayV2."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import gettempdir
from typing import TYPE_CHECKING, Any, Protocol
from uuid import uuid4

from friday_chat.config import FridayChatConfig
from friday_chat.speech import SpeechPlaybackController, add_speech_prompt_snippet
from friday_chat.tools.registry import FakeToolRegistry
from friday_chat.tools.schemas import ToolDefinition
from friday_chat.turns.models import ChatModelResponse, InteractionTurn, ToolCallRequest

if TYPE_CHECKING:
    from friday_memory import MemoryRecoveryParticipant
    from friday_transcript import TranscriptSnapshotParticipant

    from friday_chat.reorganization.coordinator import MaintenanceMutationAdapter
    from friday_chat.reorganization.layout import FridayChatMaintenanceLayout
    from friday_chat.reorganization.mutation import LifecycleStepReport

Message = Mapping[str, Any]

MAINTENANCE_LLM_ROLES: tuple[str, ...] = (
    "synthesizer",
    "classifier",
    "researcher",
    "judge",
)

REORGANIZATION_EXECUTE_DISABLED_REASON = (
    "direct maintenance mutation is disabled; use the Friday Chat "
    "reorganization coordinator so mandatory recovery policy is enforced."
)


class ChatModel(Protocol):
    """Narrow chat model contract needed by FridayV2 turn processing."""

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ChatModelResponse:
        """Return an assistant response for the provided messages."""

    def stream_complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> AsyncIterator[str]:
        """Yield assistant response chunks for the provided messages."""


class EmbeddingService(Protocol):
    """Narrow embedding contract needed by memory and ingestion flows."""

    async def embed_text(self, text: str) -> list[float]:
        """Embed one text value."""


class ToolRegistry(Protocol):
    """Narrow tool registry contract needed by commands and turns."""

    def list_tools(self) -> Sequence[ToolDefinition]:
        """Return available tool definitions."""

    def get_context_block(self) -> str:
        """Return tool context formatted for prompts."""

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Execute one named tool."""


class MemoryController(Protocol):
    """Narrow memory contract needed by chat turns and commands."""

    async def retrieve(
        self,
        query: str,
        *,
        token_limit: int | None = None,
    ) -> list[str]:
        """Return relevant memory snippets for a query."""

    async def store_turn(self, user_message: str, assistant_message: str) -> None:
        """Store a completed user/assistant turn."""

    async def ingest_document(
        self,
        *,
        source_path: str,
        description: str | None,
        content: str,
    ) -> int:
        """Store ingested document chunks and return chunk count."""

    async def debug_retrieval(self, query: str) -> dict[str, Any]:
        """Return retrieval diagnostics for a query."""

    async def list_entities(self, name: str | None = None) -> list[dict[str, Any]]:
        """Return graph entity records."""

    async def list_relationships(self, name: str | None = None) -> list[dict[str, Any]]:
        """Return graph relationship records."""

    async def list_insights(self) -> list[dict[str, Any]]:
        """Return insight records."""

    async def list_summaries(self) -> list[dict[str, Any]]:
        """Return summary records."""

    async def list_meta_insights(self) -> list[dict[str, Any]]:
        """Return meta-insight records."""


class TranscriptStore(Protocol):
    """Narrow transcript contract needed by lifecycle and exports."""

    async def record_turn(self, user_message: str, assistant_message: str) -> None:
        """Persist one chat turn."""

    async def record_interaction(self, turn: InteractionTurn) -> None:
        """Persist a rich interaction turn."""

    async def record_context_log(self, prompt: str, raw_response: str) -> None:
        """Persist a raw prompt/response context log."""

    async def finalize(self) -> None:
        """Finalize any active transcript resources."""


class SpeechAdapter(Protocol):
    """Narrow speech contract for optional TTS output."""

    enabled: bool

    async def speak(self, text: str) -> None:
        """Speak one assistant response."""

    def cancel(self) -> None:
        """Cancel active speech playback."""


class Orchestrator(Protocol):
    """Narrow delegation contract for agent orchestration."""

    active_agent: str
    message_count: int
    cache_state: str
    agents: dict[str, tuple[str, ...]]

    async def run(self, instruction: str) -> str:
        """Run an orchestration instruction."""

    async def route(self, agent: str, message: str) -> str:
        """Route a message to a named agent."""

    def switch(self, agent: str) -> None:
        """Switch active agent."""

    def describe_agent(self, agent: str) -> str:
        """Describe one agent."""


class WorkflowEngine(Protocol):
    """Narrow workflow contract for Friday workflow commands."""

    async def run_workflow(self, name: str, arguments: Mapping[str, Any]) -> str:
        """Run a named workflow."""

    def list_workflows(self) -> dict[str, str]:
        """List workflow definitions."""

    def status(self) -> str:
        """Return workflow status."""

    async def approve(self, approval_id: str | None = None) -> str:
        """Approve pending workflow."""

    async def skip(self, approval_id: str | None = None) -> str:
        """Skip pending workflow."""


class MaintenanceService(Protocol):
    """Narrow maintenance contract used by app and background work."""

    llm_models: dict[str, str]
    actions: list[str]
    reset_calls: list[str]
    archived_transcripts: bool
    pending_extraction: list[tuple[str, str]]
    flush_pending_error: BaseException | None
    compaction_running: bool
    compaction_calls: list[dict[str, Any]]
    errors: list[BaseException]
    migration_needed: bool
    background_actions: list[str]

    async def flush_memory(self) -> None:
        """Flush memory buffers."""

    async def run_lifecycle(self) -> None:
        """Run lifecycle maintenance."""

    async def preview_reorganization_lifecycle(self) -> LifecycleStepReport:
        """Report reorganization lifecycle scope without mutation."""

    async def run_reorganization_lifecycle(self) -> LifecycleStepReport:
        """Run promotion/decay reorganization without embedding backfill."""

    async def reorganize_memory(self, mode: str) -> None:
        """Run configured memory reorganization."""

    def reorganization_execute_status(self) -> tuple[bool, str]:
        """Report whether mutating reorganization is currently safe."""

    async def flush_pending_extraction(self) -> int:
        """Flush pending extraction turns."""

    async def extract_buffered_turns(self, *, trigger_reason: str) -> int:
        """Extract buffered turns."""

    async def run_tool_decay(self) -> None:
        """Run tool decay maintenance."""

    async def run_incremental_graph_maintenance(self) -> None:
        """Run incremental graph maintenance."""

    async def compact(
        self,
        *,
        trigger_reason: str,
        time_budget_ms: int | None = None,
        current_tokens: int | None = None,
        available_budget: int | None = None,
        target_utilization: float | None = None,
    ) -> dict[str, Any]:
        """Run context compaction."""

    async def reset_store(self, store: str) -> str:
        """Reset one memory store."""

    async def archive_transcripts(self) -> None:
        """Archive transcripts for reset."""

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
        """Run manual reorganization."""

    async def lifecycle(self, *, mode: str, dry_run: bool) -> dict[str, Any]:
        """Run lifecycle command."""

    async def migrate(self, *, execute: bool) -> dict[str, Any]:
        """Run lifecycle migration."""


@dataclass
class RuntimeDiagnostics:
    """Diagnostics produced during runtime construction."""

    maintenance_llm_fallbacks: list[str] = field(default_factory=list)
    tool_context_injected: bool = False
    maintenance_warnings: list[str] = field(default_factory=list)
    framework_upgrade_gaps: list[str] = field(default_factory=list)


@dataclass
class FridayRuntime:
    """Concrete bundle of FridayV2 runtime services."""

    config: FridayChatConfig
    chat_llm: ChatModel
    embedding: EmbeddingService
    memory: MemoryController
    transcript: TranscriptStore
    tools: ToolRegistry
    speech: SpeechAdapter
    orchestrator: Orchestrator
    workflow: WorkflowEngine
    maintenance: MaintenanceService
    diagnostics: RuntimeDiagnostics
    maintenance_layout: FridayChatMaintenanceLayout
    memory_recovery: MemoryRecoveryParticipant | None
    transcript_recovery: TranscriptSnapshotParticipant | None
    reorganization_mutation: MaintenanceMutationAdapter | None = None
    tool_context: str | None = None
    budget_monitor: Any | None = None
    compactor: Any | None = None
    compaction_task: asyncio.Task[Any] | None = None


@dataclass
class FakeChatModel:
    """Deterministic fake chat model for parity tests."""

    model: str
    responses: list[str | ChatModelResponse] = field(default_factory=list)
    failures: list[BaseException] = field(default_factory=list)
    delay_seconds: float = 0.0
    calls: list[list[Message]] = field(default_factory=list)

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ChatModelResponse:
        self.calls.append(list(messages))
        if self.delay_seconds > 0:
            await asyncio.sleep(self.delay_seconds)
        if self.failures:
            raise self.failures.pop(0)
        if self.responses:
            response = self.responses.pop(0)
            if isinstance(response, str):
                return ChatModelResponse.from_text(response)
            return response
        if messages and messages[-1].get("role") == "tool":
            return ChatModelResponse.from_text(
                f"Friday: {messages[-1].get('content', '')}"
            )
        content = messages[-1].get("content", "") if messages else ""
        lowered = str(content).lower()
        tool_names = {tool.name for tool in tools}
        if "get_current_datetime" in tool_names and (
            "date" in lowered or "time" in lowered
        ):
            return ChatModelResponse(
                tool_calls=(
                    ToolCallRequest(
                        name="get_current_datetime",
                        arguments={"format": "human", "timezone_name": "local"},
                        call_id="fake-date-time",
                    ),
                )
            )
        return ChatModelResponse.from_text(f"Friday: {content}")

    async def stream_complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> AsyncIterator[str]:
        from friday_chat.turns.streaming import stream_text

        response = await self.complete(messages, tools=tools)
        async for chunk in stream_text(response.content):
            yield chunk


@dataclass
class FakeEmbeddingService:
    """Deterministic embedding service that avoids provider calls."""

    dimensions: int = 3

    async def embed_text(self, text: str) -> list[float]:
        checksum = sum(ord(character) for character in text) % 997
        values = [float(len(text)), float(len(text.split())), float(checksum)]
        return values[: self.dimensions]


@dataclass
class FakeMemoryController:
    """In-memory fake memory controller for tests."""

    stored_turns: list[tuple[str, str]] = field(default_factory=list)
    retrievals: list[str] = field(default_factory=list)
    retrieval_token_limits: list[int | None] = field(default_factory=list)
    ingested_documents: list[dict[str, str | int | None]] = field(default_factory=list)
    summaries: list[dict[str, Any]] = field(default_factory=list)
    entities: list[dict[str, Any]] = field(default_factory=list)
    relationships: list[dict[str, Any]] = field(default_factory=list)

    async def retrieve(
        self,
        query: str,
        *,
        token_limit: int | None = None,
    ) -> list[str]:
        self.retrievals.append(query)
        self.retrieval_token_limits.append(token_limit)
        snippets: list[str] = []
        for user, assistant in self.stored_turns[-3:]:
            snippets.append(f"User: {user}")
            snippets.append(f"Assistant: {assistant}")
        return snippets

    async def store_turn(self, user_message: str, assistant_message: str) -> None:
        self.stored_turns.append((user_message, assistant_message))

    async def ingest_document(
        self,
        *,
        source_path: str,
        description: str | None,
        content: str,
    ) -> int:
        chunk_count = max(1, (len(content) + 2047) // 2048)
        self.ingested_documents.append(
            {
                "source_path": source_path,
                "description": description,
                "content_length": len(content),
                "chunk_count": chunk_count,
            }
        )
        return chunk_count

    async def debug_retrieval(self, query: str) -> dict[str, Any]:
        snippets = await self.retrieve(query)
        return {
            "query": query,
            "result_count": len(snippets),
            "snippets": snippets,
        }

    async def list_entities(self, name: str | None = None) -> list[dict[str, Any]]:
        if not name:
            return list(self.entities)
        lowered = name.lower()
        return [
            entity
            for entity in self.entities
            if lowered in str(entity.get("label", entity.get("id", ""))).lower()
        ]

    async def list_relationships(self, name: str | None = None) -> list[dict[str, Any]]:
        if not name:
            return list(self.relationships)
        lowered = name.lower()
        return [
            relationship
            for relationship in self.relationships
            if lowered
            in " ".join(
                (
                    str(relationship.get("source_label", "")),
                    str(relationship.get("target_label", "")),
                    str(relationship.get("relation", "")),
                )
            ).lower()
        ]

    async def list_insights(self) -> list[dict[str, Any]]:
        return []

    async def list_summaries(self) -> list[dict[str, Any]]:
        return list(self.summaries)

    async def record_summary(self, text: str, metadata: Mapping[str, Any]) -> None:
        self.summaries.append({"text": text, "metadata": dict(metadata)})

    async def list_meta_insights(self) -> list[dict[str, Any]]:
        return []


@dataclass
class FakeTranscriptStore:
    """In-memory transcript store for runtime and lifecycle tests."""

    turns: list[tuple[str, str]] = field(default_factory=list)
    interactions: list[InteractionTurn] = field(default_factory=list)
    context_logs: list[tuple[str, str]] = field(default_factory=list)
    session_system_prompt: str | None = None
    finalized: bool = False

    async def record_turn(self, user_message: str, assistant_message: str) -> None:
        self.turns.append((user_message, assistant_message))

    async def record_interaction(self, turn: InteractionTurn) -> None:
        self.interactions.append(turn)

    async def record_context_log(self, prompt: str, raw_response: str) -> None:
        self.context_logs.append((prompt, raw_response))

    async def finalize(self) -> None:
        self.finalized = True


@dataclass
class FakeSpeechAdapter:
    """No-op speech adapter that records requested speech output."""

    enabled: bool = False
    spoken: list[str] = field(default_factory=list)
    playback: SpeechPlaybackController = field(default_factory=SpeechPlaybackController)

    async def speak(self, text: str) -> None:
        if self.enabled:
            self.spoken.append(text)
            self.playback.start(text)

    def cancel(self) -> None:
        """Cancel fake speech playback."""
        self.playback.cancel()


@dataclass
class FakeOrchestrator:
    """Deterministic orchestration fake."""

    calls: list[str] = field(default_factory=list)
    agents: dict[str, tuple[str, ...]] = field(
        default_factory=lambda: {
            "friday": ("general", "memory"),
            "researcher": ("research", "summarize"),
            "coder": ("code", "review"),
        }
    )
    active_agent: str = "friday"
    message_count: int = 0
    cache_state: str = "warm"

    async def run(self, instruction: str) -> str:
        self.calls.append(instruction)
        return f"orchestrated: {instruction}"

    async def route(self, agent: str, message: str) -> str:
        """Route a message to a fake agent."""
        if agent not in self.agents:
            raise KeyError(f"Unknown agent: {agent}")
        self.message_count += 1
        self.calls.append(f"{agent}:{message}")
        return f"{agent}: {message}"

    async def delegate(
        self,
        agent: str,
        task: str,
        **_: Any,
    ) -> str:
        """Delegate a workflow task to a fake agent."""
        return await self.route(agent, task)

    def switch(self, agent: str) -> None:
        """Switch active fake agent."""
        if agent not in self.agents:
            raise KeyError(f"Unknown agent: {agent}")
        self.active_agent = agent

    def describe_agent(self, agent: str) -> str:
        """Describe one fake agent."""
        if agent not in self.agents:
            raise KeyError(f"Unknown agent: {agent}")
        marker = "active" if agent == self.active_agent else "available"
        return f"{agent} ({marker}): {', '.join(self.agents[agent])}"


@dataclass
class FakeWorkflowEngine:
    """Deterministic workflow fake."""

    calls: list[tuple[str, Mapping[str, Any]]] = field(default_factory=list)
    workflows: dict[str, str] = field(
        default_factory=lambda: {
            "newsletter": "Draft a newsletter workflow.",
            "research": "Research and summarize a topic.",
        }
    )
    active_workflow: str | None = None
    pending_approval: str | None = None

    async def run_workflow(self, name: str, arguments: Mapping[str, Any]) -> str:
        if name not in self.workflows:
            raise KeyError(f"Unknown workflow: {name}")
        self.calls.append((name, arguments))
        self.active_workflow = name
        self.pending_approval = f"{name}:approval"
        return f"workflow {name} complete"

    def list_workflows(self) -> dict[str, str]:
        """Return fake workflow definitions."""
        return dict(self.workflows)

    def status(self) -> str:
        """Return fake workflow status."""
        if self.active_workflow is None:
            return "No active workflow."
        pending = self.pending_approval or "none"
        return f"Active workflow: {self.active_workflow}\nPending approval: {pending}"

    async def approve(self, approval_id: str | None = None) -> str:
        """Approve the pending fake workflow step."""
        if self.pending_approval is None:
            return "No pending approval."
        approved = self.pending_approval
        self.pending_approval = None
        return f"Approved {approval_id or approved}."

    async def skip(self, approval_id: str | None = None) -> str:
        """Skip the pending fake workflow step."""
        if self.pending_approval is None:
            return "No pending approval."
        skipped = self.pending_approval
        self.pending_approval = None
        return f"Skipped {approval_id or skipped}."


@dataclass
class FakeMaintenanceService:
    """Runtime maintenance fake with explicit LLM role resolution."""

    llm_models: dict[str, str]
    summary_sink: FakeMemoryController | None = None
    actions: list[str] = field(default_factory=list)
    reset_calls: list[str] = field(default_factory=list)
    archived_transcripts: bool = False
    pending_extraction: list[tuple[str, str]] = field(default_factory=list)
    flush_pending_error: BaseException | None = None
    compaction_running: bool = False
    compaction_calls: list[dict[str, Any]] = field(default_factory=list)
    errors: list[BaseException] = field(default_factory=list)
    migration_needed: bool = True
    background_actions: list[str] = field(default_factory=list)

    def reorganization_execute_status(self) -> tuple[bool, str]:
        """Keep direct fake-runtime mutation outside the coordinator disabled."""
        return False, REORGANIZATION_EXECUTE_DISABLED_REASON

    async def flush_memory(self) -> None:
        """Record configured memory flush maintenance."""
        self.actions.append("flush_memory")

    async def run_lifecycle(self) -> None:
        """Record configured lifecycle maintenance."""
        self.actions.append("run_lifecycle")

    async def preview_reorganization_lifecycle(self) -> LifecycleStepReport:
        """Return a provider-free fake lifecycle preview."""
        from friday_chat.reorganization.mutation import LifecycleStepReport

        return LifecycleStepReport(
            succeeded=True,
            scanned_count=0,
            candidate_count=0,
            changed_count=None,
        )

    async def run_reorganization_lifecycle(self) -> LifecycleStepReport:
        """Return a provider-free fake lifecycle execution report."""
        from friday_chat.reorganization.mutation import LifecycleStepReport

        self.actions.append("run_reorganization_lifecycle")
        return LifecycleStepReport(
            succeeded=True,
            scanned_count=0,
            candidate_count=0,
            changed_count=0,
        )

    async def reorganize_memory(self, mode: str) -> None:
        """Refuse the fake direct mutation path outside the coordinator."""
        _allowed, reason = self.reorganization_execute_status()
        self.actions.append("reorganize_skipped:execute_disabled")
        self.background_actions.append(f"reorganize_execute_disabled:{reason}")

    async def reset_store(self, store: str) -> str:
        """Record reset of one fake memory store."""
        self.reset_calls.append(store)
        self._raise_next_error()
        return f"reset {store}"

    async def archive_transcripts(self) -> None:
        """Record transcript archival for full reset."""
        self.archived_transcripts = True

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
        """Record a fake reorganization request."""
        if not dry_run:
            _allowed, reason = self.reorganization_execute_status()
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
        self.actions.append(f"reorganize:{mode}")
        return {
            "mode": mode,
            "dry_run": dry_run,
            "backup_first": backup_first,
            "skip_synthesis": skip_synthesis,
            "skip_verify": skip_verify,
            "skip_lifecycle": skip_lifecycle,
            "force_reembed": force_reembed,
            "scanned": 10,
            "changed": 2 if not dry_run else 0,
            "errors": [],
        }

    async def lifecycle(
        self,
        *,
        mode: str,
        dry_run: bool,
    ) -> dict[str, Any]:
        """Record a fake lifecycle request."""
        self._raise_next_error()
        self.actions.append(f"lifecycle:{mode}")
        return {
            "mode": mode,
            "dry_run": dry_run,
            "promoted": 1 if not dry_run else 0,
            "decayed": 2 if not dry_run else 0,
            "reactivated": 0,
            "short_term": 3,
            "long_term": 4,
            "decayed_count": 2,
            "access_buffer": 1,
            "errors": [],
        }

    async def migrate(self, *, execute: bool) -> dict[str, Any]:
        """Record a fake lifecycle metadata migration."""
        self._raise_next_error()
        self.actions.append(f"migrate:{'execute' if execute else 'dry-run'}")
        if not self.migration_needed and not execute:
            return {
                "needed": False,
                "vector_scanned": 0,
                "graph_nodes_scanned": 0,
                "graph_edges_scanned": 0,
                "migrated": 0,
                "skipped": 0,
                "errors": [],
            }
        return {
            "needed": True,
            "vector_scanned": 5,
            "graph_nodes_scanned": 6,
            "graph_edges_scanned": 7,
            "migrated": 3 if execute else 0,
            "skipped": 2,
            "errors": [],
        }

    async def flush_pending_extraction(self) -> int:
        """Flush pending extraction turns before compaction."""
        if self.flush_pending_error is not None:
            raise self.flush_pending_error
        flushed = len(self.pending_extraction)
        self.pending_extraction.clear()
        self.actions.append("flush_pending_extraction")
        return flushed

    async def extract_buffered_turns(self, *, trigger_reason: str) -> int:
        """Run fake entity/fact extraction for buffered turns."""
        if self.flush_pending_error is not None:
            raise self.flush_pending_error
        extracted = len(self.pending_extraction)
        self.pending_extraction.clear()
        self.background_actions.append(f"extract:{trigger_reason}:{extracted}")
        return extracted

    async def run_tool_decay(self) -> None:
        """Record fake tool lifecycle decay."""
        self.background_actions.append("tool_decay")

    async def run_incremental_graph_maintenance(self) -> None:
        """Record fake incremental graph maintenance."""
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
        """Run fake compaction."""
        self._raise_next_error()
        self.compaction_running = True
        call = {
            "trigger_reason": trigger_reason,
            "current_tokens": current_tokens if current_tokens is not None else 900,
            "available_budget": (
                available_budget if available_budget is not None else 100
            ),
            "target_utilization": (
                target_utilization if target_utilization is not None else 0.8
            ),
            "time_budget_ms": time_budget_ms if time_budget_ms is not None else 250,
        }
        self.compaction_calls.append(call)
        self.actions.append("compact")
        self.compaction_running = False
        summary_text = "Compacted 2 FridayV2 test turns."
        if self.summary_sink is not None:
            await self.summary_sink.record_summary(
                summary_text,
                {
                    "type": "summary",
                    "source_type": "in_session_compaction",
                    "trigger_reason": trigger_reason,
                },
            )
        return {
            "turns_summarized": 2,
            "tokens_saved": 300,
            "tokens_target": 250,
            "target_met": True,
            "insights_deduplicated": 1,
            "memories_promoted": 1,
            "duration_ms": 12.0,
            "time_budget_exhausted": False,
            "errors": [],
            "summary": summary_text,
            **call,
        }

    def _raise_next_error(self) -> None:
        if self.errors:
            raise self.errors.pop(0)


def build_runtime(
    config: FridayChatConfig,
    *,
    fake: bool = True,
    session_id: str = "friday-v2",
) -> FridayRuntime:
    """Build a FridayV2 runtime bundle from typed config."""
    config = _apply_startup_speech_prompt(config)
    if not fake:
        from friday_chat.reorganization.assembly import resolve_maintenance_layout

        captured_process_cwd = Path.cwd()
        maintenance_layout = resolve_maintenance_layout(
            config,
            captured_process_cwd=captured_process_cwd,
        )
        return _build_framework_runtime(
            config,
            session_id=session_id,
            maintenance_layout=maintenance_layout,
        )

    from friday_chat.reorganization.layout import FridayChatMaintenanceLayout

    fake_root = Path(gettempdir()).resolve() / f"friday-chat-fake-{uuid4().hex}"
    maintenance_layout = FridayChatMaintenanceLayout.resolve_once(
        captured_process_cwd=fake_root,
        vector_directory=fake_root / "vector",
        graph_path=fake_root / "graph.json",
        access_buffer_wal_path=None,
        transcript_database_path=fake_root / "transcript.sqlite",
        recovery_root=fake_root / "recovery",
        log_root=fake_root / "logs",
    )

    diagnostics = RuntimeDiagnostics()
    enabled_categories = _enabled_tool_categories(config.tools.registry)
    tools = FakeToolRegistry.from_enabled_categories(enabled_categories)
    tool_definitions = tools.list_tools() if config.tools.enabled else ()
    tool_context = None
    if config.tools.enabled and config.tools.context.get("include_in_context") is True:
        tool_context = tools.get_context_block()
        diagnostics.tool_context_injected = True

    maintenance_models, fallbacks = _resolve_maintenance_llms(config)
    diagnostics.maintenance_llm_fallbacks = fallbacks
    budget_monitor = _build_budget_monitor(config, diagnostics)
    memory = FakeMemoryController()
    maintenance = FakeMaintenanceService(
        llm_models=maintenance_models,
        summary_sink=memory,
    )

    return FridayRuntime(
        config=config,
        chat_llm=FakeChatModel(model=config.llm.model or "unknown"),
        embedding=FakeEmbeddingService(),
        memory=memory,
        transcript=FakeTranscriptStore(session_system_prompt=config.chat.system_prompt),
        tools=tools,
        speech=FakeSpeechAdapter(enabled=config.speech.enabled),
        orchestrator=FakeOrchestrator(),
        workflow=FakeWorkflowEngine(),
        maintenance=maintenance,
        diagnostics=diagnostics,
        maintenance_layout=maintenance_layout,
        memory_recovery=None,
        transcript_recovery=None,
        reorganization_mutation=None,
        tool_context=tool_context if tool_definitions else None,
        budget_monitor=budget_monitor,
        compactor=maintenance if budget_monitor is not None else None,
    )


def _apply_startup_speech_prompt(config: FridayChatConfig) -> FridayChatConfig:
    if not config.speech.enabled:
        return config
    config.chat.system_prompt = add_speech_prompt_snippet(config.chat.system_prompt)
    return config


def _resolve_maintenance_llms(
    config: FridayChatConfig,
) -> tuple[dict[str, str], list[str]]:
    models: dict[str, str] = {}
    fallbacks: list[str] = []
    role_configs = config.maintenance.llm

    for role in MAINTENANCE_LLM_ROLES:
        model = None
        role_config = role_configs.get(role)
        if isinstance(role_config, Mapping):
            raw_model = role_config.get("model")
            if isinstance(raw_model, str) and raw_model:
                model = raw_model

        if model is None:
            model = config.llm.model or "unknown"
            fallbacks.append(role)

        models[role] = model

    return models, fallbacks


def _build_framework_runtime(
    config: FridayChatConfig,
    *,
    session_id: str,
    maintenance_layout: FridayChatMaintenanceLayout,
) -> FridayRuntime:
    from friday_chat.adapters import (
        build_framework_chat_model,
        build_framework_embedding_service,
        build_framework_maintenance_adapter,
        build_framework_memory_adapter,
        build_framework_tool_registry,
        build_framework_transcript_adapter,
        build_framework_workflow_adapter,
    )

    diagnostics = RuntimeDiagnostics()
    chat_llm = build_framework_chat_model(config)
    embedding = build_framework_embedding_service(config)
    memory = build_framework_memory_adapter(
        config,
        embedding,
        session_id=session_id,
        maintenance_layout=maintenance_layout,
    )
    transcript = build_framework_transcript_adapter(
        config,
        session_id=session_id,
        maintenance_layout=maintenance_layout,
    )
    tools = build_framework_tool_registry(config)
    tool_definitions = tools.list_tools() if config.tools.enabled else ()
    tool_context = None
    if config.tools.enabled and config.tools.context.get("include_in_context") is True:
        tool_context = tools.get_context_block()
        diagnostics.tool_context_injected = True

    maintenance_models, fallbacks = _resolve_maintenance_llms(config)
    diagnostics.maintenance_llm_fallbacks = fallbacks

    orchestrator = FakeOrchestrator()
    workflow = build_framework_workflow_adapter(config, orchestrator=orchestrator)
    maintenance = build_framework_maintenance_adapter(
        config,
        session_id=session_id,
        memory=memory,
        embedding=embedding,
        chat_llm=chat_llm,
        llm_models=maintenance_models,
        diagnostics=diagnostics,
        maintenance_layout=maintenance_layout,
    )

    from friday_memory import (
        ExplicitMemoryMutationParticipant,
        MemoryMaintenanceLayout,
        MemoryMaintenanceParticipant,
    )

    from friday_chat.reorganization.mutation import (
        FrameworkMaintenanceMutationAdapter,
        build_explicit_maintenance_provider_registry,
    )

    memory_recovery = (
        MemoryMaintenanceParticipant(
            MemoryMaintenanceLayout(
                vector_directory=maintenance_layout.vector_directory,
                graph_path=maintenance_layout.graph_path,
                access_buffer_wal_path=maintenance_layout.access_buffer_wal_path,
                recovery_directory=maintenance_layout.recovery_root,
                log_directory=maintenance_layout.log_root,
            ),
            graph_store=memory.recovery_graph_store,
            access_buffer=maintenance.access_buffer,
        )
        if memory.recovery_graph_store is not None
        else None
    )
    memory_mutation = (
        ExplicitMemoryMutationParticipant(
            MemoryMaintenanceLayout(
                vector_directory=maintenance_layout.vector_directory,
                graph_path=maintenance_layout.graph_path,
                access_buffer_wal_path=maintenance_layout.access_buffer_wal_path,
                recovery_directory=maintenance_layout.recovery_root,
                log_directory=maintenance_layout.log_root,
            ),
            graph_store=memory.recovery_graph_store,
        )
        if memory.recovery_graph_store is not None
        else None
    )
    reorganization_mutation = (
        FrameworkMaintenanceMutationAdapter(
            memory=memory_mutation,
            providers=build_explicit_maintenance_provider_registry(config),
            lifecycle=maintenance,
        )
        if memory_mutation is not None
        else None
    )

    return FridayRuntime(
        config=config,
        chat_llm=chat_llm,
        embedding=embedding,
        memory=memory,
        transcript=transcript,
        tools=tools,
        speech=FakeSpeechAdapter(enabled=config.speech.enabled),
        orchestrator=orchestrator,
        workflow=workflow,
        maintenance=maintenance,
        diagnostics=diagnostics,
        maintenance_layout=maintenance_layout,
        memory_recovery=memory_recovery,
        transcript_recovery=transcript.store,
        reorganization_mutation=reorganization_mutation,
        tool_context=tool_context if tool_definitions else None,
        budget_monitor=maintenance.budget_monitor,
        compactor=maintenance.compactor,
    )


def _build_budget_monitor(
    config: FridayChatConfig,
    diagnostics: RuntimeDiagnostics,
) -> Any | None:
    compaction_config_data = config.memory.compaction
    if compaction_config_data.get("enabled") is not True:
        return None
    try:
        from friday_memory.context.budget_monitor import ContextBudgetMonitor
        from friday_memory.models.budget import CompactionConfig

        return ContextBudgetMonitor(config=CompactionConfig(**compaction_config_data))
    except Exception as exc:
        diagnostics.framework_upgrade_gaps.append(
            f"Unable to initialize ContextBudgetMonitor: {exc}"
        )
        return None


def _read_string_sequence(value: Any) -> tuple[str, ...] | None:
    if value is None:
        return None
    if not isinstance(value, Sequence) or isinstance(value, str):
        return None
    return tuple(item for item in value if isinstance(item, str))


def _enabled_tool_categories(registry_config: Any) -> tuple[str, ...] | None:
    if not isinstance(registry_config, Mapping):
        return None
    return _read_string_sequence(registry_config.get("enabled_categories"))


__all__ = [
    "MAINTENANCE_LLM_ROLES",
    "REORGANIZATION_EXECUTE_DISABLED_REASON",
    "ChatModel",
    "EmbeddingService",
    "FakeChatModel",
    "FakeEmbeddingService",
    "FakeMaintenanceService",
    "FakeMemoryController",
    "FakeOrchestrator",
    "FakeSpeechAdapter",
    "FakeTranscriptStore",
    "FakeWorkflowEngine",
    "FridayRuntime",
    "InteractionTurn",
    "MemoryController",
    "Orchestrator",
    "RuntimeDiagnostics",
    "SpeechAdapter",
    "TranscriptStore",
    "ToolRegistry",
    "WorkflowEngine",
    "build_runtime",
]
