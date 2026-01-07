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
  /context         - Show assembled context payload (detailed)
  /prompt          - Show full formatted prompt sent to LLM
  /debug           - Show debug info from context assembly
  /entities        - List graph entities and relationships
  /facts           - List all documents from vector store (insights + summaries)
  /insights        - List only insights (type='insight') with structured metadata
  /summaries       - List only turn summaries (type='summary')
  /transcript      - Show full transcript from persistent storage
  /export [format] - Export transcript (jsonl, markdown, or training)
  /reset           - Clear all memory stores (graph, vector, episodic)
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
    LiteLLMEmbeddingService,
    LiteLLMService,
    LLMTimeoutError,
    LLMRetryExhaustedError,
    CircuitBreakerOpenError,
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
from friday_transcript import (
    SQLiteTranscriptStore,
    TranscriptSession,
    JSONLExporter,
    MarkdownExporter,
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
            case "transcript":
                return await self.cmd_transcript()
            case "export":
                format_type = parts[1] if len(parts) > 1 else "markdown"
                return await self.cmd_export(format_type)
            case "reset":
                return await self.cmd_reset()
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
        """Show detailed context assembly."""
        if not self.last_payload:
            return "No context assembled yet. Send a message first."

        lines = ["=" * 60, "CONTEXT PAYLOAD DETAILS", "=" * 60]

        # Summary
        lines.append(f"\nSummary:")
        lines.append(f"  History turns: {len(self.last_payload.history)} (completed turns from episodic store)")
        lines.append(f"  Vector passages: {len(self.last_payload.passages)}")
        lines.append(f"  Graph entities: {len(self.last_payload.entities)}")
        lines.append(f"  Graph facts: {len(self.last_payload.facts)}")
        lines.append(f"  Recent memories: {len(self.last_payload.recent_memories)}")
        lines.append(f"\nNote: Current query is not yet a 'turn' until the response is received and saved.")

        # History details
        if self.last_payload.history:
            lines.append(f"\n--- History Turns ({len(self.last_payload.history)}) ---")
            for i, turn in enumerate(self.last_payload.history, 1):
                lines.append(f"\n  Turn {i} [{turn.id[:8]}...]:")
                user_preview = turn.user_message[:100].replace('\n', ' ')
                if len(turn.user_message) > 100:
                    user_preview += "..."
                lines.append(f"    {self.user_name}: {user_preview}")
                asst_preview = turn.assistant_message[:100].replace('\n', ' ')
                if len(turn.assistant_message) > 100:
                    asst_preview += "..."
                lines.append(f"    {self.assistant_name}: {asst_preview}")

        # Vector passages
        if self.last_payload.passages:
            lines.append(f"\n--- Vector Passages ({len(self.last_payload.passages)}) ---")
            for i, passage in enumerate(self.last_payload.passages, 1):
                text = passage.get("text", "")[:150].replace('\n', ' ')
                similarity = passage.get("similarity", 0.0)
                lines.append(f"\n  Passage {i} (similarity: {similarity:.3f}):")
                lines.append(f"    {text}...")

        # Graph entities
        if self.last_payload.entities:
            lines.append(f"\n--- Graph Entities ({len(self.last_payload.entities)}) ---")
            for entity in self.last_payload.entities[:10]:
                props = getattr(entity, 'properties', {})
                prop_str = ", ".join(f"{k}={v}" for k, v in list(props.items())[:2])
                lines.append(f"  - {entity.label} ({entity.type}): {prop_str}")

        # Graph facts
        if self.last_payload.facts:
            lines.append(f"\n--- Graph Facts ({len(self.last_payload.facts)}) ---")
            for fact in self.last_payload.facts[:10]:
                lines.append(f"  - {fact.source_id} --[{fact.relation}]--> {fact.target_id}")

        # Recent memories
        if self.last_payload.recent_memories:
            lines.append(f"\n--- Recent Memories ({len(self.last_payload.recent_memories)}) ---")
            for mem in self.last_payload.recent_memories[:5]:
                lines.append(f"  - {mem[:100]}...")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)

    def cmd_prompt(self) -> str:
        """Show the full formatted prompt sent to LLM."""
        if not self.last_messages:
            return "No prompt formatted yet. Send a message first."

        lines = ["=" * 60, "FORMATTED PROMPT (sent to LLM)", "=" * 60]

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

            # Mark the last user message as the current query
            is_current_query = (i == len(self.last_messages) - 1 and role == "user")
            label = f"{display_name} (current query)" if is_current_query else display_name
            lines.append(f"\n--- Message {i + 1}: {label} ---")

            # For system messages, show full content (contains priming context)
            if role == "system":
                # Show first 2000 chars to ensure priming context is visible
                if len(content) > 2000:
                    lines.append(content[:2000])
                    lines.append(f"\n... [{len(content) - 2000} more characters] ...")
                else:
                    lines.append(content)
            else:
                # For user/assistant, show full content (usually shorter)
                if len(content) > 300:
                    lines.append(content[:300])
                    lines.append(f"... [{len(content) - 300} more characters] ...")
                else:
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

    async def cmd_transcript(self) -> str:
        """Show full transcript from persistent storage."""
        if not self.transcript_store:
            return "Transcript storage not configured."

        try:
            entries = await self.transcript_store.get_entries(
                self.session_id, limit=10000
            )
            if not entries:
                return "No transcript entries for this session."

            lines = ["=" * 60, f"TRANSCRIPT ({len(entries)} entries)", "=" * 60]

            # Get session info
            session = await self.transcript_store.get_session(self.session_id)
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
  /context         - Show assembled context payload (detailed)
  /prompt          - Show full formatted prompt sent to LLM
  /debug           - Show debug info from context assembly
  /entities        - List graph entities and relationships
  /facts           - List all documents from vector store (insights + summaries)
  /insights        - List only insights (type='insight') with structured metadata
  /summaries       - List only turn summaries (type='summary')
  /transcript      - Show full transcript from persistent storage
  /export [format] - Export transcript (jsonl, markdown, or training)
  /reset           - Clear all memory stores (graph, vector, episodic)
  /vars            - Show scoped variables
  /set <key> <val> - Set a scoped variable (e.g., /set user:name Alice)
  /help            - Show this help
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

        # 2. Format prompt with assembled context
        messages = await self.assembler.format_prompt(
            system_prompt=self.system_prompt,
            payload=self.last_payload,
        )

        # Replace the last user message with the current input
        # (format_prompt extracts user_query from last history item, which is stale)
        if messages and messages[-1]["role"] == "user":
            messages[-1]["content"] = user_input
        else:
            messages.append({"role": "user", "content": user_input})

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
    )

    # Initialize session
    await session.initialize()
    print(f"Session initialized: {session_id}")
    print(f"Persistence directory: {persist_dir}")
    print("  - Vector store: ChromaDB")
    print(f"  - Graph store: {graph_path}")
    print(f"  - Transcript store: {transcript_path}")

    # Trigger priming by doing an initial recall (priming happens on first recall)
    if priming_config.get("enabled", True):
        await controller._ensure_session_primed(session_id)
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
