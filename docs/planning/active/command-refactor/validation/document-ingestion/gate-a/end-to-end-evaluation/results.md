# Docling → embeddings → storage: actual end-to-end results

Builder execution **PASS in normal and optimized Python**; fresh independent
review pending. Test source is committed at `c9777736`. Production source,
configuration, working environment and stores remain unchanged.

| Check | Normal | Optimized |
| --- | --- | --- |
| Genuine converted documents | 5: native/scanned PDF, DOCX, XLSX, PPTX | Same |
| Corrupt PDF / missing formula cache | Refused; absent from embedding corpus and storage | Same |
| Document/512 collection | 41 chunks across 5 documents and 6 supplemental payloads | 41 |
| Document/128 override, long DOCX | 40 chunks | 40 |
| Actual Friday-LLM calls | 4 document batches, 5 queries | Same |
| Actual Nomic responses | 86 vectors, 768 finite dimensions | Same |
| Retrieval checks | All 5 expected sources rank 1 | All 5 rank 1 |
| Separate-process reopen | Text/provenance and 5 retrieval ID lists identical; networking denied | Same |
| Offline harness tests | 74 pass | 74 pass |

All four formats were ingested through real Docling. The scanned PDF used actual
OCR. Supplemental text/Markdown/CSV/TSV/code/JSON/web-tool payloads test normalized
content only; they do not establish a new web or automatic tool ingestion route.
The default DOCX produced 7 chunks versus 40 with the smaller override.

Across both modes the broker sent **18 embedding POSTs**, yielding **162 document
vectors and 10 query vectors**. The 54 actual HTTP requests include 36 read-only
model-state observations. Including the 3 earlier status observations reserved in
the window ledger, budget usage is **57/64 requests, 172/256 vectors and
41,556/131,072 locally counted prepared tokens**. No retry, load, unload, server
restart or configuration change occurred. The loaded-instance fingerprint stayed
unchanged before and after each embedding batch/query.

The already-loaded model was `text-embedding-nomic-embed-text-v1.5`, with observed
context 2048. Nomic document/query prefixes and special tokens were counted before
requests; actual inputs stayed within the selected chunk budgets. LM Studio
returned token usage **0**, so server/local token-count equivalence is **not
qualified**. Successful bounded inference is not proof of semantic retrieval
quality or overflow behavior at the model's context ceiling. Retrieval queries
reuse known source text and establish source/persistence consistency only.

Docling defaults alone did not meet the earlier behavior matrix. This flow uses
the verified public furniture/heading/notes serialization options and conservative
Office admission checks described in the [behavior results](../behavior-evaluation/behavior-results.md).
The shared Memory adapter receives exact extracted chunks and source hashes;
absent descriptions stay absent. Query vectors use its public precomputed-vector
seam, avoiding the existing legacy query-as-document embedding path. No product
code or production embedding convention was corrected by this test.

The private combined profile contains Docling **2.150.0**, Docling Core **2.106.0**,
RapidOCR **3.10.0**, LiteLLM **1.100.1**, Chroma **1.4.0**, Certifi **2026.10.23** and
the four genuine Friday Core/Telemetry/LLM/Memory **0.1.0a4** wheels built from
`96f752d6`; package source is unchanged in the test-source commit. Standard private
resolution/install was used. One initial setup attempt retained the standalone
python-dateutil 4.0.0 constraint, conflicting with the existing Friday-LLM/botocore
constraint; allowing the compatible 2.9.0.post0 resolved it. A later import smoke
check used the module name instead of distribution name and failed only its
version lookup; the actual fully guarded imports and pipeline succeeded.

Ruff check/format pass on 29 harness Python files; private mypy passes all 29.
The retained parser/engine controls pass in both modes. Administration passes
board/dashboard, documentation, package metadata and whitespace. Preservation
checks pass 18,574 protected files, 26 symlinks and 8 retained local records.
Existing whole-repository debt remains unwaived and was not rerun for this slice.
The Python audit guard is not an OS sandbox; native-library isolation has the
previously declared residual limits.

[Exact facts](facts.json), [evidence index](evidence-index.json) and
[compact evidence](evidence.tar.gz) retain source, fixtures, commands, actual
transport/result receipts and both disposable stores. Dependencies/model assets
are excluded. The test runner's [manual commands](../../../../../../../../tests/readiness/ingest/README.md)
require a prepared private run and current operator window. A new complete run
needs sufficient separately reserved budget; do not reset this consumed ledger.

The next gate is a fresh bounded independent review against [EE-01–08](criteria.md),
then reconcile these readiness findings into the product construction directive.
This is not production `/ingest` execution, whole Gate-A 9.5 qualification,
maintainer acceptance or delivery.
