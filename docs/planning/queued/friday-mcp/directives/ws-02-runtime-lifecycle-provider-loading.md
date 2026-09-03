# Construction Directive: MCP-WS-02 Runtime Lifecycle And MCP Provider Loading

Status: Draft construction directive
Date: 2026-07-24
Tactical plan: [Friday Framework MCP Tactical Implementation Plan](../tactical-plan.md)
Workstream: `MCP-WS-02`

## AI Builder Role

You are the implementation agent for MCP runtime lifecycle integration. Your job is to make the Friday runtime capable of owning MCP client managers, connecting enabled servers during async startup, discovering available tools, preserving diagnostics, and disconnecting clients during shutdown.

This phase authorizes lifecycle plumbing and discovery flow. It does not authorize per-turn Friday Chat budget behavior, transcript persistence, memory ingestion, telemetry event wiring, health commands, resources, prompts, live refresh, or external config includes.

## Source Authority And Precedence

1. [Repository engineering policy](../../../../reference/policies/repository-engineering-policy.md)
2. [Friday Framework MCP tactical implementation plan](../tactical-plan.md)
3. [Friday Framework MCP enhancements build plan](../build-plan.md)
4. Completed `MCP-WS-00` and `MCP-WS-01`
5. Current `friday-runtime` and `friday-mcp` source

## Implementation Objective

Replace the current unsupported MCP path in runtime tool loading with an async runtime-owned MCP provider loader. The runtime must be able to connect configured MCP servers, list tools, record diagnostics, enforce optional versus required server semantics, and shut down cleanly.

## Allowed Scope

You may edit:

- `packages/friday-runtime/src/friday_runtime/di.py`
- `packages/friday-runtime/src/friday_runtime/kernel.py`
- `packages/friday-runtime/src/friday_runtime/tool_loading.py`
- `packages/friday-runtime/src/friday_runtime/tools.py`
- new runtime modules if needed for MCP provider loading
- `packages/friday-mcp/src/friday_mcp/client/manager.py`
- `packages/friday-mcp/src/friday_mcp/client/adapter.py`
- `packages/friday-runtime/tests_runtime/`
- `packages/friday-mcp/tests_mcp/`
- `tests/integration/` only for a fake-server runtime integration test

Keep edits narrowly tied to runtime lifecycle and provider loading.

## Explicit Non-Goals

- Do not implement live refresh or reload.
- Do not implement MCP resources or prompts.
- Do not expose Friday as an MCP server.
- Do not implement Friday Chat per-turn selection or budget logic.
- Do not implement memory ingestion.
- Do not implement transcript export changes.
- Do not add telemetry event emitters unless a no-op diagnostics hook is needed for later phases.
- Do not add a CLI health command.
- Do not implement `config_file`.

## Required Workstreams

### `MCP-02-01`: Async Runtime Tool Registration

Replace or augment synchronous `register_runtime_tools` behavior so MCP provider registration can occur during async runtime boot.

Do not break existing native tool registration. The runtime should still support disabled MCP with the current lightweight path.

### `MCP-02-02`: Runtime-Owned MCP Client Manager

Add a provider loader that creates, stores, and owns an `MCPClientManager` for the runtime lifetime.

The manager must not be a hidden global. It must be reachable through explicit runtime state or service composition suitable for diagnostics and shutdown.

### `MCP-02-03`: Startup Order

Implement this startup order:

1. configure runtime services;
2. connect enabled MCP servers;
3. list tools from connected servers;
4. apply discovery caps from config;
5. prepare accepted tools for later registry registration;
6. register accepted tools if this phase owns the registry boundary, or hand them to `MCP-WS-03`;
7. validate agent tool bindings after MCP discovery has completed.

If registry registration is deferred to `MCP-WS-03`, preserve enough discovered state and diagnostics for that phase.

### `MCP-02-04`: Shutdown Order

Ensure runtime shutdown disconnects MCP clients even when startup partially fails. Shutdown must be idempotent.

### `MCP-02-05`: Optional Versus Required Server Behavior

Implement required semantics:

- optional server connection or discovery failure does not fail runtime startup;
- required server connection or discovery failure fails startup;
- disabled servers are skipped;
- failures are diagnosable.

### `MCP-02-06`: Timeout Handling

Apply connection and discovery timeouts from config. A timeout for a required server must fail startup. A timeout for an optional server must be recorded and skipped.

### `MCP-02-07`: Bounded Discovery Concurrency

Implement bounded connection and discovery concurrency. Do not use unbounded `gather` over arbitrary configured servers.

### `MCP-02-08`: Diagnostics Preservation

Persist diagnostics for:

- connected servers;
- failed optional servers;
- failed required servers;
- skipped disabled servers;
- discovery timeouts;
- list-tools failures;
- partial success.

Diagnostics must be redacted.

## Migration And Removal Instructions

Remove the intentional "MCP enabled is unsupported" runtime failure only when replacement behavior is implemented and tested.

Preserve existing native tool loading behavior and tests. If changing public runtime startup signatures is unavoidable, stop and report the API migration before editing.

## Security And Governance Requirements

- Do not pass the full Friday config object into MCP clients.
- Pass only the server-specific, redacted, validated config needed to connect.
- Do not log raw env values, headers, arguments, or local secrets.
- Treat tool schemas returned during discovery as untrusted.
- Enforce timeouts.
- Bound concurrency.
- Use explicit exceptions.
- Do not add broad mypy ignores.
- Preserve cleanup behavior on partial failure.

## Testing Requirements

Add tests for:

- MCP disabled runtime boot;
- MCP enabled with no servers;
- one successful fake stdio server;
- optional server connection failure;
- required server connection failure;
- optional list-tools failure;
- required list-tools failure;
- discovery timeout;
- partial success with one good and one failed optional server;
- shutdown after successful startup;
- shutdown after partial startup failure;
- native tool loading unaffected;
- agent tool binding validation after discovery.

Negative tests must prove failed optional servers do not register tools and required failures fail startup.

## Verification Commands

Run:

```bash
uv run pytest packages/friday-runtime/tests_runtime
uv run pytest packages/friday-mcp/tests_mcp
uv run pytest tests/integration
uv run ruff check packages/friday-runtime packages/friday-mcp
uv run mypy packages/friday-runtime packages/friday-mcp
```

If integration tests are too broad due to unrelated legacy failures, run the specific MCP integration test file and report the broader failure.

## CLI, API, And UAT Requirements

No CLI command is required in this phase.

API expectations:

- Runtime startup owns MCP manager lifetime.
- Diagnostics can be inspected through a typed runtime-accessible surface.
- Shutdown is explicit and idempotent.

UAT:

- Start runtime with MCP disabled.
- Start runtime with a fake stdio MCP server.
- Start runtime with optional server failure and confirm startup succeeds with diagnostics.
- Start runtime with required server failure and confirm startup fails.

## Documentation Close-Out

Do not write user-facing MCP setup guides in this phase unless implementation changes require developer notes. User-facing docs belong to `MCP-WS-08`.

## Reporting Requirements

Report:

- lifecycle files changed;
- whether `register_runtime_tools` remained sync, became async, or was split;
- how MCP manager lifetime is owned;
- optional and required failure behavior;
- diagnostics shape;
- cleanup behavior;
- verification commands and results;
- any skipped checks;
- follow-up required for `MCP-WS-03`.

## Stop Conditions

Stop if:

- `MCP-WS-00` or `MCP-WS-01` is incomplete;
- async lifecycle integration requires a breaking public runtime startup API change;
- MCP manager ownership would become global or hidden;
- optional server failures cannot be diagnosed;
- cleanup cannot be guaranteed after partial startup;
- implementation requires live refresh, Friday Chat budget logic, memory ingestion, or telemetry event emission.
