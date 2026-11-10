"""Chat session projection and presentation for injected shared handlers."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

import friday_commands.session_views as shared_session
from friday_commands import (
    CommandExecution,
    CommandOutcome,
    CommandRequest,
    HistoryData,
    HistoryTurn,
    SessionClearedData,
)

from friday_chat.commands.contracts import (
    CommandContext,
    CommandMetadata,
    CommandResult,
)

_SESSION_BY_NAME = MappingProxyType(
    {spec.name: spec for spec in shared_session.SESSION_SPECS}
)


@dataclass(frozen=True, slots=True)
class ChatSessionPort:
    """Use the supplied context; session memory remains owned by its runtime."""

    context: CommandContext

    def history_snapshot(self) -> tuple[HistoryTurn, ...]:
        if not self.context.history:
            return ()
        return tuple(
            HistoryTurn("".join((f"{user}",)), "".join((f"{assistant}",)))
            for user, assistant in self.context.history
        )

    def clear_history(self) -> None:
        self.context.history.clear()

    async def clear_session_memory(self) -> None:
        if self.context.runtime is not None:
            await self.context.runtime.memory.clear_session_memory()


def session_metadata(name: str) -> CommandMetadata:
    """Project the two shared definitions into the unchanged Chat model."""
    spec = _SESSION_BY_NAME[name]
    return CommandMetadata(
        spec.name,
        spec.description,
        spec.category,
        spec.usage,
        spec.aliases,
        (),
        spec.detail,
    )


def adapt_session_outcome(outcome: CommandOutcome) -> CommandResult:
    """Render only the two explicit, effect-free session success shapes."""
    if (
        type(outcome) is not CommandOutcome
        or outcome.error is not None
        or outcome.ui_effects
    ):
        raise ValueError("Unsupported session outcome")
    data = outcome.data
    if type(data) is SessionClearedData:
        return CommandResult(output="Conversation history cleared.")
    if type(data) is HistoryData:
        if not data.turns:
            return CommandResult(output="No conversation history.")
        lines = ["Conversation history:"]
        for index, turn in enumerate(data.turns, start=1):
            lines.append(f"{index}. User: {turn.user_message}")
            lines.append(f"   Friday: {turn.assistant_message}")
        return CommandResult(output="\n".join(lines))
    raise ValueError("Unsupported session data")


async def invoke_session(
    name: str, args: tuple[str, ...], context: CommandContext
) -> CommandResult:
    spec = _SESSION_BY_NAME[name]
    request = CommandRequest(spec.name, args, spec)
    handler = shared_session.build_session_handlers(ChatSessionPort(context))[name]
    return adapt_session_outcome(await handler(request, CommandExecution()))
