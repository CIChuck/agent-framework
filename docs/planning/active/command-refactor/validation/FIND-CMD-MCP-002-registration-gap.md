# FIND-CMD-MCP-002 — live MCP catalog narrows to one registered tool

**Date:** 2026-10-25

**Status:** open finding on the previously verified MCP compatibility candidate;
the command-refactor initiative remains started. The historical
[VAL-CMD-MCP-001](VAL-CMD-MCP-001-report.md) review is retained as the result
for its frozen candidate, but its checks did not prove that a live Draft-07
catalog reached Friday Chat's registered tool list.

## Reproduction

- The current Chat YAML enables `openaidocs` with streamable HTTP,
  `2025-11-25`, and `auth: none`. Using credentials from the ignored
  `scripts/source-friday-chat-example-env.sh`, a read-only run through the
  configured `RuntimeMCPProvider` connected to both servers and discovered
  five OpenAI Docs tools plus 17 Zapier tools. No remote tool was invoked.
- With the YAML's default `max_schema_tokens: 4000`, discovery preparation
  admitted all five Docs definitions (3,238 encoded bytes) and one Zapier
  definition, `send_feedback`. It skipped the other 16 Zapier definitions with
  `schema_limit`. This is a shared, order-dependent pre-registration budget:
  Docs appears first in the configured server list, and even its subsequently
  rejected definitions consume the preparation budget.
- Runtime registration then rejected all five Docs definitions as
  `invalid_schema` and published only `mcp_zapier_send_feedback`, exactly
  reproducing the user's `/tools mcp` output.
- The accepted client protocol handles those schemas, but
  `packages/friday-runtime/src/friday_runtime/mcp_registration.py` still
  permits only the 2020-12 URI at the root of an input schema. Each of the five
  public OpenAI Docs tools declares the exact Draft-07 URI.
- An in-memory probe removed only those five root `$schema` declarations
  before the existing registration step; all five Docs tools then registered
  under the current selection and budget limits. No source/config file was
  changed by the probe.
- `/tools mcp` lists registered tools, so per-turn context rotation cannot
  explain the OpenAI Docs absence.

The current YAML selects the MCP category and does not exclude tools. In a
Zapier-only probe at the default budget, Friday prepared and registered four
Zapier tools, confirming the combined-server budget effect. A separate
in-memory probe raised `max_schema_tokens` to 40,000 without changing the
file: all 22 catalog definitions were prepared; 14 Zapier tools registered,
five Docs definitions still failed the Draft-07 check, and three Zapier tools
failed the existing bounded schema subset because they use `$defs`, `$ref`,
and `propertyNames`. The 22 raw definitions totaled 32,890 encoded bytes.
When the probe also stripped only the Docs root Draft-07 declarations in
memory, 19 tools registered and those same three Zapier tools remained
rejected. These probes demonstrate effects, not a recommended permanent
budget value or approval to admit new schema keywords.

The three Zapier rejections are `inspect_zapier_actions`,
`execute_zapier_read_action`, and `execute_zapier_write_action`. Supporting
references or `propertyNames` changes a security-sensitive schema boundary;
it needs its own review and directive if those capabilities are needed.

## Remediation boundary

The [proposed registration directive](../remediation/REM-CMD-MCP-002-2025-draft7-registration.md)
limits a fix to the 2025 runtime registration path and adds a full Chat
publication regression. It requires maintainer approval because the original
[CD-CMD-MCP-001](../directives/CD-CMD-MCP-001-compatibility-exception.md)
does not authorize edits to `mcp_registration.py`. Restoring the Docs tools
under the current 4,000 cap would yield six registered tools: five Docs and
one Zapier. A separate decision is needed on how many Zapier tools should be
registered and how to budget their definitions without starving another
server. Keep the unsupported Zapier schema constructs outside the Draft-07
remediation.
