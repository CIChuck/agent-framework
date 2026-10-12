import pytest
from friday_chat.telemetry import ChatTelemetryObserver
from friday_chat.tools.loop import ToolLoop
from friday_chat.tools.output import MCPOutputPolicy
from friday_chat.tools.registry import FakeToolRegistry
from friday_chat.tools.schemas import ToolDefinition
from friday_chat.turns.telemetry import turn_scope
from friday_core.mcp import MCPToolMetadata


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", [None, "tool_error", "invalid_result", "execution_error", "timeout", "output_rejected"])
async def test_mcp_returned_status_and_correlated_original(failure):
    o = ChatTelemetryObserver(enabled=True, session_id="private")
    name = "mcp_peer_private"
    class Registry(FakeToolRegistry):
        def is_mcp_tool(self, tool):
            return tool == name
        async def call_tool_record(self, tool, arguments, **kwargs):
            o.capture_event("mcp.tool_call_start", {"server_ref": "a" * 16, "tool_ref": "b" * 16, "reason": "success"})
            metadata = MCPToolMetadata(canonical_name=name, server_name="peer", original_name="private", transport="stdio", trust_level="local")
            policy = MCPOutputPolicy(4096)
            return policy.failed_record(metadata, "safe_call", failure) if failure else policy.checked_record(metadata, "safe_call", "safe", arguments)
    with turn_scope(o, "completion"):
        result = await ToolLoop(Registry(), observer=o).run(
            [{"tool_calls": [{"name": name, "arguments": {"PRIVATE_ARG": "PRIVATE"}, "id": "safe_call"}]}],
            [ToolDefinition(name, "PRIVATE_DESCRIPTION")])
    finish = [dict(e.attributes) for e in o.snapshot().events if e.name == "execution.operation_finish"]
    assert finish[0]["outcome"] == ("succeeded" if failure is None else "blocked" if failure == "output_rejected" else "failed")
    terminal = o.execution_snapshot().turns[-1]
    assert terminal.completed_tools == (failure is None)
    assert terminal.failed_tools == (failure is not None)
    original = next(e for e in o.snapshot().events if e.name == "mcp.tool_call_start")
    link = next(e for e in o.snapshot().events if e.name == "execution.mcp_link")
    assert dict(link.attributes)["source_sequence"] == original.sequence
    assert dict(link.attributes)["operation_ref"] == finish[0]["operation_ref"]
    assert dict(original.attributes) == {"server_ref": "a" * 16, "tool_ref": "b" * 16, "reason": "success"}
    assert len(result.tool_calls) == 1 and "PRIVATE_ARG" not in repr(o.snapshot())


@pytest.mark.asyncio
async def test_unknown_and_swallowed_key_error_distinguished():
    o = ChatTelemetryObserver(enabled=True, session_id="private")
    for name in ["absent", "unknown_allowed"]:
        with turn_scope(o, "completion"):
            result = await ToolLoop(FakeToolRegistry(), observer=o).run(
                [{"tool_calls": [{"name": name}]}], [ToolDefinition("unknown_allowed", "safe")])
        assert not result.tool_calls
    finishes = [dict(e.attributes) for e in o.snapshot().events if e.name == "execution.operation_finish"]
    assert len(finishes) == 1 and finishes[0]["reason"] == "unknown_tool"
    assert any(e.name == "execution.selection" for e in o.snapshot().events)


@pytest.mark.asyncio
async def test_mixed_rejections_use_trusted_membership_without_extra_lookups():
    o = ChatTelemetryObserver(enabled=True, session_id="private")
    mcp = "mcp_peer_private"
    class Registry(FakeToolRegistry):
        def __init__(self):
            super().__init__()
            self.lookups = []
            self.dispatches = []
        def is_mcp_tool(self, name):
            self.lookups.append(name)
            return name == mcp
        async def call_tool_record(self, name, arguments, **kwargs):
            self.dispatches.append(name)
            raise AssertionError("rejected call must not dispatch")
    registry = Registry()
    with turn_scope(o, "completion"):
        result = await ToolLoop(registry, observer=o, max_iterations=10).run(
            [{"tool_calls": [{"name": mcp}, {"name": "echo"}, {"name": "unknown"}, {"name": []}]}],
            [ToolDefinition("allowed", "safe")])
    rows = [dict(e.attributes) for e in o.snapshot().events if e.name == "execution.selection"]
    assert [(x["rejected_native"], x["rejected_mcp"]) for x in rows] == [(0, 1), (1, 0), (1, 0), (1, 0)]
    assert all(x["selected_native"] == x["selected_mcp"] == 0 and x["rejection_count"] == 1 for x in rows)
    assert set(registry.lookups) == {mcp, "echo", "unknown", "allowed"}
    assert len(registry.lookups) == 4 and not registry.dispatches and not result.tool_calls
    assert not any(e.name == "execution.operation_start" for e in o.snapshot().events)
    assert o.execution_snapshot().turns[-1].completed_tools == 0
