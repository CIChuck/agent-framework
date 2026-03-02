---
title: "Memory Settings"
description: "Tune decay rates, promotion thresholds, vector store, and graph parameters."
weight: 3
---

Fine-tune Friday's memory system by adjusting context window budgeting, priming behavior, memory lifecycle decay, and vector store collection strategies.

## Context Window and Token Budgeting

Token budgeting controls how Friday allocates its limited context window across different components.

**Token Budget Hierarchy**

```text
Total Context Window (e.g., 32K tokens)
├── Output Buffer (reserved for LLM response)
├── System Prompt (agent identity and instructions)
├── Priming (knowledge from prior sessions)
└── Dynamic Context (per-turn allocation)
    ├── Conversation History (episodic memory)
    ├── Retrieved Insights (vector store)
    ├── Loaded Entities (graph store)
    └── Tool Schemas (if applicable)
```

**Basic Configuration**

```yaml
memory:
  # Total context window of your LLM
  context_window: 32000

  # Tokens reserved for model output
  output_buffer: 1000

  # Maximum conversation turns to include
  max_history_turns: 20
```

**Context Window by Model**

| Model | Context Window | Recommended Setting |
|-------|----------------|---------------------|
| GPT-4o | 128K | 32000 - 128000 |
| GPT-4o-mini | 128K | 32000 - 128000 |
| Claude 3.5 Sonnet | 200K | 32000 - 200000 |
| Claude 3.5 Haiku | 200K | 32000 - 200000 |
| Gemini 1.5 Pro | 1M | 32000 - 1000000 |
| Llama 3.1 8B | 128K | 8000 - 32000 |
| Mistral 7B | 32K | 8000 - 32000 |

**Output Buffer Guidelines**

| Use Case | Recommended Buffer |
|----------|-------------------|
| Short responses (chat) | 500 - 1000 |
| Medium responses (explanations) | 1000 - 2000 |
| Long responses (documents) | 2000 - 4000 |
| Code generation | 2000 - 4000 |
| Multi-turn planning | 1500 - 3000 |

**Dynamic Budget Allocation**

Friday automatically allocates the remaining budget across dynamic components:

```python
dynamic_budget = context_window - output_buffer - len(system_prompt) - len(priming)
```

The `ContextAssembler` uses a knapsack optimization algorithm to pack maximum value into the dynamic budget:

1. Score each memory — Relevance × Importance × Recency
2. Estimate token cost — Number of tokens per memory
3. Solve knapsack — Maximize value within the budget constraint
4. Assemble context — Include selected memories

**Consolidation Settings**

Automatically summarize old conversation history to save tokens.

```yaml
memory:
  # Consolidate after N turns
  consolidate_after_turns: 50

  # Keep recent turns verbatim, summarize older turns
  consolidation_keep_recent: 10
```

After 50 turns, Friday keeps the last 10 verbatim and summarizes older turns into compact summaries, reducing token usage by 60-80%.

**Context Format Configuration**

```yaml
memory:
  # Format options: plain, json, xml, markdown
  context_format: markdown
```

| Format | Token Efficiency | LLM Comprehension | Best For |
|--------|------------------|-------------------|----------|
| `plain` | High | Good | Local models, small context |
| `json` | Medium | Good | Structured data, APIs |
| `xml` | Low | Excellent | Claude models, complex structure |
| `markdown` | Medium | Excellent | GPT-4, general purpose |

**Advanced: Per-Component Budgets**

For fine-grained control, configure explicit token budgets:

```yaml
memory:
  budgets:
    system_prompt_tokens: 1000
    history_tokens: 5000
    vector_tokens: 3000
    graph_tokens: 2000
    tool_tokens: 2000
```

This explicit allocation overrides automatic budget calculation.

## Priming Configuration

Priming preloads the agent's context with relevant knowledge from prior sessions, providing continuity and domain awareness before the user's first message.

When a session starts, Friday can prime the context with:
- Top entities by access count (most frequently referenced)
- Key relationships between entities
- Recent insights and learnings
- Session-relevant summaries

**Basic Priming Configuration**

```yaml
memory:
  priming:
    # Enable/disable priming
    enabled: true

    # Entity selection
    top_entities: 50          # Include top N most accessed entities
    include_orphans: false    # Include entities without relationships

    # Content limits
    max_insights: 50          # Maximum insights to include
    max_relationships: 100    # Maximum relationships to include

    # Temporal filtering
    recency_days: 0           # 0 = no filtering, 30 = last 30 days only

    # Token budgeting
    token_budget: 20000       # Maximum tokens for priming
```

**Entity Selection Strategies**

```yaml
memory:
  priming:
    # Strategy 1: Access-based (default)
    top_entities: 50
    sort_by: "hit_count"      # Most frequently accessed

    # Strategy 2: Recency-based
    sort_by: "last_accessed"
    recency_days: 7           # Only entities from last week

    # Strategy 3: Confidence-based
    sort_by: "confidence"     # Highest extraction confidence
    min_confidence: 0.7

    # Strategy 4: Hybrid
    sort_by: "weighted"       # Weighted combination
    weights:
      hit_count: 0.5
      confidence: 0.3
      recency: 0.2
```

**Relationship Filtering**

```yaml
memory:
  priming:
    relationships:
      include_all_types: true

      # Or specify allowed types
      allowed_types:
        - "KNOWS"
        - "USES"
        - "WORKS_ON"
        - "PREFERS"

      min_strength: 0.5
      max_per_entity: 10
```

**Recency Windows**

```yaml
memory:
  priming:
    recency:
      enabled: true
      days: 30                # Global: last 30 days

      # Per-content-type recency
      entities_days: 0        # All entities (no filter)
      relationships_days: 30
      insights_days: 7        # Insights from last week
      summaries_days: 14
```

**Token Budget Allocation**

```yaml
memory:
  priming:
    token_budget: 20000

    # Budget allocation (must sum to 1.0)
    allocation:
      entities: 0.3
      relationships: 0.2
      insights: 0.3
      summaries: 0.2
```

**Use Case Examples**

Long-running projects — optimize for continuity across many sessions:

```yaml
memory:
  priming:
    enabled: true
    token_budget: 30000
    top_entities: 100
    recency_days: 0           # All historical knowledge
    max_insights: 100
    sort_by: "hit_count"
```

Short-term tasks — optimize for recent, focused information:

```yaml
memory:
  priming:
    enabled: true
    token_budget: 10000
    top_entities: 20
    recency_days: 3
    max_insights: 20
    sort_by: "last_accessed"
```

**Environment Variable Overrides**

```bash
FRIDAY_MEMORY__PRIMING__ENABLED="true"
FRIDAY_MEMORY__PRIMING__TOP_ENTITIES="50"
FRIDAY_MEMORY__PRIMING__TOKEN_BUDGET="20000"
FRIDAY_MEMORY__PRIMING__RECENCY_DAYS="7"
```

## Lifecycle Settings

Memory lifecycle settings control how memories age, decay, and transition between stages.

**Lifecycle Stages**

1. **SHORT_TERM** — New memories, recently accessed, high decay score
2. **LONG_TERM** — Promoted memories, frequently accessed, important
3. **DECAYED** — Rarely accessed memories, marked for cleanup

**Core Decay Configuration**

```yaml
memory:
  lifecycle:
    enabled: true

    # Decay parameters
    decay_rate: 0.01          # Lambda for exponential decay (0.001-0.5)
    access_boost: 0.2         # Score boost on each access

    # Stage transition thresholds
    promotion_threshold: 0.7  # Score needed for SHORT_TERM → LONG_TERM
    decay_threshold: 0.2      # Score below which → DECAYED
```

**Decay Formula**

Friday uses exponential decay:

```text
score(t) = score_0 × e^(-λ × hours_since_last_access)
```

Where `λ` is the `decay_rate`, `score_0` is the initial score (typically 1.0), and time is measured in hours since last access.

**Decay Rate Examples**

| Decay Rate | 24h Score | 72h Score | 1 Week Score | Speed |
|------------|-----------|-----------|--------------|-------|
| 0.001 | 98% | 93% | 86% | Very slow |
| 0.005 | 88% | 68% | 39% | Slow |
| 0.01 | 79% | 49% | 19% | Medium (default) |
| 0.02 | 62% | 24% | 4% | Fast |
| 0.05 | 30% | 3% | <1% | Very fast |

```yaml
# Very slow decay - Long-term projects
memory:
  lifecycle:
    decay_rate: 0.001
    decay_threshold: 0.1

# Fast decay - Short-term tasks
memory:
  lifecycle:
    decay_rate: 0.02
    decay_threshold: 0.3
```

**Promotion Configuration**

Control how memories are promoted from SHORT_TERM to LONG_TERM:

```yaml
memory:
  lifecycle:
    promotion:
      min_age_hours: 24

      threshold: 0.7

      # Scoring weights (must sum to 1.0)
      weights:
        age: 0.2              # Time in short-term
        access: 0.4           # Access frequency (most important)
        confidence: 0.2       # Extraction confidence
        connection: 0.2       # Graph connections
```

**Decay Check Scheduling**

```yaml
memory:
  lifecycle:
    check_interval_hours: 24
    check_on_session_start: true
    check_on_session_end: false
    batch_size: 100
```

**Cleanup Configuration**

```yaml
memory:
  lifecycle:
    cleanup:
      retention_days: 30      # Keep DECAYED for 30 days
      auto_delete: true
      cleanup_interval_hours: 168  # Weekly cleanup
      max_deletions_per_run: 1000
```

**Stage-Specific Settings**

```yaml
memory:
  lifecycle:
    stages:
      short_term:
        min_age_hours: 24
        max_capacity: 10000
        decay_rate: 0.01

      long_term:
        max_capacity: 50000
        decay_rate: 0.005
        reeval_interval_days: 30

      decayed:
        retention_days: 30
        allow_resurrection: true
        resurrection_boost: 0.5
```

**Environment Variable Overrides**

```bash
FRIDAY_MEMORY__LIFECYCLE__ENABLED="true"
FRIDAY_MEMORY__LIFECYCLE__DECAY_RATE="0.01"
FRIDAY_MEMORY__LIFECYCLE__ACCESS_BOOST="0.2"
FRIDAY_MEMORY__LIFECYCLE__PROMOTION_THRESHOLD="0.7"
FRIDAY_MEMORY__LIFECYCLE__DECAY_THRESHOLD="0.2"
FRIDAY_MEMORY__LIFECYCLE__CLEANUP__RETENTION_DAYS="30"
```

## Collection Configuration

Friday's vector store supports multiple collections for organizing memories by lifecycle stage, topic, or session.

**Default Single Collection**

```yaml
memory:
  vector:
    collection_name: "friday_memories"
    multi_collection: false
```

**Multi-Collection Mode**

```yaml
memory:
  vector:
    multi_collection: true
    collection_prefix: "friday"
    collections:
      short_term: "friday_short_term"
      long_term: "friday_long_term"
      decayed: "friday_decayed"
```

**Collection Strategies**

Strategy 1: Lifecycle Stages (Recommended)

```yaml
memory:
  vector:
    strategy: "lifecycle"
    multi_collection: true
    collections:
      short_term: "friday_short_term"
      long_term: "friday_long_term"
      decayed: "friday_decayed"
    auto_migrate: true
```

Strategy 2: Session-Based

```yaml
memory:
  vector:
    strategy: "session"
    collection_template: "friday_session_{session_id}"
    merge_on_end: true
    merge_target: "friday_memories"
```

Strategy 3: User-Based (multi-tenant isolation)

```yaml
memory:
  vector:
    strategy: "user"
    collection_template: "friday_user_{user_id}"
    cross_user_search: false  # Prevent cross-user data leaks
```

**Retrieval Configuration**

```yaml
memory:
  vector:
    retrieval:
      # priority | parallel | cascade
      search_strategy: "priority"

      # Priority order (for "priority" strategy)
      search_order:
        - "short_term"
        - "long_term"

      limits:
        short_term: 20
        long_term: 30

      min_similarity:
        short_term: 0.7
        long_term: 0.75
```

**Search Strategy Details**

- **Priority**: Search collections in order, stop when quota is filled.
- **Parallel**: Search all collections simultaneously, merge results by score.
- **Cascade**: Search with fallback — trigger next collection only if insufficient results.

**Collection Size Limits**

```yaml
memory:
  vector:
    limits:
      short_term:
        max_memories: 10000
        max_size_mb: 500
        eviction_policy: "lru"  # lru | fifo | lowest_score

      long_term:
        max_memories: 50000
        max_size_mb: 2000
        eviction_policy: "lowest_score"
```

**Migration Configuration**

```yaml
memory:
  vector:
    migration:
      auto_migrate: true
      strategy: "copy_delete"  # copy_delete | move | duplicate
      batch_size: 100
      batch_delay_ms: 100
      verify_migration: true
      rollback_on_error: true
```

**Complete Multi-Collection Example**

```yaml
# config.yaml - Multi-collection configuration
memory:
  vector:
    multi_collection: true
    strategy: "lifecycle"
    collection_prefix: "friday"

    collections:
      short_term:
        name: "friday_short_term"
        metadata:
          description: "Recent memories under evaluation"
          max_age_days: 30
        limits:
          max_memories: 10000
          max_size_mb: 500
          eviction_policy: "lru"

      long_term:
        name: "friday_long_term"
        metadata:
          description: "Promoted long-term knowledge"
          max_age_days: 365
        limits:
          max_memories: 50000
          max_size_mb: 2000
          eviction_policy: "lowest_score"

      decayed:
        name: "friday_decayed"
        metadata:
          description: "Decayed memories pending deletion"
          retention_days: 30
        limits:
          max_memories: 5000
          max_size_mb: 200

    retrieval:
      search_strategy: "priority"
      search_order:
        - "short_term"
        - "long_term"
      limits:
        short_term: 20
        long_term: 30
      min_similarity:
        short_term: 0.7
        long_term: 0.75

    migration:
      auto_migrate: true
      strategy: "copy_delete"
      batch_size: 100
      verify_migration: true
      rollback_on_error: true
```

## Related Pages

- [Configuration Architecture](/docs/configuration/architecture/) — How Friday loads and merges configuration layers
- [LLM Providers](/docs/configuration/llm/) — Configure cloud and local LLM providers
- [Full Reference](/docs/configuration/reference/) — Complete configuration key reference and defaults
