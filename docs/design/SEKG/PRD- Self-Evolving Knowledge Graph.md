# Product Requirements Document: Self-Evolving Knowledge Graph (SEKG)

**Project:** Friday Agent Framework  
**Module:** `packages/friday-memory`  
**Version:** 2.2  
**Status:** Approved for Design

---

## 1. Executive Summary

The **Self-Evolving Knowledge Graph (SEKG)** is the long-term semantic memory engine for Friday. It addresses key limitations of vector-only Retrieval-Augmented Generation (RAG) by representing knowledge as structured relationships rather than keyword proximity.

Unlike static knowledge graphs that require heavy up-front ontology engineering, SEKG is designed to be **autopoietic** (self-creating). It ingests unstructured conversation data, extracts triples (`subject`, `predicate`, `object`), and evolves schema definitions based on evidence quality and temporal stability.

This enables Friday to learn domain-specific terminology, organizational relationships, and multi-hop dependencies with a deterministic, auditable source of truth.

---

## 2. Problem Statement

### 2.1 Context Drift in Vector RAG

Vector similarity frequently retrieves semantically adjacent but structurally incorrect context (for example, conflating `Friday` the assistant with `Friday` the day).

### 2.2 Schema Rigidity in Traditional Ontologies

Static OWL/RDF ontology-first designs are brittle in dynamic domains. They require predefined classes and predicates that do not adapt quickly to evolving language.

### 2.3 Insufficient Multi-Hop Reasoning

Many assistant tasks require graph traversal across relationships, not nearest-neighbor matching. Current approaches struggle to answer indirect relationship questions reliably.

---

## 3. Goals and Non-Goals

### 3.1 Goals

1. Extract atomic relationship triples from unstructured interaction text.
2. Enforce logical and structural validation before persistence.
3. Evolve schema safely using evidence-backed promotion from staging to core ontology.
4. Support deterministic multi-hop reasoning over persisted relationships.
5. Maintain graph hygiene through reconciliation and reversible merge operations.
6. Preserve provenance and auditability for all graph mutations.

### 3.2 Non-Goals (Current Version)

1. Full autonomous ontology redesign without evidence thresholds.
2. Unbounded real-time deep logical reasoning on every write path.
3. Irreversible entity reconciliation operations.

---

## 4. User Stories and Acceptance Criteria

| ID | Actor | User Story | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| US.1 | System (Extraction Engine) | As the extraction engine, I want to decompose user prompts into atomic triples automatically. | Input `Chuck created Friday.` produces `(Chuck, created, Friday)` with confidence metadata and zero-shot extraction support. |
| US.2 | System (Gatekeeper) | As the gatekeeper, I want to validate new triples against baseline logic constraints before storage. | Triples violating domain/range or type constraints are rejected or flagged. Example: `(Rock, created, Friday)` is flagged if `Rock` is not typed as `Person`. |
| US.3 | System (Morphing Engine) | As the morphing engine, I want to promote recurring relationship types into core ontology based on evidence quality. | Promotion requires evidence score threshold and temporal span checks; single-turn bursts are insufficient. |
| US.4 | Assistant (Reasoning Layer) | As the reasoning layer, I want to traverse indirect relationships to answer multi-hop questions. | Query pathing works for chains like `Chuck -> founded -> Company -> employs -> Employee`. |
| US.5 | System (Reconciliation Agent) | As the reconciliation agent, I want to merge synonym nodes while preserving undo capability. | Merge operations create snapshots and support `undo_merge()` rollback. |
| US.6 | User | As a user, I want clarification prompts when facts are ambiguous. | Ambiguous statements trigger targeted disambiguation prompts before persistence. |
| US.7 | Developer | As a maintainer, I want to visualize graph evolution across sessions. | DOT/GraphViz-compatible export shows nodes/edges added or changed over time. |

---

## 5. Functional Requirements

### 5.1 Ingestion and Triple Extraction

1. SEKG must ingest conversation text from Friday runtime loops.
2. Extraction must produce candidate triples with confidence and timestamp metadata.
3. Extraction must support zero-shot operation without domain-specific pretraining.

### 5.2 Structural Validation (Gatekeeper)

1. Fast-path validation must enforce shape and type constraints in the synchronous write path.
2. Deep-path validation must run asynchronously for heavier logical checks.
3. Validation outcomes must be classified as `valid`, `invalid`, or `ambiguous`.
4. `ambiguous` outcomes must trigger clarification workflows.

### 5.3 Evidence-Based Schema Evolution

1. Candidate facts and relationship types must first enter staging.
2. Promotion to core ontology must require evidence above threshold and temporal spread.
3. Promotion logic must account for source reliability and confidence weights.

### 5.4 Reasoning and Query

1. System must support graph traversal for indirect relationship queries.
2. Natural-language reasoning entry points must map to graph query execution.

### 5.5 Reconciliation and Hygiene

1. Background reconciliation must detect likely synonym/duplicate nodes.
2. Merge actions must be snapshot-backed and reversible.
3. Reconciliation events must preserve provenance for audit.

### 5.6 Observability and Export

1. Graph mutation events must be traceable to source interactions.
2. System must support export for graph evolution visualization.

---

## 6. Logical Architecture

SEKG operates as four cooperating engines in a continuous lifecycle.

### 6.1 Universal Extraction Engine ("Triplicator")

**Responsibility:** Convert unstructured input into candidate triples.

**Flow:**

1. Ingest raw text from conversations.
2. Perform zero-shot entity/relation extraction.
3. Attach `confidence_score` and timestamps.
4. Emit candidate triples to the gatekeeper.

### 6.2 Structural Gatekeeper ("Validator")

**Responsibility:** Enforce structural integrity and logical constraints.

**Flow:**

1. Fast-path: SHACL-like structural checks for low-latency validation.
2. Deep-path: asynchronous OWL-DL reasoning for richer consistency checks.
3. Output classification:
   - `valid`: forward to staging.
   - `invalid`: reject.
   - `ambiguous`: request clarification.

### 6.3 Morphing and Discovery Engine ("Evolution Layer")

**Responsibility:** Promote stable, high-evidence relationships into core ontology.

**Evidence Model:**

- Temporal decay evidence score: `E(t) = sum(C_i * exp(-lambda * (t - t_i)))`
- `C_i`: confidence weight (for example, direct user input > passive inference)
- `lambda`: decay constant

**Promotion Conditions:**

1. `E(t)` exceeds threshold.
2. Observations span minimum elapsed duration to prevent hallucination bursts.

### 6.4 Semantic Reconciliation Agent ("Janitor")

**Responsibility:** Deduplicate and maintain graph hygiene.

**Flow:**

1. Run asynchronously in background.
2. Use embedding similarity to identify probable duplicates.
3. Apply snapshot-backed merge operations with rollback support.

---

## 7. Integration with Friday Framework

### 7.1 Package and Module Boundaries

SEKG is implemented under `friday-memory` as a semantic memory subsystem.

### 7.2 Interface Surface (Planning)

1. `ingest(text: str)` for extraction and validation pipeline entry.
2. `query(graph_query: str)` for structured retrieval.
3. `reason(question: str)` for natural-language-to-graph reasoning.

### 7.3 Storage Model

1. Persistent ontology/triple storage for long-term memory.
2. Session-optimized in-memory graph for active reasoning performance.
3. Snapshot/transaction records for reversible reconciliation.

---

## 8. Non-Functional Requirements

### 8.1 Performance

1. Fast-path validation should preserve conversational responsiveness.
2. Expensive consistency checks should be deferred to asynchronous deep-path jobs.

### 8.2 Reliability and Safety

1. Reconciliation must be reversible.
2. Evidence-based promotion must resist transient hallucination spikes.
3. Invalid and ambiguous writes must not silently pollute core ontology.

### 8.3 Explainability and Auditability

1. Answers derived from graph traversal must be provenance-traceable.
2. Graph mutation history must be exportable and reviewable.

### 8.4 Extensibility

1. Architecture should support domain adaptation without full schema resets.
2. Validation and promotion policies should be tunable without redesign.

---

## 9. Opportunities, Risks, and Difficulty

### 9.1 Opportunities

1. Domain-agnostic starting point that converges toward domain specialization through interaction.
2. Higher explainability than embedding-only retrieval.
3. Better multi-hop reasoning for complex user questions.

### 9.2 Risks

1. **Semantic pollution:** weak gatekeeper policy can admit noisy triples.
2. **Latency pressure:** excessive synchronous validation can degrade UX.
3. **Incorrect merges:** conflation of distinct entities can harm data integrity (mitigated by rollback).

### 9.3 Difficulty Assessment

1. Overall complexity: high.
2. Primary challenge: robust promotion policy design for transitioning staged facts into stable ontology.

---

## 10. Success Metrics

1. **Attribute Retrieval Precision:** target >90% for key entity-attribute lookups.
2. **Schema Convergence:** rate of new schema creation declines over sustained interaction volume.
3. **Deduplication Impact:** reconciliation reduces redundant node count materially versus raw extraction baseline.
4. **Rollback Quality:** low percentage of merges require manual rollback.

---

## 11. Open Questions

1. What are the initial threshold defaults for evidence promotion per domain profile?
2. What latency budget should be enforced for synchronous gatekeeper validation in production?
3. Which provenance fields are mandatory for compliance and replay requirements?
4. What governance process approves promotion-policy parameter changes?
