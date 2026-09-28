# REM-002 Implementation Report

**Date:** 2026-09-27

**Role:** Separate remediator for VAL-003 F-001 and F-002 only.

**Branch:** `feature/friday-mcp-ws01-config`

**Authorization baseline:** `84c984101046613051824748bf9f6a8f8a068518`,
including the maintainer-approved downstream test location in
[REM-002](../remediation/REM-002-directive.md).

## Corrective Changes

- F-001: The MCP direct constructor, omitted-mode `from_dict()` fallback,
  and runtime source-default template now use `selected`. Non-MCP provider
  defaults remain `all`. Regression tests cover all three omitted-mode paths,
  explicit `all` through construction/parsing/runtime overrides, and invalid
  mode rejection. Temporary runtime roots keep the source-default tests
  independent of machine-specific paths.
- F-002: The new downstream Friday Chat config test loads a canonical
  `tools.providers.mcp` stanza with the real `load_friday_py_config()` YAML
  loader, confirms that the resulting `FridayChatConfig` retains it unchanged,
  and passes that same stanza to `MCPToolProviderConfig.from_dict()`. Negative
  cases show that retention does not bypass canonical validation:
  reserved `config_file` and a zero server limit remain rejected.
- The disabled MCP example now states that omitted mode defaults to
  `selected`; explicit `mode: all` remains a supported deliberate choice.

No Friday Chat source, dependency declaration, runtime loading, selection,
alias, or turn behavior changed. Runtime tests do not import Friday Chat.
The compatibility test uses Chat's existing declared runtime dependency.

## Exact Changed Files

- `packages/friday-runtime/src/friday_runtime/config.py`
- `packages/friday-runtime/tests_runtime/test_mcp_runtime_config.py`
- `packages/friday-chat/tests_chat/test_mcp_config_compatibility.py`
- `docs/planning/active/friday-mcp/execution/WS-01-config-examples.md`
- `docs/planning/active/friday-mcp/execution/REM-002-implementation-report.md`

## Remediator Checks

Commands below use `UV_CACHE_DIR=/private/tmp/friday-uv-cache`. Test commands
also use `LITELLM_LOCAL_MODEL_COST_MAP=true` to keep import-time model-cost
loading local.

- `uv run pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime -q`:
  **262 passed**.
- `uv run pytest packages/friday-chat/tests_chat/test_mcp_config_compatibility.py packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-chat/tests_chat/test_llm_config_migration.py -q`:
  **46 passed**, including the three new compatibility cases.
- `uv run ruff check packages/friday-mcp packages/friday-runtime packages/friday-chat/tests_chat/test_mcp_config_compatibility.py`:
  **passed**.
- `uv run mypy --python-version 3.13 packages/friday-mcp packages/friday-runtime packages/friday-chat/tests_chat/test_mcp_config_compatibility.py`:
  **passed**, 38 files; no new typing suppression.
- `uv run python scripts/friday-dev-board.py validate`,
  `uv run python scripts/friday-dev-board.py render --check`,
  `uv run python scripts/check-documentation-lifecycle.py`, and
  `git diff --check`: **passed**.

Known baseline failures were reproduced separately:

- `uv run mypy packages/friday-mcp packages/friday-runtime` stops at
  `.venv/lib/python3.13/site-packages/numpy/__init__.pyi:737`, whose type
  statement needs Python 3.12 or newer while root mypy targets Python 3.10.
- `uv run pytest tests/integration/test_development_board.py -q` returns
  **10 passed, 1 failed**: its unchanged assertion expects `22 tasks`, while
  board validation reports 23. VAL-003 records the broader historical
  integration run as 23 passed and this same one baseline failure.

No live MCP server, provider call, remote endpoint, or new external effect was
used. The unrelated dirty paths listed in the execution log remain untouched
and excluded from staging.

## Review Gate And Remaining Boundary

This report is remediation evidence, not independent verification or maintainer
acceptance. The candidate SHA is provided in the handoff after commit. Fresh
review must inspect both `de8db57..new_candidate` and
`22a5643..new_candidate`; VAL-003 remains historical evidence and is superseded
for decision purposes only after that review. The board remains `started`.

Runtime MCP loading still rejects enablement. Connection/discovery,
registration, and Chat runtime/selection behavior remain later workstreams;
REM-002 does not authorize WS-02.
