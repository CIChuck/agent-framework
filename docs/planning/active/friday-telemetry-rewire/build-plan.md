# Friday-telemetry-rewire: build plan

**Status:** Direction and first-slice preparation approved by the maintainer,
2026-10-04; bounded construction directives require their own approval.
**Objective:** Connect Friday Chat to the existing provider-neutral telemetry
contract so a turn is observable from startup through model calls, tools,
memory, and persistence. Local diagnostics and exporter adapters should share
the same safe events and correlation. No particular vendor is required.

## What the earlier `friday.py` launcher actually wired

The following is a source inventory, not a claim that the old system had a
complete production trace. Paths and line numbers refer to the current checkout.

| Capability | Earlier implementation and evidence | Practical limit |
| --- | --- | --- |
| Startup logging | Read `logging.level`, configured stdlib logging early with `force=True`, and applied `tools_debug` before tool loading (`tests/integration/memory/friday.py:7127-7156`). | Console log levels and tool debug messages were independent of a trace or durable log pipeline. |
| Langfuse LLM export | Read the `langfuse` config and called `configure_langfuse(langfuse_config)` before normal chat LLM construction (`friday.py:7137,7355-7375`). The helper sets `LANGFUSE_*` values and registers LiteLLM success/failure callbacks (`packages/friday-llm/src/friday_llm/langfuse_integration.py:31-105`). | This was a process-wide LiteLLM callback, not a common Friday trace. It depended on credentials, the optional package, and callback delivery. The launcher did not prove an exported trace was received. |
| Memory events | Constructed `DebugTelemetryRecorder` and passed it to `MemoryController` (`friday.py:7624-7639`). | The recorder keeps events and spans in process memory; the launcher did not pass that recorder to the primary or extraction `LiteLLMService` constructors (`friday.py:7367-7398`) or export it. |
| Context diagnostics | Estimated system, history, user, and total tokens, stored actual prompt/completion counts in `context_history`, and exposed `/context --debug`, `/debug`, and `/debug-budget` (`friday.py:1319-1379,1595-1707,1864-1873,1914-1970`). | Estimates and actual provider usage had different meanings; the history lived in process memory. |
| Turn and tool accounting | Timed initialization, budget calculation, context assembly, prompt formatting, and the LLM call; accumulated usage across a multi-call tool loop; retained tool calls/results and final turn timing (`friday.py:6025-6141,6599-6608,6664-6670,6725-6749,6883-6907`). | Many stages were debug log lines rather than structured, correlated telemetry. Streaming explicitly lacked actual token counts (`friday.py:6312-6434`). |
| Durable inspection | Persisted an `InteractionTurn` with tool calls/results, timing, token counts, model metadata, and optional raw prompt/response in SQLite (`friday.py:6149-6208,7537-7546`). | Raw capture was a separate privacy-sensitive option; transcript storage was not an event or trace exporter. |
| Reasoning-model continuity | Copied provider `reasoning_content` into the assistant tool-call message for the next call (`friday.py:6765-6786`). | It had no safe diagnostic proving preservation per follow-up request; raw reasoning must not become a telemetry payload. |

## Existing telemetry adapter: verified capabilities and limits

Friday has an abstract `TelemetryInterface` with `capture_event`, `start_span`,
and `end_span` (`packages/friday-telemetry/src/friday_telemetry/interface.py`).
The package exports `DebugTelemetryRecorder`, `OpenTelemetryProvider`, and
`CompositeProvider` (`friday_telemetry/__init__.py:85-116`). Components can
receive any implementation through constructor injection. The OTel adapter
supports an OTLP endpoint or console exporter; an OTLP collector can route to
different backends. The composite can fan out to several adapters. This is the
intended seam for Friday Chat, rather than a Langfuse-specific application
path.

This flexibility is currently **programmatic**, not fully driven by a runtime
provider registry. The headless DI assembly chooses a debug recorder when
`debug_mode` is true, otherwise an OTel provider when `telemetry_enabled` is
true, otherwise `None` (`packages/friday-runtime/src/friday_runtime/di.py:151-164`).
It does not select an arbitrary `TelemetryInterface` implementation from YAML.
`TelemetryConfig` describes sampling, headers, batch settings, and export
options (`friday_telemetry/config.py`), but the headless DI branch currently
passes only service name and endpoint to `OpenTelemetryProvider`. Friday Chat
accepts an injected interface but creates none in its CLI. Preserve the
ability to inject a custom implementation in tests and embedding applications.

The composite is not yet correct for spans: `start_span` returns the first
provider's ID, but `end_span` passes that same ID to every provider, even though
later providers generated different IDs
(`friday_telemetry/providers/composite.py:67-100`). A two-recorder probe in
this checkout ended the first span and left the second open. The existing
test checks only that both spans were created
(`friday_telemetry/tests_telemetry/test_providers.py:155-171`). This must be
fixed before claiming reliable multi-sink traces.

Langfuse sits beside this adapter today: `configure_langfuse` registers a
process-wide LiteLLM callback (`packages/friday-llm/src/friday_llm/langfuse_integration.py:31-105`),
not a `TelemetryInterface` provider. Restoring compatibility with that callback
is optional follow-up work. It must not determine the event contract or require
Friday Chat to depend on a Langfuse account.

## Current Friday Chat baseline and gaps

1. **Legacy Langfuse compatibility is configured but not activated.** `packages/friday-chat/config.example.yaml:674-678`
   enables Langfuse and names environment placeholders. The example launcher
   sources `scripts/source-friday-chat-example-env.sh` before executing the CLI
   (`scripts/run-friday-chat-example.sh:23-33`). Friday Chat parses the
   `LangfuseConfig` (`packages/friday-chat/src/friday_chat/config.py:592-598`),
   but its CLI startup (`friday_chat/cli.py:99-130`) never calls
   `configure_langfuse`. The only application call found is in the earlier
   `friday.py` launcher. This gap does not define the core telemetry architecture;
   the packet must not expose local credential values.
2. **No owned Chat telemetry assembly.** `build_runtime` accepts an optional
   telemetry object (`friday_chat/runtime.py:1205-1231`) and passes it to the MCP
   adapter (`runtime.py:1394-1403`), but the CLI provides none and the real
   runtime constructs Chat LLM, embedding, and memory services without it
   (`runtime.py:1379-1388`; `friday_chat/adapters.py:1598-1705,1754-1761`).
   Keep the accepted MCP redaction and diagnostic contracts intact.
3. **Typed Chat misses existing LLM metrics.** Friday Chat calls the typed
   `chat_completion_request` path (`adapters.py:154-175`). That method invokes
   `_call_with_retry` without the completion tracker used by legacy
   `chat_completion` (`packages/friday-llm/src/friday_llm/service.py:399-429,
   484-513`). Its Langfuse metadata also receives no conversation context.
4. **Trace and fan-out semantics need repair.** The OpenTelemetry provider records events
   only on the current span, while `start_span` creates a span without making
   it current and ignores its supplied parent ID
   (`packages/friday-telemetry/src/friday_telemetry/providers/otel.py:96-130`).
   Headless runtime telemetry defaults off and its shutdown has no exporter
   flush (`packages/friday-runtime/src/friday_runtime/config.py:654-657`,
   `friday_runtime/di.py:135-164`). Verify current exporter behavior before
   calling it end-to-end tracing. The composite span-ID mismatch described
   above also prevents correct multi-provider end spans.
5. **Local records are useful but incomplete as a timeline.** Friday Chat has
   `/debug`, `/debug-budget`, `/timing`, `/tool-budget`, and transcript commands
   (`friday_chat/commands/registry.py:1887-1894,1965-1977,2165-2173`). It
   retains an immutable selection/budget snapshot
   (`friday_chat/tools/selection.py:57-78`) and turn phase timing
   (`friday_chat/turns/models.py:42-58`). Its transcript records model,
   latency, calls/results, and optional raw context, but not a unified
   per-attempt trace or the old full per-turn token fields
   (`friday_chat/adapters.py:1185-1243`, `turns/processor.py:604-652`).
6. **Privacy and reliability boundaries differ.** MCP telemetry uses typed,
   allowlisted fields and opaque peer references
   (`packages/friday-telemetry/src/friday_telemetry/helpers/mcp.py:18-52`).
   General LLM telemetry can emit an exception message
   (`friday_telemetry/helpers/llm.py:652-667`). The example sets
   `transcript.capture_raw_prompts: true`, whereas the type default is false
   (`config.example.yaml:369-371`, `friday_chat/config.py:491-495`). Decide
   redaction, retention, and destination separately for local transcripts,
   logs, OTel, and Langfuse.

## Proposed target contract

The maintainer approved this provider-neutral direction on 2026-10-04.
The specific first-slice choices are now expressed in
[telemetry-contract.md](telemetry-contract.md) and
[CD-001](directives/CD-001-local-telemetry-assembly.md), both approved with CD-001 on 2026-10-05. The long-term criteria below remain initiative-level
criteria, not claims that the first local slice completes all observability.

- **Provider-neutral runtime assembly.** Friday Chat owns one
  `TelemetryInterface` lifetime and injects it before any LLM, embedding,
  memory, native-tool, or MCP client can make a call. Preserve custom provider
  injection; support debug, OTel/OTLP, and correctly composed adapters through
  typed, validated configuration or an explicit factory interface. Make
  disabled, configured, active, and failed states inspectable without secrets.
  Do not make Langfuse credentials or its callback a prerequisite.
- **End-to-end identity.** Carry safe session, turn, LLM request/attempt, tool
  call, and persistence identifiers across Chat and headless paths. A turn
  timeline must identify start, selected tool-set identity and rejection
  reasons, model/role, retries and timeouts, tool outcomes, memory operations,
  and transcript outcome. Each event must have a declared source and meaning.
- **Consistent LLM metrics.** Both typed and legacy completions, streaming,
  embeddings, and configured role services should report provider/model,
  duration, first-token time when available, actual versus estimated tokens,
  reasoning-token count when reported, cost estimate provenance, retry count,
  finish reason, and categorized failure. Missing provider usage is `unknown`,
  never silently zero. For multi-turn tool calls, emit only a boolean/count
  indicating whether required reasoning content was preserved in outbound
  assistant history; never export the reasoning text.
- **Tool and memory outcomes.** Reuse accepted MCP categorical events and
  diagnostics. Give native tools, retrieval, extraction, ingestion, and
  persistence the same correlation and outcome vocabulary without exporting
  arguments, results, prompt text, or memory content by default. Coordinate
  future authorization-decision events with `tool-governance` rather than
  treating telemetry as a permission system.
- **Export and local inspection.** Repair OTel parent/current-span semantics,
  composite span-ID mapping, reliable event delivery, error recording, and
  shutdown flush. Verify a fake provider and an OTLP test collector without
  vendor credentials. Keep a concise local per-turn diagnostic path when
  remote exporters are disabled. If Langfuse compatibility is retained, bridge
  it explicitly as an optional sink or callback with one correlation contract,
  no duplicate events, and clear process-wide lifecycle ownership.
- **Privacy and operations.** Define field allowlists, redaction, bounded
  cardinality, retention, sampling, secure defaults for raw capture, and
  exporter failure isolation. Provide metrics suitable for latency, failure,
  retry, tool-budget, MCP availability, and ingestion dashboards; specify
  ownership of any counters/histograms and avoid double counting events.

## Recommended implementation slices after approval

1. Ratify provider-neutral configuration/factory semantics, event schema,
   privacy rules, and the cross-package identity contract. Inventory every LLM
   service construction path and existing telemetry hook before editing code.
2. Repair the shared provider contract: composite span mapping, OTel context
   and event semantics, exporter lifecycle, and two-provider test coverage.
3. Have Friday Chat assemble or accept a selected `TelemetryInterface` and
   inject it into Chat LLM, embedding, memory, native tool, and MCP paths.
   Instrument typed completions and propagate identities through retries and
   turns; prove legacy and typed paths produce equivalent safe metrics.
4. Add local incident inspection and exported operational metrics. Validate
   privacy, exporter failure, concurrency, and recovery before claiming
   production observability.
5. Reconcile the existing `langfuse` YAML and LiteLLM callback as an optional
   compatibility integration. Enable it only through a separately tested
   adapter/bridge decision; it cannot be the core acceptance gate.

The [tactical plan](tactical-plan.md) makes this ordering concrete. Proposed
CD-001 establishes local provider-neutral wiring, lifecycle diagnostics, and
correct composite span mapping. OTel context/export lifecycle repairs precede
remote exporter activation in a later directive. Existing LLM/memory event
hooks receive the common observer only after their payload and correlation
contracts are bounded; first-slice wiring must not forward raw legacy events.

## Acceptance criteria for the approved design

- Friday Chat's real CLI path delivers the same allowlisted event and span
  semantics to two different injected `TelemetryInterface` implementations;
  neither requires vendor credentials. Disabled telemetry remains explicit.
- Composite fan-out ends the corresponding span in every child provider and
  preserves parent-child relationships. OTel spans/events reach a test
  collector; shutdown flushes or reports an export failure without corrupting
  Friday's operation.
- A typed Kimi/tool-loop test emits per-request usage/outcome events and safe
  reasoning-presence evidence for each follow-up, without raw reasoning or
  tool arguments/results in exporter payloads.
- One session/turn ID links model attempts, native and MCP calls, memory work,
  and final transcript status. Retries, timeout, cancellation, and persistence
  failure remain distinguishable; no success event precedes a failed commit.
- Local diagnostics work with every exporter disabled. Missing optional
  dependencies, malformed configuration, unavailable exporters, and an
  interrupted session have explicit, testable behavior.
- Tests prove content-bearing secrets, prompts, raw reasoning, schemas,
  arguments, tool results, and memory text do not cross the default exporter
  boundary. Raw transcript capture remains an explicit local choice.

## Decisions tracked by the contract and later gates

1. What typed configuration or factory selects one or several
   `TelemetryInterface` implementations at runtime while allowing custom
   injected adapters? Which current `TelemetryConfig` fields are supported?
2. Which event and metric fields may leave the host, and what are the default
   retention and sampling rules for local and remote destinations?
3. Should exporter activation failure stop startup when enabled, or start in a
   visible degraded state? Distinguish invalid configuration from outage.
4. Should the existing Langfuse callback remain as optional compatibility,
   become an adapter fed by Friday telemetry, or be deprecated? This decision
   must not delay the provider-neutral Friday Chat rewire.

## Boundaries

Approval authorizes preparation on the dedicated branch. Product code remains
subject to an approved construction directive and recorded start transition.
Credential disclosure, live exporter connections, changes to existing `.friday`
state, and tool-governance authorization changes remain outside this plan.
The board remains the authority for state and priority.

## Python support amendment A04 — 2026-10-05

The maintainer approved Python >=3.13.4 for the workspace ("Make it happen.").
[REM-003](remediation/REM-003-python-minimum-directive.md) binds the exact
metadata/setup migration and supersedes the old Python 3.10 runtime obligation.
Telemetry source behavior and remaining AC-06 repository failures are unchanged.

## Verification closeout amendment A05 — 2026-10-05

Maintainer "I approve both REM-004 and WVR-002." authorizes the exact
[REM-004](remediation/REM-004-verification-closeout-directive.md) fixes/checks and
separately the precise archival lint exception. This supersedes prior freeze/
three-listener restrictions only within that inventory. Local telemetry contracts,
dependency pins, no-live-provider boundary and later-unit gates remain unchanged.
Fresh approved-authority readiness precedes separate remediation and independent
product delta/aggregate review. No completion or acceptance is granted.
