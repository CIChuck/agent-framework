"""Parallel modern exports preserve legacy server/config and optional imports."""

import asyncio
import builtins
import sys

import pytest

from friday_mcp.config import MCPServerSettings, TransportType
from friday_mcp.server import (
    MCPServerBase,
    ModernStdioMCPServer,
    ModernToolsMCPServer,
    SSEMCPServer,
    StdioMCPServer,
    StreamableHTTPMCPServer,
    configure_agent_mode,
    configure_tools_mode,
)


def test_legacy_imports_constructors_defaults_unmodified():
    assert MCPServerBase.PROTOCOL_VERSION == "2024-11-05"
    assert StdioMCPServer().name == "friday-mcp-stdio"
    assert SSEMCPServer().path == "/mcp"
    assert callable(configure_agent_mode) and callable(configure_tools_mode)
    settings = MCPServerSettings()
    assert settings.transport == TransportType.STDIO
    assert {t.value for t in TransportType} == {"stdio", "sse"}
    assert not isinstance(ModernToolsMCPServer(), MCPServerBase)


def test_http_dependencies_lazy_and_fixed_missing_error(monkeypatch):
    original = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name == "fastapi" or name == "uvicorn" or name.startswith("starlette"):
            raise ImportError("dependency-private-sentinel")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)
    # Re-import actual public export module with HTTP optional imports unavailable.
    sys.modules.pop("friday_mcp.server", None)
    import friday_mcp.server as exports

    assert exports.ModernStdioMCPServer is ModernStdioMCPServer
    assert exports.StdioMCPServer is StdioMCPServer
    with pytest.raises(
        RuntimeError, match="^MCP HTTP server dependencies unavailable$"
    ):
        StreamableHTTPMCPServer().create_app()


@pytest.mark.asyncio
async def test_partial_stdio_start_failure_settles_and_retry_is_possible(monkeypatch):
    server = ModernStdioMCPServer()
    loop = asyncio.get_running_loop()

    async def failed(*args, **kwargs):
        raise OSError("private-I/O-error")

    monkeypatch.setattr(loop, "connect_read_pipe", failed)
    await server.serve()
    assert server.active_requests == 0
    server.start()
    await server.stop()


@pytest.mark.asyncio
async def test_partial_stdio_output_pipe_start_failure_closes_input(
    monkeypatch, capsys
):
    server = ModernStdioMCPServer()
    loop = asyncio.get_running_loop()

    class InputTransport:
        closed = False

        def close(self):
            self.closed = True

    transport = InputTransport()

    async def input_pipe(factory, pipe):
        return transport, factory()

    async def output_pipe(factory, pipe):
        raise OSError("private-output-pipe-sentinel")

    monkeypatch.setattr(loop, "connect_read_pipe", input_pipe)
    monkeypatch.setattr(loop, "connect_write_pipe", output_pipe)
    await server.serve()
    assert transport.closed and server.active_requests == 0
    assert "private-output-pipe-sentinel" not in capsys.readouterr().err
    server.start()
    await server.stop()
