# SOL independent design review — final round 6

Verdict: **VERIFIED**. `assessment_complete=true`; `areas_assessed=8/8`; mandatory findings: **0**. Overall design score: **9.575/10**, calculated after completing all eight areas. The score is not rounded up. This is one seat’s design assessment, not a council aggregate or maintainer acceptance.

Candidate: `7cf8956012a9c66d15f959436c6e129cde8a86c5`, branch `feature/cmd-ingest-001`, workdir `/Users/chuckrussell/Dev/gendev/agent-framework`. References below are relative to `docs/planning/active/command-refactor/validation/document-ingestion/product-construction/activation/` unless a different location is named.

## Neutral corrections assessed first

**G1 — satisfied in the design.** Shared-contracts section 4, lines 576–689, supplies an actionable common ownership state machine. Runtime and Chat accept an entry with no converter, do not resolve document configuration for text, and retain an already owned converter when its argument is omitted. Entry-only and converter-only states can converge on the same pair. Supplied objects must be identical to already bound objects; a mismatch or closing state refuses without partial adoption. The caller remains responsible for previously unowned rejected arguments. Chat’s frozen wrapper has one typed mutable holder, with constructor seeding and accessors rather than stale duplicated fields. Close rejects new work, drains entry then optional converter before clients/MCP, retains cleanup across repeated cancellation, and reports unknown quiescence. Direct converted-source ingestion separately requires a matching session; Memory neither imports Tools nor consults frontend ownership. Text uses Memory’s non-Docling planner even with the default document strategy.

**G2 — satisfied in the design and actual mappings.** Test-case-map TM-A049 expressly retains source/description/listing behavior without a document converter/settings fixture. The named C3 `test_text_ingestion_needs_no_document_binding` goes through actual default text /ingest and disposable-store readback, with zero document resolver/converter calls. Separate Chat `test_lifecycle_drains_entry_with_optional_late_converter` and Runtime `test_shutdown_drains_shared_document_worker` assign entry-only, late attachment, identical-object, mismatch and ordered-drain controls at C4. The installed helper also includes entry-only text success and cleanup without document assets. These are meaningful positives rather than refusal-only substitutes.

Shared-contracts lines 162–173 and validation-plan lines 102–110 move Tools extra/lock declarations before C1 conversion tests and Chat’s default extra/lock before C3 command adoption. Each earlier interpreter is phase-bound by Gate A5; C5 remains the final installed-profile check. Shared-contracts section 3 distinguishes absent assets from present size/hash identity mismatches. Lines 466–473 specify cooperative 64 KiB snapshot copy/hash steps, yielding, before/after descriptor identity, cancellation/deadline cleanup and no child launch from an incomplete snapshot. Snapshot and workbook preflight fall inside heartbeat/deadline proof. Lines 694–699 explicitly add .pptx while retaining text/table dispatch. Readiness lines 20–29 make the input caps per file, workbook, sheet or deck explicit.

**G3 — satisfied.** The extension was read immediately after the hash-verified request. It changes only the round cap; current authorization and README preserve the reviewed roster, scope, weights and gate. This is additional pass 3/3, global round 6/6. The full assessment below does not inherit any previous verdict. This seat stops after its report regardless of outcome.

## Full weighted assessment

Weights total 10. Each contribution equals area score × weight / 10. Area scores express design quality; there is no separate coverage score.

| Area | Weight | Score /10 | Contribution | Assessment and evidence |
| --- | ---: | ---: | ---: | --- |
| A1 | 1.50 | 9.8 | 1.4700 | README 90–118, reconciliation and approval-binding gates consistently distinguish planning, council, construction and effects. Model/parity campaigning is removed before and after coding; configured runtime guards remain. Office refusal and shared ownership amendments are carried explicitly. |
| A2 | 1.75 | 9.5 | 1.6625 | Shared-contracts sections 1–3/5 define immutable strict values, injected counter/broker/store, source/plan/vector/receipt identities and canonical serialization. Digest examples cover preparation drift, Unicode, plan and destination receipt. Matching source/session and independent parent validation close important handoff ambiguities. |
| A3 | 1.75 | 9.5 | 1.6625 | Section 4 defines the exact subprocess module, private environment/root, framed IPC/state transitions, bounded drains, one-active/one-queued admission, authoritative deadlines, TERM/KILL/reap and unhealthy-service handling. Common public ownership serves headless/Runtime/Chat; C4 demands actual worker and application cleanup evidence. |
| A4 | 1.50 | 9.6 | 1.4400 | Sections 2/3 preserve public call shapes and omitted config fields, stage I1 legacy behavior, and coordinate the I2 guarded switch. Section 5 covers explicit path origin, fresh/matching/ephemeral namespaces and strict v2 recovery without restamping. Named I2 configuration, operational and recovery positives accompany negative controls. |
| A5 | 1.25 | 9.5 | 1.1875 | Complete selected file assignments and concrete case/witness mappings specify owners/exits, retain defaults and narrow fixture changes. Validation-plan explicitly selects missed integration/non-default folders, preserves API54/import checks, and requires genuine installed normal/-O public paths plus substantively authored architecture/guides. |
| A6 | 0.75 | 9.5 | 0.7125 | Current Office decision, source/span rules and retained directive sections 3.1/3.3 preserve meaningful content, order/provenance, format-local refusal, exact final-token budgets and complete-plan validation. Partial backend effects never earn a complete receipt; cache eligibility remains destination/incarnation/collection/record-bound. |
| A7 | 0.75 | 9.6 | 0.7200 | Shared-contracts dependency/asset bindings and file-map metadata rows put counters in LLM, conversion in Tools and the default document edge in Chat. Headless profiles avoid Docling. Certifi floor, narrow lock deltas and asset provisioning remain explicit. TOOLS-DOC routing/test exceptions stay separately owned. |
| A8 | 0.75 | 9.6 | 0.7200 | README slice boundaries, validation phase selectors and uncompleted approval gates provide feasible additive I1, coordinated I2 and shared ingestion I3 sequencing. Worker proof follows worker construction at C4; final installed checks, aggregate implementation review and human UAT remain distinct later duties. |

**Exact sum: 9.575/10.** The individual-seat numerical threshold is met with zero mandatory findings. This does not establish that other seats passed.

## Mandatory gaps and future proof

None found in this bounded design assessment. Consequently there is no mandatory repair or invented additional readiness experiment. Existing assigned acceptance remains required: genuine extraction and source/store comparison; positive supported configuration routes; full-batch role/count/vector checks; namespace/recovery isolation; cache destination drift; real subprocess IPC, cancellation and process accounting; actual Chat/Runtime cleanup; and clean installed normal/optimized profiles. Missing implementation receipts today are not design defects or evidence that those requirements have passed.

The detailed future node selectors and synthetic fixture/classification expansion must be bound before their phase executes, as validation-plan lines 35–39 require. Setup/import failures cannot count as semantic refusal witnesses. The final impact revision and exact maintainer approval remain uncompleted artifacts, with concrete gate owners/timing; this review does not supply their signatures.

## Separate advisories

1. Keep a short construction checklist derived from the existing C4 state table, particularly ownership after a refused bind and entry-close failure followed by converter cleanup. This is an implementation aid; the normative obligations and witnesses already exist.
2. Preserve explicit “configured identity” wording in operator examples. A declared server alias cannot detect an undeclared backend swap. The design documents that limit and requires a new declared identity/fresh namespace for a model change; no additional serving experiment is recommended.

## Evidence and limits

The first action computed request SHA256 with Python standard library before reading it and matched `19c218ef08b8dd4d0bb409e9ab24348218441cc42293c86741871385c11c4dfd`. All 16 required input pins plus the declared current-controls/controller-check pins matched. Controller checks were treated only as identity metadata, never semantic proof. Required prose was read fully; truncated output was recovered with bounded reads. Maps were inspected through complete selected path/owner/exit views, distinct assignment meanings, mapped nodes/assertions, all planned witnesses, module/helper classifications and fixture oracles. No archive or baseline inventory was reconstructed.

Targeted supplementary reads resolved retained format/cache/dependency requirements in the directive, relevant REM acceptance rows, and existing Chat frozen-lifecycle/Runtime shutdown seams. These are interface/context checks, not product conformance. No memory, history, prior/peer reports, private reasoning, raw navigation/authority inventories, nested delegates, product execution, installs, network/provider/model/store calls or repairs were used. Finance’s excluded integration file was neither read, parsed nor executed. Protected user state was accessed solely for the eight expressly declared metadata/hash checks.

Entry and exit evidence record logical index before status with optional Git locks disabled and Python bytecode disabled. HEAD, branch, status, empty staging, required pins and all eight preserved records match the frozen request at both boundaries. Only this seat’s new external scratch was written. See `entry.json` and `exit.json` beside this report.

This is the final authorized seat. Hand back for maintainer feedback. No replacement/seventh council, construction, effects, acceptance or delivery authority follows.
