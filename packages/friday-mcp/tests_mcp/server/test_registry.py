"""Actual public registry populated only with explicit synthetic tools."""

import pytest
from friday_tools import BaseTool, DefaultToolRegistry

from friday_mcp.server import ModernToolsMCPServer, configure_modern_tools_mode
from tests_mcp.server.test_modern_protocol import rpc


class SyntheticTool(BaseTool):
    def __init__(self, name="echo", schema=None):
        self._name = name
        self._schema = schema or {
            "type": "object",
            "properties": {
                "text": {"type": "string", "minLength": 1, "x-mcp-header": "Text"}
            },
            "required": ["text"],
            "additionalProperties": False,
        }
        self.calls = []

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return "Explicit synthetic registry tool"

    @property
    def parameters_schema(self):
        return self._schema

    @property
    def category(self):
        return "utility"

    async def execute(self, **kwargs):
        self.calls.append(kwargs)
        return kwargs["text"]


@pytest.mark.asyncio
async def test_actual_public_registry_filter_prefix_snapshot_and_instances():
    registry = DefaultToolRegistry()
    tool = SyntheticTool()
    filtered = SyntheticTool("excluded")
    registry.register(tool)
    registry.register(filtered)
    server, other = ModernToolsMCPServer(), ModernToolsMCPServer()
    configure_modern_tools_mode(
        server, registry, tool_filter=["echo"], prefix="synthetic."
    )
    assert [t["name"] for t in server.tools] == ["synthetic.echo"]
    assert server.tools[0]["inputSchema"] == tool.parameters_schema
    assert other.tools == ()
    tool._schema["properties"]["text"]["minLength"] = 99
    response = await server.handle(
        rpc(
            "tools/call", params={"name": "synthetic.echo", "arguments": {"text": "ok"}}
        )
    )
    assert response["result"]["content"][0]["text"] == "ok" and tool.calls == [
        {"text": "ok"}
    ]
    assert (
        await server.handle(
            rpc("tools/call", params={"name": "excluded", "arguments": {"text": "bad"}})
        )
    )["error"]["code"] == -32602
    assert not filtered.calls
    assert (await server.handle(rpc("resources/list")))["error"]["code"] == -32601


@pytest.mark.parametrize(
    "schema",
    [
        {"type": "object", "$ref": "https://example.invalid/schema"},
        {
            "type": "object",
            "properties": {"x": {"type": "string", "x-mcp-header": "Bad Header"}},
        },
    ],
)
def test_unsupported_schema_bridge_preserves_old_catalog(schema):
    server = ModernToolsMCPServer()
    good = DefaultToolRegistry()
    good.register(SyntheticTool())
    configure_modern_tools_mode(server, good)
    before = server.tools
    bad = DefaultToolRegistry()
    bad.register(SyntheticTool("first"))
    bad.register(SyntheticTool("bad", schema))
    with pytest.raises(ValueError):
        configure_modern_tools_mode(server, bad)
    assert server.tools == before


def test_collision_staged_before_any_publication():
    registry = DefaultToolRegistry()
    a, b = SyntheticTool("a"), SyntheticTool("b")
    registry.register(a)
    registry.register(b)
    # Mutable public tool properties must not bypass collision checks.
    b._name = "a"
    server = ModernToolsMCPServer()
    with pytest.raises(ValueError, match="collision"):
        configure_modern_tools_mode(server, registry)
    assert server.tools == () and not a.calls and not b.calls
