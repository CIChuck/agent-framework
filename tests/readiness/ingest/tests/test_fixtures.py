from __future__ import annotations

import io
import re
import unittest
import xml.etree.ElementTree as ET
import zipfile
import zlib
from collections import Counter

from ingest.fixtures import (
    _rc4,
    archive,
    audit_office,
    docx,
    matrix_bytes,
    pdf,
    publish_matrix,
    publish_seeds,
    validate_archive,
    verify_matrix,
)
from ingest.manifests import (
    Refusal,
    canonical,
    decode,
    digest,
    object_value,
    require,
    sequence,
    text,
)
from ingest.startup import harness_state
from ingest.tests.test_manifests import unit


def found(pattern: bytes, raw: bytes) -> re.Match[bytes]:
    match = re.search(pattern, raw)
    if match is None:
        raise AssertionError("Required PDF structure missing")
    return match


def element(
    root: ET.Element, path: str, ns: dict[str, str] | None = None
) -> ET.Element:
    result = root.find(path, ns)
    if result is None:
        raise AssertionError("Required Office structure missing: " + path)
    return result


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

    def oracle(self) -> dict[str, object]:
        _, buffers = harness_state()
        return object_value(
            object_value(decode(buffers["fixtures/expectations.json"])["A2"])[
                "fixture_oracles"
            ]
        )

    def test_full_matrix_counts_unique_bytes_and_determinism(self) -> None:
        first = matrix_bytes()
        self.assertEqual(first, matrix_bytes())
        self.assertEqual(
            Counter(name.rsplit(".", 1)[-1] for name in first),
            {"pdf": 6, "docx": 6, "xlsx": 10, "pptx": 8},
        )
        self.assertEqual(len({digest(value) for value in first.values()}), 30)
        self.assertEqual(len(sequence(self.oracle()["cases"])), 30)

    def test_all_pdf_objects_xref_pages_scan_and_encryption(self) -> None:
        examples = matrix_bytes()
        for name, raw in examples.items():
            if not name.endswith(".pdf"):
                continue
            with self.subTest(file=name):
                start = int(raw.rsplit(b"startxref\n", 1)[1].splitlines()[0])
                self.assertEqual(raw[start : start + 4], b"xref")
                lines = raw[start:].splitlines()
                count = int(lines[1].split()[1])
                for index, line in enumerate(lines[3 : count + 2], 1):
                    self.assertTrue(
                        raw[int(line[:10]) :].startswith(f"{index} 0 obj".encode())
                    )
                pages = int(found(rb"/Type /Pages /Count (\d+)", raw)[1])
                self.assertEqual(pages, 3 if name == "pdf-pages.pdf" else 1)
        for name, blank in [("pdf-scanned.pdf", False), ("pdf-blank-image.pdf", True)]:
            raw = examples[name]
            begin = raw.index(b"/Subtype /Image")
            length = int(found(rb"/Length (\d+)", raw[begin:])[1])
            begin = raw.index(b"stream\n", begin) + 7
            pixels = zlib.decompress(raw[begin : begin + length])
            self.assertEqual(set(pixels), {255} if blank else {0, 255})
            self.assertNotIn(b"SCANNED PAGE VERIFIED", raw)
        encrypted = examples["pdf-encrypted.pdf"]
        self.assertIn(b"/Encrypt ", encrypted)
        self.assertIn(b"/Filter /Standard /V 1 /R 2", encrypted)
        self.assertNotIn(b"ENCRYPTED PRIVATE FIXTURE", encrypted)
        # RC4 known vector (RFC 6229, key 0x0102030405, offset 0).
        self.assertEqual(
            _rc4(bytes.fromhex("0102030405"), b"\0" * 16).hex(),
            "b2396305f03dc027ccc3524a0a1118a8",
        )

    def test_office_matrix_has_ordered_structural_facts_without_text(self) -> None:
        examples = matrix_bytes()
        for name, raw in examples.items():
            kind = name.rsplit(".", 1)[-1]
            if kind == "pdf":
                continue
            with self.subTest(file=name):
                facts = audit_office(raw, kind)
                self.assertIs(facts["text_extracted"], False)
                self.assertEqual(facts["format"], kind)
                self.assertNotIn(b"WORD INCLUDED BODY", canonical(facts))
                self.assertNotIn(b"SLIDE INCLUDED BODY", canonical(facts))
                self.assertNotIn(b"XLSX INCLUDED", canonical(facts))
        body = audit_office(examples["docx-body.docx"], "docx")
        self.assertEqual(body["body_order"], ["p", "p", "tbl", "p", "sectPr"])
        parts = audit_office(examples["docx-parts.docx"], "docx")
        self.assertEqual(
            parts["omitted_parts"],
            ["word/comments.xml", "word/footer.xml", "word/header.xml"],
        )
        with zipfile.ZipFile(io.BytesIO(examples["docx-merged.docx"])) as source:
            document = ET.fromstring(source.read("word/document.xml"))
            namespace = {
                "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            }
            self.assertEqual(len(document.findall(".//w:gridSpan", namespace)), 1)

    def test_workbook_visibility_cached_formula_and_value_types(self) -> None:
        examples = matrix_bytes()
        ordered = audit_office(examples["xlsx-order.xlsx"], "xlsx")
        units = [object_value(item) for item in sequence(ordered["units"])]
        self.assertEqual(
            [value["name"] for value in units],
            ["SecondByName", "FirstByName"],
        )
        for name, key, expected in [
            ("xlsx-hidden-sheet.xlsx", "hidden", True),
            ("xlsx-hidden-row.xlsx", "hidden_rows", [2]),
            ("xlsx-hidden-column.xlsx", "hidden_columns", ["2:2"]),
        ]:
            rows = [
                object_value(item)
                for item in sequence(audit_office(examples[name], "xlsx")["units"])
            ]
            index = 1 if name == "xlsx-hidden-sheet.xlsx" else 0
            self.assertEqual(rows[index][key], expected)
        self.assertEqual(
            audit_office(examples["xlsx-formula-valid.xlsx"], "xlsx")["refusal_codes"],
            [],
        )
        self.assertEqual(
            audit_office(examples["xlsx-formula-missing.xlsx"], "xlsx")[
                "missing_formula_caches"
            ],
            ["1:A2"],
        )
        self.assertEqual(
            audit_office(examples["xlsx-formula-error.xlsx"], "xlsx")[
                "error_formula_caches"
            ],
            ["1:A2"],
        )
        with zipfile.ZipFile(io.BytesIO(examples["xlsx-types.xlsx"])) as source:
            sheet = ET.fromstring(source.read("xl/worksheets/sheet1.xml"))
            ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            cells = {item.get("r"): item for item in sheet.findall(".//s:c", ns)}
            self.assertEqual(element(cells["B2"], "s:is/s:t", ns).text, "0007")
            self.assertEqual(cells["C2"].get("t"), "b")
            self.assertEqual(element(cells["C2"], "s:v", ns).text, "0")
            self.assertEqual(cells["D2"].get("s"), "1")
            self.assertEqual(element(cells["E2"], "s:v", ns).text, "0")

    def test_presentation_hidden_notes_comments_and_external_are_distinct(self) -> None:
        examples = matrix_bytes()
        hidden = audit_office(examples["pptx-hidden.pptx"], "pptx")
        self.assertEqual(
            [object_value(row)["hidden"] for row in sequence(hidden["units"])],
            [False, True],
        )
        self.assertEqual(
            object_value(sequence(hidden["units"])[0])["hidden_shapes"], ["3"]
        )
        notes = audit_office(examples["pptx-notes.pptx"], "pptx")
        self.assertEqual((notes["note_parts"], notes["comment_parts"]), (1, 0))
        comments = audit_office(examples["pptx-comments.pptx"], "pptx")
        self.assertEqual((comments["note_parts"], comments["comment_parts"]), (0, 1))
        external = audit_office(examples["pptx-external.pptx"], "pptx")
        self.assertEqual(external["external_relationships"], 1)
        self.assertEqual(
            external["refusal_codes"], ["external_relationship_requires_no_fetch"]
        )
        with zipfile.ZipFile(io.BytesIO(examples["pptx-notes.pptx"])) as source:
            part = ET.fromstring(source.read("ppt/notesSlides/notesSlide1.xml"))
            ph = element(
                part,
                ".//{http://schemas.openxmlformats.org/presentationml/2006/main}ph",
            )
            self.assertEqual(ph.get("type"), "body")

    def test_office_resource_and_xml_declaration_refusals(self) -> None:
        raw = matrix_bytes()["xlsx-formula-missing.xlsx"]
        with zipfile.ZipFile(io.BytesIO(raw)) as source:
            parts = {name: source.read(name).decode() for name in source.namelist()}
        # A missing cache in an excluded row is not an included formula error.
        key = "xl/worksheets/sheet1.xml"
        hidden = parts.copy()
        hidden[key] = hidden[key].replace('<row r="2">', '<row r="2" hidden="1">')
        self.assertEqual(audit_office(archive(hidden), "xlsx")["refusal_codes"], [])
        for changed in [
            parts[key].replace('r="A2"', 'r="A20001"'),
            parts[key].replace('r="A2"', 'r="XFE2"'),
            '<!DOCTYPE worksheet [<!ENTITY x "boom">]>' + parts[key],
        ]:
            bad = parts.copy()
            bad[key] = changed
            with self.assertRaises(Refusal):
                audit_office(archive(bad), "xlsx")
        merged = parts.copy()
        merged[key] = parts[key].replace(
            "</worksheet>",
            '<mergeCells count="1"><mergeCell ref="A2:XFD20000"/>'
            "</mergeCells></worksheet>",
        )
        with self.assertRaisesRegex(Refusal, "expansion"):
            audit_office(archive(merged), "xlsx")
        mismatched = parts.copy()
        mismatched["[Content_Types].xml"] = mismatched["[Content_Types].xml"].replace(
            "spreadsheetml.sheet.main+xml", "presentationml.presentation.main+xml"
        )
        with self.assertRaisesRegex(Refusal, "content-type"):
            audit_office(archive(mismatched), "xlsx")
        invalid_boolean = parts.copy()
        invalid_boolean[key] = parts[key].replace(
            '<row r="2">', '<row r="2" hidden="unknown">'
        )
        with self.assertRaisesRegex(Refusal, "boolean"):
            audit_office(archive(invalid_boolean), "xlsx")
        malicious_utf16 = io.BytesIO()
        with zipfile.ZipFile(malicious_utf16, "w") as target:
            for name, value in parts.items():
                data = (
                    ('<!DOCTYPE worksheet [<!ENTITY x "boom">]>' + value).encode(
                        "utf-16"
                    )
                    if name == key
                    else value.encode()
                )
                target.writestr(name, data)
        with self.assertRaisesRegex(Refusal, "declarations"):
            audit_office(malicious_utf16.getvalue(), "xlsx")
        with self.assertRaises(Refusal):
            audit_office(raw, "pptx")
        # Renamed binary data must not satisfy the format-specific root check.
        with self.assertRaises((Refusal, zipfile.BadZipFile)):
            audit_office(b"not a document", "xlsx")

    def test_matrix_publication_integrity_and_stop_are_not_conversion(self) -> None:
        root = unit()
        destination = root / "matrix"
        manifest = publish_matrix(destination, self.oracle())
        self.assertIs(manifest["converter_qualified"], False)
        self.assertEqual(
            len(verify_matrix(destination, digest(canonical(manifest)))), 30
        )
        with self.assertRaises(Refusal):
            publish_matrix(destination, self.oracle())
        target = destination / "docx-body.docx"
        target.chmod(0o644)
        target.write_bytes(b"changed")
        with self.assertRaises(Refusal):
            verify_matrix(destination, digest(canonical(manifest)))
        other = root / "partial"
        from ingest.tests.test_ledger import ledger

        log = ledger()
        calls = 0

        def stop() -> None:
            nonlocal calls
            calls += 1
            if calls == 4:
                (log.state / "stop.json").write_bytes(canonical({"schema": 1}))
            require(not log.stopped(), "Private stop witness")

        with self.assertRaisesRegex(Refusal, "stop witness"):
            publish_matrix(other, self.oracle(), stop)
        self.assertEqual(len(list(other.iterdir())), 2)
        self.assertFalse((other / "manifest.json").exists())

    def test_incomplete_oracle_rejects_before_publication(self) -> None:
        oracle = self.oracle()
        oracle["cases"] = []
        destination = unit() / "must-stay-absent"
        with self.assertRaises(Refusal):
            publish_matrix(destination, oracle)
        self.assertFalse(destination.exists())
