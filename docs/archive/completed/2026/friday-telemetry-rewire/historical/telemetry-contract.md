# Telemetry contract: first local slice

Status: Approved with CD-001 by the maintainer on 2026-10-05.
Authority: [build plan](build-plan.md). Later exporter and measurement contracts
must be specified by separate directives before implementation.

## Configuration and provider ownership

Add a strict Chat `telemetry` section with `enabled: false` and
`provider: debug` defaults. The only YAML provider in CD-001 is `debug`.
Reject unsupported providers, unknown fields, and malformed values with safe
configuration errors. Do not reinterpret the existing `langfuse` section or
change the shared `TelemetryConfig` defaults. Do not add YAML class imports,
entry-point discovery, exporter credentials, endpoints, headers, or environment
switches in this slice.

When enabled, assemble a local observer before Chat service construction.
Retain it on `FridayRuntime`; the real CLI uses the same `build_runtime` path.
`build_runtime(telemetry=...)` remains an explicit caller-owned override, even
when YAML telemetry is disabled, preserving the existing embedding API.
Wrap custom providers in the same safe event boundary as the local provider.
Never shut down a caller-owned injected provider. A composite injected by a
caller is supported without requiring a YAML composite factory.

Expose immutable diagnostics identifying configuration, selected provider kind
(`disabled`, `debug`, or `injected`), active/failed state, and categorical
delivery failures. Do not identify a failed sink as healthy. Keep local
diagnostics available when an injected provider fails. A sink exception does
not change Chat startup, shutdown, tool, or memory outcomes.

## First-slice events and local inspection

Use typed, immutable events with a closed event-name set for runtime ready,
application start, application stop, and telemetry delivery failure. Serialize
only opaque session references, bounded event sequence numbers, categorical
outcomes/reasons, and nonnegative counts. No user-supplied text becomes an event
name or reason. A startup event means runtime assembly succeeded; it does not
mean an LLM request, MCP discovery, memory write, or transcript commit succeeded.
Application stop reflects completion or failure of existing cleanup, including
cancellation; do not emit successful cleanup before cleanup finishes.

Keep the newest 256 diagnostic events locally and report dropped-event counts.
Keep failure counts after individual failure events age out. Expose a public
typed diagnostic snapshot on the runtime observer and a concise CLI startup
status. No new slash command is needed. Observations must not include prompts,
responses, reasoning, memory text, arguments, results, schemas, full config,
credentials, exception messages, storage paths, or raw session identifiers.

Preserve existing MCP event meanings and redaction. Pass MCP events through a
strict validation of the existing public `MCPEvent` contract; drop unrecognized
or invalid events visibly with a categorical count. Do not forward arbitrary
legacy LLM/memory events, silently discard their fields under a success label,
or claim those paths are instrumented. Their safe contracts and common
correlation are subsequent work.

## Composite spans

Fix `CompositeProvider` to retain the child span ID returned by each provider,
translate a composite parent into each child's parent ID, and end the
corresponding child span exactly once. Keep the first provider's span ID as the
public composite ID when it has never been published by this composite
instance. Otherwise return a fresh opaque composite-owned ID and preserve every
child mapping. Reserve published IDs for the instance lifetime, even after end,
so a stale end cannot close a later span. This collision amendment is approved
with REM-001/CD-001 A02 on 2026-10-05. An empty composite still returns a
nonempty ID and safely ends it.

Pin span ownership at start: removing a provider must not strand its open span;
adding a provider later must not send it an unrelated end. Ending an unknown or
already ended ID is a no-op. A child added after a parent started has no mapped
parent and receives `None` for that parent. Copy event/end dictionaries per sink
to prevent one provider mutating another's payload.

First-slice composite failures are best-effort: attempt every sink, retain
which child spans actually opened, clean up each recorded child, and raise a
content-free aggregated failure after fan-out if any child fails. The Chat safe
boundary catches this failure and exposes categorical degraded diagnostics.
Do not retain arbitrary exceptions or exception messages in exported data.

## Deferred decisions

Remote OTel assembly, its parent/current-context semantics, flush/shutdown,
exporter failure policy, sampling, destination retention, and vendor bridges
require later bounded contracts. No exporter is activated by CD-001. Typed and
legacy LLM metrics, usage/cost provenance, tool and memory instrumentation,
per-turn correlation, native-tool selection diagnostics, and operational
dashboards remain later units. Raw transcript capture remains governed by its
existing independent configuration; no existing data or capture setting changes.
