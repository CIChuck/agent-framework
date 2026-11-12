from __future__ import annotations

import io
import unittest
import xml.etree.ElementTree as ET
import zipfile

from ingest.fixtures import archive, docx, pdf, publish_seeds, validate_archive
from ingest.manifests import Refusal, text
from ingest.tests.test_manifests import unit


class Fixtures(unittest.TestCase):
    def test_pdf_offsets_and_distinctive_source(self) -> None:
        raw = pdf("DISTINCTIVE-SOURCE-TEXT")
        self.assertTrue(raw.startswith(b"%PDF-"))
        start = int(raw.split(b"startxref\n")[1].splitlines()[0])
        self.assertEqual(raw[start : start + 4], b"xref")
        offsets = raw.split(b"xref\n0 6\n")[1].splitlines()[1:6]
        for index, line in enumerate(offsets, 1):
            self.assertTrue(
                raw[int(line[:10]) :].startswith(str(index).encode() + b" 0 obj")
            )
        self.assertIn(b"DISTINCTIVE-SOURCE-TEXT", raw)

    def test_docx_is_real_xml_container_and_deterministic(self) -> None:
        raw = docx("distinct <source> & table")
        self.assertEqual(raw, docx("distinct <source> & table"))
        validate_archive(raw, 2048, 128 * 1024 * 1024)
        with zipfile.ZipFile(io.BytesIO(raw)) as source:
            body = ET.fromstring(source.read("word/document.xml"))
            self.assertIn("distinct <source> & table", "".join(body.itertext()))

    def test_archive_escape_duplicate_and_expansion_refuse(self) -> None:
        for raw, count, size in [
            (archive({"../escape": "x"}), 20, 20),
            (archive({"x": "a" * 1000}), 20, 100),
            (archive({"x": "a", "y": "b"}), 1, 100),
        ]:
            with self.assertRaises(Refusal):
                validate_archive(raw, count, size)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as target:
            target.writestr("duplicate", "one")
            target.writestr("duplicate", "two")
        with self.assertRaises(Refusal):
            validate_archive(buffer.getvalue(), 20, 100)

    def test_c0_seed_publication_does_not_claim_a2_qualification(self) -> None:
        destination = unit() / "seeds"
        rows = publish_seeds(destination)
        self.assertEqual(len(rows), 2)
        self.assertTrue(
            all("no converter qualification" in text(row["scope"]) for row in rows)
        )
        with self.assertRaises(Refusal):
            publish_seeds(destination)
