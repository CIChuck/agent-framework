from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from experiments.prompt_transcript_audit.fake_llm import (
    DEFAULT_PROMPT,
    DEFAULT_RESPONSE,
)
from experiments.prompt_transcript_audit.runtime import (
    run_prompt_transcript_audit_experiment,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.asyncio
async def test_run_prompt_transcript_audit_experiment_success() -> None:
    result = await run_prompt_transcript_audit_experiment(preserve_artifacts=False)

    assert result.success is True
    assert result.agent_name == "audit_probe"
    assert result.prompt == DEFAULT_PROMPT
    assert result.response == DEFAULT_RESPONSE
    assert result.session_id
    assert result.transcript_entry_persisted is True
    assert result.prompt_metadata_persisted is True
    assert result.capture_context_log_enabled is True
    assert result.context_log_present is True
    assert result.context_log_matches_composed_prompt is True
    assert result.context_log_matches_response is True
    assert result.error is None


@pytest.mark.asyncio
async def test_run_prompt_transcript_audit_without_context_log() -> None:
    result = await run_prompt_transcript_audit_experiment(
        preserve_artifacts=False,
        runtime_overrides={"transcript_capture_context_log": False},
    )

    assert result.success is True
    assert result.capture_context_log_enabled is False
    assert result.transcript_entry_persisted is True
    assert result.context_log_present is False
    assert result.context_log_matches_composed_prompt is False
    assert result.context_log_matches_response is False


@pytest.mark.asyncio
async def test_run_prompt_transcript_audit_unknown_agent() -> None:
    result = await run_prompt_transcript_audit_experiment(
        agent_name="missing_agent",
        preserve_artifacts=False,
    )

    assert result.success is False
    assert result.agent_name == "missing_agent"
    assert result.error is not None
    assert "missing_agent" in result.error


def test_run_script_json_output() -> None:
    completed = subprocess.run(
        [sys.executable, "experiments/prompt_transcript_audit/run.py", "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["success"] is True
    assert payload["agent_name"] == "audit_probe"
    assert payload["response"] == DEFAULT_RESPONSE
    assert payload["context_log_present"] is True
