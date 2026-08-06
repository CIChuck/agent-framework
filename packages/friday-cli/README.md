# Friday Framework CLI

Rich-based terminal interface components for the Friday Framework.

**Version:** 0.1.0

## Overview

Friday CLI provides professional terminal interface components using the [Rich](https://rich.readthedocs.io/) and [Prompt Toolkit](https://python-prompt-toolkit.readthedocs.io/) libraries, including:

- **Display**: Status messages, tables, syntax highlighting, progress indicators
- **Input**: Readline-style editing, command history, auto-completion

## Installation

```bash
# From the monorepo root
uv sync

# Or install directly from PyPI
pip install friday-framework-cli
```

## Quick Start

```python
from friday_cli import (
    display_error,
    display_success,
    display_table,
    spinner,
)

# Status messages
display_success("Task completed")
display_error("Something went wrong", exception=ValueError("details"))

# Tables
data = [{"name": "Alice", "role": "Admin"}, {"name": "Bob", "role": "User"}]
display_table(data, title="Users")

# Progress spinner
with spinner("Processing...") as status:
    # do work
    status.update("Almost done...")
```

## API Reference

### Console Management

#### `get_console() -> Console`
Returns the shared Rich Console instance (singleton pattern).

#### `set_console(console: Console) -> None`
Sets a custom console instance. Useful for testing or custom output destinations.

```python
from rich.console import Console
from friday_cli import set_console, get_console

# For testing - capture output
import io
string_io = io.StringIO()
test_console = Console(file=string_io, force_terminal=True)
set_console(test_console)

# Reset to default
set_console(None)
```

---

### Status Messages

All status functions display styled messages with icons.

#### `display_error(message: str, exception: Exception | None = None, show_traceback: bool = False) -> None`
Display an error message with red styling and X icon.

```python
display_error("Operation failed")

# With exception details
try:
    raise ValueError("Invalid input")
except ValueError as e:
    display_error("Validation error", exception=e)

# With full traceback
display_error("Critical failure", exception=e, show_traceback=True)
```

#### `display_warning(message: str) -> None`
Display a warning message with yellow styling and warning icon.

```python
display_warning("Configuration not found, using defaults")
```

#### `display_success(message: str) -> None`
Display a success message with green styling and checkmark icon.

```python
display_success("File saved successfully")
```

#### `display_info(message: str) -> None`
Display an info message with blue styling and info icon.

```python
display_info("Processing 42 items...")
```

---

### Structured Data Display

#### `display_json(data: Any, title: str | None = None, indent: int = 2) -> None`
Display JSON data with syntax highlighting.

```python
data = {"status": "ok", "count": 42, "items": ["a", "b", "c"]}
display_json(data, title="API Response")
```

#### `display_code(code: str, language: str = "python", line_numbers: bool = True, title: str | None = None) -> None`
Display code with syntax highlighting.

```python
code = '''
def greet(name: str) -> str:
    return f"Hello, {name}!"
'''
display_code(code, language="python", title="greeting.py")
```

#### `display_table(data: list[dict], title: str | None = None, columns: list[str] | None = None, show_header: bool = True, box_style: str = "rounded") -> None`
Display data as a formatted table.

```python
users = [
    {"name": "Alice", "age": "30", "role": "Admin"},
    {"name": "Bob", "age": "25", "role": "User"},
]
display_table(users, title="Team Members")

# Custom columns (subset or reorder)
display_table(users, columns=["name", "role"])

# Box styles: "rounded", "simple", "square"
display_table(users, box_style="simple")
```

---

### Progress Indicators

#### `spinner(message: str, spinner_type: str = "dots") -> Iterator[Status]`
Context manager for displaying a spinner during long-running operations.

```python
from friday_cli import spinner

with spinner("Loading data..."):
    # do work
    time.sleep(2)

# With status updates
with spinner("Processing...") as status:
    status.update("Step 1: Loading...")
    # step 1
    status.update("Step 2: Transforming...")
    # step 2
```

#### `progress_bar(total: int, description: str = "Processing", show_speed: bool = False) -> Iterator[Progress]`
Context manager for displaying a progress bar.

```python
from friday_cli import progress_bar

with progress_bar(100, "Downloading") as progress:
    task = progress.add_task("file.zip", total=100)
    for i in range(100):
        # do work
        progress.update(task, advance=1)
```

#### `ProgressTracker`
Helper class for tracking multi-step progress.

```python
from friday_cli import ProgressTracker

tracker = ProgressTracker(
    steps=["Load", "Process", "Save"],
    title="Data Pipeline"
)
with tracker:
    tracker.advance("Loading data...")
    # load step
    tracker.advance("Processing...")
    # process step
    tracker.advance("Saving results...")
    # save step
    tracker.complete()
```

---

### Banners and Panels

#### `display_banner(title: str, subtitle: str | None = None, version: str | None = None) -> None`
Display a welcome banner.

```python
display_banner(
    "Friday CLI",
    subtitle="Rich terminal interface",
    version="0.1.0"
)
```

#### `display_panel(content: str, title: str | None = None, style: str = "default") -> None`
Display content in a styled panel.

```python
display_panel("Important information here", title="Notice", style="info")

# Styles: "default", "info", "warning", "error", "success"
display_panel("Operation completed", style="success")
```

#### `display_separator(char: str = "─", style: str = "muted") -> None`
Display a horizontal separator line.

```python
display_separator()
display_separator(char="=", style="cyan")
```

---

### Domain-Specific Displays

These functions are designed for the Friday agent framework's specific use cases.

#### `display_help(commands: dict[str, str], tips: list[str] | None = None, title: str = "Available Commands") -> None`
Display help information with command descriptions.

```python
commands = {
    "/help": "Show this help message",
    "/history": "Show conversation history",
    "/exit": "Exit the program",
}
tips = [
    "Use Tab for command completion",
    "Type /clear to reset the session",
]
display_help(commands, tips=tips)
```

#### `display_tool_budget(tools: list[dict], circuit_states: dict[str, str] | None = None) -> None`
Display tool execution statistics and circuit breaker states.

```python
tools = [
    {"name": "web_search", "calls": 5, "tokens": 1200, "avg_time": 0.8},
    {"name": "file_read", "calls": 12, "tokens": 800, "avg_time": 0.1},
]
circuit_states = {"web_search": "CLOSED", "file_read": "CLOSED"}
display_tool_budget(tools, circuit_states)
```

#### `display_memory_stats(stats: dict[str, Any]) -> None`
Display memory system statistics.

```python
stats = {
    "entities": 42,
    "facts": 156,
    "insights": 23,
    "summaries": 8,
    "history_turns": 50,
    "sessions": 5,
    "lifecycle": {
        "ACTIVE": 30,
        "CONSOLIDATED": 10,
        "ARCHIVED": 2,
    }
}
display_memory_stats(stats)
```

#### `display_entities(entities: list[dict], relationships: list[str] | None = None) -> None`
Display graph entities and their relationships.

```python
entities = [
    {"id": "abc123", "type": "Person", "label": "Alice", "hit_count": 5},
    {"id": "def456", "type": "Project", "label": "Friday", "hit_count": 12},
]
relationships = [
    "Alice --[WORKS_ON]--> Friday",
    "Alice --[KNOWS]--> Bob",
]
display_entities(entities, relationships)
```

#### `display_history(turns: list[dict], prior_turns: list[dict] | None = None, user_name: str = "User", assistant_name: str = "Assistant") -> None`
Display conversation history.

```python
turns = [
    {
        "timestamp": "2024-01-15 10:30",
        "user_message": "Hello!",
        "assistant_message": "Hi there! How can I help?"
    },
]
prior_turns = [
    {
        "timestamp": "2024-01-14 15:00",
        "user_message": "Previous question",
        "assistant_message": "Previous answer"
    },
]
display_history(turns, prior_turns=prior_turns)
```

#### `display_context_payload(payload: dict[str, Any], token_counts: dict[str, int] | None = None) -> None`
Display the assembled context payload.

```python
payload = {
    "history": [{"user": "hi", "assistant": "hello"}],
    "prior_history": [],
    "insights": [{"text": "User prefers concise answers"}],
    "summaries": ["Previous session summary"],
    "key_facts": ["Fact 1", "Fact 2"],
    "entities": [{"label": "Project X"}],
}
token_counts = {
    "history": 500,
    "insights": 200,
    "summaries": 300,
}
display_context_payload(payload, token_counts)
```

---

### Input Handling

Advanced input handling with Prompt Toolkit for readline-style editing.

#### `InputHandler`
Full-featured input handler with history, completion, and styling.

```python
from friday_cli import InputHandler

handler = InputHandler(
    prompt_name="User",
    commands=["help", "history", "exit"],
    command_descriptions={"help": "Show help", "exit": "Quit"},
    history_file="~/.friday_history",
    multiline=False,
    enable_auto_suggest=True,
)

# Synchronous input
text = handler.get_input()

# Async input (for async contexts)
text = await handler.get_input_async()
```

**Features:**
- Readline-style editing (Ctrl+A, Ctrl+E, Ctrl+K, etc.)
- Up/down arrows for history navigation
- Tab completion for slash commands
- Auto-suggestions from history (grayed out text)
- Persistent history to file
- Alt+Enter for newline in multi-line mode

#### `create_friday_input_handler()`
Create a pre-configured handler with Friday CLI commands.

```python
from friday_cli import create_friday_input_handler

handler = create_friday_input_handler(
    user_name="Alice",
    history_file="/path/to/history",
    multiline=False,
)

# All Friday commands are pre-loaded for completion
# /help, /history, /entities, /tools, etc.
```

#### `CommandCompleter`
Standalone completer for slash commands.

```python
from friday_cli import CommandCompleter
from prompt_toolkit import PromptSession

completer = CommandCompleter(
    commands=["help", "search", "quit"],
    meta_dict={"help": "Show help"},
)

session = PromptSession(completer=completer)
```

#### Constants

```python
from friday_cli import FRIDAY_COMMANDS, FRIDAY_COMMAND_DESCRIPTIONS

# FRIDAY_COMMANDS: list of all Friday CLI command names
# FRIDAY_COMMAND_DESCRIPTIONS: dict of command -> description
```

---

### Command Registry

Decorator-based command registration with argument parsing, aliasing, and help generation.

#### `CommandRegistry`
Registry for CLI commands with dispatch and execution.

```python
from friday_cli import CommandRegistry, arg

registry = CommandRegistry()

@registry.command("greet", aliases=["g", "hello"])
def cmd_greet(ctx, name="World"):
    """Greet someone by name."""
    return f"Hello, {name}!"

@registry.command(
    "export",
    arguments=[arg("format", default="json", choices=["json", "csv"])],
    category="data",
)
async def cmd_export(ctx, format="json"):
    """Export data in the specified format."""
    return f"Exported as {format}"

# Execute commands
was_command, result = await registry.execute("/greet Alice", context)
# was_command=True, result="Hello, Alice!"

was_command, result = await registry.execute("/g Bob", context)
# was_command=True, result="Hello, Bob!" (alias)

was_command, result = await registry.execute("not a command", context)
# was_command=False, result=None
```

**Features:**
- Decorator-based registration with `@registry.command()`
- Programmatic registration with `registry.register()`
- Command aliases for shortcuts (`/h` for `/history`)
- Argument parsing with defaults and choices
- Async and sync command support
- Help text from docstrings
- Category grouping for organized help

#### `arg()` Helper
Create argument specifications for commands.

```python
from friday_cli import arg

# Required argument
arg("name", required=True, description="User name")

# Optional with default
arg("format", default="json", choices=["json", "csv", "xml"])
```

#### Help Generation

```python
# Get help as dict
help_dict = registry.get_help()
# {"/greet (/g, /hello)": "Greet someone by name.", ...}

# Get help grouped by category
by_category = registry.get_help_by_category()
# {"general": {...}, "data": {...}}

# Get data for InputHandler completion
names, descriptions = registry.get_command_for_completion()
```

#### Integration Pattern

```python
class MySession:
    def __init__(self):
        self.registry = CommandRegistry()
        self._register_commands()

    def _register_commands(self):
        self.registry.register("help", self.cmd_help, aliases=["?"])
        self.registry.register("exit", lambda ctx: "EXIT", aliases=["quit"])

    async def handle_input(self, user_input):
        # Try registry first
        was_cmd, result = await self.registry.execute(user_input, self)
        if was_cmd:
            return result

        # Fall back to other handling
        return await self.process_chat(user_input)
```

---

### Session Management

Configuration loading, lifecycle management, and graceful shutdown for CLI applications.

#### `SessionConfig`
Configuration container that loads from YAML files and provides typed access.

```python
from friday_cli import SessionConfig, load_config

# Load from YAML file
config = SessionConfig.from_yaml("config.yaml")

# Or create from dict
config = SessionConfig.from_dict({"llm": {"model": "gpt-4"}})

# Typed access to common values
print(config.user_name)        # "User" (default)
print(config.assistant_name)   # "Assistant" (default)
print(config.system_prompt)    # "You are a helpful assistant."
print(config.persist_dir)      # Path or None

# Access any configuration section
print(config.llm["model"])
print(config.memory.get("persist_directory"))

# Nested access with defaults
enabled = config.get_nested("memory", "priming", "enabled", default=True)
```

**Configuration Sections:**
- `llm` - LLM configuration (model, api_key, temperature)
- `embedding` - Embedding model configuration
- `memory` - Memory system settings
- `chat` - Chat display settings (user_name, assistant_name, system_prompt)
- `logging` - Logging configuration
- `extraction` - Entity/fact extraction settings
- `transcript` - Transcript storage settings
- `maintenance` - Maintenance task settings
- `lifecycle` - Memory lifecycle settings
- `tools` - Tool configuration

#### `SessionManager`
Async context manager for session lifecycle with signal handling.

```python
from friday_cli import SessionManager, SessionConfig

config = SessionConfig.from_yaml("config.yaml")

# Basic usage
async with SessionManager(config=config) as ctx:
    print(f"User: {ctx.config.user_name}")
    # ctx.session is None without factory

# With session factory
async def create_session(config):
    return MySession(config)

manager = SessionManager(
    config=config,
    session_factory=create_session,
    on_shutdown=lambda ctx: print("Cleaning up..."),
)

async with manager as ctx:
    session = ctx.session  # Created by factory
    # Use session...
# on_shutdown called automatically
```

**Features:**
- Async context manager (`async with`)
- Signal handling (SIGINT, SIGTERM) for graceful shutdown
- Session factory support (sync or async)
- Shutdown callback for cleanup
- Resource management via SessionContext

#### `SessionContext`
Container for an active session with its resources.

```python
from friday_cli import SessionContext

# Created by SessionManager
ctx = SessionContext(session=my_session, config=config)

# Store resources for cleanup
ctx.set_resource("db", database_connection)
ctx.set_resource("cache", cache_instance)

# Retrieve resources
db = ctx.get_resource("db")
```

#### `managed_session`
Convenience async context manager for simple cases.

```python
from friday_cli import managed_session

async with managed_session(config_path="config.yaml") as ctx:
    print(f"User: {ctx.config.user_name}")

# Or with config object
async with managed_session(config=config, session_factory=factory) as ctx:
    session = ctx.session
```

#### `validate_config`
Validate configuration and return list of errors.

```python
from friday_cli import SessionConfig, validate_config

config = SessionConfig.from_yaml("config.yaml")

# Default validation (requires llm section with model)
errors = validate_config(config)
if errors:
    for error in errors:
        print(f"Config error: {error}")

# Custom required sections
errors = validate_config(config, required_sections=["llm", "memory"])
```

#### Integration Pattern

```python
import asyncio
from friday_cli import SessionManager, SessionConfig, validate_config, display_error

async def main():
    # Load and validate config
    config = SessionConfig.from_yaml("config.yaml")
    errors = validate_config(config, required_sections=["llm"])
    if errors:
        for error in errors:
            display_error(error)
        return

    # Run with session management
    async with SessionManager(
        config=config,
        session_factory=create_my_session,
        on_shutdown=cleanup_resources,
    ) as ctx:
        await run_chat_loop(ctx.session, ctx.config)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Testing

```bash
# Run all tests
uv run pytest apps/friday-cli/tests/ -v

# Run with coverage
uv run pytest apps/friday-cli/tests/ --cov=friday_cli
```

### Testing with Captured Output

```python
import io
from rich.console import Console
from friday_cli import set_console, display_success

def test_display_success():
    string_io = io.StringIO()
    console = Console(file=string_io, force_terminal=True)
    set_console(console)

    display_success("Test passed")

    output = string_io.getvalue()
    assert "Test passed" in output
    assert "✓" in output

    set_console(None)  # Reset
```

---

## CLI Configuration

Friday CLI supports optional theming via a `cli-config.yaml` file. If present, it customizes colors, icons, and prompt styling. If absent, sensible defaults are used.

### Configuration File Location

Place `cli-config.yaml` in the same directory as your main `config.yaml`:

```
your-project/
├── config.yaml          # Main application config
└── cli-config.yaml      # Optional CLI theming
```

### Loading Configuration

```python
from friday_cli import load_cli_config, reset_console

# Load CLI config (looks for cli-config.yaml next to config.yaml)
load_cli_config("path/to/config.yaml")
reset_console()  # Rebuild console with new theme
```

### Configuration Options

```yaml
# cli-config.yaml

# Theme colors (Rich style format)
theme:
  error: "bold red"
  warning: "bold yellow"
  success: "bold green"
  info: "bold blue"
  muted: "dim"
  highlight: "bold cyan"

# Status message icons
icons:
  error: "✗"      # or "[X]" for ASCII
  warning: "⚠"    # or "[!]" for ASCII
  success: "✓"    # or "[OK]" for ASCII
  info: "ℹ"       # or "[i]" for ASCII

# Input prompt styling
prompt:
  style: "bold cyan"
  name_style: "bold cyan"
  separator_style: "white"
  continuation_style: "gray"
```

### Default Theme

| Style | Default | Usage |
|-------|---------|-------|
| `error` | Bold red | Error messages |
| `warning` | Bold yellow | Warning messages |
| `success` | Bold green | Success messages |
| `info` | Bold blue | Info messages |
| `muted` | Dim | Secondary text |
| `highlight` | Bold cyan | Emphasized text |

### Programmatic Configuration

```python
from friday_cli import CLIConfig, ThemeConfig, set_cli_config, reset_console

# Create custom config
config = CLIConfig(
    theme=ThemeConfig(error="magenta", success="bright_green"),
)
set_cli_config(config)
reset_console()

# Or load from dict
config = CLIConfig.from_dict({
    "theme": {"error": "red"},
    "icons": {"success": "[DONE]"},
})
```

---

## Dependencies

- `rich>=13.0.0` - Terminal formatting library
- `prompt_toolkit>=3.0.0` - Input handling with readline-style editing
- `pyyaml>=6.0.0` - YAML configuration loading

---

## License

Part of the Friday Framework. See root LICENSE file.
