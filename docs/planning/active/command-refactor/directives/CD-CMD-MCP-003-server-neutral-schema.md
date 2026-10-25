# MCP server-neutral schema compatibility — construction directive

**Status:** approved by Chuck Russell on 2026-10-25 in the conversation,
after reviewing this exact directive; implementation and validation pending.

**Board/branch:** `friday-command-refactor`, `feature/command-refactor`.
This is a bounded MCP follow-up on the active branch, separate from the
P0–P5 shared-command migration. The maintainer approved the behavioral
decisions in the [schema proposal](../proposals/mcp-schema-compatibility.md)
on 2026-10-25 and requested code generation after documenting them. Under
[AGENTS.md](../../../../../AGENTS.md) and the
[independent-validation policy](../../../../reference/policies/independent-validation-policy.md),
this *exact* code unit required maintainer approval before source edits.
The earlier [Draft-07 remediation](../remediation/REM-CMD-MCP-002-2025-draft7-registration.md)
deliberately prohibited keyword broadening; this directive would supersede
that prohibition only for the work described here.

## Objective and acceptance

Admit a bounded, server-neutral profile of MCP input schemas using `$defs`,
local JSON Pointer `$ref` and `propertyNames`, including productive structural
recursion. Preserve the validated source schema as the constraint authority,
check model arguments locally before an MCP call, and offer a schema to a model
only when that provider path can carry an unchanged or proven-equivalent
representation. Reject unsupported shapes with fixed safe reasons. Charge the
shared model-facing schema budget only for definitions that pass admission;
retain raw discovery, per-definition and tool-count caps. Expose one nonfatal
per-server startup count summary and later inspectable rejection reasons.

Acceptance is deterministic, fixture-based proof across Draft-07 and 2020-12
inputs, at least two independent server-shaped catalogs, runtime registration,
Friday Chat listing/export and pre-call execution. The three presently rejected
Zapier definitions are a read-only corroboration target, not a server-specific
exception or a guaranteed provider outcome. A provider that cannot faithfully
carry an accepted recursive schema must mark the tool unavailable for that
provider with a stable reason. Do not report those tools as fixed until actual
provider export and execution gates pass.

## Implementation contract

1. **Canonical and model schemas.** Keep the complete, validated input schema
   for local validation within the runtime tool owner. Sanitize descriptions
   and annotations for model presentation without dropping or weakening any
   validation keyword. Do not persist raw schemas or include peer content in
   diagnostics. Verify that plain/OpenAI exports and Chat's model request path
   preserve every admitted constraint. Annotations may be redacted; this is
   not permission to change validation semantics.
2. **Bounded reference profile.** Resolve only same-document JSON Pointers,
   including escaped pointer segments. Do not fetch remote, relative-document
   or file references. Permit recursion only through a structural instance
   step, such as an object property or array item; reject a pure alias loop.
   Apply existing raw byte/tree limits before reference analysis. Add explicit
   reference-hop, graph-work and argument size/depth/work limits; exceedance
   fails closed without a remote call. Use the source dialect for `$ref`
   sibling semantics; reject a form if faithful export is not demonstrated.
   Keep 2024/2025/2026 version and Draft-07/2020-12 boundaries unchanged.
3. **Keyword profile.** Support `$defs` as a definition container and
   `propertyNames` as an actual key constraint. Traverse referenced and
   unreferenced schema material for unsafe text and unsupported keywords.
   Preserve `definitions` or other dialect-specific forms only if explicitly
   covered by deterministic fixtures; otherwise reject them with a fixed code.
   Do not treat arbitrary extension keywords as annotations to strip.
4. **Local call validation.** Validate JSON arguments against the canonical
   schema before invoking the MCP client. On invalid input or a validation
   work limit, return a fixed, non-sensitive failure through the existing
   tool-error path; no RPC occurs. Keep server-side validation and existing
   output sanitation. The source schema and model export must remain tied to
   the same catalog generation.
5. **Provider export.** Runtime registration admits a schema independently
   of the configured model provider; Chat's model-facing selection makes an
   explicit, testable provider-compatibility decision. Preserve an unchanged schema where
   the provider accepts it. A transformation is allowed only with a bounded
   equivalence proof for the supported profile. If support or equivalence is
   unknown, do not offer that tool for that provider and record a safe code.
   Do not infer support from successful MCP discovery alone or silently drop
   `$defs`, `$ref` or `propertyNames`.
6. **Accounting and visibility.** Discovery continues to enforce raw size,
   catalog and connection limits, but it does not consume the shared
   `max_schema_tokens` cap. Registration charges only schema-admitted
   definitions' actual exported cost in encounter order; Chat's per-turn
   budget charges only provider-compatible definitions it can offer.
   Retain safe per-tool registration decisions and aggregate per-server
   discovered/registered/rejected counts. Startup output is one summary per
   server; later status exposes fixed codes for unsupported keyword,
   unsupported reference, provider export, schema budget and validation limit.
   Show only validated canonical tool identifiers when a per-tool reason needs
   an identity; otherwise show counts. Never interpolate raw peer names,
   descriptions, pointers, arguments, credentials or schema fragments into
   these messages.

## Allowed boundaries

- `packages/friday-core/src/friday_core/mcp.py` for fixed diagnostic codes and
  typed cross-package status contracts.
- `packages/friday-runtime/src/friday_runtime/mcp_registration.py` and
  `mcp_loading.py` for bounded admission, canonical/export handling, budget
  accounting and discovery/status counts.
- `packages/friday-mcp/src/friday_mcp/client/adapter.py` and at most one new
  module under `packages/friday-mcp/src/friday_mcp/client/` for the local
  validator and call boundary. Existing client/protocol source may be changed
  only by an approved amendment if a concrete test proves it necessary.
- `packages/friday-chat/src/friday_chat/tools/mcp.py`, `tools/selection.py`,
  `commands/registry.py`, `commands/tools.py`, `adapters.py` and `app.py` only
  as needed for truthful model-facing export and safe status. Do not alter
  automatic tool-turn continuity under this directive.
- Focused existing MCP tests in `packages/friday-{core,mcp,runtime,chat}/tests_*`
  and at most one new fixture module per affected package; the MCP client
  guide and this packet's execution/validation records.

No user config or models-config edits, dependency change, `friday-llm` source
edit, transport/authentication change, remote schema fetch, new MCP command,
global cap increase, live tool call, email/write action, or P0–P5 command
migration is authorized. If the actual provider boundary requires a different
package or a new dependency, stop for an amendment before editing it.

## Verification and reporting

- Record an exact keyword/dialect/export matrix and synthetic fixture corpus
  before implementation. Include local reuse, escaped pointers, productive
  recursion, `propertyNames` pass/fail, Draft-07 sibling handling, 2020-12
  siblings and safe annotation redaction.
- Negative fixtures: unknown keyword, unreferenced unsafe content, missing or
  external pointer, pure alias loop, malformed schema/arguments, size/depth/
  node/hop/work limits, provider rejection, catalog generation change, and
  invalid arguments with **zero** MCP calls.
- Integration fixtures: mixed native/MCP catalog across two server shapes;
  registered versus model-offered names; `/tools mcp`, status reasons and
  one-summary-per-server behavior; rejected schema before a valid schema must
  leave the valid tool's shared budget available. Preserve all existing raw
  caps and client/version regressions.
- Baseline already observed before this directive: 1,829 selected MCP client,
  runtime and Chat tests passed on 2026-10-25. After implementation run those
  suites, focused Ruff and mypy for changed sources, board validation,
  documentation lifecycle checks and `git diff --check`. Report exact commands
  and counts. Read-only live `initialize`/`tools/list` from already configured
  servers may corroborate shape/counts; it does not replace deterministic
  tests and must not invoke any remote tool or paid model.
- Freeze only scoped source, tests and docs in a candidate commit. Pass the
  exact authority manifest, directive, diff and test receipts to a fresh-context,
  read-only validator. Treat `VERIFIED` as validation, not maintainer acceptance.

## Stop conditions

Stop and reconcile before continuing if provider compatibility cannot be
proved without a forbidden source/dependency change, if a safe recursive
validator cannot stay bounded, if the canonical and model schemas diverge in
constraints, if validation can issue an RPC before rejecting arguments, or if
the fix needs to relax transport, credential, raw-size or protocol-version
policy. Record a partial result honestly; do not label a connected or
discovered tool as callable without all admission and export checks.
