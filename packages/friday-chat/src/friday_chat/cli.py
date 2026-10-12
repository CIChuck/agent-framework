"""Command-line entry point for FridayV2."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Annotated

import typer

from friday_chat import __version__
from friday_chat.app import FridayChatApp
from friday_chat.config import (
    FridayChatConfig,
    FridayChatConfigError,
    load_friday_py_config,
)
from friday_chat.display import (
    FridayChatDisplayConfigError,
    FridayCliDisplay,
    FridayCliInputSource,
    FridayCliOutputSink,
    resolve_display_config,
)
from friday_chat.replay import ReplayService, parse_replay_delay
from friday_chat.runtime import build_runtime
from friday_chat.turns.processor import TurnProcessor

app = typer.Typer(
    name="friday-chat",
    help=(
        "FridayV2 chat application. Runtime features are implemented "
        "incrementally from the FridayV2 planning packet."
    ),
    invoke_without_command=True,
    no_args_is_help=True,
)


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the FridayV2 package version and exit.",
        ),
    ] = False,
    replay: Annotated[
        Path | None,
        typer.Option(
            "--replay",
            help="Replay an exported transcript CSV and exit.",
        ),
    ] = None,
    replay_delay: Annotated[
        str | None,
        typer.Option(
            "--replay-delay",
            help="Delay in seconds between replayed user turns.",
        ),
    ] = None,
    config: Annotated[
        Path | None,
        typer.Option(
            "--config",
            help="Load Friday-py-style YAML config and start the interactive chat.",
        ),
    ] = None,
    cli_config: Annotated[
        Path | None,
        typer.Option(
            "--cli-config",
            help="Load Friday CLI display configuration.",
        ),
    ] = None,
    runtime_mode: Annotated[
        str,
        typer.Option(
            "--runtime",
            help="Runtime mode for --config startup: fake or real.",
        ),
    ] = "fake",
) -> None:
    """Run the FridayV2 chat CLI."""
    if version:
        typer.echo(f"friday-chat {__version__}")
        raise typer.Exit()
    if replay is not None:
        try:
            delay = parse_replay_delay(replay_delay)
            result = asyncio.run(ReplayService().replay_csv(replay, delay_seconds=delay))
        except (FileNotFoundError, ValueError) as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from exc
        typer.echo(f"Replayed {result.processed_turns} turns from {replay}")
        raise typer.Exit()
    if config is not None:
        try:
            loaded_config = load_friday_py_config(config)
            _emit_config_diagnostics(loaded_config)
            display_result = resolve_display_config(
                config_path=config,
                cli_config_path=cli_config,
            )
            display = FridayCliDisplay(
                display_result.config,
                banner=display_result.banner,
                response=display_result.response,
            )
            resolved_runtime_mode = _resolve_runtime_mode(runtime_mode)
            runtime = build_runtime(
                loaded_config,
                fake=resolved_runtime_mode == "fake",
            )
            if runtime.telemetry is not None:
                snapshot = runtime.telemetry.snapshot()
                typer.echo(
                    f"Telemetry: {snapshot.state} ({snapshot.provider})", err=True
                )
            asyncio.run(
                FridayChatApp(
                    runtime=runtime,
                    input_source=FridayCliInputSource(
                        display.prompt_text(user_name=loaded_config.chat.user_name)
                    ),
                    output_sink=FridayCliOutputSink(display_result.response),
                    turn_handler=TurnProcessor(
                        runtime,
                        heartbeat_factory=display,
                    ),
                    display=display,
                    version=__version__,
                ).run()
            )
        except (FridayChatConfigError, FridayChatDisplayConfigError) as exc:
            typer.echo(f"Config error: {exc}")
            raise typer.Exit(code=1) from exc
        except ValueError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from exc
        raise typer.Exit()


def _emit_config_diagnostics(config: FridayChatConfig) -> None:
    """Surface actionable, content-safe configuration migration diagnostics."""
    for diagnostic in config.diagnostics:
        typer.echo(
            f"Config warning [{diagnostic.path}]: {diagnostic.message}",
            err=True,
        )


def _resolve_runtime_mode(value: str) -> str:
    env_value = os.getenv("FRIDAY_CHAT_RUNTIME")
    mode = (env_value or value).strip().lower()
    if mode not in {"fake", "real"}:
        raise ValueError("Runtime mode must be 'fake' or 'real'.")
    return mode
