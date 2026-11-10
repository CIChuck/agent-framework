"""Reproduce the bounded MEMQ directive correction controls without product edits."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import re
import runpy
from pathlib import Path
from types import SimpleNamespace

MODELS = (
    "MemoryWarningData",
    "MemoryMetricData",
    "MemorySectionData",
    "MemoryStatisticsData",
    "MemoryRecordData",
    "MemoryRecordsData",
    "MemoryQueryFailedData",
    "MemoryUnavailableData",
    "GraphEntityData",
    "GraphRelationshipData",
    "GraphData",
    "IngestedDocumentData",
    "IngestedDocumentsData",
)
FACTORY = ("MEMORY_QUERY_SPECS", "MemoryQueryPort", "build_memory_query_handlers")
ADDITIONS = MODELS + FACTORY
OUTCOMES = (
    "MemoryUnavailableData",
    "MemoryStatisticsData",
    "MemoryRecordsData",
    "MemoryQueryFailedData",
    "GraphData",
    "IngestedDocumentsData",
)
PACKET = Path("docs/planning/active/command-refactor")


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def shape(node: ast.AST) -> str:
    return ast.dump(node, include_attributes=False)


def function(path: Path, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    return next(
        n
        for n in ast.parse(path.read_text()).body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name
    )


def assignment(node: ast.AST, name: str) -> ast.Assign:
    return next(
        n
        for n in ast.walk(node)
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)
    )


def api_literal(node: ast.AST) -> ast.List:
    return next(
        n.comparators[0]
        for n in ast.walk(node)
        if isinstance(n, ast.Compare)
        and isinstance(n.left, ast.Attribute)
        and isinstance(n.left.value, ast.Name)
        and n.left.value.id == "api"
        and n.left.attr == "__all__"
        and isinstance(n.comparators[0], ast.List)
    )


def append_names(node: ast.List | ast.Tuple, names: tuple[str, ...]) -> None:
    node.elts.extend(ast.Constant(n) for n in names)


def remove_names(node: ast.List | ast.Tuple, names: tuple[str, ...]) -> None:
    require(
        tuple(ast.literal_eval(n) for n in node.elts[-len(names) :]) == names,
        "Wrong appended names/order",
    )
    del node.elts[-len(names) :]


def binding_count(node: ast.AST) -> ast.Compare:
    return next(
        n
        for n in ast.walk(node)
        if isinstance(n, ast.Compare)
        and isinstance(n.left, ast.Call)
        and isinstance(n.left.func, ast.Name)
        and n.left.func.id == "len"
        and len(n.left.args) == 1
        and isinstance(n.left.args[0], ast.Name)
        and n.left.args[0].id == "expected_bindings"
    )


def diagnostic_transform(original: ast.FunctionDef) -> ast.FunctionDef:
    node = copy.deepcopy(original)
    node.body.insert(
        0,
        ast.Import(
            names=[
                ast.alias(
                    name="friday_commands.memory_queries",
                    asname="memory_queries_module",
                )
            ]
        ),
    )
    append_names(api_literal(node), ADDITIONS)
    owners = assignment(node, "owners").value
    append_names(owners.elts[0].elts[1], MODELS)
    owners.elts.append(
        ast.Tuple(
            elts=[
                ast.Name(id="memory_queries_module", ctx=ast.Load()),
                ast.Tuple(elts=[ast.Constant(n) for n in FACTORY], ctx=ast.Load()),
            ],
            ctx=ast.Load(),
        )
    )
    require(ast.literal_eval(binding_count(node).comparators[0]) == 38, "Old count")
    binding_count(node).comparators[0] = ast.Constant(54)
    return ast.fix_missing_locations(node)


def reverse_diagnostic(node: ast.FunctionDef) -> ast.FunctionDef:
    node = copy.deepcopy(node)
    expected_import = ast.Import(
        names=[
            ast.alias(
                name="friday_commands.memory_queries", asname="memory_queries_module"
            )
        ]
    )
    require(shape(node.body[0]) == shape(expected_import), "Unexpected local import")
    node.body.pop(0)
    remove_names(api_literal(node), ADDITIONS)
    owners = assignment(node, "owners").value
    row = owners.elts[-1]
    require(
        isinstance(row, ast.Tuple)
        and isinstance(row.elts[0], ast.Name)
        and row.elts[0].id == "memory_queries_module"
        and ast.literal_eval(row.elts[1]) == FACTORY,
        "Unexpected new owner row",
    )
    owners.elts.pop()
    remove_names(owners.elts[0].elts[1], MODELS)
    require(ast.literal_eval(binding_count(node).comparators[0]) == 54, "New count")
    binding_count(node).comparators[0] = ast.Constant(38)
    return node


def rejected(action, message: str) -> None:
    try:
        action()
    except ValueError:
        return
    raise ValueError("Control was not rejected: " + message)


def union_transform(original: ast.FunctionDef) -> ast.FunctionDef:
    node = copy.deepcopy(original)
    values = assignment(node, "expected").value.right
    require(isinstance(values, ast.Set) and len(values.elts) == 5, "Old expected set")
    values.elts.extend(
        ast.Attribute(
            value=ast.Name(id="contracts", ctx=ast.Load()), attr=name, ctx=ast.Load()
        )
        for name in OUTCOMES
    )
    return ast.fix_missing_locations(node)


def reverse_union(changed: ast.FunctionDef) -> ast.FunctionDef:
    node = copy.deepcopy(changed)
    values = assignment(node, "expected").value.right
    require(isinstance(values, ast.Set) and len(values.elts) == 11, "New expected set")
    for value, name in zip(values.elts[-6:], OUTCOMES, strict=True):
        require(
            isinstance(value, ast.Attribute)
            and isinstance(value.value, ast.Name)
            and value.value.id == "contracts"
            and value.attr == name,
            "Unexpected union member/order/owner",
        )
    del values.elts[-6:]
    return node


def union_controls(root: Path, out: Path) -> dict:
    path = root / "packages/friday-commands/tests_commands/test_diagnostics.py"
    name = "_check_closed_union_retains_old_variants_and_refuses_nested_values"
    original = function(path, name)
    changed = union_transform(original)
    require(shape(reverse_union(changed)) == shape(original), "Union AST reversal")
    bad = copy.deepcopy(changed)
    bad.body.append(ast.Assert(test=ast.Constant(False)))
    rejected(
        lambda: require(
            shape(reverse_union(bad)) == shape(original), "Union behavior drift"
        ),
        "unrelated union-helper assertion",
    )
    namespace = runpy.run_path(str(path))
    old_types = tuple(namespace["get_args"](namespace["FoundationData"].__value__))
    require(len(old_types) == 12, "Original union size")
    markers = {name: type(name, (), {}) for name in OUTCOMES}
    contracts = SimpleNamespace(**(vars(namespace["contracts"]) | markers))

    def invoke(node: ast.FunctionDef, members: tuple) -> None:
        union = members[0]
        for member in members[1:]:
            union = union | member
        private = namespace | {
            "contracts": contracts,
            "FoundationData": SimpleNamespace(__value__=union),
        }
        module = ast.Module(body=[copy.deepcopy(node)], type_ignores=[])
        exec(compile(ast.fix_missing_locations(module), str(path), "exec"), private)
        private[name]()

    invoke(original, old_types)
    expanded = old_types + tuple(markers.values())
    invoke(changed, expanded)
    failures = []
    nested = namespace["contracts"].DiagnosticField
    for label, node, members in [
        ("unchanged-helper-with-expanded-union", original, expanded),
        ("missing-member", changed, expanded[:-1]),
        ("extra-member", changed, expanded + (type("Extra", (), {}),)),
        ("nested-member", changed, expanded[:-1] + (nested,)),
    ]:
        try:
            invoke(node, members)
        except AssertionError as error:
            frames = []
            trace = error.__traceback__
            while trace is not None:
                code = trace.tb_frame.f_code
                if code.co_filename == str(path) and code.co_name == name:
                    frames.append(trace.tb_lineno)
                trace = trace.tb_next
            require(frames == [203], "Need canonical helper call assertion witness")
            failures.append(
                {"control": label, "file": str(path), "call_assertion_line": 203}
            )
        else:
            raise ValueError("Union control was not rejected: " + label)
    (out / "union-helper-transform.py").write_text(ast.unparse(changed) + "\n")
    return {
        "original_members": 12,
        "expanded_members": 18,
        "unchanged_and_extended_controls": "passed",
        "AST_reversal": "passed",
        "unrelated_behavior_rejected": True,
        "call_assertion_witnesses": failures,
        "limit": "Synthetic alias membership only, not implemented MQ model/whitelist proof",
    }


def current_gates(text: str, expected: str) -> None:
    gates = re.findall(r"^\*\*Next gate:\*\* (.+)$", text, re.M)
    require(
        bool(gates) and all(gate == expected for gate in gates),
        "Conflicting README gate",
    )
    require("MEMQ-001 is in planning" not in text, "Stale current MEMQ phase")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("scratch", type=Path)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.scratch.resolve()
    require(not out.is_relative_to(root), "Scratch must be external")
    out.mkdir(parents=True, exist_ok=True)
    require(not any(out.iterdir()), "Use empty scratch")
    packet = root / PACKET
    union_result = union_controls(root, out)
    authority = json.loads((packet / "authority.json").read_text())
    expected_gate = authority["memory_queries_preparation"]["next_gate"]
    index_text = (packet / "README.md").read_text()
    current_gates(index_text, expected_gate)
    rejected(
        lambda: current_gates(
            index_text + "\n**Next gate:** stale implementation gate\n", expected_gate
        ),
        "additional stale README gate",
    )
    original = function(
        root / "packages/friday-commands/tests_commands/test_diagnostics.py",
        "test_diagnostic_specs_exports_and_factory",
    )
    changed = diagnostic_transform(original)
    require(shape(reverse_diagnostic(changed)) == shape(original), "MQ-D4 AST reversal")
    bad = copy.deepcopy(changed)
    bad.body.append(ast.Assert(test=ast.Constant(False)))
    rejected(
        lambda: require(
            shape(reverse_diagnostic(bad)) == shape(original),
            "Unrelated assertion drift",
        ),
        "MQ-D4 unrelated assertion",
    )
    owners = assignment(changed, "owners")
    markers = {}
    namespace = {}
    for row in owners.value.elts:
        module_name = row.elts[0].id
        values = {
            n: markers.setdefault(n, object()) for n in ast.literal_eval(row.elts[1])
        }
        namespace[module_name] = SimpleNamespace(**values)
    body = ast.Module(
        body=[owners, assignment(changed, "expected_bindings")], type_ignores=[]
    )
    exec(
        compile(ast.fix_missing_locations(body), "<private-owner-control>", "exec"),
        namespace,
    )
    exports_node = ast.parse(
        (root / "packages/friday-commands/src/friday_commands/__init__.py").read_text()
    )
    expected = (
        tuple(ast.literal_eval(assignment(exports_node, "__all__").value)) + ADDITIONS
    )
    bindings = namespace["expected_bindings"]
    require(
        len(bindings) == len(expected) == 54 and set(bindings) == set(expected),
        "54 bindings",
    )
    require(all(bindings[n] is markers[n] for n in expected), "Binding identity")
    (out / "diagnostic-test-transform.py").write_text(ast.unparse(changed) + "\n")
    session = function(
        root / "packages/friday-commands/tests_commands/test_session_views.py",
        "test_session_specs_and_factory_are_immutable",
    )
    extended = copy.deepcopy(session)
    append_names(api_literal(extended), ADDITIONS)
    require(
        tuple(ast.literal_eval(n) for n in api_literal(extended).elts) == expected,
        "SESSION test API order",
    )
    remove_names(api_literal(extended), ADDITIONS)
    require(shape(extended) == shape(session), "SESSION test AST reversal")
    probe_checks = []
    for source, name, renamed in [
        (
            "diagnostics",
            "retained_session_neutral_behavior",
            "retained_memq_session_neutral_behavior",
        ),
        ("session", "chat_behavior", "retained_memq_session_chat_behavior"),
        ("diagnostics", "neutral_diagnostics", "retained_memq_neutral_diagnostics"),
        ("diagnostics", "chat_diagnostics", "retained_memq_chat_diagnostics"),
    ]:
        original_fn = function(packet / f"validation/{source}/installed_probe.py", name)
        copied = copy.deepcopy(original_fn)
        copied.name = renamed
        if name == "retained_session_neutral_behavior":
            values = assignment(copied, "expected_exports").value
            require(len(values.elts) == 38, "Retained baseline must have 38 exports")
            append_names(values, ADDITIONS)
            require(
                tuple(ast.literal_eval(n) for n in values.elts) == expected,
                "D5 exact API54",
            )
            remove_names(values, ADDITIONS)
        copied.name = name
        require(shape(copied) == shape(original_fn), "D5 behavioral AST drift")
        copied.body.append(ast.Assert(test=ast.Constant(False)))
        rejected(
            lambda copied=copied, original_fn=original_fn: require(
                shape(copied) == shape(original_fn), "Extra behavior"
            ),
            name,
        )
        probe_checks.append(name)
    helper = runpy.run_path(str(packet / "validation/memory-queries/format_debt.py"))
    baseline_path = packet / "validation/memory-queries/format-baseline.json"
    baseline = json.loads(baseline_path.read_text())
    current = helper["inventory"](root)
    require(current == baseline, "D0 exact format baseline reproduction")
    sample = helper["FILES"][0]
    path = root / sample
    text = path.read_text()
    fragments, formatted, excess = (
        helper[n] for n in ["fragments", "formatted", "excess"]
    )
    allowed = baseline["files"][sample]["fragments"]
    for label, value in [
        ("unchanged", text),
        ("shifted-lines", "# shifted control\n" + text),
        (
            "formatted-new-code",
            text + "\n\ndef new_formatted_control():\n    return 1\n",
        ),
    ]:
        require(not excess(fragments(value, formatted(value, path)), allowed), label)
    new = text + "\n\ndef new_unformatted_control( ): return [ 1,2 ]\n"
    require(
        bool(excess(fragments(new, formatted(new, path)), allowed)),
        "New defect not rejected",
    )
    require(
        bool(excess(allowed + [allowed[0]], allowed)), "Duplicate allowance not bounded"
    )
    result = {
        "scope": "document correction controls; no product implementation",
        "status": "passed",
        "diagnostic_bindings": len(bindings),
        "union_controls": union_result,
        "all_current_README_gates": "agree; injected stale gate rejected",
        "diagnostic_and_session_AST_reversal": "passed",
        "unrelated_assertion_rejected": True,
        "retained_probe_functions": probe_checks,
        "D5_exact_ordered_exports": 54,
        "all_four_extra_behavior_controls_rejected": True,
        "format_inventory_sha256": hashlib.sha256(
            baseline_path.read_bytes()
        ).hexdigest(),
        "format_controls": [
            "exact baseline",
            "unchanged",
            "shifted lines",
            "formatted new code",
            "new defect rejected",
            "duplicate allowance rejected",
        ],
        "baseline_format_debt": "failed/unwaived",
    }
    (out / "controls.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
