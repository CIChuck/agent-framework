# TELEM-02 true pre-build source/API baseline

Date: 2026-10-06. Builder phase: baseline preparation only.
Construction remains paused pending the controller's fresh READY release.
This report is pre-build evidence; it is neither product verification nor acceptance.

Frozen preparation base: e8b075a3861e1e3c1bfac050091a71be60b7e165.
Frozen approved authority candidate: d187ce35074697633108ef1e8ad5b404b0de9fcc.
The 17 authority pins and separate current-unit manifest hash match the approved
request. Read AGENTS, engineering/lifecycle/independent-validation policies,
CD-002, unit contract/profile, approval record, WVR-004, REM-005, build/tactical
plans, accepted first-slice contract and MCP WS-07 boundaries. No authority changed.

## Isolation and commands

`prepare.py` created two independent local shared Git clones with `--no-checkout`.
Non-cone sparse exclusion patterns were installed before detached checkout. Each
snapshot omitted exactly 267 protected tracked artifacts, with no source/config
intersection, no dirty overlays and no runtime artifact materialization. Only
tracked committed sources were read. Original .env, .friday, Chroma, transcripts,
credentials and unrelated dirty file contents were never inspected or copied.

The bootstrap command was `/usr/bin/env -i` with explicit PATH, private TMPDIR,
PYTHONDONTWRITEBYTECODE=1 and the unchanged inherited guard in PYTHONPATH, followed
by the existing read-only `.venv/bin/python` and `prepare.py`. `finalize.py` used the
same bootstrap. Each fake probe has its exact command, cwd, revision, full nonsecret
environment allowlist, raw stdout/stderr hashes, exit, elapsed time and tracked
preservation receipt. Both exit zero. Actual Python/Ruff/Mypy version commands
also exit zero. There were no pytest runs or collection, synchronization,
installation, downloads, SDK activation, native channels, sockets or listeners.

The guard SHA-256 is
`6f61ea4ca34c7abef9e0c709eb1e1feb0f3cf7733cbc59bc465d6b01182e9e81`.
Environment receipts use offline/no-sync/no-download uv, private caches and temp,
snapshot */src plus the Chat test-helper path. No HOME override or credential,
OTEL, GRPC, proxy, certificate or live-provider settings are supplied. No process
environment writes occur. Original HEAD, branch, index hash and status names remain
unchanged in original-before/after.json. No product/source/test/package-doc edit or
commit has occurred.

## Retrospective defects proved with scoped fake modules

`fake_probe.py` loads the old interface and adapter directly from each isolated
snapshot. All OpenTelemetry dependency modules, Resource, TracerProvider, tracer,
batch processor and exporters are scoped in-memory fakes; they are restored after
each scenario. Actual SDK/grpc loaded-module lists remain empty and thread identity
lists remain unchanged.

- Explicit parent_id is omitted from the underlying tracer start call.
- Standalone events disappear. Starting a logical span never establishes current
  context, so its events disappear too. An unrelated ambient span receives events.
- Event/end attributes stringify booleans, integers, floats, nested containers and
  unsupported objects; the synthetic object representation is observed.
- Construction attempts global tracer registration (against the fake trace only).
- A requested missing OTLP exporter silently constructs the console fake.
- Missing SDK preserves the existing service-only no-op and string span-ID behavior.
- The provider passes no shutdown_on_exit override, exposes no shutdown method and
  retains neither its SDK provider nor its processor for cleanup.

The final item is console-ownership baseline evidence without replaying an unowned
real SDK thread or console atexit. Installed SDK source independently confirms
TracerProvider's shutdown_on_exit=True default and atexit registration, batch worker
creation, the ignored force_flush timeout and default 30-second shutdown join. This
is source evidence, not a real baseline console/collector test claim. The mandatory
future real SDK console regression will explicitly own and close resources.

## Preserved API and dependencies

Both source/API/default/export receipts are identical across preparation base and
approved authority candidate, and selected original product source hashes match.
TelemetryInterface has exactly capture_event, start_span and end_span abstract
methods. OpenTelemetryProvider remains
`(service_name: str, endpoint: str | None = None) -> None`. All 38 existing public
exports and legacy model default expressions are recorded. TelemetryConfig defaults
remain enabled=True, otel_enabled=False; ChatTelemetryConfig remains enabled=False,
provider='debug'. The four authorized new source files are absent on this baseline.

Actual tools: Python 3.13.10, Ruff 0.14.10, Mypy 1.19.1. Installed metadata records
SDK/API/exporter/protobuf boundary 1.39.1, grpcio 1.67.1, protobuf 6.33.2 and all
relevant distribution metadata hashes. HTTP exporter is absent. Fifteen installed
SDK/API/encoder/gRPC source paths have exact hashes and source-only AST API shapes.
No dependency or lock changes are proposed. uv.lock and root/package pyproject
hashes are recorded.

One initial source-only metadata attempt assumed trace_encoder was a directory.
It failed before any snapshot or probe and was corrected to the actual public
trace_encoder.py after filename inspection. preparation-error-01.md retains this
tooling correction; it has no product/security/authority impact.

## Prospective choices, contingent on construction release

All implementation will remain inside the seven source and five test paths plus
the package README authorized by CD-002. Add strict frozen OTel/factory models
without changing either legacy model; a provider-neutral managed handle and optional
lifecycle protocol with frozen categorical result/snapshot models; lazy OTel imports
for disabled/debug; and content-free initialization/operation errors.

The adapter will use a provider-local immutable ContextVar stack and locked active
span map, instance-owned SDK provider/tracer, explicit root/parent Context objects,
bounded validated scalars and explicit cancelled outstanding-span shutdown. It will
preserve the legacy constructor's signature through private typed construction for
the managed factory. No new abstract TelemetryInterface method is needed.

The processor will implement the SDK's public SpanProcessor boundary with a bounded
queue, monotonic deadline waits, observed actual export results, cumulative counters
and cooperative worker cleanup. The owned gRPC exporter will use public channel/stub
and pinned encode_spans boundary with explicit deadlines, options and channel close;
console export will own its processor and safe writer handling without closing the
caller's stream. SDK shutdown_on_exit=False avoids global atexit ownership.

Environment conflict tests will mock key enumeration rather than alter os.environ.
HTTPS credential/channel branches remain mocked and verify all three credential
arguments None and approved native-default-public-root policy. Only the two exact
new synthetic gRPC nodes may activate literal 127.0.0.1 ephemeral collector traffic
after preflight/release; the accepted eleven HTTP nodes remain frozen. Native guard
limitations will be explicit. No additional listeners, dependency activation,
Chat YAML/CLI/headless ownership adoption or package-boundary changes are planned.

No concrete unsatisfied contract was found during source/metadata preparation.
Deadline and cleanup claims remain to be demonstrated against the pinned SDK during
authorized construction; a failure there will become a numbered finding, not a
silent scope or budget change. Full mandatory unit/aggregate/root/Chat/owning gates
and fresh independent review remain outstanding. Helper scripts must be persisted
as byte-preserving .py.gz if copied into the packet; no repository .py evidence or
raw diff artifact is authorized by this baseline phase.

## Receipt map

- report.md: this readable report.
- preparation-base-snapshot.json and approved-candidate-snapshot.json: exclusions,
  revisions and complete included tracked hashes.
- preparation-base-source-api.json and approved-candidate-source-api.json: source
  hashes, abstract/API shapes, exports, defaults and absent new-file inventory.
- preparation-base-fake-probe.stdout and approved-candidate-fake-probe.stdout:
  retrospective defect and safe-effect outputs, with raw stderr and receipt JSON.
- tooling-and-sdk-source.json, sdk-source-observations.json and
  tool-version-commands.json: exact installed metadata/source/API/tool evidence.
- baseline-consistency.json: current selected source equality, baseline equality,
  all authority/manifest pins and guard identity.
- original-before.json and original-after.json: original metadata preservation.
- prepare.py, fake_probe.py and finalize.py plus private-helper-source-hashes.json:
  independent reproducible raw helper sources and source hashes.
