# Independent TELEM-02 proposal readiness review

Verdict: **CHANGES_REQUESTED**. This is a construction-directive and separately approvable lint-proposal readiness review, not product VERIFIED, implementation approval, waiver approval, or maintainer acceptance. CD-002 has one security/configuration decision that must be made explicit before approval. WVR-004 is independently ready for a separate maintainer decision on its exact temporary scope.

Reviewer: independent agent `/root/telem02_directive_readiness`, Codex based on GPT-6; exact serving model/version is not exposed. Review date: 2026-10-06. Inputs were the frozen request `/private/tmp/telem-02/request.json`, its 15 authority pins and manifest pin, exact candidate `75aef2272d702e3ce99ec21b520914a5528407e3`, preparation base `e8b075a3861e1e3c1bfac050091a71be60b7e165`, and the complete selected diff. This fresh review received task constraints and operational infrastructure paths, not the builder's private reasoning or proposed readiness conclusions. Source observations and operational receipts were independently examined; no existing operational scripts were executed.

## 1. Required correction R02-01: decide TLS trust-root resolution before construction approval

Severity: high proposal specification gap. Affected authority: `directives/CD-002-otel-adapter-lifecycle.md:59` (AC02-07), `telem02-contract.md:119–148`, especially 122, 133–142 and 144–148. Affected future implementation: `providers/_otel_exporter.py`, strict OTel settings, initialization diagnostics, factory tests and documentation.

CD-002 requires “no env/certificate/proxy/credential resolution.” The contract excludes filesystem certificate settings and secret references, requires rejecting certificate overrides before SDK construction, forbids credential-environment loaders and calls for tests showing forbidden file/credential resolution is never attempted. It also permits `https://host:port` TLS destinations and requires explicit transport security. The proposal does not state an allowed TLS trust-root source or whether native default trust-root loading is an intentional exception to “no certificate resolution.”

The installed public `grpc.ssl_channel_credentials` API explicitly says `root_certificates=None` retrieves roots from a default location chosen by the gRPC runtime (`installed-sources/grpc/__init__.py:1699–1719`). Therefore a conventional secure-channel implementation can meet the endpoint/security wording while relying on implicit native certificate resolution, and a mocked secure-channel test would not establish the forbidden-resolution criterion. Avoiding the OTel exporter's environment/certificate helper does not settle the native gRPC trust decision. This is an ambiguity in allowed behavior, not a claim that TLS implementation is impossible or that a native loader was activated in this review.

Required mitigation: explicitly select one bounded policy in CD-002/contract/profile before approval: (a) permit a precisely named native default trust-root source while continuing to forbid environment overrides, client credentials and arbitrary certificate files; (b) name an approved explicit in-memory root source and its ownership/pin; or (c) defer TLS channel construction in this unit, with a documented content-free initialization failure for HTTPS and a later directive owning trust configuration. Do not silently make this choice in product implementation.

Required verification: mocked construction must prove the chosen root-credential argument and no forbidden credential, environment or file loader call; negative configuration tests must preserve no-channel-before-validation behavior. If HTTPS construction is deferred, test the safe failure and absence of SDK/channel effects. No real remote/TLS connection or certificate provisioning is required or authorized now. Update package migration documentation to state the supported TLS boundary and later activation gate. Freeze changed authority and obtain a fresh readiness review; this report does not amend the candidate.

## 2. Authority, scope and proposed verification assessment

All 15 request authority hashes and the separate manifest hash match exact candidate blobs (`pin-checks.json`, 16/16). The candidate diff is documentation/planning/evidence storage only; `packages/`, `uv.lock`, root metadata, AGENTS and reference policy have no preparation-base delta (`packaging-proof.json`). The exact 19 TELEM-01 controlling pins remain unchanged and valid, along with its authority manifest and report/evidence/closeout report. All 199 pre-existing REM-004-final and VAL-006 artifacts remain unchanged or byte-preserved in gzip/original-manifest storage (`accepted-artifact-preservation.json`).

The policies independently read were AGENTS, engineering, development lifecycle and independent validation, plus the pinned accepted MCP WS-07 and TELEM-01 index, build/tactical/first-slice telemetry contract, proposed CD-002/unit contract/profile/WVR/scope/listener inventory and manifest. Scope is seven exact source paths and five test paths plus telemetry README and initiative governance artifacts; it forbids package/dependency/YAML and Chat/runtime/DI edits. The separate optional lifecycle interface preserves TelemetryInterface's three methods and caller-owned injection. Compatibility corrections, safe no-op legacy missing-SDK behavior, explicit missing-exporter failure, concurrency/ownership bounds, privacy distinction between Chat allowlisted exports and arbitrary generic scalar callers, and non-goals are stated.

The provider-local immutable ContextVar stack, locked active map, explicit SDK parent context and empty root context are feasible using the public pinned SDK (`installed-sources/opentelemetry/sdk/trace/__init__.py:1107–1179`). They can avoid global tracer registration and attach-token reset across tasks. Actual SDK span, protobuf and collector tests are mandated, along with task/thread/provider isolation, cap128, stale/foreign parent errors, repeated/out-of-order/end-after-close cases and outstanding cancellation. Debug/Composite remain unchanged and regressions are required through their public boundaries.

The proposed public SpanProcessor/SpanExporter implementation is feasible without private SDK mutation. The SDK BatchSpanProcessor's forwarded flush ignores its timeout and shutdown joins with a default30second budget (`installed-sources/opentelemetry/sdk/_shared_internal/__init__.py:210–244`), so a custom owned processor is justified. The installed OTLP exporter loads environment/credential/certificate configuration and logs endpoints/UNKNOWN exceptions (`installed-sources/opentelemetry/exporter/otlp/proto/grpc/exporter.py:276–370,377–435`), supporting the decision to use an owned exporter. `proto.common.trace_encoder` publicly exports `encode_spans`; the generated TraceServiceStub exposes the unary Export boundary. Explicit resource/sampler/span limits and shutdown_on_exit=False avoid SDK resource detectors, sampling defaults and atexit ownership. Source inventory SDK hashes match independently collected installed files (`installed-source-evidence.json`).

The permission profile proposes exactly eleven existing synthetic HTTP nodes and two new literal127.0.0.1 ephemeral native gRPC nodes. Existing fixture hashes match; the new fixture/node/helper hash freeze is correctly a mandatory future precollection gate (`listener-analysis.json`). Native gRPC bypass of Python socket hooks is explicit; no claim of egress protection rests solely on that guard. The review performed no collection, tests, SDK activation, channel/listener creation, transport, native gRPC calls, provider/service interaction, downloads, installs, synchronization or dependency mutation.

Verification is appropriately mandatory and preserves raw results: focused/unit and complete Chat+telemetry, collection and full root, aggregate owning trees, changed-unit and aggregate Ruff/mypy, AST/API/invariance/privacy/concurrency probes, board/docs, native offline lock check, source resolution, lock/tool/config hashes, delta/aggregate whitespace, and fresh product delta plus2155a0f aggregate validation. Placeholder paths/counts must be expanded from the future stable candidate, never copied from TELEM-01. No new skip, listener or source suppression is granted. Acceptance/live activation remain separate.

## 3. WVR-004 and packaging: independently ready for separate decision

Root Ruff remains **raw nonzero**, not PASS. With installed Ruff0.14.10 and unchanged py313 configuration, fresh guarded replay produced preparation-base exit1/579 and candidate exit1/327. All candidate diagnostic identities match the proposed sorted multiset exactly, including path/code/start/end/message, without extra or missing findings (`lint-analysis.json`, raw `*-root-ruff.stdout` and receipts). The removal is exactly252 findings, exclusively in the18 packaged scripts, matching each recorded per-script count.

All18 gzip objects decompress exactly to preparation-base Git blobs and match both stored and original hashes. The two pre-packaging artifact manifests retain exact original bytes (`packaging-proof.json`). Accepted product and historical authority/report/evidence are unchanged. This is a reversible byte-preserving storage correction, not remediation of those scripts or a waiver for their252 findings.

The four immutable archived probe hashes, unchanged CommandRegistry source hash and class AST hash, and all17 lint configuration hashes match the scope. Registry AST hash is `34336e7c35b598b215dbb6d08e1150c2ef96e22d08cacc17b5f76e3f5be3f3e7`; its source hash is `15992e7f38fe874f0104a164180679c7e76d7e09413d68152ef5cc77c0f99308`. WVR-004 identifies owner, follow-ups, exact326 archive plus one live diagnostic, unit-limited expiry, drift invalidation and a separate explicit approval gate. It does not revive expired WVR-002/WVR-003, cover new diagnostics, alter exclusions, or waive unit/aggregate Ruff, typing or tests. A fresh final product comparison is still required. No lint exception is approved by this review.

## 4. Offline receipts and preservation

Two private shared no-checkout sparse snapshots were prepared before checkout, each omitting exactly267 protected tracked runtime artifacts. Omissions intersect no source/config/test extensions; all protected paths remain absent. No original untracked/dirty file was overlaid, no HOME override was used, and the unchanged external guard SHA-256 is `6f61ea4ca34c7abef9e0c709eb1e1feb0f3cf7733cbc59bc465d6b01182e9e81`. Subprocesses used an explicit allowlist containing offline/no-sync/no-download uv settings, private cache/temp paths, PYTHONDONTWRITEBYTECODE and isolated source paths. Snapshot tracked hashes remain unchanged (`*-snapshot-after.json`).

| Fresh command | Candidate | Preparation base |
|---|---:|---:|
| `uv run --no-sync python scripts/friday-dev-board.py validate` | exit0,24tasks | exit0,24tasks |
| `uv run --no-sync python scripts/check-documentation-lifecycle.py` | exit0,437Markdown | exit0,433Markdown |
| `uv run --no-sync ruff check . --output-format=json` | exit1,327findings | exit1,579findings |
| board `next` / telemetry `show` | exit0/0 | exit0/0 |
| selected `git diff --check` | exit0 | exact selected diff |

Tools independently returned Python3.13.10, Ruff0.14.10, Mypy1.19.1. Installed package versions were read from distribution metadata without importing SDK modules. Raw stdout/stderr and JSON receipts include command/cwd/environment/exit/timing/log hashes. Board next selects the unrelated memory-v2 item; its output supplies no implementation authority for this telemetry unit. Telemetry show remains started/granted/local with a next gate of independent proposal review and explicit construction/lint approvals.

Original HEAD/branch, index SHA-256, exact NUL-delimited status, all nonprotected tracked bytes and dirty/untracked file fingerprints match before/final (`original-before.json`, `original-final.json`). Dirty work preserved includes .DS_Store, unrelated board/dashboard edits, family-tree deletion, Chat example configuration, security tree, audit Dockerfile and queued tool-manifest packet. Protected original runtime payloads and credentials were not read or copied. The only writes were private review snapshots/artifacts.

Two reviewer-harness errors were corrected only in private orchestration: treating the accepted YAML manifest as JSON, then overbroadly treating `reviewer-artifact-manifest.json` as one of the two repackaged manifests. Neither error ran product or changed original files. The final explicit accepted-artifact check covers all199 files and passes.

## 5. Precise residual construction obligations

1. Console export is synchronous `out.write`/`out.flush` (`installed-sources/opentelemetry/sdk/trace/export/__init__.py:305–309`). The contract explicitly permits reporting unreaped/timeouts and releasing hung test doubles in finally. This source does not by itself prove an impossible proposal; construction must demonstrate budgeted return, truthful retained cleanup outcomes, deterministic test cleanup and no closure of a caller stream. It must stop if it cannot satisfy the approved cleanup requirements, rather than claim every arbitrary stream is interruptible.
2. The pinned encoder logs caught attribute-encoding exceptions (`installed-sources/opentelemetry/exporter/otlp/proto/common/_internal/__init__.py:141–157`). Scalar validation must cover protobuf-representable integer ranges and unsupported values before encoding, alongside finite floats and bounds, so invalid values do not reach a raw logger. Current generic caller strings remain outside the Chat content-safety guarantee as explicitly stated.
3. Public grpc.Channel.close delegates cancellation into native C (`installed-sources/grpc/_channel.py:2229–2250`); source inspection cannot prove an elapsed-time bound or native thread teardown. Approved deterministic construction tests must prove the supported owned transport behavior, target/options and cleanup. No native source/transport proof is claimed now.
4. The frozen workspace pins SDK1.39.1 while the package extra permits older versions. Future package docs must state the pinned supported boundary; factory compatibility/error tests and a stop on incompatible API must avoid claiming broader compatibility without evidence. No dependency change is authorized.
5. SDK get_tracer uses a warnings filter (`installed-sources/opentelemetry/sdk/trace/__init__.py:1238–1251`). The proposal's required global-tracer isolation should be tested directly. Any broader claimed absence of all Python process mutations would need precise scoping and evidence; this review does not claim imports/public SDK calls are free of incidental warning/logging module behavior.

The exit gate is an explicit TLS trust/defer policy amendment, stable new authority pins and fresh independent readiness. After that, CD-002 and WVR-004 still require separate maintainer decisions and approved-authority readiness before a separate builder constructs product.

Memory was used only for orientation to prior telemetry governance; all findings and passing checks above were independently established against frozen inputs and installed source.
<oai-mem-citation>
<citation_entries>
MEMORY.md:125-135|note=[prior telemetry governance orientation only]
</citation_entries>
<rollout_ids>
01a1079c-0038-74f0-9319-c89801c7e94e
01a0e82b-0219-7f10-b5de-5303111cc372
</rollout_ids>
</oai-mem-citation>
