# TUI-CI03 local characterization and candidate checks

**Date:** 2026-10-18 (America/New_York)
**Branch/base:** `feature/friday-tui` / `8013bb57f2499ceb0852b3d16099586649e4e107`
**Scope:** Approved [CD-TUI-CI03](../directives/CD-TUI-CI03-mcp-auto-negotiation.md).
This is local implementation evidence; independent candidate review and Ubuntu
verification are separate gates.

## CI03-A before source correction

A real owned stdio child in `test_stdio_interop.py` delays its first modern
`server/discover` reply beyond the first half of a four-second `auto`
connection budget, but responds before the total deadline. The test observes
the first discovery `TimeoutError`, then legacy `initialize` error `-32022`.
The unavailable-modern case likewise observes that sequence. Before the
source edit, the new tests failed with `MCPError -32022` (2 failed, 12
deselected). Their `finally` assertions proved the initial timeout/rejection
sequence, no `tools/call`, and full child/task reaping. Existing real legacy
`ignore-probe` and `late-probe` cases passed in the characterization run.
This confirms the specific sequence for synthetic peers; it does not assert
that the Ubuntu SDK's internal first-probe timing was directly observed.

## CI03-B/C local result

The shared MCP client now retries modern discovery at most once only when
`auto`'s first modern probe timed out and legacy `initialize` returned
`-32022`. The retry uses the same owned connection and the remaining original
deadline. Synthetic negative cases cover a peer that never answers modern
discovery, a discovery rejection without timeout, and a different legacy
error. Existing legacy and explicit-modern behavior still execute their
original paths. No tool call is replayed.

| Check | Local result |
| --- | --- |
| Real stdio interoperability suite, including new cases, three consecutive runs | 16 passed each run |
| Full `friday-mcp` suite with local loopback access | 2,682 passed |
| Full `friday-runtime` suite | 334 passed |
| Full `friday-chat` suite | 845 passed, 5 skipped, 1 existing deprecation warning |
| Unchanged `friday-cli` suite | 155 passed |
| Ruff for changed MCP source/test | Passed |
| Mypy for changed MCP source | Passed |
| `uv lock --check` | Passed |
| Workflow YAML parse and explicit-modern control assertion | Passed |
| Board validation and `git diff --check` | Passed |

The first sandboxed full MCP run had 2,645 passes and 37 HTTP/TLS fixture
failures because local `127.0.0.1` binds were denied. The full rerun with
loopback access passed all 2,682 cases; the sandbox failures are not counted
as product regressions. The workflow adds one direct official-SDK
explicit-modern control before its existing three direct `auto` attempts.

**Open gates:** Freeze and independently review the exact candidate, then push
the approved feature branch and require a green exact-source Ubuntu run.
CI01/CI02 Linux verification and eventual hands-on TUI Linux UAT remain open.
