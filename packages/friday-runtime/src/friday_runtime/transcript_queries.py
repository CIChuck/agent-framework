"""UI-neutral read adapter for persisted Friday transcripts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from friday_transcript import ContextLogEntry, TranscriptEntry, TranscriptSession

from friday_runtime.transcript_views import (
    TranscriptContextLogView,
    TranscriptEntryView,
    TranscriptQueryStore,
    TranscriptSessionView,
)


class TranscriptRecordReader(Protocol):
    """The persisted transcript reads needed by ``TranscriptQueryAdapter``."""

    async def get_session(self, session_id: str) -> TranscriptSession | None: ...

    async def list_sessions(
        self,
        limit: int = 100,
        offset: int = 0,
        user_id: str | None = None,
        active_only: bool = False,
        include_archived: bool = False,
    ) -> list[TranscriptSession]: ...

    async def get_entries(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
        after: datetime | None = None,
        before: datetime | None = None,
    ) -> list[TranscriptEntry]: ...

    async def get_context_log_for_session(
        self, session_id: str, limit: int = 100
    ) -> list[ContextLogEntry]: ...


@dataclass(frozen=True)
class TranscriptQueryAdapter(TranscriptQueryStore):
    """Map persisted transcript records to frontend-independent query views."""

    store: TranscriptRecordReader

    async def query_sessions(
        self,
        *,
        limit: int = 1000,
        include_archived: bool = False,
    ) -> tuple[TranscriptSessionView, ...]:
        sessions = await self.store.list_sessions(
            limit=min(max(limit, 0), 1000),
            include_archived=include_archived,
        )
        visible_ids = (
            await self._non_archived_session_ids()
            if include_archived
            else {session.session_id for session in sessions}
        )
        views = (
            _transcript_session_view(
                session,
                archived=session.session_id not in visible_ids,
            )
            for session in sessions
        )
        return tuple(
            sorted(
                views,
                key=lambda session: (
                    _datetime_sort_key(session.started_at),
                    session.session_id,
                ),
                reverse=True,
            )
        )

    async def query_session(self, session_id: str) -> TranscriptSessionView | None:
        session = await self.store.get_session(session_id)
        if session is None:
            return None
        return _transcript_session_view(
            session,
            archived=session_id not in await self._non_archived_session_ids(),
        )

    async def query_entries(
        self,
        session_id: str,
    ) -> tuple[TranscriptEntryView, ...]:
        entries: list[TranscriptEntry] = []
        offset = 0
        page_size = 1000
        while True:
            page = await self.store.get_entries(
                session_id,
                limit=page_size,
                offset=offset,
            )
            entries.extend(page)
            if len(page) < page_size:
                break
            offset += page_size
        views = (_transcript_entry_view(entry) for entry in entries)
        return tuple(
            sorted(
                views,
                key=lambda entry: (
                    entry.turn_number,
                    _datetime_sort_key(entry.timestamp),
                    entry.entry_id,
                ),
            )
        )

    async def query_context_logs(
        self,
        session_id: str,
    ) -> tuple[TranscriptContextLogView, ...]:
        context_logs = await self.store.get_context_log_for_session(
            session_id,
            limit=100_000,
        )
        views = (_transcript_context_log_view(entry) for entry in context_logs)
        return tuple(
            sorted(
                views,
                key=lambda entry: (
                    entry.turn_number,
                    _datetime_sort_key(entry.captured_at),
                    entry.log_id,
                ),
            )
        )

    async def _non_archived_session_ids(self) -> set[str]:
        session_ids: set[str] = set()
        offset = 0
        page_size = 1000
        while True:
            page = await self.store.list_sessions(
                limit=page_size,
                offset=offset,
                include_archived=False,
            )
            session_ids.update(session.session_id for session in page)
            if len(page) < page_size:
                break
            offset += page_size
        return session_ids


def _transcript_session_view(
    session: TranscriptSession,
    *,
    archived: bool | None = None,
) -> TranscriptSessionView:
    return TranscriptSessionView(
        session_id=session.session_id,
        user_id=session.user_id,
        started_at=session.started_at,
        ended_at=session.ended_at,
        model_name=session.model_name,
        total_turns=session.total_turns,
        total_tokens=session.total_tokens,
        archived=session.archived if archived is None else archived,
    )


def _transcript_entry_view(entry: TranscriptEntry) -> TranscriptEntryView:
    return TranscriptEntryView(
        entry_id=entry.id,
        session_id=entry.session_id,
        turn_number=entry.turn_number,
        user_message=entry.user_message,
        assistant_message=entry.assistant_message,
        timestamp=entry.timestamp,
        model_name=entry.model_name,
        total_tokens=entry.total_tokens,
        latency_ms=entry.latency_ms,
    )


def _transcript_context_log_view(
    entry: ContextLogEntry,
) -> TranscriptContextLogView:
    return TranscriptContextLogView(
        log_id=entry.id,
        session_id=entry.session_id,
        turn_number=entry.turn_number,
        entry_id=entry.entry_id,
        raw_prompt=entry.raw_prompt,
        raw_response=entry.raw_response,
        captured_at=entry.captured_at,
    )


def _datetime_sort_key(value: datetime) -> float:
    normalized = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    return normalized.timestamp()


__all__ = ["TranscriptQueryAdapter", "TranscriptRecordReader"]
