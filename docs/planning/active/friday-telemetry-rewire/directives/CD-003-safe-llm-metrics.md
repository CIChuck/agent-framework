# Approved CD-003: Safe LLM metrics and role-service injection

Status: approved by Chuck Russell on 2026-10-07. Prepared: 2026-10-06.
Initiative: friday-telemetry-rewire. Work unit: TELEM-03.
Branch: feature/friday-telemetry-rewire.
Preparation base: 4ca9baecdcdcf26fc5e8055b326c3a54cda36cb7.

Chuck Russell explicitly approved CD-003 and separately WVR-005 on 2026-10-07:
"i approve cd-003, wvr-005 - proceed to next steps". The
[approval record](CD-003-approval-record.md) binds the reviewed proposal at 22c8651.
The initiative stays started/local. Required independent lint-authority review,
approved-authority reconciliation and pre-build probes precede source construction.

## Objective and authority

Deliver closed, content-free request/attempt/batch metrics for typed and legacy
completion, both streaming APIs, and embeddings. Inject the existing borrowed
provider-neutral observer into every Friday Chat LLM construction path, including
canonical pools, legacy fallbacks, compaction, SmartFileRead, and explicit
maintenance providers. Preserve application results, exceptions, retry/circuit
policy, service selection and ownership.

Follow explicit maintainer direction, repository policies, accepted TELEM-01/02
contracts, approved build/tactical plans, then this unit's approved
[contract](../telem03-contract.md) and [verification profile](../verification-profile-TELEM-03.md).
The separate [manifest](../authority-manifest-TELEM-03.yaml) pins exact authority,
product targets, source inventory, approved lint disposition and synthetic effects.
Accepted unit manifests, contracts and evidence remain immutable.

## Exact approved product manifest

Existing source allowed:

- packages/friday-telemetry/src/friday_telemetry/__init__.py: additive public exports.
- packages/friday-llm/src/friday_llm/service.py: safe metrics on all four completion
  paths, actual retry-attempt accounting, guarded finalization and stream cleanup.
- packages/friday-llm/src/friday_llm/embeddings.py: safe query/document metrics,
  batch/retry accounting, truthful absent usage and cache/empty-input outcomes.
- packages/friday-llm/src/friday_llm/pricing.py: additive typed estimate-provenance
  API; preserve existing calculate/get_pricing results; remove its existing
  whole-file mypy ignore instead of extending it.
- packages/friday-chat/src/friday_chat/telemetry.py: explicitly validate the new
  closed event union; finite float scalars; retain bounded diagnostics and MCP checks.
- packages/friday-chat/src/friday_chat/adapters.py: optional typed keyword-only
  telemetry injection through the inventoried factories, with fixed role labels.
  Correct the two pre-existing no-any-return diagnostics in publish_mcp_memory and
  discard_mcp_memory through a declared typed snapshot-publisher boundary; preserve
  underlying bool values and MCP publication/discard behavior, with consumer probes.
- packages/friday-chat/src/friday_chat/runtime.py: pass the enabled observer through
  real framework construction; preserve disabled/fake behavior and ownership.
- packages/friday-chat/src/friday_chat/reorganization/mutation.py: optional typed
  injection into explicit maintenance LLM/embedding factories only. Recovery,
  authorization, provider readiness, mutation and persistence algorithms stay intact.

New source allowed:

- packages/friday-telemetry/src/friday_telemetry/models/llm_events.py: closed typed
  event union, scalar serialization and runtime validation.
- packages/friday-telemetry/src/friday_telemetry/helpers/safe_llm.py: provider-neutral,
  bounded request/attempt/batch accounting and best-effort emission; no pricing,
  LiteLLM dependency, prompt storage or process-global state.
- packages/friday-llm/src/friday_llm/telemetry.py: typed LiteLLM adaptation, usage
  presence/finality, exception-type classification and safe pricing projection.

Existing tests allowed:

- packages/friday-llm/tests_llm/test_service.py
- packages/friday-llm/tests_llm/test_embeddings.py
- packages/friday-llm/tests_llm/test_streaming.py
- packages/friday-llm/tests_llm/test_typed_service.py
- packages/friday-llm/tests_llm/test_resilience.py
- packages/friday-llm/tests_llm/test_pricing.py
- packages/friday-chat/tests_chat/test_telemetry.py
- packages/friday-chat/tests_chat/test_runtime.py
- packages/friday-chat/tests_chat/test_reorganization_mutation.py
- packages/friday-chat/tests_chat/test_command_production_adapters.py

New tests allowed:

- packages/friday-telemetry/tests_telemetry/test_llm_events.py
- packages/friday-telemetry/tests_telemetry/test_safe_llm.py
- packages/friday-llm/tests_llm/test_safe_telemetry.py
- packages/friday-chat/tests_chat/test_llm_telemetry_injection.py

Package documentation: packages/friday-telemetry/README.md,
packages/friday-llm/README.md and packages/friday-chat/README.md.
Total: 11 source, 14 test and 3 documentation targets. Exact allowed paths are
machine-readable in the manifest; changed paths may be a subset, never a superset.
Typing/interface corrections within these files may support the specified boundary
without changing unrelated behavior. Planning/evidence within this initiative and
its board/dashboard row may change; preserve unrelated user edits separately.

## Construction sequence and acceptance criteria

| Task / criterion | Required result and evidence |
| --- | --- |
| T03-01 / AC03-01 | Closed immutable event schema, runtime rejection, finite/bounded scalar projection and content-sentinel negatives; unchanged three-method TelemetryInterface |
| T03-02 / AC03-02 | Typed and legacy nonstreaming paths produce one logical start/finish and one finish per actual attempt, including successful retries, blocked circuit, pre-dispatch validation and parsing failure |
| T03-03 / AC03-03 | Both streaming APIs account for actual setup attempts and all raw usage chunks, first text timing and final usage; cancellation, timeout, failure and early aclose are distinct; payload/event order preserved and resources closed |
| T03-04 / AC03-04 | Embedding query/documents, cache hits, empty input, multiple batches, retries and partial failure retain correct request/batch/attempt IDs and truthful usage coverage |
| T03-05 / AC03-05 | Usage absence differs from reported zero; bounded estimate provenance covers built-in/custom/provider/prefix/partial/fallback/disabled/unknown pricing without claiming current rates or actual billing |
| T03-06 / AC03-06 | Every inventoried canonical/legacy/fallback/alias construction path receives the enabled observer; disabled supplies None; no changed model selection, alias identity or ownership |
| T03-07 / AC03-07 | Sink errors at emission/finalization never replace results, primary exceptions or cancellation; bounded local diagnostics survive; real Chat observer plus two-child Composite and synthetic managed OTel preserve allowed scalars |
| T03-08 / AC03-08 | Exact scope/API/privacy/typing/lint/root/owning/lock/docs gates pass with separately approved exact debt disposition; stable committed candidate receives fresh independent delta and aggregate VERIFIED |

Before first source edit, freeze pre-build call signatures, factory construction
inventory, model-selection/alias behavior, pricing behavior, existing test expectations
and safe fake-only probes. The preparation packet retains static evidence, not
executed behavioral proof. Record actual baseline probe outcomes before editing;
later baseline comparisons must be labelled retrospective.

## Compatibility, privacy and non-goals

The services' optional telemetry injection now emits the new schema instead of
legacy llm_completion_success/error or embeddings_generated/error payloads. Update
the existing service-event expectations and document this telemetry consumer
migration. Completion/vector results and existing invocation signatures remain
compatible; add only optional keyword-only constructor/factory role metadata.
TypedLLMClient/request/stream models do not gain mandatory fields or methods.

Keep the standalone public legacy LLMTelemetryHelper, its models and re-export
facades unchanged for compatibility. They retain historical unsafe behavior and
are explicitly outside the new safety claim; LiteLLMService and embedding service
must stop routing through them. No dual emission or raw legacy-hook adoption.

No new LLM spans in this unit: closed events correlate request/attempt/batch IDs
without holding ambient span context across generator yields. Full turn identity,
parent spans and native/MCP tool, memory, persistence and operational metrics remain
TELEM-04. Langfuse callbacks/metadata/configuration remain TELEM-05. No callback
registration, provider binding, headless assembly adoption, exporter/factory change,
configuration-template edit, dependency/lock/tool-policy change or price-table refresh.

Do not export prompts, messages, reasoning, tool names/arguments, text hashes,
vectors, raw model/service/provider-response/user/session/turn identifiers, exception
messages, arbitrary exception class names, endpoint/key/config data or pricing_model.
Telemetry must not invoke arbitrary repr/str/property access merely to report errors.
No extra provider call, read-ahead/prefetch, retry of yielded chunks or usage-token
fabrication. Explicit early close/cancellation cleanup is permitted, not new retries.

## Verification effects and stop conditions

All new tests are fake-only, in-memory and deterministic, with no provider/channel/
listener construction. Full regression gates include the existing 13 synthetic
loopback nodes in the frozen [effect inventory](../execution/TELEM-03-planning/listener-scope.json).
CD-003 approval authorizes only those named normal-user localhost effects
after final fixture/import/helper preflight. Prior unit approval is not reused.
No real state, credential loading, TLS/remote endpoint, paid call, install/sync/
download, publication, push, merge or deployment is authorized.

Root Ruff currently exits 1 with 327 exact unchanged identities. Separate
approval of [WVR-005](../validation/WVR-005-telem03-lint-disposition.md) disposes
only those for this unit; CD-003 alone cannot. Every changed-unit/aggregate lint and
typing command must exit zero. No new suppression, skip or diagnostic is covered.

After explicit scope and lint decisions, reconcile approved authority and preflight
before construction. Freeze a stable product commit and submit the complete unit
delta plus aggregate from 2155a0fc51f5b20dea4e35c6cfc70f1d52002735 to a fresh-context,
read-only validation subagent as required by AGENTS.md. Completion and maintainer
acceptance remain separate. Stop for authority drift, extra path/effect, altered
application/retry/alias behavior, unsafe projection, missing typing correction,
unbounded retained state, new failure/skip/debt or inability to preserve dirty work.
