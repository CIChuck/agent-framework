"""Opt-in diagnostic orchestration through a narrow, host-owned capability."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Protocol

from .contracts import (
    BudgetData,
    CommandArgument,
    CommandExecution,
    CommandOutcome,
    CommandRequest,
    CommandSpec,
    ContextData,
    DebugData,
    PromptData,
    RetrievalData,
    RetrievalUnavailableData,
    TimingData,
)
from .registry import CommandHandler

DIAGNOSTIC_SPECS: tuple[CommandSpec, ...] = (
    CommandSpec(
        "context",
        "Show the assembled context payload.",
        "memory",
        "/context [--debug] [--file]",
        arguments=(
            CommandArgument("--debug", "Include detailed token diagnostics."),
            CommandArgument("--file", "Export the context to a file."),
        ),
    ),
    CommandSpec(
        "prompt",
        "Show the full formatted prompt sent to the LLM.",
        "memory",
        "/prompt [--file]",
        arguments=(CommandArgument("--file", "Export the prompt to a file."),),
    ),
    CommandSpec(
        "debug", "Show context assembly debug information.", "memory", "/debug"
    ),
    CommandSpec(
        "debug-budget", "Show token budget diagnostics.", "memory", "/debug-budget"
    ),
    CommandSpec(
        "timing", "Show timing breakdown for the last turn.", "memory", "/timing"
    ),
    CommandSpec(
        "debug-retrieval",
        "Show retrieval diagnostics for a query.",
        "memory",
        "/debug-retrieval <query>",
        arguments=(
            CommandArgument(
                "query", "Retrieval query; remaining words are joined.", True
            ),
        ),
    ),
)


class DiagnosticsPort(Protocol):
    """Project host facts and perform the existing export/retrieval operations."""

    def context_text(self) -> str: ...

    def prompt_text(self) -> str: ...

    def export_context(self, data: ContextData) -> str: ...

    def export_prompt(self, data: PromptData) -> str: ...

    def debug_snapshot(self) -> DebugData: ...

    def budget_snapshot(self) -> BudgetData: ...

    def timing_snapshot(self) -> TimingData: ...

    def retrieval_available(self) -> bool: ...

    async def retrieve(self, query: str) -> RetrievalData: ...


def _validate_invocation(
    request: CommandRequest, execution: CommandExecution, canonical_name: str
) -> None:
    if type(request) is not CommandRequest:
        raise TypeError("Expected a CommandRequest")
    if type(execution) is not CommandExecution:
        raise TypeError("Expected a CommandExecution")
    if request.name != canonical_name:
        raise ValueError("Request does not match this diagnostic handler")


def build_diagnostic_handlers(port: DiagnosticsPort) -> Mapping[str, CommandHandler]:
    """Return fresh immutable handlers without inspecting the injected port."""

    async def context_handler(
        request: CommandRequest, execution: CommandExecution
    ) -> CommandOutcome:
        _validate_invocation(request, execution, "context")
        data = ContextData(port.context_text())
        if "--debug" in request.args:
            data = ContextData(data.text, len(data.text))
        if "--file" in request.args:
            path = port.export_context(data)
            if not isinstance(path, str):
                raise TypeError("Expected a string export path")
            data = ContextData(data.text, data.character_count, path)
        return CommandOutcome(data=data)

    async def prompt_handler(
        request: CommandRequest, execution: CommandExecution
    ) -> CommandOutcome:
        _validate_invocation(request, execution, "prompt")
        data = PromptData(port.prompt_text())
        if "--file" in request.args:
            path = port.export_prompt(data)
            if not isinstance(path, str):
                raise TypeError("Expected a string export path")
            data = PromptData(data.text, path)
        return CommandOutcome(data=data)

    async def debug_handler(
        request: CommandRequest, execution: CommandExecution
    ) -> CommandOutcome:
        _validate_invocation(request, execution, "debug")
        data = port.debug_snapshot()
        if type(data) is not DebugData:
            raise TypeError("Expected a DebugData")
        return CommandOutcome(data=data)

    async def budget_handler(
        request: CommandRequest, execution: CommandExecution
    ) -> CommandOutcome:
        _validate_invocation(request, execution, "debug-budget")
        data = port.budget_snapshot()
        if type(data) is not BudgetData:
            raise TypeError("Expected a BudgetData")
        return CommandOutcome(data=data)

    async def timing_handler(
        request: CommandRequest, execution: CommandExecution
    ) -> CommandOutcome:
        _validate_invocation(request, execution, "timing")
        data = port.timing_snapshot()
        if type(data) is not TimingData:
            raise TypeError("Expected a TimingData")
        return CommandOutcome(data=data)

    async def retrieval_handler(
        request: CommandRequest, execution: CommandExecution
    ) -> CommandOutcome:
        _validate_invocation(request, execution, "debug-retrieval")
        available = port.retrieval_available()
        if type(available) is not bool:
            raise TypeError("Expected a boolean retrieval availability")
        if not available:
            return CommandOutcome(data=RetrievalUnavailableData("runtime_missing"))
        if not request.args:
            return CommandOutcome(data=RetrievalUnavailableData("query_missing"))
        query = " ".join(request.args)
        data = await port.retrieve(query)
        if type(data) is not RetrievalData:
            raise TypeError("Expected a RetrievalData")
        if data.query != query:
            raise ValueError("Retrieval data does not match the query")
        return CommandOutcome(data=data)

    return MappingProxyType(
        {
            "context": context_handler,
            "prompt": prompt_handler,
            "debug": debug_handler,
            "debug-budget": budget_handler,
            "timing": timing_handler,
            "debug-retrieval": retrieval_handler,
        }
    )
