"""Direct Docling behavior evaluation in an explicitly owned disposable run."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import signal
import ssl
import subprocess
import sys
import time
import unicodedata
import urllib.request
import zipfile
from collections.abc import Callable
from http.client import HTTPMessage
from pathlib import Path
from typing import IO
from urllib.parse import urlsplit


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def write_json(path: Path, value: object) -> None:
    require(
        path.parent.resolve() == path.parent and not path.is_symlink(),
        "Report alias refused",
    )
    temporary = path.with_name(path.name + f".{time.time_ns()}.tmp")
    with temporary.open("x") as output:
        output.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def environment(root: Path) -> dict[str, str]:
    """Explicit private caches/config; no inherited provider/proxy credentials."""
    result = {
        "PATH": "/usr/bin:/bin",
        "HOME": os.environ.get("HOME", ""),
        "PYTHONDONTWRITEBYTECODE": "1",
        "UV_CACHE_DIR": str(root / "cache/uv"),
        "UV_NO_CONFIG": "true",
        "UV_PYTHON_DOWNLOADS": "never",
        "UV_HTTP_RETRIES": "0",
        "UV_HTTP_TIMEOUT": "60",
        "UV_KEYRING_PROVIDER": "disabled",
        "UV_LINK_MODE": "copy",
        "NETRC": str(root / "config/empty-netrc"),
        "XDG_CACHE_HOME": str(root / "cache/xdg"),
        "XDG_CONFIG_HOME": str(root / "config/xdg"),
        "TMPDIR": str(root / "tmp"),
        "HF_HOME": str(root / "cache/huggingface"),
        "HF_HUB_CACHE": str(root / "cache/huggingface/hub"),
        "HUGGINGFACE_HUB_CACHE": str(root / "cache/huggingface/hub"),
        "HF_HUB_DISABLE_TELEMETRY": "1",
        "DO_NOT_TRACK": "1",
        "TORCH_HOME": str(root / "cache/torch"),
        "MPLCONFIGDIR": str(root / "cache/matplotlib"),
        "TORCHINDUCTOR_CACHE_DIR": str(root / "cache/torchinductor"),
        "DOCLING_ARTIFACTS_PATH": str(root / "assets"),
        "LITELLM_MODE": "PRODUCTION",
        "LITELLM_LOCAL_MODEL_COST_MAP": "True",
        "OMP_NUM_THREADS": "4",
        "MKL_NUM_THREADS": "4",
        "OPENBLAS_NUM_THREADS": "4",
        "TOKENIZERS_PARALLELISM": "false",
    }
    netrc = root / "config/empty-netrc"
    require(not netrc.is_symlink(), "Credential sink alias refused")
    if netrc.exists():
        require(
            netrc.is_file() and netrc.stat().st_size == 0,
            "Nonempty credential sink refused",
        )
    else:
        with netrc.open("xb"):
            pass
    return result


def supervise(root: Path, name: str, argv: list[str], seconds: int) -> int:
    """Only terminate this command's own process group; keep logs on failure."""
    started = time.monotonic()
    used = 0.0
    for path in [
        *(root / "reports").glob("*.json"),
        *(root / "reports/commands").glob("*.json"),
    ]:
        value = json.loads(path.read_bytes())
        if isinstance(value, dict) and "argv" in value and "seconds" in value:
            used += float(value["seconds"])
    require(used < 7200, "Cumulative active evaluation time exhausted")
    seconds = min(seconds, int(7200 - used))
    reason: str | None = None
    peak_rss = 0
    last_disk_check = started - 10
    require(Path(name).name == name and name not in {".", ".."}, "Command name refused")
    if any(
        (root / "logs" / (name + suffix)).exists()
        or (root / "logs" / (name + suffix)).is_symlink()
        for suffix in (".stdout", ".stderr")
    ):
        name += "-" + str(time.time_ns())
    source = Path(__file__).read_bytes()
    source_sha = hashlib.sha256(source).hexdigest()
    snapshot = root / "source" / ("behavior-" + source_sha + ".py")
    require(not snapshot.is_symlink(), "Runner snapshot alias refused")
    if snapshot.exists():
        require(snapshot.read_bytes() == source, "Runner snapshot changed")
    else:
        with snapshot.open("xb") as output:
            output.write(source)
    with (
        (root / "logs" / (name + ".stdout")).open("xb") as stdout,
        (root / "logs" / (name + ".stderr")).open("xb") as stderr,
    ):
        child = subprocess.Popen(
            argv,
            cwd=root,
            env=environment(root),
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
        try:
            while child.poll() is None:
                if time.monotonic() - started > seconds:
                    reason = "time_limit"
                    break
                raw = subprocess.check_output(
                    ["/bin/ps", "-axo", "pid=,ppid=,rss="],
                    env={"PATH": "/usr/bin:/bin"},
                    text=True,
                )
                rows = [tuple(map(int, line.split())) for line in raw.splitlines()]
                owned = {child.pid}
                for _ in range(32):
                    expanded = owned | {
                        pid for pid, parent, _ in rows if parent in owned
                    }
                    if expanded == owned:
                        break
                    owned = expanded
                rss = sum(size * 1024 for pid, _, size in rows if pid in owned)
                peak_rss = max(peak_rss, rss)
                if rss > 8 * 1024**3:
                    reason = "rss_limit"
                    break
                if time.monotonic() - last_disk_check >= 10:
                    total = cache = 0
                    for folder, _dirs, files in os.walk(root, followlinks=False):
                        for filename in files:
                            path = Path(folder) / filename
                            size = path.lstat().st_size
                            total += size
                            if root / "cache/uv" in path.parents:
                                cache += size
                    if total > 16 * 1024**3 or cache > 4 * 1024**3:
                        reason = "disk_limit"
                        break
                    last_disk_check = time.monotonic()
                time.sleep(0.25)
        finally:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
            child.wait()
    record = {
        "argv": argv,
        "exit": child.returncode,
        "reason": reason,
        "seconds": time.monotonic() - started,
        "peak_rss_bytes": peak_rss,
        "scope": "private process tree; sampled RSS, no OS sandbox claim",
        "runner_sha256": source_sha,
        "prior_active_seconds": used,
    }
    commands = root / "reports/commands"
    commands.mkdir(exist_ok=True)
    write_json(commands / (name + ".json"), record)
    print(json.dumps(record), flush=True)
    return child.returncode if reason is None else 124


def setup(root: Path, uv: Path) -> int:
    require(not any((root / "target").iterdir()), "Private target must be empty")
    inputs = root / "config/requirements.in"
    require(
        not inputs.is_symlink() and inputs.stat().st_nlink == 1,
        "Requirements alias refused",
    )
    require(
        inputs.read_text()
        == "docling[rapidocr]==2.150.0\nrapidocr==3.10.0\ncertifi==2026.10.23\n",
        "Explicit behavior package profile required",
    )
    compile_args = [
        str(uv),
        "--no-config",
        "pip",
        "compile",
        str(root / "config/requirements.in"),
        "--python",
        sys.executable,
        "--no-python-downloads",
        "--only-binary",
        ":all:",
        "--no-sources",
        "--default-index",
        "https://pypi.org/simple",
        "--generate-hashes",
        "--output-file",
        str(root / "config/requirements.lock"),
    ]
    code = supervise(root, "resolve", compile_args, 900)
    if code:
        return code
    return supervise(
        root,
        "install",
        [
            str(uv),
            "--no-config",
            "pip",
            "sync",
            str(root / "config/requirements.lock"),
            "--python",
            sys.executable,
            "--no-python-downloads",
            "--target",
            str(root / "target"),
            "--require-hashes",
            "--only-binary",
            ":all:",
            "--default-index",
            "https://pypi.org/simple",
            "--link-mode",
            "copy",
            "--strict",
        ],
        1200,
    )


def offline(root: Path) -> None:
    """Conversion may read local dependencies/assets and write only this run.

    Python-visible network/process/writes are intercepted. Native libraries are
    not an OS sandbox; production preservation is checked separately.
    """
    clean = environment(root)
    os.environ.clear()
    os.environ.update(clean)
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    sys.path.insert(0, str(root / "target"))
    import mimetypes

    mimetypes.knownfiles = []
    mimetypes.init(files=[])  # Built-in mappings, no host/server configuration.

    def audit(event: str, args: tuple[object, ...]) -> None:
        if event in {
            "socket.connect",
            "socket.getaddrinfo",
            "socket.sendto",
            "subprocess.Popen",
            "os.system",
        }:
            raise PermissionError("Offline evaluation forbids network/child processes")
        if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
            if Path(os.fsdecode(args[0])).resolve() == Path("/dev/null"):
                return  # Standard sink/type probes; never a user file.
            mode, flags = args[1], args[2]
            writing = isinstance(mode, str) and any(letter in mode for letter in "wax+")
            writing = (
                writing
                or isinstance(flags, int)
                and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
            )
            if writing:
                path = Path(os.fsdecode(args[0])).resolve()
                require(
                    path == root or root in path.parents,
                    "Write outside private run refused",
                )
            else:
                path = Path(os.fsdecode(args[0])).resolve()
                allowed = (
                    root,
                    Path(sys.base_prefix).resolve(),
                    Path(__file__).resolve(),
                )
                require(
                    any(path == item or item in path.parents for item in allowed)
                    or path == Path("/System/Library/CoreServices/SystemVersion.plist"),
                    "Read outside evaluation/stdlib roots refused: " + str(path),
                )
        elif event in {
            "os.mkdir",
            "os.remove",
            "os.rmdir",
            "os.chmod",
            "os.utime",
            "os.truncate",
            "os.rename",
            "os.link",
            "os.symlink",
        }:
            for value in (
                args[:2]
                if event in {"os.rename", "os.link", "os.symlink"}
                else args[:1]
            ):
                if isinstance(value, (str, bytes, os.PathLike)):
                    path = Path(os.fsdecode(value)).resolve()
                    require(
                        path == root or root in path.parents,
                        "Mutation outside private run refused",
                    )

    sys.addaudithook(audit)


def probe(root: Path) -> int:
    offline(root)
    import importlib.metadata

    import certifi
    from packaging.version import Version

    require(
        Version(importlib.metadata.version("certifi")) >= Version("2026.10.19"),
        "Certifi security floor",
    )
    require(
        root / "target" in Path(certifi.where()).resolve().parents,
        "Wrong Certifi origin",
    )
    versions = {
        dist.metadata["Name"]: dist.version
        for dist in importlib.metadata.distributions(path=[str(root / "target")])
    }
    write_json(
        root / "reports/packages.json",
        {
            "versions": versions,
            "certifi_bundle": certifi.where(),
            "certifi_floor_pass": True,
        },
    )
    print(
        json.dumps(
            {
                "distributions": len(versions),
                "certifi": importlib.metadata.version("certifi"),
                "docling": importlib.metadata.version("docling"),
            }
        )
    )
    return 0


def prepare_inputs(root: Path) -> int:
    sys.path.insert(0, str(root / "source"))
    from ingest.fixtures import publish_matrix

    expected = json.loads(
        (root / "source/ingest/fixtures/expectations.json").read_bytes()
    )["A2"]["fixture_oracles"]
    published = publish_matrix(root / "inputs/generated", expected, lambda: None)
    write_json(root / "config/oracles.json", expected)
    write_json(root / "reports/fixtures.json", published)
    print(
        json.dumps(
            {
                "genuine_inputs": len(expected["cases"]),
                "formats": ["pdf", "docx", "xlsx", "pptx"],
            }
        )
    )
    return 0


def prepare_controls(root: Path) -> int:
    sys.path.insert(0, str(root / "source"))
    from ingest.fixtures import _pdf_pages, _text_stream

    directory = root / "inputs/supplemental"
    directory.mkdir(exist_ok=False)
    files = {
        "corrupt." + kind: b"private corrupt document fixture"
        for kind in ("pdf", "docx", "xlsx", "pptx")
    }
    files["oversize.pdf"] = b"%PDF-1.7\n" + bytes(32 * 1024**2)
    files["over-pages.pdf"] = _pdf_pages(
        [_text_stream(["LIMIT PAGE " + str(index)]) for index in range(51)]
    )
    files["mismatched.docx"] = (root / "inputs/generated/xlsx-values.xlsx").read_bytes()
    oracles = json.loads((root / "config/oracles.json").read_bytes())
    records = []
    for name, raw in files.items():
        path = directory / name
        path.write_bytes(raw)
        path.chmod(0o444)
        records.append(
            {"file": name, "size": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        )
        oracles["cases"].append(
            {
                "file": name,
                "format": path.suffix[1:],
                "contains": [],
                "excludes": [],
                "units": 51 if name == "over-pages.pdf" else 0,
                "outcome": "refuse",
                "input_group": "supplemental",
            }
        )
    write_json(root / "config/oracles.json", oracles)
    write_json(root / "reports/supplemental-controls.json", records)
    print(json.dumps({"supplemental_controls": len(records)}))
    return 0


def fetch_assets(root: Path, manifest: Path) -> int:
    clean = environment(root)
    os.environ.clear()
    os.environ.update(clean)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cafile=str(root / "target/certifi/cacert.pem"))

    class PublicRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(
            self,
            req: urllib.request.Request,
            fp: IO[bytes],
            code: int,
            msg: str,
            headers: HTTPMessage,
            newurl: str,
        ) -> urllib.request.Request | None:
            parsed = urlsplit(newurl)
            host = parsed.hostname or ""
            require(
                parsed.scheme == "https"
                and (
                    host == "huggingface.co"
                    or host.endswith(".hf.co")
                    or host.endswith(".huggingface.co")
                )
                and not parsed.username
                and not parsed.password,
                "Non-public asset redirect refused",
            )
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPSHandler(context=context),
        PublicRedirect(),
    )
    records: list[dict[str, object]] = []
    total = 0
    for item in json.loads(manifest.read_bytes())["asset_candidates"]:
        role = item["role"]
        folder = {
            "layout": "docling-project--docling-layout-heron",
            "tableformer": "docling-project--docling-models",
            "ocr": "ocr",
            "tokenizer": "nomic",
        }[role]
        destination = root / "assets" / folder / item["path"]
        require(
            destination.resolve() == destination
            and destination.is_relative_to(root / "assets"),
            "Asset destination escaped private root",
        )
        initial = urlsplit(item["url"])
        require(
            initial.scheme == "https"
            and initial.hostname == "huggingface.co"
            and initial.port in {None, 443}
            and not initial.username
            and not initial.password
            and not initial.query
            and not initial.fragment,
            "Non-public initial asset URL refused",
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        expected_size = item["size_bytes"]
        total += expected_size
        require(total <= 1024**3, "Asset budget exceeded")
        entry: dict[str, object] = {
            "role": role,
            "source": item["url"],
            "path": str(destination.relative_to(root)),
        }
        try:
            candidate = destination
            if not destination.exists():
                temporary = destination.with_name(destination.name + ".part")
                with (
                    opener.open(item["url"], timeout=60) as response,
                    temporary.open("xb") as output,
                ):
                    count = 0
                    while chunk := response.read(1024**2):
                        count += len(chunk)
                        require(count <= expected_size, "Asset exceeds declared size")
                        output.write(chunk)
                require(count == expected_size, "Incomplete asset")
                candidate = temporary
            raw = candidate.read_bytes()
            require(len(raw) == expected_size, "Asset size mismatch")
            actual = hashlib.sha256(raw).hexdigest()
            if item["expected_lfs_sha256"]:
                require(actual == item["expected_lfs_sha256"], "Asset SHA256 mismatch")
            else:
                blob = hashlib.sha1(
                    b"blob " + str(len(raw)).encode() + b"\0" + raw
                ).hexdigest()
                require(
                    blob == item["expected_git_blob_sha1"], "Asset Git-blob mismatch"
                )
            if candidate != destination:
                candidate.rename(destination)
            destination.chmod(0o444)
            entry.update(status="verified", sha256=actual, size=len(raw))
        except Exception as exc:
            entry.update(status="failed", error=type(exc).__name__ + ": " + str(exc))
        records.append(entry)
        write_json(root / "reports/assets.json", records)
        print(
            json.dumps(
                {"asset": str(destination.relative_to(root)), "status": entry["status"]}
            ),
            flush=True,
        )
    return 0 if all(row["status"] == "verified" for row in records) else 1


def compare_text(
    content: str, expected: dict[str, object], ordered: bool
) -> dict[str, object]:
    normalized = " ".join(unicodedata.normalize("NFC", content).split())
    included = expected["contains"]
    excluded = expected["excludes"]
    if not isinstance(included, list) or not isinstance(excluded, list):
        raise ValueError("Invalid independent oracle")
    missing = [item for item in included if item not in normalized]
    leaked = [item for item in excluded if item in normalized]
    positions = [normalized.find(item) for item in included]
    order_ok = not ordered or not missing and positions == sorted(positions)
    meaningful = re.sub(r"<!--.*?-->|!\[[^\]]*\]\([^)]*\)", "", normalized)
    return {
        "missing": missing,
        "leaked": leaked,
        "order_ok": order_ok,
        "meaningful": any(character.isalnum() for character in meaningful),
    }


def admission_reasons(facts: dict[str, object]) -> list[str]:
    reasons = facts.get("refusal_codes", [])
    if not isinstance(reasons, list) or not all(
        isinstance(item, str) for item in reasons
    ):
        raise ValueError("Invalid structural refusal facts")
    result = [str(item) for item in reasons]
    units = facts.get("units", [])
    if isinstance(units, list):
        for item in units:
            require(isinstance(item, dict), "Invalid structural unit")
            if not item.get("hidden", False):
                if item.get("hidden_rows"):
                    result.append("unsupported_hidden_rows")
                if item.get("hidden_columns"):
                    result.append("unsupported_hidden_columns")
    return sorted(set(result))


def convert_case(
    root: Path,
    filename: str,
    include_furniture: bool = False,
    enforce_admission: bool = False,
) -> int:
    offline(root)
    sys.path.insert(0, str(root / "source"))
    from ingest.fixtures import audit_office

    expected = next(
        row
        for row in json.loads((root / "config/oracles.json").read_bytes())["cases"]
        if row["file"] == filename
    )
    group = expected.get("input_group", "generated")
    require(group in {"generated", "supplemental"}, "Unknown input group")
    path = root / "inputs" / group / filename
    require(
        path.parent == root / "inputs" / group
        and path.is_file()
        and not path.is_symlink(),
        "Unknown input",
    )
    record: dict[str, object] = {
        "file": filename,
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "expected": expected,
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    record["phase"] = "admission"
    record["native_docling_called"] = False
    started = time.monotonic()
    expected_structural_refusal = False
    try:
        require(path.stat().st_size <= 32 * 1024**2, "Input size limit")
        if expected["format"] != "pdf":
            audit = audit_office(path.read_bytes(), expected["format"])
            record["structural_audit"] = audit
            reasons = admission_reasons(audit)
            if enforce_admission and reasons:
                expected_structural_refusal = filename in {
                    "xlsx-hidden-row.xlsx",
                    "xlsx-hidden-column.xlsx",
                }
                raise ValueError("Structural admission refused: " + ",".join(reasons))
        record["phase"] = "setup"
        from docling.datamodel.accelerator_options import (
            AcceleratorDevice,
            AcceleratorOptions,
        )
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import (
            PdfPipelineOptions,
            RapidOcrOptions,
        )
        from docling.document_converter import DocumentConverter, PdfFormatOption
        from docling_core.types.doc import ContentLayer

        origins = {
            name: str(sys.modules[name].__file__)
            for name in (
                "docling.document_converter",
                "docling.datamodel.pipeline_options",
            )
        }
        require(
            all(
                root / "target" in Path(value).resolve().parents
                for value in origins.values()
            ),
            "Unexpected Docling module origin",
        )
        record["module_origins"] = origins

        options = PdfPipelineOptions(
            artifacts_path=root / "assets",
            enable_remote_services=False,
            accelerator_options=AcceleratorOptions(
                device=AcceleratorDevice.CPU, num_threads=4
            ),
            document_timeout=300,
        )
        options.ocr_options = RapidOcrOptions(
            backend="onnxruntime",
            lang=["en"],
            det_model_path=str(root / "assets/ocr/PP-OCRv4/en_PP-OCRv3_det_infer.onnx"),
            rec_model_path=str(root / "assets/ocr/PP-OCRv3/en_PP-OCRv3_rec_infer.onnx"),
            cls_model_path=str(
                root / "assets/ocr/PP-OCRv1/ch_ppocr_mobile_v2.0_cls_infer.onnx"
            ),
        )
        converter = DocumentConverter(
            allowed_formats=[
                InputFormat.PDF,
                InputFormat.DOCX,
                InputFormat.XLSX,
                InputFormat.PPTX,
            ],
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)},
        )
        record["phase"] = "conversion"
        record["native_docling_called"] = True
        converted = converter.convert(
            path, raises_on_error=False, max_num_pages=50, max_file_size=32 * 1024**2
        )
        content = converted.document.export_to_markdown(
            included_content_layers={ContentLayer.BODY, ContentLayer.FURNITURE}
            if include_furniture
            else {ContentLayer.BODY}
        )
        notes = converted.document.export_to_markdown(
            included_content_layers={ContentLayer.NOTES}
        )
        destination = (
            root
            / "reports"
            / (
                "admitted/documents"
                if enforce_admission
                else "body-furniture/documents"
                if include_furniture
                else "documents"
            )
        )
        destination.mkdir(parents=True, exist_ok=True)
        (destination / (filename + ".md")).write_text(content)
        (destination / (filename + ".notes.md")).write_text(notes)
        converted.document.save_as_json(destination / (filename + ".json"))
        record["output_json_sha256"] = hashlib.sha256(
            (destination / (filename + ".json")).read_bytes()
        ).hexdigest()
        ordered = filename in {
            "pdf-native.pdf",
            "pdf-pages.pdf",
            "docx-body.docx",
            "docx-long.docx",
            "xlsx-order.xlsx",
            "pptx-order.pptx",
            "pptx-unicode-long.pptx",
        }
        comparison_text = content
        audit_record = record.get("structural_audit", {})
        if (
            notes.strip()
            and isinstance(audit_record, dict)
            and audit_record.get("comment_parts", 0) == 0
        ):
            comparison_text += "\n\n## Speaker notes\n\n" + notes
        comparison = compare_text(comparison_text, expected, ordered)
        record.update(
            conversion_status=converted.status.value,
            errors=[str(error) for error in converted.errors],
            characters=len(content),
            notes_characters=len(notes),
            docling_pages=len(converted.document.pages),
            tables=len(converted.document.tables),
            comparison=comparison,
        )
        refused = (
            not comparison["meaningful"]
            or converted.status.value != "success"
            or bool(converted.errors)
        )
        matches = (
            bool(refused)
            if expected["outcome"] == "refuse"
            else not refused
            and not comparison["missing"]
            and not comparison["leaked"]
            and comparison["order_ok"]
        )
        record.update(
            status="characterized"
            if expected["outcome"] == "characterize"
            else "pass"
            if matches
            else "fail",
            raw_output_retained=True,
        )
    except Exception as exc:
        # Setup/import/model failures do not prove document rejection.
        admitted_refusal = (
            record["phase"] == "admission"
            and isinstance(exc, (ValueError, zipfile.BadZipFile))
            and (expected["outcome"] == "refuse" or expected_structural_refusal)
        )
        record.update(
            status="admission_refused" if admitted_refusal else "error",
            exception=type(exc).__name__,
            error=str(exc),
        )
    record["seconds"] = time.monotonic() - started
    result_root = (
        root
        / "reports"
        / (
            "admitted"
            if enforce_admission
            else "body-furniture"
            if include_furniture
            else "."
        )
    )
    result_root.mkdir(exist_ok=True)
    write_json(result_root / (filename + ".result.json"), record)
    print(
        json.dumps(
            {"file": filename, "status": record["status"], "seconds": record["seconds"]}
        ),
        flush=True,
    )
    return (
        0 if record["status"] in {"pass", "characterized", "admission_refused"} else 1
    )


def fixed_chunks(
    content: str,
    limit: int,
    count: Callable[[str], int],
    offsets: Callable[[str], list[int]],
) -> list[str]:
    """Token-boundary slices, retaining every character and final-input limits."""
    require(type(limit) is int and 16 <= limit <= 8192, "Chunk-token limit")
    require(count("") < limit, "Prepared prefix exhausts token budget")
    chunks: list[str] = []
    start = 0
    while start < len(content):
        remaining = content[start:]
        if count(remaining) <= limit:
            chunks.append(remaining)
            break
        ends = offsets(remaining)
        require(
            bool(ends)
            and all(type(end) is int and 0 < end <= len(remaining) for end in ends),
            "Tokenizer offsets invalid",
        )
        index = min(limit, len(ends)) - 1
        while index >= 0 and count(remaining[: ends[index]]) > limit:
            index -= 1
        require(index >= 0, "Cannot split input within prepared token budget")
        end = ends[index]
        require(end > 0, "Chunker made no progress")
        chunks.append(remaining[:end])
        start += end
    require(
        "".join(chunks) == content and all(count(chunk) <= limit for chunk in chunks),
        "Chunk coverage/overflow failure",
    )
    return chunks


def recursive_chunks(
    content: str,
    limit: int,
    count: Callable[[str], int],
    offsets: Callable[[str], list[int]],
) -> list[str]:
    def divide(value: str, separators: tuple[str, ...]) -> list[str]:
        if count(value) <= limit:
            return [value]
        if not separators:
            return fixed_chunks(value, limit, count, offsets)
        separator, *rest = separators
        if separator not in value:
            return divide(value, tuple(rest))
        pieces = value.split(separator)
        return [
            part
            for index, piece in enumerate(pieces)
            for part in divide(
                piece + (separator if index < len(pieces) - 1 else ""), tuple(rest)
            )
        ]

    require(type(limit) is int and 16 <= limit <= 8192, "Chunk-token limit")
    packed: list[str] = []
    current = ""
    for piece in divide(content, ("\n\n", "\n", ". ", " ")):
        if current and count(current + piece) > limit:
            packed.append(current)
            current = ""
        current += piece
    if current:
        packed.append(current)
    require(
        "".join(packed) == content and all(count(chunk) <= limit for chunk in packed),
        "Recursive coverage/overflow failure",
    )
    return packed


def document_ready(record: dict[str, object], raw: bytes) -> bool:
    comparison = record.get("comparison")
    return (
        record.get("status") in {"pass", "characterized"}
        and record.get("native_docling_called") is True
        and record.get("conversion_status") == "success"
        and record.get("errors") == []
        and isinstance(comparison, dict)
        and comparison.get("meaningful") is True
        and record.get("output_json_sha256") == hashlib.sha256(raw).hexdigest()
    )


def chunk_cases(
    root: Path,
    limits: list[int],
    raw_defaults: bool = False,
    document_profile: str = "admitted",
) -> int:
    offline(root)
    from docling_core.transforms.chunker.hierarchical_chunker import (
        ChunkingDocSerializer,
        ChunkingSerializerProvider,
    )
    from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
    from docling_core.transforms.chunker.tokenizer.huggingface import (
        HuggingFaceTokenizer,
    )
    from docling_core.transforms.serializer.base import (
        BaseDocSerializer,
        BaseSerializerProvider,
    )
    from docling_core.transforms.serializer.markdown import MarkdownParams
    from docling_core.types.doc import ContentLayer, DocItemLabel, DoclingDocument
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        str(root / "assets/nomic"),
        tokenizer_type="bert",
        use_fast=True,
        local_files_only=True,
        trust_remote_code=False,
    )
    prefix = "search_document: "

    class EvaluationSerializer(BaseSerializerProvider):
        def __init__(self, layers: set[ContentLayer]) -> None:
            self.layers = layers

        def get_serializer(self, doc: DoclingDocument) -> BaseDocSerializer:
            return ChunkingDocSerializer(
                doc=doc,
                params=MarkdownParams(
                    layers=self.layers,
                    labels=set(DocItemLabel),
                    image_placeholder="",
                    escape_html=False,
                    escape_underscores=False,
                ),
            )

    def count(value: str) -> int:
        return len(
            tokenizer.encode(prefix + value, add_special_tokens=True, truncation=False)
        )

    def offsets(value: str) -> list[int]:
        return [
            end
            for start, end in tokenizer(
                value,
                add_special_tokens=False,
                return_offsets_mapping=True,
                truncation=False,
            )["offset_mapping"]
            if end > start
        ]

    sources: list[tuple[str, DoclingDocument]] = []
    require(
        document_profile in {"raw", "admitted", "body-furniture"},
        "Unknown document profile",
    )
    profile_root = (
        root / "reports" / ("." if document_profile == "raw" else document_profile)
    )
    skipped: list[dict[str, str]] = []
    for path in sorted((profile_root / "documents").glob("*.json")):
        raw = path.read_bytes()
        result_path = profile_root / (path.name.removesuffix(".json") + ".result.json")
        if document_profile == "admitted" and (
            not result_path.is_file()
            or not document_ready(json.loads(result_path.read_bytes()), raw)
        ):
            skipped.append(
                {"file": path.name, "reason": "not current admitted meaningful output"}
            )
            continue
        document = DoclingDocument.model_validate_json(raw)
        if any(item.text.strip() for item in document.texts) or document.tables:
            sources.append((path.name, document))
    require(bool(sources), "No current converted documents available for chunking")
    document_sources = [name for name, _ in sources]
    for kind in ("text", "markdown", "code-json", "csv", "tsv", "web-tool-payload"):
        document = DoclingDocument(name=kind)
        for index in range(120):
            document.add_text(
                label=DocItemLabel.PARAGRAPH,
                text=f"{kind} ROW {index}: café 東京 Ω distinctive content for bounded embedding input.\n",
            )
        sources.append(("supplemental-" + kind, document))
    results: list[dict[str, object]] = []
    destination = root / "reports/chunks"
    destination.mkdir(exist_ok=True)
    for name, document in sources:
        layers = {ContentLayer.BODY, ContentLayer.FURNITURE}
        result_path = profile_root / (name.removesuffix(".json") + ".result.json")
        if ".pptx.json" in name and result_path.is_file():
            audit = json.loads(result_path.read_bytes()).get("structural_audit", {})
            if audit.get("comment_parts", 0) == 0:
                layers.add(ContentLayer.NOTES)
        content = document.export_to_markdown(
            included_content_layers={ContentLayer.BODY} if raw_defaults else layers
        )
        for limit in limits:
            require(type(limit) is int and 16 <= limit <= 8192, "Chunk-token limit")
            for strategy in ("document", "recursive", "fixed"):
                row: dict[str, object] = {
                    "source": name,
                    "strategy": strategy,
                    "limit": limit,
                }
                started = time.monotonic()
                try:
                    if strategy == "document":
                        chunker = HybridChunker(
                            tokenizer=HuggingFaceTokenizer(
                                tokenizer=tokenizer, max_tokens=limit - count("")
                            ),
                            merge_peers=True,
                            always_emit_headings=not raw_defaults,
                            serializer_provider=ChunkingSerializerProvider()
                            if raw_defaults
                            else EvaluationSerializer(layers),
                        )
                        fragments = [
                            chunker.contextualize(chunk)
                            for chunk in chunker.chunk(dl_doc=document)
                        ]
                    elif strategy == "recursive":
                        fragments = recursive_chunks(content, limit, count, offsets)
                    else:
                        fragments = fixed_chunks(content, limit, count, offsets)
                    counts = [count(fragment) for fragment in fragments]
                    require(
                        bool(fragments) and all(size <= limit for size in counts),
                        "Final prepared chunk overflow/empty output",
                    )
                    row.update(
                        status="pass",
                        chunks=len(fragments),
                        max_prepared_tokens=max(counts),
                        source_reconstruction="exact"
                        if strategy != "document"
                        else "Docling contextualized representation; coverage assessed separately",
                    )
                    write_json(
                        destination / (name + f".{strategy}.{limit}.json"),
                        {
                            "chunks": [
                                {
                                    "text": fragment,
                                    "prepared": prefix + fragment,
                                    "tokens_with_specials": size,
                                }
                                for fragment, size in zip(
                                    fragments, counts, strict=True
                                )
                            ]
                        },
                    )
                except Exception as exc:
                    row.update(
                        status="fail", error=type(exc).__name__ + ": " + str(exc)
                    )
                row["seconds"] = time.monotonic() - started
                results.append(row)
    write_json(
        root
        / "reports"
        / ("chunking-default.json" if raw_defaults else "chunking.json"),
        {
            "tokenizer": "nomic-ai/nomic-embed-text-v1.5, pinned local tokenizer",
            "prefix": prefix,
            "special_tokens_counted": True,
            "model_calls": 0,
            "counter_matches_LM_Studio": "not yet qualified",
            "raw_docling_defaults": raw_defaults,
            "document_profile": document_profile,
            "actual_document_sources": document_sources,
            "skipped": skipped,
            "configured_document": "emit isolated headings; preserve body/furniture and unambiguous PPTX notes through Docling serializer",
            "recursive_fixed": "test-only policy prototypes, not production implementations",
            "results": results,
        },
    )
    print(
        json.dumps(
            {
                "cases": len(results),
                "passed": sum(row["status"] == "pass" for row in results),
                "failed": sum(row["status"] != "pass" for row in results),
                "sources": len(sources),
                "limits": limits,
            }
        ),
        flush=True,
    )
    return 0 if all(row["status"] == "pass" for row in results) else 1


def check_isolation(root: Path) -> int:
    original_home = os.environ.get("HOME", "")
    offline(root)
    import socket

    checks: dict[str, bool] = {
        "ambient_credentials_and_proxies_absent": all(
            key not in os.environ
            for key in ("OPENAI_API_KEY", "HF_TOKEN", "HTTP_PROXY", "HTTPS_PROXY")
        ),
        "home_unchanged": os.environ.get("HOME", "") == original_home,
    }
    try:
        with socket.socket() as connection:
            connection.connect(("127.0.0.1", 9))
    except PermissionError as exc:
        checks["network_denied_before_connect"] = "Offline evaluation" in str(exc)
    for operation, mode in (("write", "xb"), ("read", "rb")):
        try:
            with (root.parent / "forbidden-evaluation-canary").open(mode):
                pass
        except ValueError as exc:
            checks[operation + "_outside_run_denied"] = "outside" in str(exc)
    allowed = root / "reports/allowed-isolation-canary"
    allowed.write_text("private-only")
    checks["private_write_and_read_allowed"] = allowed.read_text() == "private-only"
    require(len(checks) == 6 and all(checks.values()), "Isolation canary failed")
    write_json(
        root / "reports/isolation.json",
        {
            "checks": checks,
            "scope": "Python-visible prevention; native/OS behavior not sandboxed",
            "production_changes": False,
        },
    )
    print(json.dumps(checks))
    return 0


def summarize(root: Path) -> int:
    """Check chunk content against independent source oracles and print results."""
    data = json.loads((root / "reports/chunking.json").read_bytes())
    oracles = {
        row["file"]: row
        for row in json.loads((root / "config/oracles.json").read_bytes())["cases"]
    }
    coverage: list[dict[str, object]] = []
    for row in data["results"]:
        name = row["source"]
        require(
            Path(name).name == name
            and row["strategy"] in {"document", "recursive", "fixed"},
            "Unsafe chunk report identity",
        )
        path = (
            root / "reports/chunks" / (name + f".{row['strategy']}.{row['limit']}.json")
        )
        if row["status"] != "pass" or not path.is_file():
            coverage.append(
                {
                    "source": name,
                    "strategy": row["strategy"],
                    "limit": row["limit"],
                    "passed": False,
                    "reason": "chunk production failed",
                }
            )
            continue
        chunks = json.loads(path.read_bytes())["chunks"]
        expected: dict[str, object]
        if name.startswith("supplemental-"):
            kind = name.removeprefix("supplemental-")
            expected = {
                "contains": [kind + " ROW 0:", kind + " ROW 119:"],
                "excludes": [],
            }
        else:
            expected = oracles[name.removesuffix(".json")]
        separator = "\n" if row["strategy"] == "document" else ""
        comparison = compare_text(
            separator.join(chunk["text"] for chunk in chunks), expected, False
        )
        passed = (
            not comparison["missing"]
            and not comparison["leaked"]
            and comparison["meaningful"]
            and all(chunk["tokens_with_specials"] <= row["limit"] for chunk in chunks)
        )
        coverage.append(
            {
                "source": name,
                "strategy": row["strategy"],
                "limit": row["limit"],
                "passed": bool(passed),
                "comparison": comparison,
            }
        )
    require(bool(coverage), "No chunk coverage results")
    result = {
        "document_profile": data["document_profile"],
        "actual_document_sources": data["actual_document_sources"],
        "cases": len(coverage),
        "passed": sum(bool(row["passed"]) for row in coverage),
        "results": coverage,
        "embedding_calls": 0,
    }
    write_json(root / "reports/chunk-content-coverage.json", result)
    print(json.dumps({key: value for key, value in result.items() if key != "results"}))
    return 0 if all(row["passed"] for row in coverage) else 1


def evaluate(root: Path, limits: list[int], raw_defaults: bool) -> int:
    """Repeat the prepared matrix; never installs or starts a model service."""
    runner = str(Path(__file__).resolve())
    flags = ["-I", "-S", "-B"] + (["-O"] if sys.flags.optimize else [])
    commands: list[dict[str, object]] = []
    mode = "optimized" if sys.flags.optimize else "normal"
    profile = "raw" if raw_defaults else "configured"
    for row in json.loads((root / "config/oracles.json").read_bytes())["cases"]:
        filename = row["file"]
        args = [
            sys.executable,
            *flags,
            runner,
            "convert",
            "--run-root",
            str(root),
            "--case",
            filename,
        ]
        if not raw_defaults:
            args += ["--include-furniture", "--enforce-admission"]
        code = supervise(root, f"{mode}-{profile}-{filename}", args, 300)
        commands.append({"case": filename, "exit": code})
    for operation in ("check-isolation", "chunks"):
        args = [sys.executable, *flags, runner, operation, "--run-root", str(root)]
        if operation == "chunks":
            args += ["--chunk-tokens", *map(str, limits)]
            args += ["--document-profile", "raw" if raw_defaults else "admitted"]
            if raw_defaults:
                args += ["--raw-chunker-defaults"]
        code = supervise(root, f"{mode}-{profile}-{operation}", args, 300)
        commands.append({"operation": operation, "exit": code})
    result = {
        "mode": mode,
        "profile": profile,
        "commands": commands,
        "all_expected_exits": all(row["exit"] == 0 for row in commands),
        "meaning": "behavior measurements and fail-closed admission, not product readiness",
        "embedding_calls": 0,
    }
    write_json(root / "reports" / (f"evaluation-{mode}-{profile}.json"), result)
    if not raw_defaults:
        result["content_coverage_exit"] = summarize(root)
        write_json(root / "reports" / (f"evaluation-{mode}-{profile}.json"), result)
    print(json.dumps(result))
    return (
        0
        if result["all_expected_exits"] and result.get("content_coverage_exit", 0) == 0
        else 1
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=[
            "setup",
            "probe",
            "fixtures",
            "controls",
            "assets",
            "convert",
            "chunks",
            "check-isolation",
            "evaluate",
            "report",
        ],
    )
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--uv", type=Path)
    parser.add_argument("--asset-manifest", type=Path)
    parser.add_argument("--case")
    parser.add_argument("--include-furniture", action="store_true")
    parser.add_argument("--chunk-tokens", type=int, nargs="+", default=[512])
    parser.add_argument("--raw-chunker-defaults", action="store_true")
    parser.add_argument("--enforce-admission", action="store_true")
    parser.add_argument(
        "--document-profile",
        choices=["raw", "admitted", "body-furniture"],
        default="admitted",
    )
    parser.add_argument("--raw-defaults", action="store_true")
    args = parser.parse_args()
    root = args.run_root.resolve(strict=True)
    require(
        root == args.run_root
        and root.name.startswith("docling-behavior-")
        and root.parent.name == "runs"
        and root.parent.parent.name == ".friday_test",
        "Explicit private behavior run required",
    )
    require(
        not {".friday", ".friday-old", ".venv", ".git", "exports"}.intersection(
            root.parts
        ),
        "Protected run ancestor refused",
    )
    for name in (
        "config",
        "logs",
        "reports",
        "target",
        "cache",
        "tmp",
        "assets",
        "inputs",
        "source",
    ):
        folder = root / name
        require(
            folder.is_dir() and folder.resolve() == folder,
            "Physical private run folders required",
        )
    require(
        sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.flags.dont_write_bytecode == 1,
        "Use base Python -I -S -B",
    )
    if args.command == "setup":
        require(
            args.uv is not None and args.uv.is_file(), "Explicit existing uv required"
        )
        return setup(root, args.uv)
    if args.command == "fixtures":
        return prepare_inputs(root)
    if args.command == "controls":
        return prepare_controls(root)
    if args.command == "assets":
        require(args.asset_manifest is not None, "Explicit asset manifest required")
        return fetch_assets(root, args.asset_manifest)
    if args.command == "convert":
        require(args.case is not None, "Explicit generated case required")
        return convert_case(
            root, args.case, args.include_furniture, args.enforce_admission
        )
    if args.command == "chunks":
        return chunk_cases(
            root, args.chunk_tokens, args.raw_chunker_defaults, args.document_profile
        )
    if args.command == "check-isolation":
        return check_isolation(root)
    if args.command == "evaluate":
        return evaluate(root, args.chunk_tokens, args.raw_defaults)
    if args.command == "report":
        return summarize(root)
    return probe(root)


if __name__ == "__main__":
    raise SystemExit(main())
