---
title: Advanced integration and operations
description: Model routing, adapters, performance, telemetry ownership, execution backends and deployment design.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: guide
---

# Advanced integration and operations

This guide covers integration decisions beyond the first Chat session. The
patterns describe application responsibilities around shipped components;
they do not introduce an automatic distributed runtime, hosted service or
deployment certification.

## Route models by service role

Use canonical model-library profiles and role bindings to separate primary chat,
extraction, passage routing, compaction, maintenance and embeddings. A small local
model may suit one role and fail another; measure the actual prompt/output
contract before changing it. [Configuration](10-configuration.md) has a complete
multi-role example.

Local chat alone does not establish local processing. Trace the destinations
of embedding calls, extraction/synthesis/judge services, document tools, speech,
MCP peers, logging and exporters. A fallback route can have a different data
destination and control support. Keep the exact model revision with evaluation
results and persistent embedding collections.

The shipped normalized control profile is specifically LM Studio's
OpenAI-compatible Chat Completions route with Qwen3.8 identity. Other LiteLLM
routes are compatibility surfaces. Check reasoning/sampling support before
moving a profile; do not silently drop unsupported controls.

## Typed model requests and streaming

This **offline Python example** constructs a request without a provider:

```python
from friday_llm import ChatCompletionRequest, GenerationOverrides, SamplingConfig

request = ChatCompletionRequest(
    messages=({"role": "user", "content": "Summarize the supplied source."},),
    overrides=GenerationOverrides(sampling=SamplingConfig(temperature=0.3)),
)
print(request.overrides.sampling.temperature)
```

Expected output: `0.3`. `chat_completion_request()` performs a typed completion;
`chat_completion_events()` yields distinct text, reasoning, tool, usage and
finish events. Text-only compatibility streaming is a different interface.
Do not append reasoning deltas to the end-user response or assume every
provider exposes the same event sequence.

Omitted typed overrides inherit defaults; explicit `None` clears a default.
Capture usage as reported, with unknown distinct from zero. Built-in cost rates
are historical estimates, not a current pricing catalog or invoice. Configure
appropriate rates if your application displays monetary estimates.

LiteLLM clients are process-shared. `close_litellm_async_clients()` is a
process-shutdown operation after all users are quiescent, not per-request
cleanup for a borrowed service. See [the LLM package](../../packages/friday-llm/README.md)
for a complete live local-server example.

## Implement an adapter deliberately

Read the actual Core protocol and a current implementation first. Match async
behavior, argument/result shapes, metadata and failure semantics, not just
method names. Define which resources your adapter owns and how callers stop,
flush or snapshot them.

| Adapter | Contract details to preserve |
| --- | --- |
| Model | Message/tool/result pairing, streaming events, cancellation and supported controls |
| Embedding | Stable dimensions/model identity, batch shape, missing/failed result behavior |
| Vector | Metadata filters, query/result shape, persistence and mutation/snapshot support |
| Graph | Node/edge identity, provenance, traversal and access-tracking semantics |
| Transcript | Session/turn identity, query ordering, snapshot consistency and privacy |
| Tool | Bounded validated inputs, exact schema, side effects and result/error contract |
| Telemetry | Borrowed ownership, event schema, bounded identifiers and truthful lifecycle outcomes |

The [SimpleVectorStore example](04-adaptive-memory.md#semantic-search-without-a-provider)
demonstrates the minimal embedding shape. It does not implement reranking,
hybrid search or durable recovery. A replacement backend needs explicit tests
for the capabilities your application depends on.

## Performance measurement

Measure stages separately: configuration/startup, context retrieval, formatting,
model first token/completion, each tool call, persistence and background work.
Use fixed synthetic workloads and record model revisions, embedding dimensions,
tool sets, state size and budgets. The earlier guides' latency targets and
percentage cost savings were not measured release guarantees.

Tune one mechanism at a time:

1. Reduce unnecessary tool schemas and oversized results before shrinking useful
   memory. Inspect `/tool-budget` and the actual formatted prompt.
2. Align priming retrieval with supporting-context limits; retrieving more than
   can be formatted wastes latency and embedding/query work.
3. Bound prior-session and current-session history; retained older turns compete
   with new evidence.
4. Use explicit compaction and maintenance configuration. They can call models
   and write stores, so assess quality and latency as well as token reduction.
5. Test cold startup and shutdown, including incomplete exporter or store work.

`memory.cache` configures supported prompt-cache behavior; it is not a generic
response cache or a guarantee that the selected provider honors cache controls.
MCP discovery's `ttlMs: 0`/private scope is not a cross-call result cache.

## Telemetry ownership and exporters

Telemetry implementations live in `friday-framework-telemetry`; Core preserves
compatibility exports. Consumers receive `TelemetryInterface`. The application
that creates a provider owns its lifecycle; a consumer must not close a borrowed
provider or register a global tracer on its behalf.

This **offline Python example** constructs and flushes an owned debug handle:

```python
from friday_telemetry import TelemetryFactoryConfig, create_telemetry

with create_telemetry(TelemetryFactoryConfig(provider="debug")) as owned:
    owned.telemetry.capture_event("example.completed", {"count": 1})
    result = owned.flush(1000)
    print(result.status)
```

Expected output: `success`. The factory defaults to disabled when no provider
is selected. The low-level debug recorder is unbounded and stores raw caller
data; it is for controlled debugging/tests. Chat's bounded local observation
layer is a different facility, disabled by default.

Optional `friday-framework-telemetry[otel]==0.1.0a3` supplies SDK/exporter
dependencies. Programmatic `TelemetryFactoryConfig(provider="otel",
otel=OTelConfig(...))` selects console or explicitly configured OTLP/gRPC.
The validated SDK/API profile is 1.39.1; metadata lower bounds do not establish
every-version compatibility.

Remote OTLP requires verified TLS; insecure collection is limited to an
explicit literal-loopback destination. The owned factory rejects inherited
OTEL/GRPC/proxy/certificate overrides and does not supply custom credential
headers, an HTTP exporter, automatic instrumentation or an ambient context
bridge. Configure through the actual [factory models](../../packages/friday-telemetry/src/friday_telemetry/config.py),
not arbitrary copied exporter environment settings.

`snapshot()`, `flush()` and `shutdown()` report categorical status, failures,
timeouts and incomplete ownership. Default/maximum lifecycle budgets are five
seconds. A flush attempt is not proof of downstream ingestion. Retain ownership
of unsettled work and follow the reported lifecycle rather than creating
replacement exporters blindly.

`CompositeProvider` captures child membership/span IDs at span start and
attempts fan-out before reporting errors. Completed public IDs remain reserved
for the composite's lifetime; define that lifetime instead of describing it as
having constant memory use across unlimited spans.

Closed LLM/MCP/execution event families exclude raw prompts, responses, reasoning,
schemas, tool payloads, paths, credentials and memory contents. Generic event
payloads, raw transcripts and legacy LLM/memory helpers are outside that
guarantee. Do not use an event recorder as a redactor.

The provider-neutral **Langfuse integration remains queued**. Legacy callback
configuration and the `langfuse` extra do not complete that implementation.
Likewise, Chat's current local diagnostics and the headless Runtime's adoption
of newer factory/correlation paths have separate integration boundaries.

## Execution backends

Friday Sandbox exposes Docker, subprocess and mock backend classes. The helper
functions return **classes**, which you instantiate. This **offline Python
example** tests the mock contract and never executes the supplied string:

```python
import asyncio
from friday_sandbox import ExecutionResult, get_mock_sandbox

async def main() -> None:
    sandbox = get_mock_sandbox()()
    sandbox.set_response(ExecutionResult(stdout="fixture result", exit_code=0))
    result = await sandbox.execute("print('this is not executed')")
    print(result.stdout)

asyncio.run(main())
```

Expected output: `fixture result`. It is not evidence of real code isolation.
Subprocess runs with host-process privileges. Docker requires a configured
SDK/daemon/image; mounts, network, capabilities and daemon access determine
the boundary. Workspace TTL/cleanup manages files and does not create an OS
security boundary. See [the Sandbox package](../../packages/friday-sandbox/README.md).

## Deployment profiles and durable state

Headless `deployment_profile` values `local`, `container` and `cloud` choose
documented path defaults/validation policy. They do not deploy containers,
create Kubernetes resources or install a hosted service.

Separate installation, workspace, runtime data and cache roots. Persist stores,
transcripts, access-buffer journals and recovery manifests outside disposable
environments. Use a single clear writer/maintenance ownership model; coordinate
quiescence across background work before backup or restore.

For multiple processes, design authentication, routing, queueing, durable state,
store concurrency, lease recovery and idempotency explicitly. Sharing a JSON
graph directory or SQLite database across arbitrary replicas is not a supported
distributed-memory architecture by implication. Serverless handlers also need
an explicit external persistence/lifecycle design.

## MCP lifecycle and trust

Modern clients retain generation-bound catalogs and captured output schemas.
Manual refresh can invalidate wrappers; integrated Runtime/Chat rediscover on
public stop/start. A call already issued settles once against its captured
definition. No refresh, recovery or timeout authorizes replay of an uncertain
mutation. Failed cleanup retains owners and blocks unsafe replacement.

HTTPS admission validates every DNS candidate and the actual numeric connection
under per-peer policy. No proxy, redirect or TLS-relaxation shortcut is implied
by a generic web client setting. Server Host/Origin/bearer/TLS policy is a
separate responsibility. See [MCP client](17-mcp-client.md), [server](18-mcp-server.md)
and [dated migration matrix](19-mcp-migration.md).

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)
