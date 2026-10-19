# CD-TUI-N01B-02: neutral persisted transcript-query adapter

**Status:** Approved for bounded construction on 2026-10-19 by Chuck Russell.

**Initiative/unit:** `friday-tui` / TUI-N01B-02 (second, separately gated
subunit of N01B).

**Branch/before-code source:** `feature/friday-tui` /
`f0e0786f69243513b9e35d66dc271c2c5f10afab`.

**Authority and precedence:** The TUI initiative is `started` on its named
branch, but [AGENTS.md](../../../../../AGENTS.md) and the
[independent-validation policy](../../../../reference/policies/independent-validation-policy.md)
require an approved exact work-unit directive before product code generation.
After explicit maintainer approval, the accepted
[architecture boundary](../architecture-reset.md),
[replacement plan](../replacement-plan.md),
[capability map](../neutral-capability-map.md),
[before-code characterization](../validation/N01B-02-before-code-characterization.md),
repository engineering policy, this directive and any scoped amendment govern
construction in that order. Resolve conflicts before editing source.

## Purpose and acceptance

An independently installed `friday-tui` must eventually query persisted
sessions, entries and context logs without importing Chat or CLI. Create one
UI-neutral, read-only adapter in `friday-runtime` that implements the verified
`TranscriptQueryStore` view contract over Friday's transcript read APIs.
Change Chat's four public query methods into delegates to that adapter, so
Chat retains exactly its current query and command behavior. This is an
adapter primitive, not TUI runtime assembly or runnable TUI commands.

## Exact change boundary after approval

1. Add `packages/friday-runtime/src/friday_runtime/transcript_queries.py`.
   It may define a narrow typed `TranscriptRecordReader` protocol for the
   existing low-level `get_session`, `list_sessions`, `get_entries` and
   `get_context_log_for_session` calls and a stateless
   `TranscriptQueryAdapter(store)` implementing `TranscriptQueryStore`.
   Keep mapping, archive enumeration and sorting helpers in this module.
2. Edit `packages/friday-chat/src/friday_chat/adapters.py` only to import that
   neutral adapter and delegate the four public `FrameworkTranscriptAdapter`
   query methods. Remove the superseded private query-only helpers/imports.
   Preserve the dataclass constructor/fields and every write, finalization,
   configuration, MCP and export behavior and the four public method
   signatures. Do not change other Chat modules.
3. Add `packages/friday-runtime/tests_runtime/test_transcript_queries.py`
   for direct neutral effects with a synthetic read store and a disposable
   SQLite store. Its neutral tests must not import Chat or CLI.
4. Add `packages/friday-chat/tests_chat/test_transcript_query_adapter_delegation.py`
   for Chat delegation and public-signature/error compatibility. Keep all
   existing Chat and `friday-cli` tests unchanged as protected comparison
   fixtures.

Scoped TUI packet/evidence, a TUI board event and generated dashboard may be
updated after construction. No other source/test path, CLI or TUI package,
dependency metadata, lock, workflow, script, runtime configuration or user
guide may change under this directive. A newly needed path requires a revised
directive and approval first.

## Required behavior and boundaries

- The neutral module imports `friday-transcript` models, the existing Runtime
  query views/protocol and standard-library modules only; it imports neither
  `friday-chat` nor `friday-cli`. The read-store port contains only the four
  needed asynchronous operations. The concrete SQLite store must satisfy it
  without changing `friday-transcript` or adding a dependency.
- Preserve `query_sessions`' default `limit=1000`, `include_archived=False`,
  limit clamp to 0..1000, archive membership scan in 1000-row pages when
  requested, mapped fields and newest-first sort by UTC-normalized
  `started_at` then session ID. Preserve `query_session`'s exact-ID lookup,
  `None` result and archive membership scan.
- Preserve `query_entries`' 1000-row paging until a short page, mapped
  fields and ascending sort by turn number, UTC-normalized timestamp and
  entry ID. Preserve `query_context_logs`' single 100,000-row-limited read,
  mapped fields and ascending sort by turn number, UTC-normalized capture
  time and log ID. Treat naive datetimes as UTC as the current helper does.
  Do not silently make context-log reads unlimited or change duplicate/tie
  behavior.
- Propagate store failures as today; no fallback, cache, write, filtering,
  sanitization, provider call or network action is added. Existing transcript
  text remains the persisted text already returned by Chat. No credentials or
  sensitive-value filtering is introduced in this unit.
- Chat delegates using its current `self.store`, without a new constructor
  argument or mutable long-lived query state. Its fake store, command
  handlers, export formatting and file bytes stay Chat-owned and unchanged.
  The neutral adapter neither chooses a session nor creates/closes a store.
- No storage path, database schema, config precedence, CLI setting or TUI
  presentation behavior changes. Tests use synthetic rows/disposable SQLite
  files only and never live providers or existing local Friday state.

## Verification and stop conditions

1. Retain the [171-pass before-code comparison](../validation/N01B-02-before-code-characterization.md).
   Test direct neutral reads of missing/current/archived sessions, default,
   zero, negative and over-1000 limits, archive membership beyond one page,
   equal and naive/aware timestamp ordering, entry pagination beyond 1000,
   context-log 100,000 limit call/order, nullable mapped values and read error
   propagation. Prove the adapter implements `TranscriptQueryStore` and makes
   no write calls. Exercise a real disposable SQLite store independently of
   Chat.
2. Test Chat's four signatures and delegation with the same store; preserve
   missing/error outcomes. Run unchanged
   `test_transcript_production_commands.py`,
   `test_transcript_export_commands.py`, `test_session_identity.py` and the
   entire `packages/friday-cli/tests_cli` suite. Compare archived filtering,
   ordering, output and export bytes with the before-code fixtures. Run the
   full Runtime and Chat suites separately after focused tests. Investigate
   any comparison failure; do not rewrite protected fixtures to make it pass.
3. Run Ruff check/format and Mypy on changed source/tests, `uv lock --check`,
   board validation, dashboard check and `git diff --check`; inspect exact
   changed paths. Build the Runtime wheel, verify it contains the new module
   and has no frontend dependency, then import and directly query from an
   isolated installation with Chat/CLI absent. Verify installed Chat still
   delegates and its exports work after adding the Chat wheel. Existing Ubuntu
   automation can check exact pushed source only after a separately authorized
   push; installed macOS/Linux TUI terminal UAT remains a later release gate.
4. Record exact commands, outcomes, before/after comparisons and limits in a
   local report. Commit a stable candidate and hand its exact authority,
   directive, commit and diff to a fresh-context read-only validator. A changed
   candidate needs fresh review. `VERIFIED` is a unit gate, not maintainer
   acceptance or permission to push, merge, release or deploy.

Stop if neutral imports load either frontend, Chat/`friday-cli` behavior or
export bytes change, the read port cannot type the existing SQLite store,
tests need modified protected fixtures, or an additional source, test,
metadata or workflow path is needed. Do not start neutral transcript writes,
exports, command effects, session/turn state, resource close, runtime
assembly, TUI implementation or terminal UAT under this directive.

**Approval fields:** Maintainer Chuck Russell; approved 2026-10-19 by the
current-session reply "CD-TUI-N01B-02 approved" to this exact directive.
Only the four named source/test paths and scoped packet/board evidence are
authorized. Push, PR, merge, release and later N01B subunits need separate
authority.
