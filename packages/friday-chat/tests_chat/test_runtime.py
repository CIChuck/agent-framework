"""Runtime factory tests for FridayV2."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, cast

import pytest
from friday_chat.adapters import (
    FrameworkAsyncClientLifecycle,
    FrameworkChatModel,
    FrameworkEmbeddingService,
    FrameworkMaintenanceAdapter,
    FrameworkMemoryAdapter,
    FrameworkToolRegistryAdapter,
    FrameworkTranscriptAdapter,
    FrameworkWorkflowAdapter,
)
from friday_chat.app import FridayChatApp, ListInputSource
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import (
    MAINTENANCE_LLM_ROLES,
    FakeAsyncClientLifecycle,
    FakeChatModel,
    FakeMemoryController,
    FakeSpeechAdapter,
    FakeTranscriptStore,
    PendingExtractionTurn,
    build_runtime,
)
from friday_chat.turns.processor import TurnProcessor
from friday_memory import (
    AccessBuffer,
    ExtractionCommitCompletedUnderCancellation,
    MemoryPromotionService,
    RetrievalFactorComputer,
)
from friday_memory.lifecycle.promotion import PromotionResult
from friday_memory.maintenance import IncrementalGraphMaintainer


def _config(data: dict[str, object]) -> FridayChatConfig:
    return FridayChatConfig.model_validate(data)


def _pending_turn(
    turn_id: str,
    user_message: str,
    assistant_message: str,
) -> PendingExtractionTurn:
    return PendingExtractionTurn(
        turn_id=turn_id,
        user_message=user_message,
        assistant_message=assistant_message,
    )


class ErroringExtractor:
    """Extractor test double that mirrors framework error payloads."""

    def __init__(self, error: str) -> None:
        self.error = error
        self.calls = 0

    async def extract(self, turn: object) -> dict[str, Any]:
        self.calls += 1
        return {"error": self.error, "extracted": {}, "stats": {}}


class SelectiveExtractor:
    """Record turns and fail on one selected user message."""

    def __init__(self, failing_message: str) -> None:
        self.failing_message = failing_message
        self.calls: list[str] = []

    async def extract(self, turn: Any) -> dict[str, Any]:
        self.calls.append(turn.user_message)
        if turn.user_message == self.failing_message:
            return {"error": "synthetic timeout", "extracted": {}, "stats": {}}
        return {"extracted": {}, "stats": {}}


class BlockingExtractor:
    """Remain in flight until the supervised task is cancelled."""

    def __init__(self) -> None:
        self.started = asyncio.Event()

    async def extract(self, _turn: object) -> dict[str, Any]:
        self.started.set()
        await asyncio.Event().wait()
        raise AssertionError("blocking extractor unexpectedly resumed")


class CommitShieldingExtractor:
    """Finish one simulated commit after the caller requests cancellation."""

    def __init__(self) -> None:
        self.started = asyncio.Event()
        self.release = asyncio.Event()
        self.committed_turn_ids: list[str] = []

    async def extract(self, turn: Any) -> dict[str, Any]:
        self.started.set()
        while True:
            try:
                await self.release.wait()
                break
            except asyncio.CancelledError:
                continue
        self.committed_turn_ids.append(turn.id)
        raise ExtractionCommitCompletedUnderCancellation


class FailingPromotionService:
    """Return a lifecycle result containing a categorical failure."""

    async def run_promotion_cycle(self, *, dry_run: bool) -> PromotionResult:
        assert dry_run is False
        return PromotionResult(errors=["synthetic lifecycle failure"])


class MemoryOnlyExecuteParticipant:
    """Participant-shaped double that must not unlock Gate A execution."""

    def preflight_status(self) -> tuple[bool, str]:
        return True, "memory-only preflight passed"


def test_runtime_factory_builds_fakes_without_provider_keys() -> None:
    config = _config({"llm": {"model": "openai/test-chat-model"}})

    runtime = build_runtime(config)

    assert isinstance(runtime.chat_llm, FakeChatModel)
    assert isinstance(runtime.async_clients, FakeAsyncClientLifecycle)
    assert runtime.chat_llm.model == "openai/test-chat-model"
    assert runtime.tool_context is None
    assert runtime.diagnostics.maintenance_llm_fallbacks == list(
        MAINTENANCE_LLM_ROLES
    )


async def test_fake_async_client_lifecycle_is_deterministic() -> None:
    lifecycle = FakeAsyncClientLifecycle()

    await lifecycle.close()

    assert lifecycle.close_calls == 1


@pytest.mark.asyncio
async def test_fake_build_start_run_never_inspects_active_recovery_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process_cwd = tmp_path / "checkout"
    recovery_root = process_cwd / ".friday" / "recovery"
    recovery_root.mkdir(parents=True)
    sentinel = recovery_root / "operator-sentinel"
    sentinel.write_text("must remain untouched")
    visited: list[Path] = []
    original_iterdir = Path.iterdir

    def recording_iterdir(path: Path):  # type: ignore[no-untyped-def]
        visited.append(path.resolve(strict=False))
        return original_iterdir(path)

    monkeypatch.chdir(process_cwd)
    monkeypatch.setattr(Path, "iterdir", recording_iterdir)
    runtime = build_runtime(
        _config(
            {
                "llm": {"model": "openai/test-chat-model"},
                "memory": {"persist_directory": ".friday/vector"},
                "maintenance": {"backup_directory": ".friday/recovery"},
            }
        )
    )
    result = await FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource([]),
    ).run()
    inspected_paths = tuple(visited)

    assert result.exit_reason == "eof"
    assert recovery_root.resolve() not in inspected_paths
    assert sentinel.read_text() == "must remain untouched"
    assert not runtime.maintenance_layout.recovery_root.is_relative_to(process_cwd)


def test_runtime_factory_builds_framework_adapters_in_real_mode(tmp_path: Path) -> None:
    config = _config(
        {
            "llm": {"model": "openai/test-chat-model"},
            "embedding": {"model": "openai/test-embedding-model"},
            "memory": {"persist_directory": str(tmp_path / "vector")},
            "transcript": {"export_directory": str(tmp_path / "exports")},
            "chat": {"workflows_dir": str(tmp_path / "workflows")},
            "tools": {"registry": []},
        }
    )

    runtime = build_runtime(config, fake=False, session_id="test-session")

    assert isinstance(runtime.chat_llm, FrameworkChatModel)
    assert isinstance(runtime.async_clients, FrameworkAsyncClientLifecycle)
    assert isinstance(runtime.embedding, FrameworkEmbeddingService)
    assert isinstance(runtime.memory, FrameworkMemoryAdapter)
    assert isinstance(runtime.transcript, FrameworkTranscriptAdapter)
    assert isinstance(runtime.tools, FrameworkToolRegistryAdapter)
    assert isinstance(runtime.workflow, FrameworkWorkflowAdapter)
    assert isinstance(runtime.maintenance, FrameworkMaintenanceAdapter)


def test_typed_primary_keeps_maintenance_fallback_on_legacy_service(
    tmp_path: Path,
) -> None:
    config = _config(
        {
            "llm": {
                "model": "openai/qwen3.8-27b-mlx",
                "generation": {
                    "reasoning": {"mode": "enabled", "effort": "medium"},
                    "sampling": {"top_p": 0.9, "top_k": 40},
                },
                "transport_target": {
                    "provider": "openai_compatible",
                    "dialect": "openai_chat_completions",
                    "serving_engine": "lm_studio",
                },
                "model_target": {
                    "model_id": "qwen3.8-27b-mlx",
                    "family": "qwen3_8",
                    "revision": "test-revision",
                },
            },
            "embedding": {"model": "openai/test-embedding-model"},
            "memory": {"persist_directory": str(tmp_path / "vector")},
            "transcript": {"export_directory": str(tmp_path / "exports")},
            "chat": {"workflows_dir": str(tmp_path / "workflows")},
            "tools": {"registry": []},
        }
    )

    runtime = build_runtime(config, fake=False, session_id="typed-primary-test")

    assert isinstance(runtime.chat_llm, FrameworkChatModel)
    assert runtime.chat_llm.service.execution_target is not None
    assert isinstance(runtime.maintenance, FrameworkMaintenanceAdapter)
    assert runtime.maintenance.llm_service is not runtime.chat_llm.service
    assert runtime.maintenance.llm_service.execution_target is None
    assert all(
        service.execution_target is None
        for service in runtime.maintenance.llm_services.values()
    )


async def test_real_runtime_manual_and_exit_execute_paths_remain_contained(
    tmp_path: Path,
) -> None:
    vector_directory = tmp_path / "vector"
    vector_directory.mkdir()
    config = _config(
        {
            "llm": {"model": "openai/test-chat-model"},
            "embedding": {"model": "openai/test-embedding-model"},
            "memory": {"persist_directory": str(vector_directory)},
            "transcript": {"export_directory": str(tmp_path / "exports")},
            "tools": {"registry": []},
        }
    )
    runtime = build_runtime(config, fake=False, session_id="synthetic-session")
    assert isinstance(runtime.maintenance, FrameworkMaintenanceAdapter)
    assert isinstance(runtime.memory, FrameworkMemoryAdapter)
    runtime.memory.__dict__["maintenance_participant"] = (
        MemoryOnlyExecuteParticipant()
    )

    manual = await runtime.maintenance.reorganize(
        mode="full",
        dry_run=False,
        backup_first=True,
    )
    await runtime.maintenance.reorganize_memory("fast")

    assert manual["errors"]
    assert "Execute disabled:" in manual["errors"][0]
    assert runtime.maintenance.actions == [
        "reorganize:full:execute_disabled",
        "reorganize_skipped:execute_disabled",
    ]


def test_real_runtime_builds_friday_py_lifecycle_collaborators(
    tmp_path: Path,
) -> None:
    config = _config(
        {
            "llm": {"model": "openai/test-chat-model"},
            "embedding": {"model": "openai/test-embedding-model"},
            "memory": {"persist_directory": str(tmp_path / "vector")},
            "lifecycle": {
                "enabled": True,
                "decay_rate": 0.01,
                "access_boost": 0.2,
                "promotion_threshold": 0.7,
                "decay_threshold": 0.5,
                "short_term_min_age_hours": 24,
                "decayed_retention_days": 3,
                "access_buffer": {
                    "max_buffer_size": 12,
                    "max_buffer_age_seconds": 34,
                    "decay_score_boost": 0.1,
                },
                "factor_computer": {
                    "decay_rate": 0.005,
                    "usage_boost_factor": 0.1,
                    "min_factor": 0.01,
                },
            },
            "transcript": {"export_directory": str(tmp_path / "exports")},
            "tools": {"registry": []},
        }
    )

    runtime = build_runtime(config, fake=False, session_id="test-session")

    assert isinstance(runtime.maintenance, FrameworkMaintenanceAdapter)
    assert isinstance(runtime.maintenance.promotion_service, MemoryPromotionService)
    assert isinstance(runtime.maintenance.access_buffer, AccessBuffer)
    assert isinstance(runtime.maintenance.factor_computer, RetrievalFactorComputer)
    assert isinstance(runtime.maintenance.incremental_maintainer, IncrementalGraphMaintainer)
    assert runtime.maintenance.access_buffer.config.max_buffer_size == 12


def test_real_runtime_workflow_adapter_loads_configured_workflow_dir(
    tmp_path: Path,
) -> None:
    workflows_dir = tmp_path / "workflows"
    workflows_dir.mkdir()
    (workflows_dir / "sample.yaml").write_text(
        "id: sample\n"
        "name: Sample Workflow\n"
        "description: Configured workflow directory fixture.\n"
        "tasks:\n"
        "  - id: draft\n"
        "    name: Draft\n"
        "    description: Draft the requested output.\n"
        "    agent: friday\n"
        "    outputs:\n"
        "      - draft\n"
        "    requires_approval: false\n"
    )
    config = _config(
        {
            "llm": {"model": "openai/test-chat-model"},
            "embedding": {"model": "openai/test-embedding-model"},
            "memory": {"persist_directory": str(tmp_path / "vector")},
            "transcript": {"export_directory": str(tmp_path / "exports")},
            "chat": {"workflows_dir": str(workflows_dir)},
            "tools": {"registry": []},
        }
    )

    runtime = build_runtime(config, fake=False, session_id="test-session")

    assert runtime.workflow.list_workflows() == {
        "sample": "Configured workflow directory fixture."
    }


def test_real_runtime_builds_passage_router_from_friday_py_config_shape(
    tmp_path: Path,
) -> None:
    config = _config(
        {
            "llm": {"model": "openai/test-chat-model"},
            "embedding": {"model": "openai/test-embedding-model"},
            "memory": {
                "persist_directory": str(tmp_path / "vector"),
                "passage_router": {
                    "enabled": True,
                    "model": "openai/router-model",
                    "temperature": 0.0,
                    "max_tokens": 80,
                    "timeout_seconds": 4.0,
                    "min_confidence": 0.75,
                    "fallback_mode": "exclude",
                    "include_on_empty_query": False,
                    "heuristic_keywords": ["remember"],
                    "min_similarity": 0.6,
                    "min_similarity_tool_output": 0.8,
                    "min_keep_on_empty": 1,
                },
            },
            "transcript": {"export_directory": str(tmp_path / "exports")},
            "tools": {"registry": []},
        }
    )

    runtime = build_runtime(config, fake=False, session_id="test-session")

    assert isinstance(runtime.memory, FrameworkMemoryAdapter)
    assert runtime.memory.passage_router is not None
    router_config = runtime.memory.passage_router.config
    assert router_config.min_confidence == 0.75
    assert router_config.fallback_mode == "exclude"


def test_real_runtime_builds_extraction_llm_from_friday_py_config_shape(
    tmp_path: Path,
) -> None:
    config = _config(
        {
            "llm": {
                "model": "openai/test-chat-model",
                "max_retries": 5,
                "timeout_seconds": 60.0,
            },
            "extraction": {
                "model": "openai/test-extraction-model",
                "api_base": "http://127.0.0.1:1234/v1",
                "api_key": "lm-studio",
                "max_retries": 4,
                "timeout_seconds": 90.0,
            },
            "embedding": {"model": "openai/test-embedding-model"},
            "memory": {"persist_directory": str(tmp_path / "vector")},
            "transcript": {"export_directory": str(tmp_path / "exports")},
            "tools": {"registry": []},
        }
    )

    runtime = build_runtime(config, fake=False, session_id="extraction-config-test")

    assert isinstance(runtime.maintenance, FrameworkMaintenanceAdapter)
    extractor = runtime.maintenance.extractor
    assert extractor is not None
    extraction_llm = extractor._llm
    assert extraction_llm.model == "openai/test-extraction-model"
    assert extraction_llm.api_base == "http://127.0.0.1:1234/v1"
    assert extraction_llm.api_key == "lm-studio"
    assert extraction_llm.resilience.max_retries == 4
    assert extraction_llm.resilience.timeout_seconds == 90.0


async def test_framework_maintenance_requeues_extraction_error_payloads() -> None:
    extractor = ErroringExtractor("LLM call timed out after 90.0s")
    adapter = FrameworkMaintenanceAdapter(
        config=_config({"llm": {"model": "openai/test-chat-model"}}),
        session_id="extraction-error-test",
        memory=cast(Any, object()),
        embedding=cast(Any, None),
        llm_service=cast(Any, object()),
        llm_models={},
        llm_services={},
        extractor=cast(Any, extractor),
    )
    pending = _pending_turn("error-turn", "remember this", "noted")
    adapter.pending_extraction = [pending]

    try:
        await adapter.extract_buffered_turns(trigger_reason="background_interval")
    except RuntimeError as exc:
        assert "Memory extraction failed" in str(exc)
    else:
        raise AssertionError("expected extraction error to fail the background batch")

    assert extractor.calls == 1
    assert adapter.pending_extraction == [pending]
    assert adapter.background_actions == []


async def test_framework_maintenance_requeues_only_unfinished_batch_turns() -> None:
    extractor = SelectiveExtractor("fail")
    adapter = FrameworkMaintenanceAdapter(
        config=_config({"llm": {"model": "openai/test-chat-model"}}),
        session_id="partial-extraction-error-test",
        memory=cast(Any, object()),
        embedding=cast(Any, None),
        llm_service=cast(Any, object()),
        llm_models={},
        llm_services={},
        extractor=cast(Any, extractor),
    )
    adapter.pending_extraction = [
        _pending_turn("complete-turn", "complete", "stored"),
        _pending_turn("failed-turn", "fail", "defer"),
        _pending_turn("later-turn", "later", "not attempted"),
    ]

    with pytest.raises(RuntimeError, match="Memory extraction failed"):
        await adapter.extract_buffered_turns(trigger_reason="background_interval")

    assert extractor.calls == ["complete", "fail"]
    assert adapter.pending_extraction == [
        _pending_turn("failed-turn", "fail", "defer"),
        _pending_turn("later-turn", "later", "not attempted"),
    ]


async def test_framework_maintenance_requeues_cancelled_inflight_turn() -> None:
    extractor = BlockingExtractor()
    adapter = FrameworkMaintenanceAdapter(
        config=_config({"llm": {"model": "openai/test-chat-model"}}),
        session_id="cancelled-extraction-test",
        memory=cast(Any, object()),
        embedding=cast(Any, None),
        llm_service=cast(Any, object()),
        llm_models={},
        llm_services={},
        extractor=cast(Any, extractor),
    )
    pending = _pending_turn("cancelled-turn", "cancelled", "preserved")
    adapter.pending_extraction = [pending]

    task = asyncio.create_task(
        adapter.extract_buffered_turns(trigger_reason="background_interval")
    )
    await extractor.started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert adapter.pending_extraction == [pending]
    assert adapter.background_actions == []


async def test_framework_maintenance_does_not_requeue_committed_cancelled_turn() -> None:
    extractor = CommitShieldingExtractor()
    adapter = FrameworkMaintenanceAdapter(
        config=_config({"llm": {"model": "openai/test-chat-model"}}),
        session_id="commit-boundary-extraction-test",
        memory=cast(Any, object()),
        embedding=cast(Any, None),
        llm_service=cast(Any, object()),
        llm_models={},
        llm_services={},
        extractor=cast(Any, extractor),
    )
    committed = _pending_turn("committed-turn", "committed", "stored")
    later = _pending_turn("later-turn", "later", "preserved")
    adapter.pending_extraction = [committed, later]

    task = asyncio.create_task(
        adapter.extract_buffered_turns(trigger_reason="background_interval")
    )
    await asyncio.wait_for(extractor.started.wait(), timeout=1.0)
    task.cancel()
    extractor.release.set()

    with pytest.raises(asyncio.CancelledError):
        await task

    assert extractor.committed_turn_ids == [committed.turn_id]
    assert adapter.pending_extraction == [later]
    assert adapter.background_actions == []


async def test_framework_maintenance_surfaces_lifecycle_result_errors() -> None:
    adapter = FrameworkMaintenanceAdapter(
        config=_config({"llm": {"model": "openai/test-chat-model"}}),
        session_id="lifecycle-error-test",
        memory=cast(Any, object()),
        embedding=cast(Any, None),
        llm_service=cast(Any, object()),
        llm_models={},
        llm_services={},
        promotion_service=cast(Any, FailingPromotionService()),
    )

    with pytest.raises(RuntimeError, match="lifecycle promotion reported errors"):
        await adapter.run_lifecycle()

    assert adapter.actions == []


def test_tool_auto_injection_follows_config() -> None:
    config = _config(
        {
            "llm": {"model": "openai/test-chat-model"},
            "tools": {
                "enabled": True,
                "registry": {"enabled_categories": ["utility"]},
                "context": {"include_in_context": True},
            },
        }
    )

    runtime = build_runtime(config)

    assert runtime.diagnostics.tool_context_injected is True
    assert runtime.tool_context is not None
    assert "echo" in runtime.tool_context
    assert "remember" not in runtime.tool_context


def test_maintenance_models_use_configured_roles_without_fallbacks() -> None:
    config = _config(
        {
            "llm": {"model": "openai/primary"},
            "maintenance": {
                "llm": {
                    role: {"model": f"openai/{role}"}
                    for role in MAINTENANCE_LLM_ROLES
                }
            },
        }
    )

    runtime = build_runtime(config)

    assert runtime.diagnostics.maintenance_llm_fallbacks == []
    assert runtime.maintenance.llm_models == {
        role: f"openai/{role}" for role in MAINTENANCE_LLM_ROLES
    }


async def test_turn_processor_records_fake_turn_and_uses_tool_context() -> None:
    config = _config(
        {
            "llm": {"model": "openai/test-chat-model"},
            "tools": {"context": {"include_in_context": True}},
            "speech": {"enabled": True},
        }
    )
    runtime = build_runtime(config)

    result = await TurnProcessor(runtime).process("hello")

    assert result.assistant_message == "Friday: hello"
    assert result.tool_context_injected is True
    assert isinstance(runtime.memory, FakeMemoryController)
    assert runtime.memory.stored_turns == [("hello", result.assistant_message)]
    assert isinstance(runtime.transcript, FakeTranscriptStore)
    assert runtime.transcript.turns == [("hello", result.assistant_message)]
    assert isinstance(runtime.speech, FakeSpeechAdapter)
    assert runtime.speech.spoken == [result.assistant_message]


async def test_real_runtime_preserves_configured_file_read_alias(
    tmp_path: Path,
) -> None:
    target = tmp_path / "config.yaml"
    target.write_text("answer: 42\n")
    config = _config(
        {
            "llm": {"model": "openai/test-chat-model"},
            "embedding": {"model": "openai/test-embedding-model"},
            "memory": {"persist_directory": str(tmp_path / "vector")},
            "transcript": {"export_directory": str(tmp_path / "exports")},
            "tools": {
                "enabled": True,
                "registry": [
                    {
                        "name": "file_read",
                        "module": "friday_tools.filesystem.smart_read",
                        "class": "SmartFileReadTool",
                    },
                    {
                        "name": "file_write",
                        "module": "friday_tools.filesystem",
                        "class": "FileWriteTool",
                    },
                ],
            },
        }
    )

    runtime = build_runtime(config, fake=False, session_id="tool-alias-test")
    tool_names = [tool.name for tool in runtime.tools.list_tools()]
    result = await runtime.tools.call_tool("file_read", {"path": str(target)})

    assert tool_names == ["file_read", "file_write"]
    assert "smart_read" not in tool_names
    assert "answer: 42" in result
    assert isinstance(runtime.tools, FrameworkToolRegistryAdapter)
    file_read_tool = runtime.tools.tools["file_read"]
    assert getattr(file_read_tool, "_fallback_llm", None) is not None
    assert getattr(file_read_tool, "_config", None) is not None


def test_real_runtime_injects_web_config_into_serper_tool(tmp_path: Path) -> None:
    config = _config(
        {
            "llm": {"model": "openai/test-chat-model"},
            "embedding": {"model": "openai/test-embedding-model"},
            "memory": {"persist_directory": str(tmp_path / "vector")},
            "transcript": {"export_directory": str(tmp_path / "exports")},
            "web": {
                "client": {"timeout": 12.0, "max_retries": 1},
                "serper_api_key": "test-serper-key",
            },
            "tools": {
                "enabled": True,
                "registry": [
                    {
                        "name": "serper_search",
                        "module": "friday_tools.web",
                        "class": "SerperSearchTool",
                    },
                    {
                        "name": "web_reader",
                        "module": "friday_tools.web",
                        "class": "WebReaderTool",
                    },
                ],
            },
        }
    )

    runtime = build_runtime(config, fake=False, session_id="web-config-test")

    assert isinstance(runtime.tools, FrameworkToolRegistryAdapter)
    serper_tool = runtime.tools.tools["serper_search"]
    web_reader_tool = runtime.tools.tools["web_reader"]
    assert serper_tool._config.serper_api_key == "test-serper-key"
    assert serper_tool._config.client.timeout == 12.0
    assert web_reader_tool._config.serper_api_key == "test-serper-key"
