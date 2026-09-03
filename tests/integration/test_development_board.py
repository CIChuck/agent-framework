from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import cast

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
    assert "22 tasks" in result.stdout

    agent_instructions = (REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "canonical operational entry point" in agent_instructions
    assert "scripts/friday-dev-board.py validate" in agent_instructions
    assert "queued -> approved -> started -> completed -> accepted" in agent_instructions
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

    archive = (
        tmp_path
        / "docs"
        / "archive"
        / "completed"
        / "2026"
        / "example-task"
    )
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
