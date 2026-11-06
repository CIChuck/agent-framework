"""Offline regression coverage for required-check discovery and watcher refusal."""

from __future__ import annotations

import runpy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pr-wait"


class RequiredChecksTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = runpy.run_path(str(SCRIPT))
        self.discovery = self.module["required_checks"]
        self.globals = self.discovery.__globals__
        self.scratch = tempfile.TemporaryDirectory(prefix="pr-wait-test-")
        self.addCleanup(self.scratch.cleanup)
        self.globals["STATE_DIR"] = Path(self.scratch.name)
        self.globals["gh"] = Mock(side_effect=AssertionError("live GitHub forbidden"))

    def test_combines_both_protection_sources(self) -> None:
        with patch.dict(
            self.globals,
            gh_lines=Mock(side_effect=[["unit", "lint"], ["unit", "security"]]),
        ):
            self.assertEqual(
                self.discovery("owner/repo", "main"), {"unit", "lint", "security"}
            )

    def test_successful_empty_discovery(self) -> None:
        with patch.dict(self.globals, gh_lines=Mock(return_value=[])):
            self.assertEqual(self.discovery("owner/repo", "main"), set())

    def test_discovery_errors_are_unknown_not_empty_or_partial(self) -> None:
        for status in (403, 404, 429, 500):
            for first_source in (True, False):
                with self.subTest(status=status, first_source=first_source):
                    error = self.module["GhError"](
                        f"HTTP {status}: unavailable", status >= 429
                    )
                    results = [error, []] if first_source else [["unit"], error]
                    with (
                        patch.dict(self.globals, gh_lines=Mock(side_effect=results)),
                        self.assertRaisesRegex(
                            self.module["GhError"], "configuration is unknown"
                        ),
                    ):
                        self.discovery("owner/repo", "main")

    def watcher(self, mode: str):
        watcher = self.module["Watcher"]("owner/repo", 1, mode, 20)
        watcher.fetch_pr = Mock(
            return_value={
                "state": "OPEN",
                "baseRefName": "main",
                "headRefOid": "a" * 40,
                "author": {"login": "author"},
                "viewer": "viewer",
                "comments": {"nodes": []},
                "reviews": {"nodes": []},
                "reviewThreads": {"nodes": []},
                "baseRef": {"target": {"oid": "b" * 40}},
                "mergeStateStatus": "CLEAN",
            }
        )
        watcher.fetch_checks = Mock(
            return_value={
                "unit": {
                    "name": "unit",
                    "bucket": "pass",
                    "link": "test:unit",
                    "description": "",
                },
                "Greptile": {
                    "name": "Greptile",
                    "bucket": "pass",
                    "link": "test:review",
                    "description": "",
                },
            }
        )
        watcher.prev_snapshot = [("Greptile", "pass"), ("unit", "pass")]
        watcher.behind = Mock(return_value="")
        return watcher

    def test_watcher_never_reports_success_when_discovery_is_unavailable(self) -> None:
        for mode in ("green", "ready"):
            with self.subTest(mode=mode):
                watcher = self.watcher(mode)
                output = Mock()
                error = self.module["GhError"]("HTTP 403: denied", False)
                with (
                    patch.dict(
                        self.globals, gh_lines=Mock(side_effect=error), print=output
                    ),
                    self.assertRaises(SystemExit) as caught,
                ):
                    watcher.run()
                self.assertEqual(caught.exception.code, 1)
                rendered = str(output.call_args_list)
                self.assertIn("configuration is unknown", rendered)
                self.assertNotIn("green on", rendered)
                self.assertNotIn("ready on", rendered)
                watcher.fetch_checks.assert_not_called()

    def test_verified_discovery_allows_existing_success_paths(self) -> None:
        for mode in ("green", "ready"):
            for required in (["unit"], []):
                with self.subTest(mode=mode, required=required):
                    watcher = self.watcher(mode)
                    with (
                        patch.dict(
                            self.globals,
                            gh_lines=Mock(return_value=required),
                            print=Mock(),
                        ),
                        self.assertRaises(SystemExit) as caught,
                    ):
                        watcher.poll()
                    self.assertEqual(caught.exception.code, 0)

    def test_configured_check_that_has_not_started_remains_pending(self) -> None:
        for mode in ("green", "ready"):
            with self.subTest(mode=mode):
                watcher = self.watcher(mode)
                with patch.dict(
                    self.globals,
                    gh_lines=Mock(return_value=["unit", "security"]),
                    print=Mock(),
                ):
                    watcher.poll()
                self.assertEqual(watcher.required, {"unit", "security"})


if __name__ == "__main__":
    unittest.main()
