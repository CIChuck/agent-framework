"""Disposable, provider-free dispatch and installed-metadata observations."""

import asyncio
import importlib.metadata
import json
import platform
from pathlib import Path

from friday_chat.commands.contracts import CommandContext
from friday_chat.commands.registry import _parse_command_input, build_default_registry
from friday_cli.commands import CommandRegistry


async def main():
    chat = build_default_registry()
    cli = CommandRegistry()
    rows = {}
    for text in (
        "plain text",
        "/",
        "/missing-command",
        "/help exit",
        "/q",
        "/quit",
        "/clearscreen",
    ):
        ctx = CommandContext()
        handled, result = await chat.execute(text, ctx)
        rows[text] = {
            "handled": handled,
            "output": result.output if result else None,
            "exit_requested": ctx.exit_requested,
            "ui_effects": [effect.value for effect in result.ui_effects]
            if result
            else [],
        }
    parser_inputs = ['/read "a b.txt"', "/", "/HELP exit"]
    entrypoints = []
    for package in ("friday-framework-cli", "friday-chat"):
        dist = importlib.metadata.distribution(package)
        for ep in dist.entry_points:
            if ep.group != "console_scripts":
                continue
            try:
                loaded = ep.load()
                observation = f"loads {type(loaded).__name__}; not invoked"
            except Exception as exc:
                observation = f"{type(exc).__name__}: {exc}"
            entrypoints.append(
                {
                    "distribution": package,
                    "version": dist.version,
                    "name": ep.name,
                    "target": ep.value,
                    "observation": observation,
                }
            )
    report = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "chat_dispatch": rows,
        "parsing": {
            s: {"chat": _parse_command_input(s), "generic_cli": cli.parse_input(s)}
            for s in parser_inputs
        },
        "entrypoints": entrypoints,
        "limits": "Current workspace environment, not isolated wheels. Only stateless in-memory dispatch probes; no provider or tool execution.",
    }
    output = Path(__file__).with_name("probes.json")
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
