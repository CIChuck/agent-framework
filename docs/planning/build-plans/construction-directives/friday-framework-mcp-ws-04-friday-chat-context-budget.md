# Construction Directive: MCP-WS-04 Friday Chat Tool Context And Budget Management

Status: Draft construction directive  
Date: 2026-07-24  
Tactical plan: [Friday Framework MCP Tactical Implementation Plan](../planning/friday-framework-mcp-tactical-implementation-plan.md)  
Workstream: `MCP-WS-04`

## AI Builder Role

You are the implementation agent for making Friday Chat MCP-aware at turn assembly time. Your job is to integrate registered MCP tools into Friday Chat tool selection while enforcing schema, tool-count, result-reservation, and memory-retrieval budgets before prompts are sent to the model.

## Source Authority And Precedence

1. [Repository engineering policy](../reference/policies/repository-engineering-policy.md)
2. [Friday Framework MCP tactical implementation plan](../planning/friday-framework-mcp-tactical-implementation-plan.md)
3. [Friday Framework MCP enhancements build plan](../planning/build-plans/friday-framework-mcp-enhancements.md)
4. Completed `MCP-WS-00` through `MCP-WS-03`
5. Current Friday Chat config, tools, and turn processor source

## Implementation Objective

Friday Chat must be able to include MCP tools without blindly injecting all discovered schemas into every turn. The turn processor must calculate a context budget that accounts for selected tool schema cost and reserved tool-result budget before memory retrieval occurs.

## Allowed Scope

You may edit:

- `packages/friday-chat/src/friday_chat/config.py`
- `packages/friday-chat/src/friday_chat/turns/processor.py`
- `packages/friday-chat/src/friday_chat/tools/`
- `packages/friday-chat/src/friday_chat/memory/`
- `packages/friday-chat/tests_chat/`
- `packages/friday-runtime/src/friday_runtime/config.py` only for config normalization needed by Friday Chat
- package exports needed for chat-visible budget types

Avoid changes to runtime lifecycle, registry internals, transcript model, memory ingestion, and telemetry unless a narrow type import is required.

## Explicit Non-Goals

- Do not implement long-term memory ingestion.
- Do not implement transcript provenance changes.
- Do not implement output sanitization or result truncation beyond reserving result budget.
- Do not add web UI for MCP configuration.
- Do not add MCP health command unless later authorized by `MCP-WS-07`.
- Do not implement resources, prompts, live refresh, server exposure, or external config includes.
- Do not add a second Friday Chat MCP config shape.

## Required Workstreams

### `MCP-04-01`: Bridge Friday Chat Config

Friday Chat must consume canonical MCP provider config from runtime models or a compatibility normalization layer. Do not create a second public MCP config structure under Friday Chat.

If current Friday Chat app config cannot consume runtime config directly, create a minimal adapter that normalizes into the same typed runtime MCP provider config.

### `MCP-04-02`: Include MCP Tools Through Existing Registry Abstraction

Use the existing tool registry abstraction to include MCP tools. Do not make Friday Chat reach into MCP client manager internals.

The selection logic must be able to inspect metadata from `MCP-WS-03`.

### `MCP-04-03`: Enforce Selected Tool Count And Schema Budget

Enforce per-turn:

- maximum selected tools;
- maximum selected MCP tools if configured;
- aggregate selected schema token budget;
- per-tool schema cap already enforced by runtime but verified defensively.

### `MCP-04-04`: Implement Context Budget Formula

Implement:

```text
available_memory_tokens =
  context_window
  - output_buffer_tokens
  - system_prompt_tokens
  - selected_tool_schema_tokens
  - reserved_tool_result_tokens
```

Then enforce the configured minimum memory retrieval floor.

### `MCP-04-05`: Prefer Tool Reduction Over Memory Starvation

If selected tool schemas would push memory below the floor, reduce selected optional tools before reducing memory below the floor. MCP tools should be reduced according to deterministic ordering or relevance rules.

### `MCP-04-06`: Required Tool Over-Budget Failure

If required selected tools cannot fit while preserving the memory floor, fail the turn with a clear diagnostic. Do not silently drop required tools.

### `MCP-04-07`: Improve Or Isolate Schema Token Estimation

The current approximate schema token estimator can remain only if it is isolated behind an interface that can be replaced. Tests must pin behavior.

### `MCP-04-08`: Add Budget Diagnostics

Expose diagnostics for:

- selected tools;
- skipped tools;
- schema token estimates;
- reserved result tokens;
- memory budget before and after tool selection;
- reasons for budget skips.

Diagnostics must not include raw unsafe schemas or secrets.

## Migration And Removal Instructions

Preserve existing non-MCP Friday Chat behavior. Existing config keys should continue to work unless a compatibility adapter explicitly translates them.

Do not remove current tool loop or registry behavior. Adapt it so MCP tools participate through the same public abstractions as native tools.

## Security And Governance Requirements

- Treat MCP schemas as untrusted even after runtime registration.
- Do not include raw diagnostics, secrets, env values, or unsafe schema content in model prompts.
- Bound selected schema size before prompt assembly.
- Preserve memory retrieval floor.
- Use explicit exceptions for impossible budget states.
- Do not add broad type suppressions.

## Testing Requirements

Add tests for:

- no tools;
- native tools only;
- MCP tools only;
- mixed native and MCP tools;
- max selected tool count;
- aggregate schema budget;
- oversized selected schema;
- reserved tool-result token budget;
- memory floor preservation;
- required tool over-budget failure;
- optional tool reduction;
- memory retrieval receives reduced token limit;
- existing non-MCP turn behavior remains unchanged;
- diagnostics for skipped tools.

Negative tests are mandatory for memory-floor exhaustion, required over-budget tools, missing metadata, and unsafe schema diagnostics.

## Verification Commands

Run:

```bash
uv run pytest packages/friday-chat/tests_chat
uv run pytest packages/friday-runtime/tests_runtime
uv run pytest packages/friday-memory/tests_memory
uv run ruff check packages/friday-chat packages/friday-runtime packages/friday-memory
uv run mypy packages/friday-chat packages/friday-runtime packages/friday-memory
```

Run integration tests if the turn processor touches cross-package runtime boot:

```bash
uv run pytest tests/integration
```

## CLI, API, And UAT Requirements

CLI:

- No new command is required.
- Existing Friday Chat startup and chat commands must continue working with MCP disabled.

API:

- Budget calculation should be testable without calling a real model.
- Tool selection should expose explainable diagnostics.

UAT:

- Start Friday Chat with MCP disabled and verify current behavior.
- Start Friday Chat with a fake MCP tool and verify the tool is selected only when it fits budget.
- Configure a small context budget and verify memory floor protection.
- Configure an oversized required tool and verify a clear failure.

## Documentation Close-Out

Do not complete user-facing docs in this phase. Record any new config or diagnostic behavior needed by `MCP-WS-08`.

## Reporting Requirements

Report:

- files changed;
- config bridge strategy;
- budget formula implementation;
- selected tool reduction behavior;
- required tool failure behavior;
- schema token estimator decision;
- memory retrieval budget evidence;
- verification commands and results;
- skipped checks;
- follow-up required for provenance and memory phases.

## Stop Conditions

Stop if:

- prior workstreams are incomplete;
- Friday Chat cannot consume canonical runtime MCP config without a second config authority;
- selected tool schemas cannot be budgeted before memory retrieval;
- preserving memory floor is impossible with current turn architecture;
- implementation requires long-term memory ingestion, transcript model changes, telemetry event emission, live refresh, or external config includes.
