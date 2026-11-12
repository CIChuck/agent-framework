# Docling behavior evaluation — measured results

Builder execution complete; **independent implementation review pending**.
Source candidate `24d15ab5`. This is a standalone document-behavior result,
not full Friday installed-profile, embedding/storage or production qualification.

Actual private stack: **Docling 2.150.0, RapidOCR 3.10.0, Certifi 2026.10.23**.
Standard uv resolved 106 packages and installed wheels in a private target.
Certifi's >=2026.10.19 floor passes after installation. All 18 selected local
layout/table/OCR/tokenizer assets verified. No alternate reader supplies text.

## Raw behavior stays visible

The original 30 genuine synthetic files were converted, not merely dispatched.
Counts below include expected refusal cases as passes; they do not count supported
files. “Characterized” is observation, not a compatibility guarantee.

| Format | Cases | Pass | Characterized | Fail |
| --- | --- | --- | --- | --- |
| PDF | 6 | 5 | 0 | 1 |
| DOCX | 6 | 5 | 1 | 0 |
| XLSX | 10 | 6 | 0 | 4 |
| PPTX | 8 | 7 | 1 | 0 |

The five raw failures matter:

- PDF: the first page marker was classified as header/furniture and omitted from
  default body-only Markdown. Parsed JSON retained it; explicitly exporting both
  body and furniture restored all three page markers.
- XLSX: hidden rows/columns were included, and missing/error formula caches were
  accepted. These four cases require fail-closed admission with the current plan;
  successful conversion alone is insufficient.
- Separately, the default HybridChunker emitted no chunk for the scanned PDF's
  isolated heading. `always_emit_headings=True` preserves that OCR text.
- Default chunk serialization omits furniture and notes. A public Docling
  serializer configured for body/furniture and unambiguous PPTX notes preserves
  the required content. PPTX comments stay excluded.

DOCX extra parts and a PPTX external relationship were characterized explicitly.
The configured profile retains DOCX body/table content but does not establish
headers/footer/comment support. It refuses the external relationship before
conversion rather than allowing a remote fetch. No personal document was used.

## Configured extraction and actual chunk content

The final committed runner executed **37 cases in each of normal and optimized
Python**: the original 30 plus corrupt PDF/DOCX/XLSX/PPTX, an oversized PDF, an
excess-page PDF and a mismatched Office extension. Each mode reports 26 pass,
1 characterized and 10 expected admission refusals, with no unexpected failure.
The 26 include six native empty/error refusals; 21 meaningful documents reach the
chunker. Admission, native reader rejection and setup failure stay distinct.

The chunk matrix uses those 21 documents plus six generated text/Markdown/code-JSON/
CSV/TSV/web-tool payloads: **27 sources ×3 strategies ×4 limits =324 cases per
mode**, all passing both final prepared token limits and independent content
oracles. The limits are 64, 128, 512, 1024; quick runs default to 512.

`document` uses Docling's public HybridChunker. `recursive` and `fixed` are test-only
policy prototypes. Fixed/recursive preserve exact serialized source characters;
Docling's contextualized chunks are checked for required and prohibited source
markers. The Nomic v1.5 local tokenizer counts `search_document: ` plus special
tokens without truncation. No LM Studio counter agreement or vector quality is
claimed. Refused, empty, failed, partial and stale outputs cannot enter the
admitted matrix.

## Repeating the behavior pipeline

The disposable run is `.friday_test/runs/docling-behavior-20261112/`. The code
lives under `tests/readiness/ingest/`; a matching frozen copy is in the run's
`source/ingest/`. Run the following from any directory, substituting absolute
paths. These commands neither install packages nor contact a model service:

```text
<base-python> -I -S -B <run>/source/ingest/behavior.py evaluate --run-root <run> --chunk-tokens 64 128 512 1024
<base-python> -I -S -B -O <run>/source/ingest/behavior.py evaluate --run-root <run> --chunk-tokens 64 128 512 1024
<base-python> -I -S -B <run>/source/ingest/behavior.py report --run-root <run>
```

Qualified base binary:
`/Users/chuckrussell/.local/share/uv/python/cpython-3.13.10-macos-aarch64-none/bin/python3.13`.
The [runner README](../../../../../../../../tests/readiness/ingest/README.md)
explains options and retained controls. Reruns replace owned semantic reports;
separate command logs remain. Preserve a report copy first when comparing runs.

## Validation and limits

- 57 retained minimal tests plus 8 behavior tests: **65 pass per mode**.
- Existing parser selector 6 positive/39 refusal and engine 7 positive/24 refusal
  controls pass per mode. They remain offline historical capabilities, not
  prerequisites for direct Docling evaluation.
- Focused Ruff, format on 27 Python files and private mypy on 27 sources pass.
- Six Python-visible isolation checks pass per mode. Conversion uses local assets
  with network denied. Resource caps are sampled, not an OS sandbox guarantee.
- Protected production files, both dirty YAMLs, `.venv`, lock, stores and exports
  remain unchanged. **LM Studio/embedding requests:0; Chroma stores created:0.**
- Earlier import setup, serializer-constructor and report-joining mistakes are
  retained as attempts and earn no semantic correctness credit. The full raw
  matrix and default chunking limitations are retained, not edited into passes.
- Repository-wide baseline debt remains unwaived; unchanged product suites and
  live services were not rerun for this test-only component.

The [evidence index](evidence-index.json) binds the compressed raw reports, fixture
originals, logs, frozen source, independent oracles and command receipts. Model
assets and third-party packages are excluded from the committed archive; their
selected versions/digests are retained. Later Friday-LLM/LM Studio and disposable
Chroma checks must qualify the same prepared inputs before full readiness. The
existing framework-wide compatibility obligations remain open.
