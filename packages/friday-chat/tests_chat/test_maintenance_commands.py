"""Maintenance command tests for FridayV2."""

from __future__ import annotations

from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import FakeMemoryController, build_runtime


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
    return RegistryCommandContext(
        runtime=build_runtime(config),
        registry=registry,
        history=[("hello", "Friday: hello")],
        last_context="context",
        last_prompt="prompt",
        last_debug={"a": "b"},
    )


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


async def test_reorganize_dry_run_default_and_execute_behavior() -> None:
    registry = build_default_registry()
    context = _context()

    _, dry_run = await registry.execute("/reorganize", context)
    _, execute = await registry.execute("/reorganize --execute --no-backup", context)

    assert dry_run is not None
    assert "Reorganization mode: full" in dry_run.output
    assert "Dry run: True" in dry_run.output
    assert execute is not None
    assert "Dry run: False" in execute.output
    assert "Backup first: False" in execute.output


async def test_reorganize_single_step_precedence() -> None:
    registry = build_default_registry()
    context = _context()

    _, result = await registry.execute(
        "/reorganize --synthesize --prune --analyze --backup",
        context,
    )

    assert result is not None
    assert "Reorganization mode: backup" in result.output


async def test_reorganize_requires_persist_dir_and_classifies_errors() -> None:
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
    assert "Check embedding service configuration" in error.output


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
    context.runtime.maintenance.pending_extraction = [("u", "a")]

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
    context.runtime.maintenance.pending_extraction = [("u", "a")]
    context.runtime.maintenance.flush_pending_error = RuntimeError("connection lost")

    _, result = await registry.execute("/compact", context)

    assert result is not None
    assert "Check reachable LLM/embedding services" in result.output
    assert context.runtime.maintenance.pending_extraction == [("u", "a")]
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
