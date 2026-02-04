"""
Tests for friday-memory models.

Tests cover:
- ProvenanceMetadata validation
- GraphNode with Hebbian learning (touch)
- GraphEdge relationships
- SessionState scoped variable enforcement
- InteractionTurn with tool calls
- ContextPayload structure
"""

import uuid
from datetime import datetime

import pytest

from friday_memory import (
    ConsolidationReport,
    ContextPayload,
    GraphEdge,
    GraphNode,
    InteractionTurn,
    ProvenanceMetadata,
    SessionState,
    ToolCall,
    ToolResult,
)


class TestProvenanceMetadata:
    """Tests for ProvenanceMetadata model."""

    def test_create_provenance(self):
        """Test basic provenance creation."""
        provenance = ProvenanceMetadata(
            source_id="doc_123",
            source_type="document",
            confidence=0.9,
            author_id="extractor",
        )
        assert provenance.source_id == "doc_123"
        assert provenance.source_type == "document"
        assert provenance.confidence == 0.9
        assert provenance.author_id == "extractor"

    def test_provenance_optional_author(self):
        """Test provenance with optional author_id."""
        provenance = ProvenanceMetadata(
            source_id="test",
            source_type="test",
            confidence=1.0,
        )
        assert provenance.author_id is None

    def test_provenance_confidence_bounds(self):
        """Test confidence is between 0 and 1."""
        # Valid bounds
        ProvenanceMetadata(source_id="t", source_type="t", confidence=0.0)
        ProvenanceMetadata(source_id="t", source_type="t", confidence=1.0)
        ProvenanceMetadata(source_id="t", source_type="t", confidence=0.5)


class TestGraphNode:
    """Tests for GraphNode model."""

    def test_create_node(self, sample_provenance: ProvenanceMetadata):
        """Test basic node creation."""
        node = GraphNode(
            id="node_1",
            type="person",
            label="Bob",
            provenance=sample_provenance,
        )
        assert node.id == "node_1"
        assert node.type == "person"
        assert node.label == "Bob"
        assert node.hit_count == 0
        assert node.properties == {}

    def test_node_with_properties(self, sample_provenance: ProvenanceMetadata):
        """Test node with custom properties."""
        node = GraphNode(
            id="node_2",
            type="project",
            label="Friday",
            properties={"status": "active", "priority": "high"},
            provenance=sample_provenance,
        )
        assert node.properties["status"] == "active"
        assert node.properties["priority"] == "high"

    def test_node_touch_hebbian_learning(self, sample_provenance: ProvenanceMetadata):
        """Test Hebbian learning via touch() method."""
        node = GraphNode(
            id="node_3",
            type="concept",
            label="Memory",
            provenance=sample_provenance,
        )
        assert node.hit_count == 0
        # last_accessed is auto-initialized with default_factory=datetime.now
        assert node.last_accessed is not None
        initial_access = node.last_accessed

        # Touch the node
        node.touch()
        assert node.hit_count == 1
        assert node.last_accessed >= initial_access
        first_access = node.last_accessed

        # Touch again
        node.touch()
        assert node.hit_count == 2
        assert node.last_accessed >= first_access


class TestGraphEdge:
    """Tests for GraphEdge model."""

    def test_create_edge(self, sample_provenance: ProvenanceMetadata):
        """Test basic edge creation."""
        edge = GraphEdge(
            source_id="node_1",
            target_id="node_2",
            relation="knows",
            provenance=sample_provenance,
        )
        assert edge.source_id == "node_1"
        assert edge.target_id == "node_2"
        assert edge.relation == "knows"
        assert edge.weight == 1.0  # default

    def test_edge_with_weight(self, sample_provenance: ProvenanceMetadata):
        """Test edge with custom weight."""
        edge = GraphEdge(
            source_id="a",
            target_id="b",
            relation="related",
            weight=0.75,
            provenance=sample_provenance,
        )
        assert edge.weight == 0.75


class TestSessionState:
    """Tests for SessionState model."""

    def test_create_session_state(self):
        """Test basic session state creation."""
        state = SessionState(
            session_id="sess_123",
            user_id="user_456",
            turn_count=5,
            start_time=datetime.now(),
            active_goals=["Debug app"],
            scoped_vars={},
        )
        assert state.session_id == "sess_123"
        assert state.turn_count == 5

    def test_scoped_var_user_prefix(self):
        """Test setting user-scoped variables."""
        state = SessionState(
            session_id="s",
            user_id="u",
            turn_count=0,
            start_time=datetime.now(),
            active_goals=[],
            scoped_vars={},
        )
        state.set_var("user:theme", "dark")
        assert state.get_var("user:theme") == "dark"

    def test_scoped_var_session_prefix(self):
        """Test setting session-scoped variables."""
        state = SessionState(
            session_id="s",
            user_id="u",
            turn_count=0,
            start_time=datetime.now(),
            active_goals=[],
            scoped_vars={},
        )
        state.set_var("session:step", 3)
        assert state.get_var("session:step") == 3

    def test_scoped_var_app_prefix(self):
        """Test setting app-scoped variables."""
        state = SessionState(
            session_id="s",
            user_id="u",
            turn_count=0,
            start_time=datetime.now(),
            active_goals=[],
            scoped_vars={},
        )
        state.set_var("app:debug_mode", True)
        assert state.get_var("app:debug_mode") is True

    def test_scoped_var_invalid_prefix_raises(self):
        """Test that invalid prefix raises ValueError."""
        state = SessionState(
            session_id="s",
            user_id="u",
            turn_count=0,
            start_time=datetime.now(),
            active_goals=[],
            scoped_vars={},
        )
        with pytest.raises(ValueError, match="must start with"):
            state.set_var("invalid:key", "value")

    def test_get_var_default(self):
        """Test get_var returns default for missing keys."""
        state = SessionState(
            session_id="s",
            user_id="u",
            turn_count=0,
            start_time=datetime.now(),
            active_goals=[],
            scoped_vars={},
        )
        assert state.get_var("user:missing") is None
        assert state.get_var("user:missing", "default") == "default"


class TestInteractionTurn:
    """Tests for InteractionTurn model."""

    def test_create_turn(self):
        """Test basic turn creation."""
        turn = InteractionTurn(
            id="turn_1",
            session_id="test_session",
            timestamp=datetime.now(),
            user_message="Hello",
            assistant_message="Hi there!",
        )
        assert turn.id == "turn_1"
        assert turn.user_message == "Hello"
        assert turn.assistant_message == "Hi there!"
        assert turn.consolidated is False
        assert turn.tool_calls == []
        assert turn.tool_results == []

    def test_turn_with_tool_calls(self):
        """Test turn with tool calls."""
        tool_call = ToolCall(
            id="call_1",
            name="search",
            arguments={"query": "python docs"},
        )
        tool_result = ToolResult(
            tool_call_id="call_1",
            output="Found 10 results",
            error=None,
        )
        turn = InteractionTurn(
            id="turn_2",
            session_id="test_session",
            timestamp=datetime.now(),
            user_message="Search for python docs",
            assistant_message="I found 10 results.",
            tool_calls=[tool_call],
            tool_results=[tool_result],
        )
        assert len(turn.tool_calls) == 1
        assert turn.tool_calls[0].name == "search"
        assert len(turn.tool_results) == 1
        assert turn.tool_results[0].output == "Found 10 results"


class TestContextPayload:
    """Tests for ContextPayload model."""

    def test_create_empty_payload(self):
        """Test creating empty payload."""
        payload = ContextPayload(
            history=[],
            passages=[],
            entities=[],
            facts=[],
            recent_memories=[],
            debug_info={},
        )
        assert payload.history == []
        assert payload.passages == []
        assert payload.debug_info == {}

    def test_payload_with_content(self, sample_turn: InteractionTurn):
        """Test payload with actual content."""
        payload = ContextPayload(
            history=[sample_turn],
            passages=[{"text": "Some doc", "similarity": 0.9}],
            entities=[],
            facts=[],
            recent_memories=["Archived: User prefers Python"],
            debug_info={"query_time": 0.05},
        )
        assert len(payload.history) == 1
        assert len(payload.passages) == 1
        assert payload.recent_memories[0] == "Archived: User prefers Python"


class TestConsolidationReport:
    """Tests for ConsolidationReport model."""

    def test_create_report(self):
        """Test creating consolidation report."""
        report = ConsolidationReport(
            session_id="sess_1",
            nodes_created=5,
            nodes_merged=2,
            conflicts_resolved=1,
            tokens_condensed=500,
            errors=[],
        )
        assert report.nodes_created == 5
        assert report.nodes_merged == 2
        assert report.tokens_condensed == 500
        assert report.errors == []

    def test_report_with_errors(self):
        """Test report with errors."""
        report = ConsolidationReport(
            session_id="sess_2",
            nodes_created=0,
            nodes_merged=0,
            conflicts_resolved=0,
            tokens_condensed=0,
            errors=["Summarization failed", "Graph unavailable"],
        )
        assert len(report.errors) == 2
