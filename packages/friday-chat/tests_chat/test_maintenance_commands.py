"""Maintenance command tests for FridayV2."""

from __future__ import annotations

import asyncio
import platform
from pathlib import Path

import pytest
from friday_chat.app import FridayChatApp
from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.config import FridayChatConfig
from friday_chat.reorganization import (
    OperationTrigger,
    RecoveryRequest,
    ReorganizationError,
    ReorganizationErrorCode,
    ReorganizationMode,
    ReorganizationRequest,
    ReorganizationResult,
    ResultStatus,
)
from friday_chat.runtime import (
    FakeMemoryController,
    PendingExtractionTurn,
    build_runtime,
)


def _context(
    *,
    persist_directory: str | None = "./vector",
    lifecycle_enabled: bool = True,
    access_buffer_enabled: bool = True,
    compaction_enabled: bool = True,
) -> RegistryCommandContext:
    config = FridayChatConfig.model_validate(
        {
            "llm": {"model": "openai/test-chat-model"},
            "memory": {
                "persist_directory": persist_directory,
                "compaction": {"enabled": compaction_enabled},
            },
            "lifecycle": {
                "enabled": lifecycle_enabled,
                "access_buffer": {"enabled": access_buffer_enabled},
                "factor_computer": {"enabled": True},
            },
        }
    )
    registry = build_default_registry()
    app = FridayChatApp(runtime=build_runtime(config), command_registry=registry)
    app.command_context.history = [("hello", "Friday: hello")]
    app.command_context.last_context = "context"
    app.command_context.last_prompt = "prompt"
    app.command_context.last_debug = {"a": "b"}
    return app.command_context


def _assert_linux_reorganize_refusal(
    context: RegistryCommandContext, output: str
) -> None:
    assert output == (
        "Reorganization failed safely (MaintenancePlatformError). "
        "Review sanitized diagnostics and recovery status."
    )
    assert context.runtime is not None
    assert context.runtime.maintenance.actions == []
    assert context.history == [("hello", "Friday: hello")]
    assert context.last_context == "context"
    assert context.last_prompt == "prompt"


def _set_test_platform(
    monkeypatch: pytest.MonkeyPatch, forced_linux: bool
) -> None:
    if forced_linux:
        monkeypatch.setattr("friday_chat.reorganization.lease.platform.system", lambda: "Linux")


async def test_reset_full_calls_all_stores_and_archives_transcripts() -> None:
    registry = build_default_registry()
    context = _context()
    assert context.runtime is not None

    _, result = await registry.execute("/reset", context)

    assert result is not None
    assert "- graph: reset" in result.output
    assert "- vector: reset" in result.output
    assert "- episodic: reset" in result.output
    assert "- transcripts: archived" in result.output
    assert context.runtime.maintenance.reset_calls == ["graph", "vector", "episodic"]
    assert context.runtime.maintenance.archived_transcripts is True
    assert context.history == []


async def test_reset_selective_calls_only_selected_store() -> None:
    registry = build_default_registry()
    context = _context()
    assert context.runtime is not None

    _, result = await registry.execute("/reset vector", context)

    assert result is not None
    assert "- vector: reset" in result.output
    assert "transcripts: archived" not in result.output
    assert context.runtime.maintenance.reset_calls == ["vector"]
    assert context.history == [("hello", "Friday: hello")]


async def test_reset_store_failure_reports_and_continues() -> None:
    registry = build_default_registry()
    context = _context()
    assert context.runtime is not None
    context.runtime.maintenance.errors = [RuntimeError("vector unavailable")]

    _, result = await registry.execute("/reset", context)

    assert result is not None
    assert "- graph: error: vector unavailable" in result.output
    assert "- vector: reset" in result.output
    assert "- episodic: reset" in result.output


@pytest.mark.parametrize("forced_linux", [False, True])
async def test_reorganize_dry_run_default_and_execute_containment(
    monkeypatch: pytest.MonkeyPatch, forced_linux: bool
) -> None:
    _set_test_platform(monkeypatch, forced_linux)
    registry = build_default_registry()
    context = _context()

    _, dry_run = await registry.execute("/reorganize", context)
    _, execute = await registry.execute("/reorganize --execute", context)

    assert dry_run is not None
    if platform.system() == "Linux":
        _assert_linux_reorganize_refusal(context, dry_run.output)
    else:
        assert "Reorganization mode: full" in dry_run.output
        assert "Dry run: True" in dry_run.output
    assert execute is not None
    assert "Reorganization execute is disabled:" in execute.output
    assert "Dry run: False" not in execute.output


async def test_reorganize_fake_service_cannot_enable_execute_directly() -> None:
    context = _context()
    assert context.runtime is not None

    result = await context.runtime.maintenance.reorganize(
        mode="full",
        dry_run=False,
        backup_first=True,
    )

    assert result["errors"]
    assert "Execute disabled:" in result["errors"][0]
    assert context.runtime.maintenance.actions == [
        "reorganize:full:execute_disabled"
    ]


async def test_manual_and_exit_share_production_coordinator_capability(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path.resolve()
    config = FridayChatConfig.model_validate(
        {
            "llm": {"model": "openai/test-chat-model"},
            "embedding": {"model": "openai/test-embedding-model"},
            "memory": {"persist_directory": str(root / "vector")},
            "lifecycle": {
                "enabled": True,
                "access_buffer": {"enabled": False},
            },
            "transcript": {"export_directory": str(root / "exports")},
            "maintenance": {
                "backup_directory": str(root / "recovery"),
                "logging": {"log_directory": str(root / "logs")},
            },
            "session": {
                "reorganize_on_exit": True,
                "reorganize_mode": "fast",
            },
            "tools": {"registry": []},
        }
    )
    runtime = build_runtime(config, fake=False, session_id="capability-test")
    app = FridayChatApp(runtime=runtime)
    capability = app.reorganization_coordinator.execution_capability
    observed: list[ReorganizationRequest] = []
    exit_requests: list[ReorganizationRequest | None] = []

    async def observe_run(
        request: ReorganizationRequest,
        **_kwargs: object,
    ) -> ReorganizationResult:
        observed.append(request)
        return ReorganizationResult(
            status=ResultStatus.COMPLETED,
            trigger=request.trigger,
            mode=request.mode,
        )

    async def observe_shutdown(
        request: ReorganizationRequest | None,
        **_kwargs: object,
    ) -> None:
        exit_requests.append(request)

    monkeypatch.setattr(app.reorganization_coordinator, "run", observe_run)
    monkeypatch.setattr(
        app.reorganization_coordinator,
        "shutdown",
        observe_shutdown,
    )

    _, manual = await app.command_registry.execute(
        "/reorganize --backup --execute",
        app.command_context,
    )
    await app._shutdown_through_coordinator()

    assert capability.memory_participant is True
    assert capability.transcript_participant is True
    assert capability.runtime_hooks is True
    assert capability.mutation_adapter is True
    assert capability.mutation_available is True
    assert runtime.maintenance.reorganization_execute_status()[0] is False
    assert manual is not None
    assert "Reorganization execute is disabled" not in manual.output
    assert [request.mode for request in observed] == [ReorganizationMode.BACKUP]
    assert len(exit_requests) == 1
    exit_request = exit_requests[0]
    assert exit_request is not None
    assert exit_request.mode is ReorganizationMode.FULL
    assert exit_request.skip_synthesis is True
    assert exit_request.skip_verify is True
    assert capability.available_for(observed[0]) is True
    assert capability.available_for(exit_request) is True

    fake_app = FridayChatApp(runtime=build_runtime(config))
    fake_capability = fake_app.reorganization_coordinator.execution_capability
    assert fake_capability.mutation_available is False
    assert fake_capability.recovery_available is False


async def test_backup_and_recovery_remain_available_without_mutation_adapter(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path.resolve()
    config = FridayChatConfig.model_validate(
        {
            "llm": {"model": "openai/test-chat-model"},
            "embedding": {"model": "openai/test-embedding-model"},
            "memory": {"persist_directory": str(root / "vector")},
            "lifecycle": {
                "enabled": True,
                "access_buffer": {"enabled": False},
            },
            "transcript": {"export_directory": str(root / "exports")},
            "maintenance": {
                "backup_directory": str(root / "recovery"),
                "logging": {"log_directory": str(root / "logs")},
            },
            "session": {
                "reorganize_on_exit": True,
                "reorganize_mode": "fast",
            },
            "tools": {"registry": []},
        }
    )
    app = FridayChatApp(
        runtime=build_runtime(config, fake=False, session_id="recovery-capability")
    )
    app.reorganization_coordinator._mutation = None
    capability = app.reorganization_coordinator.execution_capability
    ordinary_calls: list[ReorganizationRequest] = []
    recovery_calls: list[RecoveryRequest] = []
    exit_requests: list[ReorganizationRequest | None] = []

    async def observe_run(
        request: ReorganizationRequest,
        **_kwargs: object,
    ) -> ReorganizationResult:
        ordinary_calls.append(request)
        return ReorganizationResult(
            status=ResultStatus.COMPLETED,
            trigger=request.trigger,
            mode=request.mode,
        )

    async def observe_recovery(
        request: RecoveryRequest,
        **_kwargs: object,
    ) -> ReorganizationResult:
        recovery_calls.append(request)
        return ReorganizationResult(
            status=ResultStatus.PREFLIGHT_FAILED,
            trigger=OperationTrigger.RECOVERY,
            run_id=request.run_id,
            errors=[
                ReorganizationError(
                    code=ReorganizationErrorCode.PREFLIGHT_FAILED,
                    message="synthetic retained run is unavailable",
                )
            ],
        )

    async def observe_shutdown(
        request: ReorganizationRequest | None,
        **_kwargs: object,
    ) -> None:
        exit_requests.append(request)

    monkeypatch.setattr(app.reorganization_coordinator, "run", observe_run)
    monkeypatch.setattr(
        app.reorganization_coordinator,
        "recover",
        observe_recovery,
    )
    monkeypatch.setattr(
        app.reorganization_coordinator,
        "shutdown",
        observe_shutdown,
    )
    run_id = "a" * 32

    _, backup = await app.command_registry.execute(
        "/reorganize --backup --execute",
        app.command_context,
    )
    _, mutation = await app.command_registry.execute(
        "/reorganize --dedupe --execute",
        app.command_context,
    )
    _, recovery = await app.command_registry.execute(
        f"/reorganize --recover {run_id} --execute",
        app.command_context,
    )
    await app._shutdown_through_coordinator()

    assert capability.mutation_available is False
    assert capability.recovery_available is True
    assert backup is not None
    assert "Reorganization execute is disabled" not in backup.output
    assert mutation is not None
    assert "maintenance mutation adapter" in mutation.output
    assert recovery is not None
    assert "Reorganization execute is disabled" not in recovery.output
    assert [request.mode for request in ordinary_calls] == [ReorganizationMode.BACKUP]
    assert [request.run_id for request in recovery_calls] == [run_id]
    assert exit_requests == [None]

    async def failing_recovery(
        request: RecoveryRequest,
        **_kwargs: object,
    ) -> ReorganizationResult:
        del request
        raise PermissionError("secret retained-artifact path")

    async def failing_backup(
        request: ReorganizationRequest,
        **_kwargs: object,
    ) -> ReorganizationResult:
        del request
        raise RuntimeError("secret-provider-response")

    monkeypatch.setattr(
        app.reorganization_coordinator,
        "recover",
        failing_recovery,
    )
    monkeypatch.setattr(app.reorganization_coordinator, "run", failing_backup)
    _, recovery_failure = await app.command_registry.execute(
        f"/reorganize --recover {run_id} --execute",
        app.command_context,
    )
    _, backup_failure = await app.command_registry.execute(
        "/reorganize --backup --execute",
        app.command_context,
    )

    assert recovery_failure is not None
    assert recovery_failure.output == (
        "Reorganization failed safely (PermissionError). "
        "Review sanitized diagnostics and recovery status."
    )
    assert "secret" not in recovery_failure.output
    assert backup_failure is not None
    assert backup_failure.output == (
        "Reorganization failed safely (RuntimeError). "
        "Review sanitized diagnostics and recovery status."
    )
    assert "secret-provider-response" not in backup_failure.output


async def test_reorganize_rejects_plain_execute_token() -> None:
    registry = build_default_registry()
    context = _context()

    _, result = await registry.execute("/reorganize execute", context)

    assert result is not None
    assert "Unknown argument 'execute'" in result.output
    assert "--execute" in result.output
    assert context.runtime is not None
    assert context.runtime.maintenance.actions == []


async def test_reorganize_rejects_no_backup_token() -> None:
    registry = build_default_registry()
    context = _context()

    _, result = await registry.execute("/reorganize --execute --no-backup", context)

    assert result is not None
    assert "--no-backup has been removed" in result.output
    assert context.runtime is not None
    assert context.runtime.maintenance.actions == []


async def test_reorganize_rejects_unknown_tokens() -> None:
    registry = build_default_registry()
    context = _context()

    _, result = await registry.execute("/reorganize --frobnicate", context)

    assert result is not None
    assert "Unknown argument '--frobnicate'" in result.output
    assert "Usage: /reorganize" in result.output


async def test_reorganize_rejects_unknown_positional_tokens_before_preflight() -> None:
    registry = build_default_registry()
    context = _context(persist_directory=None)

    _, result = await registry.execute("/reorganize unexpected", context)

    assert result is not None
    assert "Unknown argument 'unexpected'" in result.output
    assert "memory.persist_directory is required" not in result.output


async def test_reorganize_rejects_duplicate_arguments() -> None:
    registry = build_default_registry()
    context = _context()

    _, result = await registry.execute(
        "/reorganize --execute --execute",
        context,
    )

    assert result is not None
    assert "Duplicate argument '--execute'" in result.output
    assert context.runtime is not None
    assert context.runtime.maintenance.actions == []


async def test_reorganize_rejects_conflicting_mode_flags() -> None:
    registry = build_default_registry()
    context = _context()

    _, result = await registry.execute("/reorganize --synthesize --prune", context)

    assert result is not None
    assert "Conflicting mode flags" in result.output
    assert context.runtime is not None
    assert context.runtime.maintenance.actions == []


async def test_reorganize_rejects_full_only_flags_for_single_step_modes() -> None:
    registry = build_default_registry()
    context = _context()

    _, result = await registry.execute("/reorganize --dedupe --force-reembed", context)

    assert result is not None
    assert "--force-reembed is only valid with the full reorganization mode" in result.output


async def test_reorganize_rejects_execute_for_analyze_mode() -> None:
    registry = build_default_registry()
    context = _context()

    _, result = await registry.execute("/reorganize --analyze --execute", context)

    assert result is not None
    assert "--analyze is analysis-only" in result.output


@pytest.mark.parametrize("forced_linux", [False, True])
async def test_reorganize_single_step_mode_dispatches_in_dry_run(
    monkeypatch: pytest.MonkeyPatch, forced_linux: bool
) -> None:
    _set_test_platform(monkeypatch, forced_linux)
    registry = build_default_registry()
    context = _context()

    _, result = await registry.execute("/reorganize --dedupe", context)

    assert result is not None
    if platform.system() == "Linux":
        _assert_linux_reorganize_refusal(context, result.output)
    else:
        assert "Reorganization mode: dedupe" in result.output
        assert "Dry run: True" in result.output


@pytest.mark.parametrize("forced_linux", [False, True])
async def test_reorganize_manual_default_ignores_mutating_maintenance_default(
    monkeypatch: pytest.MonkeyPatch, forced_linux: bool
) -> None:
    _set_test_platform(monkeypatch, forced_linux)
    registry = build_default_registry()
    context = _context()
    assert context.runtime is not None
    context.runtime.config.maintenance.defaults["dry_run"] = False

    _, result = await registry.execute("/reorganize", context)

    assert result is not None
    if platform.system() == "Linux":
        _assert_linux_reorganize_refusal(context, result.output)
    else:
        assert "Dry run: True" in result.output


@pytest.mark.parametrize("forced_linux", [False, True])
async def test_reorganize_requires_persist_dir_and_reports_typed_capability(
    monkeypatch: pytest.MonkeyPatch, forced_linux: bool
) -> None:
    _set_test_platform(monkeypatch, forced_linux)
    registry = build_default_registry()
    missing_context = _context(persist_directory=None)
    error_context = _context()
    assert error_context.runtime is not None
    error_context.runtime.maintenance.errors = [RuntimeError("embedding timeout")]

    _, missing = await registry.execute("/reorganize", missing_context)
    _, error = await registry.execute("/reorganize", error_context)

    assert missing is not None
    assert missing.output == "Cannot reorganize: memory.persist_directory is required."
    assert error is not None
    if platform.system() == "Linux":
        _assert_linux_reorganize_refusal(error_context, error.output)
        assert len(error_context.runtime.maintenance.errors) == 1
        assert str(error_context.runtime.maintenance.errors[0]) == "embedding timeout"
    else:
        assert "Error [capability_unavailable]" in error.output
        assert "maintenance mutation adapter is unavailable" in error.output


async def test_reorganize_recovery_parser_and_execute_containment() -> None:
    registry = build_default_registry()
    context = _context()
    run_id = "a" * 32

    _, invalid = await registry.execute("/reorganize --recover NOT-A-RUN", context)
    _, conflicting = await registry.execute(
        f"/reorganize --recover {run_id} --dedupe",
        context,
    )
    _, execute = await registry.execute(
        f"/reorganize --recover {run_id} --execute",
        context,
    )

    assert invalid is not None
    assert "32 lowercase hexadecimal characters" in invalid.output
    assert conflicting is not None
    assert "--recover cannot be combined" in conflicting.output
    assert execute is not None
    assert "Reorganization execute is disabled:" in execute.output


async def test_replay_waits_for_exclusive_maintenance_admission(
    tmp_path: Path,
) -> None:
    registry = build_default_registry()
    context = _context()
    gate = context.maintenance_gate
    assert gate is not None
    csv_path = tmp_path / "replay.csv"
    csv_path.write_text(
        "turn_number,user_message,assistant_message\n"
        "1,queued replay,prior response\n"
    )
    entered = asyncio.Event()
    release = asyncio.Event()

    async def hold_exclusive() -> None:
        async with gate.exclusive("test-recovery"):
            entered.set()
            await release.wait()

    exclusive = asyncio.create_task(hold_exclusive())
    await entered.wait()
    replay = asyncio.create_task(
        registry.execute(f"/replay {csv_path}", context)
    )
    await asyncio.sleep(0)

    assert not replay.done()
    release.set()
    await exclusive
    _, result = await replay
    assert result is not None
    assert "Replayed 1 turns" in result.output


async def test_lifecycle_precedence_and_missing_access_buffer() -> None:
    registry = build_default_registry()
    context = _context()
    missing_buffer = _context(access_buffer_enabled=False)

    _, stats = await registry.execute("/lifecycle --execute --stats", context)
    _, flush = await registry.execute("/lifecycle --flush", missing_buffer)
    _, optimize = await registry.execute("/lifecycle --optimize", context)

    assert stats is not None
    assert "Lifecycle mode: stats" in stats.output
    assert "Dry run: False" in stats.output
    assert flush is not None
    assert flush.output == "Lifecycle access buffer is not configured."
    assert optimize is not None
    assert "Lifecycle mode: optimize" in optimize.output


async def test_lifecycle_default_is_dry_run() -> None:
    registry = build_default_registry()
    context = _context()

    _, result = await registry.execute("/lifecycle", context)

    assert result is not None
    assert "Lifecycle mode: cycle" in result.output
    assert "Dry run: True" in result.output


async def test_migrate_force_execute_alias_and_no_migration_needed() -> None:
    registry = build_default_registry()
    force_context = _context()
    dry_context = _context()
    assert dry_context.runtime is not None
    dry_context.runtime.maintenance.migration_needed = False

    _, force = await registry.execute("/migrate --force", force_context)
    _, execute = await registry.execute("/migrate --execute", force_context)
    _, stats = await registry.execute("/migrate --stats", dry_context)

    assert force is not None
    assert "Migration mode: execute" in force.output
    assert execute is not None
    assert "Migration mode: execute" in execute.output
    assert stats is not None
    assert stats.output == "Migration not needed. No records changed."


async def test_compact_flushes_pending_extraction_before_run() -> None:
    registry = build_default_registry()
    context = _context()
    assert context.runtime is not None
    context.runtime.maintenance.pending_extraction = [
        PendingExtractionTurn("compact-turn", "u", "a")
    ]

    _, result = await registry.execute("/compact", context)

    assert result is not None
    assert "pending_extraction_flushed: 1" in result.output
    assert context.runtime.maintenance.pending_extraction == []
    assert context.runtime.maintenance.compaction_calls[0]["trigger_reason"] == (
        "manual_command"
    )


async def test_compact_flush_failure_preserves_pending_turns_and_skips_compactor() -> None:
    registry = build_default_registry()
    context = _context()
    assert context.runtime is not None
    pending = PendingExtractionTurn("compact-failure-turn", "u", "a")
    context.runtime.maintenance.pending_extraction = [pending]
    context.runtime.maintenance.flush_pending_error = RuntimeError("connection lost")

    _, result = await registry.execute("/compact", context)

    assert result is not None
    assert "Check reachable LLM/embedding services" in result.output
    assert context.runtime.maintenance.pending_extraction == [pending]
    assert context.runtime.maintenance.compaction_calls == []


async def test_compact_disabled_and_running_guards() -> None:
    registry = build_default_registry()
    disabled = _context(compaction_enabled=False)
    running = _context()
    assert running.runtime is not None
    running.runtime.maintenance.compaction_running = True

    _, disabled_result = await registry.execute("/compact", disabled)
    _, running_result = await registry.execute("/compact", running)

    assert disabled_result is not None
    assert disabled_result.output == "Compaction service is disabled."
    assert running_result is not None
    assert running_result.output == "Compaction is already running."


async def test_memory_store_clears_on_full_reset() -> None:
    registry = build_default_registry()
    context = _context()
    assert context.runtime is not None
    assert isinstance(context.runtime.memory, FakeMemoryController)
    context.runtime.memory.stored_turns = [("u", "a")]

    await registry.execute("/reset", context)

    assert context.runtime.memory.stored_turns == []
