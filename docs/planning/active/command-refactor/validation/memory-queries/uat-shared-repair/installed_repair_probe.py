"""Isolated installed-package proof on disposable graph/Chroma without providers."""

from __future__ import annotations

import asyncio
import json
import os
import socket
import sys
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def origins() -> dict[str, str]:
    files = {
        name: str(Path(module.__file__).resolve())
        for name, module in list(sys.modules.items())
        if name.startswith("friday_") and getattr(module, "__file__", None)
    }
    require(
        all(Path(file).is_relative_to(sys.prefix) for file in files.values()),
        "Source injection",
    )
    return files


def headless() -> dict:
    class NoFrontends:
        def find_spec(self, fullname, *_args):
            if fullname.split(".")[0] in {
                "friday_chat",
                "friday_commands",
                "friday_tui",
            }:
                raise RuntimeError("Frontend dependency: " + fullname)

    sys.meta_path.insert(0, NoFrontends())
    from friday_memory.ingestion.metadata import build_ingested_file_metadata

    for description in [None, "", "project notes"]:
        expected = {"source": "fixture.txt", "type": "ingested_file"}
        if description is not None:
            expected["description"] = description
        require(
            build_ingested_file_metadata("fixture.txt", description) == expected,
            "Metadata rule",
        )
    return {"mode": "headless", "passed": True, "origins": origins()}


async def functional(root: Path) -> dict:
    from friday_chat import adapters
    from friday_chat.adapters import FrameworkEmbeddingService
    from friday_chat.commands.contracts import CommandContext
    from friday_chat.commands.registry import build_default_registry
    from friday_chat.config import FridayChatConfig
    from friday_chat.runtime import build_runtime
    from friday_llm import LiteLLMEmbeddingService
    from friday_memory.models.graph import GraphEdge, GraphNode, ProvenanceMetadata

    class LocalEmbedding(LiteLLMEmbeddingService):
        def __init__(self):
            pass

        async def embed_query(self, text):
            return [1.0, float(len(text) % 97 + 1), 0.5]

        async def embed_documents(self, texts):
            return [await self.embed_query(text) for text in texts]

    adapters.build_framework_embedding_service = (
        lambda _config: FrameworkEmbeddingService(service=LocalEmbedding())
    )
    config = FridayChatConfig.model_validate(
        {
            "llm": {
                "model": "openai/offline-fixture",
                "api_key": "provider-prohibited",
            },
            "embedding": {
                "model": "openai/offline-fixture",
                "api_key": "provider-prohibited",
            },
            "memory": {
                "persist_directory": str(root / "vector"),
                "context_window": 4096,
                "output_buffer": 512,
            },
            "transcript": {"export_directory": str(root / "transcript")},
            "maintenance": {
                "backup_directory": str(root / "recovery"),
                "logging": {"log_directory": str(root / "logs")},
            },
            "lifecycle": {
                "enabled": True,
                "access_buffer": {
                    "enabled": True,
                    "wal_path": str(root / "access.wal"),
                },
            },
            "tools": {"enabled": False},
        }
    )
    runtime = build_runtime(config, fake=False, session_id="offline-repair")
    for path in runtime.maintenance_layout.all_declared_paths:
        require(path.resolve().is_relative_to(root), "Store path escaped private root")
    memory = runtime.memory
    registry = build_default_registry()

    async def command(text):
        handled, result = await registry.execute(text, CommandContext(runtime=runtime))
        require(handled and result is not None, "Command dispatch failed")
        return result.output

    provenance = ProvenanceMetadata(source_id="offline", source_type="document")
    labels = ["Chuck", "Peano Arithmetic (PA)", "Kurt Gödel", "nodes", "O'Brien"]
    for index, label in enumerate(labels):
        require(
            await memory.graph_store.add_node(
                GraphNode(
                    id=str(index), type="Entity", label=label, provenance=provenance
                )
            ),
            "Node seed failed",
        )
    require(
        await memory.graph_store.add_edge(
            GraphEdge(
                source_id="0", target_id="2", relation="knows", provenance=provenance
            )
        ),
        "Edge seed failed",
    )
    selections = {}
    for label in labels:
        if label == "nodes":
            continue
        outputs = [
            await command(f"/entities {quote}{label}{quote}")
            for quote in ["", '"', "'"]
        ]
        require(outputs[0] == outputs[1] == outputs[2], "Quoted selection differs")
        require(
            outputs[0].startswith(f"Entities:\n- {label} (Entity)"),
            "Wrong node selected",
        )
        selections[label] = outputs[0]
    require(
        await command('/entities "chuck"') == await command("/entities chuck"),
        "Lowercase lookup differs",
    )
    require(
        "- nodes (Entity)" in await command('/entities "nodes"'),
        "Quoted nodes reclassified",
    )
    nodes = await command("/entities nodes")
    require(
        all(f"- {label} (Entity)" in nodes for label in labels), "Node listing failed"
    )
    for argument in ['""', "''", '" "', '"Chuck', "Peano Arithmetic"]:
        require(
            await command("/entities " + argument) == "No entities found.",
            "Empty/missing name broadened",
        )
    chunks = {}
    for multi in [False, True]:
        source = root / ("batch.txt" if multi else "single.txt")
        source.write_text("many words for chunks.\n" * 500 if multi else "single chunk")
        for suffix in ["", " project notes"]:
            require(
                "Ingested file:" in await command("/ingest " + str(source) + suffix),
                "Ingest command failed",
            )
        empty_count = await memory.ingest_document(
            source_path=str(source), description="", content=source.read_text()
        )
        rows = [
            r["metadata"]
            for r in await memory.collection_manager.short_term.get_all(
                limit=None, where={"type": "ingested_file"}
            )
            if r["metadata"]["source"] == str(source)
        ]
        groups = {}
        for metadata in rows:
            require(metadata["protected"] is True, "Protection lost")
            require(
                "description" not in metadata
                or isinstance(metadata["description"], str),
                "Invalid optional description",
            )
            groups.setdefault(metadata.get("description"), []).append(metadata)
        require(
            set(groups) == {None, "", "project notes"}, "Description groups changed"
        )
        count = len(groups[None])
        require(
            count == empty_count == len(groups[""]) == len(groups["project notes"]),
            "Chunk count changed",
        )
        require((count > 1) is multi, "Wrong ingestion branch")
        if multi:
            require(
                all(
                    sorted(m["chunk_index"] for m in group) == list(range(count))
                    and all(m["chunk_count"] == count for m in group)
                    for group in groups.values()
                ),
                "Chunk metadata changed",
            )
        listing = await command("/list-ingested")
        require(
            listing.count(f"- {source} ({count} chunks): ") == 3,
            "Persisted listing failed",
        )
        require(
            "Ingested file:" in await command("/ingest " + str(source)),
            "Repeat ingest failed",
        )
        docs = [
            d
            for d in (await memory.query_ingested_documents()).documents
            if d.source_path == str(source)
        ]
        require(
            [(d.description, d.chunk_count) for d in docs]
            == [(None, count * 2), ("", count), ("project notes", count)],
            "Repeat grouping changed",
        )
        chunks[source.name] = count
    return {
        "mode": "functional",
        "passed": True,
        "selections": selections,
        "chunks": chunks,
        "origins": origins(),
    }


if __name__ == "__main__":
    mode, output, store = sys.argv[1:]
    root = Path(store).resolve()
    root.mkdir(parents=True)
    os.environ.update(LITELLM_LOCAL_MODEL_COST_MAP="True", ANONYMIZED_TELEMETRY="False")

    def no_network(*_args, **_kwargs):
        raise RuntimeError("Network/provider transport prohibited")

    socket.socket.connect = no_network
    socket.socket.connect_ex = no_network
    socket.create_connection = no_network
    result = headless() if mode == "headless" else asyncio.run(functional(root))
    Path(output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"mode": mode, "passed": True, "optimize": sys.flags.optimize}))
