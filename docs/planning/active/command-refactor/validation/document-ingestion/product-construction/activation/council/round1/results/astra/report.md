# ASTRA — activation-package council, round 1

- Candidate: `b04ab83afda313630eaaaa4e1dab09b71d9ce59c`
- Branch: `feature/cmd-ingest-001`
- assessment_complete: **true**
- areas_assessed: **8/8**
- Verdict: **CHANGES_REQUESTED**
- Mandatory findings: **2**
- Overall: **8.60/10**

The package is substantial and mostly coherent, but the exact public ingestion factory cannot obtain the prepared vectors required by its own storage interface, and the worker qualification timing remains ambiguous enough to obstruct bounded construction. These are planning defects with bounded document fixes. Missing future implementation, unexecuted future tests and absent final human approval are not findings. This score is assigned after assessing all eight areas; it is not a council average or rounded qualification. The seat does not satisfy the qualifying rule.

## Assessment

Paths below are relative to `docs/planning/active/command-refactor/validation/document-ingestion/product-construction/activation/` unless stated otherwise. Contributions are earned points against the brief's assigned weights, not separate overall scores.

| Area | Weight | Contribution | Assessment and evidence |
|---|---:|---:|---|
| A1 | 1.50 | 1.40 | Current decisions and construction status are explicit in the three decision records, authorization.json and approval-binding.json. Model qualification removal and workbook rejection control older prose. Historical proposal wording does not invalidate launch. Some operational wording remains difficult to navigate; see advisory. |
| A2 | 1.75 | 1.25 | shared-contracts.md §§1–3 gives immutable neutral values, strict loading, Unicode spans, identity hashes and complete-batch checks. The factory omits the embedding dependency needed to complete that flow: F1. Five digest examples cover space/preparation changes, Unicode, plan and receipt. |
| A3 | 1.75 | 1.50 | shared-worker-decision.md and shared-contracts.md §4 provide Tools ownership, typed progress, one active/one queued session, busy refusal, queued cancellation, termination escalation and Runtime drain. Actual embeddings stay outside the child. Feasibility timing needs reconciliation: F2. |
| A4 | 1.50 | 1.40 | shared-contracts.md §§2,5 preserve call shapes, stage the guarded switch, preserve explicit path origins, reject unbound stores and define strict v1 inspection/v2 active recovery. Case-map compatibility witnesses include positive operations and negative controls, independent ephemeral namespaces, MCP retries and truthful maintenance outcomes. |
| A5 | 1.25 | 1.15 | File map assigns source, metadata and authored guides to slices/exits; case map names 49 exceptions and 40 planned witnesses with retain-by-default rules. Helper/live classification, genuine fixtures, installed normal/optimized proof and explicit nondefault selectors are substantive. These are assignments, not proof that implementations pass. |
| A6 | 0.75 | 0.70 | Source-backed context versus coverage, complete-plan validation, no silent clamp/tail loss, typed partial effects and readback-confirmed receipts are well specified. Office decision requires actionable whole-workbook refusal before conversion. REM cache requirements bind destination, incarnation, collection and retained record provenance. |
| A7 | 0.75 | 0.70 | Shared contracts §3 and directive §3.1 assign LLM counters and Tools document assets to explicit manifest roots. Core/Commands remain neutral; Memory's narrow counter dependency avoids imposing Docling on headless installations. Default Chat document extra and legacy Tools extras remain distinct. TOOLS-DOC routing stays separate. |
| A8 | 0.75 | 0.50 | I1 additive contracts, I2 coordinated consumer switch, I3 common ingestion and AG→human UAT are coherent. Independent slice approvals and effects bindings remain explicit. The product-worker preactivation requirement conflicts with its later implementation/acceptance allocation: F2. |
| Total | 10.00 | **8.60** | Complete assessment; mandatory findings remain controlling. |

## Mandatory findings

### ASTRA-R1-01 — missing embedding dependency in the exact Memory factory

**Location:** shared-contracts.md §2, protocol table, especially lines 81–90; §3 complete-plan/batch-before-write rule; slice-file-map.json entry for `friday_memory/ingestion/document_ingestion.py`; test-case-map.json `test_headless_document_ingestion_uses_injected_tools_planner` and `test_headless_common_plan_and_destination_bound_receipts`.

**Evidence:** The exact factory accepts `destination`, `vector_store: PreparedVectorStore`, `counter`, defaults and an optional counter factory. `TokenCounter.prepare` produces `PreparedInput`, never vectors. `PreparedVectorStore.write_prepared` requires a completed `PreparedBatch` and exposes no embedding operation. `IngestionEntry.ingest` accepts source/options/session/observer, also without an embedding dependency. The additive LLM `embed_prepared` method is specified separately, but no protocol or parameter connects that service to this factory. None of the exact injected dependencies can produce the batch that the entry must validate and submit.

**Requirement:** A2 requires exact neutral protocols, injected dependencies and complete data flow. The shared-worker decision assigns embeddings to the LLM broker outside the conversion worker and policy/orchestration to Memory. The headless entry must operate through its public contract, without reaching into an undocumented concrete store field, global service or frontend object.

**Bounded fix:** Add a neutral prepared-embedding protocol and explicit factory dependency, or another equally explicit public handoff that supplies the batch while preserving Memory's complete-plan validation. Assign the implementation to the existing LLM service and bind it at composition roots. Specify identity agreement with the counter/destination, batch validation and cancellation/error propagation. Update the relevant existing map rows; no new frontend or engine is needed.

**Future acceptance implication:** I1 should establish the protocol and LLM implementation shape; I3 should instantiate the public headless factory with only its declared dependencies, embed through the parent-side injected broker exactly once, validate the whole batch before any write, and verify malformed vectors cause zero storage. Ordinary offline implementation tests suffice; this does not require model/parity qualification or live calls.

### ASTRA-R1-02 — worker feasibility has no unambiguous construction-stage disposition

**Location:** shared-contracts.md §4 lines 247–268; readiness-disposition.md RD-03 and “Proposed numeric interpretation” lines 54, 65–76; approval-binding.json gates A1/A2; parent phase-evidence-map.md “Ordering and authority,” stage table and I3-C4; file/test maps' Tools worker and headless lifecycle assignments.

**Evidence:** The proposed process/session is explicitly subject to measured feasibility “before activation.” RD-03 still asks to qualify the proposed worker, spawn/IPC/local counter, cancellation, deadline and termination grace. The numeric interpretation likewise says to qualify before activation. The referenced stage model places Q before I1 and requires A1–A5 before each slice. Yet the concrete worker is assigned to I3, with genuine shared-service progress/cancel/timeout/backpressure and Runtime-drain witnesses also at I3-C4. The parent allows standalone upstream resource probes at Q, but these documents do not distinguish which narrower fact such a probe would resolve from the actual proposed worker behavior, or explain why ordinary I3 acceptance cannot resolve it. The updated binding keeps shared resource/lifecycle acceptance required without identifying its timing clearly enough to settle this conflict.

**Requirement:** The common brief explicitly requires feasible, noncircular timing and forbids requiring completed product-worker code before authorizing its creation. Any extra pre-coding experiment must name a specific unresolved risk and explain why established evidence or normal implementation tests cannot answer it.

**Bounded fix:** Give RD-03 an explicit staged disposition: identify reusable established ceilings/profile facts and place product spawn/IPC/cancel/drain/resource measurements at the named I3 acceptance exit, before acceptance of that slice. If one narrow pre-coding probe is actually indispensable, name its risk, owner, artifact, limits and justification without depending on the uncreated product worker. Update the activation wording and binding so “activation” cannot mean either construction permission or post-build acceptance. Preserve the lifecycle safeguards and no-late-output/storage obligations.

**Future acceptance implication:** Construction permission need not certify the worker. Acceptance must exercise the actual shared service, including queued cancellation, timeout escalation, failed quiescence, no late storage and Runtime shutdown. A standalone proxy probe cannot substitute for that product acceptance.

## Separate advisories

1. Consolidate the readable current disposition of removed model qualification when next revising this package. I applied the explicit override and did not treat retained RD-01/RD-05 campaign text, the README's hosted-identity “next” step, or copied parity language in map rows as live instructions. The schema's evidence fields and existing-evidence reuse would benefit from an explicit interpretation alongside that override. Do not restore qualification under a new name or create a later mandatory campaign; preserve runtime safeguards and ordinary compatibility tests.
2. Several planned witness rows repeat broad exit prose. When binding phase selectors, sharpen each node's individual assertions, especially application cancellation versus headless lifecycle. The validation plan already requires this preparation, so the present lack of executable test bodies is not a mandatory defect.

## Inspection and preservation

The request was SHA256-hashed before reading; it matched `5c23e6db6eb72299cf8821ce4b53413468fd663bce9e14dce45cbc1690ceaf50`. The common brief matched `784d0f97fe2faf5699ed583ed3f751471995b6362f8f5d890c576c5a923c2894`. All 13 required input pins, the sanitized current controls and supplied controller-check pin matched at entry and exit. All required prose/decision/binding inputs were read. Focused JSON views covered all selected paths/owners/slices/exits, grouped repeated case mappings, all planned witnesses, helpers, fixtures and exclusions. Truncated output was recovered with bounded reads. Digest values were inspected as design examples, not executed as product tests.

Targeted optional reads answered dependency-profile, cache-binding and phase-timing questions in directive §3.1, REM cache/receipt requirements and the phase map. The only product-source inspection was Runtime `di.py`'s shutdown seam: it currently stops MCP and clears boot state, and the map explicitly assigns the required I3 extension. Its present lack of worker draining is expected future work, not a finding.

At both boundaries `GIT_OPTIONAL_LOCKS=0` and bytecode suppression were set. Logical `git ls-files -s -z` hashing preceded status. HEAD/branch matched the request; logical index was `ef217e835738dc266e88c4380d9720f75fa79590865d5e87f2bc53f38e6c618a`; staging was empty; the two dirty Chat examples and untracked `.friday-old/` status remained exact. All eight declared metadata/hash entries matched. Entry/exit receipts reside beside this report in new physical external scratch.

Controller admin results were inspected once as supplied structural evidence, not reproduced or used as semantic correctness proof. No memory, prior/peer report, raw authority/history, private reasoning or delegate inventory was read. No prohibited Finance file, dirty/state/secret contents, product import/test/build/install, network/model/store operation, archive audit or harness replay occurred. Only private scratch was written. This document verdict grants no construction, effects, UAT, acceptance or delivery authority. This seat ends after this single report.
