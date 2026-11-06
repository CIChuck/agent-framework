"""Run outside the checkout with the disposable wheel environment's python -I.

Usage: python -I installed_probe.py OUTPUT_JSON CHECKOUT_ROOT
Only stateless in-memory registry probes and entry-point --help are exercised.
"""

from __future__ import annotations

import asyncio
import importlib
import importlib.metadata
import json
import platform
import socket
import sys
from dataclasses import asdict
from pathlib import Path

NETWORK_ATTEMPTS = 0


def deny_network(*args: object, **kwargs: object) -> None:
    global NETWORK_ATTEMPTS
    NETWORK_ATTEMPTS += 1
    raise RuntimeError("Network disabled for installed baseline probe")


socket.socket.connect = deny_network
socket.create_connection = deny_network


async def main() -> None:
    output = Path(sys.argv[1]).resolve()
    checkout = Path(sys.argv[2]).resolve()
    prefix = Path(sys.prefix).resolve()
    if Path.cwd().resolve().is_relative_to(checkout):
        raise RuntimeError("Probe must run outside the source checkout")
    if any(Path(p).resolve().is_relative_to(checkout) for p in sys.path if p):
        raise RuntimeError("Source checkout is present on sys.path")

    from friday_chat.commands.registry import (
        RegistryCommandContext,
        _parse_command_input,
        build_default_registry,
    )
    from friday_cli.commands import ArgumentSpec, CommandRegistry

    chat = build_default_registry()
    cli = CommandRegistry()
    cli_calls: list[tuple[str, str]] = []

    def sync_handler(context: object, path: str) -> str:
        cli_calls.append(("sync", path))
        return path

    async def async_handler(context: object) -> str:
        cli_calls.append(("async", ""))
        return "async-ok"

    cli.register(
        "read",
        sync_handler,
        aliases=["r"],
        arguments=[ArgumentSpec("path", required=True)],
    )
    cli.register("async", async_handler)
    cli_result = await cli.execute('/r "a b.txt"', object())
    if cli_result != (True, "a b.txt"):
        raise RuntimeError("Generic CLI quoted alias behavior changed")
    if await cli.execute("/async", object()) != (True, "async-ok"):
        raise RuntimeError("Generic CLI async behavior changed")

    expected = {
        "/": ("", ()),
        "/HELP topic": ("help", ("topic",)),
        "//HELP topic": ("help", ("topic",)),
        "///HELP topic": ("/help", ("topic",)),
        "/ /HELP topic": ("help", ("topic",)),
        "/   HELP  A B": ("help", ("A", "B")),
        '/read "a b.txt"': ("read", ('"a', 'b.txt"')),
    }
    parsed = {}
    for text, tokens in expected.items():
        actual = _parse_command_input(text)
        if actual != tokens:
            raise RuntimeError(f"Frozen Chat parser mismatch for {text!r}")
        parsed[text] = {"chat": actual, "generic_cli": cli.parse_input(text)}

    dispatch = {}
    for text in (
        "plain text",
        " /HELP topic",
        "/",
        "/missing-command",
        "/help exit",
        "/q",
        "/quit",
        "/clearscreen",
    ):
        context = RegistryCommandContext(registry=chat)
        handled, result = await chat.execute(text, context)
        dispatch[text] = {
            "handled": handled,
            "result": asdict(result) if result else None,
            "exit_requested": context.exit_requested,
        }
    if dispatch["plain text"]["handled"] or dispatch[" /HELP topic"]["handled"]:
        raise RuntimeError("Leading text dispatch behavior changed")
    if not dispatch["/q"]["exit_requested"] or not dispatch["/quit"]["exit_requested"]:
        raise RuntimeError("Exit aliases changed")
    if dispatch["/clearscreen"]["result"]["ui_effects"] != ("clear_screen",):
        raise RuntimeError("Clear alias intent changed")

    entries = []
    for package in ("friday-framework-cli", "friday-chat"):
        dist = importlib.metadata.distribution(package)
        for ep in dist.entry_points:
            if ep.group != "console_scripts":
                continue
            row = {"distribution": package, "name": ep.name, "target": ep.value}
            try:
                app = ep.load()
                row["load"] = type(app).__name__
                if ep.name == "friday-chat":
                    from typer.testing import CliRunner

                    help_result = CliRunner().invoke(app, ["--help"])
                    row["help_exit_code"] = help_result.exit_code
                    row["help_contains_usage"] = "Usage" in help_result.stdout
                    if help_result.exit_code != 0:
                        row["help_error_type"] = type(help_result.exception).__name__
            except Exception as exc:
                row["load_error_type"] = type(exc).__name__
                row["load_error"] = str(exc)
            entries.append(row)

    origins = {}
    for name in (
        "friday_chat",
        "friday_cli",
        "friday_runtime",
        "friday_core",
        "friday_memory",
        "friday_agent",
        "friday_tools",
        "friday_transcript",
        "friday_llm",
    ):
        module = importlib.import_module(name)
        path = Path(module.__file__).resolve()
        if not path.is_relative_to(prefix):
            raise RuntimeError(f"{name} did not load from the disposable environment")
        origins[name] = str(path)

    metadata = {name: asdict(value) for name, value in sorted(chat.commands.items())}
    installed = sorted(
        f"{d.metadata['Name']}=={d.version}" for d in importlib.metadata.distributions()
    )
    report = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "cwd": str(Path.cwd()),
        "prefix": str(prefix),
        "isolated": bool(sys.flags.isolated),
        "module_origins": origins,
        "installed_distributions": installed,
        "chat_command_count": len(metadata),
        "chat_alias_count": sum(len(v["aliases"]) for v in metadata.values()),
        "chat_metadata": metadata,
        "parser_fixtures": parsed,
        "chat_dispatch": dispatch,
        "generic_cli_calls": cli_calls,
        "entrypoints": entries,
        "network_attempts_blocked": NETWORK_ATTEMPTS,
        "limits": "No runtime/store construction, live provider/tool calls, full installed owning-suite or terminal UAT. Known CLI entry-point failure is an observation, not a repair or waiver.",
    }
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "chat_command_count",
                    "chat_alias_count",
                    "entrypoints",
                    "network_attempts_blocked",
                )
            }
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
