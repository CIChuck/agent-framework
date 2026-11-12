from __future__ import annotations

import unittest

from ingest.config import Config
from ingest.manifests import Refusal
from ingest.paths import Layout, physical, regular_relative
from ingest.tests.test_manifests import unit


class Paths(unittest.TestCase):
    def test_new_owned_layout_and_no_reopen(self) -> None:
        root = unit()
        layout = Layout(root, "valid_1")
        layout.create()
        self.assertTrue(layout.destination("state").is_dir())
        self.assertFalse((root / ".friday").exists())
        with self.assertRaises(Refusal):
            layout.create()

    def test_escape_alias_and_symlink_refusals(self) -> None:
        root = unit()
        outside = unit()
        (root / "link").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(Refusal):
            physical(root / "link" / "new")
        for name in ("../escape", "/absolute", "a/../b", "a//b", "a\\b", "."):
            with self.subTest(name=name), self.assertRaises(Refusal):
                regular_relative(name)
        with self.assertRaises(Refusal):
            Layout(root, "../escape")

    def test_unknown_config_and_upstream_activation_refuse(self) -> None:
        root = unit()
        record = {
            "schema": 1,
            "project": str(root),
            "run_id": "case",
            "harness_sha256": "a" * 64,
            "envelope_sha256": "b" * 64,
            "interpreter_sha256": "c" * 64,
            "activation": "C0",
        }
        self.assertEqual(Config.parse(record).layout.project, root)
        for value in (
            record | {"unknown": True},
            record | {"activation": "A3"},
            record | {"schema": True},
            record | {"harness_sha256": ""},
        ):
            with self.subTest(value=value), self.assertRaises(Refusal):
                Config.parse(value)
