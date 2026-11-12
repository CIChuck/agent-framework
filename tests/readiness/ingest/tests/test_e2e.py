"""Offline E2E admission checks; fake vectors never earn live-model credit."""

from __future__ import annotations

import base64
import contextlib
import io
import json
import struct
import unittest
from pathlib import Path

from ingest import e2e
from ingest.tests.test_manifests import unit


class EndToEnd(unittest.TestCase):
    def test_transport_requires_exact_identity_count_order_and_finite_vectors(
        self,
    ) -> None:
        vector = [0.25] * 768
        valid: dict[str, object] = {
            "model": e2e.MODEL,
            "data": [{"index": 0, "embedding": vector}],
        }
        self.assertEqual(e2e.validated_vectors(valid, 1), [vector])
        bad = [
            {"model": "other", "data": valid["data"]},
            {"model": e2e.MODEL, "data": []},
            {"model": e2e.MODEL, "data": [{"index": True, "embedding": vector}]},
            {"model": e2e.MODEL, "data": [{"index": 1, "embedding": vector}]},
        ]
        for payload in bad:
            with self.subTest(payload=str(payload)[:60]), self.assertRaises(ValueError):
                e2e.validated_vectors(payload, 1)
        for values in (
            [0.0] * 768,
            vector[:-1],
            [float("nan")] + vector[1:],
            [True] + vector[1:],
        ):
            with self.assertRaises(ValueError):
                e2e.validated_vectors(
                    {"model": e2e.MODEL, "data": [{"index": 0, "embedding": values}]}, 1
                )
        with self.assertRaises(ValueError):
            e2e.validated_vectors(valid, 0)

    def test_base64_decoding_preserves_float_values(self) -> None:
        encoded = base64.b64encode(struct.pack("<768f", *([0.5] * 768))).decode()
        payload = {"model": e2e.MODEL, "data": [{"index": 0, "embedding": encoded}]}
        self.assertEqual(e2e.validated_vectors(payload, 1), [[0.5] * 768])
        with self.assertRaises(ValueError):
            e2e.validated_vectors(
                {"model": e2e.MODEL, "data": [{"index": 0, "embedding": "AA=="}]}, 1
            )

    def test_loaded_identity_requires_selected_instance_and_exact_context(self) -> None:
        def status(context: int, model: str = e2e.MODEL) -> dict[str, object]:
            return {
                "models": [
                    {
                        "type": "embedding",
                        "max_context_length": 2048,
                        "loaded_instances": [
                            {"id": model, "config": {"context_length": context}}
                        ],
                    }
                ]
            }

        self.assertEqual(e2e.model_state(status(2048))["context"], 2048)
        invalid: list[dict[str, object]] = [
            status(1024),
            status(2048, "other"),
            {"models": []},
        ]
        for payload in invalid:
            with self.assertRaises(ValueError):
                e2e.model_state(payload)

    def test_budget_exhaustion_and_invalid_reservations_preserve_state(self) -> None:
        root = unit()
        (root / "reports").mkdir()
        path = root / "reports/live-budget.json"
        e2e.write(path, {"requests": 63, "vectors": 255, "tokens": 131000})
        self.assertEqual(e2e.Budget(root).charge(1, 20), 64)
        before = path.read_bytes()
        for vectors, tokens in ((0, 0), (-1, 0), (0, -1)):
            with self.assertRaises(ValueError):
                e2e.Budget(root).charge(vectors, tokens)
            self.assertEqual(path.read_bytes(), before)

    def test_store_receipt_cannot_redirect_reopen(self) -> None:
        root = unit()
        (root / "stores").mkdir()
        run_id = "a" * 32
        store = e2e.store_path(root, run_id)
        store.mkdir()
        self.assertEqual(e2e.store_path(root, run_id, str(store)), store)
        for value in (str(root), str(store / "nested")):
            with self.assertRaises(ValueError):
                e2e.store_path(root, run_id, value)
        with self.assertRaises(ValueError):
            e2e.store_path(root, "../escape")

    def test_report_refuses_failed_stale_missing_or_modified_evidence(self) -> None:
        root = unit()
        folder = root / "reports/e2e"
        folder.mkdir(parents=True)
        runner = e2e.sha(Path(e2e.__file__).read_bytes())
        for mode in ("normal", "optimized"):
            run_id = ("a" if mode == "normal" else "b") * 32
            e2e.write(
                folder / f"{mode}.latest.json",
                {"run_id": run_id, "source_sha256": runner},
            )
            evidence = {}
            for suffix in ("corpus", "stored", "reopened", "http"):
                path = folder / f"{run_id}.{suffix}.json"
                e2e.write(path, {"fixture": suffix})
                evidence[suffix] = e2e.sha(path.read_bytes())
            e2e.write(
                folder / f"{run_id}.result.json",
                {
                    "status": "PASS",
                    "run_id": run_id,
                    "mode": mode,
                    "source_sha256": runner,
                    "evidence": evidence,
                    "commands": [
                        {"operation": operation, "exit": 0}
                        for operation in (*e2e.CASES, "chunks", "embed", "reopen")
                    ],
                },
            )
        e2e.write(root / "reports/live-budget.json", {"requests": 0})
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(e2e.report(root), 0)
        result_path = folder / ("a" * 32 + ".result.json")
        original = result_path.read_bytes()
        for field, value in (
            ("status", "FAIL"),
            ("source_sha256", "old"),
            ("evidence", {}),
            ("commands", []),
        ):
            payload = json.loads(original)
            payload[field] = value
            e2e.write(result_path, payload)
            with self.assertRaises(ValueError):
                e2e.report(root)
        result_path.write_bytes(original)
        e2e.write(folder / ("a" * 32 + ".http.json"), {"changed": True})
        with self.assertRaises(ValueError):
            e2e.report(root)
