"""Inventory existing Ruff formatting debt and reject new debt without editing source."""

from __future__ import annotations

import argparse
import ast
import difflib
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

FILES = (
    "packages/friday-chat/src/friday_chat/commands/memory.py",
    "packages/friday-chat/src/friday_chat/commands/registry.py",
    "packages/friday-chat/src/friday_chat/memory_views.py",
    "packages/friday-chat/src/friday_chat/runtime.py",
    "packages/friday-chat/src/friday_chat/adapters.py",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def formatted(text: str, path: Path) -> str:
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            "-m",
            "ruff",
            "format",
            "--no-cache",
            "--stdin-filename",
            str(path),
            "-",
        ],
        input=text,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def fragments(text: str, rendered: str) -> list[dict[str, str | int]]:
    """Bind changed text to its lexical owner; line numbers are diagnostic only."""
    owners: list[tuple[int, int, str]] = []

    def visit(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + child.name
                owners.append((child.lineno, child.end_lineno or child.lineno, name))
                visit(child, name + ".")
            else:
                visit(child, prefix)

    visit(ast.parse(text), "")
    before, after = text.splitlines(keepends=True), rendered.splitlines(keepends=True)
    result: list[dict[str, str | int]] = []
    for tag, a, b, c, d in difflib.SequenceMatcher(
        a=before, b=after, autojunk=False
    ).get_opcodes():
        if tag == "equal":
            continue
        enclosing = [
            (end - start, name)
            for start, end, name in owners
            if start <= a + 1 <= end and max(a + 1, b) <= end
        ]
        owner = min(enclosing)[1] if enclosing else "<module>"
        old, new = "".join(before[a:b]), "".join(after[c:d])
        identity = digest(json.dumps([owner, old, new]).encode())
        result.append(
            {
                "owner": owner,
                "line": a + 1,
                "before": old,
                "after": new,
                "sha256": identity,
            }
        )
    return result


def inventory(root: Path) -> dict:
    files = {}
    for name in FILES:
        path = root / name
        raw = path.read_bytes()
        text = raw.decode()
        rendered = formatted(text, path)
        diff = "".join(
            difflib.unified_diff(
                text.splitlines(keepends=True),
                rendered.splitlines(keepends=True),
                fromfile=name,
                tofile=name,
            )
        )
        files[name] = {
            "source_sha256": digest(raw),
            "formatted_sha256": digest(rendered.encode()),
            "diff": diff,
            "fragments": fragments(text, rendered),
        }
    version = subprocess.check_output(
        [sys.executable, "-I", "-B", "-m", "ruff", "--version"], text=True
    ).strip()
    return {
        "version": 1,
        "formatter_version": version,
        "config_sha256": digest((root / "pyproject.toml").read_bytes()),
        "status": "baseline formatting debt failed/unwaived",
        "files": files,
    }


def excess(current: list[dict], baseline: list[dict]) -> dict[str, int]:
    counts = Counter(str(item["sha256"]) for item in current)
    allowed = Counter(str(item["sha256"]) for item in baseline)
    return dict(counts - allowed)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("record", "check"))
    parser.add_argument("root", type=Path)
    parser.add_argument("baseline", type=Path)
    args = parser.parse_args()
    current = inventory(args.root.resolve())
    if args.mode == "record":
        with args.baseline.open("x") as output:
            output.write(json.dumps(current, indent=2) + "\n")
        print("Recorded failed/unwaived baseline formatting inventory")
        return
    baseline = json.loads(args.baseline.read_text())
    if baseline["version"] != 1 or tuple(baseline["files"]) != FILES:
        raise ValueError("Unexpected baseline inventory")
    if any(
        baseline[key] != current[key] for key in ("formatter_version", "config_sha256")
    ):
        raise ValueError("Formatter or configuration differs from baseline")
    new = {
        path: extra
        for path in FILES
        if (
            extra := excess(
                current["files"][path]["fragments"],
                baseline["files"][path]["fragments"],
            )
        )
    }
    print(json.dumps({"new_format_debt": new, "baseline_debt": "failed/unwaived"}))
    if new:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
