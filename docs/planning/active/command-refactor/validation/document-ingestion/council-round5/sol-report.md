# Sol round5 independent design/source-feasibility review

**CHANGES_REQUESTED — advisory score 8.6/10.** Three mandatory findings. This is design readiness only; no implementation conformance or runtime assurance.

Reviewer: Sol, gpt-6.1-sol, high effort. One independent read-only pass, no delegation, repairs, peer reports or builder reasoning. Historical scores in current documents were treated solely as status. A generic memory registry search supplied no candidate correctness evidence. All conclusions below come from current frozen documents and static source/test inspection.

Candidate `06f294d779c5bc9ea3016eaffdf8efb349979ce4`, branch `feature/cmd-ingest-001`; base `82c3a05a271c321c18a3967624281a5272c579b9`, amendment base `c28e6f8bba959f10137b8d772a667ec4e59389f5`. Shared root `/Users/chuckrussell/Dev/gendev/agent-framework`. Private root `/private/tmp/rem-ingest-sol-round5-FLryM9`.

Request SHA256 `e463c4e849957eb920e4260c10d408217498f6afb787da474c301a546e33c35c` matched before substantive review. Inspected wrapper SHA256 `cb0669f81efd0098c104d7b96342fcd614255021ea2bfa49cbbb6af7c2fea248` and helper SHA256 `2d383c058aec2af50f4b0c6d6b27909b7b57995755a89f3af6bcb2857eceb38a` matched. Request read in bounded sections, including all criteria/conduct/checks. REM SHA256 `2bbf54c8c987eba9b2b823c9efb6f218c4cd7058d8e0f72694ae8ed04dd12dea` verified by both boundaries. Opening/closing helper PASS, 17,643 protected entries, all six preserved metadata records checked, logical index `948187c7cb810e1721eaf094454ff68b44e4e6b35f65fad0290c6e98437a0ffe`. No shared/input write or unwrapped Git/admin operation occurred. Closing integrity followed the final shared inspection; subsequent work used private scratch only.

## Authority and amendment assessment

Authority: explicit review request; AGENTS.md; repository-engineering, development-task-lifecycle and independent-validation policies; current round5 scope/roster; maintainer fresh-store decision. The council skill was inspected as pinned authority; its controller delegation instructions do not apply to this explicitly single reviewer seat. Current authority controls say proposed/planning/in_review, implementation approval not granted, current revision prior_review_applies=false and new_council_active=true. No acceptance, construction, Gate-A execution, deletion, migration or delivery authority follows this report.

Read current REM/companion and pool amendment before tracing framework source. The amendment appropriately strengthens operational compatibility: REM lines 623–646 allow omitted fields to resolve from qualified artifact-bound readiness and STOP when baseline qualification fails; lines 648–697 retain service/default/profile/API selection and require cross-subsystem proof. It does not silently select Qwen, demand one global model or equate dimensions with space identity. The new preparation/identity/fresh-store exceptions are explicit, rather than disguised as byte-identical compatibility. The all-source policy correctly excludes automatic document splitting of structured memory records.

The broad design is feasible using shared LLM preparation/result guards, Memory namespace admission and thin composition changes. Existing Core EmbeddingModel APIs (interfaces/llm.py:106–135) already distinguish query/documents. LLM model_library.py:105–120,237–247,287–322 shows bounded extension points preserving batch/cache/resilience and target selection. The current implementation is not expected to implement the proposal yet. The gaps below concern omitted public consumers and insufficient declared contract coverage, not missing future implementation or lack of model execution today.

## Mandatory findings

### SOL-R5-M01 — High: public legacy BackupManager remains an identity-blind restore path

Evidence: `packages/friday-memory/src/friday_memory/maintenance/backup.py:137–156` discovers root files and recursively copies vector files; `:158–238` creates a file/checksum manifest; `:273–326` restores by copying into self._memory_dir, with no space/incarnation/current-ready-binding validation. `maintenance/__init__.py:160` exports it. `maintenance/reorganizer.py:148–152,227–238` constructs and exposes it; it is not just an experimental script. Existing tests `tests_memory/test_maintenance/test_backup.py:12–69` exercise this API. The REM's identity-preserving recovery at lines 932–966 and proposed exact paths at lines 1170–1176 cover the newer recovery participant but omit backup.py and its legacy BackupManifest contract.

Risk: a valid checksum says nothing about embedding-space compatibility. A legacy backup at one root layout may omit a root-level sidecar (MEMORY_FILES at backup.py:40–50); recursive vector backups can copy an old sidecar along with vectors. Direct restore can therefore either put old vectors under the current ready identity or replace that identity. A fresh initial namespace does not close this later restore API. This is an affected public consumer of store data even without an embedding call.

Required narrow mitigation: explicitly classify BackupManager and its public/exported and Reorganizer entry points. Give it a bounded guarded-store disposition: delegate bound snapshot/restore to the identity-aware recovery contract or refuse bound/live restore through this legacy API while retaining explicitly offline historical inspection. Preserve old artifact interpretation. Add exact backup.py/model/test paths only for admission/version dispatch/refusal; no backup-engine redesign or migration.

Required proofs: actual public API and Reorganizer backup/restore entries; matching bound same-incarnation positive if supported; same-dimension different-space, different dimension, different incarnation, identity-free manifest and pending/missing/tampered binding negatives before mkdir/copy/write. Verify current sidecar bytes and all destination bytes/metadata unchanged on refusal. Exercise both root-level and vector-subdirectory layouts, including copied-sidecar substitution. These extend DI-27/28/32 and Gate-A trace inventory. EC-02/09/12/16 affected.

### SOL-R5-M02 — Medium: ConsistencyAnalyzer bypasses the specified normalized namespace admission

Evidence: `maintenance/analyzer.py:129–148` probes memory_dir then memory_dir/vector and opens Chroma SQLite directly via sqlite3.connect; `:74–85` separately loads/caches graph data; `:172–186` suppresses schema/read failures into partial/default statistics. It is exported at maintenance/__init__.py:161 and used by Reorganizer at reorganizer.py:152,240–248. Existing public analyzer tests are in tests_memory/test_maintenance/test_analyzer.py. REM lines 917–930 name direct PersistentClient consumers but not this SQLite consumer; exact allowed paths omit analyzer.py.

Risk: the proposed admission rule applies to namespace reads as well as writes, and explicitly forbids probing another namespace after refusal. This reader does not traverse the adapters or new PersistentClient helper. It can inspect the wrong root, combine graph/vector statistics from different layouts or present unadmitted state as a normal analysis. Lack of inference does correctly mean it should not require tokenizer/provider readiness; it does not establish destination identity.

Required narrow mitigation: add an explicit store-only analyzer contract and normalized resolved vector/graph layout plus common identity admission before data access, or an explicitly offline historical inspection surface that cannot count as live guarded maintenance. Record the public direct API disposition, add only analyzer.py and focused analyzer fixture paths as necessary, and preserve analysis algorithms.

Required proofs: matching bound inspection succeeds with unavailable inference and zero tokenizer/provider calls; unbound/mismatched/pending namespace refuses before SQLite/graph open and produces an actionable result; a second valid candidate directory cannot be selected after first-path refusal. No state/metadata changes on refusal. Name the public analyzer test nodes and extend DI-28/29 and Gate-A trace. EC-02/09/11/16 affected.

### SOL-R5-M03 — High: public MemoryConsolidator can erase the signal from new embedding failures

Evidence: `context/consolidator.py:356–368` awaits summary store_insight, catches every Exception and only logs it. `:188–207` then marks all fetched turns consolidated and emits consolidation_completed; the inner swallowed failure never reaches report.errors. The class is maintained/exported (`context/__init__.py:23,47`, root __init__.py:32,209), and ContextAssembler's public set_consolidator/consolidate route (`context/assembler.py:137–139,443–454`) can invoke it. Current Chat/Runtime do not install this class as their ordinary extractor; classify it as public injectable, not active extraction wiring. It has real package tests (tests_memory/test_context/test_consolidator.py:65 onward). REM lines 665–697 and DI-33 require guarded unsplit summaries and typed error propagation, but proposed exact paths do not include context/consolidator.py.

Risk: a qualified replacement with a lower limit, a provenance refusal or invalid provider result can make this public subsystem silently lose its summary while marking source turns processed. A fresh namespace does not remove overflow or typed-error propagation obligations. This existing broad catch becomes directly relevant when the design intentionally adds these failures; treating it as unrelated baseline debt would miss compatibility.

Required narrow mitigation: explicitly inventory this public route separately from MemoryExtractor and InSessionCompactor. Add only narrow guard-error propagation/commit-status handling and focused tests to the allowlist, retaining prompt/batching/order policy. A refused batch must be actionable and cannot be marked consolidated as though summary storage succeeded. No general consolidation redesign is requested.

Required proofs: use a valid parsed summarization response followed by call-phase store refusal for overflow, space/provenance mismatch and invalid vector; assert actionable failure, no completed-success event and no consolidated marking for the refused source batch. Include positive round trip to guarded summary storage/recall using unchanged omitted-field config and both replacement cases, normal/optimized representative installed proof. Do not count setup/import failures. Extend DI-22/33 and Gate-A trace. EC-02/10/11/14/15/16 affected.

## Independent consumer/disposition matrix

Paths below are relative to packages unless otherwise stated. “Covered” means a proposed design contract is adequate at this gate, not runtime success. All source package roots were searched for embedding/cosine/vector constants and store/controller interfaces; maintained scripts/main.py were also searched. Transitive calls were followed, not inferred solely from keyword absence. Search artifacts are embedding-search.txt, calls.txt, transitive-files.txt and fixture-search.txt in this scratch.

| Subsystem/source anchor | Status and dependency | Disposition / required proof |
| --- | --- | --- |
| friday-llm model_library.py:105,237,287 | Active/public catalog resolver; default/profile/credentials/batch/cache/resilience | Covered by E/DI-18/33; omitted fields require qualified readiness, no model switch |
| friday-llm embeddings.py:78,165,191,249,287 | Public pool/non-pool constructors, document batching, query LRU | Covered: preserve signatures/timeout, validate every batch and cache hit, role/identity/counting keys; retain API regression tests |
| friday-core interfaces/llm.py:106 | Shared bare-list embedding APIs | Compatible signatures remain; resolved capability/envelope is additive at store boundary, not a forced embed_* return-type break |
| friday-core interfaces/memory.py:128,profiles.py:56 | Public store/query contract and full/simple factory | Narrow envelope/open-intent extensions declared; tests must preserve callers not supplying precomputed vectors and refuse bare provided vectors |
| Memory vector.py:57,111,159,195 | Persistent/ephemeral raw adapters, add/upsert/query | Covered identity-before-client and query-role correction, all reads/writes and full result preflight |
| Memory simple_vector.py:109,132 | Ephemeral NumPy store, provided query vectors | Covered; dimension/provenance/finite checks also apply here, no hidden 768 requirement |
| Memory collection_manager.py:179,559,617,667 | Multi-collection query, promotion/decay/reactivation re-embedding | Covered by declared path; query envelope passes to all collections, stored text document role |
| Memory controller.py:423,499,1460,1564,1699,1918 | Shared recall query, store and priming; catches/async paths | Covered declared changes must propagate typed guard errors through recall/priming, not empty results |
| Memory models/graph.py:205,267; graph_scorer.py:226,335 | Bare cached node/edge vectors and synchronous/asynchronous cosine | Covered reserved identity + preflight, correct fallback document role; old zero/mismatch scorer tests need exact approved oracle deltas |
| Memory adapters/graph.py:74, null_graph.py | Graph load/update/merge/text operations | Narrow identity properties declared. Graph-only rendering remains provider-free; update/merge must preserve envelopes |
| Memory context/extractor.py:570–592 | Active extraction LLM and optional separate relationship embedder | Covered explicit separation of extraction LLM from embedding binding and typed edge/insight refusal |
| Memory context/consolidator.py:188,356 | Public injectable summary store and consolidated markers | GAP M03; not ordinary Chat/Runtime extractor wiring |
| Memory context/assembler.py:137,443 | Public consolidator injection plus context/recall | Compatible forwarding for success; M03 covers indirect failure. No duplicate token guards needed |
| Memory maintenance/compactor.py:435,462,634 | Active Chat compaction, summaries and promotion | Uses controller; existing result.errors captures failures. Preserve actual Chat error rendering, no new tokenizer here. DI-22/33 covers unsplit summary and typed failure proof |
| Memory lifecycle/promotion.py:313,320,470 | Public promotion service wraps collection manager | Compatible delegation, existing report.errors preserves operation errors; DI-33 must assert no success on guard failure and no structured-record chunking |
| Memory maintenance/pruner.py:114,172 | Direct Chroma and already-stored-vector comparisons | Covered admission before direct client and comparison; no inference requirement merely to compare qualified stored vectors |
| Memory maintenance/synthesizer.py:183,712; pipeline.py:951,1031 | Direct clients and synthesis/re-embedding, currently query-role misuse | Narrow declared role fixes, same namespace compatibility independent of maintenance service name; DI-22/28/33 |
| Memory maintenance/fact_checker.py:140 | Direct client, otherwise LLM-based verification | Covered store admission, retain LLM-only selection and verification logic |
| Memory maintenance/reorganizer.py:148,227,240 | Public orchestration and legacy components | Covered embedding roles; M01/M02 are missing legacy component dispositions; no order redesign |
| Memory maintenance/analyzer.py:129 | Direct SQLite/graph/cache inspection, no new embed | GAP M02; provider-free does not mean namespace-free |
| Memory maintenance/backup.py:137,273 | Public physical backup/restore | GAP M01; distinct from new recovery participant |
| Memory maintenance/recovery.py:412,563; mutation.py:594 | Snapshot/rebuild/query probes/rollback direct clients | Covered v2 space/incarnation binding, exact destination, identity-bearing probes, same-layout restore and no sidecar overwrite |
| Memory maintenance/incremental.py | Graph dedup/orphan/Hebbian work, no direct embed | Compatible through admitted graph/controller; preserve properties and report errors, no independent model configuration |
| Memory ingestion/large_file_processor.py and tool_ingester.py | Public supplied text/tool storage, raw/derived summaries | Explicitly covered; common plan once, unsplit derived guard, no automatic caller activation |
| Memory ingestion/pipeline.py:43,169,278 | Public character-based preprocessing returning text/metadata, no store/provider call | Compatible as standalone legacy preprocessing; not new entry success proof. Any downstream store still guarded; no undocumented ingestion-policy integration claim |
| Memory multi_agent/controller.py:51,69,132 | Runtime-wired optional wrapper, recall/graph facts | Compatible controller delegation, no bare vector or dimensions; namespace visibility names are not independent physical vector spaces |
| Memory multi_agent/coordinator.py:123–193 | Public promotion writes graph then vector/journals | Compatible underlying API; catches report failed, not success on exception. Require guard failure/partial-commit regression and preserve graph/vector semantics; no transaction redesign |
| Runtime di.py:196–258,339–367 | Active pool/default assembly; optional extraction service | Covered lazy capability and public factory, not eager Chroma. Separate compatible service names allowed; mismatched extraction binding refuses before write |
| Runtime kernel.py:109–116 | Boot via DI then registry; agent/workflow creation | Compatible delegation if DI installs deferred memory instead of throwing; DI-29 must exercise real kernel startup and non-memory registry access |
| CLI container.py / profiles.py / session.py | Runtime compatibility delegation and session/context use | Covered re-export and readiness tests; no independent embedding constructor identified |
| Chat config.py:732–760; adapters.py:263–270 | Catalog resolution and embed_text currently aliasing query | Covered omitted fields/deferred capability and explicit role fixes; do not use query role for indexing |
| Chat runtime.py:1407–1528 / app.py / background.py:193–222 | Active composition, commands, background/exit compaction | Covered lazy readiness, useful /read/help/exit, reported maintenance refusal; no silent memoryless chat |
| Chat reorganization/mutation.py:262–301 and artifacts/coordinator/contracts | Distinct maintenance binding and aggregate recovery | Covered exact v2 dispatch/fingerprints and provider binding; v1 remains offline-only |
| Chat memory_mcp.py:160–206 and adapters.py:309–340 | MCP immutable transcript/publication capability | Transitive controller publication, no direct embedding/precomputed query path. Preserve its persistence/refusal semantics; no new model config or routing needed |
| friday-agent base.py:493–521 and tools/builtins.py:89,145 | Active archive/extraction and injected recall/store tools | Compatible controller/context APIs; background extraction failure currently logged. Future DI-33 should include agent caller witness; no vector envelope exposed here |
| friday-tools filesystem/smart_read.py | Public optional injected storage/cache; Chat wiring lacks Memory | Explicitly covered existing text paths; companion owns document routing. Missing injection must refuse requested storage |
| friday-tools memory/inspection.py:123–145,maintenance.py:35,lifecycle.py | Public legacy wrappers using controller/Reorganizer | Admission flows from adapter/manager for compatible APIs; legacy backup/analyzer wrapper effects fall under M01/M02. No direct vector-generation code; retain legacy API limitations rather than claiming maintained Chat activation |
| friday-tools readers/factory and direct readers | Extraction-only consumers, no embed | Companion TD-01..10 covers adapters/pagination/extras; INGEST alone cannot claim adoption |
| friday-telemetry helpers/safe_llm.py, models/llm.py:266, helpers/memory.py | Observes request dimensions/errors; no vector manufacture/store | Compatible unchanged through existing request/result telemetry; do not add embedding asset requirements to telemetry or LLM-only services |
| friday-transcript interfaces/stores | Transcript/MCP persistence and compacted/consolidated markers | Compatible data contracts remain v1; M03 prevents false consolidated updates. New Memory/Chat snapshot types must not rebind transcript classes |
| friday-commands | Pure parser/registry, no embedding dependencies | Covered stdlib-only API54 and scoped parser changes; minimal install stays independent |
| friday-mcp, sandbox, speech, finance, moltbook, optimization | No embedding/store/controller consumer found in source scan; MCP transport schema bytes and pricing context constants are not vector dimensions | Compatible unchanged at their package APIs; shared LLM-only clients retain schema/optional-dependency independence. No local code/config changes justified |
| main.py and maintained scripts | main prints a smoke message; no direct embedding/vector consumer found by script scan | Compatible unchanged; governance scripts are read-only checks here |
| Memory lifecycle/migration.py:423; Chat migration stub | Legacy inactive route with fixed 768 dummy query | Explicit REM inactive disposition is adequate. No integration credit or general migration repair; guarded direct use refuses rather than dimension pad |

## Two-scenario compatibility matrix

B = unchanged maintained catalog/pool AND maintained non-pool configurations, new YAML fields omitted; namespace is explicitly admitted/fresh where preparation changes. R = explicitly selected replacement in a fresh coherent namespace, testing both changed dimensions and same dimensions with changed artifact/preparation. No row grants permission to reset old data.

| Boundary | B expectation/proof | R expectation/proof | Design assessment |
| --- | --- | --- | --- |
| Config/default/service selection | Preserve service/profile/endpoint/credentials/batch/cache/resilience, qualify actual baseline readiness | Same selection mechanism with explicit replacement; independent namespaces may use different models | Adequate DI-18/33; no parse-only pass |
| Missing optional metadata | Qualified exact-artifact readiness supplies values; no user YAML rewrite | Explicit dimensions/cap match actual new served artifact | Missing qualification STOP, never fallback |
| API callers | Existing embed_query/documents signatures and return shapes preserved | Same APIs, actual variable dimension accepted/validated | Adequate shared design; envelope only store/query boundary |
| Preparation/role/counting | Verified current artifact, once-only prefix, local exact counter | New query/document convention, effective loaded/batch capacity | DI-18/22/24/33, future real serving parity required |
| Graph/extraction/recall | Retain extraction LLM and compatible explicit embedding bindings | New edges/nodes/insights and shared query have same space; changed-dimension and equal-dimension negative controls | Adequate declared graph paths; no zero-score fallback for unknown provenance |
| Stored-vector comparison | Compatible pruning/clustering with provider offline allowed | Fresh vectors all one identity, no legacy comparison | Adequate named direct clients; analyzer gap M02 |
| Summary/lifecycle/compaction | Preserve record semantics, guard unsplit inputs, actionable overflow | Smaller-capacity replacement refuses safely; no document re-chunking | Public consolidator gap M03; ordinary compactor result.errors must remain visible |
| Namespace/data | Explicit origin, absent vector/graph/configured WAL; exact root sidecar | New coherent vector/graph/WAL/incarnation, associated old files never imported | Strong create/open design; fresh data alone does not close later restore M01 |
| Snapshot/recovery | Bound same incarnation; old v1 only offline | Same-dimension different-space restore refuses before effects | New v2 recovery adequate; BackupManager gap M01 |
| Caches/provided vectors | Role/space/preparation/count identity and valid destination receipts | Different space/preparation/root/incarnation invalidates cache even equal dimension | Adequate DI-21/23/30, no boolean-only storage receipt |
| Non-embedding operations | Config/help/read/tool registration/exit without model/store initialization | Same, even with unavailable new embedding capability | DI-29 adequate, actual Kernel/Chat proof future |
| Public unlisted callers | Multi-agent/agent wrappers generally delegate unchanged | Same underlying contracts; no per-subsystem model rewrite | M01–03 need explicit paths/tests/dispositions |
| Packaging | Default Chat intentionally adds converter extra; bare Tools text remains usable | New counter assets/deps provisioned explicitly, no runtime downloads | Gate-A dependency feasibility remains pending; Commands minimal closure protected |

## EC-01..18 outcomes

PASS means the documented design requirement is adequate, with future named runtime proof still required. GAP means a mandatory design omission above, not a failed runtime experiment.

| Criterion | Outcome | Evidence/limit |
| --- | --- | --- |
| EC-01 | PASS | Exact frozen hashes, explicit read-only single pass and current authority; boundaries PASS |
| EC-02 | GAP | Whole-source inventory identifies BackupManager, SQLite analyzer, public consolidator missing dispositions/paths |
| EC-03 | PASS | REM 648–697, DI-33 operational baseline and no silent rebinding |
| EC-04 | PASS | Existing Core embedding signatures retained; query-envelope changes and actual main callers declared |
| EC-05 | PASS | REM 623–646 baseline qualification STOP, optional syntax and no unguarded lane |
| EC-06 | PASS | LLM owns counting/preparation/result validation; Memory owns admission, graph roles explicit |
| EC-07 | PASS | REM 750–782,840–880, DI-21/22 cached/on-demand vector provenance and typed refusal |
| EC-08 | PASS | Extraction service distinction explicit, extractor narrow path and DI-22/33 round trip |
| EC-09 | GAP | Named maintenance/direct clients covered, public physical backup/analyzer omitted M01/M02 |
| EC-10 | GAP | Unsplit summary/lifecycle design sound; public consolidator error/marker contract M03 |
| EC-11 | GAP | Main lazy startup/background/exit contract strong; unlisted public analysis/consolidation incomplete |
| EC-12 | GAP | Fresh coherent paths and same-dimension identity refusal well defined; later legacy restore bypass remains M01 |
| EC-13 | PASS | Same-space separate services, unrelated unused service failures and independent namespace models explicitly allowed |
| EC-14 | GAP | Shared overflow/cardinality/index/dimension/finite and cache validation strong; new failures swallowed by M03 |
| EC-15 | GAP | DI-18/21/22/27–33 are substantial but must gain exact M01–03 public-path negatives and installed witnesses |
| EC-16 | GAP | Proposed exact paths do not authorize the narrow changes needed for M01–03; stop/reconcile rather than infer broad permission |
| EC-17 | PASS | Companion, Certifi floor, isolated measured dependency readiness, minimal/optional installs coherent; no readiness execution claimed |
| EC-18 | PASS | Fresh source-backed matrix, two scenarios, criterion outcomes, exact boundary/check results and honest limits supplied |

## Advisories

SOL-R5-A01 (Low): current authority top-level current_scope/next_gate still describes a VERIFIED design handoff, whereas document_ingestion_remediation.current_revision correctly records pending round5 and no prior verdict applicability. Align those summaries during authorized status reconciliation to avoid a reader skipping the current gate. The specific current revision and frozen request clearly control; this is not construction authority.

SOL-R5-A02 (Low): convert the source-backed unchanged dispositions above into final Gate-A trace rows with exact test nodes for agent tools, multi-agent controller/coordinator and MCP publication. These generally need shared-boundary regression proof, not subsystem-specific model selectors or broad source edits. Keep logical multi-agent visibility namespaces distinct from physical embedding namespaces in that trace.

## Score and proof limits

| Rubric | Earned / maximum | Reason |
| --- | --- | --- |
| Framework consumer inventory | 1.7 / 2.0 | Strong lower-bound inventory, three consequential public consumers omitted |
| Operational configuration/API compatibility | 2.6 / 3.0 | Correct pool/non-pool qualified readiness and APIs; consolidation failure behavior gap |
| Model replacement/namespace safety | 1.9 / 2.5 | Strong space/incarnation/cache/recovery design, legacy physical restore not closed |
| Bounded proof/reporting | 1.9 / 2.0 | Extensive DI and installed negative obligations, missing public-path proofs |
| Scope/authority | 0.5 / 0.5 | Clear proposed-only limits and stop-before-scope-expansion policy |
| Total | 8.6 / 10 | Mandatory findings prevent VERIFIED regardless of target score |

Reproduced: opening/closing integrity; board validation (36 tasks), dashboard current, docs lifecycle (998 Markdown files), metadata (18 pyprojects), scoped whitespace; all exit 0. Inspected: static implementation/test/config templates, exact technical/amendment path diffs, current controls and policies. Existing tests show API/oracle shape only; none was executed. No public web claims were needed to reach these findings; upstream URLs in REM remain unverified design references for future pinned readiness.

Not performed: product imports/tests/builds, dependency resolution/installation, model downloads/inference/provider requests, real store operations, personal YAML/store inspection, reset/delete/migration/re-embedding, source/document repair, PR/delivery/acceptance. No runtime compatibility assurance follows this review. Future Gate-A must measure exact package/model/counter feasibility and baseline qualification, then freeze approved exact paths/signatures/test nodes. Source and normal/optimized installed proofs remain future implementation gates. Historical Ruff/collection/oracle debt remains unwaived background, not a new runtime result.

All Git/admin executions are listed exactly below from the wrapper audit. Static rg/sed/cat/pathlib reads and private report writes were exempt; search exit 1 denotes no matches (one shell glob also failed to expand), never a product failure. All outputs/caches/temp roots belong to this private scratch. No supplied receipt argv/cache path was replayed.

## Exact administrative command ledger

- Exit 0: `python3 -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/read_only_command.py /private/tmp/rem-ingest-sol-round5-FLryM9 -- python3 -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/check_integrity.py /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/review-request.json`
- Exit 0: `python3 -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/read_only_command.py /private/tmp/rem-ingest-sol-round5-FLryM9 -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate`
- Exit 0: `python3 -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/read_only_command.py /private/tmp/rem-ingest-sol-round5-FLryM9 -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check`
- Exit 0: `python3 -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/read_only_command.py /private/tmp/rem-ingest-sol-round5-FLryM9 -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py`
- Exit 0: `python3 -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/read_only_command.py /private/tmp/rem-ingest-sol-round5-FLryM9 -- uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py`
- Exit 0: `python3 -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/read_only_command.py /private/tmp/rem-ingest-sol-round5-FLryM9 -- git diff --check c28e6f8bba959f10137b8d772a667ec4e59389f5..06f294d779c5bc9ea3016eaffdf8efb349979ce4`
- Exit 0: `python3 -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/read_only_command.py /private/tmp/rem-ingest-sol-round5-FLryM9 -- git diff c28e6f8bba959f10137b8d772a667ec4e59389f5..06f294d779c5bc9ea3016eaffdf8efb349979ce4 -- docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md docs/planning/active/command-refactor/proposals/tools-document-adoption.md docs/planning/active/command-refactor/approval/ingest-existing-store-policy.md docs/planning/active/command-refactor/validation/document-ingestion/embedding-pool-compatibility.json docs/planning/active/command-refactor/validation/document-ingestion/council-round5/scope.md docs/planning/active/command-refactor/validation/document-ingestion/council-round5/roster.json`
- Exit 0: `python3 -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/read_only_command.py /private/tmp/rem-ingest-sol-round5-FLryM9 -- git diff 82c3a05a271c321c18a3967624281a5272c579b9..06f294d779c5bc9ea3016eaffdf8efb349979ce4 -- docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md docs/planning/active/command-refactor/proposals/tools-document-adoption.md docs/planning/active/command-refactor/approval/ingest-existing-store-policy.md docs/planning/active/command-refactor/validation/document-ingestion/embedding-pool-compatibility.json docs/planning/active/command-refactor/validation/document-ingestion/council-round5/scope.md docs/planning/active/command-refactor/validation/document-ingestion/council-round5/roster.json`
- Exit 0: `python3 -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/read_only_command.py /private/tmp/rem-ingest-sol-round5-FLryM9 -- python3 -B /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/check_integrity.py /private/var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-embedding-council-7qnmczu1/inputs/review-request.json`

Boundary JSON: start-integrity.json and end-integrity.json; command audit: command-audit.jsonl. Both boundary results are PASS with no failures. Six metadata records are checked by the inspected helper even though its compact output enumerates only protected_entries.
