"""Export destinations are resolved without importing a frontend."""

from __future__ import annotations

from pathlib import Path

import pytest
from friday_runtime.transcript_export_paths import (
    resolve_export_directory,
    safe_export_path,
)


@pytest.mark.parametrize("raw_directory", [None, ""])
def test_default_root_is_anchored_to_current_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    raw_directory: str | None,
) -> None:
    monkeypatch.chdir(tmp_path)

    root = resolve_export_directory(raw_directory)

    assert root == tmp_path / "exports"
    assert root.is_dir()
    assert tuple(root.iterdir()) == ()


def test_relative_and_absolute_roots_create_parents_and_allow_repeat_calls(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    relative_root = tmp_path / "nested" / "exports"
    absolute_root = tmp_path / "elsewhere" / "exports"

    assert resolve_export_directory("nested/exports") == relative_root
    assert resolve_export_directory("nested/exports") == relative_root
    assert resolve_export_directory(str(absolute_root)) == absolute_root
    assert relative_root.is_dir()
    assert absolute_root.is_dir()
    assert tuple(relative_root.iterdir()) == ()
    assert tuple(absolute_root.iterdir()) == ()


def test_root_that_is_a_file_fails_without_replacing_it(tmp_path: Path) -> None:
    root = tmp_path / "exports"
    root.write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        resolve_export_directory(str(root))

    assert root.read_text(encoding="utf-8") == "existing"


def test_safe_paths_resolve_inside_root_without_creating_files(tmp_path: Path) -> None:
    root = resolve_export_directory(str(tmp_path / "exports"))

    assert safe_export_path(root) == root
    assert (
        safe_export_path(root, "nested", "entry.csv") == root / "nested" / "entry.csv"
    )
    assert tuple(root.iterdir()) == ()


@pytest.mark.parametrize("parts", [("..", "outside.csv"), ("../outside.csv",)])
def test_traversal_is_rejected_without_creating_an_outside_file(
    tmp_path: Path,
    parts: tuple[str, ...],
) -> None:
    root = resolve_export_directory(str(tmp_path / "exports"))

    with pytest.raises(ValueError, match="^export path escaped configured root$"):
        safe_export_path(root, *parts)

    assert not (tmp_path / "outside.csv").exists()
    assert tuple(root.iterdir()) == ()


def test_existing_file_and_directory_symlinks_cannot_escape_root(
    tmp_path: Path,
) -> None:
    root = resolve_export_directory(str(tmp_path / "exports"))
    outside_file = tmp_path / "outside.csv"
    outside_file.write_text("unchanged", encoding="utf-8")
    outside_directory = tmp_path / "outside-dir"
    outside_directory.mkdir()
    (root / "linked-file.csv").symlink_to(outside_file)
    (root / "linked-dir").symlink_to(outside_directory, target_is_directory=True)

    for parts in (("linked-file.csv",), ("linked-dir", "new.csv")):
        with pytest.raises(ValueError, match="^export path escaped configured root$"):
            safe_export_path(root, *parts)

    assert outside_file.read_text(encoding="utf-8") == "unchanged"
    assert tuple(outside_directory.iterdir()) == ()


def test_symlinked_root_resolves_to_target_and_keeps_children_inside(
    tmp_path: Path,
) -> None:
    target = tmp_path / "real-exports"
    target.mkdir()
    link = tmp_path / "exports-link"
    link.symlink_to(target, target_is_directory=True)

    assert resolve_export_directory(str(link)) == target
    assert safe_export_path(link, "sessions.csv") == target / "sessions.csv"
    assert tuple(target.iterdir()) == ()
