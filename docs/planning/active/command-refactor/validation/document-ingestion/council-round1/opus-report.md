# REM-CMD-INGEST-001 + TOOLS-DOC-001 — Round 1 design-readiness review (seat OPUS)

## 1. Outcome

**CHANGES_REQUESTED** — advisory score **7.3 / 10**.

The proposal is unusually disciplined about authority, fail-closed extraction,
no-silent-truncation and claim boundaries. It is close to ready for gate A.
However, one **High** data-safety gap and seven **Medium** design gaps are
source-evident now. They are not implementation-test demands; each is a
contradiction, an unassigned owner, or a promised behavior with no feasible or
authorized mechanism in the current text. Each mitigation is a bounded document
edit to the REM and/or companion before gate A. None requires code, installs or
construction approval.

## 2. Candidate and diff identity

| Item | Value |
| --- | --- |
| Initiative / unit / companion | friday-command-refactor / REM-CMD-INGEST-001 / TOOLS-DOC-001 |
| Branch | `feature/cmd-ingest-001` (verified by helper) |
| Base → candidate | `c36e7ee51a9328918b9bb97712aa7f1d4a850d19..8be50b1218fc4db67fbd5d546fea9d7be6a2fd64` |
| Logical index SHA-256 | `f12f3152b2900cf9df29eff6fd1b8fec32d9bccbb5672a4fe6537c3116b571bf` (start = end) |
| Review mode | Fresh FULL bounded proposal/document/design readiness incl. source feasibility; not implementation conformance |
| Frozen request | `…/friday-ingest-council-r1-inputs-qj57z4f_/review-request.json`, SHA-256 `edcdfc3b…0582eb`, verified **before** substantive reading and again at end |
| Integrity helper | SHA-256 `6e1ec704…8c278c3` (matches pin); read-only code inspected before execution |
| Protected manifest / preserved state | `647f359a…05f6b` (17,536 entries) / `43bc6314…2ce8`, both matched by helper at start and end |

## 3. Authority manifest and precedence

All 11 authority pins, 12 document pins and 31 source pins matched (helper
`failures: []` at start and end). Read in full: `AGENTS.md`;
`.agents/skills/council/SKILL.md`; `.agents/skills/independent-code-validator/SKILL.md`;
`scope-decisions.md`; `discussion-decisions.json`; `format-expansion.json`;
`certifi-security-requirement.json`; `council-round1/roster.json`; the full REM
(647 lines); the full companion (142 lines); `assessment.md`; `branch-handoff.md`;
`planning-checks.json`; the head of `tactical-plan.md`/`next-phase.md` (lines 1–236
are identical); the board entry for `friday-command-refactor`. From
`authority.json` I extracted only `branch`, `current_scope`,
`product_code_authority`, `active_council_roster` and
`document_ingestion_remediation`. No unrelated review archive was read.
Policies were consulted where the request and skills reference them.

Precedence applied: (1) the explicit maintainer roster and discussion decisions,
(2) repository policies, (3) the current REM and companion within scope,
(4) historical assessment and receipts, treated as observations only.

## 4. Independence and context provenance

- Reviewer: seat OPUS, Anthropic `claude-opus-5-5`, high effort; fresh context created about 2026-11-10T21:05Z.
- I had no parent transcript, builder reasoning or peer verdict. I used no nested agents, delegation or `web-fetch` agent; public pages were fetched with `curl` into my own scratch.
- The shared checkout was used read-only under the authorized exception. It is not a detached or clean checkout: two dirty example YAMLs and `.friday-old/` are protected and were never touched.
- Roster: two OpenAI seats and one Anthropic seat. This deviates from the council skill's three-provider default, but it is recorded as an explicit maintainer exception in `roster.json` (`roster_exception`). That is truthful and acceptable. Cross-seat provider diversity is reduced, which is advisory only.

## 5. Findings (ordered by severity)

### INGEST-R1-OPUS-001 — High — current-profile embedding convention and store binding create an undeclared migration of existing stores

- **Violated requirement:** IR-10 and IR-15 (no hidden migration/reset; storage safety). This also conflicts with the REM's own "no legacy re-embedding/migration" and "store/model mismatch must fail explicitly" (REM §E lines 538–549).
- **Evidence (source and official sources):**
  - `friday_llm/embeddings.py:249-324` sends raw text for both `embed_documents` and `embed_query`. No task prefix is applied today.
  - The configured default profile is `nomic_embedding_local` → `openai/nomic-embed-text-v1.5` (`config_templates/models-config.example.yaml:88-96`). The REM keeps it selected (lines 499–501), and gate A item 7 verifies its "input-formatting convention".
  - The official Nomic v1.5 card (fetched at 21:09Z) says: "the text prompt *must* include a *task instruction prefix*" (`search_document:` / `search_query:`). The REM's rule "Apply a verified convention once inside the shared LLM adapter" (lines 503–510) therefore changes **every current Nomic query and document vector**.
  - Existing user stores were indexed without prefixes. The fresh-store decision is scoped to "model testing" (lines 544–549, `discussion-decisions.json`); it does not cover the user's continuing current-model store.
  - Collections record no embedding identity: `adapters/vector.py:89-92` creates them with only `{"hnsw":{"space":"cosine"}}`. The promised store/model binding has no existing mechanism. The files that would have to change (`adapters/vector.py`, `retrieval/collection_manager.py`) are outside the REM allowlist (lines 556–582), and line 586 excludes "Memory storage-engine" changes.
  - `/reorganize --force-reembed` (registry `_REORGANIZE_FULL_ONLY_FLAGS`) and reorganizer `embed_documents` (`maintenance/reorganizer.py:775`) would re-embed subsets with the new convention, producing mixed-convention collections.
- **Counterexample:** The user keeps the Nomic profile and an existing `.friday` store. After the change, queries are embedded as `search_query: …` against unprefixed documents. New `/ingest` chunks are stored as `search_document: …` beside unprefixed legacy chunks. Retrieval quality changes silently. Either nothing fails (contradicting "mismatch must fail explicitly") or legacy stores without identity metadata start failing at startup (an unannounced breaking change). The REM chooses neither.
- **Narrow mitigation (document):** State the legacy-store rule explicitly. Recommended rule:
  - (a) The new convention and identity binding apply only to stores created under a recorded identity, that is, fresh stores.
  - (b) A store without identity metadata is classified "legacy-unbound". Choose explicitly between refusing new ingestion into it, or keeping the legacy raw-text convention for that store, never mixing conventions.
  - (c) Name where identity is recorded (collection metadata at creation, or a sidecar) and add those exact Memory paths to the allowlist. Otherwise drop the binding promise.
  - (d) Gate A records whether the current Nomic deployment's convention is enforced or deferred.
- **Test/doc impact:** Add a DI row for a legacy-unbound store (no mixing, the declared outcome) and an identity-mismatch refusal on a fresh store. Update REM §E, the test-store decision and the allowlist.

### INGEST-R1-OPUS-002 — Medium — embedding caller inventory is limited to ingestion; known query/document misroutes sit outside the allowlist

- **Violated requirement:** IR-10 (query/document preparation), IR-08 (shared ownership) and IR-16 (gate-A completeness).
- **Evidence:**
  - Gate A item 6 inventories only *ingestion* callers. REM §E (lines 508–510) asks to "audit `embed_text` versus `embed_query`/`embed_documents`" for all callers, but the allowlist covers only Chat adapters plus LLM.
  - `ChromaVectorStore.query()` embeds query text via `_get_embeddings` → `embed_documents` whenever `query_embedding` is None (`adapters/vector.py:99-109, 222-224`).
  - `MaintenanceSynthesizer._get_embedding` embeds stored memory content through `embed_query` (`maintenance/synthesizer.py:712-714, 767`).
  - Chat `FrameworkEmbeddingService.embed_text` → `embed_query` (`adapters.py:263-264`).
  - Collection-manager promotion, decay and reactivation re-embed via `embed_documents` (`retrieval/collection_manager.py:559, 617, 667`).
  - Once `embed_query` and `embed_documents` diverge, each of these becomes a convention bug. Fixing them touches Memory retrieval and maintenance files that the REM excludes. MAINT-001 is frozen at a verified candidate.
- **Counterexample:** With an asymmetric profile, synthesizer clustering embeds documents as queries, and any `query()` call without a precomputed vector embeds the query as a document.
- **Mitigation:** Extend gate A item 6 to an **all embedding call-site inventory** (Chat, Memory retrieval/lifecycle/maintenance, Tools). For each misroute, either add its exact path to the allowlist with a MAINT-impact statement, or keep symmetric (no-instruction) formatting until a separately approved unit. Add the stop condition: "an asymmetric convention may not be enabled while any caller is unclassified."
- **Test impact:** Add a DI row asserting that each inventoried caller uses the correct role (call-phase witnesses).

### INGEST-R1-OPUS-003 — Medium — behavior when the new profile fields are absent, and on legacy non-pool embedding paths, is undefined

- **Violated requirement:** IR-09, IR-10 and IR-11 (effective capacity for *all* callers; offline/unknown behavior).
- **Evidence:**
  - `EmbeddingOptions` is a strict model with optional `embedding_options` (`model_library.py:105-120, 312`).
  - The REM requires "every embedding caller" to recheck limits and says "Unknown counting/formatting behavior is not permission to send unbounded input" (lines 523–531). It never states whether `max_input_tokens`/`expected_dimensions` become **required**, which would break every existing `models-config.yaml` including the user's dirty example, or **optional**, in which case it is undefined what retrieval, maintenance and tool callers do without them.
  - Two non-catalog paths construct services with no profile at all: Chat `build_framework_embedding_service` legacy branch (`adapters.py:1748-1760`, default `text-embedding-3-small`) and maintenance `reorganization/mutation.py:284-294`. Neither is in the allowlist.
- **Counterexample:** An existing config without the new fields either (a) fails all embeddings, so Chat retrieval and MAINT break, contradicting "preserve existing behavior" and MAINT's frozen state; or (b) bypasses the guard, contradicting "for all callers".
- **Mitigation:** Decide and record:
  - required versus optional fields;
  - the exact refusal scope (e.g., new ingestion path refuses; queries/maintenance keep current behavior with a logged "unguarded-legacy" state, or also refuse);
  - treatment of the legacy `config.embedding` and maintenance non-pool paths (allowlist them or declare them out of scope with an explicit residual risk).
- **Test impact:** DI-18 gains absent-field and legacy-path rows.

### INGEST-R1-OPUS-004 — Medium — the `document` default for *all* sources is owned by a Docling chunker; non-Docling sources and headless consumers have no defined owner or path

- **Violated requirement:** IR-07 (all-source document/512 semantics), IR-08 (typed boundaries; no forced dependency) and IR-13.
- **Evidence:**
  - REM §D table (line 409): `document` = "Docling's native hybrid chunker behind the Tools adapter". It then says plain text and web content "supply paragraph/heading blocks to the same strategy" without naming who derives those blocks for `.txt/.md/.json/.yaml/.py/.csv/.tsv` (Chat `SUPPORTED_EXTENSIONS`, `files.py:11-23`) or web text.
  - Docling `HybridChunker` operates on a `DoclingDocument`.
  - The companion says bare Tools "can retain text operations" without the extra (companion lines 96–99), and DI-16 requires a "Headless Memory/Core consumer needs no Chat".
  - With `document` as the default for every source, text ingestion in any environment without the Docling extra has no defined behavior: silent fallback to `recursive` would be a hidden second default (forbidden at line 434), and refusal would break text ingestion.
- **Counterexample:** A headless Memory consumer, or Tools installed without `[document-ingestion]`, ingests a `.md` file with defaults. No component is assigned to produce document-strategy blocks, and Docling is not importable.
- **Mitigation:** Specify the owner and algorithm of `document` for non-Docling sources. Recommended: a Memory-owned, dependency-free block segmenter (Markdown headings/paragraphs; JSON/YAML/code as recursive-equivalent with a declared rule). Docling's chunker is used only for Docling-converted documents. Also state the explicit missing-extra behavior: a typed refusal for the four formats only, while text continues.
- **Test impact:** A DI-16 row for text with the default strategy, without the Docling extra.

### INGEST-R1-OPUS-005 — Medium — the "verified serving capability" counter alternative is infeasible for Docling/semchunk chunking; counter asset location is unspecified

- **Violated requirement:** IR-09 (exact counter), IR-11 (local provisioning/offline) and IR-12 (async effects).
- **Evidence (upstream main, fetched 21:09Z; not a pinned release):**
  - `docling_core/transforms/chunker/tokenizer/base.py`: `BaseTokenizer.count_tokens` is **synchronous**.
  - `hybrid_chunker.py:421` calls `semchunk.chunkerify(self.tokenizer.get_tokenizer(), chunk_size=…)`. This needs a tokenizer object or callable and performs many repeated counts. Lines 312–318 re-count in a convergence loop.
  - LM Studio tokenization is exposed via the `lmstudio` Python SDK (`model.tokenize`), not the OpenAI-compatible REST (docs fetched 21:09Z).
  - The REM allows "provisioned assets **or** an explicitly verified serving capability" (lines 155–158, 457–458). Driving a synchronous Docling tokenizer with network counts from inside Chat's async loop needs blocking bridges and many round trips per chunk.
  - The maintainer decision rules out operator tokenizer settings, but the REM never says where provisioned counter assets live. The default HF cache is user-global mutable state.
- **Mitigation:** For chunking (all three strategies), require a local, offline, synchronous tokenizer bound to the served artifact. Use server counting only as a gate-A or preflight cross-check. Name the asset-root resolution (a packaged/provisioned path that is not the user's global cache, or a declared single assets root) as part of the readiness manifest.
- **Test impact:** DI-17 adds a check that the server counter matches the local counter at boundary inputs.

### INGEST-R1-OPUS-006 — Medium — XLSX formula-cache, hidden row/column and clipping rules lack a feasible detection mechanism; PPTX notes and comments share one layer

- **Violated requirement:** IR-04 and IR-05 (no fabricated success; missing/error caches refuse; declared omissions), and IR-16 (avoid a predictable gate-A stop).
- **Evidence (upstream main, not a pinned release):**
  - `msexcel_backend.py:878-884` loads with `data_only=True`, and `_displayed_cell_text` (lines 152–163) renders `None` as `""`. A formula whose cache is missing is indistinguishable from a blank cell in Docling output.
  - Hidden **sheets** are routed to `ContentLayer.INVISIBLE` (lines 2913–2914). No hidden row/column handling was found.
  - Merged ranges beyond `_MAX_MERGED_CELLS = 100_000` are **clipped with `_log.warning`** only (lines 671, 864–871). Unsafe ZIP paths and images are also log-and-skip (lines 1096, 2034–2191).
  - `mspowerpoint_backend.py:429-433` puts **comments into the NOTES layer**, the same layer as speaker notes (lines 2076–2093).
  - The REM requires refusal on missing/error caches, exclusion of hidden rows/columns, clipping treated as failure, labeled notes and excluded comments (lines 268–298). It also says "do not … add another engine" (line 300), and the companion says "not another extraction engine".
  - These rules cannot be enforced from Docling output alone. A secondary read-only structural audit is needed (e.g., openpyxl `data_only=False` formula inventory against cached values; row/column `hidden`; merged-cell counts; slide `show`; distinguishing notes from comments). Whether such an audit is permitted is undecided.
- **Mitigation:** Explicitly authorize, or reject, a bounded **non-text-supplying structural audit** inside the Tools adapter. Its output may only refuse ingestion or add coverage metadata, never supply content. Name its parser (openpyxl/python-pptx, already Docling backend dependencies) and its limits. Require capture of backend warnings (logging handler) as failure signals. Otherwise narrow the XLSX/PPTX contract now rather than at gate A.
- **Test impact:** DI-13/DI-14 already cover the cases; add a "backend-warning ⇒ refusal" witness.

### INGEST-R1-OPUS-007 — Medium — the all-source scope and acceptance rows require web and automatic-tool ingestion routes that the maintained product does not have

- **Violated requirement:** IR-13 (actual handoffs), IR-02 (truthful coverage) and IR-14 (meaningful proofs).
- **Evidence:**
  - Chat `/ingest` admits only local paths (`registry.py:684-700` → `SmartFileReader.read` → `Path.resolve`). There is no URL route.
  - `friday_tools/web/reader.py` and `web/fetch.py` contain no memory, store or ingest references.
  - `ToolOutputIngester` / `ingest_fire_and_forget` has **no caller** in Chat, Agent, Tools or Runtime. The only caller is legacy `tests/integration/memory/friday.py`.
  - The maintainer instruction says to "assume" text and web ingestion exist (`format-expansion.json`). The REM honestly says to "report the gap" (gate A item 6). Yet DI-16 ("across document/text/web/tool ingestion"), DI-19 ("text/web/automatic-tool/smart_read storage wiring") and TD-10 are **unconditional**, and the non-goals forbid adding fetchers.
- **Counterexample:** DI-16 cannot pass without adding a web-ingestion route (forbidden) or redefining "web ingestion".
- **Mitigation:** Record the source counter-evidence now and obtain a maintainer decision: either narrow the all-source scope to the routes that exist (`/ingest` file/text, smart_read small and large storage) or define web ingestion precisely. Make DI-16/DI-19/TD-10 conditional on the gate-A route inventory, with "absent route ⇒ documented gap, not test credit".
- **Doc impact:** REM §D, gate A item 6, DI-16/DI-19, companion TD-10.

### INGEST-R1-OPUS-008 — Medium — the Tools-side storage boundary to the Memory policy is unspecified, and large-file "raw_chunk" storage conflicts with "no double chunking"

- **Violated requirement:** IR-08 (typed boundaries, no cycles, shared policy) and IR-13.
- **Evidence:**
  - `friday-tools` declares only Core and Finance (plus an optional `llm` extra) and **no Memory dependency**. Yet `smart_read.py:38, 218-223` already lazily imports `friday_memory.ingestion.large_file_processor`.
  - The companion requires smart_read storage to use "the shared ingestion options and validated chunk plan" and TD-10 requires "token/dimension guards through the same injected policy … without Chat". The REM's Core row lists only chunk/source/options/counter contracts, with no ingestion-service protocol, and no composition root for headless Tools is named.
  - `LargeFileProcessor` stores `raw_chunk` records produced by its own 2,048-character chunker (`large_file_processor.py:887-908`; Chat config `adapters.py:2458-2463`), plus `file_synthesis` and `chunk_summary` records (lines 922–954). The REM keeps read/summarization chunking, but it does not say whether `raw_chunk` storage must be regenerated from the shared plan, and so avoid storing the summarizer's character chunks, nor whether derived summaries fall under the ingestion policy or only the embedding guard.
  - The small-file path stores the whole file as one document (`smart_read.py:604-613`).
- **Mitigation:**
  - Add a Core-level typed ingestion-entry protocol (or an explicitly declared Tools → Memory dependency) and name the headless composition root.
  - State that stored `raw_chunk` records come from the shared plan, separate from summarization windows.
  - Classify `file_synthesis` and `chunk_summary` as derived records under the guard only, or under the policy.
- **Test impact:** TD-02/TD-10 gain "stored raw chunks equal the shared-plan chunks" and "derived-record classification" assertions.

### Advisory (non-blocking)

- **OPUS-A01 (IR-12):** Specify the execution model. Docling conversion/OCR and tokenizer counting are CPU-bound and synchronous, so run them off the event loop (worker thread or process), with cancellation semantics for uninterruptible threads. `ingest` is in `_SHARED_ADMISSION_COMMANDS` (`registry.py:77-86`), so multi-minute OCR holds shared admission for the whole handler. Either accept that explicitly or acquire admission only around storage.
- **OPUS-A02 (IR-12):** Docling sniffs content and "expands generic ZIP archives into separate documents" (advanced-options docs). Require `allowed_formats` restricted to the four formats, assert that the detected `InputFormat` equals the extension-admitted format, and refuse any multi-document result.
- **OPUS-A03 (IR-09):** Effective served capacity should consider the server's physical batch/ubatch limit for embedding inputs (llama.cpp-backed servers), not only the loaded context. LM Studio REST exposes `eval_batch_size`. This is knowledge-based; verify at gate A.
- **OPUS-A04 (IR-06/O-05):** `parse_line_limit` maps malformed `--lines*` tokens anywhere in the arguments to 100 (`files.py:135-151`). `/ingest notes.txt about --lines-of-code` therefore silently ingests 100 lines, and the `/ingest` response does not report truncation. Record this as a discovered bug per O-05, and include `truncated` in the new ingest response fields.
- **OPUS-A05 (IR-16):** Gate A itself needs installs, model downloads and network access. Record its separate authorization and effects envelope: allowed hosts, model/asset destination outside user caches, size budget, and who reviews the readiness manifest.
- **OPUS-A06 (IR-06):** Specify `/read` handling of `--chunking`/`--chunk-tokens` (usage error or ignored), and whether recognized overrides inside an unquoted-semantics "quoted" description are extracted.
- **OPUS-A07 (IR-15):** The two-OpenAI/one-Anthropic roster is a recorded maintainer exception. Note the reduced provider diversity when weighting agreement between seats.

## 6. Requirement-to-evidence matrix (IR-01..IR-16)

| IR | Verdict | Independent evidence |
| --- | --- | --- |
| IR-01 | PASS | `roster.json` (explicit maintainer roster and exception); `authority.json` `product_code_authority` = design_only and `implementation_approval: not_granted`; board `implementation_authority: design_only`, branch `feature/cmd-ingest-001`; REM lines 13–17 and 162–165 separate review from construction; MAINT UAT stays separate. Helper confirmed HEAD and branch. |
| IR-02 | PASS (design) | REM §B lines 226–254: allowlist before Docling, full conversion before Memory, refusal of partial/failed/empty/diagnostic content, sideband diagnostics. Source confirms the baseline gap (`files.py:59-60, 123-133` placeholder; `registry.py:684-700` stores it). Coverage truthfulness is conditional on OPUS-006/007. |
| IR-03 | PASS (design) | REM lines 235–243, 266–267; DI-01..04. Legacy defects independently confirmed: `pdf_reader.py:147-152` in-band "[Error extracting text]" text; `docx_reader.py:107-116` emits paragraphs then tables. |
| IR-04 | **CHANGES (OPUS-006)** | Rules at REM lines 268–282 are sound. Upstream `msexcel_backend.py` `data_only=True` makes a missing cache equal a blank cell; hidden rows/columns are not handled; clipping is log-only. Legacy `xlsx_reader.py:153-191` has an active-sheet default, a 1,000-row limit and `data_only=True`, which the companion correctly keeps separate. |
| IR-05 | **CHANGES (OPUS-006)** | REM lines 269, 284–291. Upstream PPTX moves hidden slides/shapes to INVISIBLE (feasible), but notes and comments share the NOTES layer. No PPTX admission in Chat (`files.py:11-23`), factory or smart_read (confirmed). |
| IR-06 | PASS with advisories | Source: `_parse_command_input` uses `split()` (`registry.py:1196-1201`), confirming the quote-split loss. Handler identity is resolvable (`_handlers` / `BASIC_COMMAND_HANDLERS` at `registry.py:153, 1173-1174`), so default-handler-only routing is feasible. API54 confirmed (`__all__` has 54 entries; `tests_commands/test_memory_queries.py:501`). Commands has zero dependencies. A04 and A06 are advisory. |
| IR-07 | **CHANGES (OPUS-004)** | Defaults, precedence and strategy semantics match `discussion-decisions.json` and `authority.json`. Current Chat character slicer confirmed (`adapters.py:378-399, 2793-2805`, `smart_file.chunk_size or 2048`). The `document` owner for non-Docling sources is missing. Upstream HybridChunker silently drops oversized headings/captions via `warnings.warn` (`hybrid_chunker.py:318-329`); the REM's lossless split-or-refuse rule (lines 419–421) correctly anticipates this. |
| IR-08 | **CHANGES (OPUS-004, 008)** | Dependency graph from pyprojects: Core ← LLM ← Memory; Tools → Core only. No cycle is introduced by Memory receiving an injected Tools chunker, but the Tools → Memory policy boundary is undeclared and smart_read's lazy `friday_memory` import already exists. |
| IR-09 | **CHANGES (OPUS-003, 005)** | `EmbeddingOptions` strict (`model_library.py:105-120`); new fields absent today, as the REM states. Qwen card confirms 32K context and up to 2,560 dimensions with MRL (fetched); the REM keeps Qwen illustrative. LM Studio REST `loaded_instances[].config.context_length` and `max_context_length` confirmed. |
| IR-10 | **CHANGES (OPUS-001, 002)** | The overflow rules (REM lines 513–536) are strong: minimum of declared and loaded capacity, no clamping, preflight, recheck, cardinality/dimension/finite checks. Vector adapter embeds then adds in a single call (`vector.py:130-151`), so a guard inside `embed_documents` precedes persistence (feasible). Convention and store-binding gaps per OPUS-001/002. |
| IR-11 | PASS with OPUS-005 | Certifi verified on PyPI: 2026.10.19 not yanked; wheel SHA-256 `42d35340…670e1b` matches the recorded value; uploaded 2026-10-20. GHSA-6q48-6c7w-9gw2 patched version is 2026.10.18. Lock pins 2025.11.12 (`uv.lock:366-367`). Upstream Docling declares `certifi>=2024.7.4`, so the explicit floor is necessary. Packaging upstream uses `docling-slim` extras (`feat-chunking`, `feat-ocr-*`); the REM correctly refuses to assume extra names. |
| IR-12 | PASS (design) with A01/A02 | REM lines 248–251 and gate A item 4 (limits, encrypted refusal), DI-11. Docling `max_num_pages`, `max_file_size` and `document_timeout` (cut pages reported `success=False`) exist per official docs. The execution model and format sniffing are unspecified (advisory). |
| IR-13 | **CHANGES (OPUS-007, 008)** | Companion consumer table verified against source: factory routes PDF/DOCX/XLSX to legacy readers and PPTX to `BinaryFallbackReader`; smart_read `BINARY_EXTENSIONS` lacks `.pptx`; its cache queries `type=file_synthesis` (`smart_read.py:422`) while the small path stores `ingested_file`. Web and automatic-tool storage routes are absent. |
| IR-14 | PASS (plan) with OPUS-007 | DI-01..20 and TD-01..10 require genuine fixtures, real Memory/Chroma, call-phase mutation witnesses, installed normal and `-O` lanes, preserved oracles and baseline accounting. DI-16/DI-19/TD-10 need conditionalization (OPUS-007). No future product tests are demanded now. |
| IR-15 | **CHANGES (OPUS-001)** | The fresh/disposable store decision and no reset/scan/cleanup are explicit (REM lines 544–549, 625–628). Governance is truthful: board, authority, README, tactical plan and handoff agree on design_only, the next gate and the future PR base `master`. The legacy-store rule under the current profile is missing. |
| IR-16 | PASS with gaps | Gate A lists 7 steps with stop conditions (item 5; line 299 format stop; line 590 boundary stop). OPUS-002/005/006/007 identify predictable gate-A stops that should be resolved in the document first. A05 is an advisory on gate-A authorization and effects. |

## 7. Commands executed and exact results

All commands ran with `GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1`, plus
`UV_CACHE_DIR` and `XDG_CACHE_HOME` pointed at my scratch and `UV_NO_SYNC=1
UV_OFFLINE=1 UV_FROZEN=1 UV_PYTHON_DOWNLOADS=never`. The last group neutralizes
an inner `uv run python …` that `check-documentation-lifecycle.py:140-146` spawns
without `--no-sync`. Script write paths were inspected before execution:
`render --check` never writes, and `validate` never writes.

| ID | Command | Exit | Result |
| --- | --- | --- | --- |
| request-hash | `shasum -a 256 review-request.json` | 0 | `edcdfc3b…0582eb` (match) |
| helper/manifest/state hashes | `shasum -a 256` | 0 | all match pins |
| integrity-start | `python3 -B check_integrity.py review-request.json > start-integrity.json` | 0 | PASS, failures `[]`, logical `f12f3152…71bf` |
| board | `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` | 0 | "Development board validation passed: 36 tasks" |
| dashboard | `… friday-dev-board.py render --check` | 0 | "Planning dashboard is current" |
| docs | `… scripts/check-documentation-lifecycle.py` | 0 | "Documentation lifecycle validation passed: 978 Markdown files checked" |
| metadata | `… scripts/check-package-metadata.py` | 0 | "Validated 18 pyproject.toml files: … internal pins OK" |
| whitespace | `git diff --check c36e7ee5..8be50b12` | 0 | no output |
| integrity-end | same helper → `end-integrity.json` | 0 | PASS, failures `[]`, identical logical index |

A first attempt at the four `uv` checks failed with exit 127 because of zsh
word-splitting of a variable (the command was not found). It executed nothing
and was rerun with explicit argv.

Static probes: read-only `sed`, `grep` and `cat` over pinned and related source
files; a stdlib `ast`/`tomllib` probe of `friday_commands.__all__` and package
dependencies.

## 8. Reproduced vs inspected vs public-source verification

- **Reproduced (executed):** integrity start and end; the four admin checks; whitespace; the API54 count; package dependency extraction.
- **Inspected (source-only, not executed):** every source citation in §5 and §6. No product code, tests or application was run.
- **Public official sources fetched (curl, 2026-11-10 ~21:09Z, into my scratch only, treated as untrusted data):**
  - Docling `main` `msexcel_backend.py`, `mspowerpoint_backend.py` and `pyproject.toml` (version 2.150.0).
  - docling-core `main` `pyproject.toml` (2.106.0), `tokenizer/base.py` and `hybrid_chunker.py`.
  - Docling advanced-options docs.
  - LM Studio Python tokenization and REST list docs.
  - Hugging Face Qwen3-Embedding-4B and nomic-embed-text-v1.5 README.
  - PyPI certifi 2026.10.19 JSON; GitHub advisory GHSA-6q48-6c7w-9gw2.

  Upstream `main` is **not** a selected or pinned release. Those findings show design hazards that gate A must settle on the chosen release, not facts about the eventual pin.

## 9. Skipped checks and limits

- No runtime suites, builds, Ruff, mypy, installs, resolution, model downloads, provider calls or store reads, as required. Historical baseline debt (Ruff 534, root `test_display` collection conflict, seven legacy format failures, MAINT Chat1413/15) was not rerun and is not attributed to this candidate.
- Docling behaviors were checked at upstream `main` only. The pinned release may differ.
- llama.cpp ubatch behavior (A03) is from prior knowledge, not fetched.
- I did not audit every Chat/Agent embedding call site exhaustively; OPUS-002 lists the call sites found and asks gate A to complete the inventory.

## 10. Baseline failures vs regressions

This is a document-only candidate. The diff touches only planning files and
whitespace is clean. No product, test, lock or metadata regression is possible
or claimed. Source pins are unchanged.

## 11. Isolation audit

- All artifacts live under `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/0092ee75-7f1e-464d-badd-b69e2bb3a186/scratchpad/opus-ingest-r1/`: reports, check outputs, uv/XDG caches, web fetches and a start-marker file.
- Repository: `find . -name .git -prune -o -newer start-marker` returns **0** paths. The helper's protected-manifest (17,536 entries), preserved-state (6 records: two dirty YAMLs, `.friday-old`, `exports` and two export files) and status checks pass at the end.
- Supplied input root: hashes unchanged. File mtimes (21:04:26 and 21:05:02Z) predate my first command (about 21:05:30Z) and were set by the controller.
- **Disclosure:** the submodule gitdir `docker-bench-security/.git` shows a *directory* mtime of 21:12:17Z. No file inside it changed: `index` (Oct 15), refs, objects and FETCH_HEAD (20:55Z) all predate my start. This is consistent with a transient lock entry from a host-side git status/checkpoint. It is git metadata outside the governed logical identity, which was unchanged.
- **Conduct deviation:** two of my read-only git invocations (`git -C … log --oneline -1 -- <path>` at about 21:11Z, and `git ls-files -s docker-bench-security` at about 21:13Z) ran without an explicit `GIT_OPTIONAL_LOCKS=0`. Neither command takes optional index locks, and the second ran after the 21:12:17 mtime. I cannot attribute the directory mtime with certainty.
- Nothing was cleaned or restored.

## 12. Advisory score (rubric)

| Dimension | Weight | Score | Basis |
| --- | --- | --- | --- |
| Scope, authority and boundedness | 1.5 | 1.25 | Exemplary governance and claim limits; web/tool assumption contradiction (007); gate-A effects envelope (A05). |
| Shared architecture and integration | 2.0 | 1.30 | Clear ownership table, but no `document` owner for non-Docling sources (004), undeclared Tools → Memory boundary and raw_chunk ambiguity (008), embedding caller scope (002). |
| Format extraction and coverage | 2.0 | 1.60 | Thorough fail-closed four-format rules; XLSX/PPTX detection mechanism undecided (006). |
| Chunking, embedding and data safety | 3.0 | 1.90 | Strong overflow and vector validation; legacy-store convention/binding gap (001, High); absent-field behavior (003); counter feasibility (005). |
| Verification, reproducibility and reporting | 1.5 | 1.25 | Rich DI/TD matrices with negative and mutation controls; some rows unconditional on absent routes (007). |
| **Total** | 10.0 | **7.30** | No threshold applied. Score does not waive any finding. |

## 13. Recommended next gate

The controller reconciles the three seat reports. A bounded **document-only**
revision of the REM and companion addresses INGEST-R1-OPUS-001..008. Several
items need explicit maintainer decisions:

- the legacy-store rule (001);
- the web/automatic-tool route scope (007);
- whether a structural-audit parser is permitted (006);
- whether the new profile fields are required (003).

Then a fresh round-2 council reviews the revised frozen candidate. Gate A
(isolated dependency, model and counter readiness) should begin only after that,
under its own recorded authorization and effects envelope. No construction,
acceptance, merge or publication is implied by this report.
