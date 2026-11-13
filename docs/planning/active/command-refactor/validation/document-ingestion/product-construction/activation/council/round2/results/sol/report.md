# SOL independent document review — INGEST activation council, round 2

Candidate: c24ff0998010e960fb86c1a89b150ada079bbd46. Verdict: **CHANGES_REQUESTED**.
assessment_complete=true; areas_assessed=8/8. Overall design score: **9.25/10**.
Mandatory findings: **1**. This assessment is complete; the score is assigned after assessing all eight areas. The 9.5 quality gate is not met. No separate coverage score is assigned.

## Correction requirements assessed first

**C1 — satisfied.** The overview, readiness dispositions, validation plan and I3 assignments apply the removed model/parity prerequisite directly. Requirement-reconciliation explicitly disposes of DI-24: local asset integrity, deterministic effective-input counting, preparation and overflow guards remain; actual-serving parity does not. B/N/R denotes ordinary baseline/replacement/refusal operations. Older parent wording is expressly superseded rather than silently carried forward.

**C2 — satisfied.** Shared-contracts section 3 makes configured records admissible with null serving/parity evidence. Declared hosted identity has an explicit canonical model/revision basis; aliases and endpoint settings are excluded appropriately. Out-of-band alias swaps are explicitly undetectable and require operator declaration changes and fresh namespaces. I1 owns resolver/schema support, I2 binds selected default/pool/legacy paths, and ordinary positives require actual local counter assets. Batch/order/dimension/finiteness and capacity checks survive. No remote qualification experiment is required by this interpretation.

**C3 — satisfied.** Core PreparedEmbeddingService and Memory's required embedder argument close the dependency handoff. The factory checks destination/counter/embedder space agreement. Memory validates the complete plan, calls the injected broker, validates the complete batch independently and only then writes. A named headless integration witness composes Tools, LLM, Memory and disposable Chroma without Chat. No hidden global broker is implied.

**C4 — materially corrected, with F1 remaining.** I3-C4 follows construction and precedes acceptance. Cold/repeat latency, process-tree RSS, heartbeat, queue capacity, frame limits and TERM/KILL/reap bounds are explicit. Failed quiescence retains cleanup ownership and prevents admission. However, the exact launch mechanism does not agree with its selected file path and lacks the described IPC stream wiring.

**C5 — satisfied at design level.** Runtime has an explicit public registration method, read-only slots, successful ownership transfer, same-pair idempotence and rejection of incompatible rebinding. Chat independently receives entry/converter dependencies through its existing lifecycle. Close ordering and retained cleanup tasks are specified. The case map gives separate responsiveness, repeated-cancel and actual FridayChatApp.run shutdown assertions, plus /read workbook refusal and the Runtime registration/shutdown witness. No app.py modification or private RuntimeKernel access is inferred.

## Weighted A1–A8 assessment

Contributions are earned points against the approved maximum weights, not a second numerical coverage grade.

| Area | Maximum | Contribution | Evidence and outcome |
| --- | ---: | ---: | --- |
| A1 | 1.50 | 1.5000 | Current decisions and explicit reconciliation remove stale prerequisites; approval-binding leaves all activation gates incomplete. Satisfactory. |
| A2 | 1.75 | 1.6625 | Shared-contracts sections 1–3/5 define immutable values, strict serialization, injected counter/broker/store and source/plan/receipt identity; digest examples cover space, preparation drift, Unicode, plan and receipt. Strong. |
| A3 | 1.75 | 1.4000 | Shared bounded process service, session lifetime, cancellation and frontend-neutral close are coherent; exact launch/IPC defect F1 prevents fully buildable execution. Changes required. |
| A4 | 1.50 | 1.4250 | Legacy call shapes and I1 behavior preserved, I2 coordinated switch, positive consumer matrix, fresh namespace and strict v1/v2 recovery specified. Strong staged acceptance. |
| A5 | 1.25 | 1.1250 | Exact source owners/exits, 49 bounded case exceptions, retain default, helper/live classifications and 41 named witnesses; substantive guides and installed normal/-O proof required. Worker entry mapping needs F1 reconciliation. |
| A6 | 0.75 | 0.7125 | Source-backed coverage, hidden-workbook refusal, complete-plan capacity checks, destination receipts and truthful partial effects preserved. Strong. |
| A7 | 0.75 | 0.7125 | LLM counter assets, headless profiles, Tools extra/default Chat stack, Certifi floor and separate TOOLS-DOC routing responsibilities are clear. Strong. |
| A8 | 0.75 | 0.7125 | Additive I1, coordinated I2 and integrated I3 have feasible exits; independent implementation review and human UAT remain later gates. Strong. |
| Total | 10.00 | **9.2500** | One mandatory buildability correction remains. |

## Mandatory finding F1 — reconcile executable worker entry and IPC wiring

**Evidence:** shared-contracts.md lines 274–295 specifies an exact subprocess launch with `-m friday_tools.document_ingestion`, says the entry is in the already mapped Tools module, and assigns stdout framed IPC/stderr bounded diagnostics. The complete slice-file-map instead selects only `packages/friday-tools/src/friday_tools/filesystem/readers/document_ingestion.py` (line 1343) for the converter/worker. It selects no top-level `friday_tools/document_ingestion.py` shim. Its scope rule disallows unexpected source paths without reconciliation. Also, the shown create_subprocess_exec call supplies no stdin/stdout/stderr pipes or alternate connected descriptors; inherited streams do not supply the parent-owned framed control/result channel described immediately below it.

**Requirement violated:** Review A3/A5 and C4 require an exact, buildable process mechanism within the selected implementation scope. A builder following the selected file cannot launch it under the stated module name. Following the stated module requires an unselected source file; following the shown stream options leaves the declared IPC mechanism disconnected. This is a document inconsistency, not a demand for an already implemented worker.

**Bounded fix:** Tools/design owner should choose one canonical import/entry path and make the subprocess module, constructor documentation and exact file map agree. The smallest apparent path adjustment is to launch the selected nested module, subject to preserving the documented lazy/headless import boundary. Alternatively bind an explicitly approved shim path. Specify stdin/stdout/stderr pipe wiring (or exact owned descriptors), with concurrent bounded result/diagnostic draining and the existing frame limits. Rebind the affected planning hashes before construction approval. No new vendor study, model campaign or framework audit is necessary.

**Required future acceptance:** At I3-C4 and the already planned installed normal/-O lanes, actually launch the selected installed module with its exact argv/environment, complete a framed control/result exchange, exercise bounded stderr and malformed/oversize messages, and demonstrate cancellation/reap with no inherited terminal publication. This extends the existing headless subprocess/IPC witness rather than creating a new pre-coding gate. I did not execute it.

## Separate advisories

When final A5 selectors are expanded, keep process diagnostics and control/result drains explicit in the witness so a child blocked on a full stderr pipe cannot invalidate cancellation assumptions. This is implementation test detail supporting F1, not authority for another benchmark project. Preserve the distinct positive operations and refusal controls: deterministic dimension-correct vectors prove guards, not embedding efficacy or actual server parity. The document already makes that distinction accurately.

## Boundaries, evidence and limits

The request was SHA256-verified with Python standard-library hashlib before its content was read. All 15 required input pins, target/common instructions and the supplied safe controls/controller-checks pins matched. Full required prose and focused complete mapping views were inspected; repeated JSON rows were read by selected fields, and truncated views were recovered. Controller checks were not executed or treated as semantic correctness evidence.

Targeted source reads inspected the existing Chat lifecycle close seam and Runtime DI shutdown seam. Focused optional directive/REM sections resolved dependency profiles, non-Docling ownership, cache invalidation and destination receipt requirements. No whole-framework source review, historical provenance reconstruction or product conformance claim was made. Existing source lacking proposed APIs is expected staged construction, not a finding.

Entry and exit capture the logical index digest before status, with optional locks disabled and bytecode disabled. HEAD, branch, index, status, staging, all required pins and all eight declared preserved metadata entries match their frozen expectations. Only declared hashes/metadata were obtained for protected entries; their contents were never interpreted. Private entry.json and exit.json preserve the minimal boundary record.

No product import/test/build/install, network/provider/model/store operation, admin suite, excluded Finance file read, user-state content inspection, repository/input write, delegation or repair occurred. No memory, history or peer result was consulted. This verdict concerns document readiness only. It grants no construction, effects, acceptance, push, deployment or delivery authority. This single seat stops here.
