# Section 9: CLI Reference - memory-chat-v2.py

**Document Version:** 1.0
**Framework Version:** v0.1.0
**Last Updated:** 2026-01-24

---

## Overview

The `memory-chat-v2.py` CLI is Friday Framework's comprehensive interactive testing and development interface. It provides full access to Friday's memory systems, agent orchestration, workflow execution, and tool management through an intuitive command-line interface with Rich-based terminal output.

This reference documents all available commands, their parameters, output formats, and usage examples. Commands are organized by functional category for quick navigation.

**Target Audiences:**
- **Developers:** Testing memory operations, debugging context assembly, developing custom agents
- **Technical Executives:** Evaluating Friday's capabilities through hands-on exploration
- **AI Practitioners:** Understanding memory lifecycle, context engineering, and multi-agent orchestration

**Location:** `/tests/integration/memory/memory-chat-v2.py`

**Quick Start:**
```bash
# From project root
cd tests/integration/memory
python memory-chat-v2.py

# With custom config
python memory-chat-v2.py --config ../../config.yaml
```

---

## 9.1 Session Management Commands

Session management commands control the lifecycle of your Friday chat session, including initialization, cleanup, and state management.

### `/exit`, `/quit`

**Description:** Exits the chat session gracefully.

**Syntax:**
```
/exit
/quit
```

**Behavior:**
- Saves current session state to persistent storage
- Optionally triggers maintenance operations if configured with `on_exit: true` in session settings
- Archives conversation transcript to SQLite database
- Releases memory controller and LLM client resources
- Performs memory lifecycle operations (promotion/decay) if auto-lifecycle is enabled

**Parameters:** None

**Example:**
```
User: /exit
Friday: Goodbye! Session archived. Memory stats: 42 entities, 156 insights, 8 turns.
```

**Notes:**
- Safe to exit at any time - all state is persisted
- Re-running the CLI with the same session ID will restore full context
- For emergency termination, use Ctrl+C (may skip cleanup operations)

---

### `/clear`

**Description:** Clears conversation history for the current session without affecting long-term memories.

**Syntax:**
```
/clear
```

**Behavior:**
- Removes episodic memory (turn-by-turn conversation history) for current session
- Preserves long-term memories: entities in graph, insights in vector store, prior session history
- Resets turn counter to 0
- Clears cached context payload
- Maintains session ID and user ID for continuity

**Parameters:** None

**Use Cases:**
- Starting a new conversation topic without losing learned context
- Resetting after a long conversation to manage token budgets
- Testing memory retrieval without recent conversation interference
- Clearing sensitive conversation content while preserving knowledge

**Example:**
```
User: /clear
Friday: Conversation history cleared. Long-term memories preserved.
         Entities: 42 | Insights: 156 | Prior sessions: 3
```

**Developer Note:** This command only affects the episodic store. Vector and graph stores remain intact, enabling seamless context continuity across conversation restarts.

---

### `/reset`

**Description:** Complete memory wipe with full system reset. This is the "factory reset" command.

**Syntax:**
```
/reset
```

**Behavior:**
- **Clears all memory stores:**
  - Episodic: All conversation history (current + prior sessions)
  - Vector: All insights, summaries, and documents
  - Graph: All entities and relationships
- **Archives transcripts:** Exports all sessions to timestamped CSV files before deletion
- **Resets session state:** New session ID, fresh state initialization
- **Preserves configuration:** System config and tool registry remain unchanged

**Safety:**
- Requires confirmation prompt: "This will delete ALL memories. Continue? (yes/no)"
- Creates backup exports in `./exports/reset_backup_[timestamp]/`
- Irreversible after confirmation (except from backups)

**Parameters:** None

**Use Cases:**
- Starting completely fresh for testing or development
- Clearing corrupted memory state
- Resetting after experimental memory operations
- Preparing clean slate for production deployment

**Example:**
```
User: /reset
Friday: ⚠️  WARNING: This will delete ALL memories and archive transcripts.
        Continue? (yes/no): yes

        Archiving transcripts...
        ✓ Exported 5 sessions to ./exports/reset_backup_20260124_143022/

        Clearing memory stores...
        ✓ Episodic store cleared (1,234 turns deleted)
        ✓ Vector store cleared (567 documents deleted)
        ✓ Graph store cleared (89 entities, 234 relationships deleted)

        Reset complete. All memories cleared. Archives saved.
```

**Recovery:** Archives can be re-imported using the `/replay` command or by manually ingesting exported data.

---

## 9.2 Memory Inspection Commands

Memory inspection commands provide visibility into Friday's internal memory structures, context assembly, and prompt formatting.

### `/memory`

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

**Parameters:** None

**Use Cases:**
- Quick health check of memory system
- Verifying memory persistence after restart
- Monitoring memory growth over time
- Debugging missing memories (check collection counts)

**Developer Note:** This command queries all stores synchronously. For large deployments (>10K entities), consider adding pagination or filtering.

---

### `/context [--debug]`

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
- **Debugging:** Verify which memories are retrieved for a given query
- **Token Optimization:** Identify which context sections consume most tokens
- **Context Engineering:** Test different retrieval parameters and see immediate impact
- **Quality Assurance:** Ensure relevant memories are surfaced for user queries

**Developer Note:** The `--debug` flag requires `tiktoken` library. Install with: `pip install tiktoken`

---

### `/prompt`

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

**Parameters:** None

**Differences from `/context`:**
- `/context` shows the logical payload before formatting
- `/prompt` shows the final LLM API request structure
- `/prompt` includes tool schemas that don't appear in `/context`
- `/prompt` shows exact role mapping (user/assistant/system)

**Use Cases:**
- **LLM Debugging:** Verify exact prompt structure for troubleshooting unexpected responses
- **Tool Calling Issues:** Check if expected tools are included in API request
- **Format Validation:** Ensure context format (XML/JSON/plain) is correct
- **Prompt Engineering:** Optimize prompt structure for better LLM performance

**Developer Note:** This command shows the FULL prompt without truncation. For long contexts (>100K tokens), output may be very large.

---

### `/prime`

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
  Session: xyz789abc123...
    [2026-01-23 14:30] Can you review this pull request?...
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
- **Cold Start Testing:** Verify what context Friday has before any conversation
- **Priming Configuration:** Test different priming parameters and see results
- **Session Continuity:** Confirm prior session context is loaded correctly
- **Memory Debugging:** Check if expected entities/insights are prioritized

**Developer Note:** Priming is automatically executed on the first turn. This command allows manual inspection without sending a query.

---

### `/debug`

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

**Parameters:** None

**Metrics Explained:**
- **retrieval_time_ms**: Total time to fetch memories from all stores
- **knapsack_efficiency**: How well the knapsack algorithm utilized available tokens (0-1)
- **context_window_usage**: Percentage of total context window consumed
- **total_memories_considered**: All candidate memories scored for inclusion
- **memories_included**: Final count of memories included in context
- **episodic/vector/graph_query_ms**: Individual store query latencies
- **warnings**: Issues detected (e.g., approaching token limits)

**Use Cases:**
- **Performance Tuning:** Identify slow queries or inefficient retrieval
- **Context Optimization:** Verify knapsack packing is efficient
- **Capacity Planning:** Monitor context window usage trends
- **Troubleshooting:** Diagnose why expected memories weren't included

**Developer Note:** Debug info is only available after a turn has been processed. Run `/prime` or send a message first.

---

## 9.3 Memory Store Queries

Memory store query commands provide direct inspection of Friday's three-tier memory architecture.

### `/entities [--limit N]`

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
- **Hit Count**: Hebbian learning score - how often entity has been accessed
- **Relationships**: Connected entities with semantic edge labels

**Use Cases:**
- **Knowledge Graph Inspection:** Visualize what Friday has learned about entities
- **Hebbian Learning Verification:** Check if frequently-mentioned entities have high hit counts
- **Relationship Discovery:** Find connections between entities (multi-hop reasoning)
- **Entity Type Analysis:** Understand distribution of entity types in memory

**Developer Note:** Entities are sorted by type, then by hit_count descending. The `--limit` parameter applies per type, not globally.

---

### `/facts [--type TYPE]`

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

4. User expressed frustration with current deployment pipeline, specifically Docker build times exceeding 10 minutes
   [source: conversation, confidence: 0.91]

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
- **Memory Audit:** Review everything Friday has stored in vector memory
- **Quality Assurance:** Check confidence scores of extracted insights
- **Duplicate Detection:** Identify redundant or conflicting memories
- **Content Verification:** Ensure sensitive information wasn't incorrectly captured

**Developer Note:** This command queries ALL documents (limit: 10,000). For production systems, consider adding pagination.

---

### `/insights`

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
- **Preference Learning:** Track what Friday has learned about user preferences
- **Decision History:** Review major decisions and their context
- **Sentiment Analysis:** Monitor user satisfaction and frustration patterns
- **Entity Linking:** Verify insights are correctly associated with entities

**Developer Note:** Insights are the primary mechanism for Friday's adaptive learning. Quality insights lead to better context retrieval.

---

### `/summaries`

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

1. Discussion about optimizing Python function performance, covering time and space complexity trade-offs. User expressed concern about current O(n²) implementation...
   [turn: abc12345..., created: 2026-01-24 10:23]

2. Code review session for authentication module, identifying security vulnerabilities in password hashing and suggesting bcrypt implementation with salt rounds...
   [turn: def67890..., created: 2026-01-24 09:45]

3. Troubleshooting Docker deployment issues, specifically networking configuration for multi-container setup. Resolved by switching from bridge to host network mode...
   [turn: ghi11213..., created: 2026-01-23 15:30]

...
```

**Metadata:**
- **turn_id**: Associated conversation turn (links to episodic store)
- **created_at**: Summary generation timestamp
- **token_count**: Approximate token count of summary (useful for budget planning)

**Use Cases:**
- **Conversation Review:** Quickly scan past discussion topics without reading full transcripts
- **Semantic Search:** Summaries are embedded and searchable by semantic similarity
- **Context Compression:** Replace full turn history with summaries to save tokens
- **Audit Trail:** Maintain high-level record of conversation flow over time

**Developer Note:** Summaries are generated automatically during memory extraction. Extraction LLM generates paragraph-length summaries capturing key points.

---

### `/meta`

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

1. User consistently prefers functional programming patterns across Python, JavaScript, and Haskell codebases, with particular emphasis on immutability and pure functions
   [confidence: 0.94, source: synthesis, sources: 12 memories, created: 2026-01-24 11:30]

2. Performance optimization is a recurring concern across multiple projects, with focus on database queries, caching strategies, and algorithmic complexity
   [confidence: 0.89, source: synthesis, sources: 8 memories, created: 2026-01-24 11:30]

3. Docker deployment workflow causes friction due to slow build times and networking complexity, mentioned in context of UserProject, ClientWebsite, and OpenSourceLib
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
- **Pattern Discovery:** Identify recurring themes across many conversations
- **User Profiling:** Build comprehensive understanding of user preferences and workflows
- **Strategic Insights:** Surface high-level trends for decision-making
- **Memory Consolidation**: Compress related insights into unified understanding

**Developer Note:** Meta-insights use GPT-4 or Claude Sonnet for synthesis. Configure extraction LLM with sufficient capability for quality results.

---

## 9.4 Transcript Management

Transcript management commands provide access to Friday's persistent conversation storage and export capabilities.

### `/sessions`

**Description:** Lists all stored transcript sessions with metadata, marking those currently in context.

**Syntax:**
```
/sessions
```

**Output Format:**
```
===========================
TRANSCRIPT SESSIONS (23 total)
  In context: 3 (current + 2 prior)
===========================

  abc123def456 [CURRENT]
    Started: 2026-01-24 10:15:30
    User: developer@example.com
    Model: gpt-4o
    Turns: 8, Tokens: 12,450

  xyz789abc123 [IN CONTEXT]
    Started: 2026-01-23 14:20:15
    Ended: 2026-01-23 15:45:30
    User: developer@example.com
    Model: gpt-4o
    Turns: 15, Tokens: 24,680

  def456ghi789 [IN CONTEXT]
    Started: 2026-01-22 09:30:45
    Ended: 2026-01-22 10:15:20
    User: developer@example.com
    Model: claude-3.5-sonnet
    Turns: 6, Tokens: 8,900

  jkl012mno345
    Started: 2026-01-21 16:45:00
    Ended: 2026-01-21 17:30:15
    User: developer@example.com
    Model: gpt-4o
    Turns: 12, Tokens: 18,340

  ...

===========================
Use /transcript <session_id> to view a specific session.
```

**Markers:**
- **[CURRENT]**: The active session
- **[IN CONTEXT]**: Prior sessions included in priming (configured via `previous_sessions` setting)
- *No marker*: Archived sessions not currently in context

**Configuration:**
```yaml
memory:
  priming:
    previous_sessions: 2  # Include 2 most recent prior sessions in context
```

**Use Cases:**
- **Session Discovery:** Find past conversations by date or turn count
- **Context Verification:** Confirm which prior sessions are influencing current context
- **Resource Monitoring:** Track token usage across sessions
- **Model Comparison:** Review which models were used for different sessions

**Developer Note:** Sessions are ordered newest first. The "in context" count is determined by priming configuration.

---

### `/transcript [id]`

**Description:** Displays full conversation transcript from persistent storage.

**Syntax:**
```
/transcript              # Show current session
/transcript abc123def456 # Show specific session by ID
```

**Parameters:**
- `id` (optional): Session ID to display (default: current session)

**Output Format:**
```
===========================
TRANSCRIPT (8 entries) [CURRENT]
===========================

Session: abc123def456
Started: 2026-01-24 10:15:30
Model: gpt-4o
Total tokens: 12,450
Total latency: 45,230ms

--- Turn 1 [abc12345...] ---
Timestamp: 10:16:15

User:
How do I optimize this Python function for better performance?

Friday:
Let me analyze the performance characteristics of your function. To provide specific optimization recommendations, I'll need to understand the current implementation and identify bottlenecks.

First, let's examine the time complexity...

[tokens: 456, latency: 2,340ms]

--- Turn 2 [def67890...] ---
Timestamp: 10:18:22

User:
Here's the function: def process_data(items): return [item**2 for item in items]

Friday:
[Executed tool: analyze_code]
Your function has O(n) time complexity which is optimal for this operation. However, for large datasets, consider:

1. Using NumPy for vectorized operations (50-100x speedup)
2. Implementing batch processing if items don't fit in memory
3. Adding multiprocessing for CPU-bound transformations

Here's an optimized version...

[tokens: 890, latency: 3,120ms]

...

===========================
```

**Metadata Displayed:**
- **Turn number**: Sequential turn counter
- **Turn ID**: Unique identifier (first 8 chars shown)
- **Timestamp**: Time of turn within session
- **Messages**: Full user and assistant messages
- **Tool calls**: Executed tools with parameters and results (if applicable)
- **Metrics**: Token usage and latency per turn

**Use Cases:**
- **Conversation Review:** Read past interactions in full detail
- **Debugging:** Trace conversation flow and tool execution
- **Quality Assurance:** Verify Friday's responses were appropriate
- **Training Data**: Export conversations for fine-tuning (see `/export training`)

**Developer Note:** For long sessions (>100 turns), consider pagination or filtering by turn range. Current limit: 10,000 turns per query.

---

### `/transcript export`

**Description:** Exports entire transcript database to CSV files for archival or analysis.

**Syntax:**
```
/transcript export
```

**Behavior:**
- Creates timestamped export directory: `exports/transcript_export_[YYYYMMDD_HHMMSS]/`
- Generates multiple CSV files:
  - `sessions.csv`: Session metadata (ID, start/end time, user, model, token counts)
  - `entries.csv`: All conversation turns with full content
- Includes all sessions across all users (if multi-user deployment)
- Safe to run while system is active

**Output:**
```
===========================
TRANSCRIPT EXPORT COMPLETE
===========================

Export directory: ./exports/transcript_export_20260124_143022

Files created:
  - sessions.csv (23 sessions)
  - entries.csv (342 entries)

===========================
```

**CSV Format (sessions.csv):**
```csv
session_id,started_at,ended_at,user_id,model_name,total_turns,total_tokens,total_latency_ms
abc123def456,2026-01-24 10:15:30,,developer@example.com,gpt-4o,8,12450,45230
xyz789abc123,2026-01-23 14:20:15,2026-01-23 15:45:30,developer@example.com,gpt-4o,15,24680,67890
...
```

**CSV Format (entries.csv):**
```csv
id,session_id,turn_number,timestamp,user_message,assistant_message,prompt_tokens,completion_tokens,total_tokens,latency_ms
abc12345,abc123def456,1,2026-01-24 10:16:15,"How do I optimize...","Let me analyze...",234,222,456,2340
...
```

**Use Cases:**
- **Data Archival**: Backup all conversations before `/reset`
- **Analytics**: Import CSVs into analysis tools (Excel, Pandas, SQL)
- **Compliance**: Export data for regulatory requirements
- **System Migration**: Transfer transcripts between Friday deployments

**Security Note:** CSV exports may contain sensitive conversation data. Store exports securely and follow data retention policies.

---

### `/export [format]`

**Description:** Exports current session transcript in specified format.

**Syntax:**
```
/export              # Default: markdown
/export markdown     # Human-readable formatted transcript
/export jsonl        # JSON Lines for programmatic processing
/export training     # Chat-format training data
```

**Parameters:**
- `format` (optional): Output format (markdown, jsonl, training). Default: markdown

**Output Formats:**

**1. Markdown (`/export markdown`):**
```markdown
# Friday Conversation Transcript
**Session ID:** abc123def456
**Started:** 2026-01-24 10:15:30
**Model:** gpt-4o
**Total Tokens:** 12,450

---

## Turn 1
**Timestamp:** 10:16:15

**User:**
How do I optimize this Python function?

**Friday:**
Let me analyze the performance characteristics...

*Tokens: 456, Latency: 2.3s*

---

## Turn 2
...
```

**2. JSONL (`/export jsonl`):**
```jsonl
{"id":"abc12345","session_id":"abc123def456","turn_number":1,"timestamp":"2026-01-24T10:16:15Z","user_message":"How do I optimize...","assistant_message":"Let me analyze...","total_tokens":456,"latency_ms":2340}
{"id":"def67890","session_id":"abc123def456","turn_number":2,"timestamp":"2026-01-24T10:18:22Z","user_message":"Here's the function...","assistant_message":"Your function has...","total_tokens":890,"latency_ms":3120}
...
```

**3. Training (`/export training`):**
```jsonl
{"messages":[{"role":"system","content":"You are Friday..."},{"role":"user","content":"How do I optimize..."},{"role":"assistant","content":"Let me analyze..."}]}
{"messages":[{"role":"system","content":"You are Friday..."},{"role":"user","content":"Here's the function..."},{"role":"assistant","content":"Your function has..."}]}
...
```

**Export Location:** `./exports/transcript_[session_id]_[timestamp].[ext]`

**Use Cases:**
- **Documentation**: Share markdown transcripts with team members
- **Analysis**: Process JSONL with scripts or data tools
- **Fine-Tuning**: Use training format for model fine-tuning
- **Archival**: Long-term storage of specific conversations

**Format Comparison:**
| Format | Use Case | File Size | Human-Readable |
|--------|----------|-----------|----------------|
| Markdown | Documentation, sharing | Medium | Yes |
| JSONL | Programmatic processing | Small | No |
| Training | Model fine-tuning | Small | No |

**Example:**
```
User: /export training
Friday: Exported 8 training examples to: ./exports/transcript_abc123def456_20260124_143022_training.jsonl
```

---

## 9.5 Advanced Memory Operations

Advanced memory operations provide control over Friday's memory lifecycle, reorganization, and migration capabilities.

### `/reorganize [options]`

**Description:** Runs memory reorganization operations to optimize memory stores.

**Syntax:**
```
/reorganize                  # Full reorganization (all operations)
/reorganize --analyze-only   # Show what would be done (dry run)
/reorganize --skip-pruning   # Skip low-value memory removal
/reorganize --skip-synthesis # Skip meta-insight generation
/reorganize --skip-lifecycle # Skip promotion/decay operations
```

**Parameters:**
- `--analyze-only`: Preview reorganization without making changes
- `--skip-pruning`: Skip removal of low-value memories
- `--skip-synthesis`: Skip meta-insight generation from insights
- `--skip-lifecycle`: Skip lifecycle progression (promotion/decay)

**Operations Performed:**

**1. Analysis Phase:**
- Analyzes memory store health
- Identifies candidates for pruning, promotion, decay
- Calculates memory fragmentation metrics
- Estimates operation impact

**2. Pruning Phase** (unless `--skip-pruning`):
- Removes low-confidence insights (< 0.3 confidence threshold)
- Deletes orphaned entities (no relationships, hit_count = 0)
- Cleans weak relationships (hit_count < 2, age > 30 days)
- Archives pruned memories for recovery if needed

**3. Synthesis Phase** (unless `--skip-synthesis`):
- Groups related insights by topic and entities
- Generates meta-insights from insight clusters
- Calculates meta-insight confidence based on source quality
- Stores meta-insights in vector store

**4. Lifecycle Phase** (unless `--skip-lifecycle`):
- Promotes short-term memories to long-term (based on scoring)
- Decays long-term memories to decayed (based on access patterns)
- Reactivates recently-accessed decayed memories
- Updates lifecycle metadata

**Output Format:**
```
===========================
MEMORY REORGANIZATION
===========================

[1/4] Analyzing memory stores...
  ✓ Vector store: 156 documents analyzed
  ✓ Graph store: 42 entities, 87 relationships analyzed
  ✓ Episodic store: 342 turns analyzed

Memory Health:
  Fragmentation: Low (12% unused entries)
  Promotion candidates: 5 short-term memories
  Decay candidates: 8 long-term memories
  Pruning candidates: 3 low-confidence insights

[2/4] Pruning low-value memories...
  ✓ Removed 2 low-confidence insights
  ✓ Removed 1 orphaned entity (Technology: DeprecatedLib)
  ✓ Removed 4 weak relationships
  ✓ Archives saved to: ./exports/reorganize_backup_20260124_143022/

[3/4] Synthesizing meta-insights...
  ✓ Identified 3 insight clusters
  ✓ Generated 2 meta-insights
    - "User consistently prefers functional programming..."
    - "Performance optimization is recurring concern..."
  ✓ Meta-insights stored in vector store

[4/4] Running lifecycle operations...
  ✓ Promoted 4 memories to long-term
  ✓ Decayed 6 memories to decayed collection
  ✓ Reactivated 1 decayed memory

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
Reorganization behavior is controlled by maintenance config:
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
- **Periodic Maintenance:** Run weekly to keep memory stores optimized
- **Performance Recovery:** Fix degraded memory performance
- **Quality Improvement:** Generate meta-insights to enhance learning
- **Storage Management:** Prune low-value data to manage storage costs

**Scheduling:**
```bash
# Add to crontab for weekly reorganization
0 2 * * 0 cd /path/to/friday && python memory-chat-v2.py --batch "/reorganize"
```

**Developer Note:** Reorganization can be resource-intensive for large stores (>10K documents). Run during low-traffic periods.

---

### `/migrate [options]`

**Description:** Migrates existing memories to new schema versions or adds missing lifecycle metadata.

**Syntax:**
```
/migrate              # Add missing metadata (safe, add-only)
/migrate --force      # Overwrite existing metadata
/migrate --dry-run    # Preview migration without changes
```

**Parameters:**
- `--force`: Overwrite existing metadata (use with caution)
- `--dry-run`: Show migration plan without executing

**Migration Operations:**

**1. Lifecycle Metadata Migration:**
- Adds `lifecycle_stage` field (short_term/long_term/decayed)
- Adds `created_at` timestamp (if missing)
- Adds `last_accessed_at` timestamp
- Adds `access_count` counter for Hebbian tracking
- Adds `promotion_score` calculation fields

**2. Schema Version Migration:**
- Updates metadata structure to current version
- Migrates old collection names to new multi-collection architecture
- Converts deprecated fields to new formats

**Output Format:**
```
===========================
MEMORY MIGRATION
===========================

[1/3] Analyzing memories...
  ✓ Vector store: 156 documents scanned
  ✓ Graph store: 42 entities scanned

Migration needed:
  Documents missing lifecycle_stage: 23
  Documents missing created_at: 12
  Documents missing access_count: 34
  Entities missing hit_count: 0 (all up-to-date)

[2/3] Migrating memories...
  ✓ Added lifecycle_stage to 23 documents
  ✓ Added created_at to 12 documents (using current time)
  ✓ Added access_count to 34 documents (initialized to 0)
  ✓ Recalculated promotion_score for 23 documents

[3/3] Validating migration...
  ✓ All documents have required fields
  ✓ No schema violations detected

===========================
MIGRATION COMPLETE
===========================

Summary:
  Duration: 3.7 seconds
  Documents migrated: 34
  Entities migrated: 0
  Errors: 0
```

**Use Cases:**
- **Version Upgrades:** Migrate after Friday framework updates
- **Schema Changes:** Update memories when metadata structure changes
- **Data Quality:** Add missing fields to improve memory operations
- **Bulk Updates:** Apply configuration changes to existing memories

**Safety:**
- Default mode is add-only (no overwrites)
- Creates backup before migration: `./exports/migration_backup_[timestamp]/`
- `--dry-run` mode allows safe preview
- Validation step ensures data integrity

**Example (Dry Run):**
```
User: /migrate --dry-run
Friday: Migration plan (no changes will be made):
        - 23 documents would receive lifecycle_stage
        - 12 documents would receive created_at
        - 34 documents would receive access_count

        Run "/migrate" to execute migration.
```

**Developer Note:** Always run `--dry-run` first to verify migration plan. Migrations are idempotent (safe to run multiple times).

---

### `/lifecycle [options]`

**Description:** Manually triggers memory lifecycle operations (normally automatic).

**Syntax:**
```
/lifecycle              # Full cycle (promote, decay, reactivate)
/lifecycle --stats      # Show lifecycle statistics only
/lifecycle --promote    # Run promotion scoring only
/lifecycle --decay      # Run decay calculations only
/lifecycle --reactivate # Check for reactivation opportunities
```

**Parameters:**
- `--stats`: Display current lifecycle statistics without operations
- `--promote`: Run promotion scoring and promote eligible memories
- `--decay`: Run decay calculations and downgrade stale memories
- `--reactivate`: Check decayed memories for reactivation

**Lifecycle Stages:**
1. **Short-Term** → 2. **Long-Term** → 3. **Decayed** → (reactivation) → 2. **Long-Term**

**Output Format:**

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
  Eligible: 5 documents (score ≥ 0.7)
  Pending age requirement: 3 documents (< 24 hours old)

Decay Candidates (long-term → decayed):
  Eligible: 8 documents (decay score ≤ 0.3)
  Protected by recent access: 15 documents

Reactivation Opportunities (decayed → long-term):
  Recently accessed: 1 document

Average Scores:
  Short-term promotion score: 0.54
  Long-term decay score: 0.78
  Decayed reactivation potential: 0.12
```

**Full Cycle Mode (default):**
```
===========================
MEMORY LIFECYCLE CYCLE
===========================

[1/3] Promotion Phase (short-term → long-term)...
  ✓ Evaluated 23 short-term memories
  ✓ Promoted 4 memories to long-term
    - "User prefers functional programming..." (score: 0.89)
    - "Performance bottleneck in database..." (score: 0.76)
    - "Project deadline: January 31, 2026" (score: 0.81)
    - "Docker build time concerns" (score: 0.72)
  ⏸ Skipped 3 memories (< 24 hours old)

[2/3] Decay Phase (long-term → decayed)...
  ✓ Evaluated 134 long-term memories
  ✓ Decayed 6 memories to decayed collection
    - "Explored Redis caching (30 days ago)" (score: 0.18)
    - "Discussed TypeScript migration (45 days ago)" (score: 0.12)
    ...
  ✓ Protected 15 memories (accessed within 7 days)

[3/3] Reactivation Phase (decayed → long-term)...
  ✓ Evaluated 12 decayed memories
  ✓ Reactivated 1 memory to long-term
    - "Docker networking configuration" (accessed 2 hours ago)

===========================
LIFECYCLE CYCLE COMPLETE
===========================

Summary:
  Duration: 2.1 seconds
  Promoted: 4 memories
  Decayed: 6 memories
  Reactivated: 1 memory

Next automatic run: after next conversation turn
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
score = e^(-λ * days_since_last_access)

where:
  λ = 0.01 (configurable decay rate)

Examples:
  24 hours: score = 0.79
  1 week: score = 0.19
  2 weeks: score = 0.04
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

**Use Cases:**
- **Manual Control:** Override automatic lifecycle when testing
- **Monitoring:** Check lifecycle statistics for memory health
- **Debugging:** Force promotion/decay to test lifecycle behavior
- **Performance:** Run lifecycle separately from conversation turns

**Automatic vs. Manual:**
- **Automatic**: Runs after each turn if `auto_lifecycle: true` (default)
- **Manual**: Use this command to control timing or disable auto-lifecycle

**Developer Note:** Lifecycle operations are idempotent and safe to run frequently. Performance impact is minimal (<100ms for typical store sizes).

---

## 9.6 Tool Management Commands

Tool management commands provide inspection and control over Friday's tool system, including discovery, execution testing, and context injection.

### `/tools [category]`

**Description:** Lists available tools with metadata, optionally filtered by category.

**Syntax:**
```
/tools                # List all tools
/tools filesystem     # Filter by filesystem category
/tools web            # Filter by web category
```

**Parameters:**
- `category` (optional): Filter tools by category (filesystem, shell, web, git, data, text, code, integrations)

**Output Format:**
```
===========================
AVAILABLE TOOLS (52 total)
===========================

Filesystem Tools (8):
  • read_file
    Read file contents with automatic encoding detection and format parsing
    Parameters: file_path, max_lines
    Tags: filesystem, io, text

  • write_file
    Write content to file with automatic directory creation
    Parameters: file_path, content, mode
    Tags: filesystem, io, text

  • list_directory
    List directory contents with optional glob filtering and recursion
    Parameters: path, recursive, pattern
    Tags: filesystem, directory

  ...

Shell Tools (4):
  • execute_command
    Execute shell command with timeout and working directory control
    Parameters: command, cwd, timeout_seconds
    Tags: shell, system, execution

  • run_script
    Execute script with interpreter detection (Python, Bash, Node.js)
    Parameters: script_path, args, interpreter
    Tags: shell, execution, scripting

  ...

Web Tools (6):
  • http_request
    Perform HTTP request with headers, authentication, and timeout
    Parameters: url, method, headers, body, timeout
    Tags: web, http, api

  • web_search
    Search the web using configured search engine
    Parameters: query, max_results, region
    Tags: web, search, research

  ...

Git Tools (7):
  • git_status
    Show Git repository status including staged/unstaged changes
    Parameters: repo_path
    Tags: git, version-control

  • git_commit
    Create Git commit with message and optional file staging
    Parameters: repo_path, message, files
    Tags: git, version-control

  ...

[Additional categories: data, text, code, integrations...]
```

**Tool Metadata:**
- **Name**: Tool identifier for execution
- **Description**: Human-readable purpose (truncated to 80 chars)
- **Parameters**: Required and optional parameter names
- **Category**: Functional grouping
- **Tags**: Additional searchable keywords

**Use Cases:**
- **Tool Discovery:** Find available tools for specific tasks
- **Parameter Reference:** Check which parameters a tool accepts
- **Category Browsing:** Explore tools by functional area
- **Integration Planning:** Identify gaps in tool coverage

**Developer Note:** Tool list is generated from the tool registry configured in config.yaml. Add custom tools by extending the registry configuration.

---

### `/run-tool <name> [json]`

**Description:** Executes a tool directly with provided JSON parameters for testing.

**Syntax:**
```
/run-tool <tool_name> <json_params>
```

**Parameters:**
- `tool_name` (required): Name of tool to execute
- `json_params` (required): JSON object with tool parameters

**Examples:**

**1. Simple File Read:**
```
User: /run-tool read_file {"file_path": "/tmp/test.txt"}
Friday:
  Tool: read_file
  Status: success
  Duration: 0.023s

  Result:
  This is the content of the test file.
  Line 2 of the file.
  Line 3 of the file.

  Metadata:
    file_size: 89 bytes
    encoding: utf-8
    lines_read: 3
```

**2. Shell Command:**
```
User: /run-tool execute_command {"command": "ls -la /tmp", "timeout_seconds": 5}
Friday:
  Tool: execute_command
  Status: success
  Duration: 0.156s

  Result:
  total 48
  drwxrwxrwt  12 root  wheel   384 Jan 24 14:30 .
  drwxr-xr-x  20 root  wheel   640 Jan 15 09:15 ..
  -rw-r--r--   1 user  staff    89 Jan 24 14:30 test.txt
  ...

  Metadata:
    exit_code: 0
    cwd: /Users/user
```

**3. Web Request:**
```
User: /run-tool http_request {"url": "https://api.github.com/repos/python/cpython", "method": "GET"}
Friday:
  Tool: http_request
  Status: success
  Duration: 0.342s

  Result (truncated):
  {
    "id": 1903522,
    "name": "cpython",
    "full_name": "python/cpython",
    "description": "The Python programming language",
    ...
  }

  Metadata:
    status_code: 200
    content_type: application/json
    response_size: 4,567 bytes
```

**4. Tool Execution Error:**
```
User: /run-tool read_file {"file_path": "/nonexistent/file.txt"}
Friday:
  Tool: read_file
  Status: error
  Duration: 0.012s

  Error: FileNotFoundError: File not found: /nonexistent/file.txt

  Suggestion: Verify the file path exists and you have read permissions.
```

**Parameter Validation:**
The command validates parameters before execution:
```
User: /run-tool read_file {"wrong_param": "value"}
Friday:
  Error: Missing required parameter(s) for read_file: file_path

  Valid parameters:
    - file_path (string, required): Path to file to read
    - max_lines (integer, optional): Maximum lines to read
```

**Use Cases:**
- **Tool Testing:** Verify tool works correctly before using in agent workflows
- **Parameter Debugging:** Test different parameter combinations
- **Integration Validation:** Confirm external APIs/services are accessible
- **Documentation:** Generate example outputs for tool documentation

**Safety:**
- Tools execute with same permissions as Friday process
- Dangerous operations (delete, write) have confirmation prompts
- Timeout enforcement prevents hanging operations
- Sandboxing applies to code execution tools

**Developer Note:** This command bypasses the LLM and directly invokes tools. Useful for debugging tool implementations without LLM overhead.

---

### `/inject-tools <names>`

**Description:** Injects specified tools into context for testing, overriding recommendation algorithm.

**Syntax:**
```
/inject-tools <tool1>,<tool2>,<tool3>
```

**Parameters:**
- `names` (required): Comma-separated list of tool names (no spaces)

**Examples:**

**1. Inject Git Tools:**
```
User: /inject-tools git_status,git_diff,git_commit
Friday: Injected 3 tools into context:
        ✓ git_status [git]
        ✓ git_diff [git]
        ✓ git_commit [git]

        These tools will be available in all subsequent turns until /clear-tools is called.
```

**2. Inject Web and Data Tools:**
```
User: /inject-tools http_request,web_search,parse_json,jq_query
Friday: Injected 4 tools into context:
        ✓ http_request [web]
        ✓ web_search [web]
        ✓ parse_json [data]
        ✓ jq_query [data]
```

**3. Invalid Tool Name:**
```
User: /inject-tools read_file,nonexistent_tool,write_file
Friday: Warning: Tool not found: nonexistent_tool

        Injected 2 tools into context:
        ✓ read_file [filesystem]
        ✓ write_file [filesystem]

        Available tools: /tools
```

**Behavior:**
- Injected tools are included in EVERY LLM request
- Overrides the tool recommendation algorithm
- Persists until `/clear-tools` is called or session ends
- Consumes token budget (each tool schema ~100-500 tokens)

**Use Cases:**
- **Workflow Testing:** Force specific tools for testing multi-step workflows
- **Tool Development:** Test new tools in conversation without modifying recommendation logic
- **Debugging:** Isolate tool-related issues by controlling which tools are available
- **Demo/Presentation:** Ensure specific tools are available for demonstrations

**Token Budget Warning:**
```
User: /inject-tools [20 tools listed...]
Friday: Warning: Injecting 20 tools will consume ~4,500 tokens

        Current token budget allocation:
          Total: 8,000 tokens
          System prompt: 1,000 tokens
          History: 2,000 tokens
          Context: 2,500 tokens
          Tool schemas: 4,500 tokens (after injection)
          Query: 500 tokens

        This may exceed budget on long conversations.
        Consider using /tool-budget to adjust allocation.
```

**Developer Note:** Injected tools are stored in ContextAssembler state and persist across turns. Use sparingly to avoid token budget exhaustion.

---

### `/clear-tools`

**Description:** Removes all injected tools, returning to normal tool recommendation behavior.

**Syntax:**
```
/clear-tools
```

**Behavior:**
- Clears all tools previously injected via `/inject-tools`
- Restores automatic tool recommendation algorithm
- Freed token budget is reallocated to context/history
- Takes effect on next turn

**Parameters:** None

**Example:**
```
User: /clear-tools
Friday: Cleared 8 injected tools. Tool recommendation restored.

        The following tools will no longer be auto-included:
          - git_status, git_diff, git_commit
          - http_request, web_search
          - read_file, write_file, execute_command

        Tools will now be recommended based on query relevance.
```

**Use Cases:**
- **Reset Testing State:** Return to normal operation after testing
- **Token Budget Recovery:** Free up tokens consumed by injected tools
- **Algorithm Testing:** Compare behavior with/without forced tools

**Developer Note:** This command does NOT prevent tools from being recommended - it only removes the forced injection. The recommendation algorithm may still select the same tools if they're relevant to queries.

---

### `/recommend-tools <query>`

**Description:** Tests the tool recommendation algorithm for a given query without executing it.

**Syntax:**
```
/recommend-tools <query>
```

**Parameters:**
- `query` (required): User query to test recommendations for

**Output Format:**
```
===========================
TOOL RECOMMENDATIONS
===========================

Query: "How do I read and parse a JSON file?"

Recommended Tools (5):
  1. read_file (filesystem) - relevance: 0.92
     Reason: Query mentions "read" and "file"
     Parameters: file_path, max_lines

  2. parse_json (data) - relevance: 0.89
     Reason: Query specifically mentions "JSON" parsing
     Parameters: json_string

  3. jq_query (data) - relevance: 0.76
     Reason: Related to JSON data manipulation
     Parameters: json_string, query

  4. write_file (filesystem) - relevance: 0.54
     Reason: Common follow-up action after reading
     Parameters: file_path, content

  5. format_data (text) - relevance: 0.48
     Reason: Data formatting often follows parsing
     Parameters: data, format_type

Not Recommended (47 tools):
  - web_search (relevance: 0.12) - too low
  - git_status (relevance: 0.08) - no git keywords
  - execute_command (relevance: 0.23) - too low
  ...

Token Budget:
  Available for tools: 2,500 tokens
  Recommended tools cost: 1,234 tokens
  Remaining budget: 1,266 tokens

Recommendation Score Breakdown:
  Semantic similarity: 40%
  Keyword matching: 30%
  Historical usage: 20%
  Category relevance: 10%
```

**Recommendation Algorithm:**
1. **Semantic Similarity** (40%): Cosine similarity between query embedding and tool description embedding
2. **Keyword Matching** (30%): Presence of keywords in query (file, read, parse, JSON)
3. **Historical Usage** (20%): How often tool has been successfully used for similar queries
4. **Category Relevance** (10%): Category match based on query classification (filesystem, data, web, etc.)

**Use Cases:**
- **Algorithm Tuning:** Verify recommendation logic works as expected
- **Tool Coverage:** Identify gaps where expected tools aren't recommended
- **Query Engineering:** Test how query phrasing affects tool selection
- **Documentation:** Generate examples of when tools are/aren't recommended

**Example Testing Workflow:**
```bash
# Test 1: File operations
User: /recommend-tools "Read the config.yaml file"
# Verify read_file is top recommendation

# Test 2: Web operations
User: /recommend-tools "Search for Python documentation"
# Verify web_search is top recommendation

# Test 3: Git operations
User: /recommend-tools "Show me the git status and create a commit"
# Verify git_status and git_commit are recommended
```

**Developer Note:** This command does NOT modify context or send requests to the LLM. It's purely for testing the recommendation algorithm.

---

### `/tool-budget`

**Description:** Displays current tool token budget allocation and usage statistics.

**Syntax:**
```
/tool-budget
```

**Output Format:**
```
===========================
TOOL TOKEN BUDGET
===========================

Total Context Window: 8,000 tokens

Current Allocation:
  System Prompt:    1,000 tokens (12.5%)
  History:          2,000 tokens (25.0%)
  Context:          2,500 tokens (31.3%)
  Tool Schemas:     2,000 tokens (25.0%)
  Query Reserve:      500 tokens (6.3%)

Tool Schema Usage:
  Currently included: 8 tools
  Total schema size: 1,234 tokens (61.7% of budget)
  Remaining capacity: 766 tokens
  Estimated tools remaining: ~3-4 more tools

Included Tools (1,234 tokens):
  1. read_file (152 tokens)
  2. write_file (143 tokens)
  3. git_status (89 tokens)
  4. git_commit (178 tokens)
  5. http_request (234 tokens)
  6. web_search (156 tokens)
  7. parse_json (134 tokens)
  8. execute_command (148 tokens)

Tool Budget Efficiency:
  Average tool size: 154 tokens
  Tools per 1K tokens: ~6.5 tools

Budget Warnings:
  ⚠️  Context allocation (31.3%) is high - may limit tool availability
  ⚠️  Tool budget (25.0%) is near capacity - recommend priority selection

Recommendations:
  - Consider reducing history token allocation to increase tool budget
  - Use /inject-tools to explicitly select critical tools
  - Enable tool categories to limit schema sizes
  - Increase total context window if model supports it
```

**Configuration:**
Token budget is configured in config.yaml:
```yaml
memory:
  context:
    total_tokens: 8000
    budgets:
      system_prompt: 1000
      history: 2000
      context: 2500
      tools: 2000
      query: 500
```

**Use Cases:**
- **Capacity Planning:** Determine how many tools fit in available budget
- **Optimization:** Identify which sections consume most tokens
- **Debugging:** Diagnose why expected tools aren't included (budget exhausted)
- **Configuration Tuning:** Adjust budget allocations for specific use cases

**Budget Optimization Strategies:**

**1. Reduce History Budget:**
```yaml
budgets:
  history: 1500  # Down from 2000
  tools: 2500    # Up from 2000
```

**2. Enable Tool Categories:**
```python
# Only include filesystem and git tools
context_assembler.set_tool_categories(["filesystem", "git"])
```

**3. Use Larger Context Window:**
```yaml
llm:
  model: "gpt-4-turbo"  # 128K context vs. 8K
  context:
    total_tokens: 32000  # 4x increase
```

**Developer Note:** Token counts are estimates using tiktoken with cl100k_base encoding. Actual counts may vary by ±5% depending on model tokenizer.

---

## 9.7 Agent Orchestration Commands (Phase 3)

Agent orchestration commands enable multi-agent collaboration, explicit routing, delegation, and agent lifecycle management.

**Prerequisites:**
- Phase 3 (Project Hive) features must be enabled
- Agent definitions configured in `agents/` directory
- Orchestrator initialized in config.yaml

---

### `/switch [agent]`

**Description:** Switches active agent or displays current agent status.

**Syntax:**
```
/switch              # Show current agent
/switch researcher   # Switch to researcher agent
/switch coder        # Switch to coder agent
```

**Parameters:**
- `agent` (optional): Agent name to switch to (omit to show status)

**Output Format (Status):**
```
===========================
AGENT STATUS
===========================

Current Agent: friday-assistant
  Role: General-purpose AI assistant
  Goal: Help users with tasks requiring memory and reasoning
  Model: gpt-4o
  Tools: 52 available (all categories)
  Memory Mode: full (episodic + semantic + associative)

Available Agents (3):
  • friday-assistant [ACTIVE]
    General-purpose assistant with full capabilities

  • researcher
    Research and information gathering specialist

  • coder
    Code generation and debugging specialist
```

**Output Format (Switch):**
```
User: /switch researcher
Friday: Switched to agent: researcher

  Role: Research and information gathering specialist
  Goal: Find, analyze, and synthesize information from multiple sources
  Model: gpt-4o
  Tools: 8 tools (web, data)
  Memory Mode: vector_only (semantic search optimized)

  Ready for research tasks!
```

**Behavior:**
- Switches active agent for all subsequent messages
- Preserves conversation history (visible to new agent)
- Maintains session ID and memory access
- Agent-specific tools and prompts take effect immediately

**Use Cases:**
- **Task-Specific Agents:** Switch to specialist agent for focused tasks
- **Model Testing:** Compare responses from agents using different models
- **Tool Isolation:** Limit tool access by switching to restricted agents
- **Workflow Transitions:** Hand off from research agent to coder agent

**Agent Persistence:**
```
# Session 1
User: /switch researcher
User: Find papers on transformers

# Session 2 (later)
User: (continues conversation with researcher agent)
```

**Developer Note:** Agent switch does NOT create a new session. Both agents share the same memory controller and transcript.

---

### `/agents`

**Description:** Lists all registered agents with their capabilities and configurations.

**Syntax:**
```
/agents
```

**Output Format:**
```
===========================
AVAILABLE AGENTS (4 total)
===========================

friday-assistant [ACTIVE] [DEFAULT]
  Role: General-purpose AI assistant
  Goal: Help users with tasks requiring memory and reasoning
  Capabilities:
    - Full memory access (episodic + semantic + associative)
    - All tool categories (52 tools)
    - Model: gpt-4o (temperature: 0.7)
  Status: Active (12 messages in current session)
  Tags: general, assistant, full-capability

researcher
  Role: Research and information gathering specialist
  Goal: Find, analyze, and synthesize information from multiple sources
  Capabilities:
    - Vector-only memory (semantic search optimized)
    - Web and data tools only (8 tools)
    - Model: gpt-4o (temperature: 0.3)
  Status: Registered (not yet loaded)
  Tags: research, web, analysis

coder
  Role: Code generation and debugging specialist
  Goal: Write, review, and debug code across multiple languages
  Capabilities:
    - Full memory access
    - Filesystem, shell, git, code tools (24 tools)
    - Model: claude-3.5-sonnet (temperature: 0.5)
  Status: Cached (instantiated, ready for use)
  Tags: code, development, git

reviewer
  Role: Code review and quality assurance specialist
  Goal: Review code for bugs, style, security, and best practices
  Capabilities:
    - Vector-only memory (semantic search for patterns)
    - Code analysis tools only (6 tools)
    - Model: gpt-4o (temperature: 0.2)
  Status: Registered (not yet loaded)
  Tags: review, quality, security

===========================
Use /agent <name> for detailed information
Use /switch <name> to change active agent
```

**Agent Status Types:**
- **Active**: Currently processing messages
- **Cached**: Loaded in memory, ready for immediate use
- **Registered**: Defined in YAML, not yet instantiated

**Capability Summary:**
- **Memory Mode**: full, vector_only, graph_only, episodic_only, none
- **Tool Access**: Number and categories of available tools
- **Model Config**: LLM model, temperature, max_tokens

**Use Cases:**
- **Agent Discovery:** See available agents for different tasks
- **Capability Comparison:** Compare agent configurations
- **Resource Management:** Identify which agents are loaded vs. registered
- **Team Planning:** Design multi-agent workflows based on capabilities

---

### `/agent [name]`

**Description:** Shows detailed configuration and runtime information for a specific agent.

**Syntax:**
```
/agent              # Show active agent details
/agent researcher   # Show specific agent details
```

**Parameters:**
- `name` (optional): Agent name (default: active agent)

**Output Format:**
```
===========================
AGENT DETAILS: researcher
===========================

Identity:
  Name: researcher
  Role: Research and information gathering specialist
  Goal: Find, analyze, and synthesize information from multiple sources
  Version: 1.2.0
  Author: friday-team

Configuration:
  Model: gpt-4o
  Temperature: 0.3
  Max Tokens: 4000
  Memory Mode: vector_only

Tools (8):
  Web Tools:
    - http_request: HTTP client with auth support
    - web_search: Search engine integration
    - scrape_page: HTML parsing and extraction
    - download_file: File downloads with progress

  Data Tools:
    - parse_json: JSON parsing and validation
    - parse_yaml: YAML parsing
    - jq_query: JSONPath/jq-style queries
    - format_data: Pretty-printing with syntax highlighting

Memory Access:
  Mode: vector_only
  Namespace: default
  Priming: disabled (stateless research tasks)

System Prompt (excerpt):
  You are a research specialist focused on finding and analyzing
  information from web sources. Your strengths include:
  - Comprehensive web search across multiple sources
  - Critical evaluation of source credibility
  - Synthesis of information into coherent summaries
  ...

Current State:
  Status: Cached (ready for use)
  Message Count: 0 (not yet used in this session)
  Average Latency: N/A
  Total Tokens Used: 0

Tags: research, web, analysis, specialist
```

**Use Cases:**
- **Configuration Verification:** Check agent settings before use
- **Debugging:** Verify tools and memory mode are correct
- **Documentation:** Generate agent capability documentation
- **Development:** Review agent prompt and configuration

---

### `/delegate <agent> <task>`

**Description:** Delegates a task to another agent and returns result to current agent.

**Syntax:**
```
/delegate <agent_name> <task_description>
```

**Parameters:**
- `agent_name` (required): Name of agent to delegate to
- `task_description` (required): Task instructions for delegated agent

**Examples:**

**1. Research Delegation:**
```
User: I need to build a web scraper in Python
Friday (assistant): Let me gather information about Python web scraping libraries first.

/delegate researcher Find comprehensive information about Python web scraping libraries, including BeautifulSoup, Scrapy, and Selenium. Compare features, performance, and use cases.

[Researcher agent processes task...]

Researcher: Based on my research:

  BeautifulSoup:
    - Best for: Simple HTML parsing
    - Performance: Good for small-medium sites
    - Learning curve: Easy

  Scrapy:
    - Best for: Large-scale scraping projects
    - Performance: Excellent (asynchronous)
    - Learning curve: Moderate

  Selenium:
    - Best for: JavaScript-heavy sites
    - Performance: Slower (browser automation)
    - Learning curve: Moderate

  Recommendation: Use BeautifulSoup for your use case (simple product data extraction)

Friday (assistant): Based on the research, here's a BeautifulSoup implementation...
```

**2. Code Review Delegation:**
```
User: /delegate reviewer Check this authentication code for security issues: [code block]

[Reviewer agent analyzes code...]

Reviewer: Security analysis complete:

  Critical Issues (2):
    1. Password stored in plaintext (line 23)
       Recommendation: Use bcrypt for password hashing

    2. SQL query vulnerable to injection (line 45)
       Recommendation: Use parameterized queries

  Warnings (3):
    1. No rate limiting on login endpoint
    2. Session token uses weak random generator
    3. Missing CSRF protection

  Full report with code suggestions: [attached]

Friday (assistant): I've integrated the reviewer's findings. Let me show you how to fix each issue...
```

**3. Multi-Hop Delegation:**
```
User: Build and test a REST API endpoint

Friday (assistant): I'll coordinate this task across specialists.

/delegate coder Implement a REST API endpoint for user registration with email validation

[Coder agent implements endpoint...]

/delegate reviewer Review the implementation for bugs and best practices

[Reviewer agent analyzes code...]

/delegate coder Fix the issues identified: [list of issues]

[Coder agent updates code...]

Friday (assistant): The endpoint is implemented and reviewed. Here's the final code with tests...
```

**Behavior:**
- Delegated agent executes task with full tool access
- Result is returned to calling agent
- Conversation continues with original agent
- Both agents' work is recorded in transcript with provenance

**Memory Implications:**
- Delegated work is visible to both agents (shared memory)
- Provenance metadata tracks which agent contributed what
- Insights extracted by delegated agent are available to all agents

**Use Cases:**
- **Specialization:** Leverage specialist agents for subtasks
- **Workflow Orchestration:** Chain multiple agents for complex tasks
- **Parallel Execution:** Delegate to multiple agents simultaneously (future)
- **Human Simulation:** Model team collaboration patterns

**Developer Note:** Delegation is synchronous by default. Calling agent waits for delegated agent to complete before continuing.

---

### `/status`

**Description:** Shows comprehensive orchestrator status including active agents and cached agents.

**Syntax:**
```
/status
```

**Output Format:**
```
===========================
ORCHESTRATOR STATUS
===========================

Active Agent: friday-assistant
  Messages in session: 12
  Tool calls: 8
  Average latency: 2.3s
  Total tokens: 18,450

Default Agent: friday-assistant
  Fallback: Used when @routing fails or no agent specified

Session Info:
  Session ID: abc123def456
  User ID: developer@example.com
  Started: 2026-01-24 10:15:30
  Duration: 1h 23m

Cached Agents (2):
  • friday-assistant [ACTIVE]
    Loaded: 1h 23m ago
    Messages: 12
    State: Ready

  • coder
    Loaded: 45m ago
    Messages: 3 (from delegation)
    State: Ready

Registered Agents (2):
  • researcher
    Status: Not yet loaded

  • reviewer
    Status: Not yet loaded

Resource Usage:
  Memory: 234 MB (all agents)
  LLM Calls: 12 (friday-assistant), 3 (coder)
  Total Cost: $0.45 (estimated)

Orchestration Stats:
  @routing uses: 0
  Delegations: 2
  Agent switches: 1
```

**Use Cases:**
- **Session Monitoring:** Check current orchestration state
- **Resource Management:** See which agents are loaded and consuming memory
- **Cost Tracking:** Monitor LLM API usage across agents
- **Performance Analysis:** Compare latency and token usage per agent

---

### `@agent_name <message>`

**Description:** Direct routing syntax for explicitly addressing a specific agent.

**Syntax:**
```
@<agent_name> <message>
```

**Parameters:**
- `agent_name` (required): Agent to route message to
- `message` (required): Message for the agent

**Examples:**

**1. Research Request:**
```
User: @researcher Find papers on transformer architectures published after 2023
Researcher: I'll search for recent transformer papers...

[Tool: web_search executed...]

Found 8 relevant papers:
1. "Attention Is Still All You Need: Optimizations in 2024"
   Authors: Smith et al., Published: 2024-01

2. "Efficient Transformers for Edge Devices"
   Authors: Chen et al., Published: 2023-12

...

Would you like summaries of specific papers?
```

**2. Code Generation:**
```
User: @coder Implement a binary search tree in Python with insert and search methods
Coder: I'll implement a BST with proper documentation and type hints.

[Tool: write_file executed...]

Created: bst.py

Here's the implementation:

```python
class TreeNode:
    """Node in a binary search tree."""
    def __init__(self, value: int):
        self.value = value
        self.left: TreeNode | None = None
        self.right: TreeNode | None = None

class BinarySearchTree:
    ...
```

All methods include docstrings and type hints. Would you like me to add unit tests?
```

**3. Code Review:**
```
User: @reviewer Check this function for bugs:
      def calculate_average(numbers):
          return sum(numbers) / len(numbers)

Reviewer: Analysis complete:

Critical Issue:
  - ZeroDivisionError if numbers list is empty (line 2)

Recommendation:
```python
def calculate_average(numbers):
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)
```

Consider also:
  - Add type hints: def calculate_average(numbers: list[float]) -> float
  - Handle None input gracefully
  - Document expected input types in docstring
```

**Routing Behavior:**
- Message is sent to specified agent (not active agent)
- Response is attributed to routed agent
- Routing is visible in transcript with provenance
- Active agent does NOT change (unlike `/switch`)

**Differences from `/switch`:**
- `@routing`: Single message to specific agent, then returns to active agent
- `/switch`: Changes active agent for ALL subsequent messages

**Use Cases:**
- **One-Off Queries:** Ask specialist agent without switching context
- **Agent Comparison:** Test same query with different agents
- **Workflow Composition:** Coordinate multiple agents in single conversation
- **Human-Like Team:** Simulate team communication patterns

**Multi-Agent Conversation:**
```
User: I need to build a web scraper

Friday (assistant): I'll coordinate with our specialists.

User: @researcher What's the best Python library for scraping?
Researcher: Based on your requirements, I recommend BeautifulSoup for simplicity...

User: @coder Implement a scraper using BeautifulSoup for the recommended approach
Coder: Here's the implementation with error handling and rate limiting...

User: @reviewer Check the scraper for issues
Reviewer: Found 2 potential issues: [details]...

User: @coder Fix those issues
Coder: Updated the implementation with fixes...

Friday (assistant): The scraper is ready. Would you like me to document it?
```

**Developer Note:** @routing does not consume additional tokens for agent loading. The routed agent uses its own system prompt and tool set for that single turn.

---

## 9.8 Workflow Commands (Phase 4)

Workflow commands enable execution of complex multi-step automation with task graphs, variable passing, and human-in-the-loop approval gates.

**Prerequisites:**
- Phase 4 (Project Hive) features must be enabled
- Workflow definitions in `workflows/` directory (YAML format)
- Workflow engine initialized in config.yaml

---

### `/workflow list`

**Description:** Lists all available workflows from the workflows directory.

**Syntax:**
```
/workflow list
```

**Output Format:**
```
===========================
AVAILABLE WORKFLOWS (3 total)
===========================

newsletter
  Description: Generate newsletter from research and writing workflow
  Version: 1.0.0
  Author: friday-team
  Tasks: 3 (research → review_gate → write)
  Estimated Duration: 5-10 minutes
  Tags: content, automation, research

code-review
  Description: Automated code review pipeline with testing and security analysis
  Version: 1.2.0
  Author: friday-team
  Tasks: 4 (analyze → test → security_scan → review_gate)
  Estimated Duration: 2-5 minutes
  Tags: code, quality, security

research-report
  Description: Comprehensive research and report generation workflow
  Version: 1.0.0
  Author: friday-team
  Tasks: 5 (search → summarize → synthesize → fact_check_gate → format)
  Estimated Duration: 10-15 minutes
  Tags: research, analysis, reporting

===========================
Use /workflow run <name> to execute
Use /workflow run <name> --help for input parameters
```

**Workflow Metadata:**
- **Name**: Workflow identifier for execution
- **Description**: Human-readable purpose
- **Version**: Semantic version for change tracking
- **Tasks**: Task count and workflow structure preview
- **Estimated Duration**: Expected execution time (excluding approval waits)
- **Tags**: Searchable categories

**Use Cases:**
- **Workflow Discovery:** Find available automation workflows
- **Capability Planning:** Understand what workflows can accomplish
- **Template Selection:** Choose appropriate workflow for task

---

### `/workflow run <name> [inputs]`

**Description:** Executes a workflow with optional input variables.

**Syntax:**
```
/workflow run <workflow_name>
/workflow run <workflow_name> var1="value1" var2="value2"
/workflow run <workflow_name> --help
```

**Parameters:**
- `workflow_name` (required): Workflow to execute
- `inputs` (optional): Space-separated key=value pairs (use quotes for multi-word values)
- `--help`: Show required/optional inputs for workflow

**Examples:**

**1. Newsletter Workflow:**
```
User: /workflow run newsletter user_topic="AI trends in 2026" urgency="high"

Workflow: newsletter
Execution ID: exec_abc123

[Task 1/3] research (assigned to: researcher)
  Status: RUNNING
  Gathering information about AI trends in 2026...

  [Tool: web_search executed...]
  [Tool: scrape_page executed...]

  ✓ Research complete (12 sources found)
  Output: research_summary → "Recent AI trends include..."

[Task 2/3] review_gate (APPROVAL REQUIRED)
  Status: WAITING_APPROVAL

  Task: Review research findings before proceeding to writing
  Input: research_summary

  Research Preview:
    - Large language models continue rapid development
    - AI regulation frameworks emerging in EU and US
    - Multimodal AI becoming mainstream
    ...

  Approve this research? (/workflow approve or /workflow skip)

User: /workflow approve

[Task 2/3] review_gate
  Status: APPROVED

[Task 3/3] write (assigned to: coder)
  Status: RUNNING
  Writing newsletter based on approved research...

  ✓ Newsletter draft complete
  Output: newsletter_content → [full content]

===========================
WORKFLOW COMPLETE
===========================

Execution ID: exec_abc123
Duration: 3m 45s
Status: COMPLETED

Final Outputs:
  newsletter_content:
    # AI Trends Newsletter - January 2026

    ## Top Developments This Month

    1. **GPT-5 Release**: OpenAI announced GPT-5 with improved reasoning...
    2. **EU AI Act Implementation**: New regulations take effect...
    3. **Multimodal Breakthroughs**: Models combining text, image, audio...
    ...

    [Full newsletter: 1,234 words]

Use /workflow status for detailed execution log
```

**2. Code Review Workflow:**
```
User: /workflow run code-review repo_path="/path/to/repo" target_branch="feature/auth"

Workflow: code-review
Execution ID: exec_def456

[Task 1/4] analyze (assigned to: coder)
  Status: RUNNING
  Running static analysis on feature/auth...

  [Tool: execute_command executed: ruff check...]
  [Tool: execute_command executed: mypy...]

  ✓ Analysis complete
  Issues found: 3 warnings, 0 errors

[Task 2/4] test (assigned to: coder)
  Status: RUNNING
  Running test suite...

  [Tool: execute_command executed: pytest...]

  ✓ Tests passed (45/45)

[Task 3/4] security_scan (assigned to: reviewer)
  Status: RUNNING
  Scanning for security vulnerabilities...

  ✓ Security scan complete
  Issues found: 1 medium-severity issue (SQL injection potential)

[Task 4/4] review_gate (APPROVAL REQUIRED)
  Status: WAITING_APPROVAL

  Summary:
    Static Analysis: 3 warnings
    Tests: 45/45 passed
    Security: 1 medium-severity issue

  Approve merge? (/workflow approve or /workflow skip)

User: /workflow skip

[Task 4/4] review_gate
  Status: SKIPPED

===========================
WORKFLOW COMPLETE
===========================

Status: COMPLETED (with skipped tasks)

Note: Final review gate was skipped. Address security issue before merging.
```

**3. Input Validation:**
```
User: /workflow run newsletter
Error: Missing required input(s): user_topic

Required Inputs:
  - user_topic (string): Topic for newsletter content

Optional Inputs:
  - urgency (string): Priority level (low/medium/high), default: medium
  - max_sources (integer): Maximum research sources, default: 10

Example: /workflow run newsletter user_topic="AI trends" urgency="high"
```

**Variable Syntax:**
- Simple values: `topic="AI trends"`
- Numbers: `max_sources=10`
- Booleans: `include_images=true`
- Quoted strings: `description="A multi-word description with spaces"`

**Use Cases:**
- **Task Automation:** Execute complex multi-step workflows
- **Quality Gates:** Require human approval before critical operations
- **Reproducible Processes:** Standardize common workflows
- **Agent Coordination:** Orchestrate multiple agents with dependencies

**Developer Note:** Workflows execute asynchronously. Progress is streamed in real-time if terminal supports it.

---

### `/workflow status`

**Description:** Shows current workflow execution status with task breakdown.

**Syntax:**
```
/workflow status
```

**Output Format (Running):**
```
===========================
WORKFLOW STATUS
===========================

Workflow: newsletter
Execution ID: exec_abc123
Started: 2026-01-24 14:30:15
Duration: 2m 34s

Overall Status: RUNNING

Tasks:
  ✓ [COMPLETED] research (assigned to: researcher)
      Duration: 1m 45s
      Output: research_summary

  ⏸ [WAITING_APPROVAL] review_gate (approval required)
      Waiting since: 2026-01-24 14:32:00 (34s ago)
      Input: research_summary (12 sources)

  ⏹ [PENDING] write (assigned to: coder)
      Dependencies: review_gate (waiting)

Variables:
  Inputs:
    user_topic: "AI trends in 2026"
    urgency: "high"

  Outputs:
    research_summary: [loaded, 2,345 chars]
    newsletter_content: (not yet generated)

Next Action:
  Review research findings and approve/skip review_gate
  Commands: /workflow approve | /workflow skip
```

**Output Format (Completed):**
```
===========================
WORKFLOW STATUS
===========================

Workflow: newsletter
Execution ID: exec_abc123
Started: 2026-01-24 14:30:15
Completed: 2026-01-24 14:33:48
Duration: 3m 33s

Overall Status: COMPLETED

Tasks:
  ✓ [COMPLETED] research (assigned to: researcher)
      Duration: 1m 45s

  ✓ [COMPLETED] review_gate (approved by user)
      Duration: 34s (approval wait time)

  ✓ [COMPLETED] write (assigned to: coder)
      Duration: 1m 14s

Final Outputs:
  research_summary: [2,345 chars]
  newsletter_content: [5,678 chars]

Workflow completed successfully. Use outputs in conversation or export to file.
```

**Output Format (Failed):**
```
===========================
WORKFLOW STATUS
===========================

Workflow: code-review
Execution ID: exec_def456
Started: 2026-01-24 15:00:00
Failed: 2026-01-24 15:01:23
Duration: 1m 23s

Overall Status: FAILED

Tasks:
  ✓ [COMPLETED] analyze
      Duration: 45s

  ✗ [FAILED] test
      Duration: 38s
      Error: Test suite failed (2/45 tests failed)
      Details:
        - test_authentication.py::test_login_invalid_credentials FAILED
        - test_authentication.py::test_password_hashing FAILED

  ⏹ [SKIPPED] security_scan (dependency failed)
  ⏹ [SKIPPED] review_gate (dependency failed)

Failure Reason:
  Task 'test' failed with error: Test suite returned exit code 1

Recovery Options:
  1. Fix failing tests and re-run workflow
  2. Skip failed task and continue: /workflow run --skip-failed
  3. Restart workflow from beginning: /workflow run code-review [inputs]
```

**Task Status Types:**
- **PENDING**: Not yet started (waiting for dependencies)
- **RUNNING**: Currently executing
- **WAITING_APPROVAL**: Paused at approval gate
- **COMPLETED**: Successfully finished
- **FAILED**: Execution error
- **SKIPPED**: Manually skipped or dependency failed

**Use Cases:**
- **Progress Monitoring:** Check workflow execution state
- **Debugging:** Identify which task failed and why
- **Approval Context:** Review what requires approval
- **Timing Analysis:** See task durations for optimization

---

### `/workflow approve`

**Description:** Approves a pending task at an approval gate and continues workflow execution.

**Syntax:**
```
/workflow approve
```

**Behavior:**
- Resumes workflow from WAITING_APPROVAL state
- Executes remaining tasks in topological order
- Records approval decision in transcript
- Only valid when workflow status is WAITING_APPROVAL

**Parameters:** None

**Example:**
```
User: /workflow status
Friday: Workflow: newsletter
        Status: WAITING_APPROVAL
        Task: review_gate

        Research summary:
          - 12 sources found on "AI trends in 2026"
          - Key topics: LLMs, regulation, multimodal AI
          - Quality: High (8.5/10 average source credibility)

        Approve? /workflow approve | /workflow skip

User: /workflow approve
Friday: Approved: review_gate

        Continuing workflow...

        [Task 3/3] write (assigned to: coder)
          Status: RUNNING
          Writing newsletter based on approved research...

        [Workflow completed successfully]
```

**Approval Context:**
The approval gate receives ALL prior task outputs as context:
```yaml
- id: review_gate
  name: "Review Research Findings"
  requires_approval: true
  inputs:
    research_summary: "$research_summary"  # From prior task
    source_count: "$source_count"          # From prior task
```

**Use Cases:**
- **Quality Control:** Verify intermediate results before proceeding
- **Cost Control:** Approve expensive operations (API calls, deployments)
- **Safety Gates:** Human verification before destructive operations
- **Compliance:** Audit trail of human approvals

**Developer Note:** Approval gates are blocking. Workflow execution does NOT proceed until approval/skip is received.

---

### `/workflow skip`

**Description:** Skips a pending task at an approval gate and continues with remaining tasks.

**Syntax:**
```
/workflow skip
```

**Behavior:**
- Marks current approval gate as SKIPPED
- Sets task outputs to null
- Continues with tasks that don't depend on skipped outputs
- Skips tasks that depend on null outputs (dependency chain break)

**Parameters:** None

**Example:**
```
User: /workflow status
Friday: Workflow: code-review
        Status: WAITING_APPROVAL
        Task: review_gate

        Security scan found:
          - 1 medium-severity issue (SQL injection potential)

        Approve merge? /workflow approve | /workflow skip

User: /workflow skip
Friday: Skipped: review_gate

        Note: Workflow marked as COMPLETED but review was skipped.
        Address security issue before merging to production.

        ===========================
        WORKFLOW COMPLETE (WITH SKIPPED TASKS)
        ===========================

        Outputs:
          analysis_report: [available]
          test_results: [available]
          security_report: [available]
          merge_approved: null (skipped)
```

**Handling Null Outputs:**

**Workflow with skip handling:**
```yaml
- id: write_report
  agent: coder
  inputs:
    research_summary: "$research_summary"  # May be null if research was skipped
    fallback_content: "Research unavailable - using cached data"
  script: |
    if inputs.research_summary is None:
      return fallback_content
    return generate_report(research_summary)
```

**Use Cases:**
- **Optional Operations:** Skip non-critical tasks (e.g., optional enhancements)
- **Workflow Recovery:** Continue after minor failures
- **Testing:** Skip approval gates during workflow development
- **Emergency Bypass:** Skip stuck approval gates (use with caution)

**Developer Note:** Skipping tasks breaks dependency chains. Dependent tasks must handle null inputs gracefully or they will also be skipped.

---

## 9.9 Configuration & Utility Commands

Configuration and utility commands provide file operations, variable management, and system help.

### `/vars`

**Description:** Displays all scoped variables with their values and scope levels.

**Syntax:**
```
/vars
```

**Output Format:**
```
===========================
SCOPED VARIABLES
===========================

Session Scope (current session only):
  current_task: "Building web scraper"
  iteration_count: 3
  last_tool_used: "http_request"

User Scope (persistent across sessions):
  user:name: "Alice"
  user:preferred_language: "Python"
  user:timezone: "America/New_York"

Global Scope (shared across all users):
  system:version: "0.1.0"
  system:model: "gpt-4o"

Total: 9 variables
```

**Variable Scopes:**

**1. Session Scope:**
- Lifetime: Current session only
- Usage: Temporary workflow state
- Example: `iteration_count`, `current_task`

**2. User Scope:**
- Lifetime: All sessions for specific user
- Usage: User preferences and settings
- Prefix: `user:`
- Example: `user:name`, `user:preferred_language`

**3. Global Scope:**
- Lifetime: All sessions, all users
- Usage: System-wide configuration
- Prefix: `system:` (or no prefix for legacy)
- Example: `system:version`, `api_endpoint`

**Use Cases:**
- **State Inspection:** Check workflow variable values
- **Debugging:** Verify variables are set correctly
- **User Preferences:** Review learned user preferences
- **Configuration Review:** See system-wide settings

---

### `/set <key> <value>`

**Description:** Sets a scoped variable with automatic scope detection.

**Syntax:**
```
/set <key> <value>
/set user:name "Alice"                    # User scope
/set session:current_task "Research"      # Session scope (explicit)
/set current_task "Research"              # Session scope (implicit)
```

**Parameters:**
- `key` (required): Variable name (with optional scope prefix)
- `value` (required): Variable value (auto-typed)

**Scope Determination:**
- `user:*` prefix → User scope (persistent)
- `session:*` prefix → Session scope (temporary)
- No prefix → Session scope (default)
- `system:*` prefix → Global scope (admin only)

**Type Inference:**
```bash
/set count 42           # Integer
/set temperature 0.7    # Float
/set enabled true       # Boolean
/set name "Alice"       # String (quotes optional for single words)
/set description "A multi-word value"  # String (quotes required)
```

**Examples:**

**1. Set User Preference:**
```
User: /set user:preferred_language "Python"
Friday: Set user:preferred_language = "Python" (user scope, persistent)
```

**2. Set Session Variable:**
```
User: /set current_iteration 1
Friday: Set current_iteration = 1 (session scope)
```

**3. Update Existing Variable:**
```
User: /set current_iteration 2
Friday: Updated current_iteration: 1 → 2 (session scope)
```

**Use Cases:**
- **User Preferences:** Store learned preferences for future sessions
- **Workflow State:** Track iteration counts, flags, checkpoints
- **Configuration Override:** Temporarily override settings for testing
- **Agent Communication:** Pass variables between agents

**Variable Usage in Context:**
Variables are automatically included in the context payload:
```
Supporting Context:
  ...
  Scoped Variables:
    - current_task: "Building web scraper"
    - user:preferred_language: "Python"
```

**Developer Note:** Variables are stored in SessionState and persisted to transcript metadata. User-scoped variables require user ID tracking.

---

### `/read <path>`

**Description:** Reads a file using Friday's smart file readers with automatic format detection.

**Syntax:**
```
/read <file_path>
```

**Parameters:**
- `file_path` (required): Absolute or relative path to file

**Supported Formats:**
- **Text**: .txt, .md, .py, .js, .html, .xml, .json, .yaml, .csv
- **PDF**: .pdf (text extraction)
- **Office**: .docx, .xlsx (text/table extraction)
- **Encoding**: UTF-8, Latin-1 (auto-detected)

**Examples:**

**1. Text File:**
```
User: /read /tmp/notes.txt
Friday:
  File: /tmp/notes.txt
  Size: 1,234 bytes
  Encoding: utf-8
  Lines: 45

  Content:
  Meeting Notes - January 24, 2026

  Attendees: Alice, Bob, Carol

  Discussion Topics:
  1. Q1 roadmap review
  2. Performance optimization priorities
  3. Upcoming customer demos

  ...
```

**2. PDF Document:**
```
User: /read /docs/report.pdf
Friday:
  File: /docs/report.pdf
  Format: PDF
  Pages: 12
  Size: 2.3 MB

  Extracted Text (page 1):

  Q4 2025 Performance Report
  Executive Summary

  This quarter showed strong growth across all metrics:
  - Revenue: +23% YoY
  - User acquisition: +45% YoY
  - Customer satisfaction: 8.9/10 (up from 8.2)

  ...

  [Pages 2-12 truncated - use /read report.pdf --pages 2-5 for specific pages]
```

**3. Excel Spreadsheet:**
```
User: /read /data/sales.xlsx
Friday:
  File: /data/sales.xlsx
  Format: Excel
  Sheets: 3 (Sales, Expenses, Summary)
  Size: 456 KB

  Sheet: Sales (first 10 rows)

  | Date       | Product   | Quantity | Revenue   |
  |------------|-----------|----------|-----------|
  | 2026-01-01 | Widget A  | 120      | $12,000   |
  | 2026-01-02 | Widget B  | 85       | $8,500    |
  | 2026-01-03 | Widget A  | 140      | $14,000   |
  ...

  Use /read sales.xlsx --sheet "Expenses" for other sheets
```

**4. Reading Error:**
```
User: /read /nonexistent/file.txt
Friday:
  Error: File not found: /nonexistent/file.txt

  Suggestions:
  - Verify the file path is correct
  - Check if you have read permissions
  - Use absolute path if relative path fails
```

**Advanced Options:**
```bash
/read file.txt --max-lines 100      # Limit output
/read report.pdf --pages 1-3        # Specific pages
/read data.xlsx --sheet "Summary"   # Specific sheet
```

**Use Cases:**
- **Document Review:** Read files for analysis or summarization
- **Data Extraction:** Extract text from PDFs, Excel, Word docs
- **Code Review:** Read source files before editing
- **Research:** Ingest documentation for context

**Memory Integration:**
Files are NOT automatically ingested into memory. Use `/ingest` to add to vector store.

---

### `/ingest <path>`

**Description:** Ingests file content into vector memory for semantic search.

**Syntax:**
```
/ingest <file_path>
/ingest <file_path> --description "Custom description"
```

**Parameters:**
- `file_path` (required): Path to file to ingest
- `--description` (optional): Custom description for document

**Ingestion Process:**
1. **Read**: Extract text using format-specific readers
2. **Chunk**: Split text into semantic chunks (~500 tokens each)
3. **Embed**: Generate embeddings for each chunk
4. **Store**: Save to vector store with metadata

**Examples:**

**1. Ingest Documentation:**
```
User: /ingest /docs/api-reference.pdf
Friday:
  Ingesting: /docs/api-reference.pdf

  [1/4] Reading PDF...
    ✓ Extracted 12 pages (8,234 words)

  [2/4] Chunking text...
    ✓ Created 18 semantic chunks

  [3/4] Generating embeddings...
    ✓ Embedded 18 chunks (using text-embedding-ada-002)

  [4/4] Storing in vector memory...
    ✓ Stored in collection: memories_long_term

  ===========================
  INGESTION COMPLETE
  ===========================

  File: /docs/api-reference.pdf
  Chunks: 18
  Tokens: 8,234
  Storage: 18 documents in long-term memory

  This content is now searchable and will be retrieved for relevant queries.
```

**2. Ingest with Custom Description:**
```
User: /ingest /data/customer-feedback.csv --description "Customer survey results Q4 2025"
Friday:
  Ingesting: /data/customer-feedback.csv
  Description: "Customer survey results Q4 2025"

  [Processing...]

  ✓ Ingestion complete: 42 rows → 8 chunks → long-term memory

  Metadata added:
    - source_type: user_ingestion
    - file_path: /data/customer-feedback.csv
    - description: Customer survey results Q4 2025
    - ingested_at: 2026-01-24 14:45:00
```

**3. Ingestion Error:**
```
User: /ingest /huge-file.pdf
Friday:
  Error: File too large for ingestion (125 MB exceeds 10 MB limit)

  Suggestions:
  - Split PDF into smaller files
  - Extract relevant sections only
  - Increase ingestion limit in config.yaml (ingestion.max_file_size_mb)
```

**Metadata Stored:**
```yaml
metadata:
  source_type: user_ingestion
  file_path: /docs/api-reference.pdf
  file_format: pdf
  description: "API documentation for Friday Framework"
  chunk_index: 0
  total_chunks: 18
  ingested_at: "2026-01-24T14:45:00Z"
  confidence: 1.0  # User-provided content is always high confidence
```

**Use Cases:**
- **Knowledge Base**: Add documentation to Friday's memory
- **Context Augmentation**: Ingest project-specific information
- **Research**: Add papers, articles, reports for reference
- **Training Data**: Ingest examples for Friday to learn from

**Configuration:**
```yaml
memory:
  ingestion:
    max_file_size_mb: 10
    chunk_size_tokens: 500
    chunk_overlap_tokens: 50
    default_collection: memories_long_term
    embedding_batch_size: 100
```

**Chunking Strategy:**
- **Semantic Chunking**: Splits on paragraph/section boundaries
- **Token Limit**: Max 500 tokens per chunk (configurable)
- **Overlap**: 50-token overlap between chunks for context continuity

**Developer Note:** Ingestion is expensive (embedding API calls). Large files can take several minutes and consume significant token budgets.

---

### `/help [command]`

**Description:** Shows command reference with usage examples.

**Syntax:**
```
/help              # Show all commands by category
/help workflow     # Show detailed help for specific command
```

**Parameters:**
- `command` (optional): Specific command name for detailed help

**Output Format (General):**
```
===========================
FRIDAY CLI COMMANDS
===========================

Session Management:
  /exit, /quit    - Exit the chat
  /clear          - Clear conversation history
  /reset          - Complete memory wipe (with backup)

Memory Inspection:
  /memory         - Show memory statistics
  /context        - Show assembled context payload
  /prompt         - Show formatted LLM prompt
  /prime          - Manually trigger session priming
  /debug          - Show debug info from last turn

Memory Store Queries:
  /entities       - List graph entities
  /facts          - List all vector documents
  /insights       - List insights only
  /summaries      - List turn summaries
  /meta           - List meta-insights

Transcript Management:
  /sessions       - List all transcript sessions
  /transcript     - Show session transcript
  /export         - Export current session

Advanced Memory Operations:
  /reorganize     - Run memory reorganization
  /migrate        - Migrate memories to new schema
  /lifecycle      - Manual lifecycle operations

Tool Management:
  /tools          - List available tools
  /run-tool       - Execute tool directly
  /inject-tools   - Force specific tools into context
  /clear-tools    - Remove injected tools
  /recommend-tools - Test tool recommendations
  /tool-budget    - Show token budget info

Agent Orchestration (Phase 3):
  /switch         - Switch active agent
  /agents         - List available agents
  /agent          - Show agent details
  /delegate       - Delegate task to another agent
  /status         - Show orchestrator status
  @agent_name     - Direct routing syntax

Workflow Commands (Phase 4):
  /workflow list     - List available workflows
  /workflow run      - Execute workflow
  /workflow status   - Show workflow status
  /workflow approve  - Approve pending task
  /workflow skip     - Skip pending task

Configuration & Utilities:
  /vars           - Show scoped variables
  /set            - Set a variable
  /read           - Read file with smart detection
  /ingest         - Ingest file into memory
  /help           - Show this help

For detailed help: /help <command>
Example: /help workflow
```

**Output Format (Specific Command):**
```
User: /help workflow

===========================
COMMAND: /workflow
===========================

Description:
  Manage and execute multi-step automation workflows with
  task dependencies, agent orchestration, and human approval gates.

Subcommands:
  /workflow list
    List all available workflows with metadata

  /workflow run <name> [inputs]
    Execute a workflow with optional input variables
    Example: /workflow run newsletter topic="AI trends" urgency="high"

  /workflow status
    Show current workflow execution status

  /workflow approve
    Approve a task waiting at approval gate

  /workflow skip
    Skip a task at approval gate (may break dependencies)

Usage Examples:

  # List available workflows
  /workflow list

  # Run newsletter workflow
  /workflow run newsletter user_topic="AI trends"

  # Check workflow progress
  /workflow status

  # Approve research review gate
  /workflow approve

Related Commands:
  /agents  - List agents that can execute workflow tasks
  /status  - Show orchestrator status during workflow execution

Configuration:
  Workflows are defined in YAML files in the workflows/ directory
  See docs/guides/08-workflows.md for workflow creation guide

Tips:
  - Use /workflow run <name> --help to see required inputs
  - Workflows can be paused and resumed (approval gates)
  - Use /workflow status to monitor long-running workflows
  - Skipping approval gates may cause dependent tasks to fail
```

**Use Cases:**
- **Learning**: Discover available commands and their syntax
- **Reference**: Quick lookup for command parameters
- **Troubleshooting**: Understand command behavior and options
- **Documentation**: Generate command reference for team

**Developer Note:** Help content is generated from command docstrings and the CommandRegistry. Keep docstrings up-to-date for accurate help output.

---

## Command Reference Summary

### Quick Reference Table

| Command | Category | Description | Phase |
|---------|----------|-------------|-------|
| `/exit`, `/quit` | Session | Exit chat | Core |
| `/clear` | Session | Clear conversation history | Core |
| `/reset` | Session | Complete memory wipe | Core |
| `/memory` | Inspection | Show memory statistics | Core |
| `/context` | Inspection | Show context payload | Core |
| `/prompt` | Inspection | Show formatted LLM prompt | Core |
| `/prime` | Inspection | Trigger session priming | Core |
| `/debug` | Inspection | Show debug information | Core |
| `/entities` | Queries | List graph entities | Core |
| `/facts` | Queries | List vector documents | Core |
| `/insights` | Queries | List insights only | Core |
| `/summaries` | Queries | List turn summaries | Core |
| `/meta` | Queries | List meta-insights | Core |
| `/sessions` | Transcripts | List all sessions | Core |
| `/transcript` | Transcripts | Show session transcript | Core |
| `/export` | Transcripts | Export current session | Core |
| `/reorganize` | Advanced | Memory reorganization | Core |
| `/migrate` | Advanced | Schema migration | Core |
| `/lifecycle` | Advanced | Manual lifecycle ops | Core |
| `/tools` | Tools | List available tools | Core |
| `/run-tool` | Tools | Execute tool directly | Core |
| `/inject-tools` | Tools | Force tools into context | Core |
| `/clear-tools` | Tools | Remove injected tools | Core |
| `/recommend-tools` | Tools | Test recommendations | Core |
| `/tool-budget` | Tools | Show token budget | Core |
| `/switch` | Orchestration | Switch active agent | Phase 3 |
| `/agents` | Orchestration | List available agents | Phase 3 |
| `/agent` | Orchestration | Show agent details | Phase 3 |
| `/delegate` | Orchestration | Delegate task | Phase 3 |
| `/status` | Orchestration | Orchestrator status | Phase 3 |
| `@agent_name` | Orchestration | Direct routing | Phase 3 |
| `/workflow list` | Workflows | List workflows | Phase 4 |
| `/workflow run` | Workflows | Execute workflow | Phase 4 |
| `/workflow status` | Workflows | Show workflow status | Phase 4 |
| `/workflow approve` | Workflows | Approve task | Phase 4 |
| `/workflow skip` | Workflows | Skip task | Phase 4 |
| `/vars` | Config | Show variables | Core |
| `/set` | Config | Set variable | Core |
| `/read` | Utilities | Read file | Core |
| `/ingest` | Utilities | Ingest into memory | Core |
| `/help` | Utilities | Show help | Core |

---

## Configuration File Reference

### Session Configuration

Located in: `config.yaml`

```yaml
session:
  user_id: "developer@example.com"
  assistant_name: "Friday"
  user_name: "User"

  # Maintenance operations
  maintenance:
    on_exit: false  # Run maintenance on /exit
    auto_lifecycle: true  # Auto lifecycle after each turn
```

### Memory Configuration

```yaml
memory:
  priming:
    enabled: true
    top_n_entities: 10
    top_n_insights: 20
    recency_days: 30
    include_summaries: true
    previous_sessions: 2

  lifecycle:
    promotion:
      threshold: 0.7
      min_age_hours: 24
    decay:
      lambda: 0.01
      threshold: 0.3
      min_age_days: 7
    reactivation:
      enabled: true
      access_window_hours: 168
```

### Tool Configuration

```yaml
tools:
  enabled: true
  registry:
    - name: read_file
      module: friday_tools.filesystem
      class: ReadFileTool
      enabled: true

    - name: execute_command
      module: friday_tools.shell
      class: ExecuteCommandTool
      enabled: true
      constructor_args:
        timeout_seconds: 30
```

---

## Tips & Best Practices

### For Developers

**Memory Inspection Workflow:**
```bash
1. /memory           # Quick health check
2. /context --debug  # Token usage analysis
3. /entities         # Graph state
4. /insights         # Learning verification
5. /lifecycle --stats # Lifecycle health
```

**Tool Development Workflow:**
```bash
1. /tools                              # Check existing tools
2. /run-tool <tool> {...}             # Test new tool
3. /recommend-tools "test query"      # Verify recommendation
4. /inject-tools <tool>               # Force inclusion for testing
5. /clear-tools                        # Reset after testing
```

**Agent Development Workflow:**
```bash
1. /agents                    # Check available agents
2. /agent researcher          # Review configuration
3. /switch researcher         # Test agent behavior
4. @researcher "test query"   # Test routing
5. /status                    # Check orchestration state
```

### For Technical Executives

**Quick Evaluation Flow:**
```bash
1. /memory              # Memory capabilities
2. /prime               # Context priming demo
3. /tools filesystem    # Tool categories
4. /workflow list       # Automation capabilities
5. /agents              # Multi-agent features
```

**Demo Workflow:**
```bash
# Show learning capability
/clear
"I prefer Python over JavaScript"
/insights  # Verify preference captured

# Show memory persistence
/exit
[restart]
/prime  # Show prior session context loaded

# Show multi-agent
@researcher "Find papers on transformers"
@coder "Implement attention mechanism"
```

### For AI Practitioners

**Context Engineering Experiments:**
```bash
# Baseline
/context --debug  # Note token counts

# Adjust priming
# Edit config.yaml: top_n_entities: 5
/prime
/context --debug  # Compare token usage

# Test tool budgeting
/tool-budget
/inject-tools <many tools>
/tool-budget  # See impact
```

**Memory Lifecycle Tuning:**
```bash
# Check current state
/lifecycle --stats

# Force operations
/lifecycle --promote
/lifecycle --decay

# Verify results
/facts
/lifecycle --stats
```

---

## Troubleshooting Guide

### Common Issues

**1. Command Not Recognized**
```
Error: Unknown command: /unknow
Did you mean: /unknown?

Solution: Use /help to see all commands
```

**2. Missing Parameters**
```
Error: Missing required parameter(s): file_path

Solution: Include required parameters
Example: /read /path/to/file.txt
```

**3. Workflow Not Found**
```
Error: Workflow not found: newsleter
Available: newsletter, code-review, research-report

Solution: Use /workflow list to see exact names
```

**4. Context Window Exceeded**
```
Error: Context length exceeded (8,234 > 8,000 tokens)

Solution:
  1. /clear  # Clear history
  2. Reduce token budgets in config.yaml
  3. Use larger context window model
```

**5. Tool Execution Failed**
```
Error: Tool execution failed: read_file
FileNotFoundError: File not found

Solution: Verify file path and permissions
```

---

## Appendix: Command Aliases

Some commands support aliases for convenience:

| Command | Aliases | Notes |
|---------|---------|-------|
| `/exit` | `/quit` | Both work identically |
| `/export markdown` | `/export md` | Short form accepted |
| `/workflow` | `/wf` | Shorter syntax (future) |
| `/recommend-tools` | `/rec-tools` | Shorter syntax (future) |

---

## Appendix: Environment Variables

CLI behavior can be modified via environment variables:

```bash
# Logging
export FRIDAY_LOG_LEVEL=DEBUG          # Enable debug logging
export FRIDAY_LOG_FORMAT=structured     # JSON log format

# Config
export FRIDAY_CONFIG_PATH=./custom.yaml # Custom config file

# Memory
export FRIDAY_MEMORY_PERSIST_DIR=./mem  # Custom memory directory

# API Keys (required)
export OPENAI_API_KEY=sk-...            # OpenAI
export ANTHROPIC_API_KEY=sk-ant-...     # Anthropic
export OLLAMA_BASE_URL=http://localhost:11434  # Ollama
```

---

## Conclusion

This CLI reference covers all 40+ commands available in `memory-chat-v2.py`, organized by functional category for quick navigation. Each command includes:

- **Syntax**: Exact command structure
- **Parameters**: Required and optional parameters
- **Output Format**: Expected output structure
- **Examples**: Real-world usage scenarios
- **Use Cases**: When to use the command
- **Developer Notes**: Implementation details and caveats

**Next Steps:**

- **Section 10: Configuration Guide**: Complete reference for config.yaml settings
- **Section 11: Advanced Topics**: Deep dives into architecture and optimization
- **Section 12: Use Cases & Examples**: Real-world Friday implementations

**For Support:**
- GitHub Issues: [repository-url]/issues
- Documentation: [docs-url]
- Community: [discord/slack-url]

---

*This CLI reference is part of the Friday Agent Framework User Guide v1.0*
