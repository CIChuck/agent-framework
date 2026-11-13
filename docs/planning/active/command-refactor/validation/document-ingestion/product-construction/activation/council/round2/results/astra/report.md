# ASTRA — INGEST activation package, round 2

Verdict: **CHANGES_REQUESTED**. assessment_complete=true; areas_assessed=8/8. Overall design score: **9.39/10**. One mandatory finding. This is a complete independent document-readiness assessment of candidate `c24ff0998010e960fb86c1a89b150ada079bbd46`, not an implementation verdict or construction authorization. The 9.5 gate is not met, and the mandatory finding independently prevents VERIFIED.

## Correction assessment first

C1 is addressed. README lines 3–6 and 90–102, readiness RD-01/RD-03/RD-05, validation lines 31–33 and 52–54, and requirement-reconciliation rows 11–15 apply the decisions directly. DI-24 is expressly reconciled. Baseline/replacement/refusal operations are ordinary implementation tests; neither live serving identity nor parity is moved into a later mandatory campaign. Approval-binding keeps all activation gates incomplete and does not mistake this council for authorization.

C2 is addressed. Shared-contracts section 3 admits configured records with null historical evidence fields, defines declared artifact identity for hosted models, excludes endpoint/alias/credential knobs from space identity, and explicitly acknowledges the undetectable unchanged-alias swap. I1 owns resolver support; I2 binds selected default/pool/legacy routes and their local assets. Exact counting, capacity, complete response indices, dimensions, finiteness and fresh-space protections remain. Default compatibility must be demonstrated positively rather than achieved by disabling unresolved consumers.

C3 is addressed. Shared-contracts lines 88–117 define the required injected PreparedEmbeddingService, its space and method, the public Memory factory, space agreement and whole-plan/whole-batch validation before writes. The headless document witness explicitly composes Tools, LLM and Memory into a disposable Chroma destination without Chat. No hidden broker, global client or Tools-to-LLM dependency supplies embeddings.

C4 is substantially addressed, with the mandatory exact-path conflict below. Timing is noncircular: build at I3-C1, prove at I3-C4, then accept I3. The document specifies subprocess execution, bounded frames, process-group termination, memory limits, timing, heartbeat, admission and failed-reap behavior. No pre-coding experiment is required. However, the literal worker launch target is inconsistent with the selected implementation file.

C5 is addressed at design level. Shared-contracts lines 328–361 provide Runtime registration, ownership transfer, same-pair idempotence, rejection during shutdown, retained cleanup and ordered closure. Chat has its own optional lifecycle injection and closes shared services before LLM clients. The case map gives individual responsiveness, cancellation, application shutdown, Runtime shutdown and /read workbook-refusal assertions. These are future acceptance requirements, not completed proof.

## Complete weighted assessment

Contributions below are awarded directly against the approved maximum weights. They total one overall design score; there is no separate coverage score and no averaging of seats.

| Area | Weight | Contribution | Outcome and evidence |
| --- | ---: | ---: | --- |
| A1 | 1.50 | 1.48 | Satisfied. Current reconciliation, decisions, README and approval-binding consistently distinguish planning approval, implementation acceptance and later human authority. Historical wording is explicitly subordinated. |
| A2 | 1.75 | 1.70 | Satisfied with advisory. Exact immutable values, strict loading, injected broker/counter/store contracts, full-batch checks and source/plan/receipt identities are specified. Digest examples support field coverage; the Unicode example could be labelled more precisely. |
| A3 | 1.75 | 1.50 | Changes required: F1. Ownership, queue bounds, cancellation, failure quarantine and shared headless lifecycle are otherwise concrete, but the executable module must match the mapped worker. |
| A4 | 1.50 | 1.46 | Satisfied. I1 preserves legacy calls; I2 switches maintained consumers together. Configured records, guarded fresh namespaces, explicit origins, per-kernel ephemeral isolation and strict v2 recovery prevent silent migration or fallback. |
| A5 | 1.25 | 1.10 | Changes required: F1 crosses the exact file map. Otherwise mapped old-case oracles, opt-in helpers, installed normal/optimized probes, named public witnesses and substantive guide work provide actionable coverage. |
| A6 | 0.75 | 0.73 | Satisfied. Whole-workbook refusal, meaningful content, source-backed coverage/context, exact budgets, complete-plan refusal and truthful partial results are preserved. Parent cache rules bind completed destination storage and revalidate admission. |
| A7 | 0.75 | 0.72 | Satisfied. Core/Commands stay neutral; LLM owns local counter records/assets; Memory consumes the narrow counter dependency; Tools owns the optional document stack. Default Chat and headless profiles remain distinct; TOOLS-DOC routing is separate. |
| A8 | 0.75 | 0.70 | Satisfied subject to F1. I1 foundation, coordinated I2 integration, I3 extraction/adoption/worker acceptance, aggregate review and UAT have feasible ordering. Exact impact/assets/effects approvals remain later explicit deliverables. |

The deductions reflect design precision and the executable-path defect. The score is not rounded upward to the quality threshold. Future test absence is not treated as a defect in this planning candidate.

## Mandatory finding F1 — worker entry point contradicts exact file scope

**Evidence:** shared-contracts.md lines 274–279 mandates `asyncio.create_subprocess_exec(sys.executable, '-I', '-B', '-m', 'friday_tools.document_ingestion', '--worker', ...)` and says the entry is in the already mapped Tools module. But slice-file-map.json `files[86].path` selects only `packages/friday-tools/src/friday_tools/filesystem/readers/document_ingestion.py` for the document worker, at I3-C1/I3-C4. No selected path supplies `friday_tools/document_ingestion.py` or a package at that top-level name. The map's rule forbids unexpected helper/source paths without reconciliation.

These are different Python module names. A builder following the selected file cannot satisfy the literal launch command. A builder adding the top-level entry would exceed the declared exact scope. This is an internal design conflict, independent of whether future worker code has been written. It violates Review A3's buildable shared-process mechanism and A5's exact file assignment requirement, and leaves C4's exact subprocess mechanism incompletely reconciled.

**Bounded fix:** align the command with `friday_tools.filesystem.readers.document_ingestion`, keeping its worker entry in the selected file, or explicitly select and approve the top-level bootstrap file and reconcile affected scope/dependency/import claims. Choose one canonical launch/import path and use it consistently in the shared contract, factory documentation and installed witness. This requires a planning correction, not a new vendor study or pre-coding execution gate.

**Required future acceptance:** the existing I3-C4 headless worker test and I3-C5 installed normal/optimized lanes must launch the exact selected module using the specified isolated subprocess invocation, from a request directory outside the source tree. Require genuine conversion, framed IPC and cancellation/reap behavior with installed origins and no source-path fallback. A mock that merely checks argv does not establish this. These checks remain post-build obligations.

## Optional advisories

1. In digest-vectors.json, `text_content_unicode` hashes canonical JSON containing a content field. Shared-contracts lines 53–56 correctly define content_sha256 as the raw UTF-8 text hash. Rename the example to clarify that it demonstrates canonical JSON escaping, or add an explicitly labelled raw-content hash example. The current normative rule is clear, so this is not another mandatory finding.
2. The proposed 8 GiB process-tree RSS threshold is concrete but still requires an operational monitor. When implementing the existing I3-C4 witness, record sampling behavior and descendant accounting alongside the required peak/timing/profile evidence. This clarifies the existing acceptance record; it does not create a preliminary benchmark or broaden the package scope.

## Inspection and limits

The supplied request SHA256 was verified with Python standard-library hashlib before its contents were read. A newly created physical temporary directory outside the checkout and supplied inputs holds this report and entry/exit evidence. All fifteen required current-input hashes, the safe-controls hash and controller-checks hash matched at entry and exit. The common brief and current authorization were read in full. The controller-checks file was hash-checked only; no administrative result was used as semantic correctness evidence.

I read the required prose and approval binding, all selected file assignments, all mapped case dispositions and all planned witnesses. Repeated JSON rows were inspected through focused/grouped views, with truncated output recovered by bounded subsequent reads. I inspected the five digest examples for contract meaning, without claiming product serialization execution. Targeted directive excerpts resolved cache eligibility, dependency/profile ownership and stage boundaries; its supplied pin matched. I read only narrow current source seams in Chat adapters, Chat app and Runtime DI. They confirm an existing independent Chat lifecycle builder, awaited registry-result publication and Runtime shutdown seam. They do not prove the proposed implementation.

Entry and exit identity matched: HEAD and branch as requested, logical index digest `db67d02d4cbc6554e0ac2ae6b6176fa24113dbd7cdde07c34fab82de6aeca694`, unchanged declared dirty status, empty staged diff. Logical index was obtained before status with optional locks disabled; Python bytecode was disabled. All eight declared metadata entries, including allowed file hashes, matched. Evidence is in entry.json and exit.json beside this report.

No memory, history, peer reports, raw authority/navigation, inventory archives, prohibited Finance source, user YAML/state/credentials or preserved directory contents were inspected. No product tests/imports/builds/installs, network, providers, models, stores, repairs or delegates ran. Only private scratch was written. This seat stops here. The verdict grants no construction, effects, acceptance, publication or delivery authority.
