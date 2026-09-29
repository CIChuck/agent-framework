"""MCP export is closed, scalar-only and independent of peer content."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from friday_telemetry import (
    DebugTelemetryRecorder,
    MCPEvent,
    MCPTelemetryHelper,
    OpenTelemetryProvider,
    opaque_mcp_ref,
)
from pydantic import ValidationError


def test_closed_event_rejects_payload_and_opaque_refs_are_stable() -> None:
    with pytest.raises(ValidationError):
        MCPEvent.model_validate(
            {"name": "tool_call_finish", "arguments": {"token": "SECRET"}}
        )
    with pytest.raises(ValidationError):
        MCPEvent(name="connection_finish", server_ref="SECRET")
    assert opaque_mcp_ref("server", "peer") == opaque_mcp_ref("server", "peer")
    assert opaque_mcp_ref("server", "peer") != opaque_mcp_ref("tool", "peer")


def test_debug_and_otel_export_inputs_exclude_all_untrusted_surfaces() -> None:
    sentinel = "SENTINEL-RAW-SECRET"
    recorder = DebugTelemetryRecorder()
    helper = MCPTelemetryHelper(recorder)
    helper.emit(
        "tool_call_finish",
        server_id=f"server-{sentinel}",
        tool_name=f"tool-{sentinel}",
        reason="success",
        count=1,
    )
    assert len(recorder.events) == 1
    event = recorder.events[0]
    assert event.name == "mcp.tool_call_finish"
    assert set(event.data) == {"server_ref", "tool_ref", "reason", "count"}
    assert sentinel not in repr(event)

    captured = []
    span = SimpleNamespace(
        is_recording=lambda: True,
        add_event=lambda name, attributes: captured.append((name, attributes)),
    )
    provider = object.__new__(OpenTelemetryProvider)
    provider._initialized = True
    provider._trace_module = SimpleNamespace(get_current_span=lambda: span)
    MCPTelemetryHelper(provider).emit(
        "tool_skipped",
        server_id=f"server-{sentinel}",
        reason="schema_limit",
    )
    assert len(captured) == 1
    assert captured[0][0] == "mcp.tool_skipped"
    assert sentinel not in repr(captured)
    assert set(captured[0][1]) == {"server_ref", "reason"}


def test_disabled_and_throwing_recorders_do_not_change_operation() -> None:
    class Throwing(DebugTelemetryRecorder):
        def capture_event(self, event_name, data):
            raise RuntimeError("SENTINEL-RAW-SECRET")

    MCPTelemetryHelper(None).emit("connection_start", server_id="peer")
    MCPTelemetryHelper(Throwing()).emit("connection_start", server_id="peer")
