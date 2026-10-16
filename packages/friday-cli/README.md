# Friday CLI Components

Reusable Rich and Prompt Toolkit components for terminal applications: display, input, commands, configuration and session lifecycle. For the supported Friday chat application, install and run **Friday Chat**.

**Distribution:** [friday-framework-cli](https://pypi.org/project/friday-framework-cli/) · **Import:** `friday_cli`
**Python:** 3.13.4+ · **Status:** alpha · **License:** MIT

## Installation

```bash
python -m pip install "friday-framework-cli==0.1.0a4"
```

Friday distributions use the same release version; keep internal Friday dependencies aligned.

## Quick start: display structured output

```python
from friday_cli import display_success, display_table, spinner

display_success("Application ready")
display_table([{"package": "friday-cli", "status": "ready"}], title="Components")
with spinner("Preparing session") as status:
    status.update("Prepared")
```

This only renders terminal output. It makes no model requests and does not start an interactive session.

## Choose a component

| Surface | Public entry points |
| --- | --- |
| Console and display | `get_console`, `set_console`, `display_error`, `display_json`, `display_table`, `display_panel` |
| Progress | `spinner`, `progress_bar`, `ProgressTracker` |
| Interactive input | `InputHandler`, `CommandCompleter` |
| Slash commands | `CommandRegistry`, `arg` |
| Session lifecycle | `SessionConfig`, `SessionManager`, `managed_session` |
| Theme configuration | `CLIConfig`, `load_cli_config`, `reset_console` |
| Cancellation | `CancellationToken`, `CancellableContext`, `run_cancellable` |

`InputHandler` needs a suitable interactive terminal. A command registry parses and dispatches your handlers; it does not create an agent or grant permissions to its commands. Use `SessionManager` for owned session startup/shutdown and keep session factories application-specific.

## Configuration and application choice

`cli-config.yaml` configures theme colors, status icons and prompts. Load it through `load_cli_config` and rebuild the console with `reset_console` when changing an existing console. Runtime/model/tool configuration belongs to the application, not the terminal theme.

The package metadata declares a historical `friday` console entry point, but `friday_cli.main` currently contains only a placeholder: that executable is not a working application entry point. Use `friday-chat --help` for the maintained chat CLI. Legacy container, REPL and server modules remain compatibility surfaces; prefer `friday_runtime.RuntimeKernel` for new headless applications.

## Development

Work from the monorepo root after the [shared contributor setup](https://github.com/CIChuck/agent-framework/blob/master/README.md#development).
Run the focused suite:

```bash
uv run --no-sync pytest packages/friday-cli/tests_cli -q
```

## Documentation and support

[Chat application](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-chat/README.md) · [Runtime composition](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-runtime/README.md) · [Theme configuration](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-cli/src/friday_cli/cli_config.py) · [Source](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-cli/src/friday_cli) · [Issues](https://github.com/CIChuck/agent-framework/issues) · [Contributing](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/15-contributing.md)

## License

[MIT](https://github.com/CIChuck/agent-framework/blob/master/LICENSE).
