# CD-TUI-N01B-08: neutral transcript append and context-log effects

**Status:** Approved by Chuck Russell on 2026-10-19 for the four named local
Runtime/Chat source and test paths below, plus scoped TUI evidence. The
approval is the current-session reply “approved and authorized - proceed”
after the controller linked this exact directive, named its four-path local
scope and cited the `AGENTS.md` directive gate. N01B-07's [exact-source Ubuntu
gate](../validation/VAL-N01B-07-postrun-4fc8309d.md) is independently
VERIFIED; its one push is consumed.

**Initiative/unit:** `friday-tui` / TUI-N01B-08, a bounded transcript-write
subunit after N01B-07. **Branch/before-code source:** `feature/friday-tui`;
approved planning candidate `bec5b875` has the same product bytes as pushed
`4a646dc7`. Recheck branch, source and authority before editing product code.

**Authority and precedence:** [AGENTS.md](../../../../../AGENTS.md), the
[independent-validation policy](../../../../reference/policies/independent-validation-policy.md),
[accepted independent-package boundary](../architecture-reset.md),
[replacement plan](../replacement-plan.md),
[capability map](../neutral-capability-map.md),
[before-code characterization](../validation/N01B-08-before-code-transcript-write-characterization.md),
repository engineering policy and this directive. Reconcile any conflict
before editing source.

## Purpose and acceptance

An independently installed TUI must eventually persist transcript entries
without importing Chat or CLI. Extract only Chat's already characterized
append and optional raw-context-log store effects into a neutral Runtime
helper. Chat delegates those effects while preserving its existing method,
entry fields, observable order, errors, partial commits, pending-state and
turn-number behavior. The TUI does not call the helper in this unit. This is
one independently testable step, not a complete neutral transcript writer.

## Approved exact local change boundary

1. Add only `packages/friday-runtime/src/friday_runtime/transcript_write_effects.py`.
   Define a narrow `TranscriptWriteStore` structural async protocol for
   `append_entry(TranscriptEntry) -> bool` and
   `store_context_log(ContextLogEntry) -> bool`. Provide one public async
   `append_transcript_entry_with_context` effect accepting that store, a
   `TranscriptEntry` and a `Callable[[], tuple[str, str] | None]`
   pending-context supplier. Invoke the supplier only after a successful
   awaited append. Return `bool` for whether a context-log write was
   attempted so Chat can clear its pending state at the same point. The
   helper may import the standard library and `friday-transcript` public
   models, but no frontend, configuration, command registry, provider or
   concrete store implementation.
2. Edit only `packages/friday-chat/src/friday_chat/adapters.py` to delegate
   the existing append/context-log block after `TranscriptEntry`
   construction. Keep its preflight, `_ensure_session`, `_next_turn_number`,
   tool-model and entry construction, `record_turn`, `record_context_log`,
   `record_mcp_interaction`, receipt readback, `finalize` and public methods
   in Chat. Pass a supplier for the current `_pending_context_log`; clear it
   only when the helper reports an attempted context-log call; then advance
   `_turn_number` exactly as today.
3. Add only `packages/friday-runtime/tests_runtime/test_transcript_write_effects.py`
   for direct effect behavior with a fake structural store and no Chat/CLI
   import availability.
4. Add only `packages/friday-chat/tests_chat/test_transcript_write_effect_delegation.py`
   for Chat delegation and disposable SQLite persistence comparison. All
   existing Chat, Runtime and `friday-cli` tests are protected fixtures.

Scoped TUI planning/evidence files, the TUI board event and generated
dashboard may be updated. No other source/test path, TUI
package, `friday-transcript` source/protocol, package metadata, lock,
workflow, script, runtime configuration or user guide may change. A newly
needed path or semantic change requires an amended directive and separate
maintainer approval.

## Required effect semantics and ordering

- Preserve the complete order: safe MCP preflight; session ensure; next-turn
  lookup; tool-record and entry construction; append; late pending-context
  read; optional context-log write; pending-state clear; cached turn advance.
  An unsafe MCP record still reaches no store call.
- If `append_entry` returns `False`, raise the exact
  `RuntimeError("Failed to append transcript entry.")`; do not read pending
  context, write a context log, clear pending state or advance the cached
  turn. Propagate an append exception unchanged.
- On a successful append, read pending state **after** the await. If it is
  absent, make no context-log call. If present, build `ContextLogEntry` with
  the entry's session ID, turn number and entry ID, and the supplied raw
  prompt/response; retain model-generated ID and capture time defaults.
  Await `store_context_log`. As Chat does now, ignore its `False` result,
  clear pending state and advance the cached turn. Do not turn it into an
  error or add an automatic retry.
- If context-log construction or storage raises or is cancelled, propagate
  it unchanged. The entry may already be committed; pending state remains
  and Chat's cached turn does not advance. Do not add rollback, transaction,
  compensation, deduplication, cleanup or a new retry policy.
- Keep `record_mcp_interaction` receipt/readback checks in Chat after the
  delegated effect, with exact persisted call/result/provenance facts.
  Existing Chat and `friday-cli` behavior and public signatures must stay
  unchanged. No thinking-token, tool-result display or TUI UI behavior is
  implemented here.

## Verification and stop conditions

1. Retain the [279-pass read-only baseline and disposable failure
   probes](../validation/N01B-08-before-code-transcript-write-characterization.md).
   Direct Runtime tests cover no context, successful context, exact appended
   and context model values, false/exception append, false/exception context
   result, late supplier read and no frontend imports. Check exception and
   cancellation propagation without altering store policy.
2. Chat delegation tests use disposable SQLite to compare entry/context
   persistence, current pending and turn-number state, preflight with zero
   store effects, session/turn/model/append/context order, false and raised
   outcomes, and MCP receipt readback. Existing N01B-07 and MCP-memory
   fixtures remain protected. The full unchanged `friday-cli` suite passes.
3. Run full Runtime and Chat suites, scoped Ruff check/format and targeted
   Mypy, offline lock, board/dashboard, changed-document links and
   `git diff --check`; inspect exact changed paths. Build wheels and verify
   a Runtime-only installed environment exercises the neutral effect
   without Chat/CLI. Probe Chat persistence separately from installed
   wheels. A fresh exact-source Ubuntu run requires separately authorized
   non-force push; installed macOS/Linux TUI terminal UAT remains a release
   gate.
4. Record commands, counts, behavior comparisons and limits. Commit a
   stable candidate and hand exact authority, directive, candidate/diff
   and checks to a fresh-context read-only validator. A changed candidate
   requires fresh review. `VERIFIED` does not grant push, maintainer
   acceptance, PR, merge or release.

Stop if Runtime imports Chat/CLI, entry/context fields or error prose
change, pending context is read before append, a returned `False` context
write starts failing Chat, an exception causes new cleanup or retry,
receipt verification moves, a protected test needs editing, or any other
source/test path is needed. Do not begin session creation, turn-number,
entry-building, transcript close, runtime assembly or TUI implementation
under this directive.
