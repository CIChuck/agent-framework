# ASTRA — INGEST round 1 independent design-readiness review

**CHANGES_REQUESTED — advisory score 8.5/10.** One mandatory finding (high); two low advisory observations. This is readiness for gate A and final directive drafting, not implementation conformance, acceptance, or permission to build.

## Identity, authority and independence

- Reviewer: ASTRA, GPT-6 Astra, high reasoning effort; 2026-11-10. Fresh review task context; no builder transcript/private reasoning or current peer verdicts consulted. No delegated or nested agents. No memory lookup or prior-review conclusions used.
- Repository: `/Users/chuckrussell/Dev/gendev/agent-framework`.
- Candidate: `8be50b1218fc4db67fbd5d546fea9d7be6a2fd64`; branch `feature/cmd-ingest-001`.
- Base and independently reproduced merge-base: `c36e7ee51a9328918b9bb97712aa7f1d4a850d19`. Diff: `c36e7ee51a9328918b9bb97712aa7f1d4a850d19..8be50b1218fc4db67fbd5d546fea9d7be6a2fd64`.
- Request: `/private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/friday-ingest-council-r1-inputs-qj57z4f_/review-request.json`, verified before substantive reading: SHA256 `edcdfc3b2f2734499b54c919db86a35d5731d712ecd81e84a904eb2ad40582eb`.
- Immutable helper SHA256: `6e1ec704678475fa6dbd45301c94a824e217a177cc8c83e05ee05b6f606278c3`, verified before execution.
- Full proposal and companion reviewed, not merely their small branch delta. Request authority/document/source pins checked by supplied helper. Policy hierarchy: explicit maintainer direction, engineering/lifecycle/validation policies, current proposed contracts. Read AGENTS, council and independent-code-validator skills. Explicit single-seat/no-delegation instruction controls the council skill's orchestration default.
- Current authority.json inspection was restricted to branch, current_scope, product_code_authority, active_council_roster and document_ingestion_remediation. Board is started/design_only/pushed; planning/in_review is consistent. Sol/Astra/Opus5.5 is the authorized roster; no prior MAINT scoring threshold applies. MAINT status mentioned in packet navigation supplies no evidence for this proposal.
- Authorized shared-checkout read-only exception used. Own scratch: `/private/tmp/ingest-r1-astra-sBNoaL`. Existing dirty YAML and `.friday-old` were preserved. No installation, resolution, model download, application invocation, provider call, user-store query, repair, acceptance or publication.

Evidence shorthand below: **REM** = `docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md`; **TD** = `docs/planning/active/command-refactor/proposals/tools-document-adoption.md`. Source paths are repository-relative and refer to frozen current bytes. Line references identify inspected code/design, not executed product behavior.

## Findings

### INGEST-R1-ASTRA-001 — high, mandatory: all-source smart_read ownership conflicts with the unit split

**Violated requirement:** settled all-source shared policy (discussion-decisions.json), REM D (lines 365–443), A.6 (147–153), DI-16/19; IR-07/08/13/16. Repository engineering policy requires explicit cross-package contracts and bounded changes.

**Evidence:** REM promises every storage handoff uses the selected policy and INGEST proves smart_read wiring. Its exact allowlist (556–590) admits the new Tools converter, Memory ingestion modules and Chat composition, but omits `packages/friday-tools/src/friday_tools/filesystem/smart_read.py`; REM 309–316 retains legacy Tools consumer behavior. TD 34–50 sequences INGEST completion first and Tools entry-point changes second; TD 111–121 places smart_read changes in that later unit.

Current smart_read has two different storage paths. `smart_read.py:582–654` directly calls `self._memory.store_document(text=content, ...)` for small files, bypassing `LargeFileProcessor` and `ToolOutputIngester`. Its constructor (178–207) takes a concrete MemoryController and has no common ingestion-options capability. `run:283–319` returns session/persistent cache hits before processing; session validity at 376–400 compares mtime only. Altering Memory's large-file processor cannot fix either path. `memory_controller.py:1918–2017` forwards supplied strings to collection storage, without this proposed ingestion policy; that controller is also outside the listed change scope. Chat tool construction at `adapters.py:2351–2381` is not the public headless Tools path.

**Concrete counterexample:** a headless smart_read consumer with a fresh store and a text file below its character threshold but above 512 model tokens, `store_to_memory=True`, takes the direct single-document call. INGEST's permitted large-file policy changes leave that path unchanged. A prior context-only cached read followed by storage enabled returns before any new policy handoff; changing the model/budget likewise does not enter the processor. A lower LLM limit guard only enforces model capacity, not the requested 512-token ingestion budget or splitting. A Chat-only injected proxy does not establish the promised public headless behavior and cannot repair a cache return before the proxy is called.

**Risk:** a compliant implementation can either leave an advertised all-source hole or modify a companion-only file before that unit's directive. This is a known source-level boundary conflict, not a demand to have implementation now. Gate A's general stop-if-paths-expand rule safely prevents unauthorized construction but should explicitly identify this already demonstrated prerequisite instead of presenting the split as satisfiable unchanged.

**Narrow mitigation:** reconcile the documents before freezing directives. Assign the minimal existing text/tool smart_read storage/cache/options handoff to INGEST (leaving four-format reader routing for TD), with a neutral injected capability and exact paths; alternatively record a maintainer-approved staged scope and make all-source completion depend on the companion. Do not silently weaken the settled all-source requirement or add general Tools refactoring.

**Future verification/doc impact:** DI-16/19 and TD-02/05/10 must identify which unit proves small, large and force_chunked public headless paths; test read-only cache then storage opt-in, strategy/budget/profile drift, and an above-512/below-model-limit input with exact source coverage. Update both allowlists, completion claims and consumer matrix. No product test execution is required to resolve this design finding.

### INGEST-R1-ASTRA-002 — low, advisory: explicitly bind returned vector indices to source order

REM 533–536 specifies cardinality, dimension and finite values. `friday-llm/.../embeddings.py:382–394` currently extracts response vectors in response-list order. A response containing two valid vectors in reversed input-index order passes the listed shape checks while associating embeddings with the wrong text. This is a source-informed strengthening of the future guard contract, not a claimed newly introduced runtime regression.

At gate A/directive drafting, require provider index/order semantics to be verified, reorder only using validated unique indices when appropriate, and refuse duplicate/missing/out-of-range indices. Add a shuffled-index and duplicate-index negative control alongside DI-18. Clarify the LLM contract; no new provider or storage engine is needed. IR-10 remains design-pass with this advisory because the proposal already requires full result validation and one vector per input.

### INGEST-R1-ASTRA-003 — low, advisory: make reserved description tokens explicit

REM C and D reserve recognized `--chunking=`/`--chunk-tokens=` tokens anywhere before/after the source while preserving other description semantics. For `/ingest "a.txt" notes --chunking=fixed`, the option is necessarily removed from the description. A description that discusses the literal option has no documented escaping/terminator rule; only the source path is unquoted. Existing `registry.py:689–695` joins remaining description arguments, and `files.py:142–158` already reserves broad `--lines` tokens.

Document that these exact tokens are reserved and illustrate the supported way to include literal option text, or explicitly defer a literal escape syntax rather than allowing implementers to invent shell rules. DI-05/16 should freeze quoted option-like paths, before/after flags, duplicate/malformed flags, description quote characters and option-prefix lookalikes. This is a usability clarification, not a demand for a global parser change; IR-06 passes for this gate.

## Full criterion matrix

PASS means coherent bounded design evidence for this gate only. It never means a future converter or installed deployment has passed.

| Criterion | Outcome | Independent requirement/source evidence and assessment |
|---|---|---|
| IR-01 | PASS | Start integrity pins branch/HEAD/index/all authority; current authority fields, board current row and roster agree on design_only. REM 3–35 and 638–647 separate discussion decisions, gate A, construction and MAINT acceptance. Independently reproduced merge-base is the requested merged parent. |
| IR-02 | PASS | REM 209–253 admits exactly local regular four-format paths, meaningful source content, complete conversion and zero ingest on partial/error/empty results; DI-04/06/07/09 require real stored-text proof. Source `files.py:13–25,52–64,129–139` independently confirms placeholder admission and missing PPTX; `base.py:36–40` makes success error-only. These baseline defects are covered by the proposed contract, not evidence it is implemented. |
| IR-03 | PASS | REM 230–247, format table and DI-01/02/03/09 require PDF page/order/OCR and interleaved DOCX tables. Inspected `pdf_reader.py:139–185` permits per-page diagnostic text and empty success; `docx_reader.py:99–123` collects paragraphs before tables. The proposal explicitly rejects carrying those semantics forward and bounds unspecified Word parts as disclosed omissions. |
| IR-04 | PASS | REM 264–307 and DI-13 require visible sheets in workbook order, hidden unit counts, saved-cache missing/error refusal, no recalculation, typed values and loss detection. `xlsx_reader.py:151–230` independently shows active-sheet/sheet/range/read-only data_only semantics; direct default limit is 1000 whereas factory.read passes its own None. TD 61–76 distinguishes selection/pagination from whole-workbook ingestion, including explicit hidden selection. Gate A must prove actual formula/visibility detection; support labels alone are insufficient, and inability forces contract revision. |
| IR-05 | PASS | REM format table and 285–307 require slides, notes, bullets/tables, original numbers, hidden content and detected visual omissions; DI-14 and TD-09 make late-slide/notes proofs mandatory. Source Chat extension map has no PPTX and factory routes unmatched files to BinaryFallbackReader; smart_read has no conversion route. Proposed rejection of image-only/empty native content and no media fetching is coherent. Within-slide ordering is appropriately frozen on real fixtures at gate A. |
| IR-06 | PASS/advisory 003 | REM C requires untouched raw tail, exact quoted interiors, no interpolation, leading scoped flags, default-handler identity checks and unchanged root API54. `registry.py:164–197,1196–1201` shows raw user_input remains available when actual handler is selected, so scoped parsing is feasible without global split changes. `files.py:142–158` supplies existing --lines semantics. DI-05/06/16 cover custom handlers and malformed options; reserved-description clarification advised above. |
| IR-07 | CHANGES_REQUESTED/001 | REM D and discussion decisions coherently specify per-field CLI > YAML > built-in document/512, all three strategies, final-input budgets, no overlap knob, split-or-refuse and no second pass. Source `adapters.py:378–404,2793ff` uses character slicing; `chunker.py:88,105–131` estimates tokens. These are correctly replaced in the proposal, but the known smart_read direct path is unassigned in INGEST. |
| IR-08 | CHANGES_REQUESTED/001 | REM 89–102,209–222,428–443 assigns minimal Core contracts, Tools native Docling ownership, injected Memory policy and LLM guards; package metadata confirms Commands has no dependencies and both Tools and Memory depend on Core. Native structure can remain private behind a typed capability. Existing smart_read dynamically imports Memory, and large_file_processor.py:525 imports Tools code chunking: baseline coupling must not become the new contract. The missing public storage/cache handoff ownership prevents a complete bounded integration plan. |
| IR-09 | PASS | REM 449–554 and A.7 require strict positive cap/dimension, exact artifact identity, offline counter or verified serving count, smaller served cap and refusal for unknown identity. Source model_library.py:105–120,245–246,312–320 has only batch/cache options; packaged YAML selects Nomic. Qwen 4B remains illustrative; official card independently supports 32K/up-to-2560, not actual server capacity. No model-switch implication. |
| IR-10 | PASS/advisory 002 | REM 503–541 separates query/document formatting, final headers/special tokens, all-chunk preflight, LLM overflow rejection and complete result validation before storage. `adapters.py:263–270` shows embed_text aliases queries, while collection manager uses embed_documents and embedding service currently forwards raw input. Call-site audit is necessary and expressly required. Full cardinality/dimension/finite guards are specified; response index binding is an advisable explicit addition. No rollback is promised for unrelated multi-write failures. |
| IR-11 | PASS | REM A and 167–204 declare extra, lock, actual-target semantic-version/origin verification after every installation, optimized lane and negative controls for Certifi>=2026.10.19. Package metadata independently shows current optional legacy readers and Chat bare Tools dependency. Docling/counter/OCR dependencies and offline asset hashes/licenses are explicitly gate-A work with stop conditions; unknown graph or external executable cannot be assumed away. Official Certifi advisory and release metadata support the floor's recorded context, not whole-graph security. |
| IR-12 | PASS with gate-A risk | REM 133–146,226–253 and DI-04/11 bound archives/page/cell/slide/file resources, errors, local assets, no remote enrichment or external references, and cancelled extraction cannot later ingest. TD 57–60 preserves sandbox-first behavior corroborated by smart_read.py:247–264. Exact thresholds, async execution model and progress/cancellation mechanics remain to freeze; DI-11 explicitly avoids unsupported hard-timeout promises. Gate A should demonstrate cancellation suppression even if a worker conversion finishes late. |
| IR-13 | CHANGES_REQUESTED/001 | Independently traced command registry → SmartFileReader → FrameworkMemoryAdapter, smart_read small direct store versus large processor, and tool_ingester.py:230–305 admission → chunk → collection. Web reader.py:163–173 explicitly truncates normalized text with metadata; fetch.py has existing max-length clipping. REM A.6/D correctly preserve extraction/admission and require inventory rather than invent missing URL ingestion. TD recognizes factory and smart_read independence and file_synthesis cache provenance. Actual small/cache handoffs conflict with staged ownership as finding 001 explains. |
| IR-14 | PASS | REM DI-01..20/618–621 and TD-01..10 require genuine independently valid fixtures, actual registry/public consumers, Chroma stored chunks, source and installed ordinary/-O lanes, offline OCR/counters, canonical origins and call-phase mutation witnesses. Existing test_files_replay_shell.py:25–51 uses fake extension fixtures and Sheet1 expectations, confirming exact oracle exceptions are necessary. No mock-only positive claim or setup-failure rejection credit. Existing metadata.py preserves absent versus explicit-empty description and should retain its oracle. |
| IR-15 | PASS | REM 538–549,623–636 and TD cache rules explicitly require disposable stores, no reset/migration/purge, no automatic Qwen selection, store/model mismatch refusal. Current authority and branch handoff target master and separate parent merge from current approval. Immutable start check verifies both dirty configs and protected generated state. Historical delivery receipt was inspected, not independently queried remotely. |
| IR-16 | CHANGES_REQUESTED/001 | REM A has bounded graph, platform, models, format coverage, counter readiness and exact-signature stop conditions; these are legitimate future gate work. General refusal on unsupported coverage and unknown serving behavior is sound. Known smart_read scope conflict must be explicitly reconciled before final directives, rather than leaving the first unit's all-source completion dependent on an excluded second-unit path. Absence of construction approval is not a blocker. |

## Reproduced checks, commands and results

Required administrative commands were newly executed with reviewer-owned receipts. No historical receipt/controller script was replayed. Environment for these and every Git subprocess:

```text
GIT_OPTIONAL_LOCKS=0
PYTHONDONTWRITEBYTECODE=1
UV_CACHE_DIR=/private/tmp/ingest-r1-astra-sBNoaL/uv-cache
XDG_CACHE_HOME=/private/tmp/ingest-r1-astra-sBNoaL/xdg-cache
```

`shasum -a 256` against request and helper: exit 0, exact hashes above. New scratch was created with `mktemp -d /private/tmp/ingest-r1-astra-XXXXXX`, exit 0. Immutable helper, before substantive reading:

```text
python3 -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/friday-ingest-council-r1-inputs-qj57z4f_/check_integrity.py /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/friday-ingest-council-r1-inputs-qj57z4f_/review-request.json
```

Output was redirected exclusively to own `start-integrity.json`; helper passed, no failures. It computes `git ls-files -s -z` logical identity before status. End run uses identical argv and own `end-integrity.json`.

| Exact command | Exit | Reproduced result |
|---|---:|---|
| `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` | 0 | 36 tasks valid |
| `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check` | 0 | Dashboard current |
| `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py` | 0 | 978 Markdown files checked |
| `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py` | 0 | 18 pyproject files valid |
| `git diff --check c36e7ee51a9328918b9bb97712aa7f1d4a850d19..8be50b1218fc4db67fbd5d546fea9d7be6a2fd64` | 0 | No whitespace errors |
| `git diff --name-only c36e7ee51a9328918b9bb97712aa7f1d4a850d19..8be50b1218fc4db67fbd5d546fea9d7be6a2fd64` | 0 | Exactly the request's 12 planning/status paths |
| `git merge-base HEAD c36e7ee51a9328918b9bb97712aa7f1d4a850d19` | 0 | Requested base |

`admin-results.json` contains complete argv/exits/stdout/stderr and individual `.log` receipts. `candidate.diff` contains the requested path-filtered diff excluding authority.json, whose permitted current fields were separately extracted. Stdlib AST inspection of smart_read (`ast.parse`, no imports/execution of product modules) wrote `static-handoffs.json`: independently confirms run's two paths, direct small-file store and early cache returns. Static probe exit 0. Read-only source searches used rg/sed/cat/nl; one search for `friday_memory/controller.py` returned missing-path error 2, then rg --files located and inspection used `controller/memory_controller.py`. No readiness conclusion depends on that failed lookup. No runtime suite/build/lint/type-check was required or executed.

## External verification log

Official public documentation only was opened with the web tool on review date; no local server was contacted. Findings below establish design plausibility, not selected-release installation or model readiness.

- [Docling supported formats](https://docling-project.github.io/docling/usage/supported_formats/): independently confirms PDF/DOCX/XLSX/PPTX input support. It does not establish formula-cache fidelity, notes/visibility coverage or resource bounds of any selected release.
- [Docling chunking](https://docling-project.github.io/docling/concepts/chunking/): native chunking takes structured DoclingDocument, contextualization can add metadata, HybridChunker uses tokenizer-guided splitting/merging, and tokenizer extras differ. This supports retaining native structure and counting contextualized input; it does not prove the proposed final 512-token limit.
- [Docling advanced options](https://docling-project.github.io/docling/usage/advanced_options/): provides offline assets, remote-service controls, size/resource and archive-limit configuration. Selected release/platform and exact failure semantics remain gate-A proof.
- [Qwen4B official model card](https://huggingface.co/Qwen/Qwen3-Embedding-4B): 32K context/up to 2560 output dimensions supports the illustrative numeric example only. No activation or performance claim is derived.
- [LM Studio tokenization](https://lmstudio.ai/docs/python/tokenization): documents model-bound tokenization for embedding models as well as LLMs. [Model listing](https://lmstudio.ai/docs/developer/rest/list) distinguishes loaded-instance context length from model maximum. Actual artifact identity, special-token/template parity and server truncation behavior still require exact deployment proof.
- [Certifi advisory](https://github.com/certifi/python-certifi/security/advisories/GHSA-6q48-6c7w-9gw2): lists emSign removal and patched 2026.10.18. [2026.10.19 release metadata](https://pypi.org/pypi/certifi/2026.10.19/json) is available. The maintainer's stricter >=2026.10.19 requirement remains binding. No wheel download/hash or installed-origin proof was performed here.

## Limits, baseline accounting and next gate

Assessment.md/json and planning-checks.json were inspected as historical observations; their probes were not rerun and their stored argv was not executed. Current baseline defects were independently confirmed from source. Root Ruff 534, display collection conflict7196, seven legacy format failures and MAINT Chat1413/15 remain request-reported failed/unwaived background, not reproduced failures or new regressions. No claim of runtime correctness, extracted quality, package graph compatibility, OCR/model readiness, performance, live provider safety or installed behavior follows from this report.

Gate A still needs exact Docling/core/backend release/graph; four-format coverage and independent omission detection; format type/merge/selection rules; tokenizer and contextualization parity; effective loaded caps; actual vector dimension/formatting; no-truncation proof; OCR asset manifest; bounded resource/async behavior; supported extras and Certifi post-install proof. These pending items are intentional and not themselves mandatory findings in this design round. Unproven rules must stop readiness, not become warning-only success. Read-only `/read` should not initialize an embedding model merely to render successfully extracted text.

Recommended next gate: reconcile the three independent design reports, resolve finding 001 in the planning split, then undertake separately authorized gate-A investigation and exact directive drafting. No implementation, remediation, lifecycle advance or acceptance was performed by this reviewer.

## Advisory rubric

| Dimension | Awarded / weight | Rationale |
|---|---:|---|
| Scope, authority and boundedness | 1.4 / 1.5 | Strong explicit gates; known unit split needs correction. |
| Shared architecture and integration | 1.4 / 2.0 | Neutral ownership is sensible; public small-file/cache handoff is not reconciled. |
| Format extraction and coverage | 1.9 / 2.0 | Four formats, actual versus declared coverage, refusal and genuine-fixture proof are carefully scoped. |
| Chunking, embedding and data safety | 2.4 / 3.0 | Exact counters/final budgets/served caps/shape validation are strong; all-source handoff conflict and index-binding clarification remain. |
| Verification, reproducibility and reporting | 1.4 / 1.5 | Thorough future proof matrix and green current admin checks; no installed readiness inferred. |
| **Total** | **8.5 / 10** | Advisory only; cannot waive the mandatory finding. |

## Final integrity and isolation audit

End results are appended below after the immutable helper finishes. All generated files, cache roots and this report are in the newly created own scratch; no locator outside it was created. No cleanup/restoration was attempted. Integrity checks hash protected stores only; no store content was queried or printed. The six preserved metadata records cover the two dirty YAML files, `.friday-old`, `exports`, and the two named export files. Matching protected content does not purport to audit arbitrary host-wide activity; it is the supplied governed boundary check plus a command/output-location audit.

Start integrity: **PASS**, exit 0. End integrity: **PASS**, exit 0. Both receipts are identical: candidate `8be50b1218fc4db67fbd5d546fea9d7be6a2fd64`, branch `feature/cmd-ingest-001`, logical index `f12f3152b2900cf9df29eff6fd1b8fec32d9bccbb5672a4fe6537c3116b571bf`, all 17,536 protected entries and six preserved metadata records match; failures `[]`. Request/helper/pin/status/staged-diff checks pass. Output-location/command audit found no isolation breach. Formal result remains **CHANGES_REQUESTED, 8.5/10**.
