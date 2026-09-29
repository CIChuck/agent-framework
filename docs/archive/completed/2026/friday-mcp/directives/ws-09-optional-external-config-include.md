# Construction Directive: MCP-WS-09 Optional External MCP Config Include

Status: Draft construction directive
Date: 2026-07-24
Tactical plan: [Friday Framework MCP Tactical Implementation Plan](../tactical-plan.md)
Workstream: `MCP-WS-09`

## AI Builder Role

You are the implementation agent for the deferred optional external MCP config include phase. Your job is to allow users to reference an external MCP config file while preserving `tools.providers.mcp` as the single canonical configuration model.

This phase must not start until inline MCP configuration is stable and tested.

## Source Authority And Precedence

1. [Repository engineering policy](../../../../../reference/policies/repository-engineering-policy.md)
2. [Friday Framework MCP tactical implementation plan](../tactical-plan.md)
3. [Friday Framework MCP enhancements build plan](../build-plan.md)
4. Completed `MCP-WS-01`
5. Current runtime and MCP config implementation

## Implementation Objective

Implement optional `tools.providers.mcp.config_file` support so an external file can be loaded, validated, normalized, and merged into the same typed MCP provider model used by inline config. The external file must not become a second authority or a bypass around validation.

## Allowed Scope

You may edit:

- `packages/friday-runtime/src/friday_runtime/config.py`
- `packages/friday-mcp/src/friday_mcp/config.py`
- `packages/friday-runtime/tests_runtime/`
- `packages/friday-mcp/tests_mcp/`
- `docs/guides/`
- Friday Chat config templates if external include support is documented for desktop installs

Do not edit MCP runtime lifecycle, registry, Friday Chat turn behavior, memory ingestion, transcript export, or telemetry unless a narrow config API adjustment is required.

## Explicit Non-Goals

- Do not create a separate MCP config authority.
- Do not let external config bypass typed validation.
- Do not support multiple competing config files unless explicitly added to the tactical plan.
- Do not implement live reload of external config.
- Do not watch files.
- Do not support remote config URLs.
- Do not allow unsafe path traversal.
- Do not implement resources, prompts, live refresh, or server exposure.

## Required Workstreams

### `MCP-09-01`: Include Semantics

Define how `tools.providers.mcp.config_file` behaves:

- whether it replaces inline `config.servers`;
- whether it merges with inline values;
- which side wins on conflicts;
- whether inline security and limits can override external values;
- whether external file can contain full provider config or only `servers`.

Document the decision in tests and guide snippets.

### `MCP-09-02`: Path Resolution And Allowed Roots

Define and implement:

- relative path resolution;
- absolute path handling;
- allowed roots;
- missing-file behavior;
- unreadable-file behavior;
- path traversal rejection;
- symlink behavior if relevant;
- user data path expectations for desktop installs.

Fail closed on unsafe paths.

### `MCP-09-03`: Parse Into Canonical Model

Parse the external file into the same typed MCP provider model used by inline config. Do not create a second schema.

YAML parsing must use existing project config utilities where practical. Avoid ad hoc string parsing.

### `MCP-09-04`: Preserve Validation, Redaction, Diagnostics, And Precedence

External config must receive the same validation as inline config:

- unknown keys;
- duplicate servers;
- invalid transports;
- missing commands;
- invalid `cwd`;
- invalid trust levels;
- invalid limits;
- unsafe env/header handling.

Diagnostics must be redacted and must identify whether the error came from inline config or external config.

### `MCP-09-05`: Examples

Add examples for:

- inline config only;
- external file with server list;
- inline security and limits with external server list;
- missing external file;
- rejected path traversal;
- desktop user config file location.

## Migration And Removal Instructions

Replace the `MCP-WS-01` behavior that rejected `config_file` with implemented include loading. Preserve the clear validation error for unsupported include shapes.

Do not remove inline config support. Inline config remains canonical.

## Security And Governance Requirements

- Fail closed on unsafe paths.
- Do not read remote URLs.
- Do not load files outside allowed roots.
- Do not log full external config content.
- Do not leak secrets from the external file.
- Redact env, headers, arguments, and secret-like values.
- Use typed parsing and explicit exceptions.
- Do not add broad mypy suppressions.

## Testing Requirements

Add tests for:

- valid relative include;
- valid absolute include under allowed root;
- missing file;
- unreadable file if practical;
- invalid YAML;
- unknown keys;
- duplicate server names;
- inline and external conflict behavior;
- path traversal;
- disallowed root;
- unsupported remote URL;
- external config normalizes into canonical typed provider model;
- inline config remains supported;
- redacted diagnostics.

Negative tests are mandatory for path traversal, disallowed roots, invalid files, unknown keys, and duplicate servers.

## Verification Commands

Run:

```bash
uv run pytest packages/friday-runtime/tests_runtime
uv run pytest packages/friday-mcp/tests_mcp
uv run pytest packages/friday-chat/tests_chat
uv run ruff check packages/friday-runtime packages/friday-mcp packages/friday-chat
uv run mypy packages/friday-runtime packages/friday-mcp packages/friday-chat
```

If docs are updated:

```bash
uv run pytest packages/friday-runtime/tests_runtime
```

Report any unavailable docs checker honestly.

## CLI, API, And UAT Requirements

CLI:

- Existing Friday Chat startup must work with inline config and external include config.
- No new command is required.

API:

- Public config API should expose the effective normalized MCP provider config.
- Diagnostics should preserve source location enough to debug include failures without leaking file contents.

UAT:

- Start with inline MCP config only.
- Start with external MCP config include.
- Start with missing external config and verify clear failure.
- Start with unsafe path traversal and verify failure.
- Verify effective config is identical after normalization for equivalent inline and external configurations.

## Documentation Close-Out

Update guides only after tests prove include behavior. Documentation must state:

- inline config is canonical;
- external includes are optional;
- allowed path rules;
- merge or replacement semantics;
- examples for desktop user config paths;
- secrets still belong in environment variables or approved local secret stores.

## Reporting Requirements

Report:

- files changed;
- include semantics;
- path resolution behavior;
- allowed-root behavior;
- conflict precedence;
- validation parity with inline config;
- docs updated;
- verification commands and results;
- skipped checks.

## Stop Conditions

Stop if:

- inline MCP config is not stable;
- include semantics are not approved;
- path allowlist policy is unclear;
- external config would bypass validation;
- implementation requires live reload, remote config URLs, multiple config authorities, resources, prompts, server exposure, or broad Friday Chat behavior changes.
