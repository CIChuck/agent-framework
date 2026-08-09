"""Gate B coverage for Friday Chat session identity composition."""

from __future__ import annotations

import asyncio
import socket
from collections.abc import AsyncIterator
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from friday_chat.adapters import (
    FrameworkMaintenanceAdapter,
    FrameworkMemoryAdapter,
    FrameworkTranscriptAdapter,
)
from friday_chat.app import FridayChatApp, ListInputSource
from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.config import FridayChatConfig
from friday_chat.replay import ReplayService
from friday_chat.runtime import build_runtime
from friday_chat.session import (
    FridaySession,
    SessionIdentity,
    SessionIdentityMismatchError,
)
from friday_chat.turns.models import InteractionTurn, TurnMetrics
from friday_llm import LiteLLMEmbeddingService, LiteLLMService


def _config(data: dict[str, object] | None = None) -> FridayChatConfig:
    return FridayChatConfig.model_validate(
        data or {"llm": {"model": "fake/test-chat-model"}}
    )


def _production_config(tmp_path: Path) -> FridayChatConfig:
    state_root = tmp_path / "state"
    return _config(
        {
            "llm": {"model": "openai/test-chat-model"},
            "embedding": {"model": "openai/test-embedding-model"},
            "memory": {"persist_directory": str(state_root / "vector")},
            "transcript": {
                "export_directory": str(state_root / "transcripts"),
            },
            "maintenance": {
                "backup_directory": str(state_root / "recovery"),
                "logging": {"log_directory": str(state_root / "logs")},
            },
            "tools": {"enabled": False, "registry": []},
        }
    )


def _prohibit_transports(monkeypatch: pytest.MonkeyPatch) -> None:
    async def reject_provider_call(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("provider transport is prohibited in identity tests")

    async def reject_provider_stream(
        *_args: object,
        **_kwargs: object,
    ) -> AsyncIterator[str]:
        raise AssertionError("provider transport is prohibited in identity tests")
        yield ""  # pragma: no cover - preserves the async-iterator contract

    def reject_network_call(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("network access is prohibited in identity tests")

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


def test_runtime_generates_one_immutable_unique_identity_per_build() -> None:
    first = build_runtime(_config()).session_identity
    second = build_runtime(_config()).session_identity

    assert first.value.startswith("session_")
    assert second.value.startswith("session_")
    assert first != second
    identity_attribute = "value"
    with pytest.raises(FrozenInstanceError):
        setattr(first, identity_attribute, "replacement")


def test_injected_identity_is_shared_by_runtime_app_commands_and_replay() -> None:
    identity = SessionIdentity("deterministic-session")
    runtime = build_runtime(_config(), session_identity=identity)
    app = FridayChatApp(runtime=runtime, input_source=ListInputSource([]))
    context = RegistryCommandContext(
        runtime=runtime,
        registry=build_default_registry(),
    )
    replay = ReplayService(runtime=runtime, session_identity=identity)

    assert runtime.session_identity is identity
    assert app.session.identity is identity
    assert app.session.session_id == identity.value
    assert app.command_context.session_identity is identity
    assert context.session_identity is identity
    assert replay.runtime.session_identity is identity


def test_composition_rejects_every_injected_identity_disagreement() -> None:
    runtime_identity = SessionIdentity("runtime-session")
    runtime = build_runtime(_config(), session_identity=runtime_identity)
    same_value_session = FridaySession(
        session_id=runtime_identity.value,
        user_id="User",
    )
    FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource([]),
        session=same_value_session,
    )

    assert same_value_session.identity is runtime_identity

    with pytest.raises(SessionIdentityMismatchError):
        build_runtime(
            _config(),
            session_identity=runtime_identity,
            session_id="different-session",
        )
    with pytest.raises(SessionIdentityMismatchError):
        FridayChatApp(
            runtime=runtime,
            input_source=ListInputSource([]),
            session=FridaySession(
                session_id="different-session",
                user_id="User",
            ),
        )
    with pytest.raises(SessionIdentityMismatchError):
        ReplayService(
            runtime=runtime,
            session_identity=SessionIdentity("different-session"),
        )


async def test_framework_identity_reaches_adapters_and_lazy_persistence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _prohibit_transports(monkeypatch)
    monkeypatch.chdir(tmp_path)
    identity = SessionIdentity("production-session")
    runtime = build_runtime(
        _production_config(tmp_path),
        fake=False,
        session_identity=identity,
    )

    assert isinstance(runtime.memory, FrameworkMemoryAdapter)
    assert isinstance(runtime.transcript, FrameworkTranscriptAdapter)
    assert isinstance(runtime.maintenance, FrameworkMaintenanceAdapter)
    assert runtime.memory.session_id == identity.value
    assert runtime.transcript.session_id == identity.value
    assert runtime.maintenance.session_id == identity.value
    assert runtime.session_identity is identity
    for path in (
        runtime.maintenance_layout.vector_directory,
        runtime.maintenance_layout.graph_path,
        runtime.maintenance_layout.transcript_database_path,
        runtime.maintenance_layout.recovery_root,
        runtime.maintenance_layout.log_root,
    ):
        assert path.resolve(strict=False).is_relative_to(tmp_path.resolve())

    assert await runtime.transcript.store.get_session(identity.value) is None
    await runtime.transcript.record_interaction(
        InteractionTurn(
            turn_id="identity-turn",
            user_message="user marker",
            assistant_message="assistant marker",
            prompt="prompt marker",
            context="",
            memory_snippets=(),
            metrics=TurnMetrics(
                retrieval_seconds=0.0,
                llm_seconds=0.0,
                persistence_seconds=0.0,
                total_seconds=0.0,
            ),
        )
    )

    persisted = await runtime.transcript.store.get_session(identity.value)
    assert persisted is not None
    assert persisted.session_id == identity.value
    assert await runtime.transcript.store.count_entries(identity.value) == 1
