"""
YAML workflow loader.

Supports both legacy flat workflows and canonical workflow -> pipeline bundles.
"""

# mypy: disable-error-code=import-untyped

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from friday_agent.workflows.models import (
    PipelineArtifactContract,
    PipelineDefinition,
    TaskDefinition,
    TaskNode,
    WorkflowDefinition,
    WorkflowPipelineDefinition,
)

logger = logging.getLogger(__name__)


class WorkflowLoadError(Exception):
    """Raised when workflow loading fails."""

    pass


@dataclass(frozen=True)
class CanonicalWorkflowBundle:
    """Canonical workflow definition plus referenced pipeline definitions."""

    workflow: WorkflowPipelineDefinition
    pipelines: dict[str, PipelineDefinition]


class WorkflowLoader:
    """
    Load workflow definitions from YAML files.

    `load()` preserves the legacy flat workflow shape.
    `load_canonical()` loads the Phase 4 canonical workflow/pipeline bundle.
    """

    def __init__(self, workflows_dir: Path | str | None = None):
        if workflows_dir is None:
            self._workflows_dir = Path.cwd() / "workflows"
        else:
            self._workflows_dir = Path(workflows_dir)

        self._cache: dict[str, WorkflowDefinition] = {}
        self._canonical_cache: dict[str, CanonicalWorkflowBundle] = {}

    @property
    def workflows_dir(self) -> Path:
        """Get the workflows directory."""
        return self._workflows_dir

    def list_workflows(self) -> list[str]:
        """
        List available workflow names.

        Includes both legacy `*.yaml` files and canonical workflow directories.
        """
        if not self._workflows_dir.exists():
            return []

        workflows = set()
        for path in self._workflows_dir.glob("*.yaml"):
            workflows.add(path.stem)
        for path in self._workflows_dir.glob("*.yml"):
            workflows.add(path.stem)
        for path in self._workflows_dir.iterdir():
            if path.is_dir() and self._find_workflow_manifest(path) is not None:
                workflows.add(path.name)

        return sorted(workflows)

    def load(self, name: str) -> WorkflowDefinition:
        """Load a legacy flat workflow definition."""
        if name in self._cache:
            return self._cache[name]

        path = self._legacy_workflow_path(name)
        workflow = self._parse_legacy_yaml(path)

        errors = workflow.validate_graph()
        if errors:
            raise WorkflowLoadError(f"Invalid workflow '{name}': {errors}")

        self._cache[name] = workflow
        logger.info("Loaded legacy workflow: %s", name)
        return workflow

    def load_canonical(self, name: str) -> CanonicalWorkflowBundle:
        """Load a canonical Phase 4 workflow bundle."""
        if name in self._canonical_cache:
            return self._canonical_cache[name]

        workflow_dir = self._workflows_dir / name
        if not workflow_dir.exists() or not workflow_dir.is_dir():
            raise WorkflowLoadError(f"Canonical workflow directory not found: {name}")

        workflow_path = self._find_workflow_manifest(workflow_dir)
        if workflow_path is None:
            raise WorkflowLoadError(f"Canonical workflow manifest not found: {name}")

        workflow = self._parse_canonical_workflow_yaml(workflow_path)
        pipelines_dir = workflow_dir / "pipelines"
        if not pipelines_dir.exists() or not pipelines_dir.is_dir():
            raise WorkflowLoadError(
                f"Canonical workflow pipelines directory not found: {pipelines_dir}"
            )

        pipelines: dict[str, PipelineDefinition] = {}
        for pipeline_id in workflow.pipeline_refs:
            pipeline_path = self._find_named_yaml(pipelines_dir, pipeline_id)
            if pipeline_path is None:
                raise WorkflowLoadError(
                    f"Canonical workflow '{name}' missing pipeline '{pipeline_id}'"
                )
            pipelines[pipeline_id] = self._parse_pipeline_yaml(pipeline_path)

        errors = workflow.validate_reference_integrity(pipelines)
        for pipeline_id, pipeline in pipelines.items():
            for error in pipeline.validate_graph():
                errors.append(f"{pipeline_id}: {error}")
        errors.extend(self._validate_artifact_contracts(workflow, pipelines))

        if errors:
            raise WorkflowLoadError(f"Invalid canonical workflow '{name}': {errors}")

        bundle = CanonicalWorkflowBundle(workflow=workflow, pipelines=pipelines)
        self._canonical_cache[name] = bundle
        logger.info("Loaded canonical workflow bundle: %s", name)
        return bundle

    def load_all(self) -> dict[str, WorkflowDefinition]:
        """Load all legacy flat workflows from directory."""
        if not self._workflows_dir.exists():
            return {}

        workflows = {}
        for path in self._workflows_dir.glob("*.yaml"):
            name = path.stem
            workflows[name] = self.load(name)
        for path in self._workflows_dir.glob("*.yml"):
            name = path.stem
            if name not in workflows:
                workflows[name] = self.load(name)
        return workflows

    def reload(self, name: str) -> WorkflowDefinition:
        """Force reload legacy workflow (bypass cache)."""
        self._cache.pop(name, None)
        return self.load(name)

    def reload_canonical(self, name: str) -> CanonicalWorkflowBundle:
        """Force reload canonical workflow bundle (bypass cache)."""
        self._canonical_cache.pop(name, None)
        return self.load_canonical(name)

    def load_legacy_as_canonical(self, name: str) -> CanonicalWorkflowBundle:
        """Load a legacy flat workflow and adapt it into a canonical bundle."""
        workflow = self.load(name)
        bundle = self.adapt_legacy_workflow(workflow)
        self._canonical_cache[name] = bundle
        logger.info("Adapted legacy workflow to canonical bundle: %s", name)
        return bundle

    def clear_cache(self) -> None:
        """Clear workflow caches."""
        self._cache.clear()
        self._canonical_cache.clear()

    def adapt_legacy_workflow(
        self,
        workflow: WorkflowDefinition,
    ) -> CanonicalWorkflowBundle:
        """Translate a flat workflow definition into a single-pipeline bundle."""
        pipeline_id = f"{workflow.id}_legacy_pipeline"
        tasks = [self._adapt_legacy_task(task) for task in workflow.tasks]

        adapted_workflow = WorkflowPipelineDefinition(
            workflow_id=workflow.id,
            version=workflow.version,
            name=workflow.name,
            goal=workflow.description,
            pipeline_refs=(pipeline_id,),
            entry_pipeline_id=pipeline_id,
            completion_criteria=(workflow.description,),
            timeout_seconds=workflow.timeout_seconds,
        )
        adapted_pipeline = PipelineDefinition(
            pipeline_id=pipeline_id,
            version=workflow.version,
            workflow_id=workflow.id,
            goal=workflow.description,
            tasks=tasks,
            entrypoints=tuple(task.id for task in workflow.tasks if not task.depends_on),
            exit_conditions=tuple(
                f"Legacy workflow task(s) complete: {', '.join(task.outputs)}"
                for task in workflow.tasks
                if task.outputs
            ),
            timeout_seconds=workflow.timeout_seconds,
            input_contract=self._collect_legacy_input_contract(workflow),
            output_contract=self._collect_legacy_output_contract(workflow),
            artifact_contract=PipelineArtifactContract(),
        )
        return CanonicalWorkflowBundle(
            workflow=adapted_workflow,
            pipelines={pipeline_id: adapted_pipeline},
        )

    def _legacy_workflow_path(self, name: str) -> Path:
        path = self._workflows_dir / f"{name}.yaml"
        if path.exists():
            return path
        path = self._workflows_dir / f"{name}.yml"
        if path.exists():
            return path
        raise WorkflowLoadError(f"Workflow not found: {name}")

    def _find_workflow_manifest(self, workflow_dir: Path) -> Path | None:
        for candidate in ("workflow.yaml", "workflow.yml"):
            path = workflow_dir / candidate
            if path.exists():
                return path
        return None

    def _find_named_yaml(self, root: Path, name: str) -> Path | None:
        for suffix in (".yaml", ".yml"):
            path = root / f"{name}{suffix}"
            if path.exists():
                return path
        return None

    def _read_yaml_object(self, path: Path) -> dict[str, Any]:
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise WorkflowLoadError(f"Invalid YAML in {path}: {e}") from e
        except OSError as e:
            raise WorkflowLoadError(f"Cannot read workflow file {path}: {e}") from e

        if not isinstance(data, dict):
            raise WorkflowLoadError(f"Workflow must be a YAML object: {path}")
        return data

    def _parse_legacy_yaml(self, path: Path) -> WorkflowDefinition:
        data = self._read_yaml_object(path)

        required = ["id", "name", "description", "tasks"]
        missing = [f for f in required if f not in data]
        if missing:
            raise WorkflowLoadError(f"Missing required fields: {missing}")

        tasks = [TaskNode(**task_data) for task_data in data["tasks"]]
        return WorkflowDefinition(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            tasks=tasks,
            timeout_seconds=data.get("timeout_seconds", 3600),
            max_retries=data.get("max_retries", 1),
            version=data.get("version", "1.0.0"),
            author=data.get("author"),
            tags=data.get("tags", []),
        )

    def _adapt_legacy_task(self, task: TaskNode) -> TaskDefinition:
        """Translate a legacy task node into canonical single-pipeline form."""
        completion_criteria = [f"Complete legacy task '{task.name}'."]
        if task.requires_approval:
            completion_criteria.append("Honor approval gate before completion.")

        return TaskDefinition(
            task_id=task.id,
            name=task.name,
            description=task.description,
            owner_agent_id=task.agent,
            required_skills=(
                (task.skill_ref,) if task.skill_ref is not None else tuple()
            ),
            input_contract={input_name: "any" for input_name in task.inputs},
            input_bindings=dict(task.inputs),
            output_contract={output_name: "any" for output_name in task.outputs},
            dependencies=task.depends_on,
            retry_policy={"max_attempts": str(task.max_retries)},
            hitl_policy_ref="approval_gate" if task.requires_approval else None,
            completion_criteria=tuple(completion_criteria),
        )

    def _collect_legacy_input_contract(
        self,
        workflow: WorkflowDefinition,
    ) -> dict[str, str]:
        """Collect root workflow inputs used by adapted legacy tasks."""
        produced = {output for task in workflow.tasks for output in task.outputs}
        contract: dict[str, str] = {}
        for task in workflow.tasks:
            for input_name, binding in task.inputs.items():
                if binding.startswith("$") and binding[1:] not in produced:
                    contract.setdefault(input_name, "any")
        return contract

    def _collect_legacy_output_contract(
        self,
        workflow: WorkflowDefinition,
    ) -> dict[str, str]:
        """Collect final workflow outputs exposed by adapted legacy tasks."""
        dependency_targets = {dep for task in workflow.tasks for dep in task.depends_on}
        terminal_tasks = [task for task in workflow.tasks if task.id not in dependency_targets]
        contract: dict[str, str] = {}
        for task in terminal_tasks:
            for output_name in task.outputs:
                contract.setdefault(output_name, "any")
        return contract

    def _parse_canonical_workflow_yaml(self, path: Path) -> WorkflowPipelineDefinition:
        data = self._read_yaml_object(path)
        required = ["workflow_id", "version", "name", "goal", "pipeline_refs"]
        missing = [field for field in required if field not in data]
        if missing:
            raise WorkflowLoadError(
                f"Missing required canonical workflow fields: {missing}"
            )
        try:
            return WorkflowPipelineDefinition(**data)
        except Exception as e:
            raise WorkflowLoadError(
                f"Invalid canonical workflow '{path.parent.name}': {e}"
            ) from e

    def _parse_pipeline_yaml(self, path: Path) -> PipelineDefinition:
        data = self._read_yaml_object(path)
        required = ["pipeline_id", "version", "workflow_id", "goal", "tasks"]
        missing = [field for field in required if field not in data]
        if missing:
            raise WorkflowLoadError(
                f"Missing required pipeline fields in {path.name}: {missing}"
            )
        try:
            return PipelineDefinition(**data)
        except Exception as e:
            raise WorkflowLoadError(f"Invalid pipeline '{path.name}': {e}") from e

    def _validate_artifact_contracts(
        self,
        workflow: WorkflowPipelineDefinition,
        pipelines: dict[str, PipelineDefinition],
    ) -> list[str]:
        """Validate workflow/pipeline artifact contract coherence."""
        errors: list[str] = []
        produced_index: dict[tuple[str, str], str] = {}

        for pipeline_id, pipeline in pipelines.items():
            for produced in pipeline.artifact_contract.produced:
                produced_index[(pipeline_id, produced.artifact_id)] = produced.type

        for required in workflow.required_artifacts:
            produced_type = produced_index.get(
                (required.produced_by_pipeline, required.artifact_id)
            )
            if produced_type is None:
                errors.append(
                    f"workflow required_artifact '{required.artifact_id}' is not "
                    f"produced by pipeline '{required.produced_by_pipeline}'"
                )
                continue
            if produced_type != required.type:
                errors.append(
                    f"workflow required_artifact '{required.artifact_id}' type mismatch: "
                    f"{produced_type} != {required.type}"
                )

        for pipeline_id, pipeline in pipelines.items():
            for consumed in pipeline.artifact_contract.consumed:
                produced_type = produced_index.get(
                    (consumed.from_pipeline, consumed.artifact_id)
                )
                if produced_type is None:
                    errors.append(
                        f"pipeline '{pipeline_id}' consumes artifact "
                        f"'{consumed.artifact_id}' from unknown producer pipeline "
                        f"'{consumed.from_pipeline}'"
                    )
                    continue
                if produced_type != consumed.type:
                    errors.append(
                        f"pipeline '{pipeline_id}' consumed artifact "
                        f"'{consumed.artifact_id}' type mismatch: "
                        f"{produced_type} != {consumed.type}"
                    )

        return errors
