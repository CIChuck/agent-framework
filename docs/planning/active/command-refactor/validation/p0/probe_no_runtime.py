"""Capture every default invocation with fresh, disposable in-memory state."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from friday_chat.commands.registry import RegistryCommandContext, build_default_registry

OUT = Path(__file__).resolve().parent


def state(context):
    return {
        "history": context.history,
        "variables": context.variables,
        "exit_requested": context.exit_requested,
        "injected_payload": context.injected_payload,
        "tool_results": context.tool_results,
        "security_stats": context.security_stats,
    }


async def main():
    registry = build_default_registry()
    source = json.loads((OUT / "inventory.json").read_text())
    rows = []
    for command in source["commands"]:
        context = RegistryCommandContext(registry=registry)
        before = json.loads(json.dumps(state(context)))
        text = "/" + command["name"]
        try:
            handled, result = await registry.execute(text, context)
            observation = {
                "handled": handled,
                "output": result.output if result else None,
                "ui_effects": [e.value for e in result.ui_effects] if result else [],
                "result_exit_requested": result.exit_requested if result else None,
            }
        except Exception as exc:
            observation = {"exception": type(exc).__name__, "message": str(exc)}
        rows.append(
            {
                "case_id": command["case_id"],
                "invocation": text,
                "fixture": "fresh RegistryCommandContext(runtime=None); no provider, tool, file path or store configured",
                "before": before,
                "observation": observation,
                "after": state(context),
            }
        )
    (OUT / "no-runtime.json").write_text(json.dumps(rows, indent=2) + "\n")
    lines = [
        "# Default-invocation behavior audit",
        "",
        "Date: 2026-11-04",
        "",
        "Fixture: fresh in-memory `RegistryCommandContext(runtime=None)` per case.",
        "No provider, external tool or persistent store is configured. This captures",
        "the actual default/no-runtime branch of all 50 commands; it does not prove",
        "successful initialized-runtime behavior or classify every failure branch.",
        "",
        "Reproduce with `uv run python docs/planning/active/command-refactor/validation/p0/probe_no_runtime.py`.",
        "",
        "[Full before/after state and outputs](p0/no-runtime.json). All retained and",
        "retired names still exist in this baseline; retirement is a future change.",
        "",
        "| Case | Invocation | Observed first line | State change |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        obs = row["observation"]
        output = obs.get("output") or (
            "exception: " + obs["exception"] if "exception" in obs else "(no text)"
        )
        changed = [
            key for key in row["before"] if row["before"][key] != row["after"][key]
        ]
        effects = obs.get("ui_effects", [])
        change = ", ".join(changed + effects) or "none in captured fields"
        lines.append(
            f"| {row['case_id']} | `{row['invocation']}` | {output.splitlines()[0].replace('|', '&#124;')} | {change} |"
        )
    lines += [
        "",
        "## Coverage limits",
        "",
        "Positive service/state effects, invalid grammar, cancellation, partial failure",
        "ordering and frontend rendering remain separate obligations. No-runtime",
        "branches that ignore extra arguments must not be silently tightened during",
        "extraction. For `/cls`, dispatch requests a UI effect; this does not invoke",
        "a terminal. For `/exit`, the result/context flag changes; no process exits.",
        "",
        "Compare against the [source ledger](par-coverage-ledger.md) and",
        "[baseline failure controls](p0-failure-disposition.md) before defining directives.",
        "",
    ]
    (OUT.parent / "default-behavior-audit.md").write_text("\n".join(lines))
    exceptions = [r["case_id"] for r in rows if "exception" in r["observation"]]
    print(
        f"Captured {len(rows)} default invocations; unhandled exceptions: {exceptions}"
    )


if __name__ == "__main__":
    asyncio.run(main())
