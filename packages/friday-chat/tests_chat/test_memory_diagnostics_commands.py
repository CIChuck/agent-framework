"""Gate D memory diagnostics against typed fake and disposable real adapters."""

from __future__ import annotations

import asyncio
import json
import socket
from collections.abc import AsyncIterator, Iterator
from datetime import datetime, timezone
from pathlib import Path

import pytest
from friday_chat import adapters
from friday_chat.adapters import FrameworkEmbeddingService, FrameworkMemoryAdapter
from friday_chat.app import FridayChatApp, ListInputSource, ListOutputSink
from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.config import FridayChatConfig
from friday_chat.memory_views import (
    MemoryDiagnosticReason,
    MemoryMetric,
    MemoryMetricState,
    MemoryRecordKind,
)
from friday_chat.runtime import FakeMemoryController, FridayRuntime, build_runtime
from friday_chat.session import FridaySession
from friday_llm import LiteLLMEmbeddingService, LiteLLMService
from friday_memory import (
    GraphEdge,
    GraphNode,
    MemoryVectorAddition,
    ProvenanceMetadata,
)
from friday_memory.models.budget import BudgetSeverity, BudgetStatus
from friday_transcript import TranscriptEntry, TranscriptSession

SESSION_ID = "gate-d-current-session"
REPOSITORY_ROOT = Path(__file__).resolve(strict=False).parents[3]
ACTIVE_STATE_ROOTS = (
    REPOSITORY_ROOT / ".friday",
    Path.home().resolve(strict=False) / ".friday",
)


class DeterministicEmbeddingBackend(LiteLLMEmbeddingService):
    """Provider-free embedding backend used behind the framework adapter."""

    def __init__(self) -> None:
        """Avoid constructing a provider transport."""

    async def embed_query(self, text: str) -> list[float]:
        return _embedding_for(text)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [_embedding_for(text) for text in texts]


class SliceOnlyLineage(list[str]):
    """List probe that rejects iteration over the unbounded original value."""

    def __iter__(self) -> Iterator[str]:
        raise AssertionError("unbounded source lineage iteration is prohibited")


@pytest.fixture(autouse=True)
def prohibit_provider_and_network_transports(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fail before any provider or network transport can be reached."""

    async def reject_provider_call(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("provider transport is prohibited in Gate D tests")

    async def reject_provider_stream(
        *_args: object,
        **_kwargs: object,
    ) -> AsyncIterator[str]:
        raise AssertionError("provider transport is prohibited in Gate D tests")
        yield ""  # pragma: no cover - preserves the async-iterator contract

    def reject_network_call(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("network access is prohibited in Gate D tests")

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
) -> FridayRuntime:
    """Build lifecycle-enabled real adapters entirely below a disposable root."""
    state_root = tmp_path / "gate-d-state"
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
                "model": "openai/gate-d-test-chat",
                "api_key": "provider-prohibited",
            },
            "embedding": {
                "model": "openai/gate-d-test-embedding",
                "api_key": "provider-prohibited",
            },
            "memory": {
                "persist_directory": str(state_root / "vector"),
                "context_window": 4096,
                "output_buffer": 512,
                "priming": {"enabled": True, "previous_sessions": 2},
            },
            "transcript": {"export_directory": str(state_root / "transcript")},
            "maintenance": {
                "backup_directory": str(state_root / "recovery"),
                "logging": {"log_directory": str(state_root / "logs")},
            },
            "lifecycle": {
                "enabled": True,
                "access_buffer": {
                    "enabled": True,
                    "wal_path": str(state_root / "access-buffer.wal"),
                },
            },
            "tools": {"enabled": False},
        }
    )
    runtime = build_runtime(config, fake=False, session_id=SESSION_ID)
    assert isinstance(runtime.memory, FrameworkMemoryAdapter)
    disposable_root = tmp_path.resolve(strict=True)
    for path in runtime.maintenance_layout.all_declared_paths:
        candidate = path.resolve(strict=False)
        candidate.relative_to(disposable_root)
        for active_root in ACTIVE_STATE_ROOTS:
            resolved_active = active_root.parent.resolve(strict=False) / active_root.name
            assert not candidate.is_relative_to(resolved_active), candidate
    return runtime


def test_memory_metric_preserves_zero_unavailable_and_not_configured() -> None:
    zero = MemoryMetric.available(0)
    unavailable: MemoryMetric[int] = MemoryMetric.unavailable(
        MemoryDiagnosticReason.STORE_READ_FAILED
    )
    not_configured: MemoryMetric[int] = MemoryMetric.not_configured()

    assert zero.state is MemoryMetricState.AVAILABLE
    assert zero.value == 0
    assert unavailable.state is MemoryMetricState.UNAVAILABLE
    assert unavailable.value is None
    assert not_configured.state is MemoryMetricState.NOT_CONFIGURED
    assert not_configured.value is None
    with pytest.raises(ValueError, match="requires only a value"):
        MemoryMetric[int](state=MemoryMetricState.AVAILABLE)


async def test_command_boundary_renders_at_most_one_hundred_typed_records(
    tmp_path: Path,
) -> None:
    runtime = build_runtime(
        FridayChatConfig.model_validate(
            {
                "llm": {"model": "fake/gate-d"},
                "transcript": {"export_directory": str(tmp_path / "exports")},
            }
        )
    )
    assert isinstance(runtime.memory, FakeMemoryController)
    runtime.memory.insights = [
        {"id": f"bounded-{index:03d}", "text": f"bounded-record-{index:03d}"}
        for index in range(105)
    ]

    output = await _execute(runtime, "/insights")

    rendered = [line for line in output.splitlines() if line.startswith("- bounded")]
    assert len(rendered) == 100
    assert "- bounded-record-099" in rendered
    assert "bounded-record-100" not in output


async def test_memory_reports_exact_seeded_public_store_and_context_values(
    production_runtime: FridayRuntime,
) -> None:
    memory = _framework_memory(production_runtime)
    await memory.store_turn("episodic user", "episodic assistant")
    assert await memory.collection_manager.add_to_short_term(
        ["short record", "long record", "decayed record"],
        [{"type": "insight"}, {"type": "insight"}, {"type": "insight"}],
        ids=["short-record", "long-record", "decayed-record"],
    )
    assert await memory.collection_manager.promote_memory("long-record")
    assert await memory.collection_manager.promote_memory("decayed-record")
    assert await memory.collection_manager.demote_to_decayed("decayed-record")

    provenance = ProvenanceMetadata(source_id="gate-d", source_type="interaction")
    assert await memory.graph_store.add_node(
        GraphNode(id="node-a", type="Entity", label="Node A", provenance=provenance)
    )
    assert await memory.graph_store.add_node(
        GraphNode(id="node-b", type="Entity", label="Node B", provenance=provenance)
    )
    assert await memory.graph_store.add_edge(
        GraphEdge(
            source_id="node-a",
            target_id="node-b",
            relation="related_to",
            provenance=provenance,
        )
    )
    assert memory.access_buffer is not None
    await memory.access_buffer.record_access("short-record", "short_term")
    await memory.access_buffer.record_access("short-record", "short_term")
    await _seed_transcript(production_runtime)

    session = FridaySession(session_id=SESSION_ID, user_id="Gate D")
    session.turn_ids.extend(["turn-a", "turn-b"])
    context = RegistryCommandContext(
        runtime=production_runtime,
        registry=build_default_registry(),
        session=session,
        history=[("user", "assistant")],
        variables={"scope": "value"},
        last_budget_status=BudgetStatus(
            total_tokens=120,
            message_tokens=90,
            tool_tokens=30,
            available_budget=600,
            utilization_pct=20.0,
            severity=BudgetSeverity.NORMAL,
        ),
    )

    output = await _execute(production_runtime, "/memory", context=context)

    assert "- episodic_current_session_turns: 1" in output
    assert "- short_term: 1" in output
    assert "- long_term: 1" in output
    assert "- decayed: 1" in output
    assert "- active_total: 2" in output
    assert "- total: 3" in output
    assert "Graph:\n- nodes: 2\n- relationships: 1" in output
    assert "- current_session_entries: 1" in output
    assert "- access_buffer_entries: 1" in output
    assert "- access_buffer_accesses: 2" in output
    assert "Priming:\n- enabled: true\n- previous_sessions: 2" in output
    assert "- in_process_turns: 1" in output
    assert "- tracked_turn_ids: 2" in output
    assert "- scoped_variables: 1" in output
    assert "- total_tokens: 120" in output
    assert "- message_tokens: 90" in output
    assert "- tool_schema_tokens: 30" in output
    assert "- available_budget: 600" in output
    assert "- utilization: 20.0%" in output
    assert "- severity: normal" in output


async def test_meta_reads_inherited_synthesis_shape_across_active_collections(
    production_runtime: FridayRuntime,
) -> None:
    memory = _framework_memory(production_runtime)
    short_addition = _synthesis_addition(
        memory_id="meta-short",
        document="Short-term synthesized meta insight.",
    )
    long_addition = _synthesis_addition(
        memory_id="meta-long",
        document="Long-term synthesized meta insight.",
    )
    decayed_addition = _synthesis_addition(
        memory_id="meta-decayed",
        document="Decayed synthesized meta insight must remain hidden.",
    )
    for addition in (short_addition, long_addition, decayed_addition):
        await _seed_synthesis_addition(memory, addition)
    assert await memory.collection_manager.promote_memory(long_addition.memory_id)
    assert await memory.collection_manager.promote_memory(decayed_addition.memory_id)
    assert await memory.collection_manager.demote_to_decayed(
        decayed_addition.memory_id
    )

    output = await _execute(production_runtime, "/meta")

    assert short_addition.document in output
    assert long_addition.document in output
    assert decayed_addition.document not in output
    assert "collection=short_term" in output
    assert "collection=long_term" in output
    assert "stage=short_term" in output
    assert "stage=long_term" in output
    assert "confidence=0.875" in output
    assert "source_count=2" in output
    assert "provenance=synthesis" in output
    assert "source_ids=source-a, source-b" in output
    assert "verification=verified (0.900)" in output
    assert "created=" in output
    assert "Decayed records: excluded" in output


async def test_meta_empty_state_is_actionable_and_read_only(
    production_runtime: FridayRuntime,
) -> None:
    memory = _framework_memory(production_runtime)
    before = await memory.collection_manager.get_stats()

    output = await _execute(production_runtime, "/meta")

    after = await memory.collection_manager.get_stats()
    assert output.startswith(
        "No meta insights found. Run /reorganize --full --execute with synthesis enabled,"
    )
    assert "or use /help reorganize to inspect available modes." in output
    assert "Decayed records: excluded" in output
    assert after == before


async def test_memory_partial_count_failure_retains_other_real_values(
    production_runtime: FridayRuntime,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    memory = _framework_memory(production_runtime)
    assert await memory.collection_manager.add_to_short_term(
        ["long record"],
        [{"type": "insight"}],
        ids=["long-record"],
    )
    assert await memory.collection_manager.promote_memory("long-record")

    async def fail_count() -> int:
        raise RuntimeError("secret path /private/store")

    monkeypatch.setattr(memory.collection_manager.short_term, "count", fail_count)

    output = await _execute(production_runtime, "/memory")

    assert "- short_term: unavailable (store read failed)" in output
    assert "- long_term: 1" in output
    assert "- active_total: unavailable (store read failed)" in output
    assert "- vector short-term: store read failed" in output
    assert "secret path" not in output
    assert "/private/store" not in output


async def test_meta_partial_failure_returns_records_and_sanitized_warning(
    production_runtime: FridayRuntime,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    memory = _framework_memory(production_runtime)
    addition = _synthesis_addition(
        memory_id="meta-long",
        document="Visible record from the available long-term store.",
    )
    await _seed_synthesis_addition(memory, addition)
    assert await memory.collection_manager.promote_memory(addition.memory_id)

    async def fail_query(
        *,
        limit: int | None = None,
        where: dict[str, object] | None = None,
    ) -> list[dict[str, object]]:
        del limit, where
        raise RuntimeError("raw database path /private/secret.sqlite")

    monkeypatch.setattr(
        memory.collection_manager.short_term,
        "get_all",
        fail_query,
    )

    output = await _execute(production_runtime, "/meta")

    assert addition.document in output
    assert "Warnings:\n- vector short-term: store read failed" in output
    assert "raw database path" not in output
    assert "/private/secret.sqlite" not in output


async def test_meta_omits_oversized_scalar_lineage_before_json_parsing(
    production_runtime: FridayRuntime,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    memory = _framework_memory(production_runtime)
    oversized_characters = json.dumps(["x" * 33_000], separators=(",", ":"))
    oversized_bytes = json.dumps(
        ["😀" * 9_000],
        ensure_ascii=False,
        separators=(",", ":"),
    )

    async def raw_short_records(
        *,
        limit: int | None = None,
        where: dict[str, object] | None = None,
    ) -> list[dict[str, object]]:
        del limit, where
        return [
            {
                "id": "oversized-characters",
                "text": "Oversized character lineage.",
                "metadata": {
                    "type": "meta_insight",
                    "source_count": 33_000,
                    "source_memories": oversized_characters,
                },
            },
            {
                "id": "oversized-bytes",
                "text": "Oversized byte lineage.",
                "metadata": {
                    "type": "meta_insight",
                    "source_count": 9_000,
                    "source_memories": oversized_bytes,
                },
            },
        ]

    async def no_long_records(
        *,
        limit: int | None = None,
        where: dict[str, object] | None = None,
    ) -> list[dict[str, object]]:
        del limit, where
        return []

    def reject_json_loads(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("oversized lineage must be rejected before JSON parsing")

    monkeypatch.setattr(memory.collection_manager.short_term, "get_all", raw_short_records)
    monkeypatch.setattr(memory.collection_manager.long_term, "get_all", no_long_records)
    monkeypatch.setattr(adapters.json, "loads", reject_json_loads)

    output = await _execute(production_runtime, "/meta")

    assert "Oversized character lineage." in output
    assert "Oversized byte lineage." in output
    assert "source_count=33000" in output
    assert "source_count=9000" in output
    assert output.count("source_ids=unavailable") == 2
    assert "😀" not in output


async def test_meta_inspects_only_bounded_prefix_of_oversized_decoded_lineage(
    production_runtime: FridayRuntime,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    memory = _framework_memory(production_runtime)
    lineage = SliceOnlyLineage([f"source-{index:03d}" for index in range(1_000)])

    async def raw_short_records(
        *,
        limit: int | None = None,
        where: dict[str, object] | None = None,
    ) -> list[dict[str, object]]:
        del limit, where
        return [
            {
                "id": "oversized-decoded-list",
                "text": "Oversized decoded lineage remains bounded.",
                "metadata": {
                    "type": "meta_insight",
                    "source_count": 1_000,
                    "source_memories": lineage,
                },
            }
        ]

    async def no_long_records(
        *,
        limit: int | None = None,
        where: dict[str, object] | None = None,
    ) -> list[dict[str, object]]:
        del limit, where
        return []

    monkeypatch.setattr(memory.collection_manager.short_term, "get_all", raw_short_records)
    monkeypatch.setattr(memory.collection_manager.long_term, "get_all", no_long_records)

    output = await _execute(production_runtime, "/meta")

    assert "source_count=1000" in output
    assert (
        "source_ids=source-000, source-001, source-002, source-003, "
        "source-004, source-005, source-006, source-007, ..."
    ) in output
    assert "source-008" not in output


async def test_app_retains_typed_budget_and_exposes_last_context_metrics(
    tmp_path: Path,
) -> None:
    runtime = build_runtime(
        FridayChatConfig.model_validate(
            {
                "llm": {"model": "fake/gate-d"},
                "memory": {"context_window": 1000, "output_buffer": 100},
                "transcript": {"export_directory": str(tmp_path / "exports")},
                "session": {"lifecycle_on_exit": False},
            }
        ),
        session_id="gate-d-app-session",
    )
    output = ListOutputSink()
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource(["hello", "/memory"]),
        output_sink=output,
    )

    await app.run()

    assert isinstance(app.command_context.last_budget_status, BudgetStatus)
    memory_output = next(value for value in output.values if value.startswith("Memory"))
    assert "- in_process_turns: 1" in memory_output
    assert "- tracked_turn_ids: 1" in memory_output
    assert "- episodic_current_session_turns: 1" in memory_output
    assert "- current_session_entries: 1" in memory_output
    assert "- total_tokens: unavailable" not in memory_output
    assert "- severity: normal" in memory_output


async def test_memory_sanitizes_untrusted_session_identity(tmp_path: Path) -> None:
    session_id = "gate-d\x1b[31m\ninjected-session"
    runtime = build_runtime(
        FridayChatConfig.model_validate(
            {
                "llm": {"model": "fake/gate-d"},
                "transcript": {"export_directory": str(tmp_path / "exports")},
            }
        ),
        session_id=session_id,
    )

    output = await _execute(runtime, "/memory")

    assert session_id not in output
    assert "\x1b" not in output
    assert "- session_id: gate-d [31m injected-session" in output


async def _execute(
    runtime: FridayRuntime,
    command: str,
    *,
    context: RegistryCommandContext | None = None,
) -> str:
    registry = context.registry if context is not None else build_default_registry()
    resolved_context = context or RegistryCommandContext(
        runtime=runtime,
        registry=registry,
    )
    handled, result = await registry.execute(command, resolved_context)
    assert handled is True
    assert result is not None
    if not isinstance(result.output, str):
        raise TypeError("command result output must be text")
    return result.output


def _framework_memory(runtime: FridayRuntime) -> FrameworkMemoryAdapter:
    if not isinstance(runtime.memory, FrameworkMemoryAdapter):
        raise TypeError("test requires FrameworkMemoryAdapter")
    return runtime.memory


async def _seed_transcript(runtime: FridayRuntime) -> None:
    store = runtime.transcript
    if not isinstance(store, adapters.FrameworkTranscriptAdapter):
        raise TypeError("test requires FrameworkTranscriptAdapter")
    assert await store.store.create_session(
        TranscriptSession(session_id=SESSION_ID, model_name="gate-d-test-chat")
    )
    assert await store.store.append_entry(
        TranscriptEntry(
            id="gate-d-entry",
            session_id=SESSION_ID,
            turn_number=1,
            user_message="transcript user",
            assistant_message="transcript assistant",
        )
    )


def _synthesis_addition(*, memory_id: str, document: str) -> MemoryVectorAddition:
    return MemoryVectorAddition(
        collection="memories_short_term",
        memory_id=memory_id,
        document=document,
        embedding=(0.25, 0.75),
        source_memory_ids=("source-a", "source-b"),
        topic="diagnostics",
        confidence=0.9,
        reasoning="Two diagnostic sources support this meta insight",
        synthesis_fingerprint="b" * 64,
        synthesis_version="1",
        created_at=datetime.now(timezone.utc),
    )


async def _seed_synthesis_addition(
    memory: FrameworkMemoryAdapter,
    addition: MemoryVectorAddition,
) -> None:
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


def _embedding_for(text: str) -> list[float]:
    checksum = sum(text.encode("utf-8"))
    return [float(checksum % 101) / 101.0, float((checksum * 7) % 103) / 103.0]


def test_memory_record_kind_is_closed() -> None:
    assert tuple(kind.value for kind in MemoryRecordKind) == (
        "insight",
        "summary",
        "meta_insight",
    )
