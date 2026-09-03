# Construction Directive: MCP-WS-01 Configuration Model And Validation

Status: Draft construction directive
Date: 2026-07-24
Tactical plan: [Friday Framework MCP Tactical Implementation Plan](../tactical-plan.md)
Workstream: `MCP-WS-01`

## AI Builder Role

You are the implementation agent for the Friday Framework MCP configuration phase. Your job is to make `tools.providers.mcp` a strict, typed, canonical configuration surface without connecting to MCP servers or registering tools.

## Source Authority And Precedence

1. [Repository engineering policy](../../../../reference/policies/repository-engineering-policy.md)
2. [Friday Framework MCP tactical implementation plan](../tactical-plan.md)
3. [Friday Framework MCP enhancements build plan](../build-plan.md)
4. Completed `MCP-WS-00` contract implementation
5. Current runtime and MCP config source

## Implementation Objective

Extend MCP and runtime config parsing so Friday can validate and normalize canonical MCP provider configuration under `tools.providers.mcp`. The output of this phase must be a typed model that later runtime, chat, memory, telemetry, and docs phases can consume.

## Allowed Scope

You may edit:

- `packages/friday-mcp/src/friday_mcp/config.py`
- `packages/friday-runtime/src/friday_runtime/config.py`
- `packages/friday-mcp/tests_mcp/`
- `packages/friday-runtime/tests_runtime/`
- package exports needed for config models
- config templates only if they are already part of the current editable install template work

Do not edit runtime lifecycle, tool loading, Friday Chat turn processing, transcript, memory, or telemetry unless a compile/import adjustment is strictly required by config type changes.

## Explicit Non-Goals

- Do not connect to MCP servers.
- Do not discover MCP tools.
- Do not register MCP tools.
- Do not implement async runtime provider loading.
- Do not implement external `config_file` loading.
- Do not implement Friday Chat tool budget behavior.
- Do not implement memory ingestion.
- Do not add CLI health commands.
- Do not silently accept unknown config keys.

## Required Workstreams

### `MCP-01-01`: Extend Provider Config Shape

Implement the canonical MCP provider model with:

- `enabled`;
- `mode`;
- `include_tools`;
- `exclude_tools`;
- `config.auto_connect`;
- `tool_name_prefix`;
- `discovery`;
- `limits`;
- `security`;
- `ingestion`;
- `servers`.

Use the DTOs and defaults from `MCP-WS-00`. If `MCP-WS-00` has not been completed, stop.

### `MCP-01-02`: Extend Server Config Shape

Support server fields:

- `name`;
- `enabled`;
- `required`;
- `transport`;
- `command`;
- `args`;
- `env`;
- `cwd`;
- `timeout_seconds`;
- `tool_timeout_seconds`;
- `retry_attempts`;
- `trust_level`.

Validate transport-specific requirements. For stdio, require an explicit command unless the server is disabled. For remote transports, apply the trust posture decided in `MCP-WS-00`.

### `MCP-01-03`: Reject `config_file`

If `tools.providers.mcp.config_file` appears, fail validation with an actionable message that says external MCP config includes are reserved for `MCP-WS-09`.

Do not implement include loading.

### `MCP-01-04`: Reject Unknown MCP Provider Keys

Current runtime config already rejects unknown top-level providers. This phase must also reject unknown keys inside the MCP provider config and nested MCP server config.

### `MCP-01-05`: Validate Invalid Combinations

Add explicit validation for:

- duplicate server names;
- duplicate canonical server IDs if normalization is applied;
- disabled servers;
- invalid transports;
- missing stdio commands;
- unsafe or disallowed `cwd`;
- invalid timeout values;
- invalid retry counts;
- invalid limit values;
- invalid trust levels;
- conflicting include and exclude behavior;
- `required: true` on a disabled server if that combination is not allowed by policy.

Use explicit exceptions with clear messages.

### `MCP-01-06`: Define Config Precedence

Document and implement precedence in code where this phase owns it:

1. canonical runtime config file;
2. explicit construction or test overrides;
3. permitted environment overrides;
4. Friday Chat aliases only after canonical normalization.

Do not add a second MCP-specific config authority.

### `MCP-01-07`: Add Config Examples

Add or update examples for:

- MCP disabled;
- one stdio server;
- optional server failure semantics;
- required server failure semantics;
- strict include filters;
- strict exclude filters;
- rejected `config_file`.

Examples must match tests.

## Migration And Removal Instructions

Preserve existing config behavior for non-MCP tool providers. Existing MCP config shapes may be accepted only if they normalize into the canonical model without ambiguity. If backwards compatibility creates ambiguity, stop and report the conflict.

Do not remove existing config fields unless tests prove they are replaced by canonical fields and no current caller depends on them.

## Security And Governance Requirements

- Do not pass full config to servers.
- Do not log raw `env`, headers, secrets, or local paths beyond redacted diagnostics.
- Validate `cwd` against allowed workspace roots or the configured path policy.
- Reject unsafe path traversal.
- Use explicit exceptions rather than `assert`.
- Do not add broad mypy suppressions.
- Keep config parsing typed and deterministic.

## Testing Requirements

Add tests for:

- canonical config parsing;
- provider disabled behavior;
- empty server list behavior;
- one valid stdio server;
- optional server config;
- required server config;
- include and exclude filters;
- unknown provider keys;
- unknown server keys;
- rejected `config_file`;
- invalid transport;
- missing stdio command;
- unsafe `cwd`;
- invalid timeout and retry values;
- invalid limits;
- duplicate server names;
- invalid trust levels;
- round-trip DTO behavior where applicable.

Negative tests are mandatory.

## Verification Commands

Run:

```bash
uv run pytest packages/friday-mcp/tests_mcp
uv run pytest packages/friday-runtime/tests_runtime
uv run ruff check packages/friday-mcp packages/friday-runtime
uv run mypy packages/friday-mcp packages/friday-runtime
```

If config templates are edited, also run the relevant Friday Chat config tests:

```bash
uv run pytest packages/friday-chat/tests_chat
```

Report any unrelated legacy failures exactly.

## CLI, API, And UAT Requirements

No CLI behavior is required in this phase.

API expectations:

- Runtime config returns a typed MCP provider config.
- Unsupported future fields fail with actionable messages.
- Disabled MCP config remains cheap to parse and safe.

UAT:

- Parse a sample config with MCP disabled.
- Parse a sample config with one stdio server.
- Verify `config_file` fails before runtime startup.

## Documentation Close-Out

Update developer-facing config comments or examples if they are part of the config templates. End-user guide work belongs to `MCP-WS-08`, but examples added here must be usable by that phase.

## Reporting Requirements

Report:

- files changed;
- supported config fields;
- rejected config fields;
- validation errors added;
- backwards-compatibility decisions;
- examples added or updated;
- verification commands and results;
- skipped checks and why;
- blockers for `MCP-WS-02`.

## Stop Conditions

Stop if:

- `MCP-WS-00` contracts are missing;
- canonical config cannot be modeled without a second config authority;
- supporting old and new config shapes would be ambiguous;
- path security cannot be validated with current policy;
- Friday Chat aliases would require behavior changes outside config normalization;
- implementation requires runtime connection or tool registration behavior.
