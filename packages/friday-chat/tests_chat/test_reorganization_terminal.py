"""Terminal lifecycle safety for the Friday Chat maintenance boundary."""

from __future__ import annotations

import os
import platform
import pty
import select
import subprocess
import sys
import textwrap
import time

import pytest
from friday_chat.app import FridayChatApp, ListInputSource
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import FakeTranscriptStore, build_runtime

DARWIN_ONLY = pytest.mark.skipif(
    platform.system() != "Darwin",
    reason="provider-free maintenance PTY is verified on the supported platform",
)


async def test_app_shutdown_closes_admission_and_finalizes_without_artifacts() -> None:
    runtime = build_runtime(
        FridayChatConfig.model_validate(
            {"llm": {"model": "openai/test-chat-model"}}
        )
    )
    app = FridayChatApp(runtime=runtime, input_source=ListInputSource([]))

    result = await app.run()

    assert result.exit_reason == "eof"
    assert app.background.closed
    assert app.maintenance_gate.snapshot.accepting_shared is False
    assert isinstance(runtime.transcript, FakeTranscriptStore)
    assert runtime.transcript.finalized
    assert not runtime.maintenance_layout.recovery_root.exists()
    assert not runtime.maintenance_layout.log_root.exists()


@DARWIN_ONLY
def test_provider_free_pty_acknowledges_before_bounded_progress_completes() -> None:
    script = textwrap.dedent(
        """
        import asyncio

        from friday_chat.app import ConsoleOutputSink, FridayChatApp, ListInputSource
        from friday_chat.config import FridayChatConfig
        from friday_chat.reorganization import (
            ProgressStep,
            ReorganizationResult,
            ResultStatus,
        )
        from friday_chat.reorganization.coordinator import ReorganizationCoordinator
        from friday_chat.runtime import build_runtime

        async def slow_provider_free_run(self, request, *, progress=None):
            if progress is not None:
                await progress(ProgressStep.PREFLIGHT, "Inspecting provider-free backup")
            await asyncio.sleep(1.0)
            if progress is not None:
                await progress(ProgressStep.COMPLETE, "Provider-free backup preview complete")
            return ReorganizationResult(
                status=ResultStatus.DRY_RUN_COMPLETE,
                trigger=request.trigger,
                mode=request.mode,
                attempted_steps=[ProgressStep.PREFLIGHT, ProgressStep.COMPLETE],
                completed_steps=[ProgressStep.PREFLIGHT, ProgressStep.COMPLETE],
            )

        ReorganizationCoordinator.run = slow_provider_free_run
        runtime = build_runtime(
            FridayChatConfig.model_validate(
                {
                    "llm": {"model": "openai/test-chat-model"},
                    "memory": {"persist_directory": "./synthetic-vector"},
                }
            )
        )
        app = FridayChatApp(
            runtime=runtime,
            input_source=ListInputSource(["/reorganize --backup"]),
            output_sink=ConsoleOutputSink(),
        )
        asyncio.run(app.run())
        """
    )
    master, slave = pty.openpty()
    process = subprocess.Popen(
        [sys.executable, "-c", script],
        stdin=subprocess.DEVNULL,
        stdout=slave,
        stderr=slave,
        close_fds=True,
    )
    os.close(slave)
    captured = bytearray()
    deadline = time.monotonic() + 0.8
    try:
        while time.monotonic() < deadline:
            ready, _, _ = select.select([master], [], [], 0.05)
            if ready:
                chunk = os.read(master, 4096)
                if not chunk:
                    break
                captured.extend(chunk)
                if b"Reorganization accepted:" in captured:
                    break
        early_output = captured.decode("utf-8", errors="replace")
        assert "Reorganization accepted: mode=backup; dry_run=true" in early_output
        assert "Status: dry_run_complete" not in early_output
        assert process.poll() is None

        completion_deadline = time.monotonic() + 3.0
        while (
            b"Status: dry_run_complete" not in captured
            and time.monotonic() < completion_deadline
        ):
            ready, _, _ = select.select([master], [], [], 0.05)
            if not ready:
                continue
            try:
                chunk = os.read(master, 4096)
            except OSError:
                break
            if not chunk:
                break
            captured.extend(chunk)
        process.wait(timeout=5)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        os.close(master)

    output = captured.decode("utf-8", errors="replace")
    assert process.returncode == 0
    assert "Status: dry_run_complete" in output
    assert 1 <= output.count("Reorganization progress") <= 24
    assert "synthetic memory" not in output
    assert "transcript content" not in output
