---
title: "Three-Tier Memory System"
description: "Episodic, short-term, and long-term memory tiers and how they interact."
weight: 1
---

Friday organizes memory into episodic (recent turns), short-term (session-scoped facts), and long-term (persistent knowledge) tiers that interact through promotion and decay.

---

## Cognitive Science Foundation

Friday's memory architecture is inspired by human memory systems identified in cognitive psychology:

1. **Episodic Memory** — Autobiographical events ("I had lunch with Alice yesterday")
2. **Semantic Memory** — Factual knowledge ("Python is a programming language")
3. **Associative Memory** — Conceptual relationships ("Alice prefers Python for web development")

These aren't just storage categories—they represent fundamentally different ways of organizing and retrieving information. Friday implements all three to mirror how humans naturally remember and reason.

---

## The Three Stores

```text
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

---

## Episodic Memory: The Conversation Log

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

**Storage Characteristics:**
- **Size**: ~1-5KB per turn (depends on response length, tool calls)
- **Growth**: Linear with conversation volume
- **Retention**: Permanent (no automatic deletion, archive manually)
- **Performance**: Fast retrieval by session_id + timestamp index

**Example schema:**

```sql
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
- **Portable**: Works on any platform Python runs on
- **Swappable**: Implement `TranscriptStoreAdapter` for PostgreSQL/MySQL/MongoDB if needed

**CLI commands:** `/transcript`, `/history`, `/export jsonl`

---

## Semantic Memory: The Knowledge Vault

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

### Multi-Collection Architecture

Friday uses **three collections** to implement lifecycle stages:

```text
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

### Embedding Models

| Model | Dimensions | Cost | Use Case |
|-------|-----------|------|----------|
| **text-embedding-3-small** (OpenAI) | 1536 | $0.02/1M tokens | Default, good balance |
| **text-embedding-3-large** (OpenAI) | 3072 | $0.13/1M tokens | Higher quality, more expensive |
| **nomic-embed-text-v1.5** (local) | 768 | Free (local) | Privacy-sensitive, offline |
| **voyage-2** (Voyage AI) | 1024 | $0.12/1M tokens | Specialized for retrieval |

**Storage Characteristics:**
- **Size**: ~6KB per insight (1536 floats + metadata + text)
- **Retention**: Lifecycle-managed (short → long → decayed → deleted)
- **Performance**: Similarity search ~50-200ms for 10K documents

**CLI commands:** `/facts`, `/insights`, `/lifecycle --stats`

---

## Associative Memory: The Knowledge Graph

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
  - metadata: Additional attributes

Relationship (Edge):
  - source: Entity name (start node)
  - verb: Semantic relationship type
  - target: Entity name (end node)
  - context: Supporting information
  - confidence: 0.0-1.0
  - hit_count: Relationship access frequency
```

### Semantic Relationship Verbs

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

### Hebbian Learning

The `hit_count` field implements **"neurons that fire together, wire together"**:

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

### Retrieval Patterns

**Entity Lookup:**

```python
# Get all information about an entity
entity = graph_store.get_entity("Alice")
# Returns: type, description, hit_count, all relationships
```

**Relationship Query:**

```python
# What technologies does Alice use?
tech = graph_store.query_relationships(
    source="Alice",
    verb="USES",
    target_type="Technology"
)
# Returns: ["Python", "FastAPI", "Git"]
```

**Priming (Session Initialization):**

```python
# Load most important entities by Hebbian hit_count
top_entities = graph_store.get_top_entities(
    limit=10,  # Top 10 most accessed
    min_hit_count=5  # Only entities accessed at least 5 times
)
```

**Persistence Format (JSON):**

```json
{
  "entities": {
    "Alice": {
      "type": "Person",
      "description": "User working on Python web development",
      "hit_count": 47,
      "created_at": "2026-01-15T10:00:00Z",
      "last_accessed": "2026-01-24T14:30:00Z"
    },
    "FastAPI": {
      "type": "Technology",
      "description": "Python web framework for APIs",
      "hit_count": 89,
      "created_at": "2026-01-15T11:00:00Z",
      "last_accessed": "2026-01-24T14:30:00Z"
    }
  },
  "relationships": [
    {
      "source": "Alice",
      "verb": "USES",
      "target": "FastAPI",
      "context": "For building production APIs",
      "confidence": 0.95,
      "hit_count": 12
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

**CLI commands:** `/entities`, `/entities --sort hit_count`

---

## How the Three Stores Work Together

**Complementary Retrieval:**

```text
User Query: "What did I say about Python web frameworks last week?"

1. EPISODIC (Time-based):
   └─ Search turns from last week → Find conversation mentioning "Python web frameworks"

2. SEMANTIC (Content-based):
   └─ Similarity search for "Python web frameworks"
      → Retrieve insights about FastAPI, Flask preferences

3. ASSOCIATIVE (Relationship-based):
   └─ Find entities: "Python", "FastAPI", "Flask"
   └─ Traverse relationships: User PREFERS FastAPI, FastAPI USED_FOR web APIs

Result: Rich context combining chronological record (episodic),
        conceptual knowledge (semantic), and structured relationships (associative)
```

**Example: Context Assembly for "Should I use FastAPI or Flask?"**

**From Episodic:**
```text
Turn 15 (2 days ago): "I'm building a web API"
Turn 16 (2 days ago): "FastAPI has great documentation"
Turn 17 (2 days ago): "Flask seems simpler but less features"
```

**From Semantic:**
```text
Insight 1 (confidence 0.92): "User prefers FastAPI over Flask for production APIs"
Insight 2 (confidence 0.85): "User values automatic documentation and type safety"
Insight 3 (confidence 0.78): "User is building a REST API with authentication"
```

**From Associative:**
```text
User -[PREFERS]-> FastAPI
User -[WORKING_ON]-> web_api_project
web_api_project -[USES]-> Python
FastAPI -[BASED_ON]-> Python
Flask -[ALTERNATIVE_TO]-> FastAPI
```

Friday can now respond with personalized, contextual advice that knows the user's preference for FastAPI (semantic + associative), recalls the specific conversation about documentation (episodic), and understands the connection between the user's project and framework choice (associative).

**This is the power of three-tier memory: comprehensive, contextual, and connected.**

---

## Storage Characteristics Summary

| Store | Backend | Size per Item | Retention | Query Speed |
|-------|---------|--------------|-----------|-------------|
| **Episodic** | SQLite | 1-5KB per turn | Permanent | <1ms (indexed) |
| **Semantic** | ChromaDB | ~6KB per insight | Lifecycle-managed | 50-200ms |
| **Associative** | NetworkX+JSON | ~500B entity, ~300B relationship | Permanent with pruning | 10-50ms |
