# CD-CMD-TOOLS-DOC-001 — public Tools document adoption

Version: **0.4, bounded corrected conditional construction draft**, 2026-11-12.
Execution phase: **validation**; validation state: **in_review as interaction context**.
Branch: `feature/cmd-ingest-001`; planning baseline: `8c36d8e2`.

This is the separately directed companion to
[CD-CMD-INGEST-001](CD-CMD-INGEST-001-product.md). It implements the reviewed
[TOOLS-DOC plan](../proposals/tools-document-adoption.md), TD-01–10, and the
manifest-pinned [REM](../remediation/REM-CMD-INGEST-001-pdf-docx.md), compatibility
annex and approved package assessment. Chuck authorizes bounded document corrections
and at most three additional reviews of the main directive, including this
companion interaction. This is additional pass2/3; stop on a passing all-seat9.5
result or after the third additional council. The INGEST Q replacement-model
qualification remains a dependency of this companion too.
No companion construction or live-effects approval is recorded by this document.

## Activation and objective

Activate only after INGEST's common readiness, frozen shared interfaces and
applicable implementation slices are independently verified, the exact companion
file/case/oracle appendices are complete, and Chuck approves this directive and
its hashes. INGEST's approval or converter-helper success is not companion
approval or adoption proof. The [readiness decision](../validation/document-ingestion/product-construction/readiness-decision.md)
and unresolved factory-selection qualification remain binding.

Upgrade both existing public consumers to the **same** qualified Docling
capability: `ReaderFactory`/`get_reader_for_path` and `SmartFileReadTool.run`.
They are independent routes and each needs its own public-entry evidence.
No new converter, Memory policy, embedding guard, frontend or automatic storage.

## Exact scope and behavior

| Allowed Tools path | Bounded change |
| --- | --- |
| `src/friday_tools/filesystem/readers/document_adapter.py` (new) | Typed ReaderResult adaptation and selection/pagination of the frozen shared source/provenance. |
| `src/friday_tools/filesystem/readers/document_ingestion.py` | Only the already-planned selection/unit access in the approved shared contract; changed contract bytes require a new INGEST aggregate review. |
| `src/friday_tools/filesystem/readers/factory.py`, reader `__init__.py`, filesystem `__init__.py` | Route only PDF/DOCX/XLSX/PPTX through the shared adapter; necessary public exports. |
| `src/friday_tools/filesystem/smart_read.py` | Document routing, extracted-character sizing, structured common-entry handoff and conversion-cache identity. No second storage/chunking implementation. |
| `pyproject.toml`, `README.md` | Exact supported profile, optional extra behavior, local assets and limitations; retain legacy extras. Only a justified companion-specific lock delta. |
| `tests_tools/test_filesystem_readers.py`, `test_smart_read.py`, `test_document_ingestion.py`, new `test_document_adoption.py`, scoped synthetic document fixtures | Exact migration-map entries, public positive/refusal/cache/selection/sandbox tests and installed proof. |

Paths above are relative to `packages/friday-tools/`. The only other allowed
changes are companion evidence/status and affected sections of the already
named architecture/guide deliverables. No Core/Memory/LLM/Chat production edit,
legacy direct-reader rewrite, text/web tool redesign or new package dependency
edge is inferred. A larger change returns for scope reconciliation.

Preserve filesystem sandbox denial **before** source/converter access. A failed
conversion is a typed error, never binary-skip success, Latin-1/ZIP text or a
fallback reader. Bare Tools retains existing text use and reports missing document
profile/assets actionably. The Docling-enabled profile enforces the common
Certifi floor and exact local asset/version manifests.

Preserve ReaderResult/ToolResult shapes and freeze intentional text/order deltas.
PDF pagination uses pages; DOCX uses explicitly defined body blocks; PPTX uses
original slide indices. XLSX retains active-sheet default, explicit sheet
name/index, range, header and data-row offset/limit semantics. Explicit hidden
sheet/range selection is distinguished from whole-workbook visible defaults.
Do not map slash-command `--lines` onto these APIs. RD-02/RD-06 require actual
selected-release proof of selection and structure; an unsupported requirement
stops adoption rather than triggering legacy fallback or fabricated success.

Whole-document smart_read uses complete admitted content, counts extracted
characters rather than binary bytes, and retains add_to_context,
store_to_memory, force_chunked and force_reprocess. Pass native structure into
the injected common entry once. Existing context summaries may keep scoped
read processing; all source storage uses the shared plan and derived records
use its unsplit guard. No previously unwired Chat/Runtime Memory entry is enabled.
An explicit storage request without the entry fails actionably.

Conversion caches bind content, selection, backend/assets/settings and source
identity. Storage receipts additionally bind strategy/budget, preparation/counter,
embedding space and actual destination/incarnation/collections/record provenance.
Recheck opt-in and admission on hits; bypass old ineligible entries without
purging them. A conversion cache hit does not establish successful storage.

Retain direct specialized PdfReader/DocxReader/XlsxReader compatibility APIs,
FileReadTool's line/text role and XLSM's explicit legacy route. PPT/PPTM/XLS,
macros, additional Docling formats, new fetchers and remote OCR are not admitted.

## Required verification and migration

TD-01–10 are incorporated individually and must each receive attributable public
and installed evidence. At minimum:

1. Both actual public consumers read distinctive complete text/order/metadata
   from genuine PDF, scanned PDF, DOCX, XLSX and PPTX. Demonstrate converter
   delegation, full scope, notes, late markers, multiple sheets/slides and
   separately selected XLSX ranges. Mock-only routing is insufficient.
2. Both refuse corruption, empty/partial output, missing library/assets,
   unsafe structure and failed sandbox access, before storage or success-cache
   publication. The existing corrupt eight-byte `%PDF-1.4` seed does not become a genuine
   positive PDF merely because its old test classified it as binary.
3. Cache-hit/drift/reprocess, small/large/force_chunked and all three strategies
   prove exactly one shared source plan and truthful source/derived handling.
   Exercise injected headless Memory and a fresh admitted store without Chat.
4. Prove text/code/CSV/web and unrelated binary behavior retained, direct legacy
   readers retained, no automatic storage, exact fixture/oracle deltas and
   meaningful call-phase rejection controls with an unchanged control.
5. Clean installed Tools-with-profile works **without Chat** in normal and
   optimized probes; confirm artifact origins, dependency checks and post-install
   Certifi version/CA origin. Bare Tools imports/discovers registered tools
   without a document extra. No model call without a separate live window.

The shared baseline inventory is read-only evidence. Before changing a test,
incorporate its exact old/new node/oracle into the companion migration appendix;
unmapped bodies remain retained. Keep named TD/DI/FC gates and unchanged public
signatures. Document INGEST and TOOLS-DOC status separately in package/guide
tables; authored examples need actual public-candidate evidence.

Use the same private candidate environments, cache/basetemp ownership, static
checks, exact selectors, preservation and fresh read-only validation rules as
the INGEST directive. Source and installed results are distinct. Freeze a new
candidate and review the companion plus its interaction with the full bounded
INGEST aggregate; changes to shared authority/code invalidate prior decisions
for those changed bytes.

Stop on unqualified selection/provenance, dependency/asset drift, required
caller-contract change, missing migration coverage, new path/owner or protected
state change. No automatic remediation loop, production deployment, model
switch, cleanup, publication or delivery is authorized. Present verified public
consumer results and a disposable operator checklist for human acceptance.
