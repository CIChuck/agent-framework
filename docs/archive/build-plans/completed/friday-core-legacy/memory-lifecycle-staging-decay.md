# Memory Lifecycle: Short-Term/Long-Term Separation and Temporal Decay

## Problem Statement

The current friday-memory implementation lacks effective separation between short-term and long-term memories:

1. **No Short-Term Stage**: Memories go directly from episodic to consolidated (long-term) without a short-term/working memory phase for evaluation
2. **No Temporal Decay**: All memories are treated equally regardless of age or access frequency - old, unused memories persist indefinitely
3. **Missing Lifecycle**: No clear promotion criteria or demotion paths for memories

## Current Architecture

| Store | Purpose | Current State |
|-------|---------|---------------|
| **Episodic** | Recent conversation history | SQLite `transcript.db`, short-term only |
| **Graph** | Entity relationships | NetworkX JSON, has `hit_count` but no decay |
| **Vector** | Semantic search | ChromaDB, has `consolidated` flag but binary |

The `consolidated` flag in vector metadata only indicates "has been processed" - not memory maturity or importance. The graph store tracks `hit_count` for Hebbian learning but never decreases importance of unused memories.

### Current Flow

```
User Message → Episodic Store (transcript.db)
                    ↓
              Consolidation
                    ↓
         Graph Store + Vector Store
              (consolidated=True)
```

No intermediate evaluation, no decay, no lifecycle management.

## Proposed Solution

### Memory Lifecycle Stages

```
EPISODIC → SHORT_TERM → LONG_TERM → DECAYED
    ↑                     │
    └─────────────────────┘ (rare: reactivation on access)
```

| Stage | Description | Retention |
|-------|-------------|-----------|
| `EPISODIC` | Raw conversation turns | Hours (current behavior) |
| `SHORT_TERM` | Consolidated insights awaiting promotion | Days |
| `LONG_TERM` | Proven, frequently-accessed memories | Indefinite (with decay) |
| `DECAYED` | Low-value memories for cleanup | Until pruned |

### Stage Transition Rules

| Transition | Trigger | Criteria |
|------------|---------|----------|
| EPISODIC → SHORT_TERM | Consolidation cycle | Insight extracted from episodic data |
| SHORT_TERM → LONG_TERM | Reorganization | Promotion score >= `promotion_threshold` AND age >= `short_term_min_age_hours` |
| LONG_TERM → DECAYED | Decay cycle | decay_score < `decay_threshold` |
| DECAYED → DELETED | Retention expiry | Age in DECAYED > `decayed_retention_days` |
| DELETED → (hard delete) | Manual prune | Explicit `/prune --force` command |
| DECAYED → LONG_TERM | Access | Memory accessed while in DECAYED state (reactivation) |

> **Soft-Delete Pattern**: DECAYED memories are not immediately removed. They enter a soft-delete state where they are excluded from retrieval but retained for recovery. Only after the retention period AND explicit confirmation are they permanently deleted.

---

## Core Components

### 1. MemoryStage Enum

```python
from enum import Enum

class MemoryStage(str, Enum):
    """Memory lifecycle stages."""
    EPISODIC = "episodic"       # Raw conversation, not yet consolidated
    SHORT_TERM = "short_term"   # Consolidated, awaiting promotion
    LONG_TERM = "long_term"     # Proven, frequently-accessed
    DECAYED = "decayed"         # Low-value, excluded from retrieval but recoverable
    DELETED = "deleted"         # Soft-deleted, pending hard delete after retention period
```

### 2. MemoryLifecycleMetadata

```python
from datetime import datetime
from pydantic import BaseModel, Field

class MemoryLifecycleMetadata(BaseModel):
    """Lifecycle tracking metadata for memories."""
    stage: MemoryStage = Field(default=MemoryStage.SHORT_TERM)
    decay_score: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed_at: datetime = Field(default_factory=datetime.now)
    last_decay_at: datetime | None = Field(default=None)
    promoted_at: datetime | None = Field(default=None)
    access_count: int = Field(default=0, ge=0)
```

### 3. DecayConfig

> **Two Decay Rates**: This system uses two separate decay rates for different purposes:
> - **Lifecycle decay** (`decay_rate`): Controls stage transitions (SHORT_TERM → LONG_TERM → DECAYED). Default: 0.01/hour (softer curve, ~79% remaining after 24h)
> - **Inclusion decay** (in `LongTermInclusionScorer`): Affects retrieval priority within a stage. Default: 0.005/hour (~89% remaining after 24h)
>
> These serve different purposes: lifecycle decay determines whether a memory is worth keeping, while inclusion decay determines whether it's worth retrieving for a specific query.

```python
class DecayConfig(BaseModel):
    """Configuration for temporal decay mechanism."""
    enabled: bool = Field(default=True, description="Enable decay calculations")

    # Decay parameters
    decay_rate: float = Field(
        default=0.01,  # Softer curve: ~79% after 24h, ~37% after 1 week
        ge=0.001,
        le=0.5,
        description="Lambda for exponential decay (higher = faster decay). At 0.01: 24h→79%, 72h→49%, 168h→19%"
    )
    access_boost: float = Field(
        default=0.2,
        ge=0.0,
        le=0.5,
        description="Score boost on each access"
    )

    # Thresholds
    promotion_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum score for SHORT_TERM → LONG_TERM promotion"
    )
    decay_threshold: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Score below which memory becomes DECAYED"
    )

    # Timing
    short_term_min_age_hours: int = Field(
        default=24,
        ge=1,
        description="Minimum hours in SHORT_TERM before eligible for promotion"
    )
    decay_check_interval_hours: int = Field(
        default=24,
        ge=1,
        description="How often to run decay calculations"
    )

    # Cleanup
    decayed_retention_days: int = Field(
        default=30,
        ge=1,
        description="Days to retain DECAYED memories before deletion"
    )

    # Promotion scoring weights (must sum to 1.0)
    promotion_weight_age: float = Field(
        default=0.2, ge=0.0, le=1.0,
        description="Weight for time spent in short-term"
    )
    promotion_weight_access: float = Field(
        default=0.4, ge=0.0, le=1.0,
        description="Weight for access frequency (most important)"
    )
    promotion_weight_confidence: float = Field(
        default=0.2, ge=0.0, le=1.0,
        description="Weight for extraction confidence"
    )
    promotion_weight_connection: float = Field(
        default=0.2, ge=0.0, le=1.0,
        description="Weight for graph connections"
    )

    @model_validator(mode='after')
    def validate_weights_sum(self) -> 'DecayConfig':
        """Ensure promotion weights sum to 1.0."""
        total = (
            self.promotion_weight_age +
            self.promotion_weight_access +
            self.promotion_weight_confidence +
            self.promotion_weight_connection
        )
        if not (0.99 <= total <= 1.01):  # Allow small float tolerance
            raise ValueError(f"Promotion weights must sum to 1.0, got {total}")
        return self
```

### 4. DecayCalculator

```python
import math
from datetime import datetime, timedelta

class DecayCalculator:
    """Calculates temporal decay for memories."""

    def __init__(self, config: DecayConfig):
        self._config = config

    def calculate_decay(
        self,
        current_score: float,
        last_decay_at: datetime,
        now: datetime | None = None,
    ) -> float:
        """
        Apply exponential decay to a memory's score.

        Formula: score(t) = score_0 * exp(-lambda * hours)

        Args:
            current_score: Current decay score (0.0-1.0)
            last_decay_at: When decay was last calculated
            now: Current time (default: datetime.now())

        Returns:
            New decay score after applying decay
        """
        now = now or datetime.now()
        hours_elapsed = (now - last_decay_at).total_seconds() / 3600

        if hours_elapsed <= 0:
            return current_score

        decay_factor = math.exp(-self._config.decay_rate * hours_elapsed)
        new_score = current_score * decay_factor

        return max(0.0, min(1.0, new_score))

    def apply_access_boost(self, current_score: float) -> float:
        """
        Boost score when memory is accessed.

        Args:
            current_score: Current decay score

        Returns:
            New score after applying boost
        """
        return min(1.0, current_score + self._config.access_boost)

    def should_decay_to_stage(self, score: float) -> bool:
        """Check if score is below decay threshold."""
        return score < self._config.decay_threshold
```

### 5. PromotionScorer

```python
class PromotionScorer:
    """Calculates promotion scores for SHORT_TERM → LONG_TERM transition."""

    def __init__(self, config: DecayConfig):
        self._config = config
        # Use configurable weights from DecayConfig
        self._weights = {
            "age": config.promotion_weight_age,
            "access": config.promotion_weight_access,
            "confidence": config.promotion_weight_confidence,
            "connection": config.promotion_weight_connection,
        }

    def calculate_promotion_score(
        self,
        created_at: datetime,
        access_count: int,
        confidence: float,
        relationship_count: int,
        now: datetime | None = None,
    ) -> float:
        """
        Calculate promotion score for a memory in SHORT_TERM.

        Args:
            created_at: When memory was created
            access_count: Number of times accessed
            confidence: Extraction confidence score (0.0-1.0)
            relationship_count: Number of graph relationships
            now: Current time

        Returns:
            Promotion score (0.0-1.0)
        """
        now = now or datetime.now()
        hours_in_short_term = (now - created_at).total_seconds() / 3600

        factors = {
            "age": min(1.0, hours_in_short_term / 72),  # Max at 3 days
            "access": min(1.0, access_count / 5),     # Max at 5 accesses
            "confidence": confidence,
            "connection": min(1.0, relationship_count / 3),  # Max at 3 connections
        }

        return sum(factors[k] * self._weights[k] for k in factors)

    def is_eligible_for_promotion(
        self,
        stage: MemoryStage,
        created_at: datetime,
        now: datetime | None = None,
    ) -> bool:
        """Check if memory is eligible for promotion consideration."""
        if stage != MemoryStage.SHORT_TERM:
            return False

        now = now or datetime.now()
        hours_in_short_term = (now - created_at).total_seconds() / 3600

        return hours_in_short_term >= self._config.short_term_min_age_hours
```

### 6. MemoryPromotionService

```python
from dataclasses import dataclass
from typing import Protocol

@dataclass
class PromotionResult:
    """Result of a promotion/decay cycle."""
    promoted_to_long_term: int = 0
    decayed_from_long_term: int = 0
    reactivated: int = 0
    deleted: int = 0
    errors: list[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class MemoryPromotionService:
    """
    Manages memory lifecycle transitions.

    Responsibilities:
    - Promote SHORT_TERM → LONG_TERM based on promotion score
    - Decay LONG_TERM → DECAYED based on decay score
    - Reactivate DECAYED → LONG_TERM on access
    - Clean up old DECAYED memories
    """

    def __init__(
        self,
        config: DecayConfig,
        graph_store: GraphStoreAdapter,
        vector_store: VectorStoreAdapter,
    ):
        self._config = config
        self._graph_store = graph_store
        self._vector_store = vector_store
        self._decay_calculator = DecayCalculator(config)
        self._promotion_scorer = PromotionScorer(config)

    async def run_promotion_cycle(self, dry_run: bool = True) -> PromotionResult:
        """
        Run a full promotion/decay cycle.

        Steps:
        1. Apply decay to all LONG_TERM memories
        2. Check LONG_TERM memories for decay threshold
        3. Check SHORT_TERM memories for promotion eligibility
        4. Clean up expired DECAYED memories
        """
        result = PromotionResult()
        now = datetime.now()

        # Step 1 & 2: Decay and demote LONG_TERM memories
        long_term_memories = await self._get_memories_by_stage(MemoryStage.LONG_TERM)
        for memory in long_term_memories:
            new_score = self._decay_calculator.calculate_decay(
                memory.decay_score,
                memory.last_decay_at or memory.created_at,
                now,
            )

            if self._decay_calculator.should_decay_to_stage(new_score):
                if not dry_run:
                    await self._transition_stage(
                        memory.id,
                        MemoryStage.DECAYED,
                        decay_score=new_score,
                    )
                result.decayed_from_long_term += 1
            elif not dry_run:
                await self._update_decay_score(memory.id, new_score, now)

        # Step 3: Promote eligible SHORT_TERM memories
        short_term_memories = await self._get_memories_by_stage(MemoryStage.SHORT_TERM)
        for memory in short_term_memories:
            if not self._promotion_scorer.is_eligible_for_promotion(
                memory.stage, memory.created_at, now
            ):
                continue

            score = self._promotion_scorer.calculate_promotion_score(
                created_at=memory.created_at,
                access_count=memory.access_count,
                confidence=memory.confidence or 0.5,
                relationship_count=await self._count_relationships(memory.id),
                now=now,
            )

            if score >= self._config.promotion_threshold:
                if not dry_run:
                    await self._transition_stage(
                        memory.id,
                        MemoryStage.LONG_TERM,
                        promoted_at=now,
                    )
                result.promoted_to_long_term += 1

        # Step 4: Clean up expired DECAYED memories
        if not dry_run:
            result.deleted = await self._cleanup_expired_decayed(now)

        return result

    async def on_memory_accessed(self, memory_id: str) -> None:
        """
        Handle memory access event.

        Boosts decay score and potentially reactivates DECAYED memories.
        """
        memory = await self._get_memory(memory_id)
        if memory is None:
            return

        new_score = self._decay_calculator.apply_access_boost(memory.decay_score)

        # Reactivate if DECAYED
        if memory.stage == MemoryStage.DECAYED:
            await self._transition_stage(
                memory_id,
                MemoryStage.LONG_TERM,
                decay_score=new_score,
            )
        else:
            await self._update_access(memory_id, new_score)
```

---

## Data Model Changes

### GraphNode Extensions

```python
# In packages/friday-memory/src/friday_memory/models/graph.py

class GraphNode(BaseModel):
    """Enhanced graph node with lifecycle metadata."""
    id: str
    node_type: NodeType
    name: str
    description: str | None = None

    # Existing Hebbian learning field
    hit_count: int = 0

    # NEW: Lifecycle fields
    stage: MemoryStage = Field(default=MemoryStage.SHORT_TERM)
    decay_score: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed_at: datetime = Field(default_factory=datetime.now)
    last_decay_at: datetime | None = Field(default=None)
    promoted_at: datetime | None = Field(default=None)

    # NEW: Graph-Vector linkage for coordinated decay
    source_memory_ids: list[str] = Field(
        default_factory=list,
        description="IDs of vector memories that contributed to this node"
    )

    # Existing fields
    properties: dict[str, Any] = Field(default_factory=dict)
    embedding: list[float] | None = None
```

### Vector Store Metadata

```python
# Metadata schema for vector store documents
VECTOR_METADATA_SCHEMA = {
    # Existing fields
    "consolidated": bool,
    "source_type": str,
    "confidence": float,

    # NEW: Lifecycle fields
    "stage": str,  # MemoryStage value
    "decay_score": float,
    "created_at": str,  # ISO format
    "last_accessed_at": str,
    "last_decay_at": str | None,
    "promoted_at": str | None,
    "access_count": int,
}
```

---

## Storage Architecture Decision

### Separate Collections for Short-Term and Long-Term (Recommended)

Use **separate ChromaDB collections** for short-term and long-term memories:

| Collection | Purpose | Retrieval Strategy |
|------------|---------|-------------------|
| `memories_short_term` | Recent consolidated insights | Lower similarity threshold (0.5), always queried |
| `memories_long_term` | Proven, frequently-accessed | Higher similarity threshold (0.7), relevancy-scored |
| `memories_decayed` | Low-value, pending cleanup | Not queried by default |

**Rationale:**
- Long-term memories require **higher relevancy** to justify inclusion (older = must be more relevant)
- Separate collections allow **different retrieval thresholds** per stage
- No risk of missing relevant long-term memories due to short-term results crowding top-N
- **Parallel queries** to both collections add minimal latency (embedding dominates)
- Clean "graduation" semantics on promotion

```python
# Parallel queries with different thresholds
short_term_results, longterm_results = await asyncio.gather(
    short_term_collection.query(embedding, n_results=5, min_similarity=0.5),
    longterm_collection.query(embedding, n_results=5, min_similarity=0.7),
)

# Merge by inclusion score
all_results = merge_and_score(short_term_results, longterm_results)
```

### Promotion Mechanics

Promotion from short-term to long-term is an atomic delete+insert operation:

```python
from enum import Enum

class PromotionState(str, Enum):
    """Tracks promotion progress for crash recovery."""
    NONE = "none"
    PENDING = "pending"      # Added to long-term, not yet deleted from short-term
    COMPLETE = "complete"

async def promote_memory(self, memory_id: str) -> None:
    """Promote memory from short-term to long-term with crash recovery support."""
    # Read from short-term
    memory = await self._short_term_collection.get(memory_id)

    # Mark promotion as pending (for crash recovery)
    memory.metadata["promotion_state"] = PromotionState.PENDING.value
    memory.metadata["stage"] = MemoryStage.LONG_TERM.value
    memory.metadata["promoted_at"] = datetime.now().isoformat()
    memory.metadata["hit_count"] = 0  # Reset for long-term tracking

    # Insert into long-term
    await self._longterm_collection.add(
        ids=[memory_id],
        embeddings=[memory.embedding],
        documents=[memory.document],
        metadatas=[memory.metadata],
    )

    # Delete from short-term
    await self._short_term_collection.delete(ids=[memory_id])

    # Mark promotion complete (only in long-term copy)
    await self._longterm_collection.update_metadata(memory_id, {
        "promotion_state": PromotionState.COMPLETE.value,
    })
```

### Promotion Atomicity Note

> **Important**: Promotion is implemented as add-then-delete, which is NOT atomic. If the process crashes between the `add` and `delete` operations, a memory may exist in both collections temporarily.
>
> **Mitigations**:
> 1. The `promotion_state` metadata flag tracks progress - PENDING means the short-term copy should be deleted
> 2. The `/migrate` command is idempotent and will deduplicate on next run
> 3. The reorganization `--analyze` step detects cross-collection duplicates
> 4. On startup, scan for `promotion_state=PENDING` and complete the promotion
>
> **Accepted Risk**: Temporary duplicates are harmless (same content, same ID). The next reorganization cycle or startup recovery will clean them up.

```python
async def recover_incomplete_promotions(self) -> int:
    """Complete any promotions that were interrupted by crash."""
    # Find memories with pending promotion state in long-term
    pending = await self._longterm_collection.query_metadata({
        "promotion_state": PromotionState.PENDING.value
    })

    recovered = 0
    for memory in pending:
        # Delete from short-term (completing the promotion)
        await self._short_term_collection.delete(ids=[memory.id])

        # Mark promotion complete
        await self._longterm_collection.update_metadata(memory.id, {
            "promotion_state": PromotionState.COMPLETE.value,
        })
        recovered += 1

    return recovered
```

### Graph Store

The graph store remains a **single NetworkX store** with stage metadata on nodes. Graph entities don't have the same collection-based retrieval pattern, and relevancy filtering is handled differently (see Graph Path Relevancy below).

### Graph-Vector Decay Linkage

Graph nodes track which vector memories contributed to their creation via provenance linkage. This enables coordinated decay between stores.

```python
# Enhanced GraphNode with source memory tracking
class GraphNode(BaseModel):
    # ... existing fields ...

    # NEW: Track which vector memories contributed to this node
    source_memory_ids: list[str] = Field(
        default_factory=list,
        description="IDs of vector memories that contributed to this node's creation"
    )
```

**Decay Rules**:
1. When a vector memory transitions to DECAYED, check all graph nodes that reference it
2. If **ALL** source memories for a node are DECAYED, mark the node as DECAYED too
3. If **ANY** source memory is still active, keep the node active
4. Orphaned nodes (no source_memory_ids) are not automatically decayed

```python
async def propagate_decay_to_graph(
    self,
    decayed_memory_ids: set[str],
) -> int:
    """
    Mark graph nodes as decayed if all their source memories have decayed.

    Called during the decay cycle after vector memories are demoted.
    """
    nodes_decayed = 0

    for node in self._graph_store.get_all_nodes():
        # Skip nodes without source linkage (legacy or manually created)
        if not node.source_memory_ids:
            continue

        # Skip nodes already decayed
        if node.stage == MemoryStage.DECAYED:
            continue

        # Check if ALL source memories have decayed
        all_sources_decayed = all(
            mid in decayed_memory_ids
            for mid in node.source_memory_ids
        )

        if all_sources_decayed:
            node.stage = MemoryStage.DECAYED
            node.last_decay_at = datetime.now()
            await self._graph_store.update_node(node)
            nodes_decayed += 1

    return nodes_decayed


async def reactivate_graph_node_on_vector_access(
    self,
    memory_id: str,
) -> int:
    """
    Reactivate graph nodes when their source memory is accessed.

    If a DECAYED vector memory is reactivated, its linked graph nodes
    should also be reactivated.
    """
    nodes_reactivated = 0

    # Find all nodes that list this memory as a source
    for node in self._graph_store.get_all_nodes():
        if memory_id in node.source_memory_ids and node.stage == MemoryStage.DECAYED:
            node.stage = MemoryStage.LONG_TERM
            node.last_accessed_at = datetime.now()
            node.decay_score = 0.5  # Reset to neutral
            await self._graph_store.update_node(node)
            nodes_reactivated += 1

    return nodes_reactivated
```

**Linking at Consolidation Time**:

```python
# In consolidator.py - when creating graph nodes from extracted entities
async def _store_entity(
    self,
    entity: ExtractedEntity,
    source_memory_id: str,  # ID of the vector memory being consolidated
) -> str:
    """Store entity and link to source memory."""
    existing_node = await self._graph_store.find_by_label(entity.name)

    if existing_node:
        # Add source to existing node
        if source_memory_id not in existing_node.source_memory_ids:
            existing_node.source_memory_ids.append(source_memory_id)
            await self._graph_store.update_node(existing_node)
        return existing_node.id
    else:
        # Create new node with source linkage
        node = GraphNode(
            id=str(uuid4()),
            type=entity.entity_type,
            label=entity.name,
            source_memory_ids=[source_memory_id],
            stage=MemoryStage.SHORT_TERM,
            # ... other fields
        )
        await self._graph_store.add_node(node)
        return node.id
```

---

## Relevancy-Aware Retrieval

### The Core Principle

**Relevancy trumps longevity.** A long-term memory is only valuable if it's semantically relevant to the current query. Old memories require higher similarity scores to justify inclusion.

### Long-Term Memory Inclusion Scoring

Long-term memories use a multi-factor inclusion score:

```python
import math
from datetime import datetime

class LongTermInclusionScorer:
    """
    Calculate whether a long-term memory should be included in context.

    Inclusion = f(similarity, age, usage)

    - similarity: Semantic relevancy to current query (0.0-1.0)
    - age: Older memories need higher similarity to qualify
    - usage: Frequently-used memories get a boost (hit_count)
    """

    def __init__(
        self,
        decay_rate: float = 0.005,  # Per-hour decay
        usage_boost_factor: float = 0.1,
        inclusion_threshold: float = 0.6,
    ):
        self.decay_rate = decay_rate
        self.usage_boost_factor = usage_boost_factor
        self.inclusion_threshold = inclusion_threshold

    def calculate_inclusion_score(
        self,
        similarity: float,
        created_at: datetime,
        hit_count: int,
        now: datetime | None = None,
    ) -> float:
        """
        Calculate inclusion score for a long-term memory.

        Returns:
            Score between 0.0 and ~1.5 (with usage boost)
        """
        now = now or datetime.now()
        age_hours = (now - created_at).total_seconds() / 3600

        # Time decay: exponential decrease
        # At 24h: ~0.89, at 72h: ~0.70, at 168h (1 week): ~0.43
        time_factor = math.exp(-self.decay_rate * age_hours)

        # Usage boost: logarithmic (diminishing returns)
        # hit_count=1: 1.0, hit_count=5: 1.16, hit_count=20: 1.30
        usage_factor = 1.0 + (self.usage_boost_factor * math.log(1 + hit_count))

        # Combined score
        return similarity * time_factor * usage_factor

    def should_include(
        self,
        similarity: float,
        created_at: datetime,
        hit_count: int,
    ) -> bool:
        """Check if memory meets inclusion threshold."""
        score = self.calculate_inclusion_score(similarity, created_at, hit_count)
        return score >= self.inclusion_threshold


# Examples:
scorer = LongTermInclusionScorer()

# 3-day old memory, similarity 0.8, hit_count 5
# time_factor = exp(-0.005 * 72) ≈ 0.70
# usage_factor = 1 + 0.1 * log(6) ≈ 1.18
# score = 0.8 * 0.70 * 1.18 ≈ 0.66 → INCLUDED (above 0.6)

# Same memory with similarity 0.6
# score = 0.6 * 0.70 * 1.18 ≈ 0.50 → EXCLUDED

# 1-week old memory, similarity 0.9, hit_count 15
# time_factor = exp(-0.005 * 168) ≈ 0.43
# usage_factor = 1 + 0.1 * log(16) ≈ 1.28
# score = 0.9 * 0.43 * 1.28 ≈ 0.50 → EXCLUDED (old, needs higher similarity)

# Same memory with hit_count 50
# usage_factor = 1 + 0.1 * log(51) ≈ 1.39
# score = 0.9 * 0.43 * 1.39 ≈ 0.54 → still EXCLUDED (age penalty too strong)
```

### Vector Store Metadata: Adding hit_count

Long-term memories track `hit_count` to measure ongoing value:

```python
LONGTERM_VECTOR_METADATA = {
    "stage": str,           # "long_term"
    "created_at": str,      # ISO timestamp
    "promoted_at": str,     # When promoted from short-term
    "hit_count": int,       # Times included in context (NEW)
    "last_accessed_at": str,
    "decay_score": float,
    "confidence": float,
    "source_type": str,
}
```

### Short-Term vs Long-Term Retrieval Comparison

| Aspect | Short-Term | Long-Term |
|--------|---------|-----------|
| Collection | `memories_short_term` | `memories_long_term` |
| Min similarity | 0.5 | 0.7 |
| Inclusion scoring | Similarity only | Similarity × Time decay × Usage boost |
| Threshold | 0.5 | 0.6 (after scoring) |
| hit_count tracked | No (use access_count) | Yes |
| Typical age | Hours to days | Days to weeks |

---

## Graph Path Relevancy Scoring

### The Problem

The graph store currently dumps all connected entities into context without assessing relevancy:

```
Query: "How do I configure logging?"
→ Extract entities: ["logging"]
→ Graph traversal returns ALL neighbors:
  logging → [Python, debugging, files, stdout, JSON, levels, handlers, formatters, ...]
→ ALL go into context, regardless of relevancy to "configure"
```

This wastes context tokens on irrelevant relationships.

### Solution: Score Node-Edge-Node Paths

Only include graph paths where the relationship is relevant to the current query:

```python
class GraphPathScorer:
    """
    Score node-edge-node paths for relevancy to current query.

    Only include paths where the combined relevancy exceeds threshold.
    """

    def __init__(
        self,
        edge_weight: float = 0.4,
        target_weight: float = 0.6,
        hit_count_boost: float = 0.05,
        inclusion_threshold: float = 0.5,
    ):
        self.edge_weight = edge_weight
        self.target_weight = target_weight
        self.hit_count_boost = hit_count_boost
        self.inclusion_threshold = inclusion_threshold

    def score_path(
        self,
        source_node: GraphNode,
        edge: GraphEdge,
        target_node: GraphNode,
        query_embedding: list[float],
        embedding_fn: Callable[[str], list[float]],
    ) -> float:
        """
        Score a graph path for relevancy.

        Args:
            source_node: Starting node (matched from query)
            edge: Relationship connecting nodes
            target_node: Connected node to potentially include
            query_embedding: Embedding of current query
            embedding_fn: Function to compute embeddings

        Returns:
            Relevancy score (0.0-1.0+)
        """
        # Edge relevancy: Is this relationship type relevant?
        edge_text = f"{source_node.name} {edge.relationship} {target_node.name}"
        edge_embedding = edge.embedding or embedding_fn(edge_text)
        edge_similarity = cosine_similarity(edge_embedding, query_embedding)

        # Target relevancy: Is the connected entity relevant?
        target_embedding = target_node.embedding or embedding_fn(target_node.description)
        target_similarity = cosine_similarity(target_embedding, query_embedding)

        # Weighted combination
        relevancy = (
            edge_similarity * self.edge_weight +
            target_similarity * self.target_weight
        )

        # Usage boost from hit counts (proven paths)
        min_hits = min(source_node.hit_count, target_node.hit_count)
        usage_factor = 1.0 + (self.hit_count_boost * math.log(1 + min_hits))

        return relevancy * usage_factor

    def filter_paths(
        self,
        paths: list[tuple[GraphNode, GraphEdge, GraphNode]],
        query_embedding: list[float],
        embedding_fn: Callable[[str], list[float]],
    ) -> list[tuple[GraphNode, GraphEdge, GraphNode, float]]:
        """Filter and score paths, returning only relevant ones."""
        scored_paths = []

        for source, edge, target in paths:
            score = self.score_path(source, edge, target, query_embedding, embedding_fn)
            if score >= self.inclusion_threshold:
                scored_paths.append((source, edge, target, score))

        # Sort by score descending
        scored_paths.sort(key=lambda x: x[3], reverse=True)
        return scored_paths
```

### Pre-Computing Edge Embeddings

To avoid latency during retrieval, compute edge embeddings during consolidation:

```python
# During consolidation or graph update
async def add_relationship(
    self,
    source_id: str,
    target_id: str,
    relationship: str,
    embedding_fn: Callable[[str], Awaitable[list[float]]],
) -> None:
    """Add relationship with pre-computed embedding."""
    source = self._graph.nodes[source_id]
    target = self._graph.nodes[target_id]

    # Pre-compute edge embedding
    edge_text = f"{source['name']} {relationship} {target['name']}"
    edge_embedding = await embedding_fn(edge_text)

    self._graph.add_edge(
        source_id,
        target_id,
        relationship=relationship,
        embedding=edge_embedding,  # Store for fast retrieval
        created_at=datetime.now().isoformat(),
    )
```

### Graph Retrieval with Relevancy Filtering

```python
# In MemoryController or GraphStoreAdapter

async def get_relevant_graph_context(
    self,
    query: str,
    query_embedding: list[float],
    max_paths: int = 10,
) -> list[GraphPath]:
    """
    Get graph paths relevant to the current query.

    Unlike current approach, this filters out irrelevant connections.
    """
    # Extract entities from query
    entities = self._extract_entities(query)

    # Get all candidate paths (1-hop neighbors)
    candidate_paths = []
    for entity in entities:
        node = self._graph.get_node_by_name(entity)
        if node:
            for neighbor_id in self._graph.neighbors(node.id):
                edge = self._graph.get_edge(node.id, neighbor_id)
                neighbor = self._graph.nodes[neighbor_id]
                candidate_paths.append((node, edge, neighbor))

    # Score and filter paths
    scorer = GraphPathScorer()
    relevant_paths = scorer.filter_paths(
        candidate_paths,
        query_embedding,
        self._embedding_fn,
    )

    # Return top N most relevant
    return relevant_paths[:max_paths]
```

---

## Context Assembly Integration

### Updated MemoryController.recall()

```python
async def recall(
    self,
    query: str,
    session_id: str | None = None,
    token_limit: int = 2000,
    include_history: bool = True,
    history_limit: int = 10,
    short_term_results: int = 5,
    longterm_results: int = 5,
    graph_paths: int = 10,
) -> ContextPayload:
    """
    Orchestrates parallel retrieval from all memory stores.

    Retrieval Strategy:
    1. Episodic: Recent turns (unchanged)
    2. Short-term: Query with lower similarity threshold
    3. Long-term: Query with higher threshold + inclusion scoring
    4. Graph: Relevancy-filtered paths only
    """
    query_embedding = await self._embed(query)

    # Parallel retrieval
    episodic_task = self._get_episodic_history(session_id, history_limit)
    short_term_task = self._short_term_collection.query(
        query_embedding,
        n_results=short_term_results,
        min_similarity=0.5,
    )
    longterm_task = self._longterm_collection.query(
        query_embedding,
        n_results=longterm_results * 2,  # Over-fetch for scoring
        min_similarity=0.7,
    )
    graph_task = self.get_relevant_graph_context(
        query,
        query_embedding,
        max_paths=graph_paths,
    )

    history, short_term_memories, longterm_memories, graph_paths = await asyncio.gather(
        episodic_task,
        short_term_task,
        longterm_task,
        graph_task,
    )

    # Apply inclusion scoring to long-term memories
    scorer = LongTermInclusionScorer()
    included_longterm = [
        m for m in longterm_memories
        if scorer.should_include(
            m.similarity,
            datetime.fromisoformat(m.metadata["created_at"]),
            m.metadata.get("hit_count", 0),
        )
    ][:longterm_results]  # Limit after filtering

    # Track access for included memories
    for memory in short_term_memories + included_longterm:
        await self._track_access(memory.id)

    # Build context payload
    return ContextPayload(
        history=history,
        passages=short_term_memories + included_longterm,
        entities=[path.target for path in graph_paths],
        facts=[self._path_to_fact(path) for path in graph_paths],
    )
```

### What Gets Included in Context?

| Source | Inclusion Criteria |
|--------|-------------------|
| **Episodic** | Recent turns (unchanged) |
| **Short-Term** | similarity >= 0.5 |
| **Long-Term** | similarity >= 0.7 AND inclusion_score >= 0.6 |
| **Graph Paths** | path_relevancy >= 0.5 |
| **Decayed** | Not queried by default |

### Access Tracking

When memories are included in context, track access for decay/promotion:

```python
async def _track_access(self, memory_id: str, collection: str) -> None:
    """Track that a memory was included in context."""
    if collection == "long_term":
        # Increment hit_count for long-term memories
        await self._longterm_collection.update_metadata(
            memory_id,
            {
                "hit_count": {"$inc": 1},
                "last_accessed_at": datetime.now().isoformat(),
            }
        )
    else:
        # Boost decay_score for short-term memories
        await self._promotion_service.on_memory_accessed(memory_id)
```

This creates a virtuous cycle:
- Useful short-term memories get accessed → boosted → promoted to long-term
- Useful long-term memories get hit_count increases → survive inclusion scoring
- Unused memories decay → eventually pruned

---

## Latency Optimization

**Design Principle:** Move as much computation as possible from the latency-sensitive retrieval path to the batch-oriented reorganization phase (which runs during low usage).

### Latency Budget

| Operation | Target | Strategy |
|-----------|--------|----------|
| Query embedding | ~100ms | Unavoidable |
| Vector search (parallel) | ~40ms | Acceptable |
| Inclusion scoring | **<2ms** | Use pre-computed factors |
| Graph path filtering | **<20ms** | Pre-embedded edges + pre-filtering |
| Access tracking | **0ms** | Async buffered writes |
| **Total** | **<165ms** | Down from ~250-300ms |

---

### Optimization A: Pre-computed Retrieval Factors (Required)

Calculate time decay and usage boost during reorganization, not retrieval.

```python
# During reorganization (batch, background)
class RetrievalFactorComputer:
    """Pre-compute retrieval factors for long-term memories."""

    async def compute_factors(self, collection: Collection) -> int:
        """Update retrieval_factor for all long-term memories."""
        now = datetime.now()
        updated = 0

        for memory in collection.get_all():
            created_at = datetime.fromisoformat(memory.metadata["created_at"])
            age_hours = (now - created_at).total_seconds() / 3600
            hit_count = memory.metadata.get("hit_count", 0)

            # Pre-compute the non-similarity components
            time_factor = math.exp(-0.005 * age_hours)
            usage_factor = 1.0 + (0.1 * math.log(1 + hit_count))
            retrieval_factor = time_factor * usage_factor

            await collection.update_metadata(memory.id, {
                "retrieval_factor": retrieval_factor,
                "factor_computed_at": now.isoformat(),
            })
            updated += 1

        return updated
```

**At retrieval (fast path):**

```python
# Simple multiplication instead of exponential calculation
def calculate_inclusion_score(similarity: float, metadata: dict) -> float:
    """Fast inclusion scoring using pre-computed factor."""
    retrieval_factor = metadata.get("retrieval_factor", 0.5)
    return similarity * retrieval_factor
```

**Savings:** ~4ms per query

---

### Optimization B: Lazy Access Tracking (Required)

Buffer access events in memory, batch-write during reorganization.

```python
import time
from pathlib import Path
import aiofiles

class AccessBuffer:
    """
    Buffer access events for batch processing.

    Eliminates synchronous DB writes during retrieval.
    Flushed during reorganization, on graceful shutdown, or after max_buffer_age_seconds.
    Optionally persists to a write-ahead log (WAL) for crash recovery.
    """

    def __init__(
        self,
        max_buffer_size: int = 1000,
        max_buffer_age_seconds: int = 300,  # 5-minute max age
        wal_path: Path | None = None,       # Optional write-ahead log for crash recovery
    ):
        self._short_term_buffer: dict[str, int] = {}  # memory_id → access_count
        self._longterm_buffer: dict[str, int] = {}
        self._max_size = max_buffer_size
        self._max_age = max_buffer_age_seconds
        self._last_flush_time = time.time()
        self._wal_path = wal_path
        self._lock = asyncio.Lock()

    async def record_access(
        self,
        memory_id: str,
        collection_type: str,  # "short_term" or "long_term"
    ) -> None:
        """
        Record access event (O(1), in-memory only).

        This is called during retrieval - must be fast.
        """
        async with self._lock:
            buffer = (
                self._short_term_buffer
                if collection_type == "short_term"
                else self._longterm_buffer
            )
            buffer[memory_id] = buffer.get(memory_id, 0) + 1

            # Optional: persist to WAL for crash recovery
            if self._wal_path:
                await self._persist_to_wal(memory_id, collection_type)

            # Auto-flush if buffer gets too large
            if len(buffer) > self._max_size:
                await self._flush_buffer(collection_type)

            # Time-based flush check
            if time.time() - self._last_flush_time > self._max_age:
                await self._flush_buffer(collection_type)
                self._last_flush_time = time.time()

    async def _persist_to_wal(self, memory_id: str, collection_type: str) -> None:
        """Optional: Append to WAL for crash recovery."""
        if self._wal_path:
            async with aiofiles.open(self._wal_path, 'a') as f:
                await f.write(f"{memory_id},{collection_type},{time.time()}\n")

    async def recover_from_wal(self) -> int:
        """Replay WAL entries on startup (if WAL exists)."""
        if not self._wal_path or not self._wal_path.exists():
            return 0

        recovered = 0
        async with aiofiles.open(self._wal_path, 'r') as f:
            async for line in f:
                try:
                    memory_id, collection_type, _ = line.strip().split(',')
                    buffer = (
                        self._short_term_buffer
                        if collection_type == "short_term"
                        else self._longterm_buffer
                    )
                    buffer[memory_id] = buffer.get(memory_id, 0) + 1
                    recovered += 1
                except ValueError:
                    continue  # Skip malformed lines

        # Clear WAL after recovery
        if recovered > 0:
            self._wal_path.unlink(missing_ok=True)

        return recovered

    async def flush_all(
        self,
        short_term_collection: Collection,
        longterm_collection: Collection,
    ) -> dict[str, int]:
        """
        Batch-write all buffered accesses.

        Called during reorganization.
        """
        async with self._lock:
            short_term_copy = self._short_term_buffer.copy()
            longterm_copy = self._longterm_buffer.copy()
            self._short_term_buffer.clear()
            self._longterm_buffer.clear()
            self._last_flush_time = time.time()

        # Batch update short-term (boost decay_score)
        for memory_id, count in short_term_copy.items():
            current = await short_term_collection.get(memory_id)
            new_score = min(1.0, current.metadata["decay_score"] + (0.1 * count))
            await short_term_collection.update_metadata(memory_id, {
                "decay_score": new_score,
                "last_accessed_at": datetime.now().isoformat(),
            })

        # Batch update long-term (increment hit_count)
        for memory_id, count in longterm_copy.items():
            await longterm_collection.update_metadata(memory_id, {
                "hit_count": {"$inc": count},
                "last_accessed_at": datetime.now().isoformat(),
            })

        # Clear WAL after successful flush
        if self._wal_path:
            self._wal_path.unlink(missing_ok=True)

        return {
            "short_term_flushed": len(short_term_copy),
            "longterm_flushed": len(longterm_copy),
        }
```

**At retrieval:**

```python
# Fire-and-forget, no await needed
asyncio.create_task(self._access_buffer.record_access(memory.id, "long_term"))
```

**At startup (optional crash recovery):**

```python
# Recover any access events that weren't flushed before crash
recovered = await self._access_buffer.recover_from_wal()
if recovered > 0:
    logger.info(f"Recovered {recovered} access events from WAL")
```

**Savings:** ~10ms per query (eliminates synchronous DB writes)

---

### Optimization C: Mandatory Edge Pre-embedding (Required)

Never compute edge embeddings at retrieval time. All edges must be embedded during consolidation or reorganization.

```python
# During consolidation (when edge is created)
async def add_relationship(
    self,
    source_id: str,
    target_id: str,
    relationship: str,
) -> None:
    """Add relationship with mandatory embedding."""
    source = self._graph.nodes[source_id]
    target = self._graph.nodes[target_id]

    # ALWAYS compute embedding at creation time
    edge_text = f"{source['name']} {relationship} {target['name']}"
    edge_embedding = await self._embedding_fn(edge_text)

    self._graph.add_edge(
        source_id,
        target_id,
        relationship=relationship,
        embedding=edge_embedding,  # Never None
        created_at=datetime.now().isoformat(),
    )


# During reorganization (backfill any missing)
async def ensure_edge_embeddings(self) -> int:
    """Backfill embeddings for any edges missing them."""
    count = 0
    for edge in self._graph.get_all_edges():
        if not edge.get("embedding"):
            source = self._graph.get_node(edge["source"])
            target = self._graph.get_node(edge["target"])
            edge_text = f"{source.name} {edge['relationship']} {target.name}"
            edge["embedding"] = await self._embedding_fn(edge_text)
            count += 1
    return count
```

**At retrieval:**

```python
def score_path(self, source, edge, target, query_embedding) -> float:
    # Edge embedding is ALWAYS available - no fallback computation
    edge_similarity = cosine_similarity(edge["embedding"], query_embedding)
    # ...
```

**Savings:** ~100ms+ per query (eliminates fallback embedding generation)

---

### Optimization D: Relevancy Tier Pre-classification (Future Enhancement)

Pre-classify long-term memories into "hot", "warm", "cold" tiers based on recent query patterns.

```python
# During reorganization
class RelevancyTierBuilder:
    """Pre-classify memories based on recent query topic relevancy."""

    async def build_tiers(
        self,
        collection: Collection,
        recent_queries: list[str],
        hot_threshold: float = 0.7,
        warm_threshold: float = 0.4,
    ) -> dict[str, int]:
        """
        Classify memories into retrieval tiers.

        Tiers:
        - hot: High relevancy to recent topics, query first
        - warm: Moderate relevancy, query if hot insufficient
        - cold: Low relevancy, skip unless explicitly needed
        """
        # Compute topic centroid from recent queries
        query_embeddings = [await self._embed(q) for q in recent_queries[-50:]]
        topic_centroid = np.mean(query_embeddings, axis=0)

        tier_counts = {"hot": 0, "warm": 0, "cold": 0}

        for memory in collection.get_all():
            similarity = cosine_similarity(memory.embedding, topic_centroid)

            if similarity > hot_threshold:
                tier = "hot"
            elif similarity > warm_threshold:
                tier = "warm"
            else:
                tier = "cold"

            await collection.update_metadata(memory.id, {
                "relevancy_tier": tier,
                "tier_computed_at": datetime.now().isoformat(),
            })
            tier_counts[tier] += 1

        return tier_counts
```

**At retrieval (future):**

```python
# Query hot tier first (smaller, faster)
results = await longterm_collection.query(
    embedding,
    where={"relevancy_tier": "hot"},
    n_results=5,
)

# Expand to warm only if needed
if len([r for r in results if r.similarity > 0.7]) < 2:
    warm_results = await longterm_collection.query(
        embedding,
        where={"relevancy_tier": "warm"},
        n_results=5,
    )
    results.extend(warm_results)
```

**Potential savings:** ~15-20ms (smaller search space)

---

### Optimization E: Graph Path Pre-scoring (Future Enhancement)

Pre-compute path relevancy scores against recent query patterns.

```python
# During reorganization
async def precompute_path_scores(
    self,
    recent_queries: list[str],
) -> int:
    """
    Score graph paths against recent query topics.

    Stores avg_relevancy and max_relevancy on each edge
    for fast pre-filtering at retrieval time.
    """
    query_embeddings = [await self._embed(q) for q in recent_queries[-100:]]
    updated = 0

    for source in self._graph.get_all_nodes():
        for neighbor_id in self._graph.neighbors(source.id):
            edge = self._graph.get_edge(source.id, neighbor_id)
            target = self._graph.get_node(neighbor_id)

            # Score against all recent queries
            scores = []
            for q_emb in query_embeddings:
                score = self._score_path_fast(source, edge, target, q_emb)
                scores.append(score)

            # Store aggregated scores
            edge["avg_relevancy"] = float(np.mean(scores))
            edge["max_relevancy"] = float(np.max(scores))
            edge["relevancy_computed_at"] = datetime.now().isoformat()
            updated += 1

    return updated
```

**At retrieval (future):**

```python
# Fast pre-filter using pre-computed scores
candidate_paths = [
    (s, e, t) for s, e, t in all_paths
    if e.get("avg_relevancy", 0) > 0.3
]

# Only fully score the filtered candidates
scored_paths = self._scorer.filter_paths(candidate_paths, query_embedding)
```

**Potential savings:** ~25-35ms (fewer paths to score)

---

### Reorganization Integration

Add latency optimization steps to the reorganization pipeline:

```python
async def reorganize(self, ...) -> ReorganizationReport:
    # ... existing steps ...

    # Step 7: Latency optimizations (NEW)
    logger.info("Step 7: Computing retrieval optimizations...")

    # 7a. Flush access buffer
    access_stats = await self._access_buffer.flush_all(
        self._short_term_collection,
        self._longterm_collection,
    )
    report.access_events_flushed = sum(access_stats.values())

    # 7b. Compute retrieval factors for long-term
    factors_updated = await self._factor_computer.compute_factors(
        self._longterm_collection
    )
    report.retrieval_factors_updated = factors_updated

    # 7c. Ensure all edges have embeddings
    edges_embedded = await self._graph_store.ensure_edge_embeddings()
    report.edges_embedded = edges_embedded

    # 7d. (Future) Build relevancy tiers
    # tier_counts = await self._tier_builder.build_tiers(...)

    # 7e. (Future) Pre-score graph paths
    # paths_scored = await self._path_scorer.precompute_path_scores(...)
```

---

### Latency Comparison

| Operation | Before | After | Savings |
|-----------|--------|-------|---------|
| Query embedding | 100ms | 100ms | - |
| Vector search (parallel) | 40ms | 40ms | - |
| Inclusion scoring | 5ms | **1ms** | 4ms |
| Graph path scoring | 50ms | **20ms** | 30ms |
| Access tracking | 10ms | **0ms** | 10ms |
| Edge embedding fallback | 100ms+ | **0ms** | 100ms+ |
| **Total** | **~250-300ms** | **~160ms** | **35-45%** |

---

## Observability

### Lifecycle Metrics

Track these metrics during reorganization to monitor memory health:

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `memory.lifecycle.short_term_count` | Total short-term memories | >10,000 |
| `memory.lifecycle.long_term_count` | Total long-term memories | >50,000 |
| `memory.lifecycle.decayed_count` | Total decayed memories | >5,000 |
| `memory.lifecycle.promotion_rate` | Promotions per cycle | <5% of eligible |
| `memory.lifecycle.decay_rate` | Decays per cycle | >50% of long-term |
| `memory.lifecycle.avg_time_to_promotion` | Hours in short-term before promotion | >168 (1 week) |
| `memory.lifecycle.reactivation_count` | Decayed memories reactivated | - |
| `memory.lifecycle.graph_nodes_decayed` | Graph nodes decayed via linkage | - |

### LifecycleMetrics Model

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class LifecycleMetrics:
    """Metrics emitted after each lifecycle cycle."""
    timestamp: datetime = field(default_factory=datetime.now)

    # Collection counts
    short_term_count: int = 0
    long_term_count: int = 0
    decayed_count: int = 0

    # Cycle activity
    promotions_this_cycle: int = 0
    demotions_this_cycle: int = 0
    reactivations_this_cycle: int = 0
    graph_nodes_decayed: int = 0
    graph_nodes_reactivated: int = 0

    # Health indicators
    avg_decay_score_short_term: float = 0.0
    avg_decay_score_long_term: float = 0.0
    avg_hit_count_long_term: float = 0.0
    avg_time_in_short_term_hours: float = 0.0

    # Access buffer stats
    access_events_flushed: int = 0
    wal_events_recovered: int = 0


async def emit_lifecycle_metrics(
    self,
    short_term_collection: Collection,
    longterm_collection: Collection,
    decayed_collection: Collection,
    cycle_result: PromotionResult,
) -> LifecycleMetrics:
    """
    Collect and emit lifecycle metrics after reorganization.

    Integrates with existing telemetry infrastructure.
    """
    now = datetime.now()

    # Count documents in each collection
    short_term_docs = await short_term_collection.get_all()
    longterm_docs = await longterm_collection.get_all()
    decayed_docs = await decayed_collection.get_all()

    # Calculate averages
    avg_decay_st = (
        sum(d.metadata.get("decay_score", 0) for d in short_term_docs) / len(short_term_docs)
        if short_term_docs else 0.0
    )
    avg_decay_lt = (
        sum(d.metadata.get("decay_score", 0) for d in longterm_docs) / len(longterm_docs)
        if longterm_docs else 0.0
    )
    avg_hits = (
        sum(d.metadata.get("hit_count", 0) for d in longterm_docs) / len(longterm_docs)
        if longterm_docs else 0.0
    )
    avg_time_st = (
        sum(
            (now - datetime.fromisoformat(d.metadata.get("created_at", now.isoformat()))).total_seconds() / 3600
            for d in short_term_docs
        ) / len(short_term_docs)
        if short_term_docs else 0.0
    )

    metrics = LifecycleMetrics(
        timestamp=now,
        short_term_count=len(short_term_docs),
        long_term_count=len(longterm_docs),
        decayed_count=len(decayed_docs),
        promotions_this_cycle=cycle_result.promoted_to_long_term,
        demotions_this_cycle=cycle_result.decayed_from_long_term,
        reactivations_this_cycle=cycle_result.reactivated,
        avg_decay_score_short_term=avg_decay_st,
        avg_decay_score_long_term=avg_decay_lt,
        avg_hit_count_long_term=avg_hits,
        avg_time_in_short_term_hours=avg_time_st,
    )

    # Emit via telemetry (uses existing infrastructure)
    self._telemetry.emit("memory.lifecycle.metrics", metrics.__dict__)

    return metrics
```

### /status Command Enhancement

Update `/status` in memory-chat.py to show lifecycle breakdown:

```python
async def cmd_status(self, args: str) -> str:
    """Show memory status including lifecycle breakdown."""
    lines = ["Memory Status", "=" * 50, ""]

    # Get collection counts
    short_term = await self._short_term_collection.count()
    long_term = await self._longterm_collection.count()
    decayed = await self._decayed_collection.count()

    # Calculate averages (sample for performance)
    st_sample = await self._short_term_collection.get_sample(limit=100)
    lt_sample = await self._longterm_collection.get_sample(limit=100)

    avg_decay_st = sum(d.metadata.get("decay_score", 0) for d in st_sample) / len(st_sample) if st_sample else 0
    avg_hits_lt = sum(d.metadata.get("hit_count", 0) for d in lt_sample) / len(lt_sample) if lt_sample else 0

    lines.append(f"Short-Term: {short_term:,} memories (avg decay: {avg_decay_st:.2f})")
    lines.append(f"Long-Term:  {long_term:,} memories (avg hits: {avg_hits_lt:.1f})")
    lines.append(f"Decayed:    {decayed:,} memories (pending cleanup)")

    # Last cycle info (if available)
    if self._last_lifecycle_report:
        report = self._last_lifecycle_report
        age = (datetime.now() - report.timestamp).total_seconds() / 3600
        lines.append("")
        lines.append(f"Last Cycle ({age:.0f}h ago):")
        lines.append(f"  Promoted: {report.promoted_to_long_term} | "
                    f"Decayed: {report.decayed_from_long_term} | "
                    f"Reactivated: {report.reactivated}")

    # Graph stats
    graph_nodes = self._graph_store.count_nodes()
    graph_decayed = self._graph_store.count_nodes_by_stage(MemoryStage.DECAYED)
    lines.append("")
    lines.append(f"Graph Nodes: {graph_nodes:,} total ({graph_decayed} decayed)")

    return "\n".join(lines)
```

**Example Output:**
```
Memory Status
==================================================

Short-Term: 156 memories (avg decay: 0.82)
Long-Term:  1,203 memories (avg hits: 4.2)
Decayed:    89 memories (pending cleanup)

Last Cycle (2h ago):
  Promoted: 12 | Decayed: 3 | Reactivated: 1

Graph Nodes: 342 total (15 decayed)
```

---

## Integration Points

### 1. Consolidator Updates

```python
# In packages/friday-memory/src/friday_memory/context/consolidator.py

async def _store_insight(self, insight: ExtractedInsight) -> None:
    """Store insight with SHORT_TERM lifecycle stage."""
    metadata = {
        "consolidated": True,
        "source_type": "consolidation",
        "confidence": insight.confidence,
        # NEW: Lifecycle initialization
        "stage": MemoryStage.SHORT_TERM.value,
        "decay_score": 1.0,
        "created_at": datetime.now().isoformat(),
        "last_accessed_at": datetime.now().isoformat(),
        "access_count": 0,
    }

    await self._vector_store.add(
        document=insight.text,
        metadata=metadata,
        embedding=insight.embedding,
    )
```

### 2. MemoryController Access Tracking

```python
# In packages/friday-memory/src/friday_memory/controller/memory_controller.py

async def query(self, query: str, ...) -> MemoryQueryResult:
    """Query memories and track access."""
    results = await self._vector_store.query(query, ...)

    # NEW: Boost decay scores for accessed memories
    for result in results.memories:
        await self._promotion_service.on_memory_accessed(result.id)

    return results
```

### 3. Reorganizer Pipeline

```python
# In packages/friday-memory/src/friday_memory/maintenance/reorganizer.py

async def reorganize(...) -> ReorganizationReport:
    """Full reorganization with lifecycle management."""
    # Existing steps...

    # NEW: Step 6 - Run promotion/decay cycle
    if not skip_lifecycle:
        logger.info("Step 6/6: Running lifecycle promotion/decay...")
        report.lifecycle_report = await self._promotion_service.run_promotion_cycle(
            dry_run=dry_run
        )
```

---

## Files to Create

| File | Purpose |
|------|---------|
| `packages/friday-memory/src/friday_memory/lifecycle/__init__.py` | Module exports |
| `packages/friday-memory/src/friday_memory/lifecycle/stages.py` | `MemoryStage` enum (including DELETED), `MemoryLifecycleMetadata`, `PromotionState` |
| `packages/friday-memory/src/friday_memory/lifecycle/decay.py` | `DecayConfig` (with configurable weights), `DecayCalculator` |
| `packages/friday-memory/src/friday_memory/lifecycle/promotion.py` | `PromotionScorer` (using config weights), `MemoryPromotionService` |
| `packages/friday-memory/src/friday_memory/lifecycle/migration.py` | Migration utilities for existing memories |
| `packages/friday-memory/src/friday_memory/lifecycle/scoring.py` | `LongTermInclusionScorer` for relevancy-aware retrieval |
| `packages/friday-memory/src/friday_memory/lifecycle/linkage.py` | Graph-vector decay linkage (`propagate_decay_to_graph`, `reactivate_graph_node_on_vector_access`) |
| `packages/friday-memory/src/friday_memory/lifecycle/metrics.py` | `LifecycleMetrics` dataclass, `emit_lifecycle_metrics()` |
| `packages/friday-memory/src/friday_memory/retrieval/__init__.py` | Retrieval module exports |
| `packages/friday-memory/src/friday_memory/retrieval/graph_scorer.py` | `GraphPathScorer` for graph relevancy filtering |
| `packages/friday-memory/src/friday_memory/retrieval/collection_manager.py` | Multi-collection management (short-term, long-term, decayed) |
| `packages/friday-memory/src/friday_memory/retrieval/access_buffer.py` | `AccessBuffer` with time-based flush and optional WAL |
| `packages/friday-memory/src/friday_memory/retrieval/factor_computer.py` | `RetrievalFactorComputer` for pre-computed scores |
| `packages/friday-memory/src/friday_memory/retrieval/tier_builder.py` | `RelevancyTierBuilder` for hot/warm/cold classification (Future) |

## Files to Modify

| File | Changes |
|------|---------|
| `packages/friday-memory/src/friday_memory/models/graph.py` | Add lifecycle fields, `source_memory_ids`, edge embedding to `GraphNode`/`GraphEdge` |
| `packages/friday-memory/src/friday_memory/maintenance/models.py` | Add `DecayConfig` (with weights, buffer config), relevancy thresholds to `MaintenanceConfig` |
| `packages/friday-memory/src/friday_memory/context/consolidator.py` | Write to `memories_short_term` collection, set initial stage, link graph nodes to source memories |
| `packages/friday-memory/src/friday_memory/context/assembler.py` | Integrate relevancy-aware retrieval in budget priority |
| `packages/friday-memory/src/friday_memory/controller/memory_controller.py` | Parallel collection queries, inclusion scoring, access tracking, promotion state handling |
| `packages/friday-memory/src/friday_memory/maintenance/reorganizer.py` | Add lifecycle step, collection promotion, graph-vector decay propagation, metrics emission |
| `packages/friday-memory/src/friday_memory/adapters/vector_store.py` | Multi-collection support, hit_count tracking |
| `packages/friday-memory/src/friday_memory/adapters/graph_store.py` | Edge embeddings, path relevancy support, `source_memory_ids` updates |
| `tests/integration/memory/memory-chat.py` | Add `/migrate`, `/recover`, `/prune`, `/status` commands |
| `tests/integration/memory/config.yaml` | Add collection names, relevancy thresholds, access buffer config |

---

## Implementation Phases

### Phase 1: Data Model (Foundation)
1. Create `lifecycle/` module with `MemoryStage` enum
2. Create `MemoryLifecycleMetadata` model
3. Add `DecayConfig` to maintenance models
4. Extend `GraphNode` with lifecycle fields
5. Add `embedding` field to graph edges for path relevancy
6. Update vector metadata schema with `hit_count`

### Phase 2: Multi-Collection Architecture
1. Create `retrieval/collection_manager.py` for managing short-term/long-term/decayed collections
2. Update `VectorStoreAdapter` to support multiple collections
3. Configure collection names in `config.yaml`
4. Implement atomic promotion (delete from short-term, insert to long-term)

### Phase 3: Relevancy Scoring Services
1. Implement `LongTermInclusionScorer` (similarity × time_decay × usage_boost)
2. Implement `GraphPathScorer` for node-edge-node relevancy
3. Add pre-computed edge embeddings during consolidation
4. Write unit tests for scoring algorithms

### Phase 4: Lifecycle Services
1. Implement `DecayCalculator` with exponential decay
2. Implement `PromotionScorer` with weighted scoring
3. Implement `MemoryPromotionService` orchestrator
4. Write unit tests for lifecycle services

### Phase 5: Latency Optimization (Required)
1. Implement `AccessBuffer` for lazy access tracking (fire-and-forget)
2. Implement `RetrievalFactorComputer` for pre-computed `retrieval_factor`
3. Ensure mandatory edge embeddings during consolidation
4. Add backfill step to reorganization for missing edge embeddings
5. Update `MemoryController.recall()` to use pre-computed factors
6. Update reorganization to flush access buffer and recompute factors

### Phase 6: Retrieval Integration
1. Update `MemoryController.recall()` with parallel collection queries
2. Apply fast inclusion scoring using pre-computed `retrieval_factor`
3. Apply `GraphPathScorer` to filter graph paths (using pre-embedded edges)
4. Use `AccessBuffer.record_access()` (async, non-blocking)

### Phase 7: Context Assembly Updates
1. Update `ContextAssembler._apply_budget()` priority hierarchy
2. Integrate relevancy scores into budget decisions
3. Ensure DECAYED memories are excluded by default

### Phase 8: Reorganization Integration
1. Add lifecycle step to reorganization pipeline
2. Implement collection-based promotion during reorganization
3. Add latency optimization step to reorganization:
   - Flush `AccessBuffer` to batch-update hit_count/decay_score
   - Recompute `retrieval_factor` for all long-term memories
   - Backfill missing edge embeddings
4. Add `--skip-lifecycle` option to `/reorganize` command
5. Update `ReorganizationReport` with lifecycle and optimization results

### Phase 9: Migration & /migrate Command
1. Create `MemoryMigrator` class in `lifecycle/migration.py`
2. Migrate existing single collection → short-term + long-term collections
3. Add `/migrate` command to memory-chat.py with `--dry-run` and `--force`
4. Make migration idempotent (safe to run multiple times)

### Phase 10: Testing & Documentation
1. Write unit tests for scoring algorithms
2. Write unit tests for latency optimization components
3. Write integration tests for full lifecycle flow
4. Benchmark retrieval latency (target: <165ms)
5. Add lifecycle section to FRIDAY-FEATURES.md
6. Update config.yaml documentation
7. Manual testing in memory-chat.py

### Phase 11: Future Enhancements (Optional)
1. Implement `RelevancyTierBuilder` for hot/warm/cold classification (Optimization D)
2. Implement graph path pre-scoring against recent queries (Optimization E)
3. Add tier-based retrieval (query hot first, expand if needed)

---

## Configuration Example

```yaml
# config.yaml

# Vector store collections
vector:
  collections:
    short_term: "memories_short_term"
    long_term: "memories_long_term"
    decayed: "memories_decayed"

# Relevancy thresholds for retrieval
# NOTE: This uses a DIFFERENT decay rate (0.005) than lifecycle decay (0.01)
# Inclusion decay affects retrieval priority, not stage transitions
retrieval:
  short_term:
    min_similarity: 0.5       # Lower bar for recent memories
  long_term:
    min_similarity: 0.7       # Higher bar for older memories
    inclusion_threshold: 0.6  # After applying time decay + usage boost
    decay_rate: 0.005         # Per-hour decay for inclusion scoring (separate from lifecycle)
    usage_boost_factor: 0.1   # Logarithmic boost per hit_count
  graph:
    path_threshold: 0.5       # Min relevancy for node-edge-node paths
    edge_weight: 0.4          # Weight for edge relevancy
    target_weight: 0.6        # Weight for target node relevancy

maintenance:
  # Existing settings...

  # Decay configuration for lifecycle management
  # NOTE: decay_rate here (0.01) controls stage transitions, not retrieval priority
  decay:
    enabled: true
    decay_rate: 0.01          # Per-hour: 24h→79%, 72h→49%, 168h→19%
    access_boost: 0.2         # Boost on each access
    promotion_threshold: 0.7  # Min score for SHORT_TERM → LONG_TERM
    decay_threshold: 0.2      # Below this → DECAYED
    short_term_min_age_hours: 24 # Min time in short-term before promotion
    decay_check_interval_hours: 24
    decayed_retention_days: 30

    # Promotion scoring weights (must sum to 1.0)
    promotion_weight_age: 0.2
    promotion_weight_access: 0.4
    promotion_weight_confidence: 0.2
    promotion_weight_connection: 0.2

  # Access buffer configuration
  access_buffer:
    max_buffer_size: 1000     # Flush after this many events
    max_buffer_age_seconds: 300  # Flush after 5 minutes regardless of size
    wal_enabled: false        # Enable write-ahead log for crash recovery
    wal_path: "./access_buffer.wal"
```

---

## Verification Plan

### Unit Tests - Lifecycle
- [ ] `DecayCalculator.calculate_decay()` applies correct exponential decay
- [ ] `DecayCalculator.apply_access_boost()` caps at 1.0
- [ ] `PromotionScorer.calculate_promotion_score()` returns correct weighted score
- [ ] `PromotionScorer.is_eligible_for_promotion()` respects minimum age
- [ ] `MemoryStage` transitions are valid (including DELETED state)
- [ ] `DecayConfig` validates promotion weights sum to 1.0
- [ ] Configurable promotion weights are used by `PromotionScorer`

### Unit Tests - Relevancy Scoring
- [ ] `LongTermInclusionScorer.calculate_inclusion_score()` applies time decay correctly
- [ ] `LongTermInclusionScorer` usage boost is logarithmic (diminishing returns)
- [ ] `LongTermInclusionScorer.should_include()` respects threshold
- [ ] `GraphPathScorer.score_path()` weights edge vs target correctly
- [ ] `GraphPathScorer.filter_paths()` excludes low-relevancy paths
- [ ] Old memories require higher similarity to pass inclusion
- [ ] Two decay rates (0.01 lifecycle, 0.005 inclusion) are correctly applied in their respective contexts

### Unit Tests - Multi-Collection
- [ ] `CollectionManager` creates separate short-term/long-term/decayed collections
- [ ] Promotion atomically moves document between collections
- [ ] `hit_count` increments correctly on long-term memory access
- [ ] `PromotionState.PENDING` is set before promotion starts
- [ ] `recover_incomplete_promotions()` completes pending promotions

### Unit Tests - Latency Optimization
- [ ] `AccessBuffer.record_access()` completes in <1ms (O(1) dict update)
- [ ] `AccessBuffer.flush_all()` correctly batch-updates collections
- [ ] `AccessBuffer` time-based flush triggers after `max_buffer_age_seconds`
- [ ] `AccessBuffer.recover_from_wal()` replays WAL entries correctly
- [ ] WAL is cleared after successful flush
- [ ] `RetrievalFactorComputer.compute_factors()` updates all long-term memories
- [ ] Pre-computed `retrieval_factor` matches manual calculation
- [ ] Edge embeddings are always present after consolidation (never None)

### Unit Tests - Graph-Vector Linkage
- [ ] `GraphNode.source_memory_ids` is populated during consolidation
- [ ] `propagate_decay_to_graph()` decays nodes when ALL sources are decayed
- [ ] `propagate_decay_to_graph()` keeps nodes active if ANY source is active
- [ ] `reactivate_graph_node_on_vector_access()` reactivates linked graph nodes
- [ ] Orphaned graph nodes (no source_memory_ids) are not auto-decayed

### Unit Tests - Soft Delete
- [ ] DECAYED memories are not immediately deleted
- [ ] DELETED state is applied after retention period
- [ ] `/recover` moves memory from DECAYED back to LONG_TERM
- [ ] `/recover` resets decay_score to 0.5
- [ ] `/prune --force` only deletes memories past retention period

### Integration Tests - Retrieval
- [ ] Parallel queries to short-term + long-term complete without timeout
- [ ] Short-term memories with similarity >= 0.5 are included
- [ ] Long-term memories require similarity >= 0.7 AND inclusion_score >= 0.6
- [ ] Graph paths with relevancy < 0.5 are excluded from context
- [ ] Irrelevant long-term memories (old, low similarity) are filtered out
- [ ] DECAYED and DELETED memories are excluded from retrieval

### Integration Tests - Lifecycle
- [ ] Consolidation creates memories in `memories_short_term` collection
- [ ] Memory access boosts decay_score (short-term) or hit_count (long-term)
- [ ] Reorganization promotes eligible short-term → long-term
- [ ] Reorganization demotes low-score long-term → decayed
- [ ] DECAYED memories are reactivated on access
- [ ] Graph nodes are decayed when linked vector memories decay
- [ ] `/migrate` correctly splits existing collection into short-term + long-term
- [ ] `/migrate --force` updates all memories
- [ ] `/migrate` is idempotent (running twice produces same result)

### Integration Tests - Latency Benchmarks
- [ ] Full `recall()` completes in <165ms with 1000 short-term + 1000 long-term memories
- [ ] Inclusion scoring adds <2ms overhead per query
- [ ] Graph path filtering adds <25ms overhead (with pre-embedded edges)
- [ ] No synchronous DB writes during retrieval (access tracking is async)
- [ ] Reorganization successfully flushes access buffer
- [ ] Reorganization successfully recomputes retrieval factors

### Integration Tests - Observability
- [ ] `LifecycleMetrics` captures all collection counts
- [ ] `/status` displays lifecycle breakdown
- [ ] Telemetry events are emitted after each cycle
- [ ] Alert thresholds are configurable

### Manual Testing (memory-chat.py)
```bash
# 0. Migrate existing memories (if upgrading)
/migrate              # Preview migration
/migrate --force      # Execute migration

# 1. Create memories
/chat Tell me about machine learning
/consolidate

# 2. Verify SHORT_TERM
/status  # Should show lifecycle breakdown

# 3. Access memory multiple times
/recall machine learning
/recall machine learning

# 4. Run lifecycle
/reorganize

# 5. Verify promotion
/meta  # Should show promoted memories

# 6. Wait and verify decay
# (After 24+ hours)
/reorganize
/status  # Check decay scores decreased

# 7. Test recovery
/recover <memory_id> --reason "Testing recovery"
/status  # Verify memory returned to LONG_TERM

# 8. Test soft delete
/prune              # Preview expired memories
/prune --force      # Delete if any past retention
```

---

## Migration Strategy

Migration splits the existing single collection into separate short-term and long-term collections:

```python
async def migrate_to_multi_collection(
    old_collection: Collection,
    short_term_collection: Collection,
    longterm_collection: Collection,
    graph_store: GraphStoreAdapter,
) -> MigrationReport:
    """
    Migrate from single collection to multi-collection architecture.

    Strategy:
    - Consolidated memories → long-term collection (with hit_count=0)
    - Unconsolidated memories → short-term collection
    - Graph nodes get lifecycle metadata added
    """
    now = datetime.now()
    report = MigrationReport()

    # Read all documents from old collection
    all_docs = old_collection.get(include=["embeddings", "documents", "metadatas"])

    for i, doc_id in enumerate(all_docs["ids"]):
        metadata = all_docs["metadatas"][i]
        embedding = all_docs["embeddings"][i]
        document = all_docs["documents"][i]

        # Determine target collection based on consolidated flag
        is_consolidated = metadata.get("consolidated", False)

        if is_consolidated:
            # Move to long-term collection
            target_collection = longterm_collection
            metadata.update({
                "stage": MemoryStage.LONG_TERM.value,
                "hit_count": 0,  # Start fresh for long-term tracking
                "promoted_at": now.isoformat(),
            })
            report.longterm_created += 1
        else:
            # Move to short-term collection
            target_collection = short_term_collection
            metadata.update({
                "stage": MemoryStage.SHORT_TERM.value,
                "access_count": 0,
            })
            report.short_term_created += 1

        # Add common lifecycle fields
        metadata.update({
            "decay_score": 0.5,  # Neutral starting point
            "created_at": metadata.get("created_at", now.isoformat()),
            "last_accessed_at": now.isoformat(),
            "last_decay_at": now.isoformat(),
        })

        # Insert into target collection
        await target_collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[document],
            metadatas=[metadata],
        )

        report.vectors_migrated += 1

    # Migrate graph store (add lifecycle metadata, keep in same store)
    for node in graph_store.get_all_nodes():
        if not hasattr(node, "stage") or node.stage is None:
            node.stage = MemoryStage.LONG_TERM
            node.decay_score = 0.5
            node.created_at = getattr(node, "created_at", now)
            node.last_accessed_at = now
            node.last_decay_at = now

            await graph_store.update_node(node)
            report.nodes_migrated += 1

    # Add embeddings to graph edges (optional, can be async)
    if embedding_fn:
        for edge in graph_store.get_all_edges():
            if not edge.get("embedding"):
                source = graph_store.get_node(edge["source"])
                target = graph_store.get_node(edge["target"])
                edge_text = f"{source.name} {edge['relationship']} {target.name}"
                edge["embedding"] = await embedding_fn(edge_text)
                await graph_store.update_edge(edge)
                report.edges_embedded += 1

    return report
```

### Migration Steps

1. **Backup first**: `/reorganize --backup`
2. **Create new collections**: `memories_short_term`, `memories_long_term`
3. **Read all from old collection**: Get documents, embeddings, metadata
4. **Route to appropriate collection**: Based on `consolidated` flag
5. **Add lifecycle metadata**: `stage`, `decay_score`, `hit_count`, timestamps
6. **Update graph nodes**: Add lifecycle fields
7. **Optionally embed graph edges**: For path relevancy scoring
8. **Delete old collection** (optional, after verification)

---

## /migrate Command

A new `/migrate` command will be added to `memory-chat.py` for upgrading existing memory stores to include lifecycle metadata.

### Command Interface

```
/migrate [--dry-run] [--force]
```

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview migration without modifying data (default) |
| `--force` | Actually perform the migration |

### Implementation

```python
# In tests/integration/memory/memory-chat.py

async def cmd_migrate(self, args: str) -> str:
    """Migrate existing memories to include lifecycle metadata."""
    parts = args.strip().split()
    dry_run = "--force" not in parts

    lines = []
    mode = "DRY RUN" if dry_run else "EXECUTING"
    lines.append(f"Memory Lifecycle Migration ({mode})")
    lines.append("=" * 50)

    # Check if migration is needed
    needs_migration = await self._check_migration_needed()
    if not needs_migration:
        lines.append("\nNo migration needed - all memories have lifecycle metadata.")
        return "\n".join(lines)

    # Run migration
    from friday_memory.lifecycle.migration import MemoryMigrator

    migrator = MemoryMigrator(
        graph_store=self._graph_store,
        vector_store=self._vector_store,
    )

    report = await migrator.migrate(dry_run=dry_run)

    lines.append(f"\nVector Store:")
    lines.append(f"  Documents scanned: {report.vectors_scanned}")
    lines.append(f"  Documents migrated: {report.vectors_migrated}")
    lines.append(f"  Already migrated: {report.vectors_skipped}")

    lines.append(f"\nGraph Store:")
    lines.append(f"  Nodes scanned: {report.nodes_scanned}")
    lines.append(f"  Nodes migrated: {report.nodes_migrated}")
    lines.append(f"  Already migrated: {report.nodes_skipped}")

    if report.errors:
        lines.append(f"\nErrors ({len(report.errors)}):")
        for error in report.errors[:5]:
            lines.append(f"  - {error}")
        if len(report.errors) > 5:
            lines.append(f"  ... and {len(report.errors) - 5} more")

    if dry_run:
        lines.append("\nRun '/migrate --force' to apply these changes.")
    else:
        lines.append("\nMigration complete!")

    return "\n".join(lines)

async def _check_migration_needed(self) -> bool:
    """Check if any memories lack lifecycle metadata."""
    # Check vector store
    sample = await self._vector_store.get_sample(limit=10)
    for doc in sample:
        if "stage" not in doc.metadata:
            return True

    # Check graph store
    nodes = self._graph_store.get_all_nodes()[:10]
    for node in nodes:
        if not hasattr(node, "stage") or node.stage is None:
            return True

    return False
```

### MigrationReport Model

```python
# In packages/friday-memory/src/friday_memory/lifecycle/migration.py

from pydantic import BaseModel, Field

class MigrationReport(BaseModel):
    """Report from lifecycle migration."""
    # Vector store stats
    vectors_scanned: int = 0
    vectors_migrated: int = 0
    vectors_skipped: int = 0

    # Graph store stats
    nodes_scanned: int = 0
    nodes_migrated: int = 0
    nodes_skipped: int = 0

    # Errors
    errors: list[str] = Field(default_factory=list)

    @property
    def total_migrated(self) -> int:
        return self.vectors_migrated + self.nodes_migrated

    @property
    def success(self) -> bool:
        return len(self.errors) == 0
```

### Usage Examples

```bash
# Preview what would be migrated
/migrate
# Output:
# Memory Lifecycle Migration (DRY RUN)
# ==================================================
#
# Vector Store:
#   Documents scanned: 156
#   Documents migrated: 156
#   Already migrated: 0
#
# Graph Store:
#   Nodes scanned: 89
#   Nodes migrated: 89
#   Already migrated: 0
#
# Run '/migrate --force' to apply these changes.

# Actually perform migration
/migrate --force
# Output:
# Memory Lifecycle Migration (EXECUTING)
# ==================================================
#
# Vector Store:
#   Documents scanned: 156
#   Documents migrated: 156
#   Already migrated: 0
#
# Graph Store:
#   Nodes scanned: 89
#   Nodes migrated: 89
#   Already migrated: 0
#
# Migration complete!

# Run again (idempotent)
/migrate
# Output:
# Memory Lifecycle Migration (DRY RUN)
# ==================================================
#
# No migration needed - all memories have lifecycle metadata.
```

### Backup Recommendation

The migration is non-destructive (adds fields, doesn't modify existing data), but users should be advised to backup first:

```bash
# Recommended workflow
/reorganize --backup   # Create backup
/migrate --force       # Run migration
/status                # Verify migration
```

---

## /recover Command

A recovery command allows manually reactivating DECAYED or DELETED memories.

### Command Interface

```
/recover <memory_id> [--reason <reason>]
```

| Option | Description |
|--------|-------------|
| `memory_id` | The ID of the memory to recover |
| `--reason` | Optional reason for recovery (logged) |

### Implementation

```python
async def cmd_recover(self, args: str) -> str:
    """Recover a decayed or deleted memory."""
    parts = args.strip().split()
    if not parts:
        return "Usage: /recover <memory_id> [--reason <reason>]"

    memory_id = parts[0]
    reason = None
    if "--reason" in parts:
        reason_idx = parts.index("--reason")
        if reason_idx + 1 < len(parts):
            reason = " ".join(parts[reason_idx + 1:])

    # Find memory in decayed or deleted collection
    memory = await self._decayed_collection.get(memory_id)
    if not memory:
        return f"Memory '{memory_id}' not found in decayed/deleted memories."

    # Recover to LONG_TERM
    memory.metadata["stage"] = MemoryStage.LONG_TERM.value
    memory.metadata["decay_score"] = 0.5  # Reset to neutral
    memory.metadata["recovered_at"] = datetime.now().isoformat()
    memory.metadata["recovery_reason"] = reason

    # Move to long-term collection
    await self._longterm_collection.add(
        ids=[memory_id],
        embeddings=[memory.embedding],
        documents=[memory.document],
        metadatas=[memory.metadata],
    )

    # Delete from decayed collection
    await self._decayed_collection.delete(ids=[memory_id])

    # Log recovery action
    self._log_recovery(memory_id, reason)

    # Also recover linked graph nodes
    recovered_nodes = await self._promotion_service.reactivate_graph_node_on_vector_access(memory_id)

    return f"Recovered memory '{memory_id}' to LONG_TERM (decay_score reset to 0.5). {recovered_nodes} linked graph nodes also reactivated."
```

### /prune Command (Hard Delete)

```
/prune [--dry-run] [--force]
```

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview what would be deleted (default) |
| `--force` | Actually delete memories past retention period |

```python
async def cmd_prune(self, args: str) -> str:
    """Hard-delete memories past retention period."""
    parts = args.strip().split()
    dry_run = "--force" not in parts

    cutoff = datetime.now() - timedelta(days=self._config.decayed_retention_days)

    # Find memories past retention
    expired = await self._decayed_collection.query_metadata({
        "decayed_at": {"$lt": cutoff.isoformat()}
    })

    if not expired:
        return "No memories past retention period."

    lines = [f"Found {len(expired)} memories past {self._config.decayed_retention_days}-day retention period."]

    if dry_run:
        lines.append("")
        lines.append("Preview (first 10):")
        for m in expired[:10]:
            lines.append(f"  - {m.id}: {m.document[:50]}...")
        lines.append("")
        lines.append("Run '/prune --force' to permanently delete.")
    else:
        deleted = await self._decayed_collection.delete(ids=[m.id for m in expired])
        lines.append(f"Permanently deleted {deleted} memories.")

    return "\n".join(lines)
```

---

## Decisions Made

| Question | Decision |
|----------|----------|
| **Storage architecture** | Separate collections for short-term, long-term, and decayed |
| **Long-term retrieval** | Query in parallel with short-term, apply inclusion scoring |
| **Inclusion scoring** | similarity × time_decay × usage_boost, threshold 0.6 |
| **Graph relevancy** | Score node-edge-node paths, filter by relevancy >= 0.5 |
| **hit_count tracking** | Yes, in long-term vector store metadata |
| **Edge embeddings** | Pre-compute during consolidation for fast path scoring |

## Open Questions

1. ~~**Decay Granularity**: Should decay be per-memory or per-entity?~~
   - **RESOLVED**: Per-memory (vectors have individual decay), with graph nodes linked via `source_memory_ids`
   - Graph nodes decay when ALL their source vector memories have decayed (see "Graph-Vector Decay Linkage")

2. ~~**Cross-Store Consistency**: When a vector decays, should its related graph node also decay?~~
   - **RESOLVED**: Yes, via `source_memory_ids` linkage
   - `propagate_decay_to_graph()` decays nodes when all source memories decay
   - Reactivation also propagates (see "Graph-Vector Decay Linkage")

3. **Access Definition**: What counts as "access"?
   - **Decision**: Context assembly inclusion (when memory is selected for prompt)
   - Not just query results, but actually included in context

4. **Reactivation Threshold**: Should reactivation require multiple accesses or just one?
   - Current design: Single access reactivates DECAYED → LONG_TERM
   - May want higher bar (e.g., 2-3 accesses) to prevent noise
   - *Note: Recovery via `/recover` command provides explicit manual reactivation*

5. **DECAYED Visibility**: Should DECAYED memories still appear in queries?
   - **Decision**: No, decayed memories are in separate collection, not queried by default
   - Can be explicitly queried via `/recover` command for debugging/recovery

6. **Edge Embedding Cost**: Pre-computing edge embeddings adds overhead during consolidation
   - Tradeoff: Slower consolidation vs faster retrieval
   - May want to make this configurable or batch process async
