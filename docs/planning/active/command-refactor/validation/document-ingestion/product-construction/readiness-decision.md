# INGEST — measured readiness and construction handoff

Version: **0.1 draft**, 2026-11-12; source baseline `8c36d8e2`.

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

## Remaining activation decisions and evidence

Each row closes by exact proof or an explicit approved contract/impact amendment.
It is not resolved by silently changing a fixture, disabling a subsystem or
presenting refusal alone as backwards compatibility.

| ID | Open item | Required bounded disposition |
| --- | --- | --- |
| RD-01 | Framework-wide embedding readiness | Complete source-linked call-site/configuration B01–08 and FC-01–14 matrix, public/direct openers and active/public/absent route dispositions. Qualify maintained baseline configurations with omitted new fields and their exact artifact/preparation/counter facts; require actual baseline and replacement-model positive operations plus refusals. Current Nomic E2E does not qualify all services, consumers or a replacement model. |
| RD-02 | Hidden-row/column and Office selection contract | The measured profile refuses workbooks containing unsupported hidden rows/columns; the approved REM requires exclusions with truthful coverage. Prove the exclusion/Docling-provenance mapping, or present a specifically worded conservative-refusal amendment and revised impact for Chuck. No such amendment is approved here. Also freeze factory's explicit sheet/range/hidden selection and notes/comment distinction for the companion. |
| RD-03 | Limits, resources and interruption | Qualify the selected byte/page/sheet/cell/slide/expanded-archive ceilings, numeric runtime/disk/RSS bounds, cold/warm timings and cancellation/quiescence against genuine boundary fixtures. Native guard is not an OS sandbox. The large corpus provides new inputs, not completed boundary/worker proof. |
| RD-04 | Exact shared API and namespace/recovery data | Freeze runtime-validated immutable contracts, exact per-slice file list, source/chunk/receipt metadata, local counter interface, identity/digest vectors, fresh-path origin, graph/query envelopes, ready-marker publication and strict nested v1/v2 recovery. Bind a complete asset/provisioning manifest without new import cycles. Existing source public call shapes remain preserved. |
| RD-05 | Token/model boundary | Nomic E2E observed loaded context 2048 and 768-dimensional finite vectors. Local preparation counts include prefixes/special tokens, but LM Studio usage returned zero: server/local equivalence is unqualified. Establish exact model-bound counter/limits and boundary/overflow evidence without treating zero usage as verification. Actual new calls need a new authorized window; the old consumed ledger is immutable. |
| RD-06 | Product and Tools installation/provenance | Qualify default Chat with document extra, bare Tools text use, Tools-with-profile without Chat, Commands-only, and counter-enabled headless Memory/Runtime/CLI/Agent. Re-resolve the exact compatible graph, assets/licenses/origins, extra names and proposed lock delta. A private test target is not an installed product closure or proof of factory pagination. |
| RD-07 | Migration, documentation and final readiness gate | Expand the exact phase/node/oracle maps from the baseline inventory; classify offline/live modules and retain all valid obligations. Complete the architecture/guide evidence matrix and scope any measured impact amendment. Obtain the required aggregate readiness review with the established 9.5/no-mandatory-findings gate, then bind Chuck's exact construction approval. No council is activated by this drafting instruction. |

These are requirements of the existing REM/assessment, not a request to repeat
all package-metadata experiments. Reuse byte-bound suitable evidence, execute
missing named behavioral witnesses, and distinguish inspections from fresh runs.
Document current unknowns accurately. Preparation of the implementation directives
can proceed while these dependent activation items remain open.

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
