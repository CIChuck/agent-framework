"""Cancellation and retry safety for live memory extraction."""

from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace
from typing import Any, cast

import pytest
from friday_memory import (
    ExtractionCommitCompletedUnderCancellation,
    InteractionTurn,
    MemoryController,
    MemoryExtractor,
)


class StaticExtractionLlm:
    """Return one deterministic extraction response without provider I/O."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self._content = json.dumps(payload)

    async def chat_completion(self, **_kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(content=self._content, reasoning_content=None)


@pytest.mark.asyncio
async def test_cancellation_waits_for_current_turn_commit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    extractor = MemoryExtractor(
        memory_controller=cast(Any, object()),
        llm=cast(
            Any,
            StaticExtractionLlm(
                {"entities": [], "relationships": [], "insights": []}
            ),
        ),
    )
    commit_started = asyncio.Event()
    release_commit = asyncio.Event()
    commit_completed = asyncio.Event()

    async def controlled_commit(
        _turn: InteractionTurn,
        _extracted: dict[str, Any],
    ) -> dict[str, int]:
        commit_started.set()
        await release_commit.wait()
        commit_completed.set()
        return {"insights_stored": 0}

    monkeypatch.setattr(extractor, "_store_extractions", controlled_commit)
    task = asyncio.create_task(
        extractor.extract(
            InteractionTurn(
                id="stable-turn",
                session_id="session",
                user_message="Remember this",
                assistant_message="Noted",
            )
        )
    )
    await asyncio.wait_for(commit_started.wait(), timeout=1.0)

    task.cancel()
    await asyncio.sleep(0)
    assert task.done() is False
    assert commit_completed.is_set() is False

    release_commit.set()
    with pytest.raises(ExtractionCommitCompletedUnderCancellation):
        await asyncio.wait_for(task, timeout=1.0)

    assert commit_completed.is_set() is True


@pytest.mark.asyncio
async def test_repeating_same_turn_upserts_extraction_records(
    memory_controller: MemoryController,
) -> None:
    extractor = MemoryExtractor(
        memory_controller=memory_controller,
        llm=cast(
            Any,
            StaticExtractionLlm(
                {
                    "entities": [],
                    "relationships": [],
                    "insights": [
                        {
                            "text": "The user prefers deterministic retries.",
                            "topic": "preference",
                            "confidence": 0.95,
                            "sentiment": "positive",
                            "entities": [],
                        }
                    ],
                    "summary": "The turn established a retry preference.",
                }
            ),
        ),
    )
    turn = InteractionTurn(
        id="stable-turn",
        session_id="session",
        user_message="I prefer deterministic retries.",
        assistant_message="Understood.",
    )

    first = await extractor.extract(turn)
    second = await extractor.extract(turn)

    assert "error" not in first
    assert "error" not in second
    short_term = memory_controller.collection_manager.short_term
    assert await short_term.count() == 2
    records = await short_term.get_all(limit=None)
    assert {record["metadata"]["type"] for record in records} == {
        "insight",
        "summary",
    }
