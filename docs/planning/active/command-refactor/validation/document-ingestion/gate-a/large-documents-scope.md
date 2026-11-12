# Large-document corpus — bounded test-only preparation

Chuck requests larger documents to exercise Qwen's extended embedding context and
expects Friday may adopt that model later. This controller amendment records the
explicit request within the approved isolated readiness-harness work. It does not
select a production model or authorize model management, inference or stores.

Add only `tests/readiness/ingest/large_documents.py`, its focused test module,
the minimal `stages.py` selftest selector and local README instructions. Generate
fresh private assets under `.friday_test/runs/large-documents-<id>/inputs/corpus`.
Reuse the committed stdlib container writers, preserving their bytes. Production
packages, configuration, dependencies/lock, existing corpora, evaluated runs and
model assets remain unchanged. No download or production/personal-document scan.

Build five controlled lengths (16,64,128,256,384 sections) in each of PDF, DOCX,
XLSX and PPTX:20 genuine files, with five UTF-8 reference texts and independent
start/middle/tail facts, explicit supersession and cross-section retrieval queries.
Use varied fictional technical content, identifiable section IDs, workbook sheet
boundaries and slide/page counts. No real user data or repetitive binary padding.
PDFs remain native text; reuse earlier OCR evidence rather than claiming a new
large-scanned-document test. Respect existing50-page/100-slide/32-sheet and32MiB
per-file bounds; all new retained corpus data is capped at16MiB.

Words, characters and native units are measured. Qwen token counts remain null
until the exact tokenizer/serving profile is qualified. Do not label approximate
word counts as8K/32K tokens or claim these documents fit a particular model.
The later comparison keeps document/512 defaults, then explicitly tests larger
chunk budgets, with Qwen-only fresh stores and actual Friday-LLM communication.
Those inference/chunking/storage operations are not part of this preparation.

Publish to a new directory only, write the hash manifest last and refuse existing
output, symlinks, hardlinks, unexpected files, changed input bytes or source
binding. Failed preparation must not acquire a success manifest. Verify generated
Office structure and actual PDF text with existing private native readers; no
alternative reader supplies production ingestion text. Optional native validation
reads only the declared existing private dependency target, writes only the new
run and denies Python-visible network/child effects; retain native-I/O limits.

Required checks: deterministic generation; content/fact and length progression;
real native-format/unit/whole-section/anchor validation; tamper/source/publish
refusals; normal/-O offline tests; focused Ruff/format and typing; preservation and
administration. Freeze a stable candidate and obtain one fresh read-only validator
under repository policy. No automatic council or whole-readiness9.5/production/
acceptance/delivery claim. Approved historical directives/evidence stay intact.
