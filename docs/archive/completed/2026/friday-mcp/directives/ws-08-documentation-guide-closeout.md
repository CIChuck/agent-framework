# Construction Directive: MCP-WS-08 Documentation And Guide Close-Out

Status: Approved for documentation-only WS-08 execution by the maintainer's
"continue with ws-08" on 2026-09-29; reconciled exact scope below
Date: 2026-09-29
Tactical plan: [Friday Framework MCP Tactical Implementation Plan](../tactical-plan.md)
Workstream: `MCP-WS-08`

## AI Builder Role

You are the documentation implementation agent for the Friday Framework MCP enhancement. Your job is to update end-user and contributor-facing documentation so MCP configuration, tool budgets, memory behavior, diagnostics, and troubleshooting are accurate and tied to tested implementation behavior.

## Source Authority And Precedence

1. Explicit maintainer direction to continue WS-08, within this documentation
   workstream and without product-code or external-effects authority.
2. [Repository engineering policy](../../../../../reference/policies/repository-engineering-policy.md),
   [development lifecycle](../../../../../reference/policies/development-task-lifecycle.md),
   and [independent validation policy](../../../../../reference/policies/independent-validation-policy.md).
3. [Friday Framework MCP build plan](../build-plan.md) and
   [tactical plan](../tactical-plan.md).
4. Independently verified and explicitly accepted WS-00 through WS-07,
   including [WS-07 closeout](../execution/WS-07-closeout.md) and
   [VAL-016](../validation/VAL-016-report.md).
5. Current source, parser tests, distributed templates, package READMEs, and guides.

## Implementation Objective

Create accurate user-facing documentation for configuring and operating MCP client support in Friday. Documentation must distinguish current implemented behavior from deferred behavior and must not claim support for resources, prompts, live refresh, server exposure, or external config includes unless those phases are actually implemented.

## Allowed Scope

The complete deliverable path manifest is:

- `docs/guides/README.md`
- `docs/guides/05-tools.md`
- `docs/guides/10-configuration.md`
- `docs/guides/11-advanced-topics.md`
- `docs/guides/13-troubleshooting.md`
- `docs/guides/17-mcp-client.md` (new)
- `packages/friday-mcp/README.md`
- `packages/friday-runtime/README.md`
- `packages/friday-chat/README.md`
- `packages/friday-chat/config.example.yaml`
- `packages/friday-chat/src/friday_chat/config_templates/config.example.yaml`

Only this directive, a readiness/implementation report, validation request,
review/evidence, closeout, packet/board state and rendered dashboard may be
added or updated as process artifacts. Do not change implementation source,
tests, other templates, package metadata, build plans or historical evidence.
If behavior differs from the intended documentation, record the mismatch and
stop for a separate product decision.

## Explicit Non-Goals

- Do not implement missing MCP behavior.
- Do not document deferred features as available.
- Do not add external MCP config include docs unless `MCP-WS-09` has been completed.
- Do not add marketing pages.
- Do not reorganize the entire docs tree.
- Do not alter package build metadata except for including documented templates if already authorized elsewhere.
- Do not add a Chat MCP health command, an external config include, remote
  integrated transport, a telemetry endpoint, live refresh or memory ingestion
  by default. The integrated runtime supports local stdio only; the lower-level
  `friday-mcp` package may expose additional protocol APIs separately.
- Do not run paid/live providers or make external network requests. Local
  synthetic stdio peers and scratch paths are permitted for verification.

## Required Workstreams

### `MCP-08-01`: User Guide MCP Setup Examples

Update `docs/guides/` with tested examples for:

- MCP disabled;
- one stdio server;
- optional server behavior;
- required server behavior;
- include filters;
- exclude filters;
- security defaults;
- environment-variable-based secrets.

Examples must match parser tests and current config templates.

### `MCP-08-02`: Canonical Config Location

Document that MCP client configuration belongs under:

```yaml
tools:
  providers:
    mcp:
```

State clearly that this is the canonical config surface for both framework runtime and Friday Chat compatibility.

### `MCP-08-03`: Reserved `config_file`

Document that `tools.providers.mcp.config_file` is reserved and rejected until the optional external include phase is implemented.

WS-09 is deferred; do not imply that the reserved key is usable.

### `MCP-08-04`: Tool Budget Behavior

Explain:

- discovered tools are not blindly inserted into every turn;
- selected tool schema tokens reduce the available memory retrieval budget;
- result-token reservation also reduces available memory retrieval budget;
- Friday preserves a minimum memory retrieval floor;
- oversized or over-budget tools may be skipped or cause a diagnostic failure.

### `MCP-08-05`: Default Memory Behavior

Document:

- transcript records may include MCP calls;
- long-term memory ingestion is disabled by default;
- explicit per-server or per-tool allowlists are required for ingestion;
- MCP-derived memories carry source, trust, freshness, and truncation labels.

### `MCP-08-06`: Secret Handling

Document:

- API keys and secrets should remain environment variables;
- config should reference environment-variable names or non-secret values according to implementation behavior;
- diagnostics and telemetry are redacted;
- raw arguments and outputs are not stored by default.

### `MCP-08-07`: Troubleshooting

Add troubleshooting entries for:

- missing tools;
- disabled server;
- optional server startup failure;
- required server startup failure;
- invalid stdio command;
- invalid `cwd`;
- name collision;
- schema cap skip;
- aggregate budget skip;
- oversized result truncation;
- missing include filter match;
- memory ingestion not occurring because default is disabled.

### `MCP-08-08`: Package README Updates

Update package READMEs where public behavior changed:

- `friday-mcp`: client configuration and supported first-pass transports;
- `friday-runtime`: runtime provider loading and diagnostics;
- `friday-chat`: chat usage, budgets, and local desktop config implications.

## Migration And Removal Instructions

Remove or correct stale documentation that conflicts with implemented MCP behavior. Do not remove unrelated docs. If older docs describe target or legacy architecture, add a short accuracy note instead of rewriting broad sections unless the stale content would mislead users.

## Security And Governance Requirements

- Do not include real secrets in examples.
- Use placeholder env var names such as `EXAMPLE_API_KEY`.
- Do not encourage committing `.env`, `.friday/`, Chroma data, transcript databases, or local runtime state.
- Do not document unsafe raw output or raw argument persistence as default.
- Do not recommend broad trust for remote MCP transports unless implemented security policy supports it.

## Testing Requirements

Documentation tests should include:

- config snippets copied into or mirrored by parser tests;
- link checks if a docs checker exists;
- manual review for install-time templates versus editable user config versus runtime state folders;
- command examples checked against actual package entry points when feasible.

If no docs checker exists, report that and rely on snippet validation through config tests.

## Verification Commands

Run documentation-adjacent validation:

```bash
UV_CACHE_DIR=/private/tmp/friday-uv-cache LITELLM_LOCAL_MODEL_COST_MAP=true uv run --no-sync pytest -q packages/friday-runtime/tests_runtime
UV_CACHE_DIR=/private/tmp/friday-uv-cache LITELLM_LOCAL_MODEL_COST_MAP=true uv run --no-sync pytest -q packages/friday-chat/tests_chat
UV_CACHE_DIR=/private/tmp/friday-uv-cache LITELLM_LOCAL_MODEL_COST_MAP=true uv run --no-sync pytest -q packages/friday-mcp/tests_mcp
```

Also parse every new YAML guide example with the current Runtime and Chat MCP
config models, including disabled, selected, optional, required, filters,
environment interpolation and rejected `config_file`. Exercise one local
synthetic stdio server and required-server failure through the accepted runtime
path. Run `scripts/check-documentation-lifecycle.py`, board validate/next/show/
render, and `git diff --check`. If another docs or link checker exists, run it;
otherwise record the available lifecycle/link evidence.

The broad Chat suite has an inherited PTY timing failure and three localhost
fixture bind PermissionErrors; report it as nonzero, not passing or waived.
Run the focused MCP/Chat config, budget and ingestion coverage separately and
distinguish any new failure from this byte-checked WS-07 baseline.

Run formatting checks for touched README and guide Markdown only if a project command exists. Do not invent a new formatter.

## CLI, API, And UAT Requirements

CLI:

- Document only implemented CLI behavior.
- If an MCP health command exists, include exact command syntax and redacted example output.

API:

- Document stable public config and diagnostic APIs only.

UAT:

- Follow the guide with MCP disabled.
- Follow the guide with one fake or safe stdio MCP server.
- Verify required-server failure instructions match actual error behavior.
- Verify memory ingestion docs match actual default behavior.

## Documentation Close-Out

This phase is documentation close-out. Before finishing:

- ensure `docs/guides/README.md` references the MCP guide if appropriate;
- ensure examples mention `tools.providers.mcp`;
- ensure deferred items are labeled deferred;
- ensure config templates and guide snippets match;
- ensure package READMEs do not contradict the guide.

## Reporting Requirements

Report:

- files changed;
- guide sections added;
- package README updates;
- config snippets validated;
- deferred features explicitly labeled;
- docs checker or substitute validation used;
- verification commands and results;
- skipped checks.

## Stop Conditions

Stop if:

- implementation behavior from earlier phases is not available to document;
- examples cannot be validated against config tests;
- docs would need to claim unimplemented behavior;
- existing docs directly contradict implementation and require product direction;
- documenting external config includes would be necessary before `MCP-WS-09` is complete.
