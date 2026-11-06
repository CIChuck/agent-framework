# TUI-N01B-07 local construction checks

**Date/branch:** 2026-10-19, `feature/friday-tui`.
**Approved directive:** [CD-TUI-N01B-07](../directives/CD-TUI-N01B-07-neutral-transcript-tool-records.md).
**Before-code evidence:** [303-pass characterization](N01B-07-before-code-transcript-tool-record-characterization.md)
at unchanged pushed product source `aa8ae784`.
**Authority commit:** `f78ab6aa` records the maintainer's exact local
four-path approval before code edits.
**Outcome at builder check:** Local checks passed; candidate was ready for
fresh-context read-only independent review. No N01B-07 push, exact-source
Ubuntu run, installed TUI terminal UAT or maintainer acceptance is claimed.

## Bounded change

The new `friday_runtime.transcript_tool_records` module exposes a structural
`TranscriptToolCallInput` protocol and two UI-neutral functions. The first
rejects unsafe MCP facts and correlates valid provenance before a caller
touches a transcript store. The second constructs `ToolCall` and
`ToolResult` models after the caller has established session/turn order.
It retains caller-supplied and fallback IDs, copied arguments, UTF-8 result
byte limits, fixed failure-code mapping and existing error messages.

`FrameworkTranscriptAdapter.record_interaction` delegates those two stages
in their prior order. Chat still owns the session, turn-number cache,
`TranscriptEntry`, append, pending context log, MCP receipt/readback and
`record_turn` compatibility method. No TUI package, complete neutral
transcript writer, persistence policy, CLI source, package metadata,
workflow or lock was changed.

Eleven new direct Runtime cases cover empty/native/MCP/mixed calls, provided
and fallback IDs, argument copying, exact Unicode byte boundary, seven
unsafe preflight conditions, invalid correlation error and frontend import
isolation. Five new Chat cases cover delegation/store order, persisted
entry/context data, mixed receipt readback, rejected preflight with zero
store effects, model-construction timing after session creation, and append
failure plus retry. Existing Runtime, Chat and `friday-cli` tests remain
unchanged comparison fixtures.

## Tests and static gates

Tests used `UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache`,
`LITELLM_LOCAL_MODEL_COST_MAP=true`, `PYTHONDONTWRITEBYTECODE=1`,
`PYTEST_ADDOPTS='-p no:cacheprovider'` and `uv run --frozen --offline`.
No live provider was used. Full Runtime and Chat runs used loopback access
for existing synthetic HTTP/MCP fixtures.

| Gate | Result |
| --- | --- |
| New direct Runtime and Chat tests | 16 passed (11 Runtime, five Chat). |
| Full Runtime package | 393 passed. |
| Full Chat package | 871 passed, five skipped, one existing deprecation warning. |
| Unchanged full `friday-cli` package | 155 passed. |
| Ruff check on four scoped source/test paths | Passed. |
| Ruff format on new Runtime source and both new tests | Passed. The whole Chat adapter remains unformatted at baseline: formatter edit lines were identical before and after this bounded change (74 removals, 151 additions). |
| Targeted Mypy on four scoped source/test paths | No issues. |
| `uv lock --check --offline` | Passed; lock unchanged. |
| Board/dashboard, authority JSON, changed links and exact path/whitespace checks | Board passed for 34 tasks; dashboard current; JSON parsed; 388 local Markdown links resolved; exactly four approved product/test paths; diff check passed. |

The first sandboxed full Runtime attempt had 384 passes and nine existing
HTTP fixture failures because binding `127.0.0.1` was denied. The unchanged
suite passed 393/393 when rerun with loopback access. These were sandbox
restrictions, not source failures. The full suites ran after the last code
or test edit.

## Installed-wheel boundary

`uv build --all-packages --wheel --offline` built all 17 workspace wheels
under `/private/tmp/friday-tui-n01b07-wheels`. The Runtime wheel's new
module and Chat wheel's edited adapter match checkout bytes: SHA-256
`e64238f0bf8be99fe6f415d278fba6f52b41bb3ced9114e5cd081692ab5108f0`
and
`50d16899eba618b7778e86dc707e0708c3056cb86e0fa4f9cc1c00a310aa1a8c`,
respectively. Runtime wheel metadata excludes Chat and CLI dependencies.

An isolated Python 3.13.10 Runtime-only environment installed 111
compatible packages. From `/private/tmp`, `python -I` confirmed Chat/CLI
are unavailable, exercised both neutral functions with native and MCP
records and rejected unsafe raw MCP arguments. A separate installed Chat
environment with 127 compatible packages persisted a mixed MCP/native
entry and context log through `FrameworkTranscriptAdapter`, read back the
matching receipt and rejected an unsafe second entry without a write.
Both environments passed `uv pip check`. Temporary wheel and probe state
is outside the repository and not committed.

## Remaining boundary

The four scoped product/test paths were committed as stable candidate
`a196e95a`. Subsequently, a fresh-context
[independent review](VAL-N01B-07-prepush-a196e95a.md) returned `VERIFIED` for
the local N01B-07 work unit. The four product/test paths are now frozen.
Installed macOS/Linux TUI terminal UAT, controlled real-provider/tool
testing, later neutral transcript persistence and full initiative
acceptance remain separate gates. A separate authorization is required
before any N01B-07 branch push or exact-source Ubuntu run.
