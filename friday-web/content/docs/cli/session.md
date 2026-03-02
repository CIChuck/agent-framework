---
title: "Session Commands"
description: "Start, resume, list, and export conversation sessions."
weight: 1
---

Use the `memory-chat-v2.py` CLI to start new conversations, resume prior sessions, inspect session history, and export transcripts. Session commands control the lifecycle of your Friday chat session.

The CLI is Friday Framework's comprehensive interactive testing and development interface. It provides full access to Friday's memory systems, agent orchestration, workflow execution, and tool management through an intuitive command-line interface.

**Location:** `tests/integration/memory/memory-chat-v2.py`

**Quick Start:**

```bash
# From project root
cd tests/integration/memory
python memory-chat-v2.py

# With custom config
python memory-chat-v2.py --config ../../config.yaml
```

---

## `/exit`, `/quit`

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

**Example:**

```
User: /exit
Friday: Goodbye! Session archived. Memory stats: 42 entities, 156 insights, 8 turns.
```

**Notes:**
- Safe to exit at any time — all state is persisted
- Re-running the CLI with the same session ID will restore full context
- For emergency termination, use Ctrl+C (may skip cleanup operations)

---

## `/clear`

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

This command only affects the episodic store. Vector and graph stores remain intact, enabling seamless context continuity across conversation restarts.

---

## `/reset`

**Description:** Complete memory wipe with full system reset. This is the "factory reset" command.

**Syntax:**

```
/reset
```

**Behavior:**
- Clears all memory stores:
  - Episodic: All conversation history (current and prior sessions)
  - Vector: All insights, summaries, and documents
  - Graph: All entities and relationships
- Archives transcripts: Exports all sessions to timestamped CSV files before deletion
- Resets session state: New session ID, fresh state initialization
- Preserves configuration: System config and tool registry remain unchanged

{{< callout type="warning" >}}
`/reset` deletes ALL memories. This action is irreversible except from backup archives created before deletion.
{{< /callout >}}

**Safety:**
- Requires confirmation prompt: "This will delete ALL memories. Continue? (yes/no)"
- Creates backup exports in `./exports/reset_backup_[timestamp]/`

**Use Cases:**
- Starting completely fresh for testing or development
- Clearing corrupted memory state
- Resetting after experimental memory operations
- Preparing clean slate for production deployment

**Example:**

```
User: /reset
Friday: WARNING: This will delete ALL memories and archive transcripts.
        Continue? (yes/no): yes

        Archiving transcripts...
        Exported 5 sessions to ./exports/reset_backup_20260124_143022/

        Clearing memory stores...
        Episodic store cleared (1,234 turns deleted)
        Vector store cleared (567 documents deleted)
        Graph store cleared (89 entities, 234 relationships deleted)

        Reset complete. All memories cleared. Archives saved.
```

**Recovery:** Archives can be re-imported using the `/replay` command or by manually ingesting exported data.

---

## `/sessions`

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
- No marker: Archived sessions not currently in context

**Configuration:**

```yaml
memory:
  priming:
    previous_sessions: 2  # Include 2 most recent prior sessions in context
```

**Use Cases:**
- Session discovery: Find past conversations by date or turn count
- Context verification: Confirm which prior sessions are influencing current context
- Resource monitoring: Track token usage across sessions
- Model comparison: Review which models were used for different sessions

Sessions are ordered newest first. The "in context" count is determined by priming configuration.

---

## `/transcript [id]`

**Description:** Displays full conversation transcript from persistent storage.

**Syntax:**

```
/transcript              # Show current session
/transcript abc123def456 # Show specific session by ID
```

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
Let me analyze the performance characteristics of your function...

[tokens: 456, latency: 2,340ms]

--- Turn 2 [def67890...] ---
Timestamp: 10:18:22

User:
Here's the function: def process_data(items): return [item**2 for item in items]

Friday:
[Executed tool: analyze_code]
Your function has O(n) time complexity which is optimal for this operation. However,
for large datasets, consider:

1. Using NumPy for vectorized operations (50-100x speedup)
2. Implementing batch processing if items don't fit in memory
3. Adding multiprocessing for CPU-bound transformations

[tokens: 890, latency: 3,120ms]

...

===========================
```

**Metadata Displayed:**
- Turn number: Sequential turn counter
- Turn ID: Unique identifier (first 8 chars shown)
- Timestamp: Time of turn within session
- Messages: Full user and assistant messages
- Tool calls: Executed tools with parameters and results (if applicable)
- Metrics: Token usage and latency per turn

**Use Cases:**
- Conversation review: Read past interactions in full detail
- Debugging: Trace conversation flow and tool execution
- Quality assurance: Verify Friday's responses were appropriate
- Training data: Export conversations for fine-tuning (see `/export training`)

---

## `/transcript export`

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
- Data archival: Backup all conversations before `/reset`
- Analytics: Import CSVs into analysis tools (Excel, Pandas, SQL)
- Compliance: Export data for regulatory requirements
- System migration: Transfer transcripts between Friday deployments

{{< callout type="warning" >}}
CSV exports may contain sensitive conversation data. Store exports securely and follow data retention policies.
{{< /callout >}}

---

## `/export [format]`

**Description:** Exports current session transcript in specified format.

**Syntax:**

```
/export              # Default: markdown
/export markdown     # Human-readable formatted transcript
/export jsonl        # JSON Lines for programmatic processing
/export training     # Chat-format training data
```

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
```

**2. JSONL (`/export jsonl`):**

```jsonl
{"id":"abc12345","session_id":"abc123def456","turn_number":1,"timestamp":"2026-01-24T10:16:15Z","user_message":"How do I optimize...","assistant_message":"Let me analyze...","total_tokens":456,"latency_ms":2340}
{"id":"def67890","session_id":"abc123def456","turn_number":2,"timestamp":"2026-01-24T10:18:22Z","user_message":"Here's the function...","assistant_message":"Your function has...","total_tokens":890,"latency_ms":3120}
```

**3. Training (`/export training`):**

```jsonl
{"messages":[{"role":"system","content":"You are Friday..."},{"role":"user","content":"How do I optimize..."},{"role":"assistant","content":"Let me analyze..."}]}
{"messages":[{"role":"system","content":"You are Friday..."},{"role":"user","content":"Here's the function..."},{"role":"assistant","content":"Your function has..."}]}
```

**Export Location:** `./exports/transcript_[session_id]_[timestamp].[ext]`

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

## Related Pages

- [Memory Commands](/docs/cli/memory/) — Inspect, search, prune, and export memory stores
- [Workflow Commands](/docs/cli/workflows/) — Run, validate, and manage workflow executions
- [Agent Lifecycle](/docs/agents/lifecycle/) — Session initialization and turn archiving
