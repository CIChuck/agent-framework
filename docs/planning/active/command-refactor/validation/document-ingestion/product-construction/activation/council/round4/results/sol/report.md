# SOL independent read-only INGEST activation design review

Candidate: `a4b18fe5743ea8543bd000f6f85d8225d4dbb676`, branch `feature/cmd-ingest-001`.
Additional pass 1/3; global round 4/6. Seat: SOL. Workdir: `/Users/chuckrussell/Dev/gendev/agent-framework`.

**VERIFIED — assessment_complete=true; areas_assessed=8/8; mandatory_findings=0; overall=9.57/10.**

This is an independent assessment of the proposed activation design at these exact bytes. It supplies no construction, effects, human acceptance, publication or delivery authority. The overall score was assigned after completing E1–E5 and the full A1–A8 assessment. No prior or peer verdict was used, no seat averaging applies, and the score is not rounded upward to meet the gate.

**Neutral correction assessment, completed first**

E1 — Satisfied as a design requirement. Shared-contracts section 3, “Document-conversion settings binding,” specifies public Tools resolver/factory signatures in the already selected document_ingestion module. Explicit absolute settings_path wins over the single supplied FRIDAY_DOCUMENT_CONVERSION_MANIFEST environment value; invalid explicit input cannot fall back. The strict independent settings record binds asset manifest, profile and scratch root. The resolver bounds local reads, rejects malformed/escaping bindings and performs no spawn or directory creation. Binary hashing occurs in the owned worker before use. Neither Memory nor the embedding manifest is needed for document /read; plain text does not resolve either document binding. I3-C1 owns the resolver, I3-C3 composition, I3-C5 installed/operator documentation. The case map names strict resolver and plain-text-preservation witnesses, plus genuine installed positive conversion through the same binding. These are substantive acceptance assignments, not controller-hash claims.

E2 — Satisfied as a design requirement. Shared-contracts section 4 explicitly acknowledges that nested-module execution runs the existing parent initializers before worker setup. Their silence/offline behavior and startup cost are included in installed launch, cold-time and RSS acceptance. The module retains a protocol descriptor and redirects fd 1 before heavy imports; stderr is continuously drained with bounded retention. The version-1 envelope/state table defines open/opened, plan/planned, progress, close/closed and failure, with wrong attempt, unknown keys/version/kind and invalid or duplicate transitions refusing. Actual installed connected-pipe exchanges and malformed/oversize/EOF tests are assigned to I3-C4 in ordinary and optimized lanes. No bootstrap or initializer edits are inferred.

E3 — Satisfied as a design requirement. Section 3 retains capability_record_sha256 from the selected deployment record in resolved capabilities and LocalTokenCounterFactory. Every create reads one bounded buffer, verifies that retained hash, then parses those same bytes; transfer retains the expected hash. The two named I1-C2 tests cover strict manifest containment and factory-byte drift, while actual cross-process mutation is assigned to I3-C4. Validation-plan explicitly includes the unchanged simple-vector regression module at I1; its mapped fixture adaptations remain I2 work.

E4 — Satisfied as a design requirement. Section 4 puts mutable bindings, retained tasks and closing state in typed _OwnedIngestionState within existing adapters.py under the public frozen lifecycle wrapper. Binding and request-start transitions are ordered against close using a short synchronous lock without awaiting under it. Converter-only binding supports lazy /read, registration precedes open, rejected registration preserves caller ownership, and a later entry must use the same converter. Ordered entry/converter/client cleanup and repeated-cancel drain are assigned to the actual application and Runtime witnesses. Existing frozen lifecycle and no-argument builder source were inspected; this is a buildable extension of those seams, not a claim that the extension exists.

E5 — Satisfied for this pass. Optional YAML additions and both independent manifest bindings are distinguished. Current approval-binding lists parent/appendix identities, leaves A1–A5 incomplete and denies product generation. Requirement reconciliation explains superseded model/Office/worker obligations. The current extension changes only council budget to rounds 4–6. Older three-round language is explicitly subordinate; it does not invalidate this authorized seat or expand technical scope.

**Full bounded assessment**

Weights sum to 10. Each contribution is weight × area rating / 10; the one overall score is their exact sum.

| Area | Weight | Rating /10 | Contribution | Evidence and judgment |
| --- | ---: | ---: | ---: | --- |
| A1 | 1.50 | 9.7 | 1.4550 | README activation status, three decisions, reconciliation and incomplete approval gates preserve selected Docling, remove parity campaign, narrow XLSX behavior and stage worker acceptance honestly. |
| A2 | 1.75 | 9.6 | 1.6800 | Shared-contracts §§1–3/5 define immutable values, strict loaders, identities, resolver precedence, explicit broker/factory/store injection and full-batch validation; digest vectors distinguish canonical JSON from raw content bytes. |
| A3 | 1.75 | 9.5 | 1.6625 | Shared-contracts §4 and shared-worker decision define one shared Tools service, bounded queue, typed progress, cancellation, deadlines, retained drains and headless ownership. Real startup/IPC and failed-reap proof remains necessary at I3-C4. |
| A4 | 1.50 | 9.6 | 1.4400 | Additive I1 and coordinated I2 preserve legacy positives until guarded switch. Exact routes support defaults/pool/non-pool/legacy with omitted YAML fields; explicit origins, namespace admission, ephemeral isolation and strict v1/v2 recovery are assigned. |
| A5 | 1.25 | 9.5 | 1.1875 | Complete selected file assignments and semantic case-map review establish owners/exits, narrow exceptions, retain default, helper/live exclusions and meaningful replacement positives. Installed normal/-O proof and authored guides have explicit duties. |
| A6 | 0.75 | 9.5 | 0.7125 | Complete-content admission, structured spans/context, exact counting, whole-batch preflight, truthful partial outcomes and readback receipts are explicit. Directive §3.3 retains destination/incarnation/provenance-sensitive cache eligibility; Office amendment has actual command refusal/positive controls. |
| A7 | 0.75 | 9.5 | 0.7125 | Directive §3.1 and readiness RD-06 retain narrow LLM counter support, Tools document extra, default Chat dependency, Certifi floor, provisioned assets and headless independence. TOOLS-DOC routing remains separately bounded. |
| A8 | 0.75 | 9.6 | 0.7200 | README slice boundaries, validation plan and maps sequence I1 foundations, I2 consumer switch and I3 extraction/adoption/lifecycle/install work; exact approval/effects, aggregate review and human UAT remain later gates. |
| Overall | 10.00 | — | **9.5700** | **8/8 assessed; zero mandatory findings.** |

The principal design strength is that extraction, planning, embeddings and storage have distinct explicit owners without losing one end-to-end identity chain. A converted source remains in its owned session; Memory receives neutral source/plan data, invokes injected dependencies, validates the entire embedding batch and only then attempts storage. Refusal tests supplement positive compatibility flows. Fresh-store and recovery constraints are not treated as repair permission. Source-backed context can repeat while coverage remains complete, and ambiguous backend effects cannot yield a success receipt.

**Mandatory gaps and fixes**

None identified within this bounded design review. No remediation is requested. Future implementation and acceptance remain required at the assigned exits; their present absence is not scored as a missing design artifact or demanded as a pre-coding experiment.

**Separate advisories and required future evidence**

1. Preserve the real installed launch witness as written. Inspection confirms that the Tools parent initializer eagerly imports filesystem and finance surfaces. Early module redirection cannot protect output emitted before module entry. The design acknowledges this and requires silent/offline supported-profile startup with its cost counted. Keep the stop-for-scope-reconciliation outcome if the unchanged initializers cannot satisfy that witness; do not substitute an argv mock or a new bootstrap. This is an implementation risk with an actionable test, not an established present design contradiction.
2. Keep converter-only lifecycle tests distinct from admitted-ingestion tests. Exercise bind/start versus close and repeated cancellation through actual Chat application shutdown, including failure to establish quiescence. The typed holder and ownership-transfer rules must remain observable in the implemented API.
3. At phase approval, bind the promised exact selectors, dependency/assets and helper classifications. Retain-default is not permission to run an unclassified live module. Broad future witness names must expand into concrete assertions and ordinary positive operations, as validation-plan requires. Configured identities must retain their documented inability to detect an undisclosed server alias swap.

**Evidence and limits**

Python standard-library SHA256 verified request.json against `d8bc163d63a0c37309676e5df7cf9d34f8278491a481ab1d3596bb1926bb2ded` before reading it. The current extension was then read at its declared repository path before the common brief and substantive inputs. All 16 required input pins, plus declared control-file pins, matched. Control files were used only for identity metadata, never semantic correctness proof.

All required current documents and the full semantic mapping scope were inspected; repeated mapping rows were condensed without rebuilding inventory. Targeted source inspection covered the existing Chat lifecycle/builder and runtime composition references, Runtime shutdown references and Tools parent initializers. Focused directive §3.1/§3.3 reads resolved dependency, format and cache questions. No exhaustive source or parent review was attempted. Output truncation was recovered with bounded and deduplicated views.

No product import, test, build, install, network/provider/model/store operation, AST/archive/provenance audit or administrative suite ran. No memory/history/peer reports, excluded Finance integration contents, dirty YAML or private state/credential contents were read. Declared preserved files received hash/metadata checks only. No delegates, repairs or further pass occurred.

Entry and exit logical index hashes were obtained before status with optional locks disabled; both equal `2f3eb131a2a684bfc95663d61e4a9070ed3c40d3a3913c37cd85e4d1245ec934`. HEAD, branch, status and empty staging matched the request at both boundaries. All eight preserved records and all required pins remained unchanged. Bytecode was disabled. Only this newly created physical private scratch was written; entry.json and exit.json contain minimal boundary evidence. This single seat stops here.
