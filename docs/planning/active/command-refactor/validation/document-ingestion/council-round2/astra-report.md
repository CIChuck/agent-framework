# ASTRA independent design review — round 2

Outcome: **CHANGES_REQUESTED**. Independent advisory score: **9.0/10**. One mandatory finding and one advisory. This is a document/design gate, not implementation conformance.

Candidate: `2956b861de75fcf7ebf463c82f5f470cf6fa7b40`, branch `feature/cmd-ingest-001`, workdir `/Users/chuckrussell/Dev/gendev/agent-framework`. Correction base: `4f9cb13a7a868ec28305a6fe6445007cd3727532`. Aggregate technical comparison: `c36e7ee51a9328918b9bb97712aa7f1d4a850d19..2956b861de75fcf7ebf463c82f5f470cf6fa7b40`.

Request SHA256: `3a113826ce9b458ce21aa17298ed1ce5c7a096eb93f930353f82070ac6865455`. Helper SHA256: `6e1ec704678475fa6dbd45301c94a824e217a177cc8c83e05ee05b6f606278c3`. Both independently verified before reading the request or executing the helper. The helper was also inspected before execution. All authority/document/source pins in the request passed at both boundaries.

Reviewer: ASTRA, gpt-6-astra, high effort, 2026-11-10. Fresh task context; I did not author this candidate and received no builder transcript/private reasoning or current-round peer reports. Correction brief finding requirements were used as scope, not proof. Historical score/status sentences appeared in permitted current-status diffs and were disregarded. No prior peer report was opened, no nested delegation occurred. General harness guidance was present; no memory files or previous rollout reports were consulted.

Authority: explicit request and document-only iteration authorization; AGENTS.md; repository-engineering-policy.md; development-task-lifecycle.md; independent-validation-policy.md; council and independent-code-validator skills; pinned scope/discussion/format/security records. The named two-OpenAI/one-Anthropic roster and shared-checkout read-only exception supersede generic skill defaults. Review does not grant gate-A activation, construction, acceptance, delivery, or a changed MAINT verdict.

## Rubric

| Dimension | Score | Reason |
| --- | ---: | --- |
| Scope, authority, boundedness | 1.5/1.5 | Settled decisions and distinct proposal/readiness/construction gates are explicit. |
| Shared architecture and integration | 1.8/2.0 | Shared headless entry and source/derived separation are clear; direct maintenance clients remain incompletely reconciled. |
| Format extraction and coverage | 2.0/2.0 | Four-format contract is strict, with explicit audit/mapping refusal and selected-release stop conditions. |
| Chunking, embedding, data safety | 2.3/3.0 | Strong token, role, identity and full-batch contracts; snapshot/restore identity gap is material. |
| Verification, reproducibility, reporting | 1.4/1.5 | Strong future genuine-fixture and mutation evidence, but identity recovery coverage is missing. |
| Total | **9.0/10** | Threshold did not influence the verdict or score. |

## Findings

1. **INGEST-R2-ASTRA-001 — mandatory, high: reconcile authoritative embedding identity with maintenance snapshot/restore and direct clients.**

   Requirements: IR-R02, IR-R03, IR-10, IR-14 and IR-16. REM section E lines 701–731 requires the root sidecar to be the single authority, checks before client I/O, and identity validation on every vector read/write including maintenance. REM lines 796–798 name allowed maintenance/store seams, while lines 815–823 exclude recovery and require scope reconciliation if integration cannot fit. Those rules do not currently compose with the existing recovery boundary.

   Source evidence: `packages/friday-memory/src/friday_memory/maintenance/recovery.py:410` constructs a PersistentClient directly. `create_snapshot` at 866–945 exports Chroma logical data and graph data; it has no root embedding-space binding. `recovery_models.py:217` carries only schema/strategy/collections in ChromaLogicalSnapshot; `MemorySnapshotManifest` at 289–300 binds layout and store sources but not the new embedding identity. `_restore_vector_snapshot` at 1500–1513 opens the destination directly, deletes its collections and repopulates them. `restore_snapshot` at 1550–1570 invokes this path. These are maintained paths: Chat `reorganization/coordinator.py:1445` calls snapshot and `:1540` calls restore. Separately, `maintenance/pruner.py:105–175` opens a raw client and compares stored vectors; the reorganizer constructs it at `reorganizer.py:153`. Updating ChromaVectorStore alone cannot guard these calls.

   Risk/inference: a vector-only snapshot cannot independently establish which embedding space it belongs to. A restore may reconstruct vectors beneath an unrelated surviving ready sidecar, or reconstruct a namespace without its authoritative binding. Layout/hash integrity does not prove embedding identity. Even a same-space rollback needs an explicit contract proving that the binding remains coherent. The proposal's broad maintenance check requirement and simultaneous recovery exclusion leave that decision to an implementer without an authorized seam. This is a design contradiction, not a demand for implementation proof today.

   Narrow mitigation: add a bounded identity-preservation/admission contract for snapshot, verify and restore (including snapshot provenance, destination matching, missing/legacy identity refusal, and before-client-I/O checks). Name the minimal recovery/model paths necessary, retaining existing orchestration and rollback semantics. Alternatively, explicitly refuse affected maintenance operations on the new namespace before any effect until separately authorized compatibility work is complete; explain the product limitation and avoid claiming preserved maintenance availability. Classify direct raw-client readers such as the pruner and place their admission at a documented owning boundary. No migration, recovery redesign, re-embedding, or broad maintenance refactor is requested.

   Future verification impact: same-space snapshot/restore positive; same-dimension different-space negative; absent/malformed/pending binding; identity-free historical snapshot; no client/provider/write on mismatch; preserved binding and vector identity through automatic rollback. Include canonical direct participant and maintained Chat entry paths. A short document correction is sufficient at this gate; runtime execution belongs to the future approved directive.

2. **INGEST-R2-ASTRA-002 — advisory: make completed-storage cache receipts destination-specific.**

   REM lines 141–156 and 743–746, companion cache contract and DI-23 now correctly reject mtime-only/context-only and stale-policy cache hits. The enumerated cache identity includes embedding space but does not explicitly distinguish two independent fresh roots or collections using the same embedding space. Current `smart_read.py:286–318` returns early from caches, while `:595–625` uses path-level deduplication and a stored flag.

   Clarify that successful storage evidence is scoped to a destination namespace/collection (and a suitable incarnation or validated record receipt), rather than treating embedding-space equality as evidence that the target contains the source. Add a same-model fresh-destination/collection-switch case, and a missing-stored-record case if record existence is part of the chosen receipt contract. This is advisory because the proposed current admission checks and successful-storage requirement can reasonably be implemented to cover it; make that interpretation explicit at signature freeze. No new cache cleanup or generic transaction layer is needed.

## Correction-first review and disposition

I inspected the technical correction diff first, then the entire current REM and companion, retained authority decisions, source seams and a technical-path-filtered aggregate comparison. Current status diffs were inspected separately; authority.json was limited to permitted current fields. No unfiltered aggregate/history diff was read.

| Correction theme | Independent disposition |
| --- | --- |
| CR-01 / IR-R01 | Resolved at design level: Core injected entry, public Memory factory, INGEST ownership of existing smart_read storage/cache, and exact raw-versus-derived semantics are explicit. Advisory 002 sharpens destination receipts. |
| CR-02 / IR-R02 | Substantially improved but incomplete: fresh-only binding, same-dimension mismatch and envelopes are defined; finding 001 identifies the uncovered snapshot/direct-client seam. |
| CR-03 / IR-R03 | Query/document role inventory repaired for named embedding callers, including vector adapter, synthesizer and graph fallback. Direct-client maintenance identity admission still needs finding 001. |
| CR-04 / IR-R04 | Resolved in proposal: optional parsing, mandatory verified operation capability, non-pool refusal, read-only read availability. |
| CR-05 / IR-R05 | Resolved: deterministic Memory text adapter is an explicit implementation; missing Docling affects converted formats only. |
| CR-06 / IR-R06 | Resolved: offline synchronous counting, manifest asset root, server cross-check, worker quiescence/admission and stop-on-unbounded behavior. |
| CR-07 / IR-R07 | Resolved at this gate: non-text audit and mapping, cached-formula distinction and unknown-warning refusal; exact release feasibility remains intentionally pending. |
| CR-08 / IR-R08 | Resolved: active/public-not-wired/absent routes and capability-only tests are explicit. Maintained source search found no ToolOutputIngester references in Chat/Agent/Tools/Runtime source. |

Advisory dispositions in the correction brief were independently checked against the current text: direct query role is named; response indices must form a complete unique set; scoped flags/terminator/read refusal are specified; worker cancellation makes no hard-kill claim; wrong-format/ZIP expansion refuses; deployed capacity is not assumed from evaluation batch size; legacy malformed text lines are characterized with truncation; gate-A hosts/assets/budgets need separate activation; and roster diversity is stated truthfully. These textual dispositions are not runtime proof.

## All 24 criterion results

PASS means adequate proposed design for this document-only gate, not implemented behavior. References to REM are to `docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md`; TD refers to the companion's acceptance table.

| Criterion | Result | Requirement/source evidence and limits |
| --- | --- | --- |
| IR-01 | PASS | REM 3–40, iteration authorization and current authority; exact SHA/branch/pins verified; board design_only; distinct MAINT acceptance and future master PR base. |
| IR-02 | PASS | REM 277–327, DI-04/07/09. `commands/files.py:44–62,122–132` confirms placeholder defect; proposed extraction precedes storage and excludes diagnostic/empty success. |
| IR-03 | PASS | REM 308–320,339–340, DI-01/02/03. Legacy `pdf_reader.py:139–175` embeds page errors; `docx_reader.py:107–115` separates paragraphs/tables. Proposed repair explicitly addresses both. |
| IR-04 | PASS | REM 341,344–355,375–391, DI-13/25. `xlsx_reader.py:190–225` shows data_only/active-sheet/range behavior. Required cache/visibility audit and no-clipping rule are coherent; release proof pending. |
| IR-05 | PASS | REM 342,357–391, DI-14/25; companion TD-09. Native content/notes, hidden units, original indices and visual omissions are bounded; unknown mapping stops readiness. |
| IR-06 | PASS | REM 402–437,498–513, DI-05/06; registry parser source and `files.py:135–151`. Untouched raw tail, default-handler ownership, opaque literal suffix and API54 exclusion are explicit. |
| IR-07 | PASS | REM 471–560, DI-16/17. Independent CLI/YAML precedence, final 512 budget, structure boundaries and overlap freeze; character settings are not aliases. |
| IR-08 | PASS | REM 94–157,543–551; Core/Memory/Tools/LLM package dependencies inspected. Core protocol plus Memory factory avoids a new Tools/Memory cycle and forbids duplicate splitting. |
| IR-09 | PASS | REM 562–636,662–681; strict `model_library.py:105–109,312–321` requires deliberate schema/resolver changes. Exact served artifact/counter/capacity required; Qwen illustrative only. |
| IR-10 | FAIL | REM 638–746 has strong preparation, cardinality/index/dimension/full-batch checks. Finding 001: recovery can bypass the promised durable identity boundary. |
| IR-11 | PASS | REM 159–275,589–593; current package metadata and required post-install version/origin/negative controls. Exact release/counter compatibility remains an explicit gate-A obligation. |
| IR-12 | PASS | REM 219–235,294–391,756–775; DI-11/25/26 and companion sandbox-first requirement. Thread is not represented as OS sandbox; inability to bound work stops. |
| IR-13 | PASS | REM route table and source/derived/cache contract, DI-19/23; `smart_read.py:260–367,595–625`, `large_file_processor.py:841–955`, `tool_ingester.py:258–303`; companion TD-02/05/10. Advisory 002. |
| IR-14 | FAIL | DI-01..26 and TD-01..10 are otherwise substantive, including call-phase mutants, genuine fixtures, installed/optimized/Chroma evidence and baseline failures. Missing identity snapshot/restore lane follows finding 001. |
| IR-15 | PASS | REM 701–754, current board/handoff and immutable integrity checks. No hidden reset/migration; named roster and future master base. Stale top-level roster link still names round1 but identical roster is separately pinned for round2; no substantive ambiguity. |
| IR-16 | FAIL | Gate-A experiment boundaries are coherent for dependencies, format audit, counters and resource limits. Finding 001 is a known cross-contract omission needing a bounded decision before the final directive, not an experiment to leave implicit. |
| IR-R01 | PASS | REM 103–157; companion sequence/TD-10; actual small/large/cache source confirms the repaired ownership requirement. |
| IR-R02 | FAIL | REM 693–746 resolves fresh binding/envelopes/legacy refusal, but recovery/direct clients remain outside that authority; finding 001. |
| IR-R03 | FAIL | REM 648–658,796–804 includes named role handoffs and pool/non-pool guards; finding 001 leaves actual maintenance vector access incompletely classified. No claim that all callers were dynamically exercised. |
| IR-R04 | PASS | REM 572–593, DI-18/22. Old catalog entries parse, selected missing capabilities refuse at use, non-pool paths cannot guess, /read remains meaningful. |
| IR-R05 | PASS | REM 517–551, DI-08/16/17. Memory-owned text blocks and exact counter work without conversion extra; no fallback after document converter failure. |
| IR-R06 | PASS | REM 228–235,589–593,662–681,756–775; DI-24/26. Synchronous local counter and off-loop execution, admission retention and late-result discard are explicit. |
| IR-R07 | PASS | REM 375–391, DI-13/14/25. Structural inspectors supply facts only; formula blanks/warnings/mapping refuse safely. Selected-release evidence is intentionally future. |
| IR-R08 | PASS | REM 119–157 and DI-19; companion route matrix/TD-10; bounded maintained-caller search exit1 confirms no named class reference in four maintained source roots. No absent fetch route is activated. |

## Executed checks, commands, and exits

All commands ran in the requested workdir through `OWN_SCRATCH/run` after its bootstrap. `OWN_SCRATCH` is this report's containing directory. `INPUTS` is `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-design-r2-p8slwm9l/inputs`. These abbreviations identify exact absolute paths, not historical output destinations.

| Exact child argv (wrapper prepended) | Exit | Actual result |
| --- | ---: | --- |
| `python3 -B INPUTS/check_integrity.py INPUTS/review-request.json` | 0, twice | start-integrity.json and end-integrity.json both PASS, failures empty |
| `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` | 0 | 36 tasks passed |
| `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check` | 0 | dashboard current |
| `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py` | 0 | 982 Markdown files passed |
| `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py` | 0 | 18 pyproject files passed |
| `git diff --check 4f9cb13a7a868ec28305a6fe6445007cd3727532..2956b861de75fcf7ebf463c82f5f470cf6fa7b40` | 0 | no whitespace errors |
| `rg -n ToolOutputIngester packages/friday-chat/src packages/friday-agent/src packages/friday-tools/src packages/friday-runtime/src` | 1 | no matches; expected search result, not a failed test |

`commands.log` records literal argv, exported Git/Python environment and exits for every wrapped command, including the exact filtered diff and source-search path lists. Source/policy reads used Python pathlib with bounded line ranges; administrative Python snippets were not product execution. Their stdin bodies remain in the review tool transcript; the command log records argv rather than duplicating stdin. The bootstrap exported both required variables before invoking Python, verified hashes, created only the private scratch and wrapper, and read the verified request; exit0, no Git call. All remaining shell invocations called that same wrapper. No builder receipt/script was replayed; the specifically authorized immutable integrity helper and named repository administration checks were the only executed repository/supplied programs.

Helper child Git sequence, with inherited environment: `git ls-files -s -z` FIRST; then `git rev-parse HEAD`, `git branch --show-current`, `git status --porcelain=v1 --untracked-files=all`, `git diff --cached --name-only`. Both runs exited0. Logical digest is `587b8099a2c6a1be5adc8bfe021bbc9cd6c6ebdcbf54a78d543d57007125ebe3` at both boundaries. Exact dirty state matched, no staged diff. All 17,561 protected entries and six preserved metadata records matched. Additional recovery/pruner source hashes were recorded in additional-source-pins.json and rechecked unchanged.

## Isolation and limits

The wrapper exports `GIT_OPTIONAL_LOCKS=0`, `PYTHONDONTWRITEBYTECODE=1`, `UV_OFFLINE=1`, `UV_NO_SYNC=1`; UV_CACHE_DIR, XDG_CACHE_HOME and TMPDIR are beneath this newly created scratch. It uses the supplied argv without resetting environment and logs the relevant values before execution. All administrative UV invocations additionally pass offline/frozen/no-sync/no-python-downloads. No installs, dependency resolution, product imports/tests/builds, inference, model download, application/store open, mutation, cleanup, commits or repairs were performed. Protected store bytes were hashed solely by the authorized integrity helper; they were not opened through an application/database API. No repository or supplied-scratch writes were observed. No output/cache path points at supplied inputs or earlier review scratch.

This is bounded evidence, not a system-wide syscall audit. The shared checkout is intentionally dirty, not detached/clean. Some large tool outputs were truncated; the critical correction/current-design/authority sections were read in narrower calls, and findings rely on displayed source evidence. The immutable request pins, start/end helper reports, private administrative outputs and command log provide reproducible boundaries. I make no claim to have executed every source path or validated all runtime behaviors merely because its bytes are pinned.

No runtime tests were required or executed. Historical root Ruff 534, root test_display collection conflict7196, seven legacy format failures and MAINT Chat1413/15 remain reported, failed/unwaived background; I did not reproduce or reclassify them. Future DI/TD checks were inspected as proposed obligations, not passed receipts. Existing placeholder slicing and unguarded embeddings are baseline gaps the proposal intends to repair, not candidate code regressions.

## Official-reference inspection

Official [Docling chunking documentation](https://docling-project.github.io/docling/concepts/chunking/) supports native structural chunking with token-aware refinement and contextualization; [offline configuration](https://docling-project.github.io/docling/usage/advanced_options/) exposes prefetched artifact paths. These support the architecture but do not prove the chosen release or Office mapping. Official Excel/PowerPoint backend pages were consulted as current upstream references only; no installed-release claim follows.

The [Nomic card](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) distinguishes search document/query task prefixes. The [Qwen4B card](https://huggingface.co/Qwen/Qwen3-Embedding-4B) gives 32K context and up to2560 dimensions; it does not verify the user's served capacity. [LM Studio tokenization documentation](https://lmstudio.ai/docs/python/tokenization) is reference material, not a locally verified offline counter. The [Certifi release page](https://pypi.org/project/certifi/2026.10.19/) and [official advisory](https://github.com/certifi/python-certifi/security/advisories/GHSA-6q48-6c7w-9gw2) were fetched; the mandatory floor remains the maintainer's2026.10.19 requirement. No artifact was downloaded or hashed by this review.

## Next gate

Reconcile mandatory finding001 in the proposed design and future exact allowlist/tests, then obtain a fresh review of the changed frozen candidate. Pending gate-A experiments are legitimate and must retain their explicit stop conditions. No construction, readiness execution, MAINT acceptance or delivery authority is granted by this report.
