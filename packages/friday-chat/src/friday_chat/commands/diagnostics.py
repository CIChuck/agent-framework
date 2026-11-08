"""Chat diagnostics projection, presentation and fixed-file export effects."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType

import friday_commands.diagnostics as shared_diagnostics
from friday_commands import (
    BudgetData,
    CommandExecution,
    CommandOutcome,
    CommandRequest,
    ContextData,
    DebugData,
    DebugTurnData,
    DiagnosticField,
    PromptData,
    RetrievalData,
    RetrievalUnavailableData,
    TimingCounter,
    TimingData,
    TimingTurnData,
)

from friday_chat.commands.contracts import (
    CommandArgument,
    CommandContext,
    CommandMetadata,
    CommandResult,
)
from friday_chat.commands.memory import preview_text
from friday_chat.commands.transcript import export_directory as _export_directory

_DIAGNOSTIC_BY_NAME = MappingProxyType(
    {spec.name: spec for spec in shared_diagnostics.DIAGNOSTIC_SPECS}
)


def _plain(value: object, spec: str = "") -> str:
    # Drop a formatter's str subclass without invoking its formatter again.
    return "".join((format(value, spec),))


@dataclass(frozen=True, slots=True)
class _RenderedContext:
    """Host-local presentation of the exact text/count used for an export."""

    data: ContextData
    body: str


@dataclass(slots=True)
class _ContextExport:
    rendered: _RenderedContext | None = None


@dataclass(frozen=True, slots=True)
class ChatDiagnosticsPort:
    """Project only the capability requested, retaining legacy host read order."""

    context: CommandContext
    _context_export: _ContextExport = field(
        default_factory=_ContextExport, init=False, repr=False, compare=False
    )

    def context_text(self) -> str:
        return self.context.last_context or _build_context_text(self.context)

    def prompt_text(self) -> str:
        return self.context.last_prompt or _build_prompt_text(self.context)

    def export_context(self, data: ContextData) -> str:
        body = _render_context(data)
        path = str(_write_export_file(self.context, "context", body))
        if data.character_count is not None:
            # Formatting accepted str subclasses is observable. Reuse this body
            # only for the matching shared outcome, after the write succeeds.
            self._context_export.rendered = _RenderedContext(data, body)
        return path

    def export_prompt(self, data: PromptData) -> str:
        return str(_write_export_file(self.context, "prompt", _render_prompt(data)))

    def debug_snapshot(self) -> DebugData:
        context = self.context
        execution = (
            context.runtime.telemetry.execution_snapshot()
            if context.runtime is not None and context.runtime.telemetry is not None
            else None
        )
        if not context.last_debug and not (execution and execution.turns):
            return DebugData(False)
        fields = tuple(
            DiagnosticField(_plain(key), _plain(value))
            for key, value in sorted(context.last_debug.items())
        )
        turn_data = None
        if execution and execution.turns:
            turn = execution.turns[-1]
            turn_data = DebugTurnData(
                _plain(turn.turn_ref),
                _plain(turn.outcome),
                _plain(turn.persistence),
                _plain(turn.completed_tools),
                _plain(turn.failed_tools),
            )
        return DebugData(True, fields, turn_data)

    def budget_snapshot(self) -> BudgetData:
        context = self.context
        memory = context.runtime.config.memory if context.runtime is not None else None
        context_window = memory.context_window if memory is not None else None
        output_buffer = memory.output_buffer if memory is not None else None
        return BudgetData(
            _plain(context_window) if context_window else None,
            _plain(output_buffer) if output_buffer else None,
        )

    def timing_snapshot(self) -> TimingData:
        context = self.context
        execution = (
            context.runtime.telemetry.execution_snapshot()
            if context.runtime is not None and context.runtime.telemetry is not None
            else None
        )
        if not context.last_timing and not (execution and execution.turns):
            return TimingData(False)
        fields = tuple(
            DiagnosticField(_plain(key), _plain(value, ".3f"))
            for key, value in sorted(context.last_timing.items())
        )
        turn_data = None
        if execution and execution.turns:
            turn = execution.turns[-1]
            turn_data = TimingTurnData(
                _plain(turn.duration_ms / 1000, ".3f"),
                _plain(turn.outcome),
                _plain(turn.persistence),
                tuple(
                    TimingCounter(_plain(kind), _plain(outcome), _plain(count))
                    for kind, outcome, count in execution.counters
                ),
            )
        return TimingData(True, fields, turn_data)

    def retrieval_available(self) -> bool:
        return self.context.runtime is not None

    async def retrieve(self, query: str) -> RetrievalData:
        runtime = self.context.runtime
        if runtime is None:
            raise AttributeError("'NoneType' object has no attribute 'memory'")
        diagnostics = await runtime.memory.debug_retrieval(query)
        snippets = diagnostics.get("snippets", [])
        debug_info = diagnostics.get("debug_info", {})
        count = len(snippets) if isinstance(snippets, list) else 0
        fields = []
        if isinstance(debug_info, dict):
            for key in sorted(debug_info):
                fields.append(DiagnosticField(_plain(key), _plain(debug_info[key])))
        previews: tuple[str, ...] = ()
        if isinstance(snippets, list) and snippets:
            previews = tuple(preview_text(str(snippet)) for snippet in snippets[:10])
        return RetrievalData(query, count, tuple(fields), previews)


def diagnostic_metadata(name: str) -> CommandMetadata:
    """Project all shared metadata fields into the unchanged Chat model."""
    spec = _DIAGNOSTIC_BY_NAME[name]
    return CommandMetadata(
        spec.name,
        spec.description,
        spec.category,
        spec.usage,
        spec.aliases,
        tuple(
            CommandArgument(
                argument.name,
                argument.description,
                argument.required,
                argument.default,
                argument.choices,
            )
            for argument in spec.arguments
        ),
        spec.detail,
    )


def _render_context(data: ContextData, rendered: _RenderedContext | None = None) -> str:
    if (
        rendered is not None
        and data.text is rendered.data.text
        and data.character_count == rendered.data.character_count
    ):
        text = rendered.body
    else:
        text = data.text
        if data.character_count is not None:
            text = f"{text}\n\nDebug:\n- characters: {data.character_count}"
    if data.export_path is not None:
        text = f"{text}\n\nExported context to {data.export_path}"
    return text


def _render_prompt(data: PromptData) -> str:
    text = data.text
    if data.export_path is not None:
        text = f"{text}\n\nExported prompt to {data.export_path}"
    return text


def _render_debug(data: DebugData) -> str:
    if not data.recorded:
        return "No debug information recorded."
    lines = ["Debug information:"]
    lines.extend(f"- {field.key}: {field.value}" for field in data.fields)
    if data.turn is not None:
        turn = data.turn
        lines.extend(
            (
                f"- turn: {turn.turn_ref}",
                f"- outcome: {turn.outcome}",
                f"- persistence: {turn.persistence}",
                f"- completed_tools: {turn.completed_tools}",
                f"- failed_tools: {turn.failed_tools}",
            )
        )
    return "\n".join(lines)


def _render_timing(data: TimingData) -> str:
    if not data.recorded:
        return "No timing data recorded."
    lines = ["Timing:"]
    lines.extend(f"- {field.key}: {field.value}s" for field in data.fields)
    if data.turn is not None:
        turn = data.turn
        lines.append(
            f"- observed_turn: {turn.seconds}s "
            f"({turn.outcome}, persistence={turn.persistence})"
        )
        lines.extend(
            f"- {counter.kind}/{counter.outcome}: {counter.count}"
            for counter in turn.counters
        )
    return "\n".join(lines)


def adapt_diagnostic_outcome(
    outcome: CommandOutcome, *, _rendered_context: _RenderedContext | None = None
) -> CommandResult:
    """Render only the seven explicit diagnostic success shapes, without effects."""
    if (
        type(outcome) is not CommandOutcome
        or outcome.error is not None
        or outcome.ui_effects
    ):
        raise ValueError("Unsupported diagnostic outcome")
    data = outcome.data
    if type(data) is ContextData:
        text = _render_context(data, _rendered_context)
    elif type(data) is PromptData:
        text = _render_prompt(data)
    elif type(data) is DebugData:
        text = _render_debug(data)
    elif type(data) is BudgetData:
        window = "unknown" if data.context_window is None else data.context_window
        buffer = "unknown" if data.output_buffer is None else data.output_buffer
        text = f"Token budget:\n- context_window: {window}\n- output_buffer: {buffer}"
    elif type(data) is TimingData:
        text = _render_timing(data)
    elif type(data) is RetrievalUnavailableData:
        text = (
            "Memory runtime is not initialized."
            if data.reason == "runtime_missing"
            else "Usage: /debug-retrieval <query>"
        )
    elif type(data) is RetrievalData:
        lines = [
            "Retrieval diagnostics:",
            f"- query: {data.query}",
            f"- result_count: {data.result_count}",
        ]
        lines.extend(f"- {field.key}: {field.value}" for field in data.fields)
        if data.previews:
            lines.append("Results:")
            lines.extend(f"- {preview}" for preview in data.previews)
        text = "\n".join(lines)
    else:
        raise ValueError("Unsupported diagnostic data")
    return CommandResult(output=text)


async def invoke_diagnostic(
    name: str, args: tuple[str, ...], context: CommandContext
) -> CommandResult:
    spec = _DIAGNOSTIC_BY_NAME[name]
    request = CommandRequest(spec.name, args, spec)
    port = ChatDiagnosticsPort(context)
    handler = shared_diagnostics.build_diagnostic_handlers(port)[name]
    outcome = await handler(request, CommandExecution())
    return adapt_diagnostic_outcome(
        outcome, _rendered_context=port._context_export.rendered
    )


def _build_context_text(context: CommandContext) -> str:
    sections = ["Context payload:"]
    if context.runtime is not None and context.runtime.tool_context:
        sections.append(context.runtime.tool_context)
    else:
        sections.append("No tool context injected.")
    sections.append(f"History turns: {len(context.history)}")
    return "\n".join(sections)


def _build_prompt_text(context: CommandContext) -> str:
    system_prompt = (
        context.runtime.config.chat.system_prompt
        if context.runtime is not None
        else "You are Friday."
    )
    sections = [f"System: {system_prompt}"]
    if context.history:
        user_message, assistant_message = context.history[-1]
        sections.append(f"User: {user_message}")
        sections.append(f"Friday: {assistant_message}")
    return "\n".join(sections)


def _write_export_file(context: CommandContext, kind: str, text: str) -> Path:
    export_directory = _export_directory(context)
    export_directory.mkdir(parents=True, exist_ok=True)
    path = export_directory / f"friday_{kind}.txt"
    path.write_text(text, encoding="utf-8")
    return path
