"""Capture pilot behavior from a clean Git export, using only fake app services."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib
import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

RETIRED = (
    "clear-tools",
    "inject-tools",
    "recommend-tools",
    "run-tool",
    "tool-budget",
    "inject-payload",
    "prime",
    "set",
    "vars",
)


async def capture(source: Path) -> dict[str, object]:
    # Explicit export paths override installed editable source for every workspace
    # package; third-party dependencies still come from the existing test env.
    sources = sorted((source / "packages").glob("*/src"))
    sys.path[:0] = [str(path) for path in sources]
    from friday_chat.app import FridayChatApp, ListInputSource, ListOutputSink
    from friday_chat.commands.registry import (
        CommandArgument,
        CommandContext,
        CommandRegistry,
        CommandResult,
        RegistryCommandContext,
        _exit_handler,
        _help_handler,
        build_default_registry,
    )
    from friday_chat.commands.session import cls_handler
    from friday_chat.config import FridayChatConfig
    from friday_chat.runtime import build_runtime

    registry = build_default_registry()
    if len(registry.canonical_names()) != 41 or len(registry.command_names()) != 44:
        raise RuntimeError("Expected the accepted 41-name, three-alias surface")
    names = sorted(registry.command_names())
    focuses = [None, "", " ", *names, *RETIRED, "unknown-pilot-name", "/q", "//q"]
    help_rows = [
        {"focus": focus, "output": registry.render_help(focus)} for focus in focuses
    ]
    inputs = [
        "ordinary text",
        " /help",
        "/",
        "/ HELP",
        "//HELP",
        "///HELP",
        "/ /HELP",
        "/HeLp",
        "/help\tq",
        "/help\nq",
        "/help q",
        "/help /q",
        "/help //q",
        "/help exit ignored",
        '/help "exit ignored"',
        "/exit",
        "/quit extra",
        "/q",
        "/cls extra",
        "/clearscreen",
        *("/" + name for name in RETIRED),
    ]
    dispatch = []
    for text in inputs:
        context = RegistryCommandContext(registry=registry)
        handled, result = await registry.execute(text, context)
        dispatch.append(
            {
                "input": text,
                "handled": handled,
                "output": None if result is None else result.output,
                "result_handled": None if result is None else result.handled,
                "exit": None if result is None else result.exit_requested,
                "effects": []
                if result is None
                else [effect.value for effect in result.ui_effects],
                "context_exit": context.exit_requested,
            }
        )

    custom = []

    def custom_help(label: str, argument: CommandArgument) -> None:
        selected = CommandRegistry()
        selected.register(
            "inspect",
            description="Inspect item.",
            category="utility",
            arguments=(argument,),
            aliases=("show",),
        )
        for focus in (None, "inspect", "show", "absent"):
            try:
                value = {"output": selected.render_help(focus)}
            except (TypeError, ValueError) as error:
                value = {"exception": type(error).__name__}
            custom.append({"case": label, "focus": focus, **value})

    for label, kwargs in (
        ("numeric-default", {"default": 7}),
        ("truthy-required", {"required": "yes"}),
        ("falsy-required", {"required": 0}),
        ("list-choices", {"choices": ["text", "json"]}),
        ("string-choices", {"choices": "ab"}),
        ("mapping-choices", {"choices": {"text": 1, "json": 2}}),
        ("invalid-choice", {"choices": ("text", 7)}),
    ):
        # Intentionally invalid static types characterize the permissive legacy API.
        custom_help(label, CommandArgument("format", "Output format.", **kwargs))
    selected = CommandRegistry()
    selected.register("safe", description="Safe.", category="utility")
    selected.register(
        "bad",
        description="Bad.",
        category="utility",
        arguments=(CommandArgument("arg", "Argument.", choices=(7,)),),
    )
    for focus in ("safe", "unknown"):
        custom.append(
            {
                "case": "unrelated-bad-entry",
                "focus": focus,
                "output": selected.render_help(focus),
            }
        )
    for name, aliases in ((" /odd ", ("",)), ("plain", (" /ALIAS ",))):
        selected = CommandRegistry()
        selected.register(name, description="Odd.", category="utility", aliases=aliases)
        for focus in (None, "", " ", " /odd ", "/alias", " //ALIAS "):
            custom.append(
                {
                    "case": "normalization",
                    "name": name,
                    "focus": focus,
                    "output": selected.render_help(focus),
                }
            )
    empty = CommandRegistry()
    custom.append({"case": "empty-catalog", "output": empty.render_help()})

    async def sentinel(_context, args, metadata):
        return CommandResult(output=f"custom:{metadata.name}:{args!r}")

    for name in ("help", "exit", "cls", *RETIRED):
        selected = CommandRegistry()
        selected.register(
            name, description="Custom.", category="custom", handler=sentinel
        )
        _, result = await selected.execute("/" + name + " extra")
        custom.append({"case": "custom-handler", "name": name, "output": result.output})
    for name, handler in (
        ("renamed-help", _help_handler),
        ("renamed-exit", _exit_handler),
        ("renamed-cls", cls_handler),
    ):
        selected = CommandRegistry()
        selected.register(
            name, description="Wrapper.", category="custom", handler=handler
        )
        for context in (CommandContext(), RegistryCommandContext(registry=empty)):
            _, result = await selected.execute("/" + name, context)
            custom.append(
                {
                    "case": "wrapper-context",
                    "name": name,
                    "registry_context": isinstance(context, RegistryCommandContext),
                    "output": result.output,
                    "exit": result.exit_requested,
                    "effects": [effect.value for effect in result.ui_effects],
                }
            )

    async def capture_lifecycle(display_kind):
        events = []
        config = FridayChatConfig.model_validate({"llm": {"model": "fake/pilot-probe"}})
        runtime = build_runtime(config, fake=True, session_id="pilot-frozen-probe")
        original_close = runtime.async_clients.close

        async def close():
            events.append("close_clients")
            await original_close()

        runtime.async_clients.close = close

        class Output(ListOutputSink):
            async def write(self, text):
                events.append("output:" + text)
                await super().write(text)

        class Display:
            def render_banner(self, **_kwargs):
                pass

            def prompt_text(self, **_kwargs):
                return "User: "

            def create_heartbeat(self, _kind):
                return self

            def start(self):
                pass

            def stop(self):
                pass

            def clear_screen(self):
                events.append("clear")
                if display_kind == "failed":
                    raise RuntimeError("private display detail")

        output = Output()
        app = FridayChatApp(
            runtime=runtime,
            input_source=ListInputSource(["/cls", "/clearscreen", "/q"]),
            output_sink=output,
            display=None if display_kind == "missing" else Display(),
        )
        result = await app.run()
        return {
            "display": display_kind,
            "events": events,
            "output": output.values,
            "result": asdict(result),
            "context_exit": app.command_context.exit_requested,
            "started": app.started,
            "background_closed": app.background.closed,
            "client_close_count": runtime.async_clients.close_calls,
            "transcript_finalized": runtime.transcript.finalized,
        }

    lifecycle = [
        await capture_lifecycle(kind) for kind in ("available", "missing", "failed")
    ]
    origins = {}
    for name in (
        "friday_chat.commands.registry",
        "friday_chat.commands.session",
        "friday_chat.commands.contracts",
        "friday_chat.app",
        "friday_chat.runtime",
    ):
        origin = Path(importlib.import_module(name).__file__).resolve()
        if not origin.is_relative_to(source):
            raise RuntimeError(f"Module escaped clean export: {name}")
        origins[name] = str(origin.relative_to(source))
    source_hashes = {
        str(path.relative_to(source)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((source / "packages").glob("*/src/**/*.py"))
    }
    return {
        "schema": 1,
        "provenance": {
            "source_root": str(source),
            "module_origins": origins,
            "source_hashes": source_hashes,
            "python": sys.version,
        },
        "observations": {
            "metadata": {
                name: asdict(value) for name, value in sorted(registry.commands.items())
            },
            "help": help_rows,
            "dispatch": dispatch,
            "custom": custom,
            "lifecycle": lifecycle,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    source = args.source_root.resolve()
    entries = subprocess.check_output(["git", "ls-tree", "-r", "-z", args.revision])
    expected = {}
    for entry in entries.decode().split("\0"):
        if not entry:
            continue
        attributes, name = entry.split("\t", 1)
        if name.startswith("packages/") and "/src/" in name and name.endswith(".py"):
            expected[name] = attributes.split()[2]
    actual = {
        str(path.relative_to(source))
        for path in (source / "packages").glob("*/src/**/*.py")
    }
    if not expected or actual != set(expected):
        raise SystemExit("Export source inventory differs from Git revision")
    for name, blob in expected.items():
        data = (source / name).read_bytes()
        if hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() != blob:
            raise SystemExit(f"Export differs from Git revision: {name}")
    document = asyncio.run(capture(source))
    document["provenance"]["revision"] = (
        subprocess.check_output(["git", "rev-parse", "--verify", args.revision])
        .decode()
        .strip()
    )
    document["provenance"]["capture_sha256"] = hashlib.sha256(
        Path(__file__).read_bytes()
    ).hexdigest()
    args.output.write_text(json.dumps(document, sort_keys=True, indent=2) + "\n")
    print(
        "Captured:",
        {key: len(value) for key, value in document["observations"].items()},
    )


if __name__ == "__main__":
    main()
