"""Tool commands for FridayV2."""

from __future__ import annotations

import unicodedata
from collections.abc import Sequence

from friday_chat.commands.contracts import (
    CommandContext,
    CommandMetadata,
    CommandResult,
)
from friday_chat.tools.schemas import ToolDefinition
from friday_chat.tools.selection import ToolSelectionError, ToolSelectionMode


def list_runtime_tools(context: CommandContext) -> list[ToolDefinition]:
    """Return the currently registered runtime tool definitions."""
    if context.runtime is None:
        return []
    return list(context.runtime.tools.list_tools())


def find_tool(context: CommandContext, name: str) -> ToolDefinition | None:
    """Find one registered runtime tool by exact name."""
    for tool in list_runtime_tools(context):
        if tool.name == name:
            return tool
    return None


async def inject_tools_handler(
    context: CommandContext,
    args: tuple[str, ...],
    _metadata: CommandMetadata,
) -> CommandResult:
    """Atomically replace automatic selection with an exact manual tool set."""
    if not args:
        return CommandResult(output="Usage: /inject-tools <names>")
    if context.runtime is None:
        return CommandResult(output="Error: Tool registry not initialized.")

    selection = context.runtime.tool_selection
    selection.synchronize_registered_tools(context.runtime.tools.list_tools())
    try:
        snapshot = selection.inject_manual(args)
    except ToolSelectionError as exc:
        return CommandResult(
            output=(
                f"Tool injection rejected ({exc.reason.value}): "
                f"{_selection_error_text(exc)}. "
                "Manual selection unchanged."
            )
        )

    selected_metadata = tuple(
        zip(
            snapshot.selected_names,
            snapshot.selected_categories,
            strict=True,
        )
    )
    visible_metadata = selected_metadata[:20]
    lines = ["Injected tools:"]
    lines.extend(
        f"- {_display_text(name)} ({_display_text(category)})"
        for name, category in visible_metadata
    )
    if len(selected_metadata) > len(visible_metadata):
        lines.append(f"- ... (+{len(selected_metadata) - len(visible_metadata)} more)")
    lines.append(
        f"Schema budget: {snapshot.schema_tokens}/{snapshot.maximum_schema_tokens} tokens"
    )
    return CommandResult(output="\n".join(lines))


async def clear_tools_handler(
    context: CommandContext,
    _args: tuple[str, ...],
    _metadata: CommandMetadata,
) -> CommandResult:
    """Restore automatic relevance selection."""
    if context.runtime is None:
        return CommandResult(output="Error: Tool registry not initialized.")
    context.runtime.tool_selection.clear_manual()
    return CommandResult(output="Cleared injected tools.")


async def tool_budget_handler(
    context: CommandContext,
    _args: tuple[str, ...],
    _metadata: CommandMetadata,
) -> CommandResult:
    """Inspect registered, manual, selected, executed, and budget state."""
    if context.runtime is None:
        return CommandResult(output="Tool budget unavailable: runtime not initialized.")

    state = context.runtime.tool_selection
    state.synchronize_registered_tools(context.runtime.tools.list_tools())
    calculator = state.calculator
    manual = state.manual_preview()
    last = state.last_turn_snapshot
    automatic = state.last_automatic_snapshot
    if manual is not None:
        estimate = manual
        estimate_source = "pending_manual"
    elif state.mode is ToolSelectionMode.AUTOMATIC and automatic is not None:
        estimate = automatic
        estimate_source = "last_automatic"
    elif state.mode is ToolSelectionMode.AUTOMATIC:
        estimate = None
        estimate_source = "automatic_pre_turn"
    else:
        estimate = None
        estimate_source = "disabled"
    estimated_tokens = estimate.schema_tokens if estimate is not None else 0
    utilization = estimate.utilization_pct if estimate is not None else 0.0
    maximum_schema_tokens = (
        estimate.maximum_schema_tokens
        if estimate is not None
        else calculator.maximum_schema_tokens
    )
    maximum_tools = estimate.max_tools if estimate is not None else calculator.max_tools
    budget_ratio = (
        estimate.max_budget_ratio
        if estimate is not None
        else float(calculator.max_budget_ratio)
    )

    if last is None:
        last_mode = "not yet completed"
        last_selected = "not yet selected"
        last_schema_tokens = "not available"
    else:
        last_mode = last.mode.value
        last_selected = _format_names(last.selected_names)
        last_schema_tokens = str(last.schema_tokens)
    if automatic is None:
        automatic_selected = "not yet selected"
        automatic_schema_tokens = "not available"
    else:
        automatic_selected = _format_names(automatic.selected_names)
        automatic_schema_tokens = str(automatic.schema_tokens)

    lines = [
        "Tool budget:",
        f"- mode: {state.mode.value}",
        f"- registered: {_format_names(state.registered_names)}",
        f"- pending_manual: {_format_names(state.manual_names)}",
        f"- estimate_source: {estimate_source}",
        f"- automatic_selected: {automatic_selected}",
        f"- automatic_schema_tokens: {automatic_schema_tokens}",
        f"- last_completed_mode: {last_mode}",
        f"- last_selected: {last_selected}",
        f"- executed: {_format_names(state.last_executed_names)}",
        f"- estimated_schema_tokens: {estimated_tokens}",
        f"- last_schema_tokens: {last_schema_tokens}",
        f"- maximum_schema_tokens: {maximum_schema_tokens}",
        f"- max_tools: {maximum_tools}",
        f"- max_budget_ratio: {budget_ratio:.3f}",
        f"- utilization_pct: {utilization:.1f}",
    ]
    if last is not None and last.rejections:
        visible_rejections = last.rejections[:20]
        rejection_text = ", ".join(
            f"{_display_text(rejection.name)} ({rejection.reason.value})"
            for rejection in visible_rejections
        )
        if len(last.rejections) > len(visible_rejections):
            rejection_text += (
                f", ... (+{len(last.rejections) - len(visible_rejections)} more)"
            )
        lines.append("- last_rejected: " + rejection_text)
    return CommandResult(output="\n".join(lines))


def _selection_error_text(exc: ToolSelectionError) -> str:
    if exc.names:
        return _format_names(exc.names)
    return "request rejected"


def _format_names(names: Sequence[str]) -> str:
    if not names:
        return "none"
    display_limit = 20
    visible = ", ".join(_display_text(name) for name in names[:display_limit])
    if len(names) > display_limit:
        visible += f", ... (+{len(names) - display_limit} more)"
    return f"{len(names)} ({visible})"


def _display_text(value: str, *, limit: int = 96) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    safe = "".join(
        character
        for character in normalized
        if not unicodedata.category(character).startswith("C")
    )
    if len(safe) <= limit:
        return safe
    return safe[:limit] + "..."


__all__ = [
    "clear_tools_handler",
    "find_tool",
    "inject_tools_handler",
    "list_runtime_tools",
    "tool_budget_handler",
]
