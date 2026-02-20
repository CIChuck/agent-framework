"""
Transcript integration interfaces.

Provides the bridge adapter that connects TranscriptStore implementations
to the EpisodicStoreAdapter protocol, enabling persistent transcript storage
to be used as an episodic memory backend.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from friday_core.interfaces.memory import EpisodicStoreAdapter

if TYPE_CHECKING:
    # Forward references to types - avoids circular imports
    from typing import TypeAlias

    TranscriptEntry: TypeAlias = Any
    TranscriptSession: TypeAlias = Any
    InteractionTurn: TypeAlias = Any


@runtime_checkable
class TranscriptStoreProtocol(Protocol):
    """
    Minimal protocol for transcript stores.

    This is a subset of the full TranscriptStore protocol from friday-transcript,
    containing only the methods needed by the bridge adapter.
    """

    async def append_entry(self, entry: "TranscriptEntry") -> bool:
        """Append a transcript entry."""
        ...

    async def get_entries(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
        after: datetime | None = None,
        before: datetime | None = None,
    ) -> list["TranscriptEntry"]:
        """Retrieve transcript entries for a session."""
        ...

    async def count_entries(self, session_id: str) -> int:
        """Count entries in a session."""
        ...

    async def create_session(self, session: "TranscriptSession") -> bool:
        """Create a new transcript session."""
        ...

    async def get_session(self, session_id: str) -> "TranscriptSession | None":
        """Retrieve session metadata."""
        ...


class TranscriptBackedEpisodicStore(EpisodicStoreAdapter):
    """
    Bridge adapter that connects TranscriptStore to EpisodicStoreAdapter.

    Allows friday-memory's MemoryController to use transcript storage
    for persistent episodic memory without direct dependency on
    friday-transcript.

    Usage:
        from friday_transcript import SQLiteTranscriptStore
        from friday_core import TranscriptBackedEpisodicStore

        transcript = SQLiteTranscriptStore("./transcript.db")
        episodic = TranscriptBackedEpisodicStore(transcript)

        controller = MemoryController(episodic_store=episodic, ...)
    """

    def __init__(
        self,
        transcript_store: TranscriptStoreProtocol,
        model_name: str = "unknown",
        system_prompt: str | None = None,
    ) -> None:
        """
        Initialize the bridge adapter.

        Args:
            transcript_store: The underlying TranscriptStore implementation
            model_name: Model name for new sessions (used in session creation)
            system_prompt: System prompt for new sessions
        """
        self._store = transcript_store
        self._model_name = model_name
        self._system_prompt = system_prompt

        # Track turn counts per session for turn_number assignment
        self._turn_counts: dict[str, int] = {}

    async def _ensure_session_exists(self, session_id: str) -> None:
        """Create session if it doesn't exist."""
        # Import here to avoid circular import at module level
        try:
            from friday_transcript import TranscriptSession
        except ImportError:
            # If friday-transcript not installed, skip session creation
            return

        session = await self._store.get_session(session_id)
        if session is None:
            new_session = TranscriptSession(
                session_id=session_id,
                model_name=self._model_name,
                system_prompt=self._system_prompt,
            )
            await self._store.create_session(new_session)

    async def add_turn(self, session_id: str, turn: "InteractionTurn") -> bool:
        """
        Add a turn to the transcript.

        Converts InteractionTurn to TranscriptEntry and appends it.
        """
        await self._ensure_session_exists(session_id)

        # Import here to avoid circular import at module level
        try:
            from friday_transcript import ToolCall, ToolResult, TranscriptEntry
        except ImportError as e:
            raise ImportError(
                "friday-transcript is required for TranscriptBackedEpisodicStore. "
                "Install it with: pip install friday-transcript"
            ) from e

        # Get next turn number (don't increment until write succeeds)
        if session_id not in self._turn_counts:
            self._turn_counts[session_id] = await self._store.count_entries(session_id)
        turn_number = self._turn_counts[session_id] + 1

        # Convert InteractionTurn to TranscriptEntry
        entry = TranscriptEntry(
            id=turn.id,
            session_id=session_id,
            turn_number=turn_number,
            user_message=turn.user_message,
            assistant_message=turn.assistant_message,
            # Agent tracking for provenance
            agent_id=getattr(turn, "agent_id", None),
            tool_calls=[
                ToolCall(id=tc.id, name=tc.name, arguments=tc.arguments)
                for tc in getattr(turn, "tool_calls", [])
            ],
            tool_results=[
                ToolResult(
                    tool_call_id=tr.tool_call_id,
                    output=tr.output,
                    error=tr.error,
                )
                for tr in getattr(turn, "tool_results", [])
            ],
            timestamp=turn.timestamp,
            metadata=getattr(turn, "metadata", {}),
            # Timing metrics
            response_started_at=getattr(turn, "response_started_at", None),
            response_completed_at=getattr(turn, "response_completed_at", None),
            # Token usage metrics
            prompt_tokens=getattr(turn, "prompt_tokens", None),
            completion_tokens=getattr(turn, "completion_tokens", None),
            total_tokens=getattr(turn, "total_tokens", None),
            latency_ms=getattr(turn, "latency_ms", None),
            # Model configuration
            model_name=getattr(turn, "model_name", None),
            temperature=getattr(turn, "temperature", None),
            context_tokens_used=getattr(turn, "context_tokens_used", None),
        )

        # Only increment turn count after successful write
        result = await self._store.append_entry(entry)
        if result:
            self._turn_counts[session_id] = turn_number
        return result

    async def get_turns(
        self, session_id: str, limit: int = 10, offset: int = 0
    ) -> list["InteractionTurn"]:
        """
        Get turns from the transcript.

        Retrieves TranscriptEntries and converts them to InteractionTurns.
        """
        # Import here to avoid circular import
        try:
            from friday_memory import InteractionTurn
            from friday_memory.models import ToolCall as MemoryToolCall
            from friday_memory.models import ToolResult as MemoryToolResult
        except ImportError:
            # If friday-memory not available, return empty
            return []

        # Fetch a large window and filter compacted entries in Python.
        # count_entries() includes compacted entries, so offset-based
        # paging can yield fewer than `limit` active turns when compacted
        # entries exist.  Session sizes are bounded (typically <200 turns)
        # so fetching a generous window is not a performance concern.
        fetch_limit = max(limit * 3, 500)
        entries = await self._store.get_entries(
            session_id,
            limit=fetch_limit,
            offset=offset,
        )

        turns = []
        for entry in entries:
            turn = InteractionTurn(
                id=entry.id,
                session_id=entry.session_id,
                timestamp=entry.timestamp,
                user_message=entry.user_message,
                assistant_message=entry.assistant_message,
                # Agent tracking for provenance
                agent_id=getattr(entry, "agent_id", None),
                tool_calls=[
                    MemoryToolCall(id=tc.id, name=tc.name, arguments=tc.arguments)
                    for tc in entry.tool_calls
                ],
                tool_results=[
                    MemoryToolResult(
                        tool_call_id=tr.tool_call_id,
                        output=tr.output,
                        error=tr.error,
                    )
                    for tr in entry.tool_results
                ],
                metadata=entry.metadata,
                # Use persisted consolidated state from the entry
                consolidated=getattr(entry, "consolidated", False),
                compacted=getattr(entry, "compacted", False),
            )
            # Exclude compacted turns from raw history retrieval
            if not turn.compacted:
                turns.append(turn)

        # Return the most recent `limit` active turns
        return turns[-limit:] if len(turns) > limit else turns

    async def get_unconsolidated_turns(
        self, session_id: str, limit: int = 100
    ) -> list["InteractionTurn"]:
        """
        Get turns that haven't been consolidated yet.

        Delegates to the underlying store's persistent consolidation tracking.
        """
        # Import here to avoid circular import
        try:
            from friday_memory import InteractionTurn
            from friday_memory.models import ToolCall as MemoryToolCall
            from friday_memory.models import ToolResult as MemoryToolResult
        except ImportError:
            return []

        # Delegate to store if it supports persistent consolidation tracking
        if hasattr(self._store, "get_unconsolidated_entries"):
            entries = await self._store.get_unconsolidated_entries(session_id, limit)
            turns = []
            for entry in entries:
                turn = InteractionTurn(
                    id=entry.id,
                    session_id=entry.session_id,
                    timestamp=entry.timestamp,
                    user_message=entry.user_message,
                    assistant_message=entry.assistant_message,
                    # Agent tracking for provenance
                    agent_id=getattr(entry, "agent_id", None),
                    tool_calls=[
                        MemoryToolCall(id=tc.id, name=tc.name, arguments=tc.arguments)
                        for tc in entry.tool_calls
                    ],
                    tool_results=[
                        MemoryToolResult(
                            tool_call_id=tr.tool_call_id,
                            output=tr.output,
                            error=tr.error,
                        )
                        for tr in entry.tool_results
                    ],
                    metadata=entry.metadata,
                    consolidated=False,  # By definition, these are unconsolidated
                )
                turns.append(turn)
            return turns

        # Fallback: return all turns (legacy stores without consolidation tracking)
        return await self.get_turns(session_id, limit=limit)

    async def mark_consolidated(self, turn_ids: list[str]) -> bool:
        """
        Mark turns as consolidated (extracted to long-term memory).

        Delegates to the underlying store's persistent consolidation tracking.
        """
        if not turn_ids:
            return True

        # Delegate to store if it supports persistent consolidation tracking
        if hasattr(self._store, "mark_entries_consolidated"):
            count = await self._store.mark_entries_consolidated(turn_ids)
            return count > 0

        # Fallback for stores without persistent consolidation support
        # Log warning since consolidation state won't persist across restarts
        import logging

        logging.getLogger(__name__).warning(
            "Store doesn't support persistent consolidation tracking; "
            "consolidation state will be lost on restart"
        )
        return False

    async def mark_compacted(self, turn_ids: list[str]) -> bool:
        """
        Mark turns as compacted (summarized by InSessionCompactor).

        Compacted turns are excluded from raw history retrieval via
        ``get_turns()`` but remain in the transcript for audit purposes.
        Delegates to the underlying store if it supports persistent
        compaction tracking.
        """
        if not turn_ids:
            return True

        if hasattr(self._store, "mark_entries_compacted"):
            count = await self._store.mark_entries_compacted(turn_ids)
            return count > 0

        # Fallback for stores without persistent compaction support
        import logging

        logging.getLogger(__name__).warning(
            "Store doesn't support persistent compaction tracking; "
            "compaction state will be lost on restart"
        )
        return False

    async def rewind_history(self, session_id: str, target_turn_id: str) -> bool:
        """
        Rewind is not supported for append-only transcripts.

        Transcripts are immutable audit logs. This method returns False
        to indicate the operation is not supported.

        For recovery scenarios, consider starting a new session instead.
        """
        # Transcripts are append-only - rewind not supported
        return False

    # --- Additional utility methods ---

    async def clear_session(self, session_id: str) -> None:
        """
        Clear local tracking for a session.

        Note: This does NOT delete transcript data (which is immutable).
        It only clears the in-memory turn count cache.
        """
        self._turn_counts.pop(session_id, None)
