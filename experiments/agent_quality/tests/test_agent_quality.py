from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from experiments.agent_quality.fake_llm import DEFAULT_PROMPT, DEFAULT_RESPONSE
from experiments.agent_quality.runtime import run_agent_quality_experiment

REPO_ROOT = Path(__file__).resolve().parents[3]

@pytest.mark.asyncio
async def test_run_agent_quality_experiment_success() -> None:
    result = await run_agent_quality_experiment()

    assert result.success is True
    assert result.agent_name == "quality_probe"
    assert result.prompt == DEFAULT_PROMPT
    assert result.response == DEFAULT_RESPONSE
    assert result.session_id
    assert result.error is None


@pytest.mark.asyncio
async def test_run_agent_quality_experiment_unknown_agent() -> None:
    result = await run_agent_quality_experiment(agent_name="missing_agent")

    assert result.success is False
    assert result.agent_name == "missing_agent"
    assert result.error is not None
    assert "missing_agent" in result.error


def test_run_script_json_output() -> None:
    completed = subprocess.run(
        [sys.executable, "experiments/agent_quality/run.py", "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["success"] is True
    assert payload["agent_name"] == "quality_probe"
    assert payload["response"] == DEFAULT_RESPONSE
