"""Physical ownership and explicit run layout; no application defaults."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from ingest.manifests import require


def regular_relative(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    require(
        value == path.as_posix() and not path.is_absolute(),
        "Non-canonical relative path",
    )
    require(
        bool(path.parts) and all(part not in {".", "..", ""} for part in path.parts),
        "Path escape",
    )
    require("\\" not in value and "\0" not in value, "Invalid path spelling")
    return path


def physical(path: Path, owner: bool = True) -> Path:
    require(
        path.is_absolute() and ".." not in path.parts, "Explicit absolute path required"
    )
    for part in reversed((path, *path.parents)):
        require(not part.is_symlink(), "Symlink ancestor refused")
        # Root/system ancestors may be shared; the selected root itself must be owned.
        if part.exists() and owner and part == path:
            require(part.stat().st_uid == os.getuid(), "Selected path is not owned")
    return path.resolve(strict=False)


def within(path: Path, root: Path) -> bool:
    candidate = physical(path, owner=False)
    return candidate == root or root in candidate.parents


@dataclass(frozen=True)
class Layout:
    project: Path
    run_id: str

    def __post_init__(self) -> None:
        require(self.project == physical(self.project), "Project alias refused")
        require(self.project.is_dir(), "Project root absent")
        require(
            bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", self.run_id)),
            "Invalid run ID",
        )
        physical(self.workspace)
        physical(self.run)

    @property
    def workspace(self) -> Path:
        return self.project / ".friday_test"

    @property
    def run(self) -> Path:
        return self.workspace / "runs" / self.run_id

    @property
    def control(self) -> Path:
        return self.workspace / "control" / self.run_id

    def destination(self, relative: str) -> Path:
        path = self.run / regular_relative(relative)
        physical(path)
        require(within(path, self.run), "Run path escape")
        return path

    def create(self) -> None:
        require(not self.run.exists(), "Run root must be absent")
        self.run.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        physical(self.run.parent)
        self.run.mkdir(mode=0o700)
        for name in (
            "harness",
            "source-export",
            "source-git",
            "target",
            "config",
            "wheelhouse",
            "cache",
            "fixtures",
            "state",
            "logs",
            "reports",
        ):
            self.destination(name).mkdir(mode=0o700)
