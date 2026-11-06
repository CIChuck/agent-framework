"""Capture default wheel imports/help without runtime construction or network.

Usage outside checkout: VENV/bin/python -I probe.py OUTPUT_JSON CHECKOUT_ROOT
The tools/finance and generic CLI entry-point failures are expected baselines.
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib
import importlib.metadata
import json
import platform
import socket
import sys
from dataclasses import asdict
from functools import partial
from pathlib import Path
from typing import NoReturn

STAGE = "initialization"
NETWORK_ATTEMPTS: list[dict[str, str]] = []


def deny_network(operation: str, *args: object, **kwargs: object) -> NoReturn:
    NETWORK_ATTEMPTS.append({"stage": STAGE, "operation": operation})
    raise RuntimeError("Network disabled for default-profile capture")


def audit_network(event: str, args: tuple[object, ...]) -> None:
    if event in {
        "socket.connect",
        "socket.getaddrinfo",
        "socket.gethostbyname",
        "socket.gethostbyaddr",
        "socket.sendto",
        "socket.sendmsg",
    }:
        deny_network(f"audit:{event}")


sys.addaudithook(audit_network)
for operation in (
    "create_connection",
    "getaddrinfo",
    "gethostbyname",
    "gethostbyname_ex",
    "gethostbyaddr",
):
    setattr(socket, operation, partial(deny_network, operation))
for operation in ("connect", "connect_ex", "sendto", "sendmsg"):
    if hasattr(socket.socket, operation):
        setattr(socket.socket, operation, partial(deny_network, operation))


async def main() -> None:
    global STAGE
    output = Path(sys.argv[1]).resolve()
    checkout = Path(sys.argv[2]).resolve()
    prefix = Path(sys.prefix).resolve()
    if not sys.flags.isolated or Path.cwd().resolve().is_relative_to(checkout):
        raise RuntimeError("Run isolated Python from outside the checkout")
    if any(Path(p).resolve().is_relative_to(checkout) for p in sys.path if p):
        raise RuntimeError("Checkout must not appear on sys.path")

    imports: dict[str, dict[str, object]] = {}
    for name in (
        "friday_chat",
        "friday_chat.commands.registry",
        "friday_chat.cli",
        "friday_cli",
        "friday_cli.commands",
        "friday_cli.main",
        "friday_runtime",
        "friday_tools",
    ):
        STAGE = f"import:{name}"
        try:
            module = importlib.import_module(name)
        except Exception as exc:
            imports[name] = {
                "state": "failed",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "missing_module": getattr(exc, "name", None),
            }
        else:
            origin = Path(module.__file__).resolve()
            if not origin.is_relative_to(prefix):
                raise RuntimeError(f"{name} did not load from the disposable venv")
            imports[name] = {"state": "imported", "origin": str(origin)}

    STAGE = "stateless_chat_registry"
    from friday_chat.commands.registry import (
        RegistryCommandContext,
        build_default_registry,
    )

    registry = build_default_registry()
    handled, result = await registry.execute(
        "/help exit", RegistryCommandContext(registry=registry)
    )
    metadata = {k: asdict(v) for k, v in sorted(registry.commands.items())}
    chat = {
        "canonical_names": len(metadata),
        "aliases": sum(len(v["aliases"]) for v in metadata.values()),
        "metadata": metadata,
        "help_exit_handled": handled,
        "help_exit_has_output": bool(result and result.output),
    }

    entries: list[dict[str, object]] = []
    for distribution in ("friday-chat", "friday-framework-cli"):
        for entry in importlib.metadata.distribution(distribution).entry_points:
            if entry.group != "console_scripts":
                continue
            STAGE = f"entrypoint:{entry.name}"
            row: dict[str, object] = {
                "distribution": distribution,
                "name": entry.name,
                "target": entry.value,
            }
            try:
                app = entry.load()
            except Exception as exc:
                row.update(load="failed", error_type=type(exc).__name__, error=str(exc))
            else:
                row["load"] = "loaded"
                if entry.name == "friday-chat":
                    from typer.testing import CliRunner

                    help_result = CliRunner().invoke(app, ["--help"])
                    row["help_exit_code"] = help_result.exit_code
                    row["help_contains_usage"] = "Usage" in help_result.stdout
            entries.append(row)

    imported = all(
        row["state"] == "imported"
        for name, row in imports.items()
        if name != "friday_tools"
    )
    tools = imports["friday_tools"]
    expected = (
        imported
        and tools["state"] == "failed"
        and tools.get("error_type") == "ModuleNotFoundError"
        and tools.get("missing_module") == "friday_finance"
        and chat["canonical_names"] == 50
        and chat["aliases"] == 3
        and chat["help_exit_handled"]
        and chat["help_exit_has_output"]
        and any(
            e["name"] == "friday-chat"
            and e.get("load") == "loaded"
            and e.get("help_exit_code") == 0
            and e.get("help_contains_usage")
            for e in entries
        )
        and any(
            e["name"] == "friday"
            and e.get("load") == "failed"
            and e.get("error_type") == "AttributeError"
            for e in entries
        )
    )
    report = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "cwd": str(Path.cwd()),
        "prefix": str(prefix),
        "isolated": bool(sys.flags.isolated),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "module_imports": imports,
        "chat_registry": chat,
        "entrypoints": entries,
        "installed_distributions": sorted(
            f"{d.metadata['Name']}=={d.version}"
            for d in importlib.metadata.distributions()
        ),
        "network_attempts_blocked": len(NETWORK_ATTEMPTS),
        "network_events": NETWORK_ATTEMPTS,
        "matches_expected_baseline": bool(expected),
        "limits": "Import/help observations only; known tools and CLI defects remain. No runtime/store construction, provider/tool execution, full installed suites or terminal/audio UAT. Exit zero means baseline capture matched, not healthy clients.",
    }
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                "matches_expected_baseline": report["matches_expected_baseline"],
                "module_imports": imports,
                "entrypoints": entries,
                "network_attempts_blocked": len(NETWORK_ATTEMPTS),
            }
        )
    )
    if not expected:
        raise RuntimeError(
            "Observed default profile differs from the expected baseline"
        )


if __name__ == "__main__":
    asyncio.run(main())
