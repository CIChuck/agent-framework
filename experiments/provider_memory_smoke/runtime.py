"""Runtime harness for the provider-backed memory smoke experiment."""

from __future__ import annotations

import asyncio
import importlib
import json
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from friday_agent import DefaultToolRegistry, InteractiveAgent
from friday_agent.prompting import compose_system_prompt
from friday_core.profiles import MemoryProfile
from friday_runtime.config import RuntimeConfig
from friday_runtime.kernel import RuntimeKernel

yaml = cast(Any, importlib.import_module("yaml"))

EXPERIMENT_ROOT = Path(__file__).resolve().parent
BASE_RUNTIME_CONFIG_PATH = EXPERIMENT_ROOT / "config" / "runtime.yaml"
LOCAL_RUNTIME_CONFIG_PATH = EXPERIMENT_ROOT / "config" / "runtime.local.yaml"
SCENARIO_CONFIG_PATH = EXPERIMENT_ROOT / "config" / "scenario.yaml"
LOCAL_RUNTIME_CONFIG_EXAMPLE_PATH = (
    EXPERIMENT_ROOT / "config" / "runtime.local.yaml.example"
)
ARTIFACTS_DIR = EXPERIMENT_ROOT / "artifacts"


@dataclass(frozen=True)
class ProviderMemorySmokeScenarioConfig:
    agent_name: str
    prompt: str


@dataclass
class ProviderMemorySmokeResult:
    success: bool
    agent_name: str
    session_id: str | None
    prompt: str
    runtime_base_system_prompt: str | None
    rendered_system_prompt: str | None
    composed_system_prompt: str | None
    agent_role: str | None
    agent_goal: str | None
    agent_context_strategy: str | None
    agent_llm_service: str | None
    agent_temperature: float | None
    response: str
    memory_profile: str
    runtime_data_root: str
    chroma_path: str
    inference_llm_service: str
    extraction_llm_service: str | None
    embedding_service: str | None
    extraction_enabled: bool
    extracted_entities_count: int
    extracted_relationships_count: int
    extracted_insights_count: int
    extracted_summaries_count: int
    artifact_result_path: str | None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _result_profile_fields(agent: InteractiveAgent | None) -> dict[str, Any]:
    if agent is None:
        return {
            "runtime_base_system_prompt": None,
            "rendered_system_prompt": None,
            "composed_system_prompt": None,
            "agent_role": None,
            "agent_goal": None,
            "agent_context_strategy": None,
            "agent_llm_service": None,
            "agent_temperature": None,
        }

    profile = agent.profile
    prompt_composition = compose_system_prompt(
        profile=profile,
        runtime_base_prompt=agent.runtime_base_system_prompt,
    )
    return {
        "runtime_base_system_prompt": prompt_composition.runtime_base_prompt,
        "rendered_system_prompt": prompt_composition.agent_prompt,
        "composed_system_prompt": prompt_composition.composed_system_prompt,
        "agent_role": profile.role,
        "agent_goal": profile.goal,
        "agent_context_strategy": profile.context_strategy,
        "agent_llm_service": profile.llm_service,
        "agent_temperature": profile.temperature,
    }


def _experiment_agents_dir() -> Path:
    return EXPERIMENT_ROOT / "agents"


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Runtime config must be a mapping: {path}")
    return cast(dict[str, Any], payload)


def _deep_merge(target: dict[str, Any], source: dict[str, Any]) -> None:
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_merge(cast(dict[str, Any], target[key]), value)
        else:
            target[key] = value


def _load_merged_config_payload(
    base_config_path: Path,
    local_config_path: Path,
) -> dict[str, Any]:
    if not local_config_path.exists():
        raise FileNotFoundError(
            "Missing local runtime config overlay: "
            f"{local_config_path}. Create it from "
            f"{LOCAL_RUNTIME_CONFIG_EXAMPLE_PATH} before running this experiment."
        )

    merged = _load_yaml_mapping(base_config_path)
    _deep_merge(merged, _load_yaml_mapping(local_config_path))
    return merged


def _load_scenario_config(
    path: Path = SCENARIO_CONFIG_PATH,
) -> ProviderMemorySmokeScenarioConfig:
    scenario_raw = _load_yaml_mapping(path)
    allowed_keys = {"agent_name", "prompt"}
    unknown_keys = set(scenario_raw) - allowed_keys
    if unknown_keys:
        raise ValueError(
            f"Unknown keys in provider memory smoke scenario config: {sorted(unknown_keys)}"
        )

    agent_name = scenario_raw.get("agent_name")
    prompt = scenario_raw.get("prompt")
    if not isinstance(agent_name, str) or not agent_name.strip():
        raise ValueError("scenario.agent_name must be a non-empty string")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("scenario.prompt must be a non-empty string")

    return ProviderMemorySmokeScenarioConfig(
        agent_name=agent_name.strip(),
        prompt=prompt.strip(),
    )


def _write_runtime_yaml(payload: dict[str, Any]) -> Path:
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".yaml",
        prefix="provider-memory-smoke-",
        delete=False,
        encoding="utf-8",
    ) as handle:
        yaml.safe_dump(payload, handle, sort_keys=False)
        return Path(handle.name)


def _load_runtime_config(
    *,
    debug_telemetry: bool,
    base_config_path: Path = BASE_RUNTIME_CONFIG_PATH,
    local_config_path: Path = LOCAL_RUNTIME_CONFIG_PATH,
) -> RuntimeConfig:
    merged_payload = _load_merged_config_payload(base_config_path, local_config_path)
    runtime_yaml = _write_runtime_yaml(merged_payload)
    try:
        return RuntimeConfig.from_sources(
            yaml_path=runtime_yaml,
            overrides={
                "debug_mode": debug_telemetry,
                "agents_dir": str(_experiment_agents_dir()),
            },
        )
    finally:
        runtime_yaml.unlink(missing_ok=True)


def _install_experiment_tool_registry(kernel: RuntimeKernel) -> None:
    """Avoid unrelated tool-discovery failures for the no-tools smoke path."""

    def create_tool_registry() -> None:
        kernel._di.tool_registry = DefaultToolRegistry()

    cast(Any, kernel._di)._create_tool_registry = create_tool_registry


async def _collect_extraction_counts(kernel: RuntimeKernel) -> dict[str, int]:
    memory = kernel._di.memory
    if memory is None:
        return {
            "entities": 0,
            "relationships": 0,
            "insights": 0,
            "summaries": 0,
        }

    entities = await memory.graph.get_top_nodes(100)
    relationships = await memory.graph.get_all_edges()
    insights = await memory._collection_manager.get_all(
        limit=100,
        where={"type": "insight"},
    )
    summaries = await memory._collection_manager.get_all(
        limit=100,
        where={"type": "summary"},
    )
    return {
        "entities": len(entities),
        "relationships": len(relationships),
        "insights": len(insights),
        "summaries": len(summaries),
    }


async def _await_extraction_evidence(
    kernel: RuntimeKernel,
    *,
    timeout_seconds: float = 45.0,
    poll_interval_seconds: float = 0.5,
) -> dict[str, int]:
    deadline = asyncio.get_running_loop().time() + timeout_seconds
    latest = await _collect_extraction_counts(kernel)

    while asyncio.get_running_loop().time() < deadline:
        if latest["entities"] > 0 or latest["insights"] > 0 or latest["summaries"] > 0:
            return latest
        await asyncio.sleep(poll_interval_seconds)
        latest = await _collect_extraction_counts(kernel)

    return latest


def _persist_result_artifact(result: ProviderMemorySmokeResult) -> str:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact_path = ARTIFACTS_DIR / f"provider-memory-smoke-{timestamp}.json"
    result.artifact_result_path = str(artifact_path)
    artifact_path.write_text(
        json.dumps(result.to_dict(), indent=2),
        encoding="utf-8",
    )
    return str(artifact_path)


async def run_provider_memory_smoke_experiment(
    *,
    prompt: str | None = None,
    agent_name: str | None = None,
    debug_telemetry: bool = False,
    preserve_artifacts: bool = True,
    base_config_path: Path = BASE_RUNTIME_CONFIG_PATH,
    local_config_path: Path = LOCAL_RUNTIME_CONFIG_PATH,
    scenario_config_path: Path = SCENARIO_CONFIG_PATH,
) -> ProviderMemorySmokeResult:
    artifact_result_path: str | None = None
    session_id: str | None = None

    kernel: RuntimeKernel | None = None
    config: RuntimeConfig | None = None
    scenario_config: ProviderMemorySmokeScenarioConfig | None = None
    interactive_agent: InteractiveAgent | None = None
    try:
        config = _load_runtime_config(
            debug_telemetry=debug_telemetry,
            base_config_path=base_config_path,
            local_config_path=local_config_path,
        )
        scenario_config = _load_scenario_config(scenario_config_path)
        effective_agent_name = agent_name or scenario_config.agent_name
        effective_prompt = prompt or scenario_config.prompt
        Path(config.runtime_paths.runtime_data_root).mkdir(parents=True, exist_ok=True)
        Path(config.chroma_path).mkdir(parents=True, exist_ok=True)
        config.resolve_artifacts_root_path(config.artifacts_root_dir).mkdir(
            parents=True,
            exist_ok=True,
        )
        kernel = RuntimeKernel(
            config=config,
            memory_profile=MemoryProfile.FULL,
        )
        _install_experiment_tool_registry(kernel)

        await kernel.start()
        session_id = await kernel.create_session(user_id="experiment")
        agent = kernel.spawn_agent(effective_agent_name)
        if not isinstance(agent, InteractiveAgent):
            raise TypeError(
                "Experiment agent "
                f"'{effective_agent_name}' did not resolve to InteractiveAgent"
            )
        interactive_agent = agent

        await agent.initialize_session(session_id=session_id, user_id="experiment")
        response = await agent.run(effective_prompt)
        extraction_counts = await _await_extraction_evidence(kernel)

        coarse_extraction_ok = (
            extraction_counts["entities"] > 0
            or extraction_counts["insights"] > 0
            or extraction_counts["summaries"] > 0
        )

        result = ProviderMemorySmokeResult(
            success=bool(response.strip()) and coarse_extraction_ok,
            agent_name=effective_agent_name,
            session_id=agent.session_id,
            prompt=effective_prompt,
            **_result_profile_fields(agent),
            response=response,
            memory_profile=MemoryProfile.FULL.value,
            runtime_data_root=config.runtime_paths.runtime_data_root,
            chroma_path=config.chroma_path,
            inference_llm_service=config.llm_pool.default_service,
            extraction_llm_service=config.memory_extraction.llm_service,
            embedding_service=config.embedding_pool.default_service,
            extraction_enabled=config.memory_extraction.enabled,
            extracted_entities_count=extraction_counts["entities"],
            extracted_relationships_count=extraction_counts["relationships"],
            extracted_insights_count=extraction_counts["insights"],
            extracted_summaries_count=extraction_counts["summaries"],
            artifact_result_path=None,
            error=(
                None
                if bool(response.strip()) and coarse_extraction_ok
                else "Provider memory smoke run completed without coarse extraction evidence."
            ),
        )
        if preserve_artifacts:
            artifact_result_path = _persist_result_artifact(result)
            result.artifact_result_path = artifact_result_path
        return result
    except Exception as exc:
        result = ProviderMemorySmokeResult(
            success=False,
            agent_name=(
                agent_name
                or (
                    scenario_config.agent_name
                    if scenario_config is not None
                    else "memory_probe"
                )
            ),
            session_id=session_id,
            prompt=(
                prompt
                or (
                    scenario_config.prompt
                    if scenario_config is not None
                    else ""
                )
            ),
            **_result_profile_fields(interactive_agent),
            response="",
            memory_profile=MemoryProfile.FULL.value,
            runtime_data_root=(
                config.runtime_paths.runtime_data_root if config else ""
            ),
            chroma_path=config.chroma_path if config else "",
            inference_llm_service=config.llm_pool.default_service if config else "agent_primary",
            extraction_llm_service=(
                config.memory_extraction.llm_service if config else "extraction_primary"
            ),
            embedding_service=(
                config.embedding_pool.default_service if config else "embedding_primary"
            ),
            extraction_enabled=config.memory_extraction.enabled if config else True,
            extracted_entities_count=0,
            extracted_relationships_count=0,
            extracted_insights_count=0,
            extracted_summaries_count=0,
            artifact_result_path=None,
            error=str(exc),
        )
        if preserve_artifacts:
            artifact_result_path = _persist_result_artifact(result)
            result.artifact_result_path = artifact_result_path
        return result
    finally:
        try:
            if kernel is not None:
                await kernel.stop()
        finally:
            pass
