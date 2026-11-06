# TUI-N01B-05 local construction checks

**Date/branch:** 2026-10-19, `feature/friday-tui`.
**Approved directive:** [CD-TUI-N01B-05](../directives/CD-TUI-N01B-05-neutral-single-file-export-effects.md).
**Before-code evidence:** [239-pass characterization](N01B-05-before-code-single-file-export-characterization.md) at unchanged product source `887e43a02d7213e65436b1d85bfafbe255ac865c`.
**Authority commit:** `13bc923f` recorded the maintainer's exact local approval before code edits.
**Outcome:** Local builder checks passed. Freeze the candidate and request a fresh-context read-only review. No N01B-05 push, exact-source Ubuntu run, installed TUI terminal UAT or maintainer acceptance is claimed.

## Bounded change

The new `friday_runtime.transcript_export_files` writes one caller-prevalidated
current-session or context-log export with the existing neutral serializers and
one UTF-8 `Path.write_text` call. It makes no root, filename, directory,
configuration, store or command decision. Chat's two single-file wrappers keep
their public export-root and private safe-path calls, fixed filenames,
Markdown-only display-name lookup, Chat-owned `TranscriptExportResult`, counts,
handler output and generic error behavior. The two-file `/transcript export`
writer and shared `/context --file` and `/prompt --file` paths were not edited.
No CLI, TUI, metadata, lock, workflow or other product path changed.

Direct Runtime tests cover all four canonical formats and prompt JSON, exact
Unicode and embedded-newline bytes, empty outputs, overwrite, absent parent,
unsupported direct format, missing Markdown names, one UTF-8 write call with
propagated failure, and import without frontend modules. New Chat registry
tests observe Runtime delegation, format/path/name selection, exact file bytes,
result identity/counts, no-log handling and generic write error. The unchanged
Chat fixture pins all seven before-code export hashes on fake and disposable
SQLite stores and protects the path-hook seam and two-file behavior.

## Tests and static gates

Commands used `UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache`,
`LITELLM_LOCAL_MODEL_COST_MAP=true`, `PYTHONDONTWRITEBYTECODE=1` and
`PYTEST_ADDOPTS='-p no:cacheprovider'` with `uv run --frozen --offline`.
The full-package reruns had local loopback access for disposable HTTP/MCP
fixtures and no live provider.

| Gate | Result |
| --- | --- |
| New Runtime and Chat tests | 14 passed. |
| Final focused Runtime/Chat export, query, session and protected full `friday-cli` comparison | 253 passed; pre-code comparison was 239. |
| Full Runtime package | 377 passed. |
| Full Chat package | 862 passed, five skipped, one existing deprecation warning. |
| Unchanged full `friday-cli` package | 155 passed. |
| Ruff check on four scoped source/test paths | Passed. |
| Targeted Mypy on four scoped source/test paths | No issues. |
| Ruff format on three new files | Passed. Whole-file Chat formatting remains red on four unchanged, unrelated ranges in the pre-code file; no edited range is identified by Ruff. |
| `uv lock --check --offline` | Passed; lock unchanged. |
| Board validation and generated dashboard | Passed for 34 tasks; dashboard rendered. |

The initial sandboxed full Runtime and Chat runs failed only where existing
localhost HTTP/MCP fixtures could not bind `127.0.0.1` (nine Runtime failures,
ten Chat failures and three Chat setup errors). Rerunning those same full
suites with loopback access passed at the counts above. No product edit was
made to address the sandbox restriction.

The final focused comparison and Ruff/Mypy checks were repeated after the
last test-file formatting edit. Full suites and wheel builds preceded only
that test formatting edit; product source was unchanged. `git diff --check`
passed.

## Installed-wheel boundary

`uv build --all-packages --wheel --offline` built all 17 workspace wheels in
`/private/tmp/friday-tui-n01b05-wheels`. Runtime and Chat wheel copies of the
changed product source match checkout bytes. An isolated Python 3.13 venv
installed Runtime and its dependencies only: `uv pip check` passed for 111
packages. From `/private/tmp`, `python -I` loaded the installed neutral writer,
confirmed `friday_chat` and `friday_cli` were unavailable and absent from
loaded modules, found no Chat/CLI Runtime requirement, and matched all five
frozen single-file SHA-256 values with disposable files.

Chat and its dependencies were then installed separately; `uv pip check`
passed for 127 packages. An isolated `python -I` process ran the installed
Chat registry with deterministic persisted views. `/transcript export`,
`/export` default/CSV/JSONL/training/Markdown/`md`, `/export-prompts`,
`/context --file` and `/prompt --file` retained their outputs and files. All
seven export hashes matched the [frozen before-code values](N01B-05-before-code-single-file-export-characterization.md),
and the two shared file commands retained exact UTF-8 bytes. The installed
`TranscriptExportResult` retained its Chat module identity.

## Remaining boundary

Repository-wide documentation lifecycle validation still reports six broken
absolute `/private/tmp/telem-01/review` links in an unchanged telemetry
report. They predate this unit and are outside the directive. Changed N01B-05
planning-document local links, exact changed-path allowlist, board/dashboard,
authority JSON, whitespace and offline lock checks must be reconciled at
candidate freeze. Installed macOS/Linux TUI terminal UAT and a controlled
real-provider/tool run remain later release gates. A separate authorization
is required before a branch push or exact-source Ubuntu run for this unit.
