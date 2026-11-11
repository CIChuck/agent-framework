# INGEST-001 — framework embedding compatibility contract

Status: **PROPOSED normative annex to REM-CMD-INGEST-001; implementation unapproved**.
This annex incorporates the framework-wide technical themes and selected
high/medium advisories, including the compatibility-cycle pass1 source corrections. It is a contract for future construction and proof, not executed
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
MCP overflow/failure reporting; identity-safe physical backup/restore admission
in FC-03; and isolated ephemeral profile persistence. Public backup creation is
retained, not retired. None permits a silent model change. A formerly successful supported B/N
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

B02's existing hosted default may not qualify under this immutable serving-identity
rule. Report this risk before Gate A and check it first within any separately
authorized readiness envelope. Do not replace the default, drop the baseline or
weaken identity checks to obtain a passing review. If it cannot qualify, return
the concrete incompatibility for maintainer disposition.

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
| Maintained Chat/Runtime semantic recall | Neither composition root injects GraphPathScorer. Preserve unscored graph retrieval, without new graph-vector comparison or provenance preflight. FC-08 still guards actual query/vector/insight/summary operations. |
| Public injectable sync and async graph scorer | Both are public-injectable, not wired in maintained Chat/Runtime. Identity-safe comparisons and document-role fallback are capability proofs, not route proofs; no new scoring/backfill wiring. |
| Graph vectors from extraction, MAINT REEMBED and recovery | Maintained write/preserve paths. Guard writes/envelopes and snapshot identity; do not newly compare them during ordinary recall. |
| Chat compaction; maintained extraction; public-unwired MemoryConsolidator | Preserve unsplit records. Compaction reports failures; FC-06 separately covers extraction acknowledgement/owned tasks and consolidation. |
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
| ContextAssembler inner background task and Runtime shutdown | FC-06 owns the actual extraction task and observable terminal status. The Agent outer scheduling wrapper is not completion proof; no new scheduler or retry queue. |
| Tools MemoryMaintenanceTool/MemoryResetTool and GraphInspectionTool/VectorInspectionTool | Public injectable wrappers, no automatic activation. Retain admitted backup/maintenance/confirmed-clear and provider-offline inspection; expose typed failure/partial results. Lower-layer proof alone is insufficient. |
| Chat FrameworkMaintenanceAdapter.reorganize/reorganize_memory | Non-dry-run legacy compatibility execution stays disabled; callable admitted dry-run remains. Maintained /reorganize still uses the coordinator with unchanged ordering. |
| Runtime _friday_tools_catalog | Actual pkgutil.walk_packages/import_module startup is the minimal-install optional-dependency witness. |
| Context assembly, passage routing, tool recommendation and ordinary tool registration | Preserve nonsemantic/LLM-only paths and lazy unavailable capability; no new document/embedding prerequisite. |
| Telemetry and Transcript package contracts | Compatible unchanged unless a concrete boundary proves otherwise. Existing zero-attempt error telemetry is sufficient; transcript-v1 classes stay unchanged. |
| Commands, MCP transports, Speech, Sandbox, Finance, Moltbook, Optimization, main/scripts | Source-backed unchanged/transitive dispositions and minimal-install/import checks; no unrelated source changes inferred. Dynamic tool imports remain a documented residual risk and installed registry witnesses cover configured supported tools. |
| Lifecycle migration.py, Chat migration/reset/reorganize compatibility stubs | Keep actual inactive/stub/disabled classifications; no migration repair, activation or integration credit. |

## Exact narrow integration requirements

**FC-01 — startup and owned rejection logging.** Defer resourceful
MemoryExtractor/rejection-handler construction until namespace admission; inert
settings can exist earlier. Startup and /read cannot mkdir/open a log in a
refused, unbound or not-yet-created namespace. First-use CREATE_FRESH must work
when the packaged log is inside vector/. Qualify the configured target as owned
by that admitted namespace or an independent safe log root. Stale/foreign or
unknown ownership refuses extraction readiness with an actionable remedy; no
store scan, silent redirect or YAML rewrite. Keep qualified independent targets.

Bind each emission to its admitted extractor/namespace using an extractor-owned
sink/logger with propagation disabled and an owned handler lease. Do not fan out
through the module-global logger to every configured path. Reconfiguration or
close releases only that owner's handler after its task quiesces. Failed
construction releases any new handler. Repeated same-owner/path setup is
idempotent; two kernels cannot write or close each other's handlers. An explicit
shared independent destination needs shared-target admission and owner-specific
leases, not accidental global fan-out. A revoked/closed owner cannot write the
old target; re-admit before reopening. Preserve standalone public filter and
configure_rejection_logging call shapes and qualified independent logging; the
final directive freezes private ownership injection without a logging redesign.
Chat logging.extraction_rejections_file currently has no source consumer: keep
it inert, never activate a second handler from it.

**FC-02 — active MCP snapshots and public failure mapping.** Treat
mcp_tool_snapshot as one exact structured record, exempt from document/512
chunking. Retain opt-in, sanitization, byte ceiling, deterministic identity,
pending/publish/discard ownership and transcript receipt protocol. Count the
final stored record with document-role shared guards; byte-valid token overflow
returns oversized before provider/store effects, never splits or truncates it.
Preserve known typed refusal exceptions ahead of generic storage_failed catches.

The actual Chat persist_mcp_interaction entry must consume the preparation
outcome. Its narrow memory_mcp.py adaptation is required:

| Preparation/result | Receipt/publication disposition | Public observer and turn result |
| --- | --- | --- |
| Disabled, ineligible, unallowlisted or unsafe | Existing policy skip; memory_ingested=false and no memory correlation. | Retain policy-skip behavior and no new activation. |
| Byte or token oversized | Skip this snapshot, with false ingested flag/no memory correlation. | Explicit oversized initial decision, never ingested/published or an indistinguishable initial policy skip. |
| Typed readiness/space/provenance/invalid-result refusal, or storage_failed | No successful skipped receipt for failed preparation. | Safe failure category, then existing MCPMemoryPersistenceError through turn persistence; retry eligibility retained. |
| Ownership conflict | Existing hard ownership failure; no foreign-record deletion. | Safe ownership-conflict category and existing persistence error. |
| Prepared/published/publication pending | Existing exact snapshot, verified append/readback and pending ownership. | Preserve published/pending outcomes and truthful flags. |

The observer keeps its callback shape with additional bounded safe reason
literals. It stays optional/non-authoritative; no raw document/provider/secret
text is reported. Keep receipt/provenance schemas unchanged. Existing skipped
receipts cannot recover an original capacity reason: replay reports their skip,
not a fabricated reason. Non-capacity failures are never persisted as skips.
Retain current cancellation, readback and cleanup of newly owned, uncommitted
snapshots; preserve existing/durably receipted pending records. Mixed ordinary/MCP
turns keep existing partial-turn behavior, with explicit persistence failure;
no new whole-turn rollback/atomicity is promised. Freeze exact approved error
oracles in the final directive and test real public publication/receipt/observer,
not only MCPMemoryIngester.

**FC-03 — compatible public physical backups.** Retain BackupManager
create_backup, verify_backup and restore_backup signatures/return types and the
old BackupManifest class. Public create, enabled module backup, Reorganizer
backup/backup_first and the injectable Tools wrapper must still succeed under
admitted B/N. Do not retire them, disable backup_first or substitute a different
API as proof of compatibility.

Use shared store-only admission and the resolved layout before live source
reads, destination mkdir or copy; no provider/tokenizer. Require a destination
outside the active vector namespace and reject source/destination recursion or
symlink escapes. Preserve an existing safe default, such as memory-root/backups
beside vector/. If the default/explicit root is inside vector/, refuse before
mkdir and point to the existing external backup_root/backup_dir option; do not
silently relocate it. Copy the ready binding as immutable artifact evidence,
without changing live source bytes/metadata. Keep the legacy manifest model;
a separate strictly versioned bound receipt in the backup records the exact
manifest/sidecar digests, normalized layout and incarnation. Freeze its schema
and exact source/artifact member mapping at Gate A.

Public restore succeeds into the SAME admitted space/incarnation/layout only,
with validated bound receipt and permitted data inventory. Identity/target
checks are mandatory even with verify_first=False; that flag controls the old
optional data-checksum pass, not admission. Never copy a ready/pending marker,
overwrite/recreate the live binding, clone another incarnation or attach an old
artifact to a fresh namespace. Validate every path and identity before any live
write. Identity-free artifacts retain offline manifest/checksum inspection;
live restore remains refused by the approved fresh-store policy. Foreign,
pending/malformed artifacts and an unsafe destination refuse before mkdir/copy.
Preserve existing physical-copy consistency/quiescence preconditions and disclose
limitations: no new online/crash-atomic Chroma backup engine. Prove positive
public create/verify/same-incarnation restore on quiescent disposable B/N stores,
including restored data and retained live identity. Maintained v2 snapshot and
rollback remains separate proof; disabled module restore stays disabled. No
generic bridge, migration, new command or maintenance-order change.

**FC-04 — analyzer and raw SQLite.** Public ConsistencyAnalyzer uses
the resolved exact layout and shared store-only admission before live graph or
SQLite reads, with no alternative-root probing. All its SQLite opens, including
Chroma and transcript databases, use explicit read-only URI mode and cannot
create absent files/journals. No provider/tokenizer for admitted store-only
analysis. Preserve algorithms and ordinary schema diagnostics; typed admission
failure cannot become successful empty analysis. Offline historical artifact
inspection is separate and not positive admitted live-analysis proof.

**FC-05 — no hidden embedder, retained callable shapes.** Qualified
public legacy synthesis keeps its injected service and document-role storage.
Preserve accepted embed_query, embed and bare-callable invocation shapes at the
public boundary: composition resolves an exact identity/counter capability from
the existing service/readiness record and wraps that shape with the shared LLM
guard/role adapter. This is the qualification route, not a new model selector.
The wrapped callable must preserve the invocation shape and error/cancellation
semantics while applying the qualified document preparation exactly once. A
query-only callable with hidden preparation cannot be guessed into a document
provider: qualify its bounded adapter or stop readiness. Its raw name or
dimensions alone is not qualification. Freeze exact wrapper
signatures at Gate A and test all three existing shapes positively in B/N.
Unqualified/missing/failed/invalid services refuse actionably before collection.add;
never omit vectors and invoke Chroma's default embedder. This is the existing
capability-refusal rule, not retirement of duck-typed callers. Public/dry-run
reads still need admission; disabled module mutations remain disabled. No new
CLI fallback or automatic model.

**FC-06 — extraction, background ownership and consolidation.** These
are separate paths and need separate witnesses. In maintained MemoryExtractor
storage, typed readiness/identity/provenance/overflow/invalid-result refusals at
entity/relationship, edge embedding, insight batch/fallback or summary boundaries
must surface as failed extraction (typed raise or result.error), including mixed
partial outputs. Never turn a failed edge embedding into a vectorless edge.
An absent edge vector is allowed when no edge embedder is configured, not when
a configured service refuses. Known guard errors do not enter per-item fallback;
retain unrelated non-guard fallback/error policy. Count only actual persistence;
false/incomplete persistence returns cannot acknowledge the output as stored.
Keep the existing stable insight/summary IDs and upsert semantics, graph dedup
and partial-state reporting; do not promise a new all-or-nothing transaction.
Prompts, ontology and extraction LLM selection stay unchanged.

Chat _extract_turns keeps the failed/unprocessed turns in pending_extraction and
does not mark them completed. Preserve its existing cancellation/commit-completed
distinction. Successful retry uses the same output-slot identities; test against
duplicate records instead of claiming full semantic exactly-once extraction.

Memory ContextAssembler owns the actual inner task it starts for
extract_context(async_execution=True), consumes its result/exception and retains
per-turn queued/running/completed/failed-retryable/cancelled/skipped-unavailable
status. Keep the existing method signature and None return; add only a typed
read-only status/wait capability on the concrete Memory assembler, not a new Core
requirement for custom context engines. Telemetry-disabled callers can inspect
that status; a scheduling/turn_archived event is not extraction completion.
Retain active task handles to completion, bound terminal-state retention to the
session lifetime, and drain/cancel-and-await owned tasks before closing their
extractor/sink during existing Runtime shutdown. Do not let the Agent's outer
wrapper's return acknowledge the inner task. No-extractor is an explicit skip;
failed work remains eligible for an explicit later call. No new automatic retry,
queue, scheduler, durable journal or Agent public signature is introduced.

MemoryConsolidator remains public-unwired. Persist a successful batch summary
before acknowledging its source turns; failed batches remain retryable, mixed
batches acknowledge only successful work and report failure. Preserve its
prompts, batching, deduplication and scheduling.

**FC-07 — lifecycle truthfulness.** In non-dry-run mode count promotion,
demotion/reactivation only after successful mutation, respecting false returns
as failures as well as exceptions. Preserve prospective dry-run counts. Keep
partial results and errors visible through both structured results and ordinary
public lifecycle-tool `execute()` text. Do not bury errors solely in `data` while
displaying completed counts. Preserve thresholds/order and generic Tools APIs.

**FC-08 — actual recall and injectable graph scoring.** Typed shared
readiness/space/provenance/overflow/invalid-vector errors propagate through actual
recall/query, CollectionManager.get_all gather, controller priming/fetch,
_fetch_recent_insights, _fetch_recent_summaries and get_insights_by_author.
Preserve unrelated partial-read warnings/degradation and cancellation. Public
tools may adapt refusal to explicit failure/unavailable, never empty successful
ContextPayload. FC-06 covers actual background completion/acknowledgement.

Neither maintained Chat nor Runtime composition injects GraphPathScorer. Keep
their ordinary graph retrieval UNSCORED: it does not compare stored graph
vectors and gains no vector-provenance preflight for an unused scorer. Stored
graph vectors are maintained write/preserve state for extraction, REEMBED and
recovery; guard those writes/snapshots. Both synchronous filter_paths_sync and
async scoring/fallback are public-INJECTABLE APIs only. On explicitly injected
comparisons, validate compatible query/stored-vector identity; an existing
foreign/unknown/invalid vector fails the semantic operation, while a genuinely
absent vector retains its existing zero contribution. Async fallback uses guarded
document-role embeddings. No scorer/fallback/backfill is newly wired. Require
actual Chat/Runtime spies proving ZERO graph-vector comparisons alongside public
injected-scorer B/N/R capability tests, clearly labelled as different proofs.

**FC-09 — Runtime profile matrix and concrete ephemeral isolation.**
Preserve public MemoryProfile/factory shapes. FULL uses persistent vector/lifecycle
collections and graph; VECTOR_ONLY uses persistent vector/lifecycle collections
and NullGraphStore. Both require explicit open intent/admission. EPHEMERAL and
TESTING use in-memory front and lifecycle stores with one identity/incarnation
per kernel, never PersistentClient/default disk roots.

Do not assume two Chroma EphemeralClients are isolated: the pinned backend shares
one in-memory system. Namespace every Chroma-backed in-memory physical collection
with the kernel's unique incarnation, carrying the same scope through front,
short/long/decayed/MCP collections and admission. Keep logical configured base
names/API semantics; internal suffixed names must satisfy backend constraints.
Per-kernel clear/close deletes only owned collections and never resets the shared
system or another kernel. Two kernels with different identities and the same
logical names in one process must not share records/query results or dimension
state. This is profile isolation, not a security or new profile-system promise.
Transcript persistence stays independently configured; Memory profile does not
enable/disable it. No Memory-caused graph/transcript-parent mkdir on refused or
ephemeral Memory paths. Isolate independent transcript effects in no-disk tests.

**FC-10 — configuration and CLI origin.** Apply B01–B08, including divergent
Chat legacy hint versus actual pool default. Retain raw explicit-origin from
YAML/environment/constructor before default merging or dataclass forwarding.
An explicitly supplied literal equal to the default qualifies as explicit;
a fallback value passed internally by FridayConfig does not. Use an internal
typed origin/sentinel handoff without removing existing caller arguments or
inventing a new public YAML knob. If origin cannot be preserved for a maintained
constructor shape, stop and reconcile instead of assuming it was explicit.

**FC-11 — maintenance admission, probe and dimensions.** Admitted namespace
identity precedes ALL real provider probes, including the synthesizer/chat LLM
probe as well as embedding probes. Embedding probes use the shared guard; refused
rows make no LLM/provider/model call, not merely zero embedding calls.
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
requirement. Actual minimal installed profiles must prove these edges. Invoke
Runtime's real _friday_tools_catalog pkgutil/import discovery without Docling/OCR;
its normal Memory dependency still supplies the counter extra. Separately test
optional-package absence in a private copied-prefix import control with counter
and document packages unavailable. Clearly label that as an import/dependency
failure control, not a supported fully resolved Runtime installation. Tool
modules, including the new document reader and embedding-limits module, must
remain lazy; unsupported execution fails actionably. A synthetic registry is
not proof of the actual catalog import path.

**FC-13 — indirect consumers and inspection.** Add actual agent tools,
archive/background extraction, Runtime multi-agent controller/coordinator,
MCP publication and MEMQ stats/records/list-ingested to the trace table. Preserve
public contracts, authorization visibility, durable receipt ownership and honest
partial failure. Store-only inspection of an admitted namespace works with
inference unavailable; unavailable state projects an explicit unavailable result,
not initialized clients or false empty success. Public legacy preprocessing can
remain callable but its output is not evidence of the common chunk plan, and it
must not split an already accepted plan a second time. Public injectable Tools
maintenance/reset/graph/vector inspection wrappers join actual-call tests. Keep
existing confirmed-reset semantics and scope; before any clear, shared store-only
admission validates the whole target layout. Refusal precedes graph/vector/
episodic effects, without a new rollback guarantee for unrelated later errors.
Successful reset retains the namespace binding; never implement model migration
or erase the sidecar. Maintenance wrappers expose actual errors/partial results,
not unconditional completed text. Legacy Chat execute methods stay disabled;
their admitted dry-run and maintained coordinator path are separately tested.
No new automatic wiring or actual user reset is authorized.

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
| FC-01 | `test_rejection_logging_obeys_namespace_admission` | Real first-use startup plus two owned sinks/kernels, reconfigure/close, failed setup, repeated same-path and unchanged old-root metadata. |
| FC-02 | `test_mcp_snapshot_embedding_compatibility` | Real persist_mcp_interaction/turn observer, snapshot receipts and ownership: B/N, overflow, typed refusal, storage/ownership failure and mixed calls. |
| FC-03 | `test_legacy_backup_guarded_namespace_disposition` | Public BackupManager create/verify/same-incarnation restore, module backup, Reorganizer backup_first and Tools wrapper positives; receipt/sidecar/unsafe-root/clone refusals and separate maintained v2 proof. |
| FC-04 | `test_analyzer_store_only_namespace_admission` | `tests_memory/test_maintenance/test_analyzer.py`; provider-offline success and no SQLite/graph open on refusal. |
| FC-05 | `test_legacy_synthesis_never_uses_default_embedder` | Synthesizer and module entry; spy on absent/failed embedder plus Chroma writes/default embedding. |
| FC-06 | `test_consolidation_acknowledges_only_stored_batches` | `tests_memory/test_context/test_consolidator.py`; positive, mixed failure and retry. |
| FC-06 | `test_extraction_acknowledges_only_stored_outputs` | Real Chat pending extraction, edge/batch/fallback/summary refusals, stable-ID retry and no vectorless edge after guard error. |
| FC-06 | `test_background_extraction_status_observes_owned_task` | Actual Agent archive plus real ContextAssembler, delayed post-return failure, telemetry off, wait/status, no-extractor, cancellation and Runtime shutdown. |
| FC-07 | `test_lifecycle_counts_and_tool_text_report_actual_effects` | `tests_memory/test_lifecycle/test_promotion.py`, Tools memory-tool tests; execute text plus structured result. |
| FC-08 | `test_recall_propagates_embedding_refusals` | Actual vector/query/priming/insight/summary consumers and get_all/refusal propagation; unscored maintained graph route separately spied. |
| FC-08 | `test_injected_graph_scorer_binding_and_unscored_routes` | Actual Chat/Runtime have zero graph-vector comparisons; explicitly injected sync/async scorer B/N plus same-dimension foreign R. No new maintained wiring. |
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
rewrite. Existing backup consistency limits, maintenance sequencing, verification, quarantine,
rollback and user-state safeguards remain; no broader transaction promise.
