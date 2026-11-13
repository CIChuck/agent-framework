# Large-document corpus — generated assets

**Version 2 independently VERIFIED for corpus preparation.** The [fresh review](validation/round2/review-report.md) closes LD-CORPUS-001 and passes LD-01–08 on frozen candidate `4735e3e1`. The actual generation source is `f17b3d32`. This result covers native validity and offline controls; Qwen inference remains pending.

The corpus contains 20 genuine PDF, DOCX, XLSX and PPTX documents at five controlled lengths, plus five UTF-8 reference texts. Each size uses the same source content across formats so extraction results can be compared.

| Sections | Canonical words | PDF pages | XLSX sheets | PPTX slides |
| --- | ---: | ---: | ---: | ---: |
| 16 | 1,368 | 2 | 1 | 4 |
| 64 | 5,304 | 8 | 1 | 16 |
| 128 | 10,552 | 16 | 2 | 32 |
| 256 | 21,048 | 31 | 4 | 64 |
| 384 | 31,544 | 46 | 6 | 96 |

These are **words, not Qwen tokens**. Exact token counts remain unset until the matching tokenizer and serving profile are qualified. Large sources still need chunking; a larger model limit permits measured chunk-budget comparisons, rather than establishing that a whole document should become one vector.

Fictional Orion procedures contain unique section IDs, known opening/middle/tail facts, a provisional route explicitly revoked at the end, and questions requiring evidence from separate sections. The corpus provides controlled completeness, truncation, source-reference and retrieval tests. It is not a representative real-document benchmark for semantic quality. Supplied real documents could later complement it through explicit copied-input manifests.

[LD-REM-001](LD-REM-001.md) corrects the first corpus, whose tail repeated both answers to a cross-section question. In version 2 the calibration key appears only in the middle and the release code only at the end. Neither section alone supplies both answers. Publication and validation of actual native text enforce this relation. An integrity-valid DOCX with the middle key appended to its tail passes file verification and then fails native semantic validation. The [negative witness](cross-section-negative.json) records that distinction. Original corpora and the [first review](validation/round1/review-report.md) remain preserved; original data receives no cross-section-control credit.

Normal and optimized generation produce byte-identical documents, reference text, oracles and manifests. Real private PDFium, python-docx, openpyxl and python-pptx readers validate all 25 files per mode, recovering every section's complete body, ordered ID and known facts. Native page, sheet and slide counts match. The largest PDF's first, middle and last pages were rendered and inspected with no clipping or overlap. This is representative PDF layout evidence, not exhaustive Office rendering.

The corrected files are in `.friday_test/runs/large-documents-20261112-v2-normal/inputs/corpus/`, with an identical optimized copy in the corresponding `-optimized` run. Names range from `orion-016` through `orion-384`. `oracles.json` contains known facts and questions; `manifest.json` binds source and asset hashes. Both copies and their reproducible source/receipts are retained in the [compact archive](evidence-v2.tar.gz), with [member hashes](evidence-index-v2.json) and [measured facts](facts-v2.json). Dependencies are excluded. Manual commands are in the [harness README](../../../../../../../../tests/readiness/ingest/README.md).

All 88 offline tests pass per mode, with focused Ruff/format and private mypy on 31 sources. The independent report distinguishes fresh executions from inspected typing evidence and other receipts. Earlier evaluated `behavior.py`, `e2e.py` and fixture bytes remain unchanged. Broad product suites were not rerun; known repository debt remains unwaived. The audit guard covers Python-visible effects and is not an OS sandbox.

No new Docling conversion, chunking, embedding or storage pass is claimed for these documents. There were no model requests, installs, downloads or production changes. Next, qualify Qwen's embedding-serving mode and matching tokenizer before a reserved isolated comparison. Whole Gate-A 9.5, product construction, model selection, acceptance and delivery remain separate decisions.
