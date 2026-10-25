# Proposed remediation directive — 2025 Draft-07 tool registration

**Status:** proposed for exact-scope maintainer approval; no product source
edits under this directive yet.

**Board/branch:** `friday-command-refactor` on `feature/command-refactor`;
bounded follow-up to [CD-CMD-MCP-001](../directives/CD-CMD-MCP-001-compatibility-exception.md)
and [FIND-CMD-MCP-002](../validation/FIND-CMD-MCP-002-registration-gap.md).
This is separate from shared-command P0–P5 implementation.

## Objective and acceptance

Friday's 2025 MCP client can discover exact Draft-07 input schemas, but the
runtime registration sanitizer still rejects their root `$schema` URI. Admit
the exact `http://json-schema.org/draft-07/schema#` declaration only for a
server configured with `protocol_version: '2025-11-25'`. Apply the existing
bounded inline-schema subset and semantic/annotation scanning, then strip the
dialect annotation from the published canonical schema as the 2020-12 path
already does. Do not broaden accepted keywords, remote references, embedded
content, schema size/token limits, tool-name policy or result handling.

The accepted result is that the five-tool OpenAI Docs catalog publishes five
registered `mcp_openaidocs_*` tools with the current Chat YAML and defaults.
Under the current 4,000 shared schema cap, this leaves only one Zapier tool
registered. This directive does not change that cap or support Zapier's
`$defs`, `$ref`, and `propertyNames` constructs.
The 2024 and 2026 registration paths must retain their current Draft-07
rejection, and unknown/malformed dialects must still fail safely. This
directive does not resolve the Zapier tool count. Authenticated diagnostics in
[FIND-CMD-MCP-002](../validation/FIND-CMD-MCP-002-registration-gap.md) show
that the shared schema budget skips 16 Zapier tools after the five Docs
definitions consume budget, and three Zapier definitions also exceed the
supported schema subset when the budget is raised in memory. Handle either
issue under a separate decision and scope.

## Allowed files and implementation

- `packages/friday-runtime/src/friday_runtime/mcp_registration.py`: pass a
  2025-only dialect permission from the typed server configuration into
  `sanitize_definition`/root `_schema`; keep the default strict behavior for
  other callers. Do not log or retain raw peer definitions.
- `packages/friday-runtime/tests_runtime/test_mcp_registration.py` and the
  existing HTTP integration tests: prove exact 2025 admission, 2024/2026 and
  unknown-dialect rejection, unchanged subset/security/budget behavior, and
  the five-tool catalog path.
- `packages/friday-chat/tests_chat/test_mcp_http_integration.py`: add an
  application-level check that a 2025 Draft-07 tool appears in the registered
  Chat tool list and `/tools mcp`, not merely in `tools/list` discovery.
- `docs/guides/17-mcp-client.md` and this packet's execution/validation
  receipts: correct the documented publication boundary and record evidence.

Do not edit the user's modified Chat config or models config, alter the MCP
server, change authentication/query policy, increase caps, add commands, call
remote tools, or change command-refactor scope.

## Verification and stop conditions

Run focused registration, MCP client, runtime HTTP, and Friday Chat MCP
integration suites; focused Ruff and mypy; board and documentation checks.
Repeat a read-only live OpenAI Docs initialize/list/registration smoke test
without credentials or tool calls, but keep live service availability separate
from deterministic acceptance. Freeze a scoped candidate commit and obtain a
fresh-context, read-only work-unit review. Record the raw discovery count,
prepared count, decision codes and published count without peer schemas or
descriptions.

Stop and reconcile this directive if the fix requires changes outside the
listed paths, permits additional dialects/keywords, modifies credential or
network handling, or reveals a separate Zapier-specific rejection. The prior
VERIFIED candidate is not proof of this remediation's result.
