"""Run narrow baseline controls without changing tracked examples or tests."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
OUT = Path(__file__).resolve().parent
NODES = [
    "packages/friday-chat/tests_chat/compat/test_config_compatibility.py::test_repository_and_packaged_examples_share_model_bindings",
    "packages/friday-chat/tests_chat/test_command_disposable_uat.py::test_real_app_cli_pty_command_uat_is_contained_and_provider_free",
    "packages/friday-chat/tests_chat/test_display.py::test_production_clear_emits_control_sequence_through_pty",
]


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="friday-p0-controls-") as scratch:
        temp = Path(scratch)
        for name in ("config.example.yaml", "models-config.example.yaml"):
            (temp / name).write_bytes(
                subprocess.check_output(
                    ["git", "show", f"HEAD:packages/friday-chat/{name}"], cwd=ROOT
                )
            )
        plugin = temp / "p0_controls.py"
        plugin.write_text("""from pathlib import Path
import os

def pytest_collection_modifyitems(items):
    root = Path(os.environ['FRIDAY_P0_CONTROL_INPUTS'])
    for item in items:
        if item.path.name not in ('test_config_compatibility.py', 'test_command_disposable_uat.py'):
            continue
        module = item.module
        if hasattr(module, 'EXAMPLE_CONFIG'):
            module.EXAMPLE_CONFIG = root / 'config.example.yaml'
        if hasattr(module, 'EXAMPLE_MODEL_LIBRARY'):
            module.EXAMPLE_MODEL_LIBRARY = root / 'models-config.example.yaml'
""")
        results = []
        lanes = (
            ("head-examples-original-term", True, None),
            ("head-examples-xterm", True, "xterm-256color"),
        )
        if "--full" in sys.argv:
            lanes = (("head-examples-xterm-full-chat", True, "xterm-256color"),)
        for label, _head_inputs, term in lanes:
            env = os.environ.copy()
            env["FRIDAY_P0_CONTROL_INPUTS"] = str(temp)
            env["PYTHONPATH"] = str(temp) + os.pathsep + env.get("PYTHONPATH", "")
            if term is not None:
                env["TERM"] = term
            selected = (
                [
                    "packages/friday-chat/tests_chat",
                    "--ignore=packages/friday-chat/tests_chat/test_live_lmstudio.py",
                ]
                if "--full" in sys.argv
                else NODES
            )
            args = [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "-ra",
                "-p",
                "p0_controls",
                *selected,
            ]
            run = subprocess.run(
                args, cwd=ROOT, env=env, capture_output=True, text=True
            )
            (OUT / (label + ".log")).write_text(
                "\n".join(line.rstrip() for line in run.stdout.splitlines()) + "\n"
            )
            results.append(
                {
                    "control": label,
                    "example_source": "HEAD Git blobs; module constants redirected by temporary collection plugin",
                    "TERM": env.get("TERM"),
                    "returncode": run.returncode,
                    "command": [
                        "python",
                        "-m",
                        "pytest",
                        "-q",
                        "-ra",
                        "-p",
                        "p0_controls",
                        *selected,
                    ],
                    "stderr": run.stderr,
                }
            )
        (
            OUT
            / ("full-control.json" if "--full" in sys.argv else "failure-controls.json")
        ).write_text(json.dumps(results, indent=2) + "\n")
        print(
            json.dumps(
                [
                    {
                        k: v
                        for k, v in r.items()
                        if k in ("control", "TERM", "returncode")
                    }
                    for r in results
                ]
            )
        )


if __name__ == "__main__":
    main()
