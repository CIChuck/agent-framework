# TUI-CI01 second Ubuntu Actions run

**Run:** [Friday TUI Linux verification #39173445329](https://github.com/CIChuck/agent-framework/actions/runs/39173445329),
push event for `feature/friday-tui`, job `117811133186`, completed with
`failure` on 2026-10-18.

**Source and checkout:** both
`7a41004aae8b375ebd01ff23fa0fb5f4e62bee1a`. Runner was GitHub-hosted
Ubuntu 24.04.5 LTS, Python 3.13.12 and uv 0.11.3. Locked selection installed
`mcp==2.3.0`, `cryptography==50.0.2` and `pytest-mock==3.15.1`.

**Results:** Checkout, uv setup, locked dependency installation, version
logging and focused neutral-loader/Chat-facade tests passed; the focused
invocation reported 21 passed. Full Runtime reported 331 passed and three
failed in 47.83 seconds:

1. `test_di_loads_friday_tools_provider_with_category_filter` and
   `test_kernel_start_succeeds_when_runtime_loads_declared_friday_tool`
   failed because importing `friday_tools` also imports `friday_finance`,
   which the selected CI environment lacked. The existing
   `friday-framework-finance` workspace package provides it.
2. `test_real_public_kernel_stdio_profiles_and_child_cleanup[auto-True]`
   failed with `ToolProviderLoadError: Required MCP server unavailable`.
   The test's `auto`/modern synthetic stdio server has a three-second
   configured timeout. The Actions output did not expose its underlying
   lifecycle outcome, so the cause is not established. The same focused test
   passed on local macOS in 1.89 seconds; that does not establish Linux
   behavior.

The full Chat and unchanged `friday-cli` suites, wheel builds, wheel metadata
and installed-wheel isolation checks were skipped after the Runtime failure.
No Linux verification claim is supported by this run.

**Disposition:** `RD-TUI-CI01-04` authorizes a workflow-only correction to
the locked finance package selection and the matching Chat-side wheel
closure. The MCP failure remains open for the next complete Ubuntu run. A
repeat requiring product or test edits stops this unit for separate scope.
