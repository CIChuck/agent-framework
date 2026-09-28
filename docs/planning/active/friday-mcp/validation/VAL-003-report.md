# VAL-003 — Independent MCP-WS-01 Work-Unit Review

**Verdict:** `CHANGES_REQUESTED`

**Decision status:** Superseded for the current candidate by REM-002 commit
`dd6c65b`; retained as historical findings. Fresh VAL-004 delta and aggregate
validation is pending, so no WS-01 verification is claimed.

**Reviewer:** Fresh-context Codex validation subagent, independent of the
builder (model/version not exposed).

**Date:** 2026-09-27

**Mode:** Full, read-only work-unit review.

**Candidate:** `de8db57b565968fa02e429e16a481e00c6a92024`

**Base and diff:**
`22a5643943da06043515494e23b3dfe549052c55..de8db57b565968fa02e429e16a481e00c6a92024`

The reviewer read [VAL-003's pinned request](VAL-003-request.yaml), all ten
authority documents and their hashes, the candidate diff, source, tests, and
examples. All hashes matched. The later request-only commit `0dad7aa`
changed planning metadata, not reviewed source or tests. The reviewer made
no edits, commits, board changes, MCP calls, or provider calls. One diagnostic
import triggered LiteLLM's automatic cost-map fetch attempt; restricted DNS
prevented it, and LiteLLM used its local fallback.

## Findings

### F-001 — Medium — MCP default mode violates selected-only requirement

The [build plan](../build-plan.md) requires the default MCP provider mode to
remain `selected`, avoiding default injection of every MCP tool into turns.
The candidate retains `all` in `MCPToolProviderConfig`'s default and parser
fallback and in `RuntimeConfig._default_source_data()`'s MCP template. A
direct omitted-mode parse returned `all`. This is inherited from the base,
but WS-01 owns the canonical configuration surface and leaves a mandatory
default unmet.

**Required mitigation:** Set those three MCP-only defaults to `selected`,
preserving non-MCP provider defaults. Test direct construction, omitted-mode
parsing, and default runtime config. Update examples/report if their default
claims change. No runtime tool selection or Chat behavior belongs in this fix.

### F-002 — Medium — No Friday Chat canonical-model consumption evidence

The approved [WS-01 directive](../directives/ws-01-configuration-model-validation.md)
and [tactical plan](../tactical-plan.md) require a test proving Friday Chat
can import or consume the same canonical MCP config model without a second
shape. The candidate's new tests exercise runtime parsing only; none
references Friday Chat, and source/test search found no canonical-model
consumer there. The approved WS-01 boundary reserves actual Chat turn or
alias behavior for WS-04, but still requires config-compatibility evidence.

**Required mitigation:** Add a bounded cross-package config-only test, in an
allowed WS-01 test location, that parses one canonical MCP stanza through the
existing Friday Chat configuration surface and then through the canonical
runtime MCP model. Demonstrate no second MCP shape is needed. Do not change
Friday Chat source, aliases, tool selection, or turn processing. Report any
dependency or import boundary revealed by that test.

## Checks, Baselines, And Residual Risk

- Core/MCP/runtime tests: **257 passed**. Affected-package Ruff: passed.
  Python 3.13 mypy: passed on 37 files. Board validation, dashboard freshness,
  documentation lifecycle, and candidate diff whitespace checks: passed.
- Default-target package-wide mypy stops at the known NumPy stub syntax
  mismatch under the repository's Python 3.10 mypy target. The broader
  integration suite has **23 passed, 1 baseline failure**: its unchanged
  board test expects 22 tasks while the base already had 23. Neither is a
  WS-01 code regression.
- The reviewed config does not connect servers, register tools, or provide
  live interoperability. Runtime loading, registry integration, and Chat
  turn behavior remain later workstreams and are not verified here.
- Unrelated dirty checkout paths were not modified by the reviewer.

Candidate `de8db57` remains historical evidence, not a verified work unit.
[REM-002](../remediation/REM-002-directive.md) binds F-001 and F-002 for a
new candidate and fresh delta plus aggregate review. The wider initiative
remains `started`; neither completion nor acceptance is claimed.
