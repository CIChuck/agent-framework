# TUI-CI01 fourth Ubuntu Actions run

**Run:** [Friday TUI Linux verification #39175010441](https://github.com/CIChuck/agent-framework/actions/runs/39175010441),
push event for `feature/friday-tui`, job `117815761846`, completed with
`failure` on 2026-10-18.

**Source and checkout:** both
`94f968143ee9890cf761b0e3be9004735e5a6aaf`. GitHub-hosted Ubuntu
24.04.5 LTS ran Python 3.13.12 and uv 0.11.3. Locked test selection included
`mcp==2.3.0`, `cryptography==50.0.2`, `pytest-mock==3.15.1`, and the existing
Finance and Moltbook workspace packages at `0.1.0a4`.

**Test and package results:**

| Check | Result |
| --- | --- |
| Neutral Runtime loader and Chat config facade | 21 passed |
| Full Runtime suite | 333 passed, 1 failed |
| Standalone MCP `auto`/modern stdio diagnostic | 1 failed |
| Full Chat suite | 816 passed, 5 failed, 23 skipped, 1 warning |
| Unchanged `friday-cli` suite | 155 passed |
| Local wheel build and hashes | 13 wheels built; SHA-256 hashes logged in the Actions run |
| Runtime wheel metadata | Passed: direct Pydantic/PyYAML dependencies and no Chat/CLI dependency |
| Installed Runtime isolation | Passed: `uv pip check` for 111 packages; imported outside checkout without Chat or CLI installed/importable |
| Installed Chat facade | Passed: `uv pip check` for 130 packages; Chat facade exports the installed Runtime model/error identities |

The Runtime failure was
`test_real_public_kernel_stdio_profiles_and_child_cleanup[auto-True]`:
`ToolProviderLoadError: Required MCP server unavailable`. It also failed as
the sole test in a separate 8.45-second diagnostic invocation. This is the
third successive Linux run with that case failing. The current log does not
show the underlying MCP lifecycle outcome. The configured three-second test
timeout and the `auto` profile's half-budget modern handshake are possible
factors inferred from source, not a confirmed root cause.

The Chat failures were:

- `test_cli.py::test_cli_help`: the help command exited successfully, but the
  rendered output did not contain the asserted literal `--version`. The CLI
  declares that option; the Linux rendering/test discrepancy needs diagnosis.
- Four `test_maintenance_commands.py` cases for `/reorganize` received the
  sanitized `MaintenancePlatformError` response instead of their expected
  command result. The production lease registry explicitly rejects platforms
  other than Darwin in `_ensure_darwin_capability()`. The Linux behavior and
  test expectations need a separately authorized compatibility decision.

The workflow ran independent suites and wheel checks despite earlier test
failures, while preserving the failing job conclusion. The dependency
selection and installed-wheel isolation checks now work on Ubuntu. The full
Linux verification gate is **not met**: neither the failed Runtime/Chat tests
nor the standalone diagnostic can be waived or skipped under TUI-CI01. The
approved CI01 directive stops when product or test edits are required. Those
edits need a separately scoped, maintainer-approved directive; no protected
package source, test, metadata, or lockfile was changed in this unit.
