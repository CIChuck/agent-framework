"""Offline E2E admission checks; fake vectors never earn live-model credit."""

from __future__ import annotations

import base64
import contextlib
import io
import json
import os
import struct
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from ingest import e2e
from ingest.tests.test_manifests import unit


def report_fixture() -> Path:
    """Synthetic reporting receipts only; no conversion, inference or store credit."""
    root = unit() / ".friday_test/runs/docling-behavior-e2e-synthetic"
    for name in (
        "config",
        "logs",
        "reports/e2e",
        "target",
        "cache",
        "tmp",
        "assets",
        "inputs",
        "source/ingest",
    ):
        (root / name).mkdir(parents=True)
    source = Path(e2e.__file__)
    (root / "source/ingest/e2e.py").write_bytes(source.read_bytes())
    behavior = source.with_name("behavior.py").read_bytes()
    (root / "source/ingest/behavior.py").write_bytes(behavior)
    runner = e2e.sha(source.read_bytes())
    folder = root / "reports/e2e"
    for mode in ("normal", "optimized"):
        run_id = ("a" if mode == "normal" else "b") * 32
        e2e.write(
            folder / f"{mode}.latest.json",
            {"run_id": run_id, "source_sha256": runner},
        )
        evidence = {}
        for suffix in ("corpus", "stored", "reopened", "http"):
            path = folder / f"{run_id}.{suffix}.json"
            payload: dict[str, object] = {"fixture": "synthetic report " + suffix}
            if suffix == "corpus":
                payload.update(
                    run_id=run_id,
                    e2e_sha256=runner,
                    conversion_attempts={
                        "pdf-native.pdf.json": {
                            "attempt_id": run_id,
                            "runner_sha256": e2e.sha(behavior),
                        },
                        "docx-long.docx.json": {
                            "attempt_id": run_id,
                            "runner_sha256": e2e.sha(behavior),
                        },
                    },
                )
            e2e.write(path, payload)
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
    return root


def replace_report_corpus(root: Path, payload: dict[str, object]) -> None:
    """Keep synthetic artifact hashes valid to exercise source-binding controls."""
    folder = root / "reports/e2e"
    corpus_path = folder / ("a" * 32 + ".corpus.json")
    e2e.write(corpus_path, payload)
    result_path = folder / ("a" * 32 + ".result.json")
    result = e2e.read(result_path)
    evidence = e2e.obj(result["evidence"])
    evidence["corpus"] = e2e.sha(corpus_path.read_bytes())
    result["evidence"] = evidence
    e2e.write(result_path, result)


def report_main(root: Path, output: io.StringIO) -> int:
    """Exercise canonical dispatch under the guarded normal/optimized interpreter."""
    source = str(root / "source/ingest/e2e.py")
    with (
        patch.object(e2e, "__file__", source),
        patch.object(sys, "argv", [source, "report", "--run-root", str(root)]),
        patch.object(sys, "path", list(sys.path)),
        contextlib.redirect_stdout(output),
    ):
        return e2e.main()


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
        root = report_fixture()
        folder = root / "reports/e2e"
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

    def test_report_requires_valid_nonempty_consistent_conversion_bindings(
        self,
    ) -> None:
        bad: list[object] = [None, [], {}, {"source": None}]
        for digest in (None, True, "", "old", "A" * 64, "g" * 64, "0" * 63):
            bad.append({"source": {"runner_sha256": digest}})
        root = report_fixture()
        corpus_path = root / "reports/e2e" / ("a" * 32 + ".corpus.json")
        original = e2e.read(corpus_path)
        binding = e2e.obj(original["conversion_attempts"])
        bad.extend(
            [
                {"source": {}},
                {"source": {"runner_sha256": "0" * 64}},
                {**binding, "conflict": {"runner_sha256": "0" * 64}},
            ]
        )
        missing = dict(original)
        del missing["conversion_attempts"]
        replace_report_corpus(root, missing)
        with self.assertRaisesRegex(ValueError, "Report conversion source binding"):
            e2e.report(root)
        for attempts in bad:
            with self.subTest(attempts=attempts):
                replace_report_corpus(
                    root, {**original, "conversion_attempts": attempts}
                )
                with self.assertRaisesRegex(ValueError, "Report conversion"):
                    e2e.report(root)

    def test_report_keeps_earlier_mode_after_admission_pointer_advances(self) -> None:
        root = report_fixture()
        admitted = root / "reports/admitted"
        admitted.mkdir()
        for name in ("pdf-native.pdf", "docx-long.docx"):
            e2e.write(admitted / (name + ".attempt.json"), {"attempt_id": "b" * 32})
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(e2e.report(root), 0)

    def test_report_refuses_missing_changed_and_aliased_conversion_source(self) -> None:
        for change in ("missing", "changed", "symlink", "hardlink", "parent-symlink"):
            with self.subTest(change=change):
                root = report_fixture()
                source = root / "source/ingest/behavior.py"
                if change == "changed":
                    source.write_bytes(source.read_bytes() + b"\n# synthetic tamper\n")
                elif change == "parent-symlink":
                    folder = source.parent
                    renamed = folder.with_name("physical-ingest")
                    folder.rename(renamed)
                    folder.symlink_to(renamed, target_is_directory=True)
                else:
                    renamed = source.with_name("physical-behavior.py")
                    source.rename(renamed)
                    if change == "symlink":
                        source.symlink_to(renamed)
                    elif change == "hardlink":
                        os.link(renamed, source)
                with self.assertRaisesRegex(ValueError, "Report conversion source"):
                    e2e.report(root)

    def test_report_refuses_aliased_corpus_binding(self) -> None:
        for alias in ("symlink", "hardlink"):
            with self.subTest(alias=alias):
                root = report_fixture()
                corpus_path = root / "reports/e2e" / ("a" * 32 + ".corpus.json")
                renamed = corpus_path.with_suffix(".physical.json")
                corpus_path.rename(renamed)
                if alias == "symlink":
                    corpus_path.symlink_to(renamed)
                else:
                    os.link(renamed, corpus_path)
                with self.assertRaisesRegex(ValueError, "binding missing/aliased"):
                    e2e.report(root)

    def test_canonical_report_dispatch_binds_both_sources(self) -> None:
        root = report_fixture()
        source = root / "source/ingest/e2e.py"
        output = io.StringIO()
        self.assertEqual(report_main(root, output), 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "PASS")
        output.seek(0)
        output.truncate()
        corpus_path = root / "reports/e2e" / ("a" * 32 + ".corpus.json")
        corpus_data = e2e.read(corpus_path)
        missing_binding = dict(corpus_data)
        del missing_binding["conversion_attempts"]
        replace_report_corpus(root, missing_binding)
        with self.assertRaisesRegex(
            ValueError, "Report conversion source binding missing"
        ):
            report_main(root, output)
        self.assertEqual(output.getvalue(), "")
        replace_report_corpus(root, corpus_data)
        behavior = source.with_name("behavior.py")
        original = behavior.read_bytes()
        behavior.write_bytes(original + b"\nraise RuntimeError('synthetic tamper')\n")
        with self.assertRaisesRegex(ValueError, "Report conversion source changed"):
            report_main(root, output)
        self.assertEqual(output.getvalue(), "")
        behavior.write_bytes(original)
        source.write_bytes(source.read_bytes() + b"\n# synthetic e2e tamper\n")
        with self.assertRaisesRegex(ValueError, "Report runner changed"):
            report_main(root, output)
        self.assertEqual(output.getvalue(), "")
