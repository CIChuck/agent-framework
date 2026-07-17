# Friday Agent Framework
## Adaptive Memory: The Heart of Friday

**Version:** 1.0
**Framework Version:** v0.1.0
**Last Updated:** 2026-01-24

---

## Overview

Memory is what separates Friday from stateless AI assistants. While most systems either have no memory or simple chat history, Friday implements a **three-tier memory architecture** inspired by cognitive science that genuinely learns and adapts over time.

This section provides a comprehensive deep dive into Friday's memory system—how it's structured, how it evolves, and how it powers Friday's ability to build understanding across days, weeks, or months of interactions.

**For Project Leaders:** Understand how Friday's memory creates compound value over time, making your AI investment increasingly effective. Learn why this architecture provides strategic differentiation and how it enables genuinely adaptive AI systems.

**For IT Leaders:** Get the technical details on memory storage, retrieval performance, lifecycle management, and operational considerations for running memory-intensive AI agents at scale.

**For Users:** Learn how to design effective agent interactions, understand what Friday remembers and why, and troubleshoot memory-related issues with confidence.

---

## 4.1 Three-Tier Memory Architecture

### Cognitive Science Foundation

Friday's memory architecture is inspired by human memory systems identified in cognitive psychology:

1. **Episodic Memory** - Autobiographical events ("I had lunch with Alice yesterday")
2. **Semantic Memory** - Factual knowledge ("Python is a programming language")
3. **Associative Memory** - Conceptual relationships ("Alice prefers Python for web development")

These aren't just storage categories—they represent fundamentally different ways of organizing and retrieving information. Friday implements all three to mirror how humans naturally remember and reason.

### The Three Stores

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRIDAY MEMORY SYSTEM                       │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐ │
│  │   EPISODIC      │  │    SEMANTIC     │  │  ASSOCIATIVE   │ │
│  │   (SQLite)      │  │   (ChromaDB)    │  │  (NetworkX)    │ │
│  │                 │  │                 │  │                │ │
│  │ Conversation    │  │ Insights &      │  │ Entities &     │ │
│  │ History         │  │ Facts           │  │ Relationships  │ │
│  │                 │  │                 │  │                │ │
│  │ "What was said" │  │ "What was       │  │ "How things    │ │
│  │                 │  │  learned"       │  │  connect"      │ │
│  │                 │  │                 │  │                │ │
│  │ Time-ordered    │  │ Embedding-      │  │ Graph-based    │ │
│  │ Retrieval       │  │ based Search    │  │ Traversal      │ │
│  └─────────────────┘  └─────────────────┘  └────────────────┘ │
│         │                      │                     │          │
│         └──────────────┬───────┴─────────────────────┘          │
│                        │                                        │
│                ┌───────▼────────┐                               │
│                │ Memory         │                               │
│                │ Controller     │                               │
│                │ (Unified API)  │                               │
│                └────────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

### 4.1.1 Episodic Memory: The Conversation Log

**Purpose:** Store the raw, chronological record of conversations—the "what happened, when, and how" of every interaction.

**Implementation:** SQLite database via `TranscriptStoreAdapter`

**Data Model:**
```python
Turn:
  - id: Unique turn identifier
  - session_id: Which conversation session
  - user_id: Which user
  - timestamp: When the turn occurred
  - user_message: What the user said
  - assistant_message: How Friday responded
  - tool_calls: List of tools executed (with parameters)
  - tool_results: Results from tool execution
  - token_usage: Prompt tokens, completion tokens, total
  - latency_ms: Response time
  - model_name: Which LLM was used
  - provenance: Which agent (if multi-agent)
```

**Retrieval Pattern:** Time-ordered, session-scoped
```python
# Get last N turns for context
recent_turns = await controller.get_recent_turns(
    session_id="current_session",
    limit=10  # Last 10 turns
)
```

**Use Cases:**
- **Conversation continuity**: Reference what was said 3 turns ago
- **Debugging**: Trace exact request/response pairs
- **Audit trails**: Complete record of all interactions
- **Training data**: Export conversations for fine-tuning
- **Context assembly**: Include recent history in LLM prompts

**Storage Characteristics:**
- **Size**: ~1-5KB per turn (depends on response length, tool calls)
- **Growth**: Linear with conversation volume
- **Retention**: Permanent (no automatic deletion, archive manually)
- **Performance**: Fast retrieval by session_id + timestamp index

**Example:**
```sql
-- Episodic memory schema
CREATE TABLE turns (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    user_message TEXT,
    assistant_message TEXT,
    tool_calls JSON,
    tool_results JSON,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    latency_ms INTEGER,
    model_name TEXT,
    provenance TEXT
);

CREATE INDEX idx_session_timestamp ON turns(session_id, timestamp);
```

**Why SQLite?**
- **Serverless**: No database daemon required
- **Embedded**: Single file, easy backup/restore
- **ACID compliant**: Transactional safety for conversation logs
- **Fast for reads**: Indexed queries are microseconds
- **Portable**: Works on any platform Python runs on
- **Swappable**: Implement `TranscriptStoreAdapter` for PostgreSQL/MySQL/MongoDB if needed

**For Project Leaders:**
- Complete audit trail for compliance (HIPAA, GDPR, SOC 2)
- Training data accumulation for custom model fine-tuning
- Product analytics (what features users ask about, where they struggle)
- ROI measurement (track agent effectiveness over time)

**For IT Leaders:**
- Simple backup strategy (copy SQLite file)
- No additional infrastructure (no database server)
- Easy to replicate for testing (clone database file)
- Can migrate to SQL server (PostgreSQL) if scaling requires it

**For Users:**
- Use `/transcript` command to see full conversation history
- Export with `/export jsonl` for analysis
- Debug with `/history` to see recent turns

### 4.1.2 Semantic Memory: The Knowledge Vault

**Purpose:** Store conceptual knowledge extracted from conversations as searchable embeddings—the "what was learned" layer.

**Implementation:** ChromaDB (vector database) via `VectorStoreAdapter`

**Data Model:**
```python
Document (Insight/Fact):
  - id: Unique identifier
  - content: Text of the insight
  - embedding: 1536-dimensional vector (OpenAI ada-002 default)
  - metadata:
      - type: "insight" | "summary" | "meta_insight"
      - confidence: 0.0-1.0
      - created_at: Timestamp
      - turn_id: Source conversation turn
      - collection: "short_term" | "long_term" | "decayed"
      - provenance: Which agent extracted it
      - tags: List of topic tags
      - access_count: Retrieval frequency
      - last_accessed: Most recent access timestamp
```

**Retrieval Pattern:** Similarity search (embedding-based)
```python
# Find relevant insights for current query
results = await vector_store.similarity_search(
    query="web API development in Python",
    limit=10,
    threshold=0.7,  # Minimum cosine similarity
    collection="long_term"  # Search long-term memories
)
```

**Multi-Collection Architecture:**

Friday uses **three collections** to implement lifecycle stages:

```
memories_short_term/
  ├─ Recently extracted insights (age < 24h)
  ├─ Unproven, tentative knowledge
  ├─ Higher retrieval threshold (0.75 similarity)
  └─ Candidates for promotion

memories_long_term/
  ├─ Promoted, validated insights (age > 24h, high access)
  ├─ Core agent knowledge
  ├─ Lower retrieval threshold (0.65 similarity)
  └─ Most relevant for context

memories_decayed/
  ├─ Unused memories (no access in > 7 days)
  ├─ "Forgotten" but recoverable
  ├─ Highest retrieval threshold (0.80 similarity)
  └─ Candidates for deletion
```

**Why separate collections?**
- **Precision control**: Long-term memories use lower threshold (retrieve more) because they're validated
- **Performance optimization**: Query long-term first (most relevant), fall back to short-term if needed
- **Lifecycle visibility**: Easy to see distribution across stages
- **Soft deletion**: Decayed memories remain searchable, can be reactivated

**Embedding Models:**

Friday supports multiple embedding models:

| Model | Dimensions | Cost | Use Case |
|-------|-----------|------|----------|
| **text-embedding-3-small** (OpenAI) | 1536 | $0.02/1M tokens | Default, good balance |
| **text-embedding-3-large** (OpenAI) | 3072 | $0.13/1M tokens | Higher quality, more expensive |
| **nomic-embed-text-v1.5** (local) | 768 | Free (local) | Privacy-sensitive, offline |
| **voyage-2** (Voyage AI) | 1024 | $0.12/1M tokens | Specialized for retrieval |

**Example Insights:**
```json
{
  "id": "insight_abc123",
  "content": "User prefers FastAPI over Flask for Python web API development due to automatic documentation and type safety",
  "embedding": [0.023, -0.145, 0.891, ...],  // 1536 dimensions
  "metadata": {
    "type": "preference",
    "confidence": 0.92,
    "created_at": "2026-01-20T15:30:00Z",
    "turn_id": "turn_xyz789",
    "collection": "long_term",
    "provenance": "copilot_agent_1",
    "tags": ["python", "web_api", "fastapi"],
    "access_count": 12,
    "last_accessed": "2026-01-24T09:15:00Z"
  }
}
```

**Use Cases:**
- **Preference learning**: Remember what user likes/dislikes
- **Pattern recognition**: Identify recurring themes or topics
- **Decision context**: Recall relevant past decisions when making new ones
- **Cross-conversation continuity**: Find related insights from months ago
- **Recommendation**: Suggest actions based on learned patterns

**Storage Characteristics:**
- **Size**: ~6KB per insight (1536 floats + metadata + text)
- **Growth**: Slower than episodic (only extracts insights, not every turn)
- **Retention**: Lifecycle-managed (short → long → decayed → deleted)
- **Performance**: Similarity search ~50-200ms for 10K documents

**Similarity Search Explained:**

When you ask: "What should I use for web APIs in Python?"

1. **Embedding generation**: Query → vector [0.112, -0.034, 0.789, ...]
2. **Cosine similarity**: Compare query vector to all insight vectors
3. **Ranking**: Sort by similarity score (0-1, higher = more similar)
4. **Threshold filtering**: Only return results above threshold (0.7)
5. **Limit**: Return top N results (default 10)

**Mathematical formula:**
```
similarity(A, B) = (A · B) / (||A|| × ||B||)
where:
  A · B = dot product (sum of element-wise multiplication)
  ||A|| = magnitude (sqrt of sum of squares)
```

**Result:** Semantically relevant insights even if keywords don't match exactly

**For Project Leaders:**
- Accumulates institutional knowledge over time (compound learning effect)
- Enables personalization without fine-tuning (cheaper, faster to implement)
- Privacy-friendly learning (can use local embeddings, no data sent to cloud)
- Measurable knowledge growth (track insight count, diversity over time)

**For IT Leaders:**
- Scales well (ChromaDB handles millions of vectors)
- Can swap to enterprise vector DB (Pinecone, Weaviate, pgvector)
- Resource requirements: ~1GB RAM per 100K insights
- GPU optional but helps for local embeddings (2-5x faster)

**For Users:**
- Use `/facts` to see all insights
- Use `/insights` to filter by type (preference, observation, decision)
- Check collection with `/lifecycle --stats`
- Test retrieval with queries to see what Friday "remembers"

### 4.1.3 Associative Memory: The Knowledge Graph

**Purpose:** Model entities (people, projects, technologies) and their relationships—the "how things connect" layer.

**Implementation:** NetworkX (graph library) + JSON persistence via `GraphStoreAdapter`

**Data Model:**
```python
Entity (Node):
  - name: "Alice" | "FastAPI" | "Python"
  - type: Person | Technology | Project | Concept
  - description: Human-readable explanation
  - hit_count: Access frequency (Hebbian learning)
  - created_at: When first mentioned
  - last_accessed: Most recent reference
  - metadata: Additional attributes (job title, version, etc.)

Relationship (Edge):
  - source: Entity name (start node)
  - verb: Semantic relationship type
  - target: Entity name (end node)
  - context: Supporting information
  - confidence: 0.0-1.0
  - hit_count: Relationship access frequency
  - created_at: When relationship established
  - last_accessed: Most recent traversal
```

**Semantic Relationship Verbs:**

Friday uses **typed relationships** with semantic meaning:

| Category | Verbs | Example |
|----------|-------|---------|
| **Ownership** | OWNS, HAS, MANAGES | User OWNS project_x |
| **Action** | USES, WORKING_ON, LEARNING, BUILT | Alice USES Python |
| **Preference** | PREFERS, LIKES, DISLIKES, AVOIDS | User PREFERS FastAPI OVER Flask |
| **Attribution** | AUTHORED, CREATED, DESIGNED | Alice AUTHORED library_y |
| **Association** | RELATED_TO, MEMBER_OF, PART_OF | FastAPI RELATED_TO Python |
| **Dependency** | DEPENDS_ON, REQUIRES, BASED_ON | project_x DEPENDS_ON library_y |
| **Social** | COLLABORATES_WITH, REPORTS_TO, KNOWS | Alice COLLABORATES_WITH Bob |

**Why typed relationships?**
- **Semantic queries**: "What does Alice PREFER?" vs. generic "What's Alice connected to?"
- **Inference**: If A DEPENDS_ON B and B DEPENDS_ON C, then A DEPENDS_ON C (transitive)
- **Natural language**: Relationships map to sentence structure ("Alice USES Python" reads naturally)

**Graph Structure:**

```
     Alice (Person, hit_count=47)
        │
        ├─[WORKING_ON]──► project_x (Project, hit_count=23)
        │                     │
        │                     └─[USES]──► FastAPI (Technology, hit_count=89)
        │                                     │
        ├─[PREFERS]──────────────────────────┘
        │                                     │
        │                                     └─[BASED_ON]──► Python (hit_count=156)
        │                                                         ▲
        └─[LEARNING]─────────────────────────────────────────────┘
```

**Hebbian Learning:**

The hit_count field implements **"neurons that fire together, wire together"**:

```python
# Every time an entity is accessed (retrieved for context, mentioned in conversation)
entity.hit_count += 1
entity.last_accessed = datetime.now()

# Over time, frequently-accessed entities naturally become more "important"
# High hit_count → Higher retrieval priority
```

**Why Hebbian learning matters:**
- **Emergent importance**: No manual curation needed—usage defines importance
- **Adaptive prioritization**: Entity importance shifts as focus changes
- **Forgetting mechanism**: Entities with low hit_count can be pruned
- **Cognitive fidelity**: Mimics how human memory strengthens with repetition

**Retrieval Patterns:**

**1. Entity Lookup:**
```python
# Get all information about an entity
entity = graph_store.get_entity("Alice")
# Returns: type, description, hit_count, all relationships
```

**2. Relationship Query:**
```python
# What technologies does Alice use?
tech = graph_store.query_relationships(
    source="Alice",
    verb="USES",
    target_type="Technology"
)
# Returns: ["Python", "FastAPI", "Git"]
```

**3. Multi-Hop Traversal:**
```python
# Find projects that use Python (2-hop: Project → USES → Technology)
projects = graph_store.find_paths(
    start_type="Project",
    relationship_chain=["USES"],
    end_entity="Python",
    max_depth=2
)
# Returns: All projects connected to Python via USES relationship
```

**4. Priming (Session Initialization):**
```python
# Load most important entities by Hebbian hit_count
top_entities = graph_store.get_top_entities(
    limit=10,  # Top 10 most accessed
    min_hit_count=5  # Only entities accessed at least 5 times
)
# Used to prime context at session start
```

**Example Graph Queries:**

**Q: "What projects has Alice worked on with Python?"**
```python
# Multi-condition query
projects = graph_store.query(
    source="Alice",
    verb="WORKING_ON",
    target_type="Project",
    then_traverse=[
        ("USES", "Python")  # Project must also USE Python
    ]
)
```

**Q: "Who has collaborated with Alice?"**
```python
# Bidirectional relationship
collaborators = graph_store.query_relationships(
    source="Alice",
    verb="COLLABORATES_WITH",
    bidirectional=True  # Check both Alice→X and X→Alice
)
```

**Q: "What does Alice prefer?"**
```python
# Typed relationship query
preferences = graph_store.query_relationships(
    source="Alice",
    verb="PREFERS",
    return_details=True  # Include context and confidence
)
```

**Use Cases:**
- **Entity-centric retrieval**: "Recall everything about Alice"
- **Relationship inference**: Deduce new facts from existing connections
- **Topic clustering**: Find related concepts through graph traversal
- **Importance ranking**: Prioritize context by Hebbian hit_count
- **Knowledge organization**: Structure understanding in human-readable form

**Storage Characteristics:**
- **Size**: ~500 bytes per entity, ~300 bytes per relationship
- **Growth**: Slower than episodic (entities are deduplicated, not per-turn)
- **Retention**: Permanent with optional pruning (low hit_count entities can be removed)
- **Performance**: Graph queries ~10-50ms for graphs with <10K entities

**Persistence Format (JSON):**
```json
{
  "entities": {
    "Alice": {
      "type": "Person",
      "description": "User working on Python web development",
      "hit_count": 47,
      "created_at": "2026-01-15T10:00:00Z",
      "last_accessed": "2026-01-24T14:30:00Z",
      "metadata": {"role": "developer"}
    },
    "FastAPI": {
      "type": "Technology",
      "description": "Python web framework for APIs",
      "hit_count": 89,
      "created_at": "2026-01-15T11:00:00Z",
      "last_accessed": "2026-01-24T14:30:00Z",
      "metadata": {"version": "0.109.0"}
    }
  },
  "relationships": [
    {
      "source": "Alice",
      "verb": "USES",
      "target": "FastAPI",
      "context": "For building production APIs",
      "confidence": 0.95,
      "hit_count": 12,
      "created_at": "2026-01-15T11:05:00Z",
      "last_accessed": "2026-01-24T14:30:00Z"
    }
  ]
}
```

**Why NetworkX + JSON?**
- **Lightweight**: No graph database server required (like SQLite for graphs)
- **Fast for small-medium graphs**: <10K entities is common for personal agents
- **Python-native**: NetworkX integrates seamlessly with Python code
- **Swappable**: Implement `GraphStoreAdapter` for Neo4j/ArangoDB when scaling beyond 100K entities
- **Inspectable**: JSON file is human-readable for debugging

**For Project Leaders:**
- Knowledge graph becomes strategic asset (accumulated understanding of domain)
- Entity-centric retrieval enables sophisticated AI reasoning
- Relationship data supports inference (deduce unstated facts)
- Visual representation possible (export to visualization tools)

**For IT Leaders:**
- Can migrate to Neo4j/ArangoDB when graph exceeds 100K entities
- NetworkX supports graph algorithms (PageRank, community detection)
- JSON persistence is backup-friendly (simple file copy)
- Graph pruning strategies available for memory management

**For Users:**
- Use `/entities` to see knowledge graph
- Check hit_count to understand what Friday considers important
- Relationships explain "why" Friday made connections
- Graph queries enable powerful memory retrieval

### How the Three Stores Work Together

**Complementary Retrieval:**

```
User Query: "What did I say about Python web frameworks last week?"

1. EPISODIC (Time-based):
   └─ Search turns from last week → Find conversation mentioning "Python web frameworks"

2. SEMANTIC (Content-based):
   └─ Similarity search for "Python web frameworks" → Retrieve insights about FastAPI, Flask preferences

3. ASSOCIATIVE (Relationship-based):
   └─ Find entities: "Python", "FastAPI", "Flask"
   └─ Traverse relationships: User PREFERS FastAPI, FastAPI USED_FOR web APIs

Result: Rich context combining chronological record (episodic),
        conceptual knowledge (semantic), and structured relationships (associative)
```

**Example: Context Assembly for "Should I use FastAPI or Flask?"**

**From Episodic:**
```
Turn 15 (2 days ago): "I'm building a web API"
Turn 16 (2 days ago): "FastAPI has great documentation"
Turn 17 (2 days ago): "Flask seems simpler but less features"
```

**From Semantic:**
```
Insight 1 (confidence 0.92): "User prefers FastAPI over Flask for production APIs"
Insight 2 (confidence 0.85): "User values automatic documentation and type safety"
Insight 3 (confidence 0.78): "User is building a REST API with authentication"
```

**From Associative:**
```
User -[PREFERS]-> FastAPI
User -[WORKING_ON]-> web_api_project
web_api_project -[USES]-> Python
FastAPI -[BASED_ON]-> Python
Flask -[ALTERNATIVE_TO]-> FastAPI
```

**Assembled Context:**
Friday can now respond with personalized, contextual advice:
- Knows user has expressed preference for FastAPI (semantic + associative)
- Recalls the specific conversation about documentation (episodic)
- Understands the connection between user's project and framework choice (associative)
- Confidence in recommendation because insight has high confidence score (semantic metadata)

**This is the power of three-tier memory: comprehensive, contextual, and connected.**

---

## 4.2 Memory Lifecycle Management

### The Four Stages: A Memory's Journey

Friday's semantic memories (insights and facts in the vector store) don't remain static—they evolve through a **lifecycle** based on usage patterns and age. This mimics how human memory works: frequently-accessed information strengthens, while unused information fades but remains recoverable.

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY LIFECYCLE                         │
│                                                             │
│   EXTRACTION          SHORT-TERM          LONG-TERM         │
│       │                  │                   │              │
│       ▼                  ▼                   ▼              │
│   [New Insight] ──► [24h + access] ──► [Validated]        │
│                         │                   │              │
│                         │                   │              │
│                         ▼                   ▼              │
│                    [No access]         [No access]         │
│                         │                   │              │
│                         ▼                   ▼              │
│                     [DECAYED]          [DECAYED]           │
│                         │                   │              │
│                         │                   │              │
│                    ┌────┴────┐         ┌────┴────┐         │
│                    │         │         │         │         │
│                    ▼         ▼         ▼         ▼         │
│              [REACTIVATED] [DELETED] [REACTIVATED] [DELETED]│
│                    │                   │                    │
│                    └───────────────────┘                    │
│                            │                                │
│                            ▼                                │
│                      [LONG-TERM]                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Stage Definitions

**1. SHORT-TERM** (`memories_short_term` collection)
- **Entry condition**: Newly extracted from conversation
- **Characteristics**:
  - Age < 24 hours (configurable)
  - Unproven, tentative knowledge
  - Higher similarity threshold for retrieval (0.75)
  - Awaiting validation through access patterns
- **Exit conditions**:
  - **Promotion → LONG-TERM**: High access + minimum age
  - **Decay → DECAYED**: No access for threshold period

**2. LONG-TERM** (`memories_long_term` collection)
- **Entry condition**: Promoted from short-term OR reactivated from decayed
- **Characteristics**:
  - Age > 24 hours AND high access frequency
  - Validated, core knowledge
  - Lower similarity threshold (0.65) - easier retrieval
  - Most relevant for context assembly
- **Exit condition**:
  - **Decay → DECAYED**: No access for extended period (7+ days)

**3. DECAYED** (`memories_decayed` collection)
- **Entry condition**: No access for threshold period from short-term or long-term
- **Characteristics**:
  - "Forgotten" but not deleted
  - Highest similarity threshold (0.80) - hard to retrieve
  - Soft-deleted pattern (recoverable)
  - Candidates for permanent deletion
- **Exit conditions**:
  - **Reactivation → LONG-TERM**: Accessed again (proves relevance)
  - **Deletion**: Manual cleanup or 30+ days in decayed state

**4. DELETED** (Removed from store)
- **Entry condition**: Manual deletion OR automated cleanup after retention period
- **Characteristics**:
  - Permanently removed from vector store
  - Cannot be recovered
  - Frees storage space and improves search performance

### Promotion: Short-Term → Long-Term

**Goal:** Identify valuable memories that deserve permanent storage.

**Promotion Scoring Algorithm:**

Memories are evaluated using a **multi-factor scoring function**:

```python
def calculate_promotion_score(memory: Insight) -> float:
    """
    Calculate promotion score (0.0-1.0) for a short-term memory.

    Score ≥ 0.7 AND age ≥ 24h → Promote to long-term
    """
    # Factor 1: Age (20% weight)
    # Older memories in short-term are more proven
    age_hours = (now() - memory.created_at).total_seconds() / 3600
    age_score = min(age_hours / 72, 1.0)  # Max score at 72 hours
    age_factor = age_score * 0.20

    # Factor 2: Access Frequency (40% weight)
    # More accessed = more valuable
    access_score = min(memory.access_count / 10, 1.0)  # Max score at 10 accesses
    access_factor = access_score * 0.40

    # Factor 3: Confidence (20% weight)
    # High extraction confidence = more trustworthy
    confidence_factor = memory.confidence * 0.20

    # Factor 4: Graph Connections (20% weight)
    # Memories connected to entities are more valuable
    connection_count = count_related_entities(memory)
    connection_score = min(connection_count / 5, 1.0)  # Max score at 5 connections
    connection_factor = connection_score * 0.20

    # Total promotion score
    return age_factor + access_factor + confidence_factor + connection_factor
```

**Promotion Criteria:**
1. **Promotion score ≥ 0.7** (default threshold)
2. **Age ≥ 24 hours** (minimum time in short-term)

**Why both conditions?**
- **Score threshold**: Ensures quality (don't promote low-value memories)
- **Age threshold**: Prevents premature promotion (let usage patterns emerge)

**Example Scenarios:**

**Scenario A: Quick Promotion (2 days)**
```
Insight: "User prefers FastAPI over Flask"
- Age: 48 hours → age_score = 0.67 → age_factor = 0.13
- Access count: 8 → access_score = 0.8 → access_factor = 0.32
- Confidence: 0.92 → confidence_factor = 0.18
- Connections: 4 (FastAPI, Flask, Python, User) → connection_factor = 0.16

Total score: 0.13 + 0.32 + 0.18 + 0.16 = 0.79 ✓ PROMOTE
```

**Scenario B: No Promotion (Low Access)**
```
Insight: "Weather was nice today"
- Age: 48 hours → age_factor = 0.13
- Access count: 0 → access_factor = 0.00
- Confidence: 0.65 → confidence_factor = 0.13
- Connections: 1 → connection_factor = 0.04

Total score: 0.13 + 0.00 + 0.13 + 0.04 = 0.30 ✗ DO NOT PROMOTE
```

**Scenario C: High Confidence, Low Usage**
```
Insight: "User mentioned project deadline in 3 months"
- Age: 30 hours → age_factor = 0.08
- Access count: 1 → access_factor = 0.04
- Confidence: 0.95 → confidence_factor = 0.19
- Connections: 2 → connection_factor = 0.08

Total score: 0.08 + 0.04 + 0.19 + 0.08 = 0.39 ✗ DO NOT PROMOTE (yet)
```

### Decay: Long-Term → Decayed

**Goal:** Identify unused memories to free up retrieval "attention" for more relevant content.

**Decay Algorithm:**

Friday uses **exponential decay** modeled after the Ebbinghaus forgetting curve:

```python
def calculate_decay_score(memory: Insight, lambda_decay: float = 0.01) -> float:
    """
    Calculate current memory strength using exponential decay.

    Score < 0.5 → Decay to decayed collection
    """
    # Time since last access (in hours)
    hours_since_access = (now() - memory.last_accessed).total_seconds() / 3600

    # Exponential decay formula
    decay_score = memory.initial_score * exp(-lambda_decay * hours_since_access)

    return decay_score
```

**Decay Formula:**
```
score(t) = score₀ × e^(-λt)

where:
  score₀ = initial score (typically 1.0 for long-term memories)
  λ = decay rate (default 0.01)
  t = hours since last access
  e = Euler's number (2.71828...)
```

**Decay Rates at λ=0.01:**
| Time Since Access | Remaining Score | % Retained |
|-------------------|-----------------|------------|
| 24 hours | 0.79 | 79% |
| 48 hours | 0.62 | 62% |
| 72 hours | 0.49 | 49% |
| 1 week (168h) | 0.19 | 19% |
| 2 weeks | 0.04 | 4% |

**Decay threshold:** When `score(t) < 0.5`, memory moves to decayed collection.

**Why exponential decay?**
- **Cognitive fidelity**: Matches human forgetting curves (Ebbinghaus, 1885)
- **Gradual forgetting**: Memories don't suddenly become irrelevant—they fade over time
- **Configurable**: Adjust λ for different retention behaviors

**Configurable Decay Rates:**

```yaml
# config.yaml
memory:
  lifecycle:
    decay_rate: 0.01  # Default: ~49% after 72h

    # Alternative configurations:
    # Fast decay (temporary task memory)
    # decay_rate: 0.05  # ~49% after 14h

    # Slow decay (learned preferences)
    # decay_rate: 0.001  # ~49% after 30 days
```

**Per-Type Decay (Advanced):**
```yaml
memory:
  lifecycle:
    decay_policies:
      preference: 0.001   # Slow decay - preferences are stable
      observation: 0.01   # Normal decay
      task: 0.05          # Fast decay - tasks are temporary
```

### Reactivation: Decayed → Long-Term

**Goal:** Recover "forgotten" memories when they become relevant again.

**The Soft-Delete Pattern:**

Friday never permanently deletes memories until explicitly confirmed. Decayed memories remain in the vector store, just with a higher retrieval threshold (0.80 vs. 0.65 for long-term).

**Reactivation Trigger:**
```python
if memory in decayed_collection and memory.similarity > 0.80:
    # Memory accessed despite being decayed → proves relevance
    memory.move_to(long_term_collection)
    memory.access_count += 1
    memory.last_accessed = now()
    memory.decay_score = 1.0  # Reset decay
```

**Reactivation Scenario:**

**Timeline:**
```
Day 1: User mentions "I'm interested in GraphQL"
        → Insight extracted: "User interested in GraphQL"
        → Short-term collection

Day 3: Insight promoted to long-term (high access during research)

Day 10: No GraphQL mentions for a week
         → Decay score = 0.49
         → Moved to decayed collection

Day 45: User asks "What was that API technology I was looking at?"
         → Semantic search: "API technology" → GraphQL insight found (sim=0.83)
         → Reactivated to long-term
         → Friday responds: "You were interested in GraphQL for APIs"
```

**Why reactivation matters:**
- **No premature deletion**: Prevents losing valuable memories permanently
- **Context-driven recovery**: Memories return when contextually relevant
- **Adaptive retention**: System learns what's important through repeated reactivation

### Lifecycle Operations

**Automatic Lifecycle (Default):**
```yaml
memory:
  lifecycle:
    auto_lifecycle: true          # Run after each turn
    promotion_threshold: 0.7      # Minimum score for promotion
    promotion_min_age_hours: 24   # Minimum time before promotion
    decay_rate: 0.01              # Exponential decay rate (λ)
    decay_threshold_turns: 3      # Check decay every N turns
```

**Manual Lifecycle (Advanced):**
```bash
# Run full lifecycle cycle manually
/lifecycle

# Individual operations
/lifecycle --promote   # Only run promotion
/lifecycle --decay     # Only run decay
/lifecycle --stats     # Show lifecycle statistics
```

**Lifecycle Stats Output:**
```
==============================================================
MEMORY LIFECYCLE STATISTICS
==============================================================
Vector Store:
  Short-term:  45 insights
  Long-term:   123 insights
  Decayed:     18 insights
  Total:       186 insights

Last Cycle: 2026-01-24 14:30:00
  Promoted:   3 insights (short → long)
  Decayed:    2 insights (long → decayed)
  Reactivated: 1 insight (decayed → long)

Candidates:
  Promotion ready:  5 insights (score ≥ 0.7, age ≥ 24h)
  Decay candidates: 8 insights (score < 0.5)

Collection Distribution:
  Short-term: 24% (ideal: 20-30%)
  Long-term:  66% (ideal: 60-70%)
  Decayed:    10% (ideal: <15%)
==============================================================
```

### Tuning Lifecycle for Your Use Case

**Personal Assistant (Stable Preferences):**
```yaml
memory:
  lifecycle:
    decay_rate: 0.001              # Very slow decay (49% after 30 days)
    promotion_threshold: 0.6       # Easier promotion
    promotion_min_age_hours: 12    # Faster promotion
```
**Rationale:** Personal preferences are stable—promote quickly, decay slowly.

**Research Assistant (Temporary Topics):**
```yaml
memory:
  lifecycle:
    decay_rate: 0.02               # Faster decay (49% after 36h)
    promotion_threshold: 0.8       # Stricter promotion
    promotion_min_age_hours: 48    # Longer validation period
```
**Rationale:** Research topics change frequently—only promote high-value insights, decay quickly.

**Customer Support (Session-Scoped):**
```yaml
memory:
  lifecycle:
    decay_rate: 0.05               # Very fast decay (49% after 14h)
    promotion_threshold: 0.9       # Very strict
    promotion_min_age_hours: 72    # Long validation
```
**Rationale:** Each customer interaction is isolated—minimal long-term retention.

**For Project Leaders:**
- Lifecycle management provides **automatic knowledge curation**—no manual cleanup needed
- Decay prevents **context pollution**—old, irrelevant memories don't interfere with current tasks
- Reactivation demonstrates **adaptive intelligence**—system recovers forgotten knowledge when needed
- Configurable policies enable **domain-specific optimization**

**For IT Leaders:**
- Lifecycle operations run **asynchronously**—don't block conversation turns
- Storage growth is **bounded**—decayed memories can be purged on schedule
- Metrics available for **operational monitoring** (`/lifecycle --stats`)
- Policies can be **A/B tested** to optimize retention vs. performance

**For Users:**
- Use `/lifecycle --stats` to understand memory distribution
- Adjust `decay_rate` if Friday forgets too quickly or retains too long
- Check `/facts --collection decayed` to see what's been "forgotten"
- Use specific queries to trigger reactivation of decayed memories

---

## 4.3 Context Engineering & Token Budgeting

### The Challenge: Limited Context Windows

LLMs have **fixed context windows**—the maximum amount of text they can process in a single request:

| Model | Context Window | Cost Implications |
|-------|----------------|-------------------|
| GPT-4o | 128K tokens | Higher cost, more capacity |
| GPT-4o-mini | 128K tokens | Lower cost, same capacity |
| Claude 3.5 Sonnet | 200K tokens | Highest capacity |
| Claude 3 Haiku | 200K tokens | Fast, budget-friendly |
| Gemini 2.5 Flash | 1M tokens | Massive capacity |
| Llama 3 (8B) | 8K tokens | Local, limited capacity |

**The Problem:** Friday's three memory stores can contain gigabytes of information, but the LLM can only see 8K-200K tokens per request.

**The Solution:** **Context Engineering**—intelligently select and structure the most relevant subset of memories to fit within the token budget.

### The Knapsack Problem

Context assembly is fundamentally a **0/1 knapsack optimization**:

```
Given:
  - N memories, each with:
    - value_i (relevance score)
    - weight_i (token cost)
  - Budget B (maximum tokens)

Find:
  - Subset S of memories where:
    - Σ weight_i ≤ B (fits within budget)
    - Σ value_i is maximized (most relevant memories)
```

**Naive approaches fail:**
- **Most recent N**: Ignores relevance (old but highly relevant memories excluded)
- **Highest similarity**: Ignores cost (one huge memory might consume entire budget)
- **Round-robin**: Ignores both relevance and cost

**Friday's Solution:** Dynamic programming knapsack solver from `friday-optimization` package.

### Token Budget Allocation

**Budget Structure:**
```yaml
memory:
  total_tokens: 8000            # Total LLM context window

  # Allocated budgets:
  system_prompt_tokens: 1000    # Identity, capabilities, guidelines
  history_tokens: 2000          # Recent conversation turns
  context_tokens: 4000          # Retrieved memories (knapsack optimized)
  query_tokens: 1000            # User's current message + buffer
```

**Why these allocations?**
- **System prompt (12.5%)**: Static, defines agent identity
- **History (25%)**: Recent turns for conversation coherence
- **Context (50%)**: Largest allocation—retrieved memories are most valuable
- **Query (12.5%)**: User message + buffer for response

**Adaptive Budgeting:**

Friday can adjust allocations dynamically:

```python
# If query is short, reallocate to context
if query_tokens < 500:
    context_tokens += (1000 - query_tokens)  # Use saved budget

# If history is minimal (early conversation), reallocate to context
if history_tokens < 1000:
    context_tokens += (2000 - history_tokens)
```

### Context Assembly Algorithm

**Step 1: Retrieve Candidate Memories**

Query all three stores in parallel:

```python
# Episodic: Recent turns
episodic_memories = await transcript_store.get_recent_turns(
    session_id=session_id,
    limit=10
)

# Semantic: Similar insights
semantic_memories = await vector_store.similarity_search(
    query=user_message,
    limit=50,  # Retrieve more candidates than budget allows
    threshold=0.7,
    collections=["long_term", "short_term"]  # Search both, long-term first
)

# Associative: Related entities
associative_memories = await graph_store.get_related_entities(
    query_terms=extract_keywords(user_message),
    limit=20,
    min_hit_count=3  # Only entities accessed at least 3 times
)
```

**Step 2: Score Candidates**

Each memory gets a **composite relevance score**:

```python
def score_memory(memory, query, current_turn):
    """Calculate relevance score (0-1) for a memory."""

    # Component 1: Semantic Similarity (40%)
    similarity = cosine_similarity(memory.embedding, query.embedding)
    sim_score = similarity * 0.40

    # Component 2: Recency (30%)
    age_hours = (current_turn - memory.created_at).total_seconds() / 3600
    recency_score = 1.0 / (1.0 + log(1 + age_hours))  # Logarithmic decay
    recency_score = recency_score * 0.30

    # Component 3: Importance (20%)
    # For semantic: confidence score
    # For associative: hit_count (Hebbian)
    if memory.type == "insight":
        importance = memory.confidence
    elif memory.type == "entity":
        importance = min(memory.hit_count / 50, 1.0)  # Normalize to 0-1
    importance_score = importance * 0.20

    # Component 4: Collection Stage (10%)
    # Long-term memories are more valuable than short-term
    stage_scores = {
        "long_term": 1.0,
        "short_term": 0.7,
        "decayed": 0.3
    }
    stage_score = stage_scores.get(memory.collection, 0.5) * 0.10

    return sim_score + recency_score + importance_score + stage_score
```

**Step 3: Estimate Token Costs**

```python
def estimate_tokens(text: str) -> int:
    """Rough token estimation: 1 token ≈ 4 characters."""
    return len(text) // 4

# Calculate cost for each memory
for memory in candidates:
    memory.token_cost = estimate_tokens(memory.content)
    memory.value = score_memory(memory, query, current_turn)
```

**Step 4: Knapsack Optimization**

```python
from friday_optimization import solve_knapsack

selected_memories = solve_knapsack(
    items=candidates,
    capacity=context_tokens,  # Token budget (e.g., 4000)
    get_weight=lambda m: m.token_cost,
    get_value=lambda m: m.value
)

# Result: Subset of memories that maximizes relevance within budget
```

**Example:**

**Budget:** 4000 tokens
**Candidates:**

| Memory | Content | Tokens | Relevance | Selected? |
|--------|---------|--------|-----------|-----------|
| M1 | "User prefers FastAPI" | 150 | 0.92 | ✓ |
| M2 | "Mentioned web API project" | 200 | 0.88 | ✓ |
| M3 | "Discussed Python vs JavaScript" | 600 | 0.45 | ✗ |
| M4 | "FastAPI has good docs" | 180 | 0.85 | ✓ |
| M5 | "Likes automated testing" | 140 | 0.78 | ✓ |
| ... | ... | ... | ... | ... |
| M47 | "Weather was nice" | 100 | 0.15 | ✗ |

**Output:** Selected 28 memories totaling 3,950 tokens with combined relevance score of 23.4

**Knapsack ensures:**
- **Optimal packing**: No wasted token budget
- **Relevance maximization**: Highest-value memories selected
- **Fairness**: Balance between many small memories vs. few large ones

### Lost-in-the-Middle Mitigation

**The Research:** Studies (Liu et al., 2023) show LLMs pay less attention to content in the middle of long contexts:

```
┌─────────────────────────────────────────────┐
│         LLM ATTENTION DISTRIBUTION          │
│                                             │
│  High │▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░▓▓▓▓▓▓▓▓▓│    │
│       │                                 │    │
│  Med  │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│    │
│       │                                 │    │
│  Low  │░░░░░░░░░░░▓▓▓▓▓▓▓▓░░░░░░░░░░░│    │
│       │                                 │    │
│       └─────────────────────────────────┘    │
│        Start        Middle          End      │
└─────────────────────────────────────────────┘

  ▓ = Strong attention
  ░ = Weak attention
```

**The Problem:** If we structure the prompt as:
```
1. System prompt (start - strong attention)
2. Retrieved memories (middle - WEAK ATTENTION) ← Problem!
3. User query (end - strong attention)
```

Then the most relevant memories (retrieved context) get the least attention!

**Friday's Solution: Tail Injection**

Place retrieved memories **immediately before** the user query:

```
1. System prompt (start)
2. Conversation history (middle - less critical for recent turns)
3. Retrieved memories (just before end) ← Strong attention!
4. User query (end)
```

**Prompt Structure:**
```python
messages = [
    {
        "role": "system",
        "content": system_prompt + "\n\n" + agent_capabilities
    },
    {
        "role": "user",
        "content": history_turn_1_user
    },
    {
        "role": "assistant",
        "content": history_turn_1_assistant
    },
    # ... more history turns ...
    {
        "role": "user",
        "content": (
            "# Relevant Context:\n" +
            retrieved_memory_1 + "\n" +
            retrieved_memory_2 + "\n" +
            # ... more retrieved memories ...
            "\n# Current Query:\n" +
            user_current_message
        )
    }
]
```

**Effect:** Retrieved memories are placed in the **recency zone** where LLM attention is highest, dramatically improving context utilization.

### Context Payload Structure

**ContextPayload Data Model:**
```python
@dataclass
class ContextPayload:
    """Assembled context ready for LLM."""

    # Core components
    system_prompt: str
    conversation_history: list[Turn]
    retrieved_insights: list[Insight]
    loaded_entities: list[Entity]
    injected_tools: list[ToolSchema]
    scoped_variables: dict[str, Any]

    # Metadata
    token_counts: dict[str, int]  # Per-component token usage
    retrieval_latency_ms: int
    knapsack_efficiency: float  # % of budget used

    # Debug info
    candidates_considered: int
    candidates_selected: int
    similarity_threshold: float
```

**Token Count Breakdown:**
```python
{
    "system_prompt": 823,
    "history": 1,456,
    "insights": 2,891,  # Knapsack-selected semantic memories
    "entities": 478,     # Graph-loaded entities
    "tools": 312,        # Tool schemas (if any)
    "variables": 45,     # Scoped variables
    "query": 215,        # User message
    "total": 6,220,      # Sum (must be ≤ total_tokens)
    "buffer": 1,780      # Remaining budget (22% unused)
}
```

### Context Formats

Friday supports multiple output formats for different LLM preferences:

**1. Plain Text (Default):**
```
You are Friday, an AI assistant with memory.

Recent Conversation:
Turn 1: User asked about Python web frameworks
Turn 2: You recommended FastAPI

Relevant Memories:
- User prefers FastAPI over Flask
- User values automatic documentation
- User is working on a REST API project

Current Query:
Should I use Flask or FastAPI for my project?
```

**2. XML (Claude Optimal):**
```xml
<system>
  <identity>You are Friday, an AI assistant with memory.</identity>
</system>

<history>
  <turn>
    <user>What's the best Python web framework?</user>
    <assistant>FastAPI is excellent for modern APIs...</assistant>
  </turn>
</history>

<context>
  <memory type="preference">User prefers FastAPI over Flask</memory>
  <memory type="observation">User values automatic documentation</memory>
  <entity name="User" type="Person">
    <relationship>WORKING_ON</relationship>
    <entity name="REST_API" type="Project"/>
  </entity>
</context>

<query>Should I use Flask or FastAPI for my project?</query>
```

**3. JSON (Structured Extraction):**
```json
{
  "system": {
    "identity": "You are Friday, an AI assistant with memory."
  },
  "history": [
    {"role": "user", "content": "What's the best Python web framework?"},
    {"role": "assistant", "content": "FastAPI is excellent..."}
  ],
  "context": {
    "memories": [
      {"type": "preference", "content": "User prefers FastAPI over Flask", "confidence": 0.92}
    ],
    "entities": [
      {"name": "User", "type": "Person", "relationships": [{"verb": "WORKING_ON", "target": "REST_API"}]}
    ]
  },
  "query": "Should I use Flask or FastAPI for my project?"
}
```

**Configuration:**
```yaml
memory:
  context_format: "xml"  # plain | xml | json | markdown
```

**For Project Leaders:**
- Context engineering is **invisible to users** but critical to quality
- Knapsack optimization provides **maximum value** per token (cost efficiency)
- Tail injection is **research-backed** performance improvement (10-20% better recall)
- Format flexibility enables **model-specific optimization**

**For IT Leaders:**
- Context assembly is **highly parallelizable** (query stores concurrently)
- Knapsack solver is **O(n × capacity)** complexity—fast for typical loads
- Token estimation avoids **expensive tokenizer calls** (4 chars ≈ 1 token)
- Format selection can be **A/B tested** for quality vs. cost

**For Users:**
- Use `/context --debug` to see token breakdown
- Check `knapsack_efficiency` to see if budget is well-utilized (>90% is ideal)
- Adjust `context_tokens` budget if retrieval feels insufficient
- Use `/prompt` to see final formatted messages sent to LLM

---

## 4.4 Memory Extraction Pipeline

### From Conversation to Structured Knowledge

Every conversation turn triggers a **background extraction process** that converts unstructured dialogue into structured memories:

```
┌────────────────────────────────────────────────────────────┐
│                   EXTRACTION PIPELINE                      │
│                                                            │
│  User Message + Assistant Response                        │
│              │                                             │
│              ▼                                             │
│  ┌──────────────────────┐                                 │
│  │  Extraction LLM      │  (Separate, cheaper model)     │
│  │  Analyzes turn for:  │                                 │
│  │  - Entities          │                                 │
│  │  - Relationships     │                                 │
│  │  - Insights          │                                 │
│  └─────────┬────────────┘                                 │
│            │                                               │
│            ├──────────► Entities (Person, Technology, ...)│
│            │            └─► Graph Store                    │
│            │                                               │
│            ├──────────► Relationships (USES, PREFERS, ...)│
│            │            └─► Graph Store                    │
│            │                                               │
│            └──────────► Insights (Preferences, decisions) │
│                         └─► Vector Store (with embeddings)│
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Extraction LLM Configuration

**Why a Separate Model?**
- **Cost optimization**: Use cheaper model (GPT-4o-mini, Claude Haiku) for structured extraction
- **Specialized prompts**: Extraction requires different capabilities than conversation
- **Temperature control**: Lower temperature (0.3) for consistent extraction
- **Parallel execution**: Main LLM handles conversation, extraction LLM runs in background

**Configuration:**
```yaml
extraction:
  enabled: true

  llm:
    model: "gpt-4o-mini"        # Cheaper model for extraction
    temperature: 0.3            # Lower = more consistent
    max_tokens: 2000            # Shorter responses (just JSON)

  confidence_threshold: 0.6     # Minimum extraction confidence

  # What to extract
  extract_entities: true
  extract_relationships: true
  extract_insights: true
```

**Cost Comparison:**

| Model | Cost per 1M tokens | Typical Extraction Cost (per turn) |
|-------|-------------------|------------------------------------|
| GPT-4o (conversation) | $2.50 | $0.005 |
| GPT-4o-mini (extraction) | $0.15 | $0.0003 |
| **Savings** | **94%** | **$0.0047 per turn** |

For 1000 turns/day: **~$1.50/day savings** by using dedicated extraction model.

### Entity Extraction

**Extraction Prompt:**
```
Analyze the following conversation turn and extract all entities mentioned.

For each entity, provide:
- name: The entity name (normalize: "fastapi" → "FastAPI")
- type: Person | Technology | Project | Concept | Organization | Location
- description: Brief explanation (1 sentence)
- confidence: 0.0-1.0 (how certain are you this is a distinct entity?)

Conversation:
User: "I'm using FastAPI for my project at Acme Corp"
Assistant: "FastAPI is great for building APIs in Python..."

Output as JSON:
{
  "entities": [
    {
      "name": "FastAPI",
      "type": "Technology",
      "description": "Python web framework for building APIs",
      "confidence": 0.95
    },
    {
      "name": "Acme Corp",
      "type": "Organization",
      "description": "User's employer",
      "confidence": 0.85
    },
    {
      "name": "Python",
      "type": "Technology",
      "description": "Programming language",
      "confidence": 0.98
    }
  ]
}
```

**Entity Normalization:**

Friday normalizes entity names to prevent duplicates:
- Case normalization: "fastapi" → "FastAPI", "python" → "Python"
- Variant consolidation: "FastAPI" = "Fast API" = "fast-api"
- Abbreviation expansion: "API" mentioned with "Application Programming Interface" → link them

**Entity Deduplication:**

```python
# When extracting entity "FastAPI"
existing_entity = graph_store.find_entity(name="FastAPI")

if existing_entity:
    # Entity exists - update metadata, increment hit_count
    existing_entity.hit_count += 1
    existing_entity.last_accessed = now()
    existing_entity.description = merge_descriptions(
        existing_entity.description,
        new_extraction.description
    )
else:
    # New entity - create node
    graph_store.add_entity(new_extraction)
```

### Relationship Extraction

**Extraction Prompt:**
```
Analyze the conversation and extract relationships between entities.

For each relationship, provide:
- source: Entity name (must be from extracted entities)
- verb: Semantic relationship (USES, PREFERS, WORKING_ON, CREATED, ...)
- target: Entity name
- context: Supporting quote or explanation
- confidence: 0.0-1.0

Use specific, semantic verbs (not generic "RELATED_TO").

Conversation:
User: "I'm using FastAPI for my project because I prefer it over Flask"

Output as JSON:
{
  "relationships": [
    {
      "source": "User",
      "verb": "USES",
      "target": "FastAPI",
      "context": "for current project",
      "confidence": 0.95
    },
    {
      "source": "User",
      "verb": "PREFERS",
      "target": "FastAPI",
      "context": "prefers over Flask",
      "confidence": 0.90
    },
    {
      "source": "FastAPI",
      "verb": "ALTERNATIVE_TO",
      "target": "Flask",
      "context": "User comparing the two",
      "confidence": 0.85
    }
  ]
}
```

**Relationship Confidence Scoring:**

```python
def score_relationship_confidence(relationship, conversation_text):
    """Calculate confidence score for extracted relationship."""

    # Factor 1: Explicit statement (60%)
    explicit_patterns = [
        "prefers", "uses", "created", "working on"
    ]
    explicit_score = 0.6 if any(p in conversation_text.lower() for p in explicit_patterns) else 0.3

    # Factor 2: Context clarity (30%)
    context_length = len(relationship.context)
    clarity_score = min(context_length / 100, 1.0) * 0.3

    # Factor 3: Entity confidence (10%)
    entity_conf = (
        get_entity(relationship.source).confidence +
        get_entity(relationship.target).confidence
    ) / 2
    entity_score = entity_conf * 0.1

    return explicit_score + clarity_score + entity_score
```

### Insight Generation

**What is an Insight?**

An insight is **actionable, preference-revealing, or decision-capturing knowledge** extracted from conversation:

**Good Insights:**
- "User prefers TypeScript over JavaScript for production code"
- "User follows test-driven development practices"
- "User is building a REST API with authentication requirements"
- "User decided to use PostgreSQL instead of MongoDB for data integrity"

**Bad Insights (Don't Extract):**
- "User said hello" (not actionable)
- "Weather was mentioned" (not preference-revealing)
- "User asked a question" (not decision-capturing)

**Extraction Prompt:**
```
Analyze the conversation and generate insights.

An insight is:
- A learned preference (what the user likes/dislikes)
- A decision made (what the user chose and why)
- An observation about user behavior or expertise

For each insight, provide:
- content: 1-2 sentences capturing the insight
- type: preference | decision | observation | expertise
- confidence: 0.0-1.0
- tags: List of relevant topics

Avoid:
- Trivial statements ("user said hello")
- Temporary facts ("user is tired today")
- Purely informational ("FastAPI is a Python framework")

Conversation:
User: "I always write tests first, then implement the feature"
Assistant: "That's test-driven development, a great practice..."

Output as JSON:
{
  "insights": [
    {
      "content": "User practices test-driven development by writing tests before implementation",
      "type": "expertise",
      "confidence": 0.92,
      "tags": ["testing", "methodology", "tdd"]
    }
  ]
}
```

**Insight Types:**

| Type | Description | Example |
|------|-------------|---------|
| **preference** | User likes/dislikes | "Prefers FastAPI over Flask" |
| **decision** | Choice made | "Decided to use PostgreSQL for transactions" |
| **observation** | Behavioral pattern | "Tends to ask for code examples" |
| **expertise** | Skill/knowledge level | "Experienced with Python, learning Rust" |

### Extraction Execution

**Asynchronous Pipeline:**

```python
async def extract_from_turn(turn: Turn):
    """Run extraction in background (doesn't block response)."""

    # Prepare extraction context
    context = f"User: {turn.user_message}\nAssistant: {turn.assistant_message}"

    # Call extraction LLM
    extraction_result = await extraction_llm.chat_completion([
        {"role": "system", "content": EXTRACTION_PROMPT},
        {"role": "user", "content": context}
    ])

    # Parse JSON response
    data = json.loads(extraction_result.content)

    # Store entities in graph
    for entity_data in data["entities"]:
        if entity_data["confidence"] >= confidence_threshold:
            await graph_store.add_or_update_entity(entity_data)

    # Store relationships in graph
    for rel_data in data["relationships"]:
        if rel_data["confidence"] >= confidence_threshold:
            await graph_store.add_relationship(rel_data)

    # Store insights in vector store
    for insight_data in data["insights"]:
        if insight_data["confidence"] >= confidence_threshold:
            # Generate embedding
            embedding = await embedding_model.embed(insight_data["content"])

            # Store in short_term collection initially
            await vector_store.add_document(
                content=insight_data["content"],
                embedding=embedding,
                metadata={
                    "type": insight_data["type"],
                    "confidence": insight_data["confidence"],
                    "tags": insight_data["tags"],
                    "turn_id": turn.id,
                    "collection": "short_term",
                    "created_at": now()
                }
            )
```

**Performance:**
- Extraction runs in **background** (doesn't delay response to user)
- Typically completes in **1-3 seconds**
- Failures are logged but don't affect conversation

**Error Handling:**

```python
try:
    await extract_from_turn(turn)
except JSONDecodeError:
    logger.warning(f"Extraction LLM returned invalid JSON for turn {turn.id}")
    # Continue - extraction failure doesn't block conversation
except ExtractionLLMError as e:
    logger.error(f"Extraction failed for turn {turn.id}: {e}")
    # Could retry with exponential backoff
except Exception as e:
    logger.error(f"Unexpected extraction error: {e}")
    # Alert monitoring system
```

### Extraction Quality Monitoring

**CLI Commands:**
```bash
# View recent extractions
/facts --limit 10 --sort created_at

# Check extraction confidence distribution
/facts --stats

# Review low-confidence extractions
/facts --confidence-max 0.7

# See entity extraction results
/entities --sort hit_count
```

**Quality Metrics:**
```
==============================================================
EXTRACTION QUALITY METRICS
==============================================================
Last 100 Turns:
  Entities extracted:     247
  Relationships extracted: 189
  Insights extracted:      134

Confidence Distribution:
  0.9-1.0 (Excellent): 45%
  0.8-0.9 (Good):      32%
  0.7-0.8 (Fair):      18%
  0.6-0.7 (Marginal):  5%

Average Confidence:
  Entities:       0.87
  Relationships:  0.82
  Insights:       0.84

Extraction Latency:
  p50: 1.2s
  p95: 2.8s
  p99: 4.1s
==============================================================
```

**For Project Leaders:**
- Background extraction is **non-blocking**—doesn't impact user experience
- Separate extraction model provides **94% cost savings** vs. using main LLM
- Confidence thresholds ensure **quality control** (only store high-confidence extractions)
- Extraction quality improves **over time** as model learns domain patterns

**For IT Leaders:**
- Extraction runs **asynchronously**—can scale independently
- Failures are **isolated**—don't cascade to conversation
- Monitoring available via **CLI commands** and **structured logs**
- Extraction model can be **tuned** (temperature, prompts, thresholds)

**For Users:**
- Use `/facts` to see what Friday learned from conversations
- Check confidence scores to understand extraction certainty
- Low confidence (<0.7) insights may be incorrect—verify if important
- Extraction happens automatically—no user action required

---

## 4.5 Session Priming & Cross-Session Continuity

### The Cold Start Problem

**Challenge:** When starting a new session (new day, new terminal window, agent restart), Friday has no context. Without priming, the first few turns feel like talking to a stranger who doesn't know you.

**Solution:** **Session Priming**—automatically load the most important memories when initializing a session, before the first user message.

### Automatic Context Priming

**What Gets Primed:**

```python
async def prime_session(session_id: str, user_id: str):
    """Load important memories before first turn."""

    # 1. Top entities by Hebbian importance
    top_entities = await graph_store.get_top_entities(
        limit=10,              # Top 10 most-accessed entities
        min_hit_count=5        # Only entities accessed at least 5 times
    )

    # 2. Recent insights (from last N days)
    recent_insights = await vector_store.query(
        collection="long_term",
        filters={
            "created_at": {"$gte": days_ago(30)}  # Last 30 days
        },
        sort_by="created_at",
        limit=20
    )

    # 3. User preferences (high-confidence insights)
    preferences = await vector_store.query(
        collection="long_term",
        filters={
            "type": "preference",
            "confidence": {"$gte": 0.8}
        },
        limit=15
    )

    # 4. Recent conversation summaries
    summaries = await transcript_store.get_session_summaries(
        user_id=user_id,
        days=7,  # Last week
        limit=5
    )

    return {
        "entities": top_entities,
        "insights": recent_insights,
        "preferences": preferences,
        "summaries": summaries
    }
```

**Priming Configuration:**
```yaml
memory:
  priming:
    enabled: true

    # What to load
    top_n_entities: 10         # Most accessed entities
    top_n_insights: 20         # Recent insights
    top_n_preferences: 15      # User preferences

    # Filters
    min_entity_hit_count: 5    # Only load frequently-accessed entities
    recency_days: 30           # Only load memories from last 30 days
    min_confidence: 0.8        # Only load high-confidence preferences
```

### Priming in Action

**Example: Friday Remembers You**

**Session 1 (Monday):**
```
User: "Hi, I'm Alice. I'm working on a Python web API using FastAPI."
Friday: "Hello Alice! I'm Friday. I'll remember that you're working with Python and FastAPI..."

[Extraction runs in background]
Entities: Alice (Person), Python (Technology), FastAPI (Technology)
Relationships: Alice WORKING_ON Python, Alice USES FastAPI
Insights: "User (Alice) is developing a web API with Python and FastAPI"

[All stored with hit_count=1]
```

**Session 2 (Tuesday):**
```
[Priming loads before first message]
- Entity: Alice (hit_count=5, type=Person)
- Entity: Python (hit_count=12, type=Technology)
- Entity: FastAPI (hit_count=8, type=Technology)
- Insight: "Alice is developing a web API with Python and FastAPI" (confidence=0.89)

User: "Good morning!"
Friday: "Good morning, Alice! How's your FastAPI project coming along?"
         ^-- Remembered name and project without being reminded!
```

**Session 3 (Next Week):**
```
[Priming loads]
- Entity: Alice (hit_count=23, type=Person)
- Entity: Python (hit_count=45, type=Technology)
- Entity: FastAPI (hit_count=31, type=Technology)
- Insights:
  - "Alice prefers FastAPI over Flask" (confidence=0.92, hit_count=7)
  - "Alice values automatic API documentation" (confidence=0.85, hit_count=5)
  - "Alice is building a REST API with authentication" (confidence=0.88, hit_count=6)

User: "Should I add OAuth2 to my API?"
Friday: "Given your FastAPI project and preference for its automatic documentation,
         yes—FastAPI has excellent OAuth2 support built in..."
         ^-- Remembers project, framework preference, and documentation value!
```

**This is cross-session continuity in action**: Friday doesn't just remember the last conversation—it remembers everything important from all conversations, weighted by access patterns.

### Memory Namespaces

**Use Case:** Isolate memories for different contexts (different users, different projects, different agent teams).

**Namespace Strategies:**

**1. User-Scoped (Default):**
```python
# Each user gets isolated memory
controller = MemoryController(...)
session_id = "session_123"
user_id = "alice"  # All memories tagged with user_id

# Alice's memories don't mix with Bob's memories
```

**2. Project-Scoped:**
```python
# Isolate memories per project
session_id = "project_webapi_session_1"
user_id = "alice"
namespace = "project:webapi"

# Alice's webapi memories separate from her mobile app memories
```

**3. Team-Scoped:**
```python
# Shared memory across team members
session_id = "team_alpha_session_5"
user_id = "alice"
namespace = "team:alpha"

# Alice and Bob share memories (knowledge base accumulation)
```

**Implementation:**

Namespaces are metadata filters on queries:

```python
# Store with namespace
await vector_store.add_document(
    content="User prefers FastAPI",
    metadata={"namespace": "project:webapi", ...}
)

# Retrieve with namespace filter
results = await vector_store.similarity_search(
    query="web framework preferences",
    filters={"namespace": "project:webapi"}
)
```

**Configuration:**
```yaml
memory:
  namespace:
    mode: "user"  # user | project | team | custom

    # For project mode
    project_id: "webapi"

    # For team mode
    team_id: "alpha"
```

### Priming Strategies for Different Use Cases

**Personal Assistant (Heavy Priming):**
```yaml
memory:
  priming:
    enabled: true
    top_n_entities: 20       # Load more context
    top_n_insights: 30
    recency_days: 90         # Look back 3 months
    min_entity_hit_count: 3  # Lower threshold
```
**Rationale:** Personal assistants benefit from rich context—load aggressively.

**Customer Support (Minimal Priming):**
```yaml
memory:
  priming:
    enabled: true
    top_n_entities: 5        # Minimal context
    top_n_insights: 10
    recency_days: 7          # Only recent
    min_entity_hit_count: 10 # High threshold
```
**Rationale:** Each customer interaction is largely independent—minimal priming.

**Research Assistant (Topic-Focused Priming):**
```yaml
memory:
  priming:
    enabled: true
    topic_filter: ["machine_learning", "nlp"]  # Only load ML/NLP memories
    top_n_entities: 15
    top_n_insights: 25
    recency_days: 60
```
**Rationale:** Focus priming on relevant topic areas.

### Priming Performance

**Latency Targets:**
- Priming should complete in **<500ms** to avoid noticeable delay
- Parallel queries to all stores (episodic, semantic, associative)
- Results cached for session duration

**Optimization:**
```python
# Parallel priming queries
priming_data = await asyncio.gather(
    graph_store.get_top_entities(limit=10),
    vector_store.query(collection="long_term", limit=20),
    vector_store.query(filters={"type": "preference"}, limit=15),
    transcript_store.get_session_summaries(days=7)
)
```

**Monitoring:**
```bash
/prime  # Manually trigger priming and see results

Output:
==============================================================
PRIMING COMPLETE
==============================================================
Loaded in 342ms:
  Entities:    10 (top by hit_count)
  Insights:    20 (recent, long-term)
  Preferences: 15 (confidence ≥ 0.8)
  Summaries:   3 (last 7 days)

Top Entities:
  1. Python (Technology, hit_count=45)
  2. FastAPI (Technology, hit_count=31)
  3. Alice (Person, hit_count=23)
  ...

Top Insights:
  - "Alice prefers FastAPI over Flask" (conf=0.92)
  - "Alice values automatic API documentation" (conf=0.85)
  ...
==============================================================
```

**For Project Leaders:**
- Priming creates **immediate value** from day 1 of agent deployment
- Cross-session continuity demonstrates **genuine learning** to stakeholders
- Namespace isolation enables **multi-tenant deployments** with memory safety
- Priming latency is **optimized** (<500ms)—doesn't impact UX

**For IT Leaders:**
- Priming queries can be **cached** at session level (refresh periodically)
- Parallel execution leverages **async I/O** for performance
- Namespace filters provide **logical isolation** (no separate databases needed)
- Monitoring via `/prime` command and structured logs

**For Users:**
- Use `/prime` to manually trigger priming and inspect loaded context
- If Friday seems to "forget" between sessions, check priming config
- Adjust `recency_days` if Friday loads too much/too little history
- Use namespaces to separate work projects from personal projects

---

## Putting It All Together: The Complete Memory System

You now understand all five components of Friday's adaptive memory:

1. **Three-Tier Architecture** (Section 4.1)
   - Episodic (SQLite): Chronological conversation logs
   - Semantic (ChromaDB): Searchable insights via embeddings
   - Associative (NetworkX): Entity relationship graph

2. **Memory Lifecycle** (Section 4.2)
   - Promotion: Short-term → Long-term (multi-factor scoring)
   - Decay: Long-term → Decayed (exponential forgetting curve)
   - Reactivation: Decayed → Long-term (soft-delete recovery)

3. **Context Engineering** (Section 4.3)
   - Knapsack optimization for token budgeting
   - Lost-in-the-middle mitigation via tail injection
   - Format flexibility (plain, XML, JSON, markdown)

4. **Extraction Pipeline** (Section 4.4)
   - Entity & relationship extraction (graph building)
   - Insight generation (preference/decision learning)
   - Background processing with separate LLM

5. **Session Priming** (Section 4.5)
   - Automatic context loading on session start
   - Cross-session continuity via Hebbian importance
   - Namespace isolation for multi-user/multi-project

**This is adaptive memory**: A system that learns, forgets, remembers, and adapts based on usage patterns—mirroring human cognition while remaining observable, configurable, and debuggable.

---

## Quick Reference: Memory System

### Key Commands
```bash
# Inspection
/memory              # Statistics across all stores
/transcript          # Episodic memory (conversation log)
/facts               # Semantic memory (insights)
/entities            # Associative memory (knowledge graph)

# Lifecycle
/lifecycle --stats   # Memory stage distribution
/lifecycle           # Run full lifecycle cycle
/lifecycle --promote # Promotion only
/lifecycle --decay   # Decay only

# Context
/context --debug     # Token budget breakdown
/prompt              # Final formatted messages
/prime               # Session priming details

# Maintenance
/reorganize          # Full memory optimization
/migrate             # Schema migrations
/reset               # Complete memory wipe
```

### Configuration Essentials
```yaml
memory:
  # Storage
  storage_path: "./friday_data"

  # Token budgeting
  total_tokens: 8000
  context_tokens: 4000

  # Lifecycle
  lifecycle:
    decay_rate: 0.01              # 49% after 72h
    promotion_threshold: 0.7       # Score for promotion
    promotion_min_age_hours: 24    # Minimum time in short-term

  # Priming
  priming:
    enabled: true
    top_n_entities: 10
    recency_days: 30

  # Extraction
extraction:
  llm:
    model: "gpt-4o-mini"
    temperature: 0.3
  confidence_threshold: 0.6
```

### Performance Targets
| Operation | Target Latency |
|-----------|----------------|
| Context assembly | <200ms |
| Session priming | <500ms |
| Extraction (background) | 1-3s |
| Lifecycle operations | 2-5s |
| Graph query | <50ms |
| Vector similarity search | 50-200ms |

---

## What's Next?

With adaptive memory mastered, you're ready to explore how Friday uses this memory to interact with the world:

**Continue to:**
- **[Section 5: Tools](05-tools.md)** - 50+ built-in tools and custom tool creation
- **[Section 7: Multi-Agent Orchestration](07-multi-agent.md)** - Collaborative agent teams with shared memory
- **[Section 9: CLI Reference](09-cli-reference.md)** - Complete command documentation
- **[Section 10: Configuration Guide](10-configuration.md)** - Detailed memory configuration options

**Or explore:**
- **[Section 11: Advanced Topics](11-advanced-topics.md)** - Memory optimization and scaling strategies
- **[Section 12: Use Cases](12-use-cases.md)** - Real-world memory-powered applications

---

*You've completed Section 4: Adaptive Memory. Friday's memory system is now fully explained—from storage architecture through lifecycle management to practical usage. Continue to Section 5 to learn how Friday uses tools to act on this knowledge.*
