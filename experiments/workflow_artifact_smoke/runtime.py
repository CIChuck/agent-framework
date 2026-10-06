"""Runtime harness for the live canonical workflow artifact smoke experiment."""

from __future__ import annotations

import importlib
import json
import re
import tempfile
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from friday_core.profiles import MemoryProfile
from friday_runtime.config import RuntimeConfig
from friday_runtime.kernel import RuntimeKernel
from friday_transcript import SQLiteTranscriptStore

from experiments.workflow_artifact_smoke.schema import (
    WorkflowArtifactSmokeResult,
    WorkflowArtifactSmokeScenarioConfig,
)

yaml = cast(Any, importlib.import_module("yaml"))

EXPERIMENT_ROOT = Path(__file__).resolve().parent
BASE_RUNTIME_CONFIG_PATH = EXPERIMENT_ROOT / "config" / "runtime.yaml"
LOCAL_RUNTIME_CONFIG_PATH = EXPERIMENT_ROOT / "config" / "runtime.local.yaml"
LOCAL_RUNTIME_CONFIG_EXAMPLE_PATH = (
    EXPERIMENT_ROOT / "config" / "runtime.local.yaml.example"
)
SCENARIO_CONFIG_PATH = EXPERIMENT_ROOT / "config" / "scenario.yaml"
ARTIFACTS_DIR = EXPERIMENT_ROOT / "artifacts"


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Config must be a mapping: {path}")
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


def _write_runtime_yaml(payload: dict[str, Any]) -> Path:
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".yaml",
        prefix="workflow-artifact-smoke-",
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
            overrides={"debug_mode": debug_telemetry},
        )
    finally:
        runtime_yaml.unlink(missing_ok=True)


def _load_scenario_config(
    path: Path = SCENARIO_CONFIG_PATH,
) -> WorkflowArtifactSmokeScenarioConfig:
    payload = _load_yaml_mapping(path)
    allowed = {"workflow_name", "query", "output_filename"}
    unknown = set(payload) - allowed
    if unknown:
        raise ValueError(
            "Unknown keys in workflow artifact smoke scenario config: "
            f"{sorted(unknown)}"
        )

    workflow_name = payload.get("workflow_name")
    query = payload.get("query")
    output_filename = payload.get("output_filename")
    if not isinstance(workflow_name, str) or not workflow_name.strip():
        raise ValueError("scenario.workflow_name must be a non-empty string")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("scenario.query must be a non-empty string")
    if not isinstance(output_filename, str) or not output_filename.strip():
        raise ValueError("scenario.output_filename must be a non-empty string")

    return WorkflowArtifactSmokeScenarioConfig(
        workflow_name=workflow_name.strip(),
        query=query.strip(),
        output_filename=output_filename.strip(),
    )


def _resolve_install_relative(config: RuntimeConfig, path_value: str) -> Path:
    raw = Path(path_value).expanduser()
    if raw.is_absolute():
        return raw.resolve()
    install_root = Path(config.install_root or ".").expanduser().resolve()
    return (install_root / raw).resolve()


def _strip_code_fences(value: str) -> str:
    stripped = value.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return stripped


def _parse_selected_article(raw_value: Any) -> tuple[dict[str, Any] | None, bool]:
    if isinstance(raw_value, dict):
        return raw_value, True
    if not isinstance(raw_value, str):
        return None, False

    candidates = [_strip_code_fences(raw_value)]
    match = re.search(r"\{.*\}", raw_value, flags=re.DOTALL)
    if match is not None:
        candidates.append(match.group(0))

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return cast(dict[str, Any], parsed), True
    return None, False


def _count_paragraphs(content: str) -> int:
    return len([chunk for chunk in re.split(r"\n\s*\n", content.strip()) if chunk.strip()])


async def _collect_transcript_summary(
    *,
    transcript_path: Path,
    session_id: str | None,
) -> dict[str, Any]:
    if session_id is None or not transcript_path.exists():
        return {
            "transcript_exists": transcript_path.exists(),
            "transcript_entry_count": 0,
            "transcript_agent_ids": [],
            "transcript_tool_call_count": 0,
        }

    store = SQLiteTranscriptStore(transcript_path)
    entries = await store.get_entries(session_id, limit=50)
    agent_ids = [
        entry.agent_id for entry in entries if isinstance(entry.agent_id, str) and entry.agent_id
    ]
    tool_call_count = 0
    for entry in entries:
        tool_calls = getattr(entry, "tool_calls", None)
        if isinstance(tool_calls, list):
            tool_call_count += len(tool_calls)

    return {
        "transcript_exists": True,
        "transcript_entry_count": len(entries),
        "transcript_agent_ids": agent_ids,
        "transcript_tool_call_count": tool_call_count,
    }


def _persist_result_artifact(result: WorkflowArtifactSmokeResult) -> str:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    artifact_path = ARTIFACTS_DIR / f"workflow-artifact-smoke-{timestamp}.json"
    result.artifact_result_path = str(artifact_path)
    artifact_path.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    return str(artifact_path)


async def run_workflow_artifact_smoke_experiment(
    *,
    workflow_name: str | None = None,
    query: str | None = None,
    output_filename: str | None = None,
    debug_telemetry: bool = False,
    preserve_artifacts: bool = True,
    base_config_path: Path = BASE_RUNTIME_CONFIG_PATH,
    local_config_path: Path = LOCAL_RUNTIME_CONFIG_PATH,
    scenario_config_path: Path = SCENARIO_CONFIG_PATH,
) -> WorkflowArtifactSmokeResult:
    config: RuntimeConfig | None = None
    kernel: RuntimeKernel | None = None

    effective_workflow_name = workflow_name or "wf_agentic_news"
    effective_query = query or ""
    effective_output_filename = output_filename or "summary_report.md"
    execution_id: str | None = None
    output_path: Path | None = None
    transcript_path = EXPERIMENT_ROOT / "runtime_data" / "transcripts" / "workflow-artifact-smoke.db"
    chroma_path = EXPERIMENT_ROOT / "runtime_data" / "memory" / "chroma"
    graph_path = EXPERIMENT_ROOT / "runtime_data" / "memory" / "graph.json"
    memory_root = EXPERIMENT_ROOT / "runtime_data" / "memory"

    try:
        scenario = _load_scenario_config(scenario_config_path)
        effective_workflow_name = workflow_name or scenario.workflow_name
        effective_query = query or scenario.query
        effective_output_filename = output_filename or scenario.output_filename

        config = _load_runtime_config(
            debug_telemetry=debug_telemetry,
            base_config_path=base_config_path,
            local_config_path=local_config_path,
        )

        output_path = config.resolve_workspace_artifact_path(effective_output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.unlink(missing_ok=True)

        transcript_path = config.resolve_transcript_path(config.transcript.path)
        chroma_path = _resolve_install_relative(config, config.chroma_path)
        graph_path = config.resolve_runtime_state_path("memory/graph.json")
        memory_root = chroma_path.parent

        kernel = RuntimeKernel(
            config=config,
            memory_profile=MemoryProfile.FULL,
        )
        await kernel.start()

        execution = await kernel.execute_workflow(
            effective_workflow_name,
            {
                "query": effective_query,
                "output_path": str(output_path),
            },
        )
        execution_id = getattr(execution, "execution_id", None)

        raw_selected_article = execution.variables.get("selected_article")
        selected_article, valid_json = _parse_selected_article(raw_selected_article)
        raw_output_path = execution.variables.get("summary_report")
        summary_artifact = execution.published_artifacts.get("summary_report")

        report_exists = output_path.exists()
        report_content = output_path.read_text(encoding="utf-8") if report_exists else ""
        selected_title = (
            str(selected_article.get("title")).strip()
            if selected_article and selected_article.get("title") is not None
            else None
        )
        selected_source = (
            str(selected_article.get("source")).strip()
            if selected_article and selected_article.get("source") is not None
            else None
        )
        mentions_source = False
        lowered_content = report_content.lower()
        if selected_title:
            mentions_source = selected_title.lower() in lowered_content
        if not mentions_source and selected_source:
            mentions_source = selected_source.lower() in lowered_content

        transcript_summary = await _collect_transcript_summary(
            transcript_path=transcript_path,
            session_id=execution_id,
        )

        result = WorkflowArtifactSmokeResult(
            success=bool(
                getattr(execution.status, "value", None) == "completed"
                and report_exists
                and _count_paragraphs(report_content) == 3
                and valid_json
                and summary_artifact is not None
                and summary_artifact.provenance.get("output_ref") == str(output_path)
                and transcript_summary["transcript_entry_count"] >= 2
                and memory_root.exists()
            ),
            workflow_name=effective_workflow_name,
            execution_id=execution_id,
            session_id=execution_id,
            query=effective_query,
            output_filename=effective_output_filename,
            output_path=str(output_path),
            output_exists=report_exists,
            output_paragraph_count=_count_paragraphs(report_content),
            output_mentions_source=mentions_source,
            selected_article_title=selected_title,
            selected_article_url=(
                str(selected_article.get("url")).strip()
                if selected_article and selected_article.get("url") is not None
                else None
            ),
            selected_article_source=selected_source,
            selected_article_published_at=(
                str(selected_article.get("published_at")).strip()
                if selected_article and selected_article.get("published_at") is not None
                else None
            ),
            selected_article_valid_json=valid_json,
            summary_artifact_present=summary_artifact is not None,
            summary_artifact_output_ref=(
                summary_artifact.provenance.get("output_ref")
                if summary_artifact is not None
                else None
            ),
            transcript_path=str(transcript_path),
            transcript_exists=transcript_summary["transcript_exists"],
            transcript_entry_count=transcript_summary["transcript_entry_count"],
            transcript_agent_ids=transcript_summary["transcript_agent_ids"],
            transcript_tool_call_count=transcript_summary["transcript_tool_call_count"],
            chroma_path=str(chroma_path),
            graph_path=str(graph_path),
            memory_root=str(memory_root),
            memory_root_exists=memory_root.exists(),
            artifact_result_path=None,
            error=None if raw_output_path else "Workflow did not emit summary_report output",
        )
    except Exception as exc:
        result = WorkflowArtifactSmokeResult(
            success=False,
            workflow_name=effective_workflow_name,
            execution_id=execution_id,
            session_id=execution_id,
            query=effective_query,
            output_filename=effective_output_filename,
            output_path=str(output_path) if output_path is not None else None,
            output_exists=output_path.exists() if output_path is not None else False,
            output_paragraph_count=0,
            output_mentions_source=False,
            selected_article_title=None,
            selected_article_url=None,
            selected_article_source=None,
            selected_article_published_at=None,
            selected_article_valid_json=False,
            summary_artifact_present=False,
            summary_artifact_output_ref=None,
            transcript_path=str(transcript_path),
            transcript_exists=transcript_path.exists(),
            transcript_entry_count=0,
            transcript_agent_ids=[],
            transcript_tool_call_count=0,
            chroma_path=str(chroma_path),
            graph_path=str(graph_path),
            memory_root=str(memory_root),
            memory_root_exists=memory_root.exists(),
            artifact_result_path=None,
            error=str(exc),
        )
    finally:
        if kernel is not None:
            await kernel.stop()

    if preserve_artifacts:
        _persist_result_artifact(result)
    return result
