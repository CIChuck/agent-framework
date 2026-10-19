# CD-TUI-N01B-04: neutral export destination and safe paths

**Status:** Proposed for maintainer review; no N01B-04 product-code authority.

**Initiative/unit:** `friday-tui` / TUI-N01B-04, a separate N01B subunit
after N01B-03's independently VERIFIED local and exact-source Ubuntu gates.

**Branch/before-code source:** `feature/friday-tui` /
`3b91c5b55a567fd5225a6430bf27fbaef35fefbf` (clean). The N01B-03
product source is unchanged from pushed `f7950581`.

**Authority and precedence:** [AGENTS.md](../../../../../AGENTS.md) and the
[independent-validation policy](../../../../reference/policies/independent-validation-policy.md)
require explicit maintainer approval of this exact directive before product
code. If approved, the accepted [architecture boundary](../architecture-reset.md),
[replacement plan](../replacement-plan.md),
[capability map](../neutral-capability-map.md),
[before-code characterization](../validation/N01B-04-before-code-export-path-characterization.md),
repository engineering policy and this directive govern the unit. Reconcile
any conflict before editing source.

## Purpose and acceptance

An independently installed TUI must resolve the same export root and reject
paths outside it without importing `friday-chat` or `friday-cli`. Move only
Chat's existing export-root creation and safe child-path resolution into a
UI-neutral Runtime module. Chat's public `export_directory(context)` remains
callable and delegates to that module. Its command handlers and registry
retain identical root choices, generated paths, files, content bytes,
return text and error outcomes. N01B-04 supplies path primitives; it does
not move export file writes or create a TUI executable.

## Exact change boundary after approval

1. Add `packages/friday-runtime/src/friday_runtime/transcript_export_paths.py`
   with typed, synchronous `resolve_export_directory(raw_directory: str |
   None) -> Path` and `safe_export_path(root: Path, *parts: str) -> Path`.
   The first applies the existing default `./exports` for `None` or empty
   string, resolves with `strict=False`, creates parents with `exist_ok=True`
   and returns the resolved root. The second resolves root and candidate
   with `strict=False`, returns the candidate if contained, and otherwise
   raises the existing `ValueError("export path escaped configured root")`.
2. Edit only `packages/friday-chat/src/friday_chat/commands/transcript.py` to
   delegate its public `export_directory(context)` and private safe-path
   use to those Runtime functions. Chat still selects the effective config
   value, calls the same path helpers at the same points, owns all export
   writers and `TranscriptExportResult`, and exposes the same public
   `export_directory` used by `commands.registry` for `/context --file` and
   `/prompt --file`. Do not change `commands.registry` or
   `friday_chat.transcripts`.
3. Add `packages/friday-runtime/tests_runtime/test_transcript_export_paths.py`
   for direct neutral root/path behavior without Chat or CLI imports.
4. Add
   `packages/friday-chat/tests_chat/test_transcript_export_path_delegation.py`
   for command and file-effect comparisons through the unchanged Chat
   registry and disposable backends. Keep all existing Chat and
   `friday-cli` tests unchanged as protected fixtures.

Scoped TUI planning/evidence files, a TUI board event and the generated
dashboard may be updated. No other product source/test path, CLI or TUI
package, dependency metadata, lock, workflow, script, runtime
configuration or user guide may change. A newly needed path or semantic
change requires an amended directive and approval first.

## Required behavior and boundaries

- The neutral module imports only standard-library path facilities. It
  must not import Chat, CLI, a provider, configuration, persistent store or
  serializer. It performs directory creation in `resolve_export_directory`
  and no content writes or network actions.
- Preserve current-cwd anchoring of a default or relative export root,
  configured absolute paths, resolution of an existing root symlink,
  recursive root creation, and repeat-call behavior. A configured root
  that is a file must fail as before. Do not add environment overrides,
  new configuration or new permission policy.
- Preserve traversal and symlink-escape rejection, exact `ValueError`
  message, and paths already inside the resolved root. Do not change the
  order of root creation, timestamped subdirectory creation, path checking
  or subsequent writes in Chat.
- Preserve the public Chat `export_directory` entry point and its behavior
  for `/context --file` and `/prompt --file`, including filenames, UTF-8
  writes, output text and error propagation. Existing transcript handlers
  retain session/format policy, archive filtering, filenames, microsecond
  UTC timestamp, overwrite and partial-failure behavior, result identity,
  counts, errors and seven frozen export byte digests.
- Keep N01B-03 serializers, N01B-01/02 query contracts, Chat/CLI source and
  tests outside this exact boundary frozen. No TUI terminal UAT or full
  command parity is claimed by this unit.

## Verification and stop conditions

1. Retain the [226-pass before-code comparison and disposable path
   probe](../validation/N01B-04-before-code-export-path-characterization.md).
   Direct Runtime tests cover default/empty, relative and absolute roots,
   cwd anchoring, nested creation, idempotence, root-as-file failure, child
   containment, `..` traversal, symlink escapes and a symlinked root.
   Assert exact resolved paths, exceptions and absence of unintended files.
2. Exercise Chat's `/transcript export`, `/export` formats and
   `/export-prompts` with fake and disposable SQLite stores; compare all
   seven frozen hashes, filenames, paths, counts, outputs, empty cases,
   configured/default roots and root/write failures. Check `/context
   --file` and `/prompt --file` through the registry, plus
   `TranscriptExportResult`'s Chat identity. Run unchanged Chat transcript,
   context/command, session-identity and full `friday-cli` comparison tests;
   do not edit protected tests to force a pass.
3. Run full Runtime and Chat suites, Ruff check/format, targeted Mypy,
   `uv lock --check --offline`, board/dashboard and local-link checks, and
   `git diff --check`; inspect the exact path allowlist. Build the Runtime
   wheel and confirm direct path helpers work from an isolated Runtime-only
   install with Chat/CLI unavailable. Install Chat separately and exercise
   the shared export root and transcript commands. Ubuntu exact-source
   automation requires a separately authorized push. Installed macOS/Linux
   TUI terminal UAT remains a later release gate.
4. Record commands, counts, paths, byte comparisons and limitations in a
   local report. Commit a stable candidate and obtain fresh-context,
   read-only independent validation of exact authority, directive, diff and
   checks. A changed candidate needs fresh review. `VERIFIED` is a unit
   gate, not maintainer acceptance or permission to push, merge or release.

Stop if Runtime imports a frontend, a Chat/CLI behavior or export byte
changes, `/context --file` or `/prompt --file` changes, protected tests need
editing, or another source/test/metadata path is needed. Export content
writes, result ownership, transcript writes, session lifecycle,
assembly/close and TUI implementation require later directives.

**Approval fields:** Maintainer approval pending. This proposal and its
before-code evidence do not authorize product source/test generation,
another push, PR, merge, release or later N01B subunits.
