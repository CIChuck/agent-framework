# REM-CMD-INGEST-001 — document extraction, shared chunking and embedding limits

Status: **PROPOSED — correction cycle1, independent design council round2**. Baseline `7ad916f2`.
This document defines a bounded repair and its dependency-readiness gate. It is
not an approved construction directive or a completed compatibility assessment.
Working branch: `feature/cmd-ingest-001`, based on published command-refactor head
`df62b77d551491cfb33ad2492c711036b09c9d4c` ([PR #15](https://github.com/CIChuck/agent-framework/pull/15)).
[Branch handoff](../validation/document-ingestion/branch-handoff.md) records scope
and construction boundaries. The assessment baseline above remains historical.
The parent is now merged into `master` at `c36e7ee5`; this scoped branch
incorporates that merge. Future INGEST-only review targets `master`.

No product edits, installs, model downloads or council invocation are authorized
by placement in this packet. The requested planning work is authorized.
The maintainer separately authorizes the fresh read-only Sol/Astra/Opus5.5
round1 design council on2026-11-10; [recorded roster](../validation/document-ingestion/council-round1/roster.json).
That review authorized no implementation or remediation. On2026-11-10 the
maintainer separately directs document corrections and up to three additional
fresh Sol/Astra/Opus councils (rounds2–4), stopping when every seat independently
returns VERIFIED with at least9.5/10 and no mandatory finding. This is bounded
document-readiness work, not gate-A execution, installation or construction.

**Maintainer scope expansion — 2026-11-10:** include XLSX workbooks and PPTX
presentations alongside PDF and DOCX. Existing text and web **reading** capabilities
are retained. Source inspection found no maintained web-to-Memory ingestion
route and no maintained automatic `ToolOutputIngester` caller. The route inventory
below supersedes the earlier assumption that those ingestion routes existed.
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
| Headless smart_read text small/large/force_chunked storage and caches | Public tool, direct small-file storage, raw/derived large-file records and early cache returns | INGEST owns existing storage/cache integration, before document routing adoption. Stored source chunks come from the shared plan. |
| Public ToolOutputIngester capability | Class exists; maintained Chat/Agent/Tools/Runtime caller absent; legacy integration caller exists | Adapt its explicitly called storage boundary and prove headlessly; do not activate automatic ingestion. |
| Web reader/fetch tools | Maintained reads, no Memory handoff | Retain reads. Supplied extracted web text exercises the shared entry as a capability proof, not proof of a fetch-to-store route. |
| Tools factory and smart_read document routing | Legacy readers/binary skips | TOOLS-DOC companion adopts the four formats after shared interfaces freeze. |

INGEST completion covers active storage paths and explicit public ingestion
capabilities, not absent web/automatic wiring or Tools four-format adoption.
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
   smart_read small/large/cache, explicit ToolOutputIngester capability, retrieval,
   lifecycle/promotion and maintenance. Classify active/public-not-wired/absent
   routes using the table above; absent routes earn no integration credit.
   Prove headless injection at existing storage handoffs. Inventory roles, legacy
   constructors, precomputed vectors and caches; asymmetric preparation cannot
   be enabled while a relevant caller is unclassified. Freeze exact paths,
   narrow affected MAINT regressions and approved oracle deltas.
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
fetch. Preserve all other description/parser semantics. No launch-time global
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
slides merely to fill a budget. Large tables retain row/header context across
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

These keys are optional for parsing an existing catalog, but **both verified
capabilities are required for any embedding operation in this guarded stack**.
An unselected old profile does not break application/config loading. A selected
profile missing either value yields an actionable readiness error when its
embedding service is used, before provider I/O; no silent unguarded mode.
Packaged selected-profile examples receive measured values only after gate A.
User-edited YAML is never overwritten. Legacy non-catalog Chat and maintenance
constructors must accept the same resolved capability from an explicit,
artifact-bound built-in readiness record or refuse at operation preflight. They
must not infer dimensions/capacity from an arbitrary alias or bypass the guard.
Read-only `/read` needs no embedding capability and remains available.

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

Memory owns a versioned canonical embedding-space identity: actual model/artifact
revision or digest, output dimension/normalization, query/document preparation
revision, tokenizer/special-token convention and distance metric. Freeze exact
canonical encoding/hash vectors at gate A. A mutable profile alias, endpoint URL
or matching vector dimension is not identity; credentials never enter it.

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
This admission covers cached/precomputed graph edge and node vectors too:
attach the embedding-space identity in reserved properties on creation/update
and verify it before similarity scoring. Unknown existing vector provenance
refuses use; do not silently recompute/backfill legacy graph vectors. Missing
vectors may use the existing on-demand document-role computation. Graph text
operations do not acquire a new embedding requirement merely to render.
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

**Test-store decision:** use fresh bound stores for the new pipeline, including
preparation changes to the current model, not only model replacement tests; no
legacy migration or bulk re-embedding implementation is required. Use disposable
empty stores in automated proof. Do not scan, delete or reset current stores as a
side effect of planning, startup, a profile edit or an ingestion command. Any
later requested reset must identify the actual test-state scope; no such reset
has been performed here.

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

## Proposed exact implementation paths

| Path | Allowed purpose |
| --- | --- |
| `packages/friday-core/src/friday_core/ingestion.py` (new), `interfaces/memory.py`, focused Core tests | Neutral immutable source/chunk/options/counter, injected ingestion entry and identity-bearing vector/query contracts. No policy/backend imports; exact signatures freeze at gate A. |
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
| Memory `maintenance/synthesizer.py`, `retrieval/graph_scorer.py`, `context/extractor.py`, `maintenance/pipeline.py`, `maintenance/reorganizer.py`, `maintenance/provider_contracts.py`, focused affected tests | Only inventoried embedding-role/capability/envelope propagation and narrow shape/refusal checks. No maintenance ordering, prompts, verification, quarantine, recovery or synthesis redesign. Correct graph edge/target document fallback roles as well as synthesizer roles. |
| Memory `models/graph.py`, `adapters/graph.py`, `adapters/null_graph.py`, focused graph tests | Only reserved embedding-identity properties/envelope propagation and refusal at vector comparison/update. No graph schema redesign, import/migration or backfill. |
| `packages/friday-llm/src/friday_llm/model_library.py`, `embeddings.py`, new `embedding_limits.py` if needed, corresponding focused tests | Strict capability fields/resolution, model-based counting/preparation, per-input guards, batch shape/dimension validation and safe failures for all callers. |
| `packages/friday-llm/pyproject.toml` | Only selected counter/provider dependencies if needed; freeze exact optional/default placement at gate A. No unrelated provider expansion. |
| `packages/friday-chat/src/friday_chat/commands/files.py` | Four-format delegation/admission and result metadata, document-line refusal; retain text behavior. |
| `packages/friday-chat/src/friday_chat/commands/registry.py` | Default file-handler-only raw-tail delegation, document failure/success adaptation and exact help cells. No other handlers/parser policy. |
| Chat `src/friday_chat/config.py`, `runtime.py`, `adapters.py` | Typed ingestion config, shared-capability wiring and effective-option presentation; remove Chat character slicing from ingestion, distinguish query/document embedding calls, preserve existing store paths and metadata helper. |
| Chat `src/friday_chat/reorganization/mutation.py`, focused provider-construction tests | Pool/non-pool embedding capability injection or explicit preflight refusal only. No reorganization sequencing/provider-role/prompt changes. |
| Chat packaged `src/friday_chat/config_templates/config.example.yaml`, `models-config.example.yaml`, focused config tests | New default/schema examples and capability requirements bound to the verified current profile. Qwen remains illustrative; do not overwrite either dirty repository example YAML. |
| `packages/friday-chat/pyproject.toml` | Default dependency on the new Tools extra only. |
| `packages/friday-chat/README.md` | Supported document behavior and provisioning. |
| `packages/friday-chat/tests_chat/test_document_ingestion.py` (new) | Actual registry and zero-ingestion-on-read-failure assertions. |
| `packages/friday-chat/tests_chat/test_files_replay_shell.py` | Replace fake PDF/DOCX/XLSX placeholder expectations with genuine extraction assertions; add PPTX coverage; keep test names and unrelated text/replay/shell assertions. |
| `tests/integration/test_document_ingestion.py` (new) | Active registry/smart_read text storage and explicitly supplied text/web/tool payloads → shared chunking → guarded embeddings → real Memory/fresh bound Chroma. Capability tests do not claim absent route wiring. Deterministic vectors plus real model-matched counting; source/installed proof helper if needed. |
| Package-local synthetic `tests_*/fixtures/document-ingestion/` (new) | Genuine text, table and scanned fixtures/provenance; no user documents. |
| `uv.lock` | Deliberate Docling graph delta and requested Certifi upgrade to at least2026.10.19, inventoried at gate A. No unrelated package upgrade. |
| This packet's document-ingestion remediation/validation/UAT/status records; planning board/dashboard; upgrade-log FU-012 | Planning, readiness, proof and human handoff for this unit only. |

Core/Memory/LLM additions above are a deliberate planning-scope expansion over
the earlier extraction-only draft. The narrow store-binding, query-envelope and
embedding-role seams above are explicit exceptions to its earlier storage/
maintenance exclusions. No storage-engine replacement, maintenance orchestration,
recovery, general model-catalog redesign, arbitrary provider, unrelated configuration,
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
| DI-18 | Catalog schema/resolver plus pool/non-pool actual guard paths: absent fields refuse at embedding-operation preflight, unselected profiles/load/read-only paths remain usable, smaller loaded/batch limit wins, identity/counter refuses, boundary inputs and once-only role formatting. Wrong count/dimension/nonfinite or shuffled-invalid indices fail before storage; valid shuffled indices reorder exactly. Call-phase bypass witnesses required. |
| DI-19 | Source-linked active/public-not-wired/absent route inventory with separate proofs. Actual text/smart_read storage and explicitly called ToolOutputIngester share options; absent web/automatic wiring is documented, earns no route-test credit and is not newly activated. Retain fetching/opt-in/quarantine/provenance. Strategy/budget/model/preparation drift invalidates ingestion caches; context-only hits cannot satisfy new storage. |
| DI-20 | Fresh disposable stores only; no reset of current state or legacy migration. Qwen4B example never activates/downloads a model. Installed normal/optimized guard and source-to-store proofs use verified counter assets, realistic exact-dimension test vectors, canonical origins and post-install Certifi checks. Real backend readiness evidence is explicitly distinguished from doubles/model-card metadata. |
| DI-21 | Fresh persistent/ephemeral binding; matching close/reopen passes; same-dimension changed artifact/preparation, missing/malformed/pending sidecar, collection attachment from a mismatched namespace and identity-free precomputed vectors refuse before provider/client/write I/O. No store-byte/mtime change on refusal. Exclusive/race/interrupted creation controls; no automatic repair. Matching identity envelope passes. |
| DI-22 | Role spy matrix for every inventoried caller: direct query, graph fallback, source/derived storage, synthesis, promotion/decay/reactivation, recall and maintenance pool/non-pool. No asymmetric convention enabled with an unclassified caller; graph edge/node cached-vector identities are checked before similarity, including unknown-provenance refusal without backfill. Whole-batch result is validated before the first persistence write. |
| DI-23 | Public headless Memory factory → Core entry → smart_read text small/large/force_chunked and warm caches, with no Chat import. Disabled→enabled storage, source change, stale/missing identity, policy drift and failures cannot bypass current admission. Stored raw texts equal common plan chunks exactly; derived records use one guarded unsplit input. |
| DI-24 | Synchronous offline tokenizer resolves only the manifest root; no network per split/global-cache lookup/download/custom-code escape. Boundary parity against actual serving behavior includes special tokens/headers and the serving physical ceiling. Unknown parity refuses readiness. |
| DI-25 | Genuine Office structure oracle distinguishes missing formula cache from blank, hidden row/column, large merged ranges, notes versus comments and backend clipping. Non-text audit cannot supply or repair text. Unknown mapping/warning refuses before ingestion; wrong-format and renamed generic ZIP/multi-document input refuse. |
| DI-26 | Event loop remains responsive during conversion/counting; cancellation before worker start, during work and immediately after completion cannot cause ingestion. Admission stays held until worker quiescence, late results discarded and cleanup idempotent. No hard-thread-timeout/OS-sandbox claim. |

Keep the old assertion bodies except the precisely documented file-format/help
exceptions; add coverage rather than broadly rewriting accepted tests. Provision
and cache model artifacts explicitly before offline tests. A mocked converter is
not sufficient positive proof. Do not add blanket source suppressions or skips.

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

Review this expanded four-format Docling boundary, proposed format defaults and
shared all-source chunking/embedding-limit contract, together with the Tools
adoption plan. The maintainer has settled document/512 defaults, all three
strategies, all-source scope, illustrative-only Qwen and fresh-store testing.
Gate A must establish the exact compatible package/model/counter manifest and final
construction directive before implementation. Current MAINT UAT remains a
separate pending human activity. The maintainer authorizes this document-only
correction and up to three further full fresh councils (rounds2–4). Each reviews
the correction delta first, then the full proposed design/companion. Stop early
only with every seat VERIFIED, no mandatory findings and scores at least9.5;
otherwise return remaining issues when that budget is exhausted. No automatic
gate-A execution, construction, acceptance or delivery follows the score gate.
