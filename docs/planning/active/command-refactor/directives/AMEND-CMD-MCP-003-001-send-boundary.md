# Amendment 001 — bind MCP calls at transport dispatch

**Historical source-work directive:** This directive and its recorded approvals
describe work on the imported source branch. They do not authorize construction
in the current TUI checkout. See [reconciliation provenance](../reconciliation/README.md);
the original bytes are preserved in its source snapshot.

**Status:** approved by Chuck Russell in the conversation on 2026-10-25;
implementation and validation pending.

**Amends:** [CD-CMD-MCP-003](CD-CMD-MCP-003-server-neutral-schema.md).
The approved directive permits existing MCP client source changes only through
an approved amendment after a concrete test demonstrates the need. This is
that narrow amendment; the original directive otherwise remains controlling.

## Evidence and required behavior

The fresh-context review of candidate
`c0d5518aa132b5e416d9806e65132476f34840ea` found that
`call_tool_at_generation` checks the current catalog before calling the
request path, but the request path schedules an exchange task that can yield
before transport dispatch. In a local synthetic test, invalidating the catalog
between these points still let the stale call dispatch one RPC. Registration
now binds the discovered generation correctly; the remaining gap is at call
dispatch. A catalog refresh that invalidates a registered wrapper **before
transport dispatch** must prevent that wrapper's RPC and return the existing
fixed `catalog_unavailable` failure. An already dispatched call retains its
existing single-settlement behavior.

## Additional allowed source boundary

- `packages/friday-mcp/src/friday_mcp/client/base.py`: add one private guard
  for generation-bound `tools/call` requests. Read the current catalog through
  the existing owner contract and compare it with the call's context-local
  generation immediately before the stdio request calls `transport.send`.
  Raw calls without a generation remain unchanged.
- `packages/friday-mcp/src/friday_mcp/client/http.py`: apply the same guard in
  the HTTP exchange task immediately before handing a `tools/call` request to
  the HTTP pool. Preserve the existing session recovery, header-binding and
  timeout behavior.
- Focused existing tests under `packages/friday-mcp/tests_mcp/client/` and
  `packages/friday-runtime/tests_runtime/`; at most one new test module if an
  existing fixture cannot express both transport races.
- `docs/guides/17-mcp-client.md` and this packet's execution and validation
  records for the verified generation guarantee and review receipts.

No change to transport implementations, HTTP policy, protocol negotiation,
authentication, tool results, automatic tool-turn continuity, client public
APIs, dependencies, user configuration or the P0–P5 command migration is
authorized. If a guard at these two dispatch seams cannot close the reproduced
race, stop and return the new source boundary to the maintainer before editing
it. Do not convert a possible in-flight request into a replay or duplicate call.

## Required regression and closeout

Use deterministic local fakes to pause the stdio and HTTP request paths after
their first catalog check but before their respective transport-dispatch seams.
Invalidate the catalog, release each path, and assert the fixed
`catalog_unavailable` error and **zero** dispatched MCP tool requests. Confirm
that a call dispatched before invalidation still settles once against its
captured output schema and HTTP header bindings, and that generation-free raw
calls and 2025 recovery behavior remain unchanged. Retain the registration
refresh-before/after test and the invalid-argument zero-RPC tests.

Rerun the approved directive's MCP client, runtime and Chat regression
selection, focused Ruff lint/format and mypy, board validation, documentation
lifecycle and `git diff --check`. Record exact commands and counts, freeze only
approved files in a new candidate, and obtain a fresh-context, read-only
aggregate review. `VERIFIED` would be work-unit validation only; maintainer
acceptance and the command refactor's later phases remain separate.
