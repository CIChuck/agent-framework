# Friday Langfuse implementation

---
title: Friday Langfuse implementation
initiative: friday-langfuse-integration
document_type: initiative-index
status: draft
work_state: queued
condition: normal
created: 2026-10-11
updated: 2026-10-11
next_gate: after MCP upgrade acceptance, prepare and approve the Langfuse integration contract and exact construction directive
implementation_authority: not_granted
---

## Objective and scheduling

Implement optional Langfuse export for Friday Chat using the accepted safe,
provider-neutral telemetry contract. This item carries forward the optional
TELEM-05 compatibility work from the
[telemetry initiative](../../active/friday-telemetry-rewire/README.md).
Core TELEM-01–04 remain accepted and closed; Langfuse is an optional destination.

Chuck Russell requested this queue item on2026-10-11: "Let's add Langfuse
implementation to the board. We'll queue that up and get to it after we do the
MCP upgrade." Priority5 follows the
[MCP protocol upgrade](../friday-mcp-protocol-upgrade/README.md) at priority4.
The board dependency requires that MCP initiative's acceptance before Langfuse
execution. Other tasks retain their relative priority order.

This direction authorizes the planning packet and scheduling. Product work is
not started and has no construction directive or implementation authority.
Prepare the concrete directive against the accepted post-MCP baseline when this
item becomes next; approval and a recorded start precede source generation.

## Verified starting point

Inspection at local HEAD46005353046553477417a730f05ff21ead64a00d:

- [LangfuseConfig](../../../../packages/friday-chat/src/friday_chat/config.py)
  parses enabled/public-key/secret-key/host settings. Chat's separate core
  telemetry configuration selects local debug recording or explicit injection;
  Langfuse settings do not establish export activation.
- [The legacy helper](../../../../packages/friday-llm/src/friday_llm/langfuse_integration.py)
  writes process-wide environment settings and registers LiteLLM success/failure
  callbacks. It has process-global configured state and no matching owned
  teardown contract. It must not be adopted unchanged as proof of a safe bridge.
- [Chat startup](../../../../packages/friday-chat/src/friday_chat/cli.py) and
  [runtime assembly](../../../../packages/friday-chat/src/friday_chat/runtime.py)
  do not call that helper. A configured enabled flag alone does not prove
  Langfuse trace delivery.
- [Accepted TELEM-04](../../active/friday-telemetry-rewire/closeout-TELEM-04.md)
  supplies validated events, causal execution context, bounded diagnostics and
  strict privacy. Its exact product is5c3a0e6; the acceptance record binds the
  [original independent evidence](../../../archive/completed/2026/friday-telemetry-rewire-telem-04/README.md).
  MCP may change shared inputs, so recheck and freeze the actual later baseline.

## Planned implementation scope

### 1. Integration contract and dependency decision

Decide whether the implementation is an optional TelemetryInterface-compatible
adapter/bridge, a controlled SDK export integration, or a narrowly supported
LiteLLM compatibility callback. Map the selected approach to actual installed
SDK behavior and current official Langfuse/LiteLLM documentation; pin the tested
versions, dependency extras and compatibility profile in the construction
directive. No SDK version or vendor API is ratified by this queue item.

Preserve the three-method TelemetryInterface, custom provider injection, Debug,
OpenTelemetry and Composite support. Langfuse credentials/packages must remain
unnecessary for users who leave this destination disabled. Establish one export
path per observation; do not activate both a bridge and automatic callback for
the same work without an explicit, tested duplicate-prevention contract.

### 2. Configuration and actual activation

Reconcile the existing langfuse YAML section with the selected runtime contract.
Define strict enabled/disabled behavior, endpoint and credential resolution,
invalid configuration, missing optional dependencies and visible outage handling.
Validate settings before external I/O. Keep credentials and credential fragments
out of logs, diagnostics, serialized events and review artifacts.

Wire actual Chat startup/runtime assembly and role-service construction as
required by the chosen architecture. Update shipped configuration examples and
documentation to match implemented behavior. A parseable configuration and an
SDK registration message are not sufficient acceptance evidence.

### 3. Safe correlation, events and duplicate prevention

Map the accepted safe session/turn/operation and LLM request/attempt identities
to the chosen Langfuse trace/observation model. Specify which validated LLM,
native/MCP tool, memory and persistence events are exported and what each means.
Keep reported usage/cost provenance, retries, timeout, cancellation, partial
persistence and final outcomes truthful.

Preserve causal parentage for nested/concurrent turns and deferred extraction,
including explicit absent origins. Ensure one observation and terminal outcome
per intended operation, with no double counting from callbacks, links or
Composite fan-out. Verify both outgoing payloads and the received/exported
observations rather than relying solely on Friday's own bookkeeping.

Default export must exclude prompts, responses, raw reasoning, tool arguments
or results, memory/document content, raw identifiers, paths and credentials.
Do not silently attach legacy content-bearing LiteLLM callbacks to the closed
observer. Any new raw-capture option requires a separate explicit privacy and
retention decision; it is outside this proposed scope.

### 4. Ownership, shutdown and failure isolation

Define who owns SDK clients, callback registrations and exporter resources.
Support multiple runtime instances without stealing or closing borrowed
providers or overwriting unrelated callbacks. If the selected API requires
process-wide registration, define safe registration, reuse, restoration and
teardown rather than relying on the legacy configured boolean.

Flush and close only owned resources, with bounded shutdown and cancellation
behavior. Backend outages, missing optional dependencies and export failures
must not alter application results, primary exceptions, retries, model chunk
order or tool/persistence outcomes. Diagnostics must distinguish configured,
active, degraded and failed states without exposing secrets.

### 5. Tests, migration and closeout

Use deterministic fake/in-memory export tests first. Freeze any optional local
receiver/SDK-worker effects and ownership before execution. A real-account or
remote-backend check needs separately specified credentials, endpoint, effects
and authorization; none are supplied by this board request.

Test disabled construction, enabled export, missing dependency/keys, invalid
settings, backend failure, cancellation, bounded flush, repeated startup,
multiple instances, mixed providers, concurrent/background lineage, unchanged
privacy, duplicate prevention and truthful final outcomes. Cover the real Chat
assembly path and the selected role/stream/embedding compatibility profile.

Provide migration instructions from the legacy helper and working YAML examples.
Run affected-package tests, exact changed-source Ruff/Mypy, broader regressions
proportional to scope and board/documentation checks. Expired telemetry lint
waivers do not transfer. Freeze the candidate and require a fresh-context
independent review before proposing completion; maintainer acceptance follows.

## Acceptance criteria

| Criterion | Required evidence |
| --- | --- |
| LF-01: optional destination | Disabled/default operation needs no Langfuse package, credentials, callbacks or connection; other injected providers remain supported. |
| LF-02: actual activation | Valid enabled configuration reaches the selected exporter through real Chat assembly; invalid/missing settings and failures have explicit safe diagnostics. |
| LF-03: truthful safe export | Received/exported observations carry correct accepted correlation and outcomes; planted content/credential sentinels are absent; no duplicate spans or terminal contributions. |
| LF-04: lifecycle | Multiple instances, cancellation, export failure and shutdown preserve application/borrowed-provider behavior; owned callbacks/resources clean up without leaks. |
| LF-05: delivery proof and compatibility | A pinned supported SDK/profile has independent export/receiver evidence; examples/migration match reality; all directive checks pass and a fresh validator returns VERIFIED. |

## Boundaries and checkpoint

This item does not authorize MCP implementation, core telemetry reopening,
headless RuntimeKernel migration, general remote OTLP assembly, OTel Meter wiring,
diagnostic persistence, dependency installation, credentials, live or paid calls,
push/merge/release, deployment or publication. Bound exact product paths and
effects in a separately approved directive after MCP acceptance.

2026-10-11: queued after MCP per explicit maintainer direction. Planning-only
scope: this packet, board/dashboard and telemetry scheduling index/log metadata.
Runtime behavior cannot change. Verify links, board order/dependency and unchanged
accepted controls/source/unrelated work. No product code or acceptance evidence
was modified by this queue addition.
