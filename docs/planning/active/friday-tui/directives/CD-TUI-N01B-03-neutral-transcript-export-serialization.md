# CD-TUI-N01B-03: neutral transcript-export serialization

**Status:** Approved for bounded construction on 2026-10-19 by Chuck Russell.

**Initiative/unit:** `friday-tui` / TUI-N01B-03, a separately gated N01B
subunit after the independently VERIFIED N01B-01 and N01B-02 query work.

**Branch/before-code source:** `feature/friday-tui` /
`c1e38d944452ff26edd5a1fa4302fe5d9a2ccfc6` (clean). The product source
is unchanged from the reviewed and pushed N01B-02 source `07177e6c`.

**Authority and precedence:** The initiative is `started` with implementation
authority, but [AGENTS.md](../../../../../AGENTS.md) and the
[independent-validation policy](../../../../reference/policies/independent-validation-policy.md)
require a maintainer-approved exact construction directive before product code.
After explicit approval, the accepted
[architecture boundary](../architecture-reset.md),
[replacement plan](../replacement-plan.md),
[capability map](../neutral-capability-map.md),
[before-code characterization](../validation/N01B-03-before-code-characterization.md),
repository engineering policy and this directive govern this subunit.
Reconcile any conflict before editing source.

## Purpose and acceptance

An independently installed `friday-tui` must eventually create exports from
persisted Runtime transcript views without importing Chat or CLI. Extract only
the six pure content serializers currently inside Chat's transcript export
writers into `friday-runtime`, and make Chat's existing writers call them.
The TUI does not yet call them; this subunit supplies a reusable primitive.
For the same ordered views and configured display names, every Chat export
file must remain byte-for-byte identical. Friday Chat and `friday-cli` command
behavior, paths, error outcomes and package boundaries must remain unchanged.

## Exact change boundary after approval

1. Add
   `packages/friday-runtime/src/friday_runtime/transcript_export_format.py`.
   Expose six typed, synchronous, side-effect-free functions:
   `serialize_sessions_csv(sessions)`, `serialize_entries_csv(entries)`,
   `serialize_entries_jsonl(entries)`, `serialize_training_jsonl(entries)`,
   `serialize_transcript_markdown(session, entries, *, user_name,
   assistant_name)`, and `serialize_context_logs_json(session,
   context_logs)`. Inputs use the frozen `friday_runtime.transcript_views`
   dataclasses and ordered `Sequence` contracts; all return `str`.
   Keep CSV row and JSON-record helpers private in that module.
2. Edit only `packages/friday-chat/src/friday_chat/commands/transcript.py` to
   delegate export *content generation* to those functions. Remove its
   superseded pure serialization helpers and imports. Preserve all public
   handlers, their arguments and return strings, session selection, archive
   handling, display formatting for `/sessions` and `/transcript`, configured
   names, output filenames, export root/path safety, directory creation,
   timestamp naming, file writes, exception handling, and record counts.
   `TranscriptExportResult` remains Chat-owned with the same identity.
3. Add
   `packages/friday-runtime/tests_runtime/test_transcript_export_format.py`
   for direct neutral serialization tests without Chat or CLI imports.
4. Add
   `packages/friday-chat/tests_chat/test_transcript_export_format_delegation.py`
   for byte-for-byte Chat command/export comparison and unchanged failure,
   empty and path behavior. Keep all existing Chat and `friday-cli` tests
   unchanged as protected comparison fixtures.

Scoped TUI planning/evidence files, a TUI board event and the generated
dashboard may be updated after construction. No other product source/test
path, CLI or TUI package, dependency metadata, lock, workflow, script,
runtime configuration, or user guide may change. A newly needed path or
semantic change requires an amended directive and approval first.

## Required behavior and boundaries

- The neutral module imports only Runtime's transcript views and standard
  library modules. It must not import Chat, CLI, a writer, provider,
  configuration, path or persistent store. It does not pick a current
  session, sort/filter query results or change their ordering.
- Preserve the exact eight-column sessions and entries CSV headers/order,
  `csv.QUOTE_ALL`, LF line termination, ISO datetime spelling, `None` to
  empty CSV fields, `False`/`True` spelling and header-only empty CSV output.
  The same entries serializer serves all-session and current-session CSV.
- Preserve JSONL sorted keys, `ensure_ascii=False`, nullable values,
  `"\n".join` without a final LF, and empty-string output for no entries.
  Training records keep user then assistant roles and replace missing
  message text with empty strings.
- Preserve Markdown headings, turn order, explicit Chat-supplied display
  names, missing-message rendering, right-trim and one final LF. Preserve
  prompt-log key names/order after sorted JSON serialization, two-space
  indentation, Unicode, nullable response and no final LF. The existing
  Chat handler still decides whether no prompt logs produce a file.
- Chat supplies its current `config.chat.user_name` and `assistant_name`
  at the writer call site. No Runtime config lookup or Chat dependency is
  introduced into the serializer. There is no filtering or credential
  masking added in this unit; the content is exactly the persisted input.
- Preserve existing UTF-8 file writes and `_safe_export_path`; no new
  filesystem effect, mutable cache, resource owner, storage schema, network
  action or command registration. No TUI executable or UAT claim arises.

## Verification and stop conditions

1. Retain the [195-pass before-code suite and seven-file byte
   probe](../validation/N01B-03-before-code-characterization.md). First
   test neutral functions on direct Runtime views: empty and multiple
   records, field/row order, UTC/naive datetime `.isoformat()` spelling,
   nullable text/numbers, CSV comma/quote/embedded LF, Unicode, JSON key
   order/nulls/no trailing LF, Markdown custom names and trailing LF, and
   context-log prompt/response content. Assert exact text/UTF-8 bytes, not
   just parseability or nonempty files; include the frozen probe digests.
2. Through Chat commands on fake and disposable SQLite stores, compare all
   seven exported file contents with before-code expectations. Check
   `/transcript export`, `/export` default and all formats including `md`,
   `/export-prompts`, zero entries, no context logs, missing sessions,
   configured/default export roots, generated paths/filenames, record counts,
   and write/path failure messages. Run the unchanged transcript production,
   export, query/delegation, session identity and full `friday-cli` suites.
   Do not alter protected tests to make a comparison pass.
3. Run full Runtime and Chat suites, Ruff check/format and targeted Mypy for
   changed files, `uv lock --check --offline`, board/dashboard validation,
   local link check and `git diff --check`. Inspect exact changed paths.
   Build the Runtime wheel; verify it contains the serializer and imports in
   an isolated installation without Chat/CLI. Add the Chat wheel to that
   isolated environment and verify its installed exports still match.
   Existing Ubuntu automation can verify exact pushed source only after a
   separately authorized push; installed macOS/Linux terminal UAT remains
   a later release gate.
4. Record commands, counts, byte comparisons and limits in a local report.
   Commit a stable candidate and give its exact authority, directive,
   commit/diff and checks to a fresh-context read-only validator. A changed
   candidate needs fresh review. `VERIFIED` is a unit gate, not maintainer
   acceptance or permission to push, merge, release or deploy.

Stop if neutral imports load a frontend, an export byte or existing command
behavior changes, protected fixtures need alteration, or an additional
product/test/metadata path is needed. Do not begin export file effects,
transcript writes, session lifecycle, assembly/close, TUI implementation or
terminal UAT under this directive.

**Approval fields:** Maintainer Chuck Russell; approved 2026-10-19 by the
current-session reply "approved" to the explicit question approving this
exact CD-TUI-N01B-03 directive. Only its four named source/test paths and
scoped TUI packet/board evidence are authorized. Push, PR, merge, release
and later N01B subunits remain separate.
