"""Controlled long-source fixtures; no model or third-party reader test credit."""

from __future__ import annotations

import io
import json
import os
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from ingest import large_documents as corpus
from ingest.tests.test_manifests import unit


def root() -> Path:
    result = unit()
    (result / "inputs").mkdir()
    return result


class LargeDocuments(unittest.TestCase):
    def test_cross_section_answers_require_middle_and_tail_in_every_profile(
        self,
    ) -> None:
        for size in corpus.SIZES:
            parts = [part.body for part in corpus.sections(size)]
            query = corpus.object_value(
                corpus.sequence(corpus.oracle(size)["queries"])[-1]
            )
            answers = [
                corpus.text(value) for value in corpus.sequence(query["answers"])
            ]
            middle, tail = parts[size // 2 - 1], parts[-1]
            self.assertIn(answers[0], middle)
            self.assertNotIn(
                answers[0], " ".join(parts[: size // 2 - 1] + parts[size // 2 :])
            )
            self.assertIn(answers[1], tail)
            self.assertNotIn(answers[1], " ".join(parts[:-1]))
            self.assertFalse(all(answer in middle for answer in answers))
            self.assertFalse(all(answer in tail for answer in answers))
            corpus.cross_section_control(parts, query)
            parts[-1] += " " + answers[0]
            with self.assertRaisesRegex(ValueError, "supplied by one section"):
                corpus.cross_section_control(parts, query)

    def test_length_progression_preserves_end_facts_and_does_not_claim_tokens(
        self,
    ) -> None:
        previous = 0
        for size in corpus.SIZES:
            value = corpus.canonical(size)
            words = len(value.split())
            self.assertGreater(words, previous)
            previous = words
            expected = corpus.oracle(size)
            for marker in [
                *corpus.sequence(expected["anchors"]),
                *corpus.sequence(expected["facts"]),
            ]:
                self.assertIn(corpus.text(marker), value)
            self.assertLess(
                value.index(f"SOURCE_START_{size}"),
                value.index(f"SOURCE_MIDDLE_{size}"),
            )
            self.assertLess(
                value.index(f"SOURCE_MIDDLE_{size}"), value.index(f"SOURCE_TAIL_{size}")
            )
            self.assertIn("COBALT. AMBER is revoked", value)
            queries = corpus.sequence(expected["queries"])
            self.assertEqual(
                corpus.object_value(queries[-1])["evidence_sections"], [size // 2, size]
            )

    def test_genuine_container_writers_are_deterministic_and_within_unit_limits(
        self,
    ) -> None:
        for size in corpus.SIZES:
            with self.subTest(size=size):
                files, units = corpus.document_files(size)
                again, _ = corpus.document_files(size)
                self.assertEqual(files, again)
                self.assertEqual(set(files), set(corpus.FORMATS))
                self.assertTrue(files["pdf"].startswith(b"%PDF-1.4"))
                self.assertTrue(files["pdf"].rstrip().endswith(b"%%EOF"))
                self.assertLessEqual(units["pdf_pages"], 50)
                self.assertLessEqual(units["pptx_slides"], 100)
                self.assertLessEqual(units["xlsx_sheets"], 32)
                for kind, part in (
                    ("docx", "word/document.xml"),
                    ("xlsx", "xl/workbook.xml"),
                    ("pptx", "ppt/presentation.xml"),
                ):
                    with zipfile.ZipFile(io.BytesIO(files[kind])) as archive:
                        self.assertEqual(archive.testzip(), None)
                        self.assertIn(part, archive.namelist())
                        self.assertIn("[Content_Types].xml", archive.namelist())
                self.assertTrue(all(len(raw) < 32 * 1024**2 for raw in files.values()))

    def test_published_inventory_has_explicit_unqualified_model_fields(self) -> None:
        folder = root()
        published = corpus.publish(folder, (16,))
        self.assertEqual(corpus.verify(folder), published)
        self.assertIs(published["qwen_serving_qualified"], False)
        self.assertIs(published["chunking_or_inference_performed"], False)
        rows = [
            corpus.object_value(value)
            for value in corpus.sequence(published["documents"])
        ]
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(row["qwen_tokens"] is None for row in rows))

    def test_existing_corpus_refuses_without_overwriting_any_bytes(self) -> None:
        folder = root()
        corpus.publish(folder, (16,))
        before = {p.name: p.read_bytes() for p in (folder / "inputs/corpus").iterdir()}
        with self.assertRaisesRegex(ValueError, "Fresh physical corpus"):
            corpus.publish(folder, (16,))
        self.assertEqual(
            before,
            {p.name: p.read_bytes() for p in (folder / "inputs/corpus").iterdir()},
        )

    def test_changed_missing_and_unexpected_files_refuse(self) -> None:
        for change in ("changed", "missing", "extra", "oracle"):
            folder = root()
            corpus.publish(folder, (16,))
            path = folder / "inputs/corpus/orion-016.pdf"
            if change == "changed":
                path.write_bytes(path.read_bytes() + b"tampered")
            elif change == "missing":
                path.unlink()
            elif change == "extra":
                path.with_name("unexpected.txt").write_text("not inventoried")
            else:
                path.with_name("oracles.json").write_text("{}")
            with self.subTest(change=change), self.assertRaises(ValueError):
                corpus.verify(folder)

    def test_model_claims_or_removed_formats_cannot_keep_verify_pass(self) -> None:
        for field, value in (
            ("qwen_serving_qualified", True),
            ("word_counts_are_not_model_tokens", False),
            ("documents", []),
        ):
            folder = root()
            corpus.publish(folder, (16,))
            path = folder / "inputs/corpus/manifest.json"
            manifest = json.loads(path.read_bytes())
            manifest[field] = value
            path.write_bytes(corpus.encode(manifest))
            with self.subTest(field=field), self.assertRaises(ValueError):
                corpus.verify(folder)

    def test_source_change_invalidates_verification(self) -> None:
        folder = root()
        source = folder / "source"
        source.mkdir()
        current = Path(corpus.__file__)
        copied = source / current.name
        copied.write_bytes(current.read_bytes())
        fixture = source / "fixtures.py"
        fixture.write_bytes(current.with_name("fixtures.py").read_bytes())
        with patch.object(corpus, "__file__", str(copied)):
            corpus.publish(folder, (16,))
            self.assertEqual(corpus.verify(folder)["schema"], 1)
            fixture.write_bytes(fixture.read_bytes() + b"\n# changed\n")
            with self.assertRaisesRegex(ValueError, "source binding changed"):
                corpus.verify(folder)

    def test_file_aliases_and_invalid_sizes_refuse(self) -> None:
        for alias in ("symlink", "hardlink"):
            folder = root()
            corpus.publish(folder, (16,))
            path = folder / "inputs/corpus/orion-016.pdf"
            renamed = folder / "physical.pdf"
            path.rename(renamed)
            if alias == "symlink":
                path.symlink_to(renamed)
            else:
                os.link(renamed, path)
            with self.assertRaises(ValueError):
                corpus.verify(folder)
        for sizes in ((), (16, 16), (17,)):
            folder = root()
            with self.assertRaises(ValueError):
                corpus.publish(folder, sizes)
            self.assertFalse((folder / "inputs/corpus").exists())
