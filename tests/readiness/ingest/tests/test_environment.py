from __future__ import annotations

import unittest

from ingest.environment import child_environment, startup_inventory
from ingest.manifests import Refusal
from ingest.tests.test_manifests import unit


class Environment(unittest.TestCase):
    def test_secrets_proxies_and_python_state_not_inherited(self) -> None:
        root = unit()
        actual = child_environment(
            root,
            {
                "HOME": "/operator-home",
                "OPENAI_API_KEY": "fake-sentinel",
                "HTTP_PROXY": "http://fake",
                "PYTHONPATH": "fake",
                "UV_INDEX_URL": "fake",
            },
        )
        self.assertEqual(actual["HOME"], "/operator-home")
        self.assertFalse(
            {"OPENAI_API_KEY", "HTTP_PROXY", "PYTHONPATH", "UV_INDEX_URL"}
            & actual.keys()
        )
        self.assertEqual(actual["LITELLM_MODE"], "PRODUCTION")
        self.assertEqual(actual["LITELLM_LOCAL_MODEL_COST_MAP"], "True")
        self.assertEqual(actual["UV_NO_PYTHON_DOWNLOADS"], "1")
        self.assertTrue(actual["NETRC"].startswith(str(root)))

    def test_site_inventory_blocks_executable_files_before_tool(self) -> None:
        root = unit()
        path = root / "armed.pth"
        path.write_text("import fake_canary\n")
        self.assertEqual(
            startup_inventory(root, False)[0]["classification"],
            "nonexecuted_guarded_data",
        )
        with self.assertRaises(Refusal):
            startup_inventory(root, True)
        path.write_text("# inert data\n")
        self.assertEqual(
            startup_inventory(root, True)[0]["classification"],
            "inert_or_owned_path_only",
        )
        path.write_text("../external\n")
        with self.assertRaises(Refusal):
            startup_inventory(root, True)
