# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
from datetime import datetime
from typing import Any

import pytest
from friday_core.interfaces.transcript import TranscriptBackedEpisodicStore
from friday_memory import InteractionTurn
from friday_transcript import TranscriptSession


class RecordingTranscriptStore:
    def __init__(self) -> None:
        self.sessions: dict[str, TranscriptSession] = {}
        self.entries: list[Any] = []
        self.context_logs: list[Any] = []

    async def append_entry(self, entry):
        self.entries.append(entry)
        return True

    async def get_entries(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
        after: datetime | None = None,
        before: datetime | None = None,
    ):
        return [entry for entry in self.entries if entry.session_id == session_id]

    async def count_entries(self, session_id: str) -> int:
        return sum(1 for entry in self.entries if entry.session_id == session_id)

    async def create_session(self, session: TranscriptSession) -> bool:
        self.sessions[session.session_id] = session
        return True

    async def get_session(self, session_id: str) -> TranscriptSession | None:
        return self.sessions.get(session_id)

    async def store_context_log(self, context_entry) -> bool:
        self.context_logs.append(context_entry)
        return True


@pytest.mark.asyncio
async def test_transcript_backed_store_persists_context_log_when_enabled():
    store = RecordingTranscriptStore()
    episodic = TranscriptBackedEpisodicStore(
        transcript_store=store,
        model_name="gpt-4o-mini",
        system_prompt="Runtime base prompt",
        capture_context_log=True,
    )

    turn = InteractionTurn(
        id="turn-1",
        session_id="session-1",
        user_message="hello",
        assistant_message="hi",
        raw_prompt='[{"role":"system","content":"Runtime base prompt"}]',
        raw_response='{"content":"hi"}',
    )

    result = await episodic.add_turn("session-1", turn)

    assert result is True
    assert len(store.entries) == 1
    assert len(store.context_logs) == 1
    assert store.context_logs[0].entry_id == "turn-1"
    assert store.sessions["session-1"].system_prompt == "Runtime base prompt"


@pytest.mark.asyncio
async def test_transcript_backed_store_skips_context_log_when_disabled():
    store = RecordingTranscriptStore()
    episodic = TranscriptBackedEpisodicStore(
        transcript_store=store,
        capture_context_log=False,
    )

    turn = InteractionTurn(
        id="turn-1",
        session_id="session-1",
        user_message="hello",
        assistant_message="hi",
        raw_prompt='[{"role":"user","content":"hello"}]',
        raw_response='{"content":"hi"}',
    )

    result = await episodic.add_turn("session-1", turn)

    assert result is True
    assert len(store.entries) == 1
    assert store.context_logs == []
