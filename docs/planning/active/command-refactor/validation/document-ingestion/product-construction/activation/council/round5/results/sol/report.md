# SOL independent read-only design review — INGEST activation

Candidate: `34981199842ef73891605a20f3b4275eeb37e943`; branch `feature/cmd-ingest-001`.
Global round 5/6, additional pass 2/3. This is one fresh seat, ending with this report.

**VERIFIED. assessment_complete=true; areas_assessed=8/8; mandatory_findings=0. Overall design score: 9.5775/10.**

The proposed package provides a coherent, bounded basis for the next exact activation approval decision. This verdict concerns design, not implemented conformance. Gates A1–A5 remain incomplete in approval-binding.json; no construction, effects, human acceptance, publication or delivery authority follows. Scores below were assigned after completing all eight areas. Contribution equals area weight multiplied by area judgment divided by ten; the total is exact, without rounding up or averaging across seats.

## Correction assessment first

**F1 — satisfied.** test-case-map.json classifies the new Commands test_file_inputs.py as offline, assigns the direct `test_parse_file_input_rem_c_semantics_and_document_option_refusal` witness to I3-C3, and states concrete quoting, opaque-description, option-order, lexical refusal and no-effects assertions. validation-plan.md includes that module directly. Its retained_regression_selectors preserve test_import_boundary.py and the actual `test_memory_query_specs_exports_and_factory` API54 node unchanged, both at I3-C3. The existing node really checks exact root exports and cardinality 54; the import module contains fresh-interpreter and optimized checks. Runtime test_di.py is classified and included in the I3 selector, with the new shutdown node at C4. These are planned acceptance selections, not claims of execution.

**F2 — satisfied.** shared-contracts.md section 3 distinguishes schema/settings errors (`readiness`) from declared manifest/profile hash mismatches (`identity`). The loaded settings digest provides traceability without inventing externally authenticated settings. Section 4 explicitly supplies runtime=None document /read with the same Tools factory, request-entry environment snapshot and locally retained try/finally cleanup. The frozen lifecycle wrapper's custom constructor seeds exactly one mutable typed holder; accessors read that holder. No stale constructor copies remain in the design. Named C3/C4 tests cover plain text independence, local ownership, bind/close ordering and repeated cancellation.

**F3 — satisfied.** Section 3's XLSX preflight is Tools-owned, bounded to 64 KiB or 64 structural records per cooperative batch, includes cancellation and the cold deadline, and precedes converter spawn. It supplies structural facts only. C4 heartbeat coverage explicitly includes preflight. Section 4 defines the converted/planning/planned state transition and rejects duplicate plans, invalid frames and terminal misuse. RSS uses the already declared psutil dependency, tracked PID/create-time identities and recursive descendants, <=100 ms sampling, conservative RSS summation and failure on lost accounting. Installed and headless witnesses cover these obligations after construction.

**F4 — satisfied.** The current extension permits rounds 4–6 and overrides only the common brief's old round-three cap. Authorization, overview and reconciliation preserve scope, roster, weights, early success stopping and the six-round maximum. Historical stop wording does not create a new restriction or permission for a replacement/seventh round.

## Full weighted assessment

All evidence references below are relative to the activation directory unless a source path is identified.

| Area | Weight | Judgment /10 | Contribution | Evidence and assessment |
| --- | ---: | ---: | ---: | --- |
| A1 | 1.50 | 9.8 | 1.4700 | README, reconciliation, three decisions and approval binding agree on selected Docling, removed serving/parity campaign, workbook refusal, shared worker and unactivated construction. Final impact approval is explicit. |
| A2 | 1.75 | 9.6 | 1.6800 | shared-contracts sections 1–3/5 define immutable values, strict loading, injected counter/broker/store, source/profile/plan/receipt identities and independent validation. Digest examples distinguish canonical JSON from raw content. |
| A3 | 1.75 | 9.5 | 1.6625 | Section 4 fixes subprocess/IPC ownership, queue bounds, deadlines, invalidation, TERM/KILL/reap, unhealthy cleanup and headless reuse. Runtime and Chat close ownership is explicit. |
| A4 | 1.50 | 9.5 | 1.4250 | Sections 2/3/5 preserve old call shapes, I1 legacy behavior and coordinated I2 transition, positive defaults, origin suppliedness, fresh namespace admission and strict v2 recovery. |
| A5 | 1.25 | 9.5 | 1.1875 | Slice map, case map and validation plan assign exact owners/paths/exits, retained oracles, narrow fixture exceptions, parser/import/API54 witnesses and actual installed normal/-O proof plus authored guides. |
| A6 | 0.75 | 9.6 | 0.7200 | Complete source coverage, provenance, explicit format refusals, no dropped tail or silent budget clamp, destination-bound receipts and truthful partial/unknown storage effects are specified. |
| A7 | 0.75 | 9.6 | 0.7200 | Tools owns converter/assets, LLM owns narrow counting support, Core/Commands remain neutral; selected directive section 3.1 specifies document extra/default Chat and headless counter profiles. TOOLS-DOC routing remains separate. |
| A8 | 0.75 | 9.5 | 0.7125 | README and validation plan sequence additive I1, coordinated consumer I2 and extraction/plan/command I3, then aggregate review and human UAT. Worker proof is C4 after build; exact approvals/assets/effects precede execution. |
| Total | 10.00 | — | **9.5775** | All eight areas assessed; no separate coverage score. |

## Aggregate buildability and compatibility

The dependency direction is implementable without a frontend-owned engine: Core declares neutral contracts; Tools owns the conversion/session process; Memory validates and orchestrates the common plan; LLM embeds outside the child; composition injects dependencies. Converted source and vendor structure remain within one owned session, so planning does not reconvert. Read-only display needs neither counter nor Memory admission. Headless composition uses public factories and admitted store.destination rather than RuntimeKernel internals.

The process design identifies a real installation constraint: Python executes parent package initializers before worker setup. Inspection confirmed the Tools initializers eagerly import existing surfaces. The design explicitly includes that setup in time/RSS accounting, requires silent/offline initialization, redirects worker stdout before heavyweight imports and stops for scope reconciliation if existing seams fail. It does not pretend an argv mock proves launch. This is an appropriate installed implementation gate, not grounds to require a pre-coding experiment.

Compatibility is positive as well as negative. Existing embed method return shapes remain, default/pool/non-pool/legacy routes need configured local records, and the case map preserves CRUD, vector equality, caching, telemetry, descriptions and listing oracles. New refusal controls supplement these positives. Namespace identity includes preparation changes even when dimensions match; fresh roots and explicit origins prevent accidental adoption. Recovery keeps v1 inspection separate from active v2, reparses participant artifacts and refuses foreign incarnation/layout rather than restamping. None of this establishes runtime correctness before implementation.

## Mandatory findings and optional advisories

**Mandatory findings: none.** No bounded document fix is required by this seat. Future acceptance remains required exactly at the mapped exits; VERIFIED does not waive any witness.

Optional advisory 1: Make installed C4 receipts easy to inspect by showing initializer/setup, audit, conversion and planning intervals alongside total cold time and RSS sample quality. The design already requires the underlying facts. This improves diagnosis without changing limits or creating a new experiment.

Optional advisory 2: When authoring C5 operator examples, pair a working embedding-independent /read binding with a missing-binding refusal and a plain-text positive. Keep the distinction between declared model identity and attested server identity prominent. These examples are already within the selected guide work; no extra source scope is proposed.

## Evidence, boundaries and limits

The request SHA256 was computed first using Python standard library and matched `77b3acddf8f650621bff4bd0917496a3f7cf2602eda52a7134f1fe0cbea2f96f` before request text was read. The extension was then read from its request-declared repository path; the initial attempted same-directory lookup did not exist and read no additional material. All sixteen required input pins matched. Required prose was read in full; repeated JSON map rows were inspected with focused views and distinct rule/assignment views, recovering output truncation. No inventory or archive was reconstructed. Controller checks were not used as semantic proof.

Targeted source reads checked the frozen Chat lifecycle seam, Runtime DI construction/shutdown, Commands import/API54 tests, Tools psutil declaration and worker parent initializers. REM sections B/C resolved concrete format and parser questions; directive section 3.1 resolved dependency-profile responsibilities. No product module was imported and no test, build, install, administrative suite, old harness, provider/model/store/network call or browser operation ran. No memory, prior/peer reports, private reasoning or raw authority/navigation/delegate inventory was consulted. Finance test_integration_massive.py was wholly excluded. Protected user/configuration/state contents were not inspected; declared file hashes and stat metadata alone were checked.

Private physical scratch is outside the checkout and supplied input directories with mode 0700. Entry and exit evidence records the logical index before status with optional Git locks disabled and bytecode disabled. Both boundaries match the candidate, branch, logical index, status, empty staging, required pins and all eight preserved records. The checkout and supplied evidence were not written. This single seat ends here.
