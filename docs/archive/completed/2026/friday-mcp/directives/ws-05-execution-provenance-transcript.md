# Construction Directive: MCP-WS-05 Tool Execution Security, Provenance, And Transcript Recording

Status: Approved construction directive
Date: 2026-09-28
Workstream: `MCP-WS-05`
Readiness: [WS-05 checkpoint](../execution/WS-05-readiness-checkpoint.md)
Preparation base: `1e845001f6b6c48e7cc255ac76460a058f026f70`
Execution base: `a609f948fe2d869ac29d0cce29d22d9334cd7d08`

## Authority And Approval Boundary

Explicit maintainer direction and repository policy govern first:
[AGENTS.md](../../../../../../AGENTS.md),
[engineering policy](../../../../../reference/policies/repository-engineering-policy.md),
[lifecycle policy](../../../../../reference/policies/development-task-lifecycle.md), and
[independent validation policy](../../../../../reference/policies/independent-validation-policy.md).
Then apply accepted WS-00 through WS-04 contracts, directives, amendments and
closeouts; the [build plan](../build-plan.md), [tactical plan](../tactical-plan.md)
and [rebaseline](../rebaseline-2026-09-27.md); this directive binds the new slice.

The maintainer explicitly approved this complete bounded directive on
2026-09-28 with "ws-05 is approved. proceed" after the planning checkpoint
`a609f94`. WS-00 through WS-04 stay accepted. Execution starts on
`feature/friday-mcp-ws05-execution` from the full base above; the board and
packet record that start before product generation. Approval covers exactly
this WS-05 slice and its required fresh independent review, not later workstreams
or delivery. Historical VAL-010 reviewed product remains the accepted predecessor;
only the new WS-05 approved paths may change.

The original generic plans mention argument hashing and `export/`. Accepted
WS-00 rejects raw arguments, results and argument hashes in shared provenance:
this slice selects full argument redaction, with no hashes or salt feature.
The actual transcript directory is `exporters/`. Accepted predecessors and
frozen plans are not rewritten to reconcile those historical proposals.

## Objective And Exact Allowed Manifest

Implement a safe Friday Chat MCP execution boundary, atomic typed per-call
provenance, and compatible transcript persistence/exports. Every attempted MCP
call must produce bounded safe output and accurate success/failure facts before
model re-entry or capture. Native tools retain existing execution behavior.

Exactly 23 implementation paths are allowed: twelve source files, two dependency
metadata files, eight test/fixture files, and one implementation report:

- `packages/friday-core/src/friday_core/mcp.py`
- `packages/friday-mcp/src/friday_mcp/client/base.py`
- `packages/friday-chat/src/friday_chat/tools/schemas.py`
- `packages/friday-chat/src/friday_chat/tools/loop.py`
- `packages/friday-chat/src/friday_chat/tools/mcp.py`
- `packages/friday-chat/src/friday_chat/tools/output.py`
- `packages/friday-chat/src/friday_chat/turns/processor.py`
- `packages/friday-chat/src/friday_chat/adapters.py`
- `packages/friday-transcript/src/friday_transcript/models/transcript.py`
- `packages/friday-transcript/src/friday_transcript/exporters/jsonl.py`
- `packages/friday-transcript/src/friday_transcript/exporters/markdown.py`
- `packages/friday-transcript/src/friday_transcript/exporters/csv.py`
- `packages/friday-transcript/pyproject.toml`
- `uv.lock`
- `packages/friday-core/tests_core/test_mcp_contracts.py`
- `packages/friday-mcp/tests_mcp/client/test_execution.py`
- `packages/friday-chat/tests_chat/test_mcp_execution_security.py`
- `packages/friday-chat/tests_chat/test_mcp_execution_transcript.py`
- `packages/friday-chat/tests_chat/test_mcp_chat_bridge.py`
- `packages/friday-transcript/tests/test_mcp_provenance.py`
- `tests/integration/test_mcp_execution_provenance.py`
- `packages/friday-chat/tests_chat/fixtures/mcp_execution_peer.py`
- `docs/planning/active/friday-mcp/execution/WS-05-implementation-report.md`

New paths are Chat `tools/output.py`, MCP `test_execution.py`, both Chat
`test_mcp_execution_*` tests, Transcript `test_mcp_provenance.py`, the integration
test and execution peer fixture, and the implementation report. Existing files
outside this manifest are read-only. Controller approval/readiness, request,
review/evidence, queue/log/index and board/dashboard artifacts are separate
process records; they do not broaden the product manifest.

`friday-core/mcp.py` changes are additive optional call-provenance byte sizes
and fixed failure codes only. `client/base.py` changes are limited to interpreting
`tools/call` error/invalid results safely. Transcript metadata adds the declared
workspace dependency `friday-framework-core==0.1.0a2`; `uv.lock` changes only that
edge. No third-party upgrades, reverse dependency or root metadata changes.

## Required Implementation

### MCP-05-01: One Typed Per-Call Contract

Reuse public `MCPToolCallProvenance` and accepted `MCPToolMetadata`. Do not create
another provider/config/provenance authority, reach into private manager state,
or reduce shared facts to `dict[str, Any]`. Add optional nonnegative
`result_size_bytes` (original decoded text's UTF-8 length, when available) and
`model_result_size_bytes` (final safe text's UTF-8 length). They exclude JSON-RPC
and JSON escaping overhead. Unknown sizes are absent rather than invented.
Add optional fixed literal `failure_code`, limited to `tool_error`,
`invalid_result`, `execution_error`, `timeout`, and `output_rejected`; no raw
exception or peer text. Reject contradictory success/failure facts. Preserve
old DTO payloads without new fields.

Extend frozen Chat `ToolCallRecord` with optional typed MCP provenance after its
existing four fields; old positional/native/fake records remain compatible.
A public optional recording boundary may return the atomic safe record; retain
existing native/fake `call_tool -> str` compatibility. Public MCP Chat
`call_tool` must itself return the same safely processed result, so direct calls
cannot bypass policy. Do not sanitize twice or cache raw output/arguments.

Populate exact accepted provider/server/original/canonical name, transport,
trust and schema state; call ID; status; redaction, sanitization, truncation and
size facts; disabled ingestion; and actual correlation IDs when assigned.
Keep each call distinct in mixed/multi-call turns, including repeated tool names.

Preserve valid unique `MCPSafeIdentifier` call IDs. Replace missing, invalid or
duplicate MCP IDs with opaque safe unique IDs; correlate assistant requests,
tool-result messages and transcript records consistently. Native IDs retain
existing behavior. Unsafe raw IDs must not reach diagnostics or persisted copies.

### MCP-05-02: Redact All MCP Arguments At Capture Boundaries

Pass original arguments and exact original MCP tool name unchanged to execution.
Before returning records, retaining continuation/history, constructing prompt
capture/raw response, diagnostics or persistence, replace MCP argument objects
with `{}`. No argument values, keys, stable hashes, redacted value summaries,
raw request serialization or peer exception text may survive in those channels.

Redact/omit MCP tool-request content as well as structured tool-call arguments;
serialized assistant requests must not bypass redaction. Apply this to
`TurnResult`, fallback responses, streaming and non-streaming tool turns,
optional raw-prompt/context logs, production and fake transcript adapters.
Native-only and mixed native portions keep existing contracts. User-authored
messages are not rewritten. This does not promise removal of arbitrary secrets
from general user/LLM prose or semantic secret classification of benign outputs.

### MCP-05-03 And MCP-05-04: Complete Bounded Output Processing

Implement the Chat consumer policy in `tools/output.py`, reusing public
`friday_core.security` without changing shared sanitizer/agent source. Treat MCP
outputs as untrusted/high-risk. Explicitly enable normalization/detection,
block detected unsafe content, disable detection logging and raw/quarantine
storage, and retain only safe output plus typed facts. Never retain/log/repr the
raw-bearing `SanitizationResult`, detection samples, raw output or exceptions.
The existing default `warn` policy is insufficient.

Measure the original decoded text's UTF-8 length ephemerally; retain a bounded
UTF-8 prefix; normalize and scan its complete retained content; block detected
injections; wrap safe content as untrusted; and enforce `max_result_bytes` on the
entire final string, including wrappers, fixed failure text and truncation
notice. Configure scan/normalization capacities to cover all retained content,
including limits above the shared defaults. Normalization expansion must also
be bounded. Any omitted content sets explicit truncation facts and a fixed safe
notice; no omitted bytes or partial UTF-8 character/marker may leak.

Account for escaped closing markers and wrapper overhead. Peer content must not
escape the untrusted envelope. If the configured cap cannot accommodate the
complete safe envelope and required failure/truncation notices, reject the
requested MCP call before RPC with a fixed safe turn-level error. Do not execute
and then exceed the cap, silently disable policy, or fabricate an execution
record for a call that never ran. Reuse the existing configured limit without
new settings. This bounds model/persistence-facing text, not inbound wire buffers,
remote execution, arbitrary secret detection, or exact context token cost.

### MCP-05-08: Accurate Failure And Cancellation Behavior

`MCPClientBase.call_tool` must recognize boolean `isError: true` as a failure
with a fixed safe exception/code; it must not return error content as success.
Missing or false `isError` keeps valid successful text behavior. A nonboolean
flag or invalid content/text result fails with a fixed safe invalid-result
exception. Retain valid existing text-block/nontext extraction compatibility;
no discovery, transport, timeout, cleanup or adapter API changes are authorized.

The Chat boundary records failed RPC/protocol/tool/timeout executions without
raw arguments, results, env, headers, secret-bearing messages or traceback
capture. Output rejection is `blocked` with `output_rejected` and rejected
sanitization state; protocol/execution failures are `failed`. Safe failures
remain within the byte cap and can re-enter the loop. Successful benign calls
are succeeded with checked sanitization facts. Do not claim unsafe data was
safe or mark unattempted calls succeeded. `CancelledError` must propagate;
cleanup and accepted owner retry semantics remain unchanged. Do not force
persistence or invent a completed turn on cancellation.

### MCP-05-05 And MCP-05-06: Typed Compatible Transcript Persistence

Add optional `mcp_provenance: MCPToolCallProvenance | None` to transcript
`ToolCall` and `ToolResult`. Pair their per-call facts and IDs consistently;
turn-level metadata is not a substitute. Bind `transcript_correlation_id` to
the actual persisted `TranscriptEntry.id`. IDs remain absent until assigned;
reject invalid supplied MCP correlation IDs safely rather than inventing a
relationship. No MCP memory records/IDs are created.

Adapt the real `FrameworkTranscriptAdapter`, and pass safe records to fake
adapters too. SQLite's existing JSON encoding/loading requires no storage
schema/source migration. Older entries load/export without new fields; optional
MCP fields are omitted when absent to preserve native serialization shape.
Existing native tool calls/results, session queries, commands, context logs and
JSONL round-trips remain compatible. Remove existing broad mypy ignore-errors
from touched model/exporter source; use meaningful typed interface repairs
within the exact manifest, never new broad suppression or a blanket waiver.

### MCP-05-07: Fixed Export Decision

JSONL with existing metadata enabled preserves full typed per-call provenance
and safe results. Existing metadata-disabled behavior continues omitting tool
metadata; do not override the caller's privacy flag.

Markdown retains `include_tool_calls=False` by default. When explicitly enabled,
MCP calls show bounded escaped summaries: safe server/canonical name, call ID,
status, sanitization/truncation and byte counts. Native output stays compatible.
CSV retains existing columns and default tool cells; MCP cells contain bounded
structured summaries with those same fields and safe result text. Native cells
remain unchanged. Full original-name/structured provenance is available in
JSONL. Human summaries must not inject raw peer names, Markdown, CSV formulas or
control characters; use canonical/safe identifiers and fixed state labels.
Record this choice for WS-08; no new commands or user-guide phase is included.

## Acceptance Criteria And Mandatory Coverage

| ID | Mandatory result and independent evidence |
| --- | --- |
| WS05-AC01 | Single public typed provenance DTO, additive sizes/fixed codes, native four-field compatibility, consistent status/ingestion validators and declared Transcript dependency. |
| WS05-AC02 | Original arguments/names execute correctly; all MCP-owned return, continuation/history, raw capture, diagnostic and persistence argument copies are empty; no hashes, argument keys, env/header or error sentinels survive. |
| WS05-AC03 | Direct bridge, ToolLoop and both turn modes enforce final UTF-8 byte caps including wrapping/normalization/truncation/failure overhead; exact/oversized/multibyte/empty/tiny-cap cases and scan limits above defaults are covered. |
| WS05-AC04 | Entire retained output is checked under explicit block/drop policy; detected content and envelope escape attempts cannot re-enter/capture unchanged; no raw quarantine, detection samples or sanitizer repr are persisted/logged. |
| WS05-AC05 | isError true, malformed flag/content, RPC/transport/timeout and sanitizer rejection yield accurate safe failure/blocked provenance; cancellation propagates and public cleanup/retry ownership is preserved. |
| WS05-AC06 | Distinct mixed/multiple/repeated calls retain exact metadata and coherent safe unique IDs; missing/invalid/duplicate IDs and concurrent executions do not misassociate results. |
| WS05-AC07 | Production SQLite adapter and fake adapter receive only safe MCP records; typed call/result provenance round-trips with actual entry correlations; old/native records and context-log behavior remain compatible. |
| WS05-AC08 | Full structured JSONL and metadata flag semantics are preserved; Markdown opt-in and existing CSV columns implement bounded escaped summaries; native exporters remain compatible. |
| WS05-AC09 | Native/no-MCP behavior, WS-04 tool selection/result reservation/memory floor and WS-02/03 lifecycle/registry remain intact; no direct MCP long-term ingestion, telemetry emission or later-phase feature is introduced. |
| WS05-AC10 | Exactly allowed product paths, narrow lock/dependency changes, required checks, real local-peer UAT, cleanup, unchanged baselines and preservation/freeze evidence are independently reproducible. |

Use synthetic sentinel arguments/errors/env/headers only; never load or print
real credentials. Exercise the public Chat bridge, real TurnProcessor (including
model re-entry, fallback, raw-capture and streaming), production SQLite and all
exporters, not only pure helper tests. A real local stdio peer must cover successful,
large UTF-8, injected, protocol-failing, malformed and interrupted calls;
request doubles supplement the public path. Verify fixture processes/tasks
settle with explicit finally cleanup and no real provider/network calls.
Positive and negative tests must include omitted raw copies, safe exception
messages/repr/logs, export escaping, old payloads, two calls sharing a tool name,
invalid correlation IDs and benign native compatibility.

## Verification Commands And Baseline Treatment

Run with `LITELLM_LOCAL_MODEL_COST_MAP=true` and
`UV_CACHE_DIR=/private/tmp/friday-uv-cache`; use the existing workspace environment,
no credentials, paid providers, external MCP services or deployment. Record
complete command output and exit status. Focused tests precede broad checks:

```bash
uv run pytest packages/friday-core/tests_core/test_mcp_contracts.py packages/friday-mcp/tests_mcp/client/test_execution.py packages/friday-chat/tests_chat/test_mcp_execution_security.py packages/friday-chat/tests_chat/test_mcp_execution_transcript.py packages/friday-chat/tests_chat/test_mcp_chat_bridge.py packages/friday-transcript/tests/test_mcp_provenance.py tests/integration/test_mcp_execution_provenance.py packages/friday-chat/tests_chat/compat/test_tool_loop_parity.py packages/friday-chat/tests_chat/compat/test_turn_contract_parity.py packages/friday-chat/tests_chat/test_turn_processing.py packages/friday-chat/tests_chat/test_transcript_production_commands.py packages/friday-chat/tests_chat/test_transcript_export_commands.py
uv run pytest packages/friday-chat/tests_chat
uv run pytest packages/friday-transcript/tests
uv run pytest packages/friday-agent/tests_agent
uv run pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime
uv run pytest packages/friday-memory/tests_memory
uv run pytest tests/integration
uv run ruff check packages/friday-core packages/friday-mcp packages/friday-chat packages/friday-transcript packages/friday-agent tests/integration/test_mcp_execution_provenance.py
uv run mypy packages/friday-core packages/friday-mcp packages/friday-chat packages/friday-transcript packages/friday-agent
uv run mypy --python-version 3.13 packages/friday-core/src/friday_core/mcp.py packages/friday-mcp/src/friday_mcp/client/base.py packages/friday-chat/src/friday_chat/tools/schemas.py packages/friday-chat/src/friday_chat/tools/loop.py packages/friday-chat/src/friday_chat/tools/mcp.py packages/friday-chat/src/friday_chat/tools/output.py packages/friday-chat/src/friday_chat/turns/processor.py packages/friday-chat/src/friday_chat/adapters.py packages/friday-transcript/src/friday_transcript/models/transcript.py packages/friday-transcript/src/friday_transcript/exporters/jsonl.py packages/friday-transcript/src/friday_transcript/exporters/markdown.py packages/friday-transcript/src/friday_transcript/exporters/csv.py
uv lock --check --offline
uv run python scripts/friday-dev-board.py validate
uv run python scripts/friday-dev-board.py render --check
uv run python scripts/check-documentation-lifecycle.py
git diff --check WORK_UNIT_BASE..CANDIDATE
```

Additionally verify Transcript's built distribution metadata declares Core and
its public model imports work with declared dependencies, rather than relying
on the ambient editable workspace. Use existing offline build tools; if that
check is unavailable, record the exact gap and stop before claiming completion.
Run independent local-peer UAT and frozen authority/product/unrelated-path
checks at review start and closeout.

The accepted VAL-010 report records unchanged Chat PTY and three localhost
fixture errors, the integration board-count assertion, and default mypy's
NumPy/Python-3.10 syntax failure. Earlier reviews record four Core profiles.py
Python-3.13 typing failures. These are historical baseline references, not
waivers or WS-05 results. Builder and validator must independently establish
failures against the unchanged accepted predecessor/approved base, report exact
commands, run unfiltered meaningful affected-source typing, and distinguish
unchanged unrelated failures from regressions. Never repair out-of-scope debt,
filter errors to manufacture a pass, add broad ignores, or silently skip a gate.
A required changed-source failure or missing mandatory evidence blocks closeout.

## Non-Goals, Migration, And Stop Conditions

No new config or Chat command; no tool selection/memory-floor/token estimation
changes; no RuntimeKernel/native registry-wide result policy; no shared Agent
or Core sanitizer refactor; no HTTP/SSE/resource/prompt/live refresh/server work;
no long-term MCP ingestion, quarantine store, telemetry emission, argument
hashes, external config include, user-guide/release/delivery work. Ordinary
existing conversation memory writes remain unchanged and must not be described
as dedicated MCP ingestion. This consumer boundary does not guarantee arbitrary
secret or prompt-injection detection. Byte caps do not guarantee input/wire
allocation bounds or exact multi-call token budgets.

Successful MCP Chat callers now receive checked/wrapped/bounded text. Peer
`isError` results now fail instead of masquerading as success. Transcript's
additive optional fields retain old/native readability and serialization shape;
there is no SQLite migration or rewritten historical transcript.

Stop and reconcile before edits if approval/start/base is absent, accepted
predecessors or frozen inputs drift, another source/test/dependency path is
needed, declared Core dependency cannot remain acyclic/minimal, the public
sanitizer cannot enforce complete retained-prefix safety within the cap, raw
copies cannot be eliminated at capture/model boundaries, or old/native exports
would break. Stop before closeout for new test/type failures, missing evidence,
unsettled peer cleanup or lack of a fresh independent validator. No automatic
security/package remediation is approved by this directive.

## Reporting And Independent Review

The implementation report must list exact files/base/candidate, all eight
tactical tasks and ten criterion outcomes, public DTO/dependency changes,
argument/result/failure/cancellation handling, byte/correlation semantics,
export decision and migration, full commands/exits, baseline reproduction,
skipped/unavailable checks, local UAT, resource/preservation/freeze results and
remaining WS-06/07/08/delivery gates. Preserve raw logs as controller evidence
without secrets or runtime databases.

Commit a stable candidate. Prepare VAL-011 with the exact approved base,
complete WS-05 aggregate diff, hashed controlling authority/report, all ten
criteria, required commands and local-effects limits. Dispatch a new conversation
with `fork_turns: none`, read-only, without builder/controller/private reasoning.
A delta-only or inherited-context review is insufficient. Return the complete
independent report and artifacts, propose closeout only after VERIFIED, and
request explicit maintainer WS-05 acceptance. Later phases and delivery require
separate authority.
