# INGEST activation appendix A2 — shared contracts

Version 0.2, 2026-11-13. **Proposed exact design; not activated.** Prepared from
`7a3e00bc9ef77adee25b61fc52ff91875e172738` and the unchanged
[directive v0.7](../../../../directives/CD-CMD-INGEST-001-product.md).
The directive, REM and compatibility annex control except for the explicit
[current requirement dispositions](requirement-reconciliation.md). This appendix
supplies exact implementation choices for approval; no product declarations below
exist yet and no document assertion is measured product evidence.

## 1. Package surfaces and value rules

New shared values/protocols live in `friday_core.ingestion`, imported explicitly
from that submodule. Core root exports need no change. Commands' root API54 and
its standard-library dependency closure remain unchanged. Core values use frozen,
slotted, keyword-only dataclasses and immutable tuples; persisted JSON has explicit strict
loaders. Construction validates values, including under `python -O`. No vendor
object, `Any`, mutable dictionary or caller-owned list crosses the new boundary.

The following notation specifies complete fields in declaration order. `Digest`
is lowercase `[0-9a-f]{64}`; `Id` is a lowercase UUID hex string of length 32.
Integers are strict (booleans are not integers); sizes/counts are nonnegative
unless positive is stated. `Scalar` is `str | int | float | bool`, with finite
floats only. Metadata is a sorted `tuple[tuple[str, Scalar], ...]` with unique
nonempty keys. Optional fields are explicitly `T | None`, default `None`.
No implicit whitespace/Unicode normalization applies to source or model text.

| Type | Exact fields and invariants |
| --- | --- |
| `ChunkStrategy` | Literal `document`, `recursive`, `fixed`. |
| `EmbeddingRole` | Literal `query`, `document`; no new clustering convention. |
| `ChunkingOptions` | `strategy: ChunkStrategy | None = None`, `max_tokens: int | None = None`; supplied budget positive. Omission is distinct from an explicit value. |
| `ResolvedChunkingOptions` | `strategy: ChunkStrategy`, `max_tokens: int`, `policy_version: Literal[1] = 1`; positive budget. |
| `SourceUnit` | `kind: Literal['document','page','sheet','slide']`, `index: int`, `label: str | None`, `included: bool`; source indices are one-based and retain original numbering. |
| `SourceSpan` | `start: int`, `end: int`, `unit_index: int | None`; half-open Python Unicode-code-point offsets in canonical `SourceDocument.content`, `0 <= start < end <= len(content)`. |
| `CellSpan` | `row: int`, `column: int`, `row_span: int`, `column_span: int`, `value_span: SourceSpan`; source coordinates/spans positive, never expanded into unrelated cells. |
| `TableStructure` | `table_id: str`, `header_spans: tuple[SourceSpan,...]`, `row_spans: tuple[SourceSpan,...]`, `cells: tuple[CellSpan,...]`; ordered, source-backed spans only. No CSV header inference. |
| `SourceBlock` | `block_id: str`, `kind: Literal['text','heading','table','separator','label']`, `span: SourceSpan`, `heading_spans: tuple[SourceSpan,...]`, `table: TableStructure | None`; table populated only for declared structured tables. Labels/separators cannot establish meaningful source content. |
| `CoverageWarning` | `code: str`, `unit_indices: tuple[int,...]`, `count: int | None`; codes are selected from the versioned format-profile allowlist. Human messages are sideband, not source text. |
| `SourceDocument` | `source_id: Id`, `source_kind: Literal['text','markdown','code','json','yaml','csv','tsv','web_text','tool_text','pdf','docx','xlsx','pptx']`, `locator: str`, `raw_sha256: Digest`, `content: str`, `content_sha256: Digest`, `conversion_profile_sha256: Digest | None`, `units: tuple[SourceUnit,...]`, `blocks: tuple[SourceBlock,...]`, `warnings: tuple[CoverageWarning,...]`, `complete: Literal[True]`; content nonempty and contains actual meaningful source text. |
| `EmbeddingSpaceIdentity` | `schema_version: Literal[1]`, `model_identity: str`, `artifact_identity: str`, `tokenizer_sha256: Digest`, `preparation_sha256: Digest`, `dimensions: int`, `normalization: Literal['none','l2']`, `metric: Literal['cosine','l2','ip']`; dimensions positive. Model/artifact identity records the configured space under section 3; a declared identity is never labelled immutable serving evidence. |
| `PreparedInput` | `space_sha256: Digest`, `role: EmbeddingRole`, `input_sha256: Digest`, `prepared_sha256: Digest`, `text: str`, `token_count: int`; text is the exact wire payload; prepared_sha256 hashes effective formatted UTF-8 input after declared client/server preparation. Count includes special tokens. Never persist embedding preparation instead of source content. |
| `PreparedVector` | `space_sha256: Digest`, `role: EmbeddingRole`, `input_sha256: Digest`, `prepared_sha256: Digest`, `values: tuple[float,...]`; exact declared dimension, finite real values, no booleans. |
| `PreparedBatch` | `inputs: tuple[PreparedInput,...]`, `vectors: tuple[PreparedVector,...]`; equal lengths, elementwise identities/roles/digests equal, every vector checked before returning any batch for storage. |
| `PlannedChunk` | `index: int`, `text: str`, `coverage_spans: tuple[SourceSpan,...]`, `context_spans: tuple[SourceSpan,...]`, `prepared: PreparedInput`; index zero-based contiguous, text nonempty, prepared input binds SHA256 of text. Context is source-backed repeated headings/headers, never invented content. |
| `ChunkPlan` | `schema_version: Literal[1]`, `source_id: Id`, `source_sha256: Digest`, `content_sha256: Digest`, `conversion_profile_sha256: Digest | None`, `options: ResolvedChunkingOptions`, `space_sha256: Digest`, `chunks: tuple[PlannedChunk,...]`, `plan_sha256: Digest`; nonempty, complete coverage/order, all prepared counts within both requested and effective limits. |
| `DestinationBinding` | `namespace_id: Id`, `incarnation: Id`, `space_sha256: Digest`, `layout_sha256: Digest`, `collection: str`; exact admitted physical destination, not multi-agent visibility label. |
| `DestinationNamespaceBinding` | `namespace_id: Id`, `incarnation: Id`, `space_sha256: Digest`, `layout_sha256: Digest`; identical namespace fields to DestinationBinding with no collection field. |
| `IngestionProgressEvent` | `attempt_id: Id`, `stage: Literal['queued','audit','conversion','planning','embedding','storage','completed','cancelled','failed']`, `completed: int | None`, `total: int | None`, `code: str`; counts nonnegative, completed <= total when both known. No frontend-rendered string or source text. |
| `IngestionReceipt` | `schema_version: Literal[1]`, `attempt_id: Id`, `source_sha256: Digest`, `plan_sha256: Digest`, `destination: DestinationBinding`, `record_ids: tuple[str,...]`, `stored_count: int`, `complete: Literal[True]`; count positive and equal to unique record IDs and accepted chunks. Only readback-confirmed storage earns this receipt. |
| `IngestionResult` | `attempt_id: Id`, `status: Literal['stored','partial','failed','cancelled']`, `options: ResolvedChunkingOptions`, `planned_count: int`, `confirmed_record_ids: tuple[str,...]`, `unconfirmed_record_ids: tuple[str,...]`, `receipt: IngestionReceipt | None`, `errors: tuple[IngestionFailure,...]`; receipt iff complete stored success. Partial/unknown effects never become a success receipt. |

`locator` is the normalized local source path or a caller-supplied provenance
label; it is never fetched. `raw_sha256` hashes admitted original file bytes or
UTF-8 supplied text; `content_sha256` hashes exact canonical Unicode text encoded
as UTF-8. File snapshot, extension/detected format and source mutation checks
precede conversion handoff. Canonical content may contain explicit unit labels,
but meaningful-content admission counts actual source text, not labels/filenames.

## 2. Errors and protocol signatures

`IngestionFailure` is a frozen value `(code: IngestionErrorCode, stage: str,
retryable: bool, safe_message: str, source_id: Id | None, attempt_id: Id | None)`.
`IngestionError(RuntimeError)` carries this value as `.failure`; it never embeds
raw document text, credentials, provider bodies or arbitrary exception repr.
Codes are exactly `usage`, `unsupported_format`, `source_unreadable`,
`source_changed`, `missing_dependency`, `missing_asset`, `encrypted`, `corrupt`,
`partial_conversion`, `empty_content`, `coverage_unproven`,
`unsupported_workbook_visibility`, `resource_limit`,
`timeout`, `cancelled`, `readiness`, `identity`, `overflow`, `response_invalid`,
`worker_busy`,
`store_refused`, `storage_failed`, `worker_failed`, `worker_not_quiescent`.
Existing domain exceptions remain public; adapters preserve typed shared errors
rather than broad-catching them as empty data or completion.

All following names are Core protocols unless the owner column says otherwise.
Signatures are exact; existing unrelated public methods remain unchanged.

| Owner / protocol | Signature and contract |
| --- | --- |
| Core `IngestionObserver` | `on_progress(self, event: IngestionProgressEvent) -> None`; nonblocking parent-side event delivery. Frontends render or enqueue the event; no frontend callable enters the child. Observer failure is reported as a delivery diagnostic and never fabricates storage success/failure or changes an issued receipt. |
| Core `TokenCounter` | `prepare(self, text: str, *, role: EmbeddingRole) -> PreparedInput`; synchronous, local, deterministic, no network/storage/truncation. `validate(self, value: PreparedInput) -> None` independently verifies wire/effective identity and exact count without appending a prefix again. `.space: EmbeddingSpaceIdentity`, `.effective_max_tokens: int`. |
| Core `CounterFactory` | `create(self) -> TokenCounter`; immutable picklable factory containing only manifest-bound local asset paths and deterministic preparation config. No model client/store/credential reference. Composition root injects it; Tools imports no LLM module by name. |
| Core `OwnedDocumentSession` | `.source: SourceDocument`; `async plan(self, options: ResolvedChunkingOptions, *, counter_factory: CounterFactory) -> ChunkPlan`; `cancel(self) -> None`; `async aclose(self) -> None`. Close invalidates further use and joins; idempotent, including after failed/cancelled plan. |
| Core `DocumentConverter` | `async aclose(self) -> None` cancels/drains owned sessions and rejects new work idempotently; `async open(self, path: Path, *, attempt_id: Id, observer: IngestionObserver | None = None) -> OwnedDocumentSession`; local conversion only. No counter needed for opening/read-only display. Source/vendor structure belongs to the owned session. |
| Core `DocumentPlanner` | `async plan(self, source: SourceDocument, options: ResolvedChunkingOptions, *, counter: TokenCounter) -> ChunkPlan`; only non-Docling implementation runs directly in Memory. Converted documents use `OwnedDocumentSession.plan`, keeping vendor structure internal. |
| Core `IngestionEntry` | `async ingest(self, source: SourceDocument, *, options: ChunkingOptions = ChunkingOptions(), description: str | None = None, document_session: OwnedDocumentSession | None = None, observer: IngestionObserver | None = None) -> IngestionResult`; Memory implements; converted document source/session identity must match. Caller owns admission and session lifetime. `async aclose(self) -> None` rejects new ingests, cancels/invalidate-and-joins active operations, and idempotently drains owned tasks before returning; shared clients/stores are not closed by this entry. |
| Memory public factory | `create_ingestion_entry(*, destination: DestinationBinding, vector_store: PreparedVectorStore, counter: TokenCounter, embedder: PreparedEmbeddingService, defaults: ChunkingOptions = ChunkingOptions(), counter_factory: CounterFactory | None = None) -> IngestionEntry` in `friday_memory.ingestion`. No Tools/Chat import; converted-document planning requires the supplied pure counter factory. |
| Core `PreparedEmbeddingService` | Read-only `.space: EmbeddingSpaceIdentity`; `async embed_prepared(self, inputs: tuple[PreparedInput,...], timeout: float | None = None) -> PreparedBatch`. The LLM implementation owns provider I/O, once-only preparation validation and full response validation. No conversion/store dependency. |
| Core `PreparedVectorStore` | `async write_prepared(self, *, texts: tuple[str,...], metadatas: tuple[tuple[tuple[str,Scalar],...],...], ids: tuple[str,...], batch: PreparedBatch) -> PreparedWriteResult`; validates all lengths, text digests and document roles before write. |
| Core `PreparedWriteResult` | Frozen value `confirmed_ids: tuple[str,...]`, `unconfirmed_ids: tuple[str,...]`, `errors: tuple[IngestionFailure,...]`; every proposed ID appears exactly once in confirmed/unconfirmed; false/ambiguous backend outcomes cannot confirm IDs without readback. |
| LLM additive method | `async embed_prepared(self, inputs: tuple[PreparedInput,...], timeout: float | None = None) -> PreparedBatch`; validates exact identity/count/role; sends already prepared text once, never prepares a second time. |

`LiteLLMEmbeddingService.embed_documents(texts, timeout)` and `embed_query(text,
timeout)` retain existing parameter/return shapes. Add only keyword-only
`capabilities: ResolvedEmbeddingCapabilities | None = None` to its constructor;
`from_spec` carries that optional resolved value. `ResolvedEmbeddingCapabilities`
in `friday_llm.embedding_limits` owns exact artifact/asset references, effective
input/batch limits, order contract, preparation and counter factory; source
serialization into Core identities uses only the fields in section 1.

I1 adds guarded methods/new configured construction without changing legacy
prepared inputs, cache keys or public positive flows. I2 switches maintained
constructors/callers together and removes the internal unguarded branch: missing
resolved capability then refuses before provider/cache effects. This is staged
construction, not a final legacy-mode config. Direct old call shapes still work
when capabilities resolve through the configured record defined below. Missing
optional serving/parity evidence never refuses a configured record. Empty document
batches retain `[]` with zero I/O.

The Memory factory checks destination/counter/embedder space equality locally,
before source/provider/store effects. Memory validates the entire plan, calls the
injected embedder, independently validates the returned entire batch and only
then calls `write_prepared`. No hidden client attribute, global broker or frontend
import supplies the missing dependency. Embedding failure/timeout/cancellation
causes no source-chunk write; partial backend effects remain truthful in the
structured result. Closing an entry waits for all such eligibility decisions.

Core's existing vector `query` adds `PreparedVector` to the optional
`query_embedding` annotation without changing positional order/defaults. Existing
raw-list shape remains representable for compatibility diagnostics; a bound
operation refuses it before client/provider I/O. Maintained consumers pass the
new query-role envelope. Do not add abstract methods to existing store ABCs:
`PreparedVectorStore` is an additional narrow protocol implemented by admitted
Memory adapters. Existing `add_documents` remains and delegates guarded embedding
and prepared writing; it never embeds an already supplied prepared batch twice.

### Exact concrete constructors and pure file-input adapter

Tools exposes `DoclingDocumentConverter(*, assets_root: Path,
profile_id: str, asset_manifest_sha256: Digest)` in its new document submodule.
Construction is inert: no import of heavyweight document engines, worker spawn,
model/counter/store creation or asset fetch until the relevant operation.
LLM exposes `LocalTokenCounterFactory(*, assets_root: Path,
asset_manifest_sha256: Digest, record_id: str)` in `embedding_limits`.
Memory store adapters add only keyword-only
`open_request: StoreOpenRequest | None = None`; new guarded factory paths require
it. I2 admission forwards it explicitly, preserving all old positional parameters.
Missing resolved identity is a typed readiness error, not inferred capability.

Commands exposes `parse_file_input(raw_tail: str, *,
command: Literal['read','ingest']) -> FileCommandInput` only in `file_inputs`.
`FileCommandInput` is its own frozen stdlib value with `path: str`,
`description: str | None`, `chunking_strategy: Literal['document','recursive','fixed'] | None`,
`chunk_tokens: int | None`, `line_tokens: tuple[str,...]`.
It follows REM C exactly for quote/opaque-description/terminator semantics and
returns raw recognized line-option tokens to Chat's retained `parse_line_limit`
helper. It imports no Core/Memory types; Chat maps validated option primitives to
Core's `ChunkingOptions`. Any document line option is refused before conversion;
legacy malformed text-line behavior is retained. The new parser has no filesystem,
provider or environment access. Handler-identity selection stays in Chat registry.

## 3. Configuration, assets and deterministic planning

Add only optional strict `max_input_tokens: int | None` and
`expected_dimensions: int | None` to `EmbeddingOptions` and the resolved spec;
omitted keys remain parseable. Existing batch/cache/resilience/default-service,
endpoint, extraction/maintenance selection and credentials keep their semantics.
Explicit contradictions refuse operation, unselected profiles/read-only startup
remain usable. Capability/schema resolution and local assets belong to LLM.
LLM's proposed `embedding-limits` extra contains `tokenizers==0.23.3`, the
measured local JSON-tokenizer backend. Existing Memory `tiktoken` is retained;
any hosted counter backend required for the supported default is explicitly bound
in the phase asset/dependency manifest before its use. No Core/Commands weights
or tokenizer binaries. This is an implementation dependency binding, not a new
hosted model qualification campaign or installation authority.

The deployment manifest binds an absolute `assets_root`; every tokenizer, OCR,
converter and capability asset has a relative path, hash, size, license/source
and backend identity. Resolve beneath that root; refuse traversal/escaping symlinks,
hash before opening and never fetch on first use or consult HOME/global caches.

The strict LLM capability record has `schema_version=1`, `record_id`, `space`,
`asset_manifest_sha256`, `tokenizer_manifest_sha256`, `preparation`,
`verified_input_limit`, `serving_input_limit`, `serving_batch_input_limit`,
`verified_batch_size`, `parity_evidence_sha256: Digest | None`,
`serving_identity_evidence_sha256: Digest | None`, and `index_contract`
(`indexed` or `qualified_ordered`). Retained `verified_*` field names now mean
locally validated configured limits, not evidence of a new serving experiment.
Input/batch limits and batch size are positive; the minimum applicable configured,
model and deployment input limit wins. Unknown required capacity/dimension/counter
fails with an explicit configuration error, never guessed values or truncation.
Evidence hashes are optional history: null is admissible and is not a runtime gate.

Preparation is strict: `query_owner`/`document_owner` (`client` or `server`) and
`query_template`/`document_template` (one literal `{text}` substitution each).
Client formatting changes wire text once; configured server formatting is counted
locally without also prefixing it client-side. `embed_prepared` independently
recounts and revalidates exact wire/effective digests; it never trusts supplied
counts. `qualified_ordered` means a configured order-preserving transport contract,
not a new empirical campaign. Indexed responses must have unique complete indices;
all count/order/dimension/finiteness checks apply before returning vectors.

LLM provisions schema/resolver support in I1 and binds all selected existing pool,
non-pool/default/legacy routes in I2 composition using unchanged model config plus
an explicit local capability manifest. Selecting a known default does not require
new YAML fields or a provider probe. A supported default must have an offline
configured record/counter at the ordinary I2 positive test; unresolved defaults
block that slice rather than quietly disabling a consumer. Record assets and their
backend dependency belong to LLM's phase manifest, with the same assets available
to Memory/Runtime/CLI headless installation profiles. No new Tools-to-LLM import.

`artifact_identity` is an already supplied artifact digest when available;
otherwise it is `declared:` plus the SHA256 of canonical JSON containing the
resolved configured model ID and optional revision (null if absent). A hosted
model can use this declared basis. Endpoint, service alias, keys and resilience/
cache/batch knobs are excluded; aliases resolving to the same model/revision,
preparation/tokenizer/dimensions yield the same space. Resolver records explicitly
label configured identity versus attested immutable identity. No attestation is
required. An out-of-band swap behind an unchanged server alias is undetectable;
operators must update the declared identity and choose a fresh namespace when
changing models. Existing files are never migrated/stamped. Optional historical
evidence does not turn a configured record into a stronger identity claim.

The pure `LocalTokenCounterFactory` contains only `assets_root`,
`asset_manifest_sha256`, `record_id`; it validates the record locally and retains
no endpoint, credential or model/store client.

LLM loads `embedding-capabilities/<record-id>.json` and tokenizer files from
`tokenizers/<artifact-id>/`; Tools loads `document-profiles/<profile-id>.json`
and the already qualified PDF/OCR assets. Bare read-only Office conversion does
not resolve a tokenizer. Headless text policy uses Memory defaults/per-call
options; Runtime gains no document-chunking YAML. Existing MCP policy is separate.

Memory resolves each ingestion option independently: call override, then Chat-
injected configuration default, then `document`/512. Above-capacity budgets refuse
before conversion when capacity is known. Actual final inputs are recounted
before provider I/O. No silent clamp, character estimate, overlap flag or lost tail.

Non-Docling document segmentation preserves original spans including separators;
blank lines delimit blocks; ATX heading runs apply to following blocks until a
heading of equal/higher level. A fenced-code block stays opaque. Recursive
refinement tries paragraph, sentence boundary after `.?!` followed by whitespace,
then Unicode-code-point boundaries. Fixed windows choose the longest nonempty
prefix whose exact prepared count fits, checking the chosen prefix rather than
assuming token counts are monotonic. No content overlap. Only source-backed
heading/table context may repeat and is recorded separately from coverage.
Never merge sheets/slides. If minimal context plus one source code point cannot
fit, refuse the complete request before embedding/storage; never drop a cell/row.
Plain CSV/TSV preserves all text and warns `table_structure_not_supplied`.

For all strategies Memory checks plan identity, contiguous chunk indices, exact
source coverage/order and final prepared counts before embedding. IDs allocated
for an attempt are retained across its explicit retry only; a new user invocation
gets a new attempt, preserving prior re-ingestion/count semantics. Do not dedupe
by source hash as an unrequested behavior change. Existing metadata helper owns
`type=ingested_file`, protection, source path and omission of absent descriptions.
New flat reserved fields use `friday_ingest_` (schema, source/plan/space/profile
hashes, strategy, max_tokens, index/count and provenance JSON string). No None or
nested object is sent to Chroma metadata. MCP and derived maintenance records
remain unsplit; their role/capability checks still apply.

### XLSX visibility admission

The [maintainer amendment](office-visibility-decision.md) selects whole-workbook
refusal when any included worksheet has hidden rows or columns. Read-only
structural detection occurs before Docling conversion or ingestion. Return
`unsupported_workbook_visibility`, sheet names/counts and an actionable safe
explanation; no partial success, hidden-value disclosure or input mutation.
Hidden worksheets retain their separate default exclusion. Visible-only workbook
conversion and all other format rules are unchanged. No row/column filtering
qualification is required for files refused under this approved policy.

## 4. Worker, read-only request and publication

The [shared worker decision](shared-worker-decision.md) applies to every frontend.
Tools implements conversion/session/process management once. Core events, results
and close protocols are UI-neutral. Memory plans/embeds/stores via injected
interfaces; actual provider clients and stores stay in the parent. Read-only
conversion constructs no Memory entry/admission/embedding service.

### Exact process and IPC mechanism

One fresh interpreter per owned document session is launched using
`asyncio.create_subprocess_exec(sys.executable, '-I', '-B', '-m',
'friday_tools.document_ingestion', '--worker', env=child_env, cwd=request_root,
start_new_session=True)` on the supported POSIX profile. This is subprocess exec,
not `multiprocessing.spawn`; never mutate parent `os.environ` or fork a live client.
The worker entry is in the already mapped Tools module. A private child environment
contains required native/locale paths, bound assets/offline settings and
`LITELLM_MODE=PRODUCTION` / `LITELLM_LOCAL_MODEL_COST_MAP=True` before counter imports.
It omits provider credentials, proxies and production config paths. Counter imports
must not read .env or fetch a cost map. Installed-profile no-network checks are
ordinary I3 acceptance, not a new vendor evaluation.

Control/result IPC uses four-byte unsigned big-endian length followed by strict
UTF-8 JSON, max 128 MiB per frame and bounded control/diagnostic fields; reject
oversize/malformed/unknown messages. No vendor object crosses IPC. The one trusted
application-injected pure CounterFactory may be serialized once in a separate
length-bounded pickle frame (max 1 MiB) for parent-to-child transfer; never unpickle
document data, result frames, command input or a user-supplied module name.
The child creates its local counter only when planning is requested. It retains
the converted Docling object until planning/close so no second conversion occurs.
Only validated immutable Core values reach the parent. stdout is framed IPC;
stderr is a bounded diagnostic sink, never source text in an ingestion payload.

A service permits one active session and one queued request. Further opens fail
with `worker_busy` before source I/O/spawn. Queued cancellation never launches.
`DocumentConverter.aclose` invalidates and drains all sessions/queue idempotently.
Each session keeps the same cancellation scope from conversion through planning;
late output is discarded. Cancellation and timeout signal the owned process group,
then reap it before releasing admission. Separate processes avoid sharing the
frontend GIL; they are not an OS sandbox.

### RD-03 implementation acceptance (I3-C4)

Build conversion in I3-C1, then measure the implemented worker at I3-C4 **before
accepting I3**. Neither finished worker evidence nor a spike is required for I1/I2
construction approval. Existing four-format evidence is reused as input selection,
not relabelled product-worker proof. These fixed limits are proposed acceptance
thresholds, not new measurements:

| Criterion | Pass/fail rule |
| --- | --- |
| Cold conversion | Snapshot admission through converted result <=300 s, including interpreter startup. |
| Warm asset-cache repeat | New session, same installed assets/input; result <=180 s. No global cache or reused orphan worker. |
| Process tree memory | Worker plus owned descendants <=8,589,934,592 bytes RSS; monitor tree, exceedance invalidates output and terminates. Record peak/startup/IPC timings, profile and platform. |
| Responsive parent | Representative genuine PDF/OCR/Office lane has a 100 ms async heartbeat with no gap >1 s while conversion/counting is active. |
| Queue/backpressure | One active/one queued; third busy before I/O; queued cancel never launches. |
| Cancel/timeout | Invalidate output, TERM owned group, wait <=2 s, KILL if needed, await OS reap with a further 2 s observation bound. No late output or provider/store write after cancellation wins. |
| Failed reap | Report `worker_not_quiescent`; mark service unhealthy and retain cleanup ownership/admission exclusion. No success or new work. Later confirmed reap may finish cleanup; unknown quiescence is not silently released. |
| Ownership | No frontend import; progress, direct cancel, repeated cancel, timeout, close, headless/Runtime shutdown all exercise the same service. |

Input ceilings remain those below in readiness-disposition; boundary refusal is
proved without an exhaustive performance benchmark. A bound that cannot be met
fails I3-C4 for reconciliation, never auto-increases limits or relaxes cleanup.

### Exact composition, registration and close ownership

`DIContainer` in `friday_runtime.di` adds public read-only slots
`ingestion_entry: IngestionEntry | None` and
`document_converter: DocumentConverter | None`, initially None, and
`bind_ingestion(self, *, entry: IngestionEntry,
document_converter: DocumentConverter) -> None`. Registration is inert and
transfers lifecycle ownership only on success. Same object pair is idempotent;
different pair/rebinding during or after shutdown raises a typed readiness error
without closing caller-owned arguments. Composition creates the Tools converter,
LLM counter/embedder and Memory entry explicitly and registers the exact pair.
No default boot creates Docling, and no document YAML policy is added.

`DIContainer.shutdown` stops new ingestion, awaits `entry.aclose()`, then
`document_converter.aclose()`, then existing MCP shutdown. Retained close tasks
are shielded/drained across repeated cancellation. A finally path attempts each
cleanup even if an earlier close fails; preserve/report the first failure and
unknown quiescence. Repeated shutdown joins the same cleanup task, never returns
false success. Existing extraction drains remain ordered before closing clients.

Chat does not use this container: its existing lifecycle builder and
`FrameworkAsyncClientLifecycle` gain optional keyword-only
`ingestion_entry: IngestionEntry | None = None` and
`document_converter: DocumentConverter | None = None`. A real-client composition
passes the same entry/converter used by registry adapters. `close()` rejects new
requests, drains entry then converter, then closes existing LLM clients, with the
same retained-task/failure rules. Fake runtime constructs no worker.

Renderer-free CLI/TUI composition can call these public factories and
`friday_runtime.di.DIContainer.bind_ingestion`, or explicitly own the pair in
try/finally around the existing RuntimeKernel. RuntimeKernel, its private `_di`,
its exports and existing CLI executable surfaces remain unchanged; this is a
reusable public capability, not a new wired CLI/TUI command. No private-field
access, RuntimeKernel patch or frontend-specific conversion engine is implied.

Chat adds `async SmartFileReader.read_document(path, *, attempt_id)` backed by
this session. Existing synchronous `read` retains text/JSON/table behavior and
**refuses the four document formats with a use-async-document-reader error**;
it must not silently block on them. Default async `/read` dispatch selects the
new method. A request holds the same cancellation state through conversion and,
for ingestion, planning/preflight; owned sessions are closed/joined before any
success is exposed. Persistent requests separately retain shared admission until
all owned work and storage eligibility checks finish.

No `app.py` edit is selected. The current app serially awaits registry execution
before writing a result; its finally path then enters coordinator/client cleanup.
Registry return is the read result's publication boundary. The handler catches
cancellation only to invalidate and drain, then re-raises; it cannot return a
late result. An inner retained cleanup task is shielded and repeatedly awaited
after repeated cancellations until the worker is reaped, then cancellation is
re-raised. A cancellation after registry return reaches the app before/while its
next await, rather than allowing an abandoned worker to publish later. Chat's
request owner is registered on runtime and `FrameworkAsyncClientLifecycle.close`
drains remaining owners before closing LLM clients; fake runtime owns no worker.
Actual `FridayChatApp.run` cancellation/shutdown must be tested. If these permitted
seams cannot satisfy publication/drain, stop for scope reconciliation; never
silently edit app.py or weaken the witness.

## 5. Namespace identity, vectors and recovery

Memory implements `StoreOpenRequest` in the Core submodule with exact fields:
`intent: Literal['create_fresh','open_matching','ephemeral']`,
`vector_root: Path | None`, `graph_path: Path | None`, `wal_path: Path | None`,
`recovery_root: Path | None`, `log_root: Path | None`,
`path_origin: Literal['unset','default','config','environment','constructor','testing']`,
`space: EmbeddingSpaceIdentity`, `ephemeral_scope: Id | None`.
Only config/environment/constructor/testing are explicit; resolving a fallback
string in CLI never upgrades origin. Runtime captures suppliedness before merging
defaults. Existence/layout checks and local capability checks precede clients,
logs, provider probes and directory creation. Existing graph/WAL or incompatible
journals refuse even when vector root is absent; unrelated Runtime state retains
the parent's exact operation-matrix behavior. Core factory forwards this request;
no alternate-root probing, inferred stamp or fallback embedder.

Persistent namespace marker is `embedding-space.json` at the admitted vector root.
Strict record fields are `schema_version=1`, `state: pending|ready`, `namespace_id`,
`incarnation`, `space` (the exact identity), `space_sha256`, `layout_sha256`.
Layout hashes normalized vector/graph/WAL paths (null remains null); sidecar bytes
never include credentials. Creation uses exclusive root creation, owner-only
pending marker, file fsync and parent fsync; initialize clients only afterwards;
ready replacement uses same-directory exclusive temp, fsync and atomic replace,
then directory fsync. A pending/malformed/raced/pre-existing-unbound destination
is not repaired. Matching reopen checks marker, exact layout and expected space.
No provider or client effects on refusal. Metadata-only consumers require an
admitted namespace but do not construct embeddings merely to inspect it.

Per-kernel ephemeral clients use a unique explicit Chroma tenant/database scope
bound to the ephemeral identity for every vector/CollectionManager participant;
no persistent CollectionManager inside an ephemeral/testing profile. Qualification
must prove two kernels cannot see or mutate each other's collections; unsupported
pinned-client behavior stops FC-09 rather than falling back to shared defaults.

`PreparedVector` identity/role/input hashes travel to queries, graph reserved
properties and storage through declared adapters. Missing graph components retain
existing sync/async-no-fallback zero contribution; async qualified fallback only
fills absent components using document role. Present invalid/foreign vectors
refuse, never become zero/backfill. Maintained Chat/Runtime recall stays unscored.

Memory adds separate strict `MemorySnapshotManifestV2`, `ChromaLogicalSnapshotV2`
and `VectorSnapshotManifestV2`. Each retains the complete existing v1 fields and
constraints; schema_version becomes Literal[2] where already versioned, and all three v2 models add `binding: DestinationNamespaceBinding` (all fields
of DestinationBinding except collection) and `binding_sha256`. Existing v1 classes
remain unchanged. `VectorSnapshotManifestV2` explicitly declares
`artifact_schema_version: Literal[2]`. V2 nested records retain source vectors and
reserved identity metadata without recomputation. Loader
`load_memory_snapshot_manifest(path: str | Path) -> MemorySnapshotManifest | MemorySnapshotManifestV2`
dispatches exact 1/2 once; `load_active_memory_snapshot_manifest(path) -> MemorySnapshotManifestV2`
refuses v1. No parse-failure fallback, unchecked cast or generic-store change.

Chat adds `RecoveryBundleManifestV2` with its existing full v1 fields/validators,
`schema_version=2`, `memory: MemorySnapshotManifestV2`, and existing Transcript-v1
payload. Public strict inspection/active loaders mirror Memory; active coordinator,
artifacts and rollback only accept the v2 type, reparse referenced participant
artifacts and compare payload/hash/binding/run identities. Allowed combinations
are only bundle1/memory1/vector1/transcript1 for offline inspection and
bundle2/memory2/vector2/transcript1 for guarded active use. The existing Chat
path-only fingerprint/journal/schema stay unchanged. Compute the Memory v2
participant fingerprint lazily from current admitted paths/binding, not in a
constructor before fresh namespace creation. Same-space different incarnation,
foreign layout or altered marker refuses restore; a snapshot never restamps or
replaces the live marker. Legacy physical BackupManager remains the narrow FC-03
copy behavior with non-colliding private evidence names, not a repair of FU-014.

Canonical JSON for all new hashes is UTF-8
`json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)`
with no newline. Schema serializers emit every declared optional key as JSON null,
reject unknown/duplicate keys and booleans in integer slots, serialize Paths as
normalized strings and tuples as arrays. Hash values exclude their own digest
field. Exact identity/plan/receipt vectors are in [digest-vectors.json](digest-vectors.json);
they are deterministic design examples, not qualified models or product execution.
