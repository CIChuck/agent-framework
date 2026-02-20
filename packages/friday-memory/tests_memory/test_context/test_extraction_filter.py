"""
Tests for OntologyConfig and ExtractionFilter.

Tests cover:
- OntologyConfig creation, from_dict, default, format_for_prompt
- ExtractionFilter entity filtering (type, blocklist, length, numeric, timestamp)
- ExtractionFilter relationship filtering and normalization
- Rejection logging output
"""

import logging

import pytest
from friday_memory.context.extraction_filter import ExtractionFilter
from friday_memory.context.ontology import NodeTypeConfig, OntologyConfig


@pytest.fixture
def default_ontology():
    """Default ontology config for testing."""
    return OntologyConfig.default()


@pytest.fixture
def default_filter(default_ontology):
    """ExtractionFilter with default ontology."""
    return ExtractionFilter(default_ontology)


class TestOntologyConfig:
    """Tests for OntologyConfig dataclass."""

    def test_default_has_node_types(self):
        """Test that default ontology includes standard node types."""
        ontology = OntologyConfig.default()
        assert "person" in ontology.allowed_node_types
        assert "organization" in ontology.allowed_node_types
        assert "technology" in ontology.allowed_node_types
        assert "location" in ontology.allowed_node_types
        assert "product" in ontology.allowed_node_types
        assert "document" in ontology.allowed_node_types
        # Should NOT include noisy types
        assert "concept" not in ontology.allowed_node_types
        assert "task" not in ontology.allowed_node_types

    def test_default_has_edge_relations(self):
        """Test that default ontology includes canonical edge relations."""
        ontology = OntologyConfig.default()
        all_relations = ontology.all_edge_relations
        assert "USES" in all_relations
        assert "CREATED" in all_relations
        assert "WORKS_AT" in all_relations
        assert "EXPERT_IN" in all_relations
        assert len(all_relations) >= 25

    def test_from_dict_basic(self):
        """Test creating OntologyConfig from dict."""
        data = {
            "node_types": {
                "person": {
                    "description": "A human",
                    "examples": ["Alice", "Bob"],
                },
                "technology": {
                    "description": "A tech tool",
                },
            },
            "edge_relations": {
                "usage": ["USES", "DEPENDS_ON"],
                "ownership": ["OWNS"],
            },
            "label_blocklist": ["morning", "data"],
            "max_label_length": 50,
            "min_label_length": 3,
        }
        ontology = OntologyConfig.from_dict(data)

        assert ontology.allowed_node_types == {"person", "technology"}
        assert "USES" in ontology.all_edge_relations
        assert "OWNS" in ontology.all_edge_relations
        assert ontology.label_blocklist == ["morning", "data"]
        assert ontology.max_label_length == 50
        assert ontology.min_label_length == 3

    def test_from_dict_with_string_node_types(self):
        """Test from_dict accepts simple string descriptions for node types."""
        data = {
            "node_types": {
                "person": "A human individual",
            },
            "edge_relations": {},
        }
        ontology = OntologyConfig.from_dict(data)
        assert "person" in ontology.allowed_node_types
        assert ontology.node_types["person"].description == "A human individual"

    def test_from_dict_defaults(self):
        """Test from_dict uses defaults for missing optional fields."""
        data = {
            "node_types": {"person": {"description": "A human"}},
            "edge_relations": {"usage": ["USES"]},
        }
        ontology = OntologyConfig.from_dict(data)
        assert ontology.max_label_length == 60
        assert ontology.min_label_length == 2
        assert ontology.label_blocklist == []

    def test_format_for_prompt(self):
        """Test that format_for_prompt produces readable text."""
        ontology = OntologyConfig(
            node_types={
                "person": NodeTypeConfig(
                    description="A human individual",
                    examples=["Alice", "Bob"],
                ),
            },
            edge_relations={
                "ownership": ["OWNS", "CREATED"],
                "usage": ["USES"],
            },
        )
        result = ontology.format_for_prompt()

        assert "ALLOWED ENTITY TYPES:" in result
        assert "person: A human individual" in result
        assert "Alice, Bob" in result
        assert "ALLOWED RELATIONS (use ONLY these):" in result
        assert "OWNS, CREATED" in result
        assert "USES" in result

    def test_edge_relations_upper(self):
        """Test edge_relations_upper returns uppercase set."""
        ontology = OntologyConfig(
            node_types={},
            edge_relations={"test": ["uses", "Created"]},
        )
        assert ontology.edge_relations_upper == {"USES", "CREATED"}


class TestExtractionFilterEntities:
    """Tests for entity filtering."""

    def test_accepts_person(self, default_filter):
        """Test that person entities are accepted."""
        entities = [{"label": "Chuck", "type": "person", "properties": {}}]
        accepted, rejected = default_filter.filter_entities(entities)
        assert len(accepted) == 1
        assert len(rejected) == 0
        assert accepted[0]["label"] == "Chuck"

    def test_accepts_technology(self, default_filter):
        """Test that technology entities are accepted."""
        entities = [{"label": "Python", "type": "technology", "properties": {}}]
        accepted, rejected = default_filter.filter_entities(entities)
        assert len(accepted) == 1

    def test_rejects_concept_type(self, default_filter):
        """Test that concept type nodes are rejected."""
        entities = [
            {"label": "morning routine", "type": "concept", "properties": {}},
        ]
        accepted, rejected = default_filter.filter_entities(entities)
        assert len(accepted) == 0
        assert len(rejected) == 1

    def test_rejects_task_type(self, default_filter):
        """Test that task type nodes are rejected."""
        entities = [
            {"label": "Fix the bug", "type": "task", "properties": {}},
        ]
        accepted, rejected = default_filter.filter_entities(entities)
        assert len(accepted) == 0
        assert len(rejected) == 1

    def test_rejects_blocklist_label(self, default_filter):
        """Test that blocklisted labels are rejected."""
        entities = [
            {"label": "morning", "type": "person", "properties": {}},
        ]
        accepted, rejected = default_filter.filter_entities(entities)
        assert len(accepted) == 0
        assert len(rejected) == 1

    def test_blocklist_case_insensitive(self, default_filter):
        """Test that blocklist matching is case-insensitive."""
        entities = [
            {"label": "MORNING", "type": "person", "properties": {}},
        ]
        accepted, rejected = default_filter.filter_entities(entities)
        assert len(accepted) == 0
        assert len(rejected) == 1

    def test_rejects_long_label(self, default_filter):
        """Test that labels exceeding max length are rejected."""
        entities = [
            {"label": "x" * 100, "type": "person", "properties": {}},
        ]
        accepted, rejected = default_filter.filter_entities(entities)
        assert len(accepted) == 0
        assert len(rejected) == 1

    def test_rejects_short_label(self, default_filter):
        """Test that labels shorter than min length are rejected."""
        entities = [
            {"label": "x", "type": "person", "properties": {}},
        ]
        accepted, rejected = default_filter.filter_entities(entities)
        assert len(accepted) == 0
        assert len(rejected) == 1

    def test_rejects_numeric_label(self, default_filter):
        """Test that purely numeric labels are rejected."""
        entities = [
            {"label": "12345", "type": "person", "properties": {}},
        ]
        accepted, rejected = default_filter.filter_entities(entities)
        assert len(accepted) == 0
        assert len(rejected) == 1

    def test_rejects_timestamp_label(self, default_filter):
        """Test that timestamp-like labels are rejected."""
        entities = [
            {"label": "1:30 PM", "type": "person", "properties": {}},
            {"label": "2024-01-15", "type": "person", "properties": {}},
        ]
        accepted, rejected = default_filter.filter_entities(entities)
        assert len(accepted) == 0
        assert len(rejected) == 2

    def test_mixed_entities(self, default_filter):
        """Test filtering a mix of valid and invalid entities."""
        entities = [
            {"label": "Chuck", "type": "person", "properties": {}},
            {"label": "morning", "type": "concept", "properties": {}},
            {"label": "Python", "type": "technology", "properties": {}},
            {"label": "Fix bug", "type": "task", "properties": {}},
        ]
        accepted, rejected = default_filter.filter_entities(entities)
        assert len(accepted) == 2
        assert len(rejected) == 2
        assert {e["label"] for e in accepted} == {"Chuck", "Python"}


class TestExtractionFilterRelationships:
    """Tests for relationship filtering."""

    def test_accepts_canonical_relation(self, default_filter):
        """Test that canonical relations pass through."""
        rels = [{"source_id": "a", "relation": "USES", "target_id": "b"}]
        accepted, rejected = default_filter.filter_relationships(rels)
        assert len(accepted) == 1
        assert accepted[0]["relation"] == "USES"

    def test_normalizes_case(self, default_filter):
        """Test that lowercase relations are normalized to canonical case."""
        rels = [{"source_id": "a", "relation": "uses", "target_id": "b"}]
        accepted, rejected = default_filter.filter_relationships(rels)
        assert len(accepted) == 1
        assert accepted[0]["relation"] == "USES"

    def test_normalizes_spaces_to_underscores(self, default_filter):
        """Test that spaces in relations are converted to underscores."""
        rels = [{"source_id": "a", "relation": "works at", "target_id": "b"}]
        accepted, rejected = default_filter.filter_relationships(rels)
        assert len(accepted) == 1
        assert accepted[0]["relation"] == "WORKS_AT"

    def test_rejects_unknown_relation(self, default_filter):
        """Test that non-canonical relations are rejected."""
        rels = [{"source_id": "a", "relation": "INVOLVES", "target_id": "b"}]
        accepted, rejected = default_filter.filter_relationships(rels)
        assert len(accepted) == 0
        assert len(rejected) == 1

    def test_rejects_is_a_relation(self, default_filter):
        """Test that IS_A (common noise) is rejected."""
        rels = [{"source_id": "a", "relation": "IS_A", "target_id": "b"}]
        accepted, rejected = default_filter.filter_relationships(rels)
        assert len(accepted) == 0
        assert len(rejected) == 1

    def test_rejects_empty_relation(self, default_filter):
        """Test that empty relation strings are rejected."""
        rels = [{"source_id": "a", "relation": "", "target_id": "b"}]
        accepted, rejected = default_filter.filter_relationships(rels)
        assert len(accepted) == 0
        assert len(rejected) == 1

    def test_does_not_mutate_original(self, default_filter):
        """Test that filtering returns copies, not mutated originals."""
        original = {"source_id": "a", "relation": "uses", "target_id": "b"}
        accepted, _ = default_filter.filter_relationships([original])
        # Original should be unchanged
        assert original["relation"] == "uses"
        # Accepted copy should be normalized
        assert accepted[0]["relation"] == "USES"

    def test_mixed_relationships(self, default_filter):
        """Test filtering a mix of valid and invalid relationships."""
        rels = [
            {"source_id": "a", "relation": "USES", "target_id": "b"},
            {"source_id": "a", "relation": "INVOLVES", "target_id": "b"},
            {"source_id": "a", "relation": "created", "target_id": "b"},
            {"source_id": "a", "relation": "FOR", "target_id": "b"},
        ]
        accepted, rejected = default_filter.filter_relationships(rels)
        assert len(accepted) == 2
        assert len(rejected) == 2
        assert {r["relation"] for r in accepted} == {"USES", "CREATED"}


class TestRejectionLogging:
    """Tests for rejection logging output.

    The rejection logger has ``propagate=False`` so that it only writes
    to its file handler in production.  In tests we temporarily
    re-enable propagation so ``caplog`` can capture the records.
    """

    @pytest.fixture(autouse=True)
    def _enable_propagation(self):
        """Temporarily enable propagation for test capture."""
        rej_logger = logging.getLogger("friday_memory.extraction.rejections")
        original = rej_logger.propagate
        rej_logger.propagate = True
        yield
        rej_logger.propagate = original

    def test_rejected_nodes_are_logged(self, default_filter, caplog):
        """Test that rejected nodes produce log output."""
        entities = [
            {"label": "morning routine", "type": "concept", "properties": {}},
        ]
        with caplog.at_level(
            logging.INFO, logger="friday_memory.extraction.rejections"
        ):
            default_filter.filter_entities(entities, turn_id="test_turn_123")

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "Rejected node" in record.message
        assert "concept" in record.message
        assert "morning routine" in record.message
        assert "test_turn_123" in record.message

    def test_rejected_edges_are_logged(self, default_filter, caplog):
        """Test that rejected edges produce log output."""
        rels = [
            {"source_id": "a", "relation": "INVOLVES", "target_id": "b"},
        ]
        with caplog.at_level(
            logging.INFO, logger="friday_memory.extraction.rejections"
        ):
            default_filter.filter_relationships(rels, turn_id="test_turn_456")

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "Rejected edge" in record.message
        assert "INVOLVES" in record.message
        assert "test_turn_456" in record.message

    def test_accepted_items_not_logged(self, default_filter, caplog):
        """Test that accepted items do not produce rejection log entries."""
        entities = [{"label": "Chuck", "type": "person", "properties": {}}]
        with caplog.at_level(
            logging.INFO, logger="friday_memory.extraction.rejections"
        ):
            default_filter.filter_entities(entities)

        # No rejection logger entries
        rejection_records = [
            r for r in caplog.records if r.name == "friday_memory.extraction.rejections"
        ]
        assert len(rejection_records) == 0
