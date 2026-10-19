"""Direct behavior of the UI-neutral transcript session-ensure effect."""

from __future__ import annotations

import asyncio
import subprocess
import sys
from datetime import datetime

import pytest
from friday_runtime.transcript_session_effects import ensure_transcript_session
from friday_transcript import TranscriptSession


class FakeSessionStore:
    def __init__(self, session: TranscriptSession | None = None) -> None:
        self.session = session
        self.events: list[str] = []
        self.get_failure: BaseException | None = None
        self.create_failure: BaseException | None = None
        self.create_result = True

    async def get_session(self, session_id: str) -> TranscriptSession | None:
        self.events.append(f"get:{session_id}")
        if self.get_failure is not None:
            raise self.get_failure
        return self.session

    async def create_session(self, session: TranscriptSession) -> bool:
        self.events.append(f"create:{session.session_id}")
        if self.create_failure is not None:
            raise self.create_failure
        if self.create_result:
            self.session = session
        return self.create_result


def _session() -> TranscriptSession:
    return TranscriptSession(session_id="session", model_name="fake/model")


@pytest.mark.asyncio
async def test_missing_session_lazily_constructs_once_after_read() -> None:
    store = FakeSessionStore()
    created = _session()
    factory_calls = 0

    def factory() -> TranscriptSession:
        nonlocal factory_calls
        store.events.append("factory")
        factory_calls += 1
        return created

    await ensure_transcript_session(store, "session", factory)
    assert store.session is created
    assert store.events == ["get:session", "factory", "create:session"]
    assert factory_calls == 1

    await ensure_transcript_session(store, "session", factory)
    assert store.session is created
    assert store.events[-1] == "get:session"
    assert factory_calls == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "ended,archived", [(False, False), (True, False), (False, True)]
)
async def test_existing_session_is_not_reopened_or_replaced(
    ended: bool, archived: bool
) -> None:
    existing = TranscriptSession(
        session_id="session",
        model_name="historical",
        ended_at=datetime(2020, 1, 2) if ended else None,
        archived=archived,
        config_snapshot={"earlier": True},
    )
    store = FakeSessionStore(existing)

    def unexpected_factory() -> TranscriptSession:
        pytest.fail("existing session evaluated new-session factory")

    await ensure_transcript_session(store, "session", unexpected_factory)
    assert store.session is existing
    assert existing.config_snapshot == {"earlier": True}
    assert existing.ended_at == (datetime(2020, 1, 2) if ended else None)
    assert existing.archived is archived
    assert store.events == ["get:session"]


@pytest.mark.asyncio
async def test_false_create_is_ignored_without_reread_or_retry() -> None:
    store = FakeSessionStore()
    store.create_result = False

    await ensure_transcript_session(store, "session", _session)
    assert store.session is None
    assert store.events == ["get:session", "create:session"]


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["get", "factory", "create"])
@pytest.mark.parametrize("failure_type", [ValueError, asyncio.CancelledError])
async def test_failure_or_cancellation_propagates_without_recovery(
    operation: str, failure_type: type[BaseException]
) -> None:
    store = FakeSessionStore()
    failure = failure_type("injected")
    if operation == "get":
        store.get_failure = failure
    elif operation == "create":
        store.create_failure = failure

    def factory() -> TranscriptSession:
        store.events.append("factory")
        if operation == "factory":
            raise failure
        return _session()

    with pytest.raises(failure_type) as caught:
        await ensure_transcript_session(store, "session", factory)

    assert caught.value is failure
    assert store.session is None
    assert (
        store.events
        == {
            "get": ["get:session"],
            "factory": ["get:session", "factory"],
            "create": ["get:session", "factory", "create:session"],
        }[operation]
    )


def test_neutral_session_effect_import_does_not_load_chat_or_cli() -> None:
    code = """
import asyncio
import builtins
import sys
from friday_transcript import TranscriptSession
original = builtins.__import__
def guarded(name, *args, **kwargs):
    if name.startswith(('friday_chat', 'friday_cli')):
        raise RuntimeError(name)
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
from friday_runtime.transcript_session_effects import ensure_transcript_session
class Store:
    async def get_session(self, session_id): return None
    async def create_session(self, session): return True
assert asyncio.run(ensure_transcript_session(
    Store(), 'session', lambda: TranscriptSession(session_id='session', model_name='fake')
)) is None
assert not any(name.startswith(('friday_chat', 'friday_cli')) for name in sys.modules)
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
