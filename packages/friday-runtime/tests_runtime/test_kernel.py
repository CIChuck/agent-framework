# mypy: ignore-errors
# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
import warnings
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from friday_agent import CopilotAgent, InteractiveAgent
from friday_core.profiles import MemoryProfile
from friday_runtime.config import (
    LLMServiceConfig,
    RuntimeConfig,
    ToolProviderConfig,
    ToolProvidersConfig,
    ToolsConfig,
)
from friday_runtime.kernel import RuntimeKernel
from friday_telemetry.providers.debug import DebugTelemetryRecorder


def _runtime_config(
    tmp_path: Path,
    agents_dir: Path,
    strict: bool = False,
    debug_mode: bool = False,
    tools_config: ToolsConfig | None = None,
    workflows_dir: Path | None = None,
) -> RuntimeConfig:
    install_root = tmp_path / "install"
    runtime_data_root = tmp_path / "runtime-data" / "friday"
    workspace_root = tmp_path / "workspace"
    install_root.mkdir(parents=True)
    runtime_data_root.parent.mkdir(parents=True)
    workspace_root.mkdir(parents=True)

    return RuntimeConfig(
        install_root=str(install_root),
        runtime_data_root=str(runtime_data_root),
        workspace_root=str(workspace_root),
        agents_dir=str(agents_dir),
        workflows_dir=str(workflows_dir) if workflows_dir is not None else None,
        strict_agent_llm_binding=strict,
        debug_mode=debug_mode,
        tools_config=tools_config or ToolsConfig(),
        llm_pool_default_service="default",
        llm_pool_services={
            "default": LLMServiceConfig(
                provider="openai",
                model="gpt-4o-mini",
                api_key="test-key",
            )
        },
    )


def _disable_tool_bootstrap(kernel: RuntimeKernel) -> None:
    kernel._di.tool_registry = MagicMock()
    kernel._di._create_tool_registry = lambda: None


@pytest.mark.asyncio
async def test_kernel_start_fails_on_unknown_agent_llm_service(tmp_path: Path):
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "researcher.yaml").write_text(
        """
name: researcher
role: "Researcher"
goal: "Find information"
system_prompt: "You are a researcher."
llm_service: missing
""".strip()
    )

    kernel = RuntimeKernel(
        config=_runtime_config(tmp_path, agents_dir),
        memory_profile=MemoryProfile.TESTING,
    )
    _disable_tool_bootstrap(kernel)

    with pytest.raises(ValueError, match="unknown llm_service"):
        await kernel.start()


@pytest.mark.asyncio
async def test_kernel_start_fails_when_strict_binding_requires_llm_service(
    tmp_path: Path,
):
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "researcher.yaml").write_text(
        """
name: researcher
role: "Researcher"
goal: "Find information"
system_prompt: "You are a researcher."
""".strip()
    )

    kernel = RuntimeKernel(
        config=_runtime_config(tmp_path, agents_dir, strict=True),
        memory_profile=MemoryProfile.TESTING,
    )
    _disable_tool_bootstrap(kernel)

    with pytest.raises(ValueError, match="must declare llm_service"):
        await kernel.start()


@pytest.mark.asyncio
async def test_kernel_start_fails_on_unregistered_agent_type(tmp_path: Path):
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "researcher.yaml").write_text(
        """
name: researcher
role: "Researcher"
goal: "Find information"
system_prompt: "You are a researcher."
llm_service: default
agent_type: custom
""".strip()
    )

    kernel = RuntimeKernel(
        config=_runtime_config(tmp_path, agents_dir),
        memory_profile=MemoryProfile.TESTING,
    )
    _disable_tool_bootstrap(kernel)

    with pytest.raises(ValueError, match="Unregistered agent_type"):
        await kernel.start()


@pytest.mark.asyncio
async def test_kernel_start_fails_when_agent_references_unloaded_tool(tmp_path: Path):
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "researcher.yaml").write_text(
        """
name: researcher
role: "Researcher"
goal: "Find information"
system_prompt: "You are a researcher."
llm_service: default
agent_type: interactive
tools:
  - web_search
""".strip()
    )

    kernel = RuntimeKernel(
        config=_runtime_config(tmp_path, agents_dir),
        memory_profile=MemoryProfile.TESTING,
    )

    with pytest.raises(ValueError, match="unavailable tool"):
        await kernel.start()


@pytest.mark.asyncio
async def test_kernel_start_succeeds_when_runtime_loads_declared_friday_tool(
    tmp_path: Path,
):
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "researcher.yaml").write_text(
        """
name: researcher
role: "Researcher"
goal: "Find information"
system_prompt: "You are a researcher."
llm_service: default
agent_type: interactive
tools:
  - web_search
""".strip()
    )

    kernel = RuntimeKernel(
        config=_runtime_config(
            tmp_path,
            agents_dir,
            tools_config=ToolsConfig(
                providers=ToolProvidersConfig(
                    builtin=ToolProviderConfig(enabled=True),
                    friday_tools=ToolProviderConfig(
                        enabled=True,
                        mode="selected",
                        include_tools=("web_search",),
                    ),
                )
            ),
        ),
        memory_profile=MemoryProfile.TESTING,
    )
    await kernel.start()

    try:
        assert "web_search" in kernel.tool_registry.list_names()
    finally:
        await kernel.stop()


@pytest.mark.asyncio
async def test_kernel_create_agent_uses_interactive_factory_mapping(tmp_path: Path):
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "researcher.yaml").write_text(
        """
name: researcher
role: "Researcher"
goal: "Find information"
system_prompt: "You are a researcher."
llm_service: default
agent_type: interactive
""".strip()
    )

    kernel = RuntimeKernel(
        config=_runtime_config(tmp_path, agents_dir),
        memory_profile=MemoryProfile.TESTING,
    )
    _disable_tool_bootstrap(kernel)
    await kernel.start()

    try:
        agent = kernel.agent_registry.create_agent("researcher")
        assert isinstance(agent, InteractiveAgent)
        assert not isinstance(agent, CopilotAgent)

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            compat_agent = kernel.get_copilot_agent()

        assert isinstance(compat_agent, CopilotAgent)
        assert any("deprecated" in str(w.message).lower() for w in caught)
    finally:
        await kernel.stop()


@pytest.mark.asyncio
async def test_kernel_execute_workflow_uses_canonical_pipeline_path(tmp_path: Path):
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    workflows_root = tmp_path / "workflows"
    workflows_dir = workflows_root / "wf_research"
    pipelines_dir = workflows_dir / "pipelines"
    pipelines_dir.mkdir(parents=True)
    (agents_dir / "researcher.yaml").write_text(
        """
name: researcher
role: "Researcher"
goal: "Find information"
system_prompt: "You are a researcher."
llm_service: default
agent_type: interactive
""".strip()
    )
    (agents_dir / "synthesizer.yaml").write_text(
        """
name: synthesizer
role: "Synthesizer"
goal: "Synthesize findings"
system_prompt: "You are a synthesizer."
llm_service: default
agent_type: interactive
""".strip()
    )
    (workflows_dir / "workflow.yaml").write_text(
        """
workflow_id: wf_research
version: 1.0.0
name: Research
goal: Produce report
pipeline_refs:
  - pl_research
  - pl_synthesis
entry_pipeline_id: pl_research
""".strip()
    )
    (pipelines_dir / "pl_research.yaml").write_text(
        """
pipeline_id: pl_research
version: 1.0.0
workflow_id: wf_research
goal: Research
upstream_pipeline_ids: []
input_contract:
  source_paths: list[str]
output_contract:
  evidence_bundle: json
tasks:
  - task_id: collect_sources
    name: Collect Sources
    description: Collect sources.
    owner_agent_id: researcher
    input_contract:
      source_paths: list[str]
    output_contract:
      evidence_bundle: json
""".strip()
    )
    (pipelines_dir / "pl_synthesis.yaml").write_text(
        """
pipeline_id: pl_synthesis
version: 1.0.0
workflow_id: wf_research
goal: Synthesize
upstream_pipeline_ids:
  - pl_research
input_contract:
  evidence_bundle: json
output_contract:
  recommendation_report: markdown
tasks:
  - task_id: produce_recommendations
    name: Produce Recommendations
    description: Produce recommendation report.
    owner_role: synthesis
    input_contract:
      evidence_bundle: json
    output_contract:
      recommendation_report: markdown
""".strip()
    )

    config = _runtime_config(tmp_path, agents_dir, workflows_dir=workflows_root)
    config.workflow_mode = "canonical"
    config.agents_role_bindings = {"synthesis": "synthesizer"}

    kernel = RuntimeKernel(
        config=config,
        memory_profile=MemoryProfile.TESTING,
    )
    _disable_tool_bootstrap(kernel)
    await kernel.start()

    try:
        mock_orchestrator = MagicMock()
        mock_orchestrator.delegate = AsyncMock(
            side_effect=[
                {"evidence_bundle": {"sources": 2}},
                {"recommendation_report": "# Recommendation"},
            ]
        )
        mock_orchestrator.set_session = AsyncMock()
        kernel._orchestrator = mock_orchestrator

        execution = await kernel.execute_workflow(
            "wf_research",
            {"source_paths": ["a.md"]},
        )

        assert execution.status.value == "completed"
        assert execution.execution_id
        assert execution.variables["recommendation_report"] == "# Recommendation"
        assert execution.execution_id == mock_orchestrator.set_session.await_args.args[0]
        assert mock_orchestrator.delegate.call_args_list[1].args[0] == "synthesizer"
    finally:
        await kernel.stop()


@pytest.mark.asyncio
async def test_kernel_execute_workflow_legacy_mode_uses_adapter_and_emits_routing_event(
    tmp_path: Path,
):
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    workflows_dir = tmp_path / "workflows"
    workflows_dir.mkdir(parents=True)
    (agents_dir / "researcher.yaml").write_text(
        """
name: researcher
role: "Researcher"
goal: "Find information"
system_prompt: "You are a researcher."
llm_service: default
agent_type: interactive
""".strip()
    )
    (agents_dir / "writer.yaml").write_text(
        """
name: writer
role: "Writer"
goal: "Write final output"
system_prompt: "You are a writer."
llm_service: default
agent_type: interactive
""".strip()
    )
    (workflows_dir / "legacy_brief.yaml").write_text(
        """
id: legacy_brief
name: Legacy Brief
description: Produce a brief.
tasks:
  - id: gather
    name: Gather
    description: Gather notes.
    agent: researcher
    inputs:
      topic: $topic
      mode: deep
    outputs:
      - notes
  - id: write
    name: Write
    description: Write the brief.
    agent: writer
    depends_on:
      - gather
    inputs:
      notes: $notes
    outputs:
      - brief
""".strip()
    )

    config = _runtime_config(
        tmp_path,
        agents_dir,
        debug_mode=True,
        workflows_dir=workflows_dir,
    )
    config.workflow_mode = "legacy"

    kernel = RuntimeKernel(
        config=config,
        memory_profile=MemoryProfile.TESTING,
    )
    _disable_tool_bootstrap(kernel)
    await kernel.start()

    try:
        assert isinstance(kernel.telemetry, DebugTelemetryRecorder)
        mock_orchestrator = MagicMock()
        mock_orchestrator.delegate = AsyncMock(
            side_effect=[
                {"notes": "notes"},
                {"brief": "# Brief"},
            ]
        )
        mock_orchestrator.set_session = AsyncMock()
        kernel._orchestrator = mock_orchestrator

        execution = await kernel.execute_workflow(
            "legacy_brief",
            {"topic": "phase 4"},
        )

        assert execution.status.value == "completed"
        assert execution.execution_id == mock_orchestrator.set_session.await_args.args[0]
        assert execution.variables["brief"] == "# Brief"
        first_prompt = mock_orchestrator.delegate.call_args_list[0].args[1]
        assert "- mode: deep" in first_prompt
        routing_event = kernel.telemetry.get_event("workflow_mode_selected")
        assert routing_event == {
            "workflow_name": "legacy_brief",
            "requested_mode": "legacy",
            "resolved_mode": "legacy_adapter",
        }
    finally:
        await kernel.stop()
