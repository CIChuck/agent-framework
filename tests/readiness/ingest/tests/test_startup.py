from __future__ import annotations

import hashlib
import json
import sys
import types
import unittest
from pathlib import Path

from ingest.bootstrap import Buffers, verified_buffers
from ingest.manifests import canonical, digest
from ingest.startup import harness_state
from ingest.tests.test_manifests import unit


def copy_harness() -> tuple[Path, Path, str]:
    root = unit()
    _, buffers = harness_state()
    entries: list[dict[str, str]] = []
    for name, raw in buffers.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        entries.append(
            {
                "path": name,
                "blob": hashlib.sha1(
                    b"blob " + str(len(raw)).encode() + b"\0" + raw
                ).hexdigest(),
                "sha256": digest(raw),
                "mode": "100644",
            }
        )
    raw = canonical(
        {"schema": 1, "commit": "a" * 40, "tree": "b" * 40, "files": entries}
    )
    manifest = unit() / "manifest.json"
    manifest.write_bytes(raw)
    return root, manifest, digest(raw)


class Startup(unittest.TestCase):
    def test_positive_and_unapproved_manifest_refusal(self) -> None:
        root, manifest, sha = copy_harness()
        self.assertIn("startup.py", verified_buffers(root, manifest, sha))
        with self.assertRaisesRegex(ValueError, "Unapproved"):
            verified_buffers(root, manifest, "0" * 64)

    def test_dirty_extra_and_pyc_refuse(self) -> None:
        for name, content in [
            ("paths.py", b"CHANGED=True"),
            ("extra.py", b"UNDECLARED=True"),
            ("__pycache__/paths.cpython-313.pyc", b"fake armed cache"),
        ]:
            root, manifest, sha = copy_harness()
            path = root / name
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(content)
            with self.subTest(name=name), self.assertRaises(ValueError):
                verified_buffers(root, manifest, sha)
            self.assertFalse((root / "effect").exists())

    def test_verified_buffer_survives_path_swap(self) -> None:
        root, manifest, sha = copy_harness()
        data = json.loads(manifest.read_bytes())
        source = b'VALUE="approved"\n'
        (root / "probe.py").write_bytes(source)
        data["files"].append(
            {
                "path": "probe.py",
                "blob": hashlib.sha1(
                    b"blob " + str(len(source)).encode() + b"\0" + source
                ).hexdigest(),
                "sha256": digest(source),
                "mode": "100644",
            }
        )
        manifest.write_bytes(canonical(data))
        buffers = verified_buffers(root, manifest, digest(manifest.read_bytes()))
        (root / "probe.py").write_bytes(b'raise RuntimeError("swapped code executed")')
        module = types.ModuleType("ingest.probe")
        Buffers(root, buffers).exec_module(module)
        self.assertEqual(module.VALUE, "approved")
        self.assertTrue(
            sys.flags.no_site and sys.flags.isolated and sys.flags.dont_write_bytecode
        )

    def test_private_startup_canary_is_armed_but_not_processed_by_safe_loader(
        self,
    ) -> None:
        import site

        root, manifest, sha = copy_harness()
        fake_site = unit()
        marker = fake_site / "canary-effect"
        module_name = "c0_armed_" + fake_site.name.replace("-", "_")
        (fake_site / (module_name + ".py")).write_text(
            "from pathlib import Path\nPath("
            + repr(str(marker))
            + ').write_text("ARMED")\n'
        )
        (fake_site / "canary.pth").write_text("import " + module_name + "\n")
        verified_buffers(root, manifest, sha)
        self.assertFalse(marker.exists())
        before = sys.path[:]
        try:
            site.addsitedir(str(fake_site))  # Deliberately unsafe PRIVATE control.
        finally:
            sys.path[:] = before
            sys.modules.pop(module_name, None)
        self.assertEqual(marker.read_text(), "ARMED")

    def test_guard_is_armed_during_verified_test_execution(self) -> None:
        from ingest.startup import _active

        self.assertIsNotNone(_active.get())
        self.assertFalse(any(name.startswith("friday_") for name in sys.modules))

    def test_guarded_child_positive_and_unapproved_script_refusal(self) -> None:
        import os
        import subprocess

        from ingest.environment import child_environment
        from ingest.tests.test_cli import controls

        root, _ = harness_state()
        cwd = unit()
        env = child_environment(cwd, {"HOME": os.environ.get("HOME", "")})
        args = controls()
        flags = ["-I", "-S", "-B"] + (["-O"] if sys.flags.optimize else [])
        result = subprocess.run(
            [
                sys.executable,
                *flags,
                str(root / "bootstrap.py"),
                "preflight",
                *args,
            ],
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "PASS")
        self.assertEqual(list(cwd.iterdir()), [])
        script = cwd / "unapproved.py"
        marker = cwd / "unapproved-effect"
        script.write_text(
            "from pathlib import Path\nPath("
            + repr(str(marker))
            + ').write_text("bad")\n'
        )
        with self.assertRaises(ValueError):
            subprocess.run(
                [sys.executable, *flags, str(script)],
                cwd=cwd,
                env=env,
                check=True,
            )
        self.assertFalse(marker.exists())
        with self.assertRaises(ValueError):
            subprocess.run(
                [
                    sys.executable,
                    "-I",
                    "-S",
                    "-B",
                    str(root / "bootstrap.py"),
                    "preflight",
                    *args,
                ],
                cwd=cwd,
                env=env | {"OPENAI_API_KEY": "fake-forbidden"},
                check=True,
            )
