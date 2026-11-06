"""Read-only registry/source inventory; run with uv run python <this-file>."""

from __future__ import annotations

import ast
import hashlib
import inspect
import json
import re
import subprocess
from dataclasses import asdict
from pathlib import Path

from friday_chat.commands.registry import build_default_registry

ROOT = Path(__file__).resolve().parents[6]
OUT = Path(__file__).resolve().parent
RETIRED = set(
    [
        "clear-tools",
        "inject-tools",
        "recommend-tools",
        "run-tool",
        "tool-budget",
        "inject-payload",
        "prime",
        "set",
        "vars",
    ]
)


def main() -> None:
    registry = build_default_registry()
    snapshot = json.loads((OUT.parent / "command-matrix.json").read_text())
    assert set(registry.commands) == {c["name"] for c in snapshot["commands"]}
    source_files = sorted(
        set(
            list((ROOT / "packages/friday-chat/src/friday_chat/commands").glob("*.py"))
            + list((ROOT / "packages/friday-cli/src/friday_cli").glob("*.py"))
            + list((ROOT / "packages/friday-chat/tests_chat").rglob("*.py"))
            + list((ROOT / "packages/friday-cli/tests_cli").rglob("*.py"))
        )
    )
    test_nodes: dict[str, list[dict[str, object]]] = {n: [] for n in registry.commands}
    for path in source_files:
        if "tests_" not in str(path):
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if not isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef)
            ) or not node.name.startswith("test_"):
                continue
            names = set()
            for value in ast.walk(node):
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    names.update(
                        re.findall(r"(?<![\w/])/([a-z][a-z-]*)(?![\w-])", value.value)
                    )
            for name in names & test_nodes.keys():
                test_nodes[name].append(
                    {
                        "file": str(path.relative_to(ROOT)),
                        "line": node.lineno,
                        "test": node.name,
                        "parameters": [a.arg for a in node.args.args],
                    }
                )
    rows = []
    for old in snapshot["commands"]:
        name = old["name"]
        meta = asdict(registry.commands[name])
        handler = registry._handlers[name]  # Read-only inspection of current ownership.
        path = Path(inspect.getsourcefile(handler)).resolve()
        source, line = inspect.getsourcelines(handler)
        tree = ast.parse("".join(source))
        accesses = sorted(
            {
                ast.unparse(n)
                for n in ast.walk(tree)
                if isinstance(n, ast.Attribute)
                and ast.unparse(n).startswith(("context.", "_context."))
            }
        )
        calls = sorted(
            {ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}
        )
        writes = sorted(
            {
                ast.unparse(t)
                for n in ast.walk(tree)
                if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign))
                for t in (n.targets if isinstance(n, ast.Assign) else [n.target])
                if "context." in ast.unparse(t)
            }
        )
        drift = {
            k: {"snapshot": old.get(k), "live": v}
            for k, v in meta.items()
            if json.loads(json.dumps(v)) != old.get(k)
        }
        rows.append(
            {
                "case_id": old["case_id"],
                "name": name,
                "metadata": meta,
                "target": "remove"
                if name in RETIRED
                else "extract; preserve semantics",
                "handler": f"{handler.__module__}.{handler.__name__}",
                "source": str(path.relative_to(ROOT)),
                "line": line,
                "direct_context_accesses": accesses,
                "direct_assignments": writes,
                "direct_calls": calls,
                "candidate_test_references": test_nodes[name],
                "metadata_drift": drift,
            }
        )
    manifest = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in source_files
    }
    report = {
        "head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "source_sha256": manifest,
        "commands": rows,
        "limits": "AST references are navigation aids, not proof of effects or case coverage. No handlers executed.",
    }
    (OUT / "inventory.json").write_text(json.dumps(report, indent=2) + "\n")
    lines = [
        "# PAR source coverage ledger",
        "",
        "Date: 2026-11-04",
        f"Source HEAD: `{report['head']}`",
        "",
        "Status: Initial P0 source map; behavioral case-level signoff remains open.",
        "",
        "Authority: [resolved decisions](../scope-decisions.md) and [next-phase checkpoint](../next-phase.md).",
        "",
        "The 50-name snapshot is unchanged. Target: 41 retained names, nine removals,",
        "three retained aliases. **Extract** means move semantics to the shared owner",
        "while preserving Chat behavior; **remove** means no legacy shim or former effect.",
        "",
        "Reproduce the source map with:",
        "",
        "```sh",
        "uv run python docs/planning/active/command-refactor/validation/p0/capture_inventory.py",
        "```",
        "",
        "[Machine-readable inventory](p0/inventory.json) includes complete live metadata,",
        "direct context accesses/assignments, calls, candidate test nodes and fixture",
        "parameter names, metadata drift and source/test SHA-256 hashes. AST matches",
        "are navigation aids: a command literal in a test is not proof that a behavior",
        "was exercised. Direct accesses omit transitive helper effects.",
        "",
        "[Baseline receipt](p0-baseline.md) records actual suite and probe results.",
        "",
        "| Case | Name / target | Handler | Direct state/service access (abridged) | Candidate test nodes |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for row in rows:
        state = (
            ", ".join(row["direct_context_accesses"][:4])
            or "See helper calls in inventory"
        )
        label = "remove" if row["name"] in RETIRED else "extract"
        lines.append(
            f"| {row['case_id']} | `/{row['name']}` — {label} | `{row['handler']}` ({row['source']}:{row['line']}) | {state} | {len(row['candidate_test_references'])} |"
        )
    lines += ["", "## Alias obligations", ""]
    for row in rows:
        for alias in row["metadata"]["aliases"]:
            lines.append(
                f"- `/{alias}` → `/{row['name']}` ({row['case_id']}): retain dispatch, help and effect equivalence; see baseline probe."
            )
    lines += [
        "",
        "## Open evidence obligations",
        "",
        "Each of the 50 rows remains **case-level review pending**: inspect the candidate",
        "test assertions, assign exact positive/invalid/unavailable/cancellation/error",
        "nodes or document why a class is inapplicable, and link actual receipts.",
        "Use existing tmp_path/fake-runtime fixtures where applicable; effectful probes",
        "must use disposable stores. Do not infer coverage from suite totals or literals.",
        "",
        "The nine removal rows retain before-change behavior evidence only; after-change",
        "unknown-name, no-effect and discovery-removal checks belong to an approved",
        "retirement directive. No handler migration or retirement occurred in P0.",
        "",
        "Before construction: finish the transitive service/effect and failure-order map,",
        "freeze exact fixture/result expectations, assign migration families and cross-family",
        "scenarios, and obtain contract/directive approval. No P0/P1 completion claimed.",
        "",
    ]
    (OUT.parent / "par-coverage-ledger.md").write_text("\n".join(lines))
    print(
        f"Captured {len(rows)} commands, {sum(len(r['metadata']['aliases']) for r in rows)} aliases, "
        f"{len(manifest)} source/test hashes; metadata drift in {sum(bool(r['metadata_drift']) for r in rows)} commands."
    )


if __name__ == "__main__":
    main()
