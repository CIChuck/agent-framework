"""
Tests for provenance tracking in friday-memory.

Tests cover:
- ProvenanceMetadata validation and normalization
- ProvenanceMetadata serialization (to_dict/from_dict)
- ProvenanceMetadata lineage tracking (with_parent)
- Factory functions (create_agent_provenance, create_user_provenance, create_extraction_provenance)
- InteractionTurn with agent_id
- MemoryController author tracking

Ref: docs/build-plan/shared-memory-provenance-build-plan.md
"""  # noqa: E501

import uuid

import pytest
from friday_memory import (
    InteractionTurn,
    ProvenanceMetadata,
)
from friday_memory.models.graph import (
    create_agent_provenance,
    create_extraction_provenance,
    create_user_provenance,
)


class TestProvenanceValidation:
    """Tests for ProvenanceMetadata validation and normalization."""

    def test_author_id_normalized_to_lowercase(self):
        """Test that author_id is normalized to lowercase."""
        provenance = ProvenanceMetadata(
            source_id="test",
            source_type="agent",
            author_id="MyAgent",
        )
        assert provenance.author_id == "myagent"

    def test_author_id_trimmed(self):
        """Test that author_id is trimmed."""
        provenance = ProvenanceMetadata(
            source_id="test",
            source_type="agent",
            author_id="  researcher  ",
        )
        assert provenance.author_id == "researcher"

    def test_author_id_empty_string_raises(self):
        """Test that empty string author_id raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            ProvenanceMetadata(
                source_id="test",
                source_type="agent",
                author_id="",
            )

    def test_author_id_whitespace_only_raises(self):
        """Test that whitespace-only author_id raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            ProvenanceMetadata(
                source_id="test",
                source_type="agent",
                author_id="   ",
            )

    def test_author_id_none_allowed(self):
        """Test that None author_id is allowed."""
        provenance = ProvenanceMetadata(
            source_id="test",
            source_type="test",
        )
        assert provenance.author_id is None

    def test_source_type_normalized(self):
        """Test that source_type is normalized to lowercase."""
        provenance = ProvenanceMetadata(
            source_id="test",
            source_type="AGENT",
        )
        assert provenance.source_type == "agent"

    def test_source_type_trimmed(self):
        """Test that source_type is trimmed."""
        provenance = ProvenanceMetadata(
            source_id="test",
            source_type="  extraction  ",
        )
        assert provenance.source_type == "extraction"


class TestProvenanceLineage:
    """Tests for ProvenanceMetadata lineage tracking."""

    def test_with_parent_adds_parent_id(self):
        """Test that with_parent adds a parent ID."""
        original = ProvenanceMetadata(
            source_id="original",
            source_type="agent",
            author_id="researcher",
        )
        derived = original.with_parent("parent_123")

        assert derived.parent_ids == ["parent_123"]
        # Original should be unchanged
        assert original.parent_ids == []

    def test_with_parent_preserves_other_fields(self):
        """Test that with_parent preserves all other fields."""
        original = ProvenanceMetadata(
            source_id="original",
            source_type="extraction",
            author_id="extractor",
            confidence=0.8,
        )
        derived = original.with_parent("parent_456")

        assert derived.source_id == original.source_id
        assert derived.source_type == original.source_type
        assert derived.author_id == original.author_id
        assert derived.confidence == original.confidence

    def test_multiple_parents_chain(self):
        """Test chaining multiple with_parent calls."""
        original = ProvenanceMetadata(
            source_id="base",
            source_type="agent",
        )
        first = original.with_parent("parent_1")
        second = first.with_parent("parent_2")
        third = second.with_parent("parent_3")

        assert third.parent_ids == ["parent_1", "parent_2", "parent_3"]

    def test_parent_ids_default_empty(self):
        """Test that parent_ids defaults to empty list."""
        provenance = ProvenanceMetadata(
            source_id="test",
            source_type="test",
        )
        assert provenance.parent_ids == []


class TestProvenanceSerialization:
    """Tests for ProvenanceMetadata to_dict/from_dict methods."""

    def test_to_dict_basic(self):
        """Test basic serialization to dict."""
        provenance = ProvenanceMetadata(
            source_id="doc_123",
            source_type="document",
            author_id="processor",
            confidence=0.95,
        )
        data = provenance.to_dict()

        assert data["source_id"] == "doc_123"
        assert data["source_type"] == "document"
        assert data["author_id"] == "processor"
        assert data["confidence"] == 0.95
        assert "created_at" in data
        assert data["parent_ids"] == []

    def test_from_dict_basic(self):
        """Test basic deserialization from dict."""
        data = {
            "source_id": "source_abc",
            "source_type": "extraction",
            "author_id": "extractor",
            "confidence": 0.8,
            "created_at": "2025-01-24T12:00:00",
            "parent_ids": [],
        }
        provenance = ProvenanceMetadata.from_dict(data)

        assert provenance.source_id == "source_abc"
        assert provenance.source_type == "extraction"
        assert provenance.author_id == "extractor"
        assert provenance.confidence == 0.8

    def test_round_trip_serialization(self):
        """Test that to_dict/from_dict are inverse operations."""
        original = ProvenanceMetadata(
            source_id="round_trip",
            source_type="test",
            author_id="tester",
            confidence=0.75,
            parent_ids=["parent_1", "parent_2"],
        )
        data = original.to_dict()
        restored = ProvenanceMetadata.from_dict(data)

        assert restored.source_id == original.source_id
        assert restored.source_type == original.source_type
        assert restored.author_id == original.author_id
        assert restored.confidence == original.confidence
        assert restored.parent_ids == original.parent_ids

    def test_from_dict_with_missing_optional_fields(self):
        """Test deserialization with minimal required fields."""
        data = {
            "source_id": "minimal",
            "source_type": "test",
        }
        provenance = ProvenanceMetadata.from_dict(data)

        assert provenance.source_id == "minimal"
        assert provenance.author_id is None
        assert provenance.parent_ids == []


class TestProvenanceFactoryFunctions:
    """Tests for provenance factory functions."""

    def test_create_agent_provenance(self):
        """Test create_agent_provenance factory."""
        provenance = create_agent_provenance("researcher")

        assert provenance.author_id == "researcher"
        assert provenance.source_type == "agent"
        assert provenance.source_id == "manual"
        assert provenance.confidence == 1.0

    def test_create_agent_provenance_with_options(self):
        """Test create_agent_provenance with custom options."""
        provenance = create_agent_provenance(
            author_id="coder",
            source_id="code_review",
            confidence=0.9,
        )

        assert provenance.author_id == "coder"
        assert provenance.source_type == "agent"
        assert provenance.source_id == "code_review"
        assert provenance.confidence == 0.9

    def test_create_user_provenance(self):
        """Test create_user_provenance factory."""
        provenance = create_user_provenance("user_123")

        assert provenance.author_id == "user_123"
        assert provenance.source_type == "user"
        assert provenance.source_id == "user_input"
        assert provenance.confidence == 1.0

    def test_create_user_provenance_with_source_id(self):
        """Test create_user_provenance with custom source_id."""
        provenance = create_user_provenance(
            user_id="user_456",
            source_id="api_request",
        )

        assert provenance.author_id == "user_456"
        assert provenance.source_id == "api_request"

    def test_create_extraction_provenance(self):
        """Test create_extraction_provenance factory."""
        provenance = create_extraction_provenance(
            author_id="consolidator",
            source_id="turn_789",
        )

        assert provenance.author_id == "consolidator"
        assert provenance.source_type == "extraction"
        assert provenance.source_id == "turn_789"
        assert provenance.confidence == 0.9

    def test_create_extraction_provenance_with_parents(self):
        """Test create_extraction_provenance with parent_ids."""
        provenance = create_extraction_provenance(
            author_id="consolidator",
            source_id="turn_999",
            parent_ids=["turn_1", "turn_2"],
            confidence=0.85,
        )

        assert provenance.parent_ids == ["turn_1", "turn_2"]
        assert provenance.confidence == 0.85


class TestInteractionTurnAgentId:
    """Tests for agent_id field in InteractionTurn."""

    def test_turn_with_agent_id(self):
        """Test creating turn with agent_id."""
        turn = InteractionTurn(
            id=str(uuid.uuid4()),
            session_id="test_session",
            user_message="Hello",
            assistant_message="Hi there!",
            agent_id="researcher",
        )
        assert turn.agent_id == "researcher"

    def test_turn_without_agent_id(self):
        """Test creating turn without agent_id defaults to None."""
        turn = InteractionTurn(
            id=str(uuid.uuid4()),
            session_id="test_session",
            user_message="Test",
            assistant_message="Response",
        )
        assert turn.agent_id is None

    def test_turn_agent_id_in_dict(self):
        """Test that agent_id is included in model_dump."""
        turn = InteractionTurn(
            id="turn_123",
            session_id="sess_456",
            user_message="Query",
            assistant_message="Answer",
            agent_id="coder",
        )
        data = turn.model_dump()
        assert data["agent_id"] == "coder"


class TestMemoryControllerAuthorTracking:
    """Tests for MemoryController author tracking."""

    def test_default_author_is_system(self, memory_controller):
        """Test that default author is 'system'."""
        assert memory_controller.current_author == "system"

    def test_set_author(self, memory_controller):
        """Test setting a new author."""
        memory_controller.set_author("researcher")
        assert memory_controller.current_author == "researcher"

    def test_set_author_normalizes_to_lowercase(self, memory_controller):
        """Test that set_author normalizes to lowercase."""
        memory_controller.set_author("MyAgent")
        assert memory_controller.current_author == "myagent"

    def test_set_author_trims_whitespace(self, memory_controller):
        """Test that set_author trims whitespace."""
        memory_controller.set_author("  coder  ")
        assert memory_controller.current_author == "coder"

    def test_set_author_empty_raises(self, memory_controller):
        """Test that empty author raises ValueError."""
        with pytest.raises(ValueError):
            memory_controller.set_author("")

    def test_set_author_whitespace_raises(self, memory_controller):
        """Test that whitespace-only author raises ValueError."""
        with pytest.raises(ValueError):
            memory_controller.set_author("   ")

    def test_custom_default_author(
        self,
        vector_store,
        graph_store,
        episodic_store,
        telemetry,
        collection_manager,
    ):
        """Test creating controller with custom default author."""
        from friday_memory import MemoryController

        controller = MemoryController(
            vector_store=vector_store,
            graph_store=graph_store,
            episodic_store=episodic_store,
            telemetry=telemetry,
            collection_manager=collection_manager,
            default_author_id="custom_agent",
        )
        assert controller.current_author == "custom_agent"
