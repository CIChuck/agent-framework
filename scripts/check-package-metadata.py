#!/usr/bin/env python3
"""Validate Friday package metadata before publishing."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path


EXPECTED_VERSION = "0.1.0a0"
EXPECTED_AUTHOR = [{"name": "Friday Team"}]
EXPECTED_LICENSE = "MIT"
REPO_URL = "https://github.com/CIChuck/agent-framework"
INTERNAL_DEP_RE = re.compile(r"friday-(?:chat|framework(?:-[A-Za-z0-9_.-]+)?)")
REQUIRED_URLS = ("Homepage", "Repository", "Issues", "Documentation", "Source")
REQUIRED_DEPENDENCY_PROJECTS = {
    "friday-framework",
    "friday-framework-agent",
    "friday-chat",
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


def project_paths() -> list[Path]:
    return [Path("pyproject.toml"), *sorted(Path("packages").glob("*/pyproject.toml"))]


def collect_dependencies(project: dict[str, object]) -> list[str]:
    dependencies = list(project.get("dependencies", []))
    optional = project.get("optional-dependencies", {})
    if isinstance(optional, dict):
        for extra_dependencies in optional.values():
            dependencies.extend(extra_dependencies)
    return dependencies


def validate_project(path: Path) -> list[str]:
    data = tomllib.loads(path.read_text())
    project = data.get("project", {})
    errors: list[str] = []

    name = project.get("name")
    version = project.get("version")

    if version != EXPECTED_VERSION:
        errors.append(f"{path}: expected version {EXPECTED_VERSION}, got {version!r}")
    if project.get("license") != EXPECTED_LICENSE:
        errors.append(f"{path}: expected license {EXPECTED_LICENSE!r}")
    if project.get("authors") != EXPECTED_AUTHOR:
        errors.append(f"{path}: expected authors {EXPECTED_AUTHOR!r}")

    readme = project.get("readme")
    if readme != "README.md":
        errors.append(f"{path}: expected readme = 'README.md'")
    elif not (path.parent / readme).is_file():
        errors.append(f"{path}: README.md does not exist beside pyproject.toml")

    urls = project.get("urls", {})
    if not isinstance(urls, dict):
        errors.append(f"{path}: project.urls is missing or malformed")
    else:
        for key in REQUIRED_URLS:
            value = urls.get(key)
            if not isinstance(value, str) or not value.startswith(REPO_URL):
                errors.append(f"{path}: project.urls.{key} must start with {REPO_URL}")

    if name in REQUIRED_DEPENDENCY_PROJECTS and "dependencies" not in project:
        errors.append(f"{path}: project.dependencies is missing")

    wheel_config = data.get("tool", {}).get("hatch", {}).get("build", {}).get(
        "targets", {}
    ).get("wheel", {})
    packages = wheel_config.get("packages")
    if name != "friday-framework" and not packages:
        errors.append(f"{path}: wheel package selection is missing")

    for dependency in collect_dependencies(project):
        if INTERNAL_DEP_RE.search(dependency) and f"=={EXPECTED_VERSION}" not in dependency:
            errors.append(
                f"{path}: internal dependency is not pinned to "
                f"{EXPECTED_VERSION}: {dependency!r}"
            )

    return errors


def main() -> int:
    errors: list[str] = []
    paths = project_paths()
    for path in paths:
        errors.extend(validate_project(path))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print(
        f"Validated {len(paths)} pyproject.toml files: version, license, "
        "authors, README, URLs, wheel package selection, and internal pins OK"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
