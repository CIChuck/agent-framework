# TUI-N01B-06 local construction checks

**Date/branch:** 2026-10-19, `feature/friday-tui`.
**Approved directive:** [CD-TUI-N01B-06](../directives/CD-TUI-N01B-06-neutral-all-session-export-effects.md).
**Before-code evidence:** [253-pass characterization](N01B-06-before-code-all-session-export-characterization.md)
at unchanged product source `010849f5`.
**Authority commit:** `d6ababf1` recorded the maintainer's exact local
approval before code edits.
**Outcome:** Local builder checks passed. Freeze the four-path candidate
and request fresh-context read-only independent review. No N01B-06 push,
exact-source Ubuntu run, installed TUI terminal UAT or maintainer
acceptance is claimed.

## Bounded change

`friday_runtime.transcript_export_files` now provides one typed function
to create a caller-named all-session directory with
`parents=False, exist_ok=False`, and one to write `sessions.csv` followed
by `entries.csv` from the existing neutral serializers to caller-validated
paths. Both propagate errors; a failure on the second write retains the
directory and completed first file. No root, timestamp, filename, query,
path-validation, cleanup or Chat result choice moved into Runtime.

Chat's `_write_all_session_export` retains its public root helper, UTC
timestamp/name, all three private safe-path calls and their order, session
and entry flattening, Chat-owned `TranscriptExportResult`, handler output
and generic error behavior. The two N01B-05 single-file wrappers and
shared `/context --file` and `/prompt --file` paths are unchanged. No
`friday-cli`, TUI, metadata, lock, workflow or other product path changed.

Five new Runtime cases cover directory flags/collision/missing parent,
exact UTF-8 and two frozen hashes, empty CSV headers, and first-/second-
write failure order and retained effects. Four new Chat cases cover
delegation and safe-path sequence, result identity/counts, frozen hashes,
query limit/order, command collision output and partial path/write
failure effects. Existing fake and disposable SQLite comparisons retain
all seven export hashes and archived-session behavior.

## Tests and static gates

Tests used `UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache`,
`LITELLM_LOCAL_MODEL_COST_MAP=true`, `PYTHONDONTWRITEBYTECODE=1`,
`PYTEST_ADDOPTS='-p no:cacheprovider'` and `uv run --frozen --offline`.
Full Runtime and Chat suites had local loopback access for existing
HTTP/MCP fixtures; no live provider was used.

| Gate | Result |
| --- | --- |
| Direct Runtime file-effect tests | 17 passed. |
| Focused Runtime/Chat export, query, session and protected full `friday-cli` comparison | 262 passed; unchanged before-code comparison was 253. |
| Full Runtime package | 382 passed. |
| Full Chat package | 866 passed, five skipped, one existing deprecation warning. |
| Unchanged full `friday-cli` package | 155 passed. |
| Ruff check on four scoped source/test paths | Passed. |
| Ruff format on Runtime source and both edited tests | Passed. Whole-file Chat source remains red on four pre-existing, unrelated ranges; the same ranges were present at authority commit `d6ababf1` and none is in an edited hunk. |
| Targeted Mypy on four scoped source/test paths | No issues. |
| `uv lock --check --offline` | Passed; lock unchanged. |
| Board validation, dashboard, authority JSON and `git diff --check` | Passed; board has 34 tasks. |

The full suites ran after the last test-formatting edit. The product diff
has exactly the four approved source/test paths, plus this scoped evidence
report. No test or configuration outside those paths was edited.

## Installed-wheel boundary

`uv build --all-packages --wheel --offline` built all 17 workspace wheels
in `/private/tmp/friday-tui-n01b06-wheels`. Runtime and Chat wheel members
for the edited source files match checkout bytes. Runtime wheel metadata
has no Chat or CLI dependency. An isolated Python 3.13.10 environment
installed Runtime and its dependencies only: `uv pip check` passed for
111 packages. From `/private/tmp`, `python -I` loaded the installed neutral
module with Chat and CLI unavailable. The two new effects plus the five
existing single-file effects matched all seven frozen SHA-256 values;
collision and second-write partial failure retained the established
filesystem effects.

Chat and its dependencies were then installed separately; `uv pip check`
passed for 127 packages. An isolated `python -I` process ran the installed
Chat registry: `/transcript export`, `/export` default/CSV/JSONL/training/
Markdown/`md`, `/export-prompts`, `/context --file` and `/prompt --file`
retained outputs and files. All seven frozen export hashes and the two
shared file-command bytes matched; `TranscriptExportResult` retained its
Chat module identity. The temporary probe scripts and venv are outside
the repository and are not committed evidence.

## Remaining boundary

Freeze the exact four-path candidate, reconcile board/dashboard, authority,
links and changed-path checks, then obtain independent review. The
repository-wide documentation lifecycle check has a known unrelated
six-link failure in an unchanged telemetry report; changed N01B-06
planning links will be checked separately. Installed macOS/Linux TUI
terminal UAT and a controlled real-provider/tool run remain later release
gates. A separate authorization is required before any branch push or
exact-source Ubuntu run for this unit.
