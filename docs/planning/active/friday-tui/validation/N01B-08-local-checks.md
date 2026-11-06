# TUI-N01B-08 local construction checks

**Date/branch:** 2026-10-19, `feature/friday-tui`.
**Approved directive:** [CD-TUI-N01B-08](../directives/CD-TUI-N01B-08-neutral-transcript-write-effects.md).
**Before-code evidence:** [279-pass characterization](N01B-08-before-code-transcript-write-characterization.md)
on product bytes matching pushed `4a646dc7`.
**Authority commit:** `0268ec33` records the maintainer's exact local
four-path approval before product edits.
**Builder outcome:** Local checks passed. The four-path candidate is ready
for a stable commit and fresh-context read-only review. No N01B-08 push,
exact-source Ubuntu run, installed TUI terminal UAT or maintainer acceptance
is claimed.

## Bounded change and preserved behavior

The new `friday_runtime.transcript_write_effects` module exposes a narrow
structural write-store protocol and one async effect. It appends the
caller-constructed `TranscriptEntry`, reads pending raw context **after** the
append await, and optionally constructs and stores `ContextLogEntry` from
the entry identity. It returns whether a context-log call was attempted.
It preserves the exact false-append error and ignores a `False` result from
context logging, matching current Chat behavior. Exceptions and
cancellation propagate without rollback or retry.

`FrameworkTranscriptAdapter.record_interaction` delegates only that
append/context block. Chat still owns preflight, session creation, turn
numbering, tool and entry construction, pending-state clearing, cached-turn
advance and MCP receipt readback. In particular, a context-log exception
can leave an entry committed while pending context and cached turn state
remain unchanged. The TUI does not call this effect yet. No existing
Chat/CLI public signature or `friday-cli` source changed.

Nine new direct Runtime tests cover no context, successful and false-result
context writes, exact entry/context identity, false/raised append, raised
or cancelled context, late pending read and frontend import isolation.
Nine new Chat tests cover delegation and store order, persisted data,
no-context and false-context cases, append failures, partial context
failure and retry state, late pending data, unsafe MCP preflight and receipt
readback. Existing N01B-07 and MCP-memory fixtures remain unchanged.

The first focused run had one failure in the new MCP receipt test because
its fixture omitted the established transcript correlation. Correcting
the fixture restored the expected receipt contract; no product edit was
needed for that failure. The final focused run passed all 23 tests (18 new,
five protected N01B-07 delegation tests).

## Local gates

Tests used `UV_CACHE_DIR=/private/tmp/friday-tui-uv-cache`,
`LITELLM_LOCAL_MODEL_COST_MAP=true`, `PYTHONDONTWRITEBYTECODE=1`,
`PYTEST_ADDOPTS='-p no:cacheprovider'` and `uv run --frozen --offline`.
Runtime and Chat full-suite synthetic HTTP/MCP fixtures used loopback bind
access; no live provider or remote service was used.

| Gate | Result |
| --- | --- |
| New direct Runtime and Chat plus protected N01B-07 delegation | 23 passed. |
| Full Runtime package | 402 passed. |
| Full Chat package | 880 passed, five skipped, one existing deprecation warning. |
| Unchanged full `friday-cli` package | 155 passed. |
| Ruff check on the four exact source/test paths | Passed. |
| Ruff format check on new Runtime source and both new test files | Passed. The pre-existing large Chat adapter is not formatter-clean and was not reformatted outside the directive's narrow delegation diff. Its formatter diff has the same 74 removed and 151 added lines at authority base and candidate. |
| Targeted Mypy on all four exact source/test paths | No issues. |
| `uv lock --check --offline` | Passed; lock unchanged. |

## Installed-wheel boundary

`uv build --all-packages --wheel --offline` built all 17 workspace wheels
under `/private/tmp/friday-tui-n01b08-wheels`. The built Runtime module
and Chat adapter match checkout bytes exactly:

| Wheel member | SHA-256 |
| --- | --- |
| `friday_runtime/transcript_write_effects.py` | `20fa34ef6f6abb013cfd2397946246ade46b45e67dac6a69f419c3b83af295a7` |
| `friday_chat/adapters.py` | `ab653ed3ab3db2f0b3643a244fb177e33515ed1b80065ed1c9defc75ec4a83a3` |

The Runtime wheel metadata has no Chat or CLI dependency. An isolated
Python 3.13.10 Runtime-only environment installed 111 compatible packages;
from `/private/tmp`, `python -I` exercised append and optional context
effects and confirmed Chat/CLI were unavailable and not imported. A
separate installed Chat environment contained 127 compatible packages.
Its wheel-byte-verified Chat and Runtime modules persisted a safe MCP
entry/context log, read back the matching receipt and rejected an unsafe
second entry without a write. `uv pip check` passed in both environments.
These disposable environments are outside the repository.

## Remaining gate

Board validation passed for 34 tasks, the generated dashboard is current,
the unique-key authority JSON parsed in its frozen validation state, and
392 changed-document local Markdown links resolved. Exact staged paths and
whitespace checks are recorded with the stable candidate commit. Freeze
the four product/test paths and request fresh-context, read-only independent
review against authority base `0268ec33`. An exact-source Ubuntu run would
require separate push authority. Installed macOS/Linux TUI terminal UAT,
controlled real-provider/tool tests and the rest of the neutral transcript
writer remain later gates.
