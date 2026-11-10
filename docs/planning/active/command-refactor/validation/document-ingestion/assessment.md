# PDF/DOCX ingestion — source assessment

Baseline: `7ad916f2530f0417e6c9fc6e9774fc96d0844f2e`.
[Reproducible observations and source hashes](assessment.json).
This is planning evidence, not a repaired-candidate validation result.

The supplied assessment is correct. `SmartFileReader.read` selects a placeholder
for PDF, DOCX and XLSX; `_ingest_handler` passes its content to the memory port.
A guarded probe invoked the actual registry on corrupt PDF/DOCX and observed
`Ingested file`, chunks1, with placeholder text delivered to a capture-memory
double. It did not use a real store. Two genuine text-bearing source fixtures
also return placeholders, and quoted paths containing two consecutive spaces
are split before reading and fail as missing files. `--lines=1` is ignored by
the placeholder path. The real two-page PDF is reported as one page there.

The existing Tools readers demonstrate real extraction: the PDF contains both
distinct page markers; the DOCX contains both paragraph markers and table text.
The DOCX reader orders paragraphs before tables rather than preserving their
interleaving. An image-only PDF returns empty text without error. A simulated
PDF page decode error returns an in-band diagnostic string with `success=True`.
Simply connecting those readers would therefore leave another false-success
route. The proposed Docling adapter must explicitly reject failed/partial/empty
conversion before memory ingestion, with no diagnostic text in its payload.

The workspace currently has pypdf6.6.0 and python-docx1.2.0. Their presence here
does not prove default installation support: Tools declares them in an optional
`documents` extra and Chat does not request it. The dependency contract must be
explicit in the repair. Docling is not yet installed or proven in this workspace.

Shared ownership remains necessary: Tools owns conversion, Commands owns scoped
path interpretation, Memory owns existing chunking/storage, and Chat delegates
and renders. The accepted optional-description metadata repair is already in
place and must remain unchanged. Existing placeholder records may exist; no
user store was inspected, and no cleanup is authorized by this assessment.

[Proposed remediation](../../remediation/REM-CMD-INGEST-001-pdf-docx.md).
