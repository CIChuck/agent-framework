"""
Shared test fixtures for friday-memory tests.
"""

import uuid
from datetime import datetime

import pytest

from friday_core import DebugTelemetryRecorder

from friday_memory import (
    ChromaVectorStore,
    ElementXGraphStore,
    GraphEdge,
    GraphNode,
    InMemoryEpisodicStore,
    InteractionTurn,
    MemoryController,
    ProvenanceMetadata,
    SessionState,
)


# --- Provenance Fixtures ---


@pytest.fixture
def sample_provenance() -> ProvenanceMetadata:
    """Create a sample provenance metadata."""
    return ProvenanceMetadata(
        source_id="test_source_123",
        source_type="test",
        confidence=0.95,
        author_id="test_author",
    )


# --- Graph Fixtures ---


@pytest.fixture
def sample_node(sample_provenance: ProvenanceMetadata) -> GraphNode:
    """Create a sample graph node."""
    return GraphNode(
        id=str(uuid.uuid4()),
        type="person",
        label="Alice",
        properties={"role": "developer", "team": "backend"},
        provenance=sample_provenance,
    )


@pytest.fixture
def sample_edge(sample_provenance: ProvenanceMetadata) -> GraphEdge:
    """Create a sample graph edge."""
    return GraphEdge(
        source_id="node_1",
        target_id="node_2",
        relation="works_with",
        weight=1.0,
        provenance=sample_provenance,
    )


# --- Session Fixtures ---


@pytest.fixture
def sample_turn() -> InteractionTurn:
    """Create a sample interaction turn."""
    return InteractionTurn(
        id=str(uuid.uuid4()),
        session_id="test_session",
        timestamp=datetime.now(),
        user_message="Hello, how are you?",
        assistant_message="I'm doing well, thank you for asking!",
        tool_calls=[],
        tool_results=[],
        consolidated=False,
    )


@pytest.fixture
def sample_session_state() -> SessionState:
    """Create a sample session state."""
    return SessionState(
        session_id="test_session_123",
        user_id="test_user_456",
        turn_count=0,
        start_time=datetime.now(),
        active_goals=["Help with coding"],
        scoped_vars={
            "user:theme": "dark",
            "session:current_task": "debugging",
        },
    )


# --- Adapter Fixtures ---


@pytest.fixture
def episodic_store() -> InMemoryEpisodicStore:
    """Create an in-memory episodic store."""
    return InMemoryEpisodicStore()


@pytest.fixture
def graph_store() -> ElementXGraphStore:
    """Create an in-memory graph store."""
    return ElementXGraphStore()


@pytest.fixture
def vector_store() -> ChromaVectorStore:
    """Create an ephemeral vector store."""
    # Use unique collection name to avoid conflicts between tests
    collection_name = f"test_collection_{uuid.uuid4().hex[:8]}"
    return ChromaVectorStore(collection_name=collection_name)


# --- Telemetry Fixtures ---


@pytest.fixture
def telemetry() -> DebugTelemetryRecorder:
    """Create a debug telemetry recorder."""
    return DebugTelemetryRecorder()


# --- Controller Fixtures ---


@pytest.fixture
def memory_controller(
    vector_store: ChromaVectorStore,
    graph_store: ElementXGraphStore,
    episodic_store: InMemoryEpisodicStore,
    telemetry: DebugTelemetryRecorder,
) -> MemoryController:
    """Create a memory controller with all stores."""
    return MemoryController(
        vector_store=vector_store,
        graph_store=graph_store,
        episodic_store=episodic_store,
        telemetry=telemetry,
    )
