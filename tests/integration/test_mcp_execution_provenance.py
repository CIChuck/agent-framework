"""Local two-peer Chat execution through typed Core/SQLite/export boundaries."""

import asyncio
import contextlib
import io
import json
import sys
from pathlib import Path

import pytest
from friday_chat.adapters import FrameworkTranscriptAdapter
from friday_chat.config import FridayChatConfig
from friday_chat.runtime import FakeChatModel, build_runtime
from friday_chat.tools.mcp import MCPChatRegistry
from friday_chat.turns.models import ChatModelResponse, ToolCallRequest
from friday_chat.turns.processor import TurnProcessor
from friday_core.mcp import MCPToolCallProvenance
from friday_transcript import JSONLExporter, SQLiteTranscriptStore, TranscriptEntry

PEER = (
    Path(__file__).resolve().parents[2]
    / "packages/friday-chat/tests_chat/fixtures/mcp_execution_peer.py"
)


@pytest.mark.asyncio
@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize("fallback", [False, True])
async def test_two_peers_later_native_reuse_persists_exact_execution_pairs(
    tmp_path, monkeypatch, streaming, fallback
):
    children = []
    spawn = asyncio.create_subprocess_exec

    async def track(*args, **kwargs):
        child = await spawn(*args, **kwargs)
        children.append(child)
        return child

    monkeypatch.setattr(asyncio, "create_subprocess_exec", track)
    configuration = FridayChatConfig.model_validate(
        {
            "transcript": {"capture_raw_prompts": True},
            "tools": {
                "loop": {"max_iterations": 2},
                "context": {"max_budget_ratio": 1.0},
                "providers": {
                    "mcp": {
                        "enabled": True,
                        "mode": "all",
                        "config": {
                            "servers": [
                                {
                                    "name": name,
                                    "command": sys.executable,
                                    "args": [str(PEER)],
                                    "required": True,
                                }
                                for name in ("peer_a", "peer_b")
                            ],
                            "limits": {
                                "max_result_bytes": 256,
                                "min_memory_retrieval_tokens": 100,
                                "reserved_tool_result_tokens": 80,
                            },
                        },
                    }
                },
            },
        }
    )
    runtime = build_runtime(configuration)
    bridge = MCPChatRegistry(
        runtime.tools, configuration.tools.mcp_provider, str(tmp_path)
    )
    runtime.tools = runtime.mcp_tools = bridge
    store = SQLiteTranscriptStore(tmp_path / "later-native.sqlite")
    runtime.transcript = FrameworkTranscriptAdapter(
        store, configuration, "later-native"
    )
    names = ("mcp_peer_a_read_file", "mcp_peer_b_other_tool")
    executed = []
    original = bridge.registry.get_callable

    def counted(name):
        function = original(name)

        async def invoke(**arguments):
            executed.append((name, arguments))
            return await function(**arguments)

        return invoke

    monkeypatch.setattr(bridge.registry, "get_callable", counted)
    model = FakeChatModel(
        "fake",
        responses=[
            ChatModelResponse(
                tool_calls=(
                    ToolCallRequest(names[0], {"case": "success"}, "shared"),
                    ToolCallRequest(names[1], {"case": "success"}, "shared"),
                )
            ),
            ChatModelResponse(
                tool_calls=(
                    ToolCallRequest("echo", {"text": "native exact"}, "shared"),
                    ToolCallRequest(names[0], {"case": "success"}, None),
                    ToolCallRequest(names[1], {"case": "success"}, "bad/id"),
                )
            ),
            ChatModelResponse(tool_calls=(ToolCallRequest(names[0], {}, "shared"),))
            if fallback
            else ChatModelResponse.from_text("done"),
        ],
    )
    runtime.chat_llm = model
    initial_tasks = set(asyncio.all_tasks())
    chunks = []

    async def capture(text):
        chunks.append(text)

    try:
        await runtime.start_mcp_tools()
        runtime.tool_selection.inject_manual((*names, "echo"))
        processor = TurnProcessor(runtime)
        result = (
            await processor.process_streaming("synthetic", on_chunk=capture)
            if streaming
            else await processor.process("synthetic")
        )
        assert executed == [(name, {"case": "success"}) for name in names * 2]
        assert len(result.tool_calls) == 5
        assert len({r.call_id for r in result.tool_calls}) == 5
        assert result.tool_calls[2].call_id == "shared"
        assert result.tool_calls[2].arguments == {"text": "native exact"}
        assert result.tool_calls[2].result == "native exact"
        records = [r for r in result.tool_calls if r.mcp_provenance is not None]
        assert [r.mcp_provenance.tool.original_name for r in records] == [
            "Read.File",
            "Other.Tool",
            "Read.File",
            "Other.Tool",
        ]
        retained = model.calls[-1]
        requests = [
            c
            for m in retained
            if m.get("role") == "assistant"
            for c in m.get("tool_calls", [])
        ]
        outputs = [m for m in retained if m.get("role") == "tool"]
        assert [c["id"] for c in requests] == [r.call_id for r in result.tool_calls]
        assert [m["tool_call_id"] for m in outputs] == [
            r.call_id for r in result.tool_calls
        ]
        entry = (await store.get_entries("later-native"))[0]
        assert len(entry.tool_calls) == 5
        output = io.StringIO()
        await JSONLExporter(store).export_session("later-native", output)
        exported = json.loads(output.getvalue().splitlines()[-1])
        roundtrip = TranscriptEntry.model_validate(exported)
        assert roundtrip.tool_calls == entry.tool_calls
        assert roundtrip.tool_results == entry.tool_results
        for call, tool_result in zip(entry.tool_calls, entry.tool_results, strict=True):
            if call.mcp_provenance is not None:
                assert call.mcp_provenance == tool_result.mcp_provenance
                assert (
                    call.id == call.mcp_provenance.call_id == tool_result.tool_call_id
                )
                assert call.mcp_provenance.transcript_correlation_id == entry.id
        assert (
            result.assistant_message.startswith("Tool results:")
            if fallback
            else (result.assistant_message == "done")
        )
        await bridge.stop()
        assert bridge.tool_metadata == {} and bridge.provider.owned_tool_names == ()
        assert bridge.provider.manager.connected_servers == []
        assert len(children) == 2 and all(
            child.returncode is not None
            and child.stdout.at_eof()
            and child.stderr.at_eof()
            for child in children
        )
        assert not [t for t in asyncio.all_tasks() - initial_tasks if not t.done()]
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
                asyncio.gather(drain(child.stdout), drain(child.stderr)), 2
            )
            await asyncio.wait_for(child.wait(), 2)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "case, status, code",
    [
        ("success", "succeeded", None),
        ("large", "succeeded", None),
        ("unsafe", "blocked", "output_rejected"),
        ("error", "failed", "tool_error"),
    ],
)
async def test_two_peer_turn_roundtrips_exact_distinct_provenance_and_native_compatibility(
    tmp_path, monkeypatch, caplog, case, status, code
):
    children = []
    spawn = asyncio.create_subprocess_exec

    async def track(*args, **kwargs):
        child = await spawn(*args, **kwargs)
        children.append(child)
        return child

    monkeypatch.setattr(asyncio, "create_subprocess_exec", track)
    config = FridayChatConfig.model_validate(
        {
            "transcript": {"capture_raw_prompts": True},
            "tools": {
                "context": {"max_budget_ratio": 1.0},
                "providers": {
                    "mcp": {
                        "enabled": True,
                        "mode": "all",
                        "config": {
                            "servers": [
                                {
                                    "name": name,
                                    "command": sys.executable,
                                    "args": [str(PEER)],
                                    "required": True,
                                }
                                for name in ["peer_a", "peer_b"]
                            ],
                            "limits": {
                                "max_result_bytes": 256,
                                "min_memory_retrieval_tokens": 100,
                                "reserved_tool_result_tokens": 80,
                            },
                        },
                    }
                },
            },
        }
    )
    runtime = build_runtime(config)
    bridge = MCPChatRegistry(runtime.tools, config.tools.mcp_provider, str(tmp_path))
    runtime.tools = bridge
    runtime.mcp_tools = bridge
    store = SQLiteTranscriptStore(tmp_path / "integration.sqlite")
    runtime.transcript = FrameworkTranscriptAdapter(
        store, config, "integration-session"
    )
    initial_tasks = set(asyncio.all_tasks())
    try:
        await runtime.start_mcp_tools()
        runtime.tool_selection.inject_manual(
            ("mcp_peer_a_read_file", "mcp_peer_b_other_tool", "echo")
        )
        runtime.chat_llm = FakeChatModel(
            "fake",
            responses=[
                ChatModelResponse(
                    tool_calls=(
                        ToolCallRequest(
                            "mcp_peer_a_read_file",
                            {"case": case, "value": "WS05_ARGUMENT_SECRET"},
                            "same",
                        ),
                        ToolCallRequest(
                            "mcp_peer_b_other_tool", {"case": "success"}, "same"
                        ),
                        ToolCallRequest("echo", {"text": "native"}, "native-call"),
                    )
                ),
                ChatModelResponse.from_text("done"),
            ],
        )
        result = await TurnProcessor(runtime).process("synthetic integration")
        assert (
            len(result.tool_calls) == 3
            and len({c.call_id for c in result.tool_calls}) == 3
        )
        assert result.tool_calls[0].mcp_provenance.status == status
        assert result.tool_calls[0].mcp_provenance.failure_code == code
        assert result.tool_calls[0].mcp_provenance.tool.server_name == "peer_a"
        assert result.tool_calls[1].mcp_provenance.tool.server_name == "peer_b"
        assert result.tool_calls[1].mcp_provenance.tool.original_name == "Other.Tool"
        assert (
            result.tool_calls[2].mcp_provenance is None
            and result.tool_calls[2].result == "native"
        )
        entry = (await store.get_entries("integration-session"))[0]
        output = io.StringIO()
        await JSONLExporter(store).export_session("integration-session", output)
        exported = json.loads(output.getvalue().splitlines()[-1])
        for call, tool_result in zip(
            exported["tool_calls"][:2], exported["tool_results"][:2], strict=True
        ):
            provenance = MCPToolCallProvenance.model_validate_json(
                json.dumps(call["mcp_provenance"])
            )
            assert provenance.transcript_correlation_id == entry.id
            assert provenance == MCPToolCallProvenance.model_validate_json(
                json.dumps(tool_result["mcp_provenance"])
            )
            assert (
                call["arguments"] == {}
                and provenance.model_result_size_bytes
                == len(tool_result["output"].encode())
                <= 256
            )
            assert (
                provenance.ingestion_decision == "disabled"
                and not provenance.memory_ingested
            )
        assert "mcp_provenance" not in exported["tool_calls"][2]
        combined = (
            output.getvalue()
            + repr(result)
            + caplog.text
            + repr(await store.get_context_log_for_session("integration-session"))
        )
        assert all(
            s not in combined
            for s in [
                "WS05_ARGUMENT_SECRET",
                "WS05_PROTOCOL_ENV_HEADER_SECRET",
                "WS05_UNSAFE_OUTPUT_SECRET",
            ]
        )
        await bridge.stop()
        assert bridge.tool_metadata == {} and bridge.provider.owned_tool_names == ()
        assert bridge.provider.manager.connected_servers == []
        assert len(children) == 2 and all(
            c.returncode is not None and c.stdout.at_eof() and c.stderr.at_eof()
            for c in children
        )
        assert not [t for t in asyncio.all_tasks() - initial_tasks if not t.done()]
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
                asyncio.gather(drain(child.stdout), drain(child.stderr)), 2
            )
            await asyncio.wait_for(child.wait(), 2)
