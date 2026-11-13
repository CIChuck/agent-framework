"""Single-writer canonical ledger, explicit promotions and cumulative reservations."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from ingest.manifests import (
    RECORD_LIMIT,
    canonical,
    decode,
    digest,
    fields,
    integer,
    require,
    text,
)

ZERO = "0" * 64
EVENTS = {"init", "candidate", "promote", "reserve", "finish", "failure"}


class Ledger:
    def __init__(self, state: Path) -> None:
        self.state = state
        self.path = state / "bindings.jsonl"
        self._lease_token: object | None = None
        self._lease_pid: int | None = None

    @contextmanager
    def lease(self) -> Iterator[object]:
        lock = self.state / "writer.lock"
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.write(fd, str(os.getpid()).encode())
            token = object()
            self._lease_token = token
            self._lease_pid = os.getpid()
            yield token
        finally:
            self._lease_token = None
            self._lease_pid = None
            os.close(fd)
            lock.unlink()

    def records(self) -> list[dict[str, object]]:
        if not self.path.exists():
            return []
        require(
            not self.path.is_symlink()
            and self.path.stat().st_size <= 16 * RECORD_LIMIT,
            "Ledger size/type refused",
        )
        raw = self.path.read_bytes()
        require(raw.endswith(b"\n"), "Truncated ledger")
        records: list[dict[str, object]] = []
        tip = ZERO
        for line in raw.splitlines():
            record = fields(
                decode(line),
                {
                    "schema",
                    "sequence",
                    "event",
                    "previous",
                    "payload",
                    "sha256",
                    "timestamp",
                },
            )
            require(
                type(record["schema"]) is int
                and record["schema"] == 1
                and record["sequence"] == len(records),
                "Ledger order/schema",
            )
            require(
                isinstance(record["event"], str)
                and record["event"] in EVENTS
                and record["previous"] == tip,
                "Ledger chain/event",
            )
            without = {key: value for key, value in record.items() if key != "sha256"}
            tip = digest(canonical(without))
            require(record["sha256"] == tip, "Ledger tampered")
            require(
                (not records) == (record["event"] == "init"), "Ledger init transition"
            )
            records.append(record)
        return records

    def append(
        self, event: str, payload: dict[str, object], expected_tip: str
    ) -> dict[str, object]:
        require(event in EVENTS, "Unknown ledger event")
        with self.lease() as token:
            return self.append_held(event, payload, expected_tip, token)

    def append_held(
        self, event: str, payload: dict[str, object], expected_tip: str, token: object
    ) -> dict[str, object]:
        """Stage owner appends without dropping/reacquiring its exclusive lease."""
        require(
            token is self._lease_token and self._lease_pid == os.getpid(),
            "Run writer lease is not owned",
        )
        require(event in EVENTS, "Unknown ledger event")
        records = self.records()
        tip = text(records[-1]["sha256"]) if records else ZERO
        require(tip == expected_tip, "Stale ledger tip")
        require((not records) == (event == "init"), "Invalid init transition")
        row: dict[str, object] = {
            "schema": 1,
            "sequence": len(records),
            "event": event,
            "previous": tip,
            "payload": payload,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        row["sha256"] = digest(canonical(row))
        encoded = canonical(row) + b"\n"
        require(len(encoded) <= RECORD_LIMIT, "Ledger record too large")
        with self.path.open("ab") as target:
            target.write(encoded)
            target.flush()
            os.fsync(target.fileno())
        return row

    def tip(self) -> str:
        records = self.records()
        return text(records[-1]["sha256"]) if records else ZERO

    def stopped(self) -> bool:
        # An offline stop is terminal for effects in this C0 run; report remains readable.
        return (self.state / "stop.json").exists()

    def reserve(self, resource: str, amount: int, ceiling: int) -> None:
        integer(amount)
        require(not self.stopped(), "Run stopped; use a new run for effects")
        records = self.records()
        used = 0
        for row in records:
            if row["event"] == "reserve":
                payload = fields(row["payload"], {"resource", "amount"})
                if payload["resource"] == resource:
                    used += integer(payload["amount"])
        require(used + amount <= ceiling, "Cumulative resource ceiling")
        self.append(
            "reserve",
            {"resource": resource, "amount": amount},
            text(records[-1]["sha256"]) if records else ZERO,
        )

    def promote(self, manifest_sha: str, receipt: dict[str, object]) -> None:
        require(not self.stopped(), "Run stopped")
        data = fields(
            receipt,
            {"schema", "actor", "run_id", "stage", "manifest_sha256", "predecessor"},
        )
        require(
            type(data["schema"]) is int
            and data["schema"] == 1
            and data["manifest_sha256"] == manifest_sha,
            "Promotion identity mismatch",
        )
        require(bool(text(data["actor"]).strip()), "Promotion actor absent")
        records = self.records()
        require(bool(records), "Run has no immutable identity")
        identity = fields(
            records[0]["payload"], {"run_id", "config_sha256", "harness_sha256"}
        )
        require(
            data["run_id"] == identity["run_id"], "Promotion belongs to another run"
        )
        stage = text(data["stage"])
        predecessors = {"A0": None, "A1": "A0", "A2": "A1", "MODEL": "A2"}
        require(stage in predecessors, "Unknown promotion stage")
        promoted = [
            fields(
                row["payload"],
                {
                    "schema",
                    "actor",
                    "run_id",
                    "stage",
                    "manifest_sha256",
                    "predecessor",
                },
            )["stage"]
            for row in records
            if row["event"] == "promote"
        ]
        require(stage not in promoted, "Stage already promoted")
        require(
            predecessors[stage] is None or predecessors[stage] in promoted,
            "Promotion prerequisite missing",
        )
        require(
            any(
                row["event"] == "candidate"
                and row["payload"]
                == {"stage": data["stage"], "manifest_sha256": manifest_sha}
                for row in records
            ),
            "Promotion has no matching candidate",
        )
        self.append("promote", data, text(data["predecessor"]))
