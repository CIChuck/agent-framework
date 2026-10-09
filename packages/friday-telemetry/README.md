# Friday Framework Telemetry

Telemetry package for the Friday Framework.

This package provides telemetry records, interfaces, provider helpers, and
debug/OpenTelemetry-oriented instrumentation support used across Friday
packages.

## Install

```bash
pip install friday-framework-telemetry
```

## Import Package

```python
import friday_telemetry
```

## License

MIT

### Composite span ownership

`CompositeProvider` retains each child's own span ID and translates nested
parent IDs per provider. A first child's ID remains public when this composite
has never published it. Reused child IDs and empty composites receive a fresh
opaque composite-owned ID; each child still receives its own ID on end.
Membership is captured when a span starts, so
removing a provider does not strand its span and adding one does not send it a
foreign end. A newly added child receives no parent for a span it never started.
Unknown or repeated ends are no-ops. Event and end payloads are copied per sink.

Published IDs remain reserved for the composite instance's lifetime, including
after a span ends. This prevents a stale end from closing a later span when a
replacement provider reuses an ID. Reservation retains only strings, growing
with the total number of published spans; completed child/provider references
and payloads are released. Use composite instances with a defined runtime
lifetime when cumulative ID retention matters.

Fan-out attempts every child even if another fails, then raises a content-free
aggregate delivery error. A partially failed start closes the children that
opened before raising. An end is attempted once per recorded child; failure is
reported rather than silently treated as success. Exporter retry, OTel context,
and lifecycle behavior are separate contracts.

## Owned programmatic telemetry

```python
from friday_telemetry import OTelConfig, TelemetryFactoryConfig, create_telemetry

settings = TelemetryFactoryConfig(
    provider="otel",
    otel=OTelConfig(exporter="console", service_name="example"),
)
with create_telemetry(settings) as handle:
    span = handle.telemetry.start_span("example.operation")
    handle.telemetry.capture_event("example.event", {"count": 1, "complete": True})
    handle.telemetry.end_span(span, {"outcome": "succeeded"})
    result = handle.flush(1000)
```

The additive factory defaults to `disabled`; `debug` creates a local recorder.
Both avoid optional SDK imports, workers and channels. Existing `TelemetryConfig`
and default-disabled Chat configuration retain their defaults. This factory is a
programmatic API; Chat YAML/CLI and headless DI do not adopt it automatically.
Embedding callers may inject `handle.telemetry` into `build_runtime(telemetry=...)`
and must close the handle themselves. Chat never closes a borrowed provider.

`OpenTelemetryProvider(service_name, endpoint=None)` preserves its constructor.
Each provider now owns its SDK tracer and explicitly releases resources through
`shutdown(timeout_millis=5000)`. No global tracer is registered and no SDK atexit
handler owns the console stream. A service-only constructor without SDK support
remains a no-op with unavailable diagnostics; explicit factory OTel or endpoint
selection fails with a content-free `TelemetryInitializationError`. A missing
requested exporter never silently falls back to console. Invalid settings fail
before channel construction; an outage after construction is visible in lifecycle
results and retained counters.

The validated optional SDK/API/encoder boundary is **1.39.1**, with grpcio 1.67.1
and protobuf 6.33.2 in this verification environment. Older versions permitted by
package metadata are not a compatibility claim; incompatible SDK versions fail
explicitly. No dependency update or HTTP exporter is included in this change.

Parent IDs must identify a live span in the same provider. Omitted parents use the
caller's provider-local task/thread context; otherwise a root uses an empty SDK
context. This deliberately avoids the application's ambient SDK span. Standalone
events create one ended event span. Context stacks are immutable, with stale entries
pruned after out-of-order or cross-context end; unknown/repeated ends are no-ops.
At most 128 spans may remain active. Shutdown marks outstanding spans cancelled.
Native auto-instrumentation and ambient context bridges are deferred.

Generic names and keys use `[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}`. Each attribute set
contains at most 64 scalars: booleans, signed 64-bit integers, finite floats, or
strings of at most 1024 UTF-8 bytes. Invalid Unicode, nested objects and unsupported
values are rejected without calling `str` or SDK warning logs. Arbitrary scalar
strings supplied by callers are not promised content-safe. Chat injection retains
its accepted closed observer/MCP payload boundary; raw LLM/memory hooks stay deferred.

`snapshot()`, `flush()` and `shutdown()` expose immutable categorical results and
cumulative actual export/failure/drop/cancellation counts. Positive integer budgets
default to and are capped at five seconds. Queue/batch defaults and maxima are
512/128, flush interval 200 ms and gRPC request deadline one second. Flush waits use
a monotonic deadline, and export success is observed at the actual exporter result.
Timeout cannot be relabeled success. Shutdown closes admission, drains, cancels
owned I/O and joins within the same budget; unreaped workers remain explicit in the
result. Repeated shutdown returns its retained result. Arbitrary Python exporter or
writer code cannot be forcibly killed; the factory provides only its owned built-ins.
Console writer failure becomes a categorical export failure and never closes the
caller's stream.

## Destination and trust boundary

The gRPC exporter requires an explicit `http://literal-loopback:port` destination
for insecure local collection or `https://host:port` for TLS. Paths, queries,
fragments, userinfo, unsupported protocols and implicit endpoints are rejected.
Before SDK/channel construction, inherited OTEL/GRPC, proxy and certificate override
key names are rejected without reading their values or changing the environment.
There are no headers, client credentials, provider plugins or custom trust files.
Resource attributes contain only `service.name`; sampling and span limits are explicit.
Channel options are fixed: `grpc.enable_http_proxy=0`, `grpc.enable_retries=0` and
4 MiB send/receive message limits. Native retry disable includes transparent retries;
the exporter makes one public RPC invocation per batch, with no application retry loop.

HTTPS uses public `grpc.ssl_channel_credentials` with root_certificates, private_key
and certificate_chain all None, ordinary hostname verification and the native gRPC
runtime-selected bundled/system public trust roots. This permitted default trust
store is the sole certificate-resolution exception. No custom roots, credential
plugins, authority override or plaintext fallback is provided. Missing roots produce
safe initialization failure or degraded export status when observed.

The verification profile mocks HTTPS credentials/channels and exercises native
gRPC only against two synthetic ephemeral 127.0.0.1 collector tests. These mocks do
not prove native filesystem behavior, real TLS handshakes or public connectivity.
Python socket guards cannot intercept all native gRPC I/O; explicit target/options
and fixture cleanup evidence are required. Real remote/TLS activation, credentials,
certificate provisioning and live providers require a later explicit profile.

## Safe LLM event boundary

`LLMEvent` and `SafeLLMTelemetry` provide immutable, runtime-validated version-one
`llm.request_start`, `llm.attempt_finish`, `llm.batch_finish` and
`llm.request_finish` events through the unchanged `TelemetryInterface.capture_event`.
Payloads contain only bounded counts, finite timing/cost values, closed categories
and generated opaque identifiers. Missing values are omitted. The helper borrows
its sink, creates no spans or exporter, and retains at most 256 content-free
failure diagnostics in its typed `snapshot()`.

Each logical invocation has its own request state. Actual provider dispatches and
embedding batches get separate IDs; no ambient span is held across stream yields.
Ordinary sink failures cannot replace application results, exceptions or cancellation.
The standalone legacy `LLMTelemetryHelper` and its exports remain available for
compatibility and retain their historical raw-content behavior. They are outside
this safety guarantee and are no longer used by the instrumented LiteLLM services.

## Correlated execution events

`ExecutionEvent` adds a strict, content-free execution family without changing
`TelemetryInterface` or accepted LLM/MCP payloads. `ExecutionContext` and
`CorrelationScope` provide instance-owned task-local opaque lineage; foreign-owner
bindings fail validation and expired inherited scopes cannot remain current.
Friday Chat owns turn/operation spans around awaited work, closes them on every
exit, and leaves public generator yields without a new ambient span.

Operational counters/histograms are a bounded provider-neutral local snapshot;
there is no new OTel Meter, global registration, exporter or vendor callback.
LLM/MCP links never contribute duplicate execution counters. Raw historical memory
and LLM helpers remain outside this safety claim. Headless assembly and Langfuse
adoption require separate work.
