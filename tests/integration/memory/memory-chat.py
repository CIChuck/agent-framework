#!/usr/bin/env python3
"""
Friday-Memory Integration Test - Memory Chat CLI

A command-line chat application that tests friday-memory's context engineering
components through an interactive chat interface with persistent memory.

Tests:
- ContextAssembler (context orchestration)
- PromptArchitect (token budgeting)
- MemoryController (unified memory facade)
- All three memory stores (episodic, vector, graph)
- ChromaDB persistence to disk

Usage:
    python memory-chat.py [--config CONFIG_PATH]

Commands (prefix with /):
  /exit, /quit     - Exit the chat
  /clear           - Clear conversation history
  /history         - Show conversation history
  /memory          - Show memory statistics
  /context         - Show assembled context payload (FULL, no truncation)
  /prompt          - Show full formatted prompt sent to LLM (FULL, no truncation)
  /prime           - Load and show primed context (works before first turn)
  /debug           - Show debug info from context assembly
  /entities        - List graph entities and relationships
  /facts           - List all documents from vector store (insights + summaries)
  /insights        - List only insights (type='insight') with structured metadata
  /summaries       - List only turn summaries (type='summary')
  /meta            - List only meta insights (type='meta_insight') from synthesis
  /sessions        - List all stored transcript sessions
  /transcript      - Show current session's transcript
  /transcript <id> - Show transcript for a specific session
  /transcript export - Export entire database to CSV
  /export [format] - Export current session (jsonl, markdown, or training)
  /reset           - Clear all memory stores (graph, vector, episodic)
  /reorganize [opts] - Run memory reorganization (analyze, prune, synthesize)
  /vars            - Show scoped variables
  /set <key> <val> - Set a scoped variable
  /help            - Show available commands
"""

import asyncio
import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# Logging will be configured after config is loaded (see main())
logger = logging.getLogger(__name__)

from friday_core import DebugTelemetryRecorder, TranscriptBackedEpisodicStore
from friday_llm import (
    CircuitBreakerOpenError,
    LiteLLMEmbeddingService,
    LiteLLMService,
    LLMRetryExhaustedError,
    LLMTimeoutError,
    ResilienceConfig,
)
from friday_memory import (
    ChromaVectorStore,
    ContextAssembler,
    ContextPayload,
    ElementXGraphStore,
    InteractionTurn,
    MemoryController,
    MemoryExtractor,
    PromptArchitect,
    SessionState,
)
from friday_memory.maintenance import MemoryReorganizer
from friday_memory.maintenance.models import (
    EmbeddingConfig,
    FactCheckConfig,
    LogConfig,
    LogFormat,
    LogVerbosity,
    MaintenanceConfig,
    PromptsConfig,
    PruneConfig,
    SynthesisConfig,
)
from friday_transcript import (
    CSVExporter,
    JSONLExporter,
    MarkdownExporter,
    SQLiteTranscriptStore,
    TranscriptSession,
)


def load_config(config_path: Path) -> dict[str, Any]:
    """Load configuration from YAML file."""
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        return yaml.safe_load(f)


def print_banner() -> None:
    """Print welcome banner."""
    print("""
+==================================================================+
|              Friday-Memory Integration Test CLI                  |
|                                                                  |
|  Type your message and press Enter to chat.                      |
|  Type /help for available commands.                              |
|  Type /exit or /quit to end the conversation.                    |
+==================================================================+
""")


class MemoryChatSession:
    """Manages a multi-turn chat session with memory integration."""

    def __init__(
        self,
        llm: LiteLLMService,
        controller: MemoryController,
        assembler: ContextAssembler,
        architect: PromptArchitect,
        system_prompt: str,
        session_id: str,
        user_id: str,
        temperature: float = 0.7,
        max_history_turns: int = 10,
        extractor: "MemoryExtractor | None" = None,
        user_name: str = "You",
        assistant_name: str = "Assistant",
        transcript_store: "SQLiteTranscriptStore | None" = None,
        context_format: str = "plain",
        persist_dir: "Path | None" = None,
        maintenance_config: "MaintenanceConfig | None" = None,
        maintenance_llms: "dict[str, LiteLLMService] | None" = None,
        transcript_export_dir: "Path | None" = None,
        embedding_function: any = None,
    ):
        self.llm = llm
        self.controller = controller
        self.assembler = assembler
        self.architect = architect
        self.system_prompt = system_prompt
        self.session_id = session_id
        self.user_id = user_id
        self.temperature = temperature
        self.max_history_turns = max_history_turns
        self.extractor = extractor
        self.user_name = user_name
        self.assistant_name = assistant_name
        self.transcript_store = transcript_store
        self.context_format = context_format
        self.persist_dir = persist_dir
        self.maintenance_config = maintenance_config
        self.maintenance_llms = maintenance_llms or {}
        self.transcript_export_dir = transcript_export_dir
        self.embedding_function = embedding_function

        # State tracking
        self.state: SessionState | None = None
        self.last_payload: ContextPayload | None = None
        self.last_messages: list[dict[str, Any]] | None = None  # Last formatted prompt
        self.turn_ids: list[str] = []

    async def initialize(self) -> None:
        """Initialize the session state."""
        self.state = await self.assembler.initialize_session(
            self.session_id, self.user_id
        )
        # Set some default scoped variables
        self.state.set_var("user:id", self.user_id)
        self.state.set_var("session:started", datetime.now().isoformat())

    async def handle_command(self, user_input: str) -> str | None:
        """Handle /commands. Returns response string or None if not a command."""
        if not user_input.startswith("/"):
            return None  # Not a command, process as chat

        parts = user_input[1:].split(maxsplit=2)  # Remove "/" and split
        cmd = parts[0].lower() if parts else ""

        match cmd:
            case "exit" | "quit":
                return "EXIT"  # Special signal to exit loop
            case "clear":
                return self.cmd_clear()
            case "history":
                return await self.cmd_history()
            case "memory":
                return self.cmd_memory()
            case "context":
                return self.cmd_context()
            case "prompt":
                return self.cmd_prompt()
            case "debug":
                return self.cmd_debug()
            case "entities":
                return await self.cmd_entities()
            case "facts":
                return await self.cmd_facts()
            case "insights":
                return await self.cmd_insights()
            case "summaries":
                return await self.cmd_summaries()
            case "meta":
                return await self.cmd_meta_insights()
            case "prime":
                return await self.cmd_prime()
            case "sessions":
                return await self.cmd_sessions()
            case "transcript":
                # Check for subcommands: /transcript <session_id> or /transcript export
                arg = parts[1] if len(parts) > 1 else None
                return await self.cmd_transcript(arg)
            case "export":
                format_type = parts[1] if len(parts) > 1 else "markdown"
                return await self.cmd_export(format_type)
            case "reset":
                return await self.cmd_reset()
            case "reorganize":
                # Parse options from remaining args
                opts = parts[1] if len(parts) > 1 else ""
                return await self.cmd_reorganize(opts)
            case "vars":
                return self.cmd_vars()
            case "set":
                if len(parts) >= 3:
                    return self.cmd_set(parts[1], parts[2])
                return "Usage: /set <key> <value>"
            case "help":
                return self.cmd_help()
            case _:
                return f"Unknown command: /{cmd}. Type /help for available commands."

    def cmd_clear(self) -> str:
        """Clear conversation history."""
        self.turn_ids.clear()
        self.last_payload = None
        if self.state:
            self.state.turn_count = 0
        return "Conversation history cleared."

    async def cmd_history(self) -> str:
        """Show conversation history (up to 100 turns from episodic store)."""
        try:
            # Fetch directly from episodic store for comprehensive view
            turns = await self.controller.episodic.get_turns(self.session_id, limit=100)
            if not turns:
                return "No conversation history yet."

            lines = ["=" * 60, f"CONVERSATION HISTORY ({len(turns)} turns)", "=" * 60]
            for i, turn in enumerate(turns, 1):
                user_msg = turn.user_message[:100] + "..." if len(turn.user_message) > 100 else turn.user_message
                asst_msg = turn.assistant_message[:100] + "..." if len(turn.assistant_message) > 100 else turn.assistant_message
                user_msg = user_msg.replace("\n", " ")
                asst_msg = asst_msg.replace("\n", " ")
                lines.append(f"\n  Turn {i} [{turn.id[:8]}...]:")
                lines.append(f"    {self.user_name}: {user_msg}")
                lines.append(f"    {self.assistant_name}: {asst_msg}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving history: {e}"

    def cmd_memory(self) -> str:
        """Show memory statistics."""
        turn_count = self.state.turn_count if self.state else 0
        var_count = len(self.state.scoped_vars) if self.state else 0
        return f"""
Memory Statistics:
  Session ID: {self.session_id}
  Turns in session: {turn_count}
  Turn IDs tracked: {len(self.turn_ids)}
  Scoped variables: {var_count}
"""

    def cmd_context(self) -> str:
        """Show detailed context assembly in configured format (FULL content)."""
        if not self.last_payload:
            return "No context assembled yet. Send a message first or use /prime."

        lines = ["=" * 60, f"CONTEXT PAYLOAD (format: {self.context_format})", "=" * 60]

        # Summary counts
        lines.append(f"\nSummary:")
        lines.append(f"  History turns: {len(self.last_payload.history)}")
        lines.append(f"  Vector passages: {len(self.last_payload.passages)}")
        lines.append(f"  Graph entities: {len(self.last_payload.entities)}")
        lines.append(f"  Graph facts: {len(self.last_payload.facts)}")
        lines.append(f"  Relationship summaries: {len(self.last_payload.recent_memories)}")
        lines.append(f"  Insights: {len(self.last_payload.insights)}")
        lines.append(f"  Summaries: {len(self.last_payload.summaries)}")

        # Show formatted supporting context using PromptArchitect
        lines.append(f"\n--- Supporting Context (format: {self.context_format}) ---")
        formatted_context = self.architect._build_supporting_context(
            self.last_payload,
            self.state,
            self.context_format,
        )
        if formatted_context:
            lines.append(formatted_context)
        else:
            lines.append("  (no supporting context)")

        # History details - FULL content (shown separately since not in supporting context)
        if self.last_payload.history:
            lines.append(f"\n--- History Turns ({len(self.last_payload.history)}) ---")
            for i, turn in enumerate(self.last_payload.history, 1):
                lines.append(f"\n  Turn {i} [{turn.id[:8]}...]:")
                lines.append(f"    {self.user_name}: {turn.user_message}")
                lines.append(f"    {self.assistant_name}: {turn.assistant_message}")

        # Vector passages (shown separately for reference)
        if self.last_payload.passages:
            lines.append(f"\n--- Vector Passages ({len(self.last_payload.passages)}) ---")
            for i, passage in enumerate(self.last_payload.passages, 1):
                text = passage.get("text", "")
                similarity = passage.get("similarity", 0.0)
                lines.append(f"\n  Passage {i} (similarity: {similarity:.3f}):")
                lines.append(f"    {text}")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)

    def cmd_prompt(self) -> str:
        """Show the FULL formatted prompt sent to LLM (no truncation for debugging)."""
        if not self.last_messages:
            return "No prompt formatted yet. Send a message first."

        lines = ["=" * 60, f"FORMATTED PROMPT (format: {self.context_format})", "=" * 60]

        # Map API roles to configured names
        role_names = {
            "user": self.user_name,
            "assistant": self.assistant_name,
            "system": "SYSTEM",
        }

        for i, msg in enumerate(self.last_messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Map role to display name
            display_name = role_names.get(role, role.upper())

            # Mark the last user message as the current query + supporting context
            is_current_query = (i == len(self.last_messages) - 1 and role == "user")
            label = f"{display_name} (supporting context + query)" if is_current_query else display_name
            lines.append(f"\n--- Message {i + 1}: {label} ---")

            # Show FULL content (no truncation for debugging)
            lines.append(content)

        lines.append("\n" + "=" * 60)
        lines.append(f"Total messages: {len(self.last_messages)}")
        return "\n".join(lines)

    def cmd_debug(self) -> str:
        """Show detailed debug info."""
        if not self.last_payload:
            return "No debug info available. Send a message first."

        debug_info = self.last_payload.debug_info
        lines = ["Debug Information:"]
        for key, value in debug_info.items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines) if len(lines) > 1 else "No debug info recorded."

    async def cmd_entities(self) -> str:
        """List graph entities and their relationships."""
        try:
            # Get all nodes and edges from graph store
            nodes = await self.controller.graph.get_all_nodes()
            edges = await self.controller.graph.get_all_edges()

            if not nodes and not edges:
                return "No entities in graph store."

            lines = ["=" * 60, "GRAPH STORE (entities & relationships)", "=" * 60]

            # Build a lookup for node labels by ID
            node_lookup = {node.id: node for node in nodes}

            # Show nodes grouped by type
            if nodes:
                lines.append(f"\nEntities ({len(nodes)} total):")
                # Group by type
                by_type: dict[str, list] = {}
                for node in nodes:
                    by_type.setdefault(node.type, []).append(node)

                for node_type, type_nodes in sorted(by_type.items()):
                    lines.append(f"\n  [{node_type}]")
                    for node in type_nodes[:500]:  # Show up to 500 per type for debugging
                        lines.append(f"    - {node.label} (hits: {node.hit_count})")
                    if len(type_nodes) > 500:
                        lines.append(f"    ... and {len(type_nodes) - 500} more")

            # Show relationships
            if edges:
                lines.append(f"\nRelationships ({len(edges)} total):")
                for edge in edges[:500]:  # Show up to 500 for debugging
                    source = node_lookup.get(edge.source_id)
                    target = node_lookup.get(edge.target_id)
                    source_label = source.label if source else edge.source_id[:8]
                    target_label = target.label if target else edge.target_id[:8]
                    lines.append(f"    {source_label} --[{edge.relation}]--> {target_label}")
                if len(edges) > 500:
                    lines.append(f"    ... and {len(edges) - 500} more")

            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving entities: {e}"

    async def cmd_facts(self) -> str:
        """List all facts/insights from the vector store."""
        try:
            # Get all documents from vector store (no practical limit for debugging)
            documents = await self.controller.vector.get_all(limit=10000)
            if not documents:
                return "No facts/insights in vector store."

            lines = ["=" * 60, "FACTS & INSIGHTS (from vector store)", "=" * 60]
            lines.append(f"\nTotal documents: {len(documents)}\n")

            for i, doc in enumerate(documents, 1):
                text = doc.get("text", "")
                metadata = doc.get("metadata", {})

                # Truncate long text
                display_text = text[:200] + "..." if len(text) > 200 else text
                display_text = display_text.replace("\n", " ")

                lines.append(f"{i}. {display_text}")

                # Show metadata if present
                if metadata:
                    source_type = metadata.get("source_type", "unknown")
                    confidence = metadata.get("confidence", "N/A")
                    lines.append(f"   [source: {source_type}, confidence: {confidence}]")
                lines.append("")

            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving facts: {e}"

    async def cmd_insights(self) -> str:
        """List only insights (type='insight') from the vector store."""
        try:
            # Query with type filter
            documents = await self.controller.vector.get_all(
                limit=10000,
                where={"type": "insight"},
            )
            if not documents:
                return "No insights in vector store."

            lines = ["=" * 60, "INSIGHTS (type='insight' from vector store)", "=" * 60]
            lines.append(f"\nTotal insights: {len(documents)}\n")

            for i, doc in enumerate(documents, 1):
                text = doc.get("text", "")
                metadata = doc.get("metadata", {})

                # Truncate long text
                display_text = text[:200] + "..." if len(text) > 200 else text
                display_text = display_text.replace("\n", " ")

                lines.append(f"{i}. {display_text}")

                # Show structured metadata
                meta_parts = []
                if metadata.get("topic"):
                    meta_parts.append(f"topic: {metadata['topic']}")
                if metadata.get("sentiment"):
                    meta_parts.append(f"sentiment: {metadata['sentiment']}")
                if metadata.get("confidence") is not None:
                    meta_parts.append(f"confidence: {metadata['confidence']}")
                if metadata.get("entities_mentioned"):
                    meta_parts.append(f"entities: {metadata['entities_mentioned']}")

                if meta_parts:
                    lines.append(f"   [{', '.join(meta_parts)}]")
                lines.append("")

            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving insights: {e}"

    async def cmd_summaries(self) -> str:
        """List only turn summaries (type='summary') from the vector store."""
        try:
            # Query with type filter
            documents = await self.controller.vector.get_all(
                limit=10000,
                where={"type": "summary"},
            )
            if not documents:
                return "No turn summaries in vector store."

            lines = ["=" * 60, "TURN SUMMARIES (type='summary' from vector store)", "=" * 60]
            lines.append(f"\nTotal summaries: {len(documents)}\n")

            for i, doc in enumerate(documents, 1):
                text = doc.get("text", "")
                metadata = doc.get("metadata", {})

                # Show full summary text (these are paragraph-length)
                display_text = text[:400] + "..." if len(text) > 400 else text
                display_text = display_text.replace("\n", " ")

                lines.append(f"{i}. {display_text}")

                # Show metadata
                turn_id = metadata.get("turn_id", "")
                created_at = metadata.get("created_at", "")
                if turn_id or created_at:
                    meta_parts = []
                    if turn_id:
                        meta_parts.append(f"turn: {turn_id[:8]}...")
                    if created_at:
                        meta_parts.append(f"created: {created_at[:19]}")
                    lines.append(f"   [{', '.join(meta_parts)}]")
                lines.append("")

            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving summaries: {e}"

    async def cmd_meta_insights(self) -> str:
        """List only meta insights (type='meta_insight') from the vector store."""
        try:
            # Query with type filter for meta_insight
            documents = await self.controller.vector.get_all(
                limit=10000,
                where={"type": "meta_insight"},
            )
            if not documents:
                return "No meta insights in vector store. Run /reorganize with synthesis to generate them."

            lines = ["=" * 60, "META INSIGHTS (type='meta_insight' from vector store)", "=" * 60]
            lines.append(f"\nTotal meta insights: {len(documents)}\n")

            for i, doc in enumerate(documents, 1):
                text = doc.get("text", "")
                metadata = doc.get("metadata", {})

                # Show full meta insight text
                display_text = text[:500] + "..." if len(text) > 500 else text
                display_text = display_text.replace("\n", " ")

                lines.append(f"{i}. {display_text}")

                # Show structured metadata
                meta_parts = []
                if metadata.get("confidence") is not None:
                    meta_parts.append(f"confidence: {metadata['confidence']}")
                if metadata.get("source_type"):
                    meta_parts.append(f"source: {metadata['source_type']}")
                if metadata.get("source_memories"):
                    source_count = len(metadata["source_memories"])
                    meta_parts.append(f"sources: {source_count} memories")
                if metadata.get("created_at"):
                    meta_parts.append(f"created: {metadata['created_at'][:19]}")

                if meta_parts:
                    lines.append(f"   [{', '.join(meta_parts)}]")
                lines.append("")

            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving meta insights: {e}"

    async def cmd_prime(self) -> str:
        """
        Show current context (works before first turn).

        Triggers a recall() to fetch insights/summaries/entities and populates
        last_payload so /context works before the first conversation turn.
        """
        try:
            # Fetch context via recall (empty query just to get supporting context)
            payload = await self.controller.recall(
                query="",
                session_id=self.session_id,
                include_history=True,
            )

            # Store for /context command
            self.last_payload = payload

            lines = ["=" * 60, "PRIMED CONTEXT", "=" * 60]

            # Summary counts
            lines.append(f"\nContext loaded:")
            lines.append(f"  Entities: {len(payload.entities)}")
            lines.append(f"  Insights: {len(payload.insights)}")
            lines.append(f"  Summaries: {len(payload.summaries)}")
            lines.append(f"  Relationships: {len(payload.recent_memories)}")
            lines.append(f"  History turns: {len(payload.history)}")

            # Show top entities
            if payload.entities:
                lines.append("\n--- Top Entities (by hit_count) ---")
                for entity in payload.entities[:15]:
                    hit_count = getattr(entity, 'hit_count', 0)
                    lines.append(f"  - {entity.label} ({entity.type}, hits: {hit_count})")

            # Show relationship summaries
            if payload.recent_memories:
                lines.append("\n--- Relationship Summaries ---")
                for summary in payload.recent_memories[:10]:
                    lines.append(f"  {summary}")

            # Show recent insights
            if payload.insights:
                lines.append("\n--- Recent Insights (most recent first) ---")
                for i, insight in enumerate(payload.insights[:5], 1):
                    text = insight.get("text", "")[:150]
                    created = insight.get("metadata", {}).get("created_at", "")[:19]
                    lines.append(f"  {i}. [{created}] {text}...")

            # Show recent summaries
            if payload.summaries:
                lines.append("\n--- Recent Summaries (most recent first) ---")
                for i, summary in enumerate(payload.summaries[:5], 1):
                    text = summary.get("text", "")[:200]
                    created = summary.get("metadata", {}).get("created_at", "")[:19]
                    lines.append(f"  {i}. [{created}] {text}...")

            lines.append("\n" + "=" * 60)
            lines.append("Use /context for full details, /prompt to see formatted prompt.")
            return "\n".join(lines)

        except Exception as e:
            return f"Error fetching primed context: {e}"

    async def cmd_sessions(self) -> str:
        """List all stored transcript sessions."""
        if not self.transcript_store:
            return "Transcript storage not configured."

        try:
            sessions = await self.transcript_store.list_sessions(limit=1000)
            if not sessions:
                return "No transcript sessions found."

            lines = ["=" * 60, f"TRANSCRIPT SESSIONS ({len(sessions)} total)", "=" * 60]

            for session in sessions:
                # Mark current session
                current = " [CURRENT]" if session.session_id == self.session_id else ""
                lines.append(f"\n  {session.session_id}{current}")
                lines.append(f"    Started: {session.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
                if session.ended_at:
                    lines.append(f"    Ended: {session.ended_at.strftime('%Y-%m-%d %H:%M:%S')}")
                lines.append(f"    User: {session.user_id}")
                lines.append(f"    Model: {session.model_name}")
                lines.append(f"    Turns: {session.total_turns}, Tokens: {session.total_tokens}")

            lines.append("\n" + "=" * 60)
            lines.append("Use /transcript <session_id> to view a specific session.")
            return "\n".join(lines)
        except Exception as e:
            return f"Error listing sessions: {e}"

    async def cmd_transcript(self, arg: str | None = None) -> str:
        """
        Show transcript from persistent storage.

        Args:
            arg: Optional argument - either a session_id or "export"
        """
        if not self.transcript_store:
            return "Transcript storage not configured."

        # Handle /transcript export
        if arg and arg.lower() == "export":
            return await self._export_all_sessions_csv()

        # Determine which session to show
        target_session_id = arg if arg else self.session_id

        try:
            entries = await self.transcript_store.get_entries(
                target_session_id, limit=10000
            )
            if not entries:
                if arg:
                    return f"No transcript entries found for session: {target_session_id}"
                return "No transcript entries for this session."

            is_current = target_session_id == self.session_id
            current_marker = " [CURRENT]" if is_current else ""
            lines = ["=" * 60, f"TRANSCRIPT ({len(entries)} entries){current_marker}", "=" * 60]

            # Get session info
            session = await self.transcript_store.get_session(target_session_id)
            if session:
                lines.append(f"\nSession: {session.session_id}")
                lines.append(f"Started: {session.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
                lines.append(f"Model: {session.model_name}")
                lines.append(f"Total tokens: {session.total_tokens}")
                lines.append(f"Total latency: {session.total_latency_ms:.0f}ms")

            for entry in entries:
                lines.append(f"\n--- Turn {entry.turn_number} [{entry.id[:8]}...] ---")
                lines.append(f"Timestamp: {entry.timestamp.strftime('%H:%M:%S')}")

                if entry.user_message:
                    lines.append(f"\n{self.user_name}:")
                    lines.append(entry.user_message)

                if entry.assistant_message:
                    lines.append(f"\n{self.assistant_name}:")
                    # Truncate long responses for display
                    msg = entry.assistant_message
                    if len(msg) > 500:
                        msg = msg[:500] + f"\n... [{len(msg) - 500} more characters]"
                    lines.append(msg)

                # Show metrics if available
                metrics = []
                if entry.total_tokens:
                    metrics.append(f"tokens: {entry.total_tokens}")
                if entry.latency_ms:
                    metrics.append(f"latency: {entry.latency_ms:.0f}ms")
                if metrics:
                    lines.append(f"\n[{', '.join(metrics)}]")

            lines.append("\n" + "=" * 60)
            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving transcript: {e}"

    async def _export_all_sessions_csv(self) -> str:
        """Export entire transcript database to CSV files."""
        if not self.transcript_store:
            return "Transcript storage not configured."

        # Determine export directory
        if self.transcript_export_dir:
            export_dir = Path(self.transcript_export_dir)
        else:
            export_dir = Path("./exports")

        try:
            # Create timestamped subdirectory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = export_dir / f"transcript_export_{timestamp}"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Use CSVExporter from friday-transcript
            exporter = CSVExporter(self.transcript_store)
            counts = await exporter.export_all_sessions(output_dir)

            lines = [
                "=" * 60,
                "TRANSCRIPT EXPORT COMPLETE",
                "=" * 60,
                f"\nExport directory: {output_dir}",
                f"\nFiles created:",
                f"  - sessions.csv ({counts['sessions']} sessions)",
                f"  - entries.csv ({counts['entries']} entries)",
                "\n" + "=" * 60,
            ]
            return "\n".join(lines)

        except Exception as e:
            return f"Error exporting transcripts: {e}"

    async def cmd_export(self, format_type: str = "markdown") -> str:
        """Export transcript to file."""
        if not self.transcript_store:
            return "Transcript storage not configured."

        try:
            # Determine output path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"transcript_{self.session_id}_{timestamp}"

            if format_type == "jsonl":
                output_path = Path(f"./{base_name}.jsonl")
                exporter = JSONLExporter(self.transcript_store)
                count = await exporter.export_session(self.session_id, output_path)
                return f"Exported {count} entries to: {output_path}"

            elif format_type == "training":
                output_path = Path(f"./{base_name}_training.jsonl")
                exporter = JSONLExporter(self.transcript_store)
                count = await exporter.export_training_data(
                    self.session_id, output_path, format_style="chat"
                )
                return f"Exported {count} training examples to: {output_path}"

            elif format_type == "markdown" or format_type == "md":
                output_path = Path(f"./{base_name}.md")
                exporter = MarkdownExporter(
                    self.transcript_store,
                    user_name=self.user_name,
                    assistant_name=self.assistant_name,
                )
                count = await exporter.export_session(self.session_id, output_path)
                return f"Exported {count} entries to: {output_path}"

            else:
                return f"Unknown format: {format_type}. Use: jsonl, markdown, or training"

        except Exception as e:
            return f"Error exporting transcript: {e}"

    async def cmd_reset(self) -> str:
        """Clear all memory stores (graph and vector)."""
        try:
            lines = ["Resetting memory stores..."]

            # Clear graph store
            graph_result = await self.controller.graph.clear()
            lines.append(f"  Graph store: cleared {graph_result['nodes_deleted']} nodes, {graph_result['edges_deleted']} edges")

            # Clear vector store
            vector_count = await self.controller.vector.clear()
            lines.append(f"  Vector store: cleared {vector_count} documents")

            # Clear episodic store for this session
            await self.controller.episodic.clear_session(self.session_id)
            lines.append(f"  Episodic store: cleared session {self.session_id}")

            # Reset turn tracking
            self.turn_ids.clear()
            if self.state:
                self.state.turn_count = 0

            lines.append("\nMemory reset complete.")
            return "\n".join(lines)
        except Exception as e:
            return f"Error resetting memory: {e}"

    async def cmd_reorganize(self, opts: str = "") -> str:
        """
        Run memory reorganization.

        Options (space-separated):
          --execute       Run for real (default is dry-run)
          --no-backup     Skip backup before modifications
          --skip-synthesis Skip LLM-based memory synthesis
          --skip-verify   Skip LLM-based fact verification
          --analyze       Just run analysis (no prune/synthesis/verify)
          --prune         Just run pruning
          --synthesize    Just run synthesis (meta-insights, relationships)
          --verify        Just run fact verification
          --backup        Just create a backup

        Examples:
          /reorganize                    - Dry run with all steps
          /reorganize --execute          - Execute all steps with backup
          /reorganize --analyze          - Just analyze (read-only)
          /reorganize --execute --prune  - Execute pruning only
          /reorganize --execute --synthesize - Execute synthesis only
        """
        if not self.persist_dir:
            return "Error: persist_dir not configured for this session."

        # Parse options
        opt_list = opts.lower().split() if opts else []

        # Determine mode
        dry_run = "--execute" not in opt_list
        backup_first = "--no-backup" not in opt_list
        skip_synthesis = "--skip-synthesis" in opt_list
        skip_verify = "--skip-verify" in opt_list
        analyze_only = "--analyze" in opt_list
        prune_only = "--prune" in opt_list
        synthesize_only = "--synthesize" in opt_list
        verify_only = "--verify" in opt_list
        backup_only = "--backup" in opt_list

        # Use maintenance config from config.yaml or defaults
        config = self.maintenance_config or MaintenanceConfig()

        # Get LLMs for maintenance operations (fall back to main chat LLM)
        synthesizer_llm = self.maintenance_llms.get("synthesizer", self.llm)
        classifier_llm = self.maintenance_llms.get("classifier", self.llm)
        researcher_llm = self.maintenance_llms.get("researcher", self.llm)
        judge_llm = self.maintenance_llms.get("judge", self.llm)

        # Create embedding function for maintenance operations
        # Use config.embedding if available, otherwise fall back to session embedding
        maintenance_embedding = self.embedding_function
        if config.embedding and not skip_synthesis:
            try:
                from friday_llm import LiteLLMEmbeddingService, ResilienceConfig
                maintenance_embedding = LiteLLMEmbeddingService(
                    model_name=config.embedding.model,
                    api_key=config.embedding.api_key,
                    api_base=config.embedding.api_base,
                    resilience=ResilienceConfig(
                        timeout_seconds=config.embedding.timeout_seconds,
                    ),
                )
            except Exception as e:
                lines = [f"Warning: Failed to create maintenance embedding service: {e}"]
                lines.append("Falling back to session embedding function.")
                print("\n".join(lines))

        # Create reorganizer with the persist_dir, config, LLMs, embedding, and collection name
        reorganizer = MemoryReorganizer(
            memory_dir=self.persist_dir,
            config=config,
            llm_service=synthesizer_llm if not skip_synthesis else None,
            classifier_llm=classifier_llm if not skip_verify else None,
            researcher_llm=researcher_llm if not skip_verify else None,
            judge_llm=judge_llm if not skip_verify else None,
            embedding_function=maintenance_embedding,
            collection_name=config.collection_name,
        )

        try:
            lines = ["=" * 60, "MEMORY REORGANIZATION", "=" * 60]

            if backup_only:
                # Just create a backup
                lines.append("\nCreating backup...")
                manifest = await reorganizer.backup()
                lines.append(f"  Backup ID: {manifest.backup_id[:8]}...")
                lines.append(f"  Location: {manifest.backup_dir}")
                lines.append(f"  Files backed up: {len(manifest.files)}")
                lines.append("\nBackup complete.")
                return "\n".join(lines)

            if analyze_only:
                # Just analyze
                lines.append("\nAnalyzing memory consistency...")
                report = await reorganizer.analyze()
                lines.append(f"\nGraph Store:")
                lines.append(f"  Nodes: {report.graph_stats.get('node_count', 0)}")
                lines.append(f"  Edges: {report.graph_stats.get('edge_count', 0)}")
                lines.append(f"\nVector Store:")
                lines.append(f"  Documents: {report.vector_stats.get('document_count', 0)}")
                lines.append(f"\nEpisodic Store:")
                lines.append(f"  Turns: {report.episodic_stats.get('turn_count', 0)}")
                lines.append(f"\nIssues Found: {len(report.issues)}")
                lines.append(f"  Critical: {report.severity_counts['critical']}")
                lines.append(f"  Warning: {report.severity_counts['warning']}")
                lines.append(f"  Info: {report.severity_counts['info']}")

                if report.duplicate_groups:
                    lines.append(f"\nDuplicate Entity Groups: {len(report.duplicate_groups)}")
                    for group in report.duplicate_groups[:5]:
                        all_ids = [group.primary_id] + group.duplicate_ids[:2]
                        lines.append(f"  - {group.match_type}: {', '.join(all_ids)}")
                    if len(report.duplicate_groups) > 5:
                        lines.append(f"  ... and {len(report.duplicate_groups) - 5} more groups")

                lines.append("\nAnalysis complete.")
                return "\n".join(lines)

            if prune_only:
                # Just prune
                mode = "DRY RUN" if dry_run else "EXECUTING"
                lines.append(f"\nPruning redundancies ({mode})...")
                if backup_first and not dry_run:
                    lines.append("Creating backup first...")

                report = await reorganizer.prune(dry_run=dry_run, backup_first=backup_first)
                lines.append(f"\nPrune Results:")
                lines.append(f"  Entities merged: {report.entities_merged}")
                lines.append(f"  Entities removed: {report.entities_removed}")
                lines.append(f"  Insights removed: {report.insights_removed}")
                lines.append(f"  Edges removed: {report.edges_removed}")

                if dry_run:
                    lines.append("\n[DRY RUN - No changes made. Use --execute to apply.]")
                else:
                    lines.append("\nPruning complete.")
                return "\n".join(lines)

            if synthesize_only:
                # Just synthesize
                mode = "DRY RUN" if dry_run else "EXECUTING"
                lines.append(f"\nSynthesizing memories ({mode})...")
                if backup_first and not dry_run:
                    lines.append("Creating backup first...")
                    await reorganizer.backup()

                report = await reorganizer.synthesize(dry_run=dry_run)
                lines.append(f"\nSynthesis Results:")
                lines.append(f"  Topic clusters found: {len(report.topic_clusters)}")
                lines.append(f"  Meta-insights created: {report.meta_insights_created}")
                lines.append(f"  Relationships inferred: {report.relationships_inferred}")
                lines.append(f"  Knowledge gaps identified: {len(report.knowledge_gaps)}")

                if report.synthesized_memories:
                    lines.append(f"\nSynthesized Memories:")
                    for mem in report.synthesized_memories[:5]:
                        content_preview = mem.content[:80] + "..." if len(mem.content) > 80 else mem.content
                        lines.append(f"  - [{mem.type}] {content_preview}")
                    if len(report.synthesized_memories) > 5:
                        lines.append(f"  ... and {len(report.synthesized_memories) - 5} more")

                if dry_run:
                    lines.append("\n[DRY RUN - No changes made. Use --execute to apply.]")
                else:
                    lines.append("\nSynthesis complete.")
                return "\n".join(lines)

            if verify_only:
                # Just verify facts
                mode = "DRY RUN" if dry_run else "EXECUTING"
                lines.append(f"\nVerifying facts ({mode})...")

                report = await reorganizer.verify(dry_run=dry_run)
                lines.append(f"\nVerification Results:")
                lines.append(f"  Facts classified: {report.facts_classified}")
                lines.append(f"  Claims verified: {report.claims_verified}")
                lines.append(f"  Claims disputed: {report.claims_disputed}")
                lines.append(f"  Claims unverifiable: {report.claims_unverifiable}")

                if dry_run:
                    lines.append("\n[DRY RUN - No changes made. Use --execute to apply.]")
                else:
                    lines.append("\nVerification complete.")
                return "\n".join(lines)

            # Full reorganization
            mode = "DRY RUN" if dry_run else "EXECUTING"
            lines.append(f"\nRunning full reorganization ({mode})...")
            lines.append(f"  Backup first: {backup_first}")
            lines.append(f"  Skip synthesis: {skip_synthesis}")
            lines.append(f"  Skip verify: {skip_verify}")
            lines.append("")

            report = await reorganizer.reorganize(
                backup_first=backup_first,
                dry_run=dry_run,
                skip_synthesis=skip_synthesis,
                skip_verify=skip_verify,
            )

            # Show summary
            summary = reorganizer.generate_report_summary(report)
            lines.append(summary)

            if dry_run:
                lines.append("\n[DRY RUN - No changes made. Use --execute to apply.]")

            return "\n".join(lines)

        except Exception as e:
            logger.exception("Reorganization failed")
            return f"Error during reorganization: {e}"

    def cmd_vars(self) -> str:
        """Show scoped variables."""
        if not self.state or not self.state.scoped_vars:
            return "No scoped variables set."
        lines = ["Scoped Variables:"]
        for key, value in self.state.scoped_vars.items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)

    def cmd_set(self, key: str, value: str) -> str:
        """Set a scoped variable."""
        if not self.state:
            return "Session not initialized."
        self.state.set_var(key, value)
        return f"Set {key} = {value}"

    def cmd_help(self) -> str:
        """Show available commands."""
        return """
Available Commands:
  /exit, /quit     - Exit the chat
  /clear           - Clear conversation history
  /history         - Show conversation history
  /memory          - Show memory statistics
  /context         - Show assembled context payload (FULL, no truncation)
  /prompt          - Show full formatted prompt sent to LLM (FULL, no truncation)
  /prime           - Load and show primed context (works before first turn)
  /debug           - Show debug info from context assembly
  /entities        - List graph entities and relationships
  /facts           - List all documents from vector store (insights + summaries)
  /insights        - List only insights (type='insight') with structured metadata
  /summaries       - List only turn summaries (type='summary')
  /meta            - List only meta insights (type='meta_insight') from synthesis
  /sessions        - List all stored transcript sessions
  /transcript      - Show current session's transcript
  /transcript <id> - Show transcript for a specific session
  /transcript export - Export entire database to CSV
  /export [format] - Export current session (jsonl, markdown, or training)
  /reset           - Clear all memory stores (graph, vector, episodic)
  /reorganize [opts] - Run memory reorganization
  /vars            - Show scoped variables
  /set <key> <val> - Set a scoped variable (e.g., /set user:name Alice)
  /help            - Show this help

Reorganize Options:
  /reorganize              - Dry run full reorganization
  /reorganize --execute    - Execute full reorganization with backup
  /reorganize --analyze    - Just analyze (read-only)
  /reorganize --prune      - Just prune (dry run)
  /reorganize --backup     - Just create a backup
  /reorganize --execute --prune --no-backup  - Execute prune without backup
  /reorganize --skip-synthesis --skip-verify - Skip LLM-dependent steps
"""

    async def _background_extract(self, turn: InteractionTurn) -> None:
        """Run extraction in background without blocking the user."""
        try:
            result = await self.extractor.extract(turn)
            if result.get("error"):
                logger.warning(f"Background extraction error: {result['error']}")
            else:
                extracted = result.get("extracted", {})
                entity_count = len(extracted.get("entities", []))
                fact_count = len(extracted.get("facts", []))
                rel_count = len(extracted.get("relationships", []))
                logger.info(
                    f"Background extraction complete: "
                    f"{entity_count} entities, {fact_count} facts, {rel_count} relationships"
                )
        except Exception as e:
            logger.warning(f"Background extraction failed: {e}")

    async def process_turn(self, user_input: str) -> str | None:
        """Process a user turn and return the response."""
        if not self.state:
            await self.initialize()

        # Calculate dynamic budget limit
        dynamic_limit = self.architect.calculate_dynamic_limit(self.system_prompt)

        # 1. Assemble context (retrieves from all stores)
        self.last_payload = await self.assembler.assemble_context(
            query=user_input,
            state=self.state,
            budget_limit=dynamic_limit,
        )

        # 2. Format prompt with assembled context AND current user input
        messages = await self.assembler.format_prompt(
            system_prompt=self.system_prompt,
            payload=self.last_payload,
            context_format=self.context_format,
            user_query=user_input,  # Pass current input directly
        )

        # Store for debugging
        self.last_messages = messages

        # Print assistant name and start streaming
        print(f"\n{self.assistant_name}:")

        full_response = ""
        try:
            # 3. Call LLM with context-enriched prompt (streaming)
            async for chunk in self.llm.chat_completion_stream(
                messages=messages,
                temperature=self.temperature,
            ):
                print(chunk, end="", flush=True)
                full_response += chunk

            # Print end newline
            print("\n")

            # 4. Create and save interaction turn
            turn = InteractionTurn(
                id=str(uuid.uuid4()),
                session_id=self.session_id,
                timestamp=datetime.now(),
                user_message=user_input,
                assistant_message=full_response,
            )
            await self.controller.add_turn(self.session_id, turn)
            self.turn_ids.append(turn.id)

            # 5. Extract entities and facts from the turn (background)
            # Run extraction asynchronously so user can continue chatting
            if self.extractor:
                asyncio.create_task(self._background_extract(turn))
                print("  [Extraction started in background]")

            # Update state turn count
            if self.state:
                self.state.turn_count += 1

            return full_response

        except LLMTimeoutError as e:
            print(f"\n\nRequest timed out after {e.timeout_seconds}s")
            print("The LLM is taking too long. Try a shorter message or check the server.")
            return None

        except LLMRetryExhaustedError as e:
            print(f"\n\nFailed after {e.attempts} attempts")
            print(f"Last error: {type(e.last_error).__name__}: {e.last_error}")
            print("\nThe LLM service is unavailable. Check if the server is running.")
            return None

        except CircuitBreakerOpenError as e:
            print(f"\n\nService temporarily unavailable")
            print(f"Circuit breaker is open. Retry in {e.retry_after:.0f} seconds.")
            return None


async def main() -> None:
    """Main chat loop."""
    # Determine config path
    if len(sys.argv) > 2 and sys.argv[1] == "--config":
        config_path = Path(sys.argv[2])
    else:
        config_path = Path(__file__).parent / "config.yaml"

    # Load configuration
    config = load_config(config_path)
    llm_config = config.get("llm", {})
    extraction_config = config.get("extraction", {})
    embedding_config = config.get("embedding", {})
    memory_config = config.get("memory", {})
    chat_config = config.get("chat", {})
    logging_config = config.get("logging", {})
    transcript_config = config.get("transcript", {})
    maintenance_yaml = config.get("maintenance", {})

    # Build MaintenanceConfig from YAML
    pruning_yaml = maintenance_yaml.get("pruning", {})
    synthesis_yaml = maintenance_yaml.get("synthesis", {})
    fact_check_yaml = maintenance_yaml.get("fact_checking", {})
    prompts_yaml = maintenance_yaml.get("prompts", {})
    logging_yaml = maintenance_yaml.get("logging", {})
    maintenance_embedding_yaml = maintenance_yaml.get("embedding", {})

    # Build PromptsConfig - only override prompts that are explicitly set in config
    prompts_kwargs = {}
    if prompts_yaml.get("classification"):
        prompts_kwargs["classification"] = prompts_yaml["classification"]
    if prompts_yaml.get("research"):
        prompts_kwargs["research"] = prompts_yaml["research"]
    if prompts_yaml.get("judge"):
        prompts_kwargs["judge"] = prompts_yaml["judge"]
    if prompts_yaml.get("meta_insight"):
        prompts_kwargs["meta_insight"] = prompts_yaml["meta_insight"]
    if prompts_yaml.get("knowledge_gap"):
        prompts_kwargs["knowledge_gap"] = prompts_yaml["knowledge_gap"]
    if prompts_yaml.get("relationship_inference"):
        prompts_kwargs["relationship_inference"] = prompts_yaml["relationship_inference"]

    # Build LogConfig - parse verbosity and format strings to enums
    log_verbosity_str = logging_yaml.get("verbosity", "normal").lower()
    log_format_str = logging_yaml.get("format", "markdown").lower()
    try:
        log_verbosity = LogVerbosity(log_verbosity_str)
    except ValueError:
        log_verbosity = LogVerbosity.NORMAL
    try:
        log_format = LogFormat(log_format_str)
    except ValueError:
        log_format = LogFormat.MARKDOWN

    # Build EmbeddingConfig for maintenance operations
    # Priority: maintenance.embedding > main embedding config > None
    maintenance_embedding_config = None
    if maintenance_embedding_yaml:
        # Use maintenance-specific embedding config
        maintenance_embedding_config = EmbeddingConfig(
            model=maintenance_embedding_yaml.get("model", "openai/nomic-embed-text-v1.5"),
            api_base=maintenance_embedding_yaml.get("api_base"),
            api_key=maintenance_embedding_yaml.get("api_key"),
            timeout_seconds=maintenance_embedding_yaml.get("timeout_seconds", 60.0),
        )
    elif embedding_config:
        # Fall back to main embedding config
        maintenance_embedding_config = EmbeddingConfig(
            model=embedding_config.get("model", "openai/nomic-embed-text-v1.5"),
            api_base=embedding_config.get("api_base"),
            api_key=embedding_config.get("api_key"),
            timeout_seconds=embedding_config.get("timeout_seconds", 60.0),
        )

    # Get collection name - prefer maintenance config, fall back to memory config
    maintenance_collection_name = (
        maintenance_yaml.get("collection_name")
        or memory_config.get("collection_name", "memory_chat_test")
    )

    maintenance_config = MaintenanceConfig(
        pruning=PruneConfig(
            stale_threshold_days=pruning_yaml.get("stale_threshold_days", 90),
            min_hit_count=pruning_yaml.get("min_hit_count", 1),
            similarity_threshold=pruning_yaml.get("similarity_threshold", 0.95),
        ),
        synthesis=SynthesisConfig(
            cluster_min_size=synthesis_yaml.get("cluster_min_size", 3),
            meta_insight_confidence=synthesis_yaml.get("meta_insight_confidence", 0.7),
        ),
        fact_checking=FactCheckConfig(
            batch_size=fact_check_yaml.get("batch_size", 50),
            verification_timeout=fact_check_yaml.get("verification_timeout", 30),
        ),
        prompts=PromptsConfig(**prompts_kwargs) if prompts_kwargs else PromptsConfig(),
        logging=LogConfig(
            enabled=logging_yaml.get("enabled", True),
            log_directory=logging_yaml.get("log_directory", "./reorganization_logs"),
            verbosity=log_verbosity,
            format=log_format,
        ),
        embedding=maintenance_embedding_config,
        collection_name=maintenance_collection_name,
        backup_directory=maintenance_yaml.get("backup_directory"),
    )

    # Load maintenance LLM configurations
    maintenance_llm_yaml = maintenance_yaml.get("llm", {})

    # Configure logging from config
    log_level_str = logging_config.get("level", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logging.basicConfig(level=log_level, format='%(name)s: %(message)s')

    # Optionally enable verbose extraction debugging
    if logging_config.get("extraction_debug", False):
        logging.getLogger('friday_memory.context.extractor').setLevel(logging.DEBUG)

    # Chat participant names
    user_name = chat_config.get("user_name", "You")
    assistant_name = chat_config.get("assistant_name", "Assistant")

    # Token budget settings - use context_window (new) or fall back to max_context_tokens (deprecated)
    context_window = memory_config.get("context_window", memory_config.get("max_context_tokens", 8192))
    output_buffer = memory_config.get("output_buffer", 2000)

    # Priming configuration (entity-driven semantic search with recency)
    priming_config = memory_config.get("priming", {
        "enabled": True,
        "top_entities": 10,
        "insights_per_entity": 3,
        "recency_days": 0,
        "token_budget": 500,
    })

    # Determine if using separate extraction model
    use_separate_extraction = (
        extraction_config.get("model")
        and extraction_config.get("model") != llm_config.get("model")
    )

    # Display configuration
    print_banner()
    print(f"Chat: {user_name} ↔ {assistant_name}")
    print(f"Chat LLM: {llm_config.get('model', 'unknown')}")
    if use_separate_extraction:
        print(f"Extraction LLM: {extraction_config.get('model')} (separate)")
    else:
        print(f"Extraction LLM: {llm_config.get('model', 'unknown')} (shared)")
    if extraction_config.get("prompt"):
        print("Extraction prompt: custom (from config)")
    else:
        print("Extraction prompt: default")
    print(f"Embedding Model: {embedding_config.get('model', 'unknown')}")
    print(f"API Base: {llm_config.get('api_base', 'default')}")
    print(f"Temperature: {llm_config.get('temperature', 0.7)}")
    print()
    print("Token Budget:")
    print(f"  Context window: {context_window}")
    print(f"  Output buffer: {output_buffer}")
    print(f"  Available for context: ~{context_window - output_buffer - 500} tokens")
    print(f"Max History Turns: {memory_config.get('max_history_turns', 10)}")
    print()
    # Context format applies to all turns
    print(f"Context Format: {memory_config.get('context_format', 'plain')}")
    print()
    if priming_config.get("enabled", True):
        top_ent = priming_config.get("top_entities", 10)
        insights_per = priming_config.get("insights_per_entity", 3)
        recency = priming_config.get("recency_days", 0)
        recency_str = f", last {recency} days" if recency > 0 else ", all time"
        print(f"Context Priming: {top_ent} entities × {insights_per} insights each{recency_str}")
        print(f"  Token budget: {priming_config.get('token_budget', 500)}")
    else:
        print("Context Priming: disabled")
    print()

    # Build resilience config
    resilience = ResilienceConfig(
        max_retries=llm_config.get("max_retries", 3),
        timeout_seconds=llm_config.get("timeout_seconds", 30.0),
    )

    # 1. Initialize Chat LLM service
    try:
        llm = LiteLLMService(
            model_name=llm_config.get("model", "openai/local-model"),
            api_key=llm_config.get("api_key"),
            api_base=llm_config.get("api_base"),
            resilience=resilience,
        )
    except Exception as e:
        print(f"Error initializing Chat LLM: {e}")
        sys.exit(1)

    # 2. Initialize Extraction LLM service (separate or shared)
    if use_separate_extraction:
        try:
            extraction_resilience = ResilienceConfig(
                max_retries=extraction_config.get("max_retries", 2),
                timeout_seconds=extraction_config.get("timeout_seconds", 60.0),
            )
            extraction_llm = LiteLLMService(
                model_name=extraction_config.get("model"),
                api_key=extraction_config.get("api_key"),
                api_base=extraction_config.get("api_base"),
                resilience=extraction_resilience,
            )
        except Exception as e:
            print(f"Error initializing Extraction LLM: {e}")
            print("Falling back to shared LLM for extraction.")
            extraction_llm = llm
    else:
        extraction_llm = llm

    # 2b. Initialize Maintenance LLM services (for /reorganize command)
    maintenance_llms: dict[str, LiteLLMService] = {}

    def create_maintenance_llm(role: str) -> LiteLLMService | None:
        """Create a LiteLLMService for a maintenance role if configured."""
        role_config = maintenance_llm_yaml.get(role, {})
        if not role_config or not role_config.get("model"):
            return None  # Fall back to main LLM
        try:
            role_resilience = ResilienceConfig(
                max_retries=role_config.get("max_retries", 2),
                timeout_seconds=role_config.get("timeout_seconds", 60.0),
            )
            return LiteLLMService(
                model_name=role_config.get("model"),
                api_key=role_config.get("api_key"),
                api_base=role_config.get("api_base"),
                resilience=role_resilience,
            )
        except Exception as e:
            logger.warning(f"Failed to create {role} LLM: {e}, will use main LLM")
            return None

    for role in ["synthesizer", "classifier", "researcher", "judge"]:
        role_llm = create_maintenance_llm(role)
        if role_llm:
            maintenance_llms[role] = role_llm

    if maintenance_llms:
        print(f"Maintenance LLMs: {', '.join(maintenance_llms.keys())}")

    # 3. Initialize Embedding service
    try:
        embedding_resilience = ResilienceConfig(
            timeout_seconds=embedding_config.get("timeout_seconds", 30.0),
        )
        embedding = LiteLLMEmbeddingService(
            model_name=embedding_config.get("model", "openai/nomic-embed-text-v1.5"),
            api_key=embedding_config.get("api_key"),
            api_base=embedding_config.get("api_base"),
            resilience=embedding_resilience,
        )
    except Exception as e:
        print(f"Error initializing LiteLLMEmbeddingService: {e}")
        sys.exit(1)

    # 3. Create memory stores
    # Persistence directory for vector, graph, and transcript stores
    persist_dir = Path(__file__).parent / memory_config.get("persist_directory", "./vector")
    persist_dir.mkdir(parents=True, exist_ok=True)

    # SQLite transcript store for persistent conversation logging
    transcript_path = persist_dir / "transcript.db"
    transcript_store = SQLiteTranscriptStore(transcript_path)

    # TranscriptBackedEpisodicStore wraps transcript for episodic memory
    system_prompt = chat_config.get("system_prompt", "You are a helpful assistant.")
    episodic = TranscriptBackedEpisodicStore(
        transcript_store=transcript_store,
        model_name=llm_config.get("model", "unknown"),
        system_prompt=system_prompt,
    )

    # ElementXGraphStore with disk persistence
    graph_path = persist_dir / "graph.json"
    graph = ElementXGraphStore(storage_path=str(graph_path))

    # ChromaVectorStore with disk persistence

    vector = ChromaVectorStore(
        collection_name=memory_config.get("collection_name", "memory_chat_test"),
        embedding_function=embedding,
        persist_directory=str(persist_dir),
    )

    # 4. Create telemetry recorder
    telemetry = DebugTelemetryRecorder()

    # 5. Create MemoryController with priming config
    controller = MemoryController(
        vector_store=vector,
        graph_store=graph,
        episodic_store=episodic,
        telemetry=telemetry,
        priming_config=priming_config,
    )

    # 6. Create PromptArchitect (token budgeting) with speaker names
    architect = PromptArchitect(
        model_name=llm_config.get("model", "gpt-4"),
        max_tokens=context_window,
        output_buffer=output_buffer,
        user_name=user_name,
        assistant_name=assistant_name,
    )

    # 7. Create ContextAssembler
    assembler = ContextAssembler(
        memory_controller=controller,
        model_name=llm_config.get("model", "gpt-4"),
        max_tokens=context_window,
        telemetry=telemetry,
    )

    # 8. Create MemoryExtractor with extraction LLM, custom prompt, and participant names
    extraction_prompt = extraction_config.get("prompt")  # None uses default
    extractor = MemoryExtractor(
        memory_controller=controller,
        llm=extraction_llm,  # Uses dedicated extraction LLM (or shared if not configured)
        telemetry=telemetry,
        prompt_template=extraction_prompt,
        user_name=user_name,
        assistant_name=assistant_name,
    )
    assembler.set_extractor(extractor)

    # 9. Create session
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    user_id = "test_user"

    # Create transcript session for persistent logging
    transcript_session = TranscriptSession(
        session_id=session_id,
        user_id=user_id,
        model_name=llm_config.get("model", "unknown"),
        system_prompt=system_prompt,
        config_snapshot={
            "temperature": llm_config.get("temperature", 0.7),
            "max_history_turns": memory_config.get("max_history_turns", 10),
        },
    )
    await transcript_store.create_session(transcript_session)

    # Get context format from memory config (applies to all turns, not just priming)
    context_format = memory_config.get("context_format", "plain")

    # Get transcript export directory from config
    transcript_export_dir = transcript_config.get("export_directory")
    if transcript_export_dir:
        transcript_export_dir = Path(transcript_export_dir)

    session = MemoryChatSession(
        llm=llm,
        controller=controller,
        assembler=assembler,
        architect=architect,
        system_prompt=system_prompt,
        session_id=session_id,
        user_id=user_id,
        temperature=llm_config.get("temperature", 0.7),
        max_history_turns=memory_config.get("max_history_turns", 10),
        extractor=extractor,
        user_name=user_name,
        assistant_name=assistant_name,
        transcript_store=transcript_store,
        context_format=context_format,
        persist_dir=persist_dir,
        maintenance_config=maintenance_config,
        maintenance_llms=maintenance_llms,
        transcript_export_dir=transcript_export_dir,
        embedding_function=embedding,
    )

    # Initialize session
    await session.initialize()
    print(f"Session initialized: {session_id}")
    print(f"Persistence directory: {persist_dir}")
    print("  - Vector store: ChromaDB")
    print(f"  - Graph store: {graph_path}")
    print(f"  - Transcript store: {transcript_path}")

    # Trigger priming and populate session.last_payload for /context command
    if priming_config.get("enabled", True):
        await controller._ensure_session_primed(session_id)

        # Fetch primed context into session.last_payload so /context works immediately
        session.last_payload = await controller.recall(
            query="",
            session_id=session_id,
            include_history=True,
        )

        priming_info = controller.get_priming_info(session_id)
        if priming_info["primed"] and priming_info["entity_count"] > 0:
            entity_count = priming_info['entity_count']
            insight_count = priming_info.get('insight_count', 0)
            summary_count = priming_info.get('summary_count', 0)
            rel_count = priming_info['relationship_count']
            print(f"Context primed: {entity_count} entities, {insight_count} insights, {summary_count} summaries, {rel_count} relationships")
            if priming_info["relationship_summaries"]:
                print("  Prior knowledge:")
                for summary in priming_info["relationship_summaries"][:3]:
                    print(f"    {summary}")
                if rel_count > 3:
                    print(f"    ... and {rel_count - 3} more")
        else:
            print("Context priming: no prior data found (new memory)")
    print("Entity extraction: enabled (LLM-based)")
    print()

    # Main loop
    while True:
        try:
            # Get user input
            user_input = input(f"{user_name}: ").strip()

            # Skip empty input
            if not user_input:
                continue

            # Handle commands
            cmd_result = await session.handle_command(user_input)
            if cmd_result is not None:
                if cmd_result == "EXIT":
                    print("\nGoodbye!")
                    break
                print(cmd_result)
                continue

            # Process as chat message
            await session.process_turn(user_input)

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nUnexpected error: {type(e).__name__}: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
