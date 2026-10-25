# Proposal — server-neutral MCP input-schema compatibility

**Status:** planning and diagnosis only; no construction directive or product-code authority.

**Branch/relationship:** `feature/command-refactor`. This is a separate MCP
follow-up, not a P0–P5 slash-command migration. Read with the
[tool-turn continuity proposal](mcp-tool-turn-continuity.md); admitting a tool
does not guarantee its schema is offered on a later turn.

## Problem and evidence

MCP discovery validates an incoming tool `inputSchema` using the applicable
JSON Schema dialect in `packages/friday-mcp/src/friday_mcp/client/protocol.py`.
Friday Runtime then sanitizes the tool before registration in
`packages/friday-runtime/src/friday_runtime/mcp_registration.py`. That second
step supports a fixed inline keyword set and rejects every other keyword as
`invalid_schema`. Its own module contract says references, definitions,
identifiers, conditionals, formats and extensions are not implemented. The
complete definition is bounded by bytes, depth and node count.

The [live-catalog finding](../validation/FIND-CMD-MCP-002-registration-gap.md)
identified three rejected Zapier tools: `inspect_zapier_actions`,
`execute_zapier_read_action`, and `execute_zapier_write_action`. Their schemas
use `$defs`, `$ref`, and `propertyNames` across the affected definitions.
These are standard JSON Schema capabilities, not a Zapier-specific wire format:
[`$defs` and `$ref`](https://json-schema.org/understanding-json-schema/structuring)
reuse or reference subschemas, and
[`propertyNames`](https://json-schema.org/understanding-json-schema/reference/object#property-names)
constrains object keys. The [MCP tool specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
defines `inputSchema` as JSON Schema. Other servers can expose the same
constructs and encounter the same rejection.

The earlier 2025 Draft-07 registration repair deliberately retained this
bounded keyword subset. Raising `max_schema_tokens` makes more catalog entries
eligible for registration but does not make unsupported schemas valid. The
registration gap is also distinct from the subsequent per-turn tool budget.

## Why the current rejection exists

The runtime publishes a sanitized schema as the model-facing tool contract.
It currently knows how to traverse and preserve the supported inline
keywords. Simply stripping `propertyNames` would weaken a constraint;
dropping `$defs`/`$ref` could remove a referenced constraint. Simply adding
their names to `_KEYWORDS` would not implement reference resolution, recursive
inspection, dialect-sensitive semantics, or provider export compatibility.
The existing fail-closed result is safer than silently changing the contract,
but its scope is too narrow for common MCP catalogs.

## Recommended server-neutral contract to design

1. Define a documented, dialect-aware supported profile for all servers,
   independent of server name. Inventory actual rejected keyword shapes from
   more than Zapier before fixing the exact profile. Record which of the three
   Zapier schemas use local versus external references; the current finding
   has not established those targets.
2. Preserve the meaning of admitted schemas end to end. Decide whether model
   providers can receive local `$defs`/`$ref` and `propertyNames` unchanged.
   Where they cannot, evaluate bounded local-reference expansion or another
   equivalent representation. A lossy export must not be called equivalent.
3. Resolve only explicitly supported local references. Do not automatically
   fetch external reference URIs. Bound traversal, expansion, cycles, bytes,
   result size and work. Valid recursive schemas may need a documented limit
   or explicit rejection if safe model export cannot represent them.
4. Validate annotations and every admitted nested schema, including referenced
   definitions. Keep peer text out of logs and error details. Report a safe
   reason such as `unsupported_keyword` or `unsupported_reference` to help
   distinguish compatibility from malformed JSON or exhausted budgets.
5. Check the complete path: MCP dialect validation, runtime registration,
   native/Chat model export, per-turn budget calculation, and tool execution.
   Decide whether Friday should validate call arguments against the admitted
   schema before forwarding; the current MCP wrapper forwards arguments to
   the client, while server-side validation remains the server's duty.

This is a **server-neutral policy**, not a promise that every possible JSON
Schema keyword or provider-specific tool format will be supported. Unsupported
features should remain explicit and explainable.

## Decisions needed before a construction directive

| Decision | Review question |
| --- | --- |
| Supported profile | Is the first unit local `$defs`/`$ref` plus `propertyNames`, or a broader JSON Schema profile backed by a keyword inventory? |
| Representation | Can each supported model provider accept the original schema, or must Friday transform it while preserving meaning? |
| Reference policy | Which local pointer and recursion forms are supported, and what bounded failure applies to external, missing or cyclic references? |
| Call validation | Must Friday enforce admitted constraints before an MCP call, in addition to server enforcement? |
| Diagnostics | Which stable, non-sensitive rejection codes and counts should `/tools mcp` or `/tool-budget` expose? |
| Budget order | Should a definition that fails registration consume the shared discovery-preparation budget? This is a separate issue exposed by the earlier finding. |

## Required proof for a later implementation

- Offline fixtures from at least two independent MCP schema shapes, including
  valid local reuse and `propertyNames` acceptance/rejection, both supported
  dialect paths, nested annotation scanning and actual model export.
- Negative cases for external/missing/cyclic references, unknown keywords,
  malformed values, excessive expansion, byte/depth/node limits, and
  cross-dialect behavior. Preserve current 2024/2025/2026 version boundaries.
- Registration-to-Chat checks that the expected tools appear in `/tools mcp`
  and that sanitized exported schemas retain the accepted constraints.
- Per-turn budget and execution regressions remain separate from registration
  proof. A two-turn Zapier-style workflow is an integration gate only after
  the [continuity proposal](mcp-tool-turn-continuity.md) is also resolved.
- Read-only live discovery may corroborate catalog counts and safe rejection
  codes; deterministic fixtures and independent review control acceptance.

No server-specific keyword bypass, token-cap increase, network reference
fetch, live write action, or product-code edit follows from this proposal.
