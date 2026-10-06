# TELEM-02 proposed adapter and factory contract

Status: proposal; not approved. Date: 2026-10-06.
Applies only after [CD-002](directives/CD-002-otel-adapter-lifecycle.md) approval.
Accepted TELEM-01 observer, Composite contract, MCP schema and borrowed ownership
remain unchanged. Factory integration into Chat YAML/CLI or headless DI is deferred;
this unit supplies the public programmatic adapter/factory and tests injected use.

## Public boundaries and intentional compatibility corrections

Keep TelemetryInterface's three abstract methods unchanged. Keep existing public
OpenTelemetryProvider(service_name, endpoint=None) call shape and opaque span IDs.
Add a separate optional typed lifecycle contract and immutable result/snapshot
models in friday_telemetry.lifecycle, exported through the package public API.
Expose flush(timeout_millis) and shutdown(timeout_millis), returning categorical
success/failure/timeout/closed results and cumulative failure/drop counts; no raw
exceptions, endpoints, header values or configuration dumps. Idempotent shutdown
returns the retained result. A borrowed arbitrary TelemetryInterface need not
implement lifecycle methods and is never implicitly closed.

Intentional corrections requiring CD-002 approval: remove global tracer-provider
registration; honor supplied parent IDs; deliver events without an ambient SDK
span; stop silently substituting console for a requested but unavailable exporter;
expose missing dependencies and exporter failures. Existing service-only legacy
construction without SDK remains no-op with unavailable diagnostics. Explicit
factory OTel selection with missing dependencies raises a content-free public
initialization error. No arbitrary exception text becomes an event or diagnostic.
Legacy endpoint construction selects gRPC; invalid destinations fail safely rather
than inheriting an environment endpoint. Document these changes and owned-provider
explicit shutdown requirements for existing programmatic/headless callers.

The accepted Chat observer remains the event allowlist for Chat injection. Generic
TelemetryInterface calls retain bounded scalar attributes; reject nested containers
and unsupported objects instead of str(object). This is not a claim that arbitrary
caller-supplied strings are content-safe. No unvalidated LLM/memory hook is connected.

## Parent, context and event rules

Use an instance-owned SDK TracerProvider and tracer, never set_tracer_provider or
an imported global tracer. Maintain a provider-local task/thread context stack
using ContextVar with immutable entries and an active-span map guarded for shared
access. Do not keep SDK attach tokens across start/end calls: cross-task reset and
out-of-order end must not corrupt another context. A private stack identifies the
current logical span only for this provider, not the application's ambient SDK
context. Native SDK auto-instrumentation/context bridges are deferred.

An explicit parent must identify an active span of this instance; reject foreign,
ended or unknown parents with a safe categorical error. An omitted parent uses the
current live entry in this execution context, otherwise a root with an explicit
empty SDK context. Convert the resolved SDK span to a public SDK parent context.
Concurrent children inherit their caller's live parent without sharing mutable
stacks. Different provider instances remain isolated even in one task. Ending an
unknown/duplicate span is a no-op; out-of-order and cross-context end removes the
active record once, with stale context entries pruned on later operations. Max128
active spans: reject further starts visibly, never evict an open span. This new
finite cap and error policy are explicit approved changes, not claimed legacy parity.

capture_event attaches a bounded scalar event to the current live provider span.
Without one, create/end one standalone event span with the event name and attributes,
so events are neither silently lost nor attached to another instance's span.
End attributes preserve bool/int/finite float/string types; no arbitrary repr.
Close outstanding spans as cancelled on shutdown; do not invent application success.
Closed providers reject new operations with a content-free failure so the accepted
Chat observer can retain its local sink-failure diagnostics.

## Owned processing, bounds and lifecycle

The [byte-preserving closeout packaging record](execution/TELEM-02-planning/evidence-packaging.json)
records18 evidence scripts stored as gzip; reports and original source bytes remain
unchanged. Replaying those scripts restores them only into a private directory.

Installed SDK1.39.1 BatchSpanProcessor.force_flush forwards to code that explicitly
ignores its timeout; its public shutdown supplies a default30second join. Simply
passing a timeout to that SDK is not sufficient evidence for this contract.
Implement a small instance-owned processor against the public SDK SpanProcessor
and SpanExporter interfaces in providers/_otel_processor.py, not private SDK fields.
Implement the gRPC SpanExporter in providers/_otel_exporter.py using the installed
public grpc channel/TraceServiceStub and pinned encode_spans/protobuf boundary.
The SDK OTLPSpanExporter logs endpoints and UNKNOWN exceptions; do not suppress its
logger globally or override private SDK methods. The owned exporter observes RPC
status, emits only closed failure categories, uses finite RPC deadlines, closes its
channel to cancel in-flight work, and performs no implicit retries for this unit.
Pin/test encoder compatibility against installed1.39.1 and real decoded requests.
Queue limit512, batch limit128, flush interval200ms, exporter request deadline1s,
flush/shutdown default5s (positive caller budgets capped at5s). Queue overflow is
counted and visible. Export success/failure is observed at the actual exporter result,
not inferred from SDK flush returning true. Queue work is bounded and counters persist.
Do not add a generic plugin registry or arbitrary exporter class loading.

Use a monotonic deadline for flush waits. Timeout/failure cannot become success;
a later successful drain may report success without erasing cumulative counts.
Shutdown closes admission, cancels remaining spans, drains within remaining budget,
requests exporter shutdown to interrupt its owned I/O, and joins its worker within
the same deadline. Report unreaped worker/timeouts explicitly. A hung test double
must be released in finally; passing lifecycle tests require no surviving worker,
channel, listener or pending task. No claim is made that Python can forcibly kill
arbitrary user exporter code: the factory offers only owned, cooperative built-ins.
If pinned exporter cannot meet these cleanup bounds, stop for a numbered finding;
do not weaken the budget, hide a thread, or mutate dependencies.

Set SDK shutdown_on_exit=False; factory callers explicitly own cleanup. No provider
atexit console output or process-global shutdown. Preserve the legacy constructor
by documenting explicit cleanup and fixing the existing synthetic provider test
with finally, rather than keeping an unowned batch thread until interpreter exit.
Generic scalar limits: max64 attributes, ASCII keys/event/span names up to128
characters with a declared safe-name pattern, scalar string values up to1024
UTF-8 bytes (reject unencodable Unicode), signed64-bit integers in the inclusive
range[-2**63,2**63-1], finite floats and bounded counters. Booleans retain boolean
type. Reject unsupported or protobuf-unrepresentable inputs safely before
SDK/encoder calls; do not rely on SDK warning logs to validate untrusted fields.

Console export uses an explicitly owned processor and safe writer-failure handling;
never closes the caller's stream. The closed-pytest-capture-stream residual must be
covered by a real SDK/console regression with deterministic explicit shutdown.

## Typed configuration/factory

Add strict frozen additive models in config.py; do not alter existing TelemetryConfig
or ChatTelemetryConfig defaults. Public factory settings select disabled (default),
debug, or otel; OTel settings select console or otlp_grpc, service_name, explicit
endpoint and the bounded processing limits above. Reject unknown fields, wrong types,
nonfinite values, unsupported protocols, userinfo/query/fragment/path destinations,
and batch limits exceeding the queue. No YAML imports, vendor provider names, dynamic
entry points, auth/header fields, custom filesystem certificates, client credentials
or secret references. The sole native public trust-root allowance below is explicit.

Disabled/debug factories do not import SDK/exporter modules or create threads,
channels or sockets. OTel creates its own SDK resource with only service.name, fixed
explicit sampling (all spans for this unit), explicit span limits, no Resource.create
host/environment detectors and no automatic SDK logging. A managed handle exposes a
TelemetryInterface, safe diagnostics and explicit lifecycle; entering/exiting an
owned handle releases resources once. Constructor failure tears down partial state.
Embedding applications inject handle.telemetry into build_runtime(telemetry=...)
and close the handle themselves; Chat still never owns injected providers.

Before SDK construction, reject conflicting telemetry/transport environment keys
(OTEL_*, GRPC_*, proxy keys and certificate override keys including SSL_CERT_FILE,
SSL_CERT_DIR, REQUESTS_CA_BUNDLE and CURL_CA_BUNDLE, case-insensitive) without
reading/logging their values or mutating os.environ. This deliberately fails explicit
OTel construction with unsupported inherited settings instead of letting the SDK
read headers, custom certificates, credential providers, endpoints or proxy destinations.
Pass supported endpoint/security/compression/timeouts explicitly to the owned
gRPC channel. No SDK export constructor or credential-environment loader is used. No process-global
environment clearing, custom truthy header hacks, fake authorization headers, or
silently inherited SDK settings. Add sentinel tests that prove forbidden custom-file,
credential-provider and endpoint resolution is never attempted; this is not a claim
that the native default public trust-root store is never loaded.

For otlp_grpc, require http://literal-loopback:port for insecure local collector,
or https://host:port for explicitly configured TLS destinations. HTTPS uses the
native gRPC runtime-selected default public trust-root store, including its normal
bundled/system-root loading. This is the sole permitted certificate-resolution
exception: call public grpc.ssl_channel_credentials(root_certificates=None,
private_key=None, certificate_chain=None), then secure_channel with ordinary hostname
verification. No application trust files, custom in-memory roots, client keys/certs,
root callbacks, credential plugins, authority/hostname overrides or insecure fallback.
The factory neither configures nor registers an alternate native trust-root loader.
Reject GRPC_DEFAULT_SSL_ROOTS_FILE_PATH (covered by GRPC_*) and the certificate keys
above before SDK/channel creation; inspect key names only. Missing/unusable default
roots yield content-free initialization failure or degraded export status according
to when failure becomes observable, never plaintext fallback or raw exceptions.
Explicitly supply transport security, timeout and NoCompression; channel options are
limited to grpc.enable_http_proxy=0 and bounded message-size limits. No default_authority
or ssl_target_name_override. The loopback HTTP branch uses insecure_channel only.

Remote HTTPS credential/channel construction is mocked for this unit: assert all
three credential arguments are None, the correct secure branch/target/options and
failure behavior, plus forbidden-loader sentinels and no channel before validation.
These tests do not prove native filesystem behavior, real TLS handshake or public
connectivity. Native default trust-store loading is allowed by the proposed production
contract but is not exercised by this verification profile. Actual remote/TLS
connections, certificate provisioning, credentials and live activation require a later
explicit profile. Package migration docs must state this trust and test boundary.
Missing exporter never falls back to console. Outage after valid construction
returns visible degraded export state without changing application outcomes.

## Privacy and deterministic evidence

Use actual pinned SDK spans and protobuf decoding, not only adapter method mocks.
Prove root/child identity, same-trace parent, standalone and current-span events,
scalar types, cancellation, sampling, drop/failure counters, repeated shutdown,
out-of-order/cross-task close, task/thread/provider isolation and no global SDK change.
Planted secrets in prompts/reasoning/MCP arguments/results/nested objects/exceptions,
configuration/environment never appear in accepted Chat-injected exports or safe
snapshots. Test raw generic input separately: its scalar caller contract is explicit.

A minimal in-process gRPC TraceService collector binds127.0.0.1:0 and receives only
synthetic ExportTraceServiceRequest values. Two exact test nodes cover successful
roundtrip and deterministic server UNAVAILABLE, using bounded fixtures and joins.
No collector executable, Docker, installed service, auth, TLS/network provisioning
or package installation. Python's socket guard cannot intercept all native gRPC I/O;
record that limitation and prove literal-loopback server/target/options by preflight
and constructor interception. Keep the inherited Python guard unchanged. The frozen
allowlist omits native proxy/credential settings. This is explicitly proposed
normal-user sandbox escape for synthetic loopback only, never an egress waiver.

## Sources and frozen implementation observations

[Source inventory](execution/TELEM-02-planning/source-inventory.json) records actual
SDK source hashes and lock pins at accepted preparation basee8b075a. SDK/API/exporter
pins are1.39.1; HTTP exporter is not installed and no install is proposed. The
package extra allowing older SDK versions is not evidence of this adapter's compatibility:
state the1.39.1 validated boundary in package docs, reject incompatible public APIs
with content-free InitializationError and stop rather than changing dependencies. gRPC is the
existing installed path. New factory/callers remain provider-neutral.

Official API references: [SDK trace and processor lifecycle](https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.html),
[context API](https://opentelemetry-python.readthedocs.io/en/latest/api/context.html),
and [Python instrumentation](https://opentelemetry.io/docs/languages/python/instrumentation/).
Latest docs are explanatory; actual installed source/lock and approved contract
control execution. No exact3.13.4 runtime or vendor delivery claim.
