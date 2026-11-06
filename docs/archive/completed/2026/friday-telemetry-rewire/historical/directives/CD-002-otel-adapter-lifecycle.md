# Approved CD-002: OTel adapter semantics and owned factory lifecycle

Status: approved by Chuck Russell. Date: 2026-10-06.
Initiative: friday-telemetry-rewire. Work unit: TELEM-02.
Branch: feature/friday-telemetry-rewire.
Preparation base: e8b075a3861e1e3c1bfac050091a71be60b7e165.
Maintainer Chuck Russell explicitly approved CD-002 and separately WVR-004 by
responding "approved" to the concrete decision after corrected independent CDR-013
READY. The [approval record](CD-002-approval-record.md) binds the exact reviewed scope,
13 synthetic loopback effects and temporary327 lint disposition. Construction begins
only after fresh reconciled approved-authority readiness and source/API baselines.

## Authority and objective

Follow explicit maintainer direction, engineering/security/lifecycle/independent
validation policies, accepted MCP WS-07, approved build/tactical direction, accepted
TELEM-01 boundaries, then this directive and approved unit contract/profile. The
separate [TELEM-02 manifest](../authority-manifest-TELEM-02.yaml) freezes these inputs;
the accepted TELEM-01 manifest and all its authority/evidence remain unchanged.

Repair the shared OTel adapter and supply a typed programmatic factory with truthful
bounded owned lifecycle, actual SDK context/parent/event evidence and synthetic
OTLP collector delivery. No Chat YAML/CLI/headless assembly adoption in this unit.
Implement exactly the [approved contract](../telem02-contract.md) and
[verification profile](../verification-profile-TELEM-02.md).
Approved [A02](CD-002-A02-native-retry-disable.md) requires fixed
grpc.enable_retries=0 on both channel branches. Its [decision record](CD-002-A02-approval-record.md)
and fresh approved-amendment readiness precede implementation/native OTLP tests.

## Exact approved product manifest

Allowed existing source (all under packages/friday-telemetry/src/friday_telemetry/):
- providers/otel.py: semantics, actual optional SDK boundary typing and lifecycle;
  remove its existing whole-file mypy ignore-errors rather than extending it.
- config.py: additive strict factory/OTel models only; legacy defaults unchanged.
- __init__.py: additive public exports only.

Allowed new source in the same directory: lifecycle.py, factory.py,
providers/_otel_processor.py, providers/_otel_exporter.py. Do not add abstract methods to TelemetryInterface,
modify Debug/Composite, or reach across framework package implementation internals.

Allowed tests under packages/friday-telemetry/tests_telemetry/:
- Existing test_providers.py and test_mcp_telemetry.py (replace private-object
  pseudo-provider fixture with actual synthetic public adapter boundary; preserve
  MCP security assertions and unrelated Debug/Composite contracts).
- New test_otel_contract.py, test_telemetry_factory.py, test_otlp_collector.py.

Allowed package documentation: packages/friday-telemetry/README.md.
Planning/authority/execution/validation artifacts inside this initiative and its
board/dashboard row may change, preserving all unrelated dirty work and accepted
TELEM-01 authority. No pyproject/lock/config-template/example YAML changes.

## Construction order and acceptance criteria

| Task / criterion | Required evidence |
| --- | --- |
| T02-01 / AC02-01 | Strict additive config/factory defaults; disabled/debug no SDK effects; invalid config/env/missing explicit exporter safe failures; legacy call-shape and no-op dependency compatibility |
| T02-02 / AC02-02 | Instance-owned SDK, correct explicit/implicit roots/parents, standalone and current events, no global tracer mutation |
| T02-03 / AC02-03 | Task/thread/provider isolation, same/different-context and out-of-order end, unknown/repeated end, active-span cap and retained counters |
| T02-04 / AC02-04 | Public-SDK owned bounded processor, actual exporter success/failure, queue drop, flush deadline, idempotent cancelled shutdown, complete worker/channel cleanup and real console regression |
| T02-05 / AC02-05 | Two exact deterministic gRPC collector nodes, protobuf parent/events/scalars and visible UNAVAILABLE result; fixed literal-loopback target/effect evidence |
| T02-06 / AC02-06 | Real Chat observer injection and two-provider Composite using synthetic managed OTel; unchanged borrowed ownership and safe payloads; local diagnostics survive sink failure |
| T02-07 / AC02-07 | Closed/no-secret export/resource/snapshot assertions, no env/proxy/custom-certificate/credential-provider resolution; explicit native public trust-root exception and mocked HTTPS branch; no global tracer registration or raw legacy-hook adoption |
| T02-08 / AC02-08 | Unit and preparation-base aggregate typing/lint/AST/API/owning/root gates, package docs/migration, lock unchanged, scope manifest and fresh delta+aggregate VERIFIED |

Before first product edit, collect frozen source/API baselines with scoped dependency
mocks and synthetic providers. Prove current ignored-parent/lost-event/global SDK and
console-ownership defects using retrospective baseline evidence where applicable;
do not label tests introduced afterward as pre-build runs. Construction is released
only after explicit CD-002 approval, separate lint decision and fresh reconciled
readiness. Existing board initiative started/granted is insufficient for this unit.

## Security, ownership and approved execution permissions

Preserve accepted Chat local-only defaults and caller-owned injection. The factory
owns only resources it creates; a caller injects and later explicitly closes the
managed OTel handle. No Chat/app/runtime/DI cleanup changes, no optional Langfuse
callback, no LLM/memory/tool/persistence schema or tracing changes. No user data,
.env/.friday, transcripts, Chroma, credentials, process-global environment writes,
live vendor, remote collector, paid calls, external messages, push/merge/deployment.
No install/download/sync, interpreter provisioning or dependency update.

Under this approval, permit normal-user sandbox escape only for the eleven exact existing
synthetic HTTP listener nodes recorded in the approved REM-004 inventory and the
two new nodes test_otlp_collector.py::test_grpc_roundtrip_preserves_spans_and_events
and ::test_grpc_unavailable_reports_export_failure. Both new fixtures bind only
127.0.0.1:0; no fixed port, remote destination or third-party collector. Record final
parameter-expanded node IDs and fixture hashes before collection, with unchanged
network guard, environment allowlist, isolated sources and protected-state omission.
Native gRPC guard limitations must remain visible; loopback target proof is mandatory.
Any additional listener node/effect or missing deterministic prerequisite stops the
run; do not silently exclude it or replace full gates with selected-node passes.

## Verification and completion

Every command in the separate profile is mandatory. Unit Ruff/type checks require
raw zero. Root Ruff must run unchanged with raw exit recorded; its current327
findings are covered only by separately approved [WVR-004](../validation/WVR-004-telem02-lint-disposition.md)
in the linked approval record, with exact identity/hash reproduction required. No inherited TELEM-01 waiver, PTY waiver, failure skip,
blanket typing relaxation or source-ignore continuation is approved by this directive.

Freeze stable product commit, exact allowed and aggregate manifests, source/tool/
config/authority hashes, baseline and candidate effects and all raw receipts. A fresh
read-only validator reviews both TELEM-02 delta and complete2155a0f aggregate with
AC02-01–08 and accepted AC-01–06 regressions. Return VERIFIED/CHANGES_REQUESTED/BLOCKED.
A readiness review of this document cannot verify future product. Maintainer
acceptance, live activation and later TELEM-03–05 remain separate gates.

Stop for unapproved path, API/config/dependency/sampling/privacy change, arbitrary
provider plugin, global SDK/env mutation, inability to enforce cleanup/deadlines,
unsafe real state/transport, source suppression or additional lint diagnostic.
Do not silently expand scope, edit accepted evidence or weaken tests to proceed.
