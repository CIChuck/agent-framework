# TUI-CI02 before-code Linux failure diagnosis

**Date and source:** 2026-10-18, clean `feature/friday-tui` at
`927dacc81d21a6e119a0c06bb8a2443d069157f5`. Read-only analysis; no
source, test or workflow edits.

## Confirmed observations

- [Ubuntu run 39175828523](https://github.com/CIChuck/agent-framework/actions/runs/39175828523)
  on that exact source failed the same Runtime MCP `auto`/modern stdio case
  in its full and standalone invocations. The exception names a required
  unavailable server, but does not expose `mcp_provider.lifecycle` in the
  captured log. `packages/friday-runtime/src/friday_runtime/mcp_loading.py`
  records more specific outcomes (`connection_timeout`,
  `connection_failed`, `discovery_timeout`, `discovery_failed`, or
  `cleanup_failed`), which must be observed before choosing a correction.
- The four Chat `/reorganize` failures returned the sanitized
  `MaintenancePlatformError` result. The production
  `DarwinLayoutLeaseRegistry._ensure_darwin_capability()` explicitly refuses
  platforms other than Darwin before mutation. An existing foundations test
  simulates Linux and expects this error. The command tests that failed on
  Ubuntu assume macOS behavior without accounting for the platform guard.
- The Chat CLI declares `--version` and its separate version-invocation test
  passes. On local macOS with installed Typer 0.21.0, a `CliRunner --help`
  invocation exits zero and contains literal `--version` without color.
  With either `GITHUB_ACTIONS=true` or `FORCE_COLOR=1`, the same invocation
  exits zero and visibly includes the option, but its raw output contains
  ANSI codes between the two hyphens. The raw `"--version" in output`
  assertion is false; after removing ANSI SGR codes, `--version`, `--config`
  and `--cli-config` are all present. `CLICOLOR_FORCE=1` alone did not
  reproduce the failure locally. This is a test-output comparison issue,
  not evidence that `--version` execution is broken.

## Remaining uncertainty and next test

The MCP root cause is not established. Its three-second synthetic fixture
timeout and `auto` profile's half-budget modern handshake are plausible
timing factors, but a transport or server failure could produce the same
top-level exception. The next Ubuntu diagnostic must report lifecycle
outcome, synthetic child diagnostics and direct MCP stdio interoperability
result before any timeout-only test correction. If production source work
is indicated, CI02 must stop for a separately approved framework directive.
