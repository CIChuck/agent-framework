# mypy: ignore-errors
"""
Rich-based display functions for terminal output.

Provides professional terminal formatting using the Rich library,
including status messages, tables, syntax highlighting, and panels.

Ref: docs/archive/build-plans/completed/friday-core-legacy/memory-chat-v2-prd.md
"""

from __future__ import annotations

import json
import traceback
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from .cli_config import get_cli_config

# Singleton console instance
_console: Console | None = None


def _build_theme() -> Theme:
    """Build Rich Theme from current CLI configuration."""
    config = get_cli_config()
    return Theme(config.theme.to_dict())


def get_console() -> Console:
    """Get the shared Rich console instance."""
    global _console
    if _console is None:
        _console = Console(theme=_build_theme(), highlight=False)
    return _console


def set_console(console: Console | None) -> None:
    """
    Set a custom console (useful for testing).

    Pass None to reset and rebuild console with current config.
    """
    global _console
    _console = console


def reset_console() -> None:
    """Reset console to rebuild with current CLI configuration."""
    global _console
    _console = None


# =============================================================================
# Category 1: Status Messages
# =============================================================================


def display_error(
    message: str,
    exception: Exception | None = None,
    show_traceback: bool = False,
) -> None:
    """
    Display an error message with red styling.

    Args:
        message: The error message to display
        exception: Optional exception for additional context
        show_traceback: Whether to show full traceback (default: False)
    """
    console = get_console()
    config = get_cli_config()
    text = Text()
    text.append(f"{config.icons.error} ", style="error")
    text.append(message, style="error")
    console.print(text)

    if exception:
        console.print(f"  [muted]Error type: {type(exception).__name__}[/muted]")
        console.print(f"  [muted]{str(exception)}[/muted]")

        if show_traceback:
            tb = traceback.format_exception(
                type(exception), exception, exception.__traceback__
            )
            console.print(
                Panel(
                    "".join(tb),
                    title="Traceback",
                    border_style="red",
                    expand=False,
                )
            )


def display_warning(message: str) -> None:
    """
    Display a warning message with yellow styling.

    Args:
        message: The warning message to display
    """
    console = get_console()
    config = get_cli_config()
    text = Text()
    text.append(f"{config.icons.warning} ", style="warning")
    text.append(message, style="warning")
    console.print(text)


def display_success(message: str) -> None:
    """
    Display a success message with green styling.

    Args:
        message: The success message to display
    """
    console = get_console()
    config = get_cli_config()
    text = Text()
    text.append(f"{config.icons.success} ", style="success")
    text.append(message, style="success")
    console.print(text)


def display_info(message: str) -> None:
    """
    Display an info message with blue styling.

    Args:
        message: The info message to display
    """
    console = get_console()
    config = get_cli_config()
    text = Text()
    text.append(f"{config.icons.info} ", style="info")
    text.append(message, style="info")
    console.print(text)


# =============================================================================
# Category 2: Structured Data Display
# =============================================================================


def display_json(
    data: Any,
    title: str | None = None,
    indent: int = 2,
) -> None:
    """
    Display JSON data with syntax highlighting.

    Args:
        data: Data to serialize and display as JSON
        title: Optional title for the panel
        indent: JSON indentation level (default: 2)
    """
    console = get_console()

    if isinstance(data, str):
        json_str = data
    else:
        json_str = json.dumps(data, indent=indent, default=str)

    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)

    if title:
        console.print(Panel(syntax, title=title, border_style="blue", expand=False))
    else:
        console.print(syntax)


def display_code(
    code: str,
    language: str = "python",
    line_numbers: bool = True,
    title: str | None = None,
) -> None:
    """
    Display code with syntax highlighting.

    Args:
        code: The code to display
        language: Programming language for highlighting (default: python)
        line_numbers: Whether to show line numbers (default: True)
        title: Optional title for the panel
    """
    console = get_console()
    syntax = Syntax(
        code,
        language,
        theme="monokai",
        line_numbers=line_numbers,
    )

    if title:
        console.print(Panel(syntax, title=title, border_style="cyan", expand=False))
    else:
        console.print(syntax)


def display_table(
    data: list[dict[str, Any]],
    title: str | None = None,
    columns: list[str] | None = None,
    show_header: bool = True,
    box_style: str = "rounded",
) -> None:
    """
    Display data as a formatted table.

    Args:
        data: List of dictionaries to display as rows
        title: Optional table title
        columns: Column names to include (auto-detected if None)
        show_header: Whether to show column headers (default: True)
        box_style: Table box style (default: rounded)
    """
    console = get_console()

    if not data:
        console.print("[muted]No data to display[/muted]")
        return

    # Auto-detect columns from first row if not specified
    if columns is None:
        columns = list(data[0].keys())

    # Create table
    from rich.box import ROUNDED, SIMPLE, SQUARE

    box_map = {
        "rounded": ROUNDED,
        "simple": SIMPLE,
        "square": SQUARE,
    }
    box = box_map.get(box_style, ROUNDED)

    table = Table(title=title, box=box, show_header=show_header)

    # Add columns
    for col in columns:
        table.add_column(col, style="cyan" if col == columns[0] else None)

    # Add rows
    for row in data:
        values = [str(row.get(col, "")) for col in columns]
        table.add_row(*values)

    console.print(table)


# =============================================================================
# Category 5: Banners & Panels
# =============================================================================


def display_banner(
    title: str,
    subtitle: str | None = None,
    version: str | None = None,
) -> None:
    """
    Display a welcome banner.

    Args:
        title: Main title text
        subtitle: Optional subtitle
        version: Optional version string
    """
    console = get_console()

    content = Text()
    content.append(title, style="bold cyan")

    if subtitle:
        content.append("\n")
        content.append(subtitle, style="muted")

    if version:
        content.append("\n")
        content.append(f"v{version}", style="dim cyan")

    console.print(
        Panel(
            content,
            border_style="cyan",
            expand=False,
            padding=(1, 4),
        )
    )


def display_panel(
    content: str,
    title: str | None = None,
    style: str = "default",
) -> None:
    """
    Display content in a panel.

    Args:
        content: Text content for the panel
        title: Optional panel title
        style: Panel style - "default", "info", "warning", "error", "success"
    """
    console = get_console()

    style_map = {
        "default": "white",
        "info": "blue",
        "warning": "yellow",
        "error": "red",
        "success": "green",
    }
    border_style = style_map.get(style, "white")

    console.print(
        Panel(
            content,
            title=title,
            border_style=border_style,
            expand=False,
        )
    )


def display_separator(char: str = "─", style: str = "muted") -> None:
    """
    Display a horizontal separator line.

    Args:
        char: Character to use for the separator
        style: Rich style for the separator
    """
    console = get_console()
    width = console.width or 80
    console.print(f"[{style}]{char * width}[/{style}]")


# =============================================================================
# Category 4: Domain-Specific Displays
# =============================================================================


def display_help(
    commands: dict[str, str],
    tips: list[str] | None = None,
    title: str = "Available Commands",
) -> None:
    """
    Display help information with command descriptions.

    Args:
        commands: Dictionary of command -> description
        tips: Optional list of usage tips
        title: Title for the help section
    """
    console = get_console()

    # Commands table
    table = Table(title=title, box=None, show_header=True, padding=(0, 2))
    table.add_column("Command", style="cyan bold")
    table.add_column("Description", style="white")

    for cmd, desc in sorted(commands.items()):
        table.add_row(cmd, desc)

    console.print(table)

    # Tips panel
    if tips:
        console.print()
        tips_text = "\n".join(f"• {tip}" for tip in tips)
        console.print(
            Panel(
                tips_text,
                title="Tips",
                border_style="green",
                expand=False,
            )
        )


def display_command_help(
    name: str,
    description: str,
    usage: str,
    arguments: list[dict[str, Any]],
    aliases: list[str] | None = None,
) -> None:
    """
    Display detailed help for a single command.

    Args:
        name: Command name
        description: Full description
        usage: Usage string (e.g., "/reset [--transcript]")
        arguments: List of argument dicts with name, description, required, default, choices
        aliases: Optional list of aliases
    """  # noqa: E501
    console = get_console()

    # Header
    console.print(f"\n[cyan bold]/{name}[/cyan bold]")
    if aliases:
        console.print(f"[dim]Aliases: {', '.join('/' + a for a in aliases)}[/dim]")

    # Description
    console.print(f"\n{description}\n")

    # Usage
    console.print(f"[yellow]Usage:[/yellow] {usage}\n")

    # Arguments
    if arguments:
        console.print("[yellow]Arguments:[/yellow]")
        for arg in arguments:
            req_marker = "[red]*[/red] " if arg.get("required") else "  "
            name_str = f"[green]{arg['name']}[/green]"
            desc_str = arg.get("description", "")

            # Build suffix with default and choices
            suffix_parts = []
            if arg.get("default") is not None:
                suffix_parts.append(f"default: {arg['default']}")
            if arg.get("choices"):
                suffix_parts.append(f"choices: {', '.join(arg['choices'])}")
            suffix = f" [dim]({', '.join(suffix_parts)})[/dim]" if suffix_parts else ""

            console.print(f"  {req_marker}{name_str}: {desc_str}{suffix}")
        console.print()


def display_tool_budget(
    tools: list[dict[str, Any]],
    circuit_states: dict[str, str] | None = None,
) -> None:
    """
    Display tool execution statistics and circuit breaker states.

    Args:
        tools: List of tool info dicts with keys: name, calls, tokens, avg_time
        circuit_states: Dict mapping tool names to circuit state (CLOSED/OPEN/HALF_OPEN)
    """
    console = get_console()

    table = Table(title="Tool Budget", show_header=True)
    table.add_column("Tool", style="cyan")
    table.add_column("Calls", justify="right")
    table.add_column("Tokens", justify="right")
    table.add_column("Avg Time", justify="right")

    if circuit_states:
        table.add_column("Circuit", justify="center")

    for tool in tools:
        name = tool.get("name", "unknown")
        calls = str(tool.get("calls", 0))
        tokens = str(tool.get("tokens", 0))
        avg_time = f"{tool.get('avg_time', 0):.2f}s"

        row = [name, calls, tokens, avg_time]

        if circuit_states:
            state = circuit_states.get(name, "CLOSED")
            state_style = {
                "CLOSED": "[green]CLOSED[/green]",
                "OPEN": "[red]OPEN[/red]",
                "HALF_OPEN": "[yellow]HALF_OPEN[/yellow]",
            }.get(state, state)
            row.append(state_style)

        table.add_row(*row)

    console.print(table)


def display_memory_stats(stats: dict[str, Any]) -> None:
    """
    Display memory system statistics.

    Args:
        stats: Dict with keys like: entities, facts, insights, summaries,
               history_turns, lifecycle_counts, etc.
    """
    console = get_console()

    # Main stats table
    table = Table(title="Memory Statistics", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    main_metrics = [
        ("Entities", stats.get("entities", 0)),
        ("Facts", stats.get("facts", 0)),
        ("Insights", stats.get("insights", 0)),
        ("Summaries", stats.get("summaries", 0)),
        ("History Turns", stats.get("history_turns", 0)),
        ("Sessions", stats.get("sessions", 0)),
    ]

    for metric, value in main_metrics:
        table.add_row(metric, str(value))

    console.print(table)

    # Lifecycle distribution if available
    lifecycle = stats.get("lifecycle", {})
    if lifecycle:
        console.print()
        lc_table = Table(title="Lifecycle Distribution", show_header=True)
        lc_table.add_column("Stage", style="cyan")
        lc_table.add_column("Count", justify="right")
        lc_table.add_column("Percentage", justify="right")

        total = sum(lifecycle.values()) or 1
        for stage, count in lifecycle.items():
            pct = f"{(count / total) * 100:.1f}%"
            lc_table.add_row(stage, str(count), pct)

        console.print(lc_table)


def display_entities(
    entities: list[dict[str, Any]],
    relationships: list[str] | None = None,
) -> None:
    """
    Display graph entities and their relationships.

    Args:
        entities: List of entity dicts with keys: id, type, label, properties, hit_count
        relationships: Optional list of relationship summary strings
    """
    console = get_console()

    # Entities table
    table = Table(title="Entities", show_header=True)
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Label")
    table.add_column("Hits", justify="right")

    for entity in entities:
        table.add_row(
            str(entity.get("id", ""))[:12],
            entity.get("type", ""),
            entity.get("label", ""),
            str(entity.get("hit_count", 0)),
        )

    console.print(table)

    # Relationships
    if relationships:
        console.print()
        console.print("[bold]Relationships:[/bold]")
        for rel in relationships:
            console.print(f"  • {rel}")


def display_history(
    turns: list[dict[str, Any]],
    prior_turns: list[dict[str, Any]] | None = None,
    user_name: str = "User",
    assistant_name: str = "Assistant",
) -> None:
    """
    Display conversation history.

    Args:
        turns: List of turn dicts with keys: user_message, assistant_message, timestamp
        prior_turns: Optional prior session turns
        user_name: Display name for user
        assistant_name: Display name for assistant
    """
    console = get_console()

    def format_turn(turn: dict[str, Any], is_prior: bool = False) -> None:
        timestamp = turn.get("timestamp", "")
        if hasattr(timestamp, "strftime"):
            timestamp = timestamp.strftime("%Y-%m-%d %H:%M")
        elif timestamp:
            timestamp = str(timestamp)[:16]

        prefix = "[dim][prior] [/dim]" if is_prior else ""
        time_str = f"[dim]{timestamp}[/dim] " if timestamp else ""

        # User message
        user_msg = turn.get("user_message", "")
        if user_msg:
            console.print(
                f"{prefix}{time_str}[bold cyan]{user_name}:[/bold cyan] {user_msg}"
            )

        # Assistant message
        asst_msg = turn.get("assistant_message", "")
        if asst_msg:
            console.print(
                f"{prefix}{time_str}[bold green]{assistant_name}:[/bold green] {asst_msg}"  # noqa: E501
            )

        console.print()

    # Prior session turns
    if prior_turns:
        console.print("[bold yellow]Prior Sessions:[/bold yellow]")
        console.print()
        for turn in prior_turns:
            format_turn(turn, is_prior=True)
        display_separator()

    # Current session turns
    console.print("[bold]Current Session:[/bold]")
    console.print()
    for turn in turns:
        format_turn(turn)


def display_context_payload(
    payload: dict[str, Any],
    token_counts: dict[str, int] | None = None,
) -> None:
    """
    Display the assembled context payload.

    Args:
        payload: Context payload dict with history, insights, summaries, etc.
        token_counts: Optional dict of component -> token count
    """
    console = get_console()

    console.print(Panel("[bold]Context Payload[/bold]", border_style="cyan"))

    # Token budget summary
    if token_counts:
        table = Table(title="Token Budget", show_header=True)
        table.add_column("Component", style="cyan")
        table.add_column("Tokens", justify="right")

        total = 0
        for component, count in token_counts.items():
            table.add_row(component, str(count))
            total += count

        table.add_row("[bold]Total[/bold]", f"[bold]{total}[/bold]")
        console.print(table)
        console.print()

    # History count
    history = payload.get("history", [])
    prior_history = payload.get("prior_history", [])
    console.print(
        f"[cyan]History:[/cyan] {len(history)} turns ({len(prior_history)} prior)"
    )

    # Insights
    insights = payload.get("insights", [])
    if insights:
        console.print(f"[cyan]Insights:[/cyan] {len(insights)}")
        for i, insight in enumerate(insights[:3], 1):
            text = insight.get("text", str(insight))[:80]
            console.print(f"  {i}. {text}...")

    # Summaries
    summaries = payload.get("summaries", [])
    if summaries:
        console.print(f"[cyan]Summaries:[/cyan] {len(summaries)}")

    # Key facts
    key_facts = payload.get("key_facts", [])
    if key_facts:
        console.print(f"[cyan]Key Facts:[/cyan] {len(key_facts)}")

    # Entities
    entities = payload.get("entities", [])
    if entities:
        console.print(f"[cyan]Entities:[/cyan] {len(entities)}")

    # Debug info
    debug_info = payload.get("debug_info", {})
    if debug_info:
        console.print()
        console.print("[dim]Debug Info:[/dim]")
        for key, value in debug_info.items():
            if not key.startswith("_"):
                console.print(f"  [dim]{key}: {value}[/dim]")
