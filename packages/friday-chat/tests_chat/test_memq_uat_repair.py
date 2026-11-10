"""Real graph/Chroma regressions for shared entity/ingestion repairs."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from friday_chat.adapters import FrameworkMemoryAdapter
from friday_chat.commands.contracts import CommandContext
from friday_chat.commands.registry import _parse_command_input, build_default_registry
from friday_memory.models.graph import GraphEdge, GraphNode, ProvenanceMetadata
from test_memory_diagnostics_commands import (
    prohibit_provider_and_network_transports as prohibit_provider_and_network_transports,
)


@pytest.fixture
def repair_runtime(tmp_path, monkeypatch):
    from test_memory_diagnostics_commands import production_runtime

    return production_runtime.__wrapped__(tmp_path, monkeypatch)


async def command(runtime, text):
    handled, result = await build_default_registry().execute(
        text, CommandContext(runtime=runtime)
    )
    assert handled and result is not None
    return result.output


@pytest.mark.asyncio
async def test_real_graph_quoted_names_select_the_same_nodes_and_relationships(
    repair_runtime, monkeypatch
):
    memory = repair_runtime.memory
    labels = [
        "Chuck",
        "Peano Arithmetic (PA)",
        "Kurt Gödel",
        "O'Brien",
        "C:\\notes",
        "nodes",
    ]
    provenance = ProvenanceMetadata(source_id="fixture", source_type="document")
    for index, label in enumerate(labels):
        assert await memory.graph_store.add_node(
            GraphNode(id=str(index), type="Entity", label=label, provenance=provenance)
        )
    assert await memory.graph_store.add_edge(
        GraphEdge(source_id="0", target_id="2", relation="knows", provenance=provenance)
    )
    calls = []
    entities, relationships = memory.list_entities, memory.list_relationships

    async def read_entities(name=None):
        calls.append(("entities", name))
        return await entities(name)

    async def read_relationships(name=None):
        calls.append(("relationships", name))
        return await relationships(name)

    monkeypatch.setattr(memory, "list_entities", read_entities)
    monkeypatch.setattr(memory, "list_relationships", read_relationships)
    for label in labels[:-1]:
        outputs = []
        for quote in ["", '"', "'"]:
            calls.clear()
            outputs.append(
                await command(repair_runtime, f"/entities {quote}{label}{quote}")
            )
            assert calls == [("entities", label), ("relationships", label)]
        assert outputs[0] == outputs[1] == outputs[2]
        assert outputs[0].startswith(f"Entities:\n- {label} (Entity)")
    calls.clear()
    assert "- nodes (Entity)" in await command(repair_runtime, '/entities "nodes"')
    assert calls == [("entities", "nodes"), ("relationships", "nodes")]
    calls.clear()
    nodes = await command(repair_runtime, "/entities nodes")
    assert all(f"- {label} (Entity)" in nodes for label in labels)
    assert calls == [("entities", None)]
    calls.clear()
    assert "- nodes (Entity)" in await command(repair_runtime, "/entities NODES")
    assert calls == [("entities", "NODES"), ("relationships", "NODES")]
    assert await command(repair_runtime, '/entities "chuck"') == await command(
        repair_runtime, "/entities chuck"
    )
    for argument in [
        '""',
        "''",
        '" "',
        '"Chuck',
        "\"Chuck'",
        "Peano Arithmetic",
    ]:
        assert (
            await command(repair_runtime, "/entities " + argument)
            == "No entities found."
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("multi", [False, True], ids=["single", "batch"])
@pytest.mark.parametrize("description", [None, "", "project notes"])
async def test_ingest_passes_exact_optional_metadata_to_controller(multi, description):
    adapter = object.__new__(FrameworkMemoryAdapter)
    adapter.config = SimpleNamespace(
        smart_file=SimpleNamespace(chunk_size=32, chunk_overlap=0)
    )
    adapter.controller = AsyncMock()
    count = await adapter._ingest_document(
        source_path="fixture.txt",
        description=description,
        content="many words for chunks.\n" * 20 if multi else "short",
    )
    if multi:
        adapter.controller.store_document.assert_not_called()
        adapter.controller.store_documents_batch.assert_awaited_once()
        args, kwargs = adapter.controller.store_documents_batch.call_args
        assert len(args[0]) == len(args[1]) == count > 1
        metadatas = args[1]
    else:
        adapter.controller.store_documents_batch.assert_not_called()
        adapter.controller.store_document.assert_awaited_once()
        args, kwargs = adapter.controller.store_document.call_args
        assert args[0] == "short" and count == 1
        metadatas = [args[1]]
    assert kwargs == {"protected": True}
    for index, metadata in enumerate(metadatas):
        expected = {"source": "fixture.txt", "type": "ingested_file"}
        if description is not None:
            expected["description"] = description
        if multi:
            expected.update(chunk_index=index, chunk_count=count)
        assert metadata == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("multi", [False, True], ids=["single", "batch"])
async def test_real_ingest_absent_empty_and_explicit_descriptions(
    repair_runtime, tmp_path, multi
):
    memory = repair_runtime.memory
    source = tmp_path / "fixture.txt"
    source.write_text("many words for chunks.\n" * 500 if multi else "single chunk")
    content = source.read_text()
    for suffix in ["", " project notes"]:
        assert "Ingested file:" in await command(
            repair_runtime, "/ingest " + str(source) + suffix
        )
    empty_count = await memory.ingest_document(
        source_path=str(source), description="", content=content
    )
    records = await memory.collection_manager.short_term.get_all(
        limit=None, where={"type": "ingested_file"}
    )
    groups = {}
    for record in records:
        metadata = record["metadata"]
        assert metadata["source"] == str(source)
        assert metadata["type"] == "ingested_file"
        assert metadata["protected"] is True
        assert "description" not in metadata or isinstance(metadata["description"], str)
        groups.setdefault(metadata.get("description"), []).append(metadata)
    assert set(groups) == {None, "", "project notes"}
    count = len(groups[None])
    assert count == empty_count == len(groups[""]) == len(groups["project notes"])
    assert (count > 1) is multi
    for values in groups.values():
        if multi:
            assert sorted(row["chunk_index"] for row in values) == list(range(count))
            assert all(row["chunk_count"] == count for row in values)
        else:
            assert all(
                "chunk_index" not in row and "chunk_count" not in row for row in values
            )
    result = await memory.query_ingested_documents()
    assert [(row.description, row.chunk_count) for row in result.documents] == [
        (None, count),
        ("", count),
        ("project notes", count),
    ]
    listing = await command(repair_runtime, "/list-ingested")
    assert listing.count(f"- {source} ({count} chunks): ") == 3
    assert "project notes" in listing
    assert "Ingested file:" in await command(repair_runtime, "/ingest " + str(source))
    result = await memory.query_ingested_documents()
    assert [(row.description, row.chunk_count) for row in result.documents] == [
        (None, count * 2),
        ("", count),
        ("project notes", count),
    ]


def test_global_whitespace_parser_keeps_other_command_and_raw_args():
    assert _parse_command_input('/entities "Peano Arithmetic (PA)"') == (
        "entities",
        ('"Peano', "Arithmetic", '(PA)"'),
    )
    assert _parse_command_input('/read "a b.txt"') == ("read", ('"a', 'b.txt"'))
