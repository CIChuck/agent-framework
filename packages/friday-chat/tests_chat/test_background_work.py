"""Background work and exit maintenance tests for FridayV2."""

from __future__ import annotations

import asyncio

import pytest
from friday_chat.app import (
    AppMaintenanceRuntimeHooks,
    ConsoleInputSource,
    FridayChatApp,
    ListInputSource,
    ListOutputSink,
)
from friday_chat.background import BackgroundTaskManager, BackgroundWorkCoordinator
from friday_chat.commands.registry import RegistryCommandContext, build_default_registry
from friday_chat.config import FridayChatConfig
from friday_chat.reorganization.gate import MaintenanceAdmissionGate
from friday_chat.runtime import FridayRuntime, PendingExtractionTurn, build_runtime
from friday_memory.models.budget import BudgetSeverity, BudgetStatus


def _runtime(
    *,
    extraction_interval: int = 0,
    compaction_enabled: bool = False,
    compaction_utilization: float = 0.0,
    compaction_threshold: float = 1.0,
    compaction_cooldown_turns: int = 1,
    context_window: int = 8192,
    output_buffer: int = 1024,
) -> FridayRuntime:
    config = FridayChatConfig.model_validate(
        {
            "llm": {"model": "openai/test-chat-model"},
            "extraction": {"interval": extraction_interval},
            "tools": {"enabled": True},
            "lifecycle": {"factor_computer": {"enabled": True}},
            "memory": {
                "context_window": context_window,
                "output_buffer": output_buffer,
                "compaction": {
                    "enabled": compaction_enabled,
                    "current_utilization": compaction_utilization,
                    "compaction_threshold": compaction_threshold,
                    "cooldown_turns": compaction_cooldown_turns,
                }
            },
        }
    )
    return build_runtime(config)


class FirstTurnThenIdlePrompt:
    """Return one turn, then remain idle until released with EOF."""

    def __init__(self, first_message: str) -> None:
        self._first_message = first_message
        self._call_count = 0
        self.idle = asyncio.Event()
        self.release = asyncio.Event()

    async def __call__(self, _prompt: str) -> str:
        self._call_count += 1
        if self._call_count == 1:
            return self._first_message
        self.idle.set()
        await self.release.wait()
        raise EOFError


class PromptDuringExtraction:
    """Submit a second chat turn while first-turn extraction is running."""

    def __init__(
        self,
        extraction_started: asyncio.Event,
        extraction_completed: asyncio.Event,
    ) -> None:
        self._extraction_started = extraction_started
        self._extraction_completed = extraction_completed
        self._call_count = 0

    async def read(self) -> str:
        self._call_count += 1
        if self._call_count == 1:
            return "first"
        if self._call_count == 2:
            await self._extraction_started.wait()
            return "second"
        await self._extraction_completed.wait()
        raise EOFError


async def test_extraction_interval_matrix() -> None:
    async def scheduled_intervals(interval: int, turns: int) -> list[str]:
        runtime = _runtime(extraction_interval=interval)
        manager = BackgroundTaskManager()
        coordinator = BackgroundWorkCoordinator(runtime, manager)
        for turn in range(1, turns + 1):
            coordinator.schedule_after_turn(
                turn_count=turn,
                user_message=f"u{turn}",
                assistant_message=f"a{turn}",
            )
        await manager.wait_for_all()
        return [
            action
            for action in runtime.maintenance.background_actions
            if action.startswith("extract:")
        ]

    assert len(await scheduled_intervals(0, 3)) == 3
    assert len(await scheduled_intervals(2, 5)) == 2
    assert await scheduled_intervals(-1, 3) == []


async def test_interval_extraction_processes_full_buffered_batch() -> None:
    runtime = _runtime(extraction_interval=3)
    manager = BackgroundTaskManager()
    coordinator = BackgroundWorkCoordinator(runtime, manager)

    for turn in range(1, 4):
        coordinator.schedule_after_turn(
            turn_count=turn,
            user_message=f"u{turn}",
            assistant_message=f"a{turn}",
        )
    await manager.wait_for_all()

    assert runtime.maintenance.background_actions == [
        "tool_decay",
        "incremental_graph_maintenance",
        "tool_decay",
        "incremental_graph_maintenance",
        "extract:background_interval:3",
        "tool_decay",
        "incremental_graph_maintenance",
    ]
    assert runtime.maintenance.pending_extraction == []


async def test_preempted_extraction_is_requeued_and_resumed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = _runtime(extraction_interval=3)
    manager = BackgroundTaskManager()
    coordinator = BackgroundWorkCoordinator(runtime, manager)
    extraction_started = asyncio.Event()
    extraction_completed = asyncio.Event()
    unrelated_release = asyncio.Event()
    extraction_attempts = 0

    unrelated_task = manager.create_task(unrelated_release.wait())

    async def controlled_extraction(*, trigger_reason: str) -> int:
        nonlocal extraction_attempts
        extraction_attempts += 1
        turns = list(runtime.maintenance.pending_extraction)
        runtime.maintenance.pending_extraction.clear()
        if extraction_attempts == 1:
            extraction_started.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                runtime.maintenance.pending_extraction[:0] = turns
                raise
        runtime.maintenance.background_actions.append(
            f"extract:{trigger_reason}:{len(turns)}"
        )
        extraction_completed.set()
        return len(turns)

    monkeypatch.setattr(
        runtime.maintenance,
        "extract_buffered_turns",
        controlled_extraction,
    )
    coordinator.schedule_after_turn(
        turn_count=3,
        user_message="foreground priority",
        assistant_message="defer extraction",
    )
    await asyncio.wait_for(extraction_started.wait(), timeout=1.0)

    assert await coordinator.preempt_extraction_for_foreground_turn() is True
    assert len(runtime.maintenance.pending_extraction) == 1
    pending = runtime.maintenance.pending_extraction[0]
    assert isinstance(pending, PendingExtractionTurn)
    assert pending.user_message == "foreground priority"
    assert pending.assistant_message == "defer extraction"
    assert pending.turn_id
    assert unrelated_task.done() is False

    coordinator.resume_preempted_extraction()
    unrelated_release.set()
    await asyncio.wait_for(extraction_completed.wait(), timeout=1.0)
    await manager.wait_for_all()

    assert extraction_attempts == 2
    assert unrelated_task.cancelled() is False
    assert runtime.maintenance.pending_extraction == []
    assert "extract:foreground_resume:1" in (
        runtime.maintenance.background_actions
    )


async def test_app_preempts_extraction_before_processing_next_chat_turn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = _runtime(extraction_interval=1)
    extraction_started = asyncio.Event()
    extraction_cancelled = asyncio.Event()
    extraction_completed = asyncio.Event()
    extraction_attempts = 0

    async def controlled_extraction(*, trigger_reason: str) -> int:
        nonlocal extraction_attempts
        extraction_attempts += 1
        turns = list(runtime.maintenance.pending_extraction)
        runtime.maintenance.pending_extraction.clear()
        if extraction_attempts == 1:
            extraction_started.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                runtime.maintenance.pending_extraction[:0] = turns
                extraction_cancelled.set()
                raise
        runtime.maintenance.background_actions.append(
            f"extract:{trigger_reason}:{len(turns)}"
        )
        extraction_completed.set()
        return len(turns)

    monkeypatch.setattr(
        runtime.maintenance,
        "extract_buffered_turns",
        controlled_extraction,
    )
    app = FridayChatApp(
        runtime=runtime,
        input_source=PromptDuringExtraction(
            extraction_started,
            extraction_completed,
        ),
        output_sink=ListOutputSink(),
    )

    result = await asyncio.wait_for(app.run(), timeout=1.0)

    assert result.turns_processed == 2
    assert extraction_cancelled.is_set()
    assert extraction_attempts == 2
    assert runtime.maintenance.pending_extraction == []
    assert "extract:background_interval:2" in (
        runtime.maintenance.background_actions
    )


async def test_background_routes_tool_decay_graph_and_budget_compaction() -> None:
    runtime = _runtime(
        extraction_interval=-1,
        compaction_enabled=True,
        compaction_utilization=0.95,
        compaction_threshold=0.8,
    )
    manager = BackgroundTaskManager()
    coordinator = BackgroundWorkCoordinator(runtime, manager)

    budget_status = BudgetStatus(
        total_tokens=950,
        available_budget=1000,
        utilization_pct=95.0,
        overage_tokens=0,
        severity=BudgetSeverity.WARNING,
        message_tokens=900,
        tool_tokens=50,
    )

    coordinator.schedule_after_turn(
        turn_count=1,
        user_message="hello",
        assistant_message="Friday: hello",
        budget_status=budget_status,
    )
    await manager.wait_for_all()

    assert "tool_decay" in runtime.maintenance.background_actions
    assert "incremental_graph_maintenance" in runtime.maintenance.background_actions
    assert runtime.maintenance.compaction_calls[0]["trigger_reason"] == (
        "budget_threshold_exceeded"
    )
    assert runtime.maintenance.compaction_calls[0]["current_tokens"] == 950
    assert runtime.maintenance.compaction_calls[0]["available_budget"] == 1000


async def test_app_completes_background_work_while_next_prompt_is_idle() -> None:
    runtime = _runtime(
        extraction_interval=1,
        compaction_enabled=True,
        compaction_threshold=0.5,
        context_window=512,
        output_buffer=100,
    )
    prompt = FirstTurnThenIdlePrompt("x" * 2000)
    app = FridayChatApp(
        runtime=runtime,
        input_source=ConsoleInputSource(prompt_fn=prompt),
        output_sink=ListOutputSink(),
    )
    app_task = asyncio.create_task(app.run())

    result = None
    try:
        await asyncio.wait_for(prompt.idle.wait(), timeout=1.0)
        await asyncio.wait_for(app.background.wait_for_all(), timeout=1.0)

        assert app_task.done() is False
        assert "extract:background_interval:1" in runtime.maintenance.background_actions
        assert "tool_decay" in runtime.maintenance.background_actions
        assert "incremental_graph_maintenance" in (
            runtime.maintenance.background_actions
        )
        assert len(runtime.maintenance.compaction_calls) == 1
    finally:
        prompt.release.set()
        result = await asyncio.wait_for(app_task, timeout=1.0)

    assert result is not None
    assert result.exit_reason == "eof"
    assert result.turns_processed == 1
    assert app.background.closed is True


async def test_budget_compaction_flushes_extraction_before_compacting() -> None:
    runtime = _runtime(
        extraction_interval=-1,
        compaction_enabled=True,
        compaction_utilization=0.0,
        compaction_threshold=0.8,
    )
    manager = BackgroundTaskManager()
    coordinator = BackgroundWorkCoordinator(runtime, manager)
    budget_status = BudgetStatus(
        total_tokens=970,
        available_budget=1000,
        utilization_pct=97.0,
        overage_tokens=0,
        severity=BudgetSeverity.CRITICAL,
        message_tokens=970,
        tool_tokens=0,
    )

    coordinator.schedule_after_turn(
        turn_count=1,
        user_message="hello",
        assistant_message="Friday: hello",
        budget_status=budget_status,
    )
    await manager.wait_for_all()

    assert runtime.maintenance.actions[:2] == ["flush_pending_extraction", "compact"]
    assert runtime.compaction_task is None


async def test_background_compaction_summary_is_visible_to_summaries_command() -> None:
    runtime = _runtime(
        extraction_interval=-1,
        compaction_enabled=True,
        compaction_utilization=0.0,
        compaction_threshold=0.8,
    )
    manager = BackgroundTaskManager()
    coordinator = BackgroundWorkCoordinator(runtime, manager)
    budget_status = BudgetStatus(
        total_tokens=970,
        available_budget=1000,
        utilization_pct=97.0,
        overage_tokens=0,
        severity=BudgetSeverity.CRITICAL,
        message_tokens=970,
        tool_tokens=0,
    )

    coordinator.schedule_after_turn(
        turn_count=1,
        user_message="hello",
        assistant_message="Friday: hello",
        budget_status=budget_status,
    )
    await manager.wait_for_all()

    registry = build_default_registry()
    _, result = await registry.execute(
        "/summaries",
        RegistryCommandContext(runtime=runtime, registry=registry),
    )

    assert result is not None
    assert "Summaries:" in result.output
    assert "Compacted 2 FridayV2 test turns." in result.output


async def test_background_task_failure_reporting() -> None:
    async def fail() -> None:
        raise RuntimeError("background failed")

    manager = BackgroundTaskManager()
    manager.create_task(fail())

    await manager.wait_for_all()

    assert len(manager.failures) == 1
    assert str(manager.failures[0]) == "background failed"


async def test_background_shutdown_cancels_pending_tasks() -> None:
    async def wait_forever() -> None:
        await asyncio.sleep(60)

    manager = BackgroundTaskManager()
    manager.create_task(wait_forever())

    await manager.close()

    assert manager.closed is True
    assert manager.pending_count == 0
    assert manager.failures == []


@pytest.mark.parametrize("shutdown", [False, True])
async def test_cancelled_background_extraction_is_deferred_or_flushed_at_shutdown(
    shutdown: bool,
) -> None:
    runtime = _runtime(extraction_interval=0)
    manager = BackgroundTaskManager()
    gate = MaintenanceAdmissionGate()
    coordinator = BackgroundWorkCoordinator(runtime, manager, gate)
    entered = asyncio.Event()
    release = asyncio.Event()

    async def hold_exclusive() -> None:
        async with gate.exclusive("test-maintenance"):
            entered.set()
            await release.wait()

    exclusive = asyncio.create_task(hold_exclusive())
    await entered.wait()
    coordinator.schedule_after_turn(
        turn_count=1,
        user_message="cancelled",
        assistant_message="not admitted",
    )
    await asyncio.sleep(0)
    assert manager.pending_count == 3
    assert len(runtime.maintenance.pending_extraction) == 1
    pending = runtime.maintenance.pending_extraction[0]
    assert isinstance(pending, PendingExtractionTurn)
    assert pending.user_message == "cancelled"
    assert pending.assistant_message == "not admitted"
    assert pending.turn_id
    assert runtime.maintenance.background_actions == []

    hooks = AppMaintenanceRuntimeHooks(runtime, manager, coordinator)
    await hooks.prepare_for_manual_maintenance()
    if shutdown:
        await hooks.close_for_shutdown(snapshot_requested=True)
        assert runtime.maintenance.pending_extraction == []
        assert runtime.maintenance.actions[:2] == [
            "flush_pending_extraction",
            "flush_memory",
        ]
    else:
        drain_result = await hooks.drain_for_manual_maintenance()
        assert drain_result.buffered_extraction_count == 1
        assert drain_result.extraction_preempted is True
        assert runtime.maintenance.pending_extraction == [pending]
        assert runtime.maintenance.actions == ["flush_memory"]

    assert manager.pending_count == 0
    assert manager.failures == []
    assert manager.closed is shutdown

    release.set()
    await exclusive
    if not shutdown:
        resume_result = hooks.resume_after_manual_maintenance()
        assert resume_result.required is True
        assert resume_result.scheduled is True
        await manager.wait_for_all()
        assert runtime.maintenance.pending_extraction == []
        assert "extract:maintenance_resume:1" in (
            runtime.maintenance.background_actions
        )
        coordinator.schedule_after_turn(
            turn_count=2,
            user_message="admitted",
            assistant_message="processed",
        )
        await manager.wait_for_all()
        assert "extract:background_interval:1" in (
            runtime.maintenance.background_actions
        )


async def test_manual_maintenance_does_not_resume_normally_buffered_turns() -> None:
    runtime = _runtime(extraction_interval=3)
    manager = BackgroundTaskManager()
    coordinator = BackgroundWorkCoordinator(runtime, manager)
    pending = PendingExtractionTurn(
        turn_id="buffered-turn",
        user_message="queued",
        assistant_message="not yet due",
    )
    runtime.maintenance.pending_extraction = [pending]
    hooks = AppMaintenanceRuntimeHooks(runtime, manager, coordinator)

    await hooks.prepare_for_manual_maintenance()
    drain = await hooks.drain_for_manual_maintenance()
    resume = hooks.resume_after_manual_maintenance()

    assert drain.buffered_extraction_count == 1
    assert drain.extraction_preempted is False
    assert drain.warnings == (
        "1 extraction turn is buffered for the next configured trigger; "
        "no extraction task was running",
    )
    assert resume.required is False
    assert resume.scheduled is False
    assert runtime.maintenance.pending_extraction == [pending]
    assert coordinator.extraction_running is False


async def test_exit_maintenance_order_extracts_before_flush_lifecycle_reorganize() -> None:
    config = FridayChatConfig.model_validate(
        {
            "llm": {"model": "openai/test-chat-model"},
            "session": {
                "flush_on_exit": True,
                "lifecycle_on_exit": True,
                "reorganize_on_exit": True,
                "reorganize_mode": "deep",
            },
        }
    )
    runtime = build_runtime(config)
    app = FridayChatApp(
        runtime=runtime,
        input_source=ListInputSource([]),
        output_sink=ListOutputSink(),
    )

    result = await app.run()

    assert result.maintenance_actions == (
        "flush_pending_extraction",
        "flush_memory",
        "run_lifecycle",
        "reorganize_skipped:execute_disabled",
    )
