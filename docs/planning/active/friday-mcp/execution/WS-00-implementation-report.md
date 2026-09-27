# MCP-WS-00 Implementation Report

**Status:** Candidate preparation; independent validation pending

## Scope And Contract Decisions

- Framework-facing contracts live in `friday_core.mcp`, which is importable
  without `friday-mcp`. `friday-mcp` continues to own its existing protocol
  configuration, manager, transports, adapters, and server APIs. No existing
  programmatic MCP import was removed or renamed.
- Tool metadata is represented by a typed, read-only sidecar keyed by
  canonical tool name. Native `ToolDefinition` and the registry are unchanged;
  WS-03 must attach the sidecar and check native-tool collisions.
- Canonical names normalize to lowercase ASCII with underscore separators;
  the default is `mcp_<server>_<tool>`, with a normalized configurable prefix.
  Names longer than 64 characters, unusable names, and collisions fail
  explicitly. No truncation is performed.
- First-pass limits are 8 servers, 25 tools/server, 50 tools total, 8192
  schema bytes/tool, 4000 schema tokens, 65536 result bytes, 2048 reserved
  tool-result tokens, 4096 minimum memory-retrieval tokens, concurrency 4/4,
  and connection/tool timeouts of 30/60 seconds. Tests check that these
  reservations leave capacity at configured 50k, 250k, and 1m scenarios;
  actual enforcement and provider-limit reconciliation are later work.
- Integrated runtime policy is stdio-only in the first pass. Existing direct
  SSE APIs are unaffected. Raw arguments and hashes are never stored by
  default, and the first-pass policy rejects enabling either. DTOs expose no
  raw argument/result fields. Long-term ingestion is disabled by default and
  requires sanitized content if later enabled.
- New source has no broad mypy ignore. Legacy ignores in untouched MCP files
  remain outside WS-00; later workstreams must address any files they touch.

## Changed Areas

- `packages/friday-core/src/friday_core/mcp.py`: new public typed contract
  module and naming/sidecar helpers.
- `packages/friday-core/tests_core/test_mcp_contracts.py`: positive, negative,
  serialization, naming, security, and default-limit tests.
- `packages/friday-mcp/tests_mcp/test_framework_contract_import.py`: import
  smoke demonstrating existing package compatibility and no circular import.
- Active planning packet and development board: approval, branch, scope,
  execution state, and validation evidence.

## Verification

- `uv run pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime -q`: **226 passed**.
- `uv run ruff check packages/friday-core packages/friday-mcp`: **passed**.
- `uv run mypy packages/friday-core/src/friday_core/mcp.py`: **passed**.
- `uv run mypy packages/friday-core packages/friday-mcp`: **blocked by the
  current NumPy stub's Python 3.12-only type syntax under the project's 3.10
  target**. With `--python-version 3.13`, four pre-existing
  `friday_core.profiles.py` return-type errors remain.
- `uv run pytest tests/integration -q`: **23 passed, 1 baseline failure**. The
  unchanged development-board test hard-codes 22 tasks while baseline
  `20c70dd` already had 23. No integration test was altered under this
  contracts-only directive.
- Board validation and documentation lifecycle checks: **passed**.

All commands above used `UV_CACHE_DIR=/private/tmp/friday-uv-cache` in the
restricted environment. No live MCP server or external credential was used.
Passing tests are local evidence; they are not an independent verdict, whole
initiative completion, or maintainer acceptance.

## Follow-Up Before WS-01

The strict canonical `tools.providers.mcp` config, required-server handling,
unsupported-key rejection, and direct-run Chat config bridge remain WS-01.
Runtime loading remains WS-02. WS-03 must adapt the metadata sidecar and
enforce name collisions against the full native registry. Later slices must
enforce schema/result budgets, retrieval floor, redaction at persistence and
telemetry boundaries, and any future keyed argument-hash policy.
