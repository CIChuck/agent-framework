"""
YAML workflow loader.

Ref: docs/build-plan/to-do/dynamic-workflows-build-plan.md
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from friday_agent.workflows.models import TaskNode, WorkflowDefinition

logger = logging.getLogger(__name__)


class WorkflowLoadError(Exception):
    """Raised when workflow loading fails."""

    pass


class WorkflowLoader:
    """
    Load workflow definitions from YAML files.

    Usage:
        loader = WorkflowLoader(Path("workflows/"))
        workflow = loader.load("newsletter")
        all_workflows = loader.load_all()
    """

    def __init__(self, workflows_dir: Path | str | None = None):
        """
        Initialize loader.

        Args:
            workflows_dir: Directory containing workflow YAML files.
                          Defaults to ./workflows/ relative to cwd.
        """
        if workflows_dir is None:
            self._workflows_dir = Path.cwd() / "workflows"
        else:
            self._workflows_dir = Path(workflows_dir)

        self._cache: dict[str, WorkflowDefinition] = {}

    @property
    def workflows_dir(self) -> Path:
        """Get the workflows directory."""
        return self._workflows_dir

    def list_workflows(self) -> list[str]:
        """
        List available workflow names.

        Returns:
            List of workflow names (without .yaml extension)
        """
        if not self._workflows_dir.exists():
            return []

        workflows = set()
        for path in self._workflows_dir.glob("*.yaml"):
            workflows.add(path.stem)
        for path in self._workflows_dir.glob("*.yml"):
            workflows.add(path.stem)

        return sorted(workflows)

    def load(self, name: str) -> WorkflowDefinition:
        """
        Load workflow by name.

        Args:
            name: Workflow name (filename without .yaml)

        Returns:
            WorkflowDefinition

        Raises:
            WorkflowLoadError: If file not found or invalid
        """
        if name in self._cache:
            return self._cache[name]

        path = self._workflows_dir / f"{name}.yaml"
        if not path.exists():
            path = self._workflows_dir / f"{name}.yml"
            if not path.exists():
                raise WorkflowLoadError(f"Workflow not found: {name}")

        workflow = self._parse_yaml(path)

        # Validate
        errors = workflow.validate_graph()
        if errors:
            raise WorkflowLoadError(f"Invalid workflow '{name}': {errors}")

        self._cache[name] = workflow
        logger.info(f"Loaded workflow: {name}")
        return workflow

    def load_all(self) -> dict[str, WorkflowDefinition]:
        """
        Load all workflows from directory.

        Returns:
            Dictionary of workflow name -> WorkflowDefinition

        Raises:
            WorkflowLoadError: If any workflow fails to load
        """
        if not self._workflows_dir.exists():
            return {}

        workflows = {}
        for path in self._workflows_dir.glob("*.yaml"):
            name = path.stem
            try:
                workflows[name] = self.load(name)
            except WorkflowLoadError as e:
                logger.error(f"Failed to load workflow {name}: {e}")
                raise

        for path in self._workflows_dir.glob("*.yml"):
            name = path.stem
            if name not in workflows:
                try:
                    workflows[name] = self.load(name)
                except WorkflowLoadError as e:
                    logger.error(f"Failed to load workflow {name}: {e}")
                    raise

        return workflows

    def _parse_yaml(self, path: Path) -> WorkflowDefinition:
        """Parse YAML file into WorkflowDefinition."""
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise WorkflowLoadError(f"Invalid YAML in {path}: {e}")  # noqa: B904

        if not isinstance(data, dict):
            raise WorkflowLoadError(f"Workflow must be a YAML object: {path}")

        # Required fields
        required = ["id", "name", "description", "tasks"]
        missing = [f for f in required if f not in data]
        if missing:
            raise WorkflowLoadError(f"Missing required fields: {missing}")

        # Parse tasks
        tasks = []
        for task_data in data["tasks"]:
            tasks.append(TaskNode(**task_data))

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

    def reload(self, name: str) -> WorkflowDefinition:
        """Force reload workflow (bypass cache)."""
        self._cache.pop(name, None)
        return self.load(name)

    def clear_cache(self) -> None:
        """Clear workflow cache."""
        self._cache.clear()
