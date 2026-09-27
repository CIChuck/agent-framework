# Construction Directive: MCP-WS-03 Tool Naming, Metadata, Filtering, And Registry Integration

Status: Draft construction directive
Date: 2026-07-24
Tactical plan: [Friday Framework MCP Tactical Implementation Plan](../tactical-plan.md)
Workstream: `MCP-WS-03`

## AI Builder Role

You are the implementation agent for converting discovered MCP tools into Friday tool registry entries. Your job is to make MCP tools deterministic, metadata-rich, filtered, budget-capped, sanitized, and compatible with existing Friday tool protocols.

## Source Authority And Precedence

1. [Repository engineering policy](../../../../reference/policies/repository-engineering-policy.md)
2. [Friday Framework MCP tactical implementation plan](../tactical-plan.md)
3. [Friday Framework MCP enhancements build plan](../build-plan.md)
4. Completed `MCP-WS-00`, `MCP-WS-01`, and `MCP-WS-02`
5. Current tool registry and MCP adapter source

## Implementation Objective

Register discovered MCP tools in the Friday runtime tool registry with canonical names, provenance metadata, strict include/exclude behavior, schema caps, collision detection, and sanitization. Native tools must continue to work unchanged.

## Allowed Scope

You may edit:

- `packages/friday-core/src/friday_core/interfaces/tools.py`
- `packages/friday-runtime/src/friday_runtime/tool_loading.py`
- `packages/friday-runtime/src/friday_runtime/tools.py`
- `packages/friday-mcp/src/friday_mcp/client/adapter.py`
- `packages/friday-mcp/src/friday_mcp/client/manager.py`
- `packages/friday-tools/src/friday_tools/` only for protocol compatibility work
- `packages/friday-core/tests_core/`
- `packages/friday-runtime/tests_runtime/`
- `packages/friday-mcp/tests_mcp/`
- `packages/friday-tools/tests_tools/`
- `tests/integration/` only for mixed native and MCP registry coverage

## Explicit Non-Goals

- Do not implement Friday Chat per-turn ranking or budget trimming.
- Do not change transcript persistence.
- Do not implement memory ingestion.
- Do not add telemetry event emission beyond diagnostics needed by registry tests.
- Do not add CLI health commands.
- Do not implement MCP resources, prompts, server exposure, live refresh, or external config includes.
- Do not change native tool APIs beyond the minimum required stable metadata strategy chosen in `MCP-WS-00`.

## Required Workstreams

### `MCP-03-01`: Canonical Tool Names

Implement deterministic canonical tool names using:

```text
<tool_name_prefix>_<server_name>_<original_tool_name>
```

The default prefix is `mcp` unless config overrides it. Normalize names to the current Friday and OpenAI-compatible tool name constraints.

### `MCP-03-02`: Collision Detection

Fail closed on normalized name collisions. Include the colliding server names, original tool names, canonical name, and provider source in diagnostics.

Do not silently overwrite or drop a colliding tool without diagnostics.

### `MCP-03-03`: Metadata Attachment

Attach metadata to every registered MCP tool:

- provider type;
- configured server name;
- original MCP tool name;
- canonical Friday tool name;
- transport;
- trust level;
- schema byte size;
- schema token estimate if available;
- discovery state;
- sanitized schema status.

Use the metadata representation selected in `MCP-WS-00`. Do not access private adapter internals from later-facing code.

### `MCP-03-04`: Include And Exclude Filters

Apply `include_tools` and `exclude_tools` against canonical prefixed names. Preserve the first-pass decision that original-name filters are deferred.

### `MCP-03-05`: Missing Include Diagnostics

Change filtering behavior so requested include names that do not match any discovered tool are diagnosable. If the policy requires failure, fail with a clear error; otherwise preserve the diagnostic for health and reporting surfaces.

### `MCP-03-06`: Discovery And Registration Caps

Enforce:

- `max_tools_per_server`;
- `max_total_tools`;
- `max_schema_bytes_per_tool`;
- aggregate schema budget where owned by runtime;
- accepted versus skipped tool counts.

Caps must apply before registry registration.

### `MCP-03-07`: Registration-Time Sanitization

Sanitize tool names, descriptions, and schemas at registration time. Preserve enough diagnostics to identify sanitized or skipped tools without exposing unsafe raw content.

### `MCP-03-08`: Protocol Compatibility

Verify registered MCP wrappers satisfy the current Friday tool protocol, including:

- `name`;
- `description`;
- `parameters_schema`;
- `category`;
- `tags`;
- `execute`;
- `to_schema`.

Do not rely on incidental attributes that are not part of the declared protocol or metadata strategy.

## Migration And Removal Instructions

If the tool protocol must be extended, preserve native tool compatibility. Prefer additive metadata access over mandatory changes to every native tool implementation.

If a registry sidecar is chosen, keep the sidecar internally consistent and test lookup behavior for both native and MCP tools.

## Security And Governance Requirements

- Treat MCP tool names, descriptions, and schemas as untrusted.
- Sanitize before registration and again verify before prompt assembly in later phases.
- Do not log raw unsafe schemas.
- Do not leak env values, headers, or server credentials in diagnostics.
- Enforce caps before exposing tools to model-facing code.
- Use explicit exceptions for essential invariants.
- Do not add broad mypy suppressions.

## Testing Requirements

Add tests for:

- canonical name generation;
- invalid character normalization;
- duplicate normalized names;
- prefix overrides;
- include filter behavior;
- exclude filter behavior;
- missing include diagnostics;
- server-level cap enforcement;
- provider-level cap enforcement;
- schema byte cap enforcement;
- metadata presence;
- metadata correctness;
- sanitized descriptions and schemas;
- protocol conformance;
- mixed native and MCP registry behavior.

Negative tests are required for oversized schemas, duplicate names, unsafe schema text, invalid names, and missing required protocol properties.

## Verification Commands

Run:

```bash
uv run pytest packages/friday-core/tests_core
uv run pytest packages/friday-mcp/tests_mcp
uv run pytest packages/friday-runtime/tests_runtime
uv run pytest packages/friday-tools/tests_tools
uv run pytest tests/integration
uv run ruff check packages/friday-core packages/friday-mcp packages/friday-runtime packages/friday-tools
uv run mypy packages/friday-core packages/friday-mcp packages/friday-runtime packages/friday-tools
```

Report unrelated legacy failures separately from new failures.

## CLI, API, And UAT Requirements

No CLI command is required in this phase.

API expectations:

- Tool registry can expose MCP metadata through the selected stable path.
- Native tools remain compatible.
- Diagnostics can explain skipped and registered MCP tools.

UAT:

- Register native tools only.
- Register one fake MCP tool.
- Register native and MCP tools together.
- Attempt duplicate canonical names and verify failure.
- Apply include and exclude filters and verify exact registered names.

## Documentation Close-Out

No end-user guide update is required in this phase. If public tool metadata APIs are added, add concise developer-facing documentation or docstrings sufficient for later phases.

## Reporting Requirements

Report:

- files changed;
- naming behavior implemented;
- metadata strategy used;
- filter semantics;
- cap enforcement points;
- sanitization behavior;
- native tool compatibility evidence;
- verification commands and results;
- skipped verification;
- follow-up required for `MCP-WS-04`.

## Stop Conditions

Stop if:

- prior workstreams are incomplete;
- canonical naming constraints cannot be satisfied;
- metadata cannot be attached without hidden cross-package coupling;
- native tool compatibility would require broad refactoring;
- cap enforcement cannot occur before registry registration;
- implementation requires Friday Chat turn changes, memory ingestion, transcript export changes, live refresh, or external config includes.
