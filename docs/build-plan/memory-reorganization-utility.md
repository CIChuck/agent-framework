# Memory Reorganization Utility Plan

## Overview

A maintenance utility for the Friday-Memory package that:
1. **Backs up** all memory stores before any destructive operations
2. **Analyzes** cross-store consistency and identifies issues
3. **Prunes** redundant/stale memories
4. **Synthesizes** new higher-order memories from patterns
5. **Classifies** facts as conversational (opinions) vs falsifiable (verifiable claims)
6. **Verifies** falsifiable claims via researcher + judge LLM pipeline
7. **Restores** from backup if anything goes wrong

## The Three Memory Stores

| Store | File | Contents |
|-------|------|----------|
| **Graph** | `graph.json` | Entities (nodes) + Relationships (edges) with hit_count, provenance |
| **Vector** | `chroma.sqlite3` + `data_level0.bin` | Insights (`type=insight`) + Summaries (`type=summary`) with embeddings |
| **Episodic** | `transcript.db` | Conversation turns with `consolidated` flag |

## Architecture Design

```
MemoryReorganizer
├── BackupManager
│   ├── create_backup(backup_dir) → BackupManifest
│   ├── restore_backup(manifest) → bool
│   └── list_backups() → list[BackupManifest]
│
├── ConsistencyAnalyzer
│   ├── find_orphaned_references() → list[Issue]
│   ├── find_duplicate_entities() → list[DuplicateGroup]
│   ├── find_conflicting_facts() → list[Conflict]
│   └── generate_report() → ConsistencyReport
│
├── RedundancyPruner
│   ├── identify_redundant_insights() → list[RedundantGroup]
│   ├── identify_stale_entities() → list[GraphNode]
│   ├── prune_redundancies(dry_run=True) → PruneReport
│   └── merge_duplicate_entities() → MergeReport
│
├── MemorySynthesizer
│   ├── analyze_topic_clusters() → list[TopicCluster]
│   ├── generate_meta_insights() → list[SynthesizedInsight]
│   ├── identify_knowledge_gaps() → list[Gap]
│   └── synthesize_memories(dry_run=True) → SynthesisReport
│
└── FactChecker
    ├── classify_facts() → list[ClassifiedFact]
    ├── identify_falsifiable_claims() → list[FalsifiableClaim]
    ├── verify_claims(dry_run=True) → VerificationReport
    └── update_fact_confidence() → int
```

## Phase 1: Backup & Recovery System

### BackupManifest Schema
```python
@dataclass
class BackupManifest:
    backup_id: str              # UUID
    created_at: datetime
    source_dir: Path            # Original memory location
    backup_dir: Path            # Backup location
    files: dict[str, str]       # {original_path: backup_path}
    checksums: dict[str, str]   # {file: sha256}
    store_stats: dict           # Counts before backup
```

### Backup Process
1. Create timestamped backup directory: `backups/YYYYMMDD_HHMMSS_<uuid>/`
2. Copy all memory files:
   - `graph.json` → backup
   - `chroma.sqlite3` → backup
   - `data_level0.bin` (and other ChromaDB files) → backup
   - `transcript.db` → backup
3. Calculate SHA256 checksums for integrity verification
4. Write `manifest.json` with metadata
5. Return BackupManifest for restore reference

### Restore Process
1. Verify checksums match
2. Stop any active memory operations
3. Copy backup files back to original locations
4. Verify restored files
5. Return success/failure

## Phase 2: Consistency Analysis

### Types of Inconsistencies

1. **Orphaned Graph References**
   - Edges pointing to non-existent nodes
   - Nodes with provenance.source_id that doesn't exist in transcript

2. **Duplicate Entities**
   - Exact label matches (case-insensitive)
   - Fuzzy matches (>0.85 similarity)
   - Same semantic meaning, different labels (use embeddings)

3. **Stale/Obsolete Data**
   - Entities with hit_count=0 and last_accessed > 30 days
   - Insights with low confidence that were never retrieved
   - Summaries from sessions that no longer exist

4. **Cross-Store Inconsistencies**
   - Insights mentioning entities not in graph
   - Graph entities never referenced in any insight
   - Turns marked consolidated but no corresponding insights

### ConsistencyReport Schema
```python
@dataclass
class ConsistencyReport:
    analyzed_at: datetime
    graph_stats: dict           # node_count, edge_count, orphan_count
    vector_stats: dict          # insight_count, summary_count, duplicate_count
    episodic_stats: dict        # turn_count, consolidated_count
    issues: list[ConsistencyIssue]
    severity_counts: dict       # {critical: N, warning: N, info: N}
```

## Phase 3: Redundancy Pruning

### Redundancy Detection Algorithms

1. **Semantic Deduplication (Vector Store)**

   **Efficient approach**: ChromaDB already stores embeddings! No re-embedding needed.

   ```python
   # Get all document IDs from collection (no embedding call)
   all_docs = vector._collection.get(include=["embeddings", "metadatas"])

   # Use ChromaDB's internal similarity via stored embeddings
   for i, doc_id in enumerate(all_docs["ids"]):
       # Query using the STORED embedding (not re-embedding text)
       similar = vector._collection.query(
           query_embeddings=[all_docs["embeddings"][i]],
           n_results=5,
           where={"id": {"$ne": doc_id}}  # Exclude self
       )

       # Check if any result is too similar (>0.95 cosine)
       if similar["distances"][0] and similar["distances"][0][0] < 0.05:
           mark_as_redundant(doc_id, similar["ids"][0][0])
   ```

   **Cost**: O(n) queries using existing embeddings, zero embedding API calls.

2. **Entity Consolidation (Graph Store)**
   - Use existing `graph.merge_nodes()` capability
   - Extend with semantic similarity via embeddings
   - Merge strategy: Keep highest hit_count, combine properties

3. **Stale Memory Pruning**
   ```python
   # Configurable thresholds (from config file or CLI args)
   config = PruneConfig(
       stale_threshold_days=90,   # --stale-days
       min_hit_count=1,           # --min-hits
   )

   for entity in graph.get_all_nodes():
       if entity.hit_count < config.min_hit_count:
           if entity.last_accessed < (now - timedelta(days=config.stale_threshold_days)):
               mark_for_pruning(entity)
   ```

### PruneReport Schema
```python
@dataclass
class PruneReport:
    dry_run: bool
    insights_removed: int
    entities_merged: int
    entities_removed: int
    edges_removed: int
    bytes_freed: int
    items: list[PrunedItem]     # Details of what was/would be removed
```

## Phase 4: Memory Synthesis (Meta-Learning)

### Synthesis Algorithms

1. **Topic Clustering**
   - Embed all insights
   - Cluster using HDBSCAN or K-means
   - Identify dominant themes per cluster

2. **Knowledge Gap Detection**
   - Find entities with few relationships
   - Find topics mentioned in turns but not in insights
   - Identify questions asked but never answered

3. **Meta-Insight Generation**
   - Analyze patterns across insights
   - Generate higher-order observations:
     ```
     "User frequently discusses Python and TypeScript together,
      suggesting a polyglot development pattern."
     ```
   - Use LLM to synthesize cross-cutting themes

4. **Relationship Inference**
   - If A→B and B→C exist, suggest A→C
   - Use LLM to validate inferred relationships
   - Add with lower confidence scores

### SynthesizedMemory Schema
```python
@dataclass
class SynthesizedMemory:
    type: str                   # "meta_insight", "inferred_relationship", "topic_summary"
    content: str
    source_memories: list[str]  # IDs of source insights/entities
    confidence: float
    reasoning: str              # LLM explanation
```

## Phase 5: Fact Verification

### The Falsifiability Test

Every fact/insight is classified by asking: **"Is this claim falsifiable?"**

| Category | Falsifiable? | Example | Action |
|----------|--------------|---------|--------|
| **Conversational Fact** | No | "Chuck believes Babe Ruth was the greatest baseball player" | Store as-is, mark `falsifiable: false` |
| **Real-World Claim** | Yes | "Babe Ruth hit 714 home runs" | Verify via fact-checking agent |

### Fact Classification Algorithm

```python
class FactClassifier:
    """Uses LLM to classify facts as falsifiable or conversational."""

    CLASSIFICATION_PROMPT = """
    Analyze this statement and determine if it is FALSIFIABLE.

    A falsifiable claim:
    - Makes an objective assertion about the real world
    - Can be verified or disproven with evidence
    - Examples: dates, statistics, scientific facts, historical events

    A conversational/subjective claim:
    - Expresses opinion, belief, preference, or feeling
    - Cannot be objectively proven true or false
    - Examples: "X is the best", "I prefer Y", "Chuck thinks Z"

    Statement: "{statement}"

    Respond with JSON:
    {
        "falsifiable": true/false,
        "reasoning": "brief explanation",
        "claim_type": "statistical|historical|scientific|opinion|preference|belief",
        "suggested_verification": "how to verify if falsifiable, null otherwise"
    }
    """
```

### Verification Pipeline

```
1. CLASSIFY: LLM determines falsifiability
   │
   ├─ falsifiable: false → Store with metadata, skip verification
   │
   └─ falsifiable: true → Continue to verification
       │
       2. EXTRACT CLAIM: Parse the verifiable assertion
       │
       3. VERIFY: Fact-checking agent researches claim
       │   ├─ Web search for authoritative sources
       │   ├─ Cross-reference multiple sources
       │   └─ Generate confidence score
       │
       4. JUDGE: Second LLM acts as impartial judge
       │   ├─ Reviews claim + evidence
       │   ├─ Determines: VERIFIED | DISPUTED | UNVERIFIABLE
       │   └─ Provides reasoning
       │
       5. UPDATE: Modify fact metadata
           ├─ verified: true/false/null
           ├─ verification_confidence: 0.0-1.0
           ├─ verification_sources: [urls]
           └─ verification_note: "correction or context"
```

### Fact Metadata Schema

```python
# Extended metadata for insights/facts in Vector Store
FactMetadata = {
    # Existing fields
    "type": "insight",
    "created_at": "2025-01-09T...",
    "provenance_source_id": "turn_abc123",

    # NEW: Falsifiability classification
    "falsifiable": bool,              # Is this claim verifiable?
    "claim_type": str,                # "statistical", "historical", "opinion", etc.

    # NEW: Verification results (only if falsifiable=True)
    "verified": bool | None,          # True=confirmed, False=disputed, None=unverified
    "verification_confidence": float, # 0.0-1.0
    "verification_sources": [str],    # URLs or source names
    "verification_note": str,         # Correction or context
    "verified_at": str,               # ISO timestamp of verification
    "verified_by": str,               # "fact_checker_agent_v1"
}
```

### FactChecker Class

```python
class FactChecker:
    def __init__(
        self,
        classifier_llm: LLMClient,      # For classification
        researcher_llm: LLMClient,      # For web research (can use tools)
        judge_llm: LLMClient,           # For final verdict
        vector_store: VectorStoreAdapter,
    ):
        ...

    async def classify_facts(
        self,
        limit: int = 100,
        unclassified_only: bool = True,
    ) -> list[ClassifiedFact]:
        """Classify facts as falsifiable or conversational."""
        ...

    async def identify_falsifiable_claims(
        self,
        unverified_only: bool = True,
    ) -> list[FalsifiableClaim]:
        """Get all falsifiable claims pending verification."""
        ...

    async def verify_claims(
        self,
        claims: list[FalsifiableClaim],
        dry_run: bool = True,
    ) -> VerificationReport:
        """
        Verify claims using researcher + judge pattern.

        Pipeline:
        1. Researcher LLM searches for evidence
        2. Judge LLM evaluates evidence and makes verdict
        3. Update vector store with verification results
        """
        ...

    async def update_fact_confidence(
        self,
        adjustments: list[ConfidenceAdjustment],
    ) -> int:
        """Bulk update confidence scores based on verification."""
        ...
```

### VerificationReport Schema

```python
@dataclass
class VerificationReport:
    analyzed_at: datetime
    total_claims: int
    verified_true: int          # Claims confirmed as accurate
    verified_false: int         # Claims found to be incorrect
    unverifiable: int           # Claims that couldn't be verified
    skipped_conversational: int # Non-falsifiable claims skipped

    claims: list[VerifiedClaim]

@dataclass
class VerifiedClaim:
    claim_id: str
    original_text: str
    falsifiable: bool
    verdict: str                # "VERIFIED" | "DISPUTED" | "UNVERIFIABLE" | "CONVERSATIONAL"
    confidence: float
    evidence_summary: str
    sources: list[str]
    correction: str | None      # If disputed, what's the correct info?
    judge_reasoning: str
```

### CLI Commands

```bash
# Classify all unclassified facts
python -m friday_memory.maintenance classify --dir ./memory

# Show falsifiable claims pending verification
python -m friday_memory.maintenance list-claims --dir ./memory --unverified

# Verify claims (dry run - shows what would be checked)
python -m friday_memory.maintenance verify --dir ./memory --dry-run

# Verify claims for real
python -m friday_memory.maintenance verify --dir ./memory --limit 50

# Show verification report
python -m friday_memory.maintenance verify-report --dir ./memory
```

## Implementation Plan

### File Structure
```
packages/friday-memory/src/friday_memory/
├── maintenance/
│   ├── __init__.py
│   ├── backup.py           # BackupManager
│   ├── analyzer.py         # ConsistencyAnalyzer
│   ├── pruner.py           # RedundancyPruner
│   ├── synthesizer.py      # MemorySynthesizer
│   ├── fact_checker.py     # FactChecker (classification + verification)
│   └── reorganizer.py      # Main orchestrator (MemoryReorganizer)
```

### CLI Integration
```bash
# Create backup
python -m friday_memory.maintenance backup --dir ./memory

# Analyze consistency
python -m friday_memory.maintenance analyze --dir ./memory --report report.json

# Prune redundancies (dry run)
python -m friday_memory.maintenance prune --dir ./memory --dry-run

# Prune for real
python -m friday_memory.maintenance prune --dir ./memory --backup-first

# Synthesize new memories
python -m friday_memory.maintenance synthesize --dir ./memory --dry-run

# Classify facts (falsifiable vs conversational)
python -m friday_memory.maintenance classify --dir ./memory

# Verify falsifiable claims
python -m friday_memory.maintenance verify --dir ./memory --dry-run

# Full reorganization (backup → analyze → prune → synthesize → classify → verify)
python -m friday_memory.maintenance reorganize --dir ./memory --backup-first
```

### Safety Guarantees

1. **Always Backup First** - Every destructive operation requires `--backup-first` or explicit `--no-backup`
2. **Dry Run Default** - All pruning/synthesis operations default to `--dry-run`
3. **Atomic Operations** - Use transactions where possible
4. **Checksum Verification** - Validate backup integrity before restore
5. **Detailed Logging** - Every operation logged with timestamps and item IDs

## Configuration

All thresholds and parameters are configurable via CLI flags or config file:

```yaml
# maintenance_config.yaml
pruning:
  stale_threshold_days: 90      # Entities older than this with low hits
  min_hit_count: 1              # Minimum access count to keep
  similarity_threshold: 0.95    # Cosine similarity for dedup (1.0 = identical)

synthesis:
  cluster_min_size: 3           # Minimum insights per topic cluster
  meta_insight_confidence: 0.7  # Confidence for synthesized insights

fact_checking:
  batch_size: 50                # Claims to verify per run
  verification_timeout: 30      # Seconds per claim lookup

llm:
  classifier_model: null        # LLM for classification (default: extraction model)
  researcher_model: null        # LLM for web research
  judge_model: null             # LLM for verdict
```

**CLI Override Examples:**
```bash
python -m friday_memory.maintenance prune --stale-days 60 --min-hits 2
python -m friday_memory.maintenance verify --batch-size 100
```

## Design Decisions (Confirmed)

1. **Meta-insight Type**: `type="meta_insight"` - Distinct from regular insights for filtering and provenance clarity

2. **Configurable Thresholds**: All pruning/synthesis thresholds configurable via config file or CLI flags

3. **Automation**: On-demand only - User explicitly triggers maintenance via CLI

4. **LLM Usage**: Configurable per-component (classifier, researcher, judge can use different models)

5. **Fact Classification**: Use falsifiability test - "Can this claim be verified or disproven?"
   - Conversational facts (`falsifiable: false`): Opinions, beliefs, preferences
   - Real-world claims (`falsifiable: true`): Statistics, dates, historical facts

6. **Verification Pipeline**: Researcher + Judge pattern
   - Researcher LLM gathers evidence (web search, authoritative sources)
   - Judge LLM renders verdict (VERIFIED, DISPUTED, UNVERIFIABLE)
   - Disputed claims get correction notes attached

7. **Fact-Checking Timing**: Maintenance-time only (batch processing)
   - Avoids latency impact during conversation
   - Future enhancement: Optional extraction-time classification for high-confidence claims

8. **Efficient Deduplication**: Use ChromaDB's stored embeddings
   - Zero embedding API calls during dedup
   - Query existing embeddings for similarity matching

## Implementation Order

### Step 1: BackupManager (Foundation)
- Create `maintenance/backup.py`
- Implement `create_backup()`, `restore_backup()`, `list_backups()`
- Add manifest with checksums
- **Test**: Backup/restore round-trip integrity

### Step 2: ConsistencyAnalyzer (Read-Only)
- Create `maintenance/analyzer.py`
- Implement orphan detection, duplicate finding, cross-store checks
- Generate detailed reports
- **Test**: Detect known inconsistencies in fixtures

### Step 3: RedundancyPruner (Destructive)
- Create `maintenance/pruner.py`
- Implement semantic dedup, stale pruning, entity merging
- Always dry-run by default
- **Test**: Verify correct items identified, backup required

### Step 4: MemorySynthesizer (Generative)
- Create `maintenance/synthesizer.py`
- Implement topic clustering, meta-insight generation
- Store with `type="meta_insight"` and `provenance.source_type="synthesis"`
- **Test**: Verify coherent synthesis from test data

### Step 5: FactChecker (Classification + Verification)
- Create `maintenance/fact_checker.py`
- Implement falsifiability classification via LLM
- Implement researcher + judge verification pipeline
- Add metadata fields: `falsifiable`, `verified`, `verification_sources`
- **Test**: Classify known facts, verify against real sources

### Step 6: CLI & Orchestrator
- Create `maintenance/__main__.py` for CLI entry point
- Create `maintenance/reorganizer.py` to orchestrate all components
- Wire up argparse with subcommands
- **Test**: End-to-end CLI workflow

## Files to Create

| File | Purpose |
|------|---------|
| `maintenance/__init__.py` | Package exports |
| `maintenance/backup.py` | BackupManager class |
| `maintenance/analyzer.py` | ConsistencyAnalyzer class |
| `maintenance/pruner.py` | RedundancyPruner class |
| `maintenance/synthesizer.py` | MemorySynthesizer class |
| `maintenance/fact_checker.py` | FactChecker class (classify + verify) |
| `maintenance/reorganizer.py` | MemoryReorganizer orchestrator |
| `maintenance/__main__.py` | CLI entry point |
| `maintenance/models.py` | Pydantic models for reports/manifests |

## Verification Plan

1. Create test fixtures with known redundancies and inconsistencies
2. Run backup → verify files and checksums
3. Run analysis → verify issues detected
4. Run prune (dry-run) → verify correct items identified
5. Run prune (real) → verify items removed, backup intact
6. Restore from backup → verify original state recovered
7. Run synthesis → verify new memories are coherent
8. Run classify → verify facts categorized correctly (opinion vs falsifiable)
9. Run verify → verify claims checked against sources, metadata updated
