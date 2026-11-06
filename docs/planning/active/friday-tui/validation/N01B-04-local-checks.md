# TUI-N01B-04 local construction checks

**Date/branch:** 2026-10-19, `feature/friday-tui`.
**Approved directive:** [CD-TUI-N01B-04](../directives/CD-TUI-N01B-04-neutral-export-destination-paths.md).
**Pre-code base:** clean planning commit `401d10583a19c1b1689cdeb7046d00e5352e5819`;
the [before-code characterization](N01B-04-before-code-export-path-characterization.md)
records the unchanged product source at `3b91c5b55a567fd5225a6430bf27fbaef35fefbf`.
**Outcome:** Local builder checks passed. Candidate freeze and fresh independent
review are next; no Ubuntu exact-source run, installed TUI UAT or maintainer
acceptance is claimed.

## Exact construction and behavior

The new `friday_runtime.transcript_export_paths` contains only standard-library
path code. `resolve_export_directory` retains `./exports` for absent/empty
configuration, current-directory anchoring, non-strict resolution, recursive
creation and repeat-call behavior. `safe_export_path` retains root/child
resolution, traversal and symlink containment, and the exact escape error.
Chat's public `export_directory` and private `_safe_export_path` delegate to
those neutral functions. The Chat registry still uses its existing public
helper for `/context --file` and `/prompt --file`. Session/format decisions,
timestamps, filenames, content serialization, UTF-8 writes, file effects,
`TranscriptExportResult` and command results remain in Chat. No `friday-cli`,
other Chat/Runtime source, package metadata, dependency lock, workflow or
runtime configuration changed.

The direct Runtime tests exercise default, empty, relative, absolute and
symlinked roots, recursive creation, idempotence and root-as-file failure;
contained children, traversal and file/directory symlink escapes; and no
unintended file writes. New Chat tests exercise actual registry commands,
delegate calls, exact configured paths/output/files and shared-export root
failure. Existing unchanged tests protect fake and disposable SQLite export
backends, seven frozen export hashes, empty cases, result identity and full
`friday-cli` behavior.

## Test and static evidence

Tests used `UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache`,
`PYTHONDONTWRITEBYTECODE=1`, `PYTEST_ADDOPTS='-p no:cacheprovider'` and
`LITELLM_LOCAL_MODEL_COST_MAP=true`. Full package tests had local loopback
access for disposable MCP/HTTP fixtures; they did not use a live provider.

| Gate | Local result |
| --- | --- |
| New Runtime and Chat tests | 13 passed. |
| Focused Runtime/Chat export, query, context, session and full protected `friday-cli` comparison | 239 passed after the final source edit; the pre-code comparison had 226 passes. |
| Full Runtime package | 365 passed. |
| Full Chat package | 860 passed, five skipped, one existing deprecation warning. |
| Ruff check on the four scoped source/test paths | Passed. |
| Targeted Mypy on the same four paths | No issues. |
| Ruff format on the three new files and edited Chat ranges | Passed. Whole-file Chat formatting remains red on four pre-existing, unrelated ranges; the same baseline file at `401d1058` is also red. |
| `uv lock --check --offline` | Passed; lock unchanged. |
| Board validation and generated dashboard | Passed for 34 tasks; dashboard current. |

The focused comparison includes all unchanged `packages/friday-cli/tests_cli`
tests. Its command is:

```sh
UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' LITELLM_LOCAL_MODEL_COST_MAP=true uv run --frozen --offline pytest -q packages/friday-runtime/tests_runtime/test_transcript_export_paths.py packages/friday-runtime/tests_runtime/test_transcript_export_format.py packages/friday-runtime/tests_runtime/test_transcript_views.py packages/friday-runtime/tests_runtime/test_transcript_queries.py packages/friday-chat/tests_chat/test_transcript_export_path_delegation.py packages/friday-chat/tests_chat/test_transcript_export_format_delegation.py packages/friday-chat/tests_chat/test_transcript_query_facade.py packages/friday-chat/tests_chat/test_transcript_query_adapter_delegation.py packages/friday-chat/tests_chat/test_transcript_production_commands.py packages/friday-chat/tests_chat/test_transcript_export_commands.py packages/friday-chat/tests_chat/test_session_identity.py packages/friday-chat/tests_chat/test_session_memory_commands.py packages/friday-chat/tests_chat/test_command_registry.py packages/friday-cli/tests_cli
```

Full package commands used the same environment and `uv run --frozen
--offline pytest -q` on `packages/friday-runtime/tests_runtime` and
`packages/friday-chat/tests_chat`, separately because their test module names
overlap. The final focused comparison, Ruff and targeted Mypy were repeated
after the last source-formatting edit; no later product source/test edits were
made.

## Installed-wheel boundary and file comparison

All 13 relevant wheels were built offline in
`/private/tmp/friday-tui-n01b04-wheels`. The final Chat and Runtime wheel source
bytes match the checkout. Runtime wheel metadata has no Chat/CLI requirement
and includes `friday_runtime/transcript_export_paths.py`.

An isolated Python 3.13 venv installed Runtime and its dependencies only;
`uv pip check` passed for 111 packages. From `/private/tmp`, `python -I`
confirmed Chat/CLI were unavailable and loaded the neutral module from the
installed wheel. A disposable-directory probe confirmed default/empty root
creation, contained children, exact traversal/symlink rejection and an
unmodified outside file.

Chat and its dependencies were then installed separately; `uv pip check`
passed for 130 packages. An isolated `python -I` process used the installed
Chat registry, a fixed fake transcript view and a disposable configured root.
It exercised `/transcript export`, `/export` in default/CSV/JSONL/training/
Markdown forms, `/export-prompts`, `/context --file` and `/prompt --file`.
All seven export-file SHA-256 digests matched the
[frozen before-code values](N01B-03-before-code-characterization.md), and the
two shared file commands retained exact output, filenames and bytes. The
installed Chat `TranscriptExportResult` retained its Chat identity. The final
installed probe was repeated after rebuilding/reinstalling the Chat wheel for
the last formatting edit.

## Remaining gate

Repository-wide documentation lifecycle validation still reports six broken
absolute `/private/tmp/telem-01/review` links in the unchanged telemetry
review report. They predate this unit and are outside its exact directive.
All 292 local links in the changed N01B-04 planning documents resolve. Exact
13-path staged allowlist and whitespace checks passed at candidate freeze,
with no unstaged or untracked files.

Freeze the exact local candidate and request a fresh-context, read-only
independent review of the approved directive, authority, diff and evidence.
Source remains scoped to four paths. No branch push, PR, merge, release,
exact-source Ubuntu run, installed macOS/Linux TUI terminal UAT, full TUI
command parity or maintainer acceptance is inferred from these local checks.
