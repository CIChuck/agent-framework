"""C0 controls; scratch is explicitly provided by the verified bootstrap."""

from __future__ import annotations

import sys
import unittest
import uuid
from pathlib import Path

from ingest.manifests import Refusal, artifact, canonical, decode, digest, integer, read


def unit() -> Path:
    root: object = getattr(sys.modules["ingest.tests"], "SCRATCH", None)
    if not isinstance(root, Path):
        raise RuntimeError(
            "Use verified bootstrap selftest with explicit private scratch"
        )
    path = root / ("case-" + uuid.uuid4().hex)
    path.mkdir()
    return path


class Manifests(unittest.TestCase):
    def test_reject_duplicate_nonfinite_and_oversize(self) -> None:
        for raw in (
            b'{"x":1,"x":2}',
            b'{"x":NaN}',
            b'{"x":1e999}',
            b" " * (1024 * 1024 + 1),
            b"[]",
        ):
            with self.subTest(raw=raw[:20]), self.assertRaises(Refusal):
                decode(raw)

    def test_canonical_positive_and_digest_binding(self) -> None:
        root = unit()
        path = root / "record.json"
        path.write_bytes(canonical({"z": [1, 2], "a": "ok"}))
        self.assertEqual(
            read(path, digest(path.read_bytes())), {"a": "ok", "z": [1, 2]}
        )
        with self.assertRaises(Refusal):
            read(path, "0" * 64)

    def test_integer_bool_and_artifact_boundaries(self) -> None:
        with self.assertRaises(Refusal):
            integer(True)
        item = {
            "url": "https://files.pythonhosted.org/a.whl",
            "sha256": "a" * 64,
            "size": 1,
            "license": "MIT",
        }
        self.assertEqual(artifact(item, {"files.pythonhosted.org"}), item)
        for update in (
            {"url": "http://files.pythonhosted.org/a.whl"},
            {"url": "https://key@files.pythonhosted.org/a.whl"},
            {"license": ""},
            {"size": 0},
            {"sha256": "a"},
        ):
            with self.subTest(update=update), self.assertRaises(Refusal):
                artifact(item | update, {"files.pythonhosted.org"})
