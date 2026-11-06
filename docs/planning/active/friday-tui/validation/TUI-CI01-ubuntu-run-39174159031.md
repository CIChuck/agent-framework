# TUI-CI01 third Ubuntu Actions run

**Run:** [Friday TUI Linux verification #39174159031](https://github.com/CIChuck/agent-framework/actions/runs/39174159031),
push event for `feature/friday-tui`, job `117813259520`, completed with
`failure` on 2026-10-18.

**Source and checkout:** both
`505c4c1d0c64e7c4cc73fb62a4889bf8746160ce`. Runner was GitHub-hosted
Ubuntu 24.04.5 LTS, Python 3.13.12 and uv 0.11.3. Locked selection installed
`mcp==2.3.0`, `cryptography==50.0.2`, `pytest-mock==3.15.1` and
`friday-framework-finance==0.1.0a4`.

**Results:** Checkout, uv setup, locked dependency installation, version
logging and focused neutral-loader/Chat-facade tests passed; the focused
invocation reported 21 passed. Full Runtime again reported 331 passed and
three failed, in 49.71 seconds:

1. `test_di_loads_friday_tools_provider_with_category_filter` and
   `test_kernel_start_succeeds_when_runtime_loads_declared_friday_tool`
   advanced past the finance import, then failed while importing
   `friday_tools.integrations`: `No module named 'friday_moltbook'`. The
   existing `friday-framework-moltbook` workspace package provides this
   optional integration. Runtime discovery imports all `friday_tools`
   submodules even for a selected category.
2. `test_real_public_kernel_stdio_profiles_and_child_cleanup[auto-True]`
   again failed with `ToolProviderLoadError: Required MCP server
   unavailable`; the underlying lifecycle outcome was not in the Actions
   log. This is a repeated Linux failure and cannot be treated as a
   transient pass. The test's configured three-second timeout and
   auto-profile half-budget handshake are possible factors inferred from
   source, not a proven cause.

The full Chat and unchanged `friday-cli` suites, wheel builds, wheel metadata
and installed-wheel isolation checks were skipped after Runtime failed.
This run does not establish Linux verification.

**Disposition:** `RD-TUI-CI01-06` selects the existing Moltbook package in
locked CI, includes its wheel in the later Chat-side installation and makes
the independent checks run after an earlier test failure while preserving
the failed job result. It also adds a separate diagnostic invocation of the
MCP case. A repeat MCP failure needing Runtime/MCP source or test changes
stops TUI-CI01 for a separately scoped directive.
