# Proposal — server-neutral MCP input-schema compatibility

**Status:** maintainer policy decisions recorded on 2026-10-25; an
[exact construction directive](../directives/CD-CMD-MCP-003-server-neutral-schema.md)
is proposed for review. No product-code authority under that directive yet.

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

### Read-only Zapier schema-shape check

On 2026-10-25, a read-only probe through the configured provider inspected
only keyword/reference shapes; it did not invoke any MCP tool or print schema
content or credentials. Each of the three rejected Zapier input schemas had
one `$defs` block, three `$ref` values that were local JSON Pointers, and two
`propertyNames` occurrences. The reachable reference graph in each schema
contains structural recursion through object/array schema keywords. It is not
an external-reference dependency or merely an unreferenced recursive
definition. This is why a first release limited to *nonrecursive* local
references would still reject all three tools. Whether Friday's model
providers can represent these recursive schemas remains unverified.

## Why the current rejection exists

The runtime publishes a sanitized schema as the model-facing tool contract.
It currently knows how to traverse and preserve the supported inline
keywords. Simply stripping `propertyNames` would weaken a constraint;
dropping `$defs`/`$ref` could remove a referenced constraint. Simply adding
their names to `_KEYWORDS` would not implement reference resolution, recursive
inspection, dialect-sensitive semantics, or provider export compatibility.
The existing fail-closed result is safer than silently changing the contract,
but its scope is too narrow for common MCP catalogs.

## Maintainer decisions

The maintainer accepted these policies in the conversation on 2026-10-25.
The local-recursion decision supersedes the earlier nonrecursive recommendation
after the Zapier schema-shape check above. These decisions settle intended
behavior, not the exact implementation or model-provider compatibility.

| Topic | Decision |
| --- | --- |
| First-release profile | Define a bounded, dialect-aware, extensible profile for every server, not a Zapier exception or an unqualified promise to support every valid JSON Schema. Inventory other rejected shapes; the first release targets `$defs`, local `$ref`, and `propertyNames`, with explicit diagnostics for still-unsupported features. |
| Model representation | Retain the validated source schema as authoritative. Offer it unchanged when a provider supports it; otherwise use only a bounded transformation proven to preserve its constraints. If faithful export is impossible, make the tool unavailable for that provider with a clear reason. Never silently drop a constraint. |
| Reference policy | Support bounded local JSON Pointer references within the same tool schema, including productive structural recursion, without infinite expansion. Reject missing targets, pure reference/alias loops, unsupported forms and external references; never fetch a schema URL. Bound validation and processing work. |
| Call validation | Validate model arguments locally against the admitted canonical schema before the MCP call. Invalid arguments cause no remote call and yield a safe validation error; the server still validates inputs. |
| Visibility | Give one nonfatal startup summary per server with discovered, registered and rejected counts, plus later inspectable per-tool rejection reasons. Use fixed, non-sensitive codes for unsupported keyword/reference/provider export/budget cases; do not display raw schemas, descriptions, credentials or arbitrary peer-supplied keyword text. |
| Budget charging | Retain raw discovery and per-definition safety limits, but charge the shared model-facing schema budget only for tools that pass schema admission. A rejected schema cannot crowd out an otherwise valid tool. |

This is a **server-neutral policy**. A provider unable to accept a faithful
representation of a recursive tool schema may still leave that tool
unavailable under the agreed preserve-or-reject rule. The three Zapier tools
must not be declared fixed until provider export, registration and execution
checks pass; local-reference support alone is insufficient proof.

## Engineering work before source edits

- Specify the exact keyword/dialect matrix and a fixture corpus from more
  than one server. Resolve how Draft-07 `definitions`, 2020-12 `$defs`, JSON
  Pointer escaping, annotations, sibling keywords and unsupported extensions
  are handled without changing schema meaning.
- Define a bounded in-memory reference graph and local argument validator.
  Distinguish productive recursion through instance structure from a pure
  alias loop; never resolve external references through the network. State
  concrete node, depth, instance-size, work and time limits and fail safely
  when a limit is reached.
- Test each supported model-provider export path against local references,
  recursive references and `propertyNames`. Use unchanged schemas where
  accepted; allow only demonstrably equivalent bounded transformations.
  Record a stable provider-compatibility reason when no faithful export exists.
- Keep sanitized canonical schemas and model exports consistent, with
  registration and per-turn accounting based on what can actually be offered.
  Decide the exact startup/status UI for the accepted diagnostic policy and
  how to avoid logging peer-controlled text. Fair allocation among *valid*
  tools from different servers remains a separate budget question.
- Review the [proposed bounded directive](../directives/CD-CMD-MCP-003-server-neutral-schema.md)
  for exact source/test paths, deterministic fixtures, expected decisions,
  security and regression gates, and stop conditions. The command-refactor
  P0–P5 plan does not supply that authority.

## Required proof for a later implementation

- Offline fixtures from at least two independent MCP schema shapes, including
  valid local reuse, productive recursive local references and
  `propertyNames` acceptance/rejection, both supported dialect paths, nested
  annotation scanning and actual model-provider export.
- Negative cases for external/missing references, pure alias loops, unknown
  keywords, malformed values, excessive work, byte/depth/node/instance/time
  limits and cross-dialect behavior. Preserve current 2024/2025/2026 version
  boundaries.
- Registration-to-Chat checks that the expected tools appear in `/tools mcp`
  and that sanitized exported schemas retain the accepted constraints.
- Pre-call checks prove invalid arguments are blocked without a remote call
  and valid arguments reach the server. A server-side validation failure still
  returns through the existing MCP error path.
- Startup and later status checks show discovered/registered/rejected counts
  and safe per-tool reasons for a different server with an unsupported schema;
  a healthy connection alone is not reported as full tool readiness.
- Budget tests show rejected schemas do not consume the shared model-facing
  cap while raw discovery caps and per-definition limits still apply.
- Per-turn budget and execution regressions remain separate from registration
  proof. A two-turn Zapier-style workflow is an integration gate only after
  the [continuity proposal](mcp-tool-turn-continuity.md) is also resolved.
- Read-only live discovery may corroborate Zapier catalog shapes and safe
  rejection codes without invoking tools; deterministic fixtures, provider
  export checks and independent review control acceptance.

No server-specific keyword bypass, token-cap increase, network reference
fetch, live write action, or product-code edit follows from these decisions.
