"""Cross-package metadata contract for the lock-step Friday release cohort."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import tomllib
from packaging.requirements import Requirement

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
COHORT_VERSION = "0.1.0a2"
COHORT_DISTRIBUTIONS = {
    "friday-chat",
    "friday-framework",
    "friday-framework-agent",
    "friday-framework-cli",
    "friday-framework-core",
    "friday-framework-finance",
    "friday-framework-llm",
    "friday-framework-mcp",
    "friday-framework-memory",
    "friday-framework-moltbook",
    "friday-framework-optimization",
    "friday-framework-runtime",
    "friday-framework-sandbox",
    "friday-framework-speech",
    "friday-framework-telemetry",
    "friday-framework-tools",
    "friday-framework-transcript",
}
INTERNAL_DEPENDENCY = re.compile(
    r"friday-(?:chat|framework(?:-[A-Za-z0-9_.-]+)?)(?:\[[^]]+\])?"
)
VERSION_FILES = {
    "friday-chat": "packages/friday-chat/src/friday_chat/__init__.py",
    "friday-framework-cli": "packages/friday-cli/src/friday_cli/__init__.py",
    "friday-framework-core": "packages/friday-core/src/friday_core/__init__.py",
    "friday-framework-mcp": "packages/friday-mcp/src/friday_mcp/__init__.py",
    "friday-framework-moltbook": (
        "packages/friday-moltbook/src/friday_moltbook/__init__.py"
    ),
    "friday-framework-sandbox": (
        "packages/friday-sandbox/src/friday_sandbox/__init__.py"
    ),
    "friday-framework-telemetry": (
        "packages/friday-telemetry/src/friday_telemetry/__init__.py"
    ),
    "friday-framework-tools": "packages/friday-tools/src/friday_tools/__init__.py",
}


def _project_paths() -> list[Path]:
    return [
        REPOSITORY_ROOT / "pyproject.toml",
        *sorted((REPOSITORY_ROOT / "packages").glob("*/pyproject.toml")),
    ]


def _dependencies(project: dict[str, object]) -> list[str]:
    raw_dependencies = project.get("dependencies", [])
    values = (
        [value for value in raw_dependencies if isinstance(value, str)]
        if isinstance(raw_dependencies, list)
        else []
    )
    optional = project.get("optional-dependencies", {})
    if isinstance(optional, dict):
        for dependencies in optional.values():
            if isinstance(dependencies, list):
                values.extend(
                    value for value in dependencies if isinstance(value, str)
                )
    return values


def test_all_friday_projects_and_internal_pins_are_lockstep() -> None:
    paths = _project_paths()

    assert len(paths) == 17
    project_names = {
        tomllib.loads(path.read_text(encoding="utf-8"))["project"]["name"]
        for path in paths
    }
    assert project_names == COHORT_DISTRIBUTIONS
    for path in paths:
        project = tomllib.loads(path.read_text(encoding="utf-8"))["project"]
        assert project["version"] == COHORT_VERSION, path
        for dependency in _dependencies(project):
            if INTERNAL_DEPENDENCY.search(dependency):
                assert f"=={COHORT_VERSION}" in dependency, (path, dependency)


def test_root_all_extra_covers_every_package_distribution() -> None:
    root_project = tomllib.loads(
        (REPOSITORY_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    requirements = [
        *root_project["dependencies"],
        *root_project["optional-dependencies"]["all"],
    ]
    included_distributions = {
        Requirement(requirement).name
        for requirement in requirements
        if INTERNAL_DEPENDENCY.search(requirement)
    }

    assert included_distributions == COHORT_DISTRIBUTIONS - {"friday-framework"}


def test_exported_runtime_versions_match_source_metadata() -> None:
    projects = {
        project["name"]: project["version"]
        for path in _project_paths()
        for project in [
            tomllib.loads(path.read_text(encoding="utf-8"))["project"]
        ]
    }
    for distribution, relative_path in VERSION_FILES.items():
        module = ast.parse(
            (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8")
        )
        versions = [
            node.value.value
            for node in module.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "__version__"
                for target in node.targets
            )
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ]
        assert versions == [projects[distribution]]
