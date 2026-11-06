# CD-TUI-N01B-09: neutral transcript session-ensure effect

**Status:** Approved by Chuck Russell on 2026-10-19 for the four named local
Runtime/Chat source and test paths and scoped TUI evidence. Approval was the
current-session reply “approved and authorized - proceed” after the controller
linked this exact directive and requested its four-path implementation scope.
No additional push, PR, merge, release or TUI terminal UAT acceptance follows
from this approval.
N01B-08's [local and exact-source Ubuntu gates](../validation/VAL-N01B-08-postrun-3a5e05cf.md)
are independently VERIFIED; its one push is consumed.

**Initiative/unit:** `friday-tui` / TUI-N01B-09, a bounded session-ensure
subunit after N01B-08. **Branch/before-code source:** `feature/friday-tui`;
planning base `78aad114` has the same product bytes as pushed `c4a5faa6`.
Recheck branch, source and authority before any product edit.

**Authority and precedence:** [AGENTS.md](../../../../../AGENTS.md), the
[independent-validation policy](../../../../reference/policies/independent-validation-policy.md),
[accepted independent-package boundary](../architecture-reset.md),
[replacement plan](../replacement-plan.md),
[capability map](../neutral-capability-map.md),
[before-code characterization](../validation/N01B-09-before-code-session-ensure-characterization.md),
repository engineering policy and this directive. Reconcile any conflict
before editing source.

## Purpose and acceptance

An independently installed TUI must eventually ensure a transcript session
without importing Chat or CLI. Extract only Chat's characterized
get-or-create session effect into a neutral Runtime helper. Chat continues
to build its current session model and delegates the effect, preserving its
observable order, existing-session handling, ignored false create result,
snapshot fields and error behavior. TUI does not call the helper in this
unit. This is not complete neutral transcript persistence or runtime
assembly.

## Approved exact local change boundary

1. Add only `packages/friday-runtime/src/friday_runtime/transcript_session_effects.py`.
   Define a narrow `TranscriptSessionStore` structural async protocol for
   `get_session(str) -> TranscriptSession | None` and
   `create_session(TranscriptSession) -> bool`. Provide one public async
   `ensure_transcript_session(store, session_id, session_factory)` effect,
   where `session_factory: Callable[[], TranscriptSession]` is evaluated
   only after a missing-session read. Return `None`, as Chat's current
   `_ensure_session` does. Import only the standard library and public
   `friday-transcript` model; do not import a frontend, configuration,
   command registry, provider or concrete store implementation.
2. Edit only `packages/friday-chat/src/friday_chat/adapters.py` so its
   existing `_ensure_session` method delegates to the neutral helper. Keep
   the `TranscriptSession` construction in Chat, including current
   `session_id`, user, `model or "unknown"`, system prompt and exact
   `model_dump(mode="json", exclude={"tools": {"providers": {"mcp"}}})`
   snapshot expression inside the lazy factory. Keep the preflight,
   `_next_turn_number`, entry and tool-record construction, append/context
   delegation, pending-state handling, receipt readback and `finalize` in
   Chat. No public Chat signature changes.
3. Add only `packages/friday-runtime/tests_runtime/test_transcript_session_effects.py`
   for direct neutral behavior with a fake structural store and no Chat/CLI
   import availability.
4. Add only `packages/friday-chat/tests_chat/test_transcript_session_effect_delegation.py`
   for Chat delegation, disposable SQLite persistence and protected
   order/failure comparisons. Existing Chat, Runtime, Transcript and
   `friday-cli` tests are protected fixtures.

Scoped TUI planning/evidence files, the TUI board event and generated
dashboard may be updated. No other source/test path, TUI package,
`friday-transcript` model/store/protocol, package metadata, lock, workflow,
script, runtime configuration or user guide may change. A newly needed
path or semantic change requires an amended directive and separate
maintainer approval.

## Required session semantics and ordering

- Preserve order: safe MCP provenance preflight; await `get_session`;
  if missing, lazily construct `TranscriptSession` and await
  `create_session`; then count entries, construct records/entry and
  perform the existing append/context effects. An unsafe MCP record
  still reaches no store call.
- A returned session, including ended, archived or historical, is left
  unchanged. Do not evaluate the factory, create another row, reopen,
  refresh its snapshot or reinterpret its configuration.
- On a miss, evaluate the factory once after the awaited read. Chat's
  new-session fields and complete MCP-stanza omission are unchanged.
  Do not add new snapshot filtering, defaults or validation. A neutral
  caller supplies its own session model; the helper does not know Chat
  configuration.
- Await `create_session` once and ignore its `False` result, as Chat does.
  Do not retry, re-read, roll back, create a replacement, raise a new
  error or change later append behavior. A failed create may leave no
  session; Chat's later append can still fail with its existing error.
- Propagate get, factory and create exceptions or cancellation unchanged.
  Do not move turn-number caching, entry construction, finalization or
  resource-close policy into this unit.

## Verification and stop conditions

1. Retain the [225-pass read-only baseline and disposable session
   probes](../validation/N01B-09-before-code-session-ensure-characterization.md).
   Direct Runtime tests cover missing/existing/ended sessions, lazy and
   single factory evaluation, false create, get/create exception and
   cancellation propagation, and no frontend imports.
2. Chat delegation tests use disposable SQLite to compare persisted
   session fields, new-session MCP-stanza omission and native provider
   shape, historical snapshot preservation, missing/existing/ended
   behavior, and the preflight/get/create/count/append order. Inject a
   false create and confirm the unchanged downstream append error and
   cached count. Existing N01B-08, MCP, Transcript and `friday-cli`
   tests remain protected.
3. Run full Runtime and Chat suites, unchanged `friday-cli`, scoped Ruff
   check/format and targeted Mypy, offline lock, board/dashboard,
   changed-document links and `git diff --check`; inspect exact changed
   paths. Build wheels and verify a Runtime-only installed environment
   calls the neutral helper without Chat/CLI. Probe Chat persistence
   separately from installed wheels. Fresh exact-source Ubuntu verification
   requires a separately authorized non-force push; installed macOS/Linux
   TUI terminal UAT remains a release gate.
4. Record commands, counts, behavior comparisons and limits. Commit a
   stable candidate and hand exact authority, directive, candidate/diff
   and checks to a fresh-context read-only validator. A changed candidate
   requires fresh review. `VERIFIED` does not grant push, maintainer
   acceptance, PR, merge or release.

Stop if Runtime imports Chat/CLI, Chat's snapshot expression or timing
changes, an existing session is reopened or rewritten, a `False` create
starts failing early, protected tests need editing, or another source/test
path is needed. Do not begin turn-number allocation, entry-building,
transcript finalization, runtime assembly or TUI implementation under
this directive.
