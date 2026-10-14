from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import cast

import pytest
import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BOARD_SCRIPT = REPOSITORY_ROOT / "scripts" / "friday-dev-board.py"


def _run(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BOARD_SCRIPT), "--root", str(root), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def _write_minimal_board(root: Path) -> None:
    for lane in ("active", "queued", "review", "blocked", "deferred", "backlog"):
        (root / "docs" / "planning" / lane).mkdir(parents=True, exist_ok=True)
    packet = root / "docs" / "planning" / "queued" / "example-task"
    packet.mkdir()
    (packet / "README.md").write_text(
        "# Example task\n\nStatus: queued\n", encoding="utf-8"
    )
    board = {
        "version": 1,
        "updated": "2026-09-03",
        "tasks": [
            {
                "id": "example-task",
                "title": "Example task",
                "priority": 1,
                "work_state": "queued",
                "condition": "normal",
                "implementation_authority": "not_granted",
                "packet": "docs/planning/queued/example-task/",
                "next_gate": "maintainer approval",
                "delivery_state": "not_started",
                "branch": None,
                "depends_on": [],
                "validation": [],
            }
        ],
        "events": [],
    }
    board_path = root / "docs" / "planning" / "board.yaml"
    board_path.write_text(yaml.safe_dump(board, sort_keys=False), encoding="utf-8")
    shutil.copyfile(
        REPOSITORY_ROOT / "docs" / "planning" / "board.schema.json",
        root / "docs" / "planning" / "board.schema.json",
    )
    result = _run(root, "render")
    assert result.returncode == 0, result.stdout + result.stderr


def _load_task(root: Path) -> dict[str, object]:
    board = yaml.safe_load(
        (root / "docs" / "planning" / "board.yaml").read_text(encoding="utf-8")
    )
    return cast(dict[str, object], board["tasks"][0])


def test_repository_development_board_is_valid_and_rendered() -> None:
    result = _run(REPOSITORY_ROOT, "validate")

    assert result.returncode == 0, result.stdout + result.stderr
    board = yaml.safe_load(
        (REPOSITORY_ROOT / "docs/planning/board.yaml").read_text(encoding="utf-8")
    )
    assert f"{len(board['tasks'])} tasks" in result.stdout

    agent_instructions = (REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "canonical operational entry point" in agent_instructions
    assert "scripts/friday-dev-board.py validate" in agent_instructions
    assert (
        "queued -> approved -> started -> completed -> accepted" in agent_instructions
    )
    assert "docs/planning/review/" in agent_instructions


def test_next_reports_the_highest_priority_gate(tmp_path: Path) -> None:
    _write_minimal_board(tmp_path)

    result = _run(tmp_path, "next")

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.startswith("AWAITING_APPROVAL example-task:")


def test_agent_cannot_approve_work(tmp_path: Path) -> None:
    _write_minimal_board(tmp_path)

    result = _run(
        tmp_path,
        "transition",
        "example-task",
        "approved",
        "--actor",
        "Codex",
        "--actor-role",
        "agent",
        "--note",
        "Attempted self-approval",
        "--next-gate",
        "start work",
    )

    assert result.returncode == 1
    assert "only a maintainer" in result.stderr
    assert _load_task(tmp_path)["work_state"] == "queued"


def test_legacy_approval_cannot_start_without_current_reapproval(
    tmp_path: Path,
) -> None:
    _write_minimal_board(tmp_path)
    board_path = tmp_path / "docs" / "planning" / "board.yaml"
    board = yaml.safe_load(board_path.read_text(encoding="utf-8"))
    task = board["tasks"][0]
    task["work_state"] = "approved"
    task["implementation_authority"] = "design_only"
    task["legacy_import"] = True
    board_path.write_text(yaml.safe_dump(board, sort_keys=False), encoding="utf-8")
    rendered = _run(tmp_path, "render")
    assert rendered.returncode == 0, rendered.stdout + rendered.stderr

    queued = tmp_path / "docs" / "planning" / "queued" / "example-task"
    active = tmp_path / "docs" / "planning" / "active" / "example-task"
    queued.rename(active)
    result = _run(
        tmp_path,
        "transition",
        "example-task",
        "started",
        "--packet",
        "docs/planning/active/example-task/",
        "--branch",
        "feature/example-task",
        "--actor",
        "Codex",
        "--actor-role",
        "agent",
        "--note",
        "Attempted execution from an imported approval",
        "--next-gate",
        "complete implementation",
    )

    assert result.returncode == 1
    assert "legacy approval must return to queued" in result.stderr


def test_started_and_completed_transitions_enforce_gates(tmp_path: Path) -> None:
    _write_minimal_board(tmp_path)
    approval = _run(
        tmp_path,
        "transition",
        "example-task",
        "approved",
        "--actor",
        "Maintainer",
        "--actor-role",
        "maintainer",
        "--note",
        "Approved bounded implementation",
        "--next-gate",
        "start approved work",
    )
    assert approval.returncode == 0, approval.stdout + approval.stderr

    queued = tmp_path / "docs" / "planning" / "queued" / "example-task"
    active = tmp_path / "docs" / "planning" / "active" / "example-task"
    queued.rename(active)
    started = _run(
        tmp_path,
        "transition",
        "example-task",
        "started",
        "--packet",
        "docs/planning/active/example-task/",
        "--branch",
        "feature/example-task",
        "--actor",
        "Codex",
        "--actor-role",
        "agent",
        "--note",
        "Started approved work",
        "--next-gate",
        "complete implementation",
    )
    assert started.returncode == 0, started.stdout + started.stderr

    review = tmp_path / "docs" / "planning" / "review" / "example-task"
    active.rename(review)
    missing_evidence = _run(
        tmp_path,
        "transition",
        "example-task",
        "completed",
        "--packet",
        "docs/planning/review/example-task/",
        "--actor",
        "Codex",
        "--actor-role",
        "agent",
        "--note",
        "Completion without evidence",
        "--next-gate",
        "maintainer acceptance",
    )
    assert missing_evidence.returncode == 1
    assert "requires at least one --evidence" in missing_evidence.stderr

    completed = _run(
        tmp_path,
        "transition",
        "example-task",
        "completed",
        "--packet",
        "docs/planning/review/example-task/",
        "--evidence",
        "focused tests passed",
        "--actor",
        "Codex",
        "--actor-role",
        "agent",
        "--note",
        "Ready for maintainer review",
        "--next-gate",
        "maintainer acceptance",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    task = _load_task(tmp_path)
    assert task["work_state"] == "completed"
    assert task["validation"] == ["focused tests passed"]

    archive = tmp_path / "docs" / "archive" / "completed" / "2026" / "example-task"
    archive.parent.mkdir(parents=True)
    review.rename(archive)
    agent_acceptance = _run(
        tmp_path,
        "transition",
        "example-task",
        "accepted",
        "--packet",
        "docs/archive/completed/2026/example-task/",
        "--actor",
        "Codex",
        "--actor-role",
        "agent",
        "--note",
        "Attempted self-acceptance",
        "--next-gate",
        "none",
    )
    assert agent_acceptance.returncode == 1
    assert "only a maintainer" in agent_acceptance.stderr

    acceptance = _run(
        tmp_path,
        "transition",
        "example-task",
        "accepted",
        "--packet",
        "docs/archive/completed/2026/example-task/",
        "--actor",
        "Maintainer",
        "--actor-role",
        "maintainer",
        "--note",
        "Accepted completed work",
        "--next-gate",
        "none",
    )
    assert acceptance.returncode == 0, acceptance.stdout + acceptance.stderr
    assert _load_task(tmp_path)["work_state"] == "accepted"

    missing_merge_evidence = _run(
        tmp_path,
        "set-delivery",
        "example-task",
        "merged",
        "--actor",
        "Codex",
        "--actor-role",
        "agent",
        "--note",
        "Observed merge",
    )
    assert missing_merge_evidence.returncode == 1
    assert "requires --evidence" in missing_merge_evidence.stderr

    merged = _run(
        tmp_path,
        "set-delivery",
        "example-task",
        "merged",
        "--actor",
        "Codex",
        "--actor-role",
        "agent",
        "--note",
        "Observed merge",
        "--evidence",
        "merge commit abc123",
    )
    assert merged.returncode == 0, merged.stdout + merged.stderr
    assert _load_task(tmp_path)["delivery_state"] == "merged"


@pytest.mark.parametrize(
    "delivery_state",
    ["local", "pushed", "merged", "released", "unknown"],
)
def test_reopening_completed_work_preserves_delivery_state(
    tmp_path: Path,
    delivery_state: str,
) -> None:
    _write_minimal_board(tmp_path)
    approval = _run(
        tmp_path,
        "transition",
        "example-task",
        "approved",
        "--actor",
        "Maintainer",
        "--actor-role",
        "maintainer",
        "--note",
        "Approved bounded implementation",
        "--next-gate",
        "start approved work",
    )
    assert approval.returncode == 0, approval.stdout + approval.stderr

    queued = tmp_path / "docs" / "planning" / "queued" / "example-task"
    active = tmp_path / "docs" / "planning" / "active" / "example-task"
    queued.rename(active)
    started = _run(
        tmp_path,
        "transition",
        "example-task",
        "started",
        "--packet",
        "docs/planning/active/example-task/",
        "--branch",
        "feature/example-task",
        "--actor",
        "Codex",
        "--actor-role",
        "agent",
        "--note",
        "Started approved work",
        "--next-gate",
        "complete implementation",
    )
    assert started.returncode == 0, started.stdout + started.stderr
    assert _load_task(tmp_path)["delivery_state"] == "local"

    review = tmp_path / "docs" / "planning" / "review" / "example-task"
    active.rename(review)
    completed = _run(
        tmp_path,
        "transition",
        "example-task",
        "completed",
        "--packet",
        "docs/planning/review/example-task/",
        "--evidence",
        "focused tests passed",
        "--actor",
        "Codex",
        "--actor-role",
        "agent",
        "--note",
        "Ready for maintainer review",
        "--next-gate",
        "maintainer acceptance",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr

    board_path = tmp_path / "docs" / "planning" / "board.yaml"
    board = yaml.safe_load(board_path.read_text(encoding="utf-8"))
    board["tasks"][0]["delivery_state"] = delivery_state
    board_path.write_text(yaml.safe_dump(board, sort_keys=False), encoding="utf-8")
    rendered = _run(tmp_path, "render")
    assert rendered.returncode == 0, rendered.stdout + rendered.stderr

    review.rename(active)
    reopened = _run(
        tmp_path,
        "transition",
        "example-task",
        "started",
        "--packet",
        "docs/planning/active/example-task/",
        "--actor",
        "Codex",
        "--actor-role",
        "agent",
        "--note",
        "Reopened completed work",
        "--next-gate",
        "complete remediation",
    )

    assert reopened.returncode == 0, reopened.stdout + reopened.stderr
    assert _load_task(tmp_path)["delivery_state"] == delivery_state


def test_delivery_state_cannot_move_backward(tmp_path: Path) -> None:
    _write_minimal_board(tmp_path)
    merged = _run(
        tmp_path,
        "set-delivery",
        "example-task",
        "merged",
        "--actor",
        "Codex",
        "--actor-role",
        "agent",
        "--note",
        "Observed merge",
        "--evidence",
        "merge commit abc123",
    )
    assert merged.returncode == 0, merged.stdout + merged.stderr
    assert _load_task(tmp_path)["delivery_state"] == "merged"

    backward = _run(
        tmp_path,
        "set-delivery",
        "example-task",
        "pushed",
        "--actor",
        "Codex",
        "--actor-role",
        "agent",
        "--note",
        "Attempted delivery downgrade",
    )

    assert backward.returncode == 1
    assert "delivery cannot move backward: merged -> pushed" in backward.stderr
    assert _load_task(tmp_path)["delivery_state"] == "merged"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _historical_fixture(root: Path, state: str = "completed") -> list[dict[str, str]]:
    _write_minimal_board(root)
    planning = root / "docs/planning"
    queued = planning / "queued/example-task"
    active = planning / "active/example-task"
    queued.rename(active)
    names = {
        "index": "README.md",
        "authority": "authority.json",
        "approval": "approval.json",
        "directive": "directives/synthetic.txt",
        "report": "validation/synthetic.txt",
    }
    files = []
    for kind, name in names.items():
        path = active / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if kind != "index":
            path.write_text(f"Synthetic immutable {kind}\n", encoding="utf-8")
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": _digest(path),
                "kind": kind,
            }
        )
    canonical = (
        "docs/planning/review/example-task/"
        if state == "completed"
        else "docs/archive/completed/2026/example-task/"
    )
    index = root / canonical / "README.md"
    index.parent.mkdir(parents=True)
    index.write_text(f"# Synthetic closeout\n\nStatus: {state}\n", encoding="utf-8")
    manifest_path = root / canonical / "historical-authority.json"
    manifest_path.write_text(
        json.dumps(
            {
                "version": 1,
                "owner": "example-task",
                "packet": "docs/planning/active/example-task/",
                "files": files,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    board_path = planning / "board.yaml"
    board = yaml.safe_load(board_path.read_text(encoding="utf-8"))
    task = board["tasks"][0]
    task.update(
        {
            "work_state": state,
            "packet": canonical,
            "implementation_authority": "closed",
            "delivery_state": "local",
            "branch": "feature/example-task",
            "approved_by": "Maintainer",
            "approved_at": "2026-10-13",
            "validation": ["synthetic VERIFIED"],
            "authority_backing_packets": [
                {
                    "packet": "docs/planning/active/example-task/",
                    "manifest": manifest_path.relative_to(root).as_posix(),
                    "manifest_sha256": _digest(manifest_path),
                }
            ],
        }
    )
    if state == "accepted":
        task.update(accepted_by="Maintainer", accepted_at="2026-10-13")
    board_path.write_text(yaml.safe_dump(board, sort_keys=False), encoding="utf-8")
    rendered = _run(root, "render")
    assert rendered.returncode == 0, rendered.stdout + rendered.stderr
    return files


@pytest.mark.parametrize("state", ["completed", "accepted"])
def test_explicit_historical_backing_preserves_one_canonical_packet(
    tmp_path: Path, state: str
) -> None:
    files = _historical_fixture(tmp_path, state)
    result = _run(tmp_path, "validate")
    assert result.returncode == 0, result.stdout + result.stderr
    assert _run(tmp_path, "render").returncode == 0
    assert _run(tmp_path, "render", "--check").returncode == 0
    assert _run(tmp_path, "show", "example-task").returncode == 0
    backings = _load_task(tmp_path)["authority_backing_packets"]
    assert isinstance(backings, list) and len(backings) == 1
    for row in files:
        assert _digest(tmp_path / row["path"]) == row["sha256"]


def test_actual_closeout_and_maintainer_acceptance_keep_original_authority(
    tmp_path: Path,
) -> None:
    files = _historical_fixture(tmp_path)
    board_path = tmp_path / "docs/planning/board.yaml"
    board = yaml.safe_load(board_path.read_text(encoding="utf-8"))
    task = board["tasks"][0]
    task.update(
        work_state="started",
        packet="docs/planning/active/example-task/",
        implementation_authority="granted",
        validation=[],
    )
    # Existing CLI validates the final transaction; staging is not a valid board.
    board_path.write_text(yaml.safe_dump(board, sort_keys=False), encoding="utf-8")
    result = _run(
        tmp_path,
        "transition",
        "example-task",
        "completed",
        "--packet",
        "docs/planning/review/example-task/",
        "--actor",
        "Builder",
        "--actor-role",
        "agent",
        "--evidence",
        "synthetic fresh independent VERIFIED",
        "--note",
        "Propose completed local work",
        "--next-gate",
        "maintainer acceptance",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert _load_task(tmp_path)["work_state"] == "completed"
    assert _run(tmp_path, "next").stdout.startswith("AWAITING_ACCEPTANCE")
    review = tmp_path / "docs/planning/review/example-task"
    archive = tmp_path / "docs/archive/completed/2026/example-task"
    archive.parent.mkdir(parents=True)
    review.rename(archive)
    board = yaml.safe_load(board_path.read_text(encoding="utf-8"))
    board["tasks"][0]["authority_backing_packets"][0]["manifest"] = (
        "docs/archive/completed/2026/example-task/historical-authority.json"
    )
    board_path.write_text(yaml.safe_dump(board, sort_keys=False), encoding="utf-8")
    staged = board_path.read_bytes()
    arguments = (
        "transition",
        "example-task",
        "accepted",
        "--packet",
        "docs/archive/completed/2026/example-task/",
        "--actor",
        "Maintainer",
        "--note",
        "Accept synthetic work",
        "--next-gate",
        "none",
    )
    denied = _run(tmp_path, *arguments, "--actor-role", "agent")
    assert denied.returncode == 1 and "only a maintainer" in denied.stderr
    assert board_path.read_bytes() == staged
    accepted = _run(tmp_path, *arguments, "--actor-role", "maintainer")
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    assert _run(tmp_path, "validate").returncode == 0
    assert _load_task(tmp_path)["work_state"] == "accepted"
    assert _load_task(tmp_path)["delivery_state"] == "local"
    assert _run(tmp_path, "next").stdout.strip() == "NO_OPEN_TASK"
    for row in files:
        assert _digest(tmp_path / row["path"]) == row["sha256"]


@pytest.mark.parametrize(
    "invalid",
    [
        "missing_manifest",
        "stale_manifest",
        "missing_file",
        "stale_file",
        "owner",
        "packet",
        "missing_role",
        "wrong_index",
        "unknown_entry",
        "unknown_manifest",
        "unknown_file",
        "duplicate_json",
        "bad_digest",
        "bad_file_digest",
        "duplicate_file",
        "absolute",
        "traversal",
        "manifest_outside",
        "file_outside",
        "manifest_symlink",
        "file_symlink",
        "packet_alias",
        "duplicate_entry",
        "version_bool",
        "bad_files_type",
    ],
)
def test_invalid_historical_backing_is_never_an_orphan_exemption(
    tmp_path: Path, invalid: str
) -> None:
    _historical_fixture(tmp_path)
    board_path = tmp_path / "docs/planning/board.yaml"
    board = yaml.safe_load(board_path.read_text(encoding="utf-8"))
    entry = board["tasks"][0]["authority_backing_packets"][0]
    manifest_path = tmp_path / entry["manifest"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    altered = False
    if invalid == "missing_manifest":
        manifest_path.unlink()
    elif invalid == "stale_manifest":
        manifest_path.write_text("{}", encoding="utf-8")
    elif invalid == "missing_file":
        (tmp_path / manifest["files"][1]["path"]).unlink()
    elif invalid == "stale_file":
        (tmp_path / manifest["files"][1]["path"]).write_text(
            "changed", encoding="utf-8"
        )
    elif invalid in {"owner", "packet"}:
        manifest[invalid] = "wrong-owner-or-packet"
        altered = True
    elif invalid == "missing_role":
        manifest["files"][1]["kind"] = "evidence"
        altered = True
    elif invalid == "wrong_index":
        manifest["files"][0]["kind"] = "evidence"
        manifest["files"][1]["kind"] = "index"
        altered = True
    elif invalid == "unknown_entry":
        entry["unknown"] = True
    elif invalid == "unknown_manifest":
        manifest["unknown"] = True
        altered = True
    elif invalid == "unknown_file":
        manifest["files"][1]["unknown"] = True
        altered = True
    elif invalid == "duplicate_json":
        raw = manifest_path.read_text(encoding="utf-8").replace(
            '"version": 1,', '"version": 1, "version": 1,'
        )
        manifest_path.write_text(raw, encoding="utf-8")
        entry["manifest_sha256"] = _digest(manifest_path)
    elif invalid == "bad_digest":
        entry["manifest_sha256"] = "not-a-digest"
    elif invalid == "bad_file_digest":
        manifest["files"][1]["sha256"] = "not-a-digest"
        altered = True
    elif invalid == "duplicate_file":
        manifest["files"].append(manifest["files"][0])
        altered = True
    elif invalid in {"absolute", "traversal"}:
        entry["packet"] = (
            "/absolute/packet/"
            if invalid == "absolute"
            else "docs/planning/active/../packet/"
        )
    elif invalid == "manifest_outside":
        other = tmp_path / "other-manifest.json"
        other.write_bytes(manifest_path.read_bytes())
        entry["manifest"] = "other-manifest.json"
    elif invalid == "file_outside":
        other = tmp_path / "outside.txt"
        other.write_text("not owned", encoding="utf-8")
        manifest["files"][1].update(path="outside.txt", sha256=_digest(other))
        altered = True
    elif invalid == "manifest_symlink":
        other = tmp_path / "outside-manifest.json"
        other.write_bytes(manifest_path.read_bytes())
        manifest_path.unlink()
        manifest_path.symlink_to(other)
    elif invalid == "file_symlink":
        target = tmp_path / manifest["files"][1]["path"]
        other = tmp_path.parent / (tmp_path.name + "-outside.txt")
        other.write_bytes(target.read_bytes())
        target.unlink()
        target.symlink_to(other)
    elif invalid == "packet_alias":
        active = tmp_path / entry["packet"]
        other = tmp_path / "alias-target"
        active.rename(other)
        active.symlink_to(other, target_is_directory=True)
    elif invalid == "duplicate_entry":
        board["tasks"][0]["authority_backing_packets"].append(dict(entry))
    elif invalid == "version_bool":
        manifest["version"] = True
        altered = True
    elif invalid == "bad_files_type":
        manifest["files"] = {"index": "not a list"}
        altered = True
    if altered:
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        entry["manifest_sha256"] = _digest(manifest_path)
    board_path.write_text(yaml.safe_dump(board, sort_keys=False), encoding="utf-8")
    before = board_path.read_bytes()
    result = _run(tmp_path, "validate")
    assert result.returncode == 1, result.stdout + result.stderr
    assert (
        "authority_backing_packets" in result.stderr
        or "duplicate JSON" in result.stderr
    )
    assert "current planning packet is absent from board" in result.stderr
    assert board_path.read_bytes() == before


@pytest.mark.parametrize("state", ["queued", "approved", "started"])
def test_open_work_cannot_hide_a_packet_as_historical_backing(
    tmp_path: Path, state: str
) -> None:
    _historical_fixture(tmp_path)
    path = tmp_path / "docs/planning/board.yaml"
    board = yaml.safe_load(path.read_text(encoding="utf-8"))
    board["tasks"][0]["work_state"] = state
    path.write_text(yaml.safe_dump(board, sort_keys=False), encoding="utf-8")
    result = _run(tmp_path, "validate")
    assert result.returncode == 1
    assert "requires a completed/review or accepted/archive owner" in result.stderr


def test_historical_declaration_does_not_hide_an_unlisted_packet(
    tmp_path: Path,
) -> None:
    _historical_fixture(tmp_path)
    other = tmp_path / "docs/planning/active/undeclared-task"
    other.mkdir()
    (other / "README.md").write_text("# Undeclared\n", encoding="utf-8")
    result = _run(tmp_path, "validate")
    assert result.returncode == 1
    assert "active/undeclared-task/" in result.stderr
    assert "absent from board: docs/planning/active/example-task/" not in result.stderr


def test_two_tasks_cannot_claim_the_same_historical_authority(tmp_path: Path) -> None:
    _historical_fixture(tmp_path)
    path = tmp_path / "docs/planning/board.yaml"
    board = yaml.safe_load(path.read_text(encoding="utf-8"))
    second = dict(board["tasks"][0])
    second.update(
        id="second-task", priority=2, packet="docs/planning/review/second-task/"
    )
    other = tmp_path / second["packet"]
    other.mkdir()
    (other / "README.md").write_text("# Second\n", encoding="utf-8")
    board["tasks"].append(second)
    path.write_text(yaml.safe_dump(board, sort_keys=False), encoding="utf-8")
    result = _run(tmp_path, "validate")
    assert result.returncode == 1
    assert "duplicates a backing packet or owner claim" in result.stderr


def test_a_current_packet_cannot_be_claimed_as_someones_history(tmp_path: Path) -> None:
    _historical_fixture(tmp_path)
    path = tmp_path / "docs/planning/board.yaml"
    board = yaml.safe_load(path.read_text(encoding="utf-8"))
    other = dict(board["tasks"][0])
    other.pop("authority_backing_packets")
    other.update(
        id="active-owner",
        priority=2,
        work_state="started",
        packet="docs/planning/active/example-task/",
        implementation_authority="granted",
    )
    board["tasks"].append(other)
    path.write_text(yaml.safe_dump(board, sort_keys=False), encoding="utf-8")
    result = _run(tmp_path, "validate")
    assert result.returncode == 1
    assert "conflicts with a current canonical packet" in result.stderr


def test_backing_cannot_be_its_owners_canonical_index(tmp_path: Path) -> None:
    _historical_fixture(tmp_path)
    path = tmp_path / "docs/planning/board.yaml"
    board = yaml.safe_load(path.read_text(encoding="utf-8"))
    board["tasks"][0]["authority_backing_packets"][0]["packet"] = board["tasks"][0][
        "packet"
    ]
    path.write_text(yaml.safe_dump(board, sort_keys=False), encoding="utf-8")
    result = _run(tmp_path, "validate")
    assert result.returncode == 1
    assert "conflicts with a current canonical packet" in result.stderr


@pytest.mark.parametrize(
    "invalid", ["empty", "wrong_type", "too_many", "unknown_field"]
)
def test_backing_entry_container_contract_is_strict(
    tmp_path: Path, invalid: str
) -> None:
    _historical_fixture(tmp_path)
    path = tmp_path / "docs/planning/board.yaml"
    board = yaml.safe_load(path.read_text(encoding="utf-8"))
    task = board["tasks"][0]
    if invalid == "empty":
        task["authority_backing_packets"] = []
    elif invalid == "wrong_type":
        task["authority_backing_packets"] = {"packet": "not a list"}
    elif invalid == "too_many":
        task["authority_backing_packets"] = [task["authority_backing_packets"][0]] * 65
    else:
        task["authority_backing_packets"][0]["unknown_field"] = True
    path.write_text(yaml.safe_dump(board, sort_keys=False), encoding="utf-8")
    result = _run(tmp_path, "validate")
    assert result.returncode == 1
    assert "authority_backing_packets" in result.stderr
    assert "current planning packet is absent from board" in result.stderr


@pytest.mark.parametrize("invalid", ["oversized", "unknown_kind", "malformed_json"])
def test_manifest_format_bounds_are_enforced_before_recognition(
    tmp_path: Path, invalid: str
) -> None:
    _historical_fixture(tmp_path)
    board_path = tmp_path / "docs/planning/board.yaml"
    board = yaml.safe_load(board_path.read_text(encoding="utf-8"))
    entry = board["tasks"][0]["authority_backing_packets"][0]
    manifest_path = tmp_path / entry["manifest"]
    if invalid == "oversized":
        manifest_path.write_bytes(b" " * (1024 * 1024 + 1))
    elif invalid == "malformed_json":
        manifest_path.write_text("{not JSON", encoding="utf-8")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"][1]["kind"] = "unknown"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    entry["manifest_sha256"] = _digest(manifest_path)
    board_path.write_text(yaml.safe_dump(board, sort_keys=False), encoding="utf-8")
    result = _run(tmp_path, "validate")
    assert result.returncode == 1
    assert "authority_backing_packets" in result.stderr
    assert "current planning packet is absent from board" in result.stderr


def test_declared_schema_preserves_strict_optional_backing_contract(
    tmp_path: Path,
) -> None:
    from jsonschema import Draft202012Validator, ValidationError

    _historical_fixture(tmp_path)
    schema = json.loads((tmp_path / "docs/planning/board.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    board = yaml.safe_load((tmp_path / "docs/planning/board.yaml").read_text())
    validator.validate(board)
    board["tasks"][0]["work_state"] = "started"
    with pytest.raises(ValidationError):
        validator.validate(board)
    board["tasks"][0]["work_state"] = "completed"
    board["tasks"][0]["authority_backing_packets"][0]["unknown"] = True
    with pytest.raises(ValidationError):
        validator.validate(board)
