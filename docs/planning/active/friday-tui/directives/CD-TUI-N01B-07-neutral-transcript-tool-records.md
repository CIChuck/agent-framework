# CD-TUI-N01B-07: neutral transcript tool-record preparation

**Status:** Proposed only; not approved for code generation. Independent
post-run review of N01B-06's `completed/success` exact-source Ubuntu run
remains the current board gate. A maintainer must separately approve this exact directive
before any N01B-07 source or test edit.

**Initiative/unit:** `friday-tui` / TUI-N01B-07, a bounded N01B transcript
write subunit after N01B-06. **Branch/before-code product source:**
`feature/friday-tui` / pushed `aa8ae784487cb723130a39e5a8421b881f40178d`;
product bytes match locally after the post-push status commit. Recheck the
source, branch and authority when this directive is considered for approval.

**Authority and precedence:** [AGENTS.md](../../../../../AGENTS.md), the
[independent-validation policy](../../../../reference/policies/independent-validation-policy.md),
[accepted independent-package boundary](../architecture-reset.md),
[replacement plan](../replacement-plan.md),
[capability map](../neutral-capability-map.md),
[before-code characterization](../validation/N01B-07-before-code-transcript-tool-record-characterization.md),
repository engineering policy and this directive. Reconcile any conflict
before editing source.

## Purpose and acceptance

An independently installed TUI must eventually write transcript records
without importing Chat or CLI. Extract Chat's pure tool-call provenance
preflight and tool-call/result record construction into a neutral Runtime
module. Keep the two-stage ordering: unsafe MCP facts are rejected before
any session/store effect; record model construction occurs after Chat's
existing session and turn-number steps. Chat delegates to the neutral
functions while retaining entry construction, persistence, raw-context
logging and MCP receipt checks. Existing Chat and `friday-cli` behavior,
bytes, errors, side effects and public types must remain unchanged. The
TUI does not call these functions in this unit.

## Exact change boundary after separate approval

1. Add only `packages/friday-runtime/src/friday_runtime/transcript_tool_records.py`.
   Define a structural, frontend-independent typed tool-call input with
   `name`, `arguments`, `result`, `call_id` and optional
   `MCPToolCallProvenance`. Provide
   `validate_transcript_tool_provenance(turn_id, calls, max_result_bytes)`
   returning one correlated provenance value or `None` per call, and
   `build_transcript_tool_records(turn_id, calls, provenance)` returning
   the corresponding `friday_transcript.ToolCall` and `ToolResult` lists.
   Export only the new public neutral names. The module may import the
   standard library, `friday_core.mcp` and `friday_transcript` models; it
   must not import a frontend, provider, config, store or command registry.
2. Edit only `packages/friday-chat/src/friday_chat/adapters.py` to replace
   the existing provenance loop with a call to the neutral validator before
   `_ensure_session`, and the existing call/result model lists with a call
   to the neutral builder after `_next_turn_number`. Retain the Chat adapter
   constructor, method signatures and monkeypatch seams, session creation,
   turn-number cache, `TranscriptEntry` fields, append/context-log order,
   receipt/readback logic and Chat-owned `record_turn` no-op.
3. Add only `packages/friday-runtime/tests_runtime/test_transcript_tool_records.py`
   for direct neutral validation and record construction without Chat/CLI
   import availability.
4. Add only `packages/friday-chat/tests_chat/test_transcript_tool_record_delegation.py`
   for persisted Chat behavior and delegation. All existing Chat,
   `friday-cli` and Runtime tests are protected comparison fixtures.

Scoped TUI planning/evidence files, the TUI board event and generated
dashboard may be updated. No other source/test path, TUI package,
`friday-transcript` or `friday-core` source, package metadata, lock,
workflow, script, runtime configuration or user guide may change. A newly
needed path or semantic change requires an amended directive and separate
maintainer approval.

## Required behavior and ordering

- Match each existing MCP preflight predicate and failure message:
  nonempty raw arguments, call ID/name mismatch, unchecked sanitization,
  UTF-8 result-byte-size mismatch or configured maximum overage, and
  unrelated transcript correlation are rejected before any store call.
  Valid provenance is model-validated with this turn's ID as transcript
  correlation; native calls keep `None` provenance and ordinary arguments.
- Preserve the existing call order and generated fallback ID
  `turn_id:index:name`. Store a copied argument mapping, unchanged result
  text, matched result ID, provenance on both records, and the provenance
  failure code as `ToolResult.error` when present. Do not add credential
  filtering, result display, serialization, retries or new persistence.
- A tool-record model validation failure that currently occurs after
  session creation must remain after session creation. Do not combine the
  two stages into one function called before `_ensure_session`.
- Chat still creates `TranscriptEntry` with its existing timestamp,
  model/temperature, latency and metadata, then appends and optionally
  stores the pending raw context log. No transaction, rollback, cleanup,
  atomicity or turn-number policy changes. Keep MCP-memory receipt
  verification in Chat and preserve its exact persisted facts.
- This unit does not supply a complete neutral transcript writer,
  lifecycle/close, assembly, TUI executable or installed terminal UAT.

## Verification and stop conditions

1. Retain the [303-pass read-only baseline](../validation/N01B-07-before-code-transcript-tool-record-characterization.md)
   across separate focused and unchanged-CLI runs. Direct Runtime tests
   cover zero/native/MCP/mixed calls, provided and fallback IDs, Unicode
   byte limits, exact correlated facts, failure-code mapping, argument
   copying, each rejected preflight condition and exception text. A
   Runtime-only import/isolation check must find no Chat/CLI dependency.
2. Chat delegation tests use a disposable SQLite store to compare exact
   persisted `ToolCall`/`ToolResult`/entry data, native and MCP cases,
   rejected preflight with no session or entry, accepted session and turn
   numbering, append failure, pending context-log behavior and MCP receipt
   readback. The existing 63 transcript/identity and 85 MCP-memory/
   telemetry tests remain protected; unchanged `friday-cli` still passes.
3. Run full Runtime and Chat suites, scoped Ruff check/format and targeted
   Mypy, offline lock, board/dashboard, changed-document links and
   `git diff --check`; inspect exact paths. Build wheels and verify an
   isolated Runtime-only install exercises both neutral functions without
   Chat/CLI. Run Chat separately from installed wheels for an equivalent
   persisted comparison. An exact-source Ubuntu run requires a separately
   authorized non-force push. Installed macOS/Linux TUI terminal UAT
   remains a release gate.
4. Record commands, counts, behavior comparisons and limits. Commit a
   stable candidate and hand the exact authority, directive, candidate/
   diff and checks to a fresh-context read-only validator. A changed
   candidate requires fresh review. `VERIFIED` does not grant push,
   maintainer acceptance, PR, merge or release.

Stop if Runtime imports Chat/CLI, an unsafe MCP record reaches the store,
validation moves after a store effect, model construction moves before the
existing session effect, Chat receipt/persistence semantics or error
prose changes, a protected test needs editing, or any other source/test
path is needed. Do not begin full transcript persistence, session close,
runtime assembly or TUI implementation under this directive.
