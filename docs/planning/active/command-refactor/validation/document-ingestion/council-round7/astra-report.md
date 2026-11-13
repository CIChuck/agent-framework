# REM-CMD-INGEST-001 independent design/source review

**CHANGES_REQUESTED — coverage 9.1/10; overall 9.0/10.**

Reviewer: gpt-6-astra, high effort. Compatibility cycle pass 2/4, global round 7. One mandatory finding; no construction, Gate-A, model replacement, reset, MAINT acceptance or delivery authority. Two further passes maximum remain for the controller; this seat neither repairs nor reissues a review.

Candidate `f1916747ad7d03e451f2b57dc00542faa6095d7c`, branch `feature/cmd-ingest-001`, repository `/Users/chuckrussell/Dev/gendev/agent-framework`. Correction delta from `8d25d53ac944ace99e3ae430364075b0c1200ff6` inspected first; aggregate base `91ac63bad5e46eceddd252d5b7727f7a1d3c623a`. Only the request's explicit technical/status diff paths were used. Current complete REM, annex and companion govern; old reports supply no correctness evidence.

Fresh review context: no builder reasoning/transcript, current peer verdicts, raw historical council reports, nested agents or implementation. Shared-checkout read-only exception used. Repository AGENTS, engineering/lifecycle/independent-validation policies, council and independent-code-validator skills were consulted. The user prohibition on nested agents controls the council skill. Procedural memory was searched, but no historical technical verdict was used. No personal YAML/store/export content was inspected. Raw authority was only processed by the verified extractor and integrity helper, never opened/grepped for evidence.

## Mandatory finding

### ASTRA-R7-001 — medium, FC-02 pending cleanup contradicts the retained public retry contract

Affected design: `embedding-compatibility-contract.md`, FC-02 (paragraph beginning “Retain current cancellation, readback and cleanup”), and its final-directive exception/proof mapping. Paths in this report are relative to the repository unless stated otherwise.

Evidence: `packages/friday-chat/src/friday_chat/memory_mcp.py:151` reads the existing receipt; lines 155–231 prepare snapshots, append/read back the receipt, publish, and on cancellation re-raise. It does **not** invoke discard on ordinary failure or cancellation. The public discard capability exists at `packages/friday-chat/src/friday_chat/adapters.py:342`; the lower store's `discard_mcp_snapshot` at `packages/friday-memory/src/friday_memory/retrieval/collection_manager.py:518` deletes an exactly matching pending record. Availability of that method is not existing publication cleanup wiring.

More decisively, `packages/friday-chat/tests_chat/test_mcp_memory.py:123` (`test_public_retry_after_partial_outcome_preserves_owned_id`) includes `false_append`: it requires one retained pending record even when no transcript entry exists, then at lines 190–204 requires retry to use the original memory correlation ID with **no additional embedding write**. `test_partial_persistence_cannot_publish_uncorrelated_memory` at line 460 likewise requires pending retention after append/readback/cancellation/publication failure. These assertions were inspected, not executed.

FC-02 currently says to retain cleanup of newly owned, uncommitted snapshots while preserving existing/durably receipted pending records. A freshly staged snapshot after false append is newly owned and uncommitted, yet the actual preserved contract retains it for retry. Deleting it would produce a new UUID and another embedding write; `MCPMemoryIngester.prepare` uses a random ID only when no matching previous record exists (`ingestion/mcp.py`, identifier construction and matching lookup). The text therefore leaves two incompatible construction outcomes and misidentifies existing behavior.

Required narrow fix: reconcile FC-02 with the actual public pending-retention/retry contract. Prefer explicitly retaining owned pending snapshots after failed/ambiguous append, readback failure and cancellation, with exact retry ownership and existing no-publication rules. Describe discard as an explicit existing capability with no newly automatic cleanup wiring. If new cleanup is intended, enumerate exactly which state can be deleted, how ownership and absence of a durable receipt are established, the intentional ID/re-embedding delta, and the exact approved assertion exceptions; do not describe that as retained behavior. No receipt schema, automatic retry, whole-turn atomicity or new transaction is needed.

Future witnesses: through real `persist_mcp_interaction`, actual adapter/collection manager and actual turn persistence, stage a first snapshot then fail append before commit; retry the same turn/call and assert the approved ID/write-count/pending outcome. Add mixed ordinary/MCP calls where a later preparation fails, and cancellation/ambiguous append/readback failure where durable ownership cannot be disproved. Existing/receipted/foreign records must never be deleted. Assert no successful skipped receipt on typed/storage failure, bounded observer reason, public persistence error, and later successful publication. Run source and normal/-O installed call-phase assertions; lower-level discard or immediate mocked preparation alone is insufficient. This is a document ambiguity, not a demand to implement unapproved product code now.

## Scores

Coverage rubric: framework direct/transitive inventory 3.6/4; baseline/replacement positive proof 2.8/3; negative identity/overflow/failure-effect coverage 1.8/2; headless/minimal/nonembedding coverage 0.9/1 = **9.1**.

Overall rubric: consumer inventory 1.8/2; operational configuration/API compatibility 2.6/3; model replacement/namespace safety 2.3/2.5; bounded proof/reporting 1.8/2; scope/authority 0.5/0.5 = **9.0**.

The deductions reflect the concrete pending-state ambiguity and remaining exact implementation-signature/member-map/qualification work, not absent unapproved implementation. No score was raised to satisfy the 9.5 gate. The specification is substantially improved, but this seat cannot return VERIFIED.

## Independent consumer and B/N/R disposition matrix

B = unchanged supported baseline configuration, optional fields omitted, qualified identity and admitted store. N = explicitly selected replacement, including changed dimension, same dimension/different artifact/preparation and smaller capacity, in coherent fresh state. R = identity/readiness/overflow/result/ownership refusal before the prohibited effects. Every positive below is a **future required witness**, not a runtime result of this review. Source names identify independently discovered seams; the accompanying AST/text artifacts make the discovery reproducible.

| Consumer / source evidence | Classification and narrow disposition | B/N positive | R / retained boundary |
|---|---|---|---|
| LLM `embeddings.py:249,287`, model_library resolver | Shared request/result/preparation/cache owner; retain query/doc APIs and options | Same selected services; document/query once-only preparation; valid complete indexed results/cache hits | Whole input batch preflight, bad indices/nonfinite/dimensions, smaller serving cap, cache identity drift; no guessed counters |
| Core `interfaces/llm.py`, `interfaces/memory.py`, `profiles.py` | Neutral typed handoff; factory delegates existing adapters | Typed identity-bearing query/vector and open intent across four profiles | Bare/foreign vectors; no new backend imports in neutral contracts |
| Memory `adapters/vector.py:84,86,109`, `simple_vector.py:109,154,168` | Direct backend and comparison boundaries | Matching store add/search/get with correct query role and dimensions | Refuse before client/provider/write; identity is stronger than equal dimension |
| `retrieval/collection_manager.py:115,381,421,559,617,667` | Lifecycle stores, gather/catch seam, transfer re-embedding | Short/long/decayed add/query/get and promotion/reactivation remain usable | Typed get_all failure cannot become partial empty success; preserve unrelated degraded reads |
| `controller/memory_controller.py:500,1590` | Query embed, priming, author reads and optional scorer delegation | Actual Chat/Runtime semantic vector recall plus unscored graph output | Guard actual vector/query/read paths, no unused graph-vector preflight |
| `retrieval/graph_scorer.py:260,357`; controller optional argument | Both sync and async are public injectable, not maintained wiring | Explicit injected matching comparisons, absent vector behavior, document fallback | Same-dimension foreign/invalid stored vector fails; no zero-score substitution or new wiring |
| `context/extractor.py:578,650–711`; Chat `adapters.py:1148` | Maintained edge/entity/insight/summary persistence and acknowledgement | Stable output-slot IDs/upserts; successful extraction and explicit retry | Typed edge refusal cannot produce vectorless edge; batch refusal cannot enter per-item fallback or completed acknowledgement |
| `context/assembler.py:398–430`; Agent `base.py:498–522`; Runtime `di.py:135` | Actual inner task is distinct from outer archive scheduling | Delayed successful result, telemetry-off status/wait, shutdown drain | Delayed post-return failure, cancellation, no-extractor skip; no automatic retry/scheduler |
| `context/consolidator.py:198,358,367`; maintenance compactor | Consolidator public-unwired; compaction separately maintained | Successful stored summary precedes source acknowledgement | Mixed/failed summary batch remains retryable; structured records unsplit |
| `context/extraction_filter.py:26,33` and filter emissions | Currently global logger; proposed owned sink is necessary | First admitted use including log under vector; independent/shared qualified targets | Two owners, close/reconfigure/failed setup/idempotence; old-root metadata unchanged; inert Chat setting stays inert |
| `ingestion/mcp.py`; Chat `memory_mcp.py:127`; `turns/processor.py:688` | Maintained opt-in exact single snapshot and public receipt/observer | Exact snapshot, one correlation, verified append, pending then publication | Oversized distinct from typed/storage/ownership failure; **ASTRA-R7-001** pending/discard ambiguity must close |
| `maintenance/backup.py:155,244,274`; Reorganizer `227,265,1162`; module `__main__.py:351` | Public physical backup family retained, module restore disabled | Actual create/verify/same-incarnation restore and backup_first, old return/class compatibility | Bound receipt/member/digest validation even verify_first=False; no marker overwrite, unsafe-root recursion/symlink/clone; quiescent disposable stores |
| `maintenance/analyzer.py:87,124` | Direct graph and SQLite opener | Admitted provider-offline analysis, exact resolved roots | Read-only Chroma AND transcript SQLite; no fallback namespace or false empty success |
| `maintenance/synthesizer.py:707`; pruner/fact_checker; reorganizer | Legacy injected callable shapes and direct openers remain public | Qualified embed_query/embed/callable via once-only shared document adapter | No missing-vector collection.add default embedder; no callable identity guessing; disabled module mutation stays disabled |
| `maintenance/pipeline.py:523,553,951,1031`; mutation `196` | Maintained provider probes, re-embedding and stored comparisons | Empty fresh graph-only and variable-dimension operation, same-space services | Admission before synthesizer LLM AND embedding probe; 8192 ceiling; independent unused services remain usable |
| `maintenance/recovery.py`, mutation; Chat reorganization coordinator/artifacts | Logical v2 separate from physical BackupManifest | Matching snapshot/verify/rollback with retained live sidecar | Strict v1 offline/v2 active dispatch, mixed versions/incarnation mismatch refuse; unchanged Chat path fingerprint/Transcript-v1 |
| `lifecycle/promotion.py:423,466`; Tools memory/lifecycle | Indirect store transfers and user-visible result | Actual mutation counts, dry-run prospective counts, public execute text | False return/exception visible in text and data, no unchanged-success counter |
| Tools `memory/maintenance.py`, `memory/inspection.py` | Injectable public wrappers, not automatic activation | Backup-first maintenance, confirmed reset retaining binding, offline graph/vector listings | Whole target admission before clear; truthful errors/partial state; semantic query still requires embedding |
| Tools smart_read `:605`, Memory large_file_processor/tool_ingester | Explicit injected source/derived storage; generic ingester not maintained automatic wiring | Shared raw chunk plan, derived unsplit records, warm destination-specific receipts | No opt-in bypass, stale context/storage cache proof, double splitting, or newly automatic ingestion |
| Tools readers / Chat file handlers | INGEST shared conversion; separate companion factory/smart_read adoption | Four genuine formats; text remains without Docling; provenance for pagination and formula/notes/visibility | Corrupt/partial/unobservable coverage refuses; no fallback text supplier; direct legacy reader APIs retained |
| Runtime `di.py:245–370`, Core profiles, CLI container | Maintained assembly; CLI forwards defaults and loses raw origin today | FULL/VECTOR_ONLY persistent; EPHEMERAL/TESTING incarnation-scoped front and lifecycle data | Same logical names across kernels/different models isolated; no shared-system reset; independent transcript effects |
| Runtime `tool_loading.py:64–100` | Real pkgutil/import catalog, not synthetic registry | Headless counter extra inherited without Docling | Actual optional-absence import control separately labelled; lazy new modules |
| Agent `tools/builtins.py:203`, archive; Memory multi_agent `coordinator.py:159–191` | Transitive Memory callers and authorization partitions | Fact/recall/archive/promote usable with preserved visibility | Honest partial graph/vector failure; no new atomic transaction or model selector |
| Commands memory_queries/session_views; Chat MEMQ adapters | Injected query ports and record/statistics presentation | Provider-offline admitted listing and ordinary help/exit | Explicit unavailable, no false empty or inference initialization |
| Transcript and Core interfaces/transcript | Independent persistence; existing lazy Memory import edge | Existing transcript-v1 and configured persistence behavior | No schema bump or profile-caused transcript toggle |
| Finance, MCP transport, Speech, Sandbox, Moltbook, Optimization, Telemetry, CLI nonmemory | Source discovery found no direct embedding provider/Chroma calls in these packages; transitive Runtime/tool or measurement use remains | Nonembedding imports/LLM/tool/read/exit regressions | No new Docling/counter prerequisite for unrelated operation; dynamic import is future installed proof |
| Lifecycle migration and Chat migration/legacy reorganize compatibility | Inactive/stub/disabled execution classified separately | Admitted callable dry-run retained where supported | No repair, activation, implicit route credit or migration authority |

The backend's installed `chromadb/api/shared_system_client.py` was statically inspected: `_get_identifier_from_settings` returns `ephemeral` for nonpersistent segment/rust clients. FC-09's per-incarnation physical names and owned-only deletion are concrete safeguards; merely using EphemeralClient is insufficient. No backend import or runtime isolation test was run.

## Baseline qualification matrix

| Family | Independent source anchor | Required preserved selection and qualification |
|---|---|---|
| B01 | Chat adapters `build_framework_embedding_service:1735`; packaged config templates | Pool default actually wins; divergent legacy hint remains a no-op with safe warning. Maintenance explicit pool binding remains distinct. |
| B02 | Same builder non-pool branch | Existing model/endpoint/credential fallback and text-embedding-3-small default; immutable serving identity may not qualify. Hard readiness stop, never silent exclusion. |
| B03 | Chat config EmbeddingConfig and builder | Sanitized compatibility alias/endpoint/extraction binding, no invented revision. A complete frozen sanitized fixture remains Gate-A work. |
| B04 | Runtime di `_create_llm_services`, `_create_context_engine` | Pool default Memory plus optional explicit extraction embedding; extraction LLM independent. |
| B05 | Runtime config `EmbeddingServiceConfig:637`, default merge `1585` | Legacy/service/default options unchanged; qualification supplies omitted capabilities. |
| B06 | CLI container FridayConfig and to_runtime_config | Explicit constructor/environment equal to default differs from implicit forwarded fallback; internal origin/sentinel, no new YAML knob. |
| B07 | Chat config MaintenanceConfig.embedding and reorganization mutation providers | Explicit maintenance service/model/endpoint; compatible identity required for shared namespace, no redirect to default. |
| B08 | Memory maintenance models `EmbeddingConfig:351`, MaintenanceConfig `458`; synthesizer `707` | Injected service and all three accepted callable shapes qualify through shared adapter. Missing embedder never means Chroma default. |

For every row B and N require real success; unresolved baseline qualification halts readiness. Replacement matrix crosses changed dimension, same dimension/different space, changed preparation, smaller capacity, independently bound namespaces, same-space differently named services and all four Runtime profiles. Store-only operation can work with inference offline if identity admission is resolved. Model relevance/false-duplicate quality is separately measured under FC-14, with no threshold retuning inferred.

## All 32 criteria

“Supported” below means the current design requirement is source-feasible and has a bounded future proof obligation; it does not mean implementation or installed proof passed. “Gap” identifies the mandatory contradiction above.

| Criterion | Disposition | Evidence and judgment |
|---|---|---|
| EC-01 | Supported | Verified controls, request pins, iteration authorization; design_only/not_granted; opening/closing integrity. |
| EC-02 | Supported with static limits | Independent rg plus AST inventory across explicit package src trees; consumer matrix above includes indirect Agent, multi-agent, Core transcript edge and catalog imports. Dynamic/custom plugin behavior needs installed witnesses. |
| EC-03 | Supported | Chat builder default selection, Runtime config/di and CLI forwarding; REM E and FC-10 preserve actual selection/options. |
| EC-04 | Supported | Core embedding APIs, adapter/query precomputed-vector call sites and collection handoffs; REM narrow Core/Memory extension and explicit downstream allowlist. |
| EC-05 | Supported, qualification future | REM E and B01–B08; actual mutable/default model strings cannot establish immutable identity. Gate A must stop on unknown baseline. |
| EC-06 | Supported | LLM cache/query/doc methods and vector adapter role seam; REM E shared once-only preparation/counter/result/cache ownership. |
| EC-07 | Supported | Package-wide scorer search and controller:1590; neither composition root injects it; FC-08 correctly requires zero maintained graph comparisons. |
| EC-08 | Supported | Extractor actual nested catches, Chat _extract_turns error/requeue, assembler create_task and Runtime shutdown; FC-06 requires delayed status and stable retry. |
| EC-09 | Supported | BackupManager/Reorganizer/module/Tools actual chain; FC-03 retains positive old public calls, strict separate receipt and logical-v2 boundary. |
| EC-10 | Supported | Collection transfer embedding calls, promotion/compaction and large-file storage; REM structured-record exemption and FC-07 preserve unsplit semantics. |
| EC-11 | Gap | Runtime/catalog/nonembedding inventory is explicit, but MCP public failure cleanup description contradicts retained behavior: ASTRA-R7-001. |
| EC-12 | Supported | REM identity/recovery and annex N; store and graph vectors require more than dimension; no personal reset authorized. |
| EC-13 | Supported | Runtime independent pools vs multi-agent visibility metadata; annex physical namespace distinction and same-space names rule. |
| EC-14 | Gap | Shared count/result/index/finite validation and catch requirements are concrete; MCP failure/retry cleanup still needs exact disposition. |
| EC-15 | Supported subject to finding | DI-18/21/22/27–34 and FC integration nodes cover B/N/R normal/-O; no demand for future execution now; MCP witness must be reconciled. |
| EC-16 | Supported | REM exact allowlist names assembler, Runtime drain, Chat memory_mcp and Tools wrappers; discoveries do not authorize broad edits. |
| EC-17 | Supported, feasibility future | REM A/B and companion TD requirements preserve Docling single owner, four formats and Certifi floor; FC-12 counter extra and actual catalog import witness. |
| EC-18 | Gap | Current pins/status coherent; honest fresh evidence/report supplied; pending/discard source contradiction prevents unqualified compatibility conclusion. |
| FC-01 | Supported | Global rejection_logger/FileHandler is actual source hazard; owned sink/lease/reconfigure/failed setup/first use requirements address it without inert-setting activation. |
| FC-02 | Gap | Actual prepare→receipt→publish and turn wrapper inspected; error taxonomy is improved, but retention/cleanup conflicts with current tests, ASTRA-R7-001. |
| FC-03 | Supported | Public signature/return/class retention, backup_first chain, disabled module restore; bound receipts and no-sidecar-copy feasible in bounded helpers. Exact member map remains Gate A. |
| FC-04 | Supported | analyzer transcript SQLite direct opens and root probing inspected; explicit read-only exact-layout admission covers them. |
| FC-05 | Supported | Synthesizer embed_query/embed/callable seam; qualified adapter and once-only document role permit positive compatibility without implicit embedder. |
| FC-06 | Supported | Extractor catches and stable IDs, consolidator mark/storage, assembler actual task, Agent outer wrapper and Runtime close identified separately. |
| FC-07 | Supported | Promotion increments before call and Tools text are real seams; success-only count plus false-return/text obligations address them. |
| FC-08 | Supported | Collection get_all gather-return_exceptions, controller reads and conditional scorer route; preserve unrelated degradation and separate injected capability proof. |
| FC-09 | Supported | Core profiles/Runtime unconditional collection path plus installed shared Chroma system; concrete incarnation names and owned cleanup required. |
| FC-10 | Supported | Chat actual default vs hint and CLI default forwarding; typed origin preservation and eight baseline families explicitly required. |
| FC-11 | Supported | Pipeline real synthesizer and embedding probes plus mutation dimension<=8192; admission first, expected dimension on empty store, no global service disablement. |
| FC-12 | Supported | Runtime actual importlib/pkgutil walk; narrow LLM extra inherited via Memory, no Docling requirement; separate unsupported-package-absence control. |
| FC-13 | Supported subject to FC-02 | Tools direct graph/vector/reset calls, Agent calls and multi-agent partial journal source; public positive/offline/typed-failure tests named; MCP shared finding remains. |
| FC-14 | Supported | Existing vector/scorer thresholds are behavioral inputs; operational proof explicitly separated from later relevance/false-duplicate UAT. |

## Proposed correction and high/medium requirement dispositions

Independent judgment, not carried verdicts: IC-01 public backups, IC-02 owned inner tasks, IC-04 owned logging, IC-05 unscored maintained graph recall and IC-06 extraction catch/acknowledgement are adequately specified at design level. IC-03 real MCP failure mapping is partially specified but remains open under ASTRA-R7-001. Original mandatory themes INGEST-EC-01 and 03–09 have bounded source-backed dispositions as above; INGEST-EC-02 is not closed.

Original high/medium groups: actual default/hint and immutable identity qualification (OPUS-A1/A3), all-provider admission (A4), CLI origin (A5), transitive callers (A6/SOL-R5-A02), dimension/empty-store (A8/ASTRA-R5-A02), headless extras (A10), offline MEMQ (A7), quality separation (A2) and legacy preprocessing (A11) are represented in FC-10–14 and the matrices. These IDs are requirement labels from the current correction map, not peer-verdict evidence.

Pass1 advisory requirement groups A1–A10: ephemeral physical names, named get_all/priming catches, public wrappers/disabled Chat routes, actual catalog imports, callable-shape qualification, LLM probe ordering, current authority, inert logging configuration, hosted-default qualification risk and read-only transcript SQLite all receive explicit proposed contracts. No executed closure is claimed. The non-pool hosted baseline is the highest Gate-A feasibility risk; its inability to qualify must stop readiness, not become a newly unsupported silent exclusion.

Advisory ASTRA-R7-A01: when freezing FC-03's receipt schema, enumerate source-member→artifact-member→restore-target mappings and data-versus-binding members explicitly, including flat versus vector-subdirectory legacy layouts. The current normative requirement already demands this, so it is not another mandatory finding. Public positive quiescent backup/restore and verify_first=False tamper witnesses should make an accidentally broad recursive sidecar copy impossible.

## Verification and limits

Five exact requested admin checks ran through the verified wrapper, all exit 0: board validate (36 tasks); dashboard render --check (current); documentation lifecycle (1008 Markdown files); package metadata (18 pyproject files); aggregate git diff --check (no output). Exact argv/cwd/environment and exits are in command-audit.jsonl. No online resolution/sync/download occurred.

Both opening and closing integrity: PASS, zero failures, 17681 protected entries, exact HEAD/branch/logical index/status and all pins plus six preserved metadata records. Current-controls extractor output equals frozen controls byte-for-byte. The wrapper forces GIT_OPTIONAL_LOCKS=0, PYTHONDONTWRITEBYTECODE=1, offline frozen no-sync uv and private cache/TMPDIR. It was inspected as audit discipline, not treated as an OS sandbox.

Fresh evidence: helper/hash comparison, static source/AST/text discovery, selected current tests, static installed Chroma source, controls comparison, five admin commands and both integrity checks. Inspected tests were never executed. Full aggregate selected diff is retained privately; current normative files were reviewed. Some long tool outputs were truncated, and AST/text inventory is discovery evidence rather than a proof that every dynamically loaded/custom implementation is semantically covered. No dynamic route closure is claimed. Two exploratory reads referenced nonexistent filenames (mutation_models.py/config.py and a core mcp directory), and one zsh mcp glob had no match; subsequent explicit source searches located the relevant mutation/models and publication seams. These are inspection misses, not failed product checks.

Future only: Gate-A package/model/counter/identity qualification, exact signatures/receipt member schema, real provider behavior, dependency installation, actual public B/N/R source and normal/-O installed tests, mutation controls and model-quality UAT. No product imports, tests, builds, provider/store operations or model execution occurred. Static Chroma inspection is not runtime proof. Old root Ruff534, test_display collection conflict7196, legacy formatting and MAINT oracle debt remain failed/unwaived background. No whole-repository-green claim.

All writes were under this fresh private directory: report, request/control copies, source-discovery/AST artifacts, diffs, command audit, check logs and wrapper tmp/cache locations. No cleanup, worktree/checkout, personal-state, repository or supplied-input write was performed. Closing integrity followed the final shared inspection; subsequent work only wrote/read/hashed own scratch. Source metadata/contents remain frozen. SHA256 inventory follows.

Recommended next gate: controller reconciles this pass within the existing four-pass limit and resolves ASTRA-R7-001 in the proposed document scope before a changed candidate receives its next authorized fresh review. This review grants no Gate-A execution or implementation authority.

## Exact evidence hashes and commands

- integrity_helper: `6ef846532b6caab0c136b50dc9bde1da1816e72742eef6e0522c4e37a36fe9ca`
- command_wrapper: `cb0669f81efd0098c104d7b96342fcd614255021ea2bfa49cbbb6af7c2fea248`
- current_controls: `6d63c0062008d8de7ebad06fa5e6bceeea29155cb58efbe3b97934f716f748b8`
- extractor: `a9fd727a2d9715e5b6759034c4bb92160993bd6d0b23efedcea6211f978e4b81`
- request: `d7e045a1e3e0a27417f02253b1d56ab73d516cdc2be528990a0ca42356fc9f6e`
- logical index: `0f185529a0084999a93b6b969b67d0a92d266491a113545f426f967bf94d5a97`

`python3 -B INPUTS/read_only_command.py OWN -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` → exit 0.

`python3 -B INPUTS/read_only_command.py OWN -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check` → exit 0.

`python3 -B INPUTS/read_only_command.py OWN -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py` → exit 0.

`python3 -B INPUTS/read_only_command.py OWN -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py` → exit 0.

`python3 -B INPUTS/read_only_command.py OWN -- git diff --check 91ac63bad5e46eceddd252d5b7727f7a1d3c623a..f1916747ad7d03e451f2b57dc00542faa6095d7c` → exit 0.

INPUTS is `/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-compat-iteration-4col5xog/pass2/inputs`; OWN is this report directory. Integrity argv at both boundaries: `python3 -B INPUTS/read_only_command.py OWN -- python3 -B INPUTS/check_integrity.py INPUTS/review-request.json`, exit 0.

- `aggregate-stat.txt` SHA256 `53cd948d6b7e9cf0e41c5e6adf2bc2f370708554851d6b1a89baacc1c95d9780`
- `aggregate.diff` SHA256 `099d2fdab75135a7b377e95ebff4f2b820e537a1148cc71b905aaa744fe5a611`
- `ast-inventory.json` SHA256 `4da833b180c53afa028b856c072bf8d0158b61b2bebbb289457dfddb935d28c5`
- `board.log` SHA256 `c4d2aec671b8fd5d5a978b1c191b186f6d151f7ace4785fbd74b06c3c5f3fdae`
- `command-audit.jsonl` SHA256 `583ba0d209355d79d055d710fdd043a3bf98b9759c778bb31ab8e57e2e26cbd3`
- `controls-copy.json` SHA256 `6d63c0062008d8de7ebad06fa5e6bceeea29155cb58efbe3b97934f716f748b8`
- `correction.diff` SHA256 `fab1df70824a3dd765a06db0a6e1107c339f773ab8626f0abdc4f6b9f64a8ede`
- `dashboard.log` SHA256 `a28df31135633728c76b88ed1a836e90f2c8046e1d72663c8881937c7693ba33`
- `docs.log` SHA256 `abd78a24f3220167e9c59bd32036a2df1866bec9f4574ff581b9b39eb65863da`
- `end-integrity.json` SHA256 `f62cb573d99acdd8f9f7f597b171400263d074558872aae44460afea95aeb56c`
- `metadata.log` SHA256 `b755228d64e991cad2a40d1ea238ea00e97d8d2fd420a5141fffa00476ed690f`
- `request-copy.json` SHA256 `12734bd544625313c83b717fa289ebfbe3210ab0a5f142c67d1fe67bae1af89c`
- `source-discovery.txt` SHA256 `94b8af4b9dc1caabd23d2137fa51750436d4871032ab774dce1be5ca32b4a63e`
- `start-integrity.json` SHA256 `f62cb573d99acdd8f9f7f597b171400263d074558872aae44460afea95aeb56c`
- `whitespace.log` SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

## Package discovery register

- `packages/friday-agent/src`: 22 Python files parsed; 2 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.
- `packages/friday-chat/src`: 61 Python files parsed; 16 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.
- `packages/friday-cli/src`: 13 Python files parsed; 1 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.
- `packages/friday-commands/src`: 7 Python files parsed; 2 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.
- `packages/friday-core/src`: 23 Python files parsed; 2 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.
- `packages/friday-finance/src`: 12 Python files parsed; 0 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.
- `packages/friday-llm/src`: 21 Python files parsed; 2 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.
- `packages/friday-mcp/src`: 29 Python files parsed; 0 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.
- `packages/friday-memory/src`: 79 Python files parsed; 31 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.
- `packages/friday-moltbook/src`: 15 Python files parsed; 0 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.
- `packages/friday-optimization/src`: 4 Python files parsed; 0 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.
- `packages/friday-runtime/src`: 9 Python files parsed; 2 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.
- `packages/friday-sandbox/src`: 9 Python files parsed; 0 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.
- `packages/friday-speech/src`: 12 Python files parsed; 1 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.
- `packages/friday-telemetry/src`: 26 Python files parsed; 2 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.
- `packages/friday-tools/src`: 87 Python files parsed; 2 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.
- `packages/friday-transcript/src`: 13 Python files parsed; 2 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.
- `packages/friday-tui/src`: 0 Python files parsed; 0 files with matching call names. Detailed caller paths and symbols are in ast-inventory.json.

This inventory includes false positives such as memoryview and virtual_memory; they are not embedding consumers. Regex provider/client/comparison results in source-discovery.txt supplement the call-name AST scan. Neither alone is treated as proof of behavior.
