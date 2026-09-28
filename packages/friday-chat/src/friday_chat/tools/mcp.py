"""Public Chat registry bridge over the accepted runtime MCP owner."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping, Sequence
from copy import deepcopy
from typing import Any, Protocol

from friday_agent import DefaultToolRegistry
from friday_core.mcp import MCPToolMetadata
from friday_runtime.config import MCPToolProviderConfig
from friday_runtime.mcp_loading import RuntimeMCPProvider

from friday_chat.tools.output import MCPOutputPolicy, safe_mcp_call_id
from friday_chat.tools.schemas import ToolCallRecord, ToolDefinition


class NativeChatRegistry(Protocol):
    """Existing Chat callable boundary; native dispatch stays with its owner."""

    def list_tools(self) -> Sequence[ToolDefinition]: ...

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str: ...


class MCPChatRegistry:
    """Reachable provider/registry owner, including after failed public cleanup."""

    def __init__(
        self,
        native: NativeChatRegistry,
        config: MCPToolProviderConfig,
        workspace_root: str,
    ) -> None:
        self.native = native
        self.provider = RuntimeMCPProvider(config, workspace_root)
        self.output_policy = MCPOutputPolicy(config.config.limits.max_result_bytes)
        self.registry = DefaultToolRegistry()
        for definition in native.list_tools():
            self.registry.register(
                name=definition.name,
                func=self._native_executor(definition.name),
                description=definition.description,
                parameters=deepcopy(definition.input_schema),
                category=definition.category,
            )

    def _native_executor(self, name: str) -> Callable[..., Awaitable[str]]:
        async def execute(**arguments: Any) -> str:
            return await self.native.call_tool(name, arguments)

        return execute

    @property
    def tool_metadata(self) -> Mapping[str, MCPToolMetadata]:
        metadata: Mapping[str, MCPToolMetadata] = self.provider.tool_metadata
        return metadata

    async def start(self) -> None:
        """Reuse public discovery/publication and their retained retry ownership."""
        try:
            await self.provider.start()
            await self.provider.register_tools(self.registry)
        except BaseException:
            await self.provider.stop()
            raise

    async def stop(self) -> None:
        """Remove owned MCP entries and settle transports through the same owner."""
        await self.provider.stop()

    def list_tools(self) -> tuple[ToolDefinition, ...]:
        definitions = list(self.native.list_tools())
        for name in self.tool_metadata:
            tool = self.registry.get(name)
            if tool is None:
                raise RuntimeError("MCP Chat registry metadata has no owned tool")
            definitions.append(
                ToolDefinition(
                    name=tool.name,
                    description=tool.description,
                    input_schema=deepcopy(tool.parameters_schema),
                    category=tool.category,
                )
            )
        return tuple(definitions)

    def get_context_block(self) -> str:
        return "Available tools:\n" + "\n".join(
            f"- {tool.name}: {tool.description}" for tool in self.list_tools()
        )

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        return (await self.call_tool_record(name, arguments)).result

    def is_mcp_tool(self, name: str) -> bool:
        """Identify owned MCP calls without inspecting a private registry."""
        return name in self.tool_metadata

    async def call_tool_record(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        call_id: str | None = None,
        used_call_ids: set[str] | None = None,
    ) -> ToolCallRecord:
        """Execute once; return only the checked output and atomic provenance."""
        metadata = self.tool_metadata.get(name)
        if metadata is None:
            result = await self.native.call_tool(name, arguments)
            return ToolCallRecord(name, arguments, result, call_id)
        self.output_policy.require_usable_limit()
        identifier = safe_mcp_call_id(
            call_id, used_call_ids if used_call_ids is not None else set()
        )
        try:
            # Exact original-name routing remains owned by the WS-03 callable.
            result = await self.registry.get_callable(name)(**arguments)
        except TimeoutError:
            return self.output_policy.failed_record(metadata, identifier, "timeout")
        except Exception as exc:
            # Optional public failure classification is validated locally. Chat
            # does not need an undeclared dependency on the protocol package.
            code = getattr(exc, "failure_code", None)
            if code == "tool_error":
                return self.output_policy.failed_record(
                    metadata, identifier, "tool_error"
                )
            if code == "invalid_result":
                return self.output_policy.failed_record(
                    metadata, identifier, "invalid_result"
                )
            return self.output_policy.failed_record(
                metadata, identifier, "execution_error"
            )
        if not isinstance(result, str):
            return self.output_policy.failed_record(
                metadata, identifier, "invalid_result"
            )
        try:
            return self.output_policy.checked_record(
                metadata, identifier, result, arguments
            )
        except Exception:
            return self.output_policy.failed_record(
                metadata, identifier, "output_rejected"
            )
