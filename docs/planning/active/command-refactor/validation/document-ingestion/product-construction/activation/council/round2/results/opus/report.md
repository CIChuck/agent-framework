# INGEST activation-package council — round 2, OPUS seat

- Seat: opus (claude-opus-5-5, high effort); fresh read-only context; no nested agents.
- Candidate: `c24ff0998010e960fb86c1a89b150ada079bbd46`, branch `feature/cmd-ingest-001`.
- Request SHA256 verified before reading: `cce1f001…4659` (matched).
- **assessment_complete = true; areas_assessed = 8/8**
- **Verdict: CHANGES_REQUESTED**
- **Overall: 8.8 / 10** (weighted 8.89, not rounded up; below the 9.5 gate; 3 mandatory findings)

## Neutral corrections C1–C5 (assessed first)

| Group | Assessment |
| --- | --- |
| C1 model/parity removal, DI24 | **Met.** README, readiness RD-01/RD-05, validation plan, slice/test maps and the requirement-reconciliation DI-24 row remove the serving/parity campaign before *and* after coding. No later gate brings it back. Leftover "qualified" wording in the maps is covered by the reconciliation row "independently qualified artifact wording". |
| C2 configured capability records | **Mostly met.** Contracts §3 makes null evidence hashes admissible. It defines the `declared:` artifact identity for hosted models, states the alias-swap limit plainly, keeps count/batch/vector/store guards, and assigns provisioning to I1 (resolver) and I2 (route binding). **Gap M3:** it never says how composition finds the capability manifest/`assets_root`, or maps an unchanged configured route to a `record_id`. |
| C3 injected embedding broker | **Met.** Core `PreparedEmbeddingService` and `create_ingestion_entry(..., embedder=...)` are required. Space equality is checked before effects, and the whole plan and returned batch are validated before `write_prepared`. There is a named headless witness (`test_headless_document_ingestion_uses_injected_tools_planner`). |
| C4 worker proof at I3-C4 | **Timing met; exactness defect M1.** Thresholds are fixed, the work is placed after the I3-C1 build, and no pre-coding gate exists. But the exact subprocess argv names a module the file map does not contain. |
| C5 Runtime/Chat lifecycle | **Signatures met; exit-timing defect M2.** `DIContainer.bind_ingestion`, ownership transfer, idempotent repeat, ordered shutdown and the Chat lifecycle keyword parameters are exact. Both /read workbook-refusal witnesses exist. The test map's exits for three /read lifecycle witnesses conflict with the file map's exits. |

## A1–A8 matrix (weights sum to 10)

| Area | Weight | Score | Contribution | Evidence |
| --- | ---: | ---: | ---: | --- |
| A1 decisions/scope/readiness | 1.50 | 9.5 | 1.425 | All three maintainer decisions are applied, with the superseded parent clauses named in requirement-reconciliation. `approval-binding.json` keeps every gate incomplete and sets `product_generation_allowed:false`. Gate A1–A5 and Review A1–A8 labels are kept apart. Small issue: the model decision's "no new council follows" is superseded only by authorization.json. |
| A2 values/protocols/identity | 1.75 | 8.75 | 1.531 | Complete frozen field lists, strict canonical JSON, and five digest vectors (all five canonical forms and hashes recomputed by me with stdlib and matched). Receipt-iff-success holds and plan/receipt/destination binding is exact. Deductions: M3, and the LLM resolver API that produces `ResolvedEmbeddingCapabilities` has no exact signature. |
| A3 process/concurrency/lifecycle | 1.75 | 8.5 | 1.488 | Strong design: exec subprocess, bounded IPC, one active plus one queued, TERM/KILL/reap, `worker_not_quiescent`, ordered DI/Chat drains, and an honest RuntimeKernel limit (pair owned in try/finally). Deductions: M1; the source of the conversion/planning *deadline* is not specified (`open` and `DoclingDocumentConverter` carry no timeout); `cwd=request_root` is undefined. |
| A4 compatibility/config/store | 1.50 | 8.5 | 1.275 | Old call shapes are kept, the keyword-only `capabilities`/`open_request` are additive, origin capture, fresh-store marker protocol, strict v1/v2 recovery combinations, no stamping or migration. Deduction: M3 is an operator-facing configuration gap for I2 default routes under the "no new YAML fields" constraint. |
| A5 slice/file/test assignments | 1.25 | 8.75 | 1.094 | 91 exact paths with owner/exit, 49 mapped cases with frozen identities, retain-by-default, explicit offline selectors, Finance exclusion, guide authoring duty. Deductions: M2; M1 is also a file-map omission. |
| A6 format/chunk/errors/effects | 0.75 | 9.5 | 0.713 | Whole-workbook refusal before conversion, with an actionable message and zero-effect assertions on both /ingest and /read. Spans, coverage and refusal on capacity, no overlap or tail loss, truthful partial results, attempt-scoped IDs. |
| A7 packages/deps/profiles | 0.75 | 9.25 | 0.694 | Ownership is clean (Tools imports no LLM; Memory imports no Tools/frontend; Runtime types only Core protocols). The narrow `tokenizers==0.23.3` extra reaches Runtime/CLI through the existing Memory→LLM edge (checked against pyproject). TOOLS-DOC stays separate. |
| A8 sequencing/approvals/handoff | 0.75 | 9.0 | 0.675 | I1/I2/I3 are buildable, the temporary unguarded branch is removed only at I2, and per-slice approval, validation, AG, UAT and A5 effects are bound. Deduction: M2 creates an exit that cannot pass with the edits permitted at that exit. |
| **Total** | 10.00 | | **8.895** | Reported overall **8.8**, truncated rather than rounded. |

## Mandatory findings

**M1 — Worker module in the exact argv is not mapped and does not exist.**
- Evidence: shared-contracts §4 "Exact process and IPC mechanism" launches `-m friday_tools.document_ingestion --worker` and says "The worker entry is in the already mapped Tools module".
- The only mapped new Tools module is `packages/friday-tools/src/friday_tools/filesystem/readers/document_ingestion.py`, which is module `friday_tools.filesystem.readers.document_ingestion`. There is no `friday_tools/document_ingestion.py` at the candidate, and none is in `slice-file-map.json`.
- Violated requirement: C4 "exact subprocess", and the file-map rule "Only listed paths…".
- Impact: the builder must either create an unmapped module or depart from the "exact" argv.
- Bounded fix: change the argv to `-m friday_tools.filesystem.readers.document_ingestion --worker`, or map the new entry module with owner/slice I3-C1. Also define `request_root`.
- Required future acceptance: the I3-C4 headless worker witness asserts the exact argv and module origin in the installed lane.

**M2 — Three /read lifecycle witnesses have conflicting exits.**
- Evidence: test-case-map puts `test_document_read_keeps_event_loop_responsive`, `test_cancelled_document_read_discards_output_and_joins_worker` and `test_shutdown_drains_document_read_worker` at **I3-C3**.
- slice-file-map assigns the lifecycle edits they need to **I3-C4**:
  - `adapters.py`: "Lifecycle builder and FrameworkAsyncClientLifecycle accept optional entry/converter pair, drain in order"; "Owned request drain before existing async-client close".
  - `files.py`/`registry.py`/`runtime.py` I3-C4: "Exercise separate read-only responsiveness/cancel/exit/shutdown witnesses".
- The parent phase-evidence-map labels these witnesses "I3-C3/C4".
- Violated requirement: Review A5/A8 (exact traceable assignments; buildable sequencing) and C5 "per-node lifecycle assertions".
- Impact: following the test map, the C3 exit requires drain code that may only be written at C4.
- Bounded fix: re-exit these three witnesses to I3-C4 (or make the drain assignment C3) so both maps agree.
- Required future acceptance: each witness is run at the exit whose permitted edits implement it.

**M3 — No defined way to discover the capability manifest or map a route to a record.**
- Evidence: contracts §3 says "binds all selected existing pool, non-pool/default/legacy routes in I2 composition using unchanged model config plus an explicit local capability manifest", "Selecting a known default does not require new YAML fields", and "The deployment manifest binds an absolute `assets_root`". `LocalTokenCounterFactory` needs `assets_root` and `record_id`.
- Nothing names how Chat/Runtime/CLI composition locates that manifest or `assets_root` (constructor/factory argument, a named environment variable, an existing config field, or packaged data). Nothing defines how a configured route resolves to a `record_id`. The resolver's public signature is also unstated.
- Violated requirement: C2 "provisioning slices", and Review A2/A4 configuration/call shapes.
- Impact: "unresolved defaults block that slice", so I2 cannot be built without inventing operator-facing configuration.
- Bounded fix: specify the exact discovery source and precedence, the manifest schema (route key → `record_id`), and the resolver signature in `friday_llm.embedding_limits`. Assign them to the I1-C2 and I2-C1 files already mapped.
- Required future acceptance: the I2-C1 witness covers resolution from that source plus refusal when it is missing or contradictory.

## Advisories (non-blocking)

1. State where the conversion/planning timeout value comes from (for example the document-profile JSON) and its default; the I3-C4 timeout witness needs it.
2. Chat composition calls `build_framework_async_client_lifecycle()` before memory construction (runtime.py ~L1419). State the reorder, or say whether the entry is created eagerly or after deferred admission, so "pass the same entry" is feasible.
3. Give the RuntimeKernel-based headless recipe for obtaining `DestinationBinding` and `PreparedVectorStore` without `_di`.
4. Add a raw-UTF-8 `content_sha256` vector. The Unicode vector currently hashes a JSON wrapper.
5. Clarify that "Memory implements `StoreOpenRequest` in the Core submodule" means the declaration lives in Core. Clarify that ChunkPlan `source_sha256` equals `raw_sha256`.
6. Shared-contracts line 417 says "Qualification must prove…" (FC-09 isolation). Reword it as an ordinary test so it does not read like a revived campaign.
7. Add TM-A048's new node `test_read_extracts_genuine_document_content` to the planned witnesses list.

## Boundaries, inputs and limits

- **Inspected:**
  - All 15 required inputs, each pinned. Read in full: README, shared-contracts, readiness, validation-plan, approval-binding, the three decisions, reconciliation, instructions, authorization, corrections.
  - Focused JSON views of the slice, test and digest maps.
  - Targeted grep/sections of the directive, REM, impact assessment and phase-evidence-map.
  - Targeted source reads: `friday_runtime/di.py` (class and shutdown), the RuntimeKernel public surface, `friday_chat/adapters.py` (`FrameworkAsyncClientLifecycle` and builder), the `runtime.py` composition order, `friday_tools` module layout, and class locations and pyproject dependency lines.
- **Executed:** only stdlib SHA256/metadata checks, canonical recomputation of the digest vectors, and read-only git (`GIT_OPTIONAL_LOCKS=0`, `PYTHONDONTWRITEBYTECODE=1`, `python3 -I -B`).
- **Not done:** no product imports, tests, builds, installs, network, provider, model or store calls. No AST, inventory or provenance audit. No harness replay. Finance `test_integration_massive.py` was not opened. No contents of user YAML, `.friday*`, exports, `.venv` or credentials were read; only declared metadata and hashes. Round 1 results, peer reports and memory were not opened. Controller-checks were hash-pinned only and not used as evidence.
- **Entry = exit:**
  - Logical index (`git ls-files --stage -z` SHA256) `db67d02d…a694`.
  - HEAD `c24ff099…`; branch `feature/cmd-ingest-001`.
  - Status identical to the expected value; staged empty.
  - All 8 preserved metadata entries matched; all 29 pins matched.
- **Limits:** this is document readiness only. It grants no construction, effects, acceptance, push or delivery authority. Single seat; stopping after this report.
