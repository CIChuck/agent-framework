#!/usr/bin/env python3
"""
Friday Memory - Advanced Example

This example demonstrates the complete context engineering pipeline:
- Document ingestion with chunking
- ContextAssembler for session management
- PromptArchitect for token budgeting and layout
- Full retrieval-augmented generation (RAG) workflow
- Memory consolidation

You'll learn:
- End-to-end document to prompt workflow
- Token budget management ("Knapsack" algorithm)
- Session state and checkpoints
- Scoped variables for personalization
- Building LLM-ready prompts

Prerequisites:
    pip install friday-memory
    # Vector store requires: OPENAI_API_KEY or another embedding provider

Run:
    python 03_advanced.py
"""

import asyncio
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, patch

from friday_core import DebugTelemetryRecorder

from friday_memory import (
    ChromaVectorStore,
    ContextAssembler,
    ContextPayload,
    DocumentIngestionPipeline,
    ElementXGraphStore,
    GraphEdge,
    GraphNode,
    InMemoryEpisodicStore,
    InteractionTurn,
    MemoryController,
    PromptArchitect,
    ProvenanceMetadata,
    SessionState,
)


def create_mock_litellm():
    """Create a mock for LiteLLM embeddings (for demo purposes)."""
    mock = AsyncMock()

    async def mock_aembedding(model, input):
        import random

        embeddings = [[random.random() for _ in range(1536)] for _ in input]
        response = AsyncMock()
        response.data = [{"embedding": emb} for emb in embeddings]
        return response

    mock.aembedding = mock_aembedding
    return mock


async def main():
    print("=" * 70)
    print("Friday Memory - Advanced Example")
    print("Complete Context Engineering Pipeline")
    print("=" * 70)

    # =========================================================================
    # Part 1: Document Ingestion Pipeline
    # =========================================================================
    print("\n[Part 1] Document Ingestion")
    print("-" * 50)

    # Create a sample document for ingestion
    sample_doc = """
# Platform Team Documentation

## Team Overview

The Platform Team is responsible for building and maintaining the core
infrastructure that powers all of our products. We focus on reliability,
scalability, and developer experience.

### Team Members

- **Alice Johnson** (Engineering Manager): Leads the team, focuses on
  architecture decisions and cross-team coordination.
- **Bob Smith** (Senior Engineer): Expert in distributed systems,
  mentors junior engineers on database optimization.
- **Carol Chen** (Engineer): Specializes in CI/CD pipelines and
  infrastructure automation.

## Work Practices

### Communication
- We prefer async standup updates over daily video calls
- All decisions are documented in our team wiki
- Slack channel: #platform-team

### Sprint Cycle
- Two-week sprints starting on Mondays
- Sprint planning: Monday 10am
- Retrospective: Every other Friday 3pm

### Code Review
- All PRs require at least one approval
- Use the CODEOWNERS file for automatic reviewer assignment
- SLA: Reviews within 24 hours

## Current Projects

1. **Database Migration**: Moving from PostgreSQL to CockroachDB
2. **API Gateway**: Building a unified gateway for all microservices
3. **Observability**: Improving tracing and metrics collection
"""

    # Write to a temp file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False
    ) as f:
        f.write(sample_doc)
        doc_path = Path(f.name)

    # Initialize the ingestion pipeline
    pipeline = DocumentIngestionPipeline(
        chunk_size=400,  # Characters per chunk
        overlap=50,  # Overlap between chunks
        author_id="doc_ingestion_demo",
    )

    # Ingest the document
    result = pipeline.ingest_file(doc_path)

    print(f"Ingested: {result.source_path}")
    print(f"  Document ID: {result.document_id}")
    print(f"  Total characters: {result.total_characters}")
    print(f"  Chunks created: {result.total_chunks}")

    print(f"\nChunk preview (first 2 chunks):")
    for i, chunk in enumerate(result.chunks[:2]):
        preview = chunk.text[:100].replace("\n", " ")
        print(f"  Chunk {i + 1}: \"{preview}...\"")
        print(f"    Provenance: {chunk.provenance.source_type}")

    # =========================================================================
    # Part 2: Setting Up the Full Stack
    # =========================================================================
    print("\n[Part 2] Full Stack Setup")
    print("-" * 50)

    # Create stores
    episodic_store = InMemoryEpisodicStore()
    graph_store = ElementXGraphStore()
    vector_store = ChromaVectorStore(
        collection_name=f"advanced_demo_{uuid.uuid4().hex[:8]}"
    )
    telemetry = DebugTelemetryRecorder()

    # Create Memory Controller
    controller = MemoryController(
        vector_store=vector_store,
        graph_store=graph_store,
        episodic_store=episodic_store,
        telemetry=telemetry,
    )

    # Create Prompt Architect (token budgeting engine)
    architect = PromptArchitect(
        model_name="gpt-4",
        max_tokens=8192,
        output_buffer=1024,  # Reserve tokens for model response
    )

    # Create Context Assembler (orchestrator)
    assembler = ContextAssembler(
        memory_controller=controller,
        prompt_architect=architect,
        model_name="gpt-4",
        max_tokens=8192,
        telemetry=telemetry,
    )

    print("Initialized:")
    print("  - MemoryController (unified memory facade)")
    print("  - PromptArchitect (token budgeting)")
    print("  - ContextAssembler (context engineering)")

    # =========================================================================
    # Part 3: Populating Memory Stores
    # =========================================================================
    print("\n[Part 3] Populating Memory")
    print("-" * 50)

    with patch("friday_memory.adapters.vector.litellm", create_mock_litellm()):
        # Store document chunks in vector store
        chunk_texts = [c.text for c in result.chunks]
        chunk_metadatas = [
            {
                "source": "platform_docs",
                "chunk_index": i,
                "doc_id": result.document_id,
            }
            for i in range(len(result.chunks))
        ]
        chunk_ids = [c.id for c in result.chunks]

        await vector_store.add_documents(
            texts=chunk_texts,
            metadatas=chunk_metadatas,
            ids=chunk_ids,
        )
        print(f"Added {len(chunk_texts)} chunks to vector store")

    # Create graph entities from document
    doc_provenance = ProvenanceMetadata(
        source_id=result.document_id,
        source_type="document",
        confidence=0.9,
        author_id="doc_ingestion_demo",
    )

    # Create entity nodes
    entities = [
        GraphNode(
            id="person_alice",
            type="Person",
            label="Alice Johnson",
            properties={"role": "Engineering Manager", "team": "Platform"},
            provenance=doc_provenance,
        ),
        GraphNode(
            id="person_bob",
            type="Person",
            label="Bob Smith",
            properties={"role": "Senior Engineer", "expertise": "distributed systems"},
            provenance=doc_provenance,
        ),
        GraphNode(
            id="person_carol",
            type="Person",
            label="Carol Chen",
            properties={"role": "Engineer", "specialty": "CI/CD"},
            provenance=doc_provenance,
        ),
        GraphNode(
            id="team_platform",
            type="Team",
            label="Platform Team",
            properties={"focus": "infrastructure", "channel": "#platform-team"},
            provenance=doc_provenance,
        ),
        GraphNode(
            id="project_db_migration",
            type="Project",
            label="Database Migration",
            properties={"from": "PostgreSQL", "to": "CockroachDB"},
            provenance=doc_provenance,
        ),
    ]

    for entity in entities:
        await controller.store_fact(entity)

    # Create relationships
    edges = [
        GraphEdge(
            source_id="person_alice",
            target_id="team_platform",
            relation="manages",
            provenance=doc_provenance,
        ),
        GraphEdge(
            source_id="person_bob",
            target_id="team_platform",
            relation="member_of",
            provenance=doc_provenance,
        ),
        GraphEdge(
            source_id="person_carol",
            target_id="team_platform",
            relation="member_of",
            provenance=doc_provenance,
        ),
        GraphEdge(
            source_id="team_platform",
            target_id="project_db_migration",
            relation="works_on",
            provenance=doc_provenance,
        ),
    ]

    for edge in edges:
        # Need to attach edges to existing nodes
        node = await graph_store.get_node(edge.source_id)
        if node:
            await controller.store_fact(node, edge)

    print(f"Added {len(entities)} entities and {len(edges)} relationships to graph")

    # =========================================================================
    # Part 4: Session Management
    # =========================================================================
    print("\n[Part 4] Session Management")
    print("-" * 50)

    session_id = "advanced_demo_session"
    user_id = "user_demo"

    # Initialize a new session
    state = await assembler.initialize_session(session_id, user_id)
    print(f"Session initialized:")
    print(f"  Session ID: {state.session_id}")
    print(f"  User ID: {state.user_id}")
    print(f"  Turn count: {state.turn_count}")

    # Set scoped variables (personalization)
    state.set_var("user:name", "Demo User")
    state.set_var("user:role", "Product Manager")
    state.set_var("session:context", "learning about Platform team")
    state.set_var("app:environment", "development")

    print(f"\nScoped variables set:")
    for key, value in state.scoped_vars.items():
        print(f"  {key}: {value}")

    # =========================================================================
    # Part 5: Simulating Conversation
    # =========================================================================
    print("\n[Part 5] Conversation Simulation")
    print("-" * 50)

    # Simulate a multi-turn conversation
    conversations = [
        ("Who leads the Platform team?", "Alice Johnson leads the Platform team as Engineering Manager."),
        ("What projects are they working on?", "The Platform team is working on Database Migration, API Gateway, and Observability improvements."),
        ("Tell me about Bob's expertise.", "Bob Smith is a Senior Engineer who specializes in distributed systems and mentors junior engineers on database optimization."),
    ]

    turn_ids = []
    for user_msg, assistant_msg in conversations:
        turn = InteractionTurn(
            id=str(uuid.uuid4()),
            session_id=session_id,
            timestamp=datetime.now(),
            user_message=user_msg,
            assistant_message=assistant_msg,
        )
        await controller.add_turn(session_id, turn)
        turn_ids.append(turn.id)
        print(f"Turn {len(turn_ids)}:")
        print(f"  User: {user_msg}")
        print(f"  Assistant: {assistant_msg[:60]}...")

    # =========================================================================
    # Part 6: Token Budget Calculation
    # =========================================================================
    print("\n[Part 6] Token Budget Calculation")
    print("-" * 50)

    system_prompt = """You are a helpful assistant for the Platform team.
You have access to team documentation and can answer questions about
team members, processes, and ongoing projects.

Always be concise and cite your sources when possible."""

    # Calculate fixed costs
    fixed_cost = architect.calculate_fixed_costs(system_prompt)
    print(f"Fixed costs:")
    print(f"  System prompt: {architect.count_tokens(system_prompt)} tokens")
    print(f"  Output buffer: 1024 tokens")
    print(f"  Total fixed: {fixed_cost} tokens")

    # Calculate dynamic limit (available for context)
    dynamic_limit = architect.calculate_dynamic_limit(system_prompt)
    print(f"\nBudget allocation:")
    print(f"  Model max tokens: 8192")
    print(f"  Dynamic limit: {dynamic_limit} tokens (for context)")

    # =========================================================================
    # Part 7: Context Assembly
    # =========================================================================
    print("\n[Part 7] Context Assembly")
    print("-" * 50)

    with patch("friday_memory.adapters.vector.litellm", create_mock_litellm()):
        # Assemble context for a new query
        query = "What are the sprint practices for the Platform team?"

        payload = await assembler.assemble_context(
            query=query,
            state=state,
            budget_limit=dynamic_limit,
        )

        print(f"Context assembled for query: \"{query}\"")
        print(f"\nPayload contents:")
        print(f"  History turns: {len(payload.history)}")
        print(f"  Vector passages: {len(payload.passages)}")
        print(f"  Graph entities: {len(payload.entities)}")
        print(f"  Graph facts: {len(payload.facts)}")

    # =========================================================================
    # Part 8: Prompt Formatting
    # =========================================================================
    print("\n[Part 8] Prompt Formatting")
    print("-" * 50)

    # Format the final prompt using the layout engine
    messages = await assembler.format_prompt(
        system_prompt=system_prompt,
        payload=payload,
    )

    print(f"Generated {len(messages)} messages for LLM:")
    for i, msg in enumerate(messages):
        role = msg["role"]
        content_preview = msg["content"][:80].replace("\n", " ")
        print(f"  [{i + 1}] {role}: \"{content_preview}...\"")

    # Show full system prompt structure
    print(f"\nSystem prompt structure:")
    system_content = messages[0]["content"]
    sections = system_content.split("\n## ")
    print(f"  Sections: {len(sections)}")
    for section in sections[1:]:  # Skip the base prompt
        title = section.split("\n")[0]
        print(f"    - {title}")

    # =========================================================================
    # Part 9: Checkpoint and Rollback
    # =========================================================================
    print("\n[Part 9] Checkpoint and Rollback")
    print("-" * 50)

    # Check current state
    current_turns = await episodic_store.get_turn_count(session_id)
    print(f"Current state: {current_turns} turns in session")

    # Restore to an earlier checkpoint (turn 2)
    checkpoint_turn_id = turn_ids[1]
    restored_state = await assembler.restore_checkpoint(session_id, checkpoint_turn_id)

    print(f"Restored to checkpoint (turn 2):")
    print(f"  Turn count now: {restored_state.turn_count}")

    # Verify rollback
    new_turn_count = await episodic_store.get_turn_count(session_id)
    print(f"  Episodic store turns: {new_turn_count}")

    # =========================================================================
    # Part 10: Observability
    # =========================================================================
    print("\n[Part 10] Telemetry and Observability")
    print("-" * 50)

    # Review captured telemetry events
    print(f"Telemetry events captured: {len(telemetry.events)}")

    # Group events by type (events are EventRecord objects with .name and .data)
    event_types: dict[str, int] = {}
    for event in telemetry.events:
        event_name = event.name
        event_types[event_name] = event_types.get(event_name, 0) + 1

    print(f"\nEvent distribution:")
    for event_type, count in sorted(event_types.items()):
        print(f"  {event_type}: {count}")

    # Show spans if any
    if telemetry.spans:
        print(f"\nActive spans: {len(telemetry.spans)}")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 70)
    print("Advanced Example Complete!")
    print("=" * 70)
    print("""
What you've learned:

1. DOCUMENT INGESTION
   - Chunking documents with overlap for semantic search
   - Maintaining provenance through the pipeline

2. CONTEXT ASSEMBLY
   - ContextAssembler orchestrates the full workflow
   - Token budgeting with the "Knapsack" algorithm
   - Priority-based pruning when context exceeds budget

3. PROMPT ARCHITECTURE
   - PromptArchitect structures prompts for optimal attention
   - Layout: System -> Transparency -> Semantic -> Episodic -> Query
   - Fixed costs (system prompt, tools) vs dynamic content

4. SESSION MANAGEMENT
   - Session state with scoped variables (user:, session:, app:)
   - Checkpoint/restore for conversation rollback
   - Turn-by-turn history tracking

5. OBSERVABILITY
   - DebugTelemetryRecorder captures all operations
   - Span tracking for performance analysis
   - Event distribution for debugging

This pipeline powers production RAG systems with proper memory management,
token budgeting, and full observability.
""")

    # Cleanup
    doc_path.unlink()


if __name__ == "__main__":
    asyncio.run(main())
