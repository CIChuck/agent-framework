# Construction Directive: MCP-WS-00 Contract And Policy Foundation

Status: Draft construction directive  
Date: 2026-07-24  
Tactical plan: [Friday Framework MCP Tactical Implementation Plan](../planning/friday-framework-mcp-tactical-implementation-plan.md)  
Workstream: `MCP-WS-00`

## AI Builder Role

You are the implementation agent for the Friday Framework MCP contract and policy foundation phase. Your job is to define the stable typed contracts, defaults, policy decisions, and test evidence that later MCP runtime, chat, memory, transcript, and telemetry phases will depend on.

This phase is architectural foundation work. Do not implement MCP server connection, tool discovery, registry registration, Friday Chat turn behavior, transcript persistence, memory ingestion, telemetry events, or external MCP config includes in this phase.

## Source Authority And Precedence

1. [Repository engineering policy](../reference/policies/repository-engineering-policy.md)
2. [Friday Framework MCP tactical implementation plan](../planning/friday-framework-mcp-tactical-implementation-plan.md)
3. [Friday Framework MCP enhancements build plan](../planning/build-plans/friday-framework-mcp-enhancements.md)
4. Current source code in `packages/`
5. Current tests in package-local test folders

`docs/methodology/constitution/gendev.md` is referenced by the planning skill but was not present when this directive was created. If it is restored before implementation, read it and reconcile this directive with it before editing source.

## Implementation Objective

Create the shared MCP client contracts and baseline policy defaults needed by the Friday Framework. The result must give later phases a typed, importable, circular-dependency-free vocabulary for MCP limits, security policy, ingestion policy, discovery state, tool metadata, call provenance, diagnostics, and naming.

## Allowed Scope

You may edit only the files necessary to define and test MCP contracts and defaults:

- `packages/friday-core/src/friday_core/`
- `packages/friday-core/src/friday_core/interfaces/`
- `packages/friday-core/tests_core/`
- `packages/friday-mcp/src/friday_mcp/`
- `packages/friday-mcp/tests_mcp/`
- Small package `__init__.py` exports where needed
- Planning notes only if a decision is explicitly finalized during implementation

If the selected ownership requires a different package, stop and report why before editing that package.

## Explicit Non-Goals

- Do not implement runtime MCP loading.
- Do not implement MCP client connection or discovery behavior.
- Do not register MCP tools.
- Do not change Friday Chat turn processing.
- Do not change memory ingestion behavior.
- Do not change transcript persistence.
- Do not add telemetry emitters.
- Do not add CLI commands.
- Do not implement MCP resources, prompts, subscriptions, server exposure, live refresh, or external config includes.
- Do not remove unrelated local changes, generated state, caches, `.friday/`, Chroma data, or transcript state.

## Required Workstreams

### `MCP-00-01`: Choose Contract Ownership

Inspect current imports and package boundaries before editing. Decide whether shared DTOs belong in `friday-core` or `friday-mcp`.

Prefer `friday-core` when a contract is consumed across runtime, chat, memory, transcript, telemetry, and MCP packages. Prefer `friday-mcp` only for MCP-protocol-local structures that do not need to become framework-wide contracts.

Document the decision in code organization and tests. Do not create circular imports.

### `MCP-00-02`: Define Required DTOs

Define typed contracts for:

- `MCPClientLimits`
- `MCPClientSecurityPolicy`
- `MCPIngestionPolicy`
- `MCPDiscoveryPolicy`
- `MCPServerRuntimePolicy`
- `MCPToolMetadata`
- `MCPToolCallProvenance`
- `MCPDiscoveryState`
- `MCPProviderDiagnostics`

Use dataclasses or Pydantic models consistently with surrounding package conventions. Prefer immutable or side-effect-light models when the object represents policy or provenance.

Every DTO must have explicit defaults where defaults are meaningful. Avoid `dict[str, Any]` unless the field is truly extensible metadata and cannot be modeled more precisely.

### `MCP-00-03`: Decide Tool Metadata Representation

Choose one of:

- extending the existing tool protocol;
- adding a registry sidecar;
- exposing metadata through a wrapper protocol.

The selected strategy must allow later phases to inspect MCP tool metadata without depending on private adapter internals. It must preserve compatibility with native Friday tools.

If none of the strategies fits without broad refactoring, stop and report the smallest viable interface proposal.

### `MCP-00-04`: Define First-Pass Default Limits

Set first-pass default values for:

- maximum MCP servers;
- maximum tools per server;
- maximum total MCP tools;
- maximum schema bytes per tool;
- aggregate selected schema token budget;
- maximum result bytes;
- connection timeout;
- tool execution timeout;
- minimum memory retrieval floor.

Defaults must be conservative. They must be test-covered and easy to override through later config models.

### `MCP-00-05`: Define Name Normalization

Define deterministic naming behavior for:

```text
mcp_<server_name>_<tool_name>
```

The normalization must produce names acceptable to Friday and OpenAI-style tool-calling APIs. It must specify collision behavior. Collision behavior must fail closed with diagnostic detail rather than silently overwriting tools.

### `MCP-00-06`: Define Argument Redaction And Hash Policy

Define how later phases will represent redacted arguments and argument hashes. Decide whether argument hashes are salted. If salted, define where salt configuration must come from and how missing salt is handled.

Do not store real arguments in tests unless the value is clearly non-secret.

### `MCP-00-07`: Define SSE Trust Posture

Define whether SSE transports are enabled in the first release, disabled, or allowed only with explicit trust policy. The default must be conservative and documented by tests.

### `MCP-00-08`: Record Mypy-Ignore Cleanup Expectations

Inspect touched MCP files for `# mypy: ignore-errors`. Remove broad ignores from touched source when practical. If removal is not practical in this phase, leave a narrow note in the implementation report identifying the remaining blocker. Do not add new broad suppressions.

## Migration And Removal Instructions

This phase should not migrate runtime behavior. It may introduce new public DTOs and exports. If an existing type must be moved or aliased, preserve backwards-compatible imports unless the tactical plan explicitly authorizes breaking changes.

Do not delete existing MCP config models. If new models overlap with existing models, add compatibility adapters or comments describing which model is protocol-local and which is framework-facing.

## Security And Governance Requirements

- Treat all MCP server names, tool names, descriptions, schemas, arguments, outputs, and diagnostics as untrusted.
- Defaults must not allow raw secrets, raw arguments, raw outputs, env values, or headers into telemetry, diagnostics, transcript exports, or memory.
- Use explicit exceptions for essential invariants.
- Do not rely on `assert` for runtime enforcement.
- Do not add `# mypy: ignore-errors` under `packages/*/src`.
- Prefer typed models or declared interfaces over `cast(...)`.
- Preserve package boundaries.

## Testing Requirements

Add focused tests for:

- DTO construction and default values;
- DTO serialization or conversion behavior where applicable;
- invalid limits;
- invalid enum or literal values;
- name normalization;
- duplicate normalized names;
- redaction policy defaults;
- unsafe defaults;
- importability from intended consuming packages;
- circular import prevention if feasible through import smoke tests.

Negative tests are required. Do not ship only happy-path DTO tests.

## Verification Commands

Run the narrowest commands needed for touched packages:

```bash
uv run pytest packages/friday-core/tests_core
uv run pytest packages/friday-mcp/tests_mcp
uv run ruff check packages/friday-core packages/friday-mcp
uv run mypy packages/friday-core packages/friday-mcp
```

If broader imports are touched, also run:

```bash
uv run python -c "from friday_runtime import RuntimeKernel; from friday_agent import InteractiveAgent; print('Friday imports OK')"
```

If any command fails due to unrelated legacy debt, report the exact command, failure summary, and the narrower command that passed.

## CLI, API, And UAT Requirements

No CLI command is required in this phase.

API expectations:

- New contracts must be importable through stable public module paths.
- Later phases must be able to consume metadata and policy DTOs without importing private implementation modules.

UAT for this phase is import and contract validation only.

## Documentation Close-Out

Update only minimal developer-facing documentation if the contract ownership decision would otherwise be unclear. Do not update user MCP setup guides in this phase.

If documentation is deferred, report that user-facing docs are covered by `MCP-WS-08`.

## Reporting Requirements

Report:

- files changed;
- contract ownership decision and reasoning;
- metadata representation decision and reasoning;
- default limit values selected;
- SSE trust posture;
- argument hash policy;
- broad mypy ignores removed or intentionally left;
- verification commands run and results;
- any skipped verification;
- any follow-up required before `MCP-WS-01`.

## Stop Conditions

Stop and ask for direction if:

- contract ownership would create circular imports;
- metadata representation requires a broad registry refactor;
- default budgets cannot be chosen from current plan constraints;
- SSE posture requires a product decision;
- argument hash salt policy requires a security decision;
- implementation would require changing runtime lifecycle, Friday Chat, memory, transcript, or telemetry behavior in this phase.
