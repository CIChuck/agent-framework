# INGEST — measured readiness and construction handoff

Version: **0.5 final bounded corrected draft**, 2026-11-12; source baseline `8c36d8e2`.

**Engineering recommendation: use Docling with the measured configured profile.**
There is genuine conversion/chunking/embedding/storage evidence, sufficient to
draft the product implementation. **Whole Gate A remains open.** This handoff
does not transform bounded component verdicts into a 9.5 aggregate result or
authorize production changes. The [construction directive](../../../directives/CD-CMD-INGEST-001-product.md)
and separate [Tools companion](../../../directives/CD-CMD-TOOLS-DOC-001-adoption.md)
are conditional drafts for Chuck's review.

## What the tests established

| Measured result | Evidence and exact claim |
| --- | --- |
| Four-format conversion and local PDF OCR | [Behavior results](../gate-a/behavior-evaluation/behavior-results.md): configured 37-case execution per mode, 21 meaningful documents and six supplied payloads entering a 324-case strategy/budget matrix per mode. Genuine source markers, failures and raw-default shortcomings retained. |
| Selected private stack | Docling 2.150.0, Core 2.106.0, RapidOCR 3.10.0/ONNX CPU and Certifi 2026.10.23; 18 local assets verified. These are tested artifacts, not a completed new product lock or all-platform claim. |
| Actual Friday-LLM → Nomic → Chroma | [End-to-end results](../gate-a/end-to-end-evaluation/results.md): native/scanned PDF, DOCX, XLSX, PPTX; 81 stored chunks per mode, five expected sources rank 1 per mode, separate-process network-free reopen. Across both modes 162 document vectors plus 10 query vectors. |
| Corrected evidence binding | Fresh independent reviews closed stale-admission and report-source findings. The original actual inference belongs to its c977 source; later offline reporting correction is not relabelled as a live replay. |
| Long-source controls | [Corrected large corpus](../gate-a/large-documents/results.md): 20 genuine documents plus five texts at five sizes, up to 31,544 canonical words / 46 PDF pages / six sheets / 96 slides. All bodies/IDs/order/facts natively validated; cross-section control corrected and independently closed. No new large-corpus Docling or Qwen inference claim. |
| Isolation | Test code under `tests/readiness/ingest/`; packages/assets/inputs/outputs/stores under isolated test runs. Production source/configuration/working environment/user stores remain unchanged. |

Retrieval queries reused known source text: this establishes source/persistence
consistency, not a general relevance-quality benchmark. Native container validity
does not prove Docling extracted a large document completely. Component advisory
scores remain their reported values; none closes the whole-readiness 9.5 gate.

## Findings that the implementation must carry forward

Docling defaults dropped PDF furniture/markers, omitted OCR-only isolated-heading
chunks, included unsupported hidden worksheet rows/columns and accepted missing/
error formula caches. Default serialization also needs explicit notes/furniture
selection. The configured test profile fixes serialization/headings and refuses
unsafe Office inputs; success is not “install Docling and use its defaults.”

The product profile must retain these corrections, source/coverage provenance,
complete-success admission and source-to-plan binding. Read-only Office structural
inspection supplies no text. Corruption, partial output, empty/OCR-no-text,
missing packages/assets and unclassified clipping cannot enter Memory. DOCX
body/table order is in scope; headers/footers/comments and Office-image OCR are
not implied by native PDF OCR support.

The private combined stack resolved python-dateutil 2.9.0.post0 after the
standalone 4.0.0 constraint conflicted with Friday-LLM/botocore. Its exact
compatible product graph, supported install profiles and unavoidable lock delta
remain required. Certifi must stay at least 2026.10.19 after every installation;
the shared CA-bundle upgrade affects other HTTPS consumers too.

## Qualification before construction versus acceptance afterwards

The [phase map](phase-evidence-map.md) distinguishes **Q** (Gate-A qualification
before product generation), **I1/I2/I3** (approved implementation and scoped exits),
**AG** (full frozen-candidate verification) and **UAT** (human execution after the
required code council). A1 closes only each row's Q disposition. It does not
require new product extras, interfaces, guards or authored current-candidate
guides to exist before permission to build them. Their actual product proofs
remain mandatory at the named exits and aggregate, not waived or relabelled.

Q uses exact upstream packages/assets, unchanged baseline Friday code/wheels,
private dependency feasibility/co-install experiments, model/deployment evidence,
inert proposed requirements and planned source/test/documentation matrices.
These are qualification artifacts, not shipped product metadata. Any separately
permitted private metadata rehearsal retains that label and its own authority;
it cannot establish actual installed-candidate support. No new effects are
activated by this documentation correction.

| ID | Q: required pre-construction disposition | Mandatory implementation / post-build acceptance |
| --- | --- | --- |
| RD-01 | Inventory current source/configuration B01–08 and FC-01–14 callers, direct openers and active/public/absent routes; qualify actual selected deployment **and N-DIM, N-SPACE, N-CAP** identity/preparation/counter/capacity per [replacement qualification plan](replacement-qualification-plan.json). Bind actual immutable identities, required counter assets and evidence in the qualification asset manifest before I1, not only candidate test names. Obtain unchanged-baseline positive operations with the baseline's original conventions in fresh disposable stores, and define candidate B/N/R nodes. **Check B02's hosted text-embedding-3-small immutable-identity risk first**; if unqualifiable, stop for maintainer disposition, without changing defaults, dropping the baseline or calling refusal compatibility. | I1 proves shared capabilities; I2 runs actual integrated existing consumer B/N/R; I3 adds ingestion paths; AG checks the complete trace and representative actual installed normal/-O operations. New-guard refusal tests are not required to exist at Q. |
| RD-02 | Prove the selected converter/audit's hidden-unit/provenance/notes/formula semantics with standalone genuine fixtures, including companion selection needs; alternatively obtain a specifically approved REM/impact amendment for a materially narrower contract. Current whole-workbook refusal is not promised hidden-row/column exclusion. | I3 proves the same admitted scope through actual command/common-entry storage; separately activated TOOLS-DOC proves actual factory sheet/range and smart_read routes. Unsupported exclusion cannot silently become a new exception. |
| RD-03 | Qualify standalone converter/counting ceilings, assets, cold/warm resource envelope and cancellable-work feasibility on genuine boundary fixtures; freeze numeric limits and the planned request/admission/cancellation assertions. Large native-valid corpus alone is insufficient. | I3 runs actual caller event-loop responsiveness, worker ownership/quiescence, before/during/after cancellation and zero late storage; AG checks preserved behavior/resource evidence on the candidate. No OS sandbox or hard native-kill claim. |
| RD-04 | Freeze exact shared contract/schema/signature/digest vectors, phase-specific path lists, proposed source/chunk/receipt and namespace/recovery data, asset/provisioning manifest and planned positive/refusal oracles. No unimplemented protocol earns runtime credit. | I1 implements/tests foundation values, guards and Memory-v2 models; I2 executes actual Chat aggregate and consumer admission; I3 executes the common chunk/receipt path. AG reviews actual old/new public contracts and strict artifact combinations. |
| RD-05 | Qualify the exact served B artifact and each N-DIM/N-SPACE/N-CAP deployment, effective limit, dimensions, synchronous local counter/preparation and actual boundary parity using separately permitted external/unchanged-code probes. One actual deployment may cover multiple scenarios only with explicit per-scenario evidence. Deterministic operational vectors/counter fixtures supplement but never replace actual serving/dependency/counter qualification. Nomic usage=0 is not parity proof; unknown parity still stops Q. Reserve any new live window separately; the consumed old ledger remains immutable. | I1 tests the implemented guard/preparation/batch API against qualified facts; I2/I3 exercise actual integrated callers, final document chunk budgets and refusals. AG installed normal/-O proof distinguishes real serving qualification from deterministic offline vectors. |
| RD-06 | Resolve a compatible proposed package graph and local asset/license/origin set on the target profile, using upstream distributions plus unchanged Friday wheels/code. Rehearse the intended default-Chat/document, bare-Tools, Commands-only and narrow-counter headless dependency shapes as **proposed** requirements, without claiming nonexistent extra names are installed product features. Freeze exact proposed metadata/lock deltas and counter split. | I1 creates/validates its exact LLM/Memory metadata edges; I2 proves real headless candidate Memory/Runtime/CLI/Agent counters; I3 creates and proves actual Tools document-ingestion/default-Chat edges and bare-Tools/shared-extractor behavior. AG repeats or byte-attributes required clean candidate profiles/origins/security checks. Tools public routing/pagination remains the companion's proof. |
| RD-07 | Freeze the initial inventory, planned per-phase case/oracle maps and offline/live classifications, planned requirement→document→source/example matrix, scope/material-impact disposition and exact approval artifacts. Obtain the required whole **readiness** 9.5 review on Q evidence; do not substitute a conditional-directive review. | Each slice proves only its own executed DI-35 migration and changed-contract documentation. I3/AG review whole-suite coverage and actual authored DI-36 content/verified examples. Required post-code DI-12 council follows freeze; human UAT remains a subsequent explicit stage. |

For each Q item record evidence, interpreter/artifact identity, permitted effects
and qualification outcome. A remaining Q unknown still stops dependent activation.
For each constructed item record the source candidate and executed public witness
at its eligible phase. No installed candidate artifact is required before its
approved generation, and no experiment is renamed as final product acceptance.
The underlying REM requirements and whole-readiness threshold remain binding.

## Replacement qualification is an explicit Q dependency

[The qualification plan](replacement-qualification-plan.json) defines logical
scenario IDs, not selected or already-qualified deployments. Before I1, replace
each pending slot with exact immutable model/artifact/preparation and actual
serving identities, dimensions/effective capacity, real offline counter assets/
digests, boundary-parity evidence and approved effects. N-DIM changes vector
dimensions; N-SPACE keeps dimensions but changes model/artifact/preparation;
N-CAP has a smaller effective capacity. Scenarios may share a qualified real
deployment when the evidence establishes each distinction. B is the explicitly
qualified baseline; its old-convention baseline probes and corrected-preparation
profile are distinguished, with separate fresh data where required.

The qualification manifest joins each scenario to B/N/R planned nodes, namespaces,
consumer families and installed lanes. Unknown or fixture-only serving evidence
keeps RD-01/RD-05 Q OPEN and stops A1. No replacement model is selected by this
document; Qwen remains illustrative. No new inference or download is authorized.
The annex permits deterministic operational witnesses after construction; those
remain labelled as operational, never real serving or relevance-quality proof.
I2/I3/AG still execute candidate N positives and refusals after the code exists.

## Canonical impact refinement and materiality

Keep one current `package-impact-assessment.md`. Preserve approved v0.6 in Git;
after Q, refine that same canonical path into a measured new version and obtain
Chuck's satisfaction against its exact hash before construction approval. This
readiness handoff is supporting evidence, not a second assessment. The current
correction leaves v0.6 bytes unchanged.

| Measured difference | Scope/materiality disposition before construction |
| --- | --- |
| Certifi 2026.10.23 and compatible dateutil 2.9.0.post0 | Exact dependency/security refinements inside the planned graph; inventory and review the actual lock/profile delta. They add no package owner or behavior exception, but still bind the final assessment/approval. Shared Certifi affects other HTTPS consumers. |
| Explicit furniture/headings/notes serialization and local OCR assets | Concrete implementation settings for already required source-content semantics; freeze hashes and limits, without claiming all Word/Office parts are supported. |
| Unsupported hidden-row/column whole-workbook refusal | Material narrowing if substituted for the REM's exclusion contract. It requires the explicit REM/impact amendment in RD-02 or proven correct exclusion. No such amendment is approved now. |
| Retained packaged explicit .friday/vector literal | Existing supplied-origin behavior under the approved fresh-store rule, not authority to stamp old data. Explain first-run/upgrade consequences in the refined canonical assessment and guides. |
| Restored B and N preconstruction qualification versus post-build execution | Assessment v0.6's baseline **and replacement** feasibility remains Q, with exact scenario/asset bindings. Earlier Q wording named only the selected deployment; this correction restores the omitted explicit N dependency without changing parent requirements. Candidate N operations stay I2/I3/AG; no readiness or construction approval is inferred. |
| Optional Qwen comparison/model switch | Separate qualification/selection decision, with fresh compatible data. Neither the correction nor Docling selection changes the production default. |

## Model selection and upgrade boundaries

Keep existing pool/default/explicit-service selection. A Nomic-qualified profile
can supply measured baseline evidence; it does not exempt other maintained
services. Qwen3-Embedding-4B is a separate candidate, not a newly selected default.
The [read-only Qwen observations](../gate-a/end-to-end-evaluation/qwen-read-only-assessment.md)
showed MLX instances classified as llm, so an embedding-serving interface, exact
tokenizer/artifact/preparation and effective limits still need qualification.
A reported runtime context does not prove model input capacity. No load/unload,
server/configuration change or Qwen inference is authorized by this handoff.

The approved fresh-store policy remains explicit: preserve old unbound files,
require a deliberately selected coherent fresh destination, and leave `/read`
available. Nomic task-prefix correction is itself a preparation-space change.
No migration, reset, legacy re-embedding or old-placeholder cleanup is included.
Retain the packaged template's current explicit path for the draft, explain its
origin consequence, and never edit either dirty repository example YAML.

## Next reviewable artifact

Review the two conditional directives, measured differences and activation table
together with the approved package-impact appendix. Any new condition is recorded
before the exact final approval. Then activate only a ready bounded slice, build
and independently verify it, integrate the next slice, and finish with actual
public `/ingest`/Tools installed proofs, substantive docs and disposable human UAT.
Product construction, production rollout/model switch, acceptance and delivery
are not granted by this document.
