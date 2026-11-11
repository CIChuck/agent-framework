# REM-CMD-INGEST-001 independent design/source-feasibility review

**CHANGES_REQUESTED — coverage 9.0/10; overall 8.7/10. Three mandatory findings.**

Reviewer: gpt-6-astra, high effort; compatibility cycle pass 1/4, global round 6. This pass counts against the cap. No reissue was launched.

Candidate `8d25d53ac944ace99e3ae430364075b0c1200ff6`, branch `feature/cmd-ingest-001`, amendment base `91ac63bad5e46eceddd252d5b7727f7a1d3c623a`, repository `/Users/chuckrussell/Dev/gendev/agent-framework`. Fresh independent context; no implementation participation, parent reasoning, peer verdicts, raw historical reviews, nested agents or repairs. Historical scores in ordinary status documents were not correctness evidence. Generic read-only procedure memory was consulted only for isolation practice.

The explicit shared-checkout exception was used with private external scratch. Review is amendment delta first, then full current REM, normative compatibility annex, Tools companion and source feasibility. Missing future implementation is not a finding. No implementation, Gate A, acceptance or delivery follows this report.

## Authority and delta assessment

Request SHA256: `72218c26f912bf58c5d7231f79aff9a7156ed0d82bb557d25b2195b7a9a7aa41`. All supplied helper hashes matched before execution and again at closing. The static extractor was inspected and run through the wrapper; its output matched frozen current-controls byte-for-byte. Raw authority was neither opened nor searched by the reviewer; only the authorized extractor/integrity helper accessed it.

AGENTS, repository engineering/lifecycle/independent-validation policies, council and independent-validator skills, scope decisions, fresh-store decision and bounded iteration authorization were read. User's prohibition on nested agents controls this reviewer seat. The current controls grant document review only and leave construction ungranted. The exact permitted technical/status diff was saved as `amendment.txt`; whole-authority and aggregate historical diffs were excluded. The delta adds the annex, broadens the proposed narrow integration/proof paths, corrects active MCP classification, and reconciles status to pass 1/4. Those are meaningful design improvements, not proof of implemented behavior. The correction map was treated as requirements, not closure evidence.

References below use repository-relative paths. `REM` = `docs/planning/active/command-refactor/remediation/REM-CMD-INGEST-001-pdf-docx.md`; `Annex` = `docs/planning/active/command-refactor/embedding-compatibility-contract.md`; `Tools plan` = `docs/planning/active/command-refactor/proposals/tools-document-adoption.md`. Short source names resolve in the consumer table. Line numbers identify inspected source anchors; named sections identify normative document anchors.

## Mandatory findings

### ASTRA-R6-001 — High: public backup compatibility is withdrawn without resolving the governing premise

Evidence: Annex FC-03 (lines 155–166) forbids BackupManager create/live restore for bound namespaces and also retains refusal for legacy-unbound namespaces. `packages/friday-memory/src/friday_memory/maintenance/backup.py:158` implements public create, and `:273` implements restore; these are not disabled APIs. `maintenance/__main__.py:346` still exposes backup, while restore and non-dry-run mutations are separately disabled. Existing `tests_memory/test_maintenance/test_backup.py:14` and `:63` characterize successful create/restore. REM section E requires existing consumers to remain operational; the recorded fresh-store approval only selects fresh stores and preservation, not retirement of the backup API.

The proposal correctly discloses the restriction, but no live namespace category remains on which that public API succeeds. A different Memory-v2 API is not positive compatibility evidence for BackupManager or its CLI backup caller. Fresh-store policy does not authorize this unrelated capability withdrawal. This is a proposed compatibility-policy conflict, not a demand to execute backups now.

Required narrow resolution: either retain identity-safe operation at the existing public entry through a separately specified bounded contract, or obtain an explicit maintainer disposition accepting this exact API/CLI retirement and its replacement workflow. Do not implement a generic bridge/migration engine under this review. Revise FC-03, the exception list, B08 disposition and final directive consistently; until resolved, do not count these public entries as B/N compatible.

Future proof: on disposable B and N stores, prove whichever public operation remains supported succeeds and preserves space/incarnation; prove foreign/pending artifacts refuse before mkdir/copy/sidecar mutation. If the maintainer explicitly accepts removal, test the precise actionable refusal and separately test the actual replacement API, with no claim that old-API positives passed. Keep disabled module restore disabled.

### ASTRA-R6-002 — High: maintained MCP caller erases the proposed failure distinctions; its source seam is outside the allowlist

Evidence: `packages/friday-memory/src/friday_memory/ingestion/mcp.py:138` returns oversized; `:185` preserves ownership error and `:187` maps ordinary storage failure to storage_failed. `packages/friday-chat/src/friday_chat/adapters.py:309` delegates preparation. The actual publication route, `packages/friday-chat/src/friday_chat/memory_mcp.py:168`, maps every preparation without a snapshot to `_skipped(call)`; `:241` reports skipped. It therefore discards oversized versus identity/readiness/storage failure. Annex FC-02 requires explicit non-capacity failure and truthful overflow mapping. REM's exact implementation-path table permits Memory ingestion/mcp.py and Chat adapters/runtime but omits Chat memory_mcp.py.

Changing only the lower-layer outcome cannot make this maintained caller distinguish a legitimate policy skip from a new guard/storage failure. Replacing the outcome with an exception would change existing receipt/partial-turn behavior and needs an explicit contract too. The supplied node name alone does not resolve that source/scope gap.

Required narrow resolution: specify the public preparation-to-publication/receipt/observer mapping for overflow, readiness/identity failure, ordinary storage failure and ownership conflict. Add only the necessary `memory_mcp.py` result-adaptation seam and its focused tests to the allowlist (or document a concrete compatible adapter solution that reaches the same public observer). Retain single immutable snapshot, opt-in, pending/publish/discard ownership and existing successful transcript behavior; no rechunking or new route.

Future proof: run the real Chat publication entry for a valid B/N snapshot, byte-valid/token-overflow record, typed identity failure, storage failure and mixed ordinary/MCP calls. Assert visible reason, exact receipt flags, pending ownership, no false ingested status, zero forbidden provider/store effects, and no conversion into indistinguishable successful policy skip. Repeat representative normal/-O installed witnesses.

### ASTRA-R6-003 — Medium: rejection-log admission lacks handler ownership across namespaces

Evidence: `packages/friday-memory/src/friday_memory/context/extraction_filter.py:25` owns a module-global rejection logger. `:44` creates parents; `:48` deduplicates only identical paths; `:55` opens a FileHandler and `:67` appends it. All filters emit to that logger (`:127`, `:178`). Extractor construction invokes configuration at `context/extractor.py:210`. Annex FC-01 defers construction and qualifies the newly selected path, but specifies no handler retirement, per-extractor routing or revalidation for a handler retained from a previously admitted namespace.

After admitted extractor A has installed handler A, constructing admitted extractor B installs handler B on the same logger. B's rejection then writes both destinations. Deferral alone does not prevent writes into A after it becomes inactive/foreign, and simultaneous independently bound kernels contaminate each other's logs. This conflicts with preservation of old roots and independent namespace operation (EC-13), despite each initial path having qualified correctly. This is a source-feasibility/proof omission, not a request for a general logging redesign.

Required narrow resolution: within the already allowed extraction_filter/extractor/assembly seam, bind each rejection emission/handler to the owning admitted capability and define disposal/reconfiguration so another namespace cannot keep writing the old target. Preserve qualified independent log roots and public semantics; do not silently redirect or edit YAML.

Future proof: two independently admitted kernels with distinct log roots, then A shutdown/reconfiguration/refusal while B rejects input. Assert B writes only its authorized target and old A bytes and metadata remain unchanged; test failed construction and repeated same-path setup without duplicate writes. Include first fresh creation with a configured vector-local log and refused legacy startup. This needs no personal stores.

## Independent consumer/disposition and B/N/R matrix

B means qualified unchanged configuration with optional new fields omitted and an admitted namespace. N requires both changed dimension and same-dimension different artifact/preparation, smaller effective capacity, and a fresh coherent namespace. R means wrong/unbound/pending identity, invalid vectors or capacity refusal before prohibited effects. Every positive below is a FUTURE obligation, not reproduced runtime evidence. A design PASS means its requirement and narrow seam are adequate, subject to the numbered findings. Inventory was independently obtained by searching 445 package source/config files, then following config/interface/store/error/public-call seams. `source-search.txt`, `transitive-search.txt` and hash-bearing `source-inventory.json` preserve the scope and matches.

| Consumer and inspected source | Classification / disposition | B and N positive requirement | R / effects / scope assessment |
| --- | --- | --- | --- |
| LLM embeddings.py:249,287; model_library.py:287 | Shared direct APIs, resolver/cache | Existing query/doc interfaces, endpoints, batch/cache/resilience; exact local counting | REM E/DI-18,24: preflight entire batch, index/cardinality/finite/dimension/role identity; allowed shared LLM seam |
| Core interfaces/llm.py:113; interfaces/memory.py; profiles.py:56 | Public protocols/factories | Identity-bearing query/store handoff through existing factory | Explicit origin/open intent; no neutral backend imports; REM allowlist |
| Memory adapters/vector.py:84,109; simple_vector.py:109,154 | Persistent and ephemeral front stores | Correct document storage/query roles in both dimensions | Admit before client; bare vectors refused; DI-21/22 |
| Memory retrieval/collection_manager.py:88,559,617,667 | Lifecycle collections and direct embedding handoffs | Store/query/promotion/demotion/reactivation preserve records | Shared identity across collection set; no hidden embedder/second chunker |
| Chat adapters.py:1735,1795; runtime.py:1421 | Maintained composition, pool default + nonpool | Preserve actual default, separate maintenance choice | Deferred startup, /read independent; FC-01/10; finding 003 for logs |
| Runtime di.py:245,292,350; config.py:1301,1588 | Maintained headless pool/nonpool/extraction binding | Four profiles; preserve distinct extraction service | FC-09/10; explicit paths, isolated ephemeral collection manager |
| CLI container.py:72,118; profiles.py:19 | Public compatibility wrapper/re-export | Constructor/env/default behavior delegates Runtime | Origin before forwarding, explicit literal equal to default; no separate client |
| Memory context/extractor.py:210,578,657 | Maintained extraction, graph/insight/summary storage | LLM selection unchanged; unsplit guarded embeddings; store→recall | Typed errors cannot acknowledge failure; log handler gap 003 |
| Memory controller/memory_controller.py:500,522,1038 | Maintained recall/priming/fetch | Shared query vector and compatible graph/vector retrieval | FC-08 explicitly repairs gather/empty catches; preflight graph provenance before query |
| Memory retrieval/graph_scorer.py:330,385 | Maintained synchronous graph scoring | Compatible cached edge/node vectors; absent vector contributes zero | Unknown/foreign existing vector fails whole semantic operation |
| Same graph_scorer.py:221 | Public-unwired async fallback | Explicit caller uses guarded document role | No activation/backfill; not maintained-route proof |
| Memory context/assembler.py:500,577 | Maintained context assembly | Recall plus passage/tool budgeting | finally-only span closure propagates recall errors; no new tokenizer for tool hints |
| Memory context/assembler.py:398; Agent base.py:494,511 | Background extraction/archival | Actual scheduled extraction succeeds and records outcome | FC-08/13 require observable failure; detached scheduling is a future proof risk; no claim task creation proves completion |
| Memory context/consolidator.py:183,196,358 | Public-unwired consolidation | Store each summary before source acknowledgement | FC-06 mixed failures retain retry eligibility; exact narrow allowlist |
| Memory maintenance/compactor.py:435,444,462 | Maintained session compaction | Store summary, then mark compacted | Existing exception boundary records errors; no document rechunking; store_insight must raise typed refusal |
| Memory lifecycle/promotion.py:423,463,569; Tools memory/lifecycle.py:41 | Maintained/public lifecycle | Actual successful counts; dry-run prospective counts | FC-07 fixes false-return/exception counts and execute text without generic Tools redesign |
| Memory maintenance/pipeline.py:526,553,951,1031 | Maintained maintenance pipeline | Compatible service; graph-only empty-collection REEMBED | Admit before probe; FC-11 dimensions from identity, no row inference |
| Memory maintenance/mutation.py:196,594,630 | Direct Chroma opener / mutation contracts | Verified expected dimension <=8192; empty store allowed | Same-size different space and >8192 refuse; no schema ceiling expansion |
| Memory maintenance/pruner.py:114; fact_checker.py:140 | Raw stored-vector/read consumers | Admitted normalized root, offline read where applicable | No alternate-root fallback or empty success on admission failure |
| Memory maintenance/synthesizer.py:183,712,765 | Public legacy synthesis/raw client | Injected qualified service and document role | FC-05 forbids omitted embeddings/default Chroma fallback; disabled CLI mutations stay disabled |
| Memory maintenance/reorganizer.py:93,213,775 | Public accessor/orchestration | Existing configuration and guarded embedding service | Preserve stage ordering/prompts; underlying guards apply |
| Memory maintenance/backup.py:158,273; __main__.py:346 | Public physical backup, enabled CLI backup | Proposed B/N old-API success absent | Finding 001; replacement v2 is distinct, not closure |
| Memory maintenance/analyzer.py:103,146,206 | Public raw SQLite/graph analysis | Admitted provider-offline live analysis | FC-04 exact layout/read-only SQLite; no mkdir/journal, no successful empty refusal |
| Memory maintenance/recovery.py:412; recovery_models.py; Chat reorganization contracts/artifacts/coordinator | Maintained snapshot/rollback | Memory-v2 + Chat-v2 + Transcript-v1, exact same incarnation | REM E/DI-27,32 strict v1 offline dispatch, no rebind/engine redesign |
| Memory ingestion/mcp.py:38,138,185; Chat adapters.py:309; memory_mcp.py:168,217,241 | Active opt-in snapshot/publication | Single exact snapshot, receipt and pending/publish ownership | Finding 002: outer route drops reasons; no document/512 chunking |
| Tools filesystem/smart_read.py:181,605; Memory ingestion/large_file_processor.py:899,954 | Public injected storage, unwired in maintained Chat/Runtime | Raw chunks equal one plan; derived summaries unsplit; headless positive | Destination/incarnation/collection/IDs validate cache completion; no opt-in activation |
| Memory ingestion/tool_ingester.py:128,147 | Public-unwired generic ingestion | Explicit caller uses common policy | Not MCP route; no automatic activation; don't split accepted plan |
| Memory ingestion/pipeline.py:39; chunker.py:71 | Public legacy preprocessing | Callable preprocessing retained | Not stored-plan evidence; no second storage chunker (FC-13) |
| Agent tools/builtins.py:109,203; tools/registry.py:597 | Indirect recall/store_fact via controller | Existing public tool shapes, authorization and storage | Typed refusal reaches actual tool failure; no added model selector |
| Memory multi_agent/controller.py:95,145; coordinator.py:159,167,190; journal.py:92 | Runtime-wired multi-agent visibility/partial commit | Shared physical space, visibility partitions preserved | Existing exception→failed journal path; partial graph/vector effects remain honest; no new atomicity promise |
| Tools memory/inspection.py:12,54,108; Chat adapters.py:2544 | MEMQ/inspection/store-only | Admitted stats/records/list-ingested, provider offline | No inference initialization or false empty result; FC-13 |
| Memory context passage/tool routing; Tools base.py:37 | Nonsemantic/LLM-only/context tools | Register and use without document or embedding assets when not needed | Lazy dependency boundary; generic Tools API unchanged |
| Core interfaces/transcript.py:85; Transcript stores/sqlite.py:306,603 | Separate persistence | Transcript contracts and v1 artifacts remain | Memory profile does not authorize transcript rewrite; isolate its independent disk effects |
| Telemetry helpers/memory.py:403, interface.py:23 | Observability, not embedding owner | Existing error/zero-attempt instrumentation | No telemetry rewrite or success inferred from attempted event |
| Commands src and pyproject; Chat cli entry; CLI server/REPL delegation | Entry/control planes | stdlib Commands closure, read/help/exit and existing headless interfaces | File parser scoped to default handlers; no new standalone CLI |
| MCP transport package source; Speech, Sandbox, Finance, Moltbook | No direct embedding/store matches in whole-source search; Tools/Agent bridges transitive | Existing nonembedding operations/imports | Unchanged; installed configured-tool registry proof required; absence of direct calls is not a claim about arbitrary plugins |
| Optimization pyproject.toml:10; src | Memory dependency but no direct embedding calls found | Import/minimal-install closure remains valid | Inherits Memory counter extra, no Docling requirement; unchanged source |
| Memory lifecycle/migration.py; Chat migrate/reset compatibility stubs | Inactive/disabled routes | No active-route credit | No activation, fixed-dimension legacy defects not repaired here |
| main.py:1; scripts static scan | Smoke entry/admin/artifact tools | main only prints; scripts' package references are artifact verification | No product route found; admin checks separately reproduced |
| Tools ReaderFactory/smart_read and direct readers | Companion-only document adoption | Four real formats through shared converter, retained selections/pagination | Tools plan TD-01..10; no fallback, no claim INGEST completes companion |

## Configuration qualification matrix

All rows remain unexecuted Gate-A obligations. Unknown baseline qualification is a hard stop, never permission to drop a baseline. Each row requires B/N successes, same-space different service names, independent namespaces with different spaces, and R identity/capacity failures. No actual model was selected.

| Family | Source anchor / effective binding | Required proof and disposition |
| --- | --- | --- |
| B01 | Chat adapters.py:1740; packaged config templates | Pool default wins over divergent legacy hint. Preserve options; warning reports ignored hint. Qualify omitted capabilities and immutable current serving identity. Design adequate. |
| B02 | Chat adapters.py:1748 | Nonpool explicit model or text-embedding-3-small; endpoint/key/resilience preserved. Hosted immutable identity and local counting must qualify or stop. |
| B03 | Chat config.py:470; REM E | Sanitized compatibility fixture, no dirty YAML. Missing revision resolved from verified deployment, never invented from alias. |
| B04 | Runtime di.py:233,350; config.py:1301 | Catalog default plus explicit extraction binding. B/N full extraction→graph/insight→recall; same-space names pass, cross-space shared root refuses. |
| B05 | Runtime config.py:1588; di.py:219 | Legacy embedding/service options remain effective; shared guard and readiness. No fallback model. |
| B06 | CLI container.py:72,118 | Preserve environment/constructor origin before default merge. Omitted path does not create; explicit default-valued path may create if absent. Typed sentinel design feasible, signatures freeze at Gate A. |
| B07 | Chat reorganization/mutation.py:268,285 | Explicit maintenance pool or inline nonpool identity, no default redirection; admit before probe. |
| B08 | Memory maintenance/reorganizer.py:93; synthesizer.py:712; Core interfaces/llm.py:113 | Public MaintenanceConfig and injected provider signatures preserved with qualified capability. No Chroma fallback. Backup restriction is separate unresolved finding 001, not successful API preservation. |

Four Runtime profiles: FULL = persistent vector/lifecycle/graph; VECTOR_ONLY = persistent vector/lifecycle plus NullGraphStore; EPHEMERAL and TESTING = isolated in-memory front/lifecycle stores with one ephemeral identity per kernel. Core profiles.py:56 and Runtime di.py:292 show why front-store-only tests would miss persistent lifecycle leakage. FC-09 explicitly corrects it. Transcript persistence must be configured independently in no-disk tests.

## All 32 criteria

PASS below means design requirement/source seam is adequate, with execution still future. PARTIAL means the referenced mandatory finding prevents full satisfaction; no prior verdict is carried forward.

| Criterion | Assessment | Independent source/document basis |
| --- | --- | --- |
| EC-01 | PASS | Current controls, pinned request, iteration authorization; opening/closing integrity and permitted delta. |
| EC-02 | PARTIAL | Whole-source inventory above; Chat memory_mcp.py:168 reveals unclosed consumer seam (002). Annex inventory is not closure. |
| EC-03 | PASS | Chat adapters.py:1735; Runtime di.py:233; reorganization/mutation.py:268; Annex B01–B08/FC-10 preserve actual bindings. |
| EC-04 | PARTIAL | Core interfaces/llm.py:113 and profiles.py:56; REM E guards API; BackupManager:158 becomes unusable (001). |
| EC-05 | PASS | REM E optional capabilities and Annex baseline qualification; model_library.py:287 is shared resolution seam; unknown baseline stops Gate A. |
| EC-06 | PASS | LLM embeddings.py:249,287; Memory vector.py:109 and collection_manager.py:559; REM E/DI-18,22,24 assign shared roles and caches. |
| EC-07 | PASS | graph_scorer.py:330 versus :221; controller.py:500,522; Annex FC-08/REM durable identity explicitly distinguish absent versus invalid vector. |
| EC-08 | PASS | extractor.py:578,657 and Runtime di.py:350; REM DI-33 and FC-14 require extraction LLM separation and complete round trip. |
| EC-09 | PARTIAL | pipeline.py:553; mutation.py:594; recovery.py:412; REM DI-27/28/32 cover guarded paths, but legacy backup compatibility unresolved (001). |
| EC-10 | PASS | consolidator.py:196; promotion.py:423; compactor.py:435; FC-06/07 preserve unsplit structured records and honest effects. |
| EC-11 | PARTIAL | Whole-package/direct/transitive inventory; Runtime di.py:245,292; public MCP error mapping and log ownership need 002/003. |
| EC-12 | PASS | REM durable identity and fresh-store sections, Annex N and FC-11; mutation.py:196 ceiling; changed/same dimensions and smaller capacity mandatory. |
| EC-13 | PARTIAL | REM E explicitly allows independent namespaces and same-space service names; extraction_filter.py:25,67 violates intended isolation unless ownership specified (003). |
| EC-14 | PARTIAL | REM E overflow/result validation, FC-02/08; actual Chat memory_mcp.py:168 erases public failure distinctions (002). |
| EC-15 | PARTIAL | REM DI-18/21/22/27–34 and Annex named nodes are strong future proof requirements; add real outer MCP/log lifecycle witnesses (002/003). |
| EC-16 | PARTIAL | REM exact implementation paths omit memory_mcp.py necessary result-adaptation seam (002); no broad rewrite authority inferred. |
| EC-17 | PASS | REM A/B and Tools plan TD-01..10; Memory/LLM pyprojects and FC-12 define minimal counting without Docling; Certifi floor remains a future exact-resolution gate. |
| EC-18 | PASS | Current bounded controls and both integrity checks coherent; this report supplies fresh findings, matrices and separate scores, no historical correctness inference. |
| FC-01 | PARTIAL | extractor.py:210; extraction_filter.py:44,67; FC-01 fixes first open but misses retained handler ownership (003). |
| FC-02 | PARTIAL | ingestion/mcp.py:138,187 and Chat memory_mcp.py:168; single-record guard adequate, outer failure adaptation/scope incomplete (002). |
| FC-03 | PARTIAL | backup.py:158,273; __main__.py:346; proposed restriction conflicts with positive compatibility premise (001). |
| FC-04 | PASS | analyzer.py:103,146,206: explicit normalized read-only admission before raw SQLite/graph is feasible in allowed seam. |
| FC-05 | PASS | synthesizer.py:712,765: injected-service success plus missing/invalid-service refusal prevents actual omitted-vector Chroma fallback. |
| FC-06 | PASS | consolidator.py:183,196,358: explicit stored-batch acknowledgement rule addresses real unconditional marking; mixed/retry test required. |
| FC-07 | PASS | promotion.py:423,463,569 and Tools memory/lifecycle.py:41: count after true mutation and expose errors through execute text. |
| FC-08 | PASS | controller.py:522,1038 and graph_scorer.py:330: typed errors survive gather/priming/graph; absent vector zero remains; async fallback unwired. |
| FC-09 | PASS | Core profiles.py:56 and Runtime di.py:245,292: all four profiles/front and lifecycle isolation specified; transcript separately controlled. |
| FC-10 | PASS | Chat adapters.py:1735, CLI container.py:72,118: actual pool default/hint and raw constructor/env origin explicitly preserved. |
| FC-11 | PASS | pipeline.py:526,553; mutation.py:196,630: admission before probes; empty dimensions from identity; <=8192 plus independent-service behavior. |
| FC-12 | PASS | Memory pyproject:11,15; Runtime/CLI/Agent dependency edges; narrow embedding-limits extra is explicit, selected assets and minimal installed proof future. |
| FC-13 | PARTIAL | Agent tools/builtins.py:109; multi_agent/coordinator.py:190; Tools inspection.py:12; preprocessing pipeline.py:39 covered; MCP outer caller still fails exact disposition (002). |
| FC-14 | PASS | Existing graph/collection scoring thresholds; FC-14/DI-33 require B/N operational round trip and separate bounded model-quality acceptance, no invented parity. |

## Original mandatory and high/medium requirement dispositions

These are judgments against the current requirement text and current source, not historical verdicts. “Adequate” is design disposition only; all runtime proof remains future.

| Original requirement group | Independent disposition |
| --- | --- |
| OPUS-M1 — Startup rejection logging can pre-create or mutate a vector directory | Incomplete: 003, retained handlers |
| OPUS-M2 — Active opt-in MCP snapshot ingestion is omitted from the route contract | Incomplete: 002, actual publication caller |
| SOL-R5-M01, OPUS-M3 — Public physical backup/restore can bypass binding and overwrite a sidecar | Unresolved compatibility exception: 001 |
| SOL-R5-M02, OPUS-M3 — ConsistencyAnalyzer opens SQLite and graph data outside normalized admission | Adequate at design level; source and future witness in FC-04 row above |
| OPUS-M3 — Legacy synthesis can omit vectors and invoke an implicit Chroma embedder | Adequate at design level; source and future witness in FC-05 row above |
| SOL-R5-M03, ASTRA-R5-001 — Consolidation can acknowledge source turns after summary-storage refusal | Adequate at design level; source and future witness in FC-06 row above |
| ASTRA-R5-002 — Lifecycle counts and tool text can report failed mutations as success | Adequate at design level; source and future witness in FC-07 row above |
| OPUS-M4 — Recall can suppress typed refusals; async graph fallback is not maintained wiring | Adequate at design level; source and future witness in FC-08 row above |
| OPUS-M5 — Runtime ephemeral/testing profiles still construct persistent lifecycle collections | Adequate at design level; source and future witness in FC-09 row above |
| OPUS-A1 — Actual canonical Chat default versus legacy hint, preserved and visible. | Adequate design requirement under FC-10; source/config matrix above, proof still future. |
| OPUS-A3 — B01–B08 qualified identities with absent/placeholder revisions and alias-swap refusal. | Adequate design requirement under FC-10; source/config matrix above, proof still future. |
| OPUS-A4 — Namespace admission before real provider probe. | Adequate design requirement under FC-11; source/config matrix above, proof still future. |
| OPUS-A5 — Preserve CLI raw explicit-origin across default forwarding. | Adequate design requirement under FC-10; source/config matrix above, proof still future. |
| SOL-R5-A02, OPUS-A6 — Actual transitive agent/multi-agent/MCP coverage and namespace distinction. | Partial for MCP public result propagation (002); other indirect dispositions adequate. |
| ASTRA-R5-A02, OPUS-A8 — Declared dimension ceiling and identity-based empty-store behavior. | Adequate design requirement under FC-11; source/config matrix above, proof still future. |
| OPUS-A10 — Headless counter extra/dependency profile without Docling. | Adequate design requirement under FC-12; source/config matrix above, proof still future. |
| OPUS-A7 — Admitted store-only MEMQ reads without inference. | Adequate design requirement under FC-13; source/config matrix above, proof still future. |
| OPUS-A2 — Operational compatibility versus later measured quality evaluation. | Adequate design requirement under FC-14; source/config matrix above, proof still future. |
| OPUS-A11 — Public-unwired preprocessing never a second stored chunk plan. | Adequate design requirement under FC-13; source/config matrix above, proof still future. |

## Scores

Coverage is **9.0/10**: direct/transitive framework coverage **3.6/4.0** (public MCP seam and retained log handlers incomplete); baseline/replacement positive proof **2.5/3.0** (legacy backup B/N deliberately removed without resolved authority); negative identity/overflow/effects **1.9/2.0**; headless/minimal-install/nonembedding **1.0/1.0**. Broad contract coverage merits substantial credit, but inventory labels do not substitute for real outer-call behavior.

Overall is independently **8.7/10**: framework inventory **1.8/2.0**; operational configuration/API compatibility **2.4/3.0**; replacement/namespace safety **2.2/2.5**; bounded proof/reporting **1.8/2.0**; scope/authority **0.5/0.5**. Scores judge proposed design, not absent unapproved implementation. Both are below 9.5. No mandatory finding is waived by a high aggregate score.

## Reproduced checks and exact outputs

All Git/admin processes, including integrity-helper children and administrative script children, inherited the supplied wrapper guard. The exact wrapper prefix was:

`python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-compat-iteration-4col5xog/pass1/inputs/read_only_command.py /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/astra-r6-independent-adyflrsx --`

- `board`: `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate`; exit **0**. Development board validation passed: 36 tasks
- `dashboard`: `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check`; exit **0**. Planning dashboard is current
- `docs`: `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py`; exit **0**. Documentation lifecycle validation passed: 1004 Markdown files checked
- `metadata`: `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py`; exit **0**. Validated 18 pyproject.toml files: version, license, authors, README, URLs, wheel package selection, and internal pins OK
- `whitespace`: `git diff --check 91ac63bad5e46eceddd252d5b7727f7a1d3c623a..8d25d53ac944ace99e3ae430364075b0c1200ff6`; exit **0**. (empty stdout)

Opening and closing invoke `python3 -B INPUTS/check_integrity.py INPUTS/review-request.json` through that exact prefix; each exit 0 / PASS. Extractor invocation through wrapper exited 0 and frozen comparison matched exactly. Amendment Git diff exited 0 and used only request technical/status path arrays. `command-audit.jsonl` records argv, guard, time and exit. Logical index was measured before status by the inspected helper.

Both integrity outputs report HEAD `8d25d53ac944ace99e3ae430364075b0c1200ff6`, branch `feature/cmd-ingest-001`, logical index `7ff069ba5dddc00af444d34fdb1a2dfaa74fde90e3f1a45aa6bd92b2e8fcd087`, 17,673 protected entries and no failures. Protected six-record metadata checks, exact status, pins and staged-diff checks all passed. Preserved dirty YAML and personal-store content were not read as evidence. One static source search requested a nonexistent `ingestion/semantic_chunker.py`; it emitted a path-not-found diagnostic, then the actual `ingestion/chunker.py` was located. This was an exempt static search, not a product/admin check failure.

Inspected only: current design/source, selected test definitions, package dependency declarations and entrypoints. Reproduced: hashes, sanitized controls equality, static source search and the five exact admin checks. Future only: real model/counter parity, version/dependency resolution, Docling/Office/OCR behavior, installed normal/-O proof, mutants, B/N/R runtime tests, model-quality UAT and any acceptance. No product imports/tests/builds, installs/downloads, provider calls, store operations or cleanup were run. Historical root lint/collection/format/MAINT oracle debt remains unwaived; admin success is not whole-repository green.

## Limits, advisories and output audit

Static discovery cannot prove arbitrary dynamically loaded third-party tools; the proposed installed registry and configured-tool witnesses remain necessary. Alias attestation and baseline hosted/local qualification are substantive Gate-A risks, not evidence that the current plan is already infeasible or permission to silently exclude a baseline. The exact Docling/version/formula/notes/counting behavior also remains a hard readiness gate. No web/model-card claim was used as installed proof, and no external browsing was needed for these source-backed findings.

Advisory A1: at final directive freeze, bind the detached background extraction completion/failure witness to the actual ContextAssembler task (`context/assembler.py:415`) rather than only to the Agent wrapper; the outer await can finish when the inner task is merely scheduled. FC-08/13 already require observable failed/retryable status, so this is a concrete proof-location advisory, not a demand for a scheduler rewrite.

All generated reports, commands, logs, hashes and caches are under this fresh mode-0700 private scratch, outside repository and supplied scratch/input trees. Static source reads/text calculations and own-report writes were correctly treated as wrapper-exempt. No repository/input writes or isolation breaches were identified; no cleanup concealed any effects. Closing integrity followed the final shared/input inspection; subsequent work only assembled this report and hashed owned artifacts.

Recommended next gate: controller disposition of these three precise design findings within the existing bounded document cycle. No reviewer repair, reissue, new council, Gate A, construction, model swap, MAINT acceptance, store action or delivery is authorized or performed by this report.

## Evidence hashes

- `start-integrity.json`: `9a66bfff679cc63f52af8d4e713abd63540e61943565348adb0bc4a7552c8fb8`
- `end-integrity.json`: `9a66bfff679cc63f52af8d4e713abd63540e61943565348adb0bc4a7552c8fb8`
- `controls-copy.json`: `b78f12e948b0e941f9387da478226588bc0dcffec02411bf1132ce4a30d8bf90`
- `amendment.txt`: `52423c7c0422fd64051728eecdf3b51c2d9c9d0c67ff0694973af86a2c4571ff`
- `command-audit.jsonl`: `a885fd046c2b2888704ea86a889e96f674f926239e925fb3a991985004438996`
- `source-inventory.json`: `5f8dd2601d47e83eb2e8ee06c9c41893f976d559a65ad22f4585c4391f291116`
- `source-search.txt`: `cf9e13ef07ca2f24f378dec3eb71043e7f98c7542191ca85cf5019d1e9c63f0e`
- `transitive-search.txt`: `47e1cd2189fb9fd4233c6f6934c6d54073b57415014bcf6ca5bb37461a4c6dc3`
- supplied `integrity_helper`: `6ef846532b6caab0c136b50dc9bde1da1816e72742eef6e0522c4e37a36fe9ca`
- supplied `command_wrapper`: `cb0669f81efd0098c104d7b96342fcd614255021ea2bfa49cbbb6af7c2fea248`
- supplied extractor: `a9fd727a2d9715e5b6759034c4bb92160993bd6d0b23efedcea6211f978e4b81`
- supplied current-controls: `b78f12e948b0e941f9387da478226588bc0dcffec02411bf1132ce4a30d8bf90`
