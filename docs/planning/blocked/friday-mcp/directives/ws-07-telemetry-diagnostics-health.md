# Construction Directive: MCP-WS-07 Telemetry, Diagnostics, And Health Surfaces

Status: Draft construction directive
Date: 2026-07-24
Tactical plan: [Friday Framework MCP Tactical Implementation Plan](../tactical-plan.md)
Workstream: `MCP-WS-07`

## AI Builder Role

You are the implementation agent for MCP operational visibility. Your job is to add redacted telemetry, structured diagnostics, and any approved health surface needed to understand MCP connection, discovery, registration, execution, budget, and ingestion behavior.

## Source Authority And Precedence

1. [Repository engineering policy](../../../../reference/policies/repository-engineering-policy.md)
2. [Friday Framework MCP tactical implementation plan](../tactical-plan.md)
3. [Friday Framework MCP enhancements build plan](../build-plan.md)
4. Completed `MCP-WS-02` through `MCP-WS-06`
5. Current telemetry, runtime diagnostics, and Friday Chat command source

## Implementation Objective

Expose MCP operational state without leaking secrets or unsafe payloads. Operators should be able to determine which servers connected, which tools registered or skipped, why budget/security decisions happened, and what happened during tool execution and optional ingestion.

## Allowed Scope

You may edit:

- `packages/friday-telemetry/src/friday_telemetry/`
- `packages/friday-telemetry/tests_telemetry/`
- `packages/friday-runtime/src/friday_runtime/`
- `packages/friday-runtime/tests_runtime/`
- `packages/friday-chat/src/friday_chat/`
- `packages/friday-chat/tests_chat/`
- `packages/friday-mcp/src/friday_mcp/client/`
- `packages/friday-mcp/tests_mcp/`

Only add Friday Chat command behavior if the health command is approved for the first implementation pass.

## Explicit Non-Goals

- Do not add telemetry endpoints or backend services.
- Do not expose raw tool schemas.
- Do not expose raw tool outputs.
- Do not expose raw arguments, env values, headers, or secrets.
- Do not implement MCP live refresh.
- Do not implement resources, prompts, server exposure, or external config includes.
- Do not change config shape except for diagnostics toggles already planned.
- Do not enable memory ingestion.

## Required Workstreams

### `MCP-07-01`: Telemetry Events

Add redacted telemetry event contracts and emission points for:

- server connection start and finish;
- server connection failure;
- list-tools start and finish;
- list-tools failure;
- skipped tool;
- registered tool;
- tool call start;
- tool call finish;
- tool call failure;
- ingestion decision;
- server disconnect.

Events must use typed payloads where local telemetry conventions support them.

### `MCP-07-02`: Telemetry Redaction

Prove telemetry excludes:

- secrets;
- raw arguments;
- raw outputs;
- raw environment values;
- headers;
- unsanitized schemas;
- full local config payloads.

### `MCP-07-03`: Runtime Diagnostics

Add diagnostics for:

- optional server failures;
- required server failures;
- discovery caps;
- schema caps;
- skipped tools;
- registered tool counts;
- normalized-name collisions;
- budget skips;
- result truncation;
- ingestion allowed or denied.

Diagnostics must be structured and redacted.

### `MCP-07-04`: Decide Friday Chat Health Command

Before adding a command, confirm whether it is authorized for the first implementation pass. If not authorized, document that structured diagnostics are available through runtime state and defer CLI exposure.

### `MCP-07-05`: Health Command If Approved

If approved, expose a Friday Chat health command that shows:

- server state;
- registered MCP tool count;
- skipped MCP tool count;
- optional failure summaries;
- required failure summaries from failed startup where available;
- budget skip summaries;
- ingestion policy summary.

The command must not display raw schemas, raw outputs, secrets, env values, or headers.

### `MCP-07-06`: Structured Diagnostic Models

Add typed diagnostic models suitable for CLI display, tests, and future web display. Do not make callers parse log text.

## Migration And Removal Instructions

Preserve telemetry opt-in behavior. Do not introduce required telemetry for MCP operation.

If diagnostics replace existing log-only behavior, keep logs useful but make structured diagnostics the testable authority.

## Security And Governance Requirements

- Redaction is mandatory.
- No raw secrets or unsafe payloads in telemetry, diagnostics, command output, or logs.
- Treat diagnostics as user-visible.
- Use explicit exceptions for diagnostic invariant failures.
- Do not add broad mypy suppressions.
- Preserve telemetry opt-in semantics.

## Testing Requirements

Add tests for:

- telemetry event shape;
- telemetry redaction;
- server connection event sequence;
- list-tools event sequence;
- skipped tool events;
- registered tool events;
- tool call success events;
- tool call failure events;
- ingestion decision events;
- optional server failure diagnostics;
- required server failure diagnostics;
- collision diagnostics;
- cap skip diagnostics;
- budget skip diagnostics;
- health command output if implemented.

Negative tests must prove secrets, headers, raw env values, raw arguments, raw outputs, and unsanitized schemas are not emitted.

## Verification Commands

Run:

```bash
uv run pytest packages/friday-telemetry/tests_telemetry
uv run pytest packages/friday-runtime/tests_runtime
uv run pytest packages/friday-chat/tests_chat
uv run pytest packages/friday-mcp/tests_mcp
uv run ruff check packages/friday-telemetry packages/friday-runtime packages/friday-chat packages/friday-mcp
uv run mypy packages/friday-telemetry packages/friday-runtime packages/friday-chat packages/friday-mcp
```

If health command behavior affects top-level flows, also run:

```bash
uv run pytest tests/integration
```

## CLI, API, And UAT Requirements

CLI:

- Health command is optional and must be explicitly approved before implementation.
- If implemented, command output must be concise, redacted, and test-covered.

API:

- Runtime diagnostics should be structured.
- Telemetry payloads should be typed or schema-stable.

UAT:

- Start with one working server and inspect diagnostics.
- Start with one optional failing server and inspect diagnostics.
- Trigger a schema cap skip and inspect diagnostics.
- Execute an MCP tool and verify success/failure events are redacted.
- If implemented, run the health command and verify no secrets or raw outputs appear.

## Documentation Close-Out

Record operational diagnostics and any health command for `MCP-WS-08`. Do not update the final end-user guide unless this phase is intentionally paired with docs.

## Reporting Requirements

Report:

- files changed;
- telemetry events added;
- diagnostics models added;
- redaction behavior;
- health command decision;
- command behavior if implemented;
- verification commands and results;
- skipped checks;
- follow-up required for documentation.

## Stop Conditions

Stop if:

- prior runtime, registry, chat, provenance, and memory phases are incomplete;
- telemetry cannot be redacted with tests;
- diagnostics require exposing raw schemas or outputs;
- health command authorization is unclear;
- implementation requires new telemetry infrastructure, external services, resources, prompts, live refresh, server exposure, or external config includes.
