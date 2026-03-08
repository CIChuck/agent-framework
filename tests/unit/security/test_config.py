# mypy: disallow-untyped-defs=False, warn-unused-ignores=False
"""Tests for security configuration models."""

import pytest
from friday_core.security import SanitizationConfig


def test_from_dict_defaults():
    config = SanitizationConfig.from_dict({})
    assert config.enabled is True
    assert config.detection.sensitivity == "medium"


def test_quarantine_path_required():
    with pytest.raises(ValueError, match="quarantine_path"):
        SanitizationConfig.from_dict(
            {
                "storage_policy": {
                    "store_raw_on_detection": True,
                    "raw_store_mode": "quarantine",
                }
            }
        )


def test_tool_overrides_parsed():
    config = SanitizationConfig.from_dict(
        {"tool_overrides": {"web_reader": "critical"}}
    )
    assert config.tool_overrides["web_reader"].value == "critical"
