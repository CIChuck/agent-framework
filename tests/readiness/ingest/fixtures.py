"""Deterministic genuine container seeds; extraction/OCR remains A2 proof."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from ingest.manifests import digest, require


def archive(members: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as target:
        for name, content in sorted(members.items()):
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            target.writestr(info, content.encode())
    return buffer.getvalue()


def validate_archive(raw: bytes, members: int, expanded: int) -> None:
    with zipfile.ZipFile(io.BytesIO(raw)) as source:
        records = source.infolist()
        require(
            len(records) <= members
            and len({item.filename for item in records}) == len(records),
            "Archive count/duplicate refused",
        )
        require(
            sum(item.file_size for item in records) <= expanded,
            "Archive expanded-byte limit",
        )
        for item in records:
            path = Path(item.filename)
            require(
                not path.is_absolute()
                and ".." not in path.parts
                and "\\" not in item.filename,
                "Archive path escape",
            )
            require(
                (item.external_attr >> 16) & 0o170000 != 0o120000, "Archive symlink"
            )


def pdf(text: str) -> bytes:
    require(
        text.isascii() and "(" not in text and ")" not in text and "\\" not in text,
        "PDF seed text is not safe literal ASCII",
    )
    stream = ("BT /F1 12 Tf 72 720 Td (" + text + ") Tj ET\n").encode()
    bodies = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length "
        + str(len(stream)).encode()
        + b" >>\nstream\n"
        + stream
        + b"endstream",
    ]
    result = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, body in enumerate(bodies, 1):
        offsets.append(len(result))
        result.extend(str(index).encode() + b" 0 obj\n" + body + b"\nendobj\n")
    start = len(result)
    result.extend(b"xref\n0 6\n0000000000 65535 f \n")
    for offset in offsets[1:]:
        result.extend(f"{offset:010} 00000 n \n".encode())
    result.extend(
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n"
        + str(start).encode()
        + b"\n%%EOF\n"
    )
    return bytes(result)


def docx(text: str) -> bytes:
    return archive(
        {
            "[Content_Types].xml": '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>',
            "_rels/.rels": '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>',
            "word/document.xml": '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>'
            + escape(text)
            + "</w:t></w:r></w:p><w:sectPr/></w:body></w:document>",
        }
    )


def publish_seeds(destination: Path) -> list[dict[str, object]]:
    """Small C0 seeds, never claimed to satisfy the full thirty-fixture A2 matrix."""
    require(not destination.exists(), "Fixture publication must be new")
    destination.mkdir()
    rows: list[dict[str, object]] = []
    for extension, data in [
        ("pdf", pdf("INGEST-C0-DISTINCTIVE-LATE-TEXT")),
        ("docx", docx("INGEST-C0-DISTINCTIVE-LATE-TEXT")),
    ]:
        path = destination / ("seed." + extension)
        path.write_bytes(data)
        rows.append(
            {
                "file": path.name,
                "sha256": digest(data),
                "scope": "C0 structural seed; no converter qualification",
            }
        )
    return rows
