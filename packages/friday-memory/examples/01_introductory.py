#!/usr/bin/env python3
"""
Friday Memory - Introductory Example

This example demonstrates the basic building blocks of friday-memory:
- Data models (ProvenanceMetadata, InteractionTurn, GraphNode)
- The InMemoryEpisodicStore for conversation history
- Basic CRUD operations

Prerequisites:
    pip install friday-memory

Run:
    python 01_introductory.py
"""

import asyncio
import uuid
from datetime import datetime

from friday_memory import (
    GraphNode,
    InMemoryEpisodicStore,
    InteractionTurn,
    ProvenanceMetadata,
    ToolCall,
    ToolResult,
)


async def main():
    print("=" * 60)
    print("Friday Memory - Introductory Example")
    print("=" * 60)

    # =========================================================================
    # Part 1: Understanding Provenance
    # =========================================================================
    print("\n[Part 1] Provenance Metadata")
    print("-" * 40)

    # Every piece of data in friday-memory has provenance tracking.
    # This ensures we always know where information came from.
    provenance = ProvenanceMetadata(
        source_id="conversation_001",
        source_type="interaction",  # Options: 'interaction', 'document', 'inference'
        confidence=0.95,
        author_id="user_alice",
    )
    print(f"Created provenance: source={provenance.source_id}, type={provenance.source_type}")
    print(f"  Confidence: {provenance.confidence}")
    print(f"  Created at: {provenance.created_at}")

    # =========================================================================
    # Part 2: Graph Nodes with Hebbian Learning
    # =========================================================================
    print("\n[Part 2] Graph Nodes")
    print("-" * 40)

    # GraphNodes represent entities, concepts, or events in the knowledge graph.
    # They support Hebbian learning through hit_count tracking.
    node = GraphNode(
        id="person_bob",
        type="Entity",
        label="Bob Smith",
        properties={
            "role": "Software Engineer",
            "department": "Engineering",
            "skills": ["Python", "TypeScript", "Rust"],
        },
        provenance=provenance,
    )

    print(f"Created node: {node.label} ({node.type})")
    print(f"  Properties: {node.properties}")
    print(f"  Hit count: {node.hit_count}")

    # Simulate accessing this node multiple times (Hebbian learning)
    # "Neurons that fire together, wire together"
    for i in range(3):
        node.touch()
        print(f"  After touch {i + 1}: hit_count = {node.hit_count}")

    # =========================================================================
    # Part 3: Episodic Memory (Conversation History)
    # =========================================================================
    print("\n[Part 3] Episodic Store")
    print("-" * 40)

    # The episodic store manages conversation history per session.
    episodic = InMemoryEpisodicStore()

    # Create some interaction turns
    session_id = "session_001"

    turn1 = InteractionTurn(
        id=str(uuid.uuid4()),
        session_id=session_id,
        timestamp=datetime.now(),
        user_message="What's the weather like today?",
        assistant_message="I'd be happy to help! Could you tell me your location?",
    )

    turn2 = InteractionTurn(
        id=str(uuid.uuid4()),
        session_id=session_id,
        timestamp=datetime.now(),
        user_message="I'm in San Francisco.",
        assistant_message="The weather in San Francisco today is 65F and sunny.",
    )

    # A turn with tool usage
    turn3 = InteractionTurn(
        id=str(uuid.uuid4()),
        session_id=session_id,
        timestamp=datetime.now(),
        user_message="Can you search for nearby coffee shops?",
        assistant_message="I found 3 coffee shops near you. Blue Bottle is the closest.",
        tool_calls=[
            ToolCall(
                id="call_001",
                name="search_places",
                arguments={"query": "coffee shops", "location": "San Francisco"},
            )
        ],
        tool_results=[
            ToolResult(
                tool_call_id="call_001",
                output='[{"name": "Blue Bottle", "distance": "0.2mi"}, ...]',
            )
        ],
    )

    # Add turns to the episodic store
    await episodic.add_turn(session_id, turn1)
    await episodic.add_turn(session_id, turn2)
    await episodic.add_turn(session_id, turn3)

    print(f"Added {await episodic.get_turn_count(session_id)} turns to session")

    # Retrieve conversation history
    history = await episodic.get_turns(session_id)
    print("\nConversation History:")
    for i, turn in enumerate(history, 1):
        print(f"  Turn {i}:")
        print(f"    User: {turn.user_message[:50]}...")
        print(f"    Assistant: {turn.assistant_message[:50]}...")
        if turn.tool_calls:
            print(f"    Tools used: {[tc.name for tc in turn.tool_calls]}")

    # =========================================================================
    # Part 4: Consolidation Tracking
    # =========================================================================
    print("\n[Part 4] Consolidation")
    print("-" * 40)

    # Turns can be marked as "consolidated" after being processed for
    # long-term memory storage.
    unconsolidated = await episodic.get_unconsolidated_turns(session_id)
    print(f"Unconsolidated turns: {len(unconsolidated)}")

    # Mark the first two turns as consolidated
    await episodic.mark_consolidated([turn1.id, turn2.id])

    unconsolidated = await episodic.get_unconsolidated_turns(session_id)
    print(f"After consolidation: {len(unconsolidated)} turns remaining")

    # =========================================================================
    # Part 5: History Rewind (Time Travel)
    # =========================================================================
    print("\n[Part 5] History Rewind")
    print("-" * 40)

    # We can "rewind" to a previous point in the conversation
    print(f"Current turn count: {await episodic.get_turn_count(session_id)}")

    # Rewind to turn 2 (removes turn 3)
    await episodic.rewind_history(session_id, turn2.id)
    print(f"After rewind to turn 2: {await episodic.get_turn_count(session_id)} turns")

    print("\n" + "=" * 60)
    print("Example complete! You've learned:")
    print("  - ProvenanceMetadata for tracking data origin")
    print("  - GraphNode with Hebbian learning (touch())")
    print("  - InMemoryEpisodicStore for conversation history")
    print("  - Consolidation tracking for long-term memory")
    print("  - History rewind for time-travel debugging")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
