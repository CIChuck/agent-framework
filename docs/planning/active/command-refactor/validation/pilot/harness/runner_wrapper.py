"""Configure the pinned runner and prevent receipt/capture collisions."""

from __future__ import annotations

import os
import re
import runpy
import sys
from pathlib import Path


def main() -> None:
    scratch = Path(__file__).resolve().parent
    if (
        len(sys.argv) < 3
        or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", sys.argv[1]) is None
    ):
        raise SystemExit("Supply a safe receipt name and command")
    requested = sys.argv[1]
    stem = requested
    suffix = 1
    while any(
        (scratch / (stem + extension)).exists() for extension in (".json", ".log")
    ):
        suffix += 1
        stem = f"{requested}-{suffix}"
    reserved = {
        scratch / (name + extension)
        for name in (requested, stem)
        for extension in (".json", ".log")
    }
    for argument in sys.argv[2:]:
        if not argument.startswith("-") and Path(argument).resolve() in reserved:
            raise SystemExit("Command argument collides with a runner receipt path")
    sys.argv[1] = stem
    # A unique basetemp prevents pytest from cleaning unrelated numbered temp
    # directories and keeps every fixture lane inside this diagnostic scratch.
    if "-m" in sys.argv[2:] and "pytest" in sys.argv[2:]:
        if any(argument.startswith("--basetemp") for argument in sys.argv[2:]):
            raise SystemExit("The diagnostic runner owns pytest --basetemp")
        (scratch / "pytest-tmp").mkdir(exist_ok=True)
        sys.argv.extend(["--basetemp", str(scratch / "pytest-tmp" / stem)])
    os.environ["UV_FIND_LINKS"] = str(scratch / "wheelhouse")
    os.environ["UV_NO_INDEX"] = "1"
    os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
    runpy.run_path(str(scratch / "run.py"), run_name="__main__")


if __name__ == "__main__":
    main()
