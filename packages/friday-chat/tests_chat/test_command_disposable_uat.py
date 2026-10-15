"""Provider-free Gate F command UAT through real Friday Chat boundaries."""

from __future__ import annotations

import asyncio
import json
import os
import re
import socket
import threading
from collections.abc import AsyncIterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import pytest
import yaml
from friday_chat import adapters
from friday_chat import display as display_module
from friday_chat.adapters import (
    FrameworkEmbeddingService,
    FrameworkMemoryAdapter,
    FrameworkToolRegistryAdapter,
    FrameworkTranscriptAdapter,
)
from friday_chat.app import FridayChatApp
from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.config import FridayChatConfig
from friday_chat.display import (
    BannerDisplayConfig,
    FridayCliDisplay,
    FridayCliInputSource,
    FridayCliOutputSink,
    Heartbeat,
    HeartbeatKind,
)
from friday_chat.runtime import FridayRuntime, build_runtime
from friday_chat.tools.schemas import ToolDefinition
from friday_chat.tools.selection import (
    ToolSelectionMode,
    canonical_tool_schema_bytes,
)
from friday_chat.turns.models import ChatModelResponse
from friday_chat.turns.processor import TurnProcessor
from friday_cli import CLIConfig
from friday_llm import LiteLLMEmbeddingService, LiteLLMService
from friday_memory import (
    GraphEdge,
    GraphNode,
    MemoryVectorAddition,
    ProvenanceMetadata,
)
from friday_transcript import TranscriptEntry, TranscriptSession
from rich.console import Console

CURRENT_SESSION_ID = "uat-current-session"
SEEDED_SESSION_ID = "uat-seeded-session"
REPOSITORY_ROOT = Path(__file__).resolve(strict=False).parents[3]
EXAMPLE_CONFIG = (
    REPOSITORY_ROOT
    / "packages/friday-chat/config.example.yaml"
)
ACTIVE_STATE_ROOTS = (
    REPOSITORY_ROOT / ".friday",
    Path.home().resolve(strict=False) / ".friday",
)


class DeterministicEmbeddingBackend(LiteLLMEmbeddingService):
    """In-process embeddings without constructing provider transport state."""

    def __init__(self) -> None:
        """Intentionally avoid the provider-backed superclass constructor."""

    async def embed_query(self, text: str) -> list[float]:
        return _embedding_for(text)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [_embedding_for(text) for text in texts]


@dataclass
class SchemaRecordingChatModel:
    """Deterministic chat double recording the exact schema payload."""

    tool_payloads: list[tuple[ToolDefinition, ...]] = field(default_factory=list)

    async def complete(
        self,
        _messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> ChatModelResponse:
        self.tool_payloads.append(tuple(tools))
        return ChatModelResponse.from_text("deterministic UAT response")

    async def stream_complete(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> AsyncIterator[str]:
        response = await self.complete(messages, tools=tools)
        yield response.content


class NoopHeartbeat:
    """Provider-free heartbeat for a scripted CLI session."""

    def start(self) -> None:
        return None

    def stop(self) -> None:
        return None


@dataclass
class RecordingPtyDisplay:
    """Record typed effects while delegating clears to the real CLI display."""

    inner: FridayCliDisplay
    clear_calls: int = 0

    def render_banner(self, *, assistant_name: str, version: str) -> None:
        self.inner.render_banner(assistant_name=assistant_name, version=version)

    def prompt_text(self, *, user_name: str) -> str:
        prompt = self.inner.prompt_text(user_name=user_name)
        if not isinstance(prompt, str):
            raise TypeError("CLI display prompt must be text")
        return prompt

    def create_heartbeat(self, _kind: HeartbeatKind) -> Heartbeat:
        return NoopHeartbeat()

    def clear_screen(self) -> None:
        self.clear_calls += 1
        self.inner.clear_screen()


@dataclass
class ScriptedPrompt:
    """Deterministic prompt callable used through the production CLI input adapter."""

    values: tuple[str, ...]
    prompts: list[str] = field(default_factory=list)
    index: int = 0

    async def __call__(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if self.index >= len(self.values):
            raise EOFError
        value = self.values[self.index]
        self.index += 1
        return value


@pytest.fixture(autouse=True)
def prohibit_provider_and_network_transports(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fail closed before any provider or network transport can run."""

    async def reject_provider_call(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("provider transport is prohibited in Gate F UAT")

    async def reject_provider_stream(
        *_args: object,
        **_kwargs: object,
    ) -> AsyncIterator[str]:
        raise AssertionError("provider transport is prohibited in Gate F UAT")
        yield ""  # pragma: no cover - preserves the async-iterator contract

    def reject_network_call(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("network access is prohibited in Gate F UAT")

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


async def test_real_app_cli_pty_command_uat_is_contained_and_provider_free(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    prohibit_provider_and_network_transports: None,
) -> None:
    """Exercise the exact Gate F slash-command sequence through real adapters."""
    if os.name != "posix":
        pytest.skip("PTY command UAT requires a POSIX platform")

    state_root = tmp_path / "friday-chat-command-uat"
    state_root.mkdir()
    monkeypatch.chdir(state_root)
    config = _config_derived_from_example(state_root)
    _assert_contained_config_paths(config, state_root)
    monkeypatch.setattr(
        adapters,
        "build_framework_embedding_service",
        lambda _config: FrameworkEmbeddingService(
            service=DeterministicEmbeddingBackend()
        ),
    )
    runtime = build_runtime(config, fake=False, session_id=CURRENT_SESSION_ID)
    _assert_contained_runtime(runtime, state_root)
    memory = _framework_memory(runtime)
    transcript = _framework_transcript(runtime)
    tools = _framework_tools(runtime)

    await _seed_transcript(
        transcript,
        session_id=CURRENT_SESSION_ID,
        user_message="current transcript UAT marker",
        assistant_message="current assistant UAT marker",
    )
    await _seed_transcript(
        transcript,
        session_id=SEEDED_SESSION_ID,
        user_message="selected transcript UAT marker",
        assistant_message="selected assistant UAT marker",
    )
    await _seed_memory(memory)

    model = SchemaRecordingChatModel()
    runtime.chat_llm = model
    automatic_turn = await TurnProcessor(runtime).process(
        "echo this deterministic schema selection"
    )
    assert automatic_turn.selected_tool_names == ("echo",)
    assert automatic_turn.tool_budget_snapshot is not None
    assert model.tool_payloads == [(tools.definitions[0],)]
    assert automatic_turn.tool_budget_snapshot.schema_bytes == (
        canonical_tool_schema_bytes(model.tool_payloads[0])
    )
    assert tools.calls == []

    commands = (
        "/sessions",
        "/transcript",
        f"/transcript {SEEDED_SESSION_ID}",
        "/memory",
        "/meta",
        "/tools",
        "/tool-budget",
        "/inject-tools echo",
        "/tool-budget",
        "/clear-tools",
        "/cls",
        "/clearscreen",
        "/q",
    )
    scripted_prompt = ScriptedPrompt(commands)
    master_fd, slave_fd = os.openpty()
    pty_chunks: list[bytes] = []
    reader = threading.Thread(
        target=_drain_pty,
        args=(master_fd, pty_chunks),
        daemon=True,
        name="friday-chat-uat-pty-reader",
    )
    try:
        with os.fdopen(slave_fd, "w", encoding="utf-8", closefd=True) as slave:
            console = Console(
                file=slave,
                force_terminal=True,
                color_system=None,
                width=240,
            )
            monkeypatch.setattr(display_module, "get_console", lambda: console)
            cli_display = FridayCliDisplay(
                config=CLIConfig.defaults(),
                banner=BannerDisplayConfig(enabled=False),
            )
            recording_display = RecordingPtyDisplay(cli_display)
            app = FridayChatApp(
                runtime=runtime,
                input_source=FridayCliInputSource(
                    recording_display.prompt_text(
                        user_name=config.chat.user_name,
                    ),
                    prompt_fn=scripted_prompt,
                ),
                output_sink=FridayCliOutputSink(),
                display=recording_display,
            )

            reader.start()
            result = await app.run()
            console.file.flush()
        reader.join(timeout=5.0)
        assert not reader.is_alive(), "PTY reader did not observe slave closure"
        pty_bytes = b"".join(pty_chunks)
    finally:
        os.close(master_fd)

    output = _strip_ansi(pty_bytes.decode("utf-8", errors="replace"))
    assert result.exit_reason == "command_exit"
    assert result.turns_processed == 0
    assert scripted_prompt.index == len(commands)
    assert scripted_prompt.prompts == [f"{config.chat.user_name}: "] * len(commands)
    assert recording_display.clear_calls == 2
    assert pty_bytes.count(b"\x1b[2J") == 2
    assert pty_bytes.count(b"\x1b[H") >= 2

    assert f"- {CURRENT_SESSION_ID} (2 turns) [current]" in output
    assert f"- {SEEDED_SESSION_ID} (1 turns) [primed]" in output
    assert f"Transcript: {CURRENT_SESSION_ID}" in output
    assert "current transcript UAT marker" in output
    assert f"Transcript: {SEEDED_SESSION_ID}" in output
    assert "selected transcript UAT marker" in output
    assert f"- session_id: {CURRENT_SESSION_ID}" in output
    assert "- episodic_current_session_turns: 2" in output
    assert "- short_term: 2" in output
    assert "- long_term: 1" in output
    assert "- decayed: 0" in output
    assert "- nodes: 2" in output
    assert "- relationships: 1" in output
    assert "Gate F synthesized meta insight." in output
    assert "provenance=synthesis" in output
    assert "Decayed records: excluded" in output
    assert "echo" in output
    assert "estimate_source: last_automatic" in output
    assert "estimate_source: pending_manual" in output
    assert "Injected tools:" in output
    assert "Cleared injected tools." in output

    assert runtime.session_identity.value == CURRENT_SESSION_ID
    assert app.session.identity == runtime.session_identity
    assert app.command_context.session_identity == runtime.session_identity
    assert runtime.tool_selection.mode is ToolSelectionMode.AUTOMATIC
    assert runtime.tool_selection.manual_names == ()
    assert runtime.tool_selection.last_automatic_snapshot is not None
    assert runtime.tool_selection.last_automatic_snapshot.selected_names == ("echo",)
    post_clear_budget = await _execute(runtime, "/tool-budget")
    assert "mode: automatic" in post_clear_budget
    assert "pending_manual: none" in post_clear_budget
    assert "estimate_source: last_automatic" in post_clear_budget
    assert tools.calls == []


def _config_derived_from_example(state_root: Path) -> FridayChatConfig:
    raw_value = yaml.safe_load(EXAMPLE_CONFIG.read_text(encoding="utf-8"))
    if not isinstance(raw_value, dict):
        raise TypeError("example config must be a mapping")
    raw = cast(dict[str, Any], raw_value)

    raw.pop("model_library", None)
    raw.pop("llm_pool", None)
    raw.pop("embedding_pool", None)
    raw["llm"] = {}
    llm = _section(raw, "llm")
    for typed_key in (
        "generation",
        "transport_target",
        "model_target",
        "provider_options",
    ):
        llm.pop(typed_key, None)
    llm.update(
        {
            "model": "openai/gate-f-provider-prohibited",
            "api_base": "http://provider.invalid/v1",
            "api_key": "gate-f-provider-prohibited",
            "max_retries": 0,
        }
    )
    embedding = _section(raw, "embedding")
    embedding.pop("embedding_service", None)
    embedding.update(
        {
            "model": "openai/gate-f-deterministic-embedding",
            "api_base": "http://provider.invalid/v1",
            "api_key": "gate-f-provider-prohibited",
        }
    )
    extraction = _section(raw, "extraction")
    extraction.pop("llm_service", None)
    extraction.update(
        {
            "interval": -1,
            "api_base": "http://provider.invalid/v1",
            "api_key": "gate-f-provider-prohibited",
            "rejection_log": str(state_root / "logs/extraction-rejections.log"),
        }
    )
    logging = _section(raw, "logging")
    logging["extraction_rejections_file"] = str(
        state_root / "logs/extraction-rejections-compat.log"
    )

    memory = _section(raw, "memory")
    memory["persist_directory"] = str(state_root / "vector")
    memory["context_window"] = 4096
    memory["output_buffer"] = 512
    _section(memory, "passage_router")["enabled"] = False
    _section(memory, "compaction")["enabled"] = False
    _section(memory, "priming")["previous_sessions"] = 2
    _section(raw, "transcript")["export_directory"] = str(
        state_root / "transcripts"
    )

    maintenance = _section(raw, "maintenance")
    maintenance["backup_directory"] = str(state_root / "recovery")
    maintenance["llm"] = {}
    _section(maintenance, "logging")["log_directory"] = str(
        state_root / "logs/reorganization"
    )
    lifecycle = _section(raw, "lifecycle")
    lifecycle["enabled"] = True
    _section(lifecycle, "access_buffer")["wal_path"] = str(
        state_root / "lifecycle/access-buffer.wal"
    )

    tools = _section(raw, "tools")
    tools["enabled"] = True
    tools["registry"] = [
        {
            "name": "echo",
            "module": "friday_tools.utility",
            "class": "EchoTool",
        }
    ]
    _section(tools, "context").update(
        {
            # This fixture replaces the example's native registry with only echo.
            "required_tools": [],
            "include_in_context": True,
            "max_tools": 1,
            "max_budget_ratio": 0.25,
            "recommendation_threshold": 0.5,
        }
    )
    _section(raw, "smart_file")["llm"] = {}
    _section(raw, "langfuse")["enabled"] = False
    _section(raw, "session").update(
        {
            "flush_on_exit": False,
            "lifecycle_on_exit": False,
            "reorganize_on_exit": False,
        }
    )
    speech = _section(raw, "speech")
    speech["enabled"] = False
    _section(_section(speech, "picovoice"), "orca")["model_path"] = str(
        state_root / "speech/orca-model.pv"
    )
    security = _section(_section(raw, "security"), "sanitization")
    _section(security, "storage_policy")["quarantine_path"] = str(
        state_root / "quarantine/tool-outputs.jsonl"
    )
    return FridayChatConfig.model_validate(raw)


async def _seed_transcript(
    transcript: FrameworkTranscriptAdapter,
    *,
    session_id: str,
    user_message: str,
    assistant_message: str,
) -> None:
    assert await transcript.store.create_session(
        TranscriptSession(
            session_id=session_id,
            model_name="gate-f-deterministic-chat",
        )
    )
    assert await transcript.store.append_entry(
        TranscriptEntry(
            id=f"entry-{session_id}",
            session_id=session_id,
            turn_number=1,
            user_message=user_message,
            assistant_message=assistant_message,
        )
    )


async def _seed_memory(memory: FrameworkMemoryAdapter) -> None:
    await memory.store_turn("episodic UAT user", "episodic UAT assistant")
    assert await memory.collection_manager.add_to_short_term(
        ["Gate F short-term insight.", "Gate F long-term insight."],
        [{"type": "insight"}, {"type": "insight"}],
        ids=["uat-short-insight", "uat-long-insight"],
    )
    assert await memory.collection_manager.promote_memory("uat-long-insight")

    addition = MemoryVectorAddition(
        collection="memories_short_term",
        memory_id="uat-meta-insight",
        document="Gate F synthesized meta insight.",
        embedding=(0.25, 0.5, 0.75),
        source_memory_ids=("uat-short-insight", "uat-long-insight"),
        topic="uat",
        confidence=0.875,
        reasoning="Two UAT insights support this meta insight",
        synthesis_fingerprint="a" * 64,
        synthesis_version="1",
        created_at=datetime.now(UTC),
    )
    assert await memory.collection_manager.add_to_short_term(
        [addition.document],
        [
            {
                "type": "meta_insight",
                "source_count": len(addition.source_memory_ids),
                "source_memories": json.dumps(
                    addition.source_memory_ids,
                    ensure_ascii=True,
                    separators=(",", ":"),
                ),
                "provenance_source_type": "synthesis",
                "maintenance_generated": True,
                "confidence": 0.875,
                "verification_status": "verified",
                "verification_confidence": 0.9,
            }
        ],
        ids=[addition.memory_id],
    )

    provenance = ProvenanceMetadata(
        source_id="gate-f-uat",
        source_type="interaction",
    )
    assert await memory.graph_store.add_node(
        GraphNode(
            id="uat-node-a",
            type="Entity",
            label="UAT Node A",
            provenance=provenance,
        )
    )
    assert await memory.graph_store.add_node(
        GraphNode(
            id="uat-node-b",
            type="Entity",
            label="UAT Node B",
            provenance=provenance,
        )
    )
    assert await memory.graph_store.add_edge(
        GraphEdge(
            source_id="uat-node-a",
            target_id="uat-node-b",
            relation="related_to",
            provenance=provenance,
        )
    )
    assert memory.access_buffer is not None
    await memory.access_buffer.record_access("uat-short-insight", "short_term")


async def _execute(runtime: FridayRuntime, command: str) -> str:
    registry = build_default_registry()
    handled, result = await registry.execute(
        command,
        RegistryCommandContext(runtime=runtime, registry=registry),
    )
    assert handled is True
    assert result is not None
    if not isinstance(result.output, str):
        raise TypeError("command result output must be text")
    return result.output


def _section(mapping: dict[str, Any], key: str) -> dict[str, Any]:
    value = mapping.get(key)
    if not isinstance(value, dict):
        raise TypeError(f"example config section {key!r} must be a mapping")
    return cast(dict[str, Any], value)


def _framework_memory(runtime: FridayRuntime) -> FrameworkMemoryAdapter:
    if not isinstance(runtime.memory, FrameworkMemoryAdapter):
        raise TypeError("UAT requires FrameworkMemoryAdapter")
    return runtime.memory


def _framework_transcript(runtime: FridayRuntime) -> FrameworkTranscriptAdapter:
    if not isinstance(runtime.transcript, FrameworkTranscriptAdapter):
        raise TypeError("UAT requires FrameworkTranscriptAdapter")
    return runtime.transcript


def _framework_tools(runtime: FridayRuntime) -> FrameworkToolRegistryAdapter:
    if not isinstance(runtime.tools, FrameworkToolRegistryAdapter):
        raise TypeError("UAT requires FrameworkToolRegistryAdapter")
    return runtime.tools


def _assert_contained_runtime(runtime: FridayRuntime, state_root: Path) -> None:
    resolved_root = state_root.resolve(strict=False)
    declared = runtime.maintenance_layout.all_declared_paths
    assert declared
    for path in declared:
        candidate = path.resolve(strict=False)
        assert candidate.is_relative_to(resolved_root), candidate
        for active_root in ACTIVE_STATE_ROOTS:
            assert not candidate.is_relative_to(active_root.resolve(strict=False))


def _assert_contained_config_paths(
    config: FridayChatConfig,
    state_root: Path,
) -> None:
    maintenance_log = config.maintenance.logging.get("log_directory")
    access_wal = config.lifecycle.access_buffer.get("wal_path")
    storage_policy = config.security.sanitization.get("storage_policy")
    if not isinstance(storage_policy, dict):
        raise TypeError("security storage policy must be a mapping")
    quarantine = storage_policy.get("quarantine_path")
    orca = config.speech.picovoice.get("orca")
    if not isinstance(orca, dict):
        raise TypeError("speech orca config must be a mapping")
    orca_model = orca.get("model_path")
    configured_paths = (
        config.logging.extraction_rejections_file,
        config.extraction.rejection_log,
        config.memory.persist_directory,
        config.transcript.export_directory,
        config.maintenance.backup_directory,
        maintenance_log,
        access_wal,
        quarantine,
        orca_model,
    )
    resolved_root = state_root.resolve(strict=False)
    for value in configured_paths:
        if not isinstance(value, str) or not value:
            raise TypeError("every UAT config path must be a non-empty string")
        candidate = Path(value).resolve(strict=False)
        assert candidate.is_relative_to(resolved_root), candidate
        for active_root in ACTIVE_STATE_ROOTS:
            assert not candidate.is_relative_to(active_root.resolve(strict=False))


def _drain_pty(master_fd: int, chunks: list[bytes]) -> None:
    while True:
        try:
            chunk = os.read(master_fd, 65536)
        except OSError:
            return
        if not chunk:
            return
        chunks.append(chunk)


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text).replace("\r", "")


def _embedding_for(text: str) -> list[float]:
    checksum = sum(text.encode("utf-8"))
    return [
        float(checksum % 101) / 101.0,
        float((checksum * 7) % 103) / 103.0,
        float((checksum * 11) % 107) / 107.0,
    ]
