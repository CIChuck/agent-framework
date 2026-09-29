# Construction Directive: MCP-WS-06 Memory Compatibility And Optional MCP Ingestion

Status: Reconciled draft construction directive; implementation approval pending
Date: 2026-09-29
Workstream: `MCP-WS-06`
Readiness: [WS-06 checkpoint](../execution/WS-06-readiness-checkpoint.md)
Preparation HEAD: `6890771127e405f3299ed783296174366c67f995`
Preparation branch: `feature/friday-mcp-ws05-execution`
Proposed execution branch: `feature/friday-mcp-ws06-memory`
Execution base: Pin the committed planning checkpoint after explicit approval.

## Authority And Approval Boundary

Maintainer instructions and [AGENTS.md](../../../../../AGENTS.md) govern first,
followed by [engineering policy](../../../../reference/policies/repository-engineering-policy.md),
[lifecycle policy](../../../../reference/policies/development-task-lifecycle.md),
and [independent validation policy](../../../../reference/policies/independent-validation-policy.md).
Apply accepted WS-00 through WS-05 contracts, directives, amendments and closeouts;
then the [build plan](../build-plan.md), [tactical plan](../tactical-plan.md),
[rebaseline](../rebaseline-2026-09-27.md), and this bounded directive.

WS-05 is explicitly accepted at `cca86b51105666d12c2e7ed571f8f9a05d2085f9`
with fresh complete [VAL-013](../validation/VAL-013-report.md). The maintainer's
"proceed" authorizes the recorded WS-06 planning/readiness gate. This new product
manifest remains unapproved. Record explicit directive approval, pin the planning
commit, create the proposed branch and record started execution before product
code. The wider initiative remains started/granted/normal/local.

The historical draft names a nonexistent Chat `memory/` directory and broad
package edits. Actual integration uses `FrameworkMemoryAdapter`, public Memory
storage/retrieval interfaces, and the real append-only transcript adapter. WS-04
already passes the reduced memory budget; WS-05 supplies safe per-call facts.
Frozen predecessor authorities and independent evidence remain unchanged.

## Objective And Exact Allowed Manifest

Add explicitly opted-in, sanitized MCP snapshot ingestion with auditable per-call
provenance, fail-closed publication, source labels and retrieval filters. Preserve
ordinary conversation/file/native-tool memory and accepted execution, transcript,
budget and ownership behavior.

Exactly 18 implementation paths are allowed: nine source files, eight test files,
and one implementation report:

- `packages/friday-memory/src/friday_memory/models/mcp.py`
- `packages/friday-memory/src/friday_memory/ingestion/mcp.py`
- `packages/friday-memory/src/friday_memory/retrieval/mcp.py`
- `packages/friday-memory/src/friday_memory/retrieval/collection_manager.py`
- `packages/friday-memory/src/friday_memory/maintenance/mutation.py`
- `packages/friday-chat/src/friday_chat/memory_mcp.py`
- `packages/friday-chat/src/friday_chat/runtime.py`
- `packages/friday-chat/src/friday_chat/adapters.py`
- `packages/friday-chat/src/friday_chat/turns/processor.py`
- `packages/friday-memory/tests_memory/test_mcp_memory.py`
- `packages/friday-memory/tests_memory/test_retrieval/test_collection_manager.py`
- `packages/friday-memory/tests_memory/test_maintenance/test_mutation_participant.py`
- `packages/friday-chat/tests_chat/test_mcp_memory.py`
- `packages/friday-chat/tests_chat/test_mcp_execution_transcript.py`
- `packages/friday-chat/tests_chat/test_mcp_turn_budget.py`
- `packages/friday-transcript/tests/test_mcp_provenance.py`
- `tests/integration/test_mcp_memory_ingestion.py`
- `docs/planning/active/friday-mcp/execution/WS-06-implementation-report.md`

New files are Memory `models/mcp.py`, `ingestion/mcp.py`, `retrieval/mcp.py`,
Chat `memory_mcp.py`, both `test_mcp_memory.py` files, the integration test and
implementation report. Public submodule imports suffice; do not edit suppressed
package initializers merely to re-export symbols. No dependency/lock/config change.
Memory already declares Core; Chat already declares Memory.

Other product files are read-only: Core contracts, generic native
`ToolOutputIngester`, MemoryController, MCP transport/registry/runtime lifecycle,
transcript models/stores/exporters and shared sanitizer. Existing local MCP peer
fixtures may be reused read-only. Controller readiness, approval, board/dashboard,
queue/log/index and independent review artifacts are separate process records.

## Required Implementation

### MCP-06-01: Typed Snapshot Provenance

Reuse public Core `MCPIngestionPolicy`, `MCPToolMetadata` and
`MCPToolCallProvenance`; do not create another configuration or execution-facts
authority. Add a typed Memory snapshot model and explicit storage/receipt interfaces.
Carry `source_type=mcp_tool`, accepted server/original and canonical tool identity,
call ID, actual memory record ID, transcript entry ID, trust, policy snapshot and
matched grant, sanitization/truncation and byte-size facts, capture time, freshness
and revocation assumptions. Use safe opaque IDs and fixed states. No arguments,
argument keys/hashes, env, headers, raw exceptions, sanitizer objects or detection
samples in metadata.

Use distinct `type=mcp_tool_snapshot` in persistent semantic storage: one bounded
record per eligible completed call, without arbitrary chunking or graph extraction.
Use validated flat scalar metadata and a bounded JSON encoding of the typed model;
no unrestricted `default=str` serialization. Explicitly reject inconsistent or
missing provenance. Preserve it through existing promotion/decay copies and reloads.
The short-term collection is persistent semantic storage and requires the same
opt-in as long-term storage; it is not an episodic-only exception.

### MCP-06-02: Disabled Default And Compatible Consumers

`long_term_memory_enabled=False` performs no direct MCP snapshot write or embedding
request and allocates no MCP memory ID. Keep safe transcript capture and ordinary
conversation `store_turn` unchanged. Assistant prose can mention tool-derived facts;
this work does not introduce global taint tracking or disable conversational extraction.

Use additive public optional capabilities for preparation/publication and verified
transcript receipts. Existing custom/fake adapters remain source-compatible; no
new mandatory methods on their old protocols. If explicit opt-in lacks either safe
capability, skip direct ingestion with a fixed safe decision. Never fall back to
the default-enabled native ingester, private controller internals or unverified
storage success.

### MCP-06-03: Exact Server Or Tool Grants

After the enabled gate, permit a call whose exact accepted server ID is in
`opted_in_servers` OR exact canonical Friday tool name is in `opted_in_tools`.
A server grant covers its tools; a canonical-tool grant covers only that tool.
The lists form a union of explicit grants. No wildcard, prefix, substring, case
folding, original-name matching, discovery-derived opt-in or implicit trust grants.
Record the matched grant without unsafe diagnostic strings.

Only successful, checked, redacted, correlated MCP records qualify. Failed,
blocked, unattempted, unchecked or mismatched call/name/size facts are ineligible.
Native tools never enter this path. Changed allowlists control future writes;
they do not imply deletion or revocation of existing records.

### MCP-06-04: Sanitization And Fail-Closed Publication

Sanitize the storage representation separately using public Core security with
explicit normalization, complete-content scanning, block/drop policy, detection
logging off and raw/quarantine persistence off. The accepted WS-05 safe result is
the input; never obtain or reconstruct discarded raw outputs/arguments. Keep
model-visible execution text distinct from storage text and preserve an untrusted
boundary; do not blindly unwrap execution envelopes.

Reject unsafe or oversized storage text with fixed safe decisions. Enforce
`max_ingested_bytes` on complete stored UTF-8 text including labels/wrappers/notices;
bound normalization, scan capacities and provenance encoding. No silent storage
truncation or invented sanitization facts. Accurately retain execution truncation.
Rejection is the selected quarantine policy: no raw unsafe quarantine or new database.

Allocate the turn ID once and each memory ID once. Prepare non-retrievable pending
snapshots. Verify durable contents/IDs before placing `ingestion_decision=ingested`,
`memory_ingested=True` and the actual memory ID into paired call/result facts of
the forthcoming interaction. Append through the real transcript adapter. Its
optional public receipt verifies the actual entry ID and paired per-call facts
through public store readback. Only then publish matching pending records.
Transcript entries stay append-only; no store/model/schema/exporter rewrite.

Own and await all operations. False write results, failed readback, absent
capabilities, partial failures, transcript/publication failure and cancellation
must not produce optimistic success or uncorrelated retrievable records. Removal
of unreceipted pending records is best-effort; failed cleanup leaves them excluded.
A crash can leave sanitized pending records excluded indefinitely; no automatic
crash recovery. After an immutable transcript confirms a durable memory write,
publication failure leaves that record pending; do not delete it and falsify the
receipt. Report the distinction between stored and retrievable.

Cover multi-call/mixed/repeated-name turns, retries and concurrency. Reuse owned
IDs on retries, never overwrite another record's provenance, propagate cancellation
and preserve existing turn persistence errors/cleanup. Carry actual ingestion facts
consistently into persisted pairs and returned turn records without changing the
earlier execution facts. Fixed safe diagnostics only.

### MCP-06-05: Freshness And Maintenance Boundaries

Record capture time, `freshness=snapshot_at_capture` and
`revocation=not_implemented`. Snapshots are captured data, not current external
truth. No fresh/revoked inference from a query, retry or allowlist change. Reject
malformed states and test stale/unknown historical metadata without relabeling it
current. No remote revocation, TTL scheduler, live refresh or old-database rewrite.

CollectionManager rejects pending/malformed MCP records from retrieval and blocks
pending promotion. Committed snapshots preserve provenance in stage movement.
The typed maintenance participant excludes MCP snapshots from synthesis, ordinary
fact verification and duplicate/prune plans that could merge them into native
facts. Limit `maintenance/mutation.py` edits to this eligibility guard and necessary
local typing; native maintenance behavior/authority remain unchanged. Unsupported
reprocessing that cannot preserve provenance is a stop condition.

### MCP-06-06: Reuse The Supplied Retrieval Budget

Preserve WS-04 selection/reservation before `memory.retrieve(token_limit=...)`.
Forward the exact supplied limit, including zero, to recall. Never subtract
schema/result costs twice or recreate context allocation in Memory.

Account for complete MCP snippets including labels/untrusted wrappers within the
remaining supplied limit using a documented consistent estimate. Count ordinary
snippets before adding MCP snippets; if they already exhaust the limit, add none.
Omit a snapshot that cannot fit intact; never strip its labels or expose an
unlabeled prefix. Preserve native ordering/behavior. This bounds newly added MCP
snippets under the estimate; it does not claim exact tokenizer accounting for
legacy native memory or rewrite MemoryController's item-count allocation.

### MCP-06-07: Labels, Filters And Old Records

Public Memory helpers validate provenance, exclude MCP records with
`include_mcp=False`, and format bounded safe source/trust/freshness labels when
included. This query option is not another runtime configuration authority.
Chat uses these helpers before string flattening and accounts for their labels.
Preserve the untrusted boundary in model context; sanitation does not make a
snapshot a trusted fact.

Malformed MCP-labeled records are excluded. Old ordinary records without MCP
fields keep native behavior. Do not reclassify conversation/file/native records.
Explicit diagnostics may inspect pending snapshots; normal semantic recall cannot
return them. Additive metadata only: no schema migration. Test production
Chroma/SQLite round-trips and older records.

## Acceptance Criteria And Mandatory Evidence

| ID | Required result |
| --- | --- |
| WS06-AC01 | Accepted Core policy/facts reused; typed snapshots/receipts, complete bounded provenance and actual safe record/entry/call IDs round-trip. |
| WS06-AC02 | Default makes zero direct MCP semantic writes/embedding calls/record IDs; safe transcript and ordinary/native/custom adapters remain compatible. |
| WS06-AC03 | Enabled plus exact server OR canonical-tool grant, union semantics; wildcard/prefix/case/original-name/unlisted/native/failed/unchecked negatives. |
| WS06-AC04 | Distinct complete storage sanitation, UTF-8 cap including overhead, multibyte/normalization/tiny-cap/injection negatives, no raw-bearing persistence/diagnostics. |
| WS06-AC05 | Verified durable write precedes ingested receipt; actual append-only transcript readback precedes publication; partial/false-return/cancel/retry/concurrency/crash-pending/multi-call cases truthful. |
| WS06-AC06 | Honest snapshot/no-revocation assumptions; pending/malformed exclusion and pending promotion guard; provenance survives stage copies/reloads; maintenance does not turn snapshots into ordinary facts. |
| WS06-AC07 | Public helpers and production Chat retain labels/exclusion; malformed MCP metadata rejected; old/native/file/conversation retrieval remains compatible. |
| WS06-AC08 | Supplied WS-04 budget forwarded once, including zero; full MCP overhead fits residual estimated budget or snapshot omitted; native selection/reserve/floor intact. |
| WS06-AC09 | Temporary production Chroma/SQLite and existing JSONL/Markdown/CSV preserve safe actual correlations, old/native/export privacy behavior; no schema/config/dependency change. |
| WS06-AC10 | Exact manifest, meaningful typing, required checks, independent base comparisons, local public UAT, isolated-package proof, cleanup and frozen predecessor/unrelated evidence complete. |

Use synthetic inputs, deterministic embeddings/model doubles, temporary databases
and an existing real local stdio peer. Exercise production adapters, TurnProcessor
streaming/non-streaming, default/opt-in, storage reload/query and exports; helpers
alone are insufficient. Inspect logs/errors/results/context/transcript/metadata for
argument, env/header, injection and exception sentinels. Explicit process/task
cleanup in `finally`; no real credentials, memory/transcript state or provider calls.

## Verification Commands And Baseline Treatment

Set `LITELLM_LOCAL_MODEL_COST_MAP=true` and
`UV_CACHE_DIR=/private/tmp/friday-uv-cache`. Record complete outputs/exits including
failed attempts. If ordinary `uv run` requests an unavailable rebuild, disclose it
and use the installed environment with `uv run --no-sync`; this does not prove a
clean install. No network/provider/paid calls or third-party upgrades.

Run focused checks before broad checks:

```bash
uv run pytest packages/friday-memory/tests_memory/test_mcp_memory.py packages/friday-memory/tests_memory/test_retrieval/test_collection_manager.py packages/friday-memory/tests_memory/test_maintenance/test_mutation_participant.py packages/friday-chat/tests_chat/test_mcp_memory.py packages/friday-chat/tests_chat/test_mcp_execution_transcript.py packages/friday-chat/tests_chat/test_mcp_turn_budget.py packages/friday-transcript/tests/test_mcp_provenance.py tests/integration/test_mcp_memory_ingestion.py
uv run pytest packages/friday-chat/tests_chat/test_mcp_execution_security.py packages/friday-chat/tests_chat/test_mcp_chat_bridge.py tests/integration/test_mcp_execution_provenance.py packages/friday-chat/tests_chat/compat/test_tool_loop_parity.py packages/friday-chat/tests_chat/compat/test_turn_contract_parity.py
uv run pytest packages/friday-memory/tests_memory
uv run pytest packages/friday-chat/tests_chat
uv run pytest packages/friday-transcript/tests
uv run pytest packages/friday-agent/tests_agent
uv run pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime
uv run pytest tests/integration
uv run ruff check packages/friday-memory packages/friday-chat packages/friday-transcript tests/integration/test_mcp_memory_ingestion.py
uv run mypy packages/friday-memory packages/friday-chat packages/friday-transcript
uv run mypy --python-version 3.13 packages/friday-memory/src/friday_memory/models/mcp.py packages/friday-memory/src/friday_memory/ingestion/mcp.py packages/friday-memory/src/friday_memory/retrieval/mcp.py packages/friday-memory/src/friday_memory/retrieval/collection_manager.py packages/friday-memory/src/friday_memory/maintenance/mutation.py packages/friday-chat/src/friday_chat/memory_mcp.py packages/friday-chat/src/friday_chat/runtime.py packages/friday-chat/src/friday_chat/adapters.py packages/friday-chat/src/friday_chat/turns/processor.py
uv lock --check --offline
uv run python scripts/friday-dev-board.py validate
uv run python scripts/friday-dev-board.py render --check
uv run python scripts/check-documentation-lifecycle.py
git diff --check WORK_UNIT_BASE..CANDIDATE
```

Remove CollectionManager's existing file-wide ignore; all nine affected source
files must meaningfully type-check. No broad suppression, error filtering, blanket
cast or implicit waiver. Repairs stay within the manifest; stop if another source
file is needed. Independently reproduce broad failures against the unchanged
approved base with exact commands/outcomes. VAL-013's Chat PTY/localhost fixtures,
integration board-count debt and default NumPy/Python-3.10 typing failure are
historical references, not waivers. Establish Memory/Ruff/typing baseline debt too.

Build Memory/Chat/Transcript/Core wheels with existing offline tools and prove
public snapshot/receipt imports plus synthetic Chroma/SQLite typed round-trip from
installed declared distributions, without editable source/PYTHONPATH masking
missing dependencies. Disclose resolver/build/install limitations separately;
missing changed-boundary distribution proof blocks completion. No dependency edits.
Independent public local-peer UAT, failure/cancel probes and freeze checks at review
start/closeout are required.

## Non-Goals And Stop Conditions

No resources/prompts/HTTP/SSE, live refresh, automatic revocation, argument hashes,
raw quarantine, global taint tracking, MemoryController redesign, native ingester
changes, graph extraction, settings/commands/UI, telemetry emission, historical
stored snapshot cleanup, provider calls or delivery. WS-07/08 need separate
approval. Record memory behavior for later WS-08; do not write its final guide.

Stop for missing approval/branch/start; changed accepted inputs; required files
outside the manifest; unsafe/uncorrelated publication; unsupported retrieval,
lifecycle or maintenance provenance preservation; schema/dependency/config migration;
missing mandatory evidence or changed-source failures. Return a concrete gap before
further product edits, not an inferred waiver.

## Report, Independent Review And Acceptance

Report all seven tasks/ten criteria with actual files, behavior, tests and exact
outputs. Include policy/defaults, stored-versus-published failures, provenance
encoding, sanitizer limits, labels/budget estimate, compatibility, immutable
receipts, maintenance guards, baseline debt, distribution proof and cleanup.

Freeze a stable scoped candidate. Fresh read-only `VAL-014` receives exact authority
hashes, approved base/candidate aggregate, criteria/checks/public evidence and no
builder/controller private reasoning or forked conversation. Repository policy
requires that subagent after code generation. Archive its complete independent
report/evidence byte-exact. Complete aggregate VERIFIED precedes proposed closeout;
only the maintainer records acceptance. Later phases/delivery remain separate.
