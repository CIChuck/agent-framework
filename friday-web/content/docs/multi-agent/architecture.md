---
title: "Shared Memory Architecture"
description: "How multiple agents read and write to a common memory plane."
weight: 1
---

Multiple Friday agents can read from and write to a shared memory plane, enabling collaborative reasoning while maintaining provenance for every stored fact.

Friday's multi-agent architecture uses a fundamentally different approach than most frameworks: **all agents share the same memory controller**. When one agent writes to the knowledge graph, vector store, or transcript system, every other agent immediately sees those changes. This "shared intelligence plane, multiple control planes" design treats multiple agents as different personas accessing unified intelligence.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Friday Multi-Agent System                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │   Researcher   │  │     Coder      │  │    Reviewer    │   │
│  │                │  │                │  │                │   │
│  │  - web_search  │  │  - write_file  │  │  - read_file   │   │
│  │  - read_file   │  │  - execute_code│  │  - analyze_code│   │
│  │  - store_fact  │  │  - run_tests   │  │  - check_style │   │
│  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘   │
│           │                   │                   │            │
│           └───────────────────┼───────────────────┘            │
│                               │                                 │
│                               ▼                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │         Shared Memory Controller (Single Instance)     │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │  Episodic Memory   (SQLite Transcripts)               │   │
│  │  - All turns from all agents in one session history   │   │
│  │  - agent_id field tracks which agent responded        │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │  Semantic Memory   (ChromaDB Vectors)                  │   │
│  │  - Insights from all agents in shared collections     │   │
│  │  - Provenance metadata: source_agent="researcher"     │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │  Associative Memory (NetworkX Graph)                   │   │
│  │  - Entity graph built by all agents collectively      │   │
│  │  - Relationships track which agent discovered them    │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## How It Works

When the user says: `@researcher find information about Python async patterns`

1. **Orchestrator** receives the message and parses the `@researcher` routing prefix
2. **Researcher agent** is activated (or reused from cache if already instantiated)
3. **Memory retrieval** happens through the shared MemoryController:
   - Vector search pulls insights about "Python" and "async" from semantic memory
   - Graph traversal loads entities like `Entity(name="Python", type=Technology)`
   - Episodic memory provides recent conversation turns (regardless of which agent created them)
4. **Researcher executes** its turn using `web_search` and `read_file` tools
5. **Memory extraction** runs after the turn, adding:
   - New insights about async patterns to the vector store (tagged `source_agent="researcher"`)
   - New relationships to the graph (e.g., `Python --HAS_PATTERN--> AsyncIO`)
   - Turn record to transcripts (with `agent_id="researcher"`)

Later, when the user says: `@coder implement an async function based on what we learned`

1. **Orchestrator** switches to the coder agent (researcher is cached but inactive)
2. **Memory retrieval** happens through the **same** MemoryController:
   - Vector search finds the researcher's insights about async patterns
   - Graph traversal accesses the `Python --HAS_PATTERN--> AsyncIO` relationship
   - Episodic memory includes both researcher and coder turns in conversation history
3. **Coder executes** with full context of what the researcher discovered
4. **Memory extraction** adds the coder's contribution to the shared graph and vector store

**The Result:** The coder doesn't need explicit handoff of data from the researcher. It automatically sees the researcher's findings through normal memory retrieval. This eliminates the "context boundary" problem that plagues isolated-agent architectures.

---

## Provenance Tracking for Attribution

With multiple agents writing to shared memory, Friday uses **provenance metadata** to track the origin of every memory entry.

**Provenance Data Model:**

```python
class ProvenanceMetadata(BaseModel):
    """
    Tracks the origin and authorship of memory entries.

    Critical for multi-agent scenarios where multiple agents contribute
    to the shared knowledge base. Enables attribution, quality filtering,
    and debugging.
    """
    source: str = Field(
        ...,
        description="Origin type: 'conversation', 'tool', 'inference', 'ingestion'"
    )
    author: str | None = Field(
        default=None,
        description="Which agent created this memory (e.g., 'researcher', 'coder')"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When this memory was created"
    )
    confidence: float = Field(
        default=1.0,
        description="Confidence score (0-1) for extraction quality"
    )

    # Optional context
    session_id: str | None = Field(default=None)
    turn_id: str | None = Field(default=None)
    extraction_model: str | None = Field(
        default=None,
        description="Which LLM model performed extraction"
    )
```

**Provenance in Action:**

Every entity, relationship, and insight stored by Friday includes provenance:

```python
# Entity created by researcher agent
Entity(
    name="FastAPI",
    type=EntityType.TECHNOLOGY,
    description="Modern Python web framework",
    provenance=ProvenanceMetadata(
        source="conversation",
        author="researcher",  # Researcher discovered this
        confidence=0.9,
        session_id="sess_123",
        turn_id="turn_42"
    )
)

# Relationship created by coder agent
Relationship(
    source="FastAPI",
    target="AsyncIO",
    relationship_type="USES",
    context="FastAPI uses asyncio for async request handling",
    provenance=ProvenanceMetadata(
        source="tool",  # From code analysis tool
        author="coder",  # Coder discovered this relationship
        confidence=1.0
    )
)

# Insight created by reviewer agent
Insight(
    content="The async implementation follows best practices with proper exception handling",
    type=InsightType.OBSERVATION,
    provenance=ProvenanceMetadata(
        source="inference",  # From LLM reasoning
        author="reviewer",  # Reviewer's assessment
        confidence=0.85
    )
)
```

**Why Provenance Matters:**

1. **Attribution Clarity**: Know which agent contributed which knowledge
2. **Quality Filtering**: Trust insights from agents with relevant expertise more
3. **Debugging**: Trace back why Friday believes something to the originating agent and turn
4. **Confidence Weighting**: Combine provenance with confidence scores for retrieval ranking
5. **Audit Trails**: Track how knowledge evolved across multiple agents

**Example: Debugging Multi-Agent Confusion**

User reports: "Friday thinks Python is a snake, not a programming language."

```python
# Query graph for "Python" entity
entities = graph_store.get_entities(name="Python")

# Check provenance
for entity in entities:
    print(f"Entity: {entity.name}")
    print(f"  Type: {entity.type}")
    print(f"  Created by: {entity.provenance.author}")
    print(f"  Confidence: {entity.provenance.confidence}")
    print(f"  Turn: {entity.provenance.turn_id}")

# Output might reveal:
# Entity: Python
#   Type: ANIMAL
#   Created by: researcher  (Wrong context from web search)
#   Confidence: 0.6
#   Turn: turn_10

# Entity: Python
#   Type: TECHNOLOGY
#   Created by: coder  (Correct context from code analysis)
#   Confidence: 0.95
#   Turn: turn_15

# Solution: Use confidence and context to prefer the coder's version
```

Provenance enables **agent-specific trust models**: If the coder agent is more reliable for technology entities than the researcher, weight the coder's contributions higher during retrieval.

---

## Shared vs. Isolated Memory

**Shared Memory Benefits:**

1. **Zero Handoff Overhead**: Agents automatically see each other's work through normal retrieval
2. **Collective Learning**: All agents benefit from experiences of any agent
3. **Context Coherence**: Conversation history is seamless across agent switches
4. **Resource Efficiency**: Single memory store, not N replicated stores per agent
5. **Simplified State Management**: One source of truth, no state synchronization logic

**Shared Memory Tradeoffs:**

1. **Namespace Collision Risk**: Multiple agents might create conflicting entities (mitigated by provenance and confidence scoring)
2. **Permission Complexity**: Some agents might need read-only access to certain memories (requires access control layer)
3. **Memory Pollution**: A buggy agent can corrupt shared knowledge (mitigated by quality filtering and maintenance operations)

**When to Use Shared vs. Isolated Memory:**

| Scenario | Recommended Approach | Rationale |
|----------|---------------------|-----------|
| Collaborative team (researcher → analyst → reporter) | Shared Memory | Agents build on each other's work; handoff would be expensive |
| Independent specialists (legal bot, medical bot, finance bot) | Isolated Memory with Namespaces | Different domains; knowledge should not cross-pollinate |
| Multi-tenant system (agent per customer) | Isolated Memory per Tenant | Privacy and data isolation requirements |
| Experimental agents (testing new models) | Temporary Isolated Memory | Prevent untrusted agents from corrupting production knowledge |

**Friday's Default:** Shared memory with provenance for attribution and quality filtering. Use memory namespaces (via metadata filtering) when isolation is needed within the same memory store.

**Comparison to Other Frameworks:**

Other frameworks (isolated memory approach):
```python
# Each agent has its own memory store
researcher_memory = ConversationMemory()
coder_memory = ConversationMemory()

# Explicit handoff required
research_results = researcher.run("Find info")
coder_memory.add_message(f"Research results: {research_results}")  # Manual copy
coder_response = coder.run("Implement this")
```

Friday (shared memory approach):
```python
# Both agents use same MemoryController
orchestrator = AgentOrchestrator(registry, memory_controller)

# No explicit handoff needed
await orchestrator.process("@researcher find info")
await orchestrator.process("@coder implement this")
# Coder automatically retrieves researcher's findings through normal memory recall
```

**Key Insight:** Friday's architecture treats multi-agent coordination as a **memory retrieval problem**, not a **data passing problem**. This dramatically simplifies agent collaboration code.

---

## Memory Namespaces

Namespaces enable memory isolation or sharing within the same memory store infrastructure:

```yaml
# No namespace: All agents share the same memories
memory_config:
  namespace: null

# Team namespace: Research team members share memories
memory_config:
  namespace: "research_team"
  # All agents with namespace="research_team" share memories

# Agent namespace: Private memory per agent
memory_config:
  namespace: "agent_researcher"
  # Only this agent sees these memories
```

**Multi-Tenant Deployment with Namespaces:**

```yaml
# Agent profile template
name: customer_assistant
memory_config:
  namespace: "customer_{{customer_id}}"  # Isolated per customer
```

```python
# Runtime instantiation with customer context
profile = loader.load("customer_assistant")
profile.memory_config["namespace"] = f"customer_{customer_id}"

agent = CopilotAgent(
    profile=profile,
    memory=memory_controller,
    ...
)
```

---

## Related Pages

- [Orchestrator Patterns](/docs/multi-agent/orchestrator/) — Routing, delegation, and agent switching
- [Collaboration Patterns](/docs/multi-agent/patterns/) — Fan-out, pipeline, consensus, and critic-revisor
- [Agent Configuration](/docs/agents/configuration/) — Memory namespace and mode configuration
