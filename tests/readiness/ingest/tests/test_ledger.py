from __future__ import annotations

import unittest

from ingest.ledger import ZERO, Ledger
from ingest.manifests import Refusal, canonical
from ingest.tests.test_manifests import unit


def ledger() -> Ledger:
    result = Ledger(unit())
    result.append(
        "init",
        {"run_id": "test", "config_sha256": "a" * 64, "harness_sha256": "b" * 64},
        ZERO,
    )
    return result


class Ledgers(unittest.TestCase):
    def test_promotion_requires_existing_candidate_actor_and_tip(self) -> None:
        log = ledger()
        sha = "c" * 64
        log.append("candidate", {"stage": "A0", "manifest_sha256": sha}, log.tip())
        receipt = {
            "schema": 1,
            "actor": "approved-controller",
            "run_id": "test",
            "stage": "A0",
            "manifest_sha256": sha,
            "predecessor": log.tip(),
        }
        log.promote(sha, receipt)
        self.assertEqual(log.records()[-1]["event"], "promote")
        with self.assertRaises(Refusal):
            log.promote(sha, receipt)
        with self.assertRaises(Refusal):
            log.promote("d" * 64, receipt)

    def test_cumulative_budget_survives_reopen_and_failure(self) -> None:
        log = ledger()
        log.reserve("requests", 63, 64)
        reopened = Ledger(log.state)
        reopened.reserve("requests", 1, 64)
        with self.assertRaises(Refusal):
            reopened.reserve("requests", 1, 64)
        self.assertEqual(len(reopened.records()), 3)

    def test_partial_tamper_and_concurrent_writer_refuse(self) -> None:
        log = ledger()
        with log.lease(), self.assertRaises(FileExistsError):
            log.append("finish", {}, log.tip())
        old = log.path.read_bytes()
        log.path.write_bytes(old[:-1])
        with self.assertRaises(Refusal):
            log.records()
        log.path.write_bytes(old.replace(b'"test"', b'"evil"'))
        with self.assertRaises(Refusal):
            log.records()

    def test_stop_is_terminal_for_counters(self) -> None:
        log = ledger()
        (log.state / "stop.json").write_bytes(canonical({"schema": 1}))
        with self.assertRaises(Refusal):
            log.reserve("requests", 1, 64)

    def test_stage_order_and_receipt_schema_refuse(self) -> None:
        log = ledger()
        sha = "e" * 64
        log.append("candidate", {"stage": "A2", "manifest_sha256": sha}, log.tip())
        receipt = {
            "schema": 1,
            "actor": "approved-controller",
            "run_id": "test",
            "stage": "A2",
            "manifest_sha256": sha,
            "predecessor": log.tip(),
        }
        with self.assertRaises(Refusal):
            log.promote(sha, receipt)
        with self.assertRaises(Refusal):
            log.promote(sha, receipt | {"schema": True})

    def test_operation_append_requires_live_same_instance_writer_lease(self) -> None:
        log = ledger()
        tip = log.tip()
        with self.assertRaises(Refusal):
            log.append_held("finish", {}, tip, object())
        with log.lease() as token:
            with self.assertRaises(Refusal):
                Ledger(log.state).append_held("finish", {}, tip, token)
            with self.assertRaises(FileExistsError):
                Ledger(log.state).append("finish", {}, tip)
            log.append_held("finish", {"operation": "owned"}, tip, token)
            with self.assertRaises(Refusal):
                log.append_held("finish", {}, tip, token)
        with self.assertRaises(Refusal):
            log.append_held("finish", {}, log.tip(), token)
        self.assertFalse((log.state / "writer.lock").exists())
