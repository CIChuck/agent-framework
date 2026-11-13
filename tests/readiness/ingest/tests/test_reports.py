from __future__ import annotations

import unittest

from ingest.manifests import Refusal, object_value, sequence, text
from ingest.reports import report
from ingest.tests.test_ledger import ledger


class Reports(unittest.TestCase):
    def test_consistency_report_preserves_incomplete_and_evidence_classes(self) -> None:
        value = report(ledger())
        self.assertEqual(value["status"], "INCOMPLETE")
        self.assertFalse(value["full_readiness"])
        self.assertEqual(value["operator_attested"], {})
        self.assertEqual(len(sequence(value["unqualified"])), 5)
        self.assertIn("no OS sandbox", text(value["containment"]))

    def test_prepared_fixture_receipt_is_not_current_byte_or_converter_proof(
        self,
    ) -> None:
        log = ledger()
        log.append(
            "finish",
            {
                "operation": "prepare_fixtures",
                "manifest_sha256": "f" * 64,
                "fixture_count": 30,
                "converter_qualified": False,
            },
            log.tip(),
        )
        value = report(log)
        rows = sequence(value["prepared_inputs"])
        self.assertEqual(len(rows), 1)
        self.assertIs(object_value(rows[0])["current_bytes_revalidated"], False)
        self.assertIs(value["full_readiness"], False)
        self.assertEqual(value["ledger_tip"], log.tip())
        self.assertEqual(
            value["executed"],
            ["C0 control-run initialization", "synthetic input preparation"],
        )
        log.append(
            "finish",
            {
                "operation": "prepare_fixtures",
                "manifest_sha256": "e" * 64,
                "fixture_count": 30,
                "converter_qualified": True,
            },
            log.tip(),
        )
        with self.assertRaises(Refusal):
            report(log)
