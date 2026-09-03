# Friday Memory Package Review — Pass 1

**Date:** 2026-08-10
**Last updated:** 2026-08-11
**Status:** First-pass, as-built review with a locked Memory V2 boundary
**Primary scope:** `packages/friday-memory`
**Adjacent scope:** Cross-package contracts used by `friday-memory`, principally
`friday-core`, `friday-agent`, `friday-runtime`, `friday-chat`,
`friday-transcript`, and `friday-tools`
**Review mode:** Read-only; no implementation changes were made

## Executive Summary

`friday-memory` is an ambitious and feature-rich package, but it is not yet a
sufficiently coherent or trustworthy context-engineering subsystem. Its
strongest areas are recovery-aware maintenance, memory lifecycle management,
provenance intent, and breadth of functionality. Its weakest areas are semantic
correctness, cross-store consistency, retrieval quality, trust boundaries, and
oversized or weakly typed architectural seams.

Several findings in this review are concrete correctness defects rather than
prospective enhancements. In particular:

1. extracted relationship IDs are not mapped to the graph nodes created for the
   extracted entities;
2. the graph representation overwrites valid relationships and can reverse
   incoming relationships during retrieval;
3. consolidation omits assistant messages and marks source turns consolidated
   after failed work;
4. prompt formatting does not reliably receive the current user query or
   session state;
5. checkpoint restoration is not coherent across transcript, vector, graph,
   lifecycle, or session-state data; and
6. multi-agent memory filtering is not sufficient to enforce namespace
   isolation.

The package test suite is green, but current coverage does not exercise several
of these semantic contracts. In one case, a graph test explicitly accepts
lossy edge replacement as expected behavior.

The largest architectural problem is the absence of a canonical, versioned
memory or claim record. Episodic, vector, and graph data are independently
mutated stores rather than projections of one durable source of truth. This
makes extraction, consolidation, lifecycle transitions, rollback, correction,
deletion, and audit substantially harder than necessary.

The recommended response is a clean Memory V2 implementation behind the
existing supported public package interface. Memory V2 is not required to
import or remain compatible with any persisted Memory V1 state. This removes
data migration, dual-read, dual-write, and legacy-index translation from the
construction scope while preserving source compatibility for the wider Agent
Framework.

## Locked Memory V2 Assumption and Compatibility Boundary

The following assumption is normative for subsequent planning and construction
based on this review:

> Memory V2 preserves the supported `friday_memory` public interface needed by
> the Agent Framework, but has no backward-compatibility obligation to any
> existing Memory V1 vector collection, graph file, transcript-backed memory
> data, lifecycle state, access buffer, embedding, memory ID, recovery artifact,
> or other persisted memory store.

This creates a deliberate distinction between API compatibility and persisted
state compatibility:

| Area | Memory V2 requirement |
|---|---|
| Installed distribution and `friday_memory` imports | Preserve |
| Declared or documented public class and model names | Preserve |
| Supported method signatures | Preserve, or extend only through optional/additive contracts |
| Existing return fields | Preserve; additive optional fields are permitted |
| Undocumented but actively consumed concrete properties | Inventory and preserve temporarily or coordinate the consumer change |
| Correct public behavior | Preserve |
| Defective or unsafe behavior | Correct rather than preserve |
| Existing vector collections and embeddings | No compatibility or import required |
| Existing graph files and graph identities | No compatibility or import required |
| Existing transcript-backed memory data | No compatibility or import required |
| Existing lifecycle, access-buffer, and job state | No compatibility or import required |
| V1 storage-engine implementation modules | No preservation requirement except where they expose a supported public symbol |
| V1-to-V2 data migration tooling | Out of scope |
| Dual-read or dual-write operation | Out of scope |
| Automatic deletion of V1 state | Prohibited unless separately authorized |

Memory V2 should use a fresh storage namespace, such as:

```text
.friday/
  <existing V1 paths and stores remain in place and are ignored>
  memory-v2/
    ledger/
    projections/
    indexes/
    jobs/
    recovery/
```

The exact configured path may differ, but the invariant is the same: Memory V2
must not automatically read, translate, modify, or delete Memory V1 state.
Existing state may be archived or removed only through a separate, explicitly
authorized operation.

Public-interface preservation does not mean preserving every concrete internal
class, private attribute, storage layout, dictionary detail, or accidental
behavior. Before construction, the surface must be classified as:

1. **Supported public API:** remains source-compatible.
2. **De facto framework API:** currently used by adjacent packages and either
   preserved temporarily or replaced through a coordinated framework change.
3. **Private implementation:** replaceable without compatibility guarantees.
4. **Defective semantics:** intentionally corrected even when results change.
5. **Memory V2 API:** richer, additive contracts adopted incrementally.

Likely de facto dependencies include `.graph`, `.vector`, `.episodic`,
`.collection_manager`, concrete `ContextAssembler` behavior, passage metadata,
and lifecycle or maintenance result models. These can be backed by V2
projection adapters without retaining any V1 storage representation.

### Explicit V2 Non-Goals

The following are out of scope unless a later decision explicitly amends this
review:

- importing, converting, reconciling, or validating V1 persisted memory;
- preserving V1 memory IDs, embeddings, scores, graph topology, lifecycle
  stage, access counts, journals, or recovery paths;
- reproducing exact V1 retrieval, summarization, consolidation, or ranking
  output;
- dual-reading or dual-writing V1 and V2 during construction or cutover;
- reverse-migrating V2 records into V1 after a rollback;
- deleting, moving, repairing, or reorganizing V1 state;
- retaining Chroma, NetworkX, or any other V1 backend solely for compatibility;
  and
- forcing immediate adoption of new V2-only APIs by otherwise compatible Agent
  Framework consumers.

### Consequences for the Rest of This Review

The clean-state decision changes how every later finding and recommendation is
to be interpreted:

1. **The findings remain as-built V1 evidence.** They explain why V2 is needed
   and identify behavior V2 must not reproduce.
2. **Priorities become V2 acceptance priorities.** A P0 item is a V2 release
   blocker if reproduced; it is not an instruction to patch V1 in place.
3. **“Preserve” means preserve a sound capability or invariant.** It does not
   mean reuse a V1 serializer, collection layout, graph format, access log,
   journal schema, recovery bundle, or implementation class.
4. **Existing tests are baseline and contract-discovery evidence.** They do not
   validate V2, and tests that encode defective behavior must be replaced rather
   than copied unchanged.
5. **Recovery begins with the first V2 record.** V2 backup, rollback,
   reorganization, reconciliation, and erasure cover V2 state only. They do not
   recover, convert, or delete V1 state.
6. **Cutover is an engine and storage-root selection, not a data conversion.**
   Starting V2 creates an empty memory system while leaving V1 state untouched.
7. **Rollback means rollback within V2.** Reverting a failed V2 operation or
   deployment does not require writing V2 records back into V1 formats.
8. **Behavioral parity is not the quality target.** Source compatibility and
   correct public contracts are required; reproducing V1 retrieval results,
   rankings, summaries, graph topology, or lifecycle decisions is not.

### API Preservation Mechanism

The supported V1-shaped models and methods should form a compatibility façade,
not the V2 domain model. This distinction permits strict V2 invariants without
breaking current callers that construct public DTOs or consume dictionary-shaped
results.

Memory V2 should normally ship as a new version of the same
`friday-framework-memory` distribution with the same `friday_memory` import
namespace. An internal `friday_memory.v2` namespace is acceptable, but requiring
all framework consumers to import a second distribution would defeat the API
preservation objective.

Examples include:

- public `GraphNode`, `GraphEdge`, `ContextPayload`, and `SessionState` objects
  remaining available while being translated into strict internal V2 records;
- `MemoryController.recall(...)` retaining its signature and existing return
  fields while adding optional retrieval-health, citation, trust, and selection
  information;
- `ContextAssembler.assemble_context(...)` binding the exact request to the
  returned payload so the existing `format_prompt(system_prompt, payload)` call
  no longer has to infer the current query from history; and
- new typed V2 APIs being additive rather than mandatory for existing Agent
  Framework consumers.

Strict `extra="forbid"` behavior belongs on persisted and internal V2 models.
Applying it indiscriminately to legacy-facing DTOs could itself break the public
interface. Translation from compatibility DTOs into strict V2 domain records is
therefore an intentional boundary.

| Current public component | V2 compatibility treatment |
|---|---|
| `MemoryController` | Retain as the main façade; delegate to V2 ledger, retrieval, lifecycle, and policy services |
| `ContextAssembler` | Retain public calls; bind a typed V2 request to the returned payload instead of inferring query or state |
| `ContextPayload` | Preserve existing fields; add optional evidence, health, citation, trust, and selection fields |
| `SessionState` | Preserve the DTO and methods; back user, session, and application scope with distinct V2 domains |
| `GraphNode` and `GraphEdge` | Preserve as boundary DTOs; translate to V2 entities and independently identified claims |
| Episodic, vector, and graph adapter types | Preserve only supported contracts; implement them as V2 projection adapters without V1 persistence |
| `MemoryExtractor` and `MemoryConsolidator` | Preserve entry points; execute typed, idempotent V2 jobs against the ledger |
| Lifecycle and maintenance entry points | Preserve supported calls and result fields; operate only on V2 state and V2 recovery formats |
| Multi-agent façade | Preserve its call surface; enforce V2 authorization inside candidate queries rather than after retrieval |
| Configuration models | Keep existing files loadable where feasible; isolate or reject V1-specific persistence paths and expose explicit V2 settings |

This table is a design direction, not a substitute for the Phase 0 symbol and
consumer inventory. The inventory determines the exact compatibility contract.

### Configuration, Cutover, and Operational Isolation

Configuration is part of the de facto framework interface and needs an explicit
compatibility policy. Existing non-storage configuration fields should remain
compatible. Every V1 persistence field must be classified during Phase 0 as
either safely mapped to a distinct V2 setting, accepted but visibly deprecated
and ignored, or rejected with an actionable startup error. Memory V2 must never
interpret an existing V1 persistence path as authorization to open V1 state,
and it must not silently ignore a setting in a way that suggests V1 memory was
loaded.

The V2 design should therefore:

1. add or derive an unambiguous V2 storage root;
2. reject or isolate any resolved path that overlaps a configured V1 store;
3. expose engine version, schema version, and resolved V2 root in diagnostics;
4. initialize an empty V2 ledger without scanning for legacy collections;
5. scope maintenance, reorganization, backup, restore, erasure, and inspection
   commands to the resolved V2 root;
6. reject V1 recovery bundles and journals rather than attempting to interpret
   them; and
7. require separate authorization for any operation that archives, relocates,
   or removes V1 state.

The clean-state decision removes a difficult migration and coexistence program,
but it does not reduce the correctness, security, retrieval, lifecycle,
evaluation, or public-contract work required for V2. The implementation remains
a multi-phase subsystem construction effort.

At cutover, users should be told that V2 starts with empty active memory. Memory
inspection and maintenance commands should report the V2 engine, schema, and
root so an empty V2 store is distinguishable from a backend failure or an
accidental connection to V1. Previous conversations and memories must not
appear in V2 unless they are explicitly reintroduced as new post-cutover source
content under a separately authorized workflow.

If `friday-transcript` remains an external component, V2 may continue to use its
public interface for newly recorded V2 turns. That does not imply importing old
transcript rows. A fresh transcript namespace or store must be selected at V2
bootstrap unless a later decision deliberately separates the transcript audit
record from active memory state.

Leaving V1 untouched also leaves its historical privacy, retention, and access
obligations intact. A V2 correction, forgetting operation, retention policy, or
erasure report can attest only to V2 ledger records, V2 projections, V2 jobs,
and V2 recovery artifacts. It must not claim system-wide deletion while V1
stores or backups still exist. V1 archival, access restriction, retention, or
destruction requires its own separately authorized policy and evidence.

### Expected Cross-Package Impact

The façade approach is intended to keep the surrounding framework largely
unchanged, but “largely unchanged” does not mean that no adjacent composition or
configuration work is required.

| Package or layer | Expected V2 impact |
|---|---|
| `friday-core` | Existing memory and context contracts remain usable; richer V2 contracts should be additive unless a separate cross-package decision is approved |
| `friday-agent` | Existing recall, context assembly, and formatting calls continue through the façade; optional V2 APIs may be adopted later |
| `friday-runtime` | Dependency injection constructs the V2 engine and façade and must stop constructing V1 stores for a V2 run |
| `friday-chat` | Additive engine/root configuration and diagnostics may be required; command behavior must target V2 state without changing ordinary chat call patterns |
| `friday-transcript` | Its public interface may be reused for newly recorded V2 turns, but V2 must use a fresh namespace or explicitly defined audit-only relationship |
| `friday-tools` | Existing supported memory imports remain; inspection and maintenance tools must be bound to the V2 façade and root |
| Maintenance and recovery commands | Existing supported command/result surfaces may remain, but artifacts and operations are V2-only |

Any discovered consumer that depends on a private V1 storage object should be
handled through a V2 projection adapter or a narrowly coordinated consumer
change. It must not cause V1 persistence compatibility to re-enter scope.

## Review Scope and Method

This pass examined the package's:

- public surface and documentation;
- data and provenance models;
- episodic, vector, and graph adapters;
- extraction and consolidation pipelines;
- document, file, and tool-output ingestion;
- lifecycle, promotion, decay, and access tracking;
- semantic and graph retrieval;
- context assembly, prompt layout, and token budgeting;
- maintenance, reorganization, backup, recovery, and mutation support;
- multi-agent namespace, promotion, policy, and journal behavior;
- concurrency, background-task, and persistence behavior;
- privacy, trust, poisoning, and data-isolation boundaries; and
- current tests, static checks, and quality-evaluation documentation.

The review treats code as the authority for as-built behavior. Planning and
guide documents were used to understand intent, but several guide claims do not
match the current implementation.

The evidence below was collected from Memory V1. The clean-state Memory V2
boundary was locked after that evidence review and changes the remediation
strategy, not the validity of the observed V1 defects.

The package contains approximately 34,000 source lines across 71 Python source
files. Sixty-six source files carry `# mypy: ignore-errors`, so a successful
package mypy run does not provide meaningful assurance over many of the most
important boundaries.

## Current Memory V1 Architecture

The intended architecture is a tri-store model:

```text
Interaction and document sources
                |
                v
      Extraction / ingestion
                |
      +---------+----------+
      |         |          |
      v         v          v
  Episodic    Vector     Graph
   store      stores      store
      |         |          |
      +---------+----------+
                |
                v
       MemoryController.recall
                |
                v
         ContextAssembler
                |
                v
         PromptArchitect
```

Lifecycle management divides vector records among short-term, long-term, and
decayed Chroma collections. A separate access buffer records retrieval activity
and feeds promotion or decay. Graph data is maintained in a NetworkX directed
graph. Transcript-backed episodic storage may be used as the conversation
record. Maintenance adds backup, journaling, verification, mutation, rollback,
and reorganization workflows.

The broad separation of episodic, semantic, and associative memory is useful.
The problem is that the three representations do not share a sufficiently
strong canonical identity, revision, transaction, or evidence model.

## Strengths to Carry Forward as V2 Design Concepts

The following are valuable foundations:

1. Graph nodes and edges require provenance models.
2. Recovery and mutation contracts are among the package's strongest and most
   strictly validated models.
3. Reorganization supports quiescence, recovery snapshots, verification,
   journals, rollback, postcondition checks, and visible progress reporting.
4. The access buffer has substantive write-ahead-log and recovery support.
5. Lifecycle promotion, decay, quarantine, and maintenance observability are
   materially developed.
6. Some extraction artifacts use stable per-turn vector identities, supporting
   idempotent retries.
7. The configurable extraction ontology provides a useful validation boundary.
8. Context assembly has explicit token estimation, routing, pruning, and budget
   diagnostics, even though its selection strategy needs improvement.
9. Maintenance-generated synthesis is quarantined until verification succeeds.
10. The package has broad unit coverage and substantial lifecycle and
    maintenance regression coverage.

These are concepts and invariants to carry forward, not a requirement to reuse
their V1 storage formats or concrete implementations. For example, V2 should
retain journaled recovery and verified rollback as capabilities while defining
new V2 journal, manifest, and recovery schemas. Existing unit tests may inform
the new conformance suite, but they are not sufficient V2 acceptance evidence.

## V1 Finding Priority and V2 Acceptance Impact

P0 means the behavior must not ship in V2. P1 means the issue must be resolved
before V2 is treated as the canonical production memory engine unless an
explicit containment decision narrows the affected capability. P2 identifies
documentation, evaluation, or maintainability work required for credible V2
release readiness.

| Priority | V1 finding | Consequence if reproduced in V2 |
|---|---|---|
| P0 | Extracted relationship identity is broken | Duplicate placeholder nodes and incorrect graph edges |
| P0 | Graph relations are lossy and incoming traversal can reverse facts | Silent knowledge loss and false context |
| P0 | Consolidation omits assistant messages and finalizes failed work | Incomplete summaries with no safe retry |
| P0 | Formatting lacks a complete request contract | Stale or duplicated user messages and missing state |
| P0 if enabled | Multi-agent isolation is incomplete | Private memory disclosure across namespaces |
| P1 | No canonical memory record or transactional projection model | Partial and inconsistent cross-store state |
| P1 | Retrieval reinforcement measures exposure rather than utility | Self-reinforcing ranking degradation |
| P1 | Tool and document memory lacks a strong trust boundary | Durable prompt injection, poisoning, or secret retention |
| P1 | Checkpoint semantics do not match production persistence | False restore guarantees and stale derived memories |
| P1 | Async ownership and synchronous adapter I/O are inconsistent | Event-loop stalls, lost work, and shutdown races |
| P1 | Persisted schemas and model/version metadata are incomplete | Weak audit, future V2 schema evolution, and re-indexing support |
| P2 | Public documentation and tests overstate behavior | Misleading integration guidance and hidden regressions |

### Finding Disposition Under the Clean V2 Decision

| Findings | V2 disposition |
|---|---|
| F-01 through F-04 | Do not port the V1 graph mutation model; implement typed extraction, entity identity, independently identified claims, reversible resolution, and provenance-preserving traversal |
| F-05 and F-06 | Replace ad hoc V1 consolidation with an idempotent, journaled V2 derivation job while preserving the supported entry point and report fields |
| F-07 through F-09 | Preserve the context/session façade, but bind exact requests to payloads and establish new V2 state and timeline semantics from the first turn |
| F-10 and F-11 | Build a new canonical ledger and lifecycle projections; do not convert V1 collections or stage state |
| F-12 through F-14 | Implement a new retrieval, fusion, selection, and feedback pipeline; V1 scores, hit counts, and ranking parity are irrelevant |
| F-15 through F-19 | Use strict internal ports, models, jobs, and adapters behind compatibility DTOs; V1 implementation modules and persisted schemas are not carried forward |
| F-20 through F-23 | Require source authority, epistemic confidence, trust, scope, authorization, and ingestion controls on every new V2 record; do not accommodate unscoped V1 records |
| F-24 | Implement measured evidence-bundle selection with a hard fit guarantee while preserving the existing high-level formatting call surface |
| F-25 | Freeze declared public compatibility and reconcile de facto consumers; do not remove required exports merely to make the V2 internals cleaner |
| F-26 | Create independent V2 quality, security, recovery, and isolation evidence; V1 greenness and output parity are not release gates |

## Detailed V1 Findings and V2 Requirements

Each subsection first records observed V1 behavior. Its concluding direction is
a V2 design or acceptance requirement unless it explicitly discusses the
compatibility façade. None of these findings requires modification or migration
of V1 persisted state.

### F-01 — Extracted Relationship Identity Is Broken

The extraction prompt tells the model that relationship `source_id` and
`target_id` values refer to the IDs in the extracted entity list:

- `packages/friday-memory/src/friday_memory/context/extractor.py:109`

During storage, each entity is instead assigned a new UUID. The model-provided
entity ID is not retained in a local mapping:

- `packages/friday-memory/src/friday_memory/context/extractor.py:504`

Relationship endpoints are then read as labels and passed to
`find_or_create_node`:

- `packages/friday-memory/src/friday_memory/context/extractor.py:548`

For example, an entity such as:

```json
{"id": "python", "label": "Python", "type": "technology"}
```

may create a UUID-backed node labelled `Python`, while a relationship using
`"source_id": "python"` can create another placeholder node labelled `python`.

This corrupts the intended relationship topology. Memory V2 extraction must use
a typed result, a local-entity-ID to committed-node-ID map, explicit
dangling-endpoint rejection, and an end-to-end acceptance test covering the
complete LLM-result-to-claim path.

### F-02 — The Graph Cannot Preserve Multiple Claims Between the Same Nodes

`ElementXGraphStore` uses `networkx.DiGraph`:

- `packages/friday-memory/src/friday_memory/adapters/graph.py:93`

A `DiGraph` supports only one edge for a given source-target pair. A second
relationship replaces the first. The test suite acknowledges and accepts this
behavior:

- `packages/friday-memory/tests_memory/test_adapters/test_graph.py:396`

The package therefore cannot faithfully represent that one person both
created, manages, and works on the same project. V2 relation identity must
include the relation or, preferably, a stable claim ID. V2 should use a claim
store in which every assertion has its own identity, evidence, status, and
revision history rather than treating a `MultiDiGraph` conversion as a V1 data
migration strategy.

### F-03 — Graph Integrity, Direction, and Provenance Are Not Preserved

`add_edge` does not verify that both endpoints exist. NetworkX can therefore
create bare nodes without the required graph-node schema or provenance.

Incoming traversal also records the current node as `from_node` even though the
actual edge is predecessor-to-current:

- `packages/friday-memory/src/friday_memory/adapters/graph.py:620`

`MemoryController` reconstructs a `GraphEdge` using this reversed direction and
replaces stored provenance with fabricated `graph_traversal` provenance:

- `packages/friday-memory/src/friday_memory/controller/memory_controller.py:1395`

This can turn a correct stored fact into a false prompt fact and removes the
evidence needed to explain where the relationship came from.

V2 graph reads must return typed claim records with their original orientation,
identity, properties, and provenance. Claim creation must reject missing
endpoints instead of relying on implicit graph-backend node creation.

### F-04 — Entity Merge Is Destructive and Lossy

`merge_nodes` redirects edges through the same single-edge `DiGraph`, so
redirected relationships can overwrite existing relationships. It copies a
secondary top-level field only if the primary field is absent or `None`:

- `packages/friday-memory/src/friday_memory/adapters/graph.py:804`

Fields such as `properties`, provenance, and source-memory IDs normally already
exist on the primary node, so secondary evidence is not unioned. Consolidation
can therefore delete facts and lineage.

Fuzzy entity resolution based primarily on label similarity is also unsafe for
different people or concepts that share a name. V2 entity resolution should
first create reversible alias or `same_as` proposals. Destructive V2
consolidation must require strong evidence, explicit merge policy, complete
property and provenance union, redirects, and rollback support.

### F-05 — Consolidation Omits Assistant Responses

`InteractionTurn` defines `assistant_message`:

- `packages/friday-memory/src/friday_memory/models/session.py:93`

The consolidator reads `assistant_response`:

- `packages/friday-memory/src/friday_memory/context/consolidator.py:373`

Consequently, consolidation summaries omit assistant explanations, decisions,
recommendations, and commitments. Existing tests create turns with
`assistant_message` but do not inspect the prompt passed to the summarizer.

This is a direct data-loss defect. V2 must use the canonical assistant field and
include a focused acceptance test proving that assistant content reaches
consolidation.

### F-06 — Consolidation Finalizes Incomplete or Failed Work

The consolidation workflow catches entity-deduplication and summarization
errors, but then marks all source turns consolidated:

- `packages/friday-memory/src/friday_memory/context/consolidator.py:179`

Additional inconsistencies include:

- `resolve_conflict` exists but is not called during `consolidate`;
- `conflicts_resolved` always remains zero;
- `nodes_created` actually counts summaries, not graph nodes;
- summary provenance identifies the session rather than the exact source turns;
- batch failures are logged but not consistently returned to the caller;
- random summary identities make retries capable of producing duplicates; and
- messages are silently truncated to 500 characters before summarization.

V2 consolidation must be a staged and idempotent job. Source turns may be marked
complete only after every required batch result has been committed and verified.
Derived records must carry their source-turn IDs and deterministic operation
identities.

### F-07 — Prompt Formatting Does Not Have a Complete Request Contract

The core `ContextEngineeringInterface.format_prompt` accepts only the system
prompt and context payload:

- `packages/friday-core/src/friday_core/interfaces/context.py:161`

The ordinary agent path calls it without the current user query:

- `packages/friday-agent/src/friday_agent/repl_base.py:73`

The concrete assembler added an optional `user_query`, but when it is absent it
derives the query from the most recent completed history turn:

- `packages/friday-memory/src/friday_memory/context/assembler.py:1707`

The agent then appends the actual current input as another user message:

- `packages/friday-agent/src/friday_agent/repl_base.py:78`

This can produce a stale user trigger followed by the real query.

Session state is similarly fragile. Formatting tries to recover the session ID
from `payload.debug_info`, but `MemoryController.recall` does not place the
session ID there. Scoped variables and active goals therefore may not reach the
prompt.

The V2 engine must use a typed context request carrying the exact query, session,
user, agent, namespace, state, strategy, trust policy, and budget. The existing
public formatting signature can remain by binding that request to the returned
payload inside the compatibility façade. Required request identity must never
be inferred from prior history or debug metadata.

### F-08 — Session-State Scope Claims Exceed the Implementation

`ContextAssembler` stores `SessionState` in an in-memory dictionary and notes
that production persistence is not implemented:

- `packages/friday-memory/src/friday_memory/context/assembler.py:104`

The `user:`, `app:`, and `session:` prefixes enforce only naming. They do not
provide different persistence lifetimes, tenant isolation, authorization, or
backing stores. Documentation nevertheless describes user variables as
persistent across sessions.

V2 must represent user profile, session working state, and application
configuration as separate typed domains with separate ownership and retention
rules. Application configuration must not be mutable through ordinary memory
content.

### F-09 — Checkpoint Restore Is Not a Coherent Memory Rewind

`restore_checkpoint` calls the episodic rewind operation, ignores its result,
and updates only the session turn count:

- `packages/friday-memory/src/friday_memory/context/assembler.py:350`

The production transcript-backed episodic adapter cannot rewind because the
transcript is append-only:

- `packages/friday-core/src/friday_core/interfaces/transcript.py:415`

Even if an in-memory episodic store rewinds successfully, graph claims, vector
insights, summaries, goals, scoped variables, and lifecycle records derived
from later turns remain active.

V2 must define checkpoint semantics over new V2 state. The recommended model is
an immutable transcript or episode ledger with a new timeline branch or
superseding session cursor. Every derived memory must carry source-turn and
timeline identity so retrieval can exclude records outside the active branch.
No V1 transcript history needs to be imported to establish this invariant.

### F-10 — There Is No Canonical Memory Record or Source of Truth

The episodic, vector, and graph stores are independently mutated. There is no
canonical `MemoryRecord` or `ClaimRecord` connecting the three projections by a
stable record ID, revision, transaction, and evidence set.

Examples of the resulting complexity include:

- extraction stores graph and vector artifacts through separate calls and
  catches per-item failures;
- graph provenance does not consistently link to the corresponding vector
  memory identity;
- lifecycle promotion and demotion move records through multi-step operations;
- consolidation can alter graph state and vector summaries independently; and
- correction, erasure, replay, schema evolution, and index rebuild do not share a
  single authoritative version history.

A durable immutable memory or claim ledger must be the canonical V2 store.
Episodic, vector, graph, and lifecycle representations must be rebuildable V2
projections updated through idempotent jobs or an outbox.

### F-11 — Lifecycle Transitions Are Not Uniformly Transactional

Promotion has a pending state and recovery routine, but demotion and
reactivation do not have equivalent journals. Each transition re-embeds text,
adds it to another collection, and deletes the original in separate operations:

- `packages/friday-memory/src/friday_memory/retrieval/collection_manager.py:434`

A crash can leave duplicates or ambiguous stage state. Re-embedding also makes
stage movement depend on the currently configured embedding model and can cause
representation drift.

Default short-term IDs use a second-resolution timestamp plus a list index:

- `packages/friday-memory/src/friday_memory/retrieval/collection_manager.py:306`

Two calls in the same second can generate the same IDs.

V2 transitions need stable UUID or content-addressed IDs, retained embedding and
embedding-version metadata, and a common journal/outbox contract. V2 is free to
use a single collection with an indexed lifecycle stage or another projection
layout because no V1 collection topology must be preserved.

### F-12 — Retrieval Ranking and Fusion Are Inconsistent

Short-term and long-term collections are queried independently. The controller
then puts all short-term results before long-term results rather than applying a
global fusion and rank:

- `packages/friday-memory/src/friday_memory/controller/memory_controller.py:1456`

Consequences include:

- a request for `n` results can yield up to `2n`;
- lower-quality short-term results can precede stronger long-term matches;
- duplicate records can appear during a lifecycle transition;
- long-term inclusion scoring is applied inconsistently;
- static similarity thresholds are not calibrated per embedding model or data
  domain; and
- the adapter advertises rerank and hybrid parameters that are not implemented
  consistently.

The V2 retrieval pipeline must not inherit this concatenation behavior. It
should define query decomposition, lexical and semantic candidates, calibrated
rank fusion, reranking, diversity selection, source and trust filters, temporal
resolution, a global result limit, and explicit abstention behavior.

### F-13 — Graph Path Scoring Does Not Control Returned Context

`_retrieve_graph_with_scoring` calculates `scored_paths` but returns the
original unfiltered entities and facts:

- `packages/friday-memory/src/friday_memory/controller/memory_controller.py:1564`

The scores are used primarily for a diagnostic count. The stated path-filtering
behavior therefore does not determine which graph context reaches the model.

In addition, extraction precomputes edge embeddings but not node embeddings,
while the graph scorer assigns substantial weight to node similarity. Default
thresholds can therefore reject most scored paths even though the unfiltered
paths continue downstream.

V2 graph scoring must produce the actual selected evidence bundles, including
their entities, claim, original provenance, score, and selection explanation.

### F-14 — Retrieval Reinforcement Measures Exposure, Not Usefulness

Vector access events are recorded immediately for retrieved candidates, before
passage routing, relevance filtering, budget pruning, rendering, citation, or
successful use. Graph fuzzy matches are similarly touched before final
selection:

- `packages/friday-memory/src/friday_memory/controller/memory_controller.py:1383`
- `packages/friday-memory/src/friday_memory/controller/memory_controller.py:1494`

This creates a popularity feedback loop: records that happen to be retrieved
become more important and are therefore retrieved more often, even if they are
never shown or are repeatedly unhelpful.

V2 should distinguish at least:

- candidate retrieved;
- selected by the context engine;
- rendered into the prompt;
- cited or used in the response;
- user confirmed;
- user corrected or rejected; and
- associated with a successful task outcome.

Only stronger usefulness signals should materially influence V2 long-term
value. V1 access counts do not need to be imported.

### F-15 — Controller and Adapter Contracts Are Incomplete

`MemoryController` calls graph methods such as `get_all_nodes`,
`get_edges_for_nodes`, `get_node_labels`, `get_nodes_by_ids`, and
`record_node_access`, but these are not declared by the core
`GraphStoreAdapter` contract.

The controller also accesses the collection manager's private embedding
function. Broad mypy suppression hides these mismatches.

`MemoryController` is 2,236 lines and owns storage, retrieval, priming,
relationship formatting, transcript conversion, session counters, background
work, lifecycle integration, and other concerns. `ContextAssembler` and
`PromptArchitect` are similarly oversized.

Recommended explicit ports include:

- `EpisodeRepository`;
- `MemoryLedger`;
- `ClaimRepository` or `ClaimGraph`;
- `SemanticIndex`;
- `EmbeddingProvider`;
- `RetrievalPipeline`;
- `ContextSelector`;
- `MemoryJobQueue`; and
- `MemoryPolicy`.

For Memory V2, the existing public `MemoryController` should become a façade
over these ports. Its public method names and supported return fields can remain
stable even though the V1 implementation and persisted representations are not
retained.

### F-16 — Vector and Graph Adapters Can Block the Event Loop

The Chroma adapter calls synchronous collection operations directly from async
methods. NetworkX graph persistence serializes the graph synchronously, often
on each mutation or access update while the async graph lock is held.

Some graph reads do not consistently use the lock, while persistence is
proportional to the full graph size. This will become increasingly expensive as
the graph grows.

V2 should either expose synchronous adapter contracts and offload them at the
orchestration boundary, or consistently run blocking adapter work in controlled
executors. It may select a different transactional graph or claim backend
without preserving NetworkX persistence.

`SimpleVectorStore.add_documents` also uses `zip(..., strict=False)`, silently
truncating mismatched texts, embeddings, metadata, or IDs:

- `packages/friday-memory/src/friday_memory/adapters/simple_vector.py:113`

V2 must explicitly validate cardinality, unique IDs, and embedding dimensions
before mutation.

### F-17 — Background Work Lacks One Durable Ownership Model

The package uses bare `asyncio.create_task` calls for extraction, access
recording, factor recalculation, compaction, maintenance, and tool-output
ingestion. Several paths do not provide durable job identity, completion
tracking, retry state, admission control, backpressure, or a shutdown drain
contract.

This creates lost-work and race risks and competes with foreground inference.
The observed interaction between foreground responses, extraction, and memory
maintenance makes shared LLM scheduling especially important.

A common V2 background-work coordinator should provide:

- durable job identity and state;
- idempotency keys;
- foreground and background priority classes;
- concurrency and resource limits;
- retry and dead-letter policy;
- cancellation and shutdown drain;
- restart reconciliation; and
- structured diagnostics.

### F-18 — Error Handling Can Turn Backend Failure Into “No Memory”

`MemoryController.recall` gathers store operations with
`return_exceptions=True` and converts failures to empty results without adding
the underlying exceptions to the returned diagnostics:

- `packages/friday-memory/src/friday_memory/controller/memory_controller.py:522`

Other recent-insight, summary, graph-deserialization, and extraction paths also
catch broad exceptions and return empty or partial results.

The caller cannot distinguish:

- there was no relevant memory;
- a memory store was unavailable;
- data failed schema validation;
- an index was incompatible; or
- extraction partially committed.

V2 recall must expose typed health or degradation information per source.
Compatibility calls can retain `ContextPayload` while adding optional health
fields or a typed V2 result. Workflows that require memory correctness must be
able to fail or abstain instead of silently continuing without memory.

### F-19 — Persisted Schemas, Versions, and Time Policy Are Inconsistent

There are two `MemoryStage` enums: one in graph models and one in lifecycle
models. The graph copy exists to avoid a circular import, demonstrating a
boundary problem.

Most domain models do not use strict `extra="forbid"` configuration or carry a
persisted schema version. Graph loading silently skips invalid stored records in
some paths, making corruption or schema-version incompatibility look like absent
memory.

Normal memory records also lack consistent metadata for:

- embedding model and dimension;
- extraction model;
- extraction prompt version;
- extraction schema version;
- index version; and
- schema-evolution state.

The package still uses many naive `datetime.now()` calls. Prior lifecycle work
added non-mutating normalization for mixed aware and naive timestamps, but the
creation policy remains inconsistent.

Persisted V2 models should be strict, schema-versioned, evolution-aware, and use
UTC-aware timestamps at their boundaries. This requirement supports future V2
schema changes; it does not create an obligation to migrate Memory V1 records.

### F-20 — Provenance Does Not Yet Provide a Sufficient Truth Model

Current provenance provides source ID, source type, author, confidence,
creation time, and parent IDs. This is a useful start, but it does not reliably
capture:

- exact source quote or span;
- source content hash and version;
- valid time versus recorded time;
- extraction model, prompt, and schema;
- evidence sets for a claim;
- negation, modality, or uncertainty type;
- contradiction and supersession status;
- user correction history; or
- the distinction among observation, claim, inference, preference,
  instruction, decision, and verified fact.

`create_user_provenance` assigns confidence `1.0` because user input is
described as always trusted:

- `packages/friday-memory/src/friday_memory/models/graph.py:345`

Source authenticity and claim truth are different concepts. A user is the
authoritative source for their stated preference, but not necessarily for an
external factual claim. V2 must represent source authority separately from
epistemic confidence.

### F-21 — Tool and Document Ingestion Lacks a Strong Trust Boundary

Unknown tools default to `ON_SUCCESS`, and file-reading tools are configured for
automatic ingestion:

- `packages/friday-memory/src/friday_memory/ingestion/tool_ingester.py:67`

Security metadata is flattened and retained, but normal retrieval eligibility
does not use it to quarantine risky tool, web, or file content. Retrieved text
is placed into a `Relevant Context` section without a strong untrusted-data
delimiter or instruction-versus-data distinction:

- `packages/friday-memory/src/friday_memory/context/layout.py:742`

This permits durable prompt injection or memory poisoning. File reads can also
persist secrets, credentials, personal information, or source that was intended
only for one task.

Required V2 controls include:

- source trust and taint classification;
- secret and PII detection or redaction;
- quarantine and verification state;
- explicit consent and retention policy;
- source-scoped access control;
- safe prompt rendering of untrusted content;
- delete and correction propagation; and
- poisoning and exfiltration tests.

### F-22 — Document Ingestion Is Fragmented and Not Version-Aware

`DocumentIngestionPipeline` uses character-oriented chunking and assigns a new
random document ID on every ingestion:

- `packages/friday-memory/src/friday_memory/ingestion/pipeline.py:84`

There is no stable source hash, document version, replacement, tombstone, or
update contract. Re-ingesting the same source naturally creates duplicates.

A separate `SemanticChunker` exists but is not the public document pipeline.
Despite its name, its logic is structural and heuristic. Some configuration
fields and source offsets are not fully connected to output metadata.

`LargeFileProcessor` contains additional defects:

- its existing-storage check uses an incompatible vector return shape;
- the error is caught, making deduplication ineffective;
- it fabricates `insight_N` return IDs instead of returning committed IDs; and
- code processing imports `friday_tools.filesystem.code_chunker` at runtime,
  although `friday-memory` does not declare `friday-tools` as a dependency.

`friday-tools` also imports `friday-memory`, producing hidden circular package
coupling.

V2 needs one ingestion contract supporting parsers, chunk strategies, stable
source and version identities, exact offsets, content hashes, ACL and trust
metadata, update and deletion semantics, and actual committed record IDs. These
identities begin with V2 ingestion; no V1 document IDs need to be reconciled.
Shared code chunking should live in a neutral package or be injected through an
interface.

### F-23 — Multi-Agent Memory Is Not Isolation-Safe

This is a stop-ship area if multi-agent memory is expected to provide a
production security boundary.

`MultiAgentMemoryController.recall` retrieves globally and filters afterward:

- `packages/friday-memory/src/friday_memory/multi_agent/controller.py:54`

The post-filter covers only passages, entities, and facts. It does not filter
history, prior history, insights, summaries, or recent-memory strings:

- `packages/friday-memory/src/friday_memory/multi_agent/controller.py:148`

Additional concerns include:

- `NamespacePolicyEngine.can_read` is not called by recall;
- `set_namespace` freely rebuilds the policy around a caller-selected
  namespace;
- caller metadata is expanded after protected namespace, visibility, and agent
  fields and can overwrite them;
- shared-write capability validation checks time but not the capability's
  session, run, issuer, signature, revocation, or use count; and
- shared promotion proceeds without arbitration if no arbitrator was set.

V2 authorization predicates must be pushed into every underlying query. V2
records without explicit scope must fail closed. Post-retrieval filtering is
neither an adequate disclosure boundary nor an efficient implementation, and no
unscoped V1 records need to be accommodated.

### F-24 — Context Budgeting Does Not Match Its Documented Algorithm

Guides describe dynamic-programming 0/1 knapsack selection, but
`ContextAssembler._apply_budget` implements a staged pruning cascade:

- implementation:
  `packages/friday-memory/src/friday_memory/context/assembler.py:633`
- documentation: `docs/guides/04-adaptive-memory.md:1000`

The cascade drops whole categories in a fixed order and then applies fixed
counts and thresholds. It does not optimize value per token, coverage,
diversity, trust, or evidence dependencies. Entity and relationship context can
also be split into incoherent fragments.

The token estimator does not treat every rendered component uniformly, and the
formatting stage can still report that the final prompt exceeds budget rather
than guaranteeing fit.

V2 context selection must operate on atomic evidence bundles with measured
token cost, relevance, importance, recency, trust, diversity, and dependency
constraints. It must either guarantee fit or return an explicit inability to
fit required context.

### F-25 — Documentation and Public API Surface Need Reconciliation

The package README is too small to describe the actual architecture. The
developer guide contains stale examples and claims, including:

- `MemoryController` construction without the now-required collection manager;
- older `MemoryExtractor` construction;
- references to nonexistent private assembler attributes;
- persistent scoped-variable claims despite in-memory implementation;
- incomplete package/module diagrams; and
- knapsack claims that do not match current code.

The top-level package also exports many internal lifecycle, maintenance,
recovery, and mutation types, creating a wide and unstable public surface.

Memory V2 must first inventory which exports are actually consumed and designate
the initial supported compatibility surface. That surface remains available for
the V2 cutover. Unused or accidental exports may be classified as unsupported,
but removing an actively consumed symbol would contradict the locked API goal
unless coordinated with the affected framework consumer. V2 should use maturity
labels for experimental additions, publish an as-built architecture, and test
executable documentation examples.

### F-26 — Memory Quality Evaluation Is Largely Missing

The current testing note at `docs/reference/testing/testing-memory.md` is mainly
an unevaluated checklist. Existing benchmarks emphasize synthetic latency and
component behavior rather than whether memory improves answer quality.

Memory V2 needs a repeatable evaluation corpus and metrics for:

- retrieval recall@k and precision@k;
- MRR and nDCG;
- entity and relationship extraction F1;
- temporal and contradiction accuracy;
- context precision and token efficiency;
- answer faithfulness to retrieved evidence;
- preference, decision, commitment, and open-loop recall;
- summary drift after repeated consolidation;
- correction and supersession propagation;
- cross-user and cross-agent isolation;
- prompt-injection and memory-poisoning resistance;
- erasure completeness across projections, journals, and backups;
- recovery and projection-rebuild correctness; and
- latency and resource use at realistic memory sizes.

Replay of real, redacted transcripts may be used as isolated evaluation fixtures
to measure V2 quality. Such fixtures are not production-state migration, must
not be loaded into an active V2 store, and do not make exact V1 output parity an
acceptance criterion. Synthetic and adversarial corpora remain required so V2
can be evaluated independently of V1 data.

## Capabilities to Add or Strengthen for Context Engineering

These are V2 capabilities. Their IDs, evidence, revisions, retention state, and
audit history begin in the V2 ledger. None requires reconstructing equivalent
state from V1 stores.

### A Typed Memory Taxonomy

The subsystem should explicitly distinguish:

- episodic events and bounded episodes;
- semantic claims and verified facts;
- user preferences and profile attributes;
- decisions and commitments;
- goals, open loops, and unresolved questions;
- constraints and negative instructions;
- procedures, skills, and successful examples;
- workspace and task state;
- tool and artifact evidence;
- corrections, disputes, and forgetting requests; and
- summaries and other derived representations.

Each category needs its own eligibility, retention, confidence, correction, and
prompt-rendering policy.

### Bi-Temporal and Revision-Aware Claims

Claims should distinguish when an assertion was true from when Friday learned
it. A claim should support:

- `valid_from` and `valid_to`;
- `recorded_at`;
- `superseded_by`;
- contradiction links;
- supporting and opposing evidence;
- confidence and verification status; and
- reversible correction history.

This is necessary for preferences, employment, project state, schedules,
versions, and other changing facts.

### Evidence-First Context Output

Every selected memory item should be able to explain:

- what it claims;
- where it came from;
- when it was observed and valid;
- whether it is trusted, inferred, disputed, or stale;
- why it was selected for this query;
- how much of the token budget it consumed; and
- what other records it depends on.

Contradictions should be rendered explicitly rather than silently collapsed.
Untrusted source text must be clearly delimited as data rather than
instructions.

### User Correction, Inspection, and Forgetting

A strong personal-memory system should support:

- listing memories by source, type, time, and confidence;
- explaining why a memory was recalled;
- correcting a claim without destroying its audit trail;
- pinning or protecting a verified preference or constraint;
- disputing or quarantining a claim;
- forgetting by source, scope, or record;
- proving propagation of deletion to indexes and projections; and
- distinguishing transcript retention from active-recall eligibility.

These inspection, correction, forgetting, and erasure guarantees apply to V2
records and V2-derived backups or projections. They do not imply that V2 can
inspect, correct, or erase V1 state.

### Retrieval Feedback Based on Outcomes

The system should learn from user confirmation, correction, citation, and task
outcomes rather than candidate retrieval frequency. Evaluation should include
counterfactual tests so already-popular memories do not crowd out newer or less
frequently retrieved but more relevant evidence.

## Recommended Target Architecture

```text
Existing Agent Framework consumers
       |
       v
Preserved friday_memory public façade
  MemoryController | ContextAssembler | existing supported models
       |
       v
Memory V2 engine
       |
       +-- Write path
       |     Sources
       |       transcripts | documents | tools | user edits | observations
       |          |
       |          v
       |     validation | trust | redaction | source versioning
       |          |
       |          v
       |     Immutable Memory / Claim Ledger
       |       - stable record and revision IDs
       |       - tenant/user/workspace/session/agent/timeline scope
       |       - memory type and lifecycle state
       |       - evidence and provenance
       |       - valid time and recorded time
       |       - trust, confidence, verification, correction, retention
       |
       +-- Projection and read path
             Immutable Memory / Claim Ledger
                    |
                    +--------------+-------------+---------------+
                    v              v             v               v
              Episodic view  Semantic index  Claim graph  Lifecycle view
                    |              |             |               |
                    +--------------+-------------+---------------+
                                           |
                                           v
                                  Retrieval pipeline
                    query analysis -> policy filtering -> fusion
                    -> reranking -> diversity -> evidence bundles
                                           |
                                           v
                                    Context selector
                         measured costs and hard budget guarantee
                                           |
                                           v
                                    Safe prompt renderer
                        citations, trust labels, instruction isolation
```

Vector and graph stores become disposable, rebuildable indexes rather than
independent authorities. A durable outbox or job ledger coordinates projection
updates and recovery.

The façade preserves the existing supported call surface while translating
those calls directly into V2 records and operations. It does not translate V1
persisted data. Terms such as `GraphNode`, `GraphEdge`, `ContextPayload`, or
`store_insight` may remain at the public boundary while mapping to richer V2
claim, evidence, retrieval, and projection models internally.

Memory V2 should initialize a new ledger and new projections. It should not
perform startup discovery of V1 collections or files, attempt opportunistic
imports, maintain dual writes, or fall back to V1 reads. This keeps the V2
invariants enforceable from the first committed record.

The `Sources` lane in the diagram means events observed or content explicitly
ingested after V2 starts, plus isolated test fixtures. It does not mean that V2
scans existing transcripts, documents, vector collections, or graph files to
reconstruct prior memory.

## Recommended Sequencing

The phases below construct Memory V2. They are not a plan to repair V1 storage
in place, and they do not include V1-to-V2 data migration.

### Phase 0 — Public Contract and Clean-State Boundary

1. Inventory the supported public and de facto Agent Framework API.
2. Freeze source-compatibility expectations for imports, call signatures,
   return fields, exceptions, and lifecycle or maintenance entry points.
3. Inventory configuration keys and define how existing configuration maps to
   an isolated V2 root without opening V1 persistence.
4. Identify defective behaviors that will intentionally change.
5. Define the fresh V2 storage root, schema version, and bootstrap behavior.
6. Prohibit automatic V1 discovery, import, mutation, deletion, dual read, and
   dual write.
7. Define compatibility façades and projection adapters for framework consumers
   that currently use concrete memory classes or properties.
8. Define automated evidence proving that V2 startup and maintenance do not
   access sentinel V1 paths.

### Phase 1 — Canonical V2 and Correctness Invariants

1. Implement typed extraction endpoint mapping and reject dangling
   relationships.
2. Represent multiple claims between the same entities while preserving
   direction and original provenance.
3. Include canonical assistant content in consolidation and finalize only
   verified batches.
4. Bind the exact query and session state through the preserved formatting
   interface.
5. Define honest checkpoint behavior over new V2 transcript or episode state.
6. Keep multi-agent mode contained until namespace isolation is enforced at
   query time.
7. Add end-to-end regression tests for each defect.
8. Define versioned `MemoryRecord`, `ClaimRecord`, evidence, scope, trust, and
   revision models.
9. Establish the authoritative ledger and projection identities.
10. Introduce explicit typed repository and pipeline ports.
11. Define UTC, future V2 schema evolution, embedding-version, and deletion
    policy.
12. Make extraction and consolidation staged and idempotent.

### Phase 2 — Retrieval and Context Selection

1. Implement query analysis and typed retrieval plans.
2. Add lexical and semantic candidate generation with calibrated fusion.
3. Add reranking, diversity, temporal reasoning, and contradiction handling.
4. Replace retrieval-based reinforcement with selection/use/outcome feedback.
5. Select atomic evidence bundles under a hard token budget.
6. Render source, trust, time, confidence, and selection explanations.

### Phase 3 — Governance and Operations

1. Add durable background job ownership and LLM resource scheduling.
2. Push scope and authorization into every store query.
3. Add trust, quarantine, PII/secret, retention, consent, and erasure controls.
4. Add projection reconciliation, future V2 schema evolution, index rebuild,
   and degraded-health reporting.
5. Complete multi-agent capability, arbitration, and promotion hardening.
6. Implement V2-only backup, restore, reorganization, rollback, and recovery
   bundles with aggregate verification.
7. Make every maintenance and inspection command verify the V2 engine, schema,
   and resolved root before operating.

### Phase 4 — Evaluation and Documentation

1. Build the memory-quality and security evaluation corpus.
2. Add realistic scale and recovery benchmarks.
3. Reconcile all documentation with as-built behavior.
4. Document and freeze the supported compatibility surface; do not remove
   actively consumed exports during initial V2 cutover.
5. Remove blanket mypy suppression incrementally, beginning with controller,
   context, lifecycle, and maintenance boundaries.
6. Verify that supported Agent Framework consumers operate through the V2
   façade without requiring access to V1 persisted state.

### Phase 5 — Framework Integration and Clean Cutover

1. Validate the preserved public contract against every active Agent Framework
   consumer, including concrete and de facto dependencies discovered in Phase
   0.
2. Run integration and UAT only against temporary or explicitly designated V2
   roots, never active V1 data.
3. Prove that startup, recall, extraction, consolidation, maintenance,
   reorganization, backup, restore, and shutdown leave sentinel V1 paths
   unchanged.
4. Select V2 through an explicit engine and storage-root configuration change;
   do not convert data during cutover.
5. Record that the first V2 session begins with empty V2 memory unless new
   sources are explicitly ingested after V2 starts.
6. Preserve V1 state after cutover until a separate archival or deletion action
   is authorized.
7. Keep deployment rollback limited to engine selection and V2 artifacts; do
   not attempt reverse migration into V1.

## V1 Baseline Validation Evidence

The following checks were run during the original V1 review. They describe the
reviewed baseline and help identify public contracts and coverage gaps. They are
not Memory V2 implementation or release evidence:

```text
uv run pytest packages/friday-memory/tests_memory -q
678 passed, 1 skipped

uv run ruff check packages/friday-memory/src packages/friday-memory/tests_memory
All checks passed

uv run mypy packages/friday-memory/src/friday_memory
Success: no issues found in 71 source files
```

The mypy result must be interpreted together with the 66 source files using
`# mypy: ignore-errors`. The successful command does not validate the suppressed
controller, context, lifecycle, maintenance, and adapter contracts.

The test result demonstrates strong component-level coverage but not complete
semantic correctness. Known gaps include:

- no end-to-end extraction relationship identity test;
- a graph test that accepts relation replacement;
- no assertion that assistant content reaches consolidation prompts;
- checkpoint tests centered on rewind-capable in-memory behavior;
- incomplete multi-agent payload-isolation coverage; and
- no comprehensive retrieval-quality, poisoning, erasure, or summary-drift
  evaluation.

Tests that encode defective V1 semantics, such as replacement of a second graph
relation, must not be carried into V2 as acceptance criteria. They should be
replaced by tests for the corrected invariant.

### Required V2 Evidence

Before V2 cutover, evidence must independently establish:

1. **Public contract compatibility:** supported imports, signatures, return
   fields, exceptions, configuration loading, and active consumer workflows.
2. **Clean-state isolation:** V2 initializes and operates without reading,
   translating, mutating, or deleting sentinel V1 stores or recovery artifacts.
3. **Canonical-state correctness:** committed ledger records and all projections
   reconcile under success, retry, cancellation, crash, and recovery.
4. **P0 semantic correctness:** extraction identity, graph multiplicity and
   direction, consolidation completeness, exact-query formatting, checkpoint
   semantics, and enabled namespace isolation.
5. **Security and governance:** authorization pushdown, fail-closed scope,
   untrusted-content handling, poisoning resistance, retention, correction, and
   V2 erasure propagation.
6. **Retrieval and context quality:** calibrated retrieval metrics, faithfulness,
   temporal and contradiction accuracy, token efficiency, hard budget fit, and
   outcome-based reinforcement behavior.
7. **Operational behavior:** bounded foreground/background concurrency, durable
   jobs, graceful drain, V2-only maintenance, verified backup and restore, and
   degraded-store diagnostics.
8. **Fresh-root UAT:** interactive Friday Chat operation using only an isolated
   V2 root, with V1 paths verified unchanged before and after the run.

No software tests were run while incorporating the clean-state assumption into
this document; only documentation coherence checks were performed.

## Questions for the Next Pass

1. Which de facto properties and exported models—particularly `.graph`,
   `.vector`, `.episodic`, `.collection_manager`, and maintenance result
   models—must be classified as supported for the initial V2 cutover?
2. Should near-term architecture prioritize single-user Friday Chat, or must
   server and multi-agent isolation be production-ready now?
3. For newly recorded V2 turns, should `friday-transcript` remain the
   authoritative conversation audit record while the V2 ledger owns active
   memory, or should episodes be canonical in the V2 ledger with transcript as
   a projection?
4. Should tool output, web content, and LLM-extracted claims remain quarantined
   until verified, or should selected source classes be automatically eligible?
5. What are the required privacy and retention guarantees: local-only storage,
   configurable retention, user-visible correction, hard deletion, and backup
   erasure?
6. Should the next artifact be a public-interface inventory, a target Memory V2
   architecture specification, or a formal evaluation plan?

## Overall Assessment

Friday Memory has substantial useful machinery, particularly around maintenance
and lifecycle recovery. Its supported public surface and sound design concepts
should be retained, but the internal Memory V1 storage engine should not
constrain Memory V2. Under the locked clean-state assumption, V2 should be
constructed around the canonical ledger and new projections rather than by
repairing V1 stores in place.

The recommended center of gravity is:

1. one canonical and versioned evidence-backed memory model;
2. rebuildable vector and graph projections;
3. typed and policy-aware retrieval;
4. measurable context selection under a hard budget;
5. explicit trust, correction, temporal, and isolation semantics; and
6. evaluation based on whether memory produces more accurate, faithful, and
   efficient answers.

Without those foundations, additional extraction, synthesis, graph, or
lifecycle features will increase complexity faster than they improve context
quality.

The final boundary is therefore explicit: preserve the supported Agent
Framework-facing API, construct fresh V2 persistence and semantics, leave V1
state untouched, and perform no V1-to-V2 data migration unless a separate
future decision changes this assumption.
