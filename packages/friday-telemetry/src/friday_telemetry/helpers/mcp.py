"""Best-effort MCP events with an explicit, content-free export boundary."""

from __future__ import annotations

from hashlib import sha256

from friday_telemetry.interface import TelemetryInterface
from friday_telemetry.models.mcp import MCPEvent, MCPEventName, MCPEventReason


def opaque_mcp_ref(kind: str, identifier: str) -> str:
    """Stable local correlation without exporting a configured or peer name."""
    return sha256(
        f"{kind}\0{identifier}".encode("utf-8", errors="surrogatepass")
    ).hexdigest()[:16]


class MCPTelemetryHelper:
    """Emit typed allowlisted events through the existing optional provider."""

    def __init__(self, telemetry: TelemetryInterface | None = None) -> None:
        self._telemetry = telemetry

    def emit(
        self,
        name: MCPEventName,
        *,
        server_id: str | None = None,
        tool_name: str | None = None,
        reason: MCPEventReason | None = None,
        count: int | None = None,
        required: bool | None = None,
    ) -> None:
        if self._telemetry is None:
            return
        try:
            event = MCPEvent(
                name=name,
                server_ref=opaque_mcp_ref("server", server_id)
                if server_id is not None
                else None,
                tool_ref=opaque_mcp_ref("tool", tool_name)
                if tool_name is not None
                else None,
                reason=reason,
                count=count,
                required=required,
            )
            self._telemetry.capture_event(f"mcp.{event.name}", event.attributes())
        except Exception:
            # Observability never changes connection, tool or memory semantics.
            return
