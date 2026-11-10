"""Opt-in history snapshots and ordered clearing through a narrow host port."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Protocol

from .contracts import (
    CommandExecution,
    CommandOutcome,
    CommandRequest,
    CommandSpec,
    HistoryData,
    HistoryTurn,
    SessionClearedData,
)
from .registry import CommandHandler

SESSION_SPECS: tuple[CommandSpec, ...] = (
    CommandSpec("clear", "Clear conversation history.", "session", "/clear"),
    CommandSpec("history", "Show conversation history.", "session", "/history"),
)


class SessionPort(Protocol):
    """Host-owned history and current-session memory, without domain leakage."""

    def history_snapshot(self) -> tuple[HistoryTurn, ...]: ...

    def clear_history(self) -> None: ...

    async def clear_session_memory(self) -> None: ...


def _validate_invocation(
    request: CommandRequest, execution: CommandExecution, canonical_name: str
) -> None:
    if type(request) is not CommandRequest:
        raise TypeError("Expected a CommandRequest")
    if type(execution) is not CommandExecution:
        raise TypeError("Expected a CommandExecution")
    if request.name != canonical_name:
        raise ValueError("Request does not match this session handler")


def build_session_handlers(port: SessionPort) -> Mapping[str, CommandHandler]:
    """Build fresh immutable handlers without reading the injected host port."""

    async def history_handler(
        request: CommandRequest, execution: CommandExecution
    ) -> CommandOutcome:
        _validate_invocation(request, execution, "history")
        return CommandOutcome(data=HistoryData(port.history_snapshot()))

    async def clear_handler(
        request: CommandRequest, execution: CommandExecution
    ) -> CommandOutcome:
        _validate_invocation(request, execution, "clear")
        port.clear_history()
        await port.clear_session_memory()
        return CommandOutcome(data=SessionClearedData())

    return MappingProxyType({"clear": clear_handler, "history": history_handler})
