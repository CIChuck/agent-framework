"""
Transcript integration interfaces.

Provides the bridge adapter that connects TranscriptStore implementations
to the EpisodicStoreAdapter protocol, enabling persistent transcript storage
to be used as an episodic memory backend.
"""

import uuid
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

        # Track consolidated turn IDs per session
        self._consolidated: dict[str, set[str]] = {}

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
            from friday_transcript import TranscriptEntry, ToolCall, ToolResult
        except ImportError as e:
            raise ImportError(
                "friday-transcript is required for TranscriptBackedEpisodicStore. "
                "Install it with: pip install friday-transcript"
            ) from e

        # Get next turn number
        if session_id not in self._turn_counts:
            self._turn_counts[session_id] = await self._store.count_entries(session_id)
        self._turn_counts[session_id] += 1
        turn_number = self._turn_counts[session_id]

        # Convert InteractionTurn to TranscriptEntry
        entry = TranscriptEntry(
            id=turn.id,
            session_id=session_id,
            turn_number=turn_number,
            user_message=turn.user_message,
            assistant_message=turn.assistant_message,
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
        )

        return await self._store.append_entry(entry)

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

        entries = await self._store.get_entries(session_id, limit=limit, offset=offset)

        turns = []
        for entry in entries:
            turn = InteractionTurn(
                id=entry.id,
                session_id=entry.session_id,
                timestamp=entry.timestamp,
                user_message=entry.user_message,
                assistant_message=entry.assistant_message,
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
                consolidated=entry.id in self._consolidated.get(session_id, set()),
            )
            turns.append(turn)

        return turns

    async def get_unconsolidated_turns(
        self, session_id: str
    ) -> list["InteractionTurn"]:
        """
        Get turns that haven't been consolidated yet.

        Since transcripts are append-only, we track consolidated status in memory.
        """
        all_turns = await self.get_turns(session_id, limit=10000)
        consolidated = self._consolidated.get(session_id, set())
        return [t for t in all_turns if t.id not in consolidated]

    async def mark_consolidated(self, turn_ids: list[str]) -> bool:
        """
        Mark turns as consolidated.

        Since transcripts are immutable, we track this in memory.
        For persistence across restarts, consider storing in session metadata.
        """
        # Determine session_id from turns (all should be same session)
        for turn_id in turn_ids:
            # Find which session this turn belongs to
            for session_id, turns_set in self._consolidated.items():
                turns_set.add(turn_id)
                return True

            # If session not found, create entry (assumes single session usage)
            # In practice, you'd want to look this up from the transcript
            if turn_ids:
                # Use a default session - in real usage this would be tracked
                default_session = "default"
                if default_session not in self._consolidated:
                    self._consolidated[default_session] = set()
                self._consolidated[default_session].update(turn_ids)

        return True

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
        It only clears the in-memory tracking state.
        """
        self._turn_counts.pop(session_id, None)
        self._consolidated.pop(session_id, None)

    def mark_session_consolidated(self, session_id: str, turn_ids: set[str]) -> None:
        """
        Bulk mark turns as consolidated for a session.

        Useful for restoring state on startup.
        """
        if session_id not in self._consolidated:
            self._consolidated[session_id] = set()
        self._consolidated[session_id].update(turn_ids)
