# REM-CMD-INGEST-001 — PDF, DOCX, XLSX and PPTX extraction before ingestion

Status: **PROPOSED — maintainer document review**. Baseline `7ad916f2`.
This document defines a bounded repair and its dependency-readiness gate. It is
not an approved construction directive or a completed compatibility assessment.
No product edits, installs, model downloads or council invocation are authorized
by placement in this packet. The requested planning work is authorized.

**Maintainer scope expansion — 2026-11-10:** include XLSX workbooks and PPTX
presentations alongside PDF and DOCX. Text and web ingestion are existing
capabilities for this plan; preserve their entry points and behavior rather than
reimplementing or migrating them to Docling. This assumption is not a new
validation claim about those capabilities. The original filename is retained
for existing links and historical evidence. Format defaults below are proposed
for document review, not implemented behavior.

## Problem and independent assessment

[Source assessment](../validation/document-ingestion/assessment.md) and
[guarded observations/source pins](../validation/document-ingestion/assessment.json)
confirm the supplied agent's central finding: `/ingest` can report success after
passing a generated PDF/DOCX placeholder to memory. Existing corrupt documents
follow that same path. A source path in `/list-ingested` proves metadata was
stored, not that source text was extracted. No personal store was inspected.

Additional observations matter to the repair:

- Quoted paths are split before the handler; consecutive spaces inside a real
  filename cannot be recovered by joining the already split argument tuple.
- The PDF placeholder reports one page and ignores `--lines`; XLSX also uses a
  placeholder. These are explicit compatibility exceptions, not parity targets.
- Tools already has real pypdf/python-docx readers, but the PDF reader can return
  page-error prose with `success=True`. Its image-only result can be empty and
  successful. DOCX currently emits all paragraphs before its tables. Connecting
  those readers unchanged would leave correctness gaps.
- The accepted missing-description metadata repair is already shared in Memory.
  It is preserved; it does not address document extraction.

## Package choice: Docling, behind a shared capability

The maintainer identified Docling as a promising backend. This proposal selects
**Docling for PDF, DOCX, XLSX and PPTX conversion**, with a pinned local pipeline. Its
structured document/Markdown output suits the existing text chunking boundary.
This is an architectural recommendation, not a measured quality/performance claim.
[Project capabilities](https://github.com/docling-project/docling),
[supported formats](https://docling-project.github.io/docling/usage/supported_formats/).

| Candidate | Evidence and role in this decision |
| --- | --- |
| Docling | Selected proposed backend: document conversion with layout/table support and local OCR capability. Exact versions, pipeline and model artifacts must pass gate A below. |
| Existing pypdf6.6.0 + python-docx1.2.0 | Already present in this workspace/lock and useful for independent fixtures/oracles. They are optional Tools dependencies, not proof of normal Chat installation support. Do not build a second fallback extraction pipeline in this repair. |
| Microsoft MarkItDown | Supports PDF/Word conversion with format-specific extras. Considered as an alternative; not added alongside Docling. [Official project](https://github.com/microsoft/markitdown). |

Docling originated at IBM Research and is now hosted under LF AI & Data. Its
code is MIT-licensed; model artifacts have their own licenses. Record those
separately. Popularity is not an acceptance criterion.
[Project provenance/license](https://github.com/docling-project/docling#license).

Docling normally downloads models on first use and supports explicit prefetching.
The proposed integration requires **provisioned local assets and no conversion-time
downloads**. Missing assets must give an actionable error before ingestion.
Remote services stay disabled. Local OCR for scanned PDFs is included in the
proposed scope; no hosted vision/LLM service is added.
[Offline/model configuration](https://docling-project.github.io/docling/usage/advanced_options/).

## Ownership and scope

| Owner | Responsibility |
| --- | --- |
| `friday-tools` | Shared typed document extraction capability, Docling adaptation, supported-format admission, conversion status/coverage checks, local asset readiness and safe errors. No Chat/TUI imports. |
| `friday-commands` | A small standard-library-only file-argument tokenizer: quoted path interpretation shared by consumers. No filesystem, Docling or Memory imports. |
| `friday-memory` | Existing chunking, embedding and persistence semantics. No source changes in this repair; metadata helper and both ingestion branches remain intact. |
| `friday-chat` | Delegates raw file arguments/extraction, retains admission and memory invocation, renders source-derived statistics/warnings and failures. |

This is a prerequisite repair for later FILE-001 extraction, **not the complete
FILE-001 command-family migration**. No new registry family, general command
framework or TUI implementation is included. MAINT-001 remains independently
verified at its frozen candidate, with human UAT/acceptance still pending.

## A — dependency and model readiness, before product construction

Prepare this evidence in an isolated environment, without modifying the working
`.venv`, user configuration or accepted lock/evidence in place:

1. Select and record one exact Docling release compatible with the repository's
   Python3.13.10/macOS arm64 profile. Resolve and hash its complete transitive
   dependency graph against current Chat. Record required version changes,
   download/install size and cold/warm conversion timing; do not infer them from
   the advertised platform list. No release has yet been installed or benchmarked.
2. Proposed packaging: add a narrow Tools extra `document-ingestion` containing
   the chosen Docling requirement **and explicit `certifi>=2026.10.19`**; make
   default Chat depend on
   `friday-framework-tools[document-ingestion]==0.1.0a4`. Keep existing Tools
   `documents`/`spreadsheets` compatibility extras intact within this unit. Include
   the selected release's XLSX/PPTX backend requirements in the resolved profile;
   inventory `openpyxl` and `python-pptx` versions if required. Do not assume the
   base Docling distribution installs every backend. The default Chat profile
   will change deliberately; the old 138-distribution closure is not its oracle.
   The neutral Commands-only closure remains one distribution.
3. Select exactly one local, CPU-capable OCR engine and required language/model
   set for an English scanned-PDF fixture. Record all layout/table/OCR weights,
   revisions, licenses, hashes, asset paths and explicit provisioning steps.
   Pin the backend rather than relying on automatic engine selection. Do not
   download every Docling model, enable VLM enrichment, or add remote services.
4. Freeze the actual conversion API, status/error mapping, Markdown serialization,
   document-size/page/sheet/row/cell/slide/decompressed-archive limits and
   model-lookup behavior. Prove the format rules in section B on the selected
   release; upstream main-branch documentation is not pinned-release proof.
   Document missing-model behavior. PDF assets are not a prerequisite for DOCX,
   XLSX or PPTX when their selected pipelines do not use them. Test that distinction.
5. Produce a readiness manifest and precise metadata/lock delta. Stop if an
   unrelated upgrade, unsupported wheel, external executable, unbounded model
   fetch or conflicting dependency requires scope beyond this proposal.

This gate is **pending**, not a silently assumed success. Before code generation,
the exact versioned implementation directive/manifest and approved scope must be
recorded. The present document is for reviewing the design and those boundaries.
No dependency synchronization or model provisioning has been performed this turn.

### Mandatory Certifi security floor — maintainer requirement

The maintainer explicitly requires **`certifi>=2026.10.19`** whenever Docling is
installed for this unit. This minimum is settled; it is not an optional backend
choice. Record it in the Tools `document-ingestion` extra alongside Docling,
resolve it into `uv.lock`, and install the resolved hash-verified artifact. A
one-off post-install `pip install --upgrade` without updating declared/locked
requirements is insufficient: subsequent synchronization must retain the floor.

The inspected baseline lock and active environment contain `certifi2025.11.12`.
Upstream advisory [GHSA-6q48-6c7w-9gw2](https://github.com/certifi/python-certifi/security/advisories/GHSA-6q48-6c7w-9gw2)
identifies the emSign root-removal fix in2026.10.18. The requested2026.10.19
release exists on [PyPI](https://pypi.org/project/certifi/2026.10.19/); the required
floor remains2026.10.19, not2026.10.18. This records the specific upstream finding,
not a claim that a version threshold proves all dependencies vulnerability-free.

Gate A and installed proof must:

- Refuse any dependency resolution that omits Certifi or selects a version below
  the floor; do not relax it to make Docling resolve. Treat the Certifi upgrade
  as a specifically requested dependency change within this unit.
- Record its exact resolved version, wheel/source provenance and actual artifact
  hashes in the new dependency manifest. An earlier bundle with Certifi2025.11.12
  cannot supply this unit's supported-installation proof. Preserve that historical
  evidence in place; generate new artifacts and profiles.
- After **all** Docling/dependency installation operations, verify with the actual
  target interpreter that installed distribution metadata reports a version at
  least2026.10.19, using `packaging.version.Version` semantics, not string ordering.
  Check the imported Certifi module/CA-bundle origins belong to the target prefix.
  Run dependency compatibility checks and repeat version/origin proof in the
  normal and optimized installed-conversion lanes.
- Include a negative control proving a below-floor installed-version report is
  rejected by the verification gate, plus an accepted floor/newer control. Do
  not count import/setup failures as evidence of this version assertion.

This requirement does not authorize modifying existing CA bundles, disabling TLS
verification, bypassing certificate errors or mutating accepted historical test
installations. No package upgrade has been executed while updating this proposal.
[Recorded baseline and source metadata](../validation/document-ingestion/certifi-security-requirement.json).

## B — extraction contract

Expose a documented typed capability in a new public Tools submodule, provisionally
`friday_tools.filesystem.readers.document_ingestion`. Keep third-party objects
inside it. Return a frozen, runtime-validated `ExtractedDocument` containing a
resolved local source path, admitted format, nonempty Markdown text, real PDF
page count, ordered XLSX sheet identities and PPTX slide count/indices where
applicable, declared coverage and immutable warning codes/messages. Counts
distinguish total, included and intentionally excluded units; unknown is not a
fabricated zero. Retain typed page/block/sheet/slide provenance for Tools adoption.
Expose a typed extraction error with stable failure categories. No `Any`-shaped
ReaderResult dictionary crosses into Chat; no new blanket typing suppression.
The implementation manifest freezes exact signatures after gate A.

The capability must:

- Accept only existing local regular `.pdf`/`.docx`/`.xlsx`/`.pptx` files,
  case-insensitively.
  Apply the explicit format allowlist before invoking Docling. No URL input,
  MIME-based expansion, generic binary fallback or plugin format discovery.
- Convert the complete admitted document before calling Memory. Accept only a
  documented successful conversion with no known failed pages/parts; partial,
  failed and unsupported results fail closed. Translate converter errors into
  sideband diagnostics, never text for chunking. Do not fall back to legacy
  readers, fake page counts or placeholder strings on failure.
- Preserve page sequence and body reading order. Required DOCX coverage includes
  interleaved paragraphs and tables; headings/table structure survive in Markdown.
  Gate A characterizes other Word parts and declares omissions. Do not claim
  exhaustive comments/headers/footers/textboxes/image extraction without proof.
- For scanned PDFs, use the pinned local OCR path. Check for meaningful source
  text in the structured document, not merely nonempty serialized Markdown:
  image markers, document titles from metadata or HTML comments are not extracted
  source text. If OCR produces no usable text, fail clearly. If OCR assets are
  missing, report missing assets, not a successful empty document.
- Return page count/coverage/warnings separately. Pass only extracted Markdown
  into the existing chunker; no status messages, filenames-as-substitute-content,
  raw binary, data-URI images or diagnostic prose in stored text. Do not fetch
  external references or enable remote conversion/enrichment services.
- Reject encrypted/password-required documents explicitly in this unit; no password
  CLI/API is added. Corruption, permission/read errors and conversion-limit
  failures produce no ingestion call. Known partial conversion is not accepted
  merely because its serializer returned some text.
- Reject any document `--lines` request before conversion. It remains a text/table
  option, not a page/paragraph count. Do not silently truncate a document or
  reinterpret lines as pages. A later page-range feature is separate scope.

### Format rules to freeze at readiness

These are deliberately text-extraction rules for the existing chunker, not a
spreadsheet calculation engine or a presentation-rendering project. The same
conversion profile applies through Chat and adopted Tools consumers. A requested
content scope is complete only when all its required content has been converted;
the declared exclusions below are not permission to accept converter failures.

| Format | Required extracted content | Proposed default and declared limits |
| --- | --- | --- |
| PDF | Native text and tables in page/reading order; local OCR for scanned pages; real page count. | Existing PDF/OCR requirements remain. No password handling, remote OCR or VLM enrichment. |
| DOCX | Paragraphs, headings and tables in body order. | Characterize and disclose omitted Word parts; no promise of full visual fidelity. |
| XLSX | Visible worksheets in workbook order, with source sheet names, row/column relationships and cell text/values retained as tables. | Read saved formula results without recalculation. Hidden sheets/rows/columns are excluded with explicit coverage warnings/counts. No new sheet/range CLI options. |
| PPTX | Visible slides in deck order, titles, text boxes, bullet hierarchy, native tables and separately labeled speaker notes. | Preserve original slide numbers and a deterministic within-slide text order. Hidden slides/shapes are excluded with coverage warnings/counts. No slide rendering or animation/media execution. |

For **XLSX**, preserve Unicode, multiline cells, booleans, zero, dates, numeric
values and leading-zero text. Define deterministic serialization of those types
and merged cells at gate A; do not duplicate merged values into unrelated cells
or lose sheet/table boundaries. Formula results are the workbook's saved cache,
not newly computed or independently verified values; report that limitation.
If an included formula has no usable cached result or has an error result, fail
before ingestion with a specific error rather than silently treating it as blank
or inventing a value. Do not resolve external workbook links, run calculations,
execute macros or add LibreOffice. Reject `.xls`/`.xlsm` in this new profile.
Charts, images, comments and embedded objects are outside workbook cell-text
coverage; disclose detected omissions. A chart-only workbook with no usable
included cell text fails the meaningful-content check.

For **PPTX**, scope the promise to native text, tables and notes. Freeze the
within-slide ordering rule against fixtures rather than claiming that every
arbitrary visual layout has a unique reading order. Charts, SmartArt, embedded
objects, images and audio/video do not establish text coverage. Report detected
omissions explicitly; do not infer their contents or fetch linked media.
Presentations with no usable native or notes text fail clearly; PDF OCR does
not imply Office-image OCR support. Comments and master/layout-only content are excluded
and disclosed when present. Reject `.ppt`/`.pptm` in this profile.

For both new formats, empty sheets/slides retain truthful source-unit metadata
but their labels do not satisfy the meaningful-content check. No first-sheet,
first-slide, preview-row or serializer-default limit may silently replace the
full admitted scope. Unexpected missing cells/slides or backend clipping is a
conversion failure, not a warning-only success. Readiness must prove detection
of these conditions and proposed visibility/notes/formula rules on real files.
If the selected release cannot support a rule, stop and revise the documented
contract before implementation; do not silently narrow it or add another engine.

Within this INGEST unit, the legacy Tools factory/reader consumers retain their
current behavior. This is **not** a claim that existing Tools entry points have
adopted Docling. The [TOOLS-DOC-001 companion plan](../proposals/tools-document-adoption.md)
requires separate routing and public-consumer proofs for `ReaderFactory` and
`SmartFileReadTool`, using the same shared converter. The common readiness gate
must preserve typed page/block/sheet/cell/slide provenance needed for that adoption. No duplicate
backend or broad Tools change is authorized by this INGEST allowlist.

## C — path parsing and Chat integration

Add a shared `friday_commands.file_inputs` submodule; keep the existing root
`__all__` and accepted API54 literal tests unchanged. It consumes the **original
raw argument tail**, never a reconstructed whitespace-split string.

Contract for the first path:

- One matching outer ASCII single/double quote pair delimits a path containing
  spaces; preserve the exact interior, including repeated spaces, Unicode,
  apostrophes and backslashes. No shell interpolation, command substitution or
  backslash escape interpretation. Use the other quote delimiter when a filename
  contains one delimiter. Unmatched quotes, empty/whitespace-only paths and
  non-whitespace immediately after the closing quote are usage errors before I/O.
- Preserve existing unquoted path behavior, leading recognized `--lines` tokens,
  text-limit defaults and remaining-description whitespace joining. Normalize
  the chosen path into argument position0, retaining the original option order
  after it. A quoted filename starting `--lines` is a path, not an option.
- Only the path is unquoted. Description quote characters retain existing
  semantics; this is not a global shell parser. Limit parsing runs on the
  arguments after the selected path, not on the path itself.

Chat routes the untouched raw tail to that helper only for the default read/
ingest handlers after resolving the actual handler. Custom handlers and other
commands retain their original arguments/authority; aliases of a default file
handler get the same file parsing. `_parse_command_input` remains unchanged for
all other paths. No join-and-strip workaround or global `shlex` replacement.

`SmartFileReader` delegates PDF/DOCX/XLSX/PPTX to the shared extraction capability and maps
its typed result into `FileReadResult`, adding only sideband backend/coverage/
warning fields needed for presentation. Text/CSV/TSV/JSON behavior remains.
`/read` displays real extracted text and document metadata. `/ingest` uses that
same successful text, then invokes the existing memory path exactly once.

Success is shown only after the memory capability returns an exact positive
chunk count for a document. Existing storage exceptions are not turned into
success. This repair guarantees no memory/embedding write before successful
extraction; it does **not** introduce an ingestion rollback transaction or claim
existing multi-chunk storage failures are atomic. Keep admission-gate behavior.

Remove the common placeholder method. Replace XLSX placeholder output with real
workbook extraction, and add PPTX admission explicitly for both `/read` and
`/ingest`. All other new Docling formats remain disabled. Existing text/table
and web ingestion routes remain outside this change; do not redirect them
through the new document pipeline or claim they were revalidated by this plan.

Update only read/ingest help/detail and their changed response fields. Preserve
the remaining catalog, aliases, parser quirks and accepted metadata oracles.
Retain immutable snapshots; supply a separate exact exception comparison.

## Proposed exact implementation paths

| Path | Allowed purpose |
| --- | --- |
| `packages/friday-tools/src/friday_tools/filesystem/readers/document_ingestion.py` (new) | Shared typed Docling extraction, local asset/status/format checks and errors. |
| `packages/friday-tools/pyproject.toml` | New document-ingestion extra with selected Docling release and mandatory `certifi>=2026.10.19`; other requirements unchanged. |
| `packages/friday-tools/README.md` | Public capability, dependency and local-model setup/limits. |
| `packages/friday-tools/tests_tools/test_document_ingestion.py` (new) | Real format/OCR extraction and typed failure/coverage tests. |
| `packages/friday-commands/src/friday_commands/file_inputs.py` (new) | Pure scoped raw-tail tokenizer; no root API export edits. |
| `packages/friday-commands/tests_commands/test_file_inputs.py` (new) | Headless quoting/leading-option/description and malformed-input proofs. |
| `packages/friday-chat/src/friday_chat/commands/files.py` | Four-format delegation/admission and result metadata, document-line refusal; retain text behavior. |
| `packages/friday-chat/src/friday_chat/commands/registry.py` | Default file-handler-only raw-tail delegation, document failure/success adaptation and exact help cells. No other handlers/parser policy. |
| `packages/friday-chat/pyproject.toml` | Default dependency on the new Tools extra only. |
| `packages/friday-chat/README.md` | Supported document behavior and provisioning. |
| `packages/friday-chat/tests_chat/test_document_ingestion.py` (new) | Actual registry and zero-ingestion-on-read-failure assertions. |
| `packages/friday-chat/tests_chat/test_files_replay_shell.py` | Replace fake PDF/DOCX/XLSX placeholder expectations with genuine extraction assertions; add PPTX coverage; keep test names and unrelated text/replay/shell assertions. |
| `tests/integration/test_document_ingestion.py` (new) | Registry → extraction → real Memory adapter → disposable Chroma, deterministic embeddings; source/installed proof helper if needed. |
| Package-local synthetic `tests_*/fixtures/document-ingestion/` (new) | Genuine text, table and scanned fixtures/provenance; no user documents. |
| `uv.lock` | Deliberate Docling graph delta and requested Certifi upgrade to at least2026.10.19, inventoried at gate A. No unrelated package upgrade. |
| This packet's document-ingestion remediation/validation/UAT/status records; planning board/dashboard; upgrade-log FU-012 | Planning, readiness, proof and human handoff for this unit only. |

No `friday-memory` source, adapters/storage/chunker implementation, MAINT pipeline,
recovery, unrelated configuration, global format/factory policy or TUI source
changes. If integration cannot fit these paths, stop and reconcile the boundary.

## Required verification after approval

| ID | Required evidence |
| --- | --- |
| DI-01 | Real two-page text PDF: distinctive first/last-page strings and correct page count, no placeholder or diagnostic payload. Validity checked independently of the converter. |
| DI-02 | Real DOCX: paragraph → table → paragraph order, Unicode and distinctive late table/body text preserved. No fake extension-only file as success fixture. |
| DI-03 | Genuine image-only scanned PDF with readable test text: real local OCR yields expected words with network blocked. Separate blank/unreadable image fixture fails empty-text checks. Missing OCR/model assets report readiness failure before ingestion. |
| DI-04 | Corrupt/encrypted documents, converter exception, PARTIAL_SUCCESS, page failure after one good page, unavailable library/model and read failure after path resolution: exact error category and zero memory/embedding calls. Diagnostic strings and image-only serializer output must not count as content. |
| DI-05 | Both quoted path forms, two consecutive spaces, Unicode/apostrophes/backslashes, optional description, omitted description, malformed/empty quotes and literal option-like filenames. Unquoted behavior/leading text flags retained; other/custom handlers unaffected. |
| DI-06 | All four document formats reject `--lines=1`, malformed and negative variants explicitly without conversion/ingestion; current text/table limit behavior is unchanged. Non-allowlisted binary/legacy/macro-enabled paths fail closed without fallback. |
| DI-07 | Invoke actual `/ingest` on genuine PDF, DOCX, XLSX and PPTX through real Memory/Chroma with deterministic embeddings; cover single/multiple chunks. Inspect stored documents, late source markers, sheet/slide separators, chunk metadata/counts, source/type/protection and absent/explicit descriptions. `/list-ingested` alone is not proof. |
| DI-08 | Headless consumers import shared tokenizer/extractor without Chat/TUI; no Docling dependency in Commands. Default clean Chat install contains the declared converter stack and Certifi>=2026.10.19, verified after all installs; plain Tools without the extra fails lazily/actionably for documents. Both ordinary and `-O` installed real conversions/OCR/storage run. |
| DI-09 | Negative controls: placeholder substitution, ignored conversion failure, metadata-only image output, dropped last PDF page/table/sheet/slide or PPTX notes, reordered DOCX table, concealed missing formula cache, quote-split regression and swallowed missing-model failure produce named call-phase assertion witnesses. Unchanged control, canonical origins and before/finish/after hashes; no setup/import rejection credit. |
| DI-10 | Full affected package/cohort/CLI/Memory regressions, focused Ruff/mypy/new-file formatting, exact metadata/lock/default closure inventory, enforced Certifi floor/negative control, source/wheel/installed data/origins and model manifest. Record baseline debt and exact approved file-help exceptions without waivers. |
| DI-11 | Bound cold/warm startup and representative document elapsed time, progress/cancellation behavior and file/resource-limit refusal. Cancelled extraction cannot trigger later background ingestion. No unsupported hard-timeout or cross-platform claim. |
| DI-12 | Freeze stable code/evidence, then separately authorized fresh OpenAI Sol/Astra independent review. No agents before maintainer document review/direction. Human UAT follows verification; acceptance and delivery remain separate. |
| DI-13 | Genuine multi-sheet XLSX with late-sheet/late-row markers, cached formulas, missing/error formula caches, blank cells, zero/false/date/leading-zero text, merged cells and hidden content. Prove table relationships, coverage warnings, no recalculation/network/macro execution, and no silent active-sheet/preview-row limit. Independent fixture validity and saved-cache oracle required. |
| DI-14 | Genuine multi-slide PPTX with late-slide markers, ordered text/bullets/tables, speaker notes, hidden slides/shapes and an image-only case. Prove original numbering, separately labeled notes, honest omitted-content coverage and no media fetching/rendering. Required native text/table/notes failures yield zero ingestion calls. |
| DI-15 | Every positive format has actual offline normal/optimized installed extraction and stored-chunk proof, plus corrupt/missing-backend/partial/empty and quoted-path tests. Existing text/web entry points and their scoped regression checks remain unchanged; do not infer broader web support from this unit. |

Keep the old assertion bodies except the precisely documented file-format/help
exceptions; add coverage rather than broadly rewriting accepted tests. Provision
and cache model artifacts explicitly before offline tests. A mocked converter is
not sufficient positive proof. Do not add blanket source suppressions or skips.

## Non-goals and historical placeholders

No user-store scan, deletion, quarantine, replacement or re-ingestion is included.
Previously stored placeholders are a plausible impact, not a confirmed inventory.
Any cleanup needs a separate read-only identification report and exact approved
record IDs/backup/disposition. Do not delete records by a substring search.

No general file-family migration, new semantic chunker, embedding change, RAG
redesign, remote OCR/vision, VLM enrichment, spreadsheet calculation/editing,
presentation rendering/editing, new URL/web conversion, additional Docling
formats, legacy/macro-enabled Office files, password interface or guarantees
for every document layout. Do not
weaken quarantine, source-protection, maintenance admission or model policy.

## Next decision

Review this expanded four-format Docling boundary, proposed format defaults and
installation/OCR requirements, together with the four-format Tools adoption plan.
Gate A must establish the exact compatible package/model manifest and final
construction directive before implementation. Current MAINT UAT remains a
separate pending human activity. No further council was launched by this task.
