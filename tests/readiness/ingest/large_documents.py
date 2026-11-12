"""Generate isolated, genuine long documents; no model or ingestion calls."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import io
import json
import os
import sys
import textwrap
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

SIZES = (16, 64, 128, 256, 384)
FORMATS = ("pdf", "docx", "xlsx", "pptx", "txt")
TOPICS = (
    "warehouse scheduling",
    "sensor calibration",
    "water distribution",
    "incident response",
    "equipment maintenance",
    "delivery reconciliation",
    "capacity forecasting",
    "environmental monitoring",
)
ROLES = (
    "planning coordinator",
    "safety reviewer",
    "field technician",
    "shift supervisor",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def object_value(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ValueError("Object with text keys required")
    result: dict[str, object] = dict(value)
    return result


def sequence(value: object) -> list[object]:
    if not isinstance(value, list):
        raise ValueError("Array required")
    return list(value)


def text(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Text required")
    return value


def encode(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def source_binding() -> dict[str, str]:
    result = {}
    for name in ("large_documents.py", "fixtures.py"):
        path = Path(__file__).with_name(name)
        require(
            path.is_file() and path.resolve() == path and path.stat().st_nlink == 1,
            "Corpus source alias/missing",
        )
        result[name] = digest(path.read_bytes())
    return result


@dataclass(frozen=True)
class Section:
    heading: str
    body: str


def sections(size: int) -> tuple[Section, ...]:
    require(type(size) is int and size in SIZES, "Unknown bounded corpus size")
    result = []
    for index in range(1, size + 1):
        topic = TOPICS[(index - 1) % len(TOPICS)]
        role = ROLES[(index // 3) % len(ROLES)]
        body = (
            f"The {role} reviews {topic} for fictional station Orion {index:04d}. "
            f"The inspection interval is {7 + index % 19} days and the reference batch is B{size:03d}-{index:04d}. "
            "Operators compare the observed readings with the signed local ledger before releasing equipment. "
            "A delayed delivery requires a separate exception record, rather than an invented completion date. "
            f"The next team checks ledger entry {max(1, index - 3):04d} and records the reason for each changed assumption. "
            "These procedures describe synthetic test operations and are not instructions for a real facility."
        )
        if index == 1:
            body += f" SOURCE_START_{size}: The pilot zone is NORTH QUAY. The earlier route AMBER is provisional."
        if index == size // 2:
            body += f" SOURCE_MIDDLE_{size}: The calibration key is COMPASS-{size}. Retain it for the final authorization."
        if index == size:
            body += f" SOURCE_TAIL_{size}: The final authorized route is COBALT. AMBER is revoked. Authorization requires COMPASS-{size} and RELEASE-{size + 17}."
        result.append(Section(f"SECTION-{index:04d} {topic.title()}", body))
    return tuple(result)


def oracle(size: int) -> dict[str, object]:
    return {
        "sections": size,
        "anchors": [
            f"SOURCE_START_{size}",
            f"SOURCE_MIDDLE_{size}",
            f"SOURCE_TAIL_{size}",
        ],
        "facts": [
            "NORTH QUAY",
            f"COMPASS-{size}",
            "COBALT",
            "AMBER is revoked",
            f"RELEASE-{size + 17}",
        ],
        "queries": [
            {
                "query": "Which pilot zone does the opening procedure name?",
                "answers": ["NORTH QUAY"],
                "evidence_sections": [1],
            },
            {
                "query": "What calibration key is recorded halfway through the manual?",
                "answers": [f"COMPASS-{size}"],
                "evidence_sections": [size // 2],
            },
            {
                "query": "What route is finally authorized, replacing the provisional route?",
                "answers": ["COBALT"],
                "evidence_sections": [size],
            },
            {
                "query": "What key and release code are jointly required for final authorization?",
                "answers": [f"COMPASS-{size}", f"RELEASE-{size + 17}"],
                "evidence_sections": [size // 2, size],
            },
        ],
    }


def canonical(size: int) -> str:
    return (
        f"ORION OPERATIONS MANUAL - {size} SECTIONS\n\n"
        + "\n\n".join(
            section.heading + "\n" + section.body for section in sections(size)
        )
        + "\n"
    )


def pdf_document(value: str) -> tuple[bytes, int]:
    from ingest.fixtures import _pdf_pages

    lines = [
        line
        for paragraph in value.splitlines()
        for line in (
            textwrap.wrap(
                paragraph, width=96, break_long_words=False, break_on_hyphens=False
            )
            or [""]
        )
    ]
    streams = []
    for start in range(0, len(lines), 68):
        stream = "BT /F1 9 Tf 40 750 Td 10 TL\n"
        for line in lines[start : start + 68]:
            literal = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            stream += f"({literal}) Tj T*\n"
        streams.append((stream + "ET\n").encode("ascii"))
    require(len(streams) <= 50, "PDF page ceiling")
    return _pdf_pages(streams), len(streams)


def presentation(size: int) -> tuple[bytes, int]:
    from ingest.fixtures import _deck, _slide

    def box(value: str, ident: int, top: int, height: int, font: int) -> str:
        paragraphs = "".join(
            f'<a:p><a:r><a:rPr lang="en-US" sz="{font}"/><a:t>{escape(line)}</a:t></a:r></a:p>'
            for line in value.splitlines()
        )
        return f'<p:sp><p:nvSpPr><p:cNvPr id="{ident}" name="Corpus text {ident}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="365760" y="{top}"/><a:ext cx="8412480" cy="{height}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr><p:txBody><a:bodyPr wrap="square"/><a:lstStyle/>{paragraphs}</p:txBody></p:sp>'

    parts = sections(size)
    slides = []
    for start in range(0, size, 4):
        title = f"ORION {size} - Sections {start + 1} to {min(size, start + 4)}"
        body = "\n".join(
            item.heading + "\n" + item.body for item in parts[start : start + 4]
        )
        slides.append(
            _slide(
                box(title, 2, 182880, 548640, 1800)
                + box(body, 3, 822960, 5669280, 1100)
            )
        )
    require(len(slides) <= 100, "Slide ceiling")
    return _deck(slides), len(slides)


def document_files(size: int) -> tuple[dict[str, bytes], dict[str, int]]:
    from ingest.fixtures import S, _cell, _paragraph, _word, _workbook, archive

    parts = sections(size)
    reference = canonical(size)
    pdf, pages = pdf_document(reference)
    body = _paragraph(f"ORION OPERATIONS MANUAL - {size} SECTIONS", True) + "".join(
        _paragraph(item.heading, True) + _paragraph(item.body) for item in parts
    )
    sheets = []
    for start in range(0, size, 64):
        rows = (
            '<row r="1">'
            + _cell("A1", "Section")
            + _cell("B1", "Topic")
            + _cell("C1", "Procedure")
            + "</row>"
        )
        for index, item in enumerate(parts[start : start + 64], 2):
            rows += (
                f'<row r="{index}" ht="100" customHeight="1">'
                + _cell(f"A{index}", item.heading.split()[0])
                + _cell(f"B{index}", " ".join(item.heading.split()[1:]))
                + _cell(f"C{index}", item.body)
                + "</row>"
            )
        sheet = f'<worksheet xmlns="{S}"><cols><col min="1" max="1" width="20" customWidth="1"/><col min="2" max="2" width="28" customWidth="1"/><col min="3" max="3" width="110" customWidth="1"/></cols><sheetData>{rows}</sheetData></worksheet>'
        sheets.append(
            (f"Sections {start + 1:03d}-{min(size, start + 64):03d}", "visible", sheet)
        )
    pptx, slides = presentation(size)
    workbook = _workbook(sheets)
    with zipfile.ZipFile(io.BytesIO(workbook)) as container:
        members = {name: container.read(name).decode() for name in container.namelist()}
    marker = '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
    require(members["xl/styles.xml"].count(marker) == 1, "Workbook style binding")
    members["xl/styles.xml"] = members["xl/styles.xml"].replace(
        marker,
        marker[:-2]
        + ' applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>',
    )
    return {
        "pdf": pdf,
        "docx": _word(body),
        "xlsx": archive(members),
        "pptx": pptx,
        "txt": reference.encode(),
    }, {"pdf_pages": pages, "xlsx_sheets": len(sheets), "pptx_slides": slides}


def physical_file(path: Path) -> bytes:
    require(
        path.is_file() and path.resolve() == path and path.stat().st_nlink == 1,
        "Corpus file missing/aliased",
    )
    require(path.stat().st_size <= 32 * 1024**2, "Corpus file size ceiling")
    return path.read_bytes()


def publish(root: Path, sizes: tuple[int, ...] = SIZES) -> dict[str, object]:
    require(
        bool(sizes)
        and len(set(sizes)) == len(sizes)
        and all(size in SIZES for size in sizes),
        "Bounded unique corpus sizes required",
    )
    source = source_binding()
    destination = root / "inputs/corpus"
    require(
        destination.parent.resolve() == destination.parent
        and not destination.exists()
        and not destination.is_symlink(),
        "Fresh physical corpus required",
    )
    payloads: dict[str, bytes] = {}
    records: list[dict[str, object]] = []
    oracles = {}
    for size in sizes:
        files, units = document_files(size)
        reference = canonical(size)
        oracles[str(size)] = oracle(size)
        for kind, raw in files.items():
            name = f"orion-{size:03d}.{kind}"
            payloads[name] = raw
            records.append(
                {
                    "path": name,
                    "format": kind,
                    "sections": size,
                    "bytes": len(raw),
                    "sha256": digest(raw),
                    "canonical_words": len(reference.split()),
                    "canonical_characters": len(reference),
                    "qwen_tokens": None,
                    "native_units": units,
                }
            )
    payloads["oracles.json"] = encode(oracles)
    require(
        sum(len(raw) for raw in payloads.values()) <= 16 * 1024**2,
        "Corpus total size ceiling",
    )
    destination.mkdir()
    for name, raw in payloads.items():
        with (destination / name).open("xb") as output:
            output.write(raw)
    manifest: dict[str, object] = {
        "schema": 1,
        "source_binding": source,
        "sizes": list(sizes),
        "documents": records,
        "oracles_sha256": digest(payloads["oracles.json"]),
        "word_counts_are_not_model_tokens": True,
        "qwen_serving_qualified": False,
        "chunking_or_inference_performed": False,
    }
    with (destination / "manifest.json").open("xb") as output:
        output.write(encode(manifest))
    return manifest


def verify(root: Path) -> dict[str, object]:
    folder = root / "inputs/corpus"
    manifest = object_value(json.loads(physical_file(folder / "manifest.json")))
    require(
        manifest.get("schema") == 1
        and manifest.get("source_binding") == source_binding(),
        "Corpus source binding changed",
    )
    require(
        manifest.get("word_counts_are_not_model_tokens") is True
        and manifest.get("qwen_serving_qualified") is False
        and manifest.get("chunking_or_inference_performed") is False,
        "Corpus qualification claims changed",
    )
    sizes = sequence(manifest.get("sizes"))
    require(
        bool(sizes)
        and all(type(size) is int and size in SIZES for size in sizes)
        and len(set(sizes)) == len(sizes),
        "Corpus sizes malformed",
    )
    records = [object_value(row) for row in sequence(manifest.get("documents"))]
    names = [text(row.get("path")) for row in records]
    require(
        bool(names)
        and len(names) == len(set(names))
        and all(Path(name).name == name for name in names),
        "Corpus file inventory malformed",
    )
    require(
        {p.name for p in folder.iterdir()} == {*names, "manifest.json", "oracles.json"},
        "Corpus file inventory changed",
    )
    require(
        len(records) == len(sizes) * len(FORMATS)
        and {(row.get("sections"), row.get("format")) for row in records}
        == {(size, kind) for size in sizes for kind in FORMATS},
        "Corpus format coverage changed",
    )
    for row in records:
        require(
            row.get("qwen_tokens") is None
            and row["path"] == f"orion-{int(str(row['sections'])):03d}.{row['format']}",
            "Corpus document identity/claim changed",
        )
        raw = physical_file(folder / text(row["path"]))
        require(
            digest(raw) == row["sha256"] and len(raw) == row["bytes"],
            "Corpus bytes changed",
        )
    require(
        digest(physical_file(folder / "oracles.json")) == manifest["oracles_sha256"],
        "Corpus oracle changed",
    )
    return manifest


def guard(root: Path, target: Path | None) -> None:
    from ingest.behavior import environment

    clean = environment(root)
    os.environ.clear()
    os.environ.update(clean)
    import mimetypes

    mimetypes.knownfiles = []
    mimetypes.init(files=[])
    allowed = [
        root,
        Path(sys.base_prefix).resolve(),
        Path("/System/Library/CoreServices/SystemVersion.plist"),
    ]
    if target is not None:
        require(
            target.resolve() == target
            and target.is_dir()
            and target.name == "target"
            and ".friday_test" in target.parts,
            "Declared private dependency target required",
        )
        allowed.append(target)
        sys.path.insert(0, str(target))

    def audit(event: str, args: tuple[object, ...]) -> None:
        require(
            not event.startswith("socket.")
            and event
            not in {"subprocess.Popen", "os.system", "os.posix_spawn", "os.exec"},
            "Corpus preparation forbids network/children",
        )
        if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(args[0])).resolve()
            if path == Path("/dev/null"):
                return
            mode, flags = args[1:3]
            writing = (
                isinstance(mode, str)
                and any(ch in mode for ch in "wax+")
                or isinstance(flags, int)
                and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
            )
            require(
                any(
                    path == item or item in path.parents
                    for item in ([root] if writing else allowed)
                ),
                "Corpus filesystem escape",
            )
        if event in {
            "os.mkdir",
            "os.remove",
            "os.rmdir",
            "os.rename",
            "os.chmod",
            "os.utime",
            "os.link",
            "os.symlink",
            "os.truncate",
        }:
            for item in (
                args[:2]
                if event in {"os.rename", "os.link", "os.symlink"}
                else args[:1]
            ):
                if isinstance(item, (str, bytes, os.PathLike)):
                    path = Path(os.fsdecode(item)).resolve()
                    require(
                        path == root or root in path.parents, "Corpus mutation escape"
                    )

    sys.addaudithook(audit)


def native_validate(root: Path, target: Path) -> dict[str, object]:
    manifest = verify(root)
    oracles = object_value(
        json.loads(physical_file(root / "inputs/corpus/oracles.json"))
    )
    modules = {
        name: importlib.import_module(name)
        for name in ("pypdfium2", "docx", "openpyxl", "pptx")
    }
    for module in modules.values():
        require(
            target in Path(module.__file__ or "").resolve().parents,
            "Native reader origin",
        )
    checked = []
    for item in sequence(manifest["documents"]):
        row = object_value(item)
        path = root / "inputs/corpus" / text(row["path"])
        kind = row["format"]
        units = object_value(row["native_units"])
        size = int(str(row["sections"]))
        if kind == "pdf":
            document = modules["pypdfium2"].PdfDocument(str(path))
            require(len(document) == units["pdf_pages"], "Actual PDF page count")
            texts = []
            for page in document:
                text_page = page.get_textpage()
                texts.append(str(text_page.get_text_range()))
                text_page.close()
                page.close()
            document.close()
            value = "\n".join(texts)
        elif kind == "docx":
            value = "\n".join(
                str(p.text) for p in modules["docx"].Document(str(path)).paragraphs
            )
        elif kind == "xlsx":
            workbook = modules["openpyxl"].load_workbook(
                str(path), read_only=True, data_only=True
            )
            require(
                len(workbook.sheetnames) == units["xlsx_sheets"], "Actual sheet count"
            )
            value = "\n".join(
                str(cell)
                for sheet in workbook
                for cells in sheet.iter_rows(values_only=True)
                for cell in cells
                if cell is not None
            )
            workbook.close()
        elif kind == "pptx":
            deck = modules["pptx"].Presentation(str(path))
            require(len(deck.slides) == units["pptx_slides"], "Actual slide count")
            value = "\n".join(
                str(shape.text)
                for slide in deck.slides
                for shape in slide.shapes
                if shape.has_text_frame
            )
        else:
            require(kind == "txt", "Native format not admitted")
            value = path.read_text()
        normalized = " ".join(value.split())
        expected = object_value(oracles[str(size)])
        for marker in [*sequence(expected["anchors"]), *sequence(expected["facts"])]:
            require(text(marker) in normalized, "Native source lost anchor/fact")
        for index in range(1, size + 1):
            require(
                normalized.count(f"SECTION-{index:04d}") == 1,
                "Native source lost/duplicated section",
            )
        for section in sections(size):
            require(section.body in normalized, "Native source lost full section body")
        checked.append(
            {
                "path": row["path"],
                "status": "PASS",
                "sections": size,
                "native_words": len(value.split()),
                "exact_section_bodies_verified": size,
                "qwen_tokens": None,
            }
        )
    result = {
        "status": "PASS",
        "manifest_sha256": digest((root / "inputs/corpus/manifest.json").read_bytes()),
        "source_binding": source_binding(),
        "results": checked,
        "inference_requests": 0,
        "docling_conversion_performed": False,
        "packages": {
            name: importlib.metadata.version(name)
            for name in ("pypdfium2", "python-docx", "openpyxl", "python-pptx")
        },
        "native_isolation_limit": "Python audit guard; not an OS sandbox",
    }
    path = root / "reports/native-validation.json"
    with path.open("xb") as output:
        output.write(encode(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("generate", "verify", "validate"))
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--target", type=Path)
    args = parser.parse_args()
    root = args.run_root
    require(
        sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.flags.dont_write_bytecode == 1,
        "Use base Python -I -S -B",
    )
    require(
        root.resolve() == root
        and root.name.startswith("large-documents-")
        and root.parent.name == "runs"
        and root.parent.parent.name == ".friday_test",
        "Physical large-document run required",
    )
    require(
        not {".friday", ".friday-old", ".git", ".venv", "exports"}.intersection(
            root.parts
        ),
        "Protected corpus ancestor",
    )
    require(
        Path(__file__).resolve() == root / "source/ingest/large_documents.py",
        "Execute frozen corpus source",
    )
    for name in ("source", "inputs", "reports", "config", "cache", "tmp"):
        require(
            (root / name).is_dir() and (root / name).resolve() == root / name,
            "Physical run folders required",
        )
    sys.path.insert(0, str(root / "source"))
    guard(root, args.target)
    if args.command == "generate":
        result = publish(root)
    elif args.command == "verify":
        result = verify(root)
    else:
        require(args.target is not None, "Native validation target required")
        result = native_validate(root, args.target)
    print(
        json.dumps(
            {
                "status": "PASS",
                "documents": len(
                    sequence(result.get("documents", result.get("results")))
                ),
                "inference_requests": 0,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
