# Proposed TELEM-03 safe LLM event contract

Status: proposed; not approved. Date: 2026-10-06. Schema version: 1.
Bound to [CD-003](directives/CD-003-safe-llm-metrics.md).

## Closed schema and identity

Use immutable typed models with runtime enforcement of allowed fields, literal
names/enums, finite nonnegative numeric values, true booleans and safe opaque IDs.
Reject unknown keys, nested payloads, bool-as-int, negative/nonfinite values,
malformed IDs and out-of-range signed64-bit integers before delivery. Serialization
omits unavailable optional values: no None or raw object reaches TelemetryInterface.
Strings are only enums, currency USD, or generated lowercase hex identifiers;
no dynamic model/service/error strings. Retained state and diagnostics are bounded.
Request, attempt, batch and model identifiers contain exactly 32 lowercase hex
characters; session_ref and pricing_ref contain exactly 16. Each serialized event
has at most 32 scalar attributes. Oversized values/events are rejected locally.

| Event | Required attributes | Optional attributes |
| --- | --- | --- |
| llm.request_start | schema_version=1, request_id, operation, api, service_role, model_ref | session_ref |
| llm.attempt_finish | same request identity, attempt_id, attempt_number, outcome, duration_ms | batch_id, batch_number, error_category |
| llm.batch_finish | same request identity, batch_id, batch_number, outcome, attempt_count, item_count, duration_ms, usage_state | input_tokens, total_tokens, error_category |
| llm.request_finish | same request identity, outcome, attempt_count, batch_count, duration_ms, usage_state, usage_coverage, cost_state | reported token counts, estimated USD costs, price_source, price_match, pricing_ref, first_text_ms, chunk_count, finish_reason, error_category |

Closed event fields include the optional currency=USD when estimated costs exist.

"Same request identity" means schema_version, request_id, operation, api,
service_role and model_ref, plus session_ref when the Chat observer supplies it.
operation is chat or embedding. api is typed_completion, legacy_completion,
typed_stream, legacy_stream, embedding_query or embedding_documents.
service_role is unspecified, primary, embedding, maintenance_default,
maintenance_synthesizer, maintenance_classifier, maintenance_researcher,
maintenance_judge, extraction, passage_router, compaction, smart_file_summarizer,
smart_file_synthesizer or maintenance_embedding. No arbitrary configured role/name.

request_id is a new UUID hex per logical invocation; attempt_id is new per actual
litellm.acompletion/aembedding invocation; embedding batch_id is new per dispatched
batch. One-based attempt_number is global within its logical request, including
all batches. batch_number is one-based. Counts are zero before dispatch. model_ref
is an opaque random per-service-instance ID, never a hash/echo of a model string.
session_ref is added by the existing Chat observer using its accepted session policy;
direct service injection does not manufacture session/turn correlation. Legacy
ConversationContext remains available to the application/callback path but its raw
IDs, parent spans and workflow/service metadata are omitted from core events.

Service roles identify construction, not dynamic operation provenance. Preserve
existing alias identity: legacy compaction may reuse researcher/default and extraction
may reuse maintenance_default. Report the actual constructed service role in those
cases, document the alias, and never relabel a shared instance's role per concurrent
caller. Explicit maintenance registry services use the four fixed maintenance roles
and maintenance_embedding. Services made outside Chat default to unspecified.

## Request, attempts and outcomes

Emit one logical start and finish when an invocation begins executing, including
validation errors, cache hit and empty input; uniterated async generators execute
nothing and emit nothing. "Exactly one" is the emission attempt, not a delivery
guarantee when a sink fails. Each real provider dispatch has one attempt_finish,
including successful retries, timeout and cancellation. Circuit preflight denial,
validation failure and cache hit have zero dispatches. Circuit behavior stays intact.

outcome is success, error, cancelled, incomplete, cache_hit, empty_input or blocked.
Attempt/batch outcomes use success/error/cancelled; request outcome additionally
supports the others. blocked means no dispatch due to open circuit. Generator
aclose before natural exhaustion is incomplete; cancellation is cancelled, never
success. Request success requires completed application parsing/stream exhaustion.
An attempt can succeed while later parsing fails: preserve both facts.
error_category is timeout, rate_limit, authentication, invalid_request, model,
network, circuit_open, unknown or none (omit none). Classify by explicitly known
exception types/controlled wrapper metadata; never inspect error messages or call
arbitrary error stringify. Unknown subclasses stay unknown without raw names.

Use monotonic elapsed milliseconds. first_text_ms runs from logical request start,
including setup/retries/backoff, to the first nonempty text delta; omit if no text.
It is time to first text, not a measured first token. chunk_count counts raw stream
chunks received, not word/token estimates. Reasoning/tool deltas are preserved for
application delivery and never exported as content. finish_reason is stop, length,
tool_calls, content_filter or other; arbitrary provider reasons map to other.
Streaming setup retry semantics stay intact; read failures never restart a stream.
No unbounded per-chunk/inter-token arrays, prefetch or extra network requests.

Record finalization on BaseException paths where needed, re-raising the original
cancellation/GeneratorExit/exception. Telemetry sink failures are ordinary Exception
only; do not swallow a caller's cancellation or process-control BaseException.
Close an acquired stream on explicit early close, failure, timeout or cancellation;
preserve an already active primary exception if cleanup also fails. Normal read,
event ordering, timeout implementation and backpressure stay compatible.

## Usage and cost truthfulness

usage_state is reported, unavailable or invalid. Missing fields are omitted;
explicit reported zero is retained. Accept actual nonnegative integral provider
counts, with bool/nonfinite/negative/overflow rejected as invalid telemetry without
changing application response parsing. Optional fields are input_tokens,
output_tokens, total_tokens and reasoning_tokens. Do not invent totals, convert
words to tokens or replace absence with zero. Extract presence from raw responses
before existing application defaults erase the distinction.

Streams may report usage after a FinishEvent. Inspect all raw chunks through
natural exhaustion, both text-only and typed APIs. Use the final cumulative usage
snapshot once, never sum repeated cumulative snapshots. Invalid or contradictory
final snapshots remain visibly invalid; do not silently fall back to an earlier
apparently valid count. Preserve existing application UsageEvent shapes/order.

usage_coverage is complete, partial or none. Complete covers the returned successful
result/all successful embedding batches, not billing for unknown failed attempts.
Partial retains known successful-batch totals when later batches fail or usage is
missing; omit any token total whose required components are unknown. Cache_hit and
empty_input have no provider usage/cost; no fabricated zero billing. Batch events
retain available per-batch usage; request sums each successful batch once only.
Explicitly document that failed attempts may incur unknown provider charges.

cost_state is estimated, unavailable or invalid. Estimated means a calculation
using reported usage and local rates, never invoice/actual billing. Emit only with
complete required usage and finite nonnegative rates/results; partial/unknown usage,
disabled pricing or unpriced model means unavailable. Invalid configured pricing
means invalid telemetry cost without changing existing calculate behavior.

The additive typed pricing API exposes source: builtin_2025, custom_config,
supplied_table or fallback; match: exact, provider, base_model, prefix or fallback.
Keep existing lookup order and numeric calculate results. Built-in prices are the
repository's historical early-2025 table, not verified current prices. Config values
are caller-supplied, not authoritative billing. pricing_ref is a bounded digest of
the effective numeric rate pair/source/match only; no raw model/pricing_model/config
names. USD amounts are optional input_cost_usd/output_cost_usd/total_cost_usd;
finite values only, with the existing rounding. Local provider zero-rate match
is an estimate with explicit provenance. No external pricing lookup or table refresh.

## Delivery, ownership and safety

The shared safe helper uses only TelemetryInterface.capture_event for these events;
no new abstract method or LLM spans. Service constructors retain telemetry=None and
existing call shapes, narrow sink typing to TelemetryInterface and add optional
keyword-only service_role. Factories likewise add only optional keyword-only
telemetry. No process-global callbacks/context/env writes or provider coupling.

Capture ordinary sink failures in bounded local safe-helper diagnostics (maximum
256 retained records, content-free category/counters); expose a typed snapshot.
Never retain the exception object, raw payload or arbitrary sink strings. Chat
keeps its accepted 256 diagnostic/128 active-span caps and MCP/lifecycle rejection
rules. Extend capture_event with explicit LLMEvent validation, never a prefix-wide
dict pass-through. Finite floats are permitted for LLM timing/cost only; existing
closed lifecycle/MCP validators continue to control their own payloads.

Enabled real-runtime assembly passes the same borrowed observer to all inventoried
constructors before use. Disabled assembly passes None and has no sink emissions.
Construction does not invoke an LLM or start exporter/channel/provider callbacks.
No runtime/factory/observer closes a borrowed sink. TELEM-01 defaults and TELEM-02
managed OTel ownership remain unchanged. Public legacy helpers remain compatibility
APIs outside this safety guarantee; instrumented services do not call them.
