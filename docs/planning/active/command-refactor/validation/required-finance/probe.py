"""Run the pinned registry fixture in a fresh default wheel installation.

Usage: python -I -B probe.py OUTPUT CHECKOUT_ROOT PINNED_REGISTRY_PROBE
No provider client, runtime/store or external tool is constructed or executed.
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib.metadata
import json
import runpy
import socket
import sys
from functools import partial
from pathlib import Path
from typing import NoReturn

output, checkout, fixture = [Path(p).resolve() for p in sys.argv[1:]]
expected_fixture_hash = (
    "22db1b2826ef44caaef26640969568e8ea9b1d1f8593f42f7aa275d2a108af3e"
)
if hashlib.sha256(fixture.read_bytes()).hexdigest() != expected_fixture_hash:
    raise RuntimeError("Historical registry fixture changed")

namespace = runpy.run_path(str(fixture))
fixture_globals = namespace["main"].__globals__
network_events: list[str] = []


def deny_network(operation: str, *args: object, **kwargs: object) -> NoReturn:
    fixture_globals["NETWORK_ATTEMPTS"] += 1
    network_events.append(operation)
    raise RuntimeError("Network disabled for required-finance default probe")


def audit_network(event: str, args: tuple[object, ...]) -> None:
    if event in {
        "socket.connect",
        "socket.bind",
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

# The fixture uses argv[1:3] for its output and checkout guard.
sys.argv = [str(fixture), str(output), str(checkout)]
asyncio.run(namespace["main"]())
report = json.loads(output.read_text())

tools_module = importlib.import_module("friday_tools")
friday_finance = importlib.import_module("friday_finance")
massive = importlib.import_module("massive")

prefix = Path(sys.prefix).resolve()
for module in (friday_finance, massive):
    if not Path(module.__file__).resolve().is_relative_to(prefix):
        raise RuntimeError("Finance/SDK import escaped disposable environment")
if tools_module.GetMarketDataTool.__module__ != "friday_tools.finance.massive":
    raise RuntimeError("Public finance tool export changed")
tools = importlib.metadata.distribution("friday-framework-tools")
if "friday-framework-finance==0.1.0a4" not in tools.requires:
    raise RuntimeError("Finance is not an unconditional installed requirement")
if "finance" not in tools.metadata.get_all("Provides-Extra", []):
    raise RuntimeError("Compatibility finance extra disappeared")
cli = importlib.metadata.distribution("friday-framework-cli")
if any(e.group == "console_scripts" for e in cli.entry_points):
    raise RuntimeError("Framework CLI unexpectedly advertises an executable")
if (prefix / "bin" / "friday").exists():
    raise RuntimeError("Retired launcher was installed")
if report["chat_command_count"] != 50 or report["chat_alias_count"] != 3:
    raise RuntimeError("Chat inventory drift")
historical = (
    checkout
    / "docs/planning/active/command-refactor/validation/step3/installed-probe.json"
)
if report["chat_metadata"] != json.loads(historical.read_text())["chat_metadata"]:
    raise RuntimeError("Chat metadata differs from frozen baseline")
if not any(
    e["name"] == "friday-chat" and e.get("help_exit_code") == 0
    for e in report["entrypoints"]
):
    raise RuntimeError("Chat help failed")

report.update(
    finance_import="passed",
    finance_sdk_import="passed",
    public_finance_tool_import="passed without constructing provider client",
    tools_requires_finance=True,
    compatibility_finance_extra=True,
    retired_friday_launcher_present=False,
    network_attempts_blocked=len(network_events),
    network_events=network_events,
    registry_fixture_sha256=expected_fixture_hash,
    probe_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    limits="Default dependency/import/registry/help proof only; no provider credentials, requests, runtime/store, full installed suites, terminal/audio UAT or foundation construction.",
)
output.write_text(json.dumps(report, indent=2) + "\n")
print(
    json.dumps(
        {
            "finance_import": report["finance_import"],
            "tools_requires_finance": True,
            "installed_count": len(report["installed_distributions"]),
            "retired_friday_launcher_present": False,
            "network_attempts_blocked": report["network_attempts_blocked"],
        }
    )
)
