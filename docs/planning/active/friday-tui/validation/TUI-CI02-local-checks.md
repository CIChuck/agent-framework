# TUI-CI02 local candidate checks

**Scope:** Approved `CD-TUI-CI02-linux-regression-remediation.md` on
`feature/friday-tui`. This is pre-push macOS evidence. It does not establish a
green Ubuntu run, close TUI-CI01, or satisfy final Linux terminal UAT.

The candidate changes only the approved Chat test files, the Runtime synthetic
MCP integration test, the TUI Linux workflow, and scoped packet/board evidence.
No product source, `friday-cli`, metadata, dependency lock or release path was
changed. The Linux `/reorganize` assertions were also exercised on macOS with
an injected Linux platform name, while the native macOS expectations remained
active. The synthetic MCP fixture retains its 3-second timeout; no timeout
correction is justified before the Ubuntu lifecycle diagnosis.

| Check | Result |
| --- | --- |
| Focused Chat CLI and maintenance tests | 46 passed, including plain/GitHub Actions/forced-color help and four injected-Linux maintenance cases |
| Focused Runtime auto-modern and direct MCP stdio cases | 2 passed |
| Full Runtime suite with loopback fixture access | 334 passed |
| Full Chat suite with loopback fixture access after final test edit | 845 passed, 5 skipped, 1 existing deprecation warning |
| Unchanged `friday-cli` suite | 155 passed |
| Ruff on three changed test files | Passed |
| Mypy on changed Chat test files | Passed |
| Workflow YAML, all embedded Bash/Python syntax | Passed; 14 steps |
| `uv lock --check`, board validation, dashboard check, `git diff --check` | Passed; board has 34 tasks |

The first unprivileged full Runtime and Chat attempts could not bind synthetic
HTTP/TLS fixtures to `127.0.0.1` under the local sandbox. Runtime reported 9
fixture bind failures; Chat reported 10 failures and 3 setup errors at the
same bind boundary. Repeating the exact full suites with local loopback access
produced the passing results above. These were environment restrictions, not
Ubuntu or product-behavior results. Focused Mypy across all three changed test
files reports 37 existing `no-untyped-def` errors in the Runtime integration
test file; the committed baseline copy reports the same 37 errors. No other
error category appeared. The Chat test files pass Mypy.

**Open gate:** Fresh-context read-only review of the exact committed candidate,
then the authorized push and GitHub-hosted Ubuntu run. CI02-C permits a bounded
synthetic timeout adjustment only if that run shows a fixture-budget timeout
and repeated direct MCP interoperability checks pass.

The first independent preflight found CI02-01: three declared Chat options
were missing from the help assertions. The bounded correction now asserts all
six declared options in all three color modes. The focused Chat tests were
rerun (46 passed), the full Chat suite was rerun with loopback access (845
passed, 5 skipped), and Ruff plus Mypy on the changed Chat tests passed.
The earlier Runtime, direct MCP and unchanged `friday-cli` results still apply
because the correction changed only Chat help assertions.

The second independent preflight showed that substring checks could still
pass after deleting a declared option row. The revised test now parses full
option names only from rendered help rows. A read-only six-case deletion
simulation confirmed that removing any one row removes its option from the
parsed set. Focused Chat rerun: 46 passed; full Chat rerun with loopback access:
845 passed and 5 skipped; Ruff and changed-Chat Mypy passed.
