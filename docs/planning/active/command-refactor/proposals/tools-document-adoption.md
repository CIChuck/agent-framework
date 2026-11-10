# TOOLS-DOC-001 — adopt shared Docling conversion in document-reading tools

Status: **PROPOSED companion work item — no construction approval**.
This is a scoped adoption plan, not a completed tool upgrade or implementation
directive. It depends on the exact shared capability and dependency/model
readiness from [REM-CMD-INGEST-001](../remediation/REM-CMD-INGEST-001-pdf-docx.md).
The maintainer expanded the document scope to **PDF, DOCX, XLSX and PPTX** on
2026-11-10. That four-format scope applies to this adoption plan as well as Chat.
Text and web ingestion are treated as existing capabilities; their redesign or
migration to Docling is excluded. No new validation claim about them is implied.

## Why a separate adoption obligation is needed

Putting the converter in Friday Tools establishes ownership and reuse. Existing
consumers still need deliberate routing changes. Source inspection at `37d789c4`,
confirmed against unchanged product bytes at `f6287faa`, shows:

| Consumer | Current behavior | Proposed adoption |
| --- | --- | --- |
| Chat `/read` and `/ingest` through `SmartFileReader` | PDF/DOCX/XLSX placeholders; PPTX not admitted | INGEST unit uses shared Docling extraction for all four formats. |
| Tools `ReaderFactory` / `get_reader_for_path` | Selects legacy PDF/DOCX/XLSX readers; PPTX reaches binary fallback | Companion unit routes all four formats through typed adapters of the same shared converter. No independent engine/configuration policy. |
| Tools `SmartFileReadTool` (`smart_read`) | PDF/DOCX/XLSX are binary-skipped; PPTX is absent from that binary list and has no document conversion path | Companion unit routes all four formats before binary/text handling, then uses existing small/large-file processing paths. |
| Tools `FileReadTool` (`file_read`) and line readers | Text/encoding/line APIs | Remain text tools; do not silently turn line-oriented operations into document conversion. |
| Direct public `PdfReader` / `DocxReader` / `XlsxReader` callers | Existing specialized reader APIs, including legacy XLSM support | Retain explicit compatibility APIs unless a separately approved contract migration covers them. Do not claim every direct reader caller has migrated. |

ReaderFactory and smart_read are independent paths today: wiring only the
factory will not upgrade smart_read. Conversely, a successful `/ingest` test
cannot establish either public Tools entry point works with Docling.

## Delivery sequence and claim boundaries

1. **INGEST unit:** establish the shared Tools conversion API, compatible pinned
   Docling/model assets and mandatory `certifi>=2026.10.19`; fix Chat file parsing
   and four-format ingestion. Freeze and independently verify that bounded unit.
2. **TOOLS-DOC unit:** use the same frozen capability to upgrade the two named
   Tools entry points and their package setup/help/tests. Produce its own exact
   implementation directive and independent verification. No second converter.
3. **Package adoption handoff:** publish a consumer matrix and installed proof.
   Describe INGEST as complete independently when appropriate, but do not call
   Tools document adoption complete until step2 and its acceptance gate pass.
   Package publication/version delivery is separately authorized.

Both units can be planned together. Do not implement step2 under INGEST's narrower
allowlist or infer step2 approval from approval of the shared dependency alone.
If the maintainer chooses one combined construction unit instead, revise and
review its exact allowlist/criteria first; no automatic scope expansion.

## Companion behavior contract to freeze before construction

- Keep extraction in Tools' shared public module, free of Chat/TUI imports.
  Docling initialization, supported formats, local model lookup, OCR, conversion
  status/empty-content refusal and typed error codes have one owner.
- Keep the Tools sandbox/path checks ahead of document access. Errors for all
  four admitted formats
  must not become binary-skip success, raw-byte/Latin-1 text, or a legacy-reader
  fallback. Other binary formats and text/code/table tool behavior stay scoped.
- Preserve the `ReaderResult`/`ToolResult` caller contracts through typed adapters.
  Define Tools pagination explicitly: PDF offsets/limits use pages; DOCX uses
  defined document blocks; PPTX uses slide indices. XLSX must retain the existing
  factory's active-sheet default, `sheet` name/index, `cell_range` and data-row
  offset/limit contracts through its adapter. Full-workbook `/ingest` and
  smart_read use the separate whole-document policy, without silently inheriting
  the legacy active-sheet/row preview. Freeze headers, merged-cell/range boundary
  behavior and truthful truncation metadata. Preserve units and document each
  intentional order/format delta. Do not reinterpret slash-command `--lines` as
  this API's pagination. An explicitly selected hidden sheet/range in the
  existing Tools API remains an explicit selection with visibility metadata;
  it does not change the default whole-document visibility rule. Unsupported
  compatibility requirements block readiness rather than trigger legacy fallback.
  The shared capability must retain the page/block/sheet/cell/slide provenance these consumers
  need; freeze that surface in the common readiness gate rather than exposing
  mutable Docling objects to callers.
- Feed extracted text into smart_read's existing size threshold and optional
  summarization/storage logic. Count extracted characters, not binary document
  bytes. Conversion itself adds no hosted LLM or remote OCR call. Preserve
  add_to_context, store_to_memory, force_chunked and force_reprocess controls.
- For document caches, bind entries to source identity and conversion-profile
  identity, including relevant backend/model/options changes. An old entry
  without that provenance cannot substitute for verified extraction. Bypass it
  and reprocess; do not delete user records. Preserve text-cache behavior.
  Its existing persistent cache queries `type=file_synthesis`, not arbitrary
  `/ingest` records; do not conflate these with the historical placeholder issue.
- Define migration of the existing Tools `documents` extra and the new
  `document-ingestion` profile, including the existing `spreadsheets` and
  `all-formats` extras, explicitly. Do not relabel a legacy-only install as
  Docling-enabled. The supported Docling-enabled Tools
  installation must include the pinned stack and Certifi floor. Bare Tools can
  retain text operations and give a clear dependency/model readiness error for
  unavailable document conversion. Avoid accidental plugin/backend selection.
- Use the common format contract for visible-sheet/slide defaults, cached-value
  formula handling, native slide content and labeled speaker notes. Selections
  are inputs to that same capability, not another extraction engine. Keep
  exclusion/coverage metadata distinct from actual backend failure. XLSM stays
  on its explicitly retained legacy route; PPT/PPTM/XLS and unrelated formats
  are not newly admitted by this profile.

## Proposed package boundary and future allowlist

Companion code changes are limited to the shared Tools document adapter if its
frozen contract needs planned unit/selection access, a new typed
`readers/document_adapter.py` if required for strategy compatibility,
`readers/factory.py`,
`readers/__init__.py` and `filesystem/__init__.py` for necessary public exports,
`filesystem/smart_read.py`, Tools dependency declarations/README, focused Tools
tests/fixtures and dependency lock changes specifically required by this profile.
No Memory chunker/storage source, Chat handler, general file-tool rewrite or
TUI implementation is included. Freeze exact paths/signatures after readiness;
this list is not construction authorization.

## Acceptance evidence for Tools adoption

| ID | Required proof through public consumers |
| --- | --- |
| TD-01 | Actual `ReaderFactory.read` / `get_reader_for_path` on genuine PDF, DOCX, XLSX and PPTX reaches the shared converter once and returns distinctive source text, order and real metadata. Only these four routes change. XLSX active-sheet/explicit-sheet/range/row compatibility is tested separately from full-workbook ingestion. |
| TD-02 | Actual `SmartFileReadTool.run(Input(...))` extracts all four formats through Docling; no binary-skip or raw ZIP/text success. Verify small and large/force_chunked paths, extracted-character sizing, full admitted scope and unchanged context/storage controls. |
| TD-03 | Both consumers refuse corrupt/encrypted/partial/empty conversion and missing library/models with no fallback/false success or unwanted storage/cache writes. Local OCR has real scanned-fixture proof, not only converter doubles. |
| TD-04 | Existing filesystem sandbox denial still wins before converter access. Text/code/CSV/web and direct legacy-reader contracts are preserved. XLSX factory routing/format deltas are exact and separately approved; XLSM remains on its legacy route. |
| TD-05 | Document cache hit/invalidation/force_reprocess and conversion-profile drift are demonstrated. Ineligible historical entries are ignored, not purged. No stale cache can conceal a converter failure for changed input/profile. |
| TD-06 | Tools pagination and structured metadata are explicit and tested. Same source/selection/profile produces matching extracted source markers before optional summaries. Compare common included content across Chat, factory and smart_read; an intentional factory sheet/range selection is not mistaken for lost full-workbook content. |
| TD-07 | Clean installed Tools-with-profile works without Chat installed; Commands remains standard-library-only. The exact Docling/model manifest and post-install `certifi>=2026.10.19` checks apply in normal and optimized modes. |
| TD-08 | Stable candidate, package/tool regressions, canonical origins, negative controls and fresh independent review; consumer matrix records implemented versus deferred entry points. Human acceptance and delivery stay separate. |
| TD-09 | Real multi-sheet/slide fixtures demonstrate common hidden-content coverage, saved formula values/refusals, late markers, notes and merged/native tables through both public consumers. No silent first-sheet/slide/row cap or dropped-note success; all four formats have installed normal/optimized public-entry proof without Chat. |

Existing `test_pdf_is_binary` expectations may change only for the explicitly
adopted formats. Preserve the other binary/text/cache/storage tests and expose
new failures honestly. No package-level upgrade claim based only on a helper
import, a mocked converter, or an ingest success message.
