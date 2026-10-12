# TELEM-02 builder implementation and checks

Role: **BUILDER_CHECKS_COMPLETE**. Stable product candidate `45f3114173a7e9ada128c7950fe1f7e63cb2ff28` atop `37a428c89ada5d736ed22163bfc525aefe8e0b5c`. This is builder evidence; independent delta/aggregate verification and maintainer acceptance remain separate gates.

The implementation adds strict disabled/debug/OTel construction and explicit caller-owned lifecycle while preserving the three-method TelemetryInterface and legacy `OTelProvider(service_name, endpoint=None)` call shape. OTel owns its public SDK provider, context/parent/event state, bounded processor and exporter; it never globally registers the provider, installs an atexit hook, creates Resource through detectors, or adopts raw legacy hooks. Missing SDK keeps the legacy service-only path an opaque-ID compatible nested no-op; explicit factory construction reports a fixed safe error.

Attributes preserve bool/int64/finite float/string scalars, reject arbitrary objects without repr, and enforce64 attributes,128 ASCII name/key characters,1024 UTF-8 string bytes and128 active spans. Queue512/batch128/interval200ms, one-second RPC and default/max five-second monotonic lifecycle budgets are explicit. Concurrent shutdown includes lock waiting/cancellation in the same deadline; results retain cumulative actual export/failure/drop/cancel outcomes. Noncooperative doubles truthfully report unreaped and are deterministically released by test cleanup.

The owned public gRPC stub/encoder uses no compression, no application retry, finite deadlines and the A02-approved literal options: proxy0, retries0, send4194304, receive4194304. HTTPS uses public native credentials with root/private-key/certificate-chain None; that branch was mocked without remote activation. Console keeps caller stream ownership. README documents1.39.1, migration, trust and activation boundaries.

Exact product scope is seven source files, five test files and package README, listed with immutable hashes in product-freeze.json/evidence.json. Unit targets are12Python/7source; preparation-base aggregate is110Python/70source with13 owning trees. Stable gates use a fresh tracked sparse snapshot with267 protected tracked artifacts omitted before checkout; preliminary overlays are separately labelled and retained. Original runtime/credential/dirty payloads were never copied or inspected.

## Stable verification results

| Gate | Result |
|---|---|
| New contract/MCP modules |90 passed;0 skipped; raw0|
| Original focused modules |135 passed; raw0|
| Complete Chat+telemetry |828 passed;5 unchanged opt-in live skips; raw0|
| Root collection, only2 named live-module exclusions |2892 collected; raw0|
| Full root, same exclusions |2891 passed;1 unchanged optional SciPy skip; raw0|
|13 owning trees, same exclusions |2873 passed;1 unchanged optional SciPy skip; raw0|
| Unit Ruff/Mypy |12Python/7source; both raw0|
| Aggregate Ruff/Mypy |110Python/70source; both raw0|
| Root Ruff |raw1; exactly327 approved WVR-004 identities; **not PASS**|
| Offline native lock check |raw0; unchanged lock/18 dependency manifests and Python floors|
| AST3.13/API/registry probes |all110 AST parsed; legacy/API/additive exports preserved; positive consumer raw0; intended negative consumers exact errors|
| Board/docs/selected+aggregate whitespace |raw0;24 tasks/449 Markdown documents|

Raw command arrays, cwd, explicit environments, stable revision, exits, elapsed times, log hashes and tracked before/after integrity are in individual receipts. WVR-004 match additionally freezes17 lint configurations,4 archive files, CommandRegistry source+AST, Ruff0.14.10 and targetpy313. No broad suppression or lint/test weakening was introduced. ExactSDK/API/exporter1.39.1 source/API hashes, grpc1.67.1, protobuf6.33.2, Python3.13.10 and Mypy1.19.1 metadata are in final-metadata-authority-receipt.json; all match prebuild metadata. Installed HTTP exporter remains absent.

All13 approved parameter-expanded listener nodes passed in root full. Every actual native collector receipt records literal loopback target, exact four options, one synthetic request, owner channel close, stopped server and joined executor. Source audits report no original checkout product imports and no owned worker at exit. The async two-provider probe restores thread/task state and creates no native listener/channel. Python socket guard cannot cover all native gRPC I/O; intercepted native targets/options and explicit cleanup provide the permitted native evidence. No remote TLS trust-root activation is claimed.

Exact six skipped node identities/reasons and unchanged prebuild/preparation-base source hashes are in final-skips-effects-cleanup.json. Complete Chat includes five previously authorized opt-in LM Studio skips because no live flag is set; full root/owners exclude only the two named live modules and retain the unchanged missing optional SciPy PageRank skip. No new contract node skips.

## Acceptance-criterion evidence

**AC02-01** — Strict additive models/default-disabled factory; zero SDK effects for disabled/debug; exact legacy two-argument constructor, no-SDK nested no-op compatibility, safe rejected config/environment/exporter dependencies.

Tests: `test_defaults_api_and_lazy_disabled_debug`, `test_strict_additive_models_reject_invalid_settings`, `test_destination_validation_precedes_channel`, `test_conflicting_environment_names_rejected_without_reading_values`, `test_missing_sdk_legacy_noop_and_explicit_factory_safe_failure`, `test_incompatible_sdk_rejected`, `test_missing_explicit_exporter_never_falls_back`.

Evidence: `final-new-contract.log`, `candidate01-pre-collection.json`, `final-cold-public-api.log`.

**AC02-02** — Instance-owned public SDK provider; correct explicit/implicit roots, parents, standalone/current events; unchanged foreign ambient/global provider.

Tests: `test_actual_parent_events_scalars_and_global_isolation`.

Evidence: `final-new-contract.log`, `sources/product/packages/friday-telemetry/src/friday_telemetry/providers/otel.py`.

**AC02-03** — Context isolation across tasks/threads/providers; out-of-order/cross-context/unknown/repeated end; active cap128 and cumulative retained counters.

Tests: `test_out_of_order_cross_context_foreign_and_duplicate_end`, `test_task_thread_and_provider_contexts_are_independent`, `test_active_limit_cancelled_close_idempotent_and_frozen`, `test_standalone_event_respects_provider_active_cap_in_another_context`.

Evidence: `final-new-contract.log`, `final-async-cleanup.log`.

**AC02-04** — Owned queue512/batch128/200ms processor with actual exporter results, drops/failure recovery; absolute monotonic flush/shutdown budgets include concurrent lock wait, cancellation and bounded reaping; console stream ownership.

Tests: `test_queue_overflow_flush_deadline_failure_recovery_and_cleanup`, `test_shutdown_cancels_cooperative_in_flight_with_one_deadline`, `test_concurrent_shutdown_uses_each_callers_budget_and_retains_completed_result`, `test_noncooperative_double_reports_unreaped_then_is_released_in_finally`, `test_sparse_queue_exports_on_bounded_interval_without_explicit_flush`, `test_actual_console_closed_capture_stream_cleanup`.

Evidence: `final-new-contract.log`, `final-skips-effects-cleanup.json`, `sources/product/packages/friday-telemetry/src/friday_telemetry/providers/_otel_processor.py`.

**AC02-05** — Exactly two native synthetic literal127.0.0.1:0 collector tests; protobuf parent/events/scalars/resources; UNAVAILABLE actual failure, received count1; exact four fixed options incl A02 retries0.

Tests: `packages/friday-telemetry/tests_telemetry/test_otlp_collector.py::test_grpc_roundtrip_preserves_spans_and_events`, `packages/friday-telemetry/tests_telemetry/test_otlp_collector.py::test_grpc_unavailable_reports_export_failure`.

Evidence: `final-skips-effects-cleanup.json`, `final-new-contract.log`, `final-root-full.log`.

**AC02-06** — Actual accepted Chat build_runtime observer injection and two-provider Composite using caller-owned managed OTel; no ownership seizure, safe payloads, local diagnostics on sink failure.

Tests: `test_real_chat_observer_two_providers_borrowed_ownership_and_privacy`.

Evidence: `final-new-contract.log`, `final-chat-telemetry.log`, `final-original-focused.log`, `final-async-cleanup.log`.

**AC02-07** — Strict scalar bounds/no repr; closed content-free results, exact resource; environment key-only rejection, no credential/proxy/SDK loader/global registration/atexit; HTTPS public None-root arguments mocked, safe failure without fallback.

Tests: `test_unrepresentable_attributes_rejected_before_sdk`, `test_names_rejected_without_sdk_warning`, `test_scalar_and_name_limits_accept_exact_boundaries_without_repr`, `test_public_grpc_transport_arguments_encoder_and_no_loaders`, `test_mocked_tls_failure_no_plaintext_fallback_or_exception_content`, `test_constructor_failure_releases_partial_owned_state`.

Evidence: `final-new-contract.log`, `final-skips-effects-cleanup.json`, `final-metadata-authority-receipt.json`.

**AC02-08** — All builder verification-profile checks complete on stable tracked candidate; exact source scope/API/registry/AST and unchanged lock/metadata; package migration docs; fresh independent delta+aggregate validator remains responsible for VERIFIED verdict.

Tests: mandatory stable profile gates and source/API receipts.

Evidence: `final-new-contract`, `final-original-focused`, `final-chat-telemetry`, `final-root-collection`, `final-root-full`, `final-owning-trees`, `final-unit-ruff`, `final-aggregate-ruff`, `final-unit-mypy`, `final-aggregate-mypy`, `final-native-lock`, `final-board`, `final-docs`, `final-public-consumer`, `final-cold-public-api`, `final-async-cleanup`, `final-registry-invariance`, `preparation-base-registry-invariance`, `final-negative-consumer`, `final-root-ruff`, `final-root-ruff-json`, `candidate01-expanded-targets.json`, `final-root-lint-disposition.json`, `final-scope-whitespace-preservation.json`.

## Prebuild, preservation and retained attempts

Independent true prebuild reference: `/private/tmp/telem-02/builder-baseline/report.md` SHA256 `6ef6850cc780067cca52ffa9ec818c593d459a04bd03b1a3fdbd03842e0520ee`; manifest SHA256 `c032f08470b8b1d0d4855fe0019a0ebf47b97e91a7a1a4b091bd8a88fd33f229`. It froze old source/API/defaults/exports and scoped fake-only defects before the first product edit. It ran no pytest or actual SDK/native worker. Its report/receipts/scripts are copied byte-for-byte to prebuild-reference; baseline originals and timestamps remain untouched.

The final scope receipt checks current original HEAD, empty index, exact13 committed product paths, product hashes,19 current authority pins+manifest and both whitespace ranges using metadata-only commands. Named unrelated dirty work and transient .claude remain uninspected; product scope changes only through explicit path staging. Parent separately owns preservation authority and governance metadata.

Initial unit Ruff had8 preliminary findings; corrected in the same authorized paths before candidate freeze, with failed raw log retained. One private static-receipt enumeration initially missed tests/lab; exact tracked18-project enumeration corrected it without changing product tests or authority. Expected negative Mypy probes retain raw1: borrowed interface has no flush/lifecycle assignment; CommandRegistry remains invariant in both directions at preparation base and current candidate. Raw root Ruff remains raw1 under exact temporary WVR-004 disposition.

Portable artifact-manifest.json lists byte hashes/sizes of reports, command receipts/logs, probes, expanded targets, source/SDK/authority snapshots, freeze and prebuild references. Private Git snapshots/clones/cache/tmp materialization are excluded. No self-approval, VERIFIED marking, push/merge/deploy, dependency install/sync/download or user live activation was performed.
