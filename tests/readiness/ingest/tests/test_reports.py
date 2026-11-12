from __future__ import annotations

import unittest

from ingest.manifests import sequence, text
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
