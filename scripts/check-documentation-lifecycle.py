#!/usr/bin/env python3
"""Validate documentation navigation, lifecycle packets, and local links."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPOSITORY_ROOT / "docs"
BASELINE_COMMIT = "482b857507409fb73556e273f96acdce1c398480"
PLANNING_LANES = ("active", "queued", "blocked", "deferred", "backlog")
RETIRED_PATH = "docs/planning/build-plans/friday-chat-v2-aechive"
RETIRED_PATH_EXEMPTIONS = {
    DOCS_ROOT
    / "planning"
    / "active"
    / "documentation-governance"
    / "README.md",
    DOCS_ROOT
    / "planning"
    / "active"
    / "documentation-governance"
    / "classification-ledger.md",
    DOCS_ROOT
    / "planning"
    / "active"
    / "documentation-governance"
    / "current-state-authority-manifest.md",
}
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
STATUS_PATTERN = re.compile(r"(?im)^(?:[-*]\s*)?(?:\*\*)?status(?:\*\*)?\s*:")


def _git_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [REPOSITORY_ROOT / line for line in result.stdout.splitlines()]


def _markdown_files() -> list[Path]:
    return sorted(
        path
        for path in _git_paths()
        if path.suffix.lower() == ".md"
        and (path == REPOSITORY_ROOT / "AGENTS.md" or DOCS_ROOT in path.parents)
        and path.exists()
    )


def _extract_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    elif " " in target:
        target = target.split(" ", 1)[0]
    return unquote(target.split("#", 1)[0].split("?", 1)[0])


def _resolve_target(source: Path, target: str) -> Path | None:
    if not target or target.startswith(("http://", "https://", "mailto:", "data:")):
        return None
    if "://" in target or "{" in target or "}" in target:
        return None
    candidate = Path(target)
    if candidate.is_absolute():
        return candidate
    return (source.parent / candidate).resolve()


def _check_links(markdown_files: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in markdown_files:
        in_fence = False
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if line.lstrip().startswith(("```", "~~~")):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for match in LINK_PATTERN.finditer(line):
                target = _extract_link_target(match.group(1))
                resolved = _resolve_target(path, target)
                if resolved is not None and not resolved.exists():
                    relative_source = path.relative_to(REPOSITORY_ROOT)
                    errors.append(
                        f"{relative_source}:{line_number}: broken link {match.group(1)!r}"
                    )
    return errors


def _check_planning_packets() -> list[str]:
    errors: list[str] = []
    for lane in PLANNING_LANES:
        lane_path = DOCS_ROOT / "planning" / lane
        if not lane_path.exists():
            errors.append(f"docs/planning/{lane}: missing lifecycle lane")
            continue
        for packet in sorted(path for path in lane_path.iterdir() if path.is_dir()):
            index = packet / "README.md"
            relative_packet = packet.relative_to(REPOSITORY_ROOT)
            if not index.exists():
                errors.append(f"{relative_packet}: missing README.md")
                continue
            header = "\n".join(index.read_text(encoding="utf-8").splitlines()[:40])
            if not STATUS_PATTERN.search(header):
                errors.append(f"{relative_packet}: README.md has no visible status")
    return errors


def _check_retired_path(markdown_files: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in markdown_files:
        if path in RETIRED_PATH_EXEMPTIONS:
            continue
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if RETIRED_PATH in line:
                relative_source = path.relative_to(REPOSITORY_ROOT)
                errors.append(
                    f"{relative_source}:{line_number}: references retired archive path"
                )
    return errors


def _check_guides_unchanged() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--quiet", BASELINE_COMMIT, "--", "docs/guides"],
        cwd=REPOSITORY_ROOT,
        check=False,
    )
    if result.returncode == 0:
        return []
    return [f"docs/guides: differs from protected baseline {BASELINE_COMMIT}"]


def main() -> int:
    markdown_files = _markdown_files()
    errors = [
        *_check_planning_packets(),
        *_check_links(markdown_files),
        *_check_retired_path(markdown_files),
        *_check_guides_unchanged(),
    ]
    if errors:
        print("Documentation lifecycle validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "Documentation lifecycle validation passed: "
        f"{len(markdown_files)} Markdown files checked"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
