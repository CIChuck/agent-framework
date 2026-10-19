# CD-TUI-N01B-01: neutral transcript-query contracts

**Status:** Proposed for maintainer review; **not approved for construction**.

**Initiative/unit:** `friday-tui` / TUI-N01B-01 (first subunit of N01B).

**Branch/before-code source:** `feature/friday-tui` /
`d7be6459da29b8f46e270c1e1cb38772ded020cc`.

**Authority:** The initiative is `started` with implementation authority
`granted`, but its [authority manifest](../authority.json) has no active N01B
directive and prohibits product code generation. Chuck Russell must approve
this exact directive before its source or test paths are changed. The accepted
[product boundaries](../architecture-reset.md), [replacement
plan](../replacement-plan.md), [capability map](../neutral-capability-map.md),
[before-code characterization](../validation/N01B-01-before-code-characterization.md),
repository engineering policy and [independent validation
policy](../../../../reference/policies/independent-validation-policy.md)
control this work in that order after explicit maintainer direction. Resolve a
conflict with those sources before editing code.

## Purpose and observable result

Provide a typed, read-only transcript-query boundary in `friday-runtime` that
a future independently installed `friday-tui` can import without importing
`friday-chat` or `friday-cli`. Keep existing Chat imports pointing to the
**same** objects, and keep Chat's persisted query and export behavior unchanged.
This extraction alone does not make `/sessions` or `/transcript` runnable in
the TUI; a later unit must expose neutral query effects and assembly.

## Exact change boundary

Permitted product and test paths after explicit approval:

1. Add `packages/friday-runtime/src/friday_runtime/transcript_views.py` as the
   only definition of `TranscriptSessionView`, `TranscriptEntryView`,
   `TranscriptContextLogView` and `TranscriptQueryStore`.
2. Edit `packages/friday-chat/src/friday_chat/transcripts.py` into a
   compatibility facade for those four names. Keep `TranscriptExportResult`
   defined there and preserve its existing fields, defaults and behavior.
   Preserve the Chat module's current five-name `__all__` and their order.
3. Add `packages/friday-runtime/tests_runtime/test_transcript_views.py` for
   neutral field/signature/default/frozen behavior and frontend-free import
   closure. Its neutral-contract tests must not import Chat or CLI; use a
   separate subprocess to check the import closure.
4. Add `packages/friday-chat/tests_chat/test_transcript_query_facade.py` for
   same-object re-exports, `TranscriptExportResult` ownership, historical Chat
   pickle lookup and current Chat import compatibility.

Scoped packet/evidence, TUI board events and generated dashboard may be
updated after construction. Existing Chat and `friday-cli` tests are protected
comparison fixtures; do not rewrite them to make the move pass. No other
source/test path, package metadata, dependency lock, workflow, TUI code or
runtime configuration may change under this directive. If another path or
dependency becomes necessary, stop and seek a revised directive first.

## Required implementation and compatibility

- Copy the three dataclass field names, types, order, positional
  construction, defaults, frozen/non-slot behavior, generated equality and
  representation from the before-code source. Preserve `TranscriptQueryStore`
  as a structural `Protocol` with the four asynchronous method names,
  signatures, defaults and return types. Do not add runtime-checkable status,
  validation, paging, I/O or store construction.
- Re-export the four neutral objects from `friday_chat.transcripts` by object
  identity, without subclassing or duplicate definitions. Existing Chat
  runtime, adapters, handlers and callers should require no import edits.
  Keep the Chat-owned export result and all export serialization/file effects
  in Chat. Do not introduce a neutral import of Chat or CLI.
- The owning `__module__` for the moved objects changes to
  `friday_runtime.transcript_views`. Old pickle *global lookups* for the four
  `friday_chat.transcripts` names must continue to resolve through the facade.
  Do not claim byte-identical new pickle output. If a supported persisted
  transcript format relies on the old module identity or serialized instance
  representation, stop and add a characterized compatibility fixture before
  proceeding.
- Preserve actual persisted query results, newest-first session ordering,
  archive handling, entries/context-log order, error behavior, count/limit
  semantics and `/sessions`/`/transcript` output and export bytes by leaving
  their implementations untouched. Do not introduce transcript writes,
  provider calls or UI behavior into the neutral contract.
- No configuration schema, environment lookup, credential handling, privacy
  filtering, storage path, network service or dependency is added. Tests use
  synthetic data and disposable stores only; no existing local Friday state
  or live provider is used.

## Verification and stop conditions

1. Retain the [before-code characterization](../validation/N01B-01-before-code-characterization.md)
   and its 171 passing tests. Add focused tests for every moved field/default,
   immutability, async protocol signature, object identity and old-module
   pickle lookup. Include negative checks for missing/optional values where
   current dataclass construction provides them, and no import of
   `friday_chat`/`friday_cli` from the neutral module.
2. Run the new tests, unchanged
   `test_transcript_production_commands.py`,
   `test_transcript_export_commands.py`, `test_session_identity.py`, and the
   entire unchanged `packages/friday-cli/tests_cli` suite. Compare transcript
   query order, archived filters, missing session, entries/context logs and
   export output with the baseline. Run full Runtime and Chat suites after
   the focused tests. A changed baseline requires investigation, not a test
   rewrite.
3. Run Ruff and Mypy for the changed source/tests, `uv lock --check`, board
   validation, dashboard check and `git diff --check`. Inspect the diff for
   only the allowed paths. Build a Runtime wheel and confirm its neutral
   module is included; in an isolated installed environment, import the
   neutral module and prove neither frontend loads or is required. Verify
   Chat's installed facade still re-exports the identical objects. The
   existing Ubuntu workflow supplies rolling automated Linux checks after an
   independently reviewed push is separately authorized. This contract-only
   unit has no terminal UAT; installed macOS and Linux terminal UAT remain
   first-shell/final-release gates.
4. Record exact commands, outcomes, before/after comparisons and limitations
   in a unit validation report. Commit a stable candidate after local checks,
   then provide its exact authority, directive, commit and diff to a fresh,
   read-only independent validator. A changed candidate needs a fresh review.
   `VERIFIED` is a work-unit gate, not maintainer acceptance or permission to
   push, merge, release or deploy.

Stop if a Chat or `friday-cli` behavior changes, old supported serialization
fails, a neutral import loads either frontend, a test needs modified protected
fixtures, or the implementation needs a different source/test/metadata path.
Do not start the neutral adapter, command effects, session/turn state,
resource close, service assembly or TUI implementation under this directive.

**Approval fields:** Maintainer approval pending; exact scope is the four
source/test paths above plus scoped packet/board evidence. No source or test
change is authorized by this proposal alone.
