# TOOLS-DOC-001 — adopt shared Docling conversion in document-reading tools

Status: **PROPOSED companion — correction cycle2 / council round3; no construction approval**.
This is a scoped adoption plan, not a completed tool upgrade or implementation
directive. It depends on the exact shared capability and dependency/model
readiness from [REM-CMD-INGEST-001](../remediation/REM-CMD-INGEST-001-pdf-docx.md).
The maintainer expanded the document scope to **PDF, DOCX, XLSX and PPTX** on
2026-11-10. That four-format scope applies to this adoption plan as well as Chat.
Text and web reading remain existing capabilities; maintained web-to-Memory
and automatic tool-output caller routes were not found. The later
maintainer discussion extends shared ingestion chunking to **all sources** with
document/512 defaults and document/recursive/fixed overrides. That common policy
and the embedding guards are established by INGEST; this companion adopts them
without duplicating policy or adding fetchers. Supplied extracted web/tool text
exercises the common entry without claiming absent product wiring. The maintainer
authorizes document correction and at most three further councils, not readiness
operations or implementation. No implementation claim is implied.

## Why a separate adoption obligation is needed

Putting the converter in Friday Tools establishes ownership and reuse. Existing
consumers still need deliberate routing changes. Source inspection at `37d789c4`,
confirmed against unchanged product bytes at `f6287faa`, shows:

| Consumer | Current behavior | Proposed adoption |
| --- | --- | --- |
| Chat `/read` and `/ingest` through `SmartFileReader` | PDF/DOCX/XLSX placeholders; PPTX not admitted | INGEST unit uses shared Docling extraction for all four formats. |
| Tools `ReaderFactory` / `get_reader_for_path` | Selects legacy PDF/DOCX/XLSX readers; PPTX reaches binary fallback | Companion unit routes all four formats through typed adapters of the same shared converter. No independent engine/configuration policy. |
| Tools `SmartFileReadTool` (`smart_read`) | Public injected storage paths exist, but maintained Chat does not supply Memory and Runtime does not construct it. PDF/DOCX/XLSX binary-skip; PPTX lacks conversion. | INGEST corrects explicitly injected text storage/cache and makes unwired storage requests fail. Companion adds document routing but does not activate maintained storage wiring. |
| Tools `FileReadTool` (`file_read`) and line readers | Text/encoding/line APIs | Remain text tools; do not silently turn line-oriented operations into document conversion. |
| Direct public `PdfReader` / `DocxReader` / `XlsxReader` callers | Existing specialized reader APIs, including legacy XLSM support | Retain explicit compatibility APIs unless a separately approved contract migration covers them. Do not claim every direct reader caller has migrated. |

ReaderFactory and smart_read are independent paths today: wiring only the
factory will not upgrade smart_read. Conversely, a successful `/ingest` test
cannot establish either public Tools entry point works with Docling.

## Delivery sequence and claim boundaries

1. **INGEST unit:** establish the shared Tools conversion API, compatible pinned
   Docling/model assets and mandatory `certifi>=2026.10.19`; fix Chat file parsing
   and four-format extraction, all-source shared chunking, typed model limits and
   guarded embedding handoffs. Include existing smart_read text small/large/cache
   storage, raw/derived classification, durable store identity and headless
   composition. Freeze and independently verify INGEST without claiming Tools
   document-consumer adoption.
2. **TOOLS-DOC unit:** use the same frozen capability to upgrade the two named
   Tools entry points and their package setup/help/tests. Produce its own exact
   implementation directive and independent verification. Existing shared text
   storage/cache policy is established by INGEST, not deferred to this companion.
   Add format routing, selections and conversion-profile caching here. No second
   converter or shared-policy implementation.
3. **Package adoption handoff:** publish a consumer matrix and installed proof.
   Describe INGEST as complete independently when appropriate, but do not call
   Tools document adoption complete until step2 and its acceptance gate pass.
   Package publication/version delivery is separately authorized.

Both units can be planned together. INGEST includes narrow existing smart_read
storage/cache changes, but not its four-format routing. Do not implement step2
or infer its approval from the shared dependency alone.
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
- Feed extracted source into smart_read's existing size threshold and optional
  summarization/storage logic. Count extracted characters, not binary document
  bytes. Conversion itself adds no hosted LLM or remote OCR call. Preserve
  add_to_context, store_to_memory, force_chunked and force_reprocess controls.
  Context-only summarization may keep its own read-processing behavior, but any
  storage handoff uses the shared ingestion options and validated chunk plan.
  Pass native structure to document chunking instead of flattening and slicing
  again. Existing text storage adopts this under INGEST; supplied web/tool text
  capability uses the same rule without claiming new maintained routes. Do not
  turn on previously disabled storage or tool ingestion.
- For document caches, bind entries to source identity and conversion-profile
  identity, including relevant backend/model/options changes. An old entry
  without that provenance cannot substitute for verified extraction. Bypass it
  and reprocess; do not delete user records. Ingestion cache identity additionally
  includes source content identity, completed-storage state, strategy/budget,
  embedding space and counting/formatting revision
  for every source type. Preserve context-only text caching where it cannot
  bypass a later storage-policy/embedding check.
  Completed-storage receipts additionally bind destination namespace path,
  incarnation, exact collection set and record IDs/provenance, validated before
  skipping storage. A matching model does not prove a fresh destination has the
  data. Missing records or a switched collection require the common entry again.
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
Core/Memory/LLM contracts and policy are established in INGEST. This companion
calls those frozen capabilities; it does not implement another Memory chunker,
  embedding guard or Chat handler. Core supplies the injected entry protocol;
headless callers construct the public Memory implementation and inject it,
without a Tools-to-Memory dependency or Chat proxy. Source raw records come from
that plan; summaries are derived records under the unsplit guard. No general
file-tool rewrite or TUI implementation
is included. Freeze exact paths/signatures after readiness;
this list is not construction authorization.

## Acceptance evidence for Tools adoption

| ID | Required proof through public consumers |
| --- | --- |
| TD-01 | Actual `ReaderFactory.read` / `get_reader_for_path` on genuine PDF, DOCX, XLSX and PPTX reaches the shared converter once and returns distinctive source text, order and real metadata. Only these four routes change. XLSX active-sheet/explicit-sheet/range/row compatibility is tested separately from full-workbook ingestion. |
| TD-02 | Actual `SmartFileReadTool.run(Input(...))` extracts all four formats through Docling; no binary-skip or raw ZIP/text success. Verify small and large/force_chunked paths, extracted-character sizing, full admitted scope, retained opt-in/context controls and exactly one shared ingestion chunk plan on storage paths. |
| TD-03 | Both consumers refuse corrupt/encrypted/partial/empty conversion and missing library/models with no fallback/false success or unwanted storage/cache writes. Local OCR has real scanned-fixture proof, not only converter doubles. |
| TD-04 | Existing filesystem sandbox denial still wins before converter access. Text/code/CSV/web extraction and direct legacy-reader contracts are preserved; plain delimited payloads disclose absent table structure rather than infer headers; shared ingestion chunking deltas are those explicitly established by INGEST. XLSX factory routing/format deltas are exact and separately approved; XLSM remains on its legacy route. |
| TD-05 | Cache hit/invalidation/force_reprocess prove conversion, strategy/budget, model and counting-profile drift. Ineligible historical entries are ignored, not purged. No stale ingestion cache can conceal a converter or embedding-guard failure. |
| TD-06 | Tools pagination and structured metadata are explicit and tested. Same source/selection/profile produces matching extracted source markers before optional summaries. Compare common included content across Chat, factory and smart_read; an intentional factory sheet/range selection is not mistaken for lost full-workbook content. |
| TD-07 | Clean installed Tools-with-profile works without Chat installed; Commands remains standard-library-only. The exact Docling/model manifest and post-install `certifi>=2026.10.19` checks apply in normal and optimized modes. |
| TD-08 | Stable candidate, package/tool regressions, canonical origins, negative controls and fresh independent review; consumer matrix records implemented versus deferred entry points. Human acceptance and delivery stay separate. |
| TD-09 | Real multi-sheet/slide fixtures demonstrate common hidden-content coverage, saved formula values/refusals, late markers, notes and merged/native tables through both public consumers. No silent first-sheet/slide/row cap or dropped-note success; all four formats have installed normal/optimized public-entry proof without Chat. |
| TD-10 | Actual headless smart_read storage on all four adopted formats observes document/512 and all explicit strategies through the injected Memory entry already established by INGEST. Stored raw chunks equal its plan, derived records use the unsplit guard, and fresh bound stores admit only matching identity. Missing capability/old cache refuses storage. Supplied web/tool payload tests are capability proof, not proof of absent product wiring. No double chunking, model activation, reset or migration. |

Existing `test_pdf_is_binary` expectations may change only for the explicitly
adopted formats. Preserve the other binary/text/cache/storage tests and expose
new failures honestly. No package-level upgrade claim based only on a helper
import, a mocked converter, or an ingest success message.
