# REM-CMD-INGEST-001 independent design/source-feasibility review

Outcome: **CHANGES_REQUESTED**. Coverage **9.1/10**; overall **8.8/10**. Two mandatory findings. No optional finding is required to explain the verdict.

Reviewer: gpt-6.1-sol, high effort. Compatibility cycle pass 1/4, global round 6. Fresh review context; no implementation participation, parent reasoning, current peer verdicts, old raw reports, delegation or repair. Review date: 2026-11-10 America/New_York (frozen authority recorded November 11 UTC). This pass counts against the cap. No reissue launched.

Repository `/Users/chuckrussell/Dev/gendev/agent-framework`; branch `feature/cmd-ingest-001`; candidate `8d25d53ac944ace99e3ae430364075b0c1200ff6`; amendment base `91ac63bad5e46eceddd252d5b7727f7a1d3c623a`. Shared-checkout exception used exactly as requested; private output root is this report's directory. No alternate checkout.

This is design readiness, not implementation conformance. Missing unapproved code is not a finding. No acceptance, construction, Gate A, MAINT acceptance or delivery follows.

## Evidence notation and review sequence

Paths below are relative to the repository. `REM` means `docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md`; `ANN` means `docs/planning/active/command-refactor/embedding-compatibility-contract.md`; `TD` means `docs/planning/active/command-refactor/proposals/tools-document-adoption.md`. Source prefixes `Memory`, `Chat`, `Runtime`, `LLM`, `Core`, `Agent`, `CLI`, `Tools` mean `packages/friday-<name>/src/friday_<name>/`. Citations with section names identify current normative text, not historical verdicts.

Verified request and helper hashes before opening the request; inspected all three supplied Python helpers. Ran opening integrity before substantive review. Reviewed the explicit technical/status amendment diff first (`amendment.diff`, 90,396 bytes); excluded whole authority diff. Then reviewed current REM, ANN, TD, scoped authority/policies, configuration and direct/transitive sources. Sanitized extractor output exactly equals frozen controls. The correction map supplies requirement IDs only; its closure labels were not accepted as evidence.

Delta assessment: the new annex substantially improves startup logging, MCP classification, raw-client admission, acknowledgement/count truthfulness, synchronous graph behavior, profile persistence, CLI origin, dimensions and headless dependency obligations. REM's new narrow rows generally match these changes. Two unresolved compatibility/scope issues remain below. Status changes consistently retain planning/in_review and design_only; no earlier verdict is carried forward. Historical dates/scores in ordinary packet text were context only.

## Mandatory findings

### SOL-R6-M01 — High: proposed FC-03 exception removes public operations and cascades into Reorganizer

Evidence: ANN:155-166 forbids BackupManager live create/restore for bound namespaces, while the primary REM already refuses legacy-unbound live operations. Thus selecting a fresh qualified B or N namespace cannot make this API operate. Current `Memory/maintenance/backup.py:25-63,166-238` exposes file-copy backup as a public API; `Memory/maintenance/__init__.py` exports it. This is distinct from module CLI restore being disabled. `Memory/maintenance/reorganizer.py:148-151,178-180` exposes the manager and calls create_backup in `cleanup` at 898-900 and default backup-first `reorganize` at 1116-1164. The effect therefore extends beyond a direct old backup call. ANN's exception list at 37-44 does not itself establish user authorization to retire those successful public flows. The frozen current authorization is document correction/review; the fresh-store choice permits coherent new destinations, not unrelated public-API retirement.

Violation: REM “Existing pool and subsystem compatibility” requires operational consumers under an admitted compatible namespace; ANN:13-28 requires successful B/N. Declaring refusal an exception cannot prove the user's compatibility premise. The proposed v2 replacement is a different API and does not show the existing public BackupManager/Reorganizer call remains operable.

Required narrow correction: reconcile this exact proposed exception with maintainer authority before claiming compatibility. Either specify a bounded compatible public-call disposition with an explicit narrow scope and unchanged backup safeguards, or record an explicit maintainer waiver identifying BackupManager create/restore, module backup, and affected backup-first Reorganizer operations and the operator remedy. Do not silently add a general backup bridge, disable backup_first, bypass admission, or reactivate disabled CLI restore.

Future proof: admitted baseline and replacement namespace through the actual public API and affected Reorganizer entry points must succeed if retained; same-space/different-space artifact and incarnation controls refuse before copying or touching the sidecar. If explicitly waived instead, freeze the exact affected positive exclusions and public diagnostics; v2 positives remain separate proof. No backup operation was executed here.

### SOL-R6-M02 — Medium: real Agent background-extraction status seam is outside the allowlist

Evidence: `Agent/base.py:494-520` stores the turn, launches `_safe_extract_context`, then emits `turn_archived`; its wrapper awaits `extract_context(async_execution=True)`. `Memory/context/assembler.py:398-428` returns silently without an extractor and otherwise launches a second, unretained `asyncio.create_task(self._extractor.extract(...))`, returning after emitting extraction_triggered. The outer Agent wrapper cannot observe that inner task's later refusal. `Memory/context/extractor.py:452-459` currently returns an error dictionary on exception, also ignored by the assembler. Changing the extractor to propagate typed errors alone leaves an unobserved task exception; returning structured error alone leaves an ignored result.

ANN:200-205 requires observable failed/retryable background status and FC-13 requires actual archive/background witnesses. REM's exact implementation table allows extractor/controller changes and indirect tests, but omits context/assembler.py (and any Agent source status adaptation); it explicitly forbids inferred edits outside its allowlist. This is a concrete discovered seam, not a request for a new scheduler or engine. Logging from the extractor may expose an error, but the design has not specified how the actual public caller retains failed/retryable completion status across the nested task boundary.

Required narrow correction: define ownership and observation of the existing background task/result and add the minimum named source seam to the allowlist, or demonstrate a precise existing allowed seam satisfying the required caller status without changing public signatures. Preserve nonblocking execution, cancellation, extraction selection and unrelated degradation. Do not build a queue, scheduler, transaction framework or automatic retry system.

Future proof: invoke real Runtime Agent archive with its actual ContextAssembler, inject a delayed typed identity/overflow/storage refusal after extract_context returns, await the owned task completion, and assert observable failed/retryable status with no extraction-completed/acknowledged success. Include no-extractor/unavailable behavior, successful B/N extraction and cancellation. Run representative installed normal and -O witnesses. An extractor-only test or an immediate mocked error cannot close this seam.

## Independent consumer/disposition and B/N/R matrix

B means existing qualified binding with capability fields omitted; N means explicit replacement in fresh coherent state; R means refusal before prohibited effects. Every retained embedding consumer needs both different-dimension N and same-dimension/different-space/preparation N, including smaller capacity. These are future required witnesses, not executed results. A row marked sufficient means design-level sufficiency subject to Gate A and final signature freeze. Namespace admission includes vector/graph/configured WAL/log/recovery associations, not only collection metadata.

| Consumer and source evidence | Actual route / disposition | B and N positive obligation | R / narrow scope assessment |
|---|---|---|---|
| LLM embeddings.py:249-326; model_library.py | Direct shared provider, batching/cache/resilience | Existing query/doc signatures, service options and qualified counter work | Preflight final input; complete indices/cardinality/dimension/finite validation, bound cache; REM E sufficient |
| Core interfaces/llm.py:113-125; interfaces/memory.py | Public protocols and precomputed query boundary | Retain embedding calls, extend vector envelope narrowly | No bare-vector bypass; actual downstream controller/adapters listed; REM allowlist sufficient |
| Core profiles.py:58-84; interfaces/transcript.py | Lazy Memory factories / existing cross-package edge | Factory forwards identity/open intent for four profiles | No new neutral backend dependency; transcript interface unchanged |
| Memory adapters/vector.py:57-109 | Persistent or client-injected Chroma front | Store/query correct roles and envelopes | Admission before client/get-or-create; no alternate root; sufficient |
| Memory adapters/simple_vector.py:73-154 | In-memory front | Qualified in-memory add/query | Identity bound before comparisons; no dimension-only acceptance |
| Memory retrieval/collection_manager.py:115-149,559,617,667 | Three lifecycle stores plus MCP staging | Short/long/decayed collections share intended space; profile-specific isolation | Admission and role/envelope propagation covers add, promotion/reactivation and precomputed queries |
| Memory controller/memory_controller.py:499-524,1568-1642 | Maintained semantic gather, graph and query reuse | Full mixed vector/graph recall, not fallback-only | Typed errors survive gather/priming/graph catch; ANN FC-08 sufficient |
| Memory retrieval/graph_scorer.py:330-409 | Maintained synchronous scoring | Compatible cached edge/node vectors contribute; absent vector remains zero | Unknown/foreign existing vector aborts; no backfill; sufficient |
| Same graph_scorer.py:221-315 | Public-unwired async fallback | Direct API positive with guarded document fallback | No maintained-wiring credit; document role corrected, sufficient |
| Memory context/extractor.py:171-212,342-459,578 | Conversation extraction; separate LLM and embeddings | Extract graph edges/insights/summaries then recall using actual bindings | Local guard/error edits allowed; actual background caller incomplete: M02 |
| Memory context/extraction_filter.py:32-66; Chat template:71 | Resourceful configured rejection log | First-use fresh creation before log open; admitted independent log roots retained | No mkdir/FileHandler in old/refused vector root; stale/unknown ownership stops; FC-01 sufficient |
| Memory context/assembler.py:398-428; Agent/base.py:494-520 | Maintained nested background task | Runtime Agent archive→extraction positive | Missing exact status seam/scope: M02 |
| Memory context/consolidator.py:162-219,358-367 | Public-unwired consolidation | Stored successful batches acknowledged | Failed/mixed batch retryability, no unconditional acknowledgement; FC-06 explicit and scoped |
| Chat adapters.py; runtime.py compaction | Maintained conversation/session compaction | Preserve unsplit text and selected service | Overflow/failure remains explicit; no document rechunking |
| Memory lifecycle/promotion.py:423-470,569; Tools memory/lifecycle.py:27-57 | Maintained lifecycle plus public tool | Successful promotion/demotion/reactivation counts after mutation; dry-run counts preserved | False returns/exceptions visible in ordinary execute text and structured results; FC-07 sufficient |
| Memory maintenance/pipeline.py:446-553,951,1031; Chat reorganization/mutation.py:158-166 | Maintained MAINT, real embedding probe | Same namespace, graph-only empty fresh REEMBED, selected maintenance service | Admission before any probe; identity expected dimension; 8192 cap in mutation.py:196-200; FC-11 sufficient |
| Memory maintenance/pruner.py:105-114; fact_checker.py:131-140 | Public direct clients and stored-vector analysis | Admitted comparison/read and normal algorithms | Exact normalized root, no probing/fallthrough, typed refusal preserved |
| Memory maintenance/synthesizer.py:174-193,707-737 | Public legacy synthesis / implicit embedder risk | Valid injected qualified model stores correct document-role vectors | Missing/failed model cannot omit vectors and trigger Chroma default; FC-05 sufficient |
| Memory maintenance/reorganizer.py:139-180,775 | Public helper access and graph embedding/backfill operations | Existing qualified APIs/roles without new automatic backfill | Direct helper admission sufficient except backup-first transitive loss M01 |
| Memory maintenance/analyzer.py:103,136-146,206 | Public raw SQLite/graph analyzer | Store-only live analysis offline provider, exact layout | Read-only SQLite, no creation/journal; no success-empty adaptation; FC-04 sufficient |
| Memory maintenance/backup.py:166-238; __main__.py:348-374 | Public physical-copy backup / module backup | No positive B/N under proposal | M01: explicit proposed retirement, not compatibility proof; offline artifact inspection retained |
| Memory maintenance/__main__.py | Legacy restore/non-dry-run mutation commands disabled | Admitted read/analyze/dry-run only | Do not mistake disabled CLI mutation for all public classes being inactive |
| Memory maintenance/recovery.py:412-458; mutation.py:594 | Maintained v2 participant/direct clients | Identity-bearing same-incarnation snapshot, restore and rollback | Strict v1 offline only; no sidecar overwrite/rebind; REM versioned handoff sufficient |
| Chat reorganization/contracts.py, artifacts.py, coordinator.py | Aggregate Memory2/Transcript1 recovery | Exact participant/aggregate reparse and rollback | Closed 1/2 dispatch; unchanged path fingerprint vs new participant digest; scoped sufficient |
| Memory ingestion/mcp.py:38-189; Chat turns/processor.py:690-719 | Active opt-in structured exact snapshot | Single immutable snapshot, stage/publish/discard and transcript receipt | Byte and token ceilings, oversized vs explicit other error, no split or false prepared; FC-02 sufficient |
| Memory ingestion/tool_ingester.py:103; ingestion/large_file_processor.py:257 | Public callable generic ingestion; no maintained automatic caller | Inject common entry, raw shared-plan chunks and unsplit derived summaries | Full preflight, opt-in, identity/destination-aware cache; no automatic wiring |
| Tools filesystem/smart_read.py; Memory large_file_processor.py | Public injected small/large/force/cache storage | Text under INGEST; four-format adoption under TD; same exact common plan | Context-only windows separate; derived overflow refuses; no missing-entry silent storage success |
| Memory ingestion/pipeline.py:42-145; SemanticChunker API | Public-unwired preprocessing | Legacy callable preprocessing retained | Does not establish accepted common plan or split it again; FC-13 sufficient |
| Chat commands/files.py, registry.py; Tools readers/factory.py | Maintained file commands / separate public reader adoption | Genuine formats, raw-tail parser; factory selection/pagination under TD | Zero memory on extraction refusal; text/web unchanged; TD-01..10 sufficient |
| Runtime di.py:196-242,246-295; Core profiles.py | FULL/VECTOR_ONLY persistent; EPHEMERAL/TESTING in-memory | All four profiles, independently isolated kernels and lifecycle stores | No persistent CollectionManager behind ephemeral front; transcript independently controlled; FC-09 sufficient |
| CLI container.py:63-73,109-127; Runtime config.py:1245-1302,1486 | Compatibility delegation and defaults/env origin | Explicit default literal vs omitted fallback preserved | Typed sentinel/origin handoff before merge; no new public knob; FC-10 sufficient |
| Agent tools/builtins.py:97-209; tools/registry.py | Controller-mediated recall/store_fact | Public success text on actual successful operation | Propagated controller errors adapt to explicit tool failure, no successful empty result |
| Memory multi_agent/controller.py:95,145; coordinator.py:159-194; journal.py | Shared physical memory, authorization visibility partitions | Shared fact/insight proposal succeeds under existing visibility | Exceptions mark failed/partial journal; no new transaction promise, FC-13 tests required |
| Chat commands/memory_queries.py:74-202; Tools memory/inspection.py | MEMQ and public inspection | Admitted stats/records/list-ingested offline provider | Deferred unavailable explicit, no initialized client or false empty; shared controller readiness seam |
| Tools memory/maintenance.py; lifecycle migration.py; Chat migration/reset stubs | Public compatibility/inactive paths | Retain actual disposition; no inactive-route integration credit | Existing guarded adapters cannot be bypassed; no reset/migration activation |
| Core context interfaces; Memory context assembly/passage routing/tool recommendation | Transitive or LLM-only work | Nonsemantic/history/tool registration stays available | No blanket document/provider prerequisite; background status exception M02 |
| Telemetry helpers/llm.py:335-449,669-723; Transcript stores/sqlite.py:1090-1155 | Observability and extraction metadata | Existing success/error semantics; Transcript1 unchanged | Zero-attempt errors enough; no telemetry rewrite or blanket semantic change |
| Commands source; MCP manager; Speech, Sandbox, Finance, Moltbook, Optimization | Unchanged/transitive or unrelated | Imports/registry/minimal profiles; optimization query-generation is not vector execution | Independent source/AST searches find no extra direct embedding client; dynamic configured tool imports need installed registry proof |
| main.py; scripts administrative entrypoints | Minimal print / admin tooling | No embedding dependency | No runtime rewrite; admin scripts exercised only as requested |

Discovery evidence: `consumer-search.txt` records direct embedding/client search across every maintained package source. `transitive-files.txt` records wider memory/vector/embedding references; `package-ast-inventory.json` parses all package Python sources and records relevant imports. This independent inventory includes packages not named in source pins. Search/AST evidence is discovery, not runtime or plugin completeness proof. TUI contains no Python source here. Dynamic runtime imports remain bounded by configured supported registry witnesses. No claim that grepping alone proves semantic closure.

## B01–B08 configuration matrix

All rows require omission of new optional fields plus qualification from exact served identity; placeholders/aliases are not immutable evidence. All qualification statuses are **future/unmeasured**. Unknown qualification hard-stops Gate A, never silently excludes B. Common N requires different dimensions, same-dimension new preparation/space, smaller capacity and independent namespaces. Common R includes alias swap, missing counter/assets, overflow, bad results and stale/unbound binding.

| ID | Source binding and expected B | N / R and qualification control | Assessment |
|---|---|---|---|
| B01 | Chat adapters.py:1735-1745 selects pool default; packaged templates config:59-71,233 | Divergent legacy hint remains ignored with warning; actual service asserted; placeholder revisions qualified | Sufficient, ANN:48-87 |
| B02 | Chat adapters.py:1749-1758 nonpool model/default text-embedding-3-small, endpoint/key fallback | Qualified hosted/local identity without changing defaults; no model swap to satisfy guard | Sufficient; hosted alias impossibility stops Gate A |
| B03 | Chat config.py nonpool compatibility loader; adapters.py same nonpool seam | Sanitized fixture only; absent revision resolved by reviewed deployment record | Sufficient requirement; actual qualification pending |
| B04 | Runtime di.py:196-242,349-367 default plus explicit extraction service | Separate extraction LLM preserved; compatible distinct service names pass; mixed space refuses | Sufficient |
| B05 | Runtime config.py:870-904; di.py:218-233 legacy service creation | Model/endpoint/key/batch/resilience not silently replaced by catalog | Sufficient |
| B06 | CLI container.py:63-73,109-127 Runtime forwarding | Explicit constructor/env default literal vs actual fallback; retain origin before forwarding | Sufficient design; typed internal handoff must be proved |
| B07 | Chat packaged maintenance.embedding and reorganization/mutation.py | Inline nonpool maintenance endpoint/model retained; sharing namespace requires same space | Sufficient |
| B08 | Memory maintenance/models.py embedding config; synthesizer.py:707-737; Core EmbeddingModel | Injected qualified service remains operable; missing service cannot trigger Chroma embedder | Sufficient for embedding; backup exception separately fails |

Independent namespaces may legitimately use different services/spaces. Same namespace requires compatible identity even if dimensions match; service names/timeouts are not identity. Runtime profile matrix is four rows, not simply persistent vs ephemeral: FULL persistent graph+vectors; VECTOR_ONLY persistent vectors/NullGraph; EPHEMERAL isolated in-memory vectors/NullGraph; TESTING same persistence isolation with its testing semantics. Lifecycle collections must match each front-store choice. Explicit transcript persistence is separately isolated in no-persistent-Memory tests (ANN:211-223).

## All 32 criterion outcomes

PASS below means sufficient proposed design/proof scope, not executed product behavior. GAP is a mandatory design gap; no missing implementation is scored as failure.

| Criterion | Outcome | Independent source/document basis |
|---|---|---|
| EC-01 | PASS | Frozen controls, iteration authorization, AGENTS and REM:28-36; integrity pins pass |
| EC-02 | GAP | Independent package source/AST inventory above discovers assembler nested-task seam outside allowlist: M02 |
| EC-03 | PASS | Chat adapters:1735-1758; Runtime di:196-242; CLI container:109-127; ANN B01–B08/FC-10 |
| EC-04 | GAP | Core llm:113-125 and Memory controller/query envelope specified; background status downstream scope omitted M02 |
| EC-05 | PASS | ANN:64-78 hard qualification stop; packaged placeholder revisions do not become supported aliases by assertion |
| EC-06 | PASS | LLM embeddings:249-326, REM E final-input counting/results; Memory owns store admission |
| EC-07 | PASS | Memory graph_scorer:221-409 and controller:1568-1642; ANN FC-08 distinguishes sync/async and absent/foreign vectors |
| EC-08 | GAP | Extractor:342-459, Runtime di:349-367; selection preserved, actual background result boundary M02 |
| EC-09 | GAP | Pipeline:446-553, mutation:196-200, recovery:412; most scope sufficient, public backup/Reorganizer operation conflict M01 |
| EC-10 | PASS | CollectionManager:559/617/667, promotion:423-470, consolidator:196-198; ANN FC-06/07 plus REM raw/derived boundaries |
| EC-11 | GAP | Whole package inventory, four Runtime profiles/CLI checked; Agent nested task remains M02; unrelated packages unaffected provisionally |
| EC-12 | PASS | ANN:19-35; REM Durable store identity and fresh-store admission; dimension alone never identity, no deletion/migration |
| EC-13 | PASS | Runtime extraction service and multi_agent coordinator shared memory; ANN:32-35 independent physical vs visibility namespaces |
| EC-14 | GAP | REM E effective-limit/index/finite validation sufficient; end-to-end background observability M02 still incomplete |
| EC-15 | GAP | DI-18/21/22/27–34 plus ANN named nodes and normal/-O witnesses strong; retained public backup positives impossible M01 |
| EC-16 | GAP | REM exact implementation table explicitly limits source edits; assembler seam requires narrow reconciliation M02 |
| EC-17 | PASS | REM A/B and TD dependency/security/certifi/local assets/format contracts retained; no current feasibility assertion |
| EC-18 | PASS | Current controls/status coherent, full matrices and honest scores here; previous verdicts not correctness evidence |
| FC-01 | PASS | Extractor:210-212/filter:44-55 vs ANN:126-139; deferral plus admitted configured log ownership and first-use test |
| FC-02 | PASS | MCP ingester:130-189, Chat processor:690-719 vs ANN:141-153; single snapshot, overflow/ownership explicit |
| FC-03 | GAP | BackupManager:166-238/Reorganizer:1162-1164 vs ANN:155-166; M01 compatibility exception lacks explicit waiver |
| FC-04 | PASS | Analyzer:136-146 raw writable SQLite/root probing; ANN:168-175 requires exact root/read-only/offline provider |
| FC-05 | PASS | Synthesizer:707-737 optional embedder; ANN:177-182 forbids missing-vector add/default embedder while preserving injected positive |
| FC-06 | PASS | Consolidator:180-198 unconditionally acknowledges; ANN:184-191 explicitly fixes success/mixed-failure acknowledgement in allowed file |
| FC-07 | PASS | Promotion:423-470 counts before mutation; Tools lifecycle:27-57 errors in data; ANN:193-198 covers false return/text/partial counts |
| FC-08 | GAP | Controller gather/graph catches explicitly covered; ANN:200-209 background status still lacks actual assembler seam M02 |
| FC-09 | PASS | Runtime di:249-295 and CollectionManager:137-149 demonstrate front/lifecycle mismatch; ANN:211-223 scopes complete four-profile correction |
| FC-10 | PASS | Actual Chat default and CLI forwarding verified; ANN:225-232 plus baseline table has explicit-origin and ignored hint tests |
| FC-11 | PASS | Pipeline:523-553 probes; mutation:196-200 ceiling; ANN:234-243 requires admission-first and identity dimension for empty stores |
| FC-12 | PASS | Memory pyproject existing tiktoken/LLM and Runtime/CLI/Agent edges; ANN:245-254 narrow extra/minimal installs, no Docling |
| FC-13 | GAP | Agent base→assembler actual nested task missing narrow scope M02; multiagent journal, MEMQ and preprocessing otherwise explicitly covered |
| FC-14 | PASS | Graph/scoring and maintenance thresholds retained; ANN:266-273 separates operational B/N from later real model relevance/false-duplicate UAT |

## Original requirement disposition

These judgments concern the requirement text and current sources, not old reviewers' conclusions. No old raw report was read.

| Original mandatory ID(s) / theme | Independent disposition |
|---|---|
| OPUS-M1 / INGEST-EC-01 | Design addressed by FC-01; first-use/log ownership required, not executed |
| OPUS-M2 / INGEST-EC-02 | Design addressed by FC-02; actual active snapshot rather than unwired generic route |
| SOL-R5-M01, OPUS-M3 / INGEST-EC-03 | Safety refusal specified, compatibility not closed: M01 |
| SOL-R5-M02, OPUS-M3 / INGEST-EC-04 | Design addressed by FC-04; read-only SQLite plus normalized layout admission |
| OPUS-M3 / INGEST-EC-05 | Design addressed by FC-05; no implicit default embedder |
| SOL-R5-M03, ASTRA-R5-001 / INGEST-EC-06 | Design addressed by FC-06; success/mixed batch acknowledgement scoped |
| ASTRA-R5-002 / INGEST-EC-07 | Design addressed by FC-07; mutation returns and public text required |
| OPUS-M4 / INGEST-EC-08 | Sync graph/recall addressed; background completion portion incomplete M02 |
| OPUS-M5 / INGEST-EC-09 | Design addressed by FC-09; four complete profile/collection witnesses |
| OPUS-A1 | Actual Chat default/hint behavior preserved in FC-10, source adapters:1740-1743 |
| OPUS-A3 | B01–B08 attestation/pinned lifetime/per-operation alias identity and hard Gate-A stop specified |
| OPUS-A4 | FC-11 orders admission before all real provider probes |
| OPUS-A5 | CLI origin before default forwarding explicitly scoped |
| SOL-R5-A02, OPUS-A6 | Indirect Agent/multiagent/MCP coverage strengthened; archive status seam still M02 |
| ASTRA-R5-A02, OPUS-A8 | Empty collection dimension from identity and 8192 ceiling explicit |
| OPUS-A10 | Narrow embedding-limits extra + Memory dependency inheritance defined |
| OPUS-A7 | Store-only MEMQ/inspection offline inference defined; no empty-success disguise |
| OPUS-A2 | Quality/relevance evaluation separately required on selected real replacement |
| OPUS-A11 | Legacy preprocessing retained without second storage chunking/integration credit |

## Verification, limits and isolation audit

Reproduced five exact required checks, all through supplied wrapper; every exit **0**:

1. `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` — 36 tasks passed (`board.log`).
2. `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check` — current (`dashboard.log`).
3. `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py` — 1004 Markdown files (`docs.log`).
4. `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py` — 18 pyprojects (`metadata.log`).
5. `git diff --check 91ac63bad5e46eceddd252d5b7727f7a1d3c623a..8d25d53ac944ace99e3ae430364075b0c1200ff6` — clean (`whitespace.log`).

Opening/closing exact helper invocation: `python3 -B INPUTS/read_only_command.py OWN -- python3 -B INPUTS/check_integrity.py INPUTS/review-request.json`, outputs `start-integrity.json` and `end-integrity.json`, both exit 0/PASS with no failures. Logical index is measured by helper before status: `7ff069ba5dddc00af444d34fdb1a2dfaa74fde90e3f1a45aa6bd92b2e8fcd087`. HEAD/branch/status, 17,673 protected entries and six preserved metadata records match at both boundaries. Helper pins raw authority bytes without displaying historical authority. No private state evidence read by reviewer.

Verified SHA256:

- request `72218c26f912bf58c5d7231f79aff9a7156ed0d82bb557d25b2195b7a9a7aa41`
- integrity helper `6ef846532b6caab0c136b50dc9bde1da1816e72742eef6e0522c4e37a36fe9ca`
- command wrapper `cb0669f81efd0098c104d7b96342fcd614255021ea2bfa49cbbb6af7c2fea248`
- extractor `a9fd727a2d9715e5b6759034c4bb92160993bd6d0b23efedcea6211f978e4b81`
- controls `b78f12e948b0e941f9387da478226588bc0dcffec02411bf1132ce4a30d8bf90`

Exact controls-copy byte comparison true; static extractor reads current selected fields only. Git diff and every admin/Git child were wrapped with GIT_OPTIONAL_LOCKS=0 and reviewer-owned UV/XDG/TMP caches. Static cat/rg/Python AST/pathlib reads and report/hash writes are exempt, not violations. Category audit: no repository/input writes, no broad authority/historical report searches, no model calls, installs/resolution, product imports/tests/builds, stores, dirty YAML reads, reset/migration/cleanup, nested agents or external messages. A few discovery commands named nonexistent guessed source filenames and returned ordinary path errors; corrected by actual source lookup, no execution or isolation consequence. Searches enumerate maintained packages, not personal state. Source text can be parsed without importing it; AST parse was the only package-wide Python processing.

Inspected evidence: current source and proposed documents, policies and sanitized current controls. Reproduced evidence: hashes, integrity, static inventory and exact five admin checks. Future evidence: exact dependency/model/counter/Office feasibility; real guarded store implementation, normal/-O installed lanes, negative mutation controls and selected model quality/UAT. No actual provider, model, installed runtime, recovery or conversion proof was executed. Existing root Ruff/collection/formatting/MAINT oracle debt is retained failed/unwaived background; these admin checks imply no whole-repository-green result. No official web lookup was needed; linked upstream claims are proposed readiness inputs, not independently measured facts in this report.

## Scores

Coverage rubric (independent): all-framework direct/transitive consumer coverage **3.6/4.0** (nested background ownership seam incomplete); baseline/replacement positive coverage **2.6/3.0** (backup/public caller positives removed); negative identity/overflow/failure effects **1.9/2.0** (background status seam); headless/minimal/nonembedding **1.0/1.0**. Total **9.1/10**.

Overall rubric (independent): framework inventory **1.8/2.0**; operational configuration/API compatibility **2.4/3.0** (public backup exception and transitive impact); model replacement/namespace safety **2.4/2.5**; bounded proof/reporting **1.7/2.0** (actual background witness/scope gap); scope/authority **0.5/0.5**. Total **8.8/10**. Strong guard architecture does not override an operational compatibility gap. Both scores fall below the user's 9.5 gate. The controller should retain CHANGES_REQUESTED; only this pass's review is complete.
