from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from experiments.workflow_artifact_smoke import runtime as workflow_runtime
from experiments.workflow_artifact_smoke.runtime import (
    WorkflowArtifactSmokeResult,
    _load_runtime_config,
    _load_scenario_config,
    _persist_result_artifact,
    run_workflow_artifact_smoke_experiment,
)


def _write_config(path: Path, body: str) -> None:
    path.write_text(body.strip(), encoding="utf-8")


def _base_runtime_yaml(tmp_path: Path) -> str:
    (tmp_path / "runtime_data" / "cache").mkdir(parents=True, exist_ok=True)
    (tmp_path / "runtime_data" / "memory").mkdir(parents=True, exist_ok=True)
    (tmp_path / "outputs").mkdir(parents=True, exist_ok=True)
    return f"""
config_policy:
  allow_env_override: false
  strict_agent_llm_binding: false
  workflow_mode: canonical
  unknown_key_policy: fail
prompting:
  base_system_prompt: Runtime base prompt
llm:
  provider: openai
  model: gpt-4o-mini
llm_pool:
  default_service: agent_primary
  services:
    agent_primary:
      provider: openai
      model: gpt-4o-mini
      api_base: https://example.invalid/v1
    extraction_primary:
      provider: openai
      model: gpt-4o-mini
      api_base: https://example.invalid/v1
embedding:
  model: text-embedding-3-small
embedding_pool:
  default_service: embedding_primary
  services:
    embedding_primary:
      provider: openai
      model: text-embedding-3-small
      api_base: https://example.invalid/v1
memory:
  mode: single_agent
  chroma_path: {tmp_path / "runtime_data" / "memory" / "chroma"}
  chroma_collection: workflow_artifact_smoke
  recall:
    semantic_retrieval_enabled: true
  extraction:
    enabled: true
    llm_service: extraction_primary
    embedding_service: embedding_primary
telemetry:
  enabled: false
  endpoint:
  debug_mode: false
agents:
  dir: experiments/workflow_artifact_smoke/agents
  role_bindings: {{}}
workflows:
  dir: experiments/workflow_artifact_smoke/workflows
tools:
  providers:
    builtin:
      enabled: true
      mode: all
    friday_tools:
      enabled: true
      mode: selected
      include_tools:
        - web_search
        - web_reader
        - file_write
    mcp:
      enabled: false
      mode: selected
      config:
        auto_connect: false
        tool_name_prefix: mcp_
        servers: []
transcript:
  enabled: true
  backend: sqlite
  path: transcripts/workflow-artifact-smoke.db
  capture_context_log: true
runtime_paths:
  install_root: {tmp_path}
  runtime_data_root: {tmp_path / "runtime_data"}
  workspace_root: {tmp_path / "outputs"}
  cache_root: {tmp_path / "runtime_data" / "cache"}
scratch:
  backend: in_memory
  path:
artifacts:
  enabled: true
  root_dir: artifacts
  lineage_required: true
  publish_on_task_success: true
"""


def _local_runtime_yaml() -> str:
    return """
llm_pool:
  services:
    agent_primary:
      api_key: chat-key
    extraction_primary:
      api_key: extraction-key
embedding_pool:
  services:
    embedding_primary:
      api_key: embed-key
"""


def _scenario_yaml() -> str:
    return """
workflow_name: wf_agentic_news
query: agentic AI news
output_filename: summary_report.md
"""


def test_load_runtime_config_reads_workflows_dir(tmp_path: Path) -> None:
    base_path = tmp_path / "runtime.yaml"
    local_path = tmp_path / "runtime.local.yaml"
    _write_config(base_path, _base_runtime_yaml(tmp_path))
    _write_config(local_path, _local_runtime_yaml())

    config = _load_runtime_config(
        debug_telemetry=False,
        base_config_path=base_path,
        local_config_path=local_path,
    )

    assert config.workflows.dir == "experiments/workflow_artifact_smoke/workflows"
    assert config.agents.dir == "experiments/workflow_artifact_smoke/agents"
    assert config.get_llm_service_config("agent_primary").api_key == "chat-key"


def test_load_scenario_config_reads_workflow_inputs(tmp_path: Path) -> None:
    scenario_path = tmp_path / "scenario.yaml"
    _write_config(scenario_path, _scenario_yaml())

    scenario = _load_scenario_config(scenario_path)

    assert scenario.workflow_name == "wf_agentic_news"
    assert scenario.query == "agentic AI news"
    assert scenario.output_filename == "summary_report.md"


@pytest.mark.asyncio
async def test_workflow_artifact_smoke_reports_missing_local_overlay(
    tmp_path: Path,
) -> None:
    base_path = tmp_path / "runtime.yaml"
    scenario_path = tmp_path / "scenario.yaml"
    _write_config(base_path, _base_runtime_yaml(tmp_path))
    _write_config(scenario_path, _scenario_yaml())

    result = await run_workflow_artifact_smoke_experiment(
        preserve_artifacts=False,
        base_config_path=base_path,
        local_config_path=tmp_path / "missing-runtime.local.yaml",
        scenario_config_path=scenario_path,
    )

    assert result.success is False
    assert result.error is not None
    assert "Missing local runtime config overlay" in result.error


@pytest.mark.asyncio
async def test_workflow_artifact_smoke_success_with_mocked_runtime(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    base_path = tmp_path / "runtime.yaml"
    local_path = tmp_path / "runtime.local.yaml"
    scenario_path = tmp_path / "scenario.yaml"
    _write_config(base_path, _base_runtime_yaml(tmp_path))
    _write_config(local_path, _local_runtime_yaml())
    _write_config(scenario_path, _scenario_yaml())

    class FakeKernel:
        def __init__(self, config: Any, memory_profile: Any) -> None:
            self.config = config
            self.memory_profile = memory_profile

        async def start(self) -> None:
            return None

        async def stop(self) -> None:
            return None

        async def execute_workflow(
            self,
            workflow_name: str,
            initial_inputs: dict[str, Any] | None = None,
        ) -> Any:
            assert initial_inputs is not None
            output_path = Path(str(initial_inputs["output_path"]))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                (
                    "Agentic AI is moving from demos into operational systems.\n\n"
                    "The selected article argues that orchestration quality, tooling, and governance "
                    "are becoming the practical differentiators.\n\n"
                    "It also frames the story as a broader industry shift visible in current reporting "
                    "from Example News."
                ),
                encoding="utf-8",
            )
            return SimpleNamespace(
                execution_id="wf_agentic_news_session",
                status=SimpleNamespace(value="completed"),
                variables={
                    "selected_article": json.dumps(
                        {
                            "title": "Example Agentic AI Article",
                            "url": "https://example.com/agentic-ai",
                            "source": "Example News",
                            "published_at": "2026-03-16",
                            "article_notes": "Structured notes about the article.",
                            "selection_rationale": "Most recent reputable result in the search set.",
                        }
                    ),
                    "summary_report": str(output_path),
                },
                published_artifacts={
                    "summary_report": SimpleNamespace(
                        provenance={"output_ref": str(output_path)}
                    )
                },
            )

    async def fake_collect_transcript_summary(
        *,
        transcript_path: Path,
        session_id: str | None,
    ) -> dict[str, Any]:
        transcript_path.parent.mkdir(parents=True, exist_ok=True)
        transcript_path.write_text("placeholder", encoding="utf-8")
        return {
            "transcript_exists": True,
            "transcript_entry_count": 2,
            "transcript_agent_ids": ["researcher", "writer"],
            "transcript_tool_call_count": 3,
        }

    monkeypatch.setattr(workflow_runtime, "RuntimeKernel", FakeKernel)
    monkeypatch.setattr(
        workflow_runtime,
        "_collect_transcript_summary",
        fake_collect_transcript_summary,
    )

    result = await run_workflow_artifact_smoke_experiment(
        preserve_artifacts=False,
        base_config_path=base_path,
        local_config_path=local_path,
        scenario_config_path=scenario_path,
    )

    assert result.success is True
    assert result.workflow_name == "wf_agentic_news"
    assert result.execution_id == "wf_agentic_news_session"
    assert result.output_exists is True
    assert result.output_paragraph_count == 3
    assert result.selected_article_valid_json is True
    assert result.selected_article_source == "Example News"
    assert result.summary_artifact_present is True
    assert result.transcript_entry_count == 2
    assert result.memory_root_exists is True


def test_persist_result_artifact_sets_embedded_artifact_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(workflow_runtime, "ARTIFACTS_DIR", tmp_path / "artifacts")
    result = WorkflowArtifactSmokeResult(
        success=True,
        workflow_name="wf_agentic_news",
        execution_id="session-1",
        session_id="session-1",
        query="agentic AI news",
        output_filename="summary_report.md",
        output_path="/tmp/summary_report.md",
        output_exists=True,
        output_paragraph_count=3,
        output_mentions_source=True,
        selected_article_title="Example",
        selected_article_url="https://example.com/article",
        selected_article_source="Example News",
        selected_article_published_at="2026-03-16",
        selected_article_valid_json=True,
        summary_artifact_present=True,
        summary_artifact_output_ref="/tmp/summary_report.md",
        transcript_path="/tmp/transcript.db",
        transcript_exists=True,
        transcript_entry_count=2,
        transcript_agent_ids=["researcher", "writer"],
        transcript_tool_call_count=3,
        chroma_path="/tmp/chroma",
        graph_path="/tmp/graph.json",
        memory_root="/tmp/memory",
        memory_root_exists=True,
        artifact_result_path=None,
        error=None,
    )

    artifact_path = _persist_result_artifact(result)

    payload = json.loads(Path(artifact_path).read_text(encoding="utf-8"))
    assert payload["artifact_result_path"] == artifact_path
    assert payload["summary_artifact_output_ref"] == "/tmp/summary_report.md"
