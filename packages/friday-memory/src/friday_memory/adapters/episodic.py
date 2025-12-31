"""
Episodic Memory Adapter Implementation.
Handles short-term history logging and time-travel (rewind).

Ref: Batch 1 Specification, Section 1.1
"""

from collections import defaultdict

from friday_core import EpisodicStoreAdapter, TelemetryInterface

from friday_memory.models import InteractionTurn


class InMemoryEpisodicStore(EpisodicStoreAdapter):
    """
    In-memory implementation of EpisodicStoreAdapter.

    Stores conversation turns in memory, organized by session.
    Suitable for development/testing; production should use
    a persistent backend (Redis, SQLite, etc.).

    Features:
    - Chronological turn storage per session
    - Consolidation tracking for extraction cycles
    - Time-travel support via rewind_history
    """

    def __init__(self, telemetry: TelemetryInterface | None = None) -> None:
        """
        Initialize the in-memory episodic store.

        Args:
            telemetry: Optional telemetry recorder for white-box testing
        """
        self._telemetry = telemetry
        # session_id -> list of turns (chronological order)
        self._sessions: dict[str, list[InteractionTurn]] = defaultdict(list)

    def _emit_event(self, event_name: str, data: dict) -> None:
        """Emit telemetry event if recorder is configured."""
        if self._telemetry:
            self._telemetry.capture_event(event_name, data)

    async def add_turn(self, session_id: str, turn: InteractionTurn) -> bool:
        """
        Logs a single user/assistant interaction.

        Args:
            session_id: Unique session identifier
            turn: The interaction turn to store

        Returns:
            True if successful
        """
        self._sessions[session_id].append(turn)
        self._emit_event(
            "episodic_turn_added",
            {"session_id": session_id, "turn_id": turn.id},
        )
        return True

    async def get_turns(
        self, session_id: str, limit: int = 10, offset: int = 0
    ) -> list[InteractionTurn]:
        """
        Retrieves chronological history for context injection.

        Args:
            session_id: Unique session identifier
            limit: Maximum number of turns to retrieve
            offset: Number of turns to skip (for pagination)

        Returns:
            List of interaction turns, ordered chronologically
        """
        turns = self._sessions.get(session_id, [])
        return turns[offset : offset + limit]

    async def get_unconsolidated_turns(
        self, session_id: str
    ) -> list[InteractionTurn]:
        """
        Retrieves turns that have NOT yet been processed by MemoryConsolidator.

        Args:
            session_id: Unique session identifier

        Returns:
            List of unprocessed interaction turns
        """
        turns = self._sessions.get(session_id, [])
        return [t for t in turns if not t.consolidated]

    async def mark_consolidated(self, turn_ids: list[str]) -> bool:
        """
        Marks specific turns as 'processed' so they aren't re-extracted.

        Args:
            turn_ids: List of turn IDs to mark as consolidated

        Returns:
            True if successful
        """
        turn_id_set = set(turn_ids)
        marked_count = 0

        for turns in self._sessions.values():
            for turn in turns:
                if turn.id in turn_id_set and not turn.consolidated:
                    turn.consolidated = True
                    marked_count += 1

        self._emit_event(
            "episodic_turns_consolidated",
            {"turn_ids": turn_ids, "marked_count": marked_count},
        )
        return True

    async def rewind_history(self, session_id: str, target_turn_id: str) -> bool:
        """
        Hard Reset: Deletes all interaction turns *after* the target_turn_id.

        Used to recover from 'death spirals' or logic errors.

        Args:
            session_id: Unique session identifier
            target_turn_id: The turn ID to rewind to (this turn is kept)

        Returns:
            True if successful, False if target turn not found
        """
        if session_id not in self._sessions:
            return False

        turns = self._sessions[session_id]

        # Find the index of the target turn
        target_index = None
        for i, turn in enumerate(turns):
            if turn.id == target_turn_id:
                target_index = i
                break

        if target_index is None:
            return False

        # Keep turns up to and including the target
        deleted_count = len(turns) - target_index - 1
        self._sessions[session_id] = turns[: target_index + 1]

        self._emit_event(
            "episodic_history_rewound",
            {
                "session_id": session_id,
                "target_turn_id": target_turn_id,
                "turns_deleted": deleted_count,
            },
        )
        return True

    # --- Additional utility methods ---

    async def get_session_ids(self) -> list[str]:
        """Return all session IDs with stored turns."""
        return list(self._sessions.keys())

    async def clear_session(self, session_id: str) -> bool:
        """Clear all turns for a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    async def get_turn_count(self, session_id: str) -> int:
        """Get the number of turns in a session."""
        return len(self._sessions.get(session_id, []))
