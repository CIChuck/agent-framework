# REM-CMD-INGEST-001 independent review — pass 3/4, global round 8

**VERIFIED — design/source-feasibility only. Coverage 9.6/10; overall 9.6/10. Zero mandatory findings.**

Reviewer: gpt-6.1-sol, high effort. Fresh seat; no builder transcript/reasoning, current peer verdicts, raw archived reports, nested agents, repairs or shared writes. Review date: 2026-11-10 America/New_York (UTC 2026-11-11). Explicit shared-checkout exception applied. This is a new assessment of current bytes; no historical verdict is carried forward.

Frozen workdir `/Users/chuckrussell/Dev/gendev/agent-framework`, branch `feature/cmd-ingest-001`, HEAD `f43368c503da19fd245730ee579806db95ed3748`. Correction delta `f1916747ad7d03e451f2b57dc00542faa6095d7c..f43368c503da19fd245730ee579806db95ed3748` was inspected FIRST through explicit technical/status paths, followed by current complete REM, normative annex and independent Tools companion plus source discovery. Aggregate `91ac63bad5e46eceddd252d5b7727f7a1d3c623a..f43368c503da19fd245730ee579806db95ed3748` inspected only through the permitted path set. Product src delta is empty (`source-delta-stat.txt`).

## Findings and limits

Mandatory findings: **none**. No newly unsafe causal dependency was found that requires expanding this document scope. Corrections remain proposed requirements, not implementation closure.

1. **SOL-R8-A01, advisory — qualify the hosted baseline first at the future gate.** Annex80–127 explicitly recognizes that the current hosted B02 default may lack immutable serving identity. Preserve its actual default, and hard-stop Gate A if it cannot qualify. Do not omit that baseline, weaken identity, replace the model, or claim refusal is operational compatibility. This is already a sufficient normative stop condition, not a newly missing design requirement. Proof: alias replacement with unchanged name/dimension must fail before effects; unchanged qualified B02 must also succeed.

2. **SOL-R8-A02, advisory — freeze paired public backup witnesses before construction.** The FU014 classification is source-supported, not runtime-proven. Baseline labels cannot excuse a new binding failure. Preserve old public return types, destinations and data members; binding receipt/marker protection are the only adaptation. No complete-recovery credit for incomplete vector/split forms. Exact paired fixture qualification, receipt encoding and name constraints remain Gate-A obligations. Annex274–326 and REM954–970 already require this.

No product imports/tests/builds, installation/resolution/downloads, model/provider inference, store operations, quality assessment or acceptance were performed. No runtime, installed compatibility or model-quality assurance follows this verdict. Missing future unapproved implementation is not a design defect. Root Ruff534, collection test_display conflict7196, legacy format and MAINT oracle debt remain failed/unwaived background; none was rerun or accepted. FU013/FU014 remain separate unwaived defects.

## Independent consumer/disposition and B/N/R matrix

B means unchanged supported configuration with new optional fields omitted and qualified readiness; N means BOTH changed dimension AND same-dimension changed model/preparation, including smaller capacity, in fresh coherent namespaces. Every success below is a **future required positive**, not a run result. R is an additional refusal proof, never a substitute for B/N. Paths/line numbers cite current source; complete static discovery artifacts are linked by filename in this private scratch.

| # / consumer | Actual route and evidence | Narrow disposition | B positive | N positive | R / baseline limit |
|---|---|---|---|---|---|
| I01 LLM direct APIs/resolver/cache | direct shared provider boundary; `packages/friday-llm/src/friday_llm/embeddings.py:149,249,287; packages/friday-llm/src/friday_llm/model_library.py` | Keep query/document interfaces, service options; qualify absent capabilities; guard cached and new vectors. | B01–08 resolved defaults/options and cache hit/miss pass | Changed dimension and same-dimension new preparation pass in fresh state; smaller capacity valid input passes | Bad indices/cardinality/nonfinite/oversize/alias swap refuse before writes |
| I02 Core interfaces/factories | neutral contract plus lazy adapter imports; `packages/friday-core/src/friday_core/interfaces/llm.py:113; packages/friday-core/src/friday_core/interfaces/memory.py; packages/friday-core/src/friday_core/profiles.py:56` | Narrow typed open-intent/query envelope, no backend policy in new neutral contracts. | Old public argument forms remain callable with admitted capability | Variable dimension carries through factory and protocol | Bare/foreign envelope or implicit fresh intent refuses before client |
| I03 Vector and Simple stores | direct embedding and comparison; `packages/friday-memory/src/friday_memory/adapters/vector.py:73,109,139,195; packages/friday-memory/src/friday_memory/adapters/simple_vector.py:109,125,168` | Correct Chroma query role; admit before client; validate supplied vectors, including empty-store paths. | Document add/upsert/query and supplied-query vector succeed | Both replacement spaces use actual dimensions, fresh namespace | Wrong role/identity/invalid present vector cannot bypass via precomputed input |
| I04 Lifecycle collections | direct document generation and cached-vector handoff; `packages/friday-memory/src/friday_memory/retrieval/collection_manager.py:115,205,421,481,559,617,667` | One admitted identity across short/long/decayed/MCP; unsplit structured records. | Add/query/promote/demote/reactivate and get_all succeed | Same operations with alternate dimensions and smaller-capacity valid inputs | No raw vector bypass; get_all gather must rethrow typed refusal |
| I05 Controller actual recall and priming | maintained; graph route UNSCORED; `packages/friday-memory/src/friday_memory/controller/memory_controller.py:137,497,522,751,787,1038,1193,1589,1639; packages/friday-chat/src/friday_chat/adapters.py:1810; packages/friday-runtime/src/friday_runtime/di.py:299` | Actual query/vector failures propagate; no new unused graph preflight. | Recall contains passages/insights/summaries; graph comparison spy=0 | Full recall succeeds in both fresh replacements; graph comparison spy=0 | Typed errors survive gather/priming/recent/author/scored-graph catches, never empty success |
| I06 Graph scorer public APIs | public injectable, neither composition injects; `packages/friday-memory/src/friday_memory/retrieval/graph_scorer.py:173,221,288,330; packages/friday-memory/src/friday_memory/controller/memory_controller.py:1625` | Validate present components before fallback; document-role fallback only for absent components. | Sync/async score and filter with compatible vectors pass | Different dimensions and preparation identities pass in separate fresh fixtures | Foreign/unknown/invalid present component refuses before any fallback/comparison |
| I07 Graph vector persistence | maintained extraction/REEMBED/recovery, independent of ordinary scoring; `packages/friday-memory/src/friday_memory/adapters/graph.py:360,456,719,745,1023; packages/friday-memory/src/friday_memory/models/graph.py` | Reserved provenance survives node/edge update/read/export; no backfill or graph-schema redesign. | Graph writes preserve compatible envelopes | Fresh graph and vector roots share replacement identity | Foreign update/recovery refuses; absent no-embedder edges allowed |
| I08 Extraction and Chat acknowledgement | maintained; typed failures currently swallowed at several seams; `packages/friday-memory/src/friday_memory/context/extractor.py:457,578,583,602,665,678,698; packages/friday-chat/src/friday_chat/adapters.py:1145,1168` | FC06 aggregates guard refusal before acknowledgement; retain prompts and stable slot IDs. | Extraction LLM, edges, insight batch, summary persist; pending removed only on success | Full extraction→stored edges/insights/summaries→recall succeeds | Guard failure cannot become vectorless edge/per-item fallback/completed turn; retry same IDs |
| I09 ContextAssembler and Agent archive | maintained double task boundary; `packages/friday-memory/src/friday_memory/context/assembler.py:398; packages/friday-agent/src/friday_agent/base.py:494,500,513; packages/friday-runtime/src/friday_runtime/di.py:135,338` | Concrete assembler owns inner task/status, closes admission before drain; no Core/Agent signature change. | Telemetry-off status/wait observes true completion | Qualified replacement extraction completes via real Agent archive | Delayed failure/cancellation retryable; late outer arrival skips unavailable and cannot reopen sink |
| I10 Rejection sink | global source logger is current hazard; `packages/friday-memory/src/friday_memory/context/extraction_filter.py:25,32,127,178; packages/friday-chat/src/friday_chat/adapters.py:2086; packages/friday-runtime/src/friday_runtime/di.py:372` | Defer until admission; per-owner lease, no-file default; standalone independent API retained. | First-use configured path and two owned extractors succeed independently | Two identities/log destinations do not fan out or close each other | Refused root zero file effects; failed setup/closed owner cannot emit; inert Chat flags stay inert |
| I11 MCP snapshot stage/publication | active opt-in Chat single-record route; `packages/friday-chat/src/friday_chat/adapters.py:316,333; packages/friday-memory/src/friday_memory/ingestion/mcp.py:38,130,155; packages/friday-memory/src/friday_memory/retrieval/collection_manager.py:481; packages/friday-chat/src/friday_chat/memory_mcp.py:126` | Existing storage inherits shared final-HTML document guard; exact record/receipt lifecycle unchanged. | Public prepare/append/readback/publish and matching reuse pass without second write | Replacement model stages valid unsplit snapshot; reuse stays store-only | Oversize skipped only; identity/result/readiness/storage/ownership fail truthfully; pending retained on append/readback/cancel/mixed failure |
| I12 MCP observer boundary | maintained processor forwards existing literals; `packages/friday-chat/src/friday_chat/turns/processor.py:688,704,713; packages/friday-runtime/src/friday_runtime/mcp_loading.py:171; packages/friday-telemetry/src/friday_telemetry/models/mcp.py:27` | Local observer union uses fixed existing literals; no processor or telemetry schema edits. | Published/pending/skipped/disabled counts work export off/on | Identical mapping independent of replacement identity | capped/unavailable/rejected/invalid_result/execution_error/blocked accepted; no failure masking |
| I13 In-session compaction and public consolidation | compaction maintained; consolidator public-unwired; `packages/friday-memory/src/friday_memory/maintenance/compactor.py:510,624; packages/friday-memory/src/friday_memory/context/consolidator.py:136,198,460; packages/friday-chat/src/friday_chat/adapters.py` | Unsplittable summary guards and truthful per-batch acknowledgement, no new scheduling. | Compaction succeeds; explicit public consolidation acknowledges stored batches | Both replacement identities produce and recall valid summaries | Failed/mixed summary storage retains failed source turns; capacity refusal never rechunks record |
| I14 Lifecycle service and lifecycle tool | maintained and public wrapper; `packages/friday-memory/src/friday_memory/lifecycle/promotion.py:342,426,466,566; packages/friday-tools/src/friday_tools/memory/lifecycle.py` | Count successful mutations/false returns correctly; public text exposes partial/errors. | Promotion/demotion/reactivation and dry-run counts correct | Same semantics with replacement spaces | False mutation/guard error produces visible errors, no completed inflation |
| I15 MAINT pipeline/providers/legacy synthesis | maintained pipeline plus callable public legacy surfaces; `packages/friday-memory/src/friday_memory/maintenance/pipeline.py:951,1031; packages/friday-memory/src/friday_memory/maintenance/synthesizer.py:697,767,795; packages/friday-memory/src/friday_memory/maintenance/reorganizer.py:775; packages/friday-chat/src/friday_chat/reorganization/mutation.py:108,157` | Admission before all probes; shared document role; preserve three callable shapes and no default embedder. | Pipeline and admitted callable query/embed/callable adapters succeed | Replacement synthesis/REEMBED pass, including empty graph-only dimensions | Missing qualification/invalid result refuses before collection.add; no implicit Chroma embedder |
| I16 Pruning/fact checks/stored-vector consumers | direct Chroma opens/comparisons; `packages/friday-memory/src/friday_memory/maintenance/pruner.py:114,172; packages/friday-memory/src/friday_memory/maintenance/fact_checker.py:140; packages/friday-memory/src/friday_memory/maintenance/mutation.py:594,628` | Exact admitted normalized root; no two-root fallback; retain algorithms and 8192 ceiling. | Working pruning/clustering/fact-check reads/mutations succeed | Variable dimension plus fresh empty collections/graph-only REEMBED succeed | Same-dimension foreign identity, >8192 dimension and failed admission stop before provider/client |
| I17 Public physical backup and analyzer | public APIs/module/accessors, distinct from maintained v2; `packages/friday-memory/src/friday_memory/maintenance/backup.py:40,53,68,137,158,240,273; packages/friday-memory/src/friday_memory/maintenance/analyzer.py:103,146,206; packages/friday-memory/src/friday_memory/maintenance/__main__.py` | Minimum fixed-marker selector/receipt/no overwrite only; read-only analyzer SQLite, no engine/layout/default repair. | Working public create/verify/restore/backup_first preserve old destinations/member sets | Same working layout on fresh replacement namespace succeeds same-incarnation restore | Absent/dual/pending marker or foreign receipt refuses; verify_first=False cannot bypass identity; FU014 gets no complete-recovery credit |
| I18 Logical recovery and mutation participant | maintained identity-preserving full recovery; `packages/friday-memory/src/friday_memory/maintenance/recovery.py:412,563,898,1378,1544; packages/friday-chat/src/friday_chat/reorganization/artifacts.py; packages/friday-chat/src/friday_chat/reorganization/coordinator.py` | Strict Memory2/Chat2 versus old1 offline dispatch; Transcript1 unchanged; no live rebinding. | Snapshot→verify→same-incarnation rollback restores data and ready marker unchanged | Both replacement spaces perform independent coherent recovery round trips | Wrong version/mixed payload/root/incarnation/identity/graph provenance refuses before live effects |
| I19 Factor/access/incremental metadata | maintained wired store-only consumers; `packages/friday-chat/src/friday_chat/adapters.py:748,966,1000,1970,2000; packages/friday-memory/src/friday_memory/retrieval/access_buffer.py:703,857; packages/friday-memory/src/friday_memory/retrieval/factor_computer.py:243; packages/friday-memory/src/friday_memory/maintenance/incremental.py:245` | Admitted guarded handles, unchanged algorithms/WAL; Chat projects result.errors and partial counts. | Flush/factors/incremental maintenance and exit succeed without inference | Independent replacement namespaces retain isolated queues/metadata | Guarded failure visible in Chat maintenance/exit; no false completed total, no WAL/token redesign |
| I20 Tools maintenance/reset/inspection | public injectable wrappers, no new automatic wiring; `packages/friday-tools/src/friday_tools/memory/maintenance.py:39,103; packages/friday-tools/src/friday_tools/memory/inspection.py:134,141; packages/friday-tools/src/friday_tools/base.py` | Whole-layout admission before clear, retain confirmation/binding; wrapper errors visible. | Maintenance/reset and no-query inspection succeed provider-offline where store-only | Same on admitted replacement fixtures | No preflight bypass through graph-first clear; vector.search defect FU013 preserved with zero semantic-positive credit |
| I21 smart_read and large-file processing | explicit public injected storage, Chat/Runtime storage not wired; `packages/friday-tools/src/friday_tools/filesystem/smart_read.py:218,421,605; packages/friday-memory/src/friday_memory/ingestion/large_file_processor.py:828` | Common source plan and destination receipts; derived summaries unsplit; no second chunker. | Small/large/force/cache storage works; disabled→enabled rechecks policy | New namespace/collection and preparation invalidate completion cache; valid storage succeeds | Missing entry/stale receipt/missing records/oversized derived input refuse, never false cache success |
| I22 Generic tool ingestion and legacy preprocessing | public-unwired capabilities; `packages/friday-memory/src/friday_memory/ingestion/tool_ingester.py:299; packages/friday-memory/src/friday_memory/ingestion/pipeline.py:39; packages/friday-memory/src/friday_memory/ingestion/chunker.py` | Shared ingestion entry for explicit source storage; old preprocessing does not establish common-plan proof. | Explicit caller stores common document/512 plan and all strategy overrides | Replacement capacities refine valid source, not structured records | No automatic activation, accepted plan cannot split twice; unsafe input/overflow refused |
| I23 Tools document consumers and read/web tools | companion independently adopts factory and smart_read; `packages/friday-tools/src/friday_tools/filesystem/readers/factory.py:289; packages/friday-tools/src/friday_tools/filesystem/smart_read.py; packages/friday-tools/src/friday_tools/filesystem/read.py; packages/friday-tools/src/friday_tools/web/client.py` | ReaderFactory and smart_read require separate TD proofs; legacy direct readers retained; web stays read-only. | Real PDF/DOCX/XLSX/PPTX and retained text/web read behavior | Same extracted content independent of embedding; adopted storage uses replacement common entry | Sandbox/missing assets/partial/empty/coverage failure precedes ingestion; no binary or legacy fallback |
| I24 Runtime profiles/config, CLI container | maintained headless assembly/transitive; `packages/friday-runtime/src/friday_runtime/di.py:245,282,338; packages/friday-core/src/friday_core/profiles.py:56; packages/friday-cli/src/friday_cli/container.py:70,109` | All four profiles, explicit origin, no early graph mkdir; per-incarnation collection suffixes for ephemeral lifecycle. | FULL/VECTOR_ONLY persistent; EPHEMERAL/TESTING no persistent Memory, same logical names isolated | Two kernels same names/different identities never share records or dimension state | Unset absent defaults refuse creation; explicit literal equal default remains explicit; unused service cannot globally disable |
| I25 Agent tools and multi-agent controller/coordinator | maintained transitive consumers; `packages/friday-agent/src/friday_agent/tools/builtins.py:109,203; packages/friday-memory/src/friday_memory/multi_agent/controller.py:57,95,145; packages/friday-memory/src/friday_memory/multi_agent/coordinator.py:159,167` | Underlying guarded memory, preserve authorization namespaces and partial commit semantics. | Actual recall/store_fact/archive/private→shared operations succeed | Different physical namespaces can use different models; visibility partitions share physical identity | Typed failures and partial commits visible; no new transaction promise |
| I26 Startup catalog, neutral and other packages | import/transitive or unaffected; `packages/friday-runtime/src/friday_runtime/tool_loading.py:60; packages/friday-core/src/friday_core/interfaces/transcript.py:250,320; all-source-call-inventory.json` | Real pkgutil/import_module path, lazy optional code; no Docling prerequisite for non-document operations. | Normal minimal Runtime/CLI/Agent Memory counter-extra installed lanes work; Commands/plain Tools reads work | Model changes do not change LLM-only services, transports, speech or registration | Missing optional stack import control distinguished from supported install; no first-use downloads |
| I27 Inactive migration and disabled legacy execution | inactive/example/disabled classification; `packages/friday-memory/src/friday_memory/lifecycle/migration.py:423,596; packages/friday-chat/src/friday_chat/adapters.py:1037` | No migration fix/activation; old dummy dimension is not a maintained positive. | Existing stub/disabled outcomes retained | No replacement success credit for inactive code | Guarded direct store cannot bypass admission; no incidental repair |

Discovery independently searched explicit `packages/*/src` roots only, using direct embed/client/comparison patterns, transitive Memory/LLM/store interfaces, dimensions and supplied-vector patterns, plus AST call inventory (79 matching source files). The two dirty top-level Chat YAML examples were outside every search root and never read. Tests and packaged templates were read only by explicit paths. No embed/Memory linkage was found in Commands, MCP transport package, Speech, Sandbox, Finance, Moltbook, Optimization or Transcript package source; those retain unaffected implementations, with dynamic Runtime tool discovery and Core transcript lazy Memory conversion separately inventoried above. Telemetry contains models/helpers, not another embedder. Searches are static evidence, not a promise about arbitrary external plugins.

## B01–B08 configuration qualification matrix

| Family | Actual source / binding | B and N requirement | Refusal/qualification stop |
|---|---|---|---|
| B01 | Chat packaged config_templates/config.example.yaml:59,232,410 and models-config.example.yaml:88; adapters.py:1735 | Memory=pool default; maintenance=explicit maintenance. Divergent ignored hint stays no-op with safe warning; options preserved. N repeats with changed dimension and same-dimension new identity/preparation in coherent fresh vector/graph/WAL/recovery/cache roots, plus smaller capacity. | Placeholder revision must resolve from verified served identity, not alias echo. |
| B02 | Chat adapters.py:1748–1758 | Non-pool configured model/endpoint/key or text-embedding-3-small default, inherited timeouts; both new fields omitted. N repeats with changed dimension and same-dimension new identity/preparation in coherent fresh vector/graph/WAL/recovery/cache roots, plus smaller capacity. | Hosted immutable identity may be infeasible: hard Gate-A stop, no default replacement. |
| B03 | Chat config.py and sanitized compatibility fixture requirement; no personal YAML read | Legacy alias/endpoint and extraction selection preserved; supplied immutable sanitized fixture required. N repeats with changed dimension and same-dimension new identity/preparation in coherent fresh vector/graph/WAL/recovery/cache roots, plus smaller capacity. | Absent revision cannot be invented; fixture qualification remains future. |
| B04 | Runtime di.py:233,348–367 | Pool default for memory and optional separate extraction service retained; LLM bindings unchanged. N repeats with changed dimension and same-dimension new identity/preparation in coherent fresh vector/graph/WAL/recovery/cache roots, plus smaller capacity. | Same namespace different service names allowed only same space; unused independent service cannot disable. |
| B05 | Runtime config.py and di.py embedding-pool construction | Legacy embedding/service config retains endpoint/model/options via shared resolver. N repeats with changed dimension and same-dimension new identity/preparation in coherent fresh vector/graph/WAL/recovery/cache roots, plus smaller capacity. | No unguarded non-pool lane; unknown identity/capacity stops. |
| B06 | CLI container.py:43,70,109,121–127 | Direct/env/default origins survive delegation; explicit literal equal default remains explicit. N repeats with changed dimension and same-dimension new identity/preparation in coherent fresh vector/graph/WAL/recovery/cache roots, plus smaller capacity. | Internally forwarded fallback is not CREATE_FRESH authority. |
| B07 | Chat maintenance config; reorganization/mutation.py:155; adapters.py maintenance assembly | Inline non-pool maintenance model/endpoint/options retain service and guard contract. N repeats with changed dimension and same-dimension new identity/preparation in coherent fresh vector/graph/WAL/recovery/cache roots, plus smaller capacity. | Independent space allowed only independent namespace; same-root mismatch refuses before probes. |
| B08 | Memory MaintenanceConfig and synthesizer.py:697–737; Core EmbeddingModel | Injected embed_query/embed/callable shapes remain callable through qualified shared wrapper, once-only document preparation. N repeats with changed dimension and same-dimension new identity/preparation in coherent fresh vector/graph/WAL/recovery/cache roots, plus smaller capacity. | Hidden query preparation must qualify or stop; no guessed identity/default Chroma embedder. |

Exact selected source-linked fixtures, endpoint/artifact attestation, counter assets/preparation revision and capacities are future readiness records. This review establishes required coverage, not their existence or qualification. Separate physical namespaces may use different models; authorization visibility partitions do not establish separate physical embedding spaces.

## EC-01–18 — exact criteria and independent outcomes

### EC-01

Exact current bounded four-pass maintainer authority, candidate pins, current controls and design-only effects. Earlier blocked/passing reviews remain history; every changed-candidate pass is fresh.

**PASS — design requirement sufficient.** Current pass3/global8, maximum4, one further full pass; no GateA/construction/reset/delivery. Evidence: current-controls.json; start/end-integrity.json; history-comparison.json; docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md:13–38,1356–1364.

### EC-02

Independent framework-wide source inventory, not limited to REM named paths. Discover direct embedding calls, provided/cached vectors, indirect storage/comparisons and affected shared contracts; include unlisted subsystems or source-backed unaffected dispositions.

**PASS — design requirement sufficient.** Independent direct/transitive discovery includes metadata, wrappers, agent tools, public-unwired and unaffected routes. Evidence: I01–I26; all-source-call-inventory.json; source-discovery.txt; transitive-discovery.txt; docs/planning/active/command-refactor/embedding-compatibility-contract.md:129–166.

### EC-03

Unchanged pre-existing catalog/pool and maintained non-pool configuration preserves default/explicit service, profile, endpoint/credential, batch/cache/resilience selection; no silent rebinding or ingestion-only model selector.

**PASS — design requirement sufficient.** Actual default/hint difference preserved; no ingestion-only selector. Evidence: B01–B08; packages/friday-chat/src/friday_chat/adapters.py:1735; packages/friday-runtime/src/friday_runtime/di.py:233; docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md:667–716.

### EC-04

Existing embedding API/protocol callers remain compatible; every necessary store/query-envelope extension has actual downstream consumers classified, narrow allowed paths and regression obligations, including previously unnamed ones.

**PASS — design requirement sufficient.** Narrow neutral query/vector envelope and actual downstream handoffs explicitly scoped. Evidence: I01–I07/I23–I24; docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md:889–893,1227–1267.

### EC-05

Optional new YAML capability fields resolve from qualified exact-identity readiness without mandatory config rewrites. Missing baseline qualification is a readiness stop; parse-only success, guessed metadata, disabled used services or an unguarded lane cannot count as compatibility.

**PASS — design requirement sufficient.** Optional YAML fields omitted still succeed when qualified; unknown baseline is Gate-A stop. Evidence: docs/planning/active/command-refactor/embedding-compatibility-contract.md:97–118; docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md:645–665; B01–B08.

### EC-06

Shared LLM owns exact preparation/counting/request/result validation, Memory owns namespace admission; all document/query roles and caches correct, no subsystem-specific duplicate guard and no asymmetric formatting with unknown caller.

**PASS — design requirement sufficient.** LLM preparation/count/result owner and Memory namespace owner separated; every final document/query/cache input covered. Evidence: docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md:784–835,839–908; I01–I07/I10/I14–I15.

### EC-07

Maintained Chat/Runtime do not inject GraphPathScorer and perform zero graph-vector comparisons. Both sync/async public-injectable scorer APIs require identity-safe B/N/R proofs, separate from real query/vector recall propagation; no new scorer wiring or unused-vector preflight.

**PASS — design requirement sufficient.** No maintained scorer injection; real recall unscored; public sync/async absent-component matrix retains fallback only on absence. Evidence: docs/planning/active/command-refactor/embedding-compatibility-contract.md:401–430; I05–I06; packages/friday-memory/src/friday_memory/retrieval/graph_scorer.py:221,330.

### EC-08

Maintain extraction LLM and embedding bindings; typed failures at actual edge/insight/summary persistence cannot become vectorless edges or completed acknowledgement. Cover real Chat pending retry and owned ContextAssembler delayed task/status with telemetry disabled.

**PASS — design requirement sufficient.** Typed edge/insight/summary failures and actual owned completion/retry/telemetry-off status specified. Evidence: docs/planning/active/command-refactor/embedding-compatibility-contract.md:350–392; I08–I09; packages/friday-chat/src/friday_chat/adapters.py:1145; packages/friday-memory/src/friday_memory/context/extractor.py:583,665,698.

### EC-09

Keep working maintenance/public backup consumers operational with minimum new-binding admission/receipt and no marker overwrite. Existing copy/default/member behavior remains; paired baseline proofs distinguish pre-existing FU014 limitations from new regressions. No physical backup repair, layout/default redesign or schema waiver; maintained logical-v2 remains separate.

**PASS — design requirement sufficient.** Minimum receipt/marker admission compatible with old API/member/default behavior; FU014 paired proof required, no baseline waiver. Evidence: docs/planning/active/command-refactor/embedding-compatibility-contract.md:274–326; I16–I17; packages/friday-memory/src/friday_memory/maintenance/backup.py:137,273.

### EC-10

Lifecycle promotion/decay/reactivation, compaction and indirect derived-record/tool/source storage are covered. Document/512 applies only to ingestion planning; no silent re-chunking of structured memory records.

**PASS — design requirement sufficient.** Derived and structured records stay unsplit; document512 only ingestion planning; lifecycle/compaction error truthfulness covered. Evidence: docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md:167–173,693–695; I04/I12–I14/I20–I21.

### EC-11

Runtime/Core/CLI/Chat plus every other maintained package/entrypoint are assessed for direct or transitive effects. Non-embedding operations, LLM-only services, tool registration, startup/background/exit and optional-dependency behavior do not acquire unexplained new failure modes. Distinguish actual wiring, public-unwired and inactive/example code.

**PASS — design requirement sufficient.** Four profiles/headless catalog/startup/shutdown/nonembedding and optional dependency effects classified. Evidence: I01–I26; docs/planning/active/command-refactor/embedding-compatibility-contract.md:154–166,477–526; packages/friday-runtime/src/friday_runtime/tool_loading.py:60.

### EC-12

Replacement model tests cover changed dimension and same-dimension different space/preparation. Fresh coherent vector/graph/WAL and relevant recovery/cache roots are explicit. Fresh data assumption does not excuse API/configuration/role/hard-coded dimension regressions or authorize deleting/migrating personal stores.

**PASS — design requirement sufficient.** Fresh coherent namespace, graph/WAL/recovery/cache roots; same-dimension changed preparation tested; no deletion/migration. Evidence: docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md:839–917,1085–1197; docs/planning/active/command-refactor/embedding-compatibility-contract.md:16–35; I17/I23.

### EC-13

Separate names/timeouts may share one compatible namespace; independently bound namespaces may legitimately use different models. One namespace cannot mix vectors, and a failure in an unrelated unused pool service does not disable a qualified operation.

**PASS — design requirement sufficient.** Namespace identity is physical, not service-name equality or global model restriction. Evidence: docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md:662–689; docs/planning/active/command-refactor/embedding-compatibility-contract.md:37–39; I24/B04/B07.

### EC-14

Effective capacity, overflow and full result/index/dimension/finite validation guard every embedding path and cache, with actionable typed propagation and no silent partial-success/error-swallowing loopholes.

**PASS — design requirement sufficient.** All final inputs and caches guarded; response indices/cardinality/dimension/nonfinite checked before storage; typed catch seams named. Evidence: docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md:806–837,905–908; docs/planning/active/command-refactor/embedding-compatibility-contract.md:201–272,401–430; I01/I10/I14.

### EC-15

DI-18/21/22/27-33 and Gate-A inventory are sufficient or identify exact gaps. Require unchanged fixture and replacement-model cross-subsystem positive/negative and normal/optimized installed proof before implementation acceptance; do not demand execution of future Gate-A/model/build tests in this design review.

**PASS — design requirement sufficient.** DI18/21/22/27–33 and FC nodes cover true B/N positives, R and source/normal/-O installed call-phase mutants. Evidence: docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md:1282–1316; docs/planning/active/command-refactor/embedding-compatibility-contract.md:537–576.

### EC-16

Newly identified affected consumers fit an explicit narrow allowed purpose or are a mandatory document-scope/test gap. No implicit permission for broad subsystem rewrites, automatic routing, model migrations, TUI or maintenance-order redesign.

**PASS — design requirement sufficient.** Narrow allowlist fits identified adaptations; no MCP/backup engine projects or implicit source edits. Evidence: docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md:1225–1277; docs/planning/active/command-refactor/embedding-compatibility-contract.md:53–78,578–583; I01–I26.

### EC-17

Retained extraction/Tools companion and security/dependency/Certifi constraints remain coherent with framework compatibility; no default dependency/schema/resource change silently breaks unlisted consumers or optional/minimal installations. Pending measured dependency feasibility remains Gate-A, not an invented implementation pass.

**PASS — design requirement sufficient.** All-source plan, four formats, independent Tools routing and Certifi floor remain coherent; exact dependency/format feasibility is future GateA. Evidence: docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md:203–332,335–449,529–634; docs/planning/active/command-refactor/proposals/tools-document-adoption.md; I20–I22/I25.

### EC-18

Current review state and exact pins are coherent, historical verdicts are not reused as proof, findings and evidence limitations are precise, and report contains complete independent consumer and two-scenario compatibility matrices with honest scores.

**PASS — design requirement sufficient.** Current pins and history coherent; exact request criteria copied, source-backed assessment and honest rubrics, no inherited correctness verdict. Evidence: start/end-integrity.json; controls-copy.json; history-comparison.json; all matrices here.

## FC-01–14 — complete normative text, source feasibility and future proof

### FC-01

Request criterion: Independently assess the complete FC-01 normative contract, actual source path/route/classification, exact scope and B/N/R success/refusal/install proof. Locate all mapped mandatory/high-medium requirements; do not infer closure from a controller map.

Normative criterion (exact current annex text):

**FC-01 — startup and owned rejection logging.** Defer resourceful
MemoryExtractor/rejection-handler construction until namespace admission; inert
settings can exist earlier. Startup and /read cannot mkdir/open a log in a
refused, unbound or not-yet-created namespace. First-use CREATE_FRESH must work
when the packaged log is inside vector/. Qualify the configured target as owned
by that admitted namespace or an independent safe log root. Stale/foreign or
unknown ownership refuses extraction readiness with an actionable remedy; no
store scan, silent redirect or YAML rewrite. Keep qualified independent targets.

Bind each emission to its admitted extractor/namespace using an extractor-owned
sink/logger with propagation disabled and an owned handler lease. Do not fan out
through the module-global logger to every configured path. Reconfiguration or
close releases only that owner's handler after its task quiesces. Failed
construction releases any new handler. Repeated same-owner/path setup is
idempotent; two kernels cannot write or close each other's handlers. An explicit
shared independent destination needs shared-target admission and owner-specific
leases, not accidental global fan-out. A revoked/closed owner cannot write the
old target; re-admit before reopening. Preserve standalone public filter and
configure_rejection_logging call shapes and qualified independent logging; the
final directive freezes private ownership injection without a logging redesign.
Chat logging.extraction_rejections and logging.extraction_rejections_file have
no source consumer: keep both inert, never activate a second handler from them.
An owned extractor with no rejection_log_path has a no-file sink; it must not
inherit a previously configured global file handler. Standalone public
configure_rejection_logging retains its independent standalone logger/filter
behavior and None return, but never attaches that logger to owned extractors.
A standalone target claimed as a Memory namespace needs the same admission;
it cannot use the standalone entry as a namespace-write bypass. Independent
qualified standalone targets remain usable. Test default/no-path extraction
after standalone setup, two owned extractors and standalone close/reconfigure.

**PASS — design/source feasibility.** ExtractionFilter globally attaches handlers and creates parents now; FC01 replaces only ownership/admission semantics. No-file default after standalone setup is explicitly covered. Source and B/N/R disposition: I09; corresponding consumer rows also apply transitively. The annex537–576 names required actual public nodes and normal/-O installed lanes; these are future proof, not executed evidence. Allowed purposes are REM1227–1267; no wider edits inferred.

### FC-02

Request criterion: Independently assess the complete FC-02 normative contract, actual source path/route/classification, exact scope and B/N/R success/refusal/install proof. Locate all mapped mandatory/high-medium requirements; do not infer closure from a controller map.

Normative criterion (exact current annex text):

**FC-02 — active MCP snapshots and public failure mapping.** Treat
mcp_tool_snapshot as one exact structured record, exempt from document/512
chunking. Retain opt-in, sanitization, byte ceiling, deterministic identity,
pending/publish/discard ownership and transcript receipt protocol. Count the
final stored record with document-role shared guards; byte-valid token overflow
returns oversized before provider/store effects, never splits or truncates it.
Preserve known typed refusal exceptions ahead of ineligible/ValueError and
generic storage_failed/Exception catches.

The actual Chat persist_mcp_interaction entry must consume the preparation
outcome. Its narrow memory_mcp.py adaptation is required:

| Preparation/result | Receipt/publication disposition | Public observer and turn result |
| --- | --- | --- |
| Disabled, ineligible, unallowlisted or unsafe | Existing policy skip; memory_ingested=false and no memory correlation. | Retain policy-skip behavior and no new activation. |
| Byte or token oversized | Skip this snapshot, with false ingested flag/no memory correlation. | Explicit oversized initial decision, never ingested/published or an indistinguishable initial policy skip. |
| Typed readiness/space/provenance/invalid-result refusal, or storage_failed | No successful skipped receipt for failed preparation. | Safe failure category, then existing MCPMemoryPersistenceError through turn persistence; retry eligibility retained. |
| Ownership conflict | Existing hard ownership failure; no foreign-record deletion. | Safe ownership-conflict category and existing persistence error. |
| Prepared/published/publication pending | Existing exact snapshot, verified append/readback and pending ownership. | Preserve published/pending outcomes and truthful flags. |

Keep the existing callback shape. At the existing memory_mcp.py decision
adaptation, use ONLY these existing MCPEventReason literals in the observer's
outcome union, so the actual processor callback can continue forwarding them
unchanged. No new telemetry enum, processor mapping feature or Runtime schema:

| Preparation/outcome category | Observer literal, existing emitted reason and counter key |
| --- | --- |
| Existing ingestion_disabled / skipped / pending / published | Same existing value. |
| oversized (byte or token) | capped |
| Readiness failure | unavailable |
| Space/provenance failure | rejected |
| Invalid embedding result | invalid_result |
| Storage failure | execution_error |
| Ownership conflict | blocked |

The observer intentionally uses the existing coarser vocabulary. Never forward
a new literal such as oversized/storage_failed to the real Runtime sink. Require
the entire observer union to be a subset of the existing strict MCPEventReason
contract, and verify actual processor/provider counts with export disabled plus
strict emitted event acceptance with it enabled. No raw document/provider/secret
text. Observer failure remains non-authoritative. Receipt/provenance schemas stay
unchanged; replay of a skipped receipt reports its established skip without
inventing the missing original capacity reason. Non-capacity guard failures do
not acquire successful skipped receipts.

RETAIN owned pending records after failed/false/ambiguous append, failed
readback, publication failure, cancellation, or a later call's preparation
failure in the same turn. Current persist_mcp_interaction performs NO automatic
discard. These records remain pending and non-retrievable until a matching
verified receipt permits publication. Retry of the same entry/call reuses the
exact owned record ID/content with no second embedding write; neither a new
UUID nor a duplicate write is an acceptable oracle. Preserve receipt ambiguity
readback and cancellation behavior. Foreign, existing and receipted records are
never deleted. discard_mcp_memory remains an explicit existing capability, not
new cleanup wiring. No automatic retry, pending garbage collector or whole-turn
rollback/atomicity is added. Test mixed ordinary/MCP calls and delayed errors
through actual public persistence, not just the lower discard method.

Token counting remains at the SAME qualified shared embedding service used
by the existing CollectionManager stage_mcp_snapshot/add_to_short_term path.
It validates the exact final sanitized, labelled/wrapped stored text before a
new embedding request or row write. MCPMemoryIngester(storage) keeps its current
constructor: do not add a separate tokenizer, counter option or prepared-input
protocol to MCP. Name the existing Chat prepare_mcp_memory/verify_mcp_memory
constructor sites as trace points proving they use that guarded storage, and
preserve typed overflow before generic storage_failed catches. Existing ownership
lookup/readback can read admitted records. Matching pending/receipted reuse is
store-only, checks namespace/ownership and makes no new embedding request; it
does not gain a token recount/provider prerequisite merely to publish an already
stored valid vector. A changed embedding space still refuses store admission.
Test the actual shared guard on first stage and same-ID/no-extra-write reuse;
do not implement new lifecycle or chunking behavior to make a snapshot fit.

**PASS — design/source feasibility.** Exact final HTML from mcp.py:130 is guarded at CollectionManager.stage_mcp_snapshot→add_to_short_term. Matching owned stored reuse returns before stage. Existing retry assertions in tests_chat/test_mcp_memory.py:98–202 require unchanged IDs/writes; no automatic discard exists in public persist. Source and B/N/R disposition: I10; corresponding consumer rows also apply transitively. The annex537–576 names required actual public nodes and normal/-O installed lanes; these are future proof, not executed evidence. Allowed purposes are REM1227–1267; no wider edits inferred.

### FC-03

Request criterion: Independently assess the complete FC-03 normative contract, actual source path/route/classification, exact scope and B/N/R success/refusal/install proof. Locate all mapped mandatory/high-medium requirements; do not infer closure from a controller map.

Normative criterion (exact current annex text):

**FC-03 — compatible public physical backups.** Retain BackupManager
create_backup, verify_backup and restore_backup signatures/return types and the
old BackupManifest class. Public create, enabled module backup, Reorganizer
backup/backup_first and the injectable Tools wrapper must still succeed under
admitted B/N. Do not retire them, disable backup_first or substitute a different
API as proof of compatibility.

Preserve the existing memory_dir/backup_root/backup_dir arguments, default
destinations, old BackupManifest and data-file selection/copy semantics. This is
not a new complete physical snapshot implementation. The existing parent form
D/vector and vector-directory form D are identity-admission cases, not new
layout features: inspect only fixed marker metadata at D/embedding-space.json
and D/vector/embedding-space.json before live copying. Exactly one ready marker
must resolve; both, pending/malformed or absent markers refuse without fallback
to another namespace. Never infer a model from files or touch an unbound root.
This bounded selector reconciles the old signature with OPEN_BOUND; it does not
invent graph/split-root discovery or scan arbitrary store paths.

For an admitted operation, preserve the old backup destination, including an
existing safe nonrecursive vector-form default. Existing creation may change
its backup-directory metadata; require unchanged vector payload/live binding,
not a new promise of no directory effects at all. Add only a strictly versioned
binding receipt beside the old manifest: canonical ready identity/digest,
namespace incarnation/vector root and exact old-manifest digest. Capture a copy
of the binding as evidence if needed; never make it restore data. This receipt
is distinct from logical-v2 snapshots and does not change the old file-set rules.

Before restore, require matching admitted identity/incarnation/vector root and
valid binding receipt, even if verify_first=False. Never overwrite/recreate a
ready/pending binding marker or clone/relabel a new root. Preserve ordinary
data-checksum option behavior. Identity-free artifacts retain offline manifest/
checksum inspection; they cannot be attached to a new guarded namespace. No new
automatic cleanup, default relocation, membership repair, transaction or backup
engine. If minimum identity admission cannot fit these paths without changing
existing working behavior, stop the construction directive for that exact scope
decision rather than implementing a broader solution.

The old vector-directory form omits per-segment backend files and the standalone
API cannot express Runtime's separate graph root. Those pre-existing completeness
limits are FU-014, failed/unwaived baseline behavior, not this unit's repair or
positive complete-recovery claim. Runtime has no maintained construction of this
legacy BackupManager; its maintained logical-v2 participant remains the required
complete recovery path. Keep module backup and public backup/backup_first working
as before on admitted fixtures; keep disabled module restore disabled. Future
paired baseline/candidate tests compare old public return types, destinations
and file sets (apart from new binding evidence), same-incarnation binding safety
and unchanged unrelated failure behavior. Genuine complete/queryable positives
use an already working baseline layout; known incomplete/split cases receive
no complete-recovery credit. Record any new failure separately from FU-014.

**PASS — design/source feasibility.** backup.py:137 copies fixed root members and recursively only vector/. Thus vector-directory form omits UUID segment files; one root cannot express Runtime split graph. This is static FU014 evidence, not a reproduced runtime failure. Fixed D versus D/vector marker resolution and separate binding receipt fit the existing signatures without authorizing engine repair. Source and B/N/R disposition: I16; corresponding consumer rows also apply transitively. The annex537–576 names required actual public nodes and normal/-O installed lanes; these are future proof, not executed evidence. Allowed purposes are REM1227–1267; no wider edits inferred.

### FC-04

Request criterion: Independently assess the complete FC-04 normative contract, actual source path/route/classification, exact scope and B/N/R success/refusal/install proof. Locate all mapped mandatory/high-medium requirements; do not infer closure from a controller map.

Normative criterion (exact current annex text):

**FC-04 — analyzer and raw SQLite.** Public ConsistencyAnalyzer uses
the resolved exact layout and shared store-only admission before live graph or
SQLite reads, with no alternative-root probing. All its SQLite opens, including
Chroma and transcript databases, use explicit read-only URI mode and cannot
create absent files/journals. No provider/tokenizer for admitted store-only
analysis. Preserve algorithms and ordinary schema diagnostics; typed admission
failure cannot become successful empty analysis. Offline historical artifact
inspection is separate and not positive admitted live-analysis proof.

**PASS — design/source feasibility.** analyzer.py:103,146,206 are actual SQLite opens. Read-only URI mode must cover transcript too, after shared store-only admission. Source and B/N/R disposition: I16; corresponding consumer rows also apply transitively. The annex537–576 names required actual public nodes and normal/-O installed lanes; these are future proof, not executed evidence. Allowed purposes are REM1227–1267; no wider edits inferred.

### FC-05

Request criterion: Independently assess the complete FC-05 normative contract, actual source path/route/classification, exact scope and B/N/R success/refusal/install proof. Locate all mapped mandatory/high-medium requirements; do not infer closure from a controller map.

Normative criterion (exact current annex text):

**FC-05 — no hidden embedder, retained callable shapes.** Qualified
public legacy synthesis keeps its injected service and document-role storage.
Preserve accepted embed_query, embed and bare-callable invocation shapes at the
public boundary: composition resolves an exact identity/counter capability from
the existing service/readiness record and wraps that shape with the shared LLM
guard/role adapter. This is the qualification route, not a new model selector.
The wrapped callable must preserve the invocation shape and error/cancellation
semantics while applying the qualified document preparation exactly once. A
query-only callable with hidden preparation cannot be guessed into a document
provider: qualify its bounded adapter or stop readiness. Its raw name or
dimensions alone is not qualification. Freeze exact wrapper
signatures at Gate A and test all three existing shapes positively in B/N.
Unqualified/missing/failed/invalid services refuse actionably before collection.add;
never omit vectors and invoke Chroma's default embedder. This is the existing
capability-refusal rule, not retirement of duck-typed callers. Public/dry-run
reads still need admission; disabled module mutations remain disabled. No new
CLI fallback or automatic model.

**PASS — design/source feasibility.** synthesizer.py:697 accepts embed_query/embed/callable and can return None; collection.add at795 otherwise invokes implicit backend behavior. Qualified shared wrapper supplies once-only document preparation and explicit refusal, retaining public forms. Source and B/N/R disposition: I14; corresponding consumer rows also apply transitively. The annex537–576 names required actual public nodes and normal/-O installed lanes; these are future proof, not executed evidence. Allowed purposes are REM1227–1267; no wider edits inferred.

### FC-06

Request criterion: Independently assess the complete FC-06 normative contract, actual source path/route/classification, exact scope and B/N/R success/refusal/install proof. Locate all mapped mandatory/high-medium requirements; do not infer closure from a controller map.

Normative criterion (exact current annex text):

**FC-06 — extraction, background ownership and consolidation.** These
are separate paths and need separate witnesses. In maintained MemoryExtractor
storage, typed readiness/identity/provenance/overflow/invalid-result refusals at
entity/relationship, edge embedding, insight batch/fallback or summary boundaries
must surface as failed extraction (typed raise or result.error), including mixed
partial outputs. Never turn a failed edge embedding into a vectorless edge.
An absent edge vector is allowed when no edge embedder is configured, not when
a configured service refuses. Known guard errors do not enter per-item fallback;
retain unrelated non-guard fallback/error policy. Count only actual persistence;
false/incomplete persistence returns cannot acknowledge the output as stored.
Keep the existing stable insight/summary IDs and upsert semantics, graph dedup
and partial-state reporting; do not promise a new all-or-nothing transaction.
Prompts, ontology and extraction LLM selection stay unchanged.

Chat _extract_turns keeps the failed/unprocessed turns in pending_extraction and
does not mark them completed. Preserve its existing cancellation/commit-completed
distinction. Successful retry uses the same output-slot identities; test against
duplicate records instead of claiming full semantic exactly-once extraction.

Memory ContextAssembler owns the actual inner task it starts for
extract_context(async_execution=True), consumes its result/exception and retains
per-turn queued/running/completed/failed-retryable/cancelled/skipped-unavailable
status. Keep the existing method signature and None return; add only a typed
read-only status/wait capability on the concrete Memory assembler, not a new Core
requirement for custom context engines. Telemetry-disabled callers can inspect
that status; a scheduling/turn_archived event is not extraction completion.
Retain active task handles to completion, bound terminal-state retention to the
session lifetime, and drain/cancel-and-await owned tasks before closing their
extractor/sink during existing Runtime shutdown. Do not let the Agent's outer
wrapper's return acknowledge the inner task. No-extractor is an explicit skip;
failed work remains eligible for an explicit later call. Close first shuts
task admission, then drains/cancels-and-awaits owned work before sink disposal.
A late Agent outer task calling an already closing/closed assembler records
skipped-unavailable, starts no extraction and cannot reopen a sink/resource.
Test that delayed scheduling race explicitly; set_extractor cannot revive a
closed instance. No new automatic retry,
queue, scheduler, durable journal or Agent public signature is introduced.

MemoryConsolidator remains public-unwired. Persist a successful batch summary
before acknowledging its source turns; failed batches remain retryable, mixed
batches acknowledge only successful work and report failure. Preserve its
prompts, batching, deduplication and scheduling.

**PASS — design/source feasibility.** extractor broad catches at583/602/665/678/698 and outer error mapping457 require typed aggregation. Chat _extract_turns already requeues on error; preserve stable slot upserts. ContextAssembler.create_task at420 discards task; Agent wraps another task at500. Status/drain belongs to concrete assembler, late admission closed before drain, telemetry off. Source and B/N/R disposition: I08; corresponding consumer rows also apply transitively. The annex537–576 names required actual public nodes and normal/-O installed lanes; these are future proof, not executed evidence. Allowed purposes are REM1227–1267; no wider edits inferred.

### FC-07

Request criterion: Independently assess the complete FC-07 normative contract, actual source path/route/classification, exact scope and B/N/R success/refusal/install proof. Locate all mapped mandatory/high-medium requirements; do not infer closure from a controller map.

Normative criterion (exact current annex text):

**FC-07 — lifecycle truthfulness.** In non-dry-run mode count promotion,
demotion/reactivation only after successful mutation, respecting false returns
as failures as well as exceptions. Preserve prospective dry-run counts. Keep
partial results and errors visible through both structured results and ordinary
public lifecycle-tool `execute()` text. Do not bury errors solely in `data` while
displaying completed counts. Preserve thresholds/order and generic Tools APIs.

**PASS — design/source feasibility.** promotion.py increments after awaited calls without consistently using false return. FC07 requires success-only counters and public text errors, without threshold/order changes. Source and B/N/R disposition: I13; corresponding consumer rows also apply transitively. The annex537–576 names required actual public nodes and normal/-O installed lanes; these are future proof, not executed evidence. Allowed purposes are REM1227–1267; no wider edits inferred.

### FC-08

Request criterion: Independently assess the complete FC-08 normative contract, actual source path/route/classification, exact scope and B/N/R success/refusal/install proof. Locate all mapped mandatory/high-medium requirements; do not infer closure from a controller map.

Normative criterion (exact current annex text):

**FC-08 — actual recall and injectable graph scoring.** Typed shared
readiness/space/provenance/overflow/invalid-vector errors propagate through actual
recall/query (including recall asyncio.gather return_exceptions unpacking),
CollectionManager.get_all gather, _retrieve_graph_with_scoring exception handling,
controller priming/fetch,
_fetch_recent_insights, _fetch_recent_summaries and get_insights_by_author.
Preserve unrelated partial-read warnings/degradation and cancellation. Public
tools may adapt refusal to explicit failure/unavailable, never empty successful
ContextPayload. FC-06 covers actual background completion/acknowledgement.

Neither maintained Chat nor Runtime composition injects GraphPathScorer. Keep
their ordinary graph retrieval UNSCORED: it does not compare stored graph
vectors and gains no vector-provenance preflight for an unused scorer. Stored
graph vectors are maintained write/preserve state for extraction, REEMBED and
recovery; guard those writes/snapshots. Both synchronous filter_paths_sync and
async scoring/fallback are public-INJECTABLE APIs only. On explicitly injected
comparisons, validate compatible query/stored-vector identity; an existing
foreign/unknown/invalid vector fails the semantic operation BEFORE any fallback
or comparison; it must never be replaced. Validate every present component first.
For genuinely absent edge/target vectors, sync scoring and async WITHOUT a
supplied fallback keep zero contribution for that missing component. Async WITH
the caller-supplied qualified embedding_fn retains existing on-demand document-
role fallback for ONLY the missing components, then scores the returned vectors.
Preserve edge/target text construction, weighting/order/thresholds and error/
cancellation propagation. Fallback is transient scoring, not stored backfill.
Test score_path/filter_paths AND their sync variants with edge-only/target-only/
both absent, once-only preparation, exact fallback call counts and nonzero
aligned component scores; R covers invalid present vectors and fallback errors. No scorer/fallback/backfill is newly wired. Require
actual Chat/Runtime spies proving ZERO graph-vector comparisons alongside public
injected-scorer B/N/R capability tests, clearly labelled as different proofs.

**PASS — design/source feasibility.** Controller construction omits graph_scorer in both roots. Its sync injectable path and public scorer async fallback are distinct. Present-vector validation must precede edge fallback even if only target is invalid; absent edge/target use exact legacy text, transient output and no backfill. Source and B/N/R disposition: I06; corresponding consumer rows also apply transitively. The annex537–576 names required actual public nodes and normal/-O installed lanes; these are future proof, not executed evidence. Allowed purposes are REM1227–1267; no wider edits inferred.

### FC-09

Request criterion: Independently assess the complete FC-09 normative contract, actual source path/route/classification, exact scope and B/N/R success/refusal/install proof. Locate all mapped mandatory/high-medium requirements; do not infer closure from a controller map.

Normative criterion (exact current annex text):

**FC-09 — Runtime profile matrix and concrete ephemeral isolation.**
Preserve public MemoryProfile/factory shapes. FULL uses persistent vector/lifecycle
collections and graph; VECTOR_ONLY uses persistent vector/lifecycle collections
and NullGraphStore. Both require explicit open intent/admission. EPHEMERAL and
TESTING use in-memory front and lifecycle stores with one identity/incarnation
per kernel, never PersistentClient/default disk roots.

Do not assume two Chroma EphemeralClients are isolated: the pinned backend shares
one in-memory system. Namespace every Chroma-backed in-memory physical collection
with the kernel's unique incarnation, carrying the same scope through front,
short/long/decayed/MCP collections and admission. Keep logical configured base
names/API semantics; internal suffixed names must satisfy backend constraints.
Per-kernel clear/close deletes only owned collections and never resets the shared
system or another kernel. Two kernels with different identities and the same
logical names in one process must not share records/query results or dimension
state. This is profile isolation, not a security or new profile-system promise.
Per-kernel tenant/database isolation is a documented alternative, but this unit
chooses incarnation-scoped collection names. Gate A freezes its exact encoding,
backend name-length limits and cleanup checks; do not mix the approaches ad hoc.
Transcript persistence stays independently configured; Memory profile does not
enable/disable it. No Memory-caused graph/transcript-parent mkdir on refused or
ephemeral Memory paths. Isolate independent transcript effects in no-disk tests.

**PASS — design/source feasibility.** Core front factory uses SimpleVectorStore for EPHEMERAL/TESTING, but Runtime CollectionManager still gets chroma_path for all profiles at di.py:292. FC09 fixes that direct profile adaptation, choosing per-incarnation collection suffixes, not a new profile system. Source and B/N/R disposition: I23; corresponding consumer rows also apply transitively. The annex537–576 names required actual public nodes and normal/-O installed lanes; these are future proof, not executed evidence. Allowed purposes are REM1227–1267; no wider edits inferred.

### FC-10

Request criterion: Independently assess the complete FC-10 normative contract, actual source path/route/classification, exact scope and B/N/R success/refusal/install proof. Locate all mapped mandatory/high-medium requirements; do not infer closure from a controller map.

Normative criterion (exact current annex text):

**FC-10 — configuration and CLI origin.** Apply B01–B08, including divergent
Chat legacy hint versus actual pool default. Retain raw explicit-origin from
YAML/environment/constructor before default merging or dataclass forwarding.
An explicitly supplied literal equal to the default qualifies as explicit;
a fallback value passed internally by FridayConfig does not. Use an internal
typed origin/sentinel handoff without removing existing caller arguments or
inventing a new public YAML knob. If origin cannot be preserved for a maintained
constructor shape, stop and reconcile instead of assuming it was explicit.

**PASS — design/source feasibility.** FridayConfig chroma_path default_factory and unconditional forwarding erase constructor/default origin today. Typed private sentinel/origin is explicitly required before merging; literal equal to default counts explicit. Chat pool default ignores embedding hint today and remains so. Source and B/N/R disposition: I23; corresponding consumer rows also apply transitively. The annex537–576 names required actual public nodes and normal/-O installed lanes; these are future proof, not executed evidence. Allowed purposes are REM1227–1267; no wider edits inferred.

### FC-11

Request criterion: Independently assess the complete FC-11 normative contract, actual source path/route/classification, exact scope and B/N/R success/refusal/install proof. Locate all mapped mandatory/high-medium requirements; do not infer closure from a controller map.

Normative criterion (exact current annex text):

**FC-11 — maintenance admission, probe and dimensions.** Admitted namespace
identity precedes ALL real provider probes, including the synthesizer/chat LLM
probe as well as embedding probes. Embedding probes use the shared guard; refused
rows make no LLM/provider/model call, not merely zero embedding calls.
For empty fresh collections use the admitted identity's expected dimension;
observed stored rows, when present, must agree. Do not infer a model from rows.
Graph-only REEMBED with empty collections must support a compatible identity.
Respect the existing VectorCollectionDimension8192 ceiling: Gate A qualifies
selected model/operation combinations against it, otherwise stops before
construction/provider effects. Do not silently expand that schema or globally
disable unrelated independent services. Freeze a positive variable-dimension
test plus same-dimension different-space and over-ceiling negatives.

**PASS — design/source feasibility.** Chat provider probe atmutation.py:108 is a real LLM call as well as embedding probe157. Memory mutation._collection_dimension returns None on empty records; admitted expected dimension must supply that case and graph-only REEMBED, retaining8192. Source and B/N/R disposition: I15; corresponding consumer rows also apply transitively. The annex537–576 names required actual public nodes and normal/-O installed lanes; these are future proof, not executed evidence. Allowed purposes are REM1227–1267; no wider edits inferred.

### FC-12

Request criterion: Independently assess the complete FC-12 normative contract, actual source path/route/classification, exact scope and B/N/R success/refusal/install proof. Locate all mapped mandatory/high-medium requirements; do not infer closure from a controller map.

Normative criterion (exact current annex text):

**FC-12 — headless counting dependencies.** Put selected exact local counter
dependencies in a narrow LLM `embedding-limits` extra, frozen after Gate A.
Memory requests that extra on its existing pinned LLM dependency, so Runtime,
CLI and Agent memory consumers inherit it without Docling. Keep existing Memory
tiktoken behavior until exact overlap/dependency resolution is proved. A direct
LLM embedding consumer requests that extra or injects an equally qualified
capability; plain LLM-only imports/configuration remain usable without it.
Missing assets/dependencies refuse only affected embedding execution actionably;
no first-use downloads. Core/Commands/plain Tools reads gain no document stack
requirement. Actual minimal installed profiles must prove these edges. Invoke
Runtime's real _friday_tools_catalog pkgutil/import discovery without Docling/OCR;
its normal Memory dependency still supplies the counter extra. Separately test
optional-package absence in a private copied-prefix import control with counter
and document packages unavailable. Clearly label that as an import/dependency
failure control, not a supported fully resolved Runtime installation. Tool
modules, including the new document reader and embedding-limits module, must
remain lazy; unsupported execution fails actionably. A synthetic registry is
not proof of the actual catalog import path.

**PASS — design/source feasibility.** Memory currently declares plain LLM plus tiktoken; Runtime transitively uses Memory. LLM embedding-limits extra plus Memory requesting it covers headless without Docling. Actual tool_loading discovery imports every module: laziness is a real requirement, not a synthetic registry proof. Source and B/N/R disposition: I25; corresponding consumer rows also apply transitively. The annex537–576 names required actual public nodes and normal/-O installed lanes; these are future proof, not executed evidence. Allowed purposes are REM1227–1267; no wider edits inferred.

### FC-13

Request criterion: Independently assess the complete FC-13 normative contract, actual source path/route/classification, exact scope and B/N/R success/refusal/install proof. Locate all mapped mandatory/high-medium requirements; do not infer closure from a controller map.

Normative criterion (exact current annex text):

**FC-13 — indirect consumers and inspection.** Add actual agent tools,
archive/background extraction, Runtime multi-agent controller/coordinator,
MCP publication and MEMQ stats/records/list-ingested to the trace table. Preserve
public contracts, authorization visibility, durable receipt ownership and honest
partial failure. Store-only inspection of an admitted namespace works with
inference unavailable; unavailable state projects an explicit unavailable result,
not initialized clients or false empty success. Public legacy preprocessing can
remain callable but its output is not evidence of the common chunk plan, and it
must not split an already accepted plan a second time. Public injectable Tools
maintenance/reset/graph/vector inspection wrappers join actual-call tests. Keep
existing confirmed-reset semantics and scope; before any clear, shared store-only
admission validates the whole target layout. Refusal precedes graph/vector/
episodic effects, without a new rollback guarantee for unrelated later errors.
The VectorInspectionTool no-query get_all branch receives positive coverage.
Its query branch already calls a nonexistent vector.search method; record it as
FU-013 under O-05, retain the pre-existing failure, give it NO positive semantic-
query credit and do not fix it incidentally. Other working actual semantic-query
APIs still need B/N positives. Successful reset retains the namespace binding; never implement model migration
or erase the sidecar. Maintenance wrappers expose actual errors/partial results,
not unconditional completed text. Legacy Chat execute methods stay disabled;
their admitted dry-run and maintained coordinator path are separately tested.
RetrievalFactorComputer, AccessBuffer.flush_all and IncrementalGraphMaintainer
remain source-unchanged metadata algorithms. Construct them only after admission
with guarded live handles, no embedding inference. Existing result.errors/partial
counts and WAL/queue retention remain; Chat adapters must inspect/project these
errors, including incremental maintenance, rather than emit unqualified completed
totals. Do not add tokenizer requirements, change thresholds, refresh quiescence
tokens or redesign WAL/commit behavior. Test real metadata-operation refusal and
error projection through the wired Chat maintenance/exit paths. If unchanged
algorithm code cannot preserve those contracts, stop for exact scope correction.
No new automatic wiring or actual user reset is authorized.

**PASS — design/source feasibility.** Tools reset currently graph-clears before vector atmaintenance.py:111; whole-layout admission prevents a newly refused vector store leaving graph cleared. Metadata algorithms expose errors; adapt Chat only, retaining WAL/ordering. Inspection search branch has no matching adapter search method, so FU013 is unwaived and receives no positive credit. Source and B/N/R disposition: I19; corresponding consumer rows also apply transitively. The annex537–576 names required actual public nodes and normal/-O installed lanes; these are future proof, not executed evidence. Allowed purposes are REM1227–1267; no wider edits inferred.

### FC-14

Request criterion: Independently assess the complete FC-14 normative contract, actual source path/route/classification, exact scope and B/N/R success/refusal/install proof. Locate all mapped mandatory/high-medium requirements; do not infer closure from a controller map.

Normative criterion (exact current annex text):

**FC-14 — operational compatibility versus model quality.** Record existing
retrieval/path/pruning thresholds without silently retuning them. B/N deterministic
success/shape/error witnesses prove operational contracts, not semantic quality.
When a real replacement is selected, require a separate bounded relevance and
false-duplicate evaluation/UAT on disposable fixtures before accepting that model.
Define measures and acceptable results in that later model-readiness envelope;
do not claim quality parity or tune thresholds using invented evidence now.
Qwen4B remains illustrative.

**PASS — design/source feasibility.** Operational B/N shapes and successes do not establish relevance or duplicate quality. Existing thresholds stay unchanged; later model-specific evaluation/UAT needs its own measures and acceptance envelope. Source and B/N/R disposition: I01; corresponding consumer rows also apply transitively. The annex537–576 names required actual public nodes and normal/-O installed lanes; these are future proof, not executed evidence. Allowed purposes are REM1227–1267; no wider edits inferred.

## Correction/advisory requirements independently judged

The correction map supplied requirement locators only. Its source IDs were not treated as peer findings or correctness proof. Every row below was judged from current normative text and source, with B/N/R obligations in the corresponding FC and inventory rows.

| Requirement | Independent assessment | Evidence |
|---|---|---|
| INGEST-EC-01: Startup rejection logging can pre-create or mutate a vector directory | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-01 assessments, inventory and exact criterion evidence above |
| INGEST-EC-02: Active opt-in MCP snapshot ingestion is omitted from the route contract | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-02 assessments, inventory and exact criterion evidence above |
| INGEST-EC-03: Public physical backup/restore can bypass binding and overwrite a sidecar | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-03 assessments, inventory and exact criterion evidence above |
| INGEST-EC-04: ConsistencyAnalyzer opens SQLite and graph data outside normalized admission | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-04 assessments, inventory and exact criterion evidence above |
| INGEST-EC-05: Legacy synthesis can omit vectors and invoke an implicit Chroma embedder | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-05 assessments, inventory and exact criterion evidence above |
| INGEST-EC-06: Consolidation can acknowledge source turns after summary-storage refusal | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-06 assessments, inventory and exact criterion evidence above |
| INGEST-EC-07: Lifecycle counts and tool text can report failed mutations as success | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-07 assessments, inventory and exact criterion evidence above |
| INGEST-EC-08: Recall can suppress typed refusals; async graph fallback is not maintained wiring | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-08 assessments, inventory and exact criterion evidence above |
| INGEST-EC-09: Runtime ephemeral/testing profiles still construct persistent lifecycle collections | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-09 assessments, inventory and exact criterion evidence above |
| OPUS-A1: Actual canonical Chat default versus legacy hint, preserved and visible. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-10 assessments, inventory and exact criterion evidence above |
| OPUS-A3: B01–B08 qualified identities with absent/placeholder revisions and alias-swap refusal. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-10 assessments, inventory and exact criterion evidence above |
| OPUS-A4: Namespace admission before real provider probe. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-11 assessments, inventory and exact criterion evidence above |
| OPUS-A5: Preserve CLI raw explicit-origin across default forwarding. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-10 assessments, inventory and exact criterion evidence above |
| SOL-R5-A02,OPUS-A6: Actual transitive agent/multi-agent/MCP coverage and namespace distinction. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-13 assessments, inventory and exact criterion evidence above |
| ASTRA-R5-A02,OPUS-A8: Declared dimension ceiling and identity-based empty-store behavior. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-11 assessments, inventory and exact criterion evidence above |
| OPUS-A10: Headless counter extra/dependency profile without Docling. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-12 assessments, inventory and exact criterion evidence above |
| OPUS-A7: Admitted store-only MEMQ reads without inference. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-13 assessments, inventory and exact criterion evidence above |
| OPUS-A2: Operational compatibility versus later measured quality evaluation. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-14 assessments, inventory and exact criterion evidence above |
| OPUS-A11: Public-unwired preprocessing never a second stored chunk plan. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-13 assessments, inventory and exact criterion evidence above |
| IC-01: Retain public create and same-incarnation identity-safe restore; no class/API retirement or generic bridge. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-03 assessments, inventory and exact criterion evidence above |
| IC-02: Own actual ContextAssembler task/status and drain at existing Runtime shutdown; preserve Agent/Core signatures. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-06 assessments, inventory and exact criterion evidence above |
| IC-03: Real Chat MCP observer/receipt failure mapping, narrow memory_mcp.py scope. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-02 assessments, inventory and exact criterion evidence above |
| IC-04: Per-owner admitted rejection sink with lifecycle/reconfiguration; no global fan-out. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-01 assessments, inventory and exact criterion evidence above |
| IC-05: Both graph scorer APIs are injectable only; actual Chat/Runtime unscored route gets no unused-vector preflight. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-08 assessments, inventory and exact criterion evidence above |
| IC-06: Typed extraction refusal surfaces before completed acknowledgement; stable-ID retry and truthful mixed output. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-06 assessments, inventory and exact criterion evidence above |
| OPUS-R6-A1: Per-incarnation physical ephemeral collections despite shared Chroma system. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-09 assessments, inventory and exact criterion evidence above |
| OPUS-R6-A2: Name get_all/priming/author read catch seams and typed propagation. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-08 assessments, inventory and exact criterion evidence above |
| OPUS-R6-A3: Explicit public Tools wrappers and disabled Chat legacy/dry-run dispositions. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-13 assessments, inventory and exact criterion evidence above |
| OPUS-R6-A4: Actual Runtime pkgutil module catalog minimal-install witness. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-12 assessments, inventory and exact criterion evidence above |
| OPUS-R6-A5: Qualified shared-guard wrapper route for all retained callable shapes. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-05 assessments, inventory and exact criterion evidence above |
| OPUS-R6-A6: Admission before LLM synthesizer probe as well as embeddings. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-11 assessments, inventory and exact criterion evidence above |
| OPUS-R6-A7: Current next-decision authority and pass count reconciled. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | EC-01 assessments, inventory and exact criterion evidence above |
| OPUS-R6-A8: Do not activate inert Chat rejection-log setting. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-01 assessments, inventory and exact criterion evidence above |
| OPUS-R6-A9: Early visibility of hosted baseline immutable-identity feasibility stop. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-10 assessments, inventory and exact criterion evidence above |
| OPUS-R6-A10: Read-only transcript SQLite as well as Chroma. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-04 assessments, inventory and exact criterion evidence above |
| IC-07: Missing vectors: zero only for sync/async without fallback; retain qualified async fallback on absent components and reject invalid present vectors first. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-08 assessments, inventory and exact criterion evidence above |
| IC-08: Keep pending records after partial/ambiguous failure/cancellation and same-ID no-extra-embedding retry; no newly automatic discard. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-02 assessments, inventory and exact criterion evidence above |
| IC-09: Use existing telemetry reason literals directly in the Chat memory_mcp observer union; real processor/provider forwarding stays unchanged and is tested. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-02 assessments, inventory and exact criterion evidence above |
| IC-10: Restore exactly35 historical Next gate lines from8d25d53a; only current gate changes subsequently. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | EC-18 assessments, inventory and exact criterion evidence above |
| IC-11: Minimum new-binding evidence/admission and marker protection while preserving old backup file/default behavior; pre-existing vector/split completeness limitations recorded as FU014, with paired baseline proofs and no complete-recovery credit. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-03 assessments, inventory and exact criterion evidence above |
| OPUS-R7-A1: Name scored-graph except and recall gather typed-failure seams. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-08 assessments, inventory and exact criterion evidence above |
| OPUS-R7-A2: Close task admission before drain; late outer Agent arrival skips unavailable, no reopened sink. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-06 assessments, inventory and exact criterion evidence above |
| OPUS-R7-A3: Default no-file owned sink vs standalone logger separation; both inert Chat flags remain inert. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-01 assessments, inventory and exact criterion evidence above |
| OPUS-R7-A4: Explicit mutation.py empty dimension/graph-only FC11 purpose. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-11 assessments, inventory and exact criterion evidence above |
| OPUS-R7-A5: Wired metadata factor/access/incremental consumers, unchanged algorithms and explicit error projection. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-13 assessments, inventory and exact criterion evidence above |
| OPUS-R7-A6: Existing VectorInspectionTool query/search mismatch gets FU013/no positive credit, no incidental repair. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-13 assessments, inventory and exact criterion evidence above |
| OPUS-R7-A7: Collection suffix isolation chosen; tenant/database alternative not mixed in ad hoc. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-09 assessments, inventory and exact criterion evidence above |
| OPUS-R7-A8: Trace existing MCP constructors to the CollectionManager shared guard; no separate MCP counter/preflight protocol and no provider requirement for store-only reuse. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | FC-02 assessments, inventory and exact criterion evidence above |
| OPUS-R7-A9: Mark old round1–4 authority historical/superseded. | Sufficient proposed requirement; actual route and causal boundary independently checked above; no executed closure claim. | EC-01 assessments, inventory and exact criterion evidence above |
## Exact future public / installed / mutation witnesses

1. Graph score_path/filter_paths and both sync variants: present compatible vectors positive; edge-only absent, target-only absent, both absent. Sync and async-without-fallback missing contributions=0 and fallback calls=0. Qualified async fallback calls=1/1/2 respectively, exact edge/target strings, once-only document preparation and nonzero aligned scores. Invalid present edge OR target (including present-invalid target with absent edge) fails before fallback calls=0. Maintained Chat/Runtime comparisons=0, with no unused provenance preflight. No new wiring/backfill.

2. Real persist_mcp_interaction/TurnProcessor/Runtime provider: false/ambiguous append/readback/cancellation/publication and later mixed-call preparation failure retain exact owned pending ID/content. Retry same entry/call has same ID, row count and embedding-write count; publish only verified receipt. Capacity maps capped, readiness unavailable, identity/provenance rejected, result invalid_result, storage execution_error, ownership blocked. Old four literals unchanged. AST subset calculation passed (reason-subset.json); actual enabled event validation and disabled export counters remain future. Observer exceptions remain nonauthoritative; noncapacity failures never receive successful skip receipts.

3. Physical public BackupManager create/verify/restore plus module backup, Reorganizer backup_first and Tools wrapper need paired baseline/candidate disposable working fixtures. Compare old destinations/API/member sets, data and queryability where baseline actually works, new minimal receipt and unchanged live marker. D versus D/vector selector must admit exactly one ready marker; dual/absent/pending/malformed and mismatched receipt fail before effects, even verify_first=False. No repair or credit substitution for FU014; logical-v2 full recovery remains separate.

4. Real Agent archive→ContextAssembler delayed inner task: observable completion/failure with telemetry disabled; close admission before drain/cancel/await; late outer task cannot reopen. Chat _extract_turns retains failed/unprocessed work and stable output IDs; mixed batch acknowledges only persisted results. Rejection sinks cover two owners, no-path owner after standalone setup, failed construction/reconfigure/close and independent qualified destination.

5. Real metadata maintenance/exit and public wrappers must project errors/partial counts with original algorithms/WAL intact. All four Runtime profiles, two in-process kernels with same logical names/different dimensions, per-incarnation collections and independent transcript settings. Empty admitted dimensions/graph-only REEMBED positive, >8192 refusal and admission-before-LLM-probe negative.

6. B01–B08 with both new fields omitted, divergent Chat hint/default, explicit constructor/env equal-default origin and implicit fallback distinguishers. Real Runtime pkgutil catalog and headless Memory/Runtime/CLI/Agent/direct-LLM-extra supported installs without Docling; optional-absence copied-prefix control is not a supported Runtime install. Four genuine formats/OCR, all-source text shared plans and independent TD01–10 consumer proofs, post-all-install Certifi version/origin floor accepted/rejected controls.

All representative FC01–13 and full B/N operational round trips run in actual normal and optimized installed lanes, canonical imports/origins and hash provenance. Named call-phase mutants must kill guard bypass, wrong-role/double preparation, same-dimension identity substitution, malformed result/index, cache/destination bypass, swallowed refusal, false acknowledgement/count, namespace fallback, marker overwrite, missing late source content and Certifi below-floor verification. Setup/import/collection failure earns zero rejection credit. Gate A must freeze exact nodes/call counts/oracles; no product execution was done here.

## Reproduced checks, pins and conduct audit

Request hash was verified BEFORE reading request: `0b9247701339f8fe25dce08d70ec08e8785fbe20c01ea1f4054bc4c51a0a202d`. Helpers were statically inspected and hashes matched before invocation:

- check_integrity.py: `6ef846532b6caab0c136b50dc9bde1da1816e72742eef6e0522c4e37a36fe9ca`
- read_only_command.py: `cb0669f81efd0098c104d7b96342fcd614255021ea2bfa49cbbb6af7c2fea248`
- extract_current_controls.py: `a9fd727a2d9715e5b6759034c4bb92160993bd6d0b23efedcea6211f978e4b81`
- frozen current-controls.json: `ea18945e10dfd7cb67e12daf2a85f174d98a644e1b279223e92dca82366620e8`

The extractor ran through the wrapper (exit0), and output bytes exactly equal frozen sanitized controls. Whole authority.json was never opened/searched by reviewer; only approved helpers read/hash it. Both opening/closing helper runs exit0 PASS, same HEAD/branch/logical index `d5b9549f8299653d66f6890c54af31f072a63687088a369be3dff0fac9be5e8d`, all17689 protected entries and six preserved metadata records match; staged diff empty and status exactly frozen. Logical index is measured before status by the inspected helper.

Every Git/admin command including helper children used `python3 -B INPUTS/read_only_command.py OWN -- ARGV`; full exact invocations and exits are in command-audit.jsonl. UV was offline/frozen/no-sync/no-python-downloads with private UV/XDG/TMP roots. Exact five checks:

- `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` — exit0; `board.txt`.
- `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check` — exit0; `dashboard.txt`.
- `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py` — exit0; `docs.txt`.
- `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py` — exit0; `metadata.txt`.
- `git diff --check 91ac63bad5e46eceddd252d5b7727f7a1d3c623a..f43368c503da19fd245730ee579806db95ed3748` — exit0; `whitespace.txt`.

Fresh deterministic document checks: all35 historical Next gate lines byte-identical to8d25d53a after excluding first/current line in each doc (README1, next-phase17, tactical-plan17); final repeated byte-line comparison agrees. Proposed observer literal set subset of existing MCPEventReason via static AST: true. Selected source aggregate diff --stat exit0 with empty output.

Authority/document/source pins were all reproduced by both integrity runs, not merely inspected receipts. Complete hash manifest follows; it includes exact reviewed authority, REM, annex, Tools and seeded source bytes. Discovery extends beyond those pins.

| Category / path | SHA256 |
|---|---|
| authority_pins: AGENTS.md | `9c2840ea92bf5f25acd5c85d36a18d2c7d9677c0768d1e811aef5efde6fc936b` |
| authority_pins: docs/reference/policies/repository-engineering-policy.md | `17b830b8990f74d1b0a25a46fc2cf2f62249f4e0d668f45b96cfe03a6cc76aff` |
| authority_pins: docs/reference/policies/development-task-lifecycle.md | `2c0241fd353145a4704699e69000dd8c4bd8404cb616e224fe77dee03165d844` |
| authority_pins: docs/reference/policies/independent-validation-policy.md | `4d951418e0f0c96a4c87d4b8a07cb4025dd94738da50893d19a6d2b7a7f82f4a` |
| authority_pins: .agents/skills/council/SKILL.md | `360493507c5f522d4a365f7f90f76c7eb37ad31ee36096a359c0715aae00b23c` |
| authority_pins: .agents/skills/independent-code-validator/SKILL.md | `578fe10d00df438be8c0dc2537ee08c08c3361ebb3615db0fd17e148b928f508` |
| authority_pins: docs/planning/active/command-refactor/scope-decisions.md | `6760092e9d7b4f38a0e96d8109fde0e95cd8c3db0aeaf05c927801243dccb749` |
| authority_pins: docs/planning/active/command-refactor/approval/ingest-existing-store-policy.md | `3a9343e77d97e2d8b94ebab2d2fa8fb3c3c339b1c4a37c32899de86e58139668` |
| authority_pins: docs/planning/active/command-refactor/validation/document-ingestion/compatibility-iteration-authorization.json | `27e55b58ce1b63e2c835e6ecc060f10bbf940610eb0e493be2556785cd249d30` |
| document_pins: docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md | `e1c90753a3e2876df0f9f6f0ca82b1893455266cee1f252276f460b48a9f2a16` |
| document_pins: docs/planning/active/command-refactor/embedding-compatibility-contract.md | `1092a332684e3f6a5f9edc3f2355c768775b0f2c01b82bcc97242932334faabb` |
| document_pins: docs/planning/active/command-refactor/proposals/tools-document-adoption.md | `8220e195f7b9b899fb377f5550920a3d9ac0699b33293a59c366ff6d2fa6d998` |
| document_pins: docs/planning/active/command-refactor/README.md | `0ad3d3a7669316e232f71c1cf0b5d2905d833ebd84ad98288a6dc1891a1347f7` |
| document_pins: docs/planning/active/command-refactor/next-phase.md | `4d3db3b9591b348b815b1a0d49eea1c1eee29f291a09f4ec72df375b2d081d03` |
| document_pins: docs/planning/active/command-refactor/tactical-plan.md | `35c6e22343ce966e4e075aabaa56441348e69f8439dd79bf4be3c3a9bf1b2e62` |
| document_pins: docs/planning/active/command-refactor/authority.json | `6643f7666d2960400a620a5970cc82e426b6826d0d17b2231a65240a801d5c85` |
| document_pins: docs/planning/active/command-refactor/execution-log.md | `7a6a91b08815bb69d5882ba057d4f843b663100dc7e6ec31fcc580b180f24296` |
| document_pins: docs/planning/active/command-refactor/validation/document-ingestion/compatibility-correction-map.json | `a7a245853ae3a188e5871caef4be1258995df8981213234c95e43e687738e890` |
| document_pins: docs/planning/active/command-refactor/validation/document-ingestion/branch-handoff.md | `b5d65613839e3ab189fe3593b90e18708ba919bca89400cd765799036dd88c3f` |
| document_pins: docs/planning/active/command-refactor/validation/document-ingestion/gate-a-handoff.md | `7e53867673df699fe7f3c668f2f853cb1a64cd01942420f19006276771585161` |
| document_pins: docs/planning/board.yaml | `16f3564f058df8314684d6a62871b4c3cb38b770c30e5a6edcf705bae6dbdcf0` |
| document_pins: docs/planning/README.md | `f614eb60dbdf3c70041fb8993b4fa188675d241ed3788a2628dac5e83b0ecbe7` |
| document_pins: docs/planning/backlog/friday-chat-framework-followups/upgrade-log.md | `9c5b87f1fe314b1870f36307b8f63ff8a7413db494d5139f01b057c0c29e6e63` |
| source_pins: packages/friday-agent/src/friday_agent/base.py | `506640728f5605ac0d5c1478b052468d498ac352b939627fb0d801e304808e88` |
| source_pins: packages/friday-chat/src/friday_chat/adapters.py | `90488c278666379825b8d971eae0a931fcc4ef4230b7a2e16fcb81aa9cc67b9d` |
| source_pins: packages/friday-chat/src/friday_chat/config.py | `734559482073fa66b2197604136d4fde805fc8f9e4ce7078f33df57c4a3c52d1` |
| source_pins: packages/friday-chat/src/friday_chat/memory_mcp.py | `62eeb681b0dbb08b154951ee401d77878a1c64053b6a16fee89991d8a547b287` |
| source_pins: packages/friday-chat/src/friday_chat/reorganization/mutation.py | `8e3321d40d452f4877d397d40f6afccf2a549a91401d21ecd8b10f95d9e60d6a` |
| source_pins: packages/friday-chat/src/friday_chat/runtime.py | `7a0003b0657e408261024be619a903f400f8e2f2f15533aa8392bd6ac904e6a2` |
| source_pins: packages/friday-chat/src/friday_chat/turns/processor.py | `8238bbb873b41b0d7644d3ef34aacba86f4e8f821a83b8d4b7b5cf3d77ccb146` |
| source_pins: packages/friday-cli/src/friday_cli/container.py | `e3cdbdeb320f70ec13c3c153fe692a39abfef8ca5e702f33bb301d53a72aa4ee` |
| source_pins: packages/friday-core/src/friday_core/__init__.py | `5343759de1e349d6060e9258fa336333d83e557273d7c68c84a7f9a913a6ecb0` |
| source_pins: packages/friday-core/src/friday_core/interfaces/__init__.py | `6d1818b41bc6e5aa959aca80658132c2dac94920f68aeb286221e8819c9e5f7b` |
| source_pins: packages/friday-core/src/friday_core/interfaces/llm.py | `8074310103ebbea065e1365afad853026bc379a8157127b5bb350211b127402b` |
| source_pins: packages/friday-core/src/friday_core/interfaces/memory.py | `5082f24ab7dda1a1a77e05702e8874cbd656bcbb19b4dabaa96b531b16ed76ac` |
| source_pins: packages/friday-core/src/friday_core/profiles.py | `8e6bed2bb0d33f9b1fcb18141827e1e8fb9256f0efae88f353f854d8899b6d75` |
| source_pins: packages/friday-llm/src/friday_llm/__init__.py | `df8c538447bb0b1bf2b2d8e2397e4f16b91f9b258088edac4dcddcf33a4403fc` |
| source_pins: packages/friday-llm/src/friday_llm/embeddings.py | `b1e269b28b907ae53189016529a85dbf75127d0754d9175be5d21a6828681a7b` |
| source_pins: packages/friday-llm/src/friday_llm/model_library.py | `754effe6adf32890073866d3192f75bbb7354642c5c32a64df456c22321b6add` |
| source_pins: packages/friday-memory/src/friday_memory/adapters/simple_vector.py | `cf7e817caaec151116ec3c53a1fd3b5cd9fcdf534f5a93063f3976025239dbb5` |
| source_pins: packages/friday-memory/src/friday_memory/adapters/vector.py | `6bf75710cdaa384ac2a371dbe214182f07170fd0a9d2dbe46a7b177bf0907833` |
| source_pins: packages/friday-memory/src/friday_memory/context/assembler.py | `e3dffd72311de5589ea30bc0c1da9d2e90dd01c0d76d9dd86761329e13d952f2` |
| source_pins: packages/friday-memory/src/friday_memory/context/consolidator.py | `d3fe57ce5cc107c29037cb85c6af92fcde2d23c0c47ade2f6575e4f11029e26a` |
| source_pins: packages/friday-memory/src/friday_memory/context/extraction_filter.py | `2e33d85e098a0f0a97e47d30fa7b3fb150d50cef771cfcd692bbef5604028911` |
| source_pins: packages/friday-memory/src/friday_memory/context/extractor.py | `62cc6d0a2afc5d61a094d20978ec5e1d130f781136f9c75b6d3f24901174bb33` |
| source_pins: packages/friday-memory/src/friday_memory/controller/memory_controller.py | `8a5708f323e0066eb982d49d43b6bb1c6fc9eb13c05b78f20718ea145ffe3712` |
| source_pins: packages/friday-memory/src/friday_memory/ingestion/large_file_processor.py | `a125280d7eeacf842d6420e0030d9a76665196a9fa3e8d47d2115fa01e802e0c` |
| source_pins: packages/friday-memory/src/friday_memory/ingestion/mcp.py | `6b8dee3f72da92db4e4f509d9e4f8760db97281534d1c593c0b01774de41054a` |
| source_pins: packages/friday-memory/src/friday_memory/ingestion/tool_ingester.py | `e20502fb54d7288ed4ced51fc206d9a1070addf472ac156fc21a42331eea19e7` |
| source_pins: packages/friday-memory/src/friday_memory/lifecycle/promotion.py | `2c1ab998b1c544767c5873f4c3721a10f66a31d35fc3fa3c585039d95512722c` |
| source_pins: packages/friday-memory/src/friday_memory/maintenance/__main__.py | `8ac55c0734a16d6e139bd36af0d334c207c601fc8f0dbec2452dd32d85b3b8cd` |
| source_pins: packages/friday-memory/src/friday_memory/maintenance/analyzer.py | `521ba2dead1b363f09d3c8227285a2803110e89caa2ab0a470a86fa4f2daa879` |
| source_pins: packages/friday-memory/src/friday_memory/maintenance/backup.py | `ddd37aa5bdcedbaf623321828e26e3af7b1ebbcea9ba041dc0e40b1421ad937b` |
| source_pins: packages/friday-memory/src/friday_memory/maintenance/compactor.py | `9a6cfe5f86098288aa4f9e04ccb11364d0008eaff72ede8a5a16481025aba5cf` |
| source_pins: packages/friday-memory/src/friday_memory/maintenance/fact_checker.py | `6c229c2c2b9c274715a1dd0bd2ac852566e2e73a6a20167ad270cd3b564fada4` |
| source_pins: packages/friday-memory/src/friday_memory/maintenance/incremental.py | `4d590ae009a5f5aefc11dd8cdc16df7db0e9f6f57a3d79e039cec7ef52ec3c8b` |
| source_pins: packages/friday-memory/src/friday_memory/maintenance/mutation.py | `edab173cf190bcfb196392220d33acf3b0d17e7ab9ae7e35b277c2b5efb90f00` |
| source_pins: packages/friday-memory/src/friday_memory/maintenance/pipeline.py | `ab930a859e58a49ef88eb5c7d2b828191737c4dd6ac93cc5483854a919fa7dd0` |
| source_pins: packages/friday-memory/src/friday_memory/maintenance/provider_contracts.py | `7efed92f926bf6f1f45d162b738cbb50edc427e0f99e3a538be668cf34f76121` |
| source_pins: packages/friday-memory/src/friday_memory/maintenance/pruner.py | `a36258551ee3c1d5349ca7579d79f6444b9e48f1817858a2f524563e65d0cf9b` |
| source_pins: packages/friday-memory/src/friday_memory/maintenance/recovery.py | `c8c0b7bff6fac81f2d3146a67915bddcd2aae83a587a8ab19bcd03475cc8f954` |
| source_pins: packages/friday-memory/src/friday_memory/maintenance/reorganizer.py | `98d2ac6db8fd835910c49fcd804ac6bf4d4a02e2534cd2d7f0bde683180e7e2c` |
| source_pins: packages/friday-memory/src/friday_memory/maintenance/synthesizer.py | `44235da056162f223a9f5ee1ede27e565fccba1b653bdd2bd81aaaed7f104b38` |
| source_pins: packages/friday-memory/src/friday_memory/retrieval/access_buffer.py | `145a41177fc2656102fe6aa91f924a71a5822b60543189ae3f399bedc08915d8` |
| source_pins: packages/friday-memory/src/friday_memory/retrieval/collection_manager.py | `41e85080c2b80545f79685da019549d4462f69c9942d7d13db029f99aff8b8de` |
| source_pins: packages/friday-memory/src/friday_memory/retrieval/factor_computer.py | `36b51c84c4fda54e845ff3bc59620322196907dfe6bb2f57ea118e7113f6357e` |
| source_pins: packages/friday-memory/src/friday_memory/retrieval/graph_scorer.py | `339b9c6859af7c2548e470e36f1ed407cd05837e8d78f0a9fe2656275edac1c3` |
| source_pins: packages/friday-runtime/src/friday_runtime/config.py | `cc248bb8b8b4e713deede41d07f0729b699f341f7f05a38304e46b004ed72d0d` |
| source_pins: packages/friday-runtime/src/friday_runtime/di.py | `8085b142495376bab4ad38465bb7bdb267f598c443e4ed2375329ed8fb670f9c` |
| source_pins: packages/friday-runtime/src/friday_runtime/mcp_loading.py | `cbff7cd8a34f4c2811448224e02e9bbc52b54363d1f0654fc81ce729092fc21e` |
| source_pins: packages/friday-runtime/src/friday_runtime/tool_loading.py | `4abcddc568aec149db96a78666b92ec2ed2962a87aa11cc9084950f19f26c2db` |
| source_pins: packages/friday-telemetry/src/friday_telemetry/models/mcp.py | `53f7a172f6a5ec7ed31f72a4fe260e2e4e97c932151a43958b8a4dc6e7641fda` |
| source_pins: packages/friday-tools/src/friday_tools/base.py | `de2e67387d56161b824b577d8e6e4113302beee4f51fc233bdd84db1a4b01254` |
| source_pins: packages/friday-tools/src/friday_tools/filesystem/smart_read.py | `23f514859df4ec0b228e0667187c28650982f3b2e6133d64de898dcfc54e6399` |
| source_pins: packages/friday-tools/src/friday_tools/memory/lifecycle.py | `a76045c4be63b3dce1aba3720a046ba459c39090b47cc7dea5e5374eed0120c7` |
| source_pins: packages/friday-tools/src/friday_tools/memory/maintenance.py | `37ec8d951272621afa74d03613f36afeeac1bb67c49a001e99df86e46829fe81` |

Output audit: fresh OWN is outside checkout and every supplied scratch/input tree. Only own reports, audit records, private caches/temp and static calculation artifacts were written. No worktrees/checkouts/staging/commits/cleanup/.venv writes or shared mutation. No raw old review/report directories or unfiltered historical aggregate diff were opened; historical scores in normal status text were not correctness evidence. No personal configuration/store/export/.friday-old content was read by reviewer. Protected hashing/stat inspection occurred only through approved integrity helper. No browser/web/model/tool-service operations. Closing integrity followed the last shared/input inspection; subsequent report/hash work used only OWN copies. No conduct breach observed.

## Honest score breakdown and next gate

| Coverage rubric | Earned / maximum |
|---|---|
| All-framework direct/transitive consumer coverage | 3.80 / 4.00 |
| Baseline and replacement positive proof coverage | 2.90 / 3.00 |
| Negative identity/overflow/failure-effect coverage | 1.95 / 2.00 |
| Headless minimal-install and nonembedding coverage | 0.95 / 1.00 |
| **Coverage** | **9.60 / 10** |

| Overall rubric | Earned / maximum |
|---|---|
| Framework consumer inventory | 1.90 / 2.00 |
| Operational configuration and API compatibility | 2.90 / 3.00 |
| Model replacement and namespace data safety | 2.40 / 2.50 |
| Bounded proof and reporting | 1.90 / 2.00 |
| Scope and authority | 0.50 / 0.50 |
| **Overall** | **9.60 / 10** |

Deductions reflect residual breadth/dynamic-consumer uncertainty and the amount of exact identity/backend/dependency/public-fixture detail intentionally deferred to the explicit hard-stop readiness gate. They do not presume future installed evidence, waive baseline defects, reward old scores or treat missing unapproved code as a present finding. Current design requirements are sufficient; measured feasibility is still unknown.

Return this single seat to the controller for pass3 reconciliation. Every seat must independently meet its own gate; this report grants no aggregate verdict or authority. At most one further full pass remains, blocked/incomplete passes count, and after pass4 stop for maintainer guidance. No fifth/reissued/replacement seat, GateA execution, construction, new model, reset/migration, MAINT acceptance or delivery is authorized.
