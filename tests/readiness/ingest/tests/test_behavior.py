"""Pure behavior-runner checks; real Docling is selected explicitly by its CLI."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from ingest import behavior
from ingest.behavior import (
    admission_reasons,
    admitted_document,
    begin_attempt,
    compare_text,
    document_ready,
    environment,
    fixed_chunks,
    recursive_chunks,
    supervise,
)
from ingest.tests.test_manifests import unit


class Behavior(unittest.TestCase):
    def test_empty_image_and_table_markup_is_not_meaningful_text(self) -> None:
        oracle: dict[str, object] = {"contains": [], "excludes": []}
        for value in ("", "  ", "<!-- image -->", "![picture](local.png)", "|---|---|"):
            self.assertIs(compare_text(value, oracle, False)["meaningful"], False)
        self.assertIs(compare_text("0", oracle, False)["meaningful"], True)

    def test_oracles_preserve_unicode_and_check_order_and_exclusion(self) -> None:
        oracle: dict[str, object] = {
            "contains": ["café", "東京"],
            "excludes": ["hidden"],
        }
        self.assertEqual(
            compare_text("cafe\u0301\n\n東京", oracle, True),
            {"missing": [], "leaked": [], "order_ok": True, "meaningful": True},
        )
        result = compare_text("東京 hidden café", oracle, True)
        self.assertEqual(result["leaked"], ["hidden"])
        self.assertIs(result["order_ok"], False)

    def test_fixed_chunks_cover_every_character_and_prepared_token_limit(self) -> None:
        value = "café 東京 Ω and text\n" * 12
        chunks = fixed_chunks(
            value,
            16,
            lambda text: len(text) + 2,
            lambda text: list(range(1, len(text) + 1)),
        )
        self.assertEqual("".join(chunks), value)
        self.assertTrue(all(len(chunk) + 2 <= 16 for chunk in chunks))
        self.assertGreater(len(chunks), 1)

    def test_recursive_chunks_retain_separators_and_unicode(self) -> None:
        value = "First paragraph.\n\n東京 second line. More text.\n" * 8
        chunks = recursive_chunks(
            value,
            32,
            lambda text: len(text) + 2,
            lambda text: list(range(1, len(text) + 1)),
        )
        self.assertEqual("".join(chunks), value)
        self.assertTrue(all(len(chunk) + 2 <= 32 for chunk in chunks))

    def test_invalid_limits_offsets_and_exhausted_prefix_refuse(self) -> None:
        for limit in (True, 0, 15, 8193):
            with self.assertRaises(ValueError):
                fixed_chunks(
                    "long source text" * 8, limit, len, lambda text: [len(text)]
                )
        with self.assertRaises(ValueError):
            fixed_chunks("long source text" * 8, 16, len, lambda text: [0])
        with self.assertRaises(ValueError):
            fixed_chunks("text", 16, lambda text: 20, lambda text: [len(text)])

    def test_private_environment_omits_credentials_and_sets_cache_roots(self) -> None:
        root = unit()
        (root / "config").mkdir()
        result = environment(root)
        self.assertEqual(result["HOME"], os.environ.get("HOME", ""))
        for key in (
            "OPENAI_API_KEY",
            "HF_TOKEN",
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "PYTHONPATH",
        ):
            self.assertNotIn(key, result)
        for key in (
            "HF_HOME",
            "UV_CACHE_DIR",
            "TORCH_HOME",
            "XDG_CACHE_HOME",
            "MPLCONFIGDIR",
        ):
            self.assertTrue(result[key].startswith(str(root) + "/"))

    def test_structural_admission_refuses_unsupported_hidden_and_formula_data(
        self,
    ) -> None:
        facts: dict[str, object] = {
            "refusal_codes": ["included_formula_cache_missing"],
            "units": [
                {"hidden": False, "hidden_rows": [2], "hidden_columns": ["2:2"]},
                {"hidden": True, "hidden_rows": [3]},
            ],
        }
        self.assertEqual(
            admission_reasons(facts),
            [
                "included_formula_cache_missing",
                "unsupported_hidden_columns",
                "unsupported_hidden_rows",
            ],
        )
        self.assertEqual(admission_reasons({"refusal_codes": [], "units": []}), [])

    def test_refused_partial_or_stale_documents_never_reach_chunking(self) -> None:
        raw = b"serialized document fixture"
        identity: dict[str, object] = {
            "supervised": False,
            "source_sha256": "input digest",
            "runner_sha256": "runner digest",
            "settings": {"include_furniture": True, "enforce_admission": True},
        }
        attempt = {"attempt_id": "a" * 32, **identity}
        record: dict[str, object] = {
            "attempt": attempt,
            **identity,
            "status": "pass",
            "native_docling_called": True,
            "conversion_status": "success",
            "errors": [],
            "comparison": {"meaningful": True},
            "output_json_sha256": hashlib.sha256(raw).hexdigest(),
        }
        self.assertTrue(document_ready(record, raw, attempt, identity))
        self.assertFalse(document_ready(record, raw + b"tamper", attempt, identity))
        updates: list[dict[str, object]] = [
            {"status": "admission_refused"},
            {"native_docling_called": False},
            {"conversion_status": "partial_success"},
            {"errors": ["incomplete conversion"]},
            {"comparison": {"meaningful": False}},
        ]
        for update in updates:
            self.assertFalse(document_ready(record | update, raw, attempt, identity))
        for field in ("source_sha256", "runner_sha256", "settings"):
            self.assertFalse(
                document_ready(record, raw, attempt, identity | {field: "changed"})
            )
        self.assertFalse(
            document_ready(record, raw, attempt | {"attempt_id": "b" * 32}, identity)
        )

    def conversion_fixture(self) -> tuple[Path, bytes]:
        root = unit()
        for folder in ("config", "reports", "inputs/generated", "logs", "source"):
            (root / folder).mkdir(parents=True)
        cases = [
            {
                "file": name,
                "format": "pdf",
                "contains": [name],
                "excludes": [],
                "outcome": "pass",
            }
            for name in ("first.pdf", "sibling.pdf")
        ]
        (root / "config/oracles.json").write_text(json.dumps({"cases": cases}))
        for row in cases:
            (root / "inputs/generated" / str(row["file"])).write_bytes(b"input bytes")
        return root, b"serialized meaningful document"

    def publish_success(
        self, root: Path, filename: str, raw: bytes, supervised: bool = False
    ) -> dict[str, object]:
        attempt = begin_attempt(root, filename, True, True, supervised)
        record: dict[str, object] = {
            "attempt": attempt,
            "source_sha256": attempt["source_sha256"],
            "runner_sha256": attempt["runner_sha256"],
            "status": "pass",
            "native_docling_called": True,
            "conversion_status": "success",
            "errors": [],
            "comparison": {"meaningful": True},
            "output_json_sha256": hashlib.sha256(raw).hexdigest(),
        }
        destination = root / "reports/admitted"
        (destination / (filename + ".result.json")).write_text(json.dumps(record))
        (
            destination / "attempts" / (str(attempt["attempt_id"]) + ".result.json")
        ).write_text(json.dumps(record))
        return record

    def test_pending_failed_and_mismatched_latest_attempts_preserve_siblings(
        self,
    ) -> None:
        root, raw = self.conversion_fixture()
        first = self.publish_success(root, "first.pdf", raw)
        first_attempt = first["attempt"]
        if not isinstance(first_attempt, dict):
            raise ValueError("Fixture attempt missing")
        sibling = self.publish_success(root, "sibling.pdf", raw)
        self.assertEqual(admitted_document(root, "first.pdf", raw), first)
        pending = begin_attempt(root, "first.pdf", True, True)
        self.assertNotEqual(pending["attempt_id"], first_attempt["attempt_id"])
        with self.assertRaises((ValueError, OSError)):
            admitted_document(root, "first.pdf", raw)
        self.assertEqual(admitted_document(root, "sibling.pdf", raw), sibling)
        destination = root / "reports/admitted"
        failed = first | {"attempt": pending, "status": "error"}
        (destination / ("first.pdf.result.json")).write_text(json.dumps(failed))
        (
            destination / "attempts" / (str(pending["attempt_id"]) + ".result.json")
        ).write_text(json.dumps(failed))
        with self.assertRaises(ValueError):
            admitted_document(root, "first.pdf", raw)
        fresh = self.publish_success(root, "first.pdf", raw)
        self.assertEqual(admitted_document(root, "first.pdf", raw), fresh)
        self.assertTrue(
            (
                destination
                / "attempts"
                / (str(first_attempt["attempt_id"]) + ".result.json")
            ).is_file()
        )
        for field in ("source_sha256", "runner_sha256", "settings"):
            with (
                patch.object(
                    behavior,
                    "conversion_identity",
                    return_value={
                        key: value
                        for key, value in pending.items()
                        if key != "attempt_id"
                    }
                    | {field: "changed"},
                ),
                self.assertRaises(ValueError),
            ):
                admitted_document(root, "first.pdf", raw)
        (root / "inputs/generated/first.pdf").write_bytes(b"changed source")
        with self.assertRaises(ValueError):
            admitted_document(root, "first.pdf", raw)
        self.assertEqual(admitted_document(root, "sibling.pdf", raw), sibling)
        self.publish_success(root, "first.pdf", raw)
        config = root / "config/oracles.json"
        oracles = json.loads(config.read_bytes())
        oracles["cases"][0]["contains"] = ["changed configuration"]
        config.write_text(json.dumps(oracles))
        with self.assertRaises(ValueError):
            admitted_document(root, "first.pdf", raw)
        self.assertEqual(admitted_document(root, "sibling.pdf", raw), sibling)

    def test_direct_and_never_started_supervised_attempts_revoke_before_setup(
        self,
    ) -> None:
        root, raw = self.conversion_fixture()
        self.publish_success(root, "first.pdf", raw)
        with (
            patch.object(behavior, "offline", side_effect=RuntimeError("setup failed")),
            self.assertRaises(RuntimeError),
        ):
            behavior.convert_case(root, "first.pdf", True, True)
        with self.assertRaises((ValueError, OSError)):
            admitted_document(root, "first.pdf", raw)

        self.publish_success(root, "first.pdf", raw)
        argv = [
            sys.executable,
            "-I",
            "-S",
            "-B",
            str(Path(behavior.__file__).resolve()),
            "convert",
            "--run-root",
            str(root),
            "--case",
            "first.pdf",
            "--include-furniture",
            "--enforce-admission",
        ]
        with (
            patch.object(
                behavior.subprocess,
                "Popen",
                side_effect=FileNotFoundError("never started"),
            ),
            self.assertRaises(FileNotFoundError),
        ):
            supervise(root, "never-started", argv, 1)
        with self.assertRaises((ValueError, OSError)):
            admitted_document(root, "first.pdf", raw)
        self.publish_success(root, "first.pdf", raw)
        (root / "inputs/generated/first.pdf").unlink()
        with self.assertRaises(ValueError):
            begin_attempt(root, "first.pdf", True, True)
        with self.assertRaises((ValueError, OSError)):
            admitted_document(root, "first.pdf", raw)

    def test_supervisor_must_confirm_even_a_published_worker_success(self) -> None:
        root, raw = self.conversion_fixture()
        record = self.publish_success(root, "first.pdf", raw, supervised=True)
        attempt = record["attempt"]
        if not isinstance(attempt, dict):
            raise ValueError("Fixture attempt missing")
        attempt_id = str(attempt["attempt_id"])
        attempts = root / "reports/admitted/attempts"
        with self.assertRaises((ValueError, OSError)):
            admitted_document(root, "first.pdf", raw)
        receipt = attempts / (attempt_id + ".supervision.json")
        for exit_code, reason in ((-15, "time_limit"), (0, "time_limit"), (1, None)):
            receipt.write_text(
                json.dumps(
                    {"attempt_id": attempt_id, "exit": exit_code, "reason": reason}
                )
            )
            with self.assertRaises(ValueError):
                admitted_document(root, "first.pdf", raw)
        receipt.write_text(
            json.dumps({"attempt_id": attempt_id, "exit": 0, "reason": None})
        )
        self.assertEqual(admitted_document(root, "first.pdf", raw), record)
