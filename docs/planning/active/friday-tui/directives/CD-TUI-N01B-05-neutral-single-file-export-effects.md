# CD-TUI-N01B-05: neutral single-file transcript export effects

**Status:** Proposed for exact maintainer review. No N01B-05 product-code,
test, push or external-delivery authority is granted by this draft.

**Initiative/unit:** `friday-tui` / TUI-N01B-05, a separately gated N01B
subunit after N01B-04's independently VERIFIED local and exact-source
Ubuntu gates.

**Branch/before-code source:** `feature/friday-tui` /
`887e43a02d7213e65436b1d85bfafbe255ac865c` (clean). The N01B-04
product source remains frozen at reviewed candidate `abeeb895`; pushed
source `4b2aadd2` passed exact-source Ubuntu verification. Two evidence-only
closeout commits are local and unpushed.

**Authority and precedence:** [AGENTS.md](../../../../../AGENTS.md) and
the [independent-validation policy](../../../../reference/policies/independent-validation-policy.md)
require explicit maintainer approval of this exact directive before
product code or tests change. If approved, the accepted
[independent-package boundary](../architecture-reset.md),
[replacement plan](../replacement-plan.md),
[capability map](../neutral-capability-map.md),
[before-code characterization](../validation/N01B-05-before-code-single-file-export-characterization.md),
repository engineering policy and this directive govern the unit.
Reconcile any conflict before editing source.

## Purpose and acceptance

An independently installed TUI must eventually write transcript exports
without importing `friday-chat` or `friday-cli`. Extract only the
single-file content-and-write effects used by Chat's `/export` and
`/export-prompts` into a UI-neutral Runtime module. N01B-03 already
provides content serializers; N01B-04 provides root/path helpers. Chat
continues to choose the session, command format, fixed filename,
configured export root, safe destination and display names, then wraps
the neutral write in its existing Chat-owned `TranscriptExportResult`
and command output. The TUI does not call this module yet. Every
existing Chat and `friday-cli` result, exported byte, path, error and
file effect must remain unchanged.

## Exact change boundary after approval

1. Add
   `packages/friday-runtime/src/friday_runtime/transcript_export_files.py`
   with two typed, synchronous functions:
   `write_current_session_file(destination: Path, session:
   TranscriptSessionView, entries: Sequence[TranscriptEntryView], *,
   export_format: str, user_name: str | None = None,
   assistant_name: str | None = None) -> None` and
   `write_context_log_file(destination: Path, session:
   TranscriptSessionView, context_logs:
   Sequence[TranscriptContextLogView]) -> None`.
   The former accepts the canonical `csv`, `jsonl`, `training` and
   `markdown` names, uses the existing N01B-03 serializer for the
   selected format, and requires supplied display names for Markdown.
   An unsupported direct format raises `ValueError`; Chat's handler
   still validates and normalizes format before this call. Each
   function makes exactly one `destination.write_text(text,
   encoding="utf-8")` call and propagates errors. It does not create
   a parent directory, choose a filename or return a Chat result type.
2. Edit only
   `packages/friday-chat/src/friday_chat/commands/transcript.py` to
   keep `_write_current_session_export` and
   `_write_context_log_export` as Chat wrappers. Each calls the
   existing public `export_directory(context)` and private
   `_safe_export_path` at the same point, then delegates the
   serialization-and-write effect to Runtime and returns the same
   `TranscriptExportResult`. Keep configured display-name access
   in the Markdown branch as today. Preserve all handlers, aliases,
   queries, format validation, command outputs and exception handling.
3. Add
   `packages/friday-runtime/tests_runtime/test_transcript_export_files.py`
   for direct neutral writes without importing Chat or CLI.
4. Add
   `packages/friday-chat/tests_chat/test_transcript_export_file_delegation.py`
   for Chat registry behavior, exact file bytes and result identity.
   Existing Chat and `friday-cli` tests are protected comparison
   fixtures and must not be edited.

Scoped TUI planning/evidence files, TUI board events and the generated
dashboard may be updated. No other product source/test path,
`friday_chat.transcripts`, CLI or TUI package, dependency metadata,
lock, workflow, script, runtime configuration or user guide may change.
A newly needed path or semantic change requires an amended directive
and explicit approval first.

## Required behavior and boundaries

- The neutral file module may import standard-library modules,
  `friday_runtime.transcript_views`, and the existing neutral
  `transcript_export_format` functions. It must not import Chat, CLI,
  a provider, config, persistent store or command registry. It
  performs no query, network, transcript write or directory creation.
- `destination` is a caller-prevalidated path; the neutral writer
  does not select or validate a root. A future TUI caller must compose
  it with N01B-04 `safe_export_path`. Chat must retain its existing
  `_safe_export_path` calls before writing so its path behavior and
  monkeypatch seam remain unchanged. Do not introduce an atomic
  write, temporary file, cleanup, rollback, chmod or retry.
- Preserve fixed filenames, configured/default and relative-root
  behavior, UTF-8 bytes, overwrite/truncation of an existing fixed
  file, no automatic parent creation by the writer, and propagation
  of `Path.write_text` errors into Chat's existing generic handler
  output. Exact serializer text, including empty CSV/JSONL/Markdown
  and prompt JSON, remains governed by N01B-03.
- `/export-prompts` still creates no file when there are no captured
  context logs. `md` remains a Chat alias for Markdown; Runtime
  accepts the normalized format only. Markdown names are taken from
  Chat configuration only for the Markdown branch.
- `TranscriptExportResult` stays defined in
  `friday_chat.transcripts` with the same module identity, defaults,
  file tuple and counts. The neutral module introduces no matching
  result class. `/transcript export` stays Chat-owned, including
  UTC timestamped directory creation, two-file write order, collision
  and partial-failure behavior. `/context --file` and
  `/prompt --file` remain unchanged Chat effects.
- No TUI executable, installed terminal UAT, real-provider check or
  full command parity is claimed by this unit.

## Verification and stop conditions

1. Retain the [239-pass unchanged baseline and source
   characterization](../validation/N01B-05-before-code-single-file-export-characterization.md).
   Direct Runtime tests cover all four canonical formats and prompt
   JSON, exact Unicode/embedded-newline UTF-8 bytes, zero entries,
   existing-file overwrite, no parent creation, unsupported direct
   format, missing Markdown names and propagated write errors.
   Test that the module can import without Chat or CLI.
2. Through Chat commands on fake and disposable SQLite stores,
   compare the five single-file exports with frozen before-code
   hashes; check `/export` default, all formats and `md`,
   `/export-prompts` current/selected session, no logs, zero
   entries, missing session, configured/default roots, filenames,
   result counts/identity, and exact outputs/errors. The unchanged
   path-delegation fixture must still observe Chat's path helper
   calls. Verify the two-file `/transcript export` and shared
   `/context --file` / `/prompt --file` effects are untouched.
   Run unchanged production, export, query, session and full
   `friday-cli` comparisons without altering their tests.
3. Run full Runtime and Chat suites, scoped Ruff check/format and
   targeted Mypy, `uv lock --check --offline`, board/dashboard and
   changed-document link checks, and `git diff --check`; inspect
   exact changed paths. Build Runtime and Chat wheels. From an
   isolated Runtime-only install, import and exercise both neutral
   writers with Chat/CLI unavailable. Then install Chat separately
   and compare installed command exports and frozen hashes. Existing
   Ubuntu automation may verify exact pushed source only after a
   separately authorized non-force push. Installed macOS/Linux TUI
   terminal UAT remains a later release gate.
4. Record commands, counts, byte comparisons and limitations in a
   local report. Commit a stable candidate and hand the exact
   authority, directive, commit/diff and checks to a fresh-context,
   read-only validator. A changed candidate needs fresh review.
   `VERIFIED` is a work-unit gate, not maintainer acceptance or
   permission to push, merge or release.

Stop if Runtime imports a frontend, a protected Chat/`friday-cli`
behavior or byte changes, `TranscriptExportResult` identity moves,
Chat's path seam disappears, an existing test needs editing, or
another source/test/metadata path is needed. Do not begin the
two-file all-session export, transcript persistence, session
lifecycle, assembly/close or TUI implementation under this directive.

**Approval fields:** Proposed by Codex on 2026-10-19 after the
maintainer's current-session “continue” for next-gate planning.
Maintainer decision: pending. Exact N01B-05 product-code/test
authorization: not granted. Push, PR, merge, release and later N01B
subunits: not authorized.
