from __future__ import annotations

import contextlib
import io
import json
import sys
import unittest

from ingest.manifests import canonical, digest, text
from ingest.stages import main
from ingest.tests.test_manifests import unit
from ingest.tests.test_startup import copy_harness


def controls() -> list[str]:
    root = unit()
    _, manifest, sha = copy_harness()
    value = {
        "schema": 1,
        "project": str(root),
        "run_id": "manual",
        "harness_sha256": sha,
        "envelope_sha256": "e" * 64,
        "interpreter_sha256": digest(
            __import__("pathlib").Path(sys.executable).read_bytes()
        ),
        "activation": "C0",
    }
    config = unit() / "control.json"
    config.write_bytes(canonical(value))
    return [
        "--harness-manifest",
        str(manifest),
        "--harness-manifest-sha256",
        sha,
        "--config",
        str(config),
        "--config-sha256",
        digest(config.read_bytes()),
    ]


def command(name: str, args: list[str]) -> tuple[int, dict[str, object]]:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = main([name, *args])
    return code, json.loads(output.getvalue())


class Cli(unittest.TestCase):
    def test_preflight_has_no_files_and_init_requires_absent_root(self) -> None:
        args = controls()
        code, preflight = command("preflight", args)
        from pathlib import Path

        run = Path(text(preflight["run_root"]))
        self.assertEqual(code, 0)
        self.assertFalse(run.exists())
        code, initialized = command("init", args)
        self.assertEqual(code, 0)
        self.assertTrue((run / "harness/run.py").is_file())
        with self.assertRaises(ValueError):
            command("init", args)
        self.assertIn("C0", text(initialized["scope"]))

    def test_unactivated_all_and_report_cannot_pass_readiness(self) -> None:
        args = controls()
        command("init", args)
        code, output = command("run", args)
        self.assertEqual(code, 3)
        self.assertFalse(output["effects_performed"])
        code, output = command("report", args)
        self.assertEqual(code, 3)
        self.assertFalse(output["full_readiness"])
        command("stop", args)
        command("stop", args)
        with self.assertRaises(ValueError):
            command("run", args)
        self.assertEqual(command("report", args)[1]["stopped"], True)

    def test_nonempty_selftest_scratch_refuses_before_discovery(self) -> None:
        args = controls()
        scratch = unit()
        (scratch / "existing").write_text("preserve")
        with self.assertRaises(ValueError):
            command("selftest", args + ["--scratch", str(scratch)])
        self.assertEqual([path.name for path in scratch.iterdir()], ["existing"])

    def test_manual_fixture_preparation_is_explicit_and_does_not_qualify_a2(
        self,
    ) -> None:
        from pathlib import Path

        from ingest.fixtures import verify_matrix

        args = controls()
        command("init", args)
        code, output = command("prepare-fixtures", args)
        self.assertEqual(code, 0)
        self.assertEqual(output["status"], "PREPARED_INPUTS")
        self.assertEqual(output["fixture_count"], 30)
        self.assertIs(output["converter_qualified"], False)
        self.assertIs(output["full_readiness"], False)
        manifest = Path(text(output["manifest"]))
        self.assertEqual(
            len(verify_matrix(manifest.parent, text(output["manifest_sha256"]))), 30
        )
        with self.assertRaises(ValueError):
            command("prepare-fixtures", args)
        self.assertEqual(command("run", args)[0], 3)
        self.assertEqual(command("report", args)[0], 3)
        command("stop", args)
        with self.assertRaises(ValueError):
            command("prepare-fixtures", args)
