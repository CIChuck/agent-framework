"""UI-neutral destination and containment rules for transcript exports."""

from __future__ import annotations

from pathlib import Path


def resolve_export_directory(raw_directory: str | None) -> Path:
    """Resolve and create the configured export root, defaulting to ``./exports``."""
    directory = Path(raw_directory or "./exports")
    resolved = directory.resolve(strict=False)
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def safe_export_path(root: Path, *parts: str) -> Path:
    """Resolve a child path and reject destinations outside the export root."""
    resolved_root = root.resolve(strict=False)
    candidate = resolved_root.joinpath(*parts).resolve(strict=False)
    if not candidate.is_relative_to(resolved_root):
        raise ValueError("export path escaped configured root")
    return candidate
