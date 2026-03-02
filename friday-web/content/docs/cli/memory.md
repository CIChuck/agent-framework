---
title: "Memory Commands"
description: "Inspect, search, prune, and export the memory stores."
weight: 2
---

The `friday memory` command group lets you search the vector store, inspect graph entities, prune stale memories, and export the full memory state. These commands provide direct visibility into Friday's three-tier memory architecture.

---

## `/memory`

**Description:** Displays comprehensive memory statistics across all storage systems.

**Syntax:**

```
/memory
```

**Output Format:**

```
=== MEMORY STATISTICS ===

Episodic Memory (Conversation History):
  Current session turns: 8
  Total token count: 12,450

Vector Store (Semantic Memory):
  Short-term collection: 23 documents
  Long-term collection: 134 documents
  Decayed collection: 12 documents
  Total insights: 89
  Total summaries: 15

Graph Store (Associative Memory):
  Total entities: 42
  Total relationships: 87
  Entity types: Person (15), Project (8), Technology (12), Concept (7)

Session State:
  Session ID: abc123def456
  User ID: developer@example.com
  Scoped variables: 3
  Active tools: 8

Health Indicators:
  Memory fragmentation: Low
  Promotion backlog: 5 candidates
  Decay pending: 8 candidates
```

**Use Cases:**
- Quick health check of memory system
- Verifying memory persistence after restart
- Monitoring memory growth over time
- Debugging missing memories (check collection counts)

---

## `/context [--debug]`

**Description:** Shows the assembled context payload sent to the ContextAssembler, including all retrieved memories, history, and supporting context.

**Syntax:**

```
/context
/context --debug
```

**Parameters:**
- `--debug` (optional): Enables detailed token counting and debug information

**Output Format (Standard):**

```
=== CONTEXT PAYLOAD ===

Entities (5):
  - Python (Technology, hits: 45)
  - UserProject (Project, hits: 23)
  - Alice (Person, hits: 12)
  ...

Key Facts (3):
  - User prefers functional programming patterns
  - Project deadline: January 31, 2026
  ...

Insights (8):
  - [2026-01-24 10:23] User expressed concern about performance
  - [2026-01-23 15:44] User prefers TypeScript over JavaScript
  ...

Summaries (2):
  - [2026-01-24] Discussion about optimization strategies...
  - [2026-01-23] Code review session for auth module...

Relationships (4):
  - Alice USES Python (hits: 12)
  - UserProject REQUIRES Python (hits: 8)
  ...

History (3 turns):
  Turn 1 [abc12345...]:
    User: How do I optimize this function?
    Friday: Let me analyze the performance characteristics...
  ...

--- Supporting Context (format: xml) ---
<context>
  <entities>
    <entity type="Technology" name="Python" relevance="0.89"/>
    ...
  </entities>
  <insights>
    <insight confidence="0.92">User prefers functional patterns</insight>
    ...
  </insights>
</context>
```

**Output Format (Debug Mode):**

Adds token estimates per section:

```
--- TOKEN ESTIMATES (debug mode) ---
  History: ~1,234 tokens (3 turns)
  Insights: ~567 tokens (8 items)
  Summaries: ~234 tokens (2 items)
  Relationships: ~123 tokens (4 items)
  Key Facts: ~89 tokens (3 items)
  Passages: ~456 tokens (6 items)
  ----------------------------------------
  Formatted Context: ~2,703 tokens (total)

--- DEBUG INFO ---
  retrieval_time_ms: 165.4
  knapsack_efficiency: 0.87
  context_window_usage: 0.34
  total_memories_considered: 234
  memories_included: 18
```

**Use Cases:**
- Debugging: Verify which memories are retrieved for a given query
- Token optimization: Identify which context sections consume most tokens
- Context engineering: Test different retrieval parameters and see immediate impact
- Quality assurance: Ensure relevant memories are surfaced for user queries

The `--debug` flag requires the `tiktoken` library (`pip install tiktoken`).

---

## `/prompt`

**Description:** Shows the exact formatted messages sent to the LLM API, including full content and tool schemas.

**Syntax:**

```
/prompt
```

**Output Format:**

```
=== FORMATTED PROMPT (format: xml) ===

--- Message 1: SYSTEM ---
You are Friday, an AI assistant with persistent memory...

--- Message 2: User (turn 1) ---
How do I optimize this Python function?

--- Message 3: Friday (turn 1) ---
Let me analyze the function's time complexity...

--- Message 4: User (supporting context + query) ---
<context>
  <entities>...</entities>
  <insights>...</insights>
</context>

Current query: What about space complexity?

===========================
Total messages: 4

===========================
ACTIVE TOOLS (passed to LLM API as 'tools' parameter)
===========================
Function calling enabled with 8 tool(s):

  • read_file [filesystem]
    Read file contents with automatic encoding detection...
    Parameters: file_path, max_lines

  • execute_command [shell]
    Execute shell command with timeout and working directory...
    Parameters: command, cwd, timeout_seconds

  ...
```

**Differences from `/context`:**
- `/context` shows the logical payload before formatting
- `/prompt` shows the final LLM API request structure
- `/prompt` includes tool schemas that don't appear in `/context`
- `/prompt` shows exact role mapping (user/assistant/system)

**Use Cases:**
- LLM debugging: Verify exact prompt structure for troubleshooting unexpected responses
- Tool calling issues: Check if expected tools are included in API request
- Format validation: Ensure context format (XML/JSON/plain) is correct
- Prompt engineering: Optimize prompt structure for better LLM performance

This command shows the FULL prompt without truncation. For long contexts (>100K tokens), output may be very large.

---

## `/prime`

**Description:** Manually triggers session priming and displays the loaded context. Works before the first conversation turn.

**Syntax:**

```
/prime
```

**Behavior:**
- Executes ContextAssembler's priming logic
- Loads top entities by hit_count (Hebbian importance)
- Retrieves recent insights from vector store
- Fetches conversation summaries from prior sessions
- Populates `last_payload` for `/context` inspection
- Does NOT send a message to the LLM

**Output Format:**

```
=== PRIMED CONTEXT ===

Context loaded:
  Entities: 10
  Key Facts: 5
  Insights: 20
  Summaries: 3
  Relationships: 8
  Prior session turns: 12
  Current session turns: 0

--- Top Entities (by hit_count) ---
  - Python (Technology, hits: 45)
  - UserProject (Project, hits: 23)
  - Alice (Person, hits: 12)
  - Docker (Technology, hits: 10)
  ...

--- Relationship Summaries ---
  Alice USES Python (hits: 12)
  UserProject REQUIRES Python (hits: 8)
  ...

--- Recent Insights (most recent first) ---
  1. [2026-01-24 10:23] User prefers functional programming patterns
  2. [2026-01-23 15:44] User expressed concern about API latency
  ...

--- Recent Summaries (most recent first) ---
  1. [2026-01-24] Discussion about optimization strategies focusing on...
  2. [2026-01-23] Code review session covering authentication module...
  ...

--- Prior Session History ---
  Session: abc123def456...
    [2026-01-24 09:15] How do I configure Docker for production?...
    [2026-01-24 09:20] What are the security implications of...
  ...

===========================
Use /context for full details, /prompt to see formatted prompt.
```

**Configuration:**

Priming behavior is controlled by config.yaml:

```yaml
memory:
  priming:
    enabled: true
    top_n_entities: 10      # How many entities to load
    top_n_insights: 20      # How many insights to load
    recency_days: 30        # Only load from last 30 days
    include_summaries: true
    previous_sessions: 2    # Include history from last 2 sessions
```

**Use Cases:**
- Cold start testing: Verify what context Friday has before any conversation
- Priming configuration: Test different priming parameters and see results
- Session continuity: Confirm prior session context is loaded correctly
- Memory debugging: Check if expected entities/insights are prioritized

Priming is automatically executed on the first turn. This command allows manual inspection without sending a query.

---

## `/debug`

**Description:** Shows detailed debug information from the last context assembly operation.

**Syntax:**

```
/debug
```

**Output Format:**

```
Debug Information:
  retrieval_time_ms: 165.4
  knapsack_efficiency: 0.87
  context_window_usage: 0.34
  total_memories_considered: 234
  memories_included: 18
  episodic_query_ms: 23.1
  vector_query_ms: 87.3
  graph_query_ms: 55.0
  context_format: xml
  tool_schemas_size: 2,340 tokens
  warnings: context_window_near_limit
```

**Metrics Explained:**
- `retrieval_time_ms`: Total time to fetch memories from all stores
- `knapsack_efficiency`: How well the knapsack algorithm utilized available tokens (0-1)
- `context_window_usage`: Percentage of total context window consumed
- `total_memories_considered`: All candidate memories scored for inclusion
- `memories_included`: Final count of memories included in context
- `episodic/vector/graph_query_ms`: Individual store query latencies
- `warnings`: Issues detected (e.g., approaching token limits)

**Use Cases:**
- Performance tuning: Identify slow queries or inefficient retrieval
- Context optimization: Verify knapsack packing is efficient
- Capacity planning: Monitor context window usage trends
- Troubleshooting: Diagnose why expected memories weren't included

Debug info is only available after a turn has been processed. Run `/prime` or send a message first.

---

## `/entities [--limit N]`

**Description:** Lists all entities from the graph store with their metadata and relationships.

**Syntax:**

```
/entities
/entities --limit 50
```

**Parameters:**
- `--limit N` (optional): Maximum number of entities to display (default: 20, max: 500)

**Output Format:**

```
===========================
GRAPH STORE (entities & relationships)
===========================

Entities (42 total):

  [Person]
    - Alice (hits: 45)
    - Bob (hits: 23)
    - Dr. Chen (hits: 12)

  [Project]
    - UserProject (hits: 67)
    - OpenSourceLib (hits: 34)
    - ClientWebsite (hits: 18)

  [Technology]
    - Python (hits: 89)
    - Docker (hits: 56)
    - PostgreSQL (hits: 34)
    - React (hits: 28)

  [Concept]
    - FunctionalProgramming (hits: 23)
    - Microservices (hits: 15)

Relationships (87 total):
    Alice --[USES]--> Python
    Alice --[COLLABORATES_WITH]--> Bob
    UserProject --[REQUIRES]--> Python
    UserProject --[DEPLOYED_ON]--> Docker
    Dr. Chen --[AUTHORED]--> OpenSourceLib
    ...
    ... and 82 more
```

**Entity Metadata:**
- **Label**: Human-readable name
- **Type**: Entity category (Person, Project, Technology, Concept, etc.)
- **Hit Count**: Hebbian learning score — how often the entity has been accessed
- **Relationships**: Connected entities with semantic edge labels

**Use Cases:**
- Knowledge graph inspection: Visualize what Friday has learned about entities
- Hebbian learning verification: Check if frequently-mentioned entities have high hit counts
- Relationship discovery: Find connections between entities (multi-hop reasoning)
- Entity type analysis: Understand distribution of entity types in memory

Entities are sorted by type, then by hit_count descending. The `--limit` parameter applies per type, not globally.

---

## `/facts [--type TYPE]`

**Description:** Lists all documents from the vector store, including insights and summaries.

**Syntax:**

```
/facts
/facts --type insight
/facts --type summary
/facts --type meta_insight
```

**Parameters:**
- `--type TYPE` (optional): Filter by document type (insight, summary, meta_insight)

**Output Format:**

```
===========================
FACTS & INSIGHTS (from vector store)
===========================

Total documents: 156

1. User prefers functional programming patterns over object-oriented approaches when writing Python code
   [source: extraction, confidence: 0.92]

2. Project deadline confirmed as January 31, 2026, with stakeholder approval received on January 15
   [source: conversation, confidence: 0.88]

3. Performance bottleneck identified in database query optimization - considering Redis caching layer
   [source: inference, confidence: 0.75]

...
```

**Document Types:**
- **insight**: Extracted facts, preferences, decisions, observations
- **summary**: Turn-level conversation summaries
- **meta_insight**: High-level patterns synthesized from multiple insights

**Metadata Fields:**
- **source_type**: Origin of document (extraction, conversation, inference, synthesis)
- **confidence**: Quality score (0-1) assigned during extraction/synthesis
- **created_at**: Timestamp of document creation
- **turn_id**: Associated conversation turn (if applicable)

**Use Cases:**
- Memory audit: Review everything Friday has stored in vector memory
- Quality assurance: Check confidence scores of extracted insights
- Duplicate detection: Identify redundant or conflicting memories
- Content verification: Ensure sensitive information wasn't incorrectly captured

---

## `/insights`

**Description:** Filtered view of `/facts` showing only insights with structured metadata.

**Syntax:**

```
/insights
```

**Output Format:**

```
===========================
INSIGHTS (type='insight' from vector store)
===========================

Total insights: 89

1. User prefers functional programming patterns when writing Python code
   [topic: coding_style, sentiment: positive, confidence: 0.92, entities: Python, FunctionalProgramming]

2. Performance bottleneck identified in database queries
   [topic: optimization, sentiment: negative, confidence: 0.75, entities: PostgreSQL, UserProject]

3. Deadline pressure for January 31 release causing stress
   [topic: project_management, sentiment: negative, confidence: 0.88, entities: UserProject]

...
```

**Structured Metadata:**
- **topic**: Categorization (coding_style, optimization, project_management, preferences, etc.)
- **sentiment**: Emotional tone (positive, negative, neutral)
- **confidence**: Extraction quality score (0-1)
- **entities_mentioned**: List of related entities from graph store

**Insight Types:**
- **Preference**: User likes/dislikes, workflow preferences
- **Decision**: Choices made, directions selected
- **Observation**: Facts noticed, patterns observed
- **Concern**: Worries, blockers, risks identified

**Use Cases:**
- Preference learning: Track what Friday has learned about user preferences
- Decision history: Review major decisions and their context
- Sentiment analysis: Monitor user satisfaction and frustration patterns
- Entity linking: Verify insights are correctly associated with entities

Insights are the primary mechanism for Friday's adaptive learning. Quality insights lead to better context retrieval.

---

## `/summaries`

**Description:** Lists conversation turn summaries stored in vector memory.

**Syntax:**

```
/summaries
```

**Output Format:**

```
===========================
TURN SUMMARIES (type='summary' from vector store)
===========================

Total summaries: 15

1. Discussion about optimizing Python function performance, covering time and space complexity
   trade-offs. User expressed concern about current O(n²) implementation...
   [turn: abc12345..., created: 2026-01-24 10:23]

2. Code review session for authentication module, identifying security vulnerabilities in
   password hashing and suggesting bcrypt implementation with salt rounds...
   [turn: def67890..., created: 2026-01-24 09:45]

3. Troubleshooting Docker deployment issues, specifically networking configuration for
   multi-container setup. Resolved by switching from bridge to host network mode...
   [turn: ghi11213..., created: 2026-01-23 15:30]

...
```

**Metadata:**
- **turn_id**: Associated conversation turn (links to episodic store)
- **created_at**: Summary generation timestamp
- **token_count**: Approximate token count of summary (useful for budget planning)

**Use Cases:**
- Conversation review: Quickly scan past discussion topics without reading full transcripts
- Semantic search: Summaries are embedded and searchable by semantic similarity
- Context compression: Replace full turn history with summaries to save tokens
- Audit trail: Maintain high-level record of conversation flow over time

Summaries are generated automatically during memory extraction. The extraction LLM generates paragraph-length summaries capturing key points.

---

## `/meta`

**Description:** Displays meta-insights generated by memory synthesis operations.

**Syntax:**

```
/meta
```

**Output Format:**

```
===========================
META INSIGHTS (type='meta_insight' from vector store)
===========================

Total meta insights: 7

1. User consistently prefers functional programming patterns across Python, JavaScript, and Haskell
   codebases, with particular emphasis on immutability and pure functions
   [confidence: 0.94, source: synthesis, sources: 12 memories, created: 2026-01-24 11:30]

2. Performance optimization is a recurring concern across multiple projects, with focus on database
   queries, caching strategies, and algorithmic complexity
   [confidence: 0.89, source: synthesis, sources: 8 memories, created: 2026-01-24 11:30]

3. Docker deployment workflow causes friction due to slow build times and networking complexity,
   mentioned in context of UserProject, ClientWebsite, and OpenSourceLib
   [confidence: 0.87, source: synthesis, sources: 6 memories, created: 2026-01-23 18:45]

...
```

**Meta-Insight Characteristics:**
- **High-Level Patterns**: Synthesized from multiple related insights
- **Cross-Context**: Span multiple conversations, projects, or time periods
- **High Confidence**: Only generated when supporting evidence is strong
- **Source Tracking**: Links back to contributing insights for verification

**Generation:**

Meta-insights are created by the `/reorganize` command during synthesis operations:

```bash
/reorganize  # Runs full reorganization including synthesis
```

**Use Cases:**
- Pattern discovery: Identify recurring themes across many conversations
- User profiling: Build comprehensive understanding of user preferences and workflows
- Strategic insights: Surface high-level trends for decision-making
- Memory consolidation: Compress related insights into unified understanding

---

## `/reorganize [options]`

**Description:** Runs memory reorganization operations to optimize memory stores.

**Syntax:**

```
/reorganize                  # Full reorganization (all operations)
/reorganize --analyze-only   # Show what would be done (dry run)
/reorganize --skip-pruning   # Skip low-value memory removal
/reorganize --skip-synthesis # Skip meta-insight generation
/reorganize --skip-lifecycle # Skip promotion/decay operations
```

**Operations Performed:**

**1. Analysis Phase:**
- Analyzes memory store health
- Identifies candidates for pruning, promotion, decay
- Calculates memory fragmentation metrics

**2. Pruning Phase** (unless `--skip-pruning`):
- Removes low-confidence insights (< 0.3 confidence threshold)
- Deletes orphaned entities (no relationships, hit_count = 0)
- Cleans weak relationships (hit_count < 2, age > 30 days)

**3. Synthesis Phase** (unless `--skip-synthesis`):
- Groups related insights by topic and entities
- Generates meta-insights from insight clusters
- Stores meta-insights in vector store

**4. Lifecycle Phase** (unless `--skip-lifecycle`):
- Promotes short-term memories to long-term (based on scoring)
- Decays long-term memories to decayed (based on access patterns)
- Reactivates recently-accessed decayed memories

**Output Format:**

```
===========================
MEMORY REORGANIZATION
===========================

[1/4] Analyzing memory stores...
  Vector store: 156 documents analyzed
  Graph store: 42 entities, 87 relationships analyzed
  Episodic store: 342 turns analyzed

Memory Health:
  Fragmentation: Low (12% unused entries)
  Promotion candidates: 5 short-term memories
  Decay candidates: 8 long-term memories
  Pruning candidates: 3 low-confidence insights

[2/4] Pruning low-value memories...
  Removed 2 low-confidence insights
  Removed 1 orphaned entity (Technology: DeprecatedLib)
  Removed 4 weak relationships
  Archives saved to: ./exports/reorganize_backup_20260124_143022/

[3/4] Synthesizing meta-insights...
  Identified 3 insight clusters
  Generated 2 meta-insights
    - "User consistently prefers functional programming..."
    - "Performance optimization is recurring concern..."

[4/4] Running lifecycle operations...
  Promoted 4 memories to long-term
  Decayed 6 memories to decayed collection
  Reactivated 1 decayed memory

===========================
REORGANIZATION COMPLETE
===========================

Summary:
  Duration: 12.3 seconds
  Documents pruned: 7
  Meta-insights created: 2
  Memories promoted: 4
  Memories decayed: 6

Next run recommended: in 7 days
```

**Configuration:**

```yaml
memory:
  maintenance:
    pruning:
      confidence_threshold: 0.3
      orphan_age_days: 30
      weak_relationship_threshold: 2
    synthesis:
      cluster_similarity_threshold: 0.7
      min_cluster_size: 3
      meta_confidence_threshold: 0.8
    lifecycle:
      promotion_threshold: 0.7
      decay_lambda: 0.01
      reactivation_enabled: true
```

**Use Cases:**
- Periodic maintenance: Run weekly to keep memory stores optimized
- Performance recovery: Fix degraded memory performance
- Quality improvement: Generate meta-insights to enhance learning
- Storage management: Prune low-value data to manage storage costs

---

## `/lifecycle [options]`

**Description:** Manually triggers memory lifecycle operations (normally automatic).

**Syntax:**

```
/lifecycle              # Full cycle (promote, decay, reactivate)
/lifecycle --stats      # Show lifecycle statistics only
/lifecycle --promote    # Run promotion scoring only
/lifecycle --decay      # Run decay calculations only
/lifecycle --reactivate # Check for reactivation opportunities
```

**Lifecycle Stages:**

```
Short-Term  →  Long-Term  →  Decayed  →  (reactivation)  →  Long-Term
```

**Statistics Mode (`--stats`):**

```
===========================
MEMORY LIFECYCLE STATISTICS
===========================

Collection Distribution:
  Short-term: 23 documents
  Long-term: 134 documents
  Decayed: 12 documents
  Total: 169 documents

Promotion Candidates (short-term → long-term):
  Eligible: 5 documents (score >= 0.7)
  Pending age requirement: 3 documents (< 24 hours old)

Decay Candidates (long-term → decayed):
  Eligible: 8 documents (decay score <= 0.3)
  Protected by recent access: 15 documents

Reactivation Opportunities (decayed → long-term):
  Recently accessed: 1 document
```

**Scoring Algorithms:**

**Promotion Score** (0-1):

```
score = (age_factor * 0.3) + (access_factor * 0.4) + (confidence_factor * 0.2) + (connection_factor * 0.1)

where:
  age_factor = min(1.0, days_in_short_term / 7)
  access_factor = min(1.0, access_count / 5)
  confidence_factor = extraction_confidence
  connection_factor = min(1.0, entity_relationships / 3)
```

**Decay Score** (0-1, exponential):

```
score = e^(-lambda * days_since_last_access)

where:
  lambda = 0.01 (configurable decay rate)

Examples:
  24 hours: score = 0.79
  1 week:   score = 0.19
  2 weeks:  score = 0.04
```

**Configuration:**

```yaml
memory:
  lifecycle:
    promotion:
      threshold: 0.7          # Minimum score for promotion
      min_age_hours: 24       # Minimum time in short-term
    decay:
      lambda: 0.01            # Decay rate constant
      min_age_days: 7         # Minimum age before decay
      threshold: 0.3          # Decay below this score
    reactivation:
      enabled: true
      access_window_hours: 168 # 7 days
```

**Automatic vs. Manual:**
- **Automatic**: Runs after each turn if `auto_lifecycle: true` (default)
- **Manual**: Use this command to control timing or disable auto-lifecycle

Lifecycle operations are idempotent and safe to run frequently. Performance impact is minimal (<100ms for typical store sizes).

---

## Related Pages

- [Session Commands](/docs/cli/session/) — Start, resume, list, and export conversation sessions
- [Workflow Commands](/docs/cli/workflows/) — Run, validate, and manage workflow executions
- [Memory Architecture](/docs/memory/) — How memories are stored and retrieved across all three stores
