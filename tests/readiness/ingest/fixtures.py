"""Deterministic genuine container seeds; extraction/OCR remains A2 proof."""

from __future__ import annotations

import hashlib
import io
import posixpath
import re
import struct
import zipfile
import zlib
from collections.abc import Callable
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

from ingest.manifests import (
    SHA256,
    Refusal,
    canonical,
    digest,
    fields,
    integer,
    read,
    require,
    sequence,
    text,
)
from ingest.paths import physical


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


# These are input generators and structural admission facts, never text readers.
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"


def _relationships(items: list[tuple[str, str, str, bool]]) -> str:
    return (
        f'<Relationships xmlns="{PKG}">'
        + "".join(
            f'<Relationship Id="{escape(key)}" Type="{R}/{kind}" '
            f'Target="{escape(target)}"'
            + (' TargetMode="External"' if external else "")
            + "/>"
            for key, kind, target, external in items
        )
        + "</Relationships>"
    )


def _content_types(parts: dict[str, str]) -> str:
    return (
        f'<Types xmlns="{CT}"><Default Extension="rels" '
        'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        + "".join(
            f'<Override PartName="/{name}" ContentType="{kind}"/>'
            for name, kind in sorted(parts.items())
        )
        + "</Types>"
    )


def _paragraph(value: str, heading: bool = False) -> str:
    properties = '<w:pPr><w:pStyle w:val="Heading1"/></w:pPr>' if heading else ""
    return (
        "<w:p>"
        + properties
        + '<w:r><w:t xml:space="preserve">'
        + escape(value)
        + "</w:t></w:r></w:p>"
    )


def _word(body: str, omitted: bool = False) -> bytes:
    if omitted:
        body = body.replace("<w:p>", '<w:p><w:commentRangeStart w:id="0"/>', 1)
        body = body.replace(
            "</w:p>",
            '<w:commentRangeEnd w:id="0"/><w:r>'
            '<w:commentReference w:id="0"/></w:r></w:p>',
            1,
        )
    types = {
        "word/document.xml": "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document.main+xml",
        "word/styles.xml": "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.styles+xml",
    }
    members = {
        "_rels/.rels": _relationships(
            [("root", "officeDocument", "word/document.xml", False)]
        ),
        "word/document.xml": f'<w:document xmlns:w="{W}" xmlns:r="{R}"><w:body>'
        + body
        + (
            '<w:sectPr><w:headerReference w:type="default" r:id="header"/>'
            '<w:footerReference w:type="default" r:id="footer"/></w:sectPr>'
            if omitted
            else "<w:sectPr/>"
        )
        + "</w:body></w:document>",
        "word/styles.xml": f'<w:styles xmlns:w="{W}"><w:style w:type="paragraph" '
        'w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>'
        '<w:style w:type="paragraph" '
        'w:styleId="Heading1"><w:name w:val="heading 1"/></w:style></w:styles>',
    }
    relationships = [("styles", "styles", "styles.xml", False)]
    if omitted:
        for name, tag, marker in [
            ("header", "hdr", "EXCLUDED WORD HEADER"),
            ("footer", "ftr", "EXCLUDED WORD FOOTER"),
        ]:
            members[f"word/{name}.xml"] = (
                f'<w:{tag} xmlns:w="{W}">' + _paragraph(marker) + f"</w:{tag}>"
            )
            types[f"word/{name}.xml"] = (
                f"application/vnd.openxmlformats-officedocument.wordprocessingml.{name}+xml"
            )
            relationships.append((name, name, f"{name}.xml", False))
        members["word/comments.xml"] = (
            f'<w:comments xmlns:w="{W}"><w:comment w:id="0" w:author="Fixture">'
            + _paragraph("EXCLUDED WORD COMMENT")
            + "</w:comment></w:comments>"
        )
        types["word/comments.xml"] = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"
        )
        relationships.append(("comments", "comments", "comments.xml", False))
    members["word/_rels/document.xml.rels"] = _relationships(relationships)
    members["[Content_Types].xml"] = _content_types(types)
    return archive(members)


def _table(rows: list[list[str]], merged: bool = False) -> str:
    return (
        '<w:tbl><w:tblPr/><w:tblGrid><w:gridCol w:w="3500"/>'
        '<w:gridCol w:w="3500"/></w:tblGrid>'
        + "".join(
            "<w:tr>"
            + "".join(
                "<w:tc><w:tcPr>"
                + (
                    '<w:gridSpan w:val="2"/>'
                    if merged and row_index == 0 and index == 0
                    else ""
                )
                + "</w:tcPr>"
                + _paragraph(value)
                + "</w:tc>"
                for index, value in enumerate(row)
            )
            + "</w:tr>"
            for row_index, row in enumerate(rows)
        )
        + "</w:tbl>"
    )


def _cell(ref: str, value: str, kind: str = "inlineStr", formula: str = "") -> str:
    content = (
        "<is><t>" + escape(value) + "</t></is>"
        if kind == "inlineStr"
        else ("<v>" + escape(value) + "</v>" if value else "")
    )
    return (
        f'<c r="{ref}" t="{kind}"'
        + (' s="1"' if kind == "n" and ref == "D2" else "")
        + ">"
        + ("<f>" + escape(formula) + "</f>" if formula else "")
        + content
        + "</c>"
    )


def _sheet(
    rows: str,
    hidden_row: bool = False,
    hidden_column: bool = False,
    merged: bool = False,
) -> str:
    return (
        f'<worksheet xmlns="{S}">'
        + ('<cols><col min="2" max="2" hidden="1"/></cols>' if hidden_column else "")
        + '<sheetData><row r="1">'
        + _cell("A1", "READINESS HEADER")
        + '</row><row r="2"'
        + (' hidden="1"' if hidden_row else "")
        + ">"
        + rows
        + "</row></sheetData>"
        + (
            '<mergeCells count="1"><mergeCell ref="A2:B2"/></mergeCells>'
            if merged
            else ""
        )
        + "</worksheet>"
    )


def _workbook(sheets: list[tuple[str, str, str]]) -> bytes:
    types = {
        "xl/workbook.xml": "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet.main+xml",
        "xl/styles.xml": "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.styles+xml",
    }
    members = {
        "_rels/.rels": _relationships(
            [("root", "officeDocument", "xl/workbook.xml", False)]
        ),
        "xl/workbook.xml": f'<workbook xmlns="{S}" xmlns:r="{R}"><sheets>'
        + "".join(
            f'<sheet name="{escape(name)}" sheetId="{i}" state="{state}" r:id="r{i}"/>'
            for i, (name, state, _) in enumerate(sheets, 1)
        )
        + "</sheets></workbook>",
        "xl/_rels/workbook.xml.rels": _relationships(
            [
                (f"r{i}", "worksheet", f"worksheets/sheet{i}.xml", False)
                for i in range(1, len(sheets) + 1)
            ]
            + [("styles", "styles", "styles.xml", False)]
        ),
        "xl/styles.xml": f'<styleSheet xmlns="{S}"><fonts count="1"><font>'
        '<sz val="11"/><name val="Calibri"/></font></fonts><fills count="2">'
        '<fill><patternFill/></fill><fill><patternFill patternType="gray125"/></fill>'
        '</fills><borders count="1"><border><left/><right/><top/><bottom/>'
        '<diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" '
        'fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2">'
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
        '<xf numFmtId="14" fontId="0" fillId="0" borderId="0" xfId="0" '
        'applyNumberFormat="1"/></cellXfs><cellStyles count="1"><cellStyle '
        'name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>',
    }
    for i, (_, _, body) in enumerate(sheets, 1):
        name = f"xl/worksheets/sheet{i}.xml"
        members[name] = body
        types[name] = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"
        )
    members["[Content_Types].xml"] = _content_types(types)
    return archive(members)


def _shape(
    value: str, ident: int = 2, notes: bool = False, hidden: bool = False
) -> str:
    return (
        f'<p:sp><p:nvSpPr><p:cNvPr id="{ident}" name="Fixture text {ident}"'
        + (' hidden="1"' if hidden else "")
        + "/>"
        "<p:cNvSpPr/>"
        + ('<p:nvPr><p:ph type="body" idx="1"/></p:nvPr>' if notes else "<p:nvPr/>")
        + "</p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/>"
        "<a:lstStyle/><a:p><a:r><a:t>"
        + escape(value)
        + "</a:t></a:r></a:p></p:txBody></p:sp>"
    )


def _slide(body: str, hidden: bool = False) -> str:
    return (
        f'<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"'
        + (' show="0"' if hidden else "")
        + "><p:cSld><p:spTree>"
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/>'
        "</p:nvGrpSpPr><p:grpSpPr/>" + body + "</p:spTree></p:cSld></p:sld>"
    )


def _deck(
    slides: list[str],
    notes: bool = False,
    comments: bool = False,
    external: bool = False,
) -> bytes:
    types = {
        "ppt/presentation.xml": "application/vnd.openxmlformats-officedocument."
        "presentationml.presentation.main+xml"
    }
    members = {
        "_rels/.rels": _relationships(
            [("root", "officeDocument", "ppt/presentation.xml", False)]
        ),
        "ppt/presentation.xml": f'<p:presentation xmlns:p="{P}" xmlns:r="{R}">'
        "<p:sldIdLst>"
        + "".join(
            f'<p:sldId id="{255 + i}" r:id="r{i}"/>' for i in range(1, len(slides) + 1)
        )
        + '</p:sldIdLst><p:sldSz cx="9144000" cy="6858000"/>'
        '<p:notesSz cx="6858000" cy="9144000"/></p:presentation>',
        "ppt/_rels/presentation.xml.rels": _relationships(
            [
                (f"r{i}", "slide", f"slides/slide{i}.xml", False)
                for i in range(1, len(slides) + 1)
            ]
            + (
                [("authors", "commentAuthors", "commentAuthors.xml", False)]
                if comments
                else []
            )
        ),
    }
    for i, body in enumerate(slides, 1):
        name = f"ppt/slides/slide{i}.xml"
        members[name] = body
        types[name] = (
            "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
        )
    extra: list[tuple[str, str, str, bool]] = []
    if notes:
        members["ppt/notesSlides/notesSlide1.xml"] = (
            f'<p:notes xmlns:p="{P}" xmlns:a="{A}"><p:cSld><p:spTree>'
            '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/>'
            "</p:nvGrpSpPr><p:grpSpPr/>"
            + _shape("SEPARATE SPEAKER NOTES", notes=True)
            + "</p:spTree></p:cSld></p:notes>"
        )
        types["ppt/notesSlides/notesSlide1.xml"] = (
            "application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"
        )
        extra.append(("notes", "notesSlide", "../notesSlides/notesSlide1.xml", False))
        members["ppt/notesSlides/_rels/notesSlide1.xml.rels"] = _relationships(
            [("slide", "slide", "../slides/slide1.xml", False)]
        )
    if comments:
        members["ppt/commentAuthors.xml"] = (
            f'<p:cmAuthorLst xmlns:p="{P}"><p:cmAuthor id="0" name="Fixture" '
            'initials="F" lastIdx="1" clrIdx="0"/></p:cmAuthorLst>'
        )
        types["ppt/commentAuthors.xml"] = (
            "application/vnd.openxmlformats-officedocument.presentationml.commentAuthors+xml"
        )
        members["ppt/comments/comment1.xml"] = (
            f'<p:cmLst xmlns:p="{P}"><p:cm authorId="0" idx="1" '
            'dt="2020-01-01T00:00:00"><p:pos x="0" y="0"/>'
            "<p:text>EXCLUDED SLIDE COMMENT</p:text></p:cm></p:cmLst>"
        )
        types["ppt/comments/comment1.xml"] = (
            "application/vnd.openxmlformats-officedocument.presentationml.comments+xml"
        )
        extra.append(("comments", "comments", "../comments/comment1.xml", False))
    if external:
        members["ppt/slides/slide1.xml"] = members["ppt/slides/slide1.xml"].replace(
            "</p:spTree>",
            '<p:pic><p:nvPicPr><p:cNvPr id="4" name="Linked image"/>'
            "<p:cNvPicPr/><p:nvPr/></p:nvPicPr><p:blipFill>"
            '<a:blip r:link="external"/><a:stretch><a:fillRect/></a:stretch>'
            '</p:blipFill><p:spPr><a:xfrm><a:off x="0" y="0"/>'
            '<a:ext cx="1000000" cy="1000000"/></a:xfrm></p:spPr></p:pic>'
            "</p:spTree>",
        )
        extra.append(
            ("external", "image", "https://fixture.invalid/never-fetch.png", True)
        )
    if extra:
        members["ppt/slides/_rels/slide1.xml.rels"] = _relationships(extra)
    members["[Content_Types].xml"] = _content_types(types)
    return archive(members)


def _rc4(key: bytes, data: bytes) -> bytes:
    """Test-fixture PDF Standard Security revision2; no security-use API."""
    permutation = list(range(256))
    cursor = 0
    for i in range(256):
        cursor = (cursor + permutation[i] + key[i % len(key)]) % 256
        permutation[i], permutation[cursor] = permutation[cursor], permutation[i]
    left = right = 0
    out = bytearray()
    for value in data:
        left = (left + 1) % 256
        right = (right + permutation[left]) % 256
        permutation[left], permutation[right] = permutation[right], permutation[left]
        out.append(value ^ permutation[(permutation[left] + permutation[right]) % 256])
    return bytes(out)


def _pdf_pages(
    streams: list[bytes],
    image: tuple[int, int, bytes] | None = None,
    encrypted: bool = False,
) -> bytes:
    """Original deterministic PDF input writer, not a production document reader."""
    bodies: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    image_id = 4 if image else 0
    if image:
        width, height, pixels = image
        compressed = zlib.compress(pixels)
        bodies.append(
            f"<< /Type /XObject /Subtype /Image /Width {width} /Height {height} "
            "/ColorSpace /DeviceGray /BitsPerComponent 8 /Filter /FlateDecode "
            f"/Length {len(compressed)} >>\nstream\n".encode()
            + compressed
            + b"\nendstream"
        )
    padding = bytes.fromhex(
        "28bf4e5e4e758a4164004e56fffa01082e2e00b6d0683e802f0ca9fe6453697a"
    )
    file_id = hashlib.md5(b"INGEST ORIGINAL SYNTHETIC PDF FIXTURE").digest()
    user = (b"fixture-password" + padding)[:32]
    owner = _rc4(hashlib.md5((b"fixture-owner" + padding)[:32]).digest()[:5], user)
    file_key = hashlib.md5(user + owner + struct.pack("<i", -4) + file_id).digest()[:5]
    kids: list[int] = []
    for stream in streams:
        page_id = len(bodies) + 1
        content_id = page_id + 1
        kids.append(page_id)
        resources = b"/Font << /F1 3 0 R >>"
        if image_id:
            resources += f" /XObject << /Im0 {image_id} 0 R >>".encode()
        bodies.append(
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << "
            + resources
            + f" >> /Contents {content_id} 0 R >>".encode()
        )
        if encrypted:
            object_key = hashlib.md5(
                file_key + content_id.to_bytes(3, "little") + b"\0\0"
            ).digest()[:10]
            stream = _rc4(object_key, stream)
        bodies.append(
            f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream"
        )
    bodies[1] = (
        f"<< /Type /Pages /Count {len(kids)} /Kids [".encode()
        + b" ".join(f"{i} 0 R".encode() for i in kids)
        + b"] >>"
    )
    encryption_id = 0
    if encrypted:
        require(image is None, "Encrypted image fixture not defined")
        encryption_id = len(bodies) + 1
        bodies.append(
            b"<< /Filter /Standard /V 1 /R 2 /Length 40 /P -4 /O <"
            + owner.hex().encode()
            + b"> /U <"
            + _rc4(file_key, padding).hex().encode()
            + b"> >>"
        )
    raw = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, body in enumerate(bodies, 1):
        offsets.append(len(raw))
        raw.extend(f"{i} 0 obj\n".encode() + body + b"\nendobj\n")
    start = len(raw)
    raw.extend(f"xref\n0 {len(bodies) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        raw.extend(f"{offset:010} 00000 n \n".encode())
    raw.extend(f"trailer\n<< /Size {len(bodies) + 1} /Root 1 0 R".encode())
    if encrypted:
        raw.extend(
            f" /Encrypt {encryption_id} 0 R /ID [<{file_id.hex()}> <{file_id.hex()}>]".encode()
        )
    raw.extend(f" >>\nstartxref\n{start}\n%%EOF\n".encode())
    return bytes(raw)


def _text_stream(lines: list[str]) -> bytes:
    require(
        all(line.isascii() and not set("()\\") & set(line) for line in lines),
        "PDF literal unsupported",
    )
    return (
        "BT /F1 14 Tf 50 740 Td "
        + " ".join(
            ("0 -24 Td " if i else "") + "(" + line + ") Tj"
            for i, line in enumerate(lines)
        )
        + " ET"
    ).encode()


def _scan(blank: bool = False) -> tuple[int, int, bytes]:
    # Original 5x7 raster glyphs; image-only PDF contains no searchable text.
    glyphs = {
        "A": "01110 10001 10001 11111 10001 10001 10001",
        "C": "01111 10000 10000 10000 10000 10000 01111",
        "D": "11110 10001 10001 10001 10001 10001 11110",
        "E": "11111 10000 10000 11110 10000 10000 11111",
        "F": "11111 10000 10000 11110 10000 10000 10000",
        "G": "01111 10000 10000 10111 10001 10001 01111",
        "I": "11111 00100 00100 00100 00100 00100 11111",
        "N": "10001 11001 10101 10011 10001 10001 10001",
        "P": "11110 10001 10001 11110 10000 10000 10000",
        "R": "11110 10001 10001 11110 10100 10010 10001",
        "S": "01111 10000 10000 01110 00001 00001 11110",
        "V": "10001 10001 10001 10001 10001 01010 00100",
        " ": "00000 00000 00000 00000 00000 00000 00000",
    }
    phrase = "SCANNED PAGE VERIFIED"
    scale = 6
    width, height = (len(phrase) * 6 + 8) * scale, 23 * scale
    pixels = bytearray(b"\xff" * (width * height))
    if not blank:
        for index, char in enumerate(phrase):
            for y, row in enumerate(glyphs[char].split()):
                for x, bit in enumerate(row):
                    if bit == "1":
                        for yy in range(scale):
                            start = ((y + 8) * scale + yy) * width + (
                                index * 6 + x + 4
                            ) * scale
                            pixels[start : start + scale] = b"\0" * scale
    return width, height, bytes(pixels)


def matrix_bytes() -> dict[str, bytes]:
    """Thirty genuine format candidates; real-reader acceptance stays unqualified."""
    table_stream = (
        b"50 680 m 500 680 l 500 600 l 50 600 l h S "
        b"50 640 m 500 640 l S 270 680 m 270 600 l S "
        b"BT /F1 14 Tf 65 655 Td (PDF TABLE HEADER) Tj "
        b"0 -40 Td (PDF TABLE VALUE ZERO 0) Tj ET"
    )
    result = {
        "pdf-native.pdf": _pdf_pages(
            [_text_stream(["PDF FIRST MARKER", "PDF LATE MARKER"])]
        ),
        "pdf-pages.pdf": _pdf_pages(
            [_text_stream([f"PDF PAGE {i} DISTINCTIVE"]) for i in range(1, 4)]
        ),
        "pdf-table.pdf": _pdf_pages([table_stream]),
        "pdf-scanned.pdf": _pdf_pages([b"q 500 0 0 100 50 600 cm /Im0 Do Q"], _scan()),
        "pdf-blank-image.pdf": _pdf_pages(
            [b"q 500 0 0 100 50 600 cm /Im0 Do Q"], _scan(True)
        ),
        "pdf-encrypted.pdf": _pdf_pages(
            [_text_stream(["ENCRYPTED PRIVATE FIXTURE"])], encrypted=True
        ),
        "docx-body.docx": _word(
            _paragraph("WORD HEADING", True)
            + _paragraph("WORD BEFORE")
            + _table([["WORD TABLE HEADER", "WORD TABLE VALUE"]])
            + _paragraph("WORD AFTER")
        ),
        "docx-unicode.docx": _word(_paragraph("WORD café 東京 Ω – 0007")),
        "docx-parts.docx": _word(_paragraph("WORD INCLUDED BODY"), True),
        "docx-merged.docx": _word(
            _table([["WORD MERGED"], ["WORD LEFT", "WORD RIGHT"]], True)
        ),
        "docx-long.docx": _word(
            "".join(
                _paragraph(f"WORD PARAGRAPH {i} " + "measured candidate content " * 25)
                for i in range(40)
            )
        ),
        "docx-empty.docx": _word(_paragraph("   ")),
        "xlsx-values.xlsx": _workbook(
            [
                (
                    "Values",
                    "visible",
                    _sheet(_cell("A2", "XLSX INCLUDED") + _cell("B2", "0", "n")),
                )
            ]
        ),
        "xlsx-order.xlsx": _workbook(
            [
                ("SecondByName", "visible", _sheet(_cell("A2", "WORKBOOK FIRST"))),
                ("FirstByName", "visible", _sheet(_cell("A2", "WORKBOOK SECOND"))),
            ]
        ),
        "xlsx-hidden-sheet.xlsx": _workbook(
            [
                ("Visible", "visible", _sheet(_cell("A2", "VISIBLE SHEET"))),
                ("Hidden", "hidden", _sheet(_cell("A2", "EXCLUDED HIDDEN SHEET"))),
            ]
        ),
        "xlsx-hidden-row.xlsx": _workbook(
            [
                (
                    "Rows",
                    "visible",
                    _sheet(_cell("A2", "EXCLUDED HIDDEN ROW"), hidden_row=True),
                )
            ]
        ),
        "xlsx-hidden-column.xlsx": _workbook(
            [
                (
                    "Columns",
                    "visible",
                    _sheet(
                        _cell("A2", "VISIBLE CELL")
                        + _cell("B2", "EXCLUDED HIDDEN COLUMN"),
                        hidden_column=True,
                    ),
                )
            ]
        ),
        "xlsx-merged.xlsx": _workbook(
            [
                (
                    "Merged",
                    "visible",
                    _sheet(_cell("A2", "MERGED ONE VALUE"), merged=True),
                )
            ]
        ),
        "xlsx-types.xlsx": _workbook(
            [
                (
                    "Types",
                    "visible",
                    _sheet(
                        _cell("A2", "café 東京\nmultiline")
                        + _cell("B2", "0007")
                        + _cell("C2", "0", "b")
                        + _cell("D2", "45292", "n")
                        + _cell("E2", "0", "n")
                    ),
                )
            ]
        ),
        "xlsx-formula-valid.xlsx": _workbook(
            [("Formula", "visible", _sheet(_cell("A2", "5", "n", "2+3")))]
        ),
        "xlsx-formula-missing.xlsx": _workbook(
            [("Formula", "visible", _sheet(_cell("A2", "", "n", "2+3")))]
        ),
        "xlsx-formula-error.xlsx": _workbook(
            [("Formula", "visible", _sheet(_cell("A2", "#DIV/0!", "e", "1/0")))]
        ),
        "pptx-order.pptx": _deck(
            [_slide(_shape("SLIDE FIRST")), _slide(_shape("SLIDE SECOND"))]
        ),
        "pptx-notes.pptx": _deck([_slide(_shape("SLIDE BODY"))], notes=True),
        "pptx-hidden.pptx": _deck(
            [
                _slide(
                    _shape("SLIDE VISIBLE")
                    + _shape("EXCLUDED HIDDEN SHAPE", 3, hidden=True)
                ),
                _slide(_shape("EXCLUDED HIDDEN SLIDE"), True),
            ]
        ),
        "pptx-table.pptx": _deck(
            [
                _slide(
                    '<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="3" name="Table"/>'
                    "<p:cNvGraphicFramePr/><p:nvPr/></p:nvGraphicFramePr><p:xfrm>"
                    '<a:off x="0" y="0"/><a:ext cx="4000000" cy="1000000"/></p:xfrm>'
                    '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">'
                    '<a:tbl><a:tblPr/><a:tblGrid><a:gridCol w="2000000"/><a:gridCol w="2000000"/>'
                    '</a:tblGrid><a:tr h="300000">'
                    + "".join(
                        "<a:tc><a:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t>"
                        + value
                        + "</a:t></a:r></a:p></a:txBody><a:tcPr/></a:tc>"
                        for value in ["SLIDE TABLE HEADER", "SLIDE TABLE VALUE"]
                    )
                    + "</a:tr></a:tbl></a:graphicData></a:graphic></p:graphicFrame>"
                )
            ]
        ),
        "pptx-comments.pptx": _deck(
            [_slide(_shape("SLIDE INCLUDED BODY"))], comments=True
        ),
        "pptx-external.pptx": _deck(
            [_slide(_shape("SLIDE LOCAL BODY"))], external=True
        ),
        "pptx-unicode-long.pptx": _deck(
            [
                _slide(
                    _shape(
                        "SLIDE café 東京 Ω "
                        + "chunk budget content " * 600
                        + "SLIDE LATE TOKEN MARKER"
                    )
                )
            ]
        ),
        "pptx-empty.pptx": _deck([_slide("")]),
    }
    require(len(result) == 30, "Fixture inventory drift")
    return result


def _xml_part(source: zipfile.ZipFile, name: str) -> ET.Element:
    try:
        require(
            source.getinfo(name).file_size <= 4 * 1024 * 1024, "XML part exceeds limit"
        )
        with source.open(name) as stream:
            raw = stream.read(4 * 1024 * 1024 + 1)
    except KeyError as exc:
        raise Refusal("Required Office part missing") from exc
    require(len(raw) <= 4 * 1024 * 1024, "XML part exceeds limit")
    try:
        encoding = "utf-8-sig"
        if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
            encoding = "utf-16"
        elif raw.startswith(b"<\0"):
            encoding = "utf-16-le"
        elif raw.startswith(b"\0<"):
            encoding = "utf-16-be"
        decoded = raw.decode(encoding)
        require(
            "<!doctype" not in decoded.lower() and "<!entity" not in decoded.lower(),
            "XML declarations refused",
        )
        return ET.fromstring(decoded)
    except (UnicodeError, ET.ParseError) as exc:
        raise Refusal("Malformed Office XML") from exc


def _coordinate(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"([A-Z]{1,3})([1-9][0-9]{0,6})", value)
    require(match is not None, "Unsupported cell coordinate")
    if match is None:
        raise Refusal("Unsupported cell coordinate")
    column = 0
    for character in match[1]:
        column = column * 26 + ord(character) - ord("A") + 1
    row = int(match[2])
    require(column <= 16384 and row <= 20000, "Worksheet coordinate limit")
    return row, column


def _boolean(value: str) -> bool:
    require(value in {"0", "1", "false", "true"}, "Unclassified Office boolean")
    return value in {"1", "true"}


def audit_office(raw: bytes, kind: str) -> dict[str, object]:
    """Only bounded structural/selection facts; never returns extracted document text."""
    require(kind in {"docx", "xlsx", "pptx"}, "Office format not admitted")
    require(len(raw) <= 32 * 1024 * 1024, "Compressed input exceeds limit")
    validate_archive(raw, 2048, 128 * 1024 * 1024)
    with zipfile.ZipFile(io.BytesIO(raw)) as source:
        names = set(source.namelist())
        roots = {
            "docx": "word/document.xml",
            "xlsx": "xl/workbook.xml",
            "pptx": "ppt/presentation.xml",
        }
        require(
            roots[kind] in names and sum(item in names for item in roots.values()) == 1,
            "Format mismatch/ambiguous Office package",
        )
        types = _xml_part(source, "[Content_Types].xml")
        require(types.tag == f"{{{CT}}}Types", "Invalid package content types")
        expected_types = {
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml",
            "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml",
        }
        declarations = [
            item.get("ContentType")
            for item in types
            if item.tag == f"{{{CT}}}Override"
            and item.get("PartName") == "/" + roots[kind]
        ]
        require(
            declarations == [expected_types[kind]], "Main part content-type mismatch"
        )
        package_roots = [
            relation
            for relation in _xml_part(source, "_rels/.rels")
            if relation.get("Type") == R + "/officeDocument"
        ]
        require(
            len(package_roots) == 1
            and package_roots[0].get("Target") == roots[kind]
            and package_roots[0].get("TargetMode", "Internal") == "Internal",
            "Package root relationship mismatch",
        )
        reasons: list[str] = []
        external = 0
        for name in sorted(names):
            if name.endswith(".rels"):
                for relation in _xml_part(source, name):
                    if relation.get("TargetMode") == "External":
                        external += 1
        if external:
            reasons.append("external_relationship_requires_no_fetch")
        facts: dict[str, object] = {
            "format": kind,
            "archive_members": len(names),
            "external_relationships": external,
        }
        if kind == "docx":
            body = _xml_part(source, roots[kind]).find(f"{{{W}}}body")
            require(body is not None, "Missing Word body")
            if body is None:
                raise ValueError("Missing body")
            facts["body_order"] = [node.tag.rsplit("}", 1)[-1] for node in body]
            facts["omitted_parts"] = sorted(
                name
                for name in names
                if name.startswith(("word/header", "word/footer", "word/comments"))
            )
        else:
            prefix, root_ns, list_name, item_name, rel_name = (
                ("xl", S, "sheets", "sheet", "workbook")
                if kind == "xlsx"
                else ("ppt", P, "sldIdLst", "sldId", "presentation")
            )
            root = _xml_part(source, roots[kind])
            units = root.find(f"{{{root_ns}}}{list_name}")
            require(units is not None, "Missing ordered source units")
            if units is None:
                raise ValueError("Missing units")
            require(len(units) <= (32 if kind == "xlsx" else 100), "Source unit limit")
            links: dict[str, str] = {}
            relation_ids: set[str] = set()
            relation_kind = "worksheet" if kind == "xlsx" else "slide"
            for item in _xml_part(source, f"{prefix}/_rels/{rel_name}.xml.rels"):
                key = item.get("Id", "")
                require(
                    bool(key) and key not in relation_ids,
                    "Missing/duplicate source relationship",
                )
                relation_ids.add(key)
                if item.get("Type") == R + "/" + relation_kind:
                    require(
                        item.get("TargetMode", "Internal") == "Internal",
                        "External source unit refused",
                    )
                    links[key] = item.get("Target", "")
            order: list[dict[str, object]] = []
            formula_missing: list[str] = []
            formula_error: list[str] = []
            cells = shapes = merged_cells = 0
            for index, unit in enumerate(units, 1):
                target = links.get(unit.get(f"{{{R}}}id", ""))
                require(target is not None, "Source unit relationship missing")
                if target is None:
                    raise ValueError("Missing relationship")
                part = posixpath.normpath(posixpath.join(prefix, target))
                require(
                    part.startswith(prefix + "/") and part in names,
                    "Source part escape/missing",
                )
                xml = _xml_part(source, part)
                if kind == "xlsx":
                    hidden_rows = [
                        integer(int(row.get("r", "0")), 1)
                        for row in xml.findall(f".//{{{S}}}row")
                        if _boolean(row.get("hidden", "false"))
                    ]
                    rows = xml.findall(f".//{{{S}}}row")
                    require(
                        all(1 <= int(row.get("r", "0")) <= 20000 for row in rows),
                        "Worksheet row limit",
                    )
                    column_spans = [
                        (int(column.get("min", "0")), int(column.get("max", "0")))
                        for column in xml.findall(f".//{{{S}}}col")
                        if _boolean(column.get("hidden", "false"))
                    ]
                    require(
                        all(
                            1 <= first <= last <= 16384 for first, last in column_spans
                        ),
                        "Invalid hidden column span",
                    )
                    hidden_columns = [f"{first}:{last}" for first, last in column_spans]
                    these_cells = xml.findall(f".//{{{S}}}c")
                    cells += len(these_cells)
                    require(cells <= 250000, "Worksheet cell limit")
                    state = unit.get("state", "visible")
                    require(
                        state in {"visible", "hidden", "veryHidden"},
                        "Unclassified sheet state",
                    )
                    hidden_sheet = state != "visible"
                    for cell in these_cells:
                        row, column = _coordinate(cell.get("r", ""))
                        included = (
                            not hidden_sheet
                            and row not in hidden_rows
                            and not any(
                                first <= column <= last for first, last in column_spans
                            )
                        )
                        formula = cell.find(f"{{{S}}}f")
                        if formula is not None and included:
                            cache = cell.find(f"{{{S}}}v")
                            ref = f"{index}:{cell.get('r', '?')}"
                            if (
                                cache is None
                                or cache.text is None
                                or not cache.text.strip()
                            ):
                                formula_missing.append(ref)
                            elif cell.get("t") == "e":
                                formula_error.append(ref)
                    merged_ranges = [
                        m.get("ref", "") for m in xml.findall(f".//{{{S}}}mergeCell")
                    ]
                    for merged in merged_ranges:
                        bounds = merged.split(":")
                        require(len(bounds) in {1, 2}, "Unsupported merged range")
                        first, last = _coordinate(bounds[0]), _coordinate(bounds[-1])
                        require(
                            first[0] <= last[0] and first[1] <= last[1],
                            "Reversed merged range",
                        )
                        merged_cells += (last[0] - first[0] + 1) * (
                            last[1] - first[1] + 1
                        )
                        require(merged_cells <= 250000, "Merged expansion cell limit")
                    order.append(
                        {
                            "index": index,
                            "name": unit.get("name", ""),
                            "part": part,
                            "hidden": hidden_sheet,
                            "hidden_rows": hidden_rows,
                            "hidden_columns": hidden_columns,
                            "cells": len(these_cells),
                            "merged_ranges": merged_ranges,
                        }
                    )
                else:
                    these_shapes = [
                        node
                        for tag in (
                            "sp",
                            "graphicFrame",
                            "pic",
                            "grpSp",
                            "cxnSp",
                            "contentPart",
                        )
                        for node in xml.findall(f".//{{{P}}}{tag}")
                    ]
                    shapes += len(these_shapes)
                    require(shapes <= 5000, "Presentation shape limit")
                    order.append(
                        {
                            "index": index,
                            "part": part,
                            "hidden": not _boolean(xml.get("show", "true")),
                            "shapes": len(these_shapes),
                            "hidden_shapes": [
                                node.get("id", "")
                                for node in xml.findall(f".//{{{P}}}cNvPr")
                                if _boolean(node.get("hidden", "false"))
                            ],
                        }
                    )
            facts["units"] = order
            if kind == "xlsx":
                facts["cells"] = cells
                facts["missing_formula_caches"] = formula_missing
                facts["error_formula_caches"] = formula_error
                if formula_missing:
                    reasons.append("included_formula_cache_missing")
                if formula_error:
                    reasons.append("included_formula_cache_error")
            else:
                facts["shapes"] = shapes
                facts["note_parts"] = sum(
                    name.startswith("ppt/notesSlides/notesSlide")
                    and name.endswith(".xml")
                    for name in names
                )
                facts["comment_parts"] = sum(
                    name.startswith("ppt/comments/") and name.endswith(".xml")
                    for name in names
                )
        facts["refusal_codes"] = reasons
        facts["text_extracted"] = False
        return facts


def publish_matrix(
    destination: Path,
    expectations: dict[str, object],
    before_write: Callable[[], None] | None = None,
) -> dict[str, object]:
    """Publish new input bytes/oracles; this performs no conversion qualification."""
    require(
        physical(destination) == destination and not destination.exists(),
        "New physical fixture destination required",
    )
    expected = fields(expectations, {"schema", "cases"})
    require(
        type(expected["schema"]) is int and expected["schema"] == 1,
        "Fixture oracle schema",
    )
    cases = sequence(expected["cases"])
    inventory = matrix_bytes()
    require(len(cases) == 30, "Independent oracle count")
    names: list[str] = []
    for value in cases:
        row = fields(
            value, {"file", "format", "contains", "excludes", "units", "outcome"}
        )
        name = text(row["file"])
        names.append(name)
        require(
            name in inventory and name.rsplit(".", 1)[-1] == row["format"],
            "Oracle file/format mismatch",
        )
        integer(row["units"])
        require(
            text(row["outcome"]) in {"extract", "refuse", "characterize"},
            "Unknown fixture outcome",
        )
        for key in ("contains", "excludes"):
            require(
                all(isinstance(item, str) for item in sequence(row[key])),
                "Oracle markers must be text",
            )
    require(
        len(set(names)) == 30 and set(names) == set(inventory),
        "Oracle/fixture selection mismatch",
    )
    if before_write:
        before_write()
    destination.mkdir(mode=0o700)
    records: list[dict[str, object]] = []
    for name, raw in sorted(inventory.items()):
        if before_write:
            before_write()
        target = destination / name
        with target.open("xb") as stream:
            stream.write(raw)
        target.chmod(0o444)
        records.append({"file": name, "sha256": digest(raw), "bytes": len(raw)})
    oracle_raw = canonical(expected)
    if before_write:
        before_write()
    with (destination / "oracles.json").open("xb") as stream:
        stream.write(oracle_raw)
    (destination / "oracles.json").chmod(0o444)
    result: dict[str, object] = {
        "schema": 1,
        "fixture_count": len(records),
        "files": records,
        "oracles_sha256": digest(oracle_raw),
        "converter_qualified": False,
        "claim": "Deterministic input publication and structural checks only; A2 conversion/OCR acceptance pending",
    }
    if before_write:
        before_write()
    with (destination / "manifest.json").open("xb") as stream:
        stream.write(canonical(result))
    (destination / "manifest.json").chmod(0o444)
    return result


def verify_matrix(destination: Path, expected_manifest: str) -> list[Path]:
    require(physical(destination) == destination, "Fixture directory alias")
    result = fields(
        read(destination / "manifest.json", expected_manifest),
        {
            "schema",
            "fixture_count",
            "files",
            "oracles_sha256",
            "converter_qualified",
            "claim",
        },
    )
    require(
        type(result["schema"]) is int
        and result["schema"] == 1
        and type(result["fixture_count"]) is int
        and result["fixture_count"] == 30
        and result["converter_qualified"] is False,
        "Unqualified input manifest schema",
    )
    rows = sequence(result["files"])
    require(len(rows) == 30, "Fixture count mismatch")
    selected: list[tuple[Path, str, int]] = []
    names: set[str] = set()
    counts = dict.fromkeys(["pdf", "docx", "xlsx", "pptx"], 0)
    for value in rows:
        row = fields(value, {"file", "sha256", "bytes"})
        name = text(row["file"])
        require(
            name == Path(name).name and not name.startswith(".") and "\\" not in name,
            "Fixture basename refused",
        )
        extension = name.rsplit(".", 1)[-1]
        require(extension in counts and name not in names, "Fixture format/duplicate")
        names.add(name)
        counts[extension] += 1
        target = destination / name
        require(physical(target) == target and target.is_file(), "Fixture path/type")
        expected = text(row["sha256"])
        require(bool(SHA256.fullmatch(expected)), "Fixture digest")
        size = integer(row["bytes"], 1)
        require(
            size <= 32 * 1024 * 1024 and target.stat().st_size == size, "Fixture size"
        )
        selected.append((target, expected, size))
    require(
        counts == {"pdf": 6, "docx": 6, "xlsx": 10, "pptx": 8}, "Fixture format counts"
    )
    require(
        {item.name for item in destination.iterdir()}
        == names | {"manifest.json", "oracles.json"},
        "Extra fixture artifact",
    )
    read(destination / "oracles.json", text(result["oracles_sha256"]))
    for target, expected, size in selected:
        with target.open("rb") as stream:
            raw = stream.read(size + 1)
        require(len(raw) == size and digest(raw) == expected, "Fixture bytes changed")
    return [target for target, _, _ in selected]
