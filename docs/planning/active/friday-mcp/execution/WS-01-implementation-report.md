# MCP-WS-01 Implementation Report

**Date:** 2026-09-27

**Work unit:** strict canonical runtime MCP configuration only

**Branch:** `feature/friday-mcp-ws01-config`, based on verified WS-00 closeout
`ab49ba5`. The candidate commit is recorded in the validation request after
the scoped implementation is committed.

## Changes And Contract

- `friday_runtime.config` now owns the strict runtime-facing
  `MCPRuntimeClientConfig` and `MCPRuntimeServerConfig` models under
  `tools.providers.mcp.config`. They reuse the immutable WS-00 discovery,
  limits, security, and ingestion DTOs. `MCPToolProviderConfig` keeps the
  existing provider envelope and now holds the typed runtime client model.
- The existing `friday_mcp.config.MCPConfig` remains protocol-local and its
  direct programmatic SSE/client and server-exposure APIs are untouched. An
  unambiguous `MCPConfig` client instance and a legacy `server: null` config
  normalize into the runtime model. Server exposure and SSE do not normalize
  into the first-pass integrated runtime surface.
- Only stdio/local server declarations are accepted. Enabled servers need an
  explicit command; disabled servers may omit it; a required server cannot be
  disabled. Unknown provider/nested/server fields, `config_file`, duplicate
  canonical server IDs, invalid limits, timeouts, retries, trust levels,
  transports, tool filters, and unsafe `cwd` values fail validation. The
  reserved `config_file` error points to MCP-WS-09.
- `cwd` is checked against `runtime_paths.workspace_root` during
  `RuntimeConfig` construction. Relative paths stay under the workspace;
  absolute paths, traversal, and symlink escapes outside it fail. Error
  reporting omits raw environment values, local paths, and untrusted keys;
  server `command`, `args`, `env`, and `cwd` are omitted from model repr.
- Existing RuntimeConfig precedence remains defaults → YAML → permitted env
  overrides → explicit construction overrides. WS-01 adds no MCP-specific
  environment override, alternate config authority, or Chat alias. The
  [parsing examples](WS-01-config-examples.md) cover disabled, local stdio,
  optional/required semantics, filters, and rejected includes. The provisional
  build-plan example's older security field spelling is superseded by the
  verified WS-00 DTO fields; unsupported spellings fail closed.

## Validation Performed By Builder

- Core, MCP, and runtime tests: **257 passed**. Focused WS-01 config tests
  cover valid and negative shapes, YAML loading, round trip, workspace/symlink
  confinement, legacy compatibility, redacted errors, and non-MCP regression.
- `ruff check packages/friday-mcp packages/friday-runtime`: passed.
- `mypy --python-version 3.13 packages/friday-mcp packages/friday-runtime`:
  passed, 37 files. No new broad source suppression was added.
- The directive's default package-wide mypy command stops at a NumPy stub
  Python 3.12 `type` statement under the repository's Python 3.10 mypy target,
  before project code. The Python 3.13 rerun above checks the affected files.
- Integration tests: **23 passed, 1 baseline failure**. The unchanged
  development-board test expects 22 tasks while the WS-00 base already had
  23. This is not a WS-01 regression or within its allowed edit scope.
- No MCP server, remote endpoint, paid provider, credential, or other live
  external effect was used.

## Deferred Boundary

Runtime loading still deliberately rejects MCP enablement. WS-02 owns
connection/discovery and required/optional failure behavior; WS-03 owns tool
registration and filter enforcement; WS-04 owns Friday Chat canonical-config
bridging and turn behavior. WS-01 only parses and validates declarations.
The wider initiative remains `started`; this report is builder evidence, not
independent validation or maintainer acceptance.
