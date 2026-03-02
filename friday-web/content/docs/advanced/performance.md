---
title: "Performance Optimization"
description: "Profiling, token budget tuning, and concurrency patterns for high-throughput use."
weight: 3
---

Optimize Friday for high-throughput workloads by profiling the Re-Act loop, tuning token budgets, and leveraging async concurrency across tool calls.

## Context Assembly Optimization

### Parallel Store Retrieval

The single largest latency improvement available is parallelizing the three memory store queries that happen at the start of every turn.

**Before (Sequential — Slow):**

```python
async def assemble_context_sequential(session_id, user_message):
    # Sequential queries = sum of latencies
    episodic = await transcript_store.get_recent_turns(session_id, limit=10)  # 50ms
    semantic = await vector_store.similarity_search(user_message, limit=20)    # 180ms
    associative = await graph_store.get_related_entities(user_message)         # 80ms

    # Total: 310ms
    return {"episodic": episodic, "semantic": semantic, "associative": associative}
```

**After (Parallel — Fast):**

```python
async def assemble_context_parallel(session_id, user_message):
    # Parallel queries = max of latencies (not sum!)
    episodic_task = transcript_store.get_recent_turns(session_id, limit=10)
    semantic_task = vector_store.similarity_search(user_message, limit=20)
    associative_task = graph_store.get_related_entities(user_message)

    episodic, semantic, associative = await asyncio.gather(
        episodic_task,
        semantic_task,
        associative_task,
    )

    # Total: 180ms (longest task) — 42% faster
    return {"episodic": episodic, "semantic": semantic, "associative": associative}
```

| Method | Latency | Improvement |
|--------|---------|-------------|
| Sequential | 310ms | Baseline |
| Parallel (asyncio.gather) | 180ms | 42% faster |

### Context Caching

Cache assembled context for rapid-fire turns in the same session.

```python
from cachetools import TTLCache

class CachedContextAssembler:
    """Context assembler with TTL cache."""

    def __init__(self, assembler, ttl_seconds=60):
        self.assembler = assembler
        self.cache = TTLCache(maxsize=100, ttl=ttl_seconds)

    async def assemble(self, session_id: str, user_message: str):
        cache_key = f"{session_id}:{hash(user_message)}"

        if cache_key in self.cache:
            logger.debug(f"Context cache hit: {cache_key}")
            return self.cache[cache_key]

        context = await self.assembler.assemble(session_id, user_message)
        self.cache[cache_key] = context
        return context
```

**Cache Invalidation:**

```python
# Invalidate cache when memory is updated
@memory_controller.on_memory_update
async def invalidate_context_cache(session_id: str):
    keys_to_remove = [k for k in cache.keys() if k.startswith(f"{session_id}:")]
    for key in keys_to_remove:
        del cache[key]
```

**Benchmark:**

| Turn | Uncached | Cached | Speedup |
|------|----------|--------|---------|
| 1 | 180ms | 180ms (miss) | 1x |
| 2 (similar) | 180ms | 2ms (hit) | 90x |
| 3 (similar) | 180ms | 2ms (hit) | 90x |
| 4 (different) | 180ms | 180ms (miss) | 1x |

This is most effective in chat interfaces where users ask rapid follow-up questions.

### Lazy Entity Loading

Avoid loading full entity details until they are actually needed.

```python
class LazyEntity:
    """Entity proxy that loads details on-demand."""

    def __init__(self, name: str, entity_type: str, graph_store):
        self.name = name
        self.type = entity_type
        self._graph_store = graph_store
        self._details = None

    @property
    async def description(self) -> str:
        if self._details is None:
            self._details = await self._graph_store.get_entity(self.name)
        return self._details.description

    @property
    async def relationships(self) -> list:
        if self._details is None:
            self._details = await self._graph_store.get_entity(self.name)
        return self._details.relationships

# Context assembly loads only entity names initially
entities = [
    LazyEntity(name="Python", entity_type="Technology", graph_store=graph_store),
    LazyEntity(name="Alice", entity_type="Person", graph_store=graph_store),
]

# Details loaded only when the agent actually accesses them
description = await entities[0].description  # Triggers DB load
```

## Memory Store Indexing

### SQLite (Episodic Store)

Add composite indexes on the columns used in the most common queries.

```sql
-- Index for session-based queries (most common)
CREATE INDEX idx_turns_session_timestamp
    ON turns(session_id, timestamp DESC);

-- Index for user-based queries
CREATE INDEX idx_turns_user_timestamp
    ON turns(user_id, timestamp DESC);

-- Index for tool execution queries
CREATE INDEX idx_turns_tool_calls
    ON turns(tool_calls)
    WHERE tool_calls IS NOT NULL;

-- Verify query plans
EXPLAIN QUERY PLAN
SELECT * FROM turns
WHERE session_id = 'abc123'
ORDER BY timestamp DESC
LIMIT 10;
```

### ChromaDB (Vector Store)

Tune HNSW index parameters for your workload's quality/speed tradeoff.

```python
# Tune HNSW index parameters at collection creation
collection = client.create_collection(
    name="memories_long_term",
    metadata={
        "hnsw:space": "cosine",           # Distance metric
        "hnsw:M": 16,                     # Max connections per layer
        "hnsw:ef_construction": 200,      # Construction effort
        "hnsw:ef_search": 100,            # Search effort
    },
)
```

**HNSW Tuning Guide:**

| Use Case | M | ef_construction | ef_search | Quality | Speed |
|----------|---|-----------------|-----------|---------|-------|
| Speed-critical | 8 | 100 | 50 | Good | Very Fast |
| Balanced (default) | 16 | 200 | 100 | Better | Fast |
| Quality-critical | 32 | 400 | 200 | Best | Slower |

### NetworkX (Graph Store)

Cache neighborhood subgraphs for entities that are queried repeatedly.

```python
from functools import lru_cache
from collections import defaultdict

# Cache entity neighborhoods
@lru_cache(maxsize=100)
def get_entity_neighborhood(entity_name: str, depth: int = 1):
    """Cache entity neighborhood subgraphs."""
    return nx.ego_graph(graph, entity_name, radius=depth)

# Index entities by type for fast filtering
entity_by_type = defaultdict(list)
for entity_name, entity_data in graph.nodes(data=True):
    entity_by_type[entity_data["type"]].append(entity_name)
```

## Token Budget Optimization

### Strategy 1: Summarize Old Turns

Keep recent turns verbatim, summarize older turns to fit the budget.

```python
async def compress_history(turns: list, max_tokens: int = 2000):
    """
    Summarize old conversation turns to fit the token budget.

    Keep recent turns verbatim, summarize older turns.
    """
    if estimate_tokens(turns) <= max_tokens:
        return turns  # Fits already

    # Keep last 3 turns verbatim
    recent_turns = turns[-3:]
    old_turns = turns[:-3]

    old_text = "\n\n".join(
        f"User: {t.user_message}\nAssistant: {t.assistant_message}"
        for t in old_turns
    )

    summary = await llm.generate(
        f"Summarize this conversation concisely:\n\n{old_text}"
    )

    summary_turn = Turn(
        id="summary",
        user_message="[Earlier conversation]",
        assistant_message=summary,
    )

    return [summary_turn] + recent_turns
```

### Strategy 2: Aggressive Relevance Filtering

Raise the similarity threshold to include only highly relevant memories.

```python
async def filter_low_relevance_memories(
    memories: list,
    threshold: float = 0.75,  # Raised from default 0.70
):
    """
    Use a higher similarity threshold to include only highly relevant memories.

    Tradeoff: Fewer memories, but each is more relevant.
    """
    filtered = [m for m in memories if m.similarity >= threshold]
    logger.info(f"Filtered {len(memories)} -> {len(filtered)} memories (threshold {threshold})")
    return filtered
```

### Strategy 3: Tool Schema Minimization

Strip descriptions from tool schemas when token budget is tight.

```python
def minimize_tool_schema(tool) -> dict:
    """
    Generate minimal tool schema (parameters only, no descriptions).

    Use when token budget is tight.
    """
    return {
        "name": tool.name,
        "parameters": {
            param_name: {"type": param_type.__name__}
            for param_name, param_type in tool.parameters_schema.__annotations__.items()
        },
    }

# Before: ~150 tokens per tool (with descriptions)
# After: ~30 tokens per tool (parameters only)
# Savings: 80%
```

### Dynamic Budget Reallocation

Allocate context tokens dynamically based on actual message size.

```python
async def assemble_context_dynamic(session_id, user_message, total_budget=8000):
    """
    Dynamically reallocate token budget based on what is available.

    Priority order: system > query > history > context
    """
    budgets = {
        "system": 1000,
        "query": len(user_message.split()),  # Actual size
        "history": 2000,
        "context": 4000,
    }

    used = budgets["system"] + budgets["query"]
    remaining = total_budget - used

    if remaining < 6000:
        # Tight budget - reduce history, prioritize context
        budgets["history"] = int(remaining * 0.3)
        budgets["context"] = int(remaining * 0.7)
    else:
        # Plenty of space - use targets
        budgets["history"] = 2000
        budgets["context"] = remaining - 2000

    return await assemble_with_budgets(
        session_id,
        user_message,
        history_budget=budgets["history"],
        context_budget=budgets["context"],
    )
```

## Memory Lifecycle Optimization

### Hot-Cold Memory Tiers

Implement multi-tier decay based on memory type for fine-grained control.

```yaml
memory:
  lifecycle:
    # Hot tier: Temporary task memory (fast decay)
    hot_tier:
      types: ["task", "scratch_note", "temporary"]
      decay_rate: 0.1           # 49% after 7 hours
      promotion_threshold: 0.9
      collection: "short_term"

    # Warm tier: Current project context (normal decay)
    warm_tier:
      types: ["observation", "decision"]
      decay_rate: 0.01          # 49% after 72 hours
      promotion_threshold: 0.7
      collection: "long_term"

    # Cold tier: Learned preferences (slow decay)
    cold_tier:
      types: ["preference", "expertise", "relationship"]
      decay_rate: 0.001         # 49% after 30 days
      promotion_threshold: 0.5
      collection: "long_term"
```

**Implementation:**

```python
class TieredLifecycleManager:
    """Lifecycle manager with hot/warm/cold tiers."""

    TIERS = {
        "hot": {"decay_rate": 0.1, "promotion_threshold": 0.9},
        "warm": {"decay_rate": 0.01, "promotion_threshold": 0.7},
        "cold": {"decay_rate": 0.001, "promotion_threshold": 0.5},
    }

    TYPE_TO_TIER = {
        "task": "hot", "scratch_note": "hot", "temporary": "hot",
        "observation": "warm", "decision": "warm",
        "preference": "cold", "expertise": "cold", "relationship": "cold",
    }

    async def calculate_decay(self, memory) -> float:
        tier = self.TYPE_TO_TIER.get(memory.type, "warm")
        config = self.TIERS[tier]

        hours_since_access = (now() - memory.last_accessed).total_seconds() / 3600
        return memory.initial_score * exp(-config["decay_rate"] * hours_since_access)
```

### Graph Pruning Strategies

As the knowledge graph grows, performance degrades. Prune intelligently to maintain quality.

**Weak Edge Removal:**

```python
async def prune_weak_edges(graph_store, min_hit_count=3, min_confidence=0.6):
    """Remove low-confidence relationships that have not been reinforced by usage."""
    pruned = 0

    for edge in graph_store.get_all_edges():
        if edge.hit_count < min_hit_count and edge.confidence < min_confidence:
            graph_store.remove_edge(edge.source, edge.verb, edge.target)
            pruned += 1

    logger.info(f"Pruned {pruned} weak edges")
    return pruned
```

**Recommended pruning thresholds by graph size:**

| Graph Size | Min Hit Count | Min Confidence | % Edges Removed |
|------------|---------------|----------------|-----------------|
| <1K entities | 2 | 0.5 | ~5% |
| 1K-10K entities | 3 | 0.6 | ~15% |
| >10K entities | 5 | 0.7 | ~25% |

**Orphan Node Cleanup:**

```python
async def remove_orphan_nodes(graph_store, min_age_days=7):
    """Remove entities with no relationships and low hit_count."""
    orphans = []

    for entity in graph_store.get_all_entities():
        relationships = graph_store.get_relationships(entity.name)

        if (
            len(relationships) == 0
            and entity.hit_count < 3
            and (now() - entity.created_at).days >= min_age_days
        ):
            orphans.append(entity.name)

    for entity_name in orphans:
        graph_store.remove_entity(entity_name)

    logger.info(f"Removed {len(orphans)} orphan entities")
    return len(orphans)
```

## Related Pages

- [Hybrid Cloud-Local](/docs/advanced/hybrid/) — Reduce cost with local model routing
- [Memory Settings](/docs/configuration/memory/) — Configure decay, priming, and lifecycle
- [Deployment Patterns](/docs/advanced/deployment/) — Production deployment architectures
