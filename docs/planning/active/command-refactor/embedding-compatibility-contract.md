# INGEST-001 — framework embedding compatibility contract

Status: **PROPOSED normative annex to REM-CMD-INGEST-001; implementation unapproved**.
This annex incorporates the round5 technical themes and the selected high/medium
advisories. It is a contract for future construction and proof, not executed
evidence. The primary [REM](remediation/REM-CMD-INGEST-001-pdf-docx.md) retains its
format, chunking, namespace, recovery and security requirements. This annex
specializes its compatibility claims; it does not authorize product code,
dependency/model operations, reset, migration or a new subsystem architecture.

## Compatibility and model replacement

For every supported maintained flow, require a successful positive under both
scenarios, not merely parsing or a safe refusal:

- **B — baseline:** pre-change pool/catalog and maintained non-pool configuration,
  with the new optional capability fields omitted, qualified readiness and an
  admitted namespace. Existing extraction LLM selection, embedding interfaces,
  effective service/model/default/endpoint/credential/batch/cache/resilience
  choices and record semantics remain, subject only to the named exceptions below.
- **N — replacement:** explicit selection of another qualified embedding model
  using the same configuration mechanism and a fresh coherent memory namespace.
  Exercise both a different vector dimension and the same dimension with a
  different model/artifact/preparation identity. Include a smaller capacity.
  Supported extraction, storage, recall, maintenance and lifecycle operations
  must succeed with valid inputs; do not satisfy N by disabling a consumer.
- **R — refusal:** stale/foreign/unbound state, unresolved capability, invalid
  results and overflow produce the specified actionable failure before the
  prohibited effects. No swallowed error, successful no-op, lost retry eligibility,
  hidden embedder, zero-score identity mismatch or silent truncation.

Replacement means a new embedding space and fresh vector-bearing state, not
automatic deletion. The operator explicitly selects the coherent vector/graph,
configured WAL, relevant recovery/log layout. No automatic reset, import,
re-embedding, namespace repair or rewriting of user configuration is included.
Unrelated transcripts/artifacts remain governed by their existing settings.
Different service names/timeouts may share one space; separate physical memory
namespaces may use different models. Multi-agent visibility namespaces are
authorization partitions, not independent physical embedding spaces.

Intentional compatibility exceptions must be individually visible in the final
directive: fresh-store-required admission; verified model-specific preparation
and query/document role correction; explicit invalid/overflow/result refusal;
MCP overflow outcome refinement; and the legacy physical-copy restriction in
FC-03. None permits a silent model change. A formerly successful supported B/N
flow that only refuses is a failed compatibility proof unless this exact
exception list and its operator remedy cover it. Any additional exception stops
readiness for maintainer disposition.

## Baseline configuration and current identity

Gate A must catalogue these source-backed families, with sanitized immutable
fixtures and actual effective binding expectations. It must not use the two
dirty repository examples or personal stores as fixtures.

| ID | Existing configuration family | Effective selection to preserve |
| --- | --- | --- |
| B01 | Chat packaged catalog/pool templates | Memory uses `embedding_pool.default_service`; maintenance uses its explicit pool service. |
| B02 | Chat non-pool default and explicit `embedding` configuration | Existing configured model/endpoint or the existing `text-embedding-3-small` default; no automatic replacement. |
| B03 | Sanitized Chat compatibility fixture | Existing non-pool alias/endpoint and extraction selection; absent revision is not invented. |
| B04 | Runtime catalog/pool configuration | Default memory binding plus optional distinct extraction service and existing LLM selection. |
| B05 | Runtime legacy `embedding:` and service configurations | Existing default/model/endpoint and service options; same resolved guard capability. |
| B06 | CLI `FridayConfig`, direct values and environment/default paths | Existing Runtime delegation, with explicit-origin retained as described in FC-10. |
| B07 | Chat inline non-pool `maintenance.embedding` | Existing separate maintenance model/endpoint and controls; same-space checks when sharing a namespace. |
| B08 | Public Memory `MaintenanceConfig.embedding` and injected EmbeddingModel users | Existing provider interface and selected service; no Chroma default substitute. |

For each selected deployment, record the configured route, exact served identity,
counter/preparation revision, effective capacity, dimensions and qualification
source. Resolve absent or placeholder revisions using a reviewed readiness record
bound to verified serving identity, not by blessing the alias as immutable.
An inert configuration can load before qualification; B/N success requires the
qualified deployment. If a baseline family cannot be qualified, Gate A stops
with that incompatibility; it is not silently excluded or labelled supported.

Record whether current identity is established by immutable serving attestation
or a deployment whose artifact is pinned and cannot change during its admitted
lifetime. A mutable endpoint/model-name echo alone is insufficient. Where the
server can replace an alias, require a verified per-operation identity check
before provider/storage effects, or explicitly refuse that deployment. Freeze
this supported-mechanism choice in the readiness manifest. A server-side swap
with the same name/dimension must fail the qualification/refusal control; if
the deployment cannot detect it, stop rather than promise protection it lacks.

Chat currently ignores canonical `embedding.embedding_service` and chooses the
pool default in `build_framework_embedding_service`. Preserve that baseline
precedence in this unit: describe the field as a legacy no-op in catalog mode,
report the effective service and a safe ignored-hint warning when it differs.
Do not newly reject the old configuration or silently make that hint an override.
Non-pool behavior, Runtime's explicit extraction binding and maintenance's
explicit binding retain their existing semantics. The divergent-name test must
prove actual selection, not merely the YAML's appearance.

## Required consumer inventory

This is a minimum, not a closed universe. Gate A and independent review search
all maintained package source/entrypoints and follow transitive config, store,
protocol and error paths. Every newly discovered consumer receives a source-backed
disposition and exact proof. Discovery of a consumer does not itself authorize
editing it. Report uncovered necessary scope before construction.

| Consumer / current route | Contract disposition |
| --- | --- |
| LLM pool/resolver, direct query/document APIs and caches | Shared preparation/counting/result guard, unchanged caller interfaces; B01–B08 and FC-10/12. |
| Core store factories/interfaces; Memory vector/simple stores and collections | Namespace admission and identity-bearing query/vector handoff; no bare-vector or direct-client bypass. |
| Chat/Runtime extraction, stored insights/summaries and graph edges | Preserve extraction LLM and actual embedding selections; full extraction→graph/vector→recall positives. |
| Maintained sync graph scorer and semantic recall | FC-08. Missing vector is distinct from a vector with unknown/foreign identity. |
| Public async graph scorer fallback | Public-unwired; retain guarded document-role fallback API, no maintained-route or installed-wiring claim. |
| Chat compaction; public-unwired MemoryConsolidator | Preserve unsplit records. Compaction reports failures; FC-06 specializes acknowledgement for the consolidator. |
| Promotion/decay/reactivation; public lifecycle tool | FC-07, completed mutation counts and visible errors. |
| MAINT pipeline, synthesis/re-embedding, stored-vector pruning/clustering and fact checks | Shared identity/roles; FC-05/11; no order/prompt/verification redesign. |
| Recovery/mutation participant and Chat aggregate v2 | Retain primary REM's identity-preserving snapshot/rollback, strict versions and no rebind. |
| Public BackupManager/Reorganizer accessors and direct SQLite ConsistencyAnalyzer | FC-03/04; distinct from the maintained v2 recovery participant. |
| `python -m friday_memory.maintenance` | Public legacy entrypoint: backup/analyze/read/dry-run admission disposition; preserve existing disabled restore and non-dry-run mutation commands. Do not reactivate them. |
| Chat MCP tool-output snapshot→Memory route | Active opt-in per-server route, FC-02; do not confuse it with public-unwired generic ToolOutputIngester. |
| smart_read raw/derived storage; generic ToolOutputIngester | Injected/public storage contract retained, no new automatic wiring; source plan versus unsplit derived records remains explicit. |
| Public DocumentIngestionPipeline/SemanticChunker | Public-unwired legacy preprocessing; does not become a second storage chunker or override the new common plan. |
| Runtime profiles, Core factories, CLI container | FC-09/10/12. Physical persistence and explicit-origin must agree across every adapter. |
| Agent archive/extraction, recall_memory/store_fact tools | Controller/context-mediated; preserve public input/output and error reporting. Exact positive/refusal witnesses are required without a new model selector. |
| Multi-agent controller/coordinator/journal | Underlying Memory space is shared; preserve authorization visibility and honest failed/partial-commit reporting. No new transaction promise. |
| MCP publication and transcript receipts; MEMQ inspection | Preserve receipt ownership and store-only availability; FC-02/13. No embedding initialization merely to list admitted data. |
| Context assembly, passage routing, tool recommendation and ordinary tool registration | Preserve nonsemantic/LLM-only paths and lazy unavailable capability; no new document/embedding prerequisite. |
| Telemetry and Transcript package contracts | Compatible unchanged unless a concrete boundary proves otherwise. Existing zero-attempt error telemetry is sufficient; transcript-v1 classes stay unchanged. |
| Commands, MCP transports, Speech, Sandbox, Finance, Moltbook, Optimization, main/scripts | Source-backed unchanged/transitive dispositions and minimal-install/import checks; no unrelated source changes inferred. Dynamic tool imports remain a documented residual risk and installed registry witnesses cover configured supported tools. |
| Lifecycle migration.py, Chat migration/reset/reorganize compatibility stubs | Keep actual inactive/stub/disabled classifications; no migration repair, activation or integration credit. |

## Exact narrow integration requirements

**FC-01 — startup and configured rejection logging.** Defer resourceful
MemoryExtractor/rejection-handler construction until namespace admission; an
inert configuration may be constructed earlier. No `mkdir` or FileHandler under
a refused, unbound or not-yet-created vector namespace during startup or `/read`.
After successful fresh creation, a log inside that admitted namespace may open.
Qualify the configured log target in the layout manifest as belonging to the
active namespace or an independent safe log root. A stale target inside a known
legacy/foreign namespace refuses extraction readiness with an actionable remedy;
do not write there, silently redirect it or rewrite YAML. Unknown target
ownership is a readiness stop, not permission to scan stores. Selecting fresh
associated log/recovery paths is part of coherent layout selection. Retain
ordinary independent log destinations when qualified. Packaged/compat fixtures
with logs inside vector/ must allow first-use CREATE_FRESH after deferral.

**FC-02 — active MCP snapshots.** Treat `mcp_tool_snapshot` as a structured,
single exact record, exempt from document/512 chunk planning like other structured
memory records. Retain opt-in, sanitization, byte ceiling, deterministic identity,
pending/publish/discard ownership and transcript receipt protocol. It still uses
document-role shared counting/result/admission guards. A snapshot passing the
byte ceiling can exceed the embedding token cap: detect before provider I/O and
return the existing `oversized` outcome with no snapshot/receipt success.
Non-capacity readiness/identity/storage failures retain an explicit failure
outcome, never an apparently prepared snapshot. Do not split, truncate or change
the stored text/receipt to make it fit. No new MCP activation or generic automatic
ToolOutputIngester wiring is included. Exact new overflow oracle is approved only
through the final construction directive; retain all other MCP assertions.

**FC-03 — public legacy physical backups.** Choose a bounded explicit
compatibility exception: legacy BackupManager file-copy create/live restore is
not a supported backup engine for a bound namespace. Detect bound/pending state
or a bound artifact and refuse before destination directories/copies/sidecar
changes, directing callers to the maintained identity-aware Memory-v2 snapshot/
restore API. Legacy-unbound live operations remain refused by the primary REM;
offline historical manifest/checksum inspection remains available without
opening live clients. Keep old BackupManifest types/signatures/interpretation;
do not broaden their validators or re-enable module CLI restore. Maintained v2
backup/restore positives must still pass. This restriction must be disclosed as
an intentional public-legacy exception, never counted as successful operation of
that old file-copy API. No general backup bridge or migration engine is added.

**FC-04 — analyzer and raw SQLite.** Public live ConsistencyAnalyzer receives
the resolved layout and shared store-only identity admission before opening
graph/SQLite data. Use the exact normalized vector root; remove alternative-root
probing on guarded paths. Open SQLite read-only with no creation/journal effects.
Do not initialize a provider/tokenizer for admitted store-only analysis. Preserve
analysis algorithms and ordinary schema diagnostics; typed admission failures
cannot become a successful empty analysis. Explicit offline legacy artifact
inspection is separate and cannot count as admitted live analysis.

**FC-05 — no hidden embedder.** Public legacy synthesis with a valid injected
service continues to work under the guarded namespace. Missing/failed/invalid
embedding service must refuse before `collection.add`, never omit vectors and
invoke Chroma's default embedding function. Retain the module CLI's disabled
mutation paths. Public/dry-run reads still need admission; no CLI repair or
automatic fallback model is authorized.

**FC-06 — consolidation acknowledgement.** Classify MemoryConsolidator as
public-unwired, separately from ordinary Chat/Runtime extraction. Successful
summary persistence precedes acknowledgement of its source batch. Shared typed
guard/refusal errors remain actionable; failed batches stay retryable and are
not marked consolidated or reported as unqualified completed success. Mixed
batches acknowledge only successfully stored work and report failures. Preserve
prompts, batching, deduplication and scheduling. No new rollback/exactly-once
transaction guarantee is claimed for unrelated storage failures.

**FC-07 — lifecycle truthfulness.** In non-dry-run mode count promotion,
demotion/reactivation only after successful mutation, respecting false returns
as failures as well as exceptions. Preserve prospective dry-run counts. Keep
partial results and errors visible through both structured results and ordinary
public lifecycle-tool `execute()` text. Do not bury errors solely in `data` while
displaying completed counts. Preserve thresholds/order and generic Tools APIs.

**FC-08 — recall and graph reality.** Let shared typed readiness, space,
provenance, overflow and invalid-vector errors propagate through recall's gather,
priming/fetch and graph exception paths. Keep ordinary unrelated degradation and
cancellation behavior. Public tools may adapt them to explicit tool failures;
they cannot become an empty successful ContextPayload. Background callers must
retain observable failed/retryable status, not falsely acknowledge extraction.
Maintained recall uses synchronous precomputed graph scoring. Preserve existing
zero contribution for a genuinely absent vector; an existing vector with unknown,
foreign or invalid provenance fails the whole semantic operation. Classify the
async on-demand fallback as public-unwired; no new fallback/backfill activation.

**FC-09 — Runtime profile matrix.** Preserve the MemoryProfile values and public
factory interfaces. FULL uses persistent vector/lifecycle collections and graph;
VECTOR_ONLY uses persistent vector/lifecycle collections and NullGraphStore.
Both require explicit persistent open intent/admission. EPHEMERAL and TESTING use
in-memory adapters and isolated in-memory lifecycle collections under one
ephemeral identity/incarnation, never PersistentClient or a default disk root.
Do not mix an ephemeral front store with persistent CollectionManager. Keep
collection APIs and visibility semantics; isolate independent ephemeral kernels.
This is a deliberate correction of profile persistence, not a new profile system.
Transcript persistence is independently governed by its existing explicit
settings; a Memory profile neither enables nor disables it. No Memory-caused
graph/transcript-parent mkdir occurs on refused/ephemeral Memory paths. Isolate
transcript effects explicitly in no-persistent-Memory tests.

**FC-10 — configuration and CLI origin.** Apply B01–B08, including divergent
Chat legacy hint versus actual pool default. Retain raw explicit-origin from
YAML/environment/constructor before default merging or dataclass forwarding.
An explicitly supplied literal equal to the default qualifies as explicit;
a fallback value passed internally by FridayConfig does not. Use an internal
typed origin/sentinel handoff without removing existing caller arguments or
inventing a new public YAML knob. If origin cannot be preserved for a maintained
constructor shape, stop and reconcile instead of assuming it was explicit.

**FC-11 — maintenance admission, probe and dimensions.** Admitted namespace
identity precedes any real provider probe, which itself uses the shared guard.
For empty fresh collections use the admitted identity's expected dimension;
observed stored rows, when present, must agree. Do not infer a model from rows.
Graph-only REEMBED with empty collections must support a compatible identity.
Respect the existing VectorCollectionDimension8192 ceiling: Gate A qualifies
selected model/operation combinations against it, otherwise stops before
construction/provider effects. Do not silently expand that schema or globally
disable unrelated independent services. Freeze a positive variable-dimension
test plus same-dimension different-space and over-ceiling negatives.

**FC-12 — headless counting dependencies.** Put selected exact local counter
dependencies in a narrow LLM `embedding-limits` extra, frozen after Gate A.
Memory requests that extra on its existing pinned LLM dependency, so Runtime,
CLI and Agent memory consumers inherit it without Docling. Keep existing Memory
tiktoken behavior until exact overlap/dependency resolution is proved. A direct
LLM embedding consumer requests that extra or injects an equally qualified
capability; plain LLM-only imports/configuration remain usable without it.
Missing assets/dependencies refuse only affected embedding execution actionably;
no first-use downloads. Core/Commands/plain Tools reads gain no document stack
requirement. Actual minimal installed profiles must prove these edges.

**FC-13 — indirect consumers and inspection.** Add actual agent tools,
archive/background extraction, Runtime multi-agent controller/coordinator,
MCP publication and MEMQ stats/records/list-ingested to the trace table. Preserve
public contracts, authorization visibility, durable receipt ownership and honest
partial failure. Store-only inspection of an admitted namespace works with
inference unavailable; unavailable state projects an explicit unavailable result,
not initialized clients or false empty success. Public legacy preprocessing can
remain callable but its output is not evidence of the common chunk plan, and it
must not split an already accepted plan a second time. No new automatic wiring.

**FC-14 — operational compatibility versus model quality.** Record existing
retrieval/path/pruning thresholds without silently retuning them. B/N deterministic
success/shape/error witnesses prove operational contracts, not semantic quality.
When a real replacement is selected, require a separate bounded relevance and
false-duplicate evaluation/UAT on disposable fixtures before accepting that model.
Define measures and acceptable results in that later model-readiness envelope;
do not claim quality parity or tune thresholds using invented evidence now.
Qwen4B remains illustrative.

## Required proof matrix and bounded scope

Proposed integration nodes below belong to a new
`tests/integration/test_embedding_compatibility.py`; existing focused tests remain
and must receive actual lower-level assertions as appropriate. These stable node
names and B/N/R parameters are requirements for the final directive, not tests
executed during this planning pass. Join each node to concrete source bindings,
installed lane, consumer and named call-phase negative witness at Gate A.

| Contract | Required integration node | Primary existing focused test/source seam |
| --- | --- | --- |
| FC-01 | `test_rejection_logging_obeys_namespace_admission` | Extractor/filter construction, packaged/compat config and Runtime/Chat startup. |
| FC-02 | `test_mcp_snapshot_embedding_compatibility` | Memory/Chat MCP tests and `tests/integration/test_mcp_memory_ingestion.py`; exact single-record success and token-overflow outcome. |
| FC-03 | `test_legacy_backup_guarded_namespace_disposition` | `tests_memory/test_maintenance/test_backup.py`; maintained v2 recovery positive and old physical-copy refusal. |
| FC-04 | `test_analyzer_store_only_namespace_admission` | `tests_memory/test_maintenance/test_analyzer.py`; provider-offline success and no SQLite/graph open on refusal. |
| FC-05 | `test_legacy_synthesis_never_uses_default_embedder` | Synthesizer and module entry; spy on absent/failed embedder plus Chroma writes/default embedding. |
| FC-06 | `test_consolidation_acknowledges_only_stored_batches` | `tests_memory/test_context/test_consolidator.py`; positive, mixed failure and retry. |
| FC-07 | `test_lifecycle_counts_and_tool_text_report_actual_effects` | `tests_memory/test_lifecycle/test_promotion.py`, Tools memory-tool tests; execute text plus structured result. |
| FC-08 | `test_recall_propagates_embedding_refusals` | Controller/scorer, Chat recall, Runtime agent and recall_memory tool; no empty-success disguise. |
| FC-09 | `test_runtime_memory_profile_identity_and_persistence` | `tests_runtime/test_kernel.py`; four profiles, independent ephemeral kernels, separately controlled transcript. |
| FC-10 | `test_existing_embedding_configuration_and_origin` | B01–B08 resolver/CLI fixtures; omitted fields, divergent hint/default, constructor/env origin. |
| FC-11 | `test_maintenance_probe_and_empty_store_dimensions` | Pipeline/provider/mutation tests; zero provider before admission, graph-only empty fresh positive. |
| FC-12 | `test_headless_embedding_install_profiles` | Real installed Memory/Runtime/CLI/Agent and direct LLM-extra profiles without Docling; assets/counter refusal and positive. |
| FC-13 | `test_indirect_memory_consumers_and_inspection` | Agent, multi-agent, MEMQ and MCP public tests; visibility/receipts, provider-offline reads and legacy preprocessing disposition. |
| FC-14 | `test_model_change_preserves_operational_contract` | Full B/N/R extraction→storage→recall→lifecycle/maintenance round trip, with quality evaluation explicitly separate. |

Every maintained B/N flow needs a positive witness; R-only coverage cannot make
an unsupported flow compatible. Test wrong shape/index/nonfinite results and
same-dimension identity drift, overflow, empty fresh collections, missing assets,
ignored service hints, mixed batches and background/exit error adaptation.
Representative FC-01..13 behavior and the full operational round trip execute in
actual normal and optimized installed lanes. Reject mutants through canonical
origin-bound call-phase assertions, never setup/import failures. No model/store
operations occur during document review. Exact real model/dependency/counter
feasibility remains Gate A, with unresolved baseline qualification a hard stop.

Only the primary REM's allowlist plus the explicit narrow rows added for this
annex authorize future construction. Keep old public signatures/classes and
assertion bodies except the named final-directive fixture/oracle exceptions.
Telemetry, unrelated packages and inactive routes receive no opportunistic
rewrite. Existing backup-engine, maintenance sequencing, verification, quarantine,
rollback and user-state safeguards remain; no broader transaction promise.
