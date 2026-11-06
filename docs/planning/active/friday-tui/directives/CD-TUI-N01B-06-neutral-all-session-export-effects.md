# CD-TUI-N01B-06: neutral all-session transcript export effects

**Status:** Approved for the exact N01B-06 local construction scope by Chuck
Russell on 2026-10-19. No push or external-delivery authority.

**Initiative/unit:** `friday-tui` / TUI-N01B-06, a separately gated N01B
subunit after N01B-05's independently VERIFIED local and exact-source
Ubuntu gates.

**Branch/before-code source:** `feature/friday-tui` /
`010849f531d2bbc08569d1825eec7e34f4db5489` (clean). N01B-05
product source is frozen at reviewed candidate `c773f272`; pushed source
`37298e48` passed exact-source Ubuntu verification. Subsequent N01B-05
closeout and N01B-06 proposal commits are local planning/evidence only; the
N01B-05 one-push authority was consumed.

**Authority and precedence:** [AGENTS.md](../../../../../AGENTS.md) and
the [independent-validation policy](../../../../reference/policies/independent-validation-policy.md)
require explicit maintainer approval of this exact directive before
product code or tests change. With this approval, the accepted
[independent-package boundary](../architecture-reset.md),
[replacement plan](../replacement-plan.md),
[capability map](../neutral-capability-map.md),
[before-code characterization](../validation/N01B-06-before-code-all-session-export-characterization.md),
repository engineering policy and this directive govern the unit.
Reconcile any conflict before editing source.

## Purpose and acceptance

An independently installed TUI must eventually export all transcript
sessions without importing `friday-chat` or `friday-cli`. Extract the
remaining two-file `/transcript export` directory-creation and write
effects into the existing UI-neutral Runtime export-file module. N01B-03
already supplies exact content serializers; N01B-04 supplies root/path
rules. Chat continues to decide which sessions to export, collect/flatten
entries, generate the UTC timestamped directory name, resolve three safe
paths, wrap the Chat-owned result and format the command output. The TUI
does not call the new functions yet. Existing Chat and `friday-cli`
queries, bytes, path calls, outputs, errors and partial-file effects
must remain unchanged.

## Exact change boundary after approval

1. Edit only
   `packages/friday-runtime/src/friday_runtime/transcript_export_files.py`
   to add two typed, synchronous functions:
   `create_all_session_export_directory(destination: Path) -> None`
   performs exactly `destination.mkdir(parents=False, exist_ok=False)`;
   `write_all_session_files(sessions_destination: Path,
   entries_destination: Path, sessions:
   Sequence[TranscriptSessionView], entries:
   Sequence[TranscriptEntryView]) -> None` writes
   `serialize_sessions_csv(sessions)` with UTF-8 to the first path, then
   `serialize_entries_csv(entries)` with UTF-8 to the second. Each path
   receives one `Path.write_text` call. Export both names in `__all__`.
2. Edit only
   `packages/friday-chat/src/friday_chat/commands/transcript.py` to
   keep `_write_all_session_export` as the Chat wrapper. In the exact
   current order, it calls `export_directory(context)`, generates the
   same UTC timestamp/name, calls `_safe_export_path` for the directory,
   delegates its creation to Runtime, calls `_safe_export_path` for
   `sessions.csv` and `entries.csv`, flattens ordered sessions/entries,
   delegates the two writes to Runtime, and returns the same
   `TranscriptExportResult`. Keep `_export_all_sessions` query policy,
   output and exception handling unchanged. Remove only the two now-
   unused serializer imports from this Chat module.
3. Edit only
   `packages/friday-runtime/tests_runtime/test_transcript_export_files.py`
   for direct neutral directory and two-file effects without importing
   Chat or CLI.
4. Edit only
   `packages/friday-chat/tests_chat/test_transcript_export_file_delegation.py`
   to verify Chat's delegation, ordering, output, result identity and
   preserved failure effects. Existing Chat and `friday-cli` tests are
   protected comparison fixtures and must not be edited.

Scoped TUI planning/evidence files, TUI board events and the generated
dashboard may be updated. No other product source/test path,
`friday_chat.transcripts`, CLI or TUI package, dependency metadata, lock,
workflow, script, runtime configuration or user guide may change. A newly
needed path or semantic change requires an amended directive and explicit
approval first.

## Required behavior and boundaries

- Runtime functions may import standard-library modules, the existing
  neutral transcript views and export serializers. They must not import
  Chat, CLI, a provider, config, persistent store or command registry.
  They do not query or mutate transcript persistence.
- All paths are caller-prevalidated. The neutral functions choose no
  root, timestamp or filename, validate no path and create no export
  root. A future TUI caller must compose them with N01B-04 path rules.
  Chat must retain its three `_safe_export_path` calls and existing
  monkeypatch seams in the same order.
- Directory creation remains after the directory path check but before
  the two child path checks. Preserve `parents=False`, `exist_ok=False`,
  default permissions, collision failure and error propagation. Do not
  introduce atomic write, temporary file, rollback, cleanup, chmod,
  retry or directory reuse.
- Write `sessions.csv` before `entries.csv` with the exact N01B-03
  serializers and UTF-8 encoding. A failure on the second write leaves
  the directory and completed first file in place; a child-path failure
  after directory creation also leaves the directory in place.
  Empty exports still create both CSV files with headers.
- Keep the 1,000-session query limit, non-archived filter, per-session
  query order, session/entry flattening order, command aliases, generic
  failure prose, success counts/directory prose and Chat-owned
  `TranscriptExportResult` module identity/defaults. The current-session
  and prompt-log single-file writers remain unchanged. `/context --file`
  and `/prompt --file` remain unchanged Chat effects.
- No TUI executable, installed terminal UAT, real-provider check or
  full command parity is claimed by this unit.

## Verification and stop conditions

1. Retain the [253-pass unchanged baseline and disposable failure
   characterization](../validation/N01B-06-before-code-all-session-export-characterization.md).
   Direct Runtime tests cover exact Unicode/embedded-newline UTF-8 bytes
   and two frozen hashes, empty headers, one mkdir call/flags, collision,
   no parent creation, no implicit path/root choice, ordered writes,
   propagation of either write failure and retained first-file effects
   on second-file failure. Import the neutral module with Chat/CLI
   unavailable.
2. Through Chat commands on fake and disposable SQLite stores, compare
   `sessions.csv` and `entries.csv` against the frozen hashes and
   verify timestamp/name, all three safe-path calls and their order,
   archive exclusion, zero sessions, query limit/order, exact result
   class/counts and command outputs. Inject collision, directory/path
   and second-write failures: the handler keeps its generic error and
   the filesystem keeps precisely the existing effects. Retain all
   five N01B-05 single-file hashes and unchanged `/context --file` /
   `/prompt --file` behavior. Run unchanged production, export, query,
   session and full `friday-cli` comparisons without editing their tests.
3. Run full Runtime and Chat suites, scoped Ruff check/format and
   targeted Mypy, `uv lock --check --offline`, board/dashboard and
   changed-document link checks, and `git diff --check`; inspect
   exact changed paths. Build Runtime and Chat wheels. From an
   isolated Runtime-only install, exercise both new functions with
   Chat/CLI unavailable and compare exact bytes/failure effects.
   Then install Chat separately and compare installed command exports
   and all seven frozen hashes. Existing Ubuntu automation may verify
   exact pushed source only after a separately authorized non-force
   push. Installed macOS/Linux TUI terminal UAT remains a release gate.
4. Record commands, counts, byte comparisons and limits in a local
   report. Commit a stable candidate and hand exact authority,
   directive, commit/diff and checks to a fresh-context read-only
   validator. A changed candidate needs fresh review. `VERIFIED` is a
   work-unit gate, not maintainer acceptance or permission to push,
   merge or release.

Stop if Runtime imports a frontend, a protected Chat/`friday-cli`
behavior or byte changes, Chat's path seam or result identity moves, an
existing protected test needs editing, an export becomes atomic, or another
source/test/metadata path is needed. Do not begin transcript persistence,
session lifecycle, assembly/close or TUI implementation under this
directive.

**Approval fields:** Chuck Russell replied “approved continue with next
steps” immediately after the controller stated that N01B-06 awaited exact
directive approval. Before code work, the controller linked this directive
and stated the interpretation: approval covers its four named local
Runtime/Chat source/test paths and scoped TUI packet evidence only.
A separate one-push authorization would be required for later exact-source
Ubuntu verification; PR, merge, release, installed TUI UAT and later N01B
subunits are not authorized.
