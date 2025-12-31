#!/usr/bin/env python3
"""
Friday Memory - Intermediate Example

This example demonstrates the MemoryController facade which orchestrates
all three memory stores:
- Vector Store (ChromaDB) for semantic search
- Graph Store (ElementX) for entity relationships
- Episodic Store for conversation history

You'll learn:
- Setting up the MemoryController with all stores
- Storing facts with provenance tracking
- Using the unified recall() API
- Entity merging and identity resolution

Prerequisites:
    pip install friday-memory
    # Vector store requires: OPENAI_API_KEY or another embedding provider

Run:
    python 02_intermediate.py

Note: This example uses mock embeddings for demonstration.
      In production, configure your embedding provider.
"""

import asyncio
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch

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
)


def create_mock_litellm():
    """Create a mock for LiteLLM embeddings (for demo purposes)."""
    mock = AsyncMock()

    async def mock_aembedding(model, input):
        import random

        # Generate random embeddings for demo
        embeddings = [[random.random() for _ in range(1536)] for _ in input]
        response = AsyncMock()
        response.data = [{"embedding": emb} for emb in embeddings]
        return response

    mock.aembedding = mock_aembedding
    return mock


async def main():
    print("=" * 60)
    print("Friday Memory - Intermediate Example")
    print("=" * 60)

    # =========================================================================
    # Part 1: Setting Up the Memory Controller
    # =========================================================================
    print("\n[Part 1] Memory Controller Setup")
    print("-" * 40)

    # Create individual stores
    episodic_store = InMemoryEpisodicStore()
    graph_store = ElementXGraphStore()
    vector_store = ChromaVectorStore(
        collection_name=f"demo_{uuid.uuid4().hex[:8]}"
    )

    # Create telemetry recorder for observability
    telemetry = DebugTelemetryRecorder()

    # Initialize the Memory Controller
    controller = MemoryController(
        vector_store=vector_store,
        graph_store=graph_store,
        episodic_store=episodic_store,
        telemetry=telemetry,
    )

    print("Memory Controller initialized with:")
    print("  - ChromaVectorStore (semantic search)")
    print("  - ElementXGraphStore (knowledge graph)")
    print("  - InMemoryEpisodicStore (conversation history)")
    print("  - DebugTelemetryRecorder (observability)")

    # =========================================================================
    # Part 2: Storing Facts in the Knowledge Graph
    # =========================================================================
    print("\n[Part 2] Storing Facts")
    print("-" * 40)

    # Create provenance for our facts
    provenance = ProvenanceMetadata(
        source_id="onboarding_doc_001",
        source_type="document",
        confidence=0.95,
        author_id="hr_system",
    )

    # Create entity nodes
    alice = GraphNode(
        id="person_alice",
        type="Person",
        label="Alice Johnson",
        properties={
            "role": "Engineering Manager",
            "department": "Platform",
            "hire_date": "2022-03-15",
        },
        provenance=provenance,
    )

    bob = GraphNode(
        id="person_bob",
        type="Person",
        label="Bob Smith",
        properties={
            "role": "Senior Engineer",
            "department": "Platform",
            "hire_date": "2021-08-01",
        },
        provenance=provenance,
    )

    platform_team = GraphNode(
        id="team_platform",
        type="Team",
        label="Platform Team",
        properties={
            "mission": "Build core infrastructure",
            "headcount": 8,
        },
        provenance=provenance,
    )

    # Store nodes
    await controller.store_fact(alice)
    await controller.store_fact(bob)
    await controller.store_fact(platform_team)
    print(f"Stored 3 entity nodes")

    # Create and store relationships
    alice_manages = GraphEdge(
        source_id="person_alice",
        target_id="team_platform",
        relation="manages",
        weight=1.0,
        provenance=provenance,
    )

    bob_member = GraphEdge(
        source_id="person_bob",
        target_id="team_platform",
        relation="member_of",
        weight=1.0,
        provenance=provenance,
    )

    alice_mentors = GraphEdge(
        source_id="person_alice",
        target_id="person_bob",
        relation="mentors",
        weight=0.8,
        provenance=provenance,
    )

    # Store edges (requires a node to attach to)
    await controller.store_fact(alice, alice_manages)
    await controller.store_fact(bob, bob_member)
    await controller.store_fact(alice, alice_mentors)
    print(f"Stored 3 relationship edges")

    # Check telemetry
    fact_events = [e for e in telemetry.events if "fact_stored" in str(e)]
    print(f"Telemetry captured {len(fact_events)} fact_stored events")

    # =========================================================================
    # Part 3: Storing Insights in Vector Store
    # =========================================================================
    print("\n[Part 3] Storing Insights (Vector Store)")
    print("-" * 40)

    # Mock LiteLLM for embedding generation
    with patch("friday_memory.adapters.vector.litellm", create_mock_litellm()):
        # Store insights (summaries, learnings) in the vector store
        insight_provenance = ProvenanceMetadata(
            source_id="learning_session_001",
            source_type="inference",
            confidence=0.85,
            author_id="consolidator",
        )

        await controller.store_insight(
            "Alice prefers async standups over daily meetings. "
            "She values written communication for status updates.",
            metadata=insight_provenance,
        )

        await controller.store_insight(
            "The Platform team follows a bi-weekly sprint cycle with "
            "retrospectives every other Friday.",
            metadata=insight_provenance,
        )

        await controller.store_insight(
            "Bob is an expert in distributed systems and has been "
            "mentoring junior engineers on database optimization.",
            metadata=insight_provenance,
        )

        print("Stored 3 insights in vector store")

    # =========================================================================
    # Part 4: Adding Conversation History
    # =========================================================================
    print("\n[Part 4] Conversation History")
    print("-" * 40)

    session_id = "session_demo_001"

    turns = [
        InteractionTurn(
            id=str(uuid.uuid4()),
            session_id=session_id,
            timestamp=datetime.now(),
            user_message="Who manages the Platform team?",
            assistant_message="Alice Johnson manages the Platform team.",
        ),
        InteractionTurn(
            id=str(uuid.uuid4()),
            session_id=session_id,
            timestamp=datetime.now(),
            user_message="What's her management style?",
            assistant_message="Alice prefers async communication and written updates.",
        ),
        InteractionTurn(
            id=str(uuid.uuid4()),
            session_id=session_id,
            timestamp=datetime.now(),
            user_message="Who else is on the team?",
            assistant_message="Bob Smith is a Senior Engineer on the Platform team.",
        ),
    ]

    for turn in turns:
        await controller.add_turn(session_id, turn)

    print(f"Added {len(turns)} turns to session '{session_id}'")

    # =========================================================================
    # Part 5: Unified Recall
    # =========================================================================
    print("\n[Part 5] Unified Recall")
    print("-" * 40)

    with patch("friday_memory.adapters.vector.litellm", create_mock_litellm()):
        # The recall() method searches all stores in parallel
        payload = await controller.recall(
            query="Tell me about Alice and the Platform team",
            session_id=session_id,
            include_history=True,
            history_limit=5,
            vector_results=3,
            graph_depth=1,
        )

        print(f"Recall Results:")
        print(f"  History turns: {len(payload.history)}")
        print(f"  Vector passages: {len(payload.passages)}")
        print(f"  Graph entities: {len(payload.entities)}")
        print(f"  Graph facts: {len(payload.facts)}")

        print(f"\nDebug Info:")
        for key, value in payload.debug_info.items():
            print(f"  {key}: {value}")

    # =========================================================================
    # Part 6: Entity Resolution (Merging Duplicates)
    # =========================================================================
    print("\n[Part 6] Entity Resolution")
    print("-" * 40)

    # Sometimes the same entity appears with different names
    # Create a duplicate "Robert Smith" (same person as Bob)
    robert = GraphNode(
        id="person_robert",
        type="Person",
        label="Robert Smith",
        properties={
            "role": "Senior Engineer",
            "nickname": "Bob",
        },
        provenance=provenance,
    )
    await controller.store_fact(robert)

    print("Before merge:")
    bob_node = await graph_store.get_node("person_bob")
    robert_node = await graph_store.get_node("person_robert")
    print(f"  Bob exists: {bob_node is not None}")
    print(f"  Robert exists: {robert_node is not None}")

    # Merge Robert into Bob (Bob is the canonical entity)
    await controller.merge_identities("person_bob", "person_robert")

    print("\nAfter merge:")
    bob_node = await graph_store.get_node("person_bob")
    robert_node = await graph_store.get_node("person_robert")
    print(f"  Bob exists: {bob_node is not None}")
    print(f"  Robert exists: {robert_node is not None}")

    # =========================================================================
    # Part 7: Graph Traversal and Discovery
    # =========================================================================
    print("\n[Part 7] Graph Traversal")
    print("-" * 40)

    # Find neighbors of a node
    alice_neighbors = await graph_store.get_neighbors("person_alice", depth=1)
    print(f"Alice's direct connections: {len(alice_neighbors)} nodes")
    for neighbor_info in alice_neighbors:
        node_data = neighbor_info["node"]
        relation = neighbor_info["relation"]
        print(f"  - {node_data.get('label', 'unknown')} ({node_data.get('type', 'unknown')}) via '{relation}'")

    # Fuzzy search for entities
    matches = await graph_store.fuzzy_search("alice", threshold=0.6)
    print(f"\nFuzzy search for 'alice': {len(matches)} matches")
    for match in matches:
        print(f"  - {match['label']} (score: {match['score']:.2f})")

    # =========================================================================
    # Part 8: Session Rollback
    # =========================================================================
    print("\n[Part 8] Session Rollback")
    print("-" * 40)

    current_count = await episodic_store.get_turn_count(session_id)
    print(f"Current turn count: {current_count}")

    # Rollback to the second turn
    await controller.rewind_session(session_id, turns[1].id)

    new_count = await episodic_store.get_turn_count(session_id)
    print(f"After rollback to turn 2: {new_count} turns")

    print("\n" + "=" * 60)
    print("Example complete! You've learned:")
    print("  - Setting up MemoryController with all stores")
    print("  - Storing facts (nodes + edges) with provenance")
    print("  - Storing insights in the vector store")
    print("  - Using recall() for unified retrieval")
    print("  - Entity merging for identity resolution")
    print("  - Graph traversal and fuzzy search")
    print("  - Session rollback for time-travel")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
