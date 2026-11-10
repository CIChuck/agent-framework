# INGEST-001 deep design council — round 1 reconciliation

**CHANGES_REQUESTED.** All three requested seats completed; no implementation or dependency/model readiness is established. This is a review of the proposed REM and Tools companion, not a failed product implementation.

| Seat | Reported outcome | Advisory score |
| --- | --- | ---: |
| [GPT-6.1 Sol](sol-report.md) | CHANGES_REQUESTED | 8.1/10 |
| [GPT-6 Astra](astra-report.md) | CHANGES_REQUESTED | 8.5/10 |
| [Claude Opus 5.5](opus-report.md) | CHANGES_REQUESTED; execution caveat below | 7.3/10 |

All seats used high effort and fresh contexts. The explicit two-OpenAI/one-Anthropic roster controls. Scores are advisory; there is no averaging or majority waiver. The earlier MAINT-specific 9.5 threshold does not apply to this request.

## Reviewed identity and evidence

Candidate: `8be50b1218fc4db67fbd5d546fea9d7be6a2fd64`, branch `feature/cmd-ingest-001`. Base: `c36e7ee51a9328918b9bb97712aa7f1d4a850d19`. The 12-path planning range and full REM/companion were reviewed.

The [exact request](review-request.json) has SHA256 `edcdfc3b2f2734499b54c919db86a35d5731d712ecd81e84a904eb2ad40582eb`. Its original absolute scratch paths are preserved, not silently rebound. The immutable helper, dispatch identity, six-record metadata snapshot and compressed protected manifest are archived beside it. [Machine-readable reconciliation](reconciliation.json) pins every report and receipt copy. Decompressing the manifest restores its exact original bytes; relocation or later replay needs a new request.

Every reviewer reported matching start/end integrity: 17,536 protected entries, six metadata records, HEAD/branch, index, staging and dirty status. The controller's [final frozen audit](controller-frozen-integrity.json), before reconciliation edits, independently passed. Logical index: `f12f3152b2900cf9df29eff6fd1b8fec32d9bccbb5672a4fe6537c3116b571bf`, measured before status. Later review/status records are a documentation delta, not a changed technical proposal or new reviewed candidate.

## Consolidated mandatory findings

The 11 raw mandatory IDs map to eight themes. All remain open; consolidation closes none.

| Theme | Source IDs | Bounded correction to specify |
| --- | --- | --- |
| Shared storage and cache ownership | SOL-001, ASTRA-001, OPUS-008 | Give `smart_read` small/large storage, warm caches and raw chunks an injected shared ingestion entry point. Reconcile INGEST and TOOLS-DOC allowlists and completion gates; classify derived summaries separately from source chunks. |
| Durable embedding-space binding | SOL-002, OPUS-001 | Bind actual artifact/revision, dimensions and preparation convention at store creation/reopen/read/write. Define unbound-store refusal and precomputed-vector admission; test same-dimension mismatches. |
| Query/document role audit | OPUS-002; SOL-003 advisory overlaps | Include retrieval, maintenance and lifecycle callers. Existing vector queries and synthesis use the opposite role; asymmetric formatting cannot be enabled with unclassified callers. |
| Absent capacity fields and legacy constructors | OPUS-003 | Specify required capabilities, missing-field refusals and non-catalog constructors. Avoid silently bypassing guards or unintentionally breaking all startup paths. |
| Non-Docling document strategy | OPUS-004 | Assign text/Markdown/code/structured-text normalization and default chunking, including minimal/headless installs and missing extras. No hidden strategy fallback. |
| Practical tokenizer execution | OPUS-005 | Assign offline model-bound tokenizer assets and synchronous local counting. Define worker/cancellation behavior; use server counting as a verified cross-check rather than a round trip for each split. |
| Office structural admission | OPUS-006 | Decide whether read-only structural inspection may detect formula caches, hidden content, clipping and notes/comments. It must not become a second text extractor. Freeze the selected release and refusal rules. |
| Actual web/tool scope | OPUS-007 | Distinguish maintained routes, legacy-only callers and absent routes. Preserve the all-source policy decision, but do not claim nonexistent wiring or introduce a fetcher without authority. |

The table abbreviates `INGEST-R1-` before each source ID. Exact evidence, severities, proposed tests and limitations remain in the seat reports. The shared storage theme is High in Astra; legacy convention/store binding is High in Opus. The controller confirms the cited direct-store/cache and embedding-role hazards from current source; they were not executed as runtime regressions.

One source detail is qualified: Opus calls the large-file raw path a 2,048-character chunker. Current `LargeFileProcessorConfig` describes target tokens and its semantic chunker estimates tokens using characters. Chat passes a default of 2,048 into that target. This is a separate existing chunker, not proof of an exact 2,048-character window. The ownership/no-double-chunking finding does not depend on that numeric wording.

## Decisions and recommended bounds before a revision

Keep the settled decisions: PDF/DOCX/XLSX/PPTX, all-source `document`/512 defaults, `document`/`recursive`/`fixed` overrides, illustrative-only Qwen4B, `certifi>=2026.10.19`, and fresh disposable test stores without migration, reset or cleanup.

The following are recommendations for a future bounded revision, not approvals or edits made by this reconciliation:

1. Apply the new embedding convention only with recorded store identity. Refuse unbound stores in the new pipeline and require a separately selected fresh test store. Do not add legacy re-embedding or inspect/delete existing stores.
2. Require verified capacity/dimensions before a guarded embedding operation; define model-catalog and legacy-constructor resolution and exact refusal scope. A model switch remains outside this review.
3. Permit bounded read-only Office admission checks, with Docling remaining the sole supplier of document text. Stop if the selected release cannot satisfy the promised coverage.
4. Clarify web/automatic-tool scope using the source inventory. A shared capability tested on supplied web text is distinct from a maintained fetching-to-storage route. Adding a route or treating it as future work needs an explicit scope decision; absent wiring earns no integration credit.

Technical ownership can then be corrected without extracting the whole runtime or reopening accepted MEMQ/verified MAINT. No technical proposal content has been changed here.

## Advisories worth retaining

Validate provider vector indices as well as vector count/shape; document reserved option tokens and literal descriptions; define asynchronous conversion and admission behavior; restrict detected formats and archive expansion; characterize serving batch limits; disclose malformed `--lines` truncation and define `/read` override behavior. Gate A needs an explicit bounded installation/download/asset envelope. The named roster is retained; reduced provider diversity is a limitation, not a reason to substitute a model.

Opus's Office/tokenizer observations use upstream `main`, not a pinned release. They identify design hazards for the selected-release readiness work. Its batch-limit advisory is knowledge-based, not reproduced. No current-release or performance claim is inferred.

## Conduct qualification and evidence limits

Opus discloses two read-only Git invocations without an explicit `GIT_OPTIONAL_LOCKS=0`, despite the request requiring that setting on all Git/child processes. Its general environment statement does not establish inherited zero for those two invocations. The controller therefore does **not** certify full command-discipline conformance for that seat. Its reported CHANGES_REQUESTED outcome, score and technical findings are preserved as qualified review evidence; they are not converted into a clean formal execution claim. No replacement review or cleanup was launched. The nested gitdir directory mtime change has no established attribution; protected identity checks passed and no contained-file drift was reported.

Sol/Astra report no conduct deviation. Reviewers independently executed administrative/integrity checks and inspected source; public-source verification is identified in their reports. No product suites, builds, installs, dependency resolution, OCR/conversion, model/provider inference or user-store operations ran in this council. Historical root Ruff534, collection conflict7196, seven legacy formatting failures and approved MAINT oracle failures remain reported failed/unwaived background, not newly reproduced product results.

Raw Sol/Astra report copies are byte-identical. Opus's readable copy removes trailing line whitespace; [the raw compressed report](opus-report.raw.md.gz) preserves exact original bytes. Hashes and all 16 per-seat criterion outcomes are in `reconciliation.json`.

## Current gate

Review the reconciled INGEST round1 findings and authorize a bounded document-only revision; resolve storage/cache ownership, embedding identity/capacity, Office audit and actual route scope before any new council, gate A or construction. MAINT human UAT/acceptance remain separate.

All council tasks are terminal. No further council, gate A, product implementation, model selection, acceptance, store reset, push or PR action follows automatically. The proposal remains design-only with `execution_phase: planning` and `validation_state: changes_requested`.
