# MCP client compatibility exception — construction directive

**Historical source-work directive:** This directive and its recorded approvals
describe work on the imported source branch. They do not authorize construction
in the current TUI checkout. See [reconciliation provenance](../reconciliation/README.md);
the original bytes are preserved in its source snapshot.

**Status:** approved by Chuck Russell on 2026-10-25 in the conversation,
after reviewing this exact directive; implementation and validation pending.

**Branch and board task:** `feature/command-refactor`; `friday-command-refactor`.
This is the maintainer-requested, bounded MCP compatibility exception on the
current branch. It is independent of P0–P5 shared-command construction and does
not change the command inventory, command contract or TUI handoff criteria.
The [command-refactor authority record](../authority.json) still requires an
approved exact construction directive before product source edits.

## Objective and observed failures

1. The anonymous OpenAI Docs streamable HTTP MCP server negotiates
   `2025-11-25` and publishes five tools whose input schemas declare
   `http://json-schema.org/draft-07/schema#`. Friday currently rejects that
   declared dialect during `tools/list` discovery. Accept that **exact**
   Draft-07 identifier for 2025-compatible input schemas and validate those
   schemas with the matching `Draft7Validator`. Retain the current 2020-12
   validation for its declared dialect, the 2026 modern profile, and output
   schemas. Unknown dialects remain unsupported in the 2025 and 2026 paths;
   the existing 2024 behavior remains unchanged.
2. Friday's HTTP endpoint parser rejects every `?` and its URL normalization
   would discard a query even if the rejection were removed. Accept ordinary
   ASCII query strings, including a bare form such as
   `https://developers.openai.com/mcp?xyz`, and preserve the query in every
   request to the selected endpoint. Keep the existing 4096-character URL
   limit and all host, scheme, port, TLS, address, fragment, userinfo and
   backslash restrictions.

The [MCP authorization specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization#access-token-usage)
requires OAuth access tokens in the `Authorization` header and forbids them in
the URI query string. The query change is for non-secret routing parameters;
`bearer_env` remains the credential mechanism. Do not add query-token
interpolation, token logging or a new authentication mode. Because a generic
query parser cannot reliably determine whether a value is secret, document
that URLs containing credentials are unsupported and keep secret handling out
of query strings. Do not claim that the parser can enforce this semantic rule.

## Allowed implementation boundary

- `packages/friday-mcp/src/friday_mcp/client/protocol.py`: 2025 input-schema
  dialect selection and matching validation only.
- `packages/friday-mcp/src/friday_mcp/client/http_policy.py`: endpoint query
  acceptance and normalization only.
- Focused tests in `packages/friday-mcp/tests_mcp/client/` and
  `packages/friday-runtime/tests_runtime/`; an existing Friday Chat MCP
  integration test may be adjusted only if needed to prove discovery through
  the application boundary.
- `docs/guides/17-mcp-client.md`: supported URL syntax, credential guidance and
  2025 Draft-07 compatibility.

Do not change MCP server behavior, connection retries, protocol negotiation,
tool invocation or ingestion policy, command architecture, the user's modified
`packages/friday-chat/config.example.yaml` or
`packages/friday-chat/models-config.example.yaml`, or package dependencies.
Keep wire failures free of peer data and credentials.

## Required verification

- Positive: a 2025 `tools/list` response with the exact Draft-07 input-schema
  URI passes discovery and its schema is checked under Draft-07; supported
  2020-12 and schema-omitted cases continue to pass.
- Negative: unknown dialects, malformed Draft-07 schemas and Draft-07 input
  schemas in the 2026-only path remain rejected. Output-schema restrictions
  remain unchanged.
- Positive: URL parsing and runtime configuration preserve `?xyz` and a
  non-secret key/value query. A disposable local HTTP fixture must observe the
  same query on initialization, discovery and session cleanup requests.
- Negative: fragments, userinfo, backslashes, malformed/oversized URLs,
  private addresses without an explicit opt-in and disallowed ports remain
  rejected. A test must confirm no query appears in a fixed failure message.
- Run focused MCP protocol/HTTP and runtime-config suites, then the applicable
  Friday Chat MCP integration suite. Run Ruff and focused mypy for changed
  packages. Record exact commands, counts, failures and environmental limits.
- As an optional, read-only live smoke check, initialize and list tools from
  `https://developers.openai.com/mcp` with `2025-11-25`; a live outage is
  reported separately from the deterministic regression gate. Do not call
  remote tools or use credentials during this check.

Freeze a candidate commit that contains only this bounded exception and hand
its exact diff, directive and test receipts to a fresh-context, read-only
validator. The validator reports `VERIFIED`, `CHANGES_REQUESTED` or `BLOCKED`;
maintainer acceptance remains separate.

## Stop conditions and open gate

Stop if the required fix expands beyond the allowed paths or changes other MCP
profiles, authentication, connection policy, tool results or public command
behavior. Reconcile the directive before continuing. Product source edits begin
under this exact approved directive and its one-branch exception under the
repository's development lifecycle.
