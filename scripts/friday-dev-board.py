#!/usr/bin/env python3
"""Validate, render, and safely update the Friday development board."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import re
import sys
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, cast

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORK_STATES = ("queued", "approved", "started", "completed", "accepted")
CONDITIONS = ("normal", "blocked", "deferred", "backlog")
DELIVERY_STATES = (
    "not_started",
    "local",
    "pushed",
    "merged",
    "released",
    "unknown",
)
AUTHORITIES = ("not_granted", "design_only", "granted", "closed")
ACTOR_ROLES = ("maintainer", "agent")
CURRENT_LANES = ("active", "queued", "review", "blocked", "deferred", "backlog")
ALLOWED_TRANSITIONS = {
    "queued": {"approved"},
    "approved": {"queued", "started"},
    "started": {"completed"},
    "completed": {"started", "accepted"},
    "accepted": set(),
}
DELIVERY_ORDER = {
    "not_started": 0,
    "local": 1,
    "pushed": 2,
    "merged": 3,
    "released": 4,
}
TASK_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_TASK_FIELDS = {
    "id",
    "title",
    "priority",
    "work_state",
    "condition",
    "implementation_authority",
    "packet",
    "next_gate",
    "delivery_state",
    "branch",
    "depends_on",
    "validation",
}
OPTIONAL_TASK_FIELDS = {
    "legacy_import",
    "approved_by",
    "approved_at",
    "accepted_by",
    "accepted_at",
    "authority_backing_packets",
}
REQUIRED_EVENT_FIELDS = {"task", "at", "actor", "actor_role", "action", "note"}
OPTIONAL_EVENT_FIELDS = {"evidence"}


class BoardError(ValueError):
    """Raised when the development board violates its contract."""


def _board_path(root: Path) -> Path:
    return root / "docs" / "planning" / "board.yaml"


def _dashboard_path(root: Path) -> Path:
    return root / "docs" / "planning" / "README.md"


def _today() -> str:
    return dt.date.today().isoformat()


def _now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def load_board(root: Path) -> dict[str, Any]:
    path = _board_path(root)
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BoardError(f"missing board: {path}") from exc
    except yaml.YAMLError as exc:
        raise BoardError(f"invalid board YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise BoardError("board root must be a mapping")
    return cast(dict[str, Any], raw)


def _required_string(task: dict[str, Any], field: str, label: str) -> str:
    value = task.get(field)
    if not isinstance(value, str) or not value.strip():
        raise BoardError(f"{label}.{field} must be a non-empty string")
    return value


def _expected_packet_prefix(task: dict[str, Any]) -> str:
    state = task["work_state"]
    condition = task["condition"]
    if state == "accepted":
        return "docs/archive/completed/"
    if condition == "blocked":
        return "docs/planning/blocked/"
    if condition == "deferred":
        return "docs/planning/deferred/"
    if condition == "backlog":
        return "docs/planning/backlog/"
    if state == "started":
        return "docs/planning/active/"
    if state == "completed":
        return "docs/planning/review/"
    return "docs/planning/queued/"


def _is_iso_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _is_iso_date_or_datetime(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        dt.datetime.fromisoformat(value)
    except ValueError:
        return _is_iso_date(value)
    return True


def _validate_declared_schema(root: Path) -> list[str]:
    path = root / "docs" / "planning" / "board.schema.json"
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ["missing board schema: docs/planning/board.schema.json"]
    except json.JSONDecodeError as exc:
        return [f"invalid board schema JSON: {exc}"]
    try:
        task = schema["$defs"]["task"]
        event = schema["$defs"]["event"]
        checks = {
            "work states": (
                set(task["properties"]["work_state"]["enum"]),
                set(WORK_STATES),
            ),
            "conditions": (
                set(task["properties"]["condition"]["enum"]),
                set(CONDITIONS),
            ),
            "delivery states": (
                set(task["properties"]["delivery_state"]["enum"]),
                set(DELIVERY_STATES),
            ),
            "authorities": (
                set(task["properties"]["implementation_authority"]["enum"]),
                set(AUTHORITIES),
            ),
            "task fields": (
                set(task["properties"]),
                REQUIRED_TASK_FIELDS | OPTIONAL_TASK_FIELDS,
            ),
            "event fields": (
                set(event["properties"]),
                REQUIRED_EVENT_FIELDS | OPTIONAL_EVENT_FIELDS,
            ),
        }
    except (KeyError, TypeError) as exc:
        return [f"board schema is missing its declared contract: {exc}"]
    return [
        f"board schema {label} disagree with the validator"
        for label, (declared, implemented) in checks.items()
        if declared != implemented
    ]


def _current_packet_paths(root: Path) -> set[str]:
    paths: set[str] = set()
    planning = root / "docs" / "planning"
    for lane in CURRENT_LANES:
        lane_path = planning / lane
        if not lane_path.exists():
            raise BoardError(f"missing planning lane: docs/planning/{lane}")
        for packet in lane_path.iterdir():
            if packet.is_dir() and (packet / "README.md").exists():
                paths.add(f"{packet.relative_to(root).as_posix()}/")
    return paths


@dataclass(frozen=True)
class AuthorityBacking:
    """An explicit immutable packet owned by one closed task."""

    packet: str
    manifest: str
    manifest_sha256: str


def _backing_record(value: object, fields: set[str], label: str) -> dict[str, object]:
    # YAML/JSON is the dynamic boundary; all subsequent values are validated.
    if not isinstance(value, dict) or set(value) != fields:
        raise BoardError(f"{label} must contain exactly the declared fields")
    return {name: value[name] for name in fields}


def _backing_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 1024:
        raise BoardError(f"{label} must be a bounded non-empty string")
    return value


def _backing_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise BoardError(f"{label} must be a lowercase SHA256 digest")
    return value


def _backing_relative_path(value: object, label: str, *, directory: bool) -> str:
    text = _backing_string(value, label)
    path = text[:-1] if directory and text.endswith("/") else text
    parts = path.split("/")
    if (
        (directory and not text.endswith("/"))
        or PurePosixPath(path).is_absolute()
        or any(part in {"", ".", ".."} for part in parts)
        or "\\" in text
        or any(ord(character) < 32 for character in text)
    ):
        raise BoardError(f"{label} must be a canonical repository-relative path")
    return text


def _backing_file(root: Path, relative: str, boundary: Path, label: str) -> Path:
    path = root / relative
    try:
        resolved = path.resolve()
        if (
            not path.is_relative_to(boundary)
            or not resolved.is_relative_to(boundary)
            or not resolved.is_file()
        ):
            raise BoardError(f"{label} is missing or escapes its owning packet")
    except (OSError, RuntimeError):
        raise BoardError(
            f"{label} cannot be resolved inside its owning packet"
        ) from None
    return resolved


def _unique_json_record(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise BoardError("authority backing manifest has duplicate JSON fields")
        result[key] = value
    return result


def _validate_backing_manifest(
    entry: AuthorityBacking, owner: str, canonical: str, root: Path, label: str
) -> None:
    base = root.resolve()
    packet = base / entry.packet
    canonical_path = base / canonical
    try:
        if packet.resolve() != packet or not packet.is_dir():
            raise BoardError(f"{label}.packet is missing or aliases another directory")
        if canonical_path.resolve() != canonical_path or not canonical_path.is_dir():
            raise BoardError(f"{label} has no canonical owning packet")
        manifest_path = _backing_file(
            base, entry.manifest, canonical_path, f"{label}.manifest"
        )
        # Bound JSON allocation before parsing; no external schema lookup.
        with manifest_path.open("rb") as stream:
            raw = stream.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise BoardError(f"{label}.manifest exceeds 1 MiB")
        if hashlib.sha256(raw).hexdigest() != entry.manifest_sha256:
            raise BoardError(f"{label}.manifest SHA256 mismatch")
        decoded: object = json.loads(raw, object_pairs_hook=_unique_json_record)
        manifest = _backing_record(
            decoded, {"version", "owner", "packet", "files"}, f"{label}.manifest"
        )
        if type(manifest["version"]) is not int or manifest["version"] != 1:
            raise BoardError(f"{label}.manifest version must equal 1")
        if manifest["owner"] != owner or manifest["packet"] != entry.packet:
            raise BoardError(f"{label}.manifest owner or packet mismatch")
        files = manifest["files"]
        if not isinstance(files, list) or not 5 <= len(files) <= 8192:
            raise BoardError(f"{label}.manifest files must contain 5..8192 records")
        kinds: set[str] = set()
        paths: set[str] = set()
        for index, value in enumerate(files):
            file_label = f"{label}.manifest.files[{index}]"
            record = _backing_record(value, {"path", "sha256", "kind"}, file_label)
            relative = _backing_relative_path(
                record["path"], file_label + ".path", directory=False
            )
            digest = _backing_digest(record["sha256"], file_label + ".sha256")
            kind = _backing_string(record["kind"], file_label + ".kind")
            if kind not in {
                "index",
                "authority",
                "approval",
                "directive",
                "report",
                "evidence",
            }:
                raise BoardError(f"{file_label}.kind is invalid")
            if relative in paths:
                raise BoardError(f"{file_label} duplicates an immutable file")
            paths.add(relative)
            if kind == "index" and relative != entry.packet + "README.md":
                raise BoardError(f"{file_label} must pin the original packet README")
            source = _backing_file(base, relative, packet, file_label)
            with source.open("rb") as stream:
                actual = hashlib.file_digest(stream, "sha256").hexdigest()
            if actual != digest:
                raise BoardError(f"{file_label} immutable file SHA256 mismatch")
            kinds.add(kind)
        if not {"index", "authority", "approval", "directive", "report"} <= kinds:
            raise BoardError(f"{label}.manifest lacks required historical record kinds")
    except BoardError:
        raise
    except (OSError, UnicodeError, ValueError, RuntimeError):
        raise BoardError(f"{label}.manifest cannot be read as bounded JSON") from None


def _authority_backings(
    tasks: Iterable[object], root: Path, canonical_packets: set[str], errors: list[str]
) -> set[str]:
    records: list[tuple[AuthorityBacking, str, str, str]] = []
    claims: dict[str, int] = {}
    for index, task in enumerate(tasks):
        if not isinstance(task, dict) or "authority_backing_packets" not in task:
            continue
        label = f"tasks[{index}].authority_backing_packets"
        try:
            owner = _backing_string(task.get("id"), label + ".owner")
            canonical = _backing_relative_path(
                task.get("packet"), label + ".canonical", directory=True
            )
            state = task.get("work_state")
            expected = (
                "docs/planning/review/"
                if state == "completed"
                else "docs/archive/completed/"
            )
            if (
                not isinstance(state, str)
                or state not in {"completed", "accepted"}
                or task.get("condition") != "normal"
                or not canonical.startswith(expected)
            ):
                raise BoardError(
                    f"{label} requires a completed/review or accepted/archive owner"
                )
            entries = task["authority_backing_packets"]
            if not isinstance(entries, list) or not 1 <= len(entries) <= 64:
                raise BoardError(f"{label} must contain 1..64 entries")
            for number, value in enumerate(entries):
                item_label = f"{label}[{number}]"
                record = _backing_record(
                    value, {"packet", "manifest", "manifest_sha256"}, item_label
                )
                packet = _backing_relative_path(
                    record["packet"], item_label + ".packet", directory=True
                )
                parts = PurePosixPath(packet).parts
                if (
                    len(parts) != 4
                    or parts[:2] != ("docs", "planning")
                    or parts[2] not in CURRENT_LANES
                ):
                    raise BoardError(
                        f"{item_label}.packet must identify one planning packet"
                    )
                entry = AuthorityBacking(
                    packet,
                    _backing_relative_path(
                        record["manifest"], item_label + ".manifest", directory=False
                    ),
                    _backing_digest(
                        record["manifest_sha256"], item_label + ".manifest_sha256"
                    ),
                )
                records.append((entry, owner, canonical, item_label))
                claims[packet] = claims.get(packet, 0) + 1
        except BoardError as exc:
            errors.append(str(exc))
    validated: set[str] = set()
    for entry, owner, canonical, label in records:
        try:
            if claims[entry.packet] != 1:
                raise BoardError(f"{label} duplicates a backing packet or owner claim")
            if entry.packet in canonical_packets:
                raise BoardError(f"{label} conflicts with a current canonical packet")
            _validate_backing_manifest(entry, owner, canonical, root, label)
            validated.add(entry.packet)
        except BoardError as exc:
            errors.append(str(exc))
    return validated


def validate_board(board: dict[str, Any], root: Path) -> list[str]:
    errors = _validate_declared_schema(root)
    root_fields = {"version", "updated", "tasks", "events"}
    unexpected_root_fields = board.keys() - root_fields
    if unexpected_root_fields:
        errors.append(
            "unexpected board fields: " + ", ".join(sorted(unexpected_root_fields))
        )
    if board.get("version") != 1:
        errors.append("version must equal 1")
    if not _is_iso_date(board.get("updated")):
        errors.append("updated must be an ISO date string")
    tasks = board.get("tasks")
    events = board.get("events")
    if not isinstance(tasks, list):
        return [*errors, "tasks must be a list"]
    if not isinstance(events, list):
        errors.append("events must be a list")

    ids: set[str] = set()
    priorities: set[int] = set()
    board_packets: set[str] = set()
    for index, raw_task in enumerate(tasks):
        label = f"tasks[{index}]"
        if not isinstance(raw_task, dict):
            errors.append(f"{label} must be a mapping")
            continue
        task = raw_task
        missing = REQUIRED_TASK_FIELDS - task.keys()
        unexpected = task.keys() - REQUIRED_TASK_FIELDS - OPTIONAL_TASK_FIELDS
        if missing:
            errors.append(f"{label} missing fields: {', '.join(sorted(missing))}")
            continue
        if unexpected:
            errors.append(
                f"{label} has unexpected fields: {', '.join(sorted(unexpected))}"
            )
        try:
            task_id = _required_string(task, "id", label)
            _required_string(task, "title", label)
            packet = _required_string(task, "packet", label)
            _required_string(task, "next_gate", label)
        except BoardError as exc:
            errors.append(str(exc))
            continue
        if not TASK_ID_PATTERN.fullmatch(task_id):
            errors.append(f"{label}.id is not a lowercase kebab-case identifier")
        if task_id in ids:
            errors.append(f"duplicate task id: {task_id}")
        ids.add(task_id)

        priority = task.get("priority")
        if not isinstance(priority, int) or isinstance(priority, bool) or priority < 1:
            errors.append(f"{label}.priority must be a positive integer")
        elif priority in priorities:
            errors.append(f"duplicate priority: {priority}")
        else:
            priorities.add(priority)

        state = task.get("work_state")
        condition = task.get("condition")
        delivery = task.get("delivery_state")
        authority = task.get("implementation_authority")
        if state not in WORK_STATES:
            errors.append(f"{label}.work_state is invalid: {state!r}")
        if condition not in CONDITIONS:
            errors.append(f"{label}.condition is invalid: {condition!r}")
        if delivery not in DELIVERY_STATES:
            errors.append(f"{label}.delivery_state is invalid: {delivery!r}")
        if authority not in AUTHORITIES:
            errors.append(f"{label}.implementation_authority is invalid: {authority!r}")
        if (
            not packet.endswith("/")
            or packet.startswith("/")
            or ".." in Path(packet).parts
        ):
            errors.append(f"{label}.packet must be a repository-relative directory")
        elif state in WORK_STATES and condition in CONDITIONS:
            expected = _expected_packet_prefix(task)
            if not packet.startswith(expected):
                errors.append(
                    f"{label}.packet must be under {expected} for "
                    f"state={state}, condition={condition}"
                )
        if packet in board_packets:
            errors.append(f"duplicate packet path: {packet}")
        board_packets.add(packet)
        packet_path = root / packet
        if not packet_path.is_dir():
            errors.append(f"{label}.packet does not exist: {packet}")
        elif not (packet_path / "README.md").is_file():
            errors.append(f"{label}.packet has no README.md: {packet}")

        branch = task.get("branch")
        if branch is not None and not isinstance(branch, str):
            errors.append(f"{label}.branch must be a string or null")
        if state == "started" and not branch:
            errors.append(f"{label}.branch is required for started work")
        for field in ("depends_on", "validation"):
            value = task.get(field)
            if not isinstance(value, list) or not all(
                isinstance(item, str) and item for item in value
            ):
                errors.append(f"{label}.{field} must be a list of strings")
        if "legacy_import" in task and not isinstance(task["legacy_import"], bool):
            errors.append(f"{label}.legacy_import must be a boolean")
        for field in ("approved_by", "accepted_by"):
            if field in task and (
                not isinstance(task[field], str) or not task[field].strip()
            ):
                errors.append(f"{label}.{field} must be a non-empty string")
        for field in ("approved_at", "accepted_at"):
            if field in task and not _is_iso_date(task[field]):
                errors.append(f"{label}.{field} must be an ISO date string")

        legacy = task.get("legacy_import") is True
        if (
            not legacy
            and state in {"approved", "started", "completed", "accepted"}
            and (not task.get("approved_by") or not task.get("approved_at"))
        ):
            errors.append(f"{label} lacks explicit approval evidence")
        if state == "completed" and not task.get("validation"):
            errors.append(f"{label}.validation is required for completed work")
        if state == "accepted":
            if condition != "normal":
                errors.append(f"{label}: accepted work must have normal condition")
            if not task.get("accepted_by") or not task.get("accepted_at"):
                errors.append(f"{label} lacks explicit acceptance evidence")

    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            continue
        for dependency in task.get("depends_on", []):
            if dependency not in ids:
                errors.append(f"tasks[{index}] depends on unknown task: {dependency}")
            elif dependency == task.get("id"):
                errors.append(f"tasks[{index}] cannot depend on itself")
            elif task.get("work_state") in {"started", "completed", "accepted"}:
                dependency_task = next(
                    candidate
                    for candidate in tasks
                    if candidate.get("id") == dependency
                )
                if dependency_task.get("work_state") != "accepted":
                    errors.append(
                        f"tasks[{index}] has an unaccepted dependency: {dependency}"
                    )

    current_packets = _current_packet_paths(root)
    current_board_packets = {
        task["packet"]
        for task in tasks
        if isinstance(task, dict)
        and isinstance(task.get("packet"), str)
        and task["packet"].startswith("docs/planning/")
    }
    authority_backings = _authority_backings(tasks, root, board_packets, errors)
    for path in sorted(current_packets - current_board_packets - authority_backings):
        errors.append(f"current planning packet is absent from board: {path}")
    for path in sorted(current_board_packets - current_packets):
        errors.append(f"board references a non-current planning packet: {path}")

    if isinstance(events, list):
        for index, event in enumerate(events):
            label = f"events[{index}]"
            if not isinstance(event, dict):
                errors.append(f"{label} must be a mapping")
                continue
            missing = REQUIRED_EVENT_FIELDS - event.keys()
            unexpected = event.keys() - REQUIRED_EVENT_FIELDS - OPTIONAL_EVENT_FIELDS
            if missing:
                errors.append(f"{label} missing fields: {', '.join(sorted(missing))}")
            if unexpected:
                errors.append(
                    f"{label} has unexpected fields: {', '.join(sorted(unexpected))}"
                )
            for field in REQUIRED_EVENT_FIELDS:
                if not isinstance(event.get(field), str) or not event[field].strip():
                    errors.append(f"{label}.{field} must be a non-empty string")
            if not _is_iso_date_or_datetime(event.get("at")):
                errors.append(f"{label}.at must be an ISO date or datetime string")
            if "evidence" in event and (
                not isinstance(event["evidence"], str) or not event["evidence"].strip()
            ):
                errors.append(f"{label}.evidence must be a non-empty string")
            if event.get("task") not in ids:
                errors.append(f"{label} references unknown task: {event.get('task')}")
            if event.get("actor_role") not in ACTOR_ROLES:
                errors.append(f"{label}.actor_role is invalid")

    return errors


def _relative_dashboard_link(packet: str) -> str:
    path = packet.rstrip("/")
    planning_prefix = "docs/planning/"
    if path.startswith(planning_prefix):
        return path.removeprefix(planning_prefix) + "/"
    docs_prefix = "docs/"
    if path.startswith(docs_prefix):
        return "../" + path.removeprefix(docs_prefix) + "/"
    return path


def _escape_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_dashboard(board: dict[str, Any]) -> str:
    tasks = sorted(board["tasks"], key=lambda task: task["priority"])
    lines = [
        "# Planning Dashboard",
        "",
        "This dashboard is generated from [`board.yaml`](board.yaml), the canonical",
        "current-state registry. Do not edit task state in this file directly.",
        "",
        "The governing workflow is the",
        "[development task lifecycle policy](../reference/policies/development-task-lifecycle.md).",
        "Directory placement does not grant implementation authority.",
        "",
    ]
    for state in WORK_STATES:
        state_tasks = [task for task in tasks if task["work_state"] == state]
        lines.extend(
            [
                f"## {state.title()}",
                "",
                "| Priority | Initiative | Condition | Authority | Delivery | Next gate |",
                "| ---: | --- | --- | --- | --- | --- |",
            ]
        )
        if not state_tasks:
            lines.append("| — | _None_ | — | — | — | — |")
        for task in state_tasks:
            link = _relative_dashboard_link(task["packet"])
            title = f"[{_escape_cell(task['title'])}]({link})"
            cells = (
                task["priority"],
                title,
                task["condition"],
                task["implementation_authority"],
                task["delivery_state"],
                _escape_cell(task["next_gate"]),
            )
            lines.append("| " + " | ".join(str(cell) for cell in cells) + " |")
        lines.append("")
    lines.extend(
        [
            "## Operating Rules",
            "",
            "- Work progresses through `queued -> approved -> started -> completed -> accepted`.",
            "- `blocked`, `deferred`, and `backlog` are conditions, not authorization.",
            "- Only the maintainer may approve or accept work.",
            "- Delivery state is tracked independently from work state.",
            "- Each current initiative has one packet `README.md` containing its detailed gate.",
            "- Completed and superseded history remains in [the archive](../archive/).",
            "",
            "## Board Commands",
            "",
            "Run `uv run python scripts/friday-dev-board.py <command>`.",
            "Use `next`, `list`, `show`, and `validate` for read-only review. Mutation commands",
            "record state, condition, or delivery transitions and regenerate this dashboard.",
            "",
        ]
    )
    return "\n".join(lines)


def _dump_board(board: dict[str, Any]) -> str:
    return yaml.safe_dump(board, sort_keys=False, allow_unicode=True, width=1000)


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    temporary.replace(path)


def _validate_or_raise(board: dict[str, Any], root: Path) -> None:
    errors = validate_board(board, root)
    if errors:
        raise BoardError("\n".join(f"- {error}" for error in errors))


def _save_board_and_dashboard(board: dict[str, Any], root: Path) -> None:
    _validate_or_raise(board, root)
    board["updated"] = _today()
    _atomic_write(_board_path(root), _dump_board(board))
    _atomic_write(_dashboard_path(root), render_dashboard(board))


def _find_task(board: dict[str, Any], task_id: str) -> dict[str, Any]:
    for task in board["tasks"]:
        if task["id"] == task_id:
            return cast(dict[str, Any], task)
    raise BoardError(f"unknown task: {task_id}")


def _append_event(
    board: dict[str, Any],
    *,
    task_id: str,
    actor: str,
    actor_role: str,
    action: str,
    note: str,
    evidence: str | None,
) -> None:
    event = {
        "task": task_id,
        "at": _now(),
        "actor": actor,
        "actor_role": actor_role,
        "action": action,
        "note": note,
    }
    if evidence:
        event["evidence"] = evidence
    board["events"].append(event)


def _command_validate(board: dict[str, Any], root: Path) -> None:
    _validate_or_raise(board, root)
    expected = render_dashboard(board)
    dashboard = _dashboard_path(root)
    if not dashboard.exists() or dashboard.read_text(encoding="utf-8") != expected:
        raise BoardError("planning dashboard is stale; run the render command")
    print(f"Development board validation passed: {len(board['tasks'])} tasks")


def _command_render(board: dict[str, Any], root: Path, check: bool) -> None:
    _validate_or_raise(board, root)
    expected = render_dashboard(board)
    dashboard = _dashboard_path(root)
    if check:
        if not dashboard.exists() or dashboard.read_text(encoding="utf-8") != expected:
            raise BoardError("planning dashboard is stale")
        print("Planning dashboard is current")
        return
    _atomic_write(dashboard, expected)
    print(f"Rendered {dashboard.relative_to(root)}")


def _command_list(board: dict[str, Any]) -> None:
    print("PRI  STATE      CONDITION  DELIVERY     INITIATIVE")
    for task in sorted(board["tasks"], key=lambda item: item["priority"]):
        print(
            f"{task['priority']:>3}  {task['work_state']:<10} "
            f"{task['condition']:<10} {task['delivery_state']:<12} {task['id']}"
        )


def _command_show(board: dict[str, Any], task_id: str) -> None:
    task = _find_task(board, task_id)
    print(yaml.safe_dump(task, sort_keys=False, allow_unicode=True).rstrip())


def _dependencies_accepted(board: dict[str, Any], task: dict[str, Any]) -> bool:
    states = {item["id"]: item["work_state"] for item in board["tasks"]}
    return all(states[dependency] == "accepted" for dependency in task["depends_on"])


def _command_next(board: dict[str, Any]) -> None:
    tasks = sorted(
        (task for task in board["tasks"] if task["work_state"] != "accepted"),
        key=lambda item: item["priority"],
    )
    if not tasks:
        print("NO_OPEN_TASK")
        return
    task = tasks[0]
    if task["condition"] != "normal":
        label = task["condition"].upper()
    elif not _dependencies_accepted(board, task):
        label = "WAITING_DEPENDENCY"
    else:
        labels = {
            "queued": "AWAITING_APPROVAL",
            "approved": "READY",
            "started": "IN_PROGRESS",
            "completed": "AWAITING_ACCEPTANCE",
        }
        label = labels[task["work_state"]]
    print(f"{label} {task['id']}: {task['next_gate']}")


def _command_transition(
    board: dict[str, Any], root: Path, args: argparse.Namespace
) -> None:
    updated = copy.deepcopy(board)
    task = _find_task(updated, args.task_id)
    old_state = task["work_state"]
    new_state = args.state
    if new_state not in ALLOWED_TRANSITIONS[old_state]:
        raise BoardError(f"transition not allowed: {old_state} -> {new_state}")
    if new_state in {"approved", "accepted"} and args.actor_role != "maintainer":
        raise BoardError(f"only a maintainer may transition work to {new_state}")
    if args.packet:
        task["packet"] = args.packet.rstrip("/") + "/"
    task["next_gate"] = args.next_gate
    if new_state == "queued":
        task["implementation_authority"] = "not_granted"
        task["branch"] = None
    if new_state == "approved":
        task["approved_by"] = args.actor
        task["approved_at"] = _today()
        task["implementation_authority"] = "granted"
        task.pop("legacy_import", None)
    if new_state == "started":
        if task.get("legacy_import") is True:
            raise BoardError(
                "legacy approval must return to queued and receive current approval"
            )
        if args.branch:
            task["branch"] = args.branch
        if not task.get("branch"):
            raise BoardError("started work requires --branch or an existing branch")
        if task["delivery_state"] == "not_started":
            task["delivery_state"] = "local"
        task["implementation_authority"] = "granted"
    if new_state == "completed":
        if not args.evidence:
            raise BoardError("completed work requires at least one --evidence value")
        task["validation"] = [*task.get("validation", []), *args.evidence]
        task["implementation_authority"] = "closed"
    if new_state == "accepted":
        task["accepted_by"] = args.actor
        task["accepted_at"] = _today()
        task["implementation_authority"] = "closed"
        task["condition"] = "normal"
    task["work_state"] = new_state
    _append_event(
        updated,
        task_id=args.task_id,
        actor=args.actor,
        actor_role=args.actor_role,
        action=f"transitioned {old_state} -> {new_state}",
        note=args.note,
        evidence="; ".join(args.evidence) if args.evidence else None,
    )
    _save_board_and_dashboard(updated, root)
    print(f"Transitioned {args.task_id}: {old_state} -> {new_state}")


def _command_condition(
    board: dict[str, Any], root: Path, args: argparse.Namespace
) -> None:
    updated = copy.deepcopy(board)
    task = _find_task(updated, args.task_id)
    old_condition = task["condition"]
    if args.packet:
        task["packet"] = args.packet.rstrip("/") + "/"
    task["condition"] = args.condition
    task["next_gate"] = args.next_gate
    _append_event(
        updated,
        task_id=args.task_id,
        actor=args.actor,
        actor_role=args.actor_role,
        action=f"condition {old_condition} -> {args.condition}",
        note=args.note,
        evidence=args.evidence,
    )
    _save_board_and_dashboard(updated, root)
    print(f"Updated {args.task_id} condition: {old_condition} -> {args.condition}")


def _command_delivery(
    board: dict[str, Any], root: Path, args: argparse.Namespace
) -> None:
    updated = copy.deepcopy(board)
    task = _find_task(updated, args.task_id)
    old_delivery = task["delivery_state"]
    new_delivery = args.delivery_state
    if old_delivery == "unknown":
        if args.actor_role != "maintainer":
            raise BoardError("only a maintainer may resolve an unknown delivery state")
    elif new_delivery == "unknown":
        raise BoardError("delivery state cannot transition to unknown")
    elif DELIVERY_ORDER[new_delivery] < DELIVERY_ORDER[old_delivery]:
        raise BoardError(
            f"delivery cannot move backward: {old_delivery} -> {new_delivery}"
        )
    if new_delivery in {"merged", "released"} and not args.evidence:
        raise BoardError(f"{new_delivery} delivery requires --evidence")
    task["delivery_state"] = new_delivery
    _append_event(
        updated,
        task_id=args.task_id,
        actor=args.actor,
        actor_role=args.actor_role,
        action=f"delivery {old_delivery} -> {new_delivery}",
        note=args.note,
        evidence=args.evidence,
    )
    _save_board_and_dashboard(updated, root)
    print(f"Updated {args.task_id} delivery: {old_delivery} -> {new_delivery}")


def _add_actor_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--actor", required=True)
    parser.add_argument("--actor-role", required=True, choices=ACTOR_ROLES)
    parser.add_argument("--note", required=True)
    parser.add_argument("--evidence")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    render = commands.add_parser("render")
    render.add_argument("--check", action="store_true")
    commands.add_parser("list")
    commands.add_parser("next")
    show = commands.add_parser("show")
    show.add_argument("task_id")

    transition = commands.add_parser("transition")
    transition.add_argument("task_id")
    transition.add_argument("state", choices=WORK_STATES)
    transition.add_argument("--packet")
    transition.add_argument("--branch")
    transition.add_argument("--next-gate", required=True)
    transition.add_argument("--evidence", action="append", default=[])
    transition.add_argument("--actor", required=True)
    transition.add_argument("--actor-role", required=True, choices=ACTOR_ROLES)
    transition.add_argument("--note", required=True)

    condition = commands.add_parser("set-condition")
    condition.add_argument("task_id")
    condition.add_argument("condition", choices=CONDITIONS)
    condition.add_argument("--packet")
    condition.add_argument("--next-gate", required=True)
    _add_actor_arguments(condition)

    delivery = commands.add_parser("set-delivery")
    delivery.add_argument("task_id")
    delivery.add_argument("delivery_state", choices=DELIVERY_STATES)
    _add_actor_arguments(delivery)
    return parser


def main() -> int:
    args = _parser().parse_args()
    root = args.root.resolve()
    try:
        board = load_board(root)
        if args.command == "validate":
            _command_validate(board, root)
        elif args.command == "render":
            _command_render(board, root, args.check)
        elif args.command == "list":
            _validate_or_raise(board, root)
            _command_list(board)
        elif args.command == "next":
            _validate_or_raise(board, root)
            _command_next(board)
        elif args.command == "show":
            _validate_or_raise(board, root)
            _command_show(board, args.task_id)
        elif args.command == "transition":
            _command_transition(board, root, args)
        elif args.command == "set-condition":
            _command_condition(board, root, args)
        elif args.command == "set-delivery":
            _command_delivery(board, root, args)
        else:
            raise BoardError(f"unsupported command: {args.command}")
    except BoardError as exc:
        print(f"Development board error:\n{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
