---
title: Adaptive memory
description: Stores, extraction, recall, context assembly, lifecycle scoring and safe maintenance.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: guide
---

# Adaptive memory

Friday memory coordinates conversation history, vector retrieval and entity
relationships. It supplies context for future model requests; it does not update
model weights or guarantee that extracted statements are correct.

## Stores and controllers

| Role | Current implementation | Persistence and prerequisites |
| --- | --- | --- |
| Episodic turns | `InMemoryEpisodicStore` | Process-local; no model required |
| Durable conversation records | `SQLiteTranscriptStore`, `JSONLTranscriptStore`; transcript-backed episodic integration | Application-owned files and session IDs |
| Ephemeral vectors | `SimpleVectorStore` | An embedding implementation; no disk persistence |
| Persistent vectors | `ChromaVectorStore` | Chroma directory/collection and compatible embeddings |
| Relationships | `ElementXGraphStore` | Graph persistence as configured by the application |
| Deliberately omitted graph | `NullGraphStore` | No relationship recall |
| Coordinated operations | `MemoryController` | Explicit vector, graph, episodic and collection-manager dependencies |

The adapter protocols are defined in Core. A possible custom backend is not an
installed implementation: Friday does not ship the old guides' Pinecone/Neo4j
adapter classes. Prefer [Runtime composition](03-core-concepts.md#runtime-composition-and-ownership)
for a full application rather than copying incomplete constructor recipes.

`MemoryController` requires `vector_store`, `graph_store`, `episodic_store` and
`collection_manager`. `CollectionManager` creates staged Chroma collections and
needs an embedding service; it is not a generic zero-cost in-memory coordinator.
Optional controller dependencies include telemetry, priming configuration,
access tracking, graph scoring and a transcript store for cross-session history.

## Durable transcripts

This **offline Python example** writes and reads one turn in a temporary SQLite
database. It needs only `friday-framework-transcript==0.1.0a3`:

```python
import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
from friday_transcript import SQLiteTranscriptStore, TranscriptEntry, TranscriptSession

async def main() -> None:
    with TemporaryDirectory() as directory:
        store = SQLiteTranscriptStore(Path(directory) / "transcript.db")
        await store.create_session(TranscriptSession(
            session_id="demo", model_name="offline-example",
        ))
        await store.append_entry(TranscriptEntry(
            id="entry-1", session_id="demo", turn_number=1,
            user_message="Name the project.", assistant_message="Friday",
        ))
        entries = await store.get_entries("demo")
        print(entries[0].assistant_message)

asyncio.run(main())
```

Expected output: `Friday`. The temporary directory is deleted on exit. To retain
data, use a persistent application-owned path. The store uses per-operation
connections; this example does not require a nonexistent public `close()` method.
Snapshot/recovery is a separate coordinated operation, discussed below.

## Semantic search without a provider

`SimpleVectorStore` accepts an object with async `embed_documents()` and
`embed_query()` methods. This **offline Python example** uses a deliberately
small deterministic embedding to demonstrate the interface, not semantic quality:

```python
import asyncio
from friday_memory import SimpleVectorStore

class DemoEmbeddings:
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [await self.embed_query(text) for text in texts]

    async def embed_query(self, text: str) -> list[float]:
        return [1.0, 0.0] if "python" in text.lower() else [0.0, 1.0]

async def main() -> None:
    store = SimpleVectorStore(embedding_function=DemoEmbeddings())
    await store.add_documents(
        texts=["Python project", "Gardening notes"],
        metadatas=[{"source": "demo"}, {"source": "demo"}],
        ids=["python", "garden"],
    )
    matches = await store.query("Python", n_results=1)
    print(matches[0]["id"])

asyncio.run(main())
```

Expected output: `python`. Production embeddings have a model identity and vector
dimension. Keep them stable for existing collections; re-embedding is an explicit
migration with backup and validation. `SimpleVectorStore`'s `rerank` and `hybrid`
arguments do not enable those algorithms in this adapter.

## From a turn to reusable memory

The owning application records a turn, schedules enabled extraction, validates
the extraction output and stores resulting entities, relationships, insights or
summaries. `MemoryExtractor`, `MemoryConsolidator` and ingestion pipelines have
different responsibilities:

| Operation | Purpose | Operational consequence |
| --- | --- | --- |
| Extraction | Structured information from conversation text using an ontology/prompt | Can call an LLM; output can be wrong or rejected |
| Consolidation | Summaries and reusable content from accumulated turns | Can call an LLM; not equivalent to deleting the transcript |
| Document ingestion | Chunking and indexing explicitly supplied content | Can embed/summarize; source trust and retention must be chosen |
| Recall | Retrieve history, semantic candidates and graph information | May call embeddings and optional routing/scoring services |
| Context assembly | Filter/prune recall into a `ContextPayload` | Inclusion is query- and budget-dependent |
| Prompt layout | Build model messages from payload, history and tools | Formatting overhead and provider limits still matter |

Chat's `extraction.interval` controls its configured extraction cadence; a turn
may be visible in a transcript before derived memory is available. Shutdown and
background failures must be inspected independently. Repeated extraction can
reinforce graph access counts; reinforcement is not factual verification.

## Recall and cross-session priming

Recall operates on a session and selected collection policies. Priming supplies
initial entities, insights, summaries, relationship information and optionally
recent turns from earlier sessions. Relevant controls in Chat include
`memory.priming.enabled`, `top_entities`, `max_insights`, `max_summaries`,
`max_known_facts`, `recency_days`, `token_budget`, `previous_sessions` and
`previous_session_turns`.

The controller's own fallback defaults and the packaged Chat template differ.
For example, the controller fallback uses no previous sessions, while the broad
template requests two. Choose explicitly instead of treating an example value
as a universal default. Use `/sessions` and `/transcript` to inspect durable data,
and `/context` or `/prompt` to inspect what the current turn actually received.

Prior-session history participates in the assembler's token estimate and is
dropped **before current-session history** when pruning is needed. The formatter
merges retained prior/current turns chronologically. It does not allocate a
separately guaranteed history quota by subtracting the supporting-context ratio.

## Context engineering

`ContextAssembler` reserves estimated formatting overhead, excludes decayed and
superseded content, applies relevance filters and prunes lower-priority material.
`PromptArchitect` places the base system message first, history next and
supporting context near the latest query in its attention layout. This placement
is an implementation strategy, not proof that a model will recall every detail.

Tools consume schema tokens and tool results consume additional context. Broad
registries can crowd out memory. Chat has separate schema-count/budget controls
and MCP result reservations; see [tools](05-tools.md#selection-and-context-budgets).

The detailed [memory-management guide](memory-management-guidelines.md) explains
the current pruning order, budget arithmetic, supporting-context section names
and opt-in background compaction. There is no implemented `solve_knapsack`
optimizer in `friday-optimization`.

## Lifecycle stages and collection movement

The public `MemoryStage` enum includes `episodic`, `short_term`, `long_term`,
`decayed` and `deleted`. Staged semantic memory uses short-term, long-term and
decayed collections. Lifecycle processing is executed by configured services;
declaring a metadata stage does not schedule an autonomous maintenance daemon.

`MemoryLifecycleMetadata` records stage, decay score, creation/access/decay times,
access count, promotion state and protection. Promotion uses a weighted score;
decay uses time since access. Inclusion scoring uses age from creation and is
a separate retrieval calculation.

| `DecayConfig` library default | Value | Meaning |
| --- | --- | --- |
| `decay_rate` | 0.01/hour | Exponential lifecycle decay |
| `access_boost` | 0.2 | Score boost capped at 1.0 |
| `promotion_threshold` | 0.7 | Minimum promotion score |
| `decay_threshold` | 0.2 | Below this score, eligible to decay |
| `short_term_min_age_hours` | 24 | Minimum age for ordinary promotion consideration |
| `decayed_retention_days` | 30 | Retention before configured cleanup |

The Chat template deliberately overrides some values, including retention and
decay threshold. Review the effective configuration before enabling maintenance.

The scorer normalizes age over 72 hours, accesses over 5 and relationships over 3,
clamps confidence to 0..1 and combines factors with weights 0.2/0.4/0.2/0.2.
Changing weights requires a sum near 1.0. High scores indicate configured usage
priority, not verified knowledge.

This **offline Python example** evaluates the default decay curve at fixed times:

```python
from datetime import datetime, timedelta, timezone
from friday_memory import DecayCalculator, DecayConfig

start = datetime(2026, 10, 1, tzinfo=timezone.utc)
calculator = DecayCalculator(DecayConfig())
for hours in (24, 72, 168):
    score = calculator.calculate_decay(1.0, start, now=start + timedelta(hours=hours))
    print(hours, round(score, 3))
```

Expected scores: `0.787`, `0.487`, `0.186`. A week at 0.01/hour retains about 19%,
not 37%. The retrieval scorer's default 0.005/hour produces a different curve.

## Provenance and namespace-aware memory

`ProvenanceMetadata` can identify source, author, confidence and time. The additive
`MultiAgentMemoryController` applies namespace visibility and shared-write policy
around the underlying controller. It is opt-in composition; sharing an ordinary
controller does not automatically create private agent namespaces.

The default policy is an in-process policy object, not authentication or a
cryptographically secure capability issuer. Do not expose it directly as a
multi-tenant authorization system. Use [multi-agent guidance](07-multi-agent.md)
for explicit handoffs and promotion boundaries.

## Maintenance, backups and recovery

Start with read-only inspection and a disposable copy. Quiesce writers,
extraction, compaction, access-buffer flushes and tool-driven ingestion before
snapshot/restore. Public recovery contracts identify participants, manifests,
quiescence tokens, supported operations and categorical errors.

Chat's coordinated `/reorganize` previews by default and requires exact
`--execute` for mutation. Current adapter capability/preflight checks can refuse
execution; see `/help reorganize`. `/reset`, `/migrate --execute`, `/lifecycle
--execute` and re-embedding have different effects and must not be used as
routine fixes for missing recall.

Do not delete Chroma directories, SQLite lock/WAL files or graph data while a
process is active. A copied live directory is not proof of a consistent backup.
Retain transcript/source evidence separately from derived-memory quality checks.

## Implementation references

- [Controller](../../packages/friday-memory/src/friday_memory/controller/memory_controller.py)
- [Collection manager](../../packages/friday-memory/src/friday_memory/retrieval/collection_manager.py)
- [Assembler](../../packages/friday-memory/src/friday_memory/context/assembler.py) and [layout](../../packages/friday-memory/src/friday_memory/context/layout.py)
- [Lifecycle](../../packages/friday-memory/src/friday_memory/lifecycle)
- [Recovery contracts](../../packages/friday-memory/src/friday_memory/maintenance/recovery.py)
- [Transcript package](../../packages/friday-transcript/README.md)

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)
