# Construction Directive: MCP-WS-07 Telemetry And Diagnostics

Status: Approved construction directive
Date: 2026-09-29
Preparation base: `e98411825c2f2275f43d45762a656e8d7b85a9b0`
Approved by: repository maintainer
Approved at: 2026-09-29
Approval evidence: explicit "proceed" after review of this exact directive and the Chat health-command deferral decision
Workstream: `MCP-WS-07`
Tactical authority: [MCP tactical plan](../tactical-plan.md), tasks `MCP-07-01` through `MCP-07-06`
Readiness: [WS-07 checkpoint](../execution/WS-07-readiness-checkpoint.md)

## Objective and first-pass decision

Make MCP connection, discovery, registration, execution, Chat budget and optional
ingestion decisions observable through typed, redacted events and public
diagnostics. Preserve accepted WS-02 through WS-06 ownership, safety and
storage contracts. This proposal **defers a new Friday Chat health command** in
this pass (`MCP-07-04/05`): the headless provider already exposes safe discovery,
diagnostics, lifecycle and registration decisions, while Chat retains the
provider through `MCPChatRegistry`. A new user command requires a separate
CLI/output contract. The maintainer explicitly accepted this bounded scope and
deferral before product work started.

## Exact proposed product manifest

Only these paths may be modified or created. A necessary change outside this
list stops implementation for scope reconciliation.

| Package | Source | Focused tests |
| --- | --- | --- |
| Telemetry | `packages/friday-telemetry/src/friday_telemetry/models/mcp.py` (new), `packages/friday-telemetry/src/friday_telemetry/helpers/mcp.py` (new), `packages/friday-telemetry/src/friday_telemetry/__init__.py` | `packages/friday-telemetry/tests_telemetry/test_mcp_telemetry.py` (new) |
| Runtime | `packages/friday-runtime/src/friday_runtime/mcp_loading.py`, `packages/friday-runtime/src/friday_runtime/di.py` | `packages/friday-runtime/tests_runtime/test_mcp_loading.py`, `packages/friday-runtime/tests_runtime/test_mcp_registration.py` |
| MCP client | `packages/friday-mcp/src/friday_mcp/client/adapter.py` | `packages/friday-mcp/tests_mcp/client/test_adapter.py`, `packages/friday-mcp/tests_mcp/client/test_execution.py` |
| Chat | `packages/friday-chat/src/friday_chat/runtime.py`, `packages/friday-chat/src/friday_chat/tools/mcp.py`, `packages/friday-chat/src/friday_chat/turns/processor.py`, `packages/friday-chat/src/friday_chat/memory_mcp.py` | `packages/friday-chat/tests_chat/test_mcp_chat_bridge.py`, `packages/friday-chat/tests_chat/test_mcp_execution_security.py`, `packages/friday-chat/tests_chat/test_mcp_turn_budget.py`, `packages/friday-chat/tests_chat/test_mcp_memory.py` |

An implementation report and WS-07 planning/validation artifacts may be added
under this initiative packet. No source or test directory wildcard is granted.
Core models, configuration, dependency metadata, transcript stores, memory
storage/retrieval, Chat commands and MCP transports are outside this manifest.

## Contract and implementation order

1. **`MCP-07-06/02`: schema and redaction first.** Define closed, immutable
   typed MCP event/diagnostic payloads with fixed event and reason enums,
   nonnegative counts, bounded safe identifiers and explicit serialization to
   the existing `TelemetryInterface.capture_event` shape. Only allowlisted
   fields may serialize. Exclude arbitrary exceptions, catalog entries,
   descriptions, schemas, arguments, results, environment, headers, command/cwd,
   full config, transcript text and memory content. If an operator identifier
   cannot safely cross an exporter, emit a stable bounded opaque identifier and
   retain its mapping in existing local diagnostics.
2. **`MCP-07-01`: lifecycle.** Instrument `RuntimeMCPProvider` for connection
   start/finish/failure, list-tools start/finish/failure, per-tool skip/register
   decisions and disconnect. Emit final counts/reasons from accepted
   `discovery`, `diagnostics`, `lifecycle` and `registration_decisions`,
   including failed startup and cleanup. Do not infer a successful disconnect
   when cleanup fails. DI passes its existing optional telemetry instance;
   disabled telemetry cannot become required for MCP operation.
3. **`MCP-07-01`: calls.** A narrow optional observer on
   `MCPToolWrapper.execute` covers headless and Chat calls without adding a
   telemetry dependency to `friday-mcp`. Runtime attaches it to admitted
   wrappers. It receives safe canonical metadata and categorical
   start/finish/failure outcomes. Chat may add final checked,
   truncated/blocked status after output policy, without duplicate RPCs or
   raw result/arguments. Observer failure cannot alter tool-call behavior.
4. **`MCP-07-03`: diagnostics.** Reuse public typed runtime discovery,
   diagnostics, lifecycle and registration decisions, including REM-005's
   bounded both-source collision evidence and REM-008's retained retry history.
   Add a typed operational snapshot only where existing values cannot express
   optional/required failures, cap skips, registered counts or disconnect
   outcome. Chat emits/retains categorical budget rejections, output truncation
   and ingestion decisions from existing `ToolBudgetSnapshot`,
   `MCPToolCallProvenance` and memory preparation/receipt results. No log-text
   parsing, raw storage or private client introspection.
5. **`MCP-07-04/05`: no command in this pass.** Keep public Python inspection
   and injectable telemetry testable. Record the command decision for WS-08.
   Do not edit `commands/registry.py`, CLI or app command wiring under this
   directive. A command requires a revised exact manifest and separate approval.

Event cardinality stays bounded: no payload text, raw call ID or per-token
events. Retried startup, failed cleanup, cancellation and memory receipt reuse
must have truthful, nonduplicative outcomes. Existing telemetry opt-in and
default-disabled direct MCP memory ingestion remain intact. No event may imply
published memory when an immutable receipt exists but its record remains pending.

## Acceptance and negative checks

- Working, optional-failing and required-failing synthetic peers yield ordered
  connection/list-tools/registration/disconnect events and typed states;
  failed cleanup/retry preserve accepted ownership and last-attempt evidence.
- Discovery/schema caps, filters, collisions and native-name collisions have
  accurate bounded reasons/counts. Both collision contenders remain typed and
  inspectable; telemetry does not dump untrusted source strings.
- Headless and Chat tool success, timeout, failure, sanitizer block and
  truncation distinguish RPC completion from post-processing. Chat budget
  rejection and optional ingestion denied/allowed/pending/published outcomes
  are represented without changing execution or storage semantics.
- Planted sentinels in arguments, output, schema, description, exception, env,
  headers, command/cwd and memory text are absent from event names, payloads,
  serialized diagnostics and WS-07-added logs. Test debug and production
  exporter input boundaries.
- Telemetry disabled, observer error and unrelated native tools preserve
  behavior. Existing constructor compatibility and import/install package
  boundaries hold without a new dependency.

## Verification and handoff

Run focused new tests, then package suites for Telemetry, Runtime, MCP and Chat
and relevant top-level integration tests. Run Ruff on affected packages,
meaningful affected-source mypy under the installed Python target, board
validate/next/show/render, documentation/link validation and exact
diff/whitespace checks. Report pre-existing broad-suite/default-mypy/offline
resolver failures separately; do not call a nonzero command passing. Prove
imports and representative events from isolated built distributions if package
boundaries change. The builder records commands/results, manifest, changed-path
hashes, candidate/base and unrelated-path fingerprints in a stable report,
then requests a fresh-context, read-only complete WS-07 aggregate review.
The validator cannot implement fixes.

Stop on an out-of-manifest edit, unclear redaction, unsafe identifier,
unbounded cardinality, telemetry required for correctness, new external
telemetry service, changed memory/receipt semantics, or a request to add the
Chat health command. No live provider, paid endpoint, merge, push, release,
historical snapshot cleanup, MCP live refresh, resources/prompts, server
exposure or external config include is authorized here.
