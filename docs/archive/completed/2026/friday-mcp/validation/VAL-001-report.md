# VAL-001 — Independent MCP-WS-00 Review

**Verdict:** `CHANGES_REQUESTED`

**Reviewer:** Fresh-context Codex validation subagent (model/version not exposed)

**Date:** 2026-09-27

**Mode:** Full, read-only work-unit review

**Candidate:** `e3ae808da73c2ec93f76109d41f3b70c750ede3f`

**Base and diff:**
`20c70dd70622e5f1b80029076a789fb58c748fb5..e3ae808da73c2ec93f76109d41f3b70c750ede3f`

The reviewer read the [request](VAL-001-request.yaml), `AGENTS.md`, the
repository engineering, lifecycle, and independent-validation policies, the
approved [WS-00 directive](../directives/ws-00-contract-policy-foundation.md),
the build/tactical plans, the rebaseline, and the candidate diff. All eight
authority hashes in the request matched. The reviewed source and tests were
unchanged by the later request-only commit `b80770b`.

## Findings

### F-001 — Medium — Incomplete shared contract shapes

The [build plan](../build-plan.md) identifies required cross-package fields
for MCP tool metadata, call provenance, and discovery state. The candidate's
`friday_core.mcp` DTOs omit schema token estimate, sanitization status, and
filtering diagnostics from tool metadata; call ID, output-sanitization and
transcript/memory correlation from provenance; and catalog/cache/rejection
state from discovery. Inspection of the DTO `model_fields` confirmed those
omissions. Security/workspace scoping and future ingestion opt-in settings in
the same required-contract section should also be reconciled while fixing the
contract shape.

This violates the WS-00 requirement to establish the *typed shapes* before
later consumers. It does not require WS-03/05/07 behavior now. Risk: those
workstreams would need to extend a supposedly stable cross-package boundary
or pass incidental untyped data.

**Required mitigation:** Add narrowly typed, content-safe fields and their
validation/serialization tests for all required shared-contract data. Keep
runtime, registry, Chat, transcript, memory, and telemetry wiring deferred.

### F-002 — Medium — Collision diagnostic lacks both source identities

The [directive](../directives/ws-00-contract-policy-foundation.md) requires
fail-closed naming collisions with diagnostic detail. The candidate's
`normalize_mcp_tool_names()` raises on a collision but reports only the
canonical name. For `("file-system", "read.file")` and
`("file_system", "read_file")`, it should identify both bounded, safely
rendered source pairs as well as the canonical collision key.

**Required mitigation:** Add safe collision detail and a regression test.
WS-03 still owns registry-time collision enforcement, including native tools.

## Evidence And Boundary

- MCP-00-01, -04, -06, -07, and -08 met the scoped criteria. MCP-00-02,
  -03, and -05 are incomplete because of F-001/F-002.
- No prohibited runtime, Friday Chat, memory, transcript, telemetry, registry,
  or CLI behavior changed in the candidate.
- Deterministic checks passed: 226 core/MCP/runtime tests, Ruff, focused mypy,
  board validation, dashboard freshness, documentation lifecycle, and diff
  whitespace check.
- The package-wide mypy command hits a NumPy stub syntax error under the
  repository's Python 3.10 mypy target; a Python 3.13 rerun reaches four
  pre-existing errors in untouched `friday_core.profiles.py`.
- The development-board integration test expects 22 tasks, but the baseline
  board already had 23. That is a pre-existing failure, not a WS-00 regression.
- No live MCP interoperability, external provider, or remote SSE check was
  authorized or performed. Unrelated dirty checkout paths were untouched.

The candidate remains `started` and is not `VERIFIED`, `completed`, or
accepted. [REM-001](../remediation/REM-001-directive.md) binds the two findings
for a new candidate and fresh review.
