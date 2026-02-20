"""Tests for skill reference validation and catalog behavior."""

import pytest
from friday_agent.skills import SkillCatalog, SkillCatalogEntry, validate_skill_ref


def test_validate_skill_ref_accepts_canonical_format():
    assert validate_skill_ref("planner.basic@1.0.0") == "planner.basic@1.0.0"


def test_validate_skill_ref_rejects_invalid_format():
    with pytest.raises(ValueError, match="Expected format"):
        validate_skill_ref("invalid ref")


def test_skill_catalog_local_and_federated_resolution():
    catalog = SkillCatalog()
    catalog.register_local("planner.basic@1.0.0", metadata={"owner": "local"})
    catalog.sync_federated_catalog(
        "shared",
        [
            "writer.advanced@2.1.0",
            SkillCatalogEntry("reviewer.audit@1.2.3", source="federated:shared"),
        ],
    )

    assert catalog.has_skill("planner.basic@1.0.0")
    assert catalog.has_skill("writer.advanced@2.1.0")
    assert catalog.resolve("planner.basic@1.0.0").source == "local"
    assert catalog.resolve("reviewer.audit@1.2.3").source == "federated:shared"
