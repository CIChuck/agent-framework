# REM-002 — MCP-WS-01 Default And Chat Compatibility Remediation

**Status:** Authorized for a separate remediator by the repository maintainer on 2026-09-27

**Date:** 2026-09-27

**Input:** [VAL-003](../validation/VAL-003-report.md) on candidate `de8db57`.
The original candidate and review remain immutable historical evidence.

## Allowed Scope

- `packages/friday-runtime/src/friday_runtime/config.py`
- `packages/friday-runtime/tests_runtime/test_mcp_runtime_config.py`
- Small WS-01 execution/report or config-example updates needed to describe
  the corrected default or cross-package test result.

Do not edit Friday Chat source or tests, the protocol-local `friday-mcp`
implementation, WS-00 contracts, unrelated tests, or any later workstream.
If the compatibility test cannot be written without changing Chat source or
the declared dependency boundary, stop and report the smallest authority
decision needed; do not widen scope unilaterally.

## Required Corrections

### F-001 — Default MCP provider mode

Set the MCP-only direct constructor default, `from_dict()` fallback, and
runtime default-source template to `selected`, as required by the build plan.
Keep the non-MCP `ToolProviderConfig` defaults unchanged. Add tests for all
three omitted-mode paths and explicit `mode: all` acceptance (so the change
does not silently prohibit a deliberate opt-in). Update any WS-01 examples
or report claims affected by the default.

### F-002 — Friday Chat config compatibility evidence

Add a config-only test in the allowed runtime test file that proves one
canonical `tools.providers.mcp` stanza can be retained by Friday Chat's
existing config parser and validated by `MCPToolProviderConfig.from_dict()`
without an alternative MCP field schema. The test must exercise the real
Friday Chat config type and the canonical runtime model. It must not claim
Chat runtime loading or tool selection works. If importing Friday Chat in a
runtime package test reveals an undeclared dependency or cycle, stop and
report that boundary rather than adding an incidental production dependency.

## Acceptance And Verification

- Both VAL-003 findings are resolved with focused negative/regression tests.
- No non-MCP default change, no new runtime loading/Chat behavior, no new
  broad typing suppression, and no new live or external effect.
- Re-run core/MCP/runtime tests, affected Ruff, Python 3.13 mypy, board and
  documentation checks, and diff whitespace check. Report the known default
  mypy/board-integration baselines separately.
- Commit a new stable candidate. A fresh independent reviewer must inspect
  both `de8db57..new_candidate` remediation delta and
  `22a5643..new_candidate` complete WS-01 aggregate before any `VERIFIED`
  claim. `VAL-003` is superseded for decision purposes only after that review.

The maintainer explicitly authorized this bounded separate-remediator pass in
the active conversation on 2026-09-27. That authorization covers F-001 and
F-002 only; it does not broaden file scope or authorize WS-02 work. The next
gate is a committed new candidate and fresh delta plus aggregate review.
