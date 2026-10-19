# TUI-N01B-09 local session-ensure construction checks

**Date/branch:** 2026-10-19, `feature/friday-tui`.
**Approved directive:** [CD-TUI-N01B-09](../directives/CD-TUI-N01B-09-neutral-transcript-session-ensure.md).
**Before-code evidence:** [225-pass characterization](N01B-09-before-code-session-ensure-characterization.md)
on product bytes matching pushed `c4a5faa6`.
**Authority commit:** `ee9d667c` records Chuck Russell's exact four-path
local approval before product edits.
**Builder outcome:** Local checks passed. Freeze the four-path candidate for
fresh-context read-only independent validation. No additional push, exact-source
Ubuntu run, installed TUI terminal UAT or maintainer acceptance is claimed.

## Bounded change and behavior comparison

The new `friday_runtime.transcript_session_effects` module exposes a structural
store protocol and one async effect. It reads a session by ID, calls the
caller-supplied factory only on a miss, awaits one create, and ignores the
create Boolean. A returned session is left alone. Get, factory and create
exceptions or cancellation propagate. The module imports no Chat or CLI code.

`FrameworkTranscriptAdapter._ensure_session` now delegates that effect but
still constructs the existing Chat-specific session model and JSON snapshot
inside a lazy factory. MCP provider configuration is omitted from a new
snapshot by the exact pre-existing expression; other provider shape remains.
Preflight, count, entry/tool construction, append/context handling, receipt
readback and finalization stay in Chat. No existing public signature changes.
The TUI does not call the helper in this unit.

The 22 new direct Runtime and Chat tests cover missing/repeated, existing,
ended and archived sessions, factory timing, false create, exception and
cancellation propagation, frontend import isolation, actual SQLite fields and
snapshots, preflight/get/create/count/append order, historical snapshot
preservation, downstream false-create append failure, and unsafe MCP preflight.
The first targeted run found that a new archived-session fixture expected
`SQLiteTranscriptStore.create_session` to persist its model's `archived` field;
the existing insert does not write that column. The corrected fixture calls
`archive_session` explicitly and checks the persisted SQL column. The existing
session-model reader also does not reflect that archived column in this
checkout, so the test reads the SQL row directly. Neither store implementation
nor established behavior was changed.

## Local gates

Tests used `UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache`,
`LITELLM_LOCAL_MODEL_COST_MAP=true`, `PYTHONDONTWRITEBYTECODE=1`,
`PYTEST_ADDOPTS='-p no:cacheprovider'` and `uv run --frozen --offline`.
Full Runtime/Chat synthetic HTTP/TLS fixtures needed local loopback bind
access. The initial sandboxed full runs failed only at `127.0.0.1` bind
permission; the same complete suites passed when run with loopback access.
No live provider or remote service was used.

| Gate | Result |
| --- | --- |
| New direct Runtime and Chat tests | 22 passed. |
| Full Runtime package | 414 passed. |
| Full Chat package | 890 passed, five skipped, one existing deprecation warning. |
| Unchanged full `friday-cli` package | 155 passed. |
| Ruff check on four exact source/test paths | Passed. |
| Ruff format check on the new Runtime source and both new test files | Passed. The pre-existing large Chat adapter was not reformatted beyond its narrow import/delegation edit. |
| Targeted Mypy on all four exact source/test paths | No issues. |
| `uv lock --check --offline` | Passed; lock unchanged. |

## Installed-wheel boundary

`uv build --all-packages --wheel --offline` built all 17 workspace wheels
under `/private/tmp/friday-tui-n01b09-wheels`. The new Runtime module and
edited Chat adapter match checkout bytes exactly:

| Wheel member | SHA-256 |
| --- | --- |
| `friday_runtime/transcript_session_effects.py` | `651c914393c9ea5fd41d836ccd99ac84fe65c993980ed6a8aea852cbe7226b8a` |
| `friday_chat/adapters.py` | `53083cada7383b0b2756ce30b5a0f7c3a8df5d550a3c948720d9369e65e8b1d7` |

The Runtime wheel metadata has no Chat or CLI dependency. An isolated
Python 3.13.10 Runtime-only environment installed 111 compatible packages;
from `/private/tmp`, `python -I` verified Chat and CLI were unavailable and
persisted/reused a session through the neutral helper and SQLite. A separate
installed Chat environment had 127 compatible packages; `python -I`
persisted a Chat interaction and checked the session snapshot and entry.
`uv pip check` passed in both environments. These environments are disposable
and outside the repository.

## Remaining gate

Board/dashboard, authority JSON, changed-document local links, exact changed
paths and whitespace are checked with the candidate. The next gate is a
stable commit and fresh-context, read-only validation against authority base
`ee9d667c`. Exact-source Ubuntu verification requires a separately authorized
non-force push. Installed macOS/Linux TUI terminal UAT and later neutral
transcript units remain open.
