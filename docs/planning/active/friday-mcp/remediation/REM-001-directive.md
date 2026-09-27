# REM-001 — MCP Shared Contract Completeness

**Status:** Prepared from VAL-001; separate remediator authorization pending

**Date:** 2026-09-27

**Candidate being remediated:** `e3ae808da73c2ec93f76109d41f3b70c750ede3f`

**Authority:** [VAL-001 findings](../validation/VAL-001-report.md), approved
[MCP-WS-00 directive](../directives/ws-00-contract-policy-foundation.md),
[build plan](../build-plan.md), and repository policies. This directive narrows
the existing WS-00 authority; it does not approve a later workstream.

## Objective And Allowed Files

Resolve F-001 and F-002 exactly once without changing MCP runtime behavior.
The remediator may edit only:

- `packages/friday-core/src/friday_core/mcp.py`
- `packages/friday-core/tests_core/test_mcp_contracts.py`
- `packages/friday-mcp/tests_mcp/test_framework_contract_import.py`, only if
  import compatibility tests need adjustment
- this active packet's execution/remediation notes for decisions and evidence

No existing MCP client/server implementation file, registry, runtime, Friday
Chat, memory, transcript, telemetry, CLI, public configuration, or unrelated
test may be changed. Do not alter the old standalone MCP API or its SSE code.

## F-001 — Complete The Foundational Typed Shapes

Reconcile every field in the build plan's “Required shared contracts” section,
not merely the examples named in VAL-001. Add or refine typed, content-safe
fields for:

1. `MCPClientSecurityPolicy`: trust posture and path/workspace scoping while
   preserving approved stdio-only and redaction defaults. Do not admit raw
   secrets, arguments, or results into DTOs.
2. `MCPIngestionPolicy`: future per-server/per-tool opt-in selections, disabled
   by default and requiring sanitation when enabled. Do not implement ingestion.
3. `MCPToolMetadata`: schema token estimate, schema sanitization state, and
   filtering diagnostics in addition to existing provider/name/transport data.
4. `MCPToolCallProvenance`: call identifier, output sanitization state,
   ingestion decision, and transcript/memory correlation identifiers in
   addition to the existing safe call fields. Keep raw arguments/results and
   argument hashes absent by default.
5. `MCPDiscoveryState`: per-server connection state, catalog version, cache
   timestamp, rejected/filtered tool diagnostics, and refresh eligibility.

Use precise bounded types, safe codes/identifiers, strict validation, and
serialization tests. Optional identifiers should be absent by default; do not
manufacture values or log raw exception text. Document field semantics needed
by WS-03/05/07 without implementing those consumers. Avoid circular imports
and broad mypy suppressions.

## F-002 — Make Collision Errors Actionable And Safe

When two source server/tool pairs normalize to the same canonical name, the
error must identify the canonical key and both source pairs with bounded,
sanitized representations. Do not echo arbitrary unbounded or secret-like
raw input. Add a regression test asserting both sources are distinguishable,
including punctuation-induced collisions. Keep normalization and fail-closed
behavior unchanged otherwise.

## Required Checks And Stop Conditions

- Run focused positive, negative, serialization, and import/collision tests.
- Run the approved WS-00 core/MCP/runtime package tests, Ruff, targeted mypy,
  board/dashboard, documentation lifecycle, and diff check.
- Report the known baseline integration and package-wide mypy failures
  separately; do not repair out-of-scope files under this directive.
- Stop if full contract completeness requires an unrelated package edit,
  public runtime behavior change, security-policy expansion, or a broad API
  refactor. Return that decision to the controller/maintainer.
- Commit a new stable candidate, then request a fresh independent delta review
  plus the required aggregate branch review. VAL-001 remains historical and
  cannot be upgraded in place.
