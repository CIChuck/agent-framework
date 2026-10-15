#!/usr/bin/env python3
"""Validate built Friday distribution artifacts before upload."""

from __future__ import annotations

import argparse
import email
import re
import sys
import tarfile
import zipfile
from pathlib import Path

DEFAULT_VERSION = "0.1.0a3"
INTERNAL_DEP_RE = re.compile(
    r"^friday-(?:chat|framework(?:-[A-Za-z0-9_.-]+)?)(?:\[[^]]+\])?"
)
EXPECTED_WHEELS = {
    "friday_chat": "friday_chat",
    "friday_framework": None,
    "friday_framework_agent": "friday_agent",
    "friday_framework_cli": "friday_cli",
    "friday_framework_core": "friday_core",
    "friday_framework_finance": "friday_finance",
    "friday_framework_llm": "friday_llm",
    "friday_framework_mcp": "friday_mcp",
    "friday_framework_memory": "friday_memory",
    "friday_framework_moltbook": "friday_moltbook",
    "friday_framework_optimization": "friday_opt",
    "friday_framework_runtime": "friday_runtime",
    "friday_framework_sandbox": "friday_sandbox",
    "friday_framework_speech": "friday_speech",
    "friday_framework_telemetry": "friday_telemetry",
    "friday_framework_tools": "friday_tools",
    "friday_framework_transcript": "friday_transcript",
}
SUSPICIOUS_PATH_PARTS = (
    ".env",
    ".friday",
    "chroma",
    "transcript.db",
    "chroma.sqlite3",
    "keys.txt",
    "PyPI-Recovery-Codes",
)
EXPECTED_WHEEL_PATHS = {
    "friday_chat": (
        "friday_chat/config_templates/config.example.yaml",
        "friday_chat/config_templates/models-config.example.yaml",
        "friday_chat/config_templates/cli-config.example.yaml",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version",
        default=DEFAULT_VERSION,
        help="Expected distribution version.",
    )
    parser.add_argument(
        "--package",
        action="append",
        default=[],
        choices=sorted(EXPECTED_WHEELS),
        help="Artifact basename to validate. Repeat for multiple packages.",
    )
    parser.add_argument(
        "artifact_dir",
        nargs="?",
        default="dist/friday-package-cohort-0.1.0a3",
        help="Directory containing wheel and sdist artifacts.",
    )
    parser.add_argument(
        "--skip-base",
        action="append",
        default=[],
        help=(
            "Artifact basename to skip. May be provided multiple times; useful "
            "for already-uploaded immutable artifacts from a partial release."
        ),
    )
    return parser.parse_args()


def read_wheel_metadata(wheel: Path) -> email.message.Message:
    with zipfile.ZipFile(wheel) as archive:
        metadata_paths = [
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        ]
        if len(metadata_paths) != 1:
            raise ValueError(f"expected exactly one METADATA file, found {metadata_paths}")
        return email.message_from_bytes(archive.read(metadata_paths[0]))


def archive_names(artifact: Path) -> list[str]:
    if artifact.suffix == ".whl":
        with zipfile.ZipFile(artifact) as archive:
            return archive.namelist()
    if artifact.name.endswith(".tar.gz"):
        with tarfile.open(artifact) as archive:
            return archive.getnames()
    return []


def validate_internal_requirements(
    wheel_name: str,
    requirements: set[str],
    expected_version: str,
) -> list[str]:
    """Require one lock-step version for every Friday wheel dependency."""
    errors: list[str] = []
    for requirement in sorted(requirements):
        if INTERNAL_DEP_RE.match(requirement) is None:
            continue
        if f"=={expected_version}" not in requirement:
            errors.append(
                f"{wheel_name}: internal dependency is not pinned to "
                f"{expected_version}: {requirement}"
            )
    return errors


def validate_wheel(
    base: str,
    import_package: str | None,
    artifact_dir: Path,
    expected_version: str,
) -> list[str]:
    errors: list[str] = []
    wheels = sorted(artifact_dir.glob(f"{base}-{expected_version}-*.whl"))
    if len(wheels) != 1:
        return [f"{base}: expected one wheel, found {len(wheels)}"]

    wheel = wheels[0]
    if not wheel.name.endswith("-py3-none-any.whl"):
        errors.append(f"{wheel.name}: expected a universal py3-none-any wheel")
    names = archive_names(wheel)
    if import_package and not any(name.startswith(f"{import_package}/") for name in names):
        errors.append(f"{wheel.name}: missing import package {import_package}")
    for expected_path in EXPECTED_WHEEL_PATHS.get(base, ()):
        if expected_path not in names:
            errors.append(f"{wheel.name}: missing expected path {expected_path}")
    if import_package is None:
        code_paths = [
            name
            for name in names
            if "/" in name
            and not name.split("/", 1)[0].endswith(".dist-info")
            and not name.split("/", 1)[0].endswith(".data")
        ]
        if code_paths:
            errors.append(f"{wheel.name}: metadata-only wheel contains code paths")

    metadata = read_wheel_metadata(wheel)
    if metadata.get("Version") != expected_version:
        errors.append(f"{wheel.name}: unexpected Version {metadata.get('Version')!r}")
    if metadata.get("License-Expression") != "MIT" and metadata.get("License") != "MIT":
        errors.append(f"{wheel.name}: expected MIT license metadata")
    if metadata.get("Description-Content-Type") != "text/markdown":
        errors.append(f"{wheel.name}: expected markdown description content type")
    if not metadata.get_payload():
        errors.append(f"{wheel.name}: missing long description payload")
    project_urls = metadata.get_all("Project-URL", [])
    if not any(value.startswith("Repository, ") for value in project_urls):
        errors.append(f"{wheel.name}: missing Repository project URL")
    requirements = set(metadata.get_all("Requires-Dist", []))
    errors.extend(
        validate_internal_requirements(
            wheel.name,
            requirements,
            expected_version,
        )
    )
    if base == "friday_framework_llm":
        required_fragments = (
            f"friday-framework-core=={expected_version}",
            f"friday-framework-telemetry=={expected_version}",
            "litellm==1.94.1",
        )
        for fragment in required_fragments:
            if not any(requirement.startswith(fragment) for requirement in requirements):
                errors.append(f"{wheel.name}: missing exact dependency {fragment}")
    if base == "friday_chat":
        chat_required_fragments = (
            f"friday-framework-core=={expected_version}",
            f"friday-framework-runtime=={expected_version}",
            f"friday-framework-memory=={expected_version}",
            f"friday-framework-llm=={expected_version}",
            f"friday-framework-agent=={expected_version}",
            f"friday-framework-tools=={expected_version}",
            f"friday-framework-transcript=={expected_version}",
            f"friday-framework-cli=={expected_version}",
            f"friday-framework-speech=={expected_version}",
            f"friday-framework-finance=={expected_version}",
            f"friday-framework-tools[finance]=={expected_version}",
            f"friday-framework-sandbox=={expected_version}",
            f"friday-framework-tools[sandbox]=={expected_version}",
            f"friday-framework-moltbook=={expected_version}",
            f"friday-framework-tools[moltbook]=={expected_version}",
        )
        for fragment in chat_required_fragments:
            if not any(requirement.startswith(fragment) for requirement in requirements):
                errors.append(f"{wheel.name}: missing exact dependency {fragment}")
        full_extra_fragments = (
            f"friday-framework-finance=={expected_version}",
            f"friday-framework-moltbook=={expected_version}",
            f"friday-framework-sandbox=={expected_version}",
            f"friday-framework-speech=={expected_version}",
            f"friday-framework-tools[finance]=={expected_version}",
            f"friday-framework-tools[moltbook]=={expected_version}",
            f"friday-framework-tools[sandbox]=={expected_version}",
        )
        for fragment in full_extra_fragments:
            if not any(
                requirement.startswith(fragment) and "extra == 'full'" in requirement
                for requirement in requirements
            ):
                errors.append(
                    f"{wheel.name}: full extra missing exact dependency {fragment}"
                )
        entry_point_paths = [
            name for name in names if name.endswith(".dist-info/entry_points.txt")
        ]
        if len(entry_point_paths) != 1:
            errors.append(
                f"{wheel.name}: expected one entry_points.txt, "
                f"found {len(entry_point_paths)}"
            )
        else:
            with zipfile.ZipFile(wheel) as archive:
                entry_points = archive.read(entry_point_paths[0]).decode("utf-8")
            if "friday-chat = friday_chat.cli:app" not in entry_points:
                errors.append(f"{wheel.name}: friday-chat console entry point missing")

    return errors


def validate_sdist(
    base: str,
    artifact_dir: Path,
    expected_version: str,
) -> list[str]:
    sdists = sorted(artifact_dir.glob(f"{base}-{expected_version}.tar.gz"))
    if len(sdists) != 1:
        return [f"{base}: expected one sdist, found {len(sdists)}"]
    names = archive_names(sdists[0])
    required_suffixes: tuple[str, ...] = ()
    if base == "friday_framework_llm":
        required_suffixes = (
            "/pyproject.toml",
            "/README.md",
            "/LICENSE",
            "/src/friday_llm/__init__.py",
            "/tests_llm/test_generation.py",
        )
    elif base == "friday_chat":
        required_suffixes = (
            "/pyproject.toml",
            "/README.md",
            "/LICENSE",
            "/src/friday_chat/__init__.py",
            "/src/friday_chat/config_templates/config.example.yaml",
            "/src/friday_chat/config_templates/models-config.example.yaml",
            "/src/friday_chat/config_templates/cli-config.example.yaml",
            "/tests_chat/test_llm_config_migration.py",
            "/tests_chat/test_llm_adapter_migration.py",
        )
    return [
        f"{sdists[0].name}: missing required sdist content {suffix}"
        for suffix in required_suffixes
        if not any(name.endswith(suffix) for name in names)
    ]


def validate_suspicious_paths(artifact_dir: Path, selected_bases: set[str]) -> list[str]:
    errors: list[str] = []
    artifacts = sorted(artifact_dir.glob("*.whl")) + sorted(artifact_dir.glob("*.tar.gz"))
    for artifact in artifacts:
        if not any(artifact.name.startswith(f"{base}-") for base in selected_bases):
            continue
        for name in archive_names(artifact):
            if any(part in name for part in SUSPICIOUS_PATH_PARTS):
                errors.append(f"{artifact.name}: suspicious path {name}")
    return errors


def validate_suspicious_content(
    artifact_dir: Path,
    selected_bases: set[str],
) -> list[str]:
    errors: list[str] = []
    secret_pattern = re.compile(rb"(?:sk|pypi)-[A-Za-z0-9_-]{20,}")
    for artifact in sorted(artifact_dir.glob("*.whl")) + sorted(
        artifact_dir.glob("*.tar.gz")
    ):
        if not any(artifact.name.startswith(f"{base}-") for base in selected_bases):
            continue
        if artifact.suffix == ".whl":
            with zipfile.ZipFile(artifact) as archive:
                members = ((name, archive.read(name)) for name in archive.namelist())
                for name, content in members:
                    if secret_pattern.search(content) or b"/Users/" in content:
                        errors.append(f"{artifact.name}: sensitive content in {name}")
        else:
            with tarfile.open(artifact) as archive:
                for member in archive.getmembers():
                    extracted = archive.extractfile(member) if member.isfile() else None
                    content = extracted.read() if extracted is not None else b""
                    if secret_pattern.search(content) or b"/Users/" in content:
                        errors.append(
                            f"{artifact.name}: sensitive content in {member.name}"
                        )
    return errors


def main() -> int:
    args = parse_args()
    artifact_dir = Path(args.artifact_dir)
    errors: list[str] = []

    if not artifact_dir.is_dir():
        print(f"{artifact_dir}: artifact directory does not exist", file=sys.stderr)
        return 1

    skipped_bases = set(args.skip_base)
    selected_bases = set(args.package) or set(EXPECTED_WHEELS)
    selected_bases -= skipped_bases
    for base in sorted(selected_bases):
        errors.extend(
            validate_wheel(
                base,
                EXPECTED_WHEELS[base],
                artifact_dir,
                args.version,
            )
        )
        errors.extend(validate_sdist(base, artifact_dir, args.version))
    errors.extend(validate_suspicious_paths(artifact_dir, selected_bases))
    errors.extend(validate_suspicious_content(artifact_dir, selected_bases))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print(
        f"Validated {len(selected_bases)} wheels and "
        f"{len(selected_bases)} "
        f"sdists in {artifact_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
