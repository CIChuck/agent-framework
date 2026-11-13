# Independent design/source-feasibility review

Outcome: **CHANGES_REQUESTED**. Coverage **9.4/10**; overall **9.3/10**. One mandatory medium finding, SOL-R7-001. These scores do not satisfy the controller gate and have not been adjusted toward 9.5.

Reviewer: gpt-6.1-sol, high effort, fresh independent review context. Review date: 2026-11-11 UTC (local session date 2026-11-10). No implementation reasoning, parent transcript, raw historical reports, current peer verdicts or nested agents were used. General repository policy and ordinary status prose were read, without treating historical scores as evidence. No procedural memory was consulted.

Candidate f1916747ad7d03e451f2b57dc00542faa6095d7c, branch feature/cmd-ingest-001, workdir /Users/chuckrussell/Dev/gendev/agent-framework. Correction delta 8d25d53ac944ace99e3ae430364075b0c1200ff6..candidate was obtained first, limited to the request's technical/status paths; aggregate base 91ac63bad5e46eceddd252d5b7727f7a1d3c623a. No raw authority history/report directories were opened. Current REM, annex and Tools companion were assessed together against independently discovered source consumers. This is design feasibility, not implementation conformance.

## Authority and boundaries

AGENTS.md, repository-engineering-policy.md, development-task-lifecycle.md, independent-validation-policy.md, council and independent-code-validator skills, scope-decisions.md and ingest-existing-store-policy.md were inspected. Explicit seat instructions override council delegation instructions. Verified current-controls extraction equals frozen controls byte for byte. Authority remains design_only, implementation_approval not_granted, planning/in_review, cycle pass2/4/global round7. Two further passes maximum remain; incomplete/blocked passes count. No reissue, extra seat, construction, Gate A, model swap, reset, MAINT acceptance or delivery is authorized here.

## Mandatory finding

1. **SOL-R7-001 — medium, mandatory: distinguish absent-vector async fallback from zero contribution.** Affected documents: embedding-compatibility-contract.md:314–318 and remediation/REM-CMD-INGEST-001-pdf-docx.md:877–882. Source: packages/friday-memory/src/friday_memory/retrieval/graph_scorer.py:245–264 and :352–358. The public async score_path explicitly calls embedding_fn for an absent edge and/or target vector, then computes cosine similarity from the returned vector. The synchronous route has no fallback. The REM's unconditional statement that genuinely absent vectors retain an existing zero contribution is false for the supported async shape with embedding_fn. FC-08 repeats that statement while also retaining guarded async fallback, leaving incompatible oracles for the same case. The corrected classification of both APIs as injectable is sound; neither Chat nor Runtime currently injects them.

Required narrow fix: qualify zero contribution as the synchronous or async-without-fallback behavior, and explicitly retain guarded document-role fallback for absent vectors only when the caller supplies the qualified async capability. Existing unknown/foreign/invalid vectors must fail rather than be replaced. Reconcile both documents and the named FC-08 proof requirements; do not add wiring, backfill, a scorer requirement for maintained recall, or source implementation in this document correction.

Future public witnesses: call actual score_path/filter_paths and score_path_sync/filter_paths_sync, with edge-only, target-only and both vectors absent. In B and N, async qualified fallback must be called only for the absent components, prepare each document exactly once, and produce the expected nonzero component similarity for aligned deterministic vectors; sync and async without fallback retain zero for absent components. R must reject an existing foreign/unknown/invalid vector before fallback/comparison and propagate fallback overflow/readiness/result errors. Repeat representative public tests in actual normal and -O installed lanes, with actual Chat/Runtime spies separately proving zero graph-vector comparisons. No immediate mocked extractor or lower-layer-only test substitutes for these witnesses. This is EC-07/FC-08 and the exact compatibility obligation, not a demand to execute future tests now.

No other mandatory finding was established. No advisory finding is promoted merely because Gate-A schemas or measured dependencies remain future.

## Independent source inventory and consumer/disposition matrix

Discovery used explicit packages/*/src roots, textual searches and a standard-library AST inventory (source-inventory.json). It scanned 442 Python files across the 18 source roots, including the empty TUI src root. Static name matching is not a proof of arbitrary dynamic plugin behavior: the real Runtime catalog installed witness remains required. The inventory is independent of the annex labels. Paths below are relative to the frozen repository. B/N/R cells are required FUTURE witnesses, not executed results. B means unchanged configuration fields omitted plus qualified baseline and admitted namespace; N includes changed dimension, same dimension/different space or preparation, and smaller capacity; R includes identity, readiness, overflow, result and storage refusal.

| Consumer and source | Actual disposition / allowed purpose | B and N successful witness | R / effect boundary |
| --- | --- | --- | --- |
| LLM model_library.py:287; embeddings.py:184,249,287,326 | Direct public query/document APIs, resolver and LRU query cache; shared guard/preparation owner | Preserve resolved model/service/endpoint/credentials/batch/cache/resilience; warm and cold queries/documents | Guard cache hits and complete result batches, indices/finite/dimension; no provider on overflow or unresolved identity |
| Core interfaces/llm.py, interfaces/memory.py; profiles.py:56 | Neutral contracts; existing lazy Memory factory dependency, explicit envelope/open-intent extension | Persistent and SimpleVector factories keep public shapes with qualified requests | No raw-vector escape, no backend initialization before admission; no document dependency in Core |
| Memory adapters/vector.py:54,99 and simple_vector.py:71,86,125 | Active/public storage/query; Chroma currently embeds query through document helper, SimpleVector uses query API | Correct once-only roles; full batch and precomputed-envelope positives | Bare/foreign vectors, malformed results and partial cardinality refuse before writes |
| retrieval/collection_manager.py:381,481,528,586,638 | Active short/long/decayed/MCP collections, gather reads and derived-record movement | Reads, promotion/demotion/reactivation with unsplit documents and matching identity | Typed errors escape get_all gather; no false empty result or copied foreign vectors |
| context/extractor.py:198,423,532–699 | Maintained extraction: entity/relationship, edge, insight batch/fallback, summary | Preserve LLM/embedding selections, stable output-slot UUIDs/upserts and graph dedup | Typed edge failure never becomes vectorless edge; batch guard failure never enters fallback; false/incomplete writes do not complete |
| Chat adapters.py:1145–1186 | Maintained pending extraction acknowledgement | Successful retry uses stable slot IDs, no duplicate persistence | Failed and unprocessed turns requeued; preserve commit-completed-under-cancellation distinction |
| context/assembler.py:398; Agent base.py:500–520; Runtime di.py:135 | Maintained inner fire-and-forget task, outer Agent wrapper is not completion | Own inner task/status/wait, delayed post-return success and shutdown drain | Delayed failure visible with telemetry off; explicit retry remains possible, no new auto-retry queue |
| controller/memory_controller.py:304,473–547,648,777,811,998,1160 | Maintained vector/query/priming/author/insight/summary reads | Real extraction→persist→recall and provider-offline admitted inspection | Guard exceptions bypass ordinary partial-read degradation; cancellation preserved |
| controller/memory_controller.py:1590–1625; Chat adapters.py:1810; Runtime di.py:295 | Both composition roots omit graph_scorer; maintained graph recall is unscored | Actual route succeeds with zero graph-vector comparisons | No unused-vector preflight or new scorer wiring |
| retrieval/graph_scorer.py:221,288,333,382 | Both sync and async are public injectable capabilities | Separate precomputed comparisons and optional async document fallback | Existing invalid/foreign vector cannot become zero/backfill; SOL-R7-001 corrects absent-vector oracle |
| context/consolidator.py:299–367 | Public unwired consolidation, separate from extractor | Persist summary before acknowledging only that successful batch | Failed/mixed batch retry without false acknowledgement |
| maintenance/compactor.py; Chat adapters.py compaction | Maintained compaction record storage, unsplit summary | Existing service/record/protection semantics | Overflow/storage failure visible; no document/512 rechunking |
| lifecycle/promotion.py:305–471; Tools memory/lifecycle.py | Maintained lifecycle plus injectable tool | Counts reflect actual completed mutations; dry-run remains prospective | False returns/exceptions retained in structured result and execute text |
| maintenance/pipeline.py:459–559,951,1031; provider_contracts.py | Maintained orchestration/provider probes and REEMBED | Same selection/order/prompts; graph-only empty collection uses admitted dimensions | Admission before synthesizer LLM AND embedding probes; no 8192-ceiling bypass |
| maintenance/pruner.py, synthesizer.py:697–799, fact_checker.py, reorganizer.py | Direct clients plus legacy public calls, stored-vector comparisons | Preserve three qualified callable shapes and once-only document preparation; positive synthesis/prune/check | No memory_dir/vector fallback after refusal; no hidden Chroma embedder on missing/failed embedder |
| maintenance/backup.py:165,239,269; reorganizer.py:227,265,287 | Public physical BackupManager and actual backup/backup_first | create/verify/same-incarnation restore returns old types; Reorganizer backup-first remains usable | Bound receipt, exact members/digests, unsafe/recursive/symlink root refusal, no sidecar overwrite, verify_first=False cannot waive identity |
| maintenance/__main__.py:346,365 | Module backup enabled, restore explicitly disabled | Actual module backup on admitted B/N | Keep disabled restore/mutation paths disabled; do not infer generic bridge |
| maintenance/analyzer.py:103,146,206 | Public graph/Chroma/transcript analysis | Exact normalized layout, offline-provider positive analysis | All SQLite opens mode=ro, no absent-file creation, no empty-success after admission failure |
| maintenance/recovery.py, recovery_models.py, mutation.py; Chat reorganization artifacts/contracts/coordinator | Maintained logical snapshot/rollback, distinct physical family | New strict Memory2/Chat2/Transcript1 same-incarnation roundtrip, independent fingerprints | Mixed/unknown/v1 active restore and identity tamper fail before effects; preserve ULP/quiescence/journal/order |
| ingestion/mcp.py; Chat memory_mcp.py:126–234; transcript SQLite receipt API | Active opt-in per-server exact single structured snapshot | Real public preparation/publication/readback/retry and mixed ordinary/MCP turn | Capacity oversized differs from typed readiness/storage and ownership failure; unchanged schema/replay limits and owned pending cleanup |
| Tools filesystem/smart_read.py:285–321,402,511,605; Memory ingestion/large_file_processor.py:810–959 | Explicitly injected public text storage/cache; maintained Chat/Runtime storage wiring absent | Raw source equals common plan; derived summary/synthesis unsplit; warm cache verifies destination/incarnation/records | No mtime-only completed-storage claim; source/options/preparation drift and disabled→enabled invalidate; unwired requested storage explicit failure |
| ingestion/tool_ingester.py; ingestion/pipeline.py and chunker.py | Public generic ingester / legacy preprocessing, not maintained automatic wiring | Explicit headless capability with shared plan, all strategies | No second split of accepted plan, no new automatic route |
| Chat commands/files.py, commands/registry.py; Tools readers/factory.py and smart_read | Chat read/ingest active; Tools four-format adoption separately proposed | Genuine four-format content through same converter; text/web reads retained, public Tools adapters prove their own paths later | Corrupt/partial/empty/missing assets cause zero ingestion; no placeholder or legacy fallback |
| Runtime di.py:250–303; Core profiles.py; adapters/vector.py:82 | FULL/VECTOR persistent; EPHEMERAL/TESTING front currently SimpleVector, lifecycle currently persistent | One identity per kernel, all four profiles; two simultaneous kernels same logical names/different models | Incarnation-scoped physical Chroma collections/cleanup only; no reset of shared system, no Memory-caused disk effects |
| CLI container.py:63–127; Runtime config.py construction/resolution | Compatibility delegates Runtime; dataclass forwards defaults | Preserve constructor/env/YAML explicit origin including supplied literal equal to default | Internally forwarded fallback is not explicit creation authority |
| Agent tools/builtins.py:109,203–204; repl_base.py:66 | recall_memory/store_fact and ContextAssembler-mediated context | Public tools preserve shape and qualified successful operations | Explicit refusal, no new model selector or protocol requirement |
| Memory multi_agent/controller.py, coordinator.py:123–192 and journal | Authorization namespaces share physical Memory identity | Visibility rules and successful graph/vector promotion/journal | Honest partial failure after graph write, no transaction or independent-space fiction |
| Commands memory_queries.py, Chat adapters.py MEMQ/stats/list-ingested | Neutral injected ports over actual admitted storage | Provider-offline stats/records/list/graph rendering | Explicit unavailable, no inference initialization or successful empty substitute |
| Tools memory/maintenance.py:44,111–113; inspection.py:134–141 | Injectable maintenance/reset/inspection; not newly activated | Actual public backup/maintenance/confirmed clear and nonsemantic inspection | Whole-layout admission before clear; binding retained; partial errors visible; semantic query separately needs readiness |
| Chat FrameworkMaintenanceAdapter legacy reorganize/reorganize_memory; maintained coordinator | Execute disabled outside coordinator; admitted dry-run remains | Test dry-run and coordinator independently | No reactivation of legacy mutation or order change |
| Runtime tool_loading.py:59–87; Tools package modules | Actual pkgutil.walk_packages/import_module dynamic discovery | Real minimal resolved Runtime includes counter extra but no Docling | Lazy new reader/limit imports; separate copied-prefix absence control is not supported-install proof |
| Transcript stores/sqlite.py; Core interfaces/transcript.py | Independent persistence and v1 snapshots; existing lazy Memory import | Retain receipt/schema/serialization and transcript setting independently | No transcript bump or Memory-profile toggle; isolate transcript writes in no-Memory-disk proofs |
| Telemetry helpers/llm.py, safe_llm.py, helpers/memory.py | Observers/tracking, not embedding execution owners | Preserve optional observation and existing contracts | Zero-attempt failures allowed; task status independent of telemetry |
| Commands session_views.py/contracts.py/diagnostics.py | Pure injected commands and immutable snapshots | Existing nonembedding/help/clear/exit/diagnostic contracts | No document stack import or new embedding prerequisite |
| Finance, MCP transports, Moltbook, Optimization, Sandbox, Speech source roots; Tools codegen | No discovered direct embedding executor; ordinary APIs or transitive Core/LLM usage | Existing nonembedding paths and lazy tools preserved | Discovery/import installed witness covers transitive coupling; no opportunistic edits |
| main.py | Hello-world nonembedding entry | Unchanged | No new startup dependency |
| lifecycle/migration.py and Chat migration stub | Legacy/inactive, not maintained capability proof | Preserve classification only | No repair/activation/migration; guarded admission cannot be bypassed |

Pinned installed Chroma source shared_system_client.py::_get_identifier_from_settings returns literal 'ephemeral' for nonpersistent local backends and shares _identifier_to_system. This supports the concrete FC-09 suffix/cleanup requirement; it is static backend evidence, not runtime proof. SimpleVector front is already independent in-process; the lifecycle Chroma collections still need the correction. Transcript independence must be preserved.

## Baseline qualification B01–B08 and replacement matrix

All rows remain FUTURE Gate-A qualification, not approved unsupported exclusions. Positive means usable operations, never safe refusal alone. All rows also require R at unresolved identity/counter, alias drift, invalid results and overflow; independent namespaces may use different models. A failure of an unused independent service cannot disable a qualified operation.

| Family | Source-backed selection / origin | B positive obligation | N positive / R specialization |
| --- | --- | --- | --- |
| B01 | Chat packaged src/config_templates catalog; adapters.py:1740 selects pool.default_service, maintenance explicit service | Omit both new fields; preserve default, divergent legacy hint remains no-op plus safe warning | Explicit replacement by same mechanism; same-space different names pass; incompatible same-root binding refuses |
| B02 | adapters.py:1749 existing text-embedding-3-small or explicit model/base/key | Hosted default cannot be silently changed/dropped; immutable identity qualification checked first | Qualified pinned deployment only; mutable alias echo is insufficient, readiness hard-stop if impossible |
| B03 | Chat non-pool compatibility construction via config/adapters | Sanitized fixture with existing alias/endpoint and extraction binding; no invented revision | Attested/pinned identity required; do not read dirty examples as fixtures |
| B04 | Runtime di.py:200 and :345 extraction pool selection | Memory default and separately selected extraction service/LLM retained | Different model in independent namespace succeeds; incompatible extraction space for same root refuses |
| B05 | Runtime config.py embedding service normalization and di.py:218 | Legacy embedding model/endpoint/options retain semantics with qualified omitted-field record | Same shared guard, no alternate client/model on readiness failure |
| B06 | CLI container.py:63–127 FridayConfig/env/default forwarding | Preserve effective defaults and raw explicit origin before forwarding; explicit literal=default eligible only if absent | Typed internal origin handoff; default fallback not CREATE_FRESH |
| B07 | Chat maintenance inline non-pool embedding construction / reorganization/mutation.py | Preserve distinct model/base/batch/resilience and qualified legacy configuration | Same-space check when namespace shared; no silent default rebinding |
| B08 | Memory MaintenanceConfig.embedding, synthesizer.py:697 three call shapes | Qualified embed_query, embed, bare callable preserved via bounded guard adapter | Once-only document preparation and cancellation/error semantics; opaque query-only preparation stops qualification |

N must exercise changed dimension, same dimension/different artifact, same dimension/different preparation, smaller capacity, independent persistent namespaces and all four Runtime profiles. Fresh coherent vector/graph/configured WAL/recovery/log layout is explicit; old files are preserved. Counter extra is inherited by normal Memory/Runtime/CLI/Agent without Docling. Direct LLM consumers need the extra or qualified injected capability. Dependency absence is a separate import control. B02 unknown qualification stops readiness; it is not a design-review runtime failure or permission to silently ship without a baseline.

## Full criterion matrix

PASS below means the proposed bounded design/proof obligation is sufficient against inspected source, not that future code/tests have passed. GAP means SOL-R7-001 remains. EC18 describes this report's evidence discipline, not a passing technical verdict.

| Criterion | Design assessment and source/document evidence |
| --- | --- |
| EC-01 | PASS: REM ownership/A–F; annex inventory and independent source-inventory.json; composition and transitive table above. |
| EC-02 | PASS: REM A–E and Tools companion TD01–10 preserve four formats, shared source plan and retained text/web reads; files/smart_read/public ingester classification above. |
| EC-03 | PASS: Annex B01–08/FC10; model_library resolve_embedding_service, Chat adapters:1740–1758, Runtime di:200–218, CLI container:109. |
| EC-04 | PASS: REM proposed paths:1220–1256; Core interfaces/memory, collection/controller and injected tools traced above; no broad API rewrite. |
| EC-05 | PASS: REM E and annex baseline qualification; existing strict EmbeddingOptions requires planned shared schema change; unresolved baseline hard-stop explicitly retained. |
| EC-06 | PASS: REM D/E shared roles/counting/cache; LLM embeddings query LRU and vector/simple store handoffs; no Docling policy in Memory/Core. |
| EC-07 | GAP: Actual unscored composition confirmed at Chat adapters:1810 and Runtime di:295, controller:1590; async absent fallback source:245–264 contradicts zero wording; SOL-R7-001. |
| EC-08 | PASS: Annex FC06 and REM scope:1233–1237; extractor:532–699, Chat _extract_turns:1145, assembler:398, Runtime shutdown:135. |
| EC-09 | PASS: FC03/04/05 plus recovery handoff; BackupManager:165/239/269 and Reorganizer:227/265/287; public positives and separate v2 required. |
| EC-10 | PASS: FC07/13 and REM raw/derived rules; CollectionManager lifecycle embedding calls and large_file_processor storage; unsplit structured records. |
| EC-11 | PASS: Independent all-src discovery plus FC09–13; Agent/context, real Runtime catalog, Core/CLI and unchanged package dispositions above. |
| EC-12 | PASS: REM identity/fresh-store matrices and annex N; vector/simple/graph/recovery paths, no migration or personal-store operation. |
| EC-13 | PASS: Annex compatibility/namespace distinction and FC09; multi_agent coordinator:123–192 is authorization layering on underlying Memory. |
| EC-14 | PASS: REM E overflow/result/cache rules and FC02/06/08; observed extractor/read catches explicitly covered, capacity separate from generic failure. |
| EC-15 | PASS: DI18/21/22/27–34 plus FC proof nodes require public B/N/R, canonical call-phase mutants and normal/-O installed lanes; no premature execution demand. |
| EC-16 | PASS: REM exact allowlist:1220–1256 and annex scope stops; newly inventoried tools/Agent remain source-unchanged unless explicit narrow seam applies. |
| EC-17 | PASS: REM A/B Certifi/assets/format rules, companion TD07/09/10 and FC12; package metadata dependency edges inspected, exact graph remains Gate A. |
| EC-18 | PASS: Current controls exact comparison, request/helper pins, opening/closing integrity, explicit matrices and two rubrics; no historical verdict reused. |
| FC-01 | PASS: FC01; extractor constructor:210–212 and extraction_filter.py:23–68 global handlers establish hazard; owned leases, first-use admission, failed construction/reconfigure/close/two kernels explicitly planned. |
| FC-02 | PASS: FC02; actual Chat memory_mcp.py:126–234 consumes snapshot absence as skip and maps exceptions; new bounded outcomes/typed failure mapping and receipt replay limits explicitly required, schema unchanged. |
| FC-03 | PASS: FC03; BackupManager signatures/manifest retained; create source recursion and restore loop inspected. Bound receipt/member/digest/path proof, same-incarnation positive, no-marker overwrite and verify_first=False admission specified; no bridge/waiver. |
| FC-04 | PASS: FC04; analyzer.py:103/146/206 raw SQLite and graph probing; exact normalized admission plus read-only URI for BOTH database families specified. |
| FC-05 | PASS: FC05; synthesizer.py:697–799 accepts three shapes then may omit embeddings. Qualified shape adapter/once-only document role and zero hidden-default-embedder witnesses sufficient. |
| FC-06 | PASS: FC06; extractor broad catches and vectorless edge risk, Chat retry acknowledgement, assembler inner create_task and Runtime shutdown independently inspected; real delayed-task/telemetry-off public proofs required. |
| FC-07 | PASS: FC07; promotion.py increments before mutation and Tools public text seam; actual completion/false-return/partial-error and dry-run obligations sufficient. |
| FC-08 | GAP: FC08 actual typed recall seams covered, no maintained scorer wiring. Absent async fallback vs unconditional zero contribution unresolved: SOL-R7-001. |
| FC-09 | PASS: FC09; Core profiles + Runtime front/lifecycle construction + installed Chroma shared-system static source; per-incarnation physical collections and scoped clear/close cover concrete isolation. |
| FC-10 | PASS: FC10; actual Chat hint/default divergence and CLI default forwarding confirmed; preserve raw origin not inferred by string comparison, no new YAML knob. |
| FC-11 | PASS: FC11; pipeline probes synthesizer before embedding and mutation dimension model; whole admission precedes both, expected empty dimension and ceiling qualification bound scope. |
| FC-12 | PASS: FC12; package dependencies and actual tool_loading catalog inspected; shared counter extra without Docling, lazy imports, separate absence control are coherent future install proofs. |
| FC-13 | PASS: FC13; Agent builtins/archive, multi-agent, MCP, MEMQ and Tools inspection/reset/maintenance traced; provider-offline reads, truthful partial results, disabled legacy vs coordinator separated. |
| FC-14 | PASS: FC14; deterministic operational proof explicitly separated from later model-quality UAT and fixed threshold calibration; no quality parity claim or retuning authority. |

## Correction delta and selected requirement dispositions

The amendment adds exact public backup retention, task ownership/acknowledgement, MCP mapping, sink ownership, corrected graph wiring, ephemeral isolation and named catch/import/probe seams. These were judged from source, not accepted from controller labels. Aggregate current requirements remain in force. Historical next-gate replacements in status prose are current routing context, not acceptance proof.

| Proposed correction | Independent design disposition |
| --- | --- |
| IC01 public backup | Sufficient proposed correction; BackupManager signatures and actual Reorganizer/Tools/module calls inspected. Separate physical receipt and logical-v2 family preserved. |
| IC02 inner task | Sufficient; actual assembler task and Runtime shutdown, not Agent wrapper alone, named in scope/tests. |
| IC03 MCP | Sufficient; actual Chat public observer/receipt/turn path named, exact reason literals freeze before construction. |
| IC04 sink ownership | Sufficient; module-global fan-out source confirmed; two owners, lifecycle, failed construction and admitted first use included. |
| IC05 graph route | Actual maintained route correction sufficient; absent-vector fallback oracle still needs SOL-R7-001. |
| IC06 extraction | Sufficient; actual edge/batch/fallback/summary and Chat retry seams included, stable IDs/cancellation retained. |

Original nine themes: EC01 logging→FC01; EC02 MCP→FC02; EC03 backup→FC03; EC04 analyzer→FC04; EC05 implicit embedder→FC05; EC06 consolidation→FC06; EC07 lifecycle counts→FC07; EC08 recall→FC08 (one residual gap); EC09 profiles→FC09. Each uses the independent FC source assessment above; no finding closure is inferred from the correction-map status.

| Selected high/medium requirement | Independent proposed disposition |
| --- | --- |
| OPUS-A1: Actual canonical Chat default versus legacy hint, preserved and visible. | Sufficient bounded requirement in FC-10; source and B/N/R proof assessed in its FC row. |
| OPUS-A3: B01–B08 qualified identities with absent/placeholder revisions and alias-swap refusal. | Sufficient bounded requirement in FC-10; source and B/N/R proof assessed in its FC row. |
| OPUS-A4: Namespace admission before real provider probe. | Sufficient bounded requirement in FC-11; source and B/N/R proof assessed in its FC row. |
| OPUS-A5: Preserve CLI raw explicit-origin across default forwarding. | Sufficient bounded requirement in FC-10; source and B/N/R proof assessed in its FC row. |
| SOL-R5-A02, OPUS-A6: Actual transitive agent/multi-agent/MCP coverage and namespace distinction. | Sufficient bounded requirement in FC-13; source and B/N/R proof assessed in its FC row; SOL-R7-001 does not alter this separate requirement. |
| ASTRA-R5-A02, OPUS-A8: Declared dimension ceiling and identity-based empty-store behavior. | Sufficient bounded requirement in FC-11; source and B/N/R proof assessed in its FC row. |
| OPUS-A10: Headless counter extra/dependency profile without Docling. | Sufficient bounded requirement in FC-12; source and B/N/R proof assessed in its FC row. |
| OPUS-A7: Admitted store-only MEMQ reads without inference. | Sufficient bounded requirement in FC-13; source and B/N/R proof assessed in its FC row; SOL-R7-001 does not alter this separate requirement. |
| OPUS-A2: Operational compatibility versus later measured quality evaluation. | Sufficient bounded requirement in FC-14; source and B/N/R proof assessed in its FC row. |
| OPUS-A11: Public-unwired preprocessing never a second stored chunk plan. | Sufficient bounded requirement in FC-13; source and B/N/R proof assessed in its FC row; SOL-R7-001 does not alter this separate requirement. |

| Pass1 advisory requirement | Independent proposed disposition |
| --- | --- |
| OPUS-R6-A1: Per-incarnation physical ephemeral collections despite shared Chroma system. | Sufficient proposed requirement in FC-09; corroborated by corresponding source/authority assessment above. |
| OPUS-R6-A2: Name get_all/priming/author read catch seams and typed propagation. | Sufficient proposed requirement in FC-08; corroborated by corresponding source/authority assessment above. |
| OPUS-R6-A3: Explicit public Tools wrappers and disabled Chat legacy/dry-run dispositions. | Sufficient proposed requirement in FC-13; corroborated by corresponding source/authority assessment above. |
| OPUS-R6-A4: Actual Runtime pkgutil module catalog minimal-install witness. | Sufficient proposed requirement in FC-12; corroborated by corresponding source/authority assessment above. |
| OPUS-R6-A5: Qualified shared-guard wrapper route for all retained callable shapes. | Sufficient proposed requirement in FC-05; corroborated by corresponding source/authority assessment above. |
| OPUS-R6-A6: Admission before LLM synthesizer probe as well as embeddings. | Sufficient proposed requirement in FC-11; corroborated by corresponding source/authority assessment above. |
| OPUS-R6-A7: Current next-decision authority and pass count reconciled. | Sufficient proposed requirement in verified current controls/status; corroborated by corresponding source/authority assessment above. |
| OPUS-R6-A8: Do not activate inert Chat rejection-log setting. | Sufficient proposed requirement in FC-01; corroborated by corresponding source/authority assessment above. |
| OPUS-R6-A9: Early visibility of hosted baseline immutable-identity feasibility stop. | Sufficient proposed requirement in FC-10; corroborated by corresponding source/authority assessment above. |
| OPUS-R6-A10: Read-only transcript SQLite as well as Chroma. | Sufficient proposed requirement in FC-04; corroborated by corresponding source/authority assessment above. |

## Scores under both supplied rubrics

Coverage: framework direct/transitive coverage 3.8/4; baseline/replacement positive coverage 2.8/3; negative identity/overflow/failure effects 1.85/2; headless/minimal/nonembedding 0.95/1 = **9.4/10**. The broad operational proof plan is strong; the optional async fallback positive branch lacks a consistent oracle, and dynamic/import consumer coverage remains an explicit future real-install obligation rather than static certainty.

Overall: framework inventory 1.9/2; operational configuration/API compatibility 2.7/3; replacement/namespace safety 2.4/2.5; bounded proof/reporting 1.8/2; scope/authority 0.5/0.5 = **9.3/10**. The main deduction is the specific preservation conflict in an existing public API, not missing unapproved product implementation or future measured Gate-A work. Exact guard/schema/source/installed proof still must precede acceptance. A high score cannot override the mandatory finding.

## Reproduced checks, pins and conduct audit

Request SHA256 d7e045a1e3e0a27417f02253b1d56ab73d516cdc2be528990a0ca42356fc9f6e was verified before request content read.
Helper SHA256 6ef846532b6caab0c136b50dc9bde1da1816e72742eef6e0522c4e37a36fe9ca; wrapper cb0669f81efd0098c104d7b96342fcd614255021ea2bfa49cbbb6af7c2fea248; extractor a9fd727a2d9715e5b6759034c4bb92160993bd6d0b23efedcea6211f978e4b81; frozen controls 6d63c0062008d8de7ebad06fa5e6bceeea29155cb58efbe3b97934f716f748b8. All matched and helper code was inspected before execution. Static extractor returned exit0 and byte-identical controls-copy.json. Raw authority was read only by the verified extractor/integrity helper, never opened/grepped by reviewer.

All Git/admin processes, including helper descendants, used python3 -B INPUTS/read_only_command.py OWN -- ARGV. Audit is command-audit.jsonl; wrapper forces GIT_OPTIONAL_LOCKS=0, no bytecode, and private caches/TMPDIR. No product import, test, build, install, resolution/download, inference, provider/store operation, reset or migration occurred. Text/AST/static source reads are exempt. The one installed backend inspection was static source only. No shell worktree/checkouts, PRs, delegation, personal state reads or cleanup occurred.

Exactly five administrative commands were reproduced offline/frozen/no-sync/no-download. Exit codes all 0:

- board: `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate`. Evidence: board.log. SHA256 c4d2aec671b8fd5d5a978b1c191b186f6d151f7ace4785fbd74b06c3c5f3fdae.
- dashboard: `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check`. Evidence: dashboard.log. SHA256 a28df31135633728c76b88ed1a836e90f2c8046e1d72663c8881937c7693ba33.
- docs: `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py`. Evidence: docs.log. SHA256 abd78a24f3220167e9c59bd32036a2df1866bec9f4574ff581b9b39eb65863da.
- metadata: `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py`. Evidence: metadata.log. SHA256 b755228d64e991cad2a40d1ea238ea00e97d8d2fd420a5141fffa00476ed690f.
- whitespace: `git diff --check 91ac63bad5e46eceddd252d5b7727f7a1d3c623a..f1916747ad7d03e451f2b57dc00542faa6095d7c`. Evidence: whitespace.log. SHA256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

Opening integrity (exit0):
```json
{
  "outcome": "PASS",
  "request_sha256": "d7e045a1e3e0a27417f02253b1d56ab73d516cdc2be528990a0ca42356fc9f6e",
  "candidate": "f1916747ad7d03e451f2b57dc00542faa6095d7c",
  "branch": "feature/cmd-ingest-001",
  "logical_index_sha256": "0f185529a0084999a93b6b969b67d0a92d266491a113545f426f967bf94d5a97",
  "protected_entries": 17681,
  "failures": []
}
```

Closing integrity after final shared/input inspection (exit0):
```json
{
  "outcome": "PASS",
  "request_sha256": "d7e045a1e3e0a27417f02253b1d56ab73d516cdc2be528990a0ca42356fc9f6e",
  "candidate": "f1916747ad7d03e451f2b57dc00542faa6095d7c",
  "branch": "feature/cmd-ingest-001",
  "logical_index_sha256": "0f185529a0084999a93b6b969b67d0a92d266491a113545f426f967bf94d5a97",
  "protected_entries": 17681,
  "failures": []
}
```

Verified inspected content hashes:
```json
{
  "docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md": "069ff23f5980f4b1abf9edcbcdbf620ec4473ef99145212bcd0571bc7c1b1554",
  "docs/planning/active/command-refactor/embedding-compatibility-contract.md": "bbafc99252f746891f671961b1f684b03e8a9f36f8d4fb702f5b83a117a3ddf3",
  "docs/planning/active/command-refactor/proposals/tools-document-adoption.md": "8220e195f7b9b899fb377f5550920a3d9ac0699b33293a59c366ff6d2fa6d998",
  ".venv/lib/python3.13/site-packages/chromadb/api/shared_system_client.py": "1176c7ee054e6f5b36b2d544de1d82969d2ff4253e263ac6f31cebed5a39a13f"
}
```

Every output/cache/temp/locator/report resides under /tmp/sol-ingest-r7-OkvKQ2, fresh external scratch outside checkout and all supplied input/scratch paths. Own-directory creation used mktemp; wrapper caches/tmp remained private. No writes to repository, .venv, supplied paths or personal state were requested or observed. No dirty example YAML, personal configuration/store/export or .friday-old evidence was read; integrity helper alone checked pinned hashes/stats, including preserved metadata records. Broad discovery stayed under explicit src roots; tests and committed packaged templates were read by explicit paths. Reports/history directories were not traversed. Some large tool displays truncated; focused follow-up reads supplied the concrete source evidence used for findings. A mistaken explicit static test/source filename lookup is not runtime evidence; no missing-file output is treated as product failure.

Freshly reproduced evidence consists of pins, static extractor comparison, source/AST discovery, selected frozen diffs, five administrative commands and both integrity checks. Inspected tests include backup/analyzer public tests, Runtime kernel setup and real Chat MCP mixed receipt test; none were executed or represented as new compatibility tests. Existing source hazards are feasibility evidence for planned repairs, not implementation defects newly introduced by this document candidate. There is no whole-repository-green claim: root Ruff534, root collection test_display conflict7196, legacy formatting and MAINT oracle debt remain failed/unwaived as supplied. No runtime rerun was authorized.

Future evidence remains exact model/serving identity, counting parity/assets, dependency graph/Docling/Certifi install feasibility, numeric budgets, frozen schema/signature/member/oracle details, actual public B/N/R execution and normal/-O installed witnesses. Their absence is expected at this design gate and is not itself a mandatory finding. Unknown baseline qualification stops Gate A; positive B/N operations cannot be silently replaced by refusal. No runtime safety, installation support, semantic model quality, human acceptance or delivery assurance follows this review.

Recommended next gate: return SOL-R7-001 for the controller's bounded document correction/disposition within the existing four-pass authorization. This pass2 counts; no reviewer repair, new delegate, extra pass or Gate-A execution is started by this report.
