from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path

from ingest.export import ObjectView
from ingest.manifests import Refusal, digest
from ingest.tests.test_manifests import unit


class Exports(unittest.TestCase):
    def test_actual_committed_blob_export_excludes_dirty_content(self) -> None:
        root = unit()
        source = root / "fixture-repository"
        source.mkdir()
        empty = root / "empty-config"
        empty.write_bytes(b"")
        templates = root / "empty-template"
        templates.mkdir()
        env = {
            "PATH": "/usr/bin:/bin",
            "HOME": os.environ.get("HOME", ""),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_SYSTEM": str(empty),
            "GIT_CONFIG_GLOBAL": str(empty),
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_AUTHOR_NAME": "C0 fixture",
            "GIT_AUTHOR_EMAIL": "fixture@invalid.example",
            "GIT_COMMITTER_NAME": "C0 fixture",
            "GIT_COMMITTER_EMAIL": "fixture@invalid.example",
            "GIT_AUTHOR_DATE": "2020-01-01T00:00:00+00:00",
            "GIT_COMMITTER_DATE": "2020-01-01T00:00:00+00:00",
        }

        def git(*args: str) -> bytes:
            return subprocess.run(
                ["/usr/bin/git", *args],
                cwd=source,
                env=env,
                check=True,
                capture_output=True,
            ).stdout

        git("init", "--template=" + str(templates))
        (source / "selected.txt").write_bytes(b"COMMITTED")
        git("add", "--", "selected.txt")
        git("-c", "core.hooksPath=/dev/null", "commit", "-m", "private C0 fixture")
        commit = git("rev-parse", "HEAD").strip().decode()
        index_before = (source / ".git/index").read_bytes()
        (source / "selected.txt").write_bytes(b"DIRTY DO NOT EXPORT")
        (source / "untracked.txt").write_bytes(b"NO")
        view = ObjectView(
            root / "object-view", source / ".git/objects", Path("/usr/bin/git")
        )
        view.create()
        result = view.export(
            commit, {"selected.txt": digest(b"COMMITTED")}, root / "export"
        )
        self.assertEqual((root / "export/selected.txt").read_bytes(), b"COMMITTED")
        self.assertEqual(result["selected.txt"], digest(b"COMMITTED"))
        self.assertFalse((root / "export/untracked.txt").exists())
        self.assertEqual((source / ".git/index").read_bytes(), index_before)
        with self.assertRaises(Refusal):
            view.export(commit, {"../escape": digest(b"bad")}, root / "escape")
        with self.assertRaises(Refusal):
            view.export(commit, {"selected.txt": "0" * 64}, root / "bad-hash")
        self.assertFalse((root / "bad-hash").exists())
