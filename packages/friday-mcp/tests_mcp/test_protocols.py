"""Tests for MCP protocols."""

from typing import Any

from friday_mcp.protocols import (
    MCPClient,
    MCPServer,
    MCPTransport,
    ToolDefinition,
)


class TestProtocols:
    """Test that protocols are properly defined."""

    def test_tool_definition_protocol(self):
        """Test ToolDefinition protocol structure."""

        class MockTool:
            @property
            def name(self) -> str:
                return "test_tool"

            @property
            def description(self) -> str:
                return "A test tool"

            @property
            def parameters_schema(self) -> dict[str, Any]:
                return {"type": "object", "properties": {}}

            @property
            def category(self) -> str:
                return "utility"

            @property
            def tags(self) -> list[str]:
                return ["test"]

            async def execute(self, **kwargs: Any) -> str:
                return "result"

            def to_schema(self, format: str = "plain") -> dict[str, Any]:
                return {
                    "name": self.name,
                    "description": self.description,
                    "parameters": self.parameters_schema,
                }

        tool = MockTool()
        assert isinstance(tool, ToolDefinition)
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"

    def test_mcp_transport_protocol(self):
        """Test MCPTransport protocol structure."""

        class MockTransport:
            async def connect(self) -> None:
                pass

            async def disconnect(self) -> None:
                pass

            async def send(self, message: dict[str, Any]) -> None:
                pass

            async def receive(self) -> dict[str, Any]:
                return {}

            @property
            def is_connected(self) -> bool:
                return True

        transport = MockTransport()
        assert isinstance(transport, MCPTransport)

    def test_mcp_client_protocol(self):
        """Test MCPClient protocol structure."""

        class MockClient:
            async def connect(self) -> None:
                pass

            async def disconnect(self) -> None:
                pass

            async def list_tools(self) -> list[dict[str, Any]]:
                return []

            async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
                return ""

            async def list_prompts(self) -> list[dict[str, Any]]:
                return []

            async def get_prompt(
                self, name: str, arguments: dict[str, Any] | None = None
            ) -> dict[str, Any]:
                return {}

            async def list_resources(self) -> list[dict[str, Any]]:
                return []

            async def read_resource(self, uri: str) -> dict[str, Any]:
                return {}

            @property
            def server_capabilities(self) -> dict[str, Any]:
                return {}

        client = MockClient()
        assert isinstance(client, MCPClient)

    def test_mcp_server_protocol(self):
        """Test MCPServer protocol structure."""
        from collections.abc import Callable

        class MockServer:
            async def start(self) -> None:
                pass

            async def stop(self) -> None:
                pass

            async def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
                return {}

            def register_tool(
                self,
                name: str,
                description: str,
                input_schema: dict[str, Any],
                handler: Callable[..., Any],
            ) -> None:
                pass

            def register_prompt(
                self,
                name: str,
                description: str,
                arguments: list[dict[str, Any]] | None,
                handler: Callable[..., Any],
            ) -> None:
                pass

            def register_resource(
                self,
                uri: str,
                name: str,
                description: str,
                mime_type: str,
                handler: Callable[..., Any],
            ) -> None:
                pass

            @property
            def is_running(self) -> bool:
                return False

        server = MockServer()
        assert isinstance(server, MCPServer)
