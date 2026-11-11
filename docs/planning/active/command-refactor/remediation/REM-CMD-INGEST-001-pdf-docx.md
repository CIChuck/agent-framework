# REM-CMD-INGEST-001 — document extraction, shared chunking and embedding limits

Status: **REVISED PLANNING — explicit test migration and architecture/documentation requirements; fresh review pending**, 2026-11-11. Baseline `7ad916f2` is historical.
This document defines a bounded repair and its dependency-readiness gate. It is
not an approved construction directive or a completed compatibility assessment.
Working branch: `feature/cmd-ingest-001`, based on published command-refactor head
`df62b77d551491cfb33ad2492c711036b09c9d4c` ([PR #15](https://github.com/CIChuck/agent-framework/pull/15)).
[Branch handoff](../validation/document-ingestion/branch-handoff.md) records scope
and construction boundaries. The assessment baseline above remains historical.
The parent is now merged into `master` at `c36e7ee5`; this scoped branch
incorporates that merge. Future INGEST-only review targets `master`.

The maintainer explicitly directs traceable restructuring of affected tests and
one canonical command-architecture document plus substantive affected guide
rewrites. [Recorded clarifications](../validation/document-ingestion/test-doc-revision-authorization.json)
authorize this requirements revision. Test names/files are not immutable when
restructure/replacement is justified; every still-valid behavior must retain
substantive coverage and each retirement needs a reason and disposition.
Documentation completion includes authored content and technical evidence,
beyond a lifecycle/link-check pass. Section G and DI-35/36 bind these obligations.

Prior technical-design reviews at `f43368c5` and assessment-v0.2 reviews at
`1a040de3` remain historical evidence for their exact old bytes. This changed
REM and assessment v0.6 need fresh review. Five rounds are complete. Chuck
explicitly authorizes [one fresh round](../validation/document-ingestion/package-impact/round6-authorization.json):
round 6 of 6, with no budget reset, replacement seat or seventh round. Use
self-contained pinned review inputs without memory/history searches. Stop for
Chuck's guidance if its conditions are unmet. Chuck
reviews the linked revision in parallel. No product/test/guide implementation,
Gate-A effects, model/store operation or delivery is authorized by this update.

The normative [framework compatibility contract](../embedding-compatibility-contract.md)
is part of this REM (SHA256 `1092a332684e3f6a5f9edc3f2355c768775b0f2c01b82bcc97242932334faabb`);
FC-01–14 specialize existing requirements and named
compatibility exceptions. Its positive B/N tests are required alongside refusals.

**Maintainer scope expansion — 2026-11-10:** include XLSX workbooks and PPTX
presentations alongside PDF and DOCX. Existing text and web **reading** capabilities
are retained. Source inspection found no maintained web-to-Memory ingestion
route and no maintained generic automatic `ToolOutputIngester` caller. There is
an active opt-in MCP tool-output snapshot route, separately classified below;
the earlier blanket no-automatic-tool-ingestion claim is superseded.
All-source policy applies to supplied extracted text regardless of origin; this
unit does not invent a URL command or activate automatic storage. The filename is retained
for existing links and historical evidence. Format defaults below are proposed
for document review, not implemented behavior.

**Discussion decisions — 2026-11-10, after `c59e8ed7`:** default ingestion to
`document` chunking with a 512-token budget, overridable per command. Accept
`document`, `recursive` and `fixed` across all ingestion sources, including
existing text/web and tool ingestion. Add model-profile input limits and expected
vector dimensions with enforced overflow checks. Qwen3-Embedding-4B remains an
illustrative profile, not the selected replacement model. Testing starts with
fresh stores; legacy re-embedding/migration is excluded. This revision supersedes
the earlier extraction-only/no-Memory-or-LLM-change boundary where stated below.

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
structured document output supplies the proposed document-aware chunking path;
Markdown is a rendering/export, not the sole structure passed between stages.
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
| `friday-core` | Minimal immutable source/block/chunk/options, ingestion-entry, embedding-space identity and prepared-vector contracts/protocols. No conversion, model execution or policy implementation. Exact additions freeze at readiness. |
| `friday-tools` | Shared document extraction and Docling chunker adaptation; format/coverage/status checks, local assets and safe errors. Retain structure internally and return neutral chunks/provenance. No Chat/TUI imports or second policy owner. |
| `friday-commands` | Standard-library-only file arguments and validation of the two command overrides. No filesystem, Docling or Memory imports; root API54 remains unchanged. |
| `friday-memory` | Shared ingestion entry/default resolution, non-Docling block segmentation, strategies and plan validation; inject Docling adaptation and exact counting. Own durable embedding-space binding and correct document/query roles. Reuse persistence/protection/description rules; no Docling/Tools imports or second split. |
| `friday-llm` | Typed embedding capabilities, model-specific input preparation, accurate token counting, effective-limit checks and returned-vector validation for all callers. No document splitting or storage policy. |
| `friday-chat` | Loads configuration, wires shared capabilities, delegates arguments/extraction/ingestion and renders effective options, statistics and safe errors. No Chat-only chunking algorithm. |
| `friday-runtime` | RuntimeKernel uses the same public Memory factory and resolved embedding capability for pool/non-pool assembly. Deferred/readiness failures cannot instantiate a legacy client or silently fall back. No second policy. |
| Core profiles / CLI compatibility container | The existing public store factory forwards typed binding/admission. CLI delegates RuntimeKernel and exposes its readiness; no independent client fallback or new executable. |

The Core ingestion-entry protocol prevents a new Tools-to-Memory dependency.
Tools consumes an injected capability; Memory implements it. Chat is one
composition root, not its owner. A public Memory factory supplies the capability
to headless clients; the caller constructs Tools with it. No new Memory import
of Tools is allowed. Existing lazy smart_read imports may remain solely for
context summarization; storage cannot bypass the injected entry. Without that
entry, reads remain read-only and explicit storage requests fail actionably.
Existing extraction/admission/opt-in rules remain. Conversation
turns and structured maintenance records are not automatically split into
document chunks; the section E embedding guard still covers their requests.

This is a prerequisite repair for later FILE-001 extraction, **not the complete
FILE-001 command-family migration**. No new registry family, general command
framework or TUI implementation is included. MAINT-001 remains independently
verified at its frozen candidate, with human UAT/acceptance still pending.

### Active routes, shared interfaces and completion claims

| Surface | Current source evidence | Obligation in this unit |
| --- | --- | --- |
| Chat `/ingest` local files/text | Maintained handler, character-sliced storage | Shared entry, all strategies and four-format conversion. No URL input. |
| Headless smart_read text small/large/force_chunked storage and caches | Public injected-Memory tool has direct small-file storage and raw/derived/cache paths. Current Chat supplies no Memory entry/controller; Runtime does not construct this tool. | INGEST corrects explicitly injected public storage/cache behavior without newly wiring it in Chat/Runtime. Storage requested without an entry now fails instead of silently doing nothing. |
| Public ToolOutputIngester capability | Class exists; maintained Chat/Agent/Tools/Runtime caller absent; legacy integration caller exists | Adapt its explicitly called storage boundary and prove headlessly; do not activate automatic ingestion. |
| MCP tool-output snapshot memory | Active Chat opt-in/per-server route through MCPMemoryIngester and CollectionManager | Preserve a single exact structured snapshot and receipt protocol; shared unsplit document-role guard and truthful overflow/failure outcome, FC-02. No document/512 splitting or new activation. |
| Web reader/fetch tools | Maintained reads, no Memory handoff | Retain reads. Supplied extracted web text exercises the shared entry as a capability proof, not proof of a fetch-to-store route. |
| Tools factory and smart_read document routing | Legacy readers/binary skips | TOOLS-DOC companion adopts the four formats after shared interfaces freeze. |
| Lifecycle migration.py / Chat migrate stub | Public legacy code is not maintained wiring; fixed-dimension dummy query and nonexistent CollectionManager method; Chat action is a stub | Remains inactive, with no integration credit or functional repair. Direct calls cannot bypass ordinary guarded-store admission. |

INGEST completion covers active storage paths and explicit public ingestion
capabilities, including the active MCP structured-record boundary, not absent
web/generic automatic wiring or Tools four-format adoption.
The companion owns document routing, pagination and conversion-cache keys;
INGEST owns existing text storage and ingestion-cache safety. Package adoption
needs both proofs; neither unit may claim the other's deferred consumer work.

The Core entry protocol takes immutable extracted-source blocks/text/provenance,
validated options and storage/admission context, and asynchronously returns a
typed receipt with exact stored chunk count, effective strategy/budget,
source/plan identity and safe warnings. Memory's public factory imports neither
Tools nor Chat. The entry owns planning, full-batch embedding validation and
persistence, rather than returning unvalidated chunks for each frontend to store
differently. Exact signatures/serialization freeze at gate A. Cache returns still
perform current identity/options/admission checks before claiming storage.

smart_read source records (`ingested_file`/`raw_chunk`) contain exactly the shared
plan's chunks. Summarization windows can remain separate but cannot supply the
stored raw chunk plan. `chunk_summary` and `file_synthesis` are derived records:
retain their text/type/protection and opt-in semantics, guard their final input
once, and refuse an oversized derived record rather than silently splitting it
into different records. Preflight all source and derived embedding inputs before
the first write; no new cross-record rollback is claimed.

Ingestion cache keys bind source content identity, options/policy, embedding
space, counting/preparation and conversion identities, plus successful storage.
An mtime-only/context-only hit is insufficient. Recheck store opt-in on every
request. Eligible extracted source may be reused, but drift or disabled→enabled
storage requires re-planning/revalidation. Ignore unqualified historical entries
without deleting or blessing them as new ingestion proof.

Successful-storage receipts additionally bind canonical destination vector path,
namespace incarnation (a fresh UUID fixed in its ready sidecar), exact destination
collection set, stored record IDs and source/plan digest. Same embedding space
does not mean the target contains the source. Before skipping storage, validate
the admitted destination and record IDs/provenance. Missing/deleted records,
different root/incarnation or collection selection invalidate completion. Reuse
eligible extraction cache content, then run the common storage entry again;
do not purge/repair historical records or trust a stored boolean alone.

The Core contracts avoid new dependency edges; they do not erase existing ones.
Memory's large-file processor lazily imports the Tools code chunker, and legacy
Tools memory inspection/maintenance/lifecycle modules import Memory without a
declared package dependency. Those edges are recorded, not broadened or repaired
here. Core also already lazily imports Memory in `profiles.py` and
`interfaces/transcript.py` without a declared Memory dependency. Those are existing
compatibility edges, not permission for new backend imports in neutral contracts.
`profiles.py` retains only its existing lazy adapter imports; the transcript
interface is inventoried and unchanged. Code chunking may drive summarization windows only; stored code raw chunks
now come from the shared plan. New policy modules import no Tools and new Tools
storage paths import no Memory directly.

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
   Explicitly resolve Docling's chunking feature and the matching tokenizer
   dependencies as well. Native chunking is implemented in `docling-core` and
   exposed through Docling; a minimal distribution may need a chunking extra.
   Freeze the selected release's actual requirements, not an assumed extra name.
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
6. Freeze a source-linked ingestion **and embedding** inventory: file/text,
   smart_read small/large/cache, explicit ToolOutputIngester capability, conversation
   extraction and compaction, graph scoring, retrieval, lifecycle/promotion and
   maintenance. Classify active/public-not-wired/absent
   routes using the table above; absent routes earn no integration credit.
   Prove headless injection at existing storage handoffs. Inventory roles, legacy
   constructors, precomputed vectors and caches; asymmetric preparation cannot
   be enabled while a relevant caller is unclassified. Freeze exact paths,
   narrow affected MAINT regressions and approved oracle deltas.
   Produce one trace table joining each caller/consumer to path origin, normalized
   destination/open intent, store/embedding readiness, vector role/envelope,
   source-versus-derived policy, exact test node, installed lane and negative
   witness/oracle exception. It consolidates the existing DI/TD obligations;
   it is not another experiment or a new source route.
   Include all direct Chroma/SQLite/file-copy openers: vector adapter/collection
   manager, recovery, mutation participant, pruner, synthesizer, fact checker,
   ConsistencyAnalyzer, BackupManager and the public maintenance module entry;
   include rejection logging, MCP snapshots, consolidation and lifecycle tools,
   plus the annex's transitive consumers. Include Runtime
   pool/non-pool assembly, Core profiles and CLI re-exports/container. Search all
   maintained package source and classify examples/dead paths separately. These
   known seams are a lower bound, not dynamic proof of every possible consumer.
7. Resolve the configured embedding profile to its exact served artifact and
   effective input limit, expected vector dimension, input-formatting convention
   and model-matched tokenizer. Provision offline local synchronous counting;
   server tokenization is a cross-check, not a repeated chunk-count mechanism.
   Unknown/mismatched limits or counters block
   the new ingestion path. Do not download, activate or select Qwen solely because
   this document includes an example. Record performance/compatibility evidence
   separately from model-card specifications.

This gate is **pending**, not a silently assumed success. Before code generation,
the exact versioned implementation directive/manifest and approved scope must be
recorded. The present document is for reviewing the design and those boundaries.
No dependency synchronization or model provisioning has been performed this turn.

### Gate-A effects envelope and assets

This iteration does not execute gate A. Its separate activation must record
exact package/model hosts and artifact URLs, license review, private scratch and
target prefix, numeric download/disk/memory/time budgets and manifest reviewer.
Use verified package-index and model-owner artifacts, no arbitrary mirror or
executable installer. Extra hosts/budget overruns stop work. No global model/HF
cache or working `.venv` mutation is allowed.

Provision one manifest-owned read-only root under the isolated target prefix:
`share/friday/ingestion-assets/<manifest-digest>/`, with tokenizer/layout/table/OCR
files, licenses, revisions and hashes. Production provisioning uses this layout.
Runtime receives the root through composition, not a per-model tokenizer knob;
it never searches/downloads into a global cache. Reject hash mismatch, path escape,
symlink or missing assets before conversion/embedding. Model-repository custom
code requires explicit code review and final-directive coverage at gate A;
otherwise stop. No speculative installation is needed for design readiness.

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
fabricated zero. Retain typed page/block/sheet/slide provenance and access to the
document chunking capability, not only a flattened Markdown string. Docling's
mutable document objects stay inside Tools; return immutable neutral contracts
and bind conversion/chunking to the same source/profile identity.
Expose a typed extraction error with stable failure categories. No `Any`-shaped
ReaderResult dictionary crosses into Chat; no new blanket typing suppression.
The implementation manifest freezes exact signatures after gate A.

The capability must:

- Accept only existing local regular `.pdf`/`.docx`/`.xlsx`/`.pptx` files,
  case-insensitively.
  Apply the explicit format allowlist before invoking Docling. No URL input,
  MIME-based expansion, generic binary fallback or plugin format discovery.
  Restrict Docling allowed formats to those four, require detected format equal
  to the extension-admitted format and exactly one converted document. Reject
  generic ZIP/multi-document expansion, including renamed archives.
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
- Return page count/coverage/warnings separately. Pass structured source content
  into the selected shared chunking strategy; no status messages, filenames-as-substitute-content,
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

These are deliberately extraction rules for the shared chunking policy, not a
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

Structural admission is explicitly permitted inside Tools. Pin openpyxl and
python-pptx (or bounded stdlib OOXML inspection of those facts) in the backend
graph. They may inventory formula/cache status, hidden units, merged ranges,
notes versus comments and resource counts; they supply **no document text** and
never repair or recalculate a file. Docling remains the sole text supplier.
The audit returns immutable scope/coverage facts and refusals, not a fallback
extraction result. Map facts to Docling provenance to enforce the admitted selection (whole-document defaults exclude
hidden/comment content; the companion may explicitly select a hidden sheet
under its retained API). If mapping cannot be proved, refuse the input. Inspect formula and
cached-value views separately; blank output is not evidence of a valid cache.
Reconcile backend warnings/status against a frozen code allowlist: clipping,
skipped required content and unclassified backend warnings refuse before
ingestion. Capture diagnostics per conversion without leaking source text or
installing global log handlers. Bound compressed/expanded bytes, members,
cells/rows/slides and parser work before expensive processing. Gate A proves
audit/output mapping on genuine fixtures; unobservable coverage is a readiness
stop, not warning-only success or authority for a second extractor.

Within INGEST the legacy Tools **document routing** remains unchanged, while
existing text storage/cache paths adopt the common entry above. This is not a
claim that existing Tools document entry points have
adopted Docling. The [TOOLS-DOC-001 companion plan](../proposals/tools-document-adoption.md)
requires separate routing and public-consumer proofs for `ReaderFactory` and
`SmartFileReadTool`, using the same shared converter. The common readiness gate
must preserve typed page/block/sheet/cell/slide provenance needed for that adoption. No duplicate
backend or broad Tools change is authorized by this INGEST allowlist.

## C — path parsing and Chat integration

Add a shared `friday_commands.file_inputs` submodule; keep the existing root
`__all__` and accepted literal API54 expectations unchanged. It consumes the **original
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
- The two new unquoted override tokens before/after the path are reserved.
  A standalone unquoted `--` is allowed only after the path: consume it and end
  file-option recognition. Remaining tokens are literal description, joined as
  before. Return options separately from opaque description so downstream line
  parsing cannot reinterpret that suffix. Description quotes remain literal.
  Prefix lookalikes of the two override names remain ordinary description.
  `/ingest a.txt -- notes --chunking=fixed` retains the literal option text.
  `/read` refuses unquoted chunking overrides before I/O; quoted option-like
  filenames remain paths. This change is scoped to the default file handlers.

Chat routes the untouched raw tail to that helper only for the default read/
ingest handlers after resolving the actual handler. Custom handlers and other
commands retain their original arguments/authority; aliases of a default file
handler get the same file parsing. `_parse_command_input` remains unchanged for
all other paths. No join-and-strip workaround or global `shlex` replacement.

`SmartFileReader` delegates PDF/DOCX/XLSX/PPTX to the shared extraction capability and maps
its typed result into `FileReadResult`, adding only sideband backend/coverage/
warning fields needed for presentation. Text/CSV/TSV/JSON behavior remains.
`/read` displays real extracted text and document metadata; it does not embed or
chunk merely to display a file. `/ingest` uses that same successful source through
the selected chunking strategy and the shared Memory ingestion entry once.
Remove the Chat-owned character slicer from that path, rather than chunking
twice. Keep the metadata helper and existing protection/storage semantics.

Success is shown only after the memory capability returns an exact positive
chunk count for a document. Existing storage exceptions are not turned into
success. This repair guarantees no memory/embedding write before successful
extraction; it does **not** introduce an ingestion rollback transaction or claim
existing multi-chunk storage failures are atomic. Keep admission-gate behavior.

Remove the common placeholder method. Replace XLSX placeholder output with real
workbook extraction, and add PPTX admission explicitly for both `/read` and
`/ingest`. All other new Docling formats remain disabled. Existing text/table
and web reading/fetching routes remain. The route table controls ingestion claims;
no URL support is added to the local-file converter.

The legacy text helper maps malformed `--lines*` tokens to a 100-line limit.
Record this as a deferred file-parser follow-up, not a document rule. Preserve
it for text/table compatibility here, but report effective line limit and
`truncated` in read/ingest receipts. The new literal `--` suffix is exempt from
that scan. Documents refuse any pre-terminator `--lines*` token. A limited source
must never be reported as the complete file.

Update only read/ingest help/detail and their changed response fields. Preserve
the remaining catalog, aliases, parser quirks and accepted metadata oracles.
Retain immutable snapshots; supply a separate exact exception comparison.

## D — shared ingestion chunking: document / 512 tokens by default

The maintainer selected these defaults for **all ingestion sources**, not only
PDF/DOCX/XLSX/PPTX. Apply one policy to command/text ingestion, explicit supplied
web/tool payloads and the active storage handoffs classified above. This policy
does not establish a new maintained web/automatic-tool route. Retain
source extraction, tool admission, quarantine/provenance and store-to-memory
controls. This is not permission to auto-ingest previously disabled tools, fetch
new URLs, or re-chunk conversation/maintenance records as documents.

MCP tool snapshots are existing structured records, not document-ingestion
payloads: preserve their exact single-record and transcript-receipt protocol
under the shared unsplit guard, as required by FC-02. The all-source document
policy does not override that protocol or create a second snapshot chunker.

The new configuration contract is:

```yaml
ingestion:
  chunking:
    strategy: document
    max_tokens: 512
```

`strategy` accepts exactly `document`, `recursive` or `fixed`; `max_tokens` is a
strict positive integer. Both keys are optional with the defaults above. Reject
invalid configured values at configuration preflight. The current schema does
not implement this section yet. Resolve explicit per-ingestion overrides first,
then YAML settings, then built-in defaults. An omitted option does not erase the
other configured value. Tool callers pass the same typed options; future TUI
consumers can reuse the interface without importing Chat.

Proposed command forms:

```text
/ingest "report.pdf"
/ingest "report.pdf" project notes --chunking=recursive --chunk-tokens=768
/ingest "report.xlsx" --chunking=document --chunk-tokens=512
```

The first form uses the effective configured defaults, initially document/512.
The two recognized `--name=value` overrides may precede or follow the source path;
remove them before constructing the description. They are ingestion options,
not `/read` options. Quoted option-like filenames remain paths. Empty values,
unknown strategy names, non-integer/zero/negative token budgets, repeated instances
of either override and missing `=` are usage errors before source I/O or network
fetch. Missing `=` refers only to exact tokens `--chunking` and `--chunk-tokens`:
`--chunking fixed` refuses, while `--chunkingX=fixed` and `--chunk=512` are description. Preserve all other description/parser semantics. No launch-time global
chunking flags or per-format precedence layer is added in this unit.

| Strategy | Boundary rule | Size enforcement |
| --- | --- | --- |
| `document` | Structure-first policy: Tools' native Docling hybrid adapter for converted documents; Memory's deterministic block segmenter for supplied text/Markdown/code/JSON/YAML/CSV/TSV and extracted web text. Preserve source boundaries and provenance. | Refine oversized units and merge suitable small units within the final-input budget. Both adapters implement the same policy contract; the text adapter is a defined implementation, not a fallback when Docling fails. |
| `recursive` | Split at paragraphs, then sentences, then safe text boundaries for oversized spans. No LLM-based semantic segmentation. | Count with the active embedding model's tokenizer, including final contextualization. No four-characters-per-token approximation as enforcement. |
| `fixed` | Deterministic bounded text windows, preserving Unicode and source coverage. | Token-sized windows, not the legacy Chat character count. It is an alternative strategy, not a promise of the old byte-for-byte chunks. |

512 is the final embedding-input **budget**, not a requested exact chunk length
or a reason to pad text. Count repeated headings, table headers, query/document
formatting and special-token overhead where applicable. It is distinct from the
embedding model's maximum accepted sequence length. Keep sheet/slide boundaries,
source order and neutral per-chunk provenance; do not merge unrelated sheets or
slides merely to fill a budget. Structured table blocks retain row/header context across
chunks. Freeze an explicit lossless split-or-refuse rule for an individual cell,
row or contextual prefix that cannot fit. No dropped source tail or silent
truncation. Do not introduce another overlap CLI/config option in this unit;
freeze/document each strategy's bounded overlap/header behavior at gate A.

For non-Docling sources Memory preserves the original Unicode source and offsets,
groups nonempty text spans at blank-line boundaries and associates Markdown ATX
headings with following blocks without rewriting source text. Code fences and
structured text remain opaque source spans; no JSON/YAML/code execution or
semantic parser is added. Oversized blocks use the declared recursive refinement
with the exact counter; preserve all source spans, including separators, through
provenance. Fix heading/fence/blank-line rules against fixtures at gate A. Empty
or whitespace-only text refuses ingestion. This implementation needs no Docling
extra and imports no Tools/Chat. Missing conversion extras affect only the four
document formats; default text ingestion still works with the local counter.

CSV/TSV passed as plain text has no declared table schema/header: preserve all
source spans and explicitly report `table_structure_not_supplied` coverage,
rather than infer a header or claim repeated-header table semantics. The header
carry promise applies to Docling/native or explicitly supplied typed table
blocks. A producer that supplies table structure can use that path. This unit
does not add CSV header inference or silently relabel a first data row as a header.
Tests distinguish structured tables from plain delimited text, including late
rows and honest coverage; changing existing text extraction is not required.

Memory owns default/override resolution and validates the complete chunk plan.
It receives a typed document-chunker capability and model token counter through
injection. Tools owns Docling adaptation; recursive/fixed strategies are shared
Memory implementations or explicit injected implementations. Core holds only
minimal common contracts. Do not add a Tools/Memory import cycle or leak third-
party document/tokenizer objects across packages. No consumer cuts an accepted
chunk plan again before persistence. Read/summarization windows may retain their
existing policy; source records use the shared plan and derived summary records
use the unsplit embedding guard, as explicitly classified above.

The existing `smart_file.chunk_size`/`chunk_overlap` and legacy estimated-token
settings are not aliases for these new token fields. They may remain for scoped
legacy read/summarization operations; never interpret 2,048 characters as 2,048
model tokens or use those settings as a hidden second ingestion default. Freeze
exact intentionally changed chunk/count/help/config oracles without editing old
snapshots broadly. The ingestion response reports effective strategy, budget and
chunk count and effective line limit/truncation when applicable; persisted chunk metadata records policy/version, embedding profile
identity and source-unit provenance using storage-compatible values.

## E — embedding profiles and enforced limits

Embedding profiles remain in the model catalog (`models-config.yaml` or the
configured equivalent); the main YAML selects named services through the existing
`embedding_pool`. Extend the strict shared LLM schema and resolver rather than
adding ignored keys to YAML. The profile's proposed `embedding_options` gains:

- `max_input_tokens`: strict positive integer declaring supported input capacity.
- `expected_dimensions`: strict positive integer for validating returned vectors.

Both keys remain optional in existing YAML. **Both verified capabilities are
required in the resolved embedding service, not necessarily in the user's
configuration.** The shared resolver may obtain omitted values from an explicit,
artifact-bound readiness record qualified at gate A; this applies equally to
catalog-backed and legacy non-catalog Chat, Runtime and maintenance construction.
An omitted new YAML field alone must not disable an otherwise qualified existing
service or require editing every subsystem's configuration. Explicit dimensions
must match the qualified deployment; an explicit token cap may select a smaller
supported limit under the overflow rules below. No guessing from an arbitrary
alias, hidden default dimension or silent unguarded mode is allowed.

Gate A must qualify the maintained baseline configurations with the new fields
omitted. If equivalent verified readiness cannot be established for a selected
baseline deployment, stop and report the compatibility gap for a maintainer
decision before claiming readiness or freezing construction. Do not treat
successful parsing followed by a newly unusable service as backward compatibility.
An actually unresolved or contradictory capability still refuses before provider
I/O. Unselected profiles do not break application/config loading, and a failure
in an independent unused service does not disable a qualified service. Packaged
examples receive measured values only after gate A; user-edited YAML is never
overwritten. Read-only `/read` needs no embedding capability and remains available.

### Existing pool and subsystem compatibility

The maintainer's premise is an acceptance requirement: retain the existing
embedding configuration mechanism and keep its existing consumers operational
under an admitted compatible namespace. Extend the shared resolver/adapter;
do not introduce a parallel embedding configuration for document ingestion.

- Keep existing service names, `embedding_pool.default_service`, profile
  references, endpoints/credentials, batch/cache options and resilience overrides
  meaningful. Preserve maintained non-pool configuration shapes and the existing
  `embed_query` / `embed_documents` call interfaces. No automatic model selection,
  vector resizing or requirement to add an `ingestion` embedding service.
- `/ingest` inherits the memory service selected by the existing composition.
  In canonical Chat this is the pool default; legacy `embedding.embedding_service`
  remains a disclosed no-op/hint under FC-10, not a newly enabled override.
  Other consumers retain their actual explicit pool bindings; no subsystem is silently
  redirected to the default. Service names and timeouts/retries may differ while
  resolving to a compatible embedding space.
- Enforce one embedding space per Memory namespace, including the graph vectors
  compared with that namespace's query vectors. Compare resolved model/artifact,
  dimension, normalization and query/document preparation identity, not pool
  names or dimensions alone. Independent namespaces may use different models;
  this is not a global single-model requirement.
- Keep model/counter preparation and request/result checks in shared LLM
  infrastructure and namespace admission in Memory. Consumers delegate through
  those contracts; they do not each implement tokenization, prefixes or guards.
  The document/512-token ingestion default does not re-chunk conversation turns,
  graph relationships, extracted insights, compaction summaries or maintenance
  records. Those unsplit inputs still obey the selected model's effective limit.
- Configuration compatibility does not authorize identity-free legacy stores,
  mixed-space comparisons, silent truncation or bypassing invalid results. The
  separately approved explicit-fresh-store policy and declared preparation/role
  corrections still apply. Preserve old files and disclose these intentional
  exceptions instead of promising unchanged vectors or unrestricted legacy use.

Freeze each of these consumers as an explicit readiness trace row, including
indirect consumers of already stored vectors:

| Consumer | Compatibility proof required |
| --- | --- |
| Conversation extraction | Retain its extraction LLM binding; relationship embeddings and stored insights/summaries use their existing embedding bindings with compatible identity. Qualify Runtime's optional extraction-service selection separately from Chat's current wiring. |
| Graph scoring and semantic recall | Maintained Chat/Runtime omit a GraphPathScorer and remain unscored; actual query/vector/priming errors propagate. Both sync and async scorer APIs are public-injectable only, with identity-safe comparison and absent-vector behavior tested separately under FC-08. No new wiring/preflight for an unused scorer. |
| Synthesis, re-embedding, pruning and clustering | Retain the maintenance binding. New vectors and existing-vector comparisons respect the destination namespace even when no new embedding call is made. |
| Promotion, decay, reactivation and session compaction | Indirect embedding/storage handoffs retain service selection and record semantics; oversized records fail actionably without silent truncation or document re-chunking. |
| Command/tool ingestion and derived summaries | Reuse the existing memory binding and shared policy; retained opt-in and source/derived boundaries apply. |
| Headless Runtime, Core factories and CLI compatibility | Catalog and non-pool paths preserve existing configuration and embedding interfaces; no independent fallback or unqualified direct client. |
| MCP snapshot, public consolidation, lifecycle tools, legacy backup/analyzer/module and indirect Agent/multi-agent/MEMQ users | Every route in the normative annex is classified and joins FC-01–14 proof; a safe refusal alone cannot establish successful supported B/N compatibility. |

These are required compatibility proofs, not permission to redesign the
subsystems or a claim that the current implementation already passes them.

Retain the endpoint, model identity/revision and existing batch/cache options.
No operator tokenizer setting or arbitrary query/document-instruction setting
is required. Resolve the matching tokenizer/counting mechanism and supported
input convention from the exact model/artifact identity. Record that resolution
in readiness/provenance; do not silently guess from an arbitrary server alias.
Chunking counts must use provisioned offline synchronous local tokenization
bound to the served artifact/preparation identity, including special tokens.
Docling's tokenizer adapter calls it locally, never an async/network bridge for
each split. Server tokenization may verify boundary parity at gate A/preflight;
it does not replace local assets. Any unresolved parity fails readiness.

Hosted profiles have no inspectable local weight digest. They require a stable,
provider-attested deployment/model revision plus the verified preparation and
dimension contract; a mutable alias alone is unsupported by this guarded unit.
Their offline tokenizer/BPE assets (for example, a supported tiktoken encoding)
must be explicitly provisioned/hashes bound in the same assets root. No first-use
download is allowed. If immutable provider identity or exact counting cannot be
established, that selected hosted route refuses embedding operations actionably;
catalog loading/read-only file commands remain possible. Do not silently switch
the model or add an unguarded hosted compatibility lane. Gate A records qualified
existing-provider routes and explicit unsupported aliases, not generic provider
support inferred from one model's success.

The following is an **illustration only**, not a selected/installed model or a
valid configuration for today's unchanged schema:

```yaml
profiles:
  qwen3_embedding_4b_local:
    kind: embedding
    endpoint: local_lmstudio
    dialect: openai_embeddings
    model: openai/qwen3-embedding-4b
    model_target:
      model_id: qwen3-embedding-4b
      family: qwen3_embedding
      revision: "<exact downloaded artifact revision>"
    embedding_options:
      max_input_tokens: 32768
      expected_dimensions: 2560
```

An illustrative main-config binding is:

```yaml
embedding_pool:
  default_service: memory
  services:
    memory:
      profile: qwen3_embedding_4b_local
      resilience_overrides:
        timeout_seconds: 60
    maintenance:
      profile: qwen3_embedding_4b_local
      resilience_overrides:
        timeout_seconds: 60
```

Qwen publishes 32K input context and up to 2,560 dimensions for this model. The
example alias/revision must match an actual supported artifact/server, and the
profile does not command the server to increase context or resize output.
[Official model card](https://huggingface.co/Qwen/Qwen3-Embedding-4B).
The current configured Nomic profile remains selected until a later explicit
model choice. Gate A verifies its actual artifact/limits/dimensions as well;
this example does not silently replace memory or maintenance bindings.

Some embedding models distinguish search queries from indexed documents using
input conventions. Apply a verified convention once inside the shared LLM
adapter, accounting for any server-applied formatting. For Qwen, the reference
retrieval usage formats queries with an instruction and leaves documents without
that instruction. Do not prepend a Nomic-specific convention to Qwen or persist
embedding-only instructions as document text. Audit `embed_text` versus
`embed_query`/`embed_documents` call sites so document storage is not accidentally
formatted as a query. Tests cover both paths. No hosted LLM call is needed for
local token counting or these deterministic formatting rules.

The all-caller inventory explicitly includes ChromaVectorStore query-without-
precomputed-vector (currently routes through embed_documents), stored-memory
synthesis (currently embed_query), collection promotion/decay/reactivation,
Chat recall/ingestion and maintenance pool/non-pool construction. Correct only
those role/capability handoffs, not maintenance stage ordering or prompts. All
indexable/derived stored text uses the declared document role; search requests
use the query role. Preserve an explicitly different clustering role only if
the frozen service contract requires it and the identity records it. Enabling
asymmetric conventions with an unclassified caller is forbidden. Existing
MAINT verification remains historical; new narrow affected regressions and
aggregate installed proof are required for these seams.

Overflow is a fixed enforcement rule, not another user-configurable policy:

1. Resolve the effective limit as the minimum of the configured supported cap
   and verified artifact/server loaded capacity, including any smaller effective
   per-input serving batch/ubatch ceiling. Do not mistake an internal evaluation
   batch size for a sequence cap without deployment evidence. A larger cap cannot
   override a smaller loaded context. Missing/contradictory identity or capacity
   blocks readiness; do not silently assume the model-card maximum.
2. Validate the configured/requested chunk budget against that capacity and the
   required formatting overhead. Reject an invalid override with the supported
   limit; do not silently clamp it. The budget already includes overhead; do not
   subtract it twice. Split content at the chunking stage.
3. Count each final contextualized/prepared input, including server/template and
   special-token effects. It must fit the requested chunk budget for ingestion
   and the effective model limit for every embedding caller. Preflight all chunks
   in an ingestion request before the first embedding/storage call. Unknown
   counting/formatting behavior is not permission to send unbounded input.
4. Recheck at the shared LLM embedding boundary for documents, queries, tool
   outputs and maintenance callers. Reject oversized input before provider I/O;
   never silently truncate or return multiple vectors for one supplied input.
   Set backend truncation refusal where supported and prove no hidden truncation
   with boundary controls for the supported deployment.
5. Validate response cardinality, expected vector length and finite numeric
   values before accepting a batch. Reject missing/extra/wrong-dimension outputs.
   Validate provider index semantics as well: reorder only on unique complete
   indices in0..N-1; refuse duplicates, gaps and out-of-range values. A provider
   with no index field needs a documented/proven order-preserving contract at
   gate A, otherwise refuse. Bind output/cache entries to the original input,
   query/document role and embedding-space identity; shape checks alone do not
   establish vector-to-text correspondence.
   Ingestion validates its full embedding result before handing it to storage;
   this does not introduce rollback for unrelated multi-write storage failures.

### Durable store identity and fresh-store admission

Memory owns a versioned canonical embedding-space identity: actual local model/
artifact revision/digest or qualified immutable hosted deployment revision, output dimension/normalization, query/document preparation
revision, tokenizer/special-token convention and distance metric. Freeze exact
canonical encoding/hash vectors at gate A. A mutable profile alias, endpoint URL
or matching vector dimension is not identity; credentials never enter it.

Here **root means the normalized vector directory**, not its memory parent:
Chat uses `FridayChatMaintenanceLayout.vector_directory` (normally `.friday/vector`);
Runtime uses resolved `RuntimeConfig.chroma_path`. The file is exactly
`<vector-directory>/embedding-space.json`. Graph storage is a separately resolved
path; graph vector envelopes must match this space and are not inferred from
the graph file being nearby. A ready binding includes a random immutable namespace
incarnation for destination receipts and recovery; same model identity does not
make two roots the same namespace.

For persistent stores, use a root-level `embedding-space.json` sidecar as the
single authoritative binding for that root's vector namespace and collections.
Do not create two independently editable identity authorities. Check it before constructing a
Chroma client that might mutate its directory. Only an explicitly requested
fresh root may be created/bound; an existing unbound root or collection is
`legacy-unbound` and refuses this stack's vector reads/writes before provider or
store-client I/O. No scan, stamping of an existing store, implicit get-or-create
upgrade or inference from old per-record metadata is allowed. A collection in
the new namespace inherits its root's identity; no client may attach an existing
collection from a different/unbound root. Ephemeral stores bind before use too.
Creation uses an exclusive pending marker before client initialization, then an
atomic ready-marker replacement only after successful initialization, with the
canonical identity/schema recorded in both states. Concurrent creation has one
winner; pending, malformed or inconsistent state refuses reopen without repair.
Freeze exact filesystem durability primitives at gate A; no general recovery
machinery is added. No marker is installed into a pre-existing unbound directory.

Validate configured/current identity at create, reopen and every vector read/write,
including lifecycle and maintenance operations. A same-dimension artifact or
preparation change still refuses; leave store bytes untouched on refusal.
Graph vector writes from extraction/REEMBED and recovery preservation carry
reserved identity envelopes, not identity inferred from dimensions. Both sync
and async GraphPathScorer APIs are public-injectable, not wired by maintained
Chat/Runtime composition. When explicitly injected, selected graph-vector
provenance is checked before a query embedding/comparison: unknown/foreign or
invalid existing vectors fail that semantic operation, with no silent zero,
skip, backfill or recomputation. Genuinely absent vectors keep their existing
zero contribution only in sync or async-without-fallback scoring. Qualified
async fallback still embeds only missing edge/target components and scores them;
never substitute a foreign/invalid existing vector. Ordinary maintained unscored recall performs no graph-vector
comparison and gains no provenance preflight on that unused scorer. Actual
query/vector/insight/summary guard failures still propagate. Graph text rendering
does not acquire an embedding requirement. FC-06/08 bind the distinct proofs.
Precomputed vectors must carry a runtime-validated identity envelope matching
the store and the declared query/document role. Bare float vectors are not
admissible through the guarded store boundary. Add the narrow Core/Memory query
contract extension and update its actual call sites explicitly, with positive
and refusal tests; no arbitrary caller may bypass admission by supplying a vector.
Store identity does not include the chunk budget: compatible re-chunking is
allowed, while ingestion caches separately bind strategy/budget and source/plan.

The selected Nomic model currently receives raw text. Applying its verified
task prefixes changes vector preparation even without selecting another model.
Enable that verified convention only with the new bound fresh-store path after
all role handoffs pass. Never mix old unprefixed vectors with new preparation;
unknown legacy stores refuse rather than silently migrate. Record whether the
served artifact already applies prefixes to prevent double preparation.
[Nomic's task convention](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5).

Tool/ingestion and embedding-service caches bind resolved source/input identity,
strategy/budget where relevant, role, embedding space, counting/preparation and
conversion profile. A stale cache cannot bypass admission or the guard; ignore
it rather than purging user records.

**Automated test-store decision:** use fresh bound disposable stores for all
new-pipeline tests, including preparation changes to the current model. No legacy
migration or bulk re-embedding implementation is required. The later explicit
[upgrade-policy decision](../approval/ingest-existing-store-policy.md) separately
selects fresh-store-required behavior, as specified below. Do not scan, delete or reset current stores as a
side effect of planning, startup, a profile edit or an ingestion command. Any
later requested reset must identify the actual test-state scope; no such reset
has been performed here.

### Assembly, direct clients and identity-preserving recovery

RuntimeKernel is the preferred headless assembly, using the same public Memory
factory as Chat. Core `create_vector_store` forwards verified identity/admission
to persistent or ephemeral adapters, refusing a missing/invalid identity before
client construction. CLI's container and profiles module delegate/re-export
those surfaces; source inspection finds no independent CLI embedding constructor.
Tests still cover the exposed CLI access to prevent fallback. All pool/non-pool
constructors resolve the same capability or retain a deferred typed refusal.

Separate store-identity admission from embedding-execution readiness: a snapshot
or stored-vector inspection need not tokenize or call an embedding provider when
the immutable configured/store identity is already resolved and matches. It
still requires namespace admission and cannot infer an unknown identity. Actual
new embedding requests require the complete counter/capacity/service readiness.
This avoids treating an offline embedding provider as permission to bypass a
binding check or as a reason to initialize it during a safe snapshot.

Use a lazy ready-or-unavailable capability at application assembly: parsing a
catalog/config and registering `/read` must not instantiate Chroma, create a
namespace, initialize model/tokenizer/provider resources or open a legacy graph.
Inert embedding-service/configuration objects that only hold validated settings
and perform no provider/network/model/store I/O may be constructed; the gate
does not require eliminating those existing lightweight objects. A memory-dependent
operation first resolves that capability; on failure it returns a stable reason
and remedy without touching the store/provider. Background consolidation and
exit maintenance obey the same check, never silently become successful no-ops.
The maintainer-selected fresh-store policy and matrix below control readiness;
this lazy boundary preserves read-only command availability without a legacy mode.

FC-01 includes resourceful extractor/rejection-log construction in this boundary:
the packaged log lives inside vector/ today and must not pre-create a namespace
or mutate an old root. FC-10/11 preserve path origin before CLI/default merging
and order real maintenance model probes after namespace admission.

Every maintained or public guarded direct opener must use the common Memory
admission helper **before** PersistentClient, raw SQLite/graph reads or live
file-copy effects: recovery discovery/export/restore, mutation participant,
pruner, synthesizer, fact checker, ConsistencyAnalyzer, BackupManager/module
entry surfaces and adapters/collection manager. FC-03 retains admitted public physical backup creation and same-incarnation
restore with a bound receipt and no sidecar overwrite, separately from the v2
recovery API. It refuses unsafe roots, cloning and identity-free live restore. Readiness/provenance failures propagate as typed failures rather than
being swallowed as empty results, skipped pruning or successful maintenance.
Each direct opener targets exactly the layout's normalized vector directory.
Remove its `[memory_dir, memory_dir/vector]` probing/fall-through from guarded
paths: a refusal ends the operation and cannot select a second namespace.
Existing BackupManager signatures use only the fixed marker-metadata selector
in FC-03 for minimum admission and new-marker protection, not new data-layout
discovery/default destinations or a physical-backup repair. Pre-existing partial
legacy-copy limitations are FU-014; classify them as baseline failures without
claiming complete recovery. Other clients lacking their required resolved
admission fail rather than guess. No model-equivalence or filename probe authorizes fallback.
Retain ordinary operation-specific error policy otherwise. This is identity
admission, not a change to verification/synthesis logic or maintenance sequencing.

New bound namespaces produce version2 logical recovery snapshots. FC-03's
identity-receipted public physical backup is a separate artifact family: it
retains BackupManifest and is not accepted by the logical-v2 loaders or used to
weaken their strict version matrix. The snapshot manifest and
logical-vector artifact record the canonical embedding-space identity/digest,
namespace incarnation and a hash/immutable copy of the ready sidecar. Include
the normalized sidecar path, binding digest and incarnation in the versioned
layout fingerprint. Graph artifact checks preserve vector-envelope identities.
All those values must agree with each other and the currently admitted live
namespace before a live client is opened or any snapshot/live file is changed.
Snapshots preserve the binding as evidence; it is not a second live authority.

Restore/automatic rollback in this unit targets the same layout and namespace
incarnation only, with matching space. No cross-root import/clone is added.
Preflight artifact hashes/schema/binding and graph provenance before deleting or
repopulating any collection. Same-dimension different-space, missing/malformed/
pending binding, identity-free snapshot or different-incarnation destination
refuse with zero live-store/provider mutation. A successful rollback restores
data under the original ready binding and leaves its sidecar bytes unchanged;
restore must never copy a snapshot identity over an unrelated live sidecar.
If the binding itself was changed/lost during a failed operation, refuse automatic
restore and retain the existing recovery-required reporting; do not auto-rebind.

Private vector-rebuild preflight may create an owned temporary namespace bound
to the snapshot's verified space, explicitly marked non-live and unable to become
a user restore destination. The live restore still requires original incarnation.
All temporary clients use the same admission helper; there is no test bypass.
Old version1 snapshots/journals stay untouched and readable for offline hash/
schema inspection, explicitly marked identity-unbound. They cannot authorize
new bound-store restore, client-based rebuild or inferred identity. Never stamp,
upgrade, delete or re-embed them. Old journal scheduling/token rules do not change.

The exact snapshot schema additions/dispatch, fingerprint vectors and fixture
exceptions freeze in the final directive. Add versioned models without relaxing
strict existing validators. Recovery ordering, snapshot quiescence/token ownership,
rollback triggers, ULP checks, journal lifecycle and user approval stay intact.
These narrow identity seams explicitly amend the earlier recovery exclusion;
they do not authorize recovery-engine redesign or a new migration framework.

### Versioned Memory-to-Chat recovery handoff

Keep `MemorySnapshotManifest` and its version1 validators/readers strict and
unchanged for historical interpretation. Add an explicitly named v2 model and a
public closed version-discriminating loader/envelope in Memory maintenance.
Only exact versions1/2 dispatch; malformed/unknown discriminants and mixed
payloads refuse. Active bound recovery explicitly requires the v2 member.
Do not broaden or silently rebind the old public class to accept both versions.
Expose the v2 model/typed loader through necessary Memory maintenance/root
exports, appending names without changing old bindings. A strict Pydantic
envelope can serve the existing typed `AtomicJsonStore.read_model`; no `Any`
payload, unchecked cast or generic serializer rewrite is needed.

Chat adds a separate strict `RecoveryBundleManifestV2`, version2 participant
writer/reader path and a closed version-dispatch inspection surface. Retain the
old aggregate model/readers as version1. The only compatible combinations are:

| Aggregate bundle | Embedded Memory | Embedded Transcript | Allowed use |
| --- | --- | --- | --- |
| Version1 | Strict Memory version1 | Existing Transcript version1 | Offline historical inspection only; never a bound-store restore. |
| Version2 | Strict identity-bearing Memory version2 | Existing Transcript version1 | Current guarded snapshot, exact verification and same-namespace rollback. |
| Any other or mixed combination | Any | Any | Refuse schema/version admission; no live effects. |

`coordinator.py` must use the typed Memory v2 loader, build the Chat v2 aggregate,
and carry that exact type through `_SnapshotEvidence` and the active rollback
path. `artifacts.py` writes/reads the v2 model and independently reparses the
referenced Memory v2 participant; embedded and referenced canonical payloads,
hashes, run identity, sidecar/space/incarnation and participant fingerprints must
match exactly. It never falls back to v1 after a v2 parsing failure. Retain all
existing path confinement, owner checks, hashes, timestamps, Transcript validation
and participant uniqueness rules. Chat reorganization/root exports may append
necessary v2 types/loaders without rebinding v1 names. Offline dispatch remains
closed and must not return an identity-free object to the active restore method.

The identity-bearing **Memory participant fingerprint** is the v2 digest of its
explicit paths plus sidecar binding/incarnation. Chat's separate
`FridayChatMaintenanceLayout.layout_fingerprint` stays the existing path-only
version1 digest used by leases/journals/approval. The aggregate checks that
path fingerprint and, independently, `participant_layout_fingerprint` against
the v2 Memory manifest and current admitted namespace. Do not substitute one
fingerprint for the other. No `layout.py`/`assembly.py` fingerprint change,
Transcript version bump, journal-schema change or maintenance-order change is
authorized. Generic AtomicJsonStore behavior remains unchanged; only the typed
models supplied by its callers change. The final directive freezes exact
versioned exports/loaders and fixture exceptions before product work.

### Execution, cancellation and admission

Conversion/OCR/structural audit and repeated chunk-count work run off Chat's
event loop in an owned worker thread with bounded input/output and per-request
state. It receives no embedding/provider/store capability. Local counting is
synchronous inside chunking; final LLM batch preflight is offloaded when needed
to keep the event loop responsive. Retain shared command admission for the whole
request, explicitly including conversion: competing maintenance can report busy.
This unit does not shorten admission or introduce concurrent memory mutations.

Cancellation marks the request ineligible for storage, discards late worker
results and waits for the worker to quiesce before releasing admission/resources.
Use shielding/cleanup so cancellation does not leave a writer-capable orphan;
the worker never performs ingestion. Report progress/finishing status rather
than promise instantaneous cancellation or a hard kill of native code. Gate A
measures worst-case cancellation and applies selected converter/resource limits.
If bounded resource/cancellation behavior cannot be supported, stop and propose
an explicit execution-boundary amendment; do not add a general worker framework
or claim Python threads provide an OS sandbox. Existing failures after storage
begins may be partial; no new ingestion transaction/rollback is implied.

[Docling chunking](https://docling-project.github.io/docling/concepts/chunking/),
[model-bound tokenization](https://lmstudio.ai/docs/python/tokenization) and
[loaded/model capacity metadata](https://lmstudio.ai/docs/developer/rest/list)
are upstream design references, not candidate-installed or backend readiness proof.

### Existing-store upgrade policy — explicitly selected by the maintainer

The [recorded answer](../approval/ingest-existing-store-policy.md) requires an
explicitly configured fresh store, preserving old files and `/read` availability.
It is distinct from the earlier testing-only decision. **There is no legacy
mode** in this unit: missing identity never enables raw preparation, unguarded
reads/writes or an implicit stateless chat fallback.

The request mechanism uses existing destinations, not a reset/upgrade command:
set Chat `memory.persist_directory` to a new, non-existing vector directory
under a deliberately selected new state parent. For example, this is a path
example only and is not applied to current configuration:

```text
memory.persist_directory = /path/to/new-friday-state/vector
derived graph path       = /path/to/new-friday-state/graph.json
identity sidecar         = /path/to/new-friday-state/vector/embedding-space.json
```

Chat's existing layout resolver derives that sibling graph path. Headless Runtime
clients explicitly configure `RuntimeConfig.chroma_path` and a consistent new
`runtime_data_root` using the existing path/containment rules. Select fresh graph
and access-WAL paths as part of that layout; existing unknown-provenance graph
vectors or buffered work cannot be silently imported into a fresh vector space.
Transcript history, backups and old namespaces are not copied, replayed, deleted
or bulk indexed by this selection. Do not rewrite either dirty example YAML.

The public factory takes a typed open intent: `OPEN_BOUND` opens only an admitted
matching namespace; `CREATE_FRESH` requires an explicitly supplied absent path.
**Unset is not explicit:** Chat's unset `memory.persist_directory` and Runtime's
absent raw vector-path setting never authorize creation, even if their fallback
`.friday/vector` or `.friday/chroma` directory is absent on a first run. The user
sees a readiness diagnostic asking for a destination to be configured; `/read`
still works. A supplied raw setting equal to the usual default is explicit and
can qualify if absent. Preserve the raw-key-origin bit before defaults/merging;
do not infer it by comparing the resolved string with its default value.
Runtime's already-supported raw configuration locations preserve this origin.
Programmatic headless callers supply a typed StoreOpenRequest containing an
explicit destination/open intent; a default RuntimeConfig alone is not a fresh
creation request. The exact typed signature freezes at gate A, not a new CLI flag.

Frontends derive CREATE_FRESH only for that explicit absent destination when a
memory-dependent operation is requested, never from an unbound directory or
profile edit. Fallback paths are diagnostic/OPEN_BOUND destinations only: an
already ready matching bound default may open, but an absent default cannot be
created without explicit origin. Config parsing and `/read` never create it.
Fresh creation preconditions are exact: the selected vector directory, the
resolved graph file, and the configured access-WAL path must all be absent.
An unconfigured WAL is absent for this purpose; do not discover another WAL by
scanning. Any existing graph or configured WAL, even empty, refuses CREATE_FRESH
before directory/marker/client/provider creation, with its path and the remedy:
select new associated destinations. Never ignore, adopt, truncate or copy it.
Apply checks under the normal admission/creation boundary and recheck before the
ready marker. An external race stops readiness; it cannot bless a newly appeared
file. A pending namespace newly allocated by this attempt is not auto-cleaned or
repaired, and pre-existing files remain untouched.

For Runtime, `runtime_data_root` is a container, not itself the vector namespace:
reusing it is permitted only when the selected vector, actual resolved graph
and configured WAL are all absent. Existing unrelated transcript/artifact files
remain in place and are not replayed into the new namespace. If reused root
contains its usual existing graph or WAL, refusal is mandatory. Choosing a new
runtime_data_root instead also selects fresh transcript/artifact locations by
the existing containment rules; disclose that effect and copy/reset nothing.

A pre-created empty directory is still existing/unbound and refuses; choose a
different absent destination. There is no automatic suffix, rename, fallback
root or stamping of old content. Direct API callers supply their intent and
resolved destination explicitly. Exact signatures freeze at gate A; no new
operator tokenizer, reset or migration option is introduced.

Application startup registers ready/deferred/unavailable Memory capabilities.
For an unavailable namespace it reports one actionable diagnostic naming the
reason/path and the remedy (configure a new absent destination, or restore the
correct matching configuration). It still accepts read-only file commands.
Memory-dependent chat turns, recall, writes, compaction, consolidation and
maintenance return an explicit readiness failure; no data-less answer, silent
skip or automatic stateless mode is presented as memory-enabled success.
Background and exit maintenance obey the same gate. Help, file reads and exit
remain usable; an exit-maintenance refusal is reported without preventing exit.

The operation matrix is mandatory in Chat, Runtime and direct factory tests:

| Namespace state | `/read` / headless file extraction | Memory-dependent turn, semantic recall or new embedding/write | Store-only snapshot/maintenance/restore |
| --- | --- | --- | --- |
| Unset destination, fallback path absent | Available | Readiness refusal; configure an explicit path. No CREATE_FRESH, marker, client, model/provider or associated-path creation. | Refuse unavailable store; no discovery/import/create. |
| Explicit destination absent and resolved graph/configured WAL absent | Available with normal file-format readiness; never creates Memory | Resolve verified capabilities and CREATE_FRESH once; then normal guarded operation. | Does not create merely to snapshot/restore; unavailable until initialized. |
| Explicit vector destination absent but graph or configured WAL exists | Available | Readiness refusal naming the associated path/remedy, before any creation or provider/store I/O. | Refuse; preserve associated content and metadata. |
| Bound ready, matching identity/incarnation | Available without embedding/Chroma startup | Allowed after operation-specific embedding/counter checks and provenance admission | Allowed under store-admission checks; operations that generate embeddings additionally require model readiness; restore requires same namespace/layout. |
| Existing directory without marker, including empty or a lost old marker | Available | Explicit readiness refusal. No legacy use, stamping, migration, automatic alternate destination or provider call | Refuse before live client, backup/restore mutation or maintenance effects. Historical artifacts remain untouched/offline-inspectable. |
| Bound ready but configured space mismatches, even same dimensions | Available | Explicit mismatch refusal; no rebind or new preparation | Refuse live operations/restore; no overwriting sidecar from a snapshot. |
| Marker exists but is pending, malformed or inconsistent | Available | Explicit refusal; no automatic repair | Explicit refusal; preserve current recovery-required reporting where applicable. |

A missing marker belongs solely to the unbound row, whether never created or
lost; no history scan tries to distinguish those cases. Marker-present invalid
states belong to the final row. All refusals preserve old state and never repair.

Availability of `/read` still depends on the admitted file's extraction assets;
it does not require Memory identity, embedding capacity or provider inference.
Fresh ephemeral stores follow FC-09: both the front adapter and lifecycle
collections are isolated in memory under one identity; no PersistentClient or
default persistent root. FULL/VECTOR_ONLY remain explicitly persistent.
Independent transcript settings are preserved and their effects are separately
controlled in the no-persistent-Memory proofs. Unknown-provenance graph vectors fail explicitly injected scorer comparisons
rather than being skipped/recomputed; maintained unscored recall does not compare them; graph/text inspection
on an admitted bound namespace needs no embedding solely for rendering.

Refusal precedes clients, models, graph/WAL loading, lease/lock creation and any
temporary entries under an existing unbound/mismatched root. Read only the
bounded path/binding metadata required to decide admission. Preserve old bytes,
modes and mtime/ctime, including parent directories: create-and-delete probes
under the old path are not allowed. No existing stores are inspected or changed
while this specification is prepared; these are future runtime/test obligations.

### Operator upgrade note

Before upgrading a legacy installation, stop writers and retain a verified backup
using the old release's authorized snapshot tooling or a consistent cold copy
of the full old state/configuration. Keep the compatible old installation for
legacy restoration if needed: the new guarded tooling will refuse snapshot or
restore of an identity-free namespace. This specification does not perform a
backup, scan, reset or legacy restore; it adds no backup engine. A fresh selection
does not replace a backup, and old artifacts are never automatically upgraded.

## F — binding framework compatibility requirements

The normative [compatibility contract](../embedding-compatibility-contract.md)
defines B01–B08, the minimum direct/transitive inventory, FC-01–14 and exact
proposed integration nodes. Its baseline and replacement-model positives,
refusal witnesses and intentional compatibility exceptions are required parts
of DI-18/21/22/27/28/29/31/33. Reconcile every discovered consumer, not only this
initial allowlist. No required route can be labelled compatible solely because
it loads YAML or safely refuses. Full model/dependency/counter feasibility and
exact signature/oracle freeze still belong to Gate A.

Freeze construction in three bounded slices after readiness: shared embedding/
namespace contracts, narrow consumer integration, then document conversion/
chunking and aggregate proof. Exact directives need separate approval. This
organization does not authorize any slice or defer cross-subsystem proof.

## Proposed exact implementation paths

| Path | Allowed purpose |
| --- | --- |
| `packages/friday-core/src/friday_core/ingestion.py` (new), `interfaces/memory.py`, `profiles.py`, focused Core tests | Neutral immutable source/chunk/options/counter, ingestion entry, explicit-origin/open-intent and identity-bearing vector/query contracts. New contracts have no policy/backend imports; profiles retains only its existing lazy adapter imports. Exact signatures freeze at gate A. |
| `packages/friday-tools/src/friday_tools/filesystem/readers/document_ingestion.py` (new) | Shared typed Docling extraction/chunking adapter, neutral provenance, local asset/status/format checks and errors. |
| `packages/friday-tools/pyproject.toml` | New document-ingestion extra with selected Docling release and mandatory `certifi>=2026.10.19`; other requirements unchanged. |
| `packages/friday-tools/README.md` | Public capability, dependency and local-model setup/limits. |
| `packages/friday-tools/tests_tools/test_document_ingestion.py` (new) | Real format/OCR extraction and typed failure/coverage tests. |
| Tools `filesystem/smart_read.py`, focused existing smart_read tests | Existing text storage/cache paths only: inject shared ingestion entry, preserve opt-in/context controls, bind cache identity and separate source-plan from derived summaries. Document routing remains the companion's work. |
| `packages/friday-commands/src/friday_commands/file_inputs.py` (new) | Pure scoped raw-tail tokenizer and ingestion override parsing; no root API export edits. |
| `packages/friday-commands/tests_commands/test_file_inputs.py` (new) | Headless quoting/options/description and malformed-input proofs. |
| `packages/friday-memory/src/friday_memory/ingestion/document_ingestion.py` (new), ingestion `__init__.py`, focused ingestion tests | Shared policy/default resolution, recursive/fixed strategies, injected document strategy and validated chunk/embedding plan handoff. Preserve metadata/protection/storage semantics. |
| Memory `ingestion/tool_ingester.py`, `ingestion/large_file_processor.py`, existing ingestion tests | Explicit callable ingestion and maintained raw/derived smart_read storage; retain opt-in/admission/context summaries. Do not activate absent web/automatic callers or split accepted plans again. |
| Memory new `ingestion/embedding_space.py`, `adapters/vector.py`, `adapters/simple_vector.py`, `controller/memory_controller.py`, `retrieval/collection_manager.py`, focused store/retrieval tests | Durable namespace sidecar or ephemeral identity admission and envelope propagation; correct query role, validate before client/provider I/O, preflight source/derived batch. No storage-engine replacement, migration or generic metadata redesign. |
| Memory `maintenance/synthesizer.py`, `retrieval/graph_scorer.py`, `context/extractor.py`, `maintenance/pipeline.py`, `maintenance/reorganizer.py`, `maintenance/provider_contracts.py`, focused affected tests | Only inventoried embedding-role/capability/envelope propagation and narrow shape/refusal checks, plus FC-06 typed extraction failure aggregation, no vectorless-edge fallback after a guard refusal and stable-ID acknowledgement/retry semantics. No maintenance ordering, prompts, verification, quarantine, recovery or synthesis redesign. Correct graph edge/target document fallback roles as well as synthesizer roles. |
| Memory `context/extraction_filter.py`, `context/consolidator.py`, `lifecycle/promotion.py`; Tools `memory/lifecycle.py`, focused existing extractor/consolidator/promotion/memory-tool tests | Only FC-01 admitted per-owner rejection sink/log-handler lifecycle, FC-06 successful-batch acknowledgement and typed failures, FC-07 truthful counts/public errors. No scheduler, prompt, lifecycle algorithm or generic Tools rewrite. |
| Memory `ingestion/mcp.py`; Chat `src/friday_chat/memory_mcp.py`, focused Memory/Chat MCP tests and `tests/integration/test_mcp_memory_ingestion.py` | Only FC-02 shared unsplit guard/readiness handoff and real Chat publication/observer/receipt failure mapping; no new receipt schema. Preserve exact snapshot text/identity/receipts/ownership and existing opt-in. Trace the existing Chat prepare/verify ingester constructors to guarded CollectionManager storage; no separate MCP counter/protocol; retain pending IDs. No snapshot splitting or new activation. |
| Memory `maintenance/backup.py`, `analyzer.py`, `__main__.py`, focused existing backup/analyzer/module tests | Only FC-03 public create/verify/same-incarnation restore admission, private minimum new-binding receipt/admission and no live-marker overwrite; existing public copy/default behavior unchanged, FU-014 separately unwaived; FC-04 normalized read-only Chroma AND transcript SQLite analysis. Preserve existing disabled CLI mutations, public signatures and old manifest classes; no backup/maintenance engine redesign. |
| Memory `context/assembler.py`, focused assembler/Agent integration tests | Only FC-06 ownership/result consumption for the existing background extraction task, typed read-only per-turn status/wait and task/sink teardown handoff. Existing extract_context signature/return stays; no Core/Agent protocol change, scheduler or retry queue. |
| Tools `src/friday_tools/memory/maintenance.py`, focused existing public-wrapper tests | Only shared store-only preflight and truthful failure/partial-result adaptation for existing injectable maintenance/reset wrappers. Existing confirmed-clear semantics and ordering stay; no new activation/reset engine or actual user reset. |
| Memory `models/graph.py`, `adapters/graph.py`, `adapters/null_graph.py`, focused graph tests | Only reserved embedding-identity properties/envelope propagation and refusal at vector comparison/update. No graph schema redesign, import/migration or backfill. |
| Memory `maintenance/recovery.py`, `recovery_models.py`, `mutation.py`, `pruner.py`, `fact_checker.py`, focused affected recovery/mutation tests | Only identity-aware direct-client admission, version2 binding capture/validation, fingerprint and same-namespace restore refusal; FC-11 _collection_dimension substitution/empty collections and graph-only REEMBED only, retaining the 8192 ceiling. Preserve existing recovery/maintenance orchestration, token/quiescence, ULP, journal and rollback policies. |
| Runtime `src/friday_runtime/di.py`, `config.py`, focused Runtime tests | Same resolved embedding/readiness and Memory factory wiring, FC-09 consistent profile persistence/ephemeral collection isolation, deferred extractor/logging, FC-06 owned-task/sink drain during existing shutdown and explicit-origin propagation; no new tool activation or runtime engine. Runtime tool_loading.py is a required source-unchanged real import-discovery witness. |
| CLI `src/friday_cli/container.py`, `profiles.py`, focused compatibility tests | Delegation/type/readiness compatibility only if needed; preserve re-exports and no executable. No independent legacy-client fallback. |
| `packages/friday-llm/src/friday_llm/model_library.py`, `embeddings.py`, new `embedding_limits.py` if needed, corresponding focused tests | Strict capability fields/resolution, model-based counting/preparation, per-input guards, batch shape/dimension validation and safe failures for all callers. |
| `packages/friday-llm/pyproject.toml`, `packages/friday-memory/pyproject.toml` | FC-12 narrow LLM embedding-limits extra and Memory's existing pinned dependency requesting it. Freeze selected exact counter packages at Gate A; Runtime/CLI/Agent memory inherits support without Docling. No unrelated provider expansion. |
| `packages/friday-chat/src/friday_chat/commands/files.py` | Four-format delegation/admission and result metadata, document-line refusal; retain text behavior. |
| `packages/friday-chat/src/friday_chat/commands/registry.py` | Default file-handler-only raw-tail delegation, document failure/success adaptation and exact help cells. No other handlers/parser policy. |
| Chat `src/friday_chat/config.py`, `runtime.py`, `adapters.py` | Typed ingestion config, shared-capability wiring and effective-option presentation; remove Chat character slicing from ingestion, distinguish query/document embedding calls, preserve existing store paths and metadata helper; FC-06 _extract_turns acknowledgement/requeue and owned-sink close/flush; FC-02 existing guarded-storage delegation only; FC-13 existing metadata result.errors projection only. |
| Memory `maintenance/__init__.py`, root `__init__.py`; Chat `reorganization/contracts.py`, `artifacts.py`, `coordinator.py`, `reorganization/__init__.py`, root `__init__.py`, focused aggregate/recovery tests | Strict new Memory/Chat v2 models and typed public loaders/exports, aggregate write/read/participant equality and same-namespace rollback only. Old v1 classes/bindings and generic AtomicJsonStore remain unchanged; no journal, path-layout fingerprint or maintenance-order redesign. |
| Chat `src/friday_chat/reorganization/mutation.py`, focused provider-construction tests | Pool/non-pool embedding capability injection or explicit preflight refusal only. No reorganization sequencing/provider-role/prompt changes. |
| Chat packaged `src/friday_chat/config_templates/config.example.yaml`, `models-config.example.yaml`, focused config tests | New default/schema examples and capability requirements bound to the verified current profile. Qwen remains illustrative; do not overwrite either dirty repository example YAML. |
| `packages/friday-chat/pyproject.toml` | Default dependency on the new Tools extra only. |
| `packages/friday-chat/README.md` | Supported document behavior and provisioning. |
| `packages/friday-chat/tests_chat/test_document_ingestion.py` (new) | Actual registry and zero-ingestion-on-read-failure assertions. |
| `packages/friday-chat/tests_chat/test_files_replay_shell.py` | Replace fake PDF/DOCX/XLSX placeholder expectations with genuine extraction assertions; add PPTX coverage. Affected cases may be renamed/split/replaced under the migration map; preserve every valid unrelated text/replay/shell requirement, not obsolete case bodies. |
| `tests/integration/test_document_ingestion.py` (new) | Active registry/smart_read text storage and explicitly supplied text/web/tool payloads → shared chunking → guarded embeddings → real Memory/fresh bound Chroma. Capability tests do not claim absent route wiring. Deterministic vectors plus real model-matched counting; source/installed proof helper if needed. |
| `tests/integration/test_embedding_compatibility.py` (new); focused existing Agent, multi-agent, MEMQ, CLI, Runtime and Core public-consumer tests | FC-01–14 named B/N/R proofs, full extraction→store→recall→maintenance/lifecycle and minimal installed profiles, actual delayed background completion, two-kernel logging/ephemeral isolation and real MCP publication outcome witnesses. Indirect consumers may remain source-unchanged; no source edit outside explicit allowlist is inferred from a test. |
| Package-local synthetic `tests_*/fixtures/document-ingestion/` (new) | Genuine text, table and scanned fixtures/provenance; no user documents. |
| Affected package-local tests/fixtures/helpers within the eight implementation owners and Agent consumer above; conditional existing `packages/friday-telemetry/tests_telemetry/`, `packages/friday-transcript/tests/`, `packages/friday-mcp/tests_mcp/`, `packages/friday-finance/tests/`, `packages/friday-speech/tests_speech/`, `packages/friday-sandbox/tests_sandbox/`, `packages/friday-moltbook/tests_moltbook/`; `tests/integration/test_package_cohort_metadata.py`; any justified Optimization witness is new (exact package-local or integration path to bind in the directive) | Test-only rename/move/split/rewrite/replace/justified retirement under the case-level migration map; every valid requirement retains executed coverage. Exact old/new files and nodes freeze in the directive before rewriting. No production-source expansion or unrelated suite overhaul. Transcript and Finance require explicit offline selectors because root testpaths omit their `tests/` folders. Finance defaults to `packages/friday-finance/tests/test_basics.py`; its `test_integration_massive.py` is live and excluded unless service/effect authority is explicit, with no executed-coverage credit from the unrun module. The directive classifies every non-default module as offline/live and binds exact selectors, including root integration witnesses. Optimization has no baseline suite. |
| `docs/architecture/command-execution.md` (new), `docs/architecture/README.md` | Canonical current-candidate command architecture and navigation: Chat input/delegation/outcomes, CLI/Runtime roles, shared package boundaries, effects, deployment/configuration and diagrammed request/admission lifecycles. Planning remains in this packet until current implementation or accepted target exists. |
| `docs/guides/00-quick-start.md`, `01-executive-summary.md`, `02-getting-started.md`, `03-core-concepts.md`, `04-adaptive-memory.md`, `05-tools.md`, `07-multi-agent.md`, `09-cli-reference.md`, `10-configuration.md`, `13-troubleshooting.md`, `memory-management-guidelines.md`, `FRIDAY-FEATURES.md`, affected `README.md`/`14-appendices.md` | Substantive rewrites/restructuring of affected chapters, command/package tables, configuration/install/upgrade examples and cross-references, as required by the architecture and guide plans. Source/installed candidate facts and version provenance control; no unrelated whole-guide rewrite or publication. |
| Affected Core/Commands/LLM/Memory/Runtime/CLI package `README.md` files, alongside named Tools/Chat READMEs | Explain changed public contracts, headless reuse, dependency/profile/readiness requirements and retained roles consistently with the canonical architecture. Exact affected files bind the directive; no unrelated feature documentation rewrite. |
| `uv.lock` | Deliberate Docling graph delta and requested Certifi upgrade to at least2026.10.19, inventoried at gate A. No unrelated package upgrade. |
| This packet's document-ingestion remediation/validation/UAT/status records and embedding-compatibility-contract.md; planning board/dashboard; upgrade-log FU-012/013/014 | Planning, readiness, proof and human handoff for this unit only. |

Core/Memory/LLM additions above are a deliberate planning-scope expansion over
the earlier extraction-only draft. The narrow store-binding, query-envelope and
embedding-role, assembly and recovery identity seams above are explicit
exceptions to its earlier storage/maintenance/recovery exclusions. No storage-engine replacement, maintenance orchestration,
recovery-engine redesign, general model-catalog redesign, arbitrary provider, unrelated configuration,
global format/factory policy or TUI source changes. Existing supported embedding
providers need a compatible bounded guard/counter contract or an explicit readiness
stop, not a new blanket suppression or silently disabled safety check. If integration
cannot fit these paths, stop and reconcile the boundary. No product edits are made
by this document update.

## Required verification after approval

| ID | Required evidence |
| --- | --- |
| DI-01 | Real two-page text PDF: distinctive first/last-page strings and correct page count, no placeholder or diagnostic payload. Validity checked independently of the converter. |
| DI-02 | Real DOCX: paragraph → table → paragraph order, Unicode and distinctive late table/body text preserved. No fake extension-only file as success fixture. |
| DI-03 | Genuine image-only scanned PDF with readable test text: real local OCR yields expected words with network blocked. Separate blank/unreadable image fixture fails empty-text checks. Missing OCR/model assets report readiness failure before ingestion. |
| DI-04 | Corrupt/encrypted documents, converter exception, PARTIAL_SUCCESS, page failure after one good page, unavailable library/model and read failure after path resolution: exact error category and zero memory/embedding calls. Diagnostic strings and image-only serializer output must not count as content. |
| DI-05 | Both quote forms, repeated spaces, Unicode/apostrophes/backslashes, description/omission, malformed quotes and option-like paths. New option reservation, before/after/duplicate/lookalike tokens, literal `--` suffix, description quotes and `/read` override refusal. Legacy text limits remain explicitly characterized with truthful truncation. Other/custom handlers unaffected. |
| DI-06 | All four document formats reject `--lines=1`, malformed and negative variants explicitly without conversion/ingestion; current text/table limit behavior is unchanged. Non-allowlisted binary/legacy/macro-enabled paths fail closed without fallback. |
| DI-07 | Invoke actual `/ingest` on genuine PDF, DOCX, XLSX and PPTX through real Memory/Chroma with deterministic embeddings; cover single/multiple chunks. Inspect stored documents, late source markers, sheet/slide separators, chunk metadata/counts, source/type/protection and absent/explicit descriptions. `/list-ingested` alone is not proof. |
| DI-08 | Headless consumers import shared tokenizer/extractor without Chat/TUI; no Docling dependency in Commands. Default clean Chat install contains the declared converter stack and Certifi>=2026.10.19, verified after all installs; plain Tools without the extra fails lazily/actionably for documents. Both ordinary and `-O` installed real conversions/OCR/storage run. |
| DI-09 | Negative controls: placeholder substitution, ignored conversion failure, metadata-only image output, dropped last PDF page/table/sheet/slide or PPTX notes, reordered DOCX table, concealed missing formula cache, quote-split regression and swallowed missing-model failure produce named call-phase assertion witnesses. Unchanged control, canonical origins and before/finish/after hashes; no setup/import rejection credit. |
| DI-10 | Full affected package/cohort/CLI/Memory regressions, focused Ruff/mypy/new-file formatting, exact metadata/lock/default closure inventory, enforced Certifi floor/negative control, source/wheel/installed data/origins and model manifest. Record baseline debt and exact approved file-help exceptions without waivers. |
| DI-11 | Bound cold/warm startup and representative document elapsed time, progress/cancellation behavior and file/resource-limit refusal. Cancelled extraction cannot trigger later background ingestion. No unsupported hard-timeout or cross-platform claim. |
| DI-12 | Freeze stable code/evidence, then separately authorized fresh GPT-6.1 Sol/GPT-6 Astra/Claude Opus5.5 independent review. No agents before maintainer document review/direction. Human UAT follows verification; acceptance and delivery remain separate. |
| DI-13 | Genuine multi-sheet XLSX with late-sheet/late-row markers, cached formulas, missing/error formula caches, blank cells, zero/false/date/leading-zero text, merged cells and hidden content. Prove table relationships, coverage warnings, no recalculation/network/macro execution, and no silent active-sheet/preview-row limit. Independent fixture validity and saved-cache oracle required. |
| DI-14 | Genuine multi-slide PPTX with late-slide markers, ordered text/bullets/tables, speaker notes, hidden slides/shapes and an image-only case. Prove original numbering, separately labeled notes, honest omitted-content coverage and no media fetching/rendering. Required native text/table/notes failures yield zero ingestion calls. |
| DI-15 | Every positive format has actual offline normal/optimized installed extraction/chunking and stored-chunk proof, plus corrupt/missing-backend/partial/empty and quoted-path tests. Existing text/web extraction and safety contracts remain; intentional chunking/count deltas are exact and reviewed. Do not infer new web-fetch support. |
| DI-16 | All strategies/defaults/independent CLI and YAML overrides on actual file/text routes, explicit supplied web/tool payloads and public ingester capability. Distinguish capability proof from absent maintained routes. Verify precedence and no I/O on usage errors. Text document-default works with no Docling extra or Chat; Commands stays stdlib-only/API54. |
| DI-17 | Real model-matched token counts on Unicode, headings, repeated table headers, long rows/cells, sections/slides and plain web/text blocks. Final inputs stay within requested budget and effective capacity; no lost tail, fabricated text, split Unicode, second chunking pass or hidden character-estimate fallback. |
| DI-18 | Catalog schema/resolver plus pool/non-pool actual guard paths: omitted new YAML fields with qualified artifact-bound readiness pass; missing resolved capabilities or contradictory explicit values refuse at embedding-operation preflight. Unselected profiles/load/read-only paths remain usable, smaller loaded/batch limit wins, identity/counter refuses, boundary inputs and once-only role formatting. Wrong count/dimension/nonfinite or shuffled-invalid indices fail before storage; valid shuffled indices reorder exactly. Call-phase bypass witnesses required. |
| DI-19 | Source-linked active/public-not-wired/absent route inventory with separate proofs. Actual text/smart_read storage and explicitly called ToolOutputIngester share options; the active opt-in MCP snapshot route follows FC-02 unsplit semantics. Absent web/generic automatic wiring is documented, earns no route-test credit and is not newly activated. Retain fetching/opt-in/quarantine/provenance. Strategy/budget/model/preparation drift invalidates ingestion caches; context-only hits cannot satisfy new storage. |
| DI-20 | Fresh disposable stores only; no reset of current state or legacy migration. Qwen4B example never activates/downloads a model. Installed normal/optimized guard and source-to-store proofs use verified counter assets, realistic exact-dimension test vectors, canonical origins and post-install Certifi checks. Real backend readiness evidence is explicitly distinguished from doubles/model-card metadata. |
| DI-21 | Fresh persistent/ephemeral binding; matching close/reopen passes; same-dimension changed artifact/preparation, missing/malformed/pending sidecar, collection attachment from a mismatched namespace and identity-free precomputed vectors refuse before provider/client/write I/O. No store-byte/mtime change on refusal. Exclusive/race/interrupted creation controls; no automatic repair. Matching identity envelope passes. |
| DI-22 | Role spy matrix for every inventoried caller: direct query and maintained unscored recall (zero graph-vector comparisons), separately public-injectable sync/async scorer and document fallback, source/derived storage, synthesis, promotion/decay/reactivation, recall and maintenance pool/non-pool. No asymmetric convention enabled with an unclassified caller; graph edge/node cached-vector identities are checked before similarity, including unknown-provenance refusal without backfill. Whole-batch result is validated before the first persistence write. |
| DI-23 | Public headless Memory factory → Core entry → smart_read text small/large/force_chunked and warm caches, with no Chat import. Disabled→enabled storage, source change, stale/missing identity, policy drift and failures cannot bypass current admission. Stored raw texts equal common plan chunks exactly; derived records use one guarded unsplit input. |
| DI-24 | Synchronous offline tokenizer resolves only the manifest root; no network per split/global-cache lookup/download/custom-code escape. Boundary parity against actual serving behavior includes special tokens/headers and the serving physical ceiling. Unknown parity refuses readiness. |
| DI-25 | Genuine Office structure oracle distinguishes missing formula cache from blank, hidden row/column, large merged ranges, notes versus comments and backend clipping. Non-text audit cannot supply or repair text. Unknown mapping/warning refuses before ingestion; wrong-format and renamed generic ZIP/multi-document input refuse. |
| DI-26 | Event loop remains responsive during conversion/counting; cancellation before worker start, during work and immediately after completion cannot cause ingestion. Admission stays held until worker quiescence, late results discarded and cleanup idempotent. No hard-thread-timeout/OS-sandbox claim. |
| DI-27 | Same-namespace snapshot/verify/restore and automatic rollback preserve binding, data and graph-vector identity. Wrong space with same dimensions, wrong incarnation/layout, identity-free v1 artifact, pending/malformed/missing sidecar and binding tamper refuse before client/live writes. No rebinding. Private bound preflight is distinct from live restore. Existing journal/quiescence/ULP policies remain tested. |
| DI-28 | Every direct client uses exact normalized-destination admission. Pruner/synthesizer/fact-checker cannot fall through to memory_dir/vector or another root after refusal; include a namespace-fallback mutant. Missing admission is not skip/empty success. Maintained Chat aggregate snapshot/rollback and direct participant entries execute; no bare-client bypass survives. |
| DI-29 | Actual Chat/Runtime pool/non-pool startup and read-only extraction: zero Chroma/model/tokenizer initialization or provider/store I/O; inert service/config objects are allowed. Test unset + absent fallback refusal, explicit value equal to default creation eligibility, unbound/empty/mismatched/invalid-marker refusal, absent vector + existing graph, absent vector + configured WAL, and reused Runtime root both with old graph/WAL (refuse) and only unrelated state (eligible). Core direct StoreOpenRequest/ephemeral and CLI delegation inherit exact policy. No stateless/legacy fallback; preserve old metadata, /read and exit. |
| DI-30 | Storage receipts are destination/incarnation/collection-specific: same-space new destination or different collection, lost record IDs/provenance and disabled→enabled storage cannot skip ingestion. Extraction cache reuse is distinct from completed-storage evidence. Unwired Chat smart_read storage remains unwired and explicitly refuses requested storage. |
| DI-31 | Plain CSV/TSV keeps all source spans/late rows and reports missing supplied table structure; structured tables repeat known headers. No inferred/fabricated header. Hosted mutable identity/missing offline BPE refuses operation; qualified pinned deployment passes only after real gate-A proof. Inactive migration/stub earns no integration credit. |
| DI-32 | Actual Chat bound Memory-v2 snapshot → aggregate-v2 writer/read/participant reparse → same-namespace restore/automatic rollback. Accept only bundle1/memory1/transcript1 for offline inspection and bundle2/memory2/transcript1 for active use; reject mixed/unknown versions, binding/incarnation/participant digest tamper and v1 bound restore before live effects. Verify old v1 validators/exports remain strict, Memory v2 fingerprint is distinct from unchanged Chat path fingerprint, and generic AtomicJsonStore needs no bypass. |
| DI-33 | Preserve pre-change catalog/pool and maintained non-pool configuration fixtures with both new fields omitted. Assert unchanged service/profile/default/endpoint selection and existing embedding call interfaces, batch/cache/resilience settings, and successful operations using qualified readiness plus fresh admitted namespaces. Exercise extraction → graph and insight/summary storage → recall, compaction/lifecycle, maintenance synthesis/re-embedding and stored-vector comparisons. Same-space different service names pass; same-dimension different-space bindings to one namespace refuse before incompatible provider/storage effects; independent namespaces may use different spaces. Include overflow and typed error propagation without silent partial-success claims. Missing baseline readiness is a gate-A stop, not a waived compatibility test. Repeat representative cross-subsystem proofs in actual normal/optimized installed lanes. |
| DI-34 | All FC-01–14 and B01–B08 in the normative compatibility annex bind the exact named integration nodes and focused lower-level assertions. Independently audit the whole framework including unnamed consumers; classify every discovered path, actual maintained versus public-unwired/inactive routes, required narrow source purposes, successful B/N and R controls and installed witness. Require exact source-backed exceptions for MCP overflow, profile persistence, identity-safe public backup/restore admission and guarded failures; safe refusal is not operational compatibility. No new unsupported route, implicit embedder, silent acknowledgement/count success or unknown baseline exclusion. |
| DI-35 | Test migration acceptance: baseline case/fixture inventory and traceable retain/restructure/replace/retire/add map; exact old/new nodes and justified oracles/retirements, every valid requirement covered by executed substantive assertions, updated selectors and meaningful public/installed/negative witnesses. Counts/old assertion bodies alone do not prove preservation; no historical evidence rewrite, silent coverage loss or unrelated suite churn. |
| DI-36 | Substantive documentation acceptance: canonical command architecture and necessary guide/README/configuration-section rewrites are complete for the candidate, coherent with source/requirements/package metadata and independently reviewed. Require change-to-document-to-source/example/probe mapping and representative verified commands/config/install examples plus structural/link checks. A documentation checker pass alone cannot satisfy content, architecture or example correctness. |


## G — required test migration and substantive documentation work

### G1 — affected tests are maintained code

Significant package test/fixture rewrites are expected where this refactor changes
owners, interfaces, setup/admission, dependency profiles or approved outputs.
Follow the [test migration plan](../test-migration-plan.md): affected tests may be
renamed, moved, split, rewritten, replaced or retired when obsolete. Preserve
every still-valid behavioral requirement through retained or replacement
coverage; do not require obsolete implementation-specific assertion bodies to
remain AST-identical. Freeze an initial old-to-new case/fixture/oracle map in the
final directive before the first test rewrite. Each retirement needs its exact
reason, governing change and coverage/obsolete-requirement disposition.

This is the narrow reconciliation with the unchanged compatibility contract's
final assertion-body preservation clause, under Chuck's recorded amendment.
Each case-level map entry explicitly incorporated into the final approved
directive is the named fixture/oracle exception for that test change, including
a mapped rename, move, split, replacement or justified retirement with its
retained/replacement obligations. The general permission alone is not an
exception for unidentified cases: unmapped body edits remain prohibited.
Existing public signatures/classes remain retained. Named FC nodes stay unless
an incorporated entry maps an approved equivalent and preserves executed gate
coverage. No amendment to the annex's other requirements is implied.

No blanket permission to rewrite unrelated suites, weaken assertions, skip or
xfail regressions, broadly accept changed snapshots, or alter production safety
to accommodate old fixtures. Counts/AST inventories are audit signals, not
semantic preservation proof. Preserve required DI/FC criteria and named gate
witnesses unless the directive explicitly maps an approved equivalent. Update
selectors/imports when cases move; uncalled/unawaited helpers do not count.
Preserve v1 fixtures for valid offline legacy inspection and add bound/v2
coverage. Accepted historical evidence/receipts are never edited retroactively.

File-format/help/count changes, source plans, guarded-store fixture/admission,
bound snapshots and exact existing MCP reason adaptations need explicit old/new
oracle entries. FU-013/014 and root baseline debt remain failed/unwaived; no
repair or false positive-credit substitution. Fresh affected-package and
aggregate/public/installed proofs are required. Provision model assets before
offline tests; mocked converter positives alone are insufficient.

### G2 — architecture and guides are authored deliverables

Follow the [command architecture plan](../command-architecture-update-plan.md)
and [guide coverage](../guide-update-handoff.md). The directive MUST include
the canonical architecture document and substantive affected-section rewrites
across guides, package READMEs and configuration examples. Explain actual Chat
and CLI/Runtime command execution, shared ownership, dependencies, admission/
cancellation, outcomes/errors and deployment/data consequences. Rebuild
affected command/package tables from the candidate; do not leave alpha3
architecture statements inconsistent with implemented shared commands.
Disambiguate the CLI component registry/`arg`, Chat application registry and
neutral Commands registry by qualified name, owner, callers and compatibility
status; identify the registry actually used by `friday-chat`. Classify CLI's
placeholder `repl.py`, `main.py` and `server/api.py` without inventing a launcher
or working server. The canonical architecture and CLI README must agree.

Documentation acceptance includes source/schema/metadata traceability, reviewed
architecture/request-flow diagrams, technically checked content and representative
verified configuration/command/install examples. Review the changed prose and
sections against source and installed candidate evidence. Lifecycle/link/schema
checks are necessary structural checks and are not the complete acceptance gate.
Use explicit candidate/release provenance; do not claim future or companion
features as installed. No source, test or live-guide implementation occurs
until the exact construction directive is approved.

## Non-goals and historical placeholders

No user-store scan, deletion, quarantine, replacement or re-ingestion is included.
Previously stored placeholders are a plausible impact, not a confirmed inventory.
Any cleanup needs a separate read-only identification report and exact approved
record IDs/backup/disposition. Do not delete records by a substring search.

No general file-family migration, LLM-based semantic chunking, automatic embedding
model replacement, legacy re-embedding/migration, RAG redesign, remote OCR/vision,
VLM enrichment, spreadsheet calculation/editing,
presentation rendering/editing, new URL/web conversion, additional Docling
formats, legacy/macro-enabled Office files, password interface or guarantees
for every document layout. Do not
weaken quarantine, source-protection, maintenance admission or model policy.

## Next decision

Review assessment v0.6, this amended REM, the test migration plan and canonical
architecture/guide plan together. Five rounds are complete; Chuck's recorded
remediate and continue authorizes exactly one fresh full council, round 6 of 6.
Use self-contained pinned inputs, with no memory/history searches. Review the
bounded correction delta first, then the complete current package impact and
governing requirements. Prior verdicts remain historical. Every seat must be
VERIFIED, with no mandatory findings and coverage/overall each at least 9.5.
After round6, stop; if unmet, ask Chuck for guidance. No replacement, seventh
round, budget reset or automatic construction follows.

Chuck's package-impact satisfaction and remaining conditions still precede
construction approval. Gate A must separately qualify exact dependencies, models,
assets, APIs and implementation/test/doc paths. The final directive binds the
accepted impact and test/documentation deliverables before code. Current MAINT
UAT is separate; no new maintained web-to-Memory route, model selection, data
reset/migration, publication or delivery is authorized here.
