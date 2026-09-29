"""Two local MCP servers with exact tool opt-in and production memory/transcript."""

import asyncio
import contextlib
import io
import json
import sys
from pathlib import Path

import pytest
from friday_chat.adapters import FrameworkMemoryAdapter, FrameworkTranscriptAdapter
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import FakeChatModel, build_runtime
from friday_chat.tools.mcp import MCPChatRegistry
from friday_chat.turns.models import ChatModelResponse, ToolCallRequest
from friday_chat.turns.processor import TurnProcessor
from friday_memory import (
    CollectionManager,
    InMemoryEpisodicStore,
    MemoryController,
    NullGraphStore,
)
from friday_transcript import JSONLExporter, SQLiteTranscriptStore

PEER = (
    Path(__file__).resolve().parents[2]
    / "packages/friday-chat/tests_chat/fixtures/mcp_execution_peer.py"
)


class Embeddings:
    async def embed_documents(self, texts):
        return [[1.0, 0.0, 0.0, 0.0] for _ in texts]

    async def embed_query(self, text):
        return [1.0, 0.0, 0.0, 0.0]


@pytest.mark.asyncio
@pytest.mark.parametrize("streaming", [False, True])
async def test_real_mixed_turn_only_exact_canonical_tool_is_ingested(
    tmp_path, monkeypatch, streaming
):
    children = []
    spawn = asyncio.create_subprocess_exec

    async def tracked(*args, **kwargs):
        child = await spawn(*args, **kwargs)
        children.append(child)
        return child

    monkeypatch.setattr(asyncio, "create_subprocess_exec", tracked)
    cfg = FridayChatConfig.model_validate(
        {
            "tools": {
                "context": {"max_budget_ratio": 1.0},
                "providers": {
                    "mcp": {
                        "enabled": True,
                        "mode": "all",
                        "config": {
                            "servers": [
                                {
                                    "name": n,
                                    "command": sys.executable,
                                    "args": [str(PEER)],
                                    "required": True,
                                }
                                for n in ("alpha", "beta")
                            ],
                            "limits": {
                                "max_result_bytes": 256,
                                "min_memory_retrieval_tokens": 100,
                                "reserved_tool_result_tokens": 80,
                            },
                            "ingestion": {
                                "long_term_memory_enabled": True,
                                "opted_in_tools": ["mcp_alpha_read_file"],
                            },
                        },
                    }
                },
            }
        }
    )
    runtime = build_runtime(cfg)
    bridge = MCPChatRegistry(runtime.tools, cfg.tools.mcp_provider, str(tmp_path))
    runtime.tools = runtime.mcp_tools = bridge
    manager = CollectionManager(Embeddings(), path=str(tmp_path / "vectors"))
    episodic = InMemoryEpisodicStore()
    graph = NullGraphStore()
    controller = MemoryController(manager.short_term, graph, episodic, manager)
    runtime.memory = FrameworkMemoryAdapter(
        controller, manager, cfg, "integration", episodic, graph
    )
    store = SQLiteTranscriptStore(tmp_path / "transcript.sqlite")
    runtime.transcript = FrameworkTranscriptAdapter(store, cfg, "integration")
    runtime.chat_llm = FakeChatModel(
        "fake",
        responses=[
            ChatModelResponse(
                tool_calls=(
                    ToolCallRequest(
                        "mcp_alpha_read_file", {"case": "success"}, "alpha-call"
                    ),
                    ToolCallRequest("echo", {"text": "native"}, "native-call"),
                    ToolCallRequest(
                        "mcp_beta_read_file", {"case": "success"}, "beta-call"
                    ),
                )
            ),
            ChatModelResponse.from_text("done"),
        ],
    )

    async def capture(text):
        pass

    try:
        await runtime.start_mcp_tools()
        runtime.tool_selection.inject_manual(
            ("mcp_alpha_read_file", "echo", "mcp_beta_read_file")
        )
        processor = TurnProcessor(runtime)
        result = (
            await processor.process_streaming("synthetic", on_chunk=capture)
            if streaming
            else await processor.process("synthetic")
        )
        assert [c.name for c in result.tool_calls] == [
            "mcp_alpha_read_file",
            "echo",
            "mcp_beta_read_file",
        ]
        assert (
            result.tool_calls[1].mcp_provenance is None
            and result.tool_calls[1].result == "native"
        )
        entry = (await store.get_entries("integration"))[0]
        assert entry.tool_calls[0].mcp_provenance.memory_ingested
        assert entry.tool_calls[2].mcp_provenance.ingestion_decision == "skipped"
        stored = await manager.get_mcp_snapshot(
            entry.tool_calls[0].mcp_provenance.memory_correlation_id
        )
        assert stored.state == "committed" and stored.snapshot.matched_grant == "tool"
        assert stored.snapshot.call.tool.server_name == "alpha"
        assert (
            stored.snapshot.transcript_entry_id == entry.id
            and await manager.short_term.count() == 1
        )
        await manager.promote_memory(stored.snapshot.record_id)
        reload = CollectionManager(Embeddings(), path=str(tmp_path / "vectors"))
        assert (
            await reload.get_mcp_snapshot(stored.snapshot.record_id)
        ).snapshot == stored.snapshot
        snippets = await runtime.memory.retrieve("result", token_limit=1024)
        assert any("MCP snapshot server=alpha" in s for s in snippets)
        assert not any("MCP snapshot server=beta" in s for s in snippets)
        output = io.StringIO()
        await JSONLExporter(store).export_session(
            "integration", output, include_metadata=True
        )
        exported = next(
            json.loads(line)
            for line in output.getvalue().splitlines()
            if json.loads(line)["_type"] == "entry"
        )
        assert (
            exported["tool_results"][0]["mcp_provenance"]["memory_correlation_id"]
            == stored.snapshot.record_id
        )
    finally:
        await bridge.stop()

        async def drain(stream):
            if stream:
                while await stream.read(4096):
                    pass

        for child in children:
            if child.returncode is None:
                with contextlib.suppress(ProcessLookupError):
                    child.kill()
            await asyncio.wait_for(
                asyncio.gather(drain(child.stdout), drain(child.stderr), child.wait()),
                3,
            )
    assert all(
        child.returncode is not None and child.stdout.at_eof() and child.stderr.at_eof()
        for child in children
    )
    assert bridge.provider.manager.connected_servers == []
