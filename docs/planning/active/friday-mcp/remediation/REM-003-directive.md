# REM-003 — MCP-WS-02 Retained Ownership Across Startup Retry

Status: Draft; awaiting maintainer authorization of separate remediator
Date: 2026-09-27
Initiative: `friday-mcp`
Work unit: `MCP-WS-02`
Finding: [VAL-005 F-001](../validation/VAL-005-report.md#f-001--high-startup-retry-discards-ownership-after-cleanup-failure)
Failed candidate: `5a2856dea0f57208906fbd6eae5419d716bbf55a`

## Authority And Role

Repository engineering and independent-validation policies, the approved
[WS-02 directive](../directives/ws-02-runtime-lifecycle-provider-loading.md),
and the complete [VAL-005 report](../validation/VAL-005-report.md) control this
bounded correction. This draft does not itself authorize product changes or
delegation. A separate remediator is required because the finding concerns
lifecycle ownership and resource integrity; the original builder must not
silently repair the failed candidate.

After maintainer authorization, implement only the numbered finding below,
commit a stable correction, then obtain fresh independent delta and complete
WS-02 aggregate review. Initiative remains `started`; no acceptance, delivery,
external-service effect, or WS-03 authority is supplied by this directive.

## F-001 — High: Preserve Retained Owners Across Startup Retry

Discovery followed by cleanup failure correctly leaves the client manager
owning a transport, but provider retry overwrites `manager`; DI retry similarly
overwrites `mcp_provider`. The next public `kernel.stop()` cannot reach the
first retained client. VAL-005 reproduces both layers and explicitly cleans its
probe resources.

Required correction:

- Preserve the existing provider and manager while they retain any resource
  whose cleanup has not completed. Retrying startup may reuse that owner or
  fail closed pending successful cleanup; it must not discard it.
- Do not infer that a false started/booted/connected flag means resource
  ownership has ended. Public shutdown must still reach every retained client.
- Once cleanup succeeds, allow a subsequent successful start using the existing
  approved lifecycle, with safe diagnostics and no stale executable handoff.
- Preserve explicit cleanup failures, diagnostic visibility, successful peer
  draining, bounded cancellation, and successful-start/shutdown idempotence.
- Update the implementation report's retry/cleanup claims and record precise
  regression evidence. No config schema or startup API change is needed.

## Allowed Files

Product correction is limited to:

- `packages/friday-runtime/src/friday_runtime/mcp_loading.py`
- `packages/friday-runtime/src/friday_runtime/di.py`
- `packages/friday-runtime/tests_runtime/test_mcp_loading.py`

The remediator may add
`docs/planning/active/friday-mcp/execution/REM-003-implementation-report.md` and
make a bounded correction/status note in
`docs/planning/active/friday-mcp/execution/WS-02-implementation-report.md`.
Controller owns review requests, board, packet index, and execution log. Do not
edit the historical VAL-005 report, authority documents, kernel source, MCP
source, configuration models, package metadata, or unrelated tests.

## Regression And Acceptance Criteria

- `REM-003-AC-01`: Provider discovery+cleanup failure followed by startup retry
  preserves the original manager or fails without replacing it.
- `REM-003-AC-02`: Public kernel startup failure followed by retry preserves
  the original provider or fails without replacing it.
- `REM-003-AC-03`: Once cleanup is permitted to succeed, public shutdown releases
  all retained clients without callers keeping saved/private owner references.
- `REM-003-AC-04`: A successful peer plus a cleanup-failing peer demonstrates
  draining, retained ownership, inspectable safe diagnostics, and eventual
  public cleanup; failed tools never enter the registry.
- `REM-003-AC-05`: Successful cleanup followed by startup succeeds, and existing
  idempotence, cancellation, optional/required failure, caps, native registry,
  workspace confinement, and redaction coverage still passes.
- `REM-003-AC-06`: Scope and public APIs remain bounded, typing remains meaningful,
  no new broad suppression is introduced, and documentation describes the
  corrected failure/retry behavior accurately.

Use deterministic in-process clients with injected cleanup failure. Test
fixtures must explicitly release any synthetic resource even on assertion
failure. Existing authorized local fake-stdio regressions must be rerun; no
real MCP/provider endpoint, credential, paid call, or external effect is allowed.

## Required Checks

Use `UV_CACHE_DIR=/private/tmp/friday-uv-cache`; Python tests also use
`LITELLM_LOCAL_MODEL_COST_MAP=true`.

```text
uv run pytest packages/friday-runtime/tests_runtime/test_mcp_loading.py -q
uv run pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime tests/integration/test_mcp_runtime_lifecycle.py -q
uv run pytest packages/friday-chat/tests_chat/test_mcp_config_compatibility.py packages/friday-chat/tests_chat/compat/test_config_compatibility.py packages/friday-chat/tests_chat/test_llm_config_migration.py -q
uv run ruff check packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py
uv run mypy --python-version 3.13 packages/friday-runtime packages/friday-mcp tests/integration/test_mcp_runtime_lifecycle.py tests/integration/mcp_fake_server.py
uv run python scripts/friday-dev-board.py validate
uv run python scripts/friday-dev-board.py render --check
uv run python scripts/check-documentation-lifecycle.py
git diff --check
```

Keep the declared NumPy/default-target mypy and integration board-count baseline
failures separate from correction regressions; do not fix unrelated baseline
code. Fresh validation must recheck both baselines and independently rerun the
provider and public-kernel failure/retry cases.

## Non-Goals And Stops

No registry insertion, final filters, schema sanitization, Chat turn behavior,
execution provenance, memory/transcript storage, telemetry emitters, CLI,
resources/prompts, remote transport, server exposure, refresh, or external
includes. No opportunistic refactor, workspace cleanup, delivery, or unchanged
baseline repair.

Stop before editing if authority has not been granted, the candidate/authority
is unstable, or the fix requires additional source/test files, a changed
public startup API, private cross-package state access, a global manager, or
expansion beyond F-001. Report the exact scope decision needed.
