"""Explicit isolated Docling -> Friday-LLM -> Memory/Chroma readiness test."""

from __future__ import annotations

import argparse
import asyncio
import base64
import datetime as dt
import fcntl
import hashlib
import importlib.metadata
import json
import math
import os
import struct
import sys
import time
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx

MODEL = "text-embedding-nomic-embed-text-v1.5"
ORIGIN = "http://127.0.0.1:1234"
CASES = (
    "pdf-native.pdf",
    "pdf-scanned.pdf",
    "docx-long.docx",
    "xlsx-values.xlsx",
    "pptx-notes.pptx",
    "corrupt.pdf",
    "xlsx-formula-missing.xlsx",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def obj(value: object) -> dict[str, object]:
    require(isinstance(value, dict), "Object required")
    if not isinstance(value, dict):
        raise ValueError("Object required")
    require(all(isinstance(key, str) for key in value), "Text keys required")
    result: dict[str, object] = dict(value)
    return result


def array(value: object) -> list[object]:
    if not isinstance(value, list):
        raise ValueError("Array required")
    return list(value)


def text(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Text required")
    return value


def integer(value: object) -> int:
    if type(value) is not int:
        raise ValueError("Integer required")
    return value


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read(path: Path) -> dict[str, object]:
    return obj(json.loads(path.read_bytes()))


def write(path: Path, value: object, *, immutable: bool = False) -> None:
    require(
        path.parent.resolve() == path.parent and not path.is_symlink(), "Output alias"
    )
    require(not path.exists() or path.stat().st_nlink == 1, "Output hardlink")
    raw = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    if immutable:
        with path.open("x") as stream:
            stream.write(raw)
    else:
        temporary = path.with_name(path.name + f".{time.time_ns()}.tmp")
        with temporary.open("x") as stream:
            stream.write(raw)
        temporary.replace(path)


def private_root(path: Path) -> Path:
    root = path.resolve(strict=True)
    require(
        root == path
        and root.name.startswith("docling-behavior-e2e-")
        and root.parent.name == "runs"
        and root.parent.parent.name == ".friday_test",
        "Explicit physical end-to-end run required",
    )
    require(
        not {".friday", ".friday-old", ".venv", ".git", "exports"}.intersection(
            root.parts
        ),
        "Protected root ancestor",
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
            "Physical run folders required",
        )
    return root


def model_state(value: object) -> dict[str, object]:
    rows = [obj(row) for row in array(obj(value).get("models"))]
    selected = [
        row
        for row in rows
        if row.get("type") == "embedding"
        and any(
            obj(instance).get("id") == MODEL
            for instance in array(row.get("loaded_instances"))
        )
    ]
    require(len(selected) == 1, "Exact Nomic instance not loaded")
    row = selected[0]
    instance = next(
        obj(item)
        for item in array(row["loaded_instances"])
        if obj(item).get("id") == MODEL
    )
    context = integer(obj(instance.get("config")).get("context_length"))
    maximum = integer(row.get("max_context_length"))
    require(context == 2048 and maximum >= context, "Loaded model context changed")
    loaded = sorted(
        text(obj(item)["id"])
        for entry in rows
        for item in array(entry.get("loaded_instances"))
    )
    return {
        "model": MODEL,
        "context": context,
        "loaded_digest": sha(json.dumps(loaded).encode()),
    }


def validated_vectors(value: object, expected: int) -> list[list[float]]:
    require(type(expected) is int and expected > 0, "Positive response count required")
    payload = obj(value)
    require(payload.get("model") == MODEL, "Response model mismatch")
    rows = array(payload.get("data"))
    require(len(rows) == expected, "Response vector count mismatch")
    vectors: list[list[float]] = []
    for index, item in enumerate(rows):
        row = obj(item)
        require(
            type(row.get("index")) is int and row["index"] == index,
            "Response vector order mismatch",
        )
        encoded = row.get("embedding")
        if isinstance(encoded, str):
            raw = base64.b64decode(encoded, validate=True)
            require(len(raw) == 768 * 4, "Encoded vector dimensions mismatch")
            values: list[object] = list(struct.unpack("<768f", raw))
        else:
            values = array(encoded)
        require(len(values) == 768, "Response dimensions mismatch")
        vector: list[float] = []
        for number in values:
            if isinstance(number, bool) or not isinstance(number, (int, float)):
                raise ValueError("Non-numeric vector component")
            require(math.isfinite(number), "Non-finite vector component")
            vector.append(float(number))
        require(any(number != 0 for number in vector), "Zero vector")
        vectors.append(vector)
    return vectors


class Budget:
    def __init__(self, root: Path) -> None:
        self.path = root / "reports/live-budget.json"

    def charge(self, vectors: int = 0, tokens: int = 0) -> int:
        require(
            type(vectors) is int
            and 0 <= vectors <= 64
            and type(tokens) is int
            and 0 <= tokens <= 131072,
            "Invalid request reservation",
        )
        lock_path = self.path.with_suffix(".lock")
        require(not lock_path.is_symlink(), "Budget lock alias")
        with lock_path.open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            state = read(self.path)
            require(
                all(
                    integer(state[key]) >= 0
                    for key in ("requests", "vectors", "tokens")
                ),
                "Invalid budget state",
            )
            requests = integer(state["requests"]) + 1
            total_vectors = integer(state["vectors"]) + vectors
            total_tokens = integer(state["tokens"]) + tokens
            require(
                requests <= 64 and total_vectors <= 256 and total_tokens <= 131072,
                "Live window budget exhausted",
            )
            state.update(requests=requests, vectors=total_vectors, tokens=total_tokens)
            write(self.path, state)
            return requests


def store_path(root: Path, run_id: str, recorded: object | None = None) -> Path:
    require(
        len(run_id) == 32 and all(ch in "0123456789abcdef" for ch in run_id),
        "Store run identity",
    )
    path = root / "stores" / run_id
    require(
        path.parent.is_dir()
        and path.parent.resolve() == path.parent
        and path.resolve() == path,
        "Store path alias",
    )
    if recorded is not None:
        require(
            text(recorded) == str(path) and path.is_dir(),
            "Store outside owned run refused",
        )
    return path


def runtime(root: Path, *, live: bool) -> None:
    """Private imports/files; actual model routes also guarded at HTTP transport."""
    from ingest.behavior import environment

    clean = environment(root)
    clean.update(
        HF_HUB_OFFLINE="1",
        TRANSFORMERS_OFFLINE="1",
        DISABLE_AIOHTTP_TRANSPORT="True",
        DISABLE_AIOHTTP_TRUST_ENV="True",
        ANONYMIZED_TELEMETRY="False",
        OTEL_SDK_DISABLED="true",
        SSL_CERT_FILE=str(root / "target/certifi/cacert.pem"),
        REQUESTS_CA_BUNDLE=str(root / "target/certifi/cacert.pem"),
    )
    os.environ.clear()
    os.environ.update(clean)
    sys.path.insert(0, str(root / "target"))
    import mimetypes

    mimetypes.knownfiles = []
    mimetypes.init(files=[])
    server_config = Path(
        "/Users/chuckrussell/.lmstudio/.internal/http-server-config.json"
    )

    def audit(event: str, args: tuple[object, ...]) -> None:
        if event in {
            "subprocess.Popen",
            "os.system",
            "os.posix_spawn",
            "os.exec",
            "socket.sendto",
        }:
            raise PermissionError("End-to-end worker forbids child/UDP effects")
        if event in {"socket.connect", "socket.getaddrinfo"}:
            address = args[1] if event == "socket.connect" else args[:2]
            require(
                live
                and isinstance(address, tuple)
                and address[:2] == ("127.0.0.1", 1234),
                "Network outside selected model endpoint refused",
            )
        if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(args[0])).resolve()
            if path == Path("/dev/null"):
                return
            mode, flags = args[1:3]
            writing = isinstance(mode, str) and any(ch in mode for ch in "wax+")
            writing = (
                writing
                or isinstance(flags, int)
                and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
            )
            allowed = (
                (root,)
                if writing
                else (
                    root,
                    Path(sys.base_prefix).resolve(),
                    Path(__file__).resolve(),
                    server_config,
                    Path("/System/Library/CoreServices/SystemVersion.plist"),
                )
            )
            require(
                any(path == item or item in path.parents for item in allowed),
                "Worker filesystem escape: " + str(path),
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
            for item in (
                args[:2]
                if event in {"os.rename", "os.link", "os.symlink"}
                else args[:1]
            ):
                if isinstance(item, (str, bytes, os.PathLike)):
                    path = Path(os.fsdecode(item)).resolve()
                    require(
                        path == root or root in path.parents, "Worker mutation escape"
                    )

    sys.addaudithook(audit)


def window(root: Path) -> dict[str, object]:
    value = read(root / "config/operator-window.json")
    require(
        value.get("production_stopped") is True
        and value.get("already_loaded_model") == MODEL
        and value.get("origin") == ORIGIN,
        "Wrong operator window",
    )
    now = dt.datetime.now(dt.UTC)
    expiry = dt.datetime.fromisoformat(text(value["expires_at_utc"]))
    require(expiry.tzinfo is not None and now < expiry, "Operator model window expired")
    config = read(
        Path("/Users/chuckrussell/.lmstudio/.internal/http-server-config.json")
    )
    require(
        config.get("justInTimeModelLoading") is False, "JIT loading is not disabled"
    )
    return value


def corpus(root: Path, run_id: str) -> dict[str, object]:
    from ingest import behavior

    expected = read(root / "reports/chunking.json")
    require(
        expected.get("document_profile") == "admitted",
        "Admitted chunk profile required",
    )
    require(behavior.summarize(root) == 0, "Current chunk content refused")
    entries: list[dict[str, object]] = []
    for item in array(expected["results"]):
        row = obj(item)
        name = text(row["source"])
        limit = integer(row["limit"])
        if row["strategy"] != "document" or not (
            limit == 512 or limit == 128 and name == "docx-long.docx.json"
        ):
            continue
        require(
            row.get("status") == "pass" and Path(name).name == name,
            "Unsafe chunk evidence",
        )
        chunks = read(root / "reports/chunks" / f"{name}.document.{limit}.json")
        for index, value in enumerate(array(chunks["chunks"])):
            chunk = obj(value)
            raw = text(chunk["text"])
            require(
                raw.strip() != "" and "content placeholder" not in raw.lower(),
                "Empty/placeholder content",
            )
            entries.append(
                {
                    "id": f"{run_id}-{limit}-{len(entries)}",
                    "source": name,
                    "budget": limit,
                    "chunk": index,
                    "text": raw,
                    "text_sha256": sha(raw.encode()),
                }
            )
    require(
        bool(entries) and any(row["budget"] == 128 for row in entries),
        "Default/override corpus absent",
    )
    result = {
        "run_id": run_id,
        "entries": entries,
        "conversion_attempts": expected["conversion_attempts"],
        "e2e_sha256": sha(Path(__file__).read_bytes()),
        "embedding_requests": 0,
    }
    write(root / "reports/e2e" / (run_id + ".corpus.json"), result, immutable=True)
    return result


async def embed(root: Path, run_id: str) -> None:
    runtime(root, live=True)
    import httpx
    import litellm
    from friday_llm import LiteLLMEmbeddingService
    from friday_llm.config import ResilienceConfig
    from friday_memory.adapters.vector import ChromaVectorStore
    from friday_memory.ingestion.metadata import build_ingested_file_metadata
    from packaging.version import Version
    from tokenizers import Tokenizer

    require(
        Version(importlib.metadata.version("certifi")) >= Version("2026.10.19"),
        "Certifi floor",
    )
    for name in ("friday_llm", "friday_memory", "litellm", "chromadb"):
        require(
            root / "target" in Path(sys.modules[name].__file__ or "").resolve().parents,
            "Unexpected package origin",
        )
    data = read(root / "reports/e2e" / (run_id + ".corpus.json"))
    require(
        data["e2e_sha256"] == sha(Path(__file__).read_bytes()),
        "Corpus code identity mismatch",
    )
    from ingest.behavior import admitted_document

    for name, attempt in obj(data["conversion_attempts"]).items():
        require(Path(name).name == name, "Unsafe conversion source")
        raw = (root / "reports/admitted/documents" / name).read_bytes()
        require(
            admitted_document(root, name.removesuffix(".json"), raw)["attempt"]
            == attempt,
            "Corpus admission superseded",
        )
    tokenizer = Tokenizer.from_file(str(root / "assets/nomic/tokenizer.json"))
    budget = Budget(root)
    ledger: list[dict[str, object]] = []
    pending: dict[str, object] = {}
    initial = read(root / "config/loaded-model-status.json")
    digest = initial["all_loaded_instances_digest"]

    def count(value: str) -> int:
        return len(tokenizer.encode(value, add_special_tokens=True).ids)

    async def request_hook(request: httpx.Request) -> None:
        window(root)
        require(
            str(request.url).split("/", 3)[:3] == ["http:", "", "127.0.0.1:1234"]
            and not request.url.query,
            "Unexpected HTTP origin/query",
        )
        if request.method == "GET":
            require(request.url.path == "/api/v1/models", "Unexpected status route")
            number = budget.charge()
            pending.clear()
            pending.update(request=number, method="GET")
        else:
            require(
                request.method == "POST" and request.url.path == "/v1/embeddings",
                "Unexpected inference route",
            )
            payload = obj(json.loads(request.content))
            require(payload.get("model") == MODEL, "Wrong wire model")
            values = [text(item) for item in array(payload["input"])]
            require(
                all(
                    item.startswith(("search_document: ", "search_query: "))
                    for item in values
                ),
                "Missing Nomic preparation",
            )
            counts = [count(item) for item in values]
            require(
                0 < len(values) <= 64 and all(0 < value <= 512 for value in counts),
                "Prepared model overflow",
            )
            number = budget.charge(len(values), sum(counts))
            pending.clear()
            pending.update(
                request=number,
                method="POST",
                inputs=len(values),
                local_tokens=sum(counts),
                input_sha256=[sha(item.encode()) for item in values],
            )

    async def response_hook(response: httpx.Response) -> None:
        raw = await response.aread()
        require(
            len(raw) <= 8 * 1024**2 and response.status_code == 200,
            "Model response failure/limit",
        )
        payload = obj(json.loads(raw))
        record = dict(pending)
        if pending["method"] == "GET":
            state = model_state(payload)
            require(state["loaded_digest"] == digest, "Loaded instance set changed")
            record["state"] = state
        else:
            vectors = validated_vectors(payload, integer(pending["inputs"]))
            record.update(dimensions=len(vectors[0]), usage=payload.get("usage"))
        record.update(response_sha256=sha(raw), status=response.status_code)
        ledger.append(record)
        write(root / "reports/e2e" / (run_id + ".http.json"), ledger)

    transport = httpx.AsyncHTTPTransport(retries=0)
    async with httpx.AsyncClient(
        transport=transport,
        trust_env=False,
        follow_redirects=False,
        timeout=60,
        event_hooks={"request": [request_hook], "response": [response_hook]},
    ) as client:
        litellm.disable_aiohttp_transport = True
        litellm.num_retries = 0
        litellm.num_retries_per_request = 0
        litellm.aclient_session = client
        service = LiteLLMEmbeddingService(
            model_name="openai/" + MODEL,
            api_key="local-test-no-auth",
            api_base=ORIGIN + "/v1",
            batch_size=32,
            cache_size=0,
            resilience=ResilienceConfig(max_retries=0, timeout_seconds=60),
        )
        calls = {"embed_documents": 0, "embed_query": 0}

        class Prepared:
            async def embed_documents(self, values: list[str]) -> list[list[float]]:
                require(
                    all(count("search_document: " + value) <= 512 for value in values),
                    "Document overflow",
                )
                result: list[list[float]] = []
                for start in range(0, len(values), 32):
                    calls["embed_documents"] += 1
                    await client.get(ORIGIN + "/api/v1/models")
                    result.extend(
                        await service.embed_documents(
                            [
                                "search_document: " + value
                                for value in values[start : start + 32]
                            ]
                        )
                    )
                    await client.get(ORIGIN + "/api/v1/models")
                return result

            async def embed_query(self, value: str) -> list[float]:
                calls["embed_query"] += 1
                await client.get(ORIGIN + "/api/v1/models")
                result = await service.embed_query("search_query: " + value)
                await client.get(ORIGIN + "/api/v1/models")
                return validated_vectors(
                    {"model": MODEL, "data": [{"index": 0, "embedding": result}]}, 1
                )[0]

        prepared = Prepared()
        directory = store_path(root, run_id)
        directory.mkdir(parents=True, exist_ok=False)
        records = [obj(item) for item in array(data["entries"])]
        collections: list[dict[str, object]] = []
        for limit in (512, 128):
            rows = [row for row in records if row["budget"] == limit]
            require(
                all(
                    count("search_document: " + text(row["text"])) <= limit
                    for row in rows
                ),
                "Collection chunk budget mismatch",
            )
            name = f"ingest-e2e-{run_id}-{limit}"
            store = ChromaVectorStore(
                collection_name=name,
                embedding_function=prepared,
                persist_directory=str(directory),
            )
            require(
                store._client.get_settings().anonymized_telemetry is False,
                "Chroma telemetry not disabled",
            )
            store._collection.modify(configuration={"hnsw": {"num_threads": 4}})
            require(await store.count() == 0, "Fresh collection required")
            metadata = [
                dict(
                    build_ingested_file_metadata(text(row["source"]), None),
                    protected=True,
                    content_sha256=row["text_sha256"],
                    chunk=row["chunk"],
                    chunk_tokens=limit,
                )
                for row in rows
            ]
            require(
                all("description" not in row for row in metadata),
                "Absent-description metadata changed",
            )
            require(
                await store.add_documents(
                    [text(row["text"]) for row in rows],
                    metadata,
                    [text(row["id"]) for row in rows],
                ),
                "Storage refused",
            )
            actual = await store.get_all(limit=None)
            require(
                await store.count() == len(rows) and len(actual) == len(rows),
                "Stored row count",
            )
            expected = {text(row["id"]): row for row in rows}
            for item in actual:
                require(
                    text(item["text"]) == expected[text(item["id"])]["text"]
                    and item["metadata"]["content_sha256"]
                    == expected[text(item["id"])]["text_sha256"]
                    and item["metadata"]["protected"] is True,
                    "Stored source/provenance changed",
                )
            raw_vectors = store._collection.get(include=["embeddings"])["embeddings"]
            require(
                raw_vectors is not None
                and len(raw_vectors) == len(rows)
                and all(
                    len(vector) == 768 and all(math.isfinite(float(x)) for x in vector)
                    for vector in raw_vectors
                ),
                "Persisted vectors invalid",
            )
            queries: list[dict[str, object]] = []
            sources = (
                (
                    "pdf-scanned.pdf.json",
                    "docx-long.docx.json",
                    "xlsx-values.xlsx.json",
                    "pptx-notes.pptx.json",
                )
                if limit == 512
                else ("docx-long.docx.json",)
            )
            for source in sources:
                item = next(row for row in rows if row["source"] == source)
                query = text(item["text"])
                vector = await prepared.embed_query(query)
                before = dict(calls)
                hits = await store.query(
                    query, n_results=min(5, len(rows)), query_embedding=vector
                )
                require(calls == before, "Storage re-embedded precomputed query")
                require(
                    any(hit["metadata"]["source"] == source for hit in hits),
                    "Expected source missing from nearest retrieval",
                )
                queries.append(
                    {
                        "source": source,
                        "query": query,
                        "vector": vector,
                        "ids": [hit["id"] for hit in hits],
                        "source_rank": next(
                            i + 1
                            for i, hit in enumerate(hits)
                            if hit["metadata"]["source"] == source
                        ),
                    }
                )
            collections.append(
                {"name": name, "budget": limit, "rows": rows, "queries": queries}
            )
        result = {
            "run_id": run_id,
            "status": "PASS",
            "e2e_sha256": sha(Path(__file__).read_bytes()),
            "corpus_sha256": sha(
                (root / "reports/e2e" / (run_id + ".corpus.json")).read_bytes()
            ),
            "store_path": str(directory),
            "collections": collections,
            "broker_calls": calls,
            "dimensions": 768,
            "model_context": 2048,
            "http_requests": len(ledger),
            "scope": "readiness flow; production /ingest parser/handler integration remains later",
        }
        write(root / "reports/e2e" / (run_id + ".stored.json"), result, immutable=True)
        litellm.aclient_session = None


async def reopen(root: Path, run_id: str) -> None:
    runtime(root, live=False)
    from friday_memory.adapters.vector import ChromaVectorStore

    data = read(root / "reports/e2e" / (run_id + ".stored.json"))
    require(
        data.get("run_id") == run_id
        and data.get("e2e_sha256") == sha(Path(__file__).read_bytes()),
        "Stored run/code identity changed",
    )
    directory = store_path(root, run_id, data["store_path"])

    class NoEmbedding:
        async def embed_documents(self, values: list[str]) -> list[list[float]]:
            raise RuntimeError("Reopen must not embed")

        async def embed_query(self, value: str) -> list[float]:
            raise RuntimeError("Reopen must not embed")

    checked = 0
    for item in array(data["collections"]):
        collection = obj(item)
        store = ChromaVectorStore(
            collection_name=text(collection["name"]),
            embedding_function=NoEmbedding(),
            persist_directory=str(directory),
        )
        expected = {text(obj(row)["id"]): obj(row) for row in array(collection["rows"])}
        actual = await store.get_all(limit=None)
        require(len(actual) == len(expected), "Reopened row count")
        for row in actual:
            require(
                row["text"] == expected[text(row["id"])]["text"]
                and row["metadata"]["content_sha256"]
                == expected[text(row["id"])]["text_sha256"],
                "Persistence text/provenance mismatch",
            )
        for value in array(collection["queries"]):
            query = obj(value)
            vector = validated_vectors(
                {"model": MODEL, "data": [{"index": 0, "embedding": query["vector"]}]},
                1,
            )[0]
            hits = await store.query(
                text(query["query"]),
                n_results=min(5, len(expected)),
                query_embedding=vector,
            )
            require(
                [hit["id"] for hit in hits] == query["ids"],
                "Reopened retrieval changed",
            )
            checked += 1
    write(
        root / "reports/e2e" / (run_id + ".reopened.json"),
        {"status": "PASS", "run_id": run_id, "queries": checked, "network_requests": 0},
        immutable=True,
    )


def run(root: Path, modes: list[str]) -> int:
    from ingest import behavior

    (root / "reports/e2e").mkdir(exist_ok=True)
    (root / "stores").mkdir(exist_ok=True)
    budget = root / "reports/live-budget.json"
    if not budget.exists():
        write(budget, {"requests": 3, "vectors": 0, "tokens": 0}, immutable=True)
    window(root)
    lock = (root / "reports/e2e-run.lock").open("a")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    outcomes: list[dict[str, object]] = []
    for mode in modes:
        run_id = uuid.uuid4().hex
        source_sha = sha(Path(__file__).read_bytes())
        write(
            root / "reports/e2e" / (mode + ".latest.json"),
            {"run_id": run_id, "source_sha256": source_sha},
        )
        flags = ["-I", "-S", "-B"] + (["-O"] if mode == "optimized" else [])
        commands: list[dict[str, object]] = []
        for case in CASES:
            group = "supplemental" if case == "corrupt.pdf" else "generated"
            require(
                (root / "inputs" / group / case).is_file(), "Prepared fixture missing"
            )
            argv = [
                sys.executable,
                *flags,
                str(root / "source/ingest/behavior.py"),
                "convert",
                "--run-root",
                str(root),
                "--case",
                case,
                "--include-furniture",
                "--enforce-admission",
            ]
            code = behavior.supervise(root, mode + "-e2e-" + case, argv, 300)
            commands.append({"operation": case, "exit": code})
        argv = [
            sys.executable,
            *flags,
            str(root / "source/ingest/behavior.py"),
            "chunks",
            "--run-root",
            str(root),
            "--chunk-tokens",
            "128",
            "512",
        ]
        commands.append(
            {
                "operation": "chunks",
                "exit": behavior.supervise(root, mode + "-e2e-chunks", argv, 300),
            }
        )
        if not all(item["exit"] == 0 for item in commands):
            write(
                root / "reports/e2e" / (run_id + ".result.json"),
                {"status": "FAIL", "run_id": run_id, "commands": commands},
                immutable=True,
            )
            return 1
        corpus(root, run_id)
        for operation in ("embed", "reopen"):
            argv = [
                sys.executable,
                *flags,
                str(Path(__file__).resolve()),
                operation,
                "--run-root",
                str(root),
                "--run-id",
                run_id,
            ]
            code = behavior.supervise(root, mode + "-e2e-" + operation, argv, 600)
            commands.append({"operation": operation, "exit": code})
            if code:
                write(
                    root / "reports/e2e" / (run_id + ".result.json"),
                    {"status": "FAIL", "run_id": run_id, "commands": commands},
                    immutable=True,
                )
                return 1
        evidence = {
            suffix: sha(
                (root / "reports/e2e" / (run_id + "." + suffix + ".json")).read_bytes()
            )
            for suffix in ("corpus", "stored", "reopened", "http")
        }
        outcome: dict[str, object] = {
            "status": "PASS",
            "run_id": run_id,
            "mode": mode,
            "source_sha256": source_sha,
            "commands": commands,
            "evidence": evidence,
        }
        write(root / "reports/e2e" / (run_id + ".result.json"), outcome, immutable=True)
        outcomes.append(outcome)
    print(json.dumps({"modes": outcomes, "budget": read(budget)}))
    return 0


def report(root: Path) -> int:
    results = []
    for mode in ("normal", "optimized"):
        pointer = read(root / "reports/e2e" / (mode + ".latest.json"))
        require(
            pointer["source_sha256"] == sha(Path(__file__).read_bytes()),
            "Report runner changed",
        )
        result = read(root / "reports/e2e" / (text(pointer["run_id"]) + ".result.json"))
        require(
            result.get("status") == "PASS"
            and result.get("run_id") == pointer["run_id"]
            and result.get("mode") == mode
            and result.get("source_sha256") == pointer["source_sha256"]
            and all(obj(item)["exit"] == 0 for item in array(result["commands"])),
            "End-to-end run incomplete/failed",
        )
        require(
            [obj(item).get("operation") for item in array(result["commands"])]
            == [*CASES, "chunks", "embed", "reopen"]
            and set(obj(result["evidence"]))
            == {"corpus", "stored", "reopened", "http"},
            "End-to-end evidence incomplete",
        )
        for suffix, expected in obj(result["evidence"]).items():
            require(
                suffix in {"corpus", "stored", "reopened", "http"}
                and sha(
                    (
                        root
                        / "reports/e2e"
                        / (text(pointer["run_id"]) + "." + suffix + ".json")
                    ).read_bytes()
                )
                == expected,
                "End-to-end evidence changed",
            )
        results.append(result)
    print(
        json.dumps(
            {
                "status": "PASS",
                "modes": results,
                "budget": read(root / "reports/live-budget.json"),
            }
        )
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "embed", "reopen", "report"))
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--run-id")
    parser.add_argument(
        "--mode", choices=("normal", "optimized", "both"), default="both"
    )
    args = parser.parse_args()
    require(
        sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.flags.dont_write_bytecode == 1,
        "Use base Python -I -S -B",
    )
    root = private_root(args.run_root)
    require(
        Path(__file__).resolve() == root / "source/ingest/e2e.py",
        "Execute frozen run source",
    )
    sys.path.insert(0, str(root / "source"))
    if args.command == "run":
        return run(
            root, ["normal", "optimized"] if args.mode == "both" else [args.mode]
        )
    if args.command == "report":
        return report(root)
    require(
        isinstance(args.run_id, str)
        and len(args.run_id) == 32
        and all(c in "0123456789abcdef" for c in args.run_id),
        "Explicit current run identity",
    )
    if args.command == "embed":
        asyncio.run(embed(root, args.run_id))
    else:
        asyncio.run(reopen(root, args.run_id))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
