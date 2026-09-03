# Construction Directive: MCP-WS-08 Documentation And Guide Close-Out

Status: Draft construction directive
Date: 2026-07-24
Tactical plan: [Friday Framework MCP Tactical Implementation Plan](../tactical-plan.md)
Workstream: `MCP-WS-08`

## AI Builder Role

You are the documentation implementation agent for the Friday Framework MCP enhancement. Your job is to update end-user and contributor-facing documentation so MCP configuration, tool budgets, memory behavior, diagnostics, and troubleshooting are accurate and tied to tested implementation behavior.

## Source Authority And Precedence

1. [Repository engineering policy](../../../../reference/policies/repository-engineering-policy.md)
2. [Friday Framework MCP tactical implementation plan](../tactical-plan.md)
3. [Friday Framework MCP enhancements build plan](../build-plan.md)
4. Completed implementation from `MCP-WS-01` through `MCP-WS-07`
5. Current config templates, package READMEs, and guides

## Implementation Objective

Create accurate user-facing documentation for configuring and operating MCP client support in Friday. Documentation must distinguish current implemented behavior from deferred behavior and must not claim support for resources, prompts, live refresh, server exposure, or external config includes unless those phases are actually implemented.

## Allowed Scope

You may edit:

- `docs/guides/`
- `docs/guides/README.md`
- `docs/planning/queued/friday-mcp/build-plan.md` only to mark documentation findings or reconcile implemented behavior
- `packages/friday-mcp/README.md`
- `packages/friday-runtime/README.md`
- `packages/friday-chat/README.md`
- Friday Chat distributed config templates
- package READMEs directly affected by public MCP behavior

Do not edit source implementation unless documentation validation exposes a small typo in examples or exported names. If behavior differs from docs, stop and report the mismatch before changing implementation.

## Explicit Non-Goals

- Do not implement missing MCP behavior.
- Do not document deferred features as available.
- Do not add external MCP config include docs unless `MCP-WS-09` has been completed.
- Do not add marketing pages.
- Do not reorganize the entire docs tree.
- Do not alter package build metadata except for including documented templates if already authorized elsewhere.

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

If `MCP-WS-09` has already been implemented, document its actual semantics instead.

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
uv run pytest packages/friday-runtime/tests_runtime
uv run pytest packages/friday-chat/tests_chat
uv run pytest packages/friday-mcp/tests_mcp
```

If a docs or link checker exists, run it and report the command. If none exists, report that no docs checker was found.

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
