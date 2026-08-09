"""Gate A reproductions for command behavior against production adapters.

The five command-area regressions in this module intentionally fail on the
pre-remediation baseline.  They are retained target-behavior tests, not xfails:
Gate A records their failure evidence before any production behavior changes.
"""

from __future__ import annotations

import asyncio
import json
import socket
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from friday_chat import adapters
from friday_chat.adapters import (
    FrameworkChatModel,
    FrameworkEmbeddingService,
    FrameworkMemoryAdapter,
    FrameworkTranscriptAdapter,
)
from friday_chat.app import FridayChatApp, ListInputSource, ListOutputSink
from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.config import FridayChatConfig
from friday_chat.display import Heartbeat, HeartbeatKind
from friday_chat.runtime import (
    FakeChatModel,
    FakeMemoryController,
    FridayRuntime,
    build_runtime,
)
from friday_chat.turns.processor import TurnProcessor
from friday_llm import LiteLLMEmbeddingService, LiteLLMService
from friday_transcript import TranscriptEntry, TranscriptSession

CURRENT_SESSION_ID = "production-current-session"
REPOSITORY_ROOT = Path(__file__).resolve(strict=False).parents[3]
ACTIVE_STATE_ROOTS = (
    REPOSITORY_ROOT / ".friday",
    Path.home().resolve(strict=False) / ".friday",
)


class DeterministicEmbeddingBackend(LiteLLMEmbeddingService):
    """In-process embedding double used behind the production adapter."""

    def __init__(self) -> None:
        """Avoid constructing any provider transport in the test double."""

    async def embed_query(self, text: str) -> list[float]:
        return _embedding_for(text)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [_embedding_for(text) for text in texts]


class RecordingHeartbeat:
    """No-op heartbeat required by the display contract."""

    def start(self) -> None:
        return None

    def stop(self) -> None:
        return None


class RecordingClearDisplay:
    """Production-shaped display double that records clear-screen effects."""

    def __init__(self) -> None:
        self.clear_calls = 0

    def render_banner(self, *, assistant_name: str, version: str) -> None:
        return None

    def prompt_text(self, *, user_name: str) -> str:
        return f"{user_name}: "

    def create_heartbeat(self, kind: HeartbeatKind) -> Heartbeat:
        return RecordingHeartbeat()

    def clear_screen(self) -> None:
        self.clear_calls += 1


@pytest.fixture(autouse=True)
def prohibit_provider_and_network_transports(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fail before a provider or network transport can be reached."""

    async def reject_provider_call(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("provider transport is prohibited in Gate A tests")

    async def reject_provider_stream(
        *_args: object,
        **_kwargs: object,
    ) -> AsyncIterator[str]:
        raise AssertionError("provider transport is prohibited in Gate A tests")
        yield ""  # pragma: no cover - preserves the async-iterator contract

    def reject_network_call(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("network access is prohibited in Gate A tests")

    monkeypatch.setenv("ANONYMIZED_TELEMETRY", "False")
    monkeypatch.setattr(LiteLLMService, "chat_completion", reject_provider_call)
    monkeypatch.setattr(
        LiteLLMService,
        "chat_completion_stream",
        reject_provider_stream,
    )
    monkeypatch.setattr(
        LiteLLMEmbeddingService,
        "embed_query",
        reject_provider_call,
    )
    monkeypatch.setattr(
        LiteLLMEmbeddingService,
        "embed_documents",
        reject_provider_call,
    )
    monkeypatch.setattr(socket.socket, "connect", reject_network_call)
    monkeypatch.setattr(socket.socket, "connect_ex", reject_network_call)
    monkeypatch.setattr(socket, "create_connection", reject_network_call)
    monkeypatch.setattr(asyncio, "open_connection", reject_provider_call)


@pytest.fixture
def production_runtime(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    prohibit_provider_and_network_transports: None,
) -> FridayRuntime:
    """Build real Friday adapters with deterministic, disposable dependencies."""
    state_root = tmp_path / "runtime-state"
    configured_paths = (
        state_root / "vector",
        state_root / "transcripts",
        state_root / "recovery",
        state_root / "logs",
    )
    for path in configured_paths:
        _assert_disposable_path(path, tmp_path)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        adapters,
        "build_framework_embedding_service",
        lambda _config: FrameworkEmbeddingService(
            service=DeterministicEmbeddingBackend()
        ),
    )
    config = FridayChatConfig.model_validate(
        {
            "llm": {
                "model": "openai/test-chat-model",
                "api_key": "gate-a-provider-prohibited",
            },
            "embedding": {
                "model": "openai/test-embedding-model",
                "api_key": "gate-a-provider-prohibited",
            },
            "memory": {
                "persist_directory": str(state_root / "vector"),
                "context_window": 4096,
                "output_buffer": 512,
            },
            "transcript": {
                "export_directory": str(state_root / "transcripts"),
            },
            "maintenance": {
                "backup_directory": str(state_root / "recovery"),
                "logging": {"log_directory": str(state_root / "logs")},
            },
            "tools": {
                "enabled": True,
                "registry": [
                    {
                        "name": "echo",
                        "module": "friday_tools.utility",
                        "class": "EchoTool",
                    }
                ],
                "context": {
                    "include_in_context": True,
                    "max_tools": 1,
                    "max_budget_ratio": 0.25,
                },
            },
        }
    )
    runtime = build_runtime(
        config,
        fake=False,
        session_id=CURRENT_SESSION_ID,
    )

    assert isinstance(runtime.memory, FrameworkMemoryAdapter)
    assert isinstance(runtime.transcript, FrameworkTranscriptAdapter)
    _assert_disposable_layout(runtime, tmp_path)
    return runtime


def test_production_fixture_paths_are_disposable(
    production_runtime: FridayRuntime,
    tmp_path: Path,
) -> None:
    """Tripwire every declared persistence path against active state roots."""
    _assert_disposable_layout(production_runtime, tmp_path)


async def test_provider_and_network_tripwires_fail_closed(
    production_runtime: FridayRuntime,
) -> None:
    """Prove both tripwires intercept calls before transport I/O."""
    assert isinstance(production_runtime.chat_llm, FrameworkChatModel)
    with pytest.raises(AssertionError, match="provider transport is prohibited"):
        await production_runtime.chat_llm.service.chat_completion(messages=[])
    with pytest.raises(AssertionError, match="network access is prohibited"):
        socket.create_connection(("127.0.0.1", 9))


async def test_sessions_lists_seeded_persisted_session(
    production_runtime: FridayRuntime,
) -> None:
    await _seed_transcript_session(
        production_runtime,
        session_id="persisted-session",
        user_message="persisted sessions user marker",
        assistant_message="persisted sessions assistant marker",
    )

    result = await _execute(production_runtime, "/sessions")

    assert "persisted-session" in result


async def test_transcript_reads_seeded_current_and_selected_sessions(
    production_runtime: FridayRuntime,
) -> None:
    selected_session_id = "persisted-selected-session"
    await _seed_transcript_session(
        production_runtime,
        session_id=CURRENT_SESSION_ID,
        user_message="current transcript user marker",
        assistant_message="current transcript assistant marker",
    )
    await _seed_transcript_session(
        production_runtime,
        session_id=selected_session_id,
        user_message="selected transcript user marker",
        assistant_message="selected transcript assistant marker",
    )

    current = await _execute(production_runtime, "/transcript")
    selected = await _execute(
        production_runtime,
        f"/transcript {selected_session_id}",
    )

    assert {
        "current_user_visible": "current transcript user marker" in current,
        "current_assistant_visible": "current transcript assistant marker" in current,
        "selected_user_visible": "selected transcript user marker" in selected,
        "selected_assistant_visible": (
            "selected transcript assistant marker" in selected
        ),
    } == {
        "current_user_visible": True,
        "current_assistant_visible": True,
        "selected_user_visible": True,
        "selected_assistant_visible": True,
    }


async def test_memory_reports_seeded_real_episodic_count(
    production_runtime: FridayRuntime,
) -> None:
    await production_runtime.memory.store_turn(
        "episodic user marker",
        "episodic assistant marker",
    )

    result = await _execute(production_runtime, "/memory")

    episodic_lines = [
        line
        for line in result.splitlines()
        if "episodic" in line.lower() and line.rstrip().endswith(": 1")
    ]
    assert episodic_lines, result


async def test_clear_aliases_request_display_effect_without_false_output(
    production_runtime: FridayRuntime,
) -> None:
    display = RecordingClearDisplay()
    output = ListOutputSink()
    app = FridayChatApp(
        runtime=production_runtime,
        input_source=ListInputSource(["/cls", "/clearscreen"]),
        output_sink=output,
        display=display,
    )

    await app.run()

    assert display.clear_calls == 2
    assert output.values == []


async def test_tool_budget_reports_schemas_selected_for_real_turn(
    production_runtime: FridayRuntime,
) -> None:
    production_runtime.chat_llm = FakeChatModel(model="gate-a-deterministic-chat")
    production_runtime.memory = FakeMemoryController()
    turn = await TurnProcessor(production_runtime).process(
        "echo this production-shaped tool selection"
    )
    assert turn.tool_schema_tokens > 0

    result = await _execute(production_runtime, "/tool-budget")

    assert "echo" in result
    assert str(turn.tool_schema_tokens) in result


async def test_meta_dispatches_seeded_real_adapter_record(
    production_runtime: FridayRuntime,
) -> None:
    assert isinstance(production_runtime.memory, FrameworkMemoryAdapter)
    seeded = await production_runtime.memory.collection_manager.add_to_short_term(
        ["Synthetic meta insight from retained Gate A control."],
        [
            {
                "type": "meta_insight",
                "source_memories": json.dumps(["source-1", "source-2"]),
                "source_count": 2,
                "provenance_source_type": "synthesis",
                "confidence": 0.8,
                "verified": True,
            }
        ],
        ids=["gate-a-meta-insight"],
    )
    assert seeded is True

    result = await _execute(production_runtime, "/meta")

    assert "Meta insights:" in result
    assert "Synthetic meta insight from retained Gate A control." in result


async def _execute(runtime: FridayRuntime, command: str) -> str:
    registry = build_default_registry()
    handled, result = await registry.execute(
        command,
        RegistryCommandContext(runtime=runtime, registry=registry),
    )
    assert handled is True
    assert result is not None
    output = result.output
    if not isinstance(output, str):
        raise TypeError("command result output must be text")
    return output


async def _seed_transcript_session(
    runtime: FridayRuntime,
    *,
    session_id: str,
    user_message: str,
    assistant_message: str,
) -> None:
    assert isinstance(runtime.transcript, FrameworkTranscriptAdapter)
    store = runtime.transcript.store
    assert await store.create_session(
        TranscriptSession(
            session_id=session_id,
            model_name="gate-a-deterministic-chat",
        )
    )
    assert await store.append_entry(
        TranscriptEntry(
            id=f"entry-{session_id}",
            session_id=session_id,
            turn_number=1,
            user_message=user_message,
            assistant_message=assistant_message,
        )
    )


def _assert_disposable_layout(runtime: FridayRuntime, tmp_path: Path) -> None:
    for path in runtime.maintenance_layout.all_declared_paths:
        _assert_disposable_path(path, tmp_path)


def _assert_disposable_path(path: Path, tmp_path: Path) -> None:
    candidate = path.resolve(strict=False)
    disposable_root = tmp_path.resolve(strict=False)
    assert candidate.is_relative_to(disposable_root), candidate
    for active_root in ACTIVE_STATE_ROOTS:
        resolved_active_root = active_root.parent.resolve(strict=False) / active_root.name
        assert not candidate.is_relative_to(resolved_active_root), candidate


def _embedding_for(text: str) -> list[float]:
    return [
        float(len(text)),
        float(len(text.split())),
        float(sum(ord(character) for character in text) % 997),
    ]
