# INGEST-001 — framework-wide embedding compatibility council, round5

**Outcome: CHANGES_REQUESTED. The all-seat9.5 gate is not met.**

Candidate `06f294d779c5bc9ea3016eaffdf8efb349979ce4`; branch `feature/cmd-ingest-001`.
Reviewed REM SHA256 `2bbf54c8c987eba9b2b823c9efb6f218c4cd7058d8e0f72694ae8ed04dd12dea`.
This is document/design readiness and source feasibility, not implementation or
runtime compatibility assurance. The maintainer explicitly included consumers
not named in the REM and both unchanged configuration and replacement models
with fresh compatible memory namespaces.

| Seat | Formal outcome | Advisory score | Report |
| --- | --- | --- | --- |
| GPT-6.1 Sol | CHANGES_REQUESTED | 8.6/10 | [Raw report](sol-report.md) |
| GPT-6 Astra | BLOCKED | 8.4/10 provisional only | [Readable report](astra-report.md), [exact original](astra-report.raw.md.gz) |
| Claude Opus5.5 | CHANGES_REQUESTED | 7.2/10 | [Raw report](opus-report.md) |

Astra exceeded the current-fields-only authority inspection boundary. Its
technical observations remain useful, but no valid formal signoff or averaged
score is inferred. All three tasks are terminal. No replacement, automatic
correction loop, Gate-A execution or construction is activated.

## Consolidated technical themes

The ten raw technical finding IDs are mapped below to nine bounded themes.
Opus M3 covers three separate legacy surfaces; overlapping reports are not
counted as separate defects. Astra's procedural blocker is additional and
retains its exact original disposition.

| Theme | Missing contract/proof | Original IDs |
| --- | --- | --- |
| INGEST-EC-01 | Startup rejection logging can pre-create or mutate a vector directory | OPUS-M1 |
| INGEST-EC-02 | Active opt-in MCP snapshot ingestion is omitted from the route contract | OPUS-M2 |
| INGEST-EC-03 | Public physical backup/restore can bypass binding and overwrite a sidecar | SOL-R5-M01, OPUS-M3 |
| INGEST-EC-04 | ConsistencyAnalyzer opens SQLite and graph data outside normalized admission | SOL-R5-M02, OPUS-M3 |
| INGEST-EC-05 | Legacy synthesis can omit vectors and invoke an implicit Chroma embedder | OPUS-M3 |
| INGEST-EC-06 | Consolidation can acknowledge source turns after summary-storage refusal | SOL-R5-M03, ASTRA-R5-001 |
| INGEST-EC-07 | Lifecycle counts and tool text can report failed mutations as success | ASTRA-R5-002 |
| INGEST-EC-08 | Recall can suppress typed refusals; async graph fallback is not maintained wiring | OPUS-M4 |
| INGEST-EC-09 | Runtime ephemeral/testing profiles still construct persistent lifecycle collections | OPUS-M5 |

### INGEST-EC-01 — Startup rejection logging can pre-create or mutate a vector directory

Sources: OPUS-M1. Severity: high.

Source anchor: `packages/friday-memory/src/friday_memory/context/extraction_filter.py:32; context/extractor.py:211; packaged config.example.yaml:71/236`.

Proposed bounded disposition: Defer extractor/log resource effects until namespace admission and define the configured log destination disposition. Preserve unrelated/legacy roots; do not rewrite user YAML.

Required proof to specify: Packaged and compat-config startup/read creates no vector directory; first admitted memory use can CREATE_FRESH; refused/old roots and parent metadata unchanged.

### INGEST-EC-02 — Active opt-in MCP snapshot ingestion is omitted from the route contract

Sources: OPUS-M2. Severity: high.

Source anchor: `packages/friday-chat/src/friday_chat/memory_mcp.py:162; packages/friday-memory/src/friday_memory/ingestion/mcp.py:166; retrieval/collection_manager.py:481`.

Proposed bounded disposition: Classify the maintained MCP-to-Memory route separately from public-unwired ToolOutputIngester. Preserve the single exact snapshot/receipt protocol; freeze unsplit guard and overflow outcome rather than applying document/512 splitting blindly.

Required proof to specify: Baseline and both replacement-model cases retain exact snapshot/publication ownership, document role and metadata; token-overflow refuses before provider I/O with truthful outcome and no snapshot success.

### INGEST-EC-03 — Public physical backup/restore can bypass binding and overwrite a sidecar

Sources: SOL-R5-M01, OPUS-M3. Severity: high.

Source anchor: `packages/friday-memory/src/friday_memory/maintenance/backup.py:137,273; maintenance/reorganizer.py:148`.

Proposed bounded disposition: Give public BackupManager and Reorganizer accessors an explicit identity-aware delegation or refusal-only disposition. Preserve offline historical interpretation; no new migration or backup engine.

Required proof to specify: Public create/restore controls cover root/vector layouts, same-space/incarnation supported positive, identity-free/mismatched/tampered sidecar negatives before mkdir/copy/write; no sidecar substitution.

### INGEST-EC-04 — ConsistencyAnalyzer opens SQLite and graph data outside normalized admission

Sources: SOL-R5-M02, OPUS-M3. Severity: medium.

Source anchor: `packages/friday-memory/src/friday_memory/maintenance/analyzer.py:74,124-186`.

Proposed bounded disposition: Declare store-only admitted analysis or explicitly offline historical inspection. Use one normalized vector/graph layout; no alternative-root probing after refusal. Preserve analysis algorithms.

Required proof to specify: Matching admitted inspection works with inference unavailable; unbound/mismatched/pending state refuses before SQLite/graph opens and creates no WAL/SHM or fallback-directory effects.

### INGEST-EC-05 — Legacy synthesis can omit vectors and invoke an implicit Chroma embedder

Sources: OPUS-M3. Severity: high.

Source anchor: `packages/friday-memory/src/friday_memory/maintenance/synthesizer.py:707-742,785-795; maintenance/__main__.py:435-446`.

Proposed bounded disposition: Require failure when the selected embedder is absent or refuses; never omit embeddings to let a collection select a hidden model. Classify public legacy helpers and module read/dry-run entries without enabling disabled mutations.

Required proof to specify: Missing/failed embedder yields zero collection writes/default embedding work; guarded public and module entry dispositions are explicit and negative witnesses preserve current disabled CLI mutation behavior.

### INGEST-EC-06 — Consolidation can acknowledge source turns after summary-storage refusal

Sources: SOL-R5-M03, ASTRA-R5-001. Severity: high.

Source anchor: `packages/friday-memory/src/friday_memory/context/consolidator.py:188-207,356-370`.

Proposed bounded disposition: Explicitly cover the public-unwired consolidator, separately from ordinary extraction/compaction. Permit only guard-error propagation and successful-batch acknowledgement changes; retain scheduling, prompts and record semantics.

Required proof to specify: Overflow, mismatch and invalid-vector storage failures leave affected turns retryable and produce no success event/acknowledgement; mixed-batch and retry positives work under baseline and replacement configurations.

### INGEST-EC-07 — Lifecycle counts and tool text can report failed mutations as success

Sources: ASTRA-R5-002. Severity: medium.

Source anchor: `packages/friday-memory/src/friday_memory/lifecycle/promotion.py:372,462; packages/friday-tools/src/friday_tools/memory/lifecycle.py:34-54; base.py:30,136`.

Proposed bounded disposition: Count completed non-dry-run mutations truthfully and expose failures in public tool execution text; preserve dry-run prospective counts, partial-results policy and lifecycle thresholds/order.

Required proof to specify: Same-space success and overflow/identity/invalid-vector failures verify both structured results and ordinary tool execute text; refused mutations are not counted as successes.

### INGEST-EC-08 — Recall can suppress typed refusals; async graph fallback is not maintained wiring

Sources: OPUS-M4. Severity: high.

Source anchor: `packages/friday-memory/src/friday_memory/controller/memory_controller.py:522-527,1625,1639; retrieval/graph_scorer.py:226,335`.

Proposed bounded disposition: Name the gather/except/priming propagation points for typed embedding readiness/provenance errors, preserving other existing degradation policies. Distinguish maintained sync scoring from public-unwired async fallback; no new fallback activation is inferred.

Required proof to specify: End-to-end Chat/Runtime/agent-tool recall returns actionable typed refusal for unknown provenance and mid-session space mismatch, rather than empty context/zero-score success. Preserve ordinary missing-vector policy explicitly.

### INGEST-EC-09 — Runtime ephemeral/testing profiles still construct persistent lifecycle collections

Sources: OPUS-M5. Severity: high.

Source anchor: `packages/friday-core/src/friday_core/profiles.py:74; packages/friday-runtime/src/friday_runtime/di.py:282-300`.

Proposed bounded disposition: Freeze a FULL/VECTOR_ONLY/EPHEMERAL/TESTING open-intent and identity matrix. State whether lifecycle collections are ephemeral or explicitly requested persistent; disclose the narrow behavior delta, without profile redesign.

Required proof to specify: Actual RuntimeKernel per-profile startup and recall witnesses cover no persistent effects for an ephemeral choice, unset persistent refusal and explicit matching persistent success, with exact existing fixture exceptions.

## Controller reconciliation and disagreements

The module maintenance CLI already refuses restore and non-dry-run synthesis/prune/verify/reorganize mutation paths. Do not portray it as an active destructive bypass or re-enable it. The public BackupManager/MemorySynthesizer APIs remain affected; module backup/analyze/read/dry-run surfaces still need admission dispositions.

Sol/Astra treated MCP publication as covered or unchanged, but the controller followed memory_mcp -> adapter -> MCPMemoryIngester -> stage_mcp_snapshot -> add_to_short_term. This is active opt-in tool-output storage; the generic ToolOutputIngester route remains public-unwired. Accept OPUS-M2 as a real missing route classification.

Sol/Astra considered recall covered by global typed-refusal intent; Opus identified specific catch/gather sites and sync-only maintained graph scoring. Retain the design intent but require explicit propagation scope and end-to-end negative witnesses; do not claim public async fallback is maintained wiring.

Astra is procedurally BLOCKED; its provisional findings are not formal conformance. INGEST-EC-06 is also supported by Sol and INGEST-EC-07 was independently checked by the controller in promotion count ordering and ToolResult/execute rendering. This does not cure the blocked seat.

These findings are static source-backed risks and missing design dispositions, not executed demonstrations that the proposed implementation fails. No implementation exists for this unit and no runtime/model/store tests ran.

The existing embedding pool remains the right configuration mechanism. These
gaps concern resource timing, hidden store/embedding paths and failure delivery
downstream of shared guards. Maintaining YAML syntax and selecting a fresh data
root does not by itself prove those paths remain operational. Most consumers
can continue delegating unchanged; being unnamed does not automatically justify
editing a subsystem.

## Complete criterion matrix

All18 rows are preserved from each report. Astra's column is provisional under
BLOCKED and is not a formal PASS. PASS elsewhere means design adequacy only;
future source/installed/model evidence remains required.

| Criterion | Sol | Astra — provisional | Opus |
| --- | --- | --- | --- |
| EC-01 | PASS | Blocked procedurally | PASS |
| EC-02 | GAP | Gap | PARTIAL |
| EC-03 | PASS | Design adequate | PARTIAL |
| EC-04 | PASS | Design adequate pending signatures | PARTIAL |
| EC-05 | PASS | Design adequate | PARTIAL |
| EC-06 | PASS | Design adequate | PARTIAL |
| EC-07 | PASS | Design adequate | PARTIAL |
| EC-08 | PASS | Design adequate | PASS |
| EC-09 | GAP | Design adequate | PARTIAL |
| EC-10 | GAP | Gap | PARTIAL |
| EC-11 | GAP | Gap | PARTIAL |
| EC-12 | GAP | Design adequate | PARTIAL |
| EC-13 | PASS | Design adequate | PASS |
| EC-14 | GAP | Gap | PARTIAL |
| EC-15 | GAP | Gap | PARTIAL |
| EC-16 | GAP | Gap | PARTIAL |
| EC-17 | PASS | Design adequate; Gate-A pending | PASS (advisory A10) |
| EC-18 | PASS | Blocked | PASS |

## Advisory dispositions for a proposed revision

Except the current top-level status correction, these are recommendations to
freeze or qualify in a later document revision, not changes applied to the REM.
All15 original advisory IDs are preserved and mapped once.

| Original IDs | Topic | Disposition |
| --- | --- | --- |
| SOL-R5-A01, ASTRA-R5-A01 | Stale top-level authority summary | Fixed only in current reconciliation status; technical documents/review artifacts unchanged. |
| SOL-R5-A02, OPUS-A6 | Agent, multi-agent and MCP consumer trace rows | Carry into proposed document correction; controller-mediated unaffected behavior can be proven without local source changes. Distinguish visibility namespaces from physical embedding namespaces. |
| ASTRA-R5-A02, OPUS-A8 | Existing dimension ceiling and empty fresh collection inference | Qualify selected dimensions against the existing ceiling and specify graph-only/empty-store behavior; no speculative ceiling removal. |
| OPUS-A1 | Chat embedding.embedding_service differs from actual default-service wiring | Characterize retained baseline behavior and explicit selection semantics; do not silently change it while claiming unchanged configuration. |
| OPUS-A2 | Similarity thresholds and retrieval quality | Operational compatibility is distinct from quality/calibration under a different model. Require measured relevance/UAT evidence if a replacement is later selected; deterministic vector shape checks are insufficient. |
| OPUS-A3 | Baseline configuration catalogue and served-artifact identity | Enumerate maintained pool/non-pool/CLI/maintenance fixture families; qualify absent/placeholder revisions and mutable alias behavior or stop readiness explicitly. |
| OPUS-A4 | Real maintenance probe ordering | Admission must precede model probe/provider I/O; add the explicit no-I/O refusal witness. |
| OPUS-A5 | CLI explicit-origin bit | Trace dataclass/default/environment origin into Runtime before defaults obscure explicit selection; add DI-29 witness. |
| OPUS-A7 | MEMQ store-only operations | Add stats/records/list-ingested dispositions to the operation matrix without requiring an embedding provider to render admitted data. |
| OPUS-A9 | Telemetry compatibility | Source supports unchanged telemetry/error outcomes; no telemetry patch is justified by this review. |
| OPUS-A10 | Runtime/CLI/Agent-only counter dependencies | Freeze exact minimal/optional dependency/readiness placement at Gate-A; do not make document conversion a prerequisite of unrelated embedding consumers. |
| OPUS-A11 | Public legacy preprocessing/chunking pipeline | Classify public-unwired preprocessing explicitly; no second storage chunking authority or automatic activation. |

## Evidence, integrity and limits

All three original report hashes match. Sol/Opus readable reports preserve exact
bytes. Astra's readable copy removes only trailing empty lines for repository
whitespace; its [exact original](astra-report.raw.md.gz) is preserved losslessly
and its decompressed hash matches the announced report. Their boundary checks passed for
17,643 protected entries, six metadata records, HEAD/branch/logical index/status
and empty staging. Recorded Git/admin pairs: Sol9, Astra8, Opus14; every recorded
pair has the required guard environment and exit0. Opus's first shell setup
attempt exited127 before running anything; it earns no check credit. Astra's
isolation breach is not erased by passing integrity or administration.

The controller independently checked the reported source seams and ran the
frozen integrity helper before writing closeout metadata. [Exact hashes and
machine-readable dispositions](reconciliation.json) retain the raw reports,
command audits, boundary receipts, immutable request/helpers and compressed
protected manifest. Frozen request paths retain their original external
locations; archives do not silently rebind that request for replay.

Required board/dashboard/docs/metadata/whitespace checks passed independently in
each seat. Product tests, model calls, dependency installs, actual store effects
and installed normal/optimized behavior were not executed. Existing root
lint/collection/formatting/MAINT oracle debt remains failed and unwaived; no
whole-repository-green claim follows.

## Next gate

Review the nine bounded themes and advisory dispositions, then decide the exact
REM amendments. A changed technical document needs a newly authorized fresh
council, including a valid Astra seat, before claiming the quality gate. No
technical REM/companion change is made by this reconciliation. Gate-A effects,
construction approval, model selection, actual data reset/migration/re-embedding,
MAINT human acceptance and delivery remain separate and ungranted.
