# Memory Management Guidelines

This document describes how Friday-Memory manages context size, token budgets, and memory lifecycle to prevent LLM timeouts and optimize performance.

## Overview

Friday-Memory uses a multi-stage memory architecture with automatic pruning to stay within token budgets. However, **there are no automatic compaction triggers based on percentage thresholds**. Memory is only pruned at context assembly time when the budget is exceeded.

## Token Budget Architecture

### Budget Calculation

```
Available Budget = Context Window - Output Buffer - Fixed Costs

Where:
  Context Window  = Model's max tokens (e.g., 32,000)
  Output Buffer   = Reserved for LLM response (default: 1,000)
  Fixed Costs     = System prompt + Tool definitions
```

### Budget Allocation

The context assembler allocates budget across components:

| Component | Default Allocation | Notes |
|-----------|-------------------|-------|
| Tool definitions | 25% of budget | Fixed cost, calculated first |
| Priming content | `token_budget` setting | Entities, insights, summaries, facts |
| Conversation history | Remaining budget | Current + prior session turns |
| Vector passages | Within history budget | Semantic search results |
| Graph context | Within history budget | Entities and relationships |

## Configuration Reference

### Key Settings (config.yaml)

```yaml
memory:
  # Model context limits
  context_window: 40000      # Your model's max tokens
  output_buffer: 1000        # Reserved for response generation

  # History limits
  max_history_turns: 15      # Max turns to include (recommend 10-20)
  consolidate_after_turns: 25  # When to trigger consolidation

  # Context format
  context_format: markdown   # Options: plain, json, xml, markdown

  # Supporting context budget (Phase 2 formatting)
  supporting_context:
    budget_ratio: 0.30       # 30% for context, 70% for history
    section_priority:        # Order of importance for truncation
      - recent_memories
      - passages
      - key_facts
      - insights
      - summaries
      - tools
      - state
    max_items:               # Hard limits per section
      passages: 10
      key_facts: 20
      insights: 15
      summaries: 10
      tools: 5

  # Priming (Phase 1 retrieval) - MUST align with supporting_context budget
  priming:
    enabled: true
    token_budget: 8000       # Should be < supporting_context_budget × 0.8
    top_entities: 50         # Entities by hit_count
    max_insights: 15         # Recent insights
    max_summaries: 10        # Turn summaries
    max_facts: 20            # Graph facts
    recency_days: 0          # Filter by age (0 = all time)
    previous_sessions: 1     # Cross-session history (bypasses supporting_context!)
    previous_session_turns: 5  # Keep low - each turn is ~200 tokens
```

### Recommended Budget Configuration

| Context Window | budget_ratio | priming.token_budget | Rationale |
|----------------|--------------|---------------------|-----------|
| 8,000 | 0.25 | 1,500 | Small models need more room for history |
| 32,000 | 0.30 | 7,000 | Balanced for most use cases |
| 64,000 | 0.30 | 15,000 | More headroom for rich context |
| 128,000 | 0.30 | 30,000 | Large windows can afford more priming |

**Rules of thumb**:
1. `priming.token_budget` should be **under 80%** of calculated supporting_context_budget
2. Supporting context budget = `(context_window - 3000) × budget_ratio`
3. Keep `previous_sessions × previous_session_turns × 200` under 20% of history budget

## Pruning Cascade

When assembled context exceeds budget, the `ContextAssembler._apply_budget()` method drops content in priority order (lowest priority first):

### Drop Order

1. **DECAYED memories** - Always excluded (filtered first)
2. **Deep history** - Turns older than 10 are dropped
3. **Low-relevancy long-term** - Long-term memories with `inclusion_score < 0.3`
4. **Weak matches** - Vector passages with `relevancy_score < 0.5`
5. **Recent history** - Keep only last 5 turns
6. **Top passages** - Keep 3 short-term, 2 long-term passages
7. **Insights/summaries** - Keep top 3 each
8. **Entities/facts** - Keep top 5 each
9. **Critical minimum** - Last 2 turns only (emergency)

### Conditional Exclusions

- **Summaries excluded** when: history has 10+ turns AND session has 3+ turns (summaries become redundant)
- **Insights filtered** by keyword overlap with current query

## Context Engineering Budget Configuration

Understanding how token budgets interact across the context engineering pipeline is critical for preventing prompt overflow and LLM timeouts.

### The Two-Phase Budget Problem

Budget enforcement happens in **two separate phases**, which can lead to overflow if not properly coordinated:

```
Phase 1: RETRIEVAL (ContextAssembler._apply_budget)
  ├── Estimates tokens using raw text lengths
  ├── Prunes history, passages, insights based on budget_limit
  └── Returns pruned ContextPayload

Phase 2: FORMATTING (PromptArchitect._format_prompt_attention)
  ├── Adds formatting overhead (timestamps, headers, separators)
  ├── Builds supporting context (passages, facts, insights, tools)
  ├── Merges prior_history with current history
  └── Returns final messages array

PROBLEM: Content added in Phase 2 bypasses Phase 1 budget checks!
```

### What Gets Added After Budget Checks

The following content is added during formatting and NOT counted during retrieval-phase budgeting:

| Content Type | Tokens Per Item | Notes |
|--------------|-----------------|-------|
| Timestamp prefix `[2026-01-30 14:23]` | ~8 tokens | Added to every history turn |
| Role prefix `[Chuck]:` or `[Friday]:` | ~3 tokens | Added to every message |
| Section headers `## Recent Insights` | ~10 tokens | One per section |
| List item prefix `- ` | ~3 tokens | Per insight/summary/fact |
| Passage metadata headers | ~15 tokens | Source, type indicators |
| Tool call summaries | ~20-50 tokens | Per historical tool use |
| Separator `---` | ~5 tokens | Between context and query |

**Example overhead for 20 history turns:**
- Timestamps: 20 × 8 = 160 tokens
- Role prefixes: 40 × 3 = 120 tokens (user + assistant per turn)
- **Total: ~280 tokens** of "invisible" overhead

### Supporting Context Budget Configuration

The `supporting_context` configuration controls how much of the dynamic budget is allocated to supporting context vs conversation history:

```yaml
memory:
  supporting_context:
    # Percentage of dynamic budget for supporting context
    budget_ratio: 0.30  # 30% for context, 70% for history

    # Priority order when truncating (first = highest priority)
    section_priority:
      - recent_memories   # Relationship summaries from graph
      - passages          # Vector search results
      - key_facts         # Extracted facts
      - insights          # Contextual observations
      - summaries         # Conversation summaries
      - tools             # Tool recommendations
      - state             # Session variables

    # Hard limits per section (applied before budget truncation)
    max_items:
      passages: 10
      key_facts: 20
      insights: 15
      summaries: 10
      tools: 5
```

### Budget Calculation Walkthrough

Here's the complete budget math for a typical configuration:

```
GIVEN:
  context_window: 40,000 tokens
  output_buffer: 1,000 tokens
  system_prompt: ~1,500 tokens
  tool_definitions: ~500 tokens
  budget_ratio: 0.30

STEP 1: Calculate Fixed Costs
  fixed_costs = system_prompt + tool_definitions + output_buffer
  fixed_costs = 1,500 + 500 + 1,000 = 3,000 tokens

STEP 2: Calculate Dynamic Budget
  dynamic_budget = context_window - fixed_costs
  dynamic_budget = 40,000 - 3,000 = 37,000 tokens

STEP 3: Allocate Dynamic Budget
  supporting_context_budget = dynamic_budget × budget_ratio
  supporting_context_budget = 37,000 × 0.30 = 11,100 tokens

  history_budget = dynamic_budget × (1 - budget_ratio)
  history_budget = 37,000 × 0.70 = 25,900 tokens
```

### Aligning Priming with Supporting Context

**Critical insight**: The `priming.token_budget` setting controls how much data is **retrieved**, while `supporting_context.budget_ratio` controls how much is **formatted** into the final prompt.

These must be aligned:

```yaml
# PROBLEMATIC: Priming retrieves more than formatting allows
priming:
  token_budget: 15000    # Retrieves 15K tokens
supporting_context:
  budget_ratio: 0.30     # But only 11.1K tokens fit!
  # Result: 4K tokens retrieved but truncated = wasted work

# ALIGNED: Priming respects formatting budget
priming:
  token_budget: 8000     # Retrieves 8K tokens (< 11.1K)
supporting_context:
  budget_ratio: 0.30     # 11.1K budget leaves headroom
  # Result: All primed content fits with room for overhead
```

### Prior History: The Hidden Budget Consumer

Cross-session history (`prior_history`) is a common source of budget overflow because it:

1. Is retrieved during priming (subject to `priming.token_budget`)
2. Is formatted into **history** messages (NOT supporting context)
3. Bypasses the `supporting_context.budget_ratio` allocation

```yaml
priming:
  # These settings add turns to prior_history
  previous_sessions: 2          # Include 2 prior sessions
  previous_session_turns: 10    # 10 turns each
  # Total: 20 prior turns × ~200 tokens = 4,000 tokens!

  # This budget covers insights/summaries/facts but NOT prior_history
  token_budget: 8000

# Prior history eats into the history_budget, not supporting_context_budget
# With history_budget = 25,900 and prior_history = 4,000
# Only 21,900 tokens remain for current session history
```

### Configuration Recommendations by Context Window

| Context Window | budget_ratio | priming.token_budget | max_history_turns | prior_turns |
|----------------|--------------|---------------------|-------------------|-------------|
| 8,000 | 0.25 | 1,500 | 5 | 0 |
| 16,000 | 0.28 | 3,500 | 10 | 3 |
| 32,000 | 0.30 | 7,000 | 15 | 5 |
| 64,000 | 0.30 | 15,000 | 20 | 10 |
| 128,000 | 0.30 | 30,000 | 30 | 15 |

**Guidelines:**

1. **Keep `priming.token_budget` under 80%** of `supporting_context_budget` to leave room for formatting overhead

2. **Limit prior_history aggressively** - each turn is 150-300 tokens and bypasses supporting context budget

3. **Calculate your actual budget**:
   ```
   supporting_context_budget = (context_window - 3000) × budget_ratio
   priming.token_budget should be < supporting_context_budget × 0.8
   ```

4. **Account for history growth** - if `max_history_turns: 20`, that's potentially 4,000-6,000 tokens

### Debugging Budget Issues

Use the `/debug-budget` command (if available) or check logs for budget warnings:

```
# Warning logged when prompt exceeds budget:
WARNING - Prompt exceeds budget: 45000 > 39000 tokens (overage: 6000 tokens, 15.4%)

# Debug log showing budget allocation:
DEBUG - Budget allocation: max_tokens=40000, fixed=3000, dynamic=37000,
        supporting_context=11100 (ratio=0.30)
```

**Common warning signs:**

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| "Prompt exceeds budget" warnings | Misaligned priming/supporting_context | Reduce `priming.token_budget` |
| Sections showing "(truncated)" | Budget too small for content | Increase `budget_ratio` or reduce priming |
| Slow responses, timeouts | Prompt near context limit | Reduce all limits conservatively |
| Missing expected context | Over-aggressive truncation | Check `section_priority` order |

## Memory Lifecycle Stages

Memories transition through stages based on access patterns and age:

```
SHORT_TERM → LONG_TERM → DECAYED → (deleted)
```

### Stage Thresholds

| Transition | Threshold | Criteria |
|------------|-----------|----------|
| SHORT_TERM → LONG_TERM | Score ≥ 0.7 | High access + confidence + connections |
| Any → DECAYED | Score < 0.2 | Low access, old age |
| DECAYED → Deleted | 30 days | Retention period expired |

### Promotion Score Weights

```python
promotion_score = (
    0.2 * age_factor +        # Older = more stable
    0.4 * access_factor +     # Most important: usage frequency
    0.2 * confidence_factor + # Extraction confidence
    0.2 * connection_factor   # Graph connectivity
)
```

### Decay Formula

```python
score(t) = initial_score * exp(-decay_rate * hours_since_last_access)

# Default decay_rate: 0.01/hour
# After 24h: 79% of original score
# After 1 week: 37% of original score
```

## Hebbian Learning (Graph Memory)

Graph nodes and edges use Hebbian learning: "neurons that fire together wire together."

### When Access is Recorded

| Event | Node hit_count | Edge hit_count |
|-------|----------------|----------------|
| Entity extracted from conversation | ✅ Incremented | - |
| **Duplicate entity detected during extraction** | ✅ Incremented | - |
| Relationship extracted from conversation | - | ✅ Incremented |
| **Duplicate edge detected during extraction** | - | ✅ Incremented |
| Entity retrieved during recall | ✅ Incremented | - |
| Graph traversal (get_neighbors) | ❌ Pure read | ❌ Pure read |

### Key Insight: Extraction Reinforcement

When the LLM extracts the same entity or relationship multiple times across conversations, the duplicate detection triggers reinforcement:

```python
# In add_node() when duplicate detected:
existing_data["hit_count"] = existing_data.get("hit_count", 0) + 1
existing_data["last_accessed"] = datetime.now().isoformat()

# In add_edge() when duplicate detected:
existing_data["hit_count"] = existing_data.get("hit_count", 0) + 1
existing_data["last_accessed"] = datetime.now().isoformat()
```

This means:
- Frequently mentioned entities naturally rise to the top
- Important relationships get reinforced over time
- Stale entities/edges (low hit_count, old last_accessed) become candidates for pruning

### Priming Priority

When selecting entities for context priming:

```python
# Sorted by hit_count DESC, then last_accessed DESC (tiebreaker)
top_nodes = sorted(
    all_nodes,
    key=lambda x: (x.hit_count, x.last_accessed or datetime.min),
    reverse=True,
)
```

## Retrieval Scoring

### Inclusion Score

Determines which memories make it into context:

```python
inclusion_score = similarity * retrieval_factor

retrieval_factor = time_factor * usage_factor

time_factor = exp(-0.005 * age_hours)
# 24h → 0.89, 72h → 0.70, 168h → 0.43

usage_factor = 1.0 + (0.1 * log(1 + hit_count))
# hit=0 → 1.0, hit=5 → 1.18, hit=20 → 1.30
```

### Minimum Similarity Thresholds

| Memory Stage | Min Similarity | Purpose |
|--------------|----------------|---------|
| Short-term | 0.5 | More permissive for recent memories |
| Long-term | 0.7 | Higher bar for older memories |
| Inclusion | 0.6 | Default threshold for context inclusion |

## Maintenance Operations

### Automatic (on session exit)

- **Lifecycle decay**: Updates scores, promotes/demotes memories
- **Access buffer flush**: Persists hit counts

### Manual Commands

| Command | Action |
|---------|--------|
| `/reorganize` | Full maintenance pipeline |
| `/reorganize --prune` | Remove redundant/stale memories |
| `/reorganize --synthesize` | Generate meta-insights from clusters |
| `/reorganize --lifecycle` | Run decay calculations |
| `/consolidate` | Summarize old turns, deduplicate |

## Diagnosing Bloated Prompts

### Symptoms

- LLM timeouts
- Slow response times
- High token usage in `/memory` output

### Diagnostic Steps

1. Run `/memory` to see token statistics:
   ```
   Context Token Usage (estimated via tiktoken):
     Last context: 28,523 tokens
     Budget used: 89.1%  ← Too high!
   ```

2. Check `/context` for what's being included

3. Review config settings for oversized allocations

### Common Causes

| Issue | Symptom | Fix |
|-------|---------|-----|
| `max_history_turns` too high | Budget used >80% | Reduce to 10-20 |
| `priming.token_budget` > supporting_context budget | "Prompt exceeds budget" warnings | Align priming with `budget_ratio × dynamic_budget × 0.8` |
| `previous_session_turns` too high | Prior history consumes history budget | Reduce to 5 or disable |
| Too many entities/insights | Priming alone exceeds budget | Reduce `top_entities`, `max_insights` |
| No lifecycle maintenance | Old memories accumulate | Run `/reorganize` periodically |
| `budget_ratio` too low | Context truncated, missing info | Increase from 0.25 to 0.35 |
| `budget_ratio` too high | Not enough room for history | Decrease to 0.25-0.30 |

## Best Practices

1. **Monitor token usage** - Use `/memory` command regularly to track context size trends

2. **Align priming with formatting budget** - Calculate your supporting_context_budget first:
   ```yaml
   # For 40K context window:
   # supporting_context_budget = (40000 - 3000) × 0.30 = 11,100 tokens
   # Set priming.token_budget to 80% of that = 8,880 → round to 8,000

   supporting_context:
     budget_ratio: 0.30
   priming:
     token_budget: 8000  # Under 80% of supporting_context_budget
   ```

3. **Be conservative with cross-session history** - Prior history bypasses supporting_context budget:
   ```yaml
   priming:
     previous_sessions: 1         # Not 2-3
     previous_session_turns: 5    # Not 10-20
   ```

4. **Run maintenance** - Execute `/reorganize` weekly or after intensive sessions

5. **Use lifecycle decay** - Enable `lifecycle.enabled: true` to automatically age out stale memories

6. **Filter by recency** - Set `priming.recency_days: 30` to exclude ancient memories

7. **Watch for warnings** - Log messages like "Prompt exceeds budget" indicate misaligned configuration

8. **Test with large payloads** - After config changes, have conversations that generate lots of context to verify budgets hold

## File References

| Component | Location |
|-----------|----------|
| Context Assembler | `packages/friday-memory/src/friday_memory/context/assembler.py` |
| Prompt Architect | `packages/friday-memory/src/friday_memory/context/layout.py` |
| SupportingContextConfig | `packages/friday-memory/src/friday_memory/context/layout.py` |
| Lifecycle Decay | `packages/friday-memory/src/friday_memory/lifecycle/decay.py` |
| Inclusion Scoring | `packages/friday-memory/src/friday_memory/retrieval/inclusion_scorer.py` |
| Reorganizer | `packages/friday-memory/src/friday_memory/maintenance/reorganizer.py` |
| Collection Manager | `packages/friday-memory/src/friday_memory/retrieval/collection_manager.py` |
| Example Config | `tests/integration/memory/config.yaml` |
