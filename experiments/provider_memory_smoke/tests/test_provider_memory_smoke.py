from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest

from experiments.provider_memory_smoke.runtime import (
    ProviderMemorySmokeResult,
    _load_runtime_config,
    _load_scenario_config,
    _persist_result_artifact,
    _result_profile_fields,
    run_provider_memory_smoke_experiment,
)


def _write_config(path: Path, body: str) -> None:
    path.write_text(body.strip(), encoding="utf-8")


def _base_runtime_yaml(tmp_path: Path) -> str:
    runtime_root = tmp_path / "runtime"
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
      model: gpt-4.1-mini
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
  chroma_path: {tmp_path / "chroma"}
  chroma_collection: provider_memory_smoke
  recall:
    semantic_retrieval_enabled: false
  extraction:
    enabled: true
    llm_service: extraction_primary
    embedding_service: embedding_primary
telemetry:
  enabled: false
  endpoint:
  debug_mode: false
agents:
  dir: experiments/provider_memory_smoke/agents
  role_bindings: {{}}
transcript:
  enabled: true
  backend: sqlite
  path: transcript/provider-memory-smoke.db
  capture_context_log: true
runtime_paths:
  install_root: .
  runtime_data_root: {runtime_root}
  workspace_root: .
  cache_root: {tmp_path / "cache"}
scratch:
  backend: in_memory
  path:
artifacts:
  enabled: true
  root_dir: artifacts
  lineage_required: true
  publish_on_task_success: true
"""


def _base_scenario_yaml() -> str:
    return """
agent_name: memory_probe
prompt: Configured scenario prompt
"""


def test_load_runtime_config_merges_local_overlay(tmp_path: Path) -> None:
    base_path = tmp_path / "runtime.yaml"
    local_path = tmp_path / "runtime.local.yaml"
    _write_config(base_path, _base_runtime_yaml(tmp_path))
    _write_config(
        local_path,
        """
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
""",
    )

    config = _load_runtime_config(
        debug_telemetry=False,
        base_config_path=base_path,
        local_config_path=local_path,
    )

    assert config.get_llm_service_config("agent_primary").api_key == "chat-key"
    assert config.get_llm_service_config("extraction_primary").api_key == "extraction-key"
    assert config.get_embedding_service_config("embedding_primary").api_key == "embed-key"
    assert config.prompting.base_system_prompt == "Runtime base prompt"
    assert config.transcript.enabled is True
    assert config.transcript.capture_context_log is True
    assert config.memory_extraction.llm_service == "extraction_primary"
    assert config.memory_extraction.embedding_service == "embedding_primary"
    assert config.memory_recall.semantic_retrieval_enabled is False


def test_load_scenario_config_reads_turn_input_from_scenario_file(tmp_path: Path) -> None:
    scenario_path = tmp_path / "scenario.yaml"
    _write_config(scenario_path, _base_scenario_yaml())

    scenario = _load_scenario_config(scenario_path)

    assert scenario.agent_name == "memory_probe"
    assert scenario.prompt == "Configured scenario prompt"


@pytest.mark.asyncio
async def test_provider_memory_smoke_reports_missing_local_overlay(tmp_path: Path) -> None:
    base_path = tmp_path / "runtime.yaml"
    scenario_path = tmp_path / "scenario.yaml"
    _write_config(base_path, _base_runtime_yaml(tmp_path))
    _write_config(scenario_path, _base_scenario_yaml())

    result = await run_provider_memory_smoke_experiment(
        prompt=None,
        preserve_artifacts=False,
        base_config_path=base_path,
        local_config_path=tmp_path / "missing-runtime.local.yaml",
        scenario_config_path=scenario_path,
    )

    assert result.success is False
    assert result.error is not None
    assert "Missing local runtime config overlay" in result.error
    assert result.runtime_base_system_prompt is None
    assert result.rendered_system_prompt is None
    assert result.composed_system_prompt is None
    assert result.agent_context_strategy is None


def test_result_profile_fields_include_layered_prompt_metadata() -> None:
    class StubProfile:
        role = "technical validation agent"
        goal = "Validate transcript capture"
        context_strategy = "minimal"
        llm_service = "agent_primary"
        temperature = 1.0

        def render_system_prompt(self) -> str:
            return "You are memory_probe. Role: technical validation agent."

    class StubAgent:
        profile = StubProfile()
        runtime_base_system_prompt = "Runtime base prompt"

    fields = _result_profile_fields(cast(Any, StubAgent()))

    assert fields["runtime_base_system_prompt"] == "Runtime base prompt"
    assert (
        fields["rendered_system_prompt"]
        == "You are memory_probe. Role: technical validation agent."
    )
    assert "Runtime base prompt" in cast(str, fields["composed_system_prompt"])
    assert fields["agent_role"] == "technical validation agent"
    assert fields["agent_goal"] == "Validate transcript capture"
    assert fields["agent_context_strategy"] == "minimal"
    assert fields["agent_llm_service"] == "agent_primary"
    assert fields["agent_temperature"] == 1.0


def test_result_to_dict_exposes_prompt_metadata() -> None:
    result = ProviderMemorySmokeResult(
        success=False,
        agent_name="memory_probe",
        session_id="session-1",
        prompt="user prompt",
        runtime_base_system_prompt="runtime base prompt",
        rendered_system_prompt="agent prompt",
        composed_system_prompt="runtime base prompt\n\nagent prompt",
        agent_role="Probe agent",
        agent_goal="Validate runtime behavior",
        agent_context_strategy="minimal",
        agent_llm_service="agent_primary",
        agent_temperature=1.0,
        response="",
        memory_profile="full",
        runtime_data_root="/tmp/runtime",
        chroma_path="/tmp/chroma",
        inference_llm_service="agent_primary",
        extraction_llm_service="extractor",
        embedding_service="embedding_primary",
        extraction_enabled=True,
        extracted_entities_count=0,
        extracted_relationships_count=0,
        extracted_insights_count=0,
        extracted_summaries_count=0,
        artifact_result_path=None,
        error="timeout",
    )

    payload = result.to_dict()

    assert payload["prompt"] == "user prompt"
    assert payload["runtime_base_system_prompt"] == "runtime base prompt"
    assert payload["rendered_system_prompt"] == "agent prompt"
    assert payload["composed_system_prompt"] == "runtime base prompt\n\nagent prompt"
    assert payload["agent_context_strategy"] == "minimal"


def test_persist_result_artifact_sets_embedded_artifact_path(tmp_path: Path) -> None:
    result = ProviderMemorySmokeResult(
        success=True,
        agent_name="memory_probe",
        session_id="session-1",
        prompt="user prompt",
        runtime_base_system_prompt="runtime base prompt",
        rendered_system_prompt="agent prompt",
        composed_system_prompt="runtime base prompt\n\nagent prompt",
        agent_role="Probe agent",
        agent_goal="Validate runtime behavior",
        agent_context_strategy="minimal",
        agent_llm_service="agent_primary",
        agent_temperature=1.0,
        response="ok",
        memory_profile="full",
        runtime_data_root="/tmp/runtime",
        chroma_path="/tmp/chroma",
        inference_llm_service="agent_primary",
        extraction_llm_service="extractor",
        embedding_service="embedding_primary",
        extraction_enabled=True,
        extracted_entities_count=1,
        extracted_relationships_count=0,
        extracted_insights_count=1,
        extracted_summaries_count=1,
        artifact_result_path=None,
        error=None,
    )

    original_dir = _persist_result_artifact.__globals__["ARTIFACTS_DIR"]
    _persist_result_artifact.__globals__["ARTIFACTS_DIR"] = tmp_path
    try:
        artifact_path = _persist_result_artifact(result)
    finally:
        _persist_result_artifact.__globals__["ARTIFACTS_DIR"] = original_dir

    payload = Path(artifact_path).read_text(encoding="utf-8")

    assert result.artifact_result_path == artifact_path
    assert artifact_path in payload
