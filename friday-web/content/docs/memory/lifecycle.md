---
title: "Memory Lifecycle"
description: "How memories are created, promoted, decayed, and reactivated over time."
weight: 2
---

Every memory in Friday follows a lifecycle: creation from an extraction event, promotion through repeated access, gradual decay when unused, and reactivation when referenced again.

Friday's semantic memories (insights and facts in the vector store) don't remain static—they evolve through a **lifecycle** based on usage patterns and age. This mimics how human memory works: frequently-accessed information strengthens, while unused information fades but remains recoverable.

---

## The Four Stages: A Memory's Journey

```text
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY LIFECYCLE                         │
│                                                             │
│   EXTRACTION          SHORT-TERM          LONG-TERM         │
│       │                  │                   │              │
│       ▼                  ▼                   ▼              │
│   [New Insight] ──► [24h + access] ──► [Validated]        │
│                         │                   │              │
│                         ▼                   ▼              │
│                    [No access]         [No access]         │
│                         │                   │              │
│                         ▼                   ▼              │
│                     [DECAYED]          [DECAYED]           │
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

### Stage 1: SHORT-TERM (`memories_short_term` collection)

- **Entry condition**: Newly extracted from conversation
- **Characteristics**:
  - Age < 24 hours (configurable)
  - Unproven, tentative knowledge
  - Higher similarity threshold for retrieval (0.75)
  - Awaiting validation through access patterns
- **Exit conditions**:
  - **Promotion → LONG-TERM**: High access + minimum age
  - **Decay → DECAYED**: No access for threshold period

### Stage 2: LONG-TERM (`memories_long_term` collection)

- **Entry condition**: Promoted from short-term OR reactivated from decayed
- **Characteristics**:
  - Age > 24 hours AND high access frequency
  - Validated, core knowledge
  - Lower similarity threshold (0.65) — easier retrieval
  - Most relevant for context assembly
- **Exit condition**:
  - **Decay → DECAYED**: No access for extended period (7+ days)

### Stage 3: DECAYED (`memories_decayed` collection)

- **Entry condition**: No access for threshold period from short-term or long-term
- **Characteristics**:
  - "Forgotten" but not deleted
  - Highest similarity threshold (0.80) — hard to retrieve
  - Soft-deleted pattern (recoverable)
  - Candidates for permanent deletion
- **Exit conditions**:
  - **Reactivation → LONG-TERM**: Accessed again (proves relevance)
  - **Deletion**: Manual cleanup or 30+ days in decayed state

### Stage 4: DELETED (Removed from store)

- **Entry condition**: Manual deletion OR automated cleanup after retention period
- Permanently removed from vector store — cannot be recovered
- Frees storage space and improves search performance

---

## Promotion: Short-Term → Long-Term

**Goal:** Identify valuable memories that deserve permanent storage.

### Promotion Scoring Algorithm

Memories are evaluated using a **multi-factor scoring function**:

```python
def calculate_promotion_score(memory: Insight) -> float:
    """
    Calculate promotion score (0.0-1.0) for a short-term memory.

    Score >= 0.7 AND age >= 24h -> Promote to long-term
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
1. **Promotion score >= 0.7** (default threshold)
2. **Age >= 24 hours** (minimum time in short-term)

**Why both conditions?**
- **Score threshold**: Ensures quality (don't promote low-value memories)
- **Age threshold**: Prevents premature promotion (let usage patterns emerge)

### Example Promotion Scenarios

**Scenario A: Quick Promotion (2 days)**

```text
Insight: "User prefers FastAPI over Flask"
- Age: 48 hours → age_factor = 0.13
- Access count: 8 → access_factor = 0.32
- Confidence: 0.92 → confidence_factor = 0.18
- Connections: 4 → connection_factor = 0.16

Total score: 0.13 + 0.32 + 0.18 + 0.16 = 0.79  PROMOTE
```

**Scenario B: No Promotion (Low Access)**

```text
Insight: "Weather was nice today"
- Age: 48 hours → age_factor = 0.13
- Access count: 0 → access_factor = 0.00
- Confidence: 0.65 → confidence_factor = 0.13
- Connections: 1 → connection_factor = 0.04

Total score: 0.13 + 0.00 + 0.13 + 0.04 = 0.30  DO NOT PROMOTE
```

---

## Decay: Long-Term → Decayed

**Goal:** Identify unused memories to free up retrieval "attention" for more relevant content.

### Decay Algorithm

Friday uses **exponential decay** modeled after the Ebbinghaus forgetting curve:

```python
def calculate_decay_score(memory: Insight, lambda_decay: float = 0.01) -> float:
    """
    Calculate current memory strength using exponential decay.

    Score < 0.5 -> Decay to decayed collection
    """
    # Time since last access (in hours)
    hours_since_access = (now() - memory.last_accessed).total_seconds() / 3600

    # Exponential decay formula
    decay_score = memory.initial_score * exp(-lambda_decay * hours_since_access)

    return decay_score
```

**Decay Formula:**

```text
score(t) = score_0 x e^(-lambda * t)

where:
  score_0 = initial score (typically 1.0 for long-term memories)
  lambda = decay rate (default 0.01)
  t = hours since last access
  e = Euler's number (2.71828...)
```

**Decay Rates at lambda=0.01:**

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
- **Configurable**: Adjust lambda for different retention behaviors

### Configurable Decay Rates

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

---

## Reactivation: Decayed → Long-Term

**Goal:** Recover "forgotten" memories when they become relevant again.

### The Soft-Delete Pattern

Friday never permanently deletes memories until explicitly confirmed. Decayed memories remain in the vector store, just with a higher retrieval threshold (0.80 vs. 0.65 for long-term).

**Reactivation Trigger:**

```python
if memory in decayed_collection and memory.similarity > 0.80:
    # Memory accessed despite being decayed -> proves relevance
    memory.move_to(long_term_collection)
    memory.access_count += 1
    memory.last_accessed = now()
    memory.decay_score = 1.0  # Reset decay
```

**Reactivation Scenario:**

```text
Day 1: User mentions "I'm interested in GraphQL"
        -> Insight extracted: "User interested in GraphQL"
        -> Short-term collection

Day 3: Insight promoted to long-term (high access during research)

Day 10: No GraphQL mentions for a week
         -> Decay score = 0.49
         -> Moved to decayed collection

Day 45: User asks "What was that API technology I was looking at?"
         -> Semantic search: "API technology" -> GraphQL insight found (sim=0.83)
         -> Reactivated to long-term
         -> Friday responds: "You were interested in GraphQL for APIs"
```

**Why reactivation matters:**
- **No premature deletion**: Prevents losing valuable memories permanently
- **Context-driven recovery**: Memories return when contextually relevant
- **Adaptive retention**: System learns what's important through repeated reactivation

---

## Lifecycle Operations

### Automatic Lifecycle (Default)

```yaml
memory:
  lifecycle:
    auto_lifecycle: true          # Run after each turn
    promotion_threshold: 0.7      # Minimum score for promotion
    promotion_min_age_hours: 24   # Minimum time before promotion
    decay_rate: 0.01              # Exponential decay rate (lambda)
    decay_threshold_turns: 3      # Check decay every N turns
```

### Manual Lifecycle (Advanced)

```bash
# Run full lifecycle cycle manually
/lifecycle

# Individual operations
/lifecycle --promote   # Only run promotion
/lifecycle --decay     # Only run decay
/lifecycle --stats     # Show lifecycle statistics
```

### Lifecycle Stats Output

```text
==============================================================
MEMORY LIFECYCLE STATISTICS
==============================================================
Vector Store:
  Short-term:  45 insights
  Long-term:   123 insights
  Decayed:     18 insights
  Total:       186 insights

Last Cycle: 2026-01-24 14:30:00
  Promoted:   3 insights (short -> long)
  Decayed:    2 insights (long -> decayed)
  Reactivated: 1 insight (decayed -> long)

Candidates:
  Promotion ready:  5 insights (score >= 0.7, age >= 24h)
  Decay candidates: 8 insights (score < 0.5)

Collection Distribution:
  Short-term: 24% (ideal: 20-30%)
  Long-term:  66% (ideal: 60-70%)
  Decayed:    10% (ideal: <15%)
==============================================================
```

---

## Tuning Lifecycle for Your Use Case

**Personal Assistant (Stable Preferences):**

```yaml
memory:
  lifecycle:
    decay_rate: 0.001              # Very slow decay (49% after 30 days)
    promotion_threshold: 0.6       # Easier promotion
    promotion_min_age_hours: 12    # Faster promotion
```

Rationale: Personal preferences are stable—promote quickly, decay slowly.

**Research Assistant (Temporary Topics):**

```yaml
memory:
  lifecycle:
    decay_rate: 0.02               # Faster decay (49% after 36h)
    promotion_threshold: 0.8       # Stricter promotion
    promotion_min_age_hours: 48    # Longer validation period
```

Rationale: Research topics change frequently—only promote high-value insights, decay quickly.

**Customer Support (Session-Scoped):**

```yaml
memory:
  lifecycle:
    decay_rate: 0.05               # Very fast decay (49% after 14h)
    promotion_threshold: 0.9       # Very strict
    promotion_min_age_hours: 72    # Long validation
```

Rationale: Each customer interaction is isolated—minimal long-term retention.

---

## Stage Transition Rules

From the FRIDAY-FEATURES.md implementation details:

| Transition | Trigger | Criteria |
|------------|---------|----------|
| SHORT_TERM → LONG_TERM | Reorganization | promotion_score >= 0.7 AND age >= 24h |
| LONG_TERM → DECAYED | Decay cycle | decay_score < 0.2 |
| DECAYED → LONG_TERM | Access | Memory accessed while decayed (reactivation) |
| DECAYED → DELETED | Retention expiry | age > 30 days + explicit confirmation |

{{< callout type="info" >}}
Lifecycle operations run asynchronously—they don't block conversation turns. Storage growth is bounded because decayed memories can be purged on schedule. Use `/lifecycle --stats` to monitor memory distribution across stages.
{{< /callout >}}

---

## Configuration Reference

```yaml
memory:
  lifecycle:
    enabled: true
    decay_rate: 0.01
    access_boost: 0.2
    promotion_threshold: 0.7
    decay_threshold: 0.2
    short_term_min_age_hours: 24
    decayed_retention_days: 30

  retrieval:
    access_buffer:
      max_buffer_size: 1000
      max_buffer_age_seconds: 300
    factor_computer:
      decay_rate: 0.005
      usage_boost_factor: 0.1
```
