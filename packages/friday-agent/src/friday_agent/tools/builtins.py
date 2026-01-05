"""
Built-in Tools for Friday Agents.

Core memory and scratchpad tools that agents can use
for information persistence and retrieval.

These tools require dependency injection for memory_controller
and session_state. Use registry.bind_dependency() to inject these
before agent execution.

Ref: Batch 3 Specification, Section 5.2
"""

import uuid
from typing import TYPE_CHECKING

from friday_agent.tools.registry import tool

if TYPE_CHECKING:
    from friday_memory import MemoryController, SessionState


@tool(
    name="scratchpad_write",
    description="Write a value to the agent's scratchpad. Use this to save important information that should survive context pruning.",
)
async def scratchpad_write(
    state: "SessionState",
    key: str,
    value: str,
) -> str:
    """
    Write a value to the agent's scratchpad.

    The scratchpad is a key-value store that persists for the session
    and survives context window pruning. Use it to save important
    intermediate results, insights, or information you'll need later.

    Args:
        state: The session state (injected via bind_dependency)
        key: The key to store the value under
        value: The value to store

    Returns:
        Confirmation message
    """
    # Use session scope for scratchpad values
    scoped_key = f"session:scratchpad:{key}"
    state.set_var(scoped_key, value)
    return f"Saved '{key}' to scratchpad"


@tool(
    name="scratchpad_read",
    description="Read a value from the agent's scratchpad. Retrieves previously saved information.",
)
async def scratchpad_read(
    state: "SessionState",
    key: str,
) -> str:
    """
    Read a value from the agent's scratchpad.

    Retrieves information previously stored with scratchpad_write.

    Args:
        state: The session state (injected via bind_dependency)
        key: The key to retrieve

    Returns:
        The stored value, or an error message if not found
    """
    scoped_key = f"session:scratchpad:{key}"
    value = state.get_var(scoped_key)

    if value is not None:
        return str(value)
    else:
        return f"No value found for key '{key}' in scratchpad"


@tool(
    name="recall_memory",
    description="Search the agent's long-term memory for relevant information. Use this when you need to remember something from past conversations or stored knowledge.",
)
async def recall_memory(
    memory: "MemoryController",
    query: str,
    limit: int = 5,
) -> str:
    """
    Search the agent's memory for relevant information.

    Queries the vector store, graph store, and episodic memory
    for information relevant to the query.

    Args:
        memory: The memory controller (injected via bind_dependency)
        query: What to search for
        limit: Maximum number of results to return

    Returns:
        Formatted string of relevant memories, or message if none found
    """
    # Use memory controller's recall method
    payload = await memory.recall(
        query=query,
        include_history=False,  # Don't include current session history
        vector_results=limit,
        graph_depth=1,
    )

    results = []

    # Add vector store passages
    for passage in payload.passages[:limit]:
        text = passage.get("text", passage.get("content", ""))
        if text:
            # Truncate long passages
            truncated = text[:300] + "..." if len(text) > 300 else text
            results.append(f"- {truncated}")

    # Add graph entities if found
    for entity in payload.entities[:3]:
        results.append(f"- Entity: {entity.label} (type: {entity.type})")

    # Add facts if found
    for fact in payload.facts[:3]:
        results.append(f"- Fact: {fact.relation}")

    if results:
        return "Relevant memories:\n" + "\n".join(results)
    else:
        return "No relevant memories found for this query."


@tool(
    name="store_fact",
    description="Explicitly store a fact in the knowledge graph. Use this when you learn something important that should be remembered long-term.",
)
async def store_fact(
    memory: "MemoryController",
    subject: str,
    predicate: str,
    object: str,
    confidence: float = 1.0,
) -> str:
    """
    Store a fact in the knowledge graph.

    Creates nodes for subject and object, and an edge representing
    their relationship.

    Args:
        memory: The memory controller (injected via bind_dependency)
        subject: The subject of the fact (e.g., "Alice")
        predicate: The relationship (e.g., "works_at")
        object: The object of the fact (e.g., "Acme Corp")
        confidence: Confidence score for this fact (0.0 to 1.0)

    Returns:
        Confirmation message
    """
    from friday_memory.models import GraphEdge, GraphNode, ProvenanceMetadata

    # Create provenance metadata
    provenance = ProvenanceMetadata(
        source_id="agent_explicit_tool",
        source_type="tool",
        confidence=confidence,
        author_id="agent",
    )

    # Create subject node
    subject_node = GraphNode(
        id=str(uuid.uuid4()),
        type="entity",
        label=subject,
        provenance=provenance,
    )

    # Create object node
    object_node = GraphNode(
        id=str(uuid.uuid4()),
        type="entity",
        label=object,
        provenance=provenance,
    )

    # Create edge
    edge = GraphEdge(
        source_id=subject_node.id,
        target_id=object_node.id,
        relation=predicate,
        provenance=provenance,
    )

    # Store in graph
    await memory.store_fact(subject_node)
    await memory.store_fact(object_node, edge)

    return f"Stored fact: {subject} {predicate} {object}"


@tool(
    name="scratchpad_list",
    description="List all keys currently stored in the scratchpad.",
)
async def scratchpad_list(
    state: "SessionState",
) -> str:
    """
    List all keys in the scratchpad.

    Args:
        state: The session state (injected via bind_dependency)

    Returns:
        Comma-separated list of keys, or message if empty
    """
    prefix = "session:scratchpad:"
    keys = [
        k[len(prefix):]
        for k in state.scoped_vars.keys()
        if k.startswith(prefix)
    ]

    if keys:
        return f"Scratchpad keys: {', '.join(keys)}"
    else:
        return "Scratchpad is empty"


@tool(
    name="scratchpad_clear",
    description="Clear all values from the scratchpad.",
)
async def scratchpad_clear(
    state: "SessionState",
) -> str:
    """
    Clear all scratchpad values.

    Args:
        state: The session state (injected via bind_dependency)

    Returns:
        Confirmation message with count of cleared items
    """
    prefix = "session:scratchpad:"
    keys_to_delete = [
        k for k in state.scoped_vars.keys()
        if k.startswith(prefix)
    ]

    for key in keys_to_delete:
        state.delete_var(key)

    return f"Cleared {len(keys_to_delete)} items from scratchpad"
