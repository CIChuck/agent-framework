# REM-CMD-INGEST-001 — document extraction, shared chunking and embedding limits

Status: **PROPOSED — independent council design review, round1**. Baseline `7ad916f2`.
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
No implementation or remediation is authorized by that review.

**Maintainer scope expansion — 2026-11-10:** include XLSX workbooks and PPTX
presentations alongside PDF and DOCX. Text and web fetching/extraction are existing
capabilities for this plan; preserve their entry points rather than replacing
their source readers. The later shared chunking decision below intentionally
changes their ingestion stage. This assumption is not a new
validation claim about those capabilities. The original filename is retained
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
| `friday-core` | Minimal public typed chunk/source/options and token-counter contracts needed by packages that already depend on Core. No conversion, model execution or ingestion policy. Exact additions freeze at readiness. |
| `friday-tools` | Shared document extraction and Docling chunker adaptation; format/coverage/status checks, local assets and safe errors. Retain structure internally and return neutral chunks/provenance. No Chat/TUI imports or second policy owner. |
| `friday-commands` | Standard-library-only file arguments and validation of the two command overrides. No filesystem, Docling or Memory imports; root API54 remains unchanged. |
| `friday-memory` | Shared ingestion policy/default resolution and chunk-plan validation; inject the document chunker and exact token counter. Reuse persistence, protection and optional-description metadata rules. No Docling/Tools imports or second chunking pass on a validated plan. |
| `friday-llm` | Typed embedding capabilities, model-specific input preparation, accurate token counting, effective-limit checks and returned-vector validation for all callers. No document splitting or storage policy. |
| `friday-chat` | Loads configuration, wires shared capabilities, delegates arguments/extraction/ingestion and renders effective options, statistics and safe errors. No Chat-only chunking algorithm. |

The limited Core contract prevents a new Tools-to-Memory or Memory-to-Tools
dependency. Existing text/web extraction, URL admission, tool opt-in and safety
rules remain, but their ingestion chunking now uses section D. Conversation
turns and structured maintenance records are not automatically split into
document chunks; the section E embedding guard still covers their requests.

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
6. Inventory every active ingestion caller before freezing exact signatures:
   file commands, text/Markdown ingestion, web-result ingestion, automatic tool
   outputs and smart_read's storage paths. Separate extraction/read-only work
   from ingestion. Prove the common policy is injected at each storage handoff;
   an existing standalone class is not evidence that Chat wires it. If an assumed
   web-ingestion route is missing, report the gap rather than silently adding a
   new fetcher or claiming coverage. Freeze exact affected paths and oracle deltas.
7. Resolve the configured embedding profile to its exact served artifact and
   effective input limit, expected vector dimension, input-formatting convention
   and model-matched tokenizer. Provision counting assets explicitly or verify
   the server's counting capability. Unknown/mismatched limits or counters block
   the new ingestion path. Do not download, activate or select Qwen solely because
   this document includes an example. Record performance/compatibility evidence
   separately from model-card specifications.

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
and web extraction/fetching routes remain. Their ingestion chunking participates
in section D without adding URL support to the local-file converter or claiming
that this planning update itself revalidated runtime behavior.

Update only read/ingest help/detail and their changed response fields. Preserve
the remaining catalog, aliases, parser quirks and accepted metadata oracles.
Retain immutable snapshots; supply a separate exact exception comparison.

## D — shared ingestion chunking: document / 512 tokens by default

The maintainer selected these defaults for **all ingestion sources**, not only
PDF/DOCX/XLSX/PPTX. Apply one policy to command ingestion, existing text/Markdown
and web-result ingestion, and the corresponding tool storage handoffs. Retain
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
| `document` | Use document sections, paragraphs, tables, sheets and slides; preserve associated headings/headers/notes provenance. Use Docling's native hybrid chunker behind the Tools adapter. | Refine oversized units and merge suitable small units within the selected final-input token budget. Plain text and existing normalized web content supply paragraph/heading blocks to the same strategy; no new fetch/conversion route. |
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

Memory owns default/override resolution and validates the complete chunk plan.
It receives a typed document-chunker capability and model token counter through
injection. Tools owns Docling adaptation; recursive/fixed strategies are shared
Memory implementations or explicit injected implementations. Core holds only
minimal common contracts. Do not add a Tools/Memory import cycle or leak third-
party document/tokenizer objects across packages. No consumer cuts an accepted
chunk plan again before persistence. Read/summarization-only processing can retain
its existing policy; every storage handoff uses the selected ingestion policy.

The existing `smart_file.chunk_size`/`chunk_overlap` and legacy estimated-token
settings are not aliases for these new token fields. They may remain for scoped
legacy read/summarization operations; never interpret 2,048 characters as 2,048
model tokens or use those settings as a hidden second ingestion default. Freeze
exact intentionally changed chunk/count/help/config oracles without editing old
snapshots broadly. The ingestion response reports effective strategy, budget and
chunk count; persisted chunk metadata records policy/version, embedding profile
identity and source-unit provenance using storage-compatible values.

## E — embedding profiles and enforced limits

Embedding profiles remain in the model catalog (`models-config.yaml` or the
configured equivalent); the main YAML selects named services through the existing
`embedding_pool`. Extend the strict shared LLM schema and resolver rather than
adding ignored keys to YAML. The profile's proposed `embedding_options` gains:

- `max_input_tokens`: strict positive integer declaring supported input capacity.
- `expected_dimensions`: strict positive integer for validating returned vectors.

Retain the endpoint, model identity/revision and existing batch/cache options.
No operator tokenizer setting or arbitrary query/document-instruction setting
is required. Resolve the matching tokenizer/counting mechanism and supported
input convention from the exact model/artifact identity. Record that resolution
in readiness/provenance; do not silently guess from an arbitrary server alias.
Counting must be exact and available offline through provisioned assets or via
an explicitly verified serving capability; missing support fails preflight.

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

Overflow is a fixed enforcement rule, not another user-configurable policy:

1. Resolve the effective limit as the minimum of the configured supported cap
   and verified artifact/server loaded capacity. A larger declared cap cannot
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
   Ingestion validates its full embedding result before handing it to storage;
   this does not introduce rollback for unrelated multi-write storage failures.

The same configured profile identity binds indexing and retrieval in a store.
A store/model mismatch must fail explicitly. Tool/ingestion caches also bind the
resolved strategy/budget, embedding identity, counting/formatting revision and
conversion profile; stale cache entries cannot bypass these checks. Leave old
entries untouched rather than purging them.

**Test-store decision:** the maintainer will start fresh for model testing; no
legacy migration or bulk re-embedding implementation is required. Use disposable
empty stores in automated proof. Do not scan, delete or reset current stores as a
side effect of planning, startup, a profile edit or an ingestion command. Any
later requested reset must identify the actual test-state scope; no such reset
has been performed here.

[Docling chunking](https://docling-project.github.io/docling/concepts/chunking/),
[model-bound tokenization](https://lmstudio.ai/docs/python/tokenization) and
[loaded/model capacity metadata](https://lmstudio.ai/docs/developer/rest/list)
are upstream design references, not candidate-installed or backend readiness proof.

## Proposed exact implementation paths

| Path | Allowed purpose |
| --- | --- |
| `packages/friday-core/src/friday_core/ingestion.py` (new), focused Core tests | Minimal neutral immutable source/chunk/options and counting protocols, if required to avoid cross-package cycles. No policy/backend imports; exact public signatures freeze at gate A. |
| `packages/friday-tools/src/friday_tools/filesystem/readers/document_ingestion.py` (new) | Shared typed Docling extraction/chunking adapter, neutral provenance, local asset/status/format checks and errors. |
| `packages/friday-tools/pyproject.toml` | New document-ingestion extra with selected Docling release and mandatory `certifi>=2026.10.19`; other requirements unchanged. |
| `packages/friday-tools/README.md` | Public capability, dependency and local-model setup/limits. |
| `packages/friday-tools/tests_tools/test_document_ingestion.py` (new) | Real format/OCR extraction and typed failure/coverage tests. |
| `packages/friday-commands/src/friday_commands/file_inputs.py` (new) | Pure scoped raw-tail tokenizer and ingestion override parsing; no root API export edits. |
| `packages/friday-commands/tests_commands/test_file_inputs.py` (new) | Headless quoting/options/description and malformed-input proofs. |
| `packages/friday-memory/src/friday_memory/ingestion/document_ingestion.py` (new), ingestion `__init__.py`, focused ingestion tests | Shared policy/default resolution, recursive/fixed strategies, injected document strategy and validated chunk/embedding plan handoff. Preserve metadata/protection/storage semantics. |
| Memory `ingestion/tool_ingester.py`, `ingestion/large_file_processor.py`, existing ingestion tests | Inject the common policy into actual text/web/tool storage paths identified at gate A; retain opt-in, admission, context-only summaries and non-ingestion behavior. No duplicate splitter on accepted chunks. |
| `packages/friday-llm/src/friday_llm/model_library.py`, `embeddings.py`, new `embedding_limits.py` if needed, corresponding focused tests | Strict capability fields/resolution, model-based counting/preparation, per-input guards, batch shape/dimension validation and safe failures for all callers. |
| `packages/friday-llm/pyproject.toml` | Only selected counter/provider dependencies if needed; freeze exact optional/default placement at gate A. No unrelated provider expansion. |
| `packages/friday-chat/src/friday_chat/commands/files.py` | Four-format delegation/admission and result metadata, document-line refusal; retain text behavior. |
| `packages/friday-chat/src/friday_chat/commands/registry.py` | Default file-handler-only raw-tail delegation, document failure/success adaptation and exact help cells. No other handlers/parser policy. |
| Chat `src/friday_chat/config.py`, `runtime.py`, `adapters.py` | Typed ingestion config, shared-capability wiring and effective-option presentation; remove Chat character slicing from ingestion, distinguish query/document embedding calls, preserve existing store paths and metadata helper. |
| Chat packaged `src/friday_chat/config_templates/config.example.yaml`, `models-config.example.yaml`, focused config tests | New default/schema examples and capability requirements bound to the verified current profile. Qwen remains illustrative; do not overwrite either dirty repository example YAML. |
| `packages/friday-chat/pyproject.toml` | Default dependency on the new Tools extra only. |
| `packages/friday-chat/README.md` | Supported document behavior and provisioning. |
| `packages/friday-chat/tests_chat/test_document_ingestion.py` (new) | Actual registry and zero-ingestion-on-read-failure assertions. |
| `packages/friday-chat/tests_chat/test_files_replay_shell.py` | Replace fake PDF/DOCX/XLSX placeholder expectations with genuine extraction assertions; add PPTX coverage; keep test names and unrelated text/replay/shell assertions. |
| `tests/integration/test_document_ingestion.py` (new) | Registry/tools/text/web → shared chunking → guarded embeddings → real Memory/disposable Chroma, deterministic vectors plus real model-matched counting; source/installed proof helper if needed. |
| Package-local synthetic `tests_*/fixtures/document-ingestion/` (new) | Genuine text, table and scanned fixtures/provenance; no user documents. |
| `uv.lock` | Deliberate Docling graph delta and requested Certifi upgrade to at least2026.10.19, inventoried at gate A. No unrelated package upgrade. |
| This packet's document-ingestion remediation/validation/UAT/status records; planning board/dashboard; upgrade-log FU-012 | Planning, readiness, proof and human handoff for this unit only. |

Core/Memory/LLM additions above are a deliberate planning-scope expansion over
the earlier extraction-only draft. No Memory storage-engine, maintenance pipeline,
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
| DI-05 | Both quoted path forms, two consecutive spaces, Unicode/apostrophes/backslashes, optional description, omitted description, malformed/empty quotes and literal option-like filenames. Unquoted behavior/leading text flags retained; other/custom handlers unaffected. |
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
| DI-16 | All three strategies execute under defaults and independent CLI/YAML overrides across document/text/web/tool ingestion. Verify exact precedence, missing/invalid/duplicate values and no I/O on usage errors. Headless Memory/Core consumer needs no Chat; Commands remains stdlib-only/API54 unchanged. |
| DI-17 | Real model-matched token counts on Unicode, headings, repeated table headers, long rows/cells, sections/slides and plain web/text blocks. Final inputs stay within requested budget and effective capacity; no lost tail, fabricated text, split Unicode, second chunking pass or hidden character-estimate fallback. |
| DI-18 | Profile schema/resolver and real guard paths: smaller loaded limit wins, unknown identity/counter refuses, below/at/over boundary inputs behave correctly, formatting applies once, one input yields one vector. Wrong count/dimension/non-finite output fails before ingestion storage. Control and named bypass mutants require call-phase assertion witnesses. |
| DI-19 | Exact active-caller inventory proves text/web/automatic-tool/smart_read storage wiring and common options; fetching, tool opt-in, quarantine and provenance retained. Config/strategy/budget/model/profile changes invalidate ingestion caches; stale cached results cannot bypass guards. Read-only tools remain read-only. |
| DI-20 | Fresh disposable stores only; no reset of current state or legacy migration. Qwen4B example never activates/downloads a model. Installed normal/optimized guard and source-to-store proofs use verified counter assets, realistic exact-dimension test vectors, canonical origins and post-install Certifi checks. Real backend readiness evidence is explicitly distinguished from doubles/model-card metadata. |

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
separate pending human activity. The currently authorized round1 council reviews
this full proposal; reconcile its three terminal reports before any further action.
