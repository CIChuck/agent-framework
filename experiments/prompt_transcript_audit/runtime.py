"""Runtime harness for the deterministic prompt/transcript audit experiment."""

from __future__ import annotations

import importlib
import json
import shutil
import tempfile
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from friday_agent import DefaultToolRegistry, InteractiveAgent
from friday_agent.prompting import compose_system_prompt
from friday_core.profiles import MemoryProfile
from friday_runtime.config import RuntimeConfig
from friday_runtime.kernel import RuntimeKernel
from friday_transcript import SQLiteTranscriptStore

from experiments.prompt_transcript_audit.fake_llm import (
    DEFAULT_PROMPT,
    DEFAULT_RESPONSE,
    DeterministicAuditLLMClient,
)
from experiments.prompt_transcript_audit.schema import (
    PromptTranscriptAuditResult,
    PromptTranscriptAuditScenarioConfig,
)

yaml = cast(Any, importlib.import_module("yaml"))

EXPERIMENT_ROOT = Path(__file__).resolve().parent
BASE_RUNTIME_CONFIG_PATH = EXPERIMENT_ROOT / "config" / "runtime.yaml"
SCENARIO_CONFIG_PATH = EXPERIMENT_ROOT / "config" / "scenario.yaml"
ARTIFACTS_DIR = EXPERIMENT_ROOT / "artifacts"


def _experiment_agents_dir() -> Path:
    return EXPERIMENT_ROOT / "agents"


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Config must be a mapping: {path}")
    return cast(dict[str, Any], payload)


def _load_scenario_config(
    path: Path = SCENARIO_CONFIG_PATH,
) -> PromptTranscriptAuditScenarioConfig:
    payload = _load_yaml_mapping(path)
    allowed_keys = {"agent_name", "prompt"}
    unknown_keys = set(payload) - allowed_keys
    if unknown_keys:
        raise ValueError(
            f"Unknown keys in prompt transcript audit scenario config: {sorted(unknown_keys)}"
        )

    agent_name = payload.get("agent_name")
    prompt = payload.get("prompt")
    if not isinstance(agent_name, str) or not agent_name.strip():
        raise ValueError("scenario.agent_name must be a non-empty string")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("scenario.prompt must be a non-empty string")

    return PromptTranscriptAuditScenarioConfig(
        agent_name=agent_name.strip(),
        prompt=prompt.strip(),
    )


def _load_runtime_config(
    runtime_root: Path,
    *,
    debug_telemetry: bool,
    base_config_path: Path = BASE_RUNTIME_CONFIG_PATH,
    overrides: Mapping[str, Any] | None = None,
) -> RuntimeConfig:
    install_root = runtime_root / "install"
    runtime_data_root = runtime_root / "runtime-data" / "friday"
    workspace_root = runtime_root / "workspace"

    install_root.mkdir(parents=True, exist_ok=True)
    runtime_data_root.parent.mkdir(parents=True, exist_ok=True)
    workspace_root.mkdir(parents=True, exist_ok=True)

    runtime_overrides: dict[str, Any] = {
        "install_root": str(install_root),
        "runtime_data_root": str(runtime_data_root),
        "workspace_root": str(workspace_root),
        "debug_mode": debug_telemetry,
        "agents_dir": str(_experiment_agents_dir()),
    }
    if overrides:
        runtime_overrides.update(dict(overrides))

    return RuntimeConfig.from_sources(
        yaml_path=base_config_path,
        overrides=runtime_overrides,
    )


def _install_experiment_tool_registry(kernel: RuntimeKernel) -> None:
    """Avoid unrelated tool-discovery failures for the no-tools audit path."""

    def create_tool_registry() -> None:
        kernel._di.tool_registry = DefaultToolRegistry()

    cast(Any, kernel._di)._create_tool_registry = create_tool_registry


def _install_deterministic_llm(
    kernel: RuntimeKernel,
    *,
    prompt: str,
    response: str,
) -> None:
    fake_llm = DeterministicAuditLLMClient(response_map={prompt: response})
    kernel._di.llm_pool["deterministic"] = fake_llm
    kernel._di.llm = fake_llm


def _persist_result_artifact(result: PromptTranscriptAuditResult) -> str:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact_path = ARTIFACTS_DIR / f"prompt-transcript-audit-{timestamp}.json"
    result.artifact_result_path = str(artifact_path)
    artifact_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    return str(artifact_path)


async def _collect_transcript_audit(
    *,
    transcript_store: SQLiteTranscriptStore,
    session_id: str,
    expected_response: str,
    expected_composed_system_prompt: str,
) -> dict[str, Any]:
    session = await transcript_store.get_session(session_id)
    entries = await transcript_store.get_entries(session_id, limit=10)
    entry = entries[0] if entries else None
    context_log = (
        await transcript_store.get_context_log_by_entry(entry.id)
        if entry is not None
        else None
    )

    metadata = dict(entry.metadata) if entry is not None else {}
    prompt_metadata_persisted = (
        metadata.get("runtime_base_system_prompt") is not None
        and metadata.get("agent_system_prompt") is not None
        and metadata.get("composed_system_prompt") is not None
    )

    context_log_messages: list[dict[str, Any]] = []
    context_log_system_prompt: str | None = None
    context_log_response_content: str | None = None
    if context_log is not None:
        raw_prompt = json.loads(context_log.raw_prompt)
        if isinstance(raw_prompt, list):
            context_log_messages = cast(list[dict[str, Any]], raw_prompt)
            for message in context_log_messages:
                if message.get("role") == "system":
                    content = message.get("content")
                    if isinstance(content, str):
                        context_log_system_prompt = content
                        break

        if context_log.raw_response:
            raw_response = json.loads(context_log.raw_response)
            if isinstance(raw_response, dict):
                content = raw_response.get("content")
                if isinstance(content, str):
                    context_log_response_content = content

    return {
        "transcript_session_system_prompt": (
            session.system_prompt if session is not None else None
        ),
        "transcript_entry_id": entry.id if entry is not None else None,
        "transcript_entry_turn_number": entry.turn_number if entry is not None else None,
        "transcript_entry_persisted": entry is not None,
        "transcript_entry_agent_id": entry.agent_id if entry is not None else None,
        "transcript_entry_llm_service": entry.llm_service if entry is not None else None,
        "transcript_entry_provider_name": (
            entry.provider_name if entry is not None else None
        ),
        "transcript_entry_model_name": entry.model_name if entry is not None else None,
        "prompt_metadata_persisted": prompt_metadata_persisted,
        "context_log_present": context_log is not None,
        "context_log_message_count": len(context_log_messages),
        "context_log_system_prompt": context_log_system_prompt,
        "context_log_matches_composed_prompt": (
            context_log_system_prompt == expected_composed_system_prompt
        ),
        "context_log_response_content": context_log_response_content,
        "context_log_matches_response": (
            context_log_response_content == expected_response
        ),
    }


async def run_prompt_transcript_audit_experiment(
    *,
    prompt: str | None = None,
    agent_name: str | None = None,
    debug_telemetry: bool = False,
    preserve_artifacts: bool = True,
    base_config_path: Path = BASE_RUNTIME_CONFIG_PATH,
    scenario_config_path: Path = SCENARIO_CONFIG_PATH,
    runtime_root: Path | None = None,
    runtime_overrides: Mapping[str, Any] | None = None,
    response: str = DEFAULT_RESPONSE,
) -> PromptTranscriptAuditResult:
    artifact_result_path: str | None = None
    created_runtime_root = runtime_root is None
    effective_runtime_root = runtime_root or Path(
        tempfile.mkdtemp(prefix="friday-prompt-transcript-audit-")
    )

    kernel: RuntimeKernel | None = None
    config: RuntimeConfig | None = None
    session_id: str | None = None
    scenario_config: PromptTranscriptAuditScenarioConfig | None = None
    interactive_agent: InteractiveAgent | None = None

    try:
        config = _load_runtime_config(
            effective_runtime_root,
            debug_telemetry=debug_telemetry,
            base_config_path=base_config_path,
            overrides=runtime_overrides,
        )
        scenario_config = _load_scenario_config(scenario_config_path)
        effective_agent_name = agent_name or scenario_config.agent_name
        effective_prompt = prompt or scenario_config.prompt

        kernel = RuntimeKernel(
            config=config,
            memory_profile=MemoryProfile.TESTING,
        )
        _install_experiment_tool_registry(kernel)

        await kernel.start()
        _install_deterministic_llm(
            kernel,
            prompt=effective_prompt,
            response=response,
        )

        session_id = await kernel.create_session(user_id="experiment")
        agent = kernel.spawn_agent(effective_agent_name)
        if not isinstance(agent, InteractiveAgent):
            raise TypeError(
                f"Experiment agent '{effective_agent_name}' did not resolve to InteractiveAgent"
            )
        interactive_agent = agent

        await agent.initialize_session(session_id=session_id, user_id="experiment")
        agent_response = await agent.run(effective_prompt)

        prompt_composition = compose_system_prompt(
            profile=agent.profile,
            runtime_base_prompt=agent.runtime_base_system_prompt,
        )
        transcript_store = kernel._di.transcript_store
        if transcript_store is None:
            raise RuntimeError("Transcript store was not configured for the audit run")

        audit = await _collect_transcript_audit(
            transcript_store=transcript_store,
            session_id=agent.session_id,
            expected_response=agent_response,
            expected_composed_system_prompt=prompt_composition.composed_system_prompt,
        )

        context_log_expected = config.transcript.capture_context_log
        context_log_ok = (
            audit["context_log_present"]
            if context_log_expected
            else not audit["context_log_present"]
        )
        success = all(
            [
                agent_response == response,
                audit["transcript_entry_persisted"],
                audit["prompt_metadata_persisted"],
                audit["transcript_session_system_prompt"]
                == config.prompting.base_system_prompt,
                context_log_ok,
                (
                    not context_log_expected
                    or audit["context_log_matches_composed_prompt"]
                ),
                (not context_log_expected or audit["context_log_matches_response"]),
            ]
        )

        result = PromptTranscriptAuditResult(
            success=success,
            agent_name=effective_agent_name,
            session_id=agent.session_id,
            prompt=effective_prompt,
            response=agent_response,
            runtime_base_system_prompt=prompt_composition.runtime_base_prompt,
            rendered_system_prompt=prompt_composition.agent_prompt,
            composed_system_prompt=prompt_composition.composed_system_prompt,
            transcript_session_system_prompt=audit["transcript_session_system_prompt"],
            transcript_entry_id=audit["transcript_entry_id"],
            transcript_entry_turn_number=audit["transcript_entry_turn_number"],
            transcript_entry_persisted=audit["transcript_entry_persisted"],
            transcript_entry_agent_id=audit["transcript_entry_agent_id"],
            transcript_entry_llm_service=audit["transcript_entry_llm_service"],
            transcript_entry_provider_name=audit["transcript_entry_provider_name"],
            transcript_entry_model_name=audit["transcript_entry_model_name"],
            prompt_metadata_persisted=audit["prompt_metadata_persisted"],
            capture_context_log_enabled=config.transcript.capture_context_log,
            context_log_present=audit["context_log_present"],
            context_log_message_count=audit["context_log_message_count"],
            context_log_system_prompt=audit["context_log_system_prompt"],
            context_log_matches_composed_prompt=audit[
                "context_log_matches_composed_prompt"
            ],
            context_log_response_content=audit["context_log_response_content"],
            context_log_matches_response=audit["context_log_matches_response"],
            llm_mode="deterministic",
            telemetry_enabled=kernel.telemetry is not None,
            artifact_result_path=None,
            error=(
                None
                if success
                else "Prompt/transcript audit invariants did not all hold."
            ),
        )
        if preserve_artifacts:
            artifact_result_path = _persist_result_artifact(result)
            result.artifact_result_path = artifact_result_path
        return result
    except Exception as exc:
        result = PromptTranscriptAuditResult(
            success=False,
            agent_name=(
                agent_name
                or (scenario_config.agent_name if scenario_config is not None else "audit_probe")
            ),
            session_id=session_id,
            prompt=prompt or (scenario_config.prompt if scenario_config is not None else DEFAULT_PROMPT),
            response="",
            runtime_base_system_prompt=(
                config.prompting.base_system_prompt if config is not None else None
            ),
            rendered_system_prompt=(
                interactive_agent.profile.render_system_prompt()
                if interactive_agent is not None
                else None
            ),
            composed_system_prompt=(
                compose_system_prompt(
                    profile=interactive_agent.profile,
                    runtime_base_prompt=interactive_agent.runtime_base_system_prompt,
                ).composed_system_prompt
                if interactive_agent is not None
                else None
            ),
            transcript_session_system_prompt=None,
            transcript_entry_id=None,
            transcript_entry_turn_number=None,
            transcript_entry_persisted=False,
            transcript_entry_agent_id=None,
            transcript_entry_llm_service=None,
            transcript_entry_provider_name=None,
            transcript_entry_model_name=None,
            prompt_metadata_persisted=False,
            capture_context_log_enabled=(
                config.transcript.capture_context_log if config is not None else False
            ),
            context_log_present=False,
            context_log_message_count=0,
            context_log_system_prompt=None,
            context_log_matches_composed_prompt=False,
            context_log_response_content=None,
            context_log_matches_response=False,
            llm_mode="deterministic",
            telemetry_enabled=(kernel.telemetry is not None if kernel is not None else False),
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
            if created_runtime_root:
                shutil.rmtree(effective_runtime_root, ignore_errors=True)
