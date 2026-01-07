"""
TranscriptStore protocol.

Defines the interface for transcript persistence backends.
Implementations must be append-only for audit compliance.
"""

from datetime import datetime
from typing import Any, Protocol, runtime_checkable

from friday_transcript.models.transcript import TranscriptEntry, TranscriptSession


@runtime_checkable
class TranscriptStore(Protocol):
    """
    Protocol for transcript persistence backends.

    All implementations must:
    - Be append-only (entries cannot be modified or deleted)
    - Support async operations
    - Maintain chronological ordering
    """

    # --- Session Management ---

    async def create_session(self, session: TranscriptSession) -> bool:
        """
        Create a new transcript session.

        Args:
            session: Session metadata to store

        Returns:
            True if created successfully
        """
        ...

    async def end_session(self, session_id: str) -> bool:
        """
        Mark a session as ended.

        Sets the ended_at timestamp and finalizes aggregates.

        Args:
            session_id: Session to end

        Returns:
            True if ended successfully
        """
        ...

    async def get_session(self, session_id: str) -> TranscriptSession | None:
        """
        Retrieve session metadata.

        Args:
            session_id: Session to retrieve

        Returns:
            Session metadata or None if not found
        """
        ...

    async def list_sessions(
        self,
        limit: int = 100,
        offset: int = 0,
        user_id: str | None = None,
        active_only: bool = False,
    ) -> list[TranscriptSession]:
        """
        List transcript sessions.

        Args:
            limit: Maximum sessions to return
            offset: Number of sessions to skip
            user_id: Filter by user ID (optional)
            active_only: Only return active (non-ended) sessions

        Returns:
            List of sessions ordered by start time (newest first)
        """
        ...

    # --- Entry Management (Append-Only) ---

    async def append_entry(self, entry: TranscriptEntry) -> bool:
        """
        Append a transcript entry.

        This is the only write operation for entries - they cannot be
        modified or deleted once appended.

        Args:
            entry: Entry to append

        Returns:
            True if appended successfully
        """
        ...

    async def get_entries(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
        after: datetime | None = None,
        before: datetime | None = None,
    ) -> list[TranscriptEntry]:
        """
        Retrieve transcript entries for a session.

        Args:
            session_id: Session to retrieve entries from
            limit: Maximum entries to return
            offset: Number of entries to skip
            after: Only entries after this timestamp
            before: Only entries before this timestamp

        Returns:
            List of entries ordered by turn_number
        """
        ...

    async def get_entry(self, entry_id: str) -> TranscriptEntry | None:
        """
        Retrieve a single entry by ID.

        Args:
            entry_id: Entry ID to retrieve

        Returns:
            Entry or None if not found
        """
        ...

    async def count_entries(self, session_id: str) -> int:
        """
        Count entries in a session.

        Args:
            session_id: Session to count

        Returns:
            Number of entries
        """
        ...

    # --- Analytics Hooks ---

    async def get_token_stats(self, session_id: str) -> dict[str, Any]:
        """
        Get token usage statistics for a session.

        Args:
            session_id: Session to analyze

        Returns:
            Dict with token statistics:
            - total_prompt_tokens: int
            - total_completion_tokens: int
            - total_tokens: int
            - avg_tokens_per_turn: float
            - max_tokens_turn: int
        """
        ...

    async def get_latency_stats(self, session_id: str) -> dict[str, Any]:
        """
        Get latency statistics for a session.

        Args:
            session_id: Session to analyze

        Returns:
            Dict with latency statistics:
            - total_latency_ms: float
            - avg_latency_ms: float
            - min_latency_ms: float
            - max_latency_ms: float
            - p50_latency_ms: float
            - p95_latency_ms: float
        """
        ...
