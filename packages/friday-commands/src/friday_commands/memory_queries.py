"""Opt-in read-only memory queries through a host-owned typed capability."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Protocol

from .contracts import (
    CommandArgument,
    CommandExecution,
    CommandOutcome,
    CommandRequest,
    CommandSpec,
    GraphData,
    IngestedDocumentsData,
    MemoryQueryFailedData,
    MemoryRecordKindName,
    MemoryRecordsData,
    MemoryStatisticsData,
    MemoryUnavailableData,
)
from .registry import CommandHandler

MEMORY_QUERY_SPECS: tuple[CommandSpec, ...] = (
    CommandSpec(
        "memory",
        "Show typed memory, transcript, session, and context statistics.",
        "memory",
        "/memory",
        detail=(
            "Reports public episodic, vector, graph, transcript, lifecycle, priming, "
            "app-session, and last-context metrics. Empty stores report zero; "
            "unavailable or unconfigured components are labeled honestly."
        ),
    ),
    CommandSpec("insights", "List durable insights.", "memory", "/insights"),
    CommandSpec("summaries", "List turn summaries.", "memory", "/summaries"),
    CommandSpec(
        "meta",
        "List active meta insights with lifecycle and provenance metadata.",
        "memory",
        "/meta",
        detail=(
            "Queries typed short- and long-term meta_insight records, excludes "
            "decayed records, and shows bounded synthesis provenance, source, "
            "confidence, and verification fields when available. It never runs "
            "synthesis or reorganization."
        ),
    ),
    CommandSpec(
        "entities",
        "List graph entities and relationships.",
        "memory",
        "/entities [nodes|name]",
        arguments=(
            CommandArgument(
                "nodes|name",
                "Use 'nodes' for node details or provide an entity name to inspect.",
            ),
        ),
    ),
    CommandSpec(
        "list-ingested",
        "List ingested document memory records.",
        "memory",
        "/list-ingested",
    ),
)


class MemoryQueryPort(Protocol):
    """Supply display facts without exposing runtime or store objects."""

    def memory_available(self) -> bool: ...

    async def memory_statistics(self) -> MemoryStatisticsData: ...

    async def memory_records(
        self, kind: MemoryRecordKindName
    ) -> MemoryRecordsData | MemoryQueryFailedData: ...

    async def graph_snapshot(
        self, name: str | None, include_relationships: bool
    ) -> GraphData: ...

    async def ingested_documents(self) -> IngestedDocumentsData: ...


def _validate_invocation(
    request: CommandRequest, execution: CommandExecution, name: str
) -> None:
    if type(request) is not CommandRequest:
        raise TypeError("Expected a CommandRequest")
    if type(execution) is not CommandExecution:
        raise TypeError("Expected a CommandExecution")
    if request.name != name:
        raise ValueError("Request does not match this memory query handler")


def build_memory_query_handlers(port: MemoryQueryPort) -> Mapping[str, CommandHandler]:
    """Store the port without inspecting it and return fresh immutable handlers."""

    def available() -> bool:
        value = port.memory_available()
        if type(value) is not bool:
            raise TypeError("Expected a boolean memory availability")
        return value

    async def memory_handler(
        request: CommandRequest, execution: CommandExecution
    ) -> CommandOutcome:
        _validate_invocation(request, execution, "memory")
        if not available():
            return CommandOutcome(data=MemoryUnavailableData("runtime_missing"))
        data = await port.memory_statistics()
        if type(data) is not MemoryStatisticsData:
            raise TypeError("Expected a MemoryStatisticsData")
        return CommandOutcome(data=data)

    def records_handler(name: str, kind: MemoryRecordKindName) -> CommandHandler:
        async def handle(
            request: CommandRequest, execution: CommandExecution
        ) -> CommandOutcome:
            _validate_invocation(request, execution, name)
            if not available():
                return CommandOutcome(data=MemoryUnavailableData("runtime_missing"))
            data = await port.memory_records(kind)
            if type(data) not in (MemoryRecordsData, MemoryQueryFailedData):
                raise TypeError("Expected memory records or query failure data")
            if data.kind != kind:
                raise ValueError("Memory record kind does not match the query")
            return CommandOutcome(data=data)

        return handle

    async def entities_handler(
        request: CommandRequest, execution: CommandExecution
    ) -> CommandOutcome:
        _validate_invocation(request, execution, "entities")
        if not available():
            return CommandOutcome(data=MemoryUnavailableData("runtime_missing"))
        nodes_only = bool(request.args) and request.args[0] == "nodes"
        name = " ".join(request.args) if request.args and not nodes_only else None
        data = await port.graph_snapshot(name, not nodes_only)
        if type(data) is not GraphData:
            raise TypeError("Expected a GraphData")
        if nodes_only and data.relationships:
            raise ValueError("Nodes-only data must not carry relationships")
        return CommandOutcome(data=data)

    async def ingested_handler(
        request: CommandRequest, execution: CommandExecution
    ) -> CommandOutcome:
        _validate_invocation(request, execution, "list-ingested")
        if not available():
            return CommandOutcome(data=MemoryUnavailableData("runtime_missing"))
        data = await port.ingested_documents()
        if type(data) is not IngestedDocumentsData:
            raise TypeError("Expected an IngestedDocumentsData")
        return CommandOutcome(data=data)

    return MappingProxyType(
        {
            "memory": memory_handler,
            "insights": records_handler("insights", "insight"),
            "summaries": records_handler("summaries", "summary"),
            "meta": records_handler("meta", "meta_insight"),
            "entities": entities_handler,
            "list-ingested": ingested_handler,
        }
    )
