"""Bounded metadata-only detection; never an OS sandbox or payload scan."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

from ingest.manifests import canonical, require
from ingest.paths import physical


@dataclass(frozen=True)
class Snapshot:
    sha256: str
    entries: int
    roots: tuple[str, ...]

    def record(self) -> dict[str, object]:
        return {
            "sha256": self.sha256,
            "entries": self.entries,
            "roots": list(self.roots),
            "evidence_class": "bounded_metadata_detection",
        }


def snapshot(roots: tuple[Path, ...], maximum: int) -> Snapshot:
    require(
        0 < maximum <= 1_000_000 and bool(roots),
        "Explicit finite snapshot scope required",
    )
    digest = hashlib.sha256()
    count = 0
    for root in sorted(roots):
        physical(root)
        pending = [root]
        while pending:
            path = pending.pop()
            require(count < maximum, "Snapshot coverage would truncate")
            require(not path.is_symlink(), "Snapshot symlink refused")
            if not path.exists():
                row: dict[str, object] = {"path": str(path), "absent": True}
            else:
                info = path.stat()
                row = {
                    "path": str(path),
                    "mode": info.st_mode,
                    "size": info.st_size,
                    "mtime_ns": info.st_mtime_ns,
                }
                if path.is_dir():
                    with os.scandir(path) as entries:
                        children = sorted(Path(entry.path) for entry in entries)
                    require(
                        len(children) + count <= maximum,
                        "Snapshot coverage would truncate",
                    )
                    pending.extend(reversed(children))
            digest.update(canonical(row) + b"\n")
            count += 1
    return Snapshot(digest.hexdigest(), count, tuple(str(root) for root in roots))


def unchanged(before: Snapshot, after: Snapshot) -> None:
    require(
        before == after, "Protected metadata changed: isolation FAILED, no restoration"
    )
