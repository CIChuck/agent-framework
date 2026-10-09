# Approved TELEM-04 contract: correlated execution and local diagnostics

Status: approved by Chuck Russell on2026-10-09; prepared2026-10-07 for CD-004.
Preparation base: e6209e3156216afde1655758e280690229f7d3e6.

## Boundary and compatibility

Instrument Friday Chat's existing execution boundaries using its borrowed,
provider-neutral observer. Keep TelemetryInterface's three methods and the
accepted LLM/MCP event models and payloads unchanged. Do not connect historical
raw memory or LLM hooks. Add a version-one execution event family and explicit
links to validated accepted events. Shared LLM services require no modification.
Headless RuntimeKernel adoption and optional Langfuse are separate work; this
unit does not claim framework-wide instrumentation of every memory invocation.

New public surfaces are closed execution models, a typed correlation context and
scope helper, and immutable diagnostics snapshots. Friday Chat TurnResult and
PendingExtractionTurn may gain an optional final field containing safe immutable
correlation metadata, default None. Existing positional fields, return values,
exception behavior, tool selection, retry policies and persistence formats stay
compatible. Adapter observation fields/constructor keywords default None. Disabled
runtime construction must preserve the accepted old call shape for test doubles.

## Identities and scopes

Use the accepted session_ref (16 lowercase hex), newly generated random turn_ref,
operation_ref and optional parent_operation_ref (32 lowercase hex). Never reuse
raw persisted turn, tool-call, user, session, model or document IDs, or hash their
content into new references. A fresh turn_ref is created before admission/selection
and retained through retrieval, model calls, tools and persistence. A blocked turn
still has a terminal observation but performs no extra application work.

The observer owns a task-local typed scope, bound and reset with context tokens
in finally, including BaseException/cancellation paths. The scope's non-exported
owner identity prevents foreign-session bindings; no process-global current-turn
dictionary, last-turn lookup or incidental sink attribute introspection. A scope
creates child operation references without storing raw arguments or responses.
Nested invocations and concurrent sessions cannot overwrite each other's lineage.

Return the safe context with a successful TurnResult and pass it explicitly from
the app to background extraction scheduling. PendingExtractionTurn retains its
origin context across the existing retry/preemption/requeue path. Each extracted
item rebinds that origin within a new operation. A batch of different turns must
not borrow its first item's identity for the whole batch. Old work items with None
context are explicitly uncorrelated. Background entry clears inherited foreground
scope; finished foreground operation/span IDs are causal references, never parents
of newly opened active SDK spans. No changes to queue ordering or commit recovery.

## Closed event schema

Every execution event uses schema_version=1, strict frozen/revalidated models,
extra=forbid, finite nonnegative milliseconds, strict counts bounded to signed
64-bit, declared enums, references validated at runtime, and at most32 flattened
scalar attributes. Omit absent values; reported zero remains zero. Reject nested
payloads, NaN/Inf, bool-as-count, overflow, unknown enums, forged models and unknown
keys before recording, metrics aggregation or sink delivery. Event names:

| Name | Meaning and fields in addition to safe identity |
| --- | --- |
| execution.turn_start | Admission to one public process/process_streaming invocation; mode=completion/streaming |
| execution.turn_finish | Exactly one terminal outcome; duration_ms; persistence=not_started/partial/completed/failed/cancelled; bounded completed/failed tool counts |
| execution.operation_start | One actual operation begins; operation_kind and optional parent_operation_ref |
| execution.operation_finish | Same operation_ref; terminal outcome, duration_ms, optional count/count_kind, persistence_state when known |
| execution.selection | Snapshot of selected/rejected native/MCP counts, schema_tokens, context_budget_tokens, opaque toolset_ref and closed rejection reasons |
| execution.reasoning_history | One actual follow-up model dispatch; iteration, present/preserved/eligible boolean facts, optional required flag and message_count; no reasoning text |
| execution.llm_link | One validated llm.request_start linked by accepted request_id to the active execution context; request/attempt/batch accounting remains owned by accepted LLM events |
| execution.mcp_link | One validated MCP observation projected with source_event, source_sequence, existing safe server_ref/tool_ref/reason/count and active execution context |

operation_kind is closed to model_call, native_tool, mcp_tool, memory_retrieve,
memory_store_turn, memory_ingest_document, memory_extract, transcript_record_turn,
transcript_context_log, transcript_interaction and persistence. Terminal outcome
is succeeded, failed, cancelled, incomplete, blocked, skipped or pending. Reasons
are closed categories: timeout, retry_exhausted, circuit_open, selection_rejected,
unknown_tool, tool_error, invalid_result, execution_error, output_rejected,
persistence_failed, extraction_failed, cancelled, unavailable or unknown. No
exception string or arbitrary class name is serialized. Normal completion is not
proof of MCP success: use its already validated status/failure/sanitization facts.
Selection reasons reuse the existing ToolRejectionReason enum, not arbitrary text.

An opaque toolset_ref identifies a single selection snapshot; it is not a stable
cross-process hash of tool names/schema. Rejections may be aggregated by the closed
reason enum. No per-tool-name mapping or unbounded set of seen identifiers.
MCP links preserve accepted event meaning and safe refs; source_sequence is the
observer-local original diagnostic sequence, not a provider call ID. Original
MCP payloads remain byte-equivalent. The new projection supplies correlated
observation; it does not claim the old MCP event independently carries a call ID.
Only links created inside a valid scope are correlated; outside events retain
accepted behavior without fabricated turn references. Every link is independently
validated; invalid originals cannot generate links or metrics.

## Placement, persistence and reasoning truth

TurnProcessor owns a turn scope around both public execution paths, and operation
scopes around selection/retrieval, every actual outer model call, tool dispatch and
persistence. Outer model calls and inner LLM attempts are distinct accounting
layers; no inferred provider-attempt count. Preserve streaming chunk order,
callback exceptions, heartbeat behavior and stream closure. No prefetch/read-ahead.

ToolLoop owns one operation per actual native/MCP invocation. Unknown/disallowed
calls produce a rejection observation without claiming dispatch. Observe swallowed
KeyError before preserving its existing control flow. Preserve MCP sanitization,
provenance validation, accepted ID repair and tool-loop results. A returned failed
or blocked MCP record cannot increment succeeded-tools counters.

Instrument memory retrieval/store and ingestion at the existing Chat boundaries;
instrument actual extraction per item in FrameworkMaintenanceAdapter. No fabricated
retrieval score, entity count, ingestion count or commit acknowledgement. No-extractor
and empty cases are skipped, not committed extraction successes. Observe the
existing ExtractionCommitCompletedUnderCancellation distinctly: the operation
records completed persistence with cancelled outcome while cancellation propagates.

Persistence observations occur around each existing awaited memory/transcript/context
log call and the accepted persist_mcp_interaction coordination. Intermediate
completions are retained as partial when a later call fails. Turn success is emitted
only after the complete existing persistence path returns; never promise atomic
rollback across independent stores. MCP receipt_committed and published/pending
remain separate accepted truths. A successful transcript receipt with pending memory
publication does not claim published ingestion. Raw transcript capture behavior is
unchanged; telemetry cannot export its prompt, response or path. Cancellation that
does not expose a public commit fact is unknown/incomplete, not fabricated success.

Before each follow-up model call, inspect the actual outgoing assistant history
after accepted redaction and before dispatch. Report only booleans/counts showing
whether available required reasoning was preserved. Preserve accepted MCP reasoning
redaction; unavailable/removed reasoning is not exported or reconstructed. This is
observational work: no change to reasoning-history construction/provider requests.

Here eligible means retention is permitted by the accepted native/MCP history
rules; present and preserved compare supplied reasoning with the actual outgoing
history. An optional required flag may be supplied only by an existing explicit
typed provider policy. Omit it when unknown; never infer a provider requirement
from a model-name string or label eligible reasoning as a verified provider mandate.

## Spans, failures and bounded metrics

Add only closed chat.turn and chat.operation span names to the observer, retaining
the existing128-open-span bound and strict SpanOutcome end payload. TurnProcessor
may own a span throughout its awaited process/process_streaming call. Operation
spans nest under that turn or an active operation. Public async-generator yields
must not retain a new ambient span. Existing stream_process buffers through
process_streaming; leave that behavior unchanged. Explicit close, context restoration
and primary-exception preservation are mandatory on every exit. Provider span IDs
remain private. No new exporter, callback registration or global OTel provider.

Ordinary sink/schema failures are locally diagnosed and cannot replace application
results, primary exceptions or cancellation. Failed starts/ends and dropped span
capacity are visible, and no missing delivery is claimed successful. Borrowed sinks
are never flushed/closed. Execution observation creates no new service calls or
database writes.

Retain accepted256 diagnostic records and128 open spans. Add at most32 compact
terminal-turn summaries. Use fixed operation/outcome counter keys and duration
histogram buckets <=1,5,10,25,50,100,250,500,1000,5000ms and >5000ms. Counters saturate
at signed64-bit maximum. Increment once from validated operation_finish/turn_finish;
LLM/MCP originals and links never increment these counters. Label dimensions are
only closed operation/outcome enums; references, source sequences and service/tool
names never become metric labels. Histogram measurement is observed elapsed time,
including failures, with no missing/invalid sample silently entered as zero.

Immutable local snapshots support exporter-off/failed inspection. Extend existing
/debug and /timing rendering with these safe summaries, including failed turns that
have no TurnResult, while preserving existing prompt/context commands and successful
timing fields. The snapshot is the provider-neutral operational metric surface;
OTel Meter/histogram instruments and persistence of diagnostics are deferred.

Default telemetry contains no prompts, messages, reasoning, tools' names/arguments/
results, document paths, memory contents, vectors, endpoint/config/credential data,
raw IDs, text hashes or exception messages. No new raw-capture option in this unit.
