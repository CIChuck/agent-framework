#!/usr/bin/env python3
"""Validate Friday package metadata before publishing."""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

DEFAULT_VERSION = "0.1.0a3"
DEFAULT_INTERNAL_VERSION = "0.1.0a3"
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument(
        "--internal-version",
        default=DEFAULT_INTERNAL_VERSION,
        help="Required exact version for internal Friday dependencies.",
    )
    parser.add_argument(
        "--internal-pin",
        action="append",
        default=[],
        metavar="NAME=VERSION",
        help=(
            "Override the required exact version for one internal Friday "
            "dependency. Repeat for mixed-version component releases."
        ),
    )
    parser.add_argument(
        "--package",
        action="append",
        default=[],
        help="Distribution name to validate. Repeat for multiple packages.",
    )
    return parser.parse_args()


def parse_internal_pins(values: list[str]) -> dict[str, str]:
    """Parse explicit mixed-version dependency expectations."""
    pins: dict[str, str] = {}
    for value in values:
        name, separator, version = value.partition("=")
        if not separator or not name.strip() or not version.strip():
            raise ValueError(f"invalid --internal-pin {value!r}; expected NAME=VERSION")
        normalized_name = name.strip().lower().replace("_", "-")
        if not INTERNAL_DEP_RE.fullmatch(normalized_name):
            raise ValueError(f"invalid internal Friday dependency name: {name!r}")
        if normalized_name in pins:
            raise ValueError(f"duplicate --internal-pin for {normalized_name}")
        pins[normalized_name] = version.strip()
    return pins


def project_paths(selected_packages: set[str]) -> list[Path]:
    paths = [Path("pyproject.toml"), *sorted(Path("packages").glob("*/pyproject.toml"))]
    if not selected_packages:
        return paths
    selected: list[Path] = []
    found: set[str] = set()
    for path in paths:
        data = tomllib.loads(path.read_text())
        name = data.get("project", {}).get("name")
        if isinstance(name, str) and name in selected_packages:
            selected.append(path)
            found.add(name)
    missing = selected_packages - found
    if missing:
        raise ValueError(f"unknown package selection: {', '.join(sorted(missing))}")
    return selected


def collect_dependencies(project: dict[str, object]) -> list[str]:
    raw_dependencies = project.get("dependencies", [])
    dependencies = (
        [value for value in raw_dependencies if isinstance(value, str)]
        if isinstance(raw_dependencies, list)
        else []
    )
    optional = project.get("optional-dependencies", {})
    if isinstance(optional, dict):
        for extra_dependencies in optional.values():
            if isinstance(extra_dependencies, list):
                dependencies.extend(
                    value for value in extra_dependencies if isinstance(value, str)
                )
    return dependencies


def validate_project(
    path: Path,
    *,
    expected_version: str,
    internal_version: str,
    internal_pins: dict[str, str] | None = None,
) -> list[str]:
    data = tomllib.loads(path.read_text())
    project = data.get("project", {})
    errors: list[str] = []

    name = project.get("name")
    version = project.get("version")

    if version != expected_version:
        errors.append(f"{path}: expected version {expected_version}, got {version!r}")
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

    expected_pins = internal_pins or {}
    for dependency in collect_dependencies(project):
        match = INTERNAL_DEP_RE.search(dependency)
        if match is not None:
            dependency_name = match.group(0).lower().replace("_", "-")
            expected_internal_version = expected_pins.get(
                dependency_name,
                internal_version,
            )
            if f"=={expected_internal_version}" in dependency:
                continue
            errors.append(
                f"{path}: internal dependency is not pinned to "
                f"{expected_internal_version}: {dependency!r}"
            )

    return errors


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    try:
        internal_pins = parse_internal_pins(args.internal_pin)
        paths = project_paths(set(args.package))
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    for path in paths:
        errors.extend(
            validate_project(
                path,
                expected_version=args.version,
                internal_version=args.internal_version,
                internal_pins=internal_pins,
            )
        )

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
