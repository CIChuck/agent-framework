# MCP-WS-07 Readiness Checkpoint

Date: 2026-09-29
Preparation HEAD: `e98411825c2f2275f43d45762a656e8d7b85a9b0`
Branch: `feature/friday-mcp-ws06-memory`
Status: Planning reconciled; **bounded implementation approval pending**
Phase/state: `planning` / `not_ready`

## Authority and source findings

WS-00 through WS-06 are independently verified and explicitly accepted.
WS-06 acceptance was recorded at `e984118` against frozen product candidate
`820e252c496712264ebf767404c1e054f025d53a` and complete
[VAL-015](../validation/VAL-015-report.md). The maintainer's subsequent
"i accept - continue" advanced this planning gate; it did not approve WS-07
product edits. Board `validate` passes 23 tasks; `next` and `show friday-mcp`
select reconciliation and separate bounded approval. The controlling
[directive](../directives/ws-07-telemetry-diagnostics-health.md) is a proposal.

| Inspected boundary | Implication for WS-07 |
| --- | --- |
| `friday_runtime.mcp_loading.RuntimeMCPProvider` | Already owns connection/list-tools/disconnect, public typed discovery/diagnostics/lifecycle/registration decisions and retained last-attempt evidence. Emit from this owner; do not bypass it or rebuild diagnostics from logs. |
| `friday_runtime.di.DIContainer` | Creates optional telemetry before MCP provider but does not pass it to the provider. Existing opt-in path can supply events without a new config or dependency. |
| `friday_mcp.client.adapter.MCPToolWrapper.execute` | Headless and Chat registry calls share this RPC boundary. A narrow optional observer covers both; the MCP package must not depend on Telemetry. |
| `friday_chat.tools.mcp.MCPChatRegistry` | Has a public provider and checked per-call record/provenance after result policy. It can distinguish RPC outcome from sanitized/truncated/blocked output. |
| `friday_chat.tools.selection.ToolBudgetSnapshot`, `turns.processor` | Accepted WS-04 already records rejection reasons and budget numbers; instrumentation should consume that snapshot, not select tools again. |
| `friday_chat.memory_mcp.persist_mcp_interaction` | Accepted WS-06 optional ingestion stages, verifies immutable receipt and may leave pending records. Events must distinguish denied, receipt committed, pending and published without altering retries. |
| `friday_telemetry.interface.TelemetryInterface` and current models | Existing `capture_event(name, data)` and Debug/OTel implementations support opt-in emission. Typed closed payloads and an allowlist are required before sending arbitrary data to exporters. |
| `friday_chat.commands.registry` | Adding a user command would expand the CLI/output contract and exact manifest. Existing provider state is inspectable through public Python APIs, so this first pass proposes to defer the command. |

The old draft granted whole source/test directories in four packages and
included an obsolete "do not enable memory ingestion" line. WS-06 now supports
opt-in ingestion; WS-07 must preserve its default-disabled policy and accepted
behavior. The reconciled directive binds exact source/test paths, the event
schema, owner/observer architecture, redaction negatives, package checks,
stop conditions and fresh independent review.

## Proposed decision and execution gate

Approve the [reconciled directive](../directives/ws-07-telemetry-diagnostics-health.md)
for telemetry and structured diagnostics **with the Chat health command
deferred**. This is the explicit `MCP-07-04/05` first-pass decision. If a
command is wanted now, revise and review its exact source/test/output
manifest before approval; no command files are currently authorized.

Upon explicit bounded approval, pin the planning commit as base, create a
dedicated `feature/friday-mcp-ws07-telemetry` branch, record approval/start,
and implement only the directive manifest. Freeze a stable candidate and
dispatch a new fresh-context, read-only validator for the complete WS-07
aggregate. A VERIFIED result still requires separate maintainer acceptance.
WS-08, initiative aggregate/pre-merge review and delivery remain separate.

This checkpoint is source-based planning, not implementation or a validation
verdict. No product code, runtime state, external MCP service, credential,
paid endpoint or delivery operation was touched. The unrelated modified
`.DS_Store`, deleted `family-tree.md`, `docker-bench-security/`, Chat config
backup and Sandbox audit Dockerfile were preserved.
