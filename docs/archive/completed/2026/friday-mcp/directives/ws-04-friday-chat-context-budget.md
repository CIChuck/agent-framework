# Construction Directive: MCP-WS-04 Friday Chat Tool Context And Budget Management

Status: Approved construction directive
Date: 2026-09-28
Tactical plan: [Friday Framework MCP Tactical Implementation Plan](../tactical-plan.md)
Workstream: `MCP-WS-04`
Approval: Maintainer explicitly said "proceed - lets build it" after reviewing
all eight proposed WS-04 features, non-goals and the approval boundary.
Work-unit base: `acd1fd1e736a38134fac40d7fdb35cd1f32cf683`
Branch: `feature/friday-mcp-ws04-chat-budget`

## AI Builder Role

You are the implementation agent for making Friday Chat MCP-aware at turn assembly time. Your job is to integrate registered MCP tools into Friday Chat tool selection while enforcing schema, tool-count, result-reservation, and memory-retrieval budgets before prompts are sent to the model.

## Source Authority And Precedence

1. [Repository engineering policy](../../../../../reference/policies/repository-engineering-policy.md)
2. [Friday Framework MCP tactical implementation plan](../tactical-plan.md)
3. [Friday Framework MCP enhancements build plan](../build-plan.md)
4. Completed `MCP-WS-00` through `MCP-WS-03`
5. Current Friday Chat config, tools, and turn processor source

## Implementation Objective

Friday Chat must be able to include MCP tools without blindly injecting all discovered schemas into every turn. The turn processor must calculate a context budget that accounts for selected tool schema cost and reserved tool-result budget before memory retrieval occurs.

## Allowed Scope

Exact product paths:

- `packages/friday-chat/src/friday_chat/config.py`
- `packages/friday-chat/src/friday_chat/tools/selection.py`
- `packages/friday-chat/src/friday_chat/tools/mcp.py` (new public Chat bridge)
- `packages/friday-chat/src/friday_chat/turns/processor.py`
- `packages/friday-chat/src/friday_chat/commands/tools.py`
- `packages/friday-chat/src/friday_chat/runtime.py`
- `packages/friday-chat/src/friday_chat/app.py`

Exact tests:

- `packages/friday-chat/tests_chat/test_mcp_config_compatibility.py`
- `packages/friday-chat/tests_chat/test_mcp_turn_budget.py` (new)
- `packages/friday-chat/tests_chat/test_mcp_chat_bridge.py` (new local peer/UAT)

Exact report: `execution/WS-04-implementation-report.md`.
Controller-owned readiness, request, review/evidence, closeout, queue, index,
execution-log and board/dashboard artifacts are separate process scope.

No runtime/core/MCP/native registry/transport source, dependency/config example,
transcript, ingestion or telemetry change. The Chat `memory/` directory named in
the old draft does not exist; existing memory retrieval already accepts exact
`token_limit`. Runtime config normalization is already available and unchanged.

Direct Chat has its own synchronous registry and does not construct RuntimeKernel.
The two Chat wiring paths above are necessary for the approved registry/config
feature: assemble an explicit Chat bridge around the accepted public
`RuntimeMCPProvider` and `DefaultToolRegistry`, start before commands/turns and
stop through the same retained owner at app exit/failure/cancellation. This is
consumer wiring; no accepted runtime/transport lifecycle semantics or budgets
change. Fake runtime construction does not connect configured external peers;
local peer tests explicitly install the bridge with fake model/storage services.

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

## Reconciled Contracts And Compatibility

- Retain canonical `tools.providers.mcp` stanza and validate with the existing
  typed `MCPToolProviderConfig`; no parallel public server/provider config.
  Invalid MCP config fails safely during Chat parsing, including when disabled.
- MCP tools use the accepted provider, public registry callable and read-only
  metadata; direct Chat's existing native tool calls stay through their adapter.
  Provider owner remains publicly reachable after incomplete startup/stop;
  repeated public cleanup retries recover before owner replacement.
- Selection inspects the sidecar, rejects missing/unmeasured/unsafe/not-registered
  metadata before prompt assembly, copies/revalidates current schemas through
  accepted public sanitation, and bounds complete current model exports.
  Unsafe annotation changes are rejected, not silently resanitized for export.
- With MCP disabled, preserve native-only/manual/disabled selection and existing
  context arithmetic. Existing Chat tool commands retain their meanings.
- Canonical MCP client limits supply result reservation and memory floor when
  Chat tools and MCP are enabled. Reserve result tokens when any tool is selected;
  empty selection reserves zero. Floor applies even with no fitting tools.
  Impossible base budgets fail before memory/model calls.
- Existing max-tools and schema-ratio limits remain authoritative. Optional
  `tools.context.max_mcp_tools` is a nonnegative per-turn MCP subset cap; no new
  global registry cap. MCP selected schemas also obey canonical aggregate and
  per-tool caps. MCP cost must never be below accepted complete-export cost;
  native estimation remains compatible behind an injectable typed interface.
- Optional `tools.context.required_tools` is a unique explicit list of registered
  native/canonical MCP names. In automatic mode these are selected before optional
  candidates. Exact manual selections are required for that turn; union them with
  configured required tools. Provider include filters and required servers do not
  implicitly mark every eligible tool required for every turn.
- Required unavailable/invalid/count/schema/floor-exceeding tools fail clearly;
  no silent dropping. Optional selection retains deterministic relevance/registry
  ordering; reduce optional MCP tools before sacrificing optional native tools
  to preserve the floor. Do not mutate the persistent manual set on failed turns.
- Typed immutable budget evidence records selected/skipped names and static
  reasons, schema costs, result reservation, floor and memory allowance before/
  after selection. Exclude raw schema bytes from diagnostic repr; commands bound
  display text. Ordinary model schemas and MCP results remain subject to the
  explicitly deferred output/security contracts, not a universal safety promise.

## Acceptance Criteria

- MCP-04-AC-01: canonical strict config bridge, compatible disabled/native/fake
  startup and no duplicate MCP authority.
- MCP-04-AC-02: real direct Chat public registry discovery/metadata/exact original
  routing, lifecycle owner retained across failed cleanup/retry and app exit;
  commands coherent without manager internals or changed runtime budgets.
- MCP-04-AC-03: per-turn total/MCP counts, aggregate/per-tool costs, defensive
  schema/metadata validation and independent model-bound schema snapshots.
- MCP-04-AC-04: output/system/schema/result reservation calculated before memory
  retrieval; exact remaining limit passed to retrieval, same streaming behavior.
- MCP-04-AC-05: floor preserved through deterministic optional reduction, including
  empty/native/MCP/mixed tools and impossible-base-budget failure.
- MCP-04-AC-06: explicit required/complete manual sets never silently omitted;
  unavailable/invalid/over-budget requirements fail before memory/model calls.
- MCP-04-AC-07: injectable typed estimator with pinned compatible native behavior
  and conservative MCP cost; no broad suppressions/dependency/config drift.
- MCP-04-AC-08: safe typed selection/budget reasons and command diagnostics with
  no peer secrets/unsafe schemas in errors/logs/repr; accurate migration/report
  and frozen local-only validation with all required checks and residual gates.

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

Run with `LITELLM_LOCAL_MODEL_COST_MAP=true UV_CACHE_DIR=/private/tmp/friday-uv-cache`
for tests and `UV_CACHE_DIR=/private/tmp/friday-uv-cache` for tooling:

```bash
uv run pytest packages/friday-chat/tests_chat
uv run pytest packages/friday-runtime/tests_runtime
uv run pytest packages/friday-memory/tests_memory
uv run ruff check packages/friday-chat packages/friday-runtime packages/friday-memory
uv run mypy packages/friday-chat packages/friday-runtime packages/friday-memory
```

Also run integration and accepted runtime/MCP regressions because Chat consumes
the public runtime provider:

```bash
uv run pytest tests/integration
uv run pytest packages/friday-core/tests_core packages/friday-mcp/tests_mcp packages/friday-runtime/tests_runtime tests/integration/test_mcp_registry.py tests/integration/test_mcp_runtime_lifecycle.py
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

## Independent Review And Delivery Gate

Commit a stable product/test/report candidate. New fresh-context read-only
VAL-010 evaluates the complete WS-04 aggregate from the work-unit base,
all eight criteria, exact authority hashes, all required commands and its own
local probes. No inherited controller/builder/remediator sessions. A changed
candidate requires a new fresh review. Controller records VERIFIED closeout
before explicit maintainer work-unit acceptance. Local fake peers only; no
live service, credentials, model/provider/network UAT or delivery authority.
