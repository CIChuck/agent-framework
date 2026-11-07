"""Compare captured observations exactly; ignore only recorded provenance."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

GROUPS = {"metadata", "help", "dispatch", "custom", "lifecycle"}


def observations(document: object) -> dict[str, object]:
    if not isinstance(document, dict) or set(document) != {
        "schema",
        "provenance",
        "observations",
    }:
        raise ValueError("Unexpected capture envelope")
    if type(document["schema"]) is not int or document["schema"] != 1:
        raise ValueError("Unsupported capture schema")
    result = document["observations"]
    if not isinstance(result, dict) or set(result) != GROUPS:
        raise ValueError("Missing or unexpected observation group")
    if not isinstance(document["provenance"], dict):
        raise ValueError("Missing provenance")
    return result


def compare(before: object, after: object) -> None:
    left, right = observations(before), observations(after)
    if before["provenance"].get("capture_sha256") != after["provenance"].get(
        "capture_sha256"
    ):
        raise ValueError("Capture program changed between lanes")

    def serialized(value: object) -> str:
        return json.dumps(value, sort_keys=True, allow_nan=False)

    if serialized(left) != serialized(right):
        changed = sorted(
            key for key in GROUPS if serialized(left[key]) != serialized(right[key])
        )
        raise ValueError(f"Behavior drift in: {', '.join(changed)}")


def selftest() -> None:
    baseline = {
        "schema": 1,
        "provenance": {"revision": "before", "capture_sha256": "frozen-script"},
        "observations": dict.fromkeys(sorted(GROUPS), {"sample": ["a", "b"]}),
    }
    compare(baseline, copy.deepcopy(baseline))
    provenance_only = copy.deepcopy(baseline)
    provenance_only["provenance"]["revision"] = "after"
    compare(baseline, provenance_only)
    mutations = []
    for key in sorted(GROUPS):
        mutation = copy.deepcopy(baseline)
        mutation["observations"][key] = {"sample": ["b", "a"]}
        mutations.append(mutation)
    missing = copy.deepcopy(baseline)
    del missing["observations"]["help"]
    mutations.append(missing)
    extra = copy.deepcopy(baseline)
    extra["observations"]["unexpected"] = []
    mutations.append(extra)
    changed_program = copy.deepcopy(baseline)
    changed_program["provenance"]["capture_sha256"] = "different-script"
    mutations.append(changed_program)
    missing_program = copy.deepcopy(baseline)
    del missing_program["provenance"]["capture_sha256"]
    mutations.append(missing_program)
    typed_before = copy.deepcopy(baseline)
    typed_after = copy.deepcopy(baseline)
    typed_before["observations"]["dispatch"] = {"handled": True}
    typed_after["observations"]["dispatch"] = {"handled": 1}
    try:
        compare(typed_before, typed_after)
    except ValueError:
        pass
    else:
        raise RuntimeError("Comparator accepted boolean-to-integer drift")
    for mutation in mutations:
        try:
            compare(baseline, mutation)
        except ValueError:
            continue
        raise RuntimeError("Comparator accepted an intentionally damaged capture")
    print(
        f"Comparator passed identity/provenance controls and {len(mutations) + 1} refusal controls"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path, nargs="?")
    parser.add_argument("after", type=Path, nargs="?")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--baseline-sha256")
    args = parser.parse_args()
    if args.selftest:
        selftest()
    elif args.before is None or args.after is None or args.baseline_sha256 is None:
        parser.error("Supply both captures and --baseline-sha256, or --selftest")
    else:
        if hashlib.sha256(args.before.read_bytes()).hexdigest() != args.baseline_sha256:
            raise SystemExit("Frozen baseline hash mismatch")
        compare(json.loads(args.before.read_text()), json.loads(args.after.read_text()))
        print("All five observation groups match exactly")


if __name__ == "__main__":
    main()
