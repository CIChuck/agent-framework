# Large-document corpus — generated assets

**Version2 correction prepared; independent delta/full review pending.**
Source `f17b3d32`. [LD-REM-001](LD-REM-001.md) corrects LD-CORPUS-001: the
first corpus repeated the middle key in its tail. The key now appears only in
the middle, with the release code only at the end; neither section alone supplies
both answers. Publication and actual native-text validation enforce that relation.
The original corpora and [first review](validation/round1/review-report.md) remain
unchanged; old data receives no cross-section-control credit.
There are20 distinct native documents (PDF, DOCX, XLSX, PPTX at five lengths)
and5 UTF-8 reference texts. The corpus occupiesthe source bytes recorded in the version2 manifest; compressed
Office files are small despite their substantial text content.

| Sections | Canonical words | PDF pages | XLSX sheets | PPTX slides |
| --- | ---: | ---: | ---: | ---: |
|16 |1,368 |2 |1 |4 |
|64 |5,304 |8 |1 |16 |
|128 |10,552 |16 |2 |32 |
|256 |21,048 |31 |4 |64 |
|384 |31,544 |46 |6 |96 |

These are **words, not Qwen tokens**. Exact token counts remain unset until the
matching tokenizer and serving profile are qualified. A large source still needs
chunking: test document/512 first, then explicitly compare larger budgets rather
than assuming a whole document should become one vector.

Fictional Orion procedures carry unique section IDs, known opening/middle/tail
facts, a provisional route explicitly revoked at the end, and cross-section
authorization questions. This controlled procedural-template corpus is useful
for completeness, truncation, source-reference and retrieval controls; it is not
a representative real-corpus semantic-quality benchmark. Supplied real documents
could later complement it through separate explicit copied-input manifests.

Normal and optimized generation produce byte-identical documents, reference text,
oracles and manifests. In both modes, real private PDFium, python-docx, openpyxl
and python-pptx readers validate all25 files: every section body, every unique
section ID and all known facts are recovered. Native page/sheet/slide counts
match. This does **not** claim a new Docling conversion, chunking, Qwen inference
or storage pass. No model calls, downloads, installs or production changes occur.

All native parses additionally enforce section order and actual two-section
answer distribution. An integrity-valid DOCX with the middle key appended to its
tail passes file verification, then fails native semantic validation with the
required one-section-sufficiency refusal. [Exact negative witness](cross-section-negative.json).

The largest PDF's first, middle and last pages were rendered using the existing
private PDFium installation and visually inspected: no clipping or overlap found.
The PNGs retain physical margins; their nonwhite bounds stay inside the pages.
This is a representative PDF layout check, not exhaustive Office rendering.

The actual corpus is at
`.friday_test/runs/large-documents-20261112-v2-normal/inputs/corpus/`.
An identical optimized copy is in the corresponding `-optimized` run. The files
are named `orion-016` through `orion-384` with format extensions. `oracles.json`
contains facts/questions; `manifest.json` binds source and every asset hash.
Both complete copies and reproducible source/receipts are retained in the
[compact archive](evidence-v2.tar.gz), with [member hashes](evidence-index-v2.json)
and [measured facts](facts-v2.json). Dependencies are excluded. Manual commands are
in the [harness README](../../../../../../../../tests/readiness/ingest/README.md).

Offline regressions88 per mode, focused Ruff/format and private mypy31 sources
pass. Prior evaluated `behavior.py`, `e2e.py` and existing fixtures retain exact
bytes. Known repository debt remains unwaived; broad product suites were not
rerun for this test-only addition. Native validation uses a Python audit guard,
not an OS sandbox; native-library I/O retains that declared limitation.

Next: fresh LD-CORPUS-001 delta and full [LD-01–08](criteria.md) review, then qualify Qwen's embedding-serving
mode and tokenizer before any larger-context inference comparison. A production
model switch remains a separate decision. Whole Gate-A9.5, product construction,
acceptance and delivery are not granted here.
