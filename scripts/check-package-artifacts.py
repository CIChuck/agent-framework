#!/usr/bin/env python3
"""Validate built Friday distribution artifacts before upload."""

from __future__ import annotations

import argparse
import email
import sys
import tarfile
import zipfile
from pathlib import Path

EXPECTED_VERSION = "0.1.0a0"
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
        "friday_chat/config_templates/cli-config.example.yaml",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "artifact_dir",
        nargs="?",
        default="dist/pypi-reservation-0.1.0a0",
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


def validate_wheel(base: str, import_package: str | None, artifact_dir: Path) -> list[str]:
    errors: list[str] = []
    wheels = sorted(artifact_dir.glob(f"{base}-{EXPECTED_VERSION}-*.whl"))
    if len(wheels) != 1:
        return [f"{base}: expected one wheel, found {len(wheels)}"]

    wheel = wheels[0]
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
    if metadata.get("Version") != EXPECTED_VERSION:
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

    return errors


def validate_sdist(base: str, artifact_dir: Path) -> list[str]:
    sdists = sorted(artifact_dir.glob(f"{base}-{EXPECTED_VERSION}.tar.gz"))
    if len(sdists) != 1:
        return [f"{base}: expected one sdist, found {len(sdists)}"]
    return []


def validate_suspicious_paths(artifact_dir: Path, skipped_bases: set[str]) -> list[str]:
    errors: list[str] = []
    artifacts = sorted(artifact_dir.glob("*.whl")) + sorted(artifact_dir.glob("*.tar.gz"))
    for artifact in artifacts:
        if any(artifact.name.startswith(f"{base}-") for base in skipped_bases):
            continue
        for name in archive_names(artifact):
            if any(part in name for part in SUSPICIOUS_PATH_PARTS):
                errors.append(f"{artifact.name}: suspicious path {name}")
    return errors


def main() -> int:
    args = parse_args()
    artifact_dir = Path(args.artifact_dir)
    errors: list[str] = []

    if not artifact_dir.is_dir():
        print(f"{artifact_dir}: artifact directory does not exist", file=sys.stderr)
        return 1

    skipped_bases = set(args.skip_base)
    for base, import_package in EXPECTED_WHEELS.items():
        if base in skipped_bases:
            continue
        errors.extend(validate_wheel(base, import_package, artifact_dir))
        errors.extend(validate_sdist(base, artifact_dir))
    errors.extend(validate_suspicious_paths(artifact_dir, skipped_bases))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print(
        f"Validated {len(EXPECTED_WHEELS) - len(args.skip_base)} wheels and "
        f"{len(EXPECTED_WHEELS) - len(args.skip_base)} "
        f"sdists in {artifact_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
