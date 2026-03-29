"""Runtime harness for the direct-agent quality experiment."""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast

from friday_agent import DefaultToolRegistry, InteractiveAgent
from friday_core.profiles import MemoryProfile
from friday_runtime.config import RuntimeConfig
from friday_runtime.kernel import RuntimeKernel

from experiments.agent_quality.fake_llm import (
    DEFAULT_PROMPT,
    DEFAULT_RESPONSE,
    DeterministicLLMClient,
)

EXPERIMENT_ROOT = Path(__file__).resolve().parent
RUNTIME_CONFIG_PATH = EXPERIMENT_ROOT / "config" / "runtime.yaml"
DEFAULT_AGENT_NAME = "quality_probe"


@dataclass
class AgentQualityExperimentResult:
    success: bool
    agent_name: str
    session_id: str | None
    prompt: str
    response: str
    llm_mode: str
    telemetry_enabled: bool
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _experiment_agents_dir() -> Path:
    return EXPERIMENT_ROOT / "agents"


def _load_runtime_config(runtime_root: Path, debug_telemetry: bool) -> RuntimeConfig:
    install_root = runtime_root / "install"
    runtime_data_root = runtime_root / "runtime-data" / "friday"
    workspace_root = runtime_root / "workspace"

    install_root.mkdir(parents=True, exist_ok=True)
    runtime_data_root.parent.mkdir(parents=True, exist_ok=True)
    workspace_root.mkdir(parents=True, exist_ok=True)

    return RuntimeConfig.from_sources(
        yaml_path=RUNTIME_CONFIG_PATH,
        overrides={
            "install_root": str(install_root),
            "runtime_data_root": str(runtime_data_root),
            "workspace_root": str(workspace_root),
            "debug_mode": debug_telemetry,
            "agents_dir": str(_experiment_agents_dir()),
        },
    )


def _install_experiment_tool_registry(kernel: RuntimeKernel) -> None:
    """Avoid unrelated tool-discovery failures for the no-tools smoke path."""

    def create_tool_registry() -> None:
        kernel._di.tool_registry = DefaultToolRegistry()

    cast(Any, kernel._di)._create_tool_registry = create_tool_registry


def _install_deterministic_llm(kernel: RuntimeKernel, prompt: str) -> None:
    fake_llm = DeterministicLLMClient(response_map={prompt: DEFAULT_RESPONSE})
    kernel._di.llm_pool["deterministic"] = fake_llm
    kernel._di.llm = fake_llm


async def run_agent_quality_experiment(
    *,
    prompt: str = DEFAULT_PROMPT,
    agent_name: str = DEFAULT_AGENT_NAME,
    debug_telemetry: bool = False,
) -> AgentQualityExperimentResult:
    runtime_root = Path(tempfile.mkdtemp(prefix="friday-agent-quality-"))
    kernel = RuntimeKernel(
        config=_load_runtime_config(runtime_root, debug_telemetry),
        memory_profile=MemoryProfile.TESTING,
    )
    _install_experiment_tool_registry(kernel)

    session_id: str | None = None
    try:
        await kernel.start()
        _install_deterministic_llm(kernel, prompt)

        session_id = await kernel.create_session(user_id="experiment")
        agent = kernel.spawn_agent(agent_name)
        if not isinstance(agent, InteractiveAgent):
            raise TypeError(
                f"Experiment agent '{agent_name}' did not resolve to InteractiveAgent"
            )

        await agent.initialize_session(session_id=session_id, user_id="experiment")
        response = await agent.run(prompt)

        return AgentQualityExperimentResult(
            success=True,
            agent_name=agent_name,
            session_id=agent.session_id,
            prompt=prompt,
            response=response,
            llm_mode="deterministic",
            telemetry_enabled=kernel.telemetry is not None,
            error=None,
        )
    except Exception as exc:
        return AgentQualityExperimentResult(
            success=False,
            agent_name=agent_name,
            session_id=session_id,
            prompt=prompt,
            response="",
            llm_mode="deterministic",
            telemetry_enabled=kernel.telemetry is not None,
            error=str(exc),
        )
    finally:
        try:
            await kernel.stop()
        finally:
            shutil.rmtree(runtime_root, ignore_errors=True)
