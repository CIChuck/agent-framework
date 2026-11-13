# Independent review — REM-CMD-INGEST-001, pass3/4, global round8

**VERIFIED — design/source-feasibility only.** Mandatory findings: **0**. Coverage **9.5/10**; overall **9.5/10**. These are this seat's independent scores, not a council outcome or permission to execute Gate A.

Reviewer: gpt-6-astra, high effort. Fresh task context; no builder transcript/private reasoning, peer verdicts or raw archived reports used. Ordinary historical status text was encountered only as status context. No nested agent, repairs or shared writes. Explicit shared-checkout exception applies; no worktree was created. Review date: 2026-11-10 America/New_York (UTC receipts dated 2026-11-11).

## Frozen identity and review sequence

Workdir `/Users/chuckrussell/Dev/gendev/agent-framework`; branch `feature/cmd-ingest-001`; HEAD `f43368c503da19fd245730ee579806db95ed3748`. Correction base `f1916747ad7d03e451f2b57dc00542faa6095d7c`; aggregate base `91ac63bad5e46eceddd252d5b7727f7a1d3c623a`.

Request SHA256 was verified BEFORE parsing: `0b9247701339f8fe25dce08d70ec08e8785fbe20c01ea1f4054bc4c51a0a202d`. Verified and inspected helper SHA256 `6ef846532b6caab0c136b50dc9bde1da1816e72742eef6e0522c4e37a36fe9ca`, wrapper `cb0669f81efd0098c104d7b96342fcd614255021ea2bfa49cbbb6af7c2fea248`, extractor `a9fd727a2d9715e5b6759034c4bb92160993bd6d0b23efedcea6211f978e4b81`, sanitized controls `ea18945e10dfd7cb67e12daf2a85f174d98a644e1b279223e92dca82366620e8`. Regenerated controls compare equal as parsed JSON. Whole authority content was not opened or searched; only the verified extractor selected its approved current fields.

Opening integrity measured logical index before status: `d5b9549f8299653d66f6890c54af31f072a63687088a369be3dff0fac9be5e8d`. It verified all authority/document/source pins, exact dirty/untracked status, no staged diff, 17,689 protected entries and the six preserved metadata records. Closing integrity follows the last shared inspection and passes identically (see receipts below). Full frozen pin manifest is `review-inputs.json`; newly discovered source hash inventory is `source-hashes.json`.

Correction delta was obtained first using only request technical/status paths, excluding authority/raw reports. Its graph fallback, pending retention, reason mapping, causal backup scope, task closing, logging, metadata and history corrections were checked against current source. Then the entire current REM, normative annex and Tools companion were examined with the selected aggregate diff. Aggregate product-path diff is empty. No previous verdict was carried forward.

## Findings and residual risk

No mandatory design finding remains in the inspected candidate. No new regression was established by static inspection. This does NOT establish working implementation or waive baseline defects.

1. **A-01, advisory — qualification risk, not missing implementation.** Annex lines85–131 and REM section E require immutable served identity and exact local counting for all eight baseline families. Chat's hosted default may fail that qualification. Check it early in separately authorized Gate A; inability to qualify is a hard stop requiring maintainer disposition. Do not replace the default or exclude it to pass. Required proof is omitted-fields B success and same-name/same-dimension alias-swap refusal, not model-card metadata.
2. **A-02, advisory — public backup proof remains unusually important.** `maintenance/backup.py:137–156` selects fixed root files plus recursive vector/. This supports FU014 classification, but it is not execution proof of a working backup layout. Before construction freeze the paired old/candidate public create/verify/restore/backup_first oracles, including defaults and exact file sets. Unknown baseline stops readiness. Preserve marker bytes/incarnation; no layout/member/engine repair is inferred. Logical-v2 recovery has separate positive proofs.
3. **A-03, advisory — exact boundary freeze.** The design deliberately defers signatures, receipt encoding, collection-name encoding and numeric resource budgets to Gate A. The frozen directive must bind those details, actual installed normal/-O public nodes and call-phase mutation witnesses before construction. Static review cannot validate dynamic tool imports, native conversion cancellation, serving identity or backend execution. No extra architecture work is requested by this observation.

Scope assessment: document conversion/shared chunking and proposed shared embedding/namespace guards cause the narrow compatibility work. MCP is an existing structured-record consumer; its lifecycle and schema are retained. Backups are existing file-copy consumers; their new binding cannot be overwritten. Existing FU013/FU014 defects get zero positive credit and remain unwaived. If new admission cannot coexist safely with working public behavior, stop on that exact dependency rather than repairing the subsystem implicitly.

## Scoring

Scores assess sufficiency and source feasibility of the proposed design, not execution of unapproved future work.

| Coverage rubric | Award / maximum | Reason |
|---|---:|---|
| All-framework direct/transitive coverage | 3.8 / 4.0 | Independent source/AST discovery plus actual composition/error paths; dynamic configured extensions remain a bounded installed-proof risk. |
| Baseline and replacement positive coverage | 2.8 / 3.0 | B01–08 and real cross-subsystem successes are required, including both replacement identities; legacy physical-copy baseline qualification remains delicate. |
| Negative identity/overflow/failure effects | 1.95 / 2.0 | Explicit zero-effect refusals, mixed calls, caches, task errors and mutation witnesses. |
| Headless/minimal/nonembedding | 0.95 / 1.0 | Concrete dependency extra and actual Runtime catalog witnesses; native/backend feasibility remains Gate A. |
| **Total** | **9.5 / 10** | No rounding upward. |

| Overall rubric | Award / maximum | Reason |
|---|---:|---|
| Framework consumer inventory | 1.9 / 2.0 | Broad static discovery with route distinctions; no claim of runtime exhaustiveness. |
| Operational configuration/API compatibility | 2.8 / 3.0 | Actual precedence, raw origin, callable shapes, retained public APIs and positive B/N; hosted baseline remains explicit risk. |
| Model replacement/namespace data safety | 2.4 / 2.5 | Same-dimension identity, namespace incarnation, caches, v2 recovery and profile isolation explicitly governed. |
| Bounded proof/reporting | 1.9 / 2.0 | Exact future consumer/call-phase/install obligations; paired backup and dependency evidence still pending by design. |
| Scope/authority | 0.5 / 0.5 | Causal scope, one further pass maximum, no construction or delivery inference. |
| **Total** | **9.5 / 10** | Advisory score cannot grant acceptance. |

## Independent consumer/disposition and B/N/R matrix

D = direct embedding/vector use; T = transitive contract/store/error consumer. Every B/N entry below is a REQUIRED FUTURE success witness, not a test executed here. B means unchanged supported configuration with optional fields omitted and qualified readiness. N includes changed dimension AND same-dimension changed identity/preparation, smaller capacity and fresh coherent vector/graph/WAL/recovery/cache destinations. R is separate negative proof; refusal cannot replace B/N. All listed sources are relative to the frozen workdir. Function names are exact locators where a line is not shown.

| Consumer | Route | Source | Disposition | B success | N success | R / exclusions | Required proof |
|---|---|---|---|---|---|---|---|
| LLM public documents/query/cache | D; active/public | packages/friday-llm/src/friday_llm/embeddings.py:249,287,334 | Preserve signatures, service/batch/cache/resilience; add shared once-only preparation, capacity and complete result/index checks. | Valid document batches and cached query preserve binding. | Both replacement spaces and smaller capacity work; cache identity changes. | Overflow, alias swap, malformed/index/nonfinite result and cache drift fail before forbidden effects. | DI-18/21/22/24/33; FC-10/12 |
| Shared catalog/resolver | T; active | packages/friday-llm/src/friday_llm/model_library.py; packages/friday-chat/src/friday_chat/adapters.py:1734 | Optional fields resolve from exact readiness; unused services do not disable chosen ones. | Omitted fields; all eight configuration families succeed. | Explicit qualified replacement through same mechanism. | Unqualified baseline hard-stops Gate A, never silently excluded. | FC-10; B01–08 |
| Core protocols/factories and CLI forwarding | T; active/public | packages/friday-core/src/friday_core/interfaces/memory.py:174; packages/friday-core/src/friday_core/profiles.py:54; packages/friday-cli/src/friday_cli/container.py:109 | Narrow identity envelope/open-intent forwarding; preserve default versus explicit origin. | Matching OPEN_BOUND, explicit absent destination; API preserved. | Fresh coherent namespace, all profiles. | Bare vectors, fallback-origin creation and unbound roots refused. | DI-21/29; FC-09/10 |
| ChromaVectorStore | D; active | packages/friday-memory/src/friday_memory/adapters/vector.py:84,109,202 | Guard before clients and every operation; correct text-query role. | Admitted writes, text and precomputed queries, store-only reads. | Variable dimensions and same-dimension new preparation in new root. | Foreign envelope, invalid vectors, wrong root, missing marker; zero client/provider effects. | DI-21/22/28 |
| SimpleVectorStore/front cache | D; active/public | packages/friday-memory/src/friday_memory/adapters/simple_vector.py:109,132 | Same identity/role contract in ephemeral/front store. | Document/query roles preserve normal API. | Independent in-memory identities. | Supplied foreign or malformed vectors fail. | DI-21/22; FC-09 |
| CollectionManager lifecycle/MCP collections | D/T; active | packages/friday-memory/src/friday_memory/retrieval/collection_manager.py:113,174,285,381,481,528 | One admitted identity for all collections; propagate gathered guard errors. | Store/query/get_all/promote/demote/reactivate and snapshot publication. | Fresh coherent replacement collections, no hidden default embedder. | Typed errors escape get_all/gather and cannot be successful empty results. | FC-02/07/08/09 |
| MemoryController semantic recall and priming | D/T; active | packages/friday-memory/src/friday_memory/controller/memory_controller.py:416,499,522,665,998,1160,1564 | Real query vector is shared; retain unscored graph route; propagate named catches. | Full extraction→recall, author/insight/summary reads. | Successful recall in new space with preserved thresholds. | Gather/priming/recent-read/scored-graph guards surface; no empty-success substitution. | FC-08/14 |
| GraphPathScorer public sync/async | D; injectable, not maintained wiring | packages/friday-memory/src/friday_memory/retrieval/graph_scorer.py:222,288,330,382 | Validate present components first. Missing components retain zero in sync/no fallback; qualified async fallback only fills absent components transiently. | All four public APIs; aligned present vectors and absent-component matrix. | Same cases in changed dimension/space with document fallback once. | Foreign/unknown/invalid PRESENT edge or target refuses before fallback/comparison. | FC-08; DI-22 |
| Graph vector producers/adapters | T; maintained writes/preservation | packages/friday-memory/src/friday_memory/context/extractor.py:578; packages/friday-memory/src/friday_memory/maintenance/pipeline.py:1034; packages/friday-memory/src/friday_memory/models/graph.py; packages/friday-memory/src/friday_memory/adapters/graph.py | Reserved envelopes for writes and recovery, without new recall scoring. | Extraction/REEMBED/recovery preserve provenance. | Fresh graph coherent with vector/WAL space. | Foreign envelope refuses comparison/update/restore; absent vectors stay distinct. | DI-21/22/27 |
| Maintained MemoryExtractor | D/T; active | packages/friday-memory/src/friday_memory/context/extractor.py:426,578,650,684,708 | Typed edge/insight/summary failures aggregate; no vectorless fallback after guard refusal; stable output-slot IDs. | Actual graph, insight and summary persistence plus retry. | New model within unsplit capacity succeeds. | Edge guard, mixed batches, false/incomplete persistence and summary failure cannot acknowledge. | FC-06 |
| Chat extraction acknowledgement | T; active | packages/friday-chat/src/friday_chat/adapters.py:_extract_turns | Consume error result, preserve failed/unprocessed pending turns and completed-under-cancellation distinction. | Successful extraction clears only completed turns. | Same stable-ID retry expectations. | Delayed/mixed failure retains eligibility and avoids duplicate record IDs. | FC-06 |
| ContextAssembler / Agent archive / shutdown | T; active | packages/friday-memory/src/friday_memory/context/assembler.py:398; packages/friday-agent/src/friday_agent/base.py:413,500,513; packages/friday-runtime/src/friday_runtime/di.py | Own inner task, telemetry-independent status/wait, close admission before drain; late outer task cannot reopen. | Archive starts and completes owned extraction, no-extractor explicit skip. | Same task ownership under replacement binding. | Delayed error/cancel/late arrival/set_extractor after close cannot falsely complete or reopen sinks. | FC-06 |
| Owned and standalone rejection sinks | T; active/public | packages/friday-memory/src/friday_memory/context/extraction_filter.py:31; packages/friday-memory/src/friday_memory/context/extractor.py:159 | Defer resourceful construction; per-owner handler lease; no-file default isolated from standalone global. | First CREATE_FRESH with log inside vector; two qualified independent owners. | Separate model namespaces keep independent sinks. | No write to old/unbound root; reconfigure/close one owner never affects another. | FC-01 |
| MemoryConsolidator | T; public-unwired | packages/friday-memory/src/friday_memory/context/consolidator.py:136,299 | Persist batch summary before acknowledging source turns; no scheduling changes. | Stored summaries acknowledge only successful source batches. | Qualified replacement unsplit summaries. | Failed/mixed batches remain retryable; no transaction promise. | FC-06 |
| Compaction and derived records | T; active/public | packages/friday-memory/src/friday_memory/maintenance/compactor.py; packages/friday-chat/src/friday_chat/adapters.py | Preserve unsplit summaries and actual result/error projection. | Working compaction and protected record semantics. | Valid smaller-capacity unsplit summaries succeed. | Oversized derived record refuses, never silently re-chunks or marks complete. | DI-22/33; EC-10 |
| MCP preparation/publication/receipt reuse | D/T; active opt-in | packages/friday-chat/src/friday_chat/memory_mcp.py:133; packages/friday-chat/src/friday_chat/adapters.py:309,320; packages/friday-memory/src/friday_memory/ingestion/mcp.py:80; packages/friday-memory/src/friday_memory/retrieval/collection_manager.py:481 | Shared final stored HTML-text guard only; retain pending ID/content and receipts; no new cleanup/counter protocol. | Prepare→append/readback→publish; matching retry store-only, no extra embedding. | Qualified replacement fresh namespace and exact unsplit snapshot. | Capacity capped; other failures no successful skip; false/ambiguous append/readback/cancel/mixed later failure retain pending. | FC-02; tests_chat/test_mcp_memory.py:98,123,460 |
| MCP processor/Runtime/Telemetry | T; active unchanged schemas | packages/friday-chat/src/friday_chat/turns/processor.py:687; packages/friday-runtime/src/friday_runtime/mcp_loading.py:171; packages/friday-telemetry/src/friday_telemetry/models/mcp.py:27 | Observer uses existing reason literals; processor forwarding/schema stay unchanged. | Counts with export off, strict events with export on; old four outcomes preserved. | Same behavior in N; no telemetry dependence for truth. | Invalid/new literal mutant rejected; observer error never changes receipt truth; mixed turn failure remains explicit. | FC-02; reason-subset.json |
| Public physical BackupManager / callers | T; public, module backup and injectable tools | packages/friday-memory/src/friday_memory/maintenance/backup.py:39,137,159,244,275; packages/friday-memory/src/friday_memory/maintenance/reorganizer.py; packages/friday-tools/src/friday_tools/memory/maintenance.py:39 | Fixed D/D-vector marker selector, minimal receipt, no marker restore; old API/default/file rules preserved. | Paired known-working create/verify/restore/backup_first positive; compare destinations and data member set. | Same-incarnation restore under each fresh qualified N; retained live marker. | Wrong/missing/both markers, receipt/digest/identity mismatch or rebind refused even verify_first=False. | FC-03; FU-014 incomplete forms get zero full-recovery credit |
| ConsistencyAnalyzer raw reads | T; public | packages/friday-memory/src/friday_memory/maintenance/analyzer.py:68,87,103,124,146,190,206 | Exact admitted layout and read-only SQLite URI for vector AND transcript. | Provider-offline graph/vector/transcript diagnostics. | Replacement namespace store-only analysis. | No client/open/create/journal effects after refused admission; preserve ordinary schema diagnostics. | FC-04 |
| Legacy synthesizer callable shapes | D; public | packages/friday-memory/src/friday_memory/maintenance/synthesizer.py:183,700,743 | Shared qualified wrapper for embed_query/embed/callable; document preparation once; never omit vectors to invoke default embedder. | All three accepted callable shapes succeed when qualified. | New qualified document identity/capacity succeeds. | No missing/failed/invalid embedder fallthrough to collection.add without vectors. | FC-05 |
| Pruner/fact checker/reorganizer direct clients | D/T; public and maintenance | packages/friday-memory/src/friday_memory/maintenance/pruner.py:114,172; packages/friday-memory/src/friday_memory/maintenance/fact_checker.py:140; packages/friday-memory/src/friday_memory/maintenance/reorganizer.py:775 | Exact normalized root, no fallback probing after guard failure; preserved algorithms/stage order. | Stored-vector comparison, dry-run and working public calls. | Compatible new spaces with unchanged thresholds. | Foreign vectors/root and unresolved capability never become skipped-success maintenance. | DI-28/33; FC-11/14 |
| MAINT pipeline/providers/mutation | D/T; maintained | packages/friday-memory/src/friday_memory/maintenance/pipeline.py:459,951,1031; packages/friday-memory/src/friday_memory/maintenance/mutation.py:200,593,628; packages/friday-chat/src/friday_chat/reorganization/mutation.py:108,157,221 | Admission precedes LLM AND embedding probes; empty dimension from identity, retain ceiling8192. | Qualified mutation/synthesis, empty and graph-only REEMBED. | Variable dimension positive and new same-dimension space. | Zero probe on refusal; over-ceiling model combination stops readiness; no global service disablement. | FC-11; DI-27/28/33 |
| Logical recovery and Chat aggregate | T; maintained | packages/friday-memory/src/friday_memory/maintenance/recovery.py:411,866,1094,1550; packages/friday-chat/src/friday_chat/reorganization/artifacts.py; packages/friday-chat/src/friday_chat/reorganization/coordinator.py | Strict new v2 typed path, separate old v1 inspection; unchanged Chat path fingerprint/journals/transcript1. | Snapshot→verify→same-incarnation restore/rollback retains live identity. | Fresh N namespace gets its own v2; no cross-root cloning. | Mixed versions/tamper/identity loss refuse before live mutation; preserve recovery-required. | DI-27/32 |
| Promotion/decay/reactivation and lifecycle Tool | T; maintained/public | packages/friday-memory/src/friday_memory/lifecycle/promotion.py:334,395,553; packages/friday-tools/src/friday_tools/memory/lifecycle.py:29 | Counts after successful mutations incl false returns; truthful ordinary execute text, preserve dry-run forecasts. | Lifecycle state transition success. | N operations succeed, unsplit records remain intact. | Guard/error/false result does not increment completion; partial errors visible. | FC-07 |
| Factor computation / access buffer / incremental | T; wired store-only metadata | packages/friday-memory/src/friday_memory/retrieval/factor_computer.py:177; packages/friday-memory/src/friday_memory/retrieval/access_buffer.py:flush_all; packages/friday-memory/src/friday_memory/maintenance/incremental.py:194; packages/friday-chat/src/friday_chat/adapters.py:1939,1970,2000 | Admitted guarded handles; unchanged algorithms/WAL/queue/quiescence; Chat projects result.errors. | Working metadata and exit flush positive without inference. | Separate admitted N handles; same algorithms. | Metadata refusal and partial errors visible, no unqualified completed totals. | FC-13 |
| Agent builtins and multi-agent promotion | T; active/public | packages/friday-agent/src/friday_agent/tools/builtins.py:89,145; packages/friday-memory/src/friday_memory/multi_agent/controller.py:54,98; packages/friday-memory/src/friday_memory/multi_agent/coordinator.py:123 | Memory-mediated scope/visibility; shared visibility namespace is not independent embedding space. | Recall/store and approved promotions preserve result/journal contracts. | Independent physical N namespaces permitted. | Failed graph/vector phase exposes failure/partial commit; no new atomicity claim. | FC-13 |
| MEMQ and Tools store-only inspection/reset | T; active/injectable | packages/friday-chat/src/friday_chat/adapters.py; packages/friday-tools/src/friday_tools/memory/inspection.py:29,71,126; packages/friday-tools/src/friday_tools/memory/maintenance.py:103 | Admitted provider-offline reads; reset entire target preflight and retained marker; FU013 query defect preserved. | Stats/get_all/graph/records/list-ingested and existing confirmed-clear witnesses. | Same reads on new N without inference. | No hidden initialization/empty-success; reset refusal before graph/vector/episodic effects. | FC-13; query/search branch zero positive credit |
| Chat file handlers / Commands raw-tail helper | T; maintained | packages/friday-chat/src/friday_chat/commands/files.py:44,122,135; packages/friday-chat/src/friday_chat/commands/registry.py | Shared converter and entry, preserve custom handlers/other parsing, document lines refusal. | Four real formats plus retained text behavior; defaults/overrides. | Same source with model-matched new plan and exact positive count. | Malformed usage before I/O; failed conversion zero ingestion; no placeholder success. | DI-01..17; Tools companion TD-01..10 |
| smart_read small/large/cache and large processor | D/T; public injected; unwired storage in maintained Chat | packages/friday-tools/src/friday_tools/filesystem/smart_read.py:233,376,402,511,582; packages/friday-memory/src/friday_memory/ingestion/large_file_processor.py:810,841 | One shared source chunk plan; unsplit derived summaries; destination/record-specific storage receipt cache. | Headless injected small/large/force_chunked storage and warm-cache success. | Fresh destination invalidates prior storage success even same model. | Disabled→enabled, changed collections/records, counter/profile/source drift cannot bypass. | DI-19/23/30; TD-02/05/10 |
| Generic ToolOutputIngester | D/T; public-unwired | packages/friday-memory/src/friday_memory/ingestion/tool_ingester.py:230,320 | Retain opt-in/security metadata and observable IngestionResult/Task; shared plan, no automatic activation. | Awaited ingest_async and returned fire-and-forget task expose stored result. | Replacement qualified source payload succeeds. | Failure returns stored=False/error; guard cannot silently become success; no extra routing. | DI-19/23; FC-13 |
| DocumentIngestionPipeline/SemanticChunker | T; legacy public-unwired | packages/friday-memory/src/friday_memory/ingestion/pipeline.py; packages/friday-memory/src/friday_memory/ingestion/chunker.py | Retain public preprocessing; never split an already accepted storage plan again. | Existing preprocessing behavior separately characterized. | Not a source of N storage-plan credit. | No double chunker/default or implicit route. | FC-13 |
| Tools factory/readers/direct APIs | T; companion-only routing | packages/friday-tools/src/friday_tools/filesystem/readers/factory.py:288,316,370 | Separate factory and smart_read adoption; direct legacy APIs/XLSM preserved. | Real public conversion, pagination, selected sheet/range versus whole source. | Injected common Memory policy after adoption. | No binary-skip/fallback, sandbox wins, missing assets lazy refusal. | TD-01..10 |
| Runtime catalog and optional installation | T; maintained startup | packages/friday-runtime/src/friday_runtime/tool_loading.py:66 | Real pkgutil/importlib discovery; lazy new modules; counter extra inherited through Memory, no Docling required. | Minimal installed catalog and text ingestion. | Direct LLM extra/injected qualified capability supports N. | Copied-prefix missing optional dependency control distinct from supported installation. | FC-12; DI-08/15 |
| Runtime profiles and independent namespaces | T; maintained | packages/friday-runtime/src/friday_runtime/di.py:245,281,342; packages/friday-core/src/friday_core/profiles.py:24 | FULL/VECTOR_ONLY persistent; EPHEMERAL/TESTING front+lifecycle memory-only; chosen incarnation collection suffix. | Four profiles; separately controlled transcript. | Two kernels different models, same logical names, zero record/dimension cross-talk. | Close/clear own collections only; no shared reset, graph-parent mkdir or late resource reopen. | FC-09; DI-29 |
| Nonembedding context/tool/LLM paths | T; maintained | packages/friday-memory/src/friday_memory/context/assembler.py:242,458; packages/friday-runtime/src/friday_runtime/tool_loading.py:24; packages/friday-chat/src/friday_chat/adapters.py:1649 | Preserve passage routing/tool recommendation, LLM-only config and lazy read/startup/exit. | Provider-independent file read/help/exit and ordinary registration. | Unrelated service names/models still independent. | Unavailable Memory surfaces reason; no stateless false success or unrelated global disable. | EC-11/13/17; FC-12 |
| Inactive migration and disabled CLI/Chat mutations | Inactive or intentionally disabled | packages/friday-memory/src/friday_memory/lifecycle/migration.py:423; packages/friday-memory/src/friday_memory/maintenance/__main__.py:365,412,435,524; packages/friday-chat/src/friday_chat/adapters.py:1035 | No activation/fixed-dimension repair; guard direct storage, retain disabled mutating CLI paths. | Existing read/dry-run/backup only where working. | No N integration credit for inactive branches. | Fixed768 dummy/nonexistent method never counted as compatible success. | EC-16; FC-03/13 |
| Other framework packages/entrypoints | T or unaffected; independently scanned | package-inventory.json; source-discovery.txt; transitive-discovery.txt | Transcript SQLite is unchanged except analyzer consumer admission; telemetry schema unchanged. Commands, MCP transport, Speech, Sandbox, Finance, Moltbook, Optimization contain no discovered embedding/store call in this scan. TUI has no Python source. Existing dynamic integrations remain bounded installed checks. | Nonembedding imports/config/reads remain available. | No new global model dependency. | Actual configured tool discovery, optional absence and public error projection tested; no automatic integrations. | EC-02/11/17; FC-12/13 |

The independent scan enumerated 442 Python files under the explicit 18 package src roots (TUI has zero). `package-inventory.json` records per-package imports; `source-discovery.txt` records direct embedding/precomputed-vector/client/comparison matches and `transitive-discovery.txt` records storage/composition consumers. Static imports/text searches are discovery, not claims of runtime execution. Explicit tests/templates were read separately; protected dirty examples were outside every search root. Source pins were seeds rather than the search universe. Additional paths found include Agent builtins, multi-agent coordinator, Tools inspection, public preprocessing, metadata algorithms and concrete Runtime tool discovery.

## B01–B08 configuration qualification matrix

| Family | Source-backed effective behavior | Required positive B/N | Required R / Gate-A qualification |
|---|---|---|---|
| B01 Chat packaged pool | `friday_chat/adapters.py:1734` indexes embedding_pool.default_service; canonical hint is not an override. | Omitted new fields, actual divergent hint/default, retained batch/cache/resilience and explicit maintenance service. N uses same pool mechanism. | Report ignored hint safely; alias swap fails; never newly redirect memory to hint. |
| B02 Chat non-pool | `adapters.py:1749` uses configured model or text-embedding-3-small and endpoint/credential fallback. | Preserve literal configured/default model and endpoint; qualified readiness supplies absent fields. | Hosted identity may not qualify: hard Gate-A stop, not default replacement. |
| B03 sanitized Chat compatibility | Same non-pool constructor and existing configuration schema; no personal YAML evidence used. | Sanitized immutable alias/endpoint/extraction fixture under B and N. | Absent revision cannot be invented; verify serving identity and counter. |
| B04 Runtime pool | `friday_runtime/di.py:342–376` retains optional extraction embedding service and distinct extraction LLM; memory uses configured default. | Full composition and separately selected compatible extraction service; independent roots may differ. | Incompatible services to same namespace refuse before effects; unused unqualified service cannot disable independent selected service. |
| B05 Runtime legacy | `RuntimeConfig` and DI resolve legacy embedding settings; Core factory receives chosen service. | Existing default/model/endpoint/controls, omitted optional fields; real headless operation. | No independent fallback or guessed identity; explicit fresh path and coherent graph/WAL required. |
| B06 CLI FridayConfig | `container.py:44–142` uses dataclass/environment defaults and forwards strings to Runtime. | Constructor explicit value equal to default, environment explicit value, and bound default open all distinguished. | No-file/unset default must not acquire explicit CREATE_FRESH origin through forwarding. |
| B07 Chat inline maintenance | `adapters.py:1876` and `reorganization/mutation.py:221` construct maintenance services separately. | Retain maintenance model/endpoint/controls and same-space service names. | No silent pool-default substitution; namespace admission before any real LLM/embed probe. |
| B08 Public MaintenanceConfig/injected model | `maintenance/synthesizer.py:700–740` supports embed_query/embed/callable; `provider_contracts.py:176` exposes batch model. | All three qualified callable shapes and actual shared EmbeddingModel use; preparation once in document role. | Unqualified/query-only hidden preparation stops; no omitted-vector Chroma default fallback. |

For all eight: record exact served identity/attestation or pinned immutable deployment, counter/preparation/assets, effective cap and expected dimension. Mutable name/endpoint/dimension alone is insufficient. Unknown baseline qualification blocks Gate A; it cannot silently remove a supported row.

## Exact challenge conclusions and future witnesses

- **Graph:** Chat `adapters.py:1810` and Runtime `di.py:299` omit graph_scorer. Public `graph_scorer.py:247–255` falls back separately on None; sync uses zero components. Future score_path/filter_paths and sync variants must exercise edge absent only, target absent only and both absent. For one path, qualified async fallback calls exactly1/1/2 respectively; sync and async without fallback call0. Present aligned components score nonzero; absence is not an empty/invalid present vector. Validate all present components before the first fallback. Verify once-only document preparation, no graph persistence/backfill, exact thresholds/order and normal/-O execution. Actual maintained recall spies require0 graph-vector comparisons and no unused-vector preflight.
- **MCP:** public `persist_mcp_interaction` retains pending state; tests `test_mcp_memory.py:123–198` assert retry ID/write count after false append, ambiguity, readback, publication and cancellation. Add later-call mixed-turn failures without deleting earlier pending. First stage counts exact final label plus HTML-escaped/wrapped text at CollectionManager/shared service. Existing matching reuse stays store-only. Proposed reasons are statically a subset of MCPEventReason (`reason-subset.json`). Runtime counts before export (`mcp_loading.py:182–194`); future actual enabled/disabled export and mixed-turn error/receipt tests must verify counts/strict event acceptance, not just invoke a lower-level ingester. No automatic discard/counter protocol/schema change.
- **Backups:** default is memory_dir/backups; root form selects fixed files, parent/vector form recurses. Runtime graph root is separately resolved and no maintained Runtime legacy BackupManager constructor was found. FC03 fixed D versus D/vector marker metadata selector plus minimum receipt resolves identity without a new layout engine. Known incomplete forms remain failed/unwaived and cannot count as complete queryable recovery. Paired baseline/candidate public tests must precede construction, with verify_first=False still enforcing identity/receipt/no-marker-overwrite. Logical-v2 snapshots are independent.
- **History:** wrapped selected git show from8d25d53a compared only **Next gate:** vectors. README historical1 + next-phase historical17 + tactical-plan historical17 =35 byte-identical lines, excluding each freeze's first/current gate. Evidence is the three `.history.json` files. Current controls agree on pass3/global8 with one further pass maximum.
- **Other corrections:** task admission closes before drain and late outer Agent calls cannot reopen; extraction false/partial returns cannot acknowledge; owner/no-file/standalone rejection sinks are distinct; recall gather/get_all/scored-graph/author/recent catches propagate guards; four Runtime profiles include shared-Chroma collection isolation, using suffixes rather than ad hoc tenants; mutation empty dimensions derive from admitted identity with8192 ceiling; metadata factor/access/incremental algorithms and WAL remain unchanged with visible Chat errors; FU013 query/search is not a success or incidental repair.
- **Document/Tools:** REM sections A–E and companion TD01–10 specify genuine PDF/DOCX/XLSX/PPTX, local OCR, complete admitted content, structural audit as non-text supplier, formula/cache/hidden units/notes mapping, document/512 plus recursive/fixed for all ingestion sources, source versus unsplit derived records, dependency/Certifi floor and separate factory/smart_read adoption. Exact selected release and native resource feasibility remain Gate A; no speculative runtime assurance is given.

## EC criteria — actual request text and disposition

All PASS outcomes mean design requirement supported by current normative text and inspected source feasibility. They are not implementation conformance results.

### EC-01 — PASS

> Exact current bounded four-pass maintainer authority, candidate pins, current controls and design-only effects. Earlier blocked/passing reviews remain history; every changed-candidate pass is fresh.

Evidence and judgment: Frozen receipts/current controls; authority section above.

### EC-02 — PASS

> Independent framework-wide source inventory, not limited to REM named paths. Discover direct embedding calls, provided/cached vectors, indirect storage/comparisons and affected shared contracts; include unlisted subsystems or source-backed unaffected dispositions.

Evidence and judgment: Independent consumer matrix and package/source inventories; annex minimum is not treated as closure.

### EC-03 — PASS

> Unchanged pre-existing catalog/pool and maintained non-pool configuration preserves default/explicit service, profile, endpoint/credential, batch/cache/resilience selection; no silent rebinding or ingestion-only model selector.

Evidence and judgment: B01–08 matrix; Chat adapters1734, Runtime DI and CLI109; REM E/FC10.

### EC-04 — PASS

> Existing embedding API/protocol callers remain compatible; every necessary store/query-envelope extension has actual downstream consumers classified, narrow allowed paths and regression obligations, including previously unnamed ones.

Evidence and judgment: Core interfaces/memory174, vector/simple adapters, controller/precomputed routes; REM E and scoped allowlist.

### EC-05 — PASS

> Optional new YAML capability fields resolve from qualified exact-identity readiness without mandatory config rewrites. Missing baseline qualification is a readiness stop; parse-only success, guessed metadata, disabled used services or an unguarded lane cannot count as compatibility.

Evidence and judgment: REM E omitted-field rule and annex85–131; B01–08 hard-stop qualification.

### EC-06 — PASS

> Shared LLM owns exact preparation/counting/request/result validation, Memory owns namespace admission; all document/query roles and caches correct, no subsystem-specific duplicate guard and no asymmetric formatting with unknown caller.

Evidence and judgment: LLM embeddings249/287, vector query202, synthesizer700, graph scorer247; REM E/DI22.

### EC-07 — PASS

> Maintained Chat/Runtime do not inject GraphPathScorer and perform zero graph-vector comparisons. Both sync/async public-injectable scorer APIs require identity-safe B/N/R proofs, separate from real query/vector recall propagation; no new scorer wiring or unused-vector preflight.

Evidence and judgment: Graph challenge and matrix; annex400–433/FC08; actual Chat1810 and Runtime299.

### EC-08 — PASS

> Maintain extraction LLM and embedding bindings; typed failures at actual edge/insight/summary persistence cannot become vectorless edges or completed acknowledgement. Cover real Chat pending retry and owned ContextAssembler delayed task/status with telemetry disabled.

Evidence and judgment: Extractor426/578/650/684; Chat _extract_turns; ContextAssembler398 and Agent500; FC06.

### EC-09 — PASS

> Keep working maintenance/public backup consumers operational with minimum new-binding admission/receipt and no marker overwrite. Existing copy/default/member behavior remains; paired baseline proofs distinguish pre-existing FU014 limitations from new regressions. No physical backup repair, layout/default redesign or schema waiver; maintained logical-v2 remains separate.

Evidence and judgment: Backup137/159/275 and recovery866/1550; annex273–322/FC03; causal classification above.

### EC-10 — PASS

> Lifecycle promotion/decay/reactivation, compaction and indirect derived-record/tool/source storage are covered. Document/512 applies only to ingestion planning; no silent re-chunking of structured memory records.

Evidence and judgment: CollectionManager528/586/638, promotion334/395, compactor, smart_read/large processor; REM D/E and FC07.

### EC-11 — PASS

> Runtime/Core/CLI/Chat plus every other maintained package/entrypoint are assessed for direct or transitive effects. Non-embedding operations, LLM-only services, tool registration, startup/background/exit and optional-dependency behavior do not acquire unexplained new failure modes. Distinguish actual wiring, public-unwired and inactive/example code.

Evidence and judgment: All18 source roots and actual Runtime catalog; profile/CLI/Agent/MCP/nonembedding rows; FC09/12/13.

### EC-12 — PASS

> Replacement model tests cover changed dimension and same-dimension different space/preparation. Fresh coherent vector/graph/WAL and relevant recovery/cache roots are explicit. Fresh data assumption does not excuse API/configuration/role/hard-coded dimension regressions or authorize deleting/migrating personal stores.

Evidence and judgment: REM durable identity and fresh-store operation matrix, v2 recovery; DI21/27/29/32/33.

### EC-13 — PASS

> Separate names/timeouts may share one compatible namespace; independently bound namespaces may legitimately use different models. One namespace cannot mix vectors, and a failure in an unrelated unused pool service does not disable a qualified operation.

Evidence and judgment: Annex B/N/R identity distinction; Runtime separate extraction service; B04/07/08 and independent namespaces.

### EC-14 — PASS

> Effective capacity, overflow and full result/index/dimension/finite validation guard every embedding path and cache, with actionable typed propagation and no silent partial-success/error-swallowing loopholes.

Evidence and judgment: REM E overflow1–5 plus FC02/06/08; actual catches and cache/service boundaries inspected.

### EC-15 — PASS

> DI-18/21/22/27-33 and Gate-A inventory are sufficient or identify exact gaps. Require unchanged fixture and replacement-model cross-subsystem positive/negative and normal/optimized installed proof before implementation acceptance; do not demand execution of future Gate-A/model/build tests in this design review.

Evidence and judgment: REM DI18/21/22/27–34 and annex named nodes; exact public/call-phase/normal/-O future proof.

### EC-16 — PASS

> Newly identified affected consumers fit an explicit narrow allowed purpose or are a mandatory document-scope/test gap. No implicit permission for broad subsystem rewrites, automatic routing, model migrations, TUI or maintenance-order redesign.

Evidence and judgment: REM exact path-purpose allowlist; FC03/13 causal stop conditions; inactive and baseline-defect exclusions.

### EC-17 — PASS

> Retained extraction/Tools companion and security/dependency/Certifi constraints remain coherent with framework compatibility; no default dependency/schema/resource change silently breaks unlisted consumers or optional/minimal installations. Pending measured dependency feasibility remains Gate-A, not an invented implementation pass.

Evidence and judgment: REM A/B/D, Certifi section, companion TD01–10; Memory/LLM metadata and real Runtime tool catalog.

### EC-18 — PASS

> Current review state and exact pins are coherent, historical verdicts are not reused as proof, findings and evidence limitations are precise, and report contains complete independent consumer and two-scenario compatibility matrices with honest scores.

Evidence and judgment: Pins, selected diffs, current controls,35 history comparison, full matrices/scores and closing integrity.

## FC criteria — full normative contract and independent disposition

The normative text below is reproduced from the frozen annex, not guessed from IDs. Source/B/N/R citations are the named consumer rows above.

### FC-01 — PASS: Startup/owned rejection logging

Independent judgment: FC-01 addresses the actual global FileHandler/mkdir seam, default no-file owner, standalone calls and late shutdown. Its per-owner change is a direct admission adaptation, not a new logging project.

Source and B/N/R evidence: **Owned and standalone rejection sinks** row (and related rows in the full inventory). Scope remains the primary REM explicit path-purpose allowlist. Proof is future actual-public, normal/-O and call-phase negative evidence specified in the annex; none is claimed executed.

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

### FC-02 — PASS: Active MCP snapshots and public failure mapping

Independent judgment: Public persistence has no automatic discard; existing tests assert exact pending-ID/write-count reuse. The corrected final-text shared guard, existing literal union and no-extra-write reuse fit the actual constructors and processor.

Source and B/N/R evidence: **MCP preparation/publication/receipt reuse** row (and related rows in the full inventory). Scope remains the primary REM explicit path-purpose allowlist. Proof is future actual-public, normal/-O and call-phase negative evidence specified in the annex; none is claimed executed.

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

### FC-03 — PASS: Compatible public physical backups

Independent judgment: Source supports FU014: root-only allowlist omits UUID segment directories in vector form; parent/vector recursion covers them, while standalone signature cannot describe Runtime split graph. Marker protection and minimal receipt are necessary new-identity adaptations; paired old API/file/default witnesses prevent using FU014 to excuse regressions.

Source and B/N/R evidence: **Public physical BackupManager / callers** row (and related rows in the full inventory). Scope remains the primary REM explicit path-purpose allowlist. Proof is future actual-public, normal/-O and call-phase negative evidence specified in the annex; none is claimed executed.

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

### FC-04 — PASS: Analyzer and raw SQLite

Independent judgment: All three raw SQLite opens and graph loading require admission; explicit read-only URI mode prevents new refusal paths from producing journals. No algorithm repair required.

Source and B/N/R evidence: **ConsistencyAnalyzer raw reads** row (and related rows in the full inventory). Scope remains the primary REM explicit path-purpose allowlist. Proof is future actual-public, normal/-O and call-phase negative evidence specified in the annex; none is claimed executed.

**FC-04 — analyzer and raw SQLite.** Public ConsistencyAnalyzer uses
the resolved exact layout and shared store-only admission before live graph or
SQLite reads, with no alternative-root probing. All its SQLite opens, including
Chroma and transcript databases, use explicit read-only URI mode and cannot
create absent files/journals. No provider/tokenizer for admitted store-only
analysis. Preserve algorithms and ordinary schema diagnostics; typed admission
failure cannot become successful empty analysis. Offline historical artifact
inspection is separate and not positive admitted live-analysis proof.

### FC-05 — PASS: No hidden embedder, retained callable shapes

Independent judgment: Current generator returns None on absent/failing callable and accepts three shapes; qualified wrappers and no omitted embeddings close the relevant new-guard fallthrough while preserving public forms.

Source and B/N/R evidence: **Legacy synthesizer callable shapes** row (and related rows in the full inventory). Scope remains the primary REM explicit path-purpose allowlist. Proof is future actual-public, normal/-O and call-phase negative evidence specified in the annex; none is claimed executed.

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

### FC-06 — PASS: Extraction, background ownership and consolidation

Independent judgment: Source confirms inner unowned task, broad per-edge/batch/summary catches and Chat error acknowledgement. The contract separately fixes guard-specific reporting, stable IDs, batch acknowledgement and late-task admission without Agent protocol/scheduler changes.

Source and B/N/R evidence: **Maintained MemoryExtractor** row (and related rows in the full inventory). Scope remains the primary REM explicit path-purpose allowlist. Proof is future actual-public, normal/-O and call-phase negative evidence specified in the annex; none is claimed executed.

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

### FC-07 — PASS: Lifecycle truthfulness

Independent judgment: Current counters increment before mutation and Tools text can report completion. FC07 requires actual successful effects including false-return handling, while retaining dry-run prospective counts and thresholds.

Source and B/N/R evidence: **Promotion/decay/reactivation and lifecycle Tool** row (and related rows in the full inventory). Scope remains the primary REM explicit path-purpose allowlist. Proof is future actual-public, normal/-O and call-phase negative evidence specified in the annex; none is claimed executed.

**FC-07 — lifecycle truthfulness.** In non-dry-run mode count promotion,
demotion/reactivation only after successful mutation, respecting false returns
as failures as well as exceptions. Preserve prospective dry-run counts. Keep
partial results and errors visible through both structured results and ordinary
public lifecycle-tool `execute()` text. Do not bury errors solely in `data` while
displaying completed counts. Preserve thresholds/order and generic Tools APIs.

### FC-08 — PASS: Actual recall and injectable graph scoring

Independent judgment: Both composition roots omit scorer injection. The named gather/catch seams exist. Public sync/async fallback distinction matches source; invalid present components must all be checked before fallback. No new wiring.

Source and B/N/R evidence: **GraphPathScorer public sync/async** row (and related rows in the full inventory). Scope remains the primary REM explicit path-purpose allowlist. Proof is future actual-public, normal/-O and call-phase negative evidence specified in the annex; none is claimed executed.

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

### FC-09 — PASS: Runtime profile matrix and concrete ephemeral isolation

Independent judgment: Runtime currently constructs lifecycle CollectionManager with path regardless of front profile. Static installed Chroma source identifies shared ephemeral system. Per-incarnation collection suffix is a concrete compatible isolation mechanism; backend encoding limits remain a Gate-A freeze obligation.

Source and B/N/R evidence: **Runtime profiles and independent namespaces** row (and related rows in the full inventory). Scope remains the primary REM explicit path-purpose allowlist. Proof is future actual-public, normal/-O and call-phase negative evidence specified in the annex; none is claimed executed.

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

### FC-10 — PASS: Configuration and CLI origin

Independent judgment: Actual Chat uses pool default despite hint; non-pool defaults are hosted. FridayConfig loses origin when it forwards defaults, so internal sentinel/origin handoff is necessary and explicitly scoped. Immutable identity qualification remains a hard Gate-A stop.

Source and B/N/R evidence: **Core protocols/factories and CLI forwarding** row (and related rows in the full inventory). Scope remains the primary REM explicit path-purpose allowlist. Proof is future actual-public, normal/-O and call-phase negative evidence specified in the annex; none is claimed executed.

**FC-10 — configuration and CLI origin.** Apply B01–B08, including divergent
Chat legacy hint versus actual pool default. Retain raw explicit-origin from
YAML/environment/constructor before default merging or dataclass forwarding.
An explicitly supplied literal equal to the default qualifies as explicit;
a fallback value passed internally by FridayConfig does not. Use an internal
typed origin/sentinel handoff without removing existing caller arguments or
inventing a new public YAML knob. If origin cannot be preserved for a maintained
constructor shape, stop and reconcile instead of assuming it was explicit.

### FC-11 — PASS: Maintenance admission, probe and dimensions

Independent judgment: Actual pipeline probes both synthesizer and embedding providers; _collection_dimension returns None for empty rows. Contract orders admission first and substitutes admitted dimension only where needed, retaining8192.

Source and B/N/R evidence: **MAINT pipeline/providers/mutation** row (and related rows in the full inventory). Scope remains the primary REM explicit path-purpose allowlist. Proof is future actual-public, normal/-O and call-phase negative evidence specified in the annex; none is claimed executed.

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

### FC-12 — PASS: Headless counting dependencies

Independent judgment: Existing Memory pins LLM and tiktoken; LLM has no counter extra today. Proposed narrow extra can serve Runtime/CLI/Agent without Docling, with real catalog imports and unavailable-package controls separately specified.

Source and B/N/R evidence: **Runtime catalog and optional installation** row (and related rows in the full inventory). Scope remains the primary REM explicit path-purpose allowlist. Proof is future actual-public, normal/-O and call-phase negative evidence specified in the annex; none is claimed executed.

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

### FC-13 — PASS: Indirect consumers and inspection

Independent judgment: Independent discovery confirms metadata algorithms, Agent/archive, multi-agent partial commit, Tools reset/inspection and smart_read cache paths. Guarded handles/error projection preserve algorithms; FU013 search defect receives no positive credit.

Source and B/N/R evidence: **Factor computation / access buffer / incremental** row (and related rows in the full inventory). Scope remains the primary REM explicit path-purpose allowlist. Proof is future actual-public, normal/-O and call-phase negative evidence specified in the annex; none is claimed executed.

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

### FC-14 — PASS: Operational compatibility versus model quality

Independent judgment: Deterministic B/N/R proves shapes/effects and binding, not relevance. Threshold preservation plus later bounded model quality/UAT is appropriate; no model is selected by this review.

Source and B/N/R evidence: **LLM public documents/query/cache** row (and related rows in the full inventory). Scope remains the primary REM explicit path-purpose allowlist. Proof is future actual-public, normal/-O and call-phase negative evidence specified in the annex; none is claimed executed.

**FC-14 — operational compatibility versus model quality.** Record existing
retrieval/path/pruning thresholds without silently retuning them. B/N deterministic
success/shape/error witnesses prove operational contracts, not semantic quality.
When a real replacement is selected, require a separate bounded relevance and
false-duplicate evaluation/UAT on disposable fixtures before accepting that model.
Define measures and acceptable results in that later model-readiness envelope;
do not claim quality parity or tune thresholds using invented evidence now.
Qwen4B remains illustrative.

## Correction-map requirements independently assessed

The map is a requirements index only. The following assessments refer to the source-backed FC judgments above, not to prior reports or controller closure labels. All are sufficient proposed dispositions; no old verdict is adopted.

| Requirement | Independent assessment/evidence |
|---|---|
| INGEST-EC-01: Startup rejection logging can pre-create or mutate a vector directory | PASS design sufficiency; independently assessed in FC-01 above, with actual caller and scope/refusal distinctions. |
| INGEST-EC-02: Active opt-in MCP snapshot ingestion is omitted from the route contract | PASS design sufficiency; independently assessed in FC-02 above, with actual caller and scope/refusal distinctions. |
| INGEST-EC-03: Public physical backup/restore can bypass binding and overwrite a sidecar | PASS design sufficiency; independently assessed in FC-03 above, with actual caller and scope/refusal distinctions. |
| INGEST-EC-04: ConsistencyAnalyzer opens SQLite and graph data outside normalized admission | PASS design sufficiency; independently assessed in FC-04 above, with actual caller and scope/refusal distinctions. |
| INGEST-EC-05: Legacy synthesis can omit vectors and invoke an implicit Chroma embedder | PASS design sufficiency; independently assessed in FC-05 above, with actual caller and scope/refusal distinctions. |
| INGEST-EC-06: Consolidation can acknowledge source turns after summary-storage refusal | PASS design sufficiency; independently assessed in FC-06 above, with actual caller and scope/refusal distinctions. |
| INGEST-EC-07: Lifecycle counts and tool text can report failed mutations as success | PASS design sufficiency; independently assessed in FC-07 above, with actual caller and scope/refusal distinctions. |
| INGEST-EC-08: Recall can suppress typed refusals; async graph fallback is not maintained wiring | PASS design sufficiency; independently assessed in FC-08 above, with actual caller and scope/refusal distinctions. |
| INGEST-EC-09: Runtime ephemeral/testing profiles still construct persistent lifecycle collections | PASS design sufficiency; independently assessed in FC-09 above, with actual caller and scope/refusal distinctions. |
| OPUS-A1: Actual canonical Chat default versus legacy hint, preserved and visible. | PASS design sufficiency; independently assessed in FC-10 above, with actual caller and scope/refusal distinctions. |
| OPUS-A3: B01–B08 qualified identities with absent/placeholder revisions and alias-swap refusal. | PASS design sufficiency; independently assessed in FC-10 above, with actual caller and scope/refusal distinctions. |
| OPUS-A4: Namespace admission before real provider probe. | PASS design sufficiency; independently assessed in FC-11 above, with actual caller and scope/refusal distinctions. |
| OPUS-A5: Preserve CLI raw explicit-origin across default forwarding. | PASS design sufficiency; independently assessed in FC-10 above, with actual caller and scope/refusal distinctions. |
| SOL-R5-A02, OPUS-A6: Actual transitive agent/multi-agent/MCP coverage and namespace distinction. | PASS design sufficiency; independently assessed in FC-13 above, with actual caller and scope/refusal distinctions. |
| ASTRA-R5-A02, OPUS-A8: Declared dimension ceiling and identity-based empty-store behavior. | PASS design sufficiency; independently assessed in FC-11 above, with actual caller and scope/refusal distinctions. |
| OPUS-A10: Headless counter extra/dependency profile without Docling. | PASS design sufficiency; independently assessed in FC-12 above, with actual caller and scope/refusal distinctions. |
| OPUS-A7: Admitted store-only MEMQ reads without inference. | PASS design sufficiency; independently assessed in FC-13 above, with actual caller and scope/refusal distinctions. |
| OPUS-A2: Operational compatibility versus later measured quality evaluation. | PASS design sufficiency; independently assessed in FC-14 above, with actual caller and scope/refusal distinctions. |
| OPUS-A11: Public-unwired preprocessing never a second stored chunk plan. | PASS design sufficiency; independently assessed in FC-13 above, with actual caller and scope/refusal distinctions. |
| IC-01: Retain public create and same-incarnation identity-safe restore; no class/API retirement or generic bridge. | PASS design sufficiency; independently assessed in FC-03 above, with actual caller and scope/refusal distinctions. |
| IC-02: Own actual ContextAssembler task/status and drain at existing Runtime shutdown; preserve Agent/Core signatures. | PASS design sufficiency; independently assessed in FC-06 above, with actual caller and scope/refusal distinctions. |
| IC-03: Real Chat MCP observer/receipt failure mapping, narrow memory_mcp.py scope. | PASS design sufficiency; independently assessed in FC-02 above, with actual caller and scope/refusal distinctions. |
| IC-04: Per-owner admitted rejection sink with lifecycle/reconfiguration; no global fan-out. | PASS design sufficiency; independently assessed in FC-01 above, with actual caller and scope/refusal distinctions. |
| IC-05: Both graph scorer APIs are injectable only; actual Chat/Runtime unscored route gets no unused-vector preflight. | PASS design sufficiency; independently assessed in FC-08 above, with actual caller and scope/refusal distinctions. |
| IC-06: Typed extraction refusal surfaces before completed acknowledgement; stable-ID retry and truthful mixed output. | PASS design sufficiency; independently assessed in FC-06 above, with actual caller and scope/refusal distinctions. |
| OPUS-R6-A1: Per-incarnation physical ephemeral collections despite shared Chroma system. | PASS design sufficiency; independently assessed in FC-09 above, with actual caller and scope/refusal distinctions. |
| OPUS-R6-A2: Name get_all/priming/author read catch seams and typed propagation. | PASS design sufficiency; independently assessed in FC-08 above, with actual caller and scope/refusal distinctions. |
| OPUS-R6-A3: Explicit public Tools wrappers and disabled Chat legacy/dry-run dispositions. | PASS design sufficiency; independently assessed in FC-13 above, with actual caller and scope/refusal distinctions. |
| OPUS-R6-A4: Actual Runtime pkgutil module catalog minimal-install witness. | PASS design sufficiency; independently assessed in FC-12 above, with actual caller and scope/refusal distinctions. |
| OPUS-R6-A5: Qualified shared-guard wrapper route for all retained callable shapes. | PASS design sufficiency; independently assessed in FC-05 above, with actual caller and scope/refusal distinctions. |
| OPUS-R6-A6: Admission before LLM synthesizer probe as well as embeddings. | PASS design sufficiency; independently assessed in FC-11 above, with actual caller and scope/refusal distinctions. |
| OPUS-R6-A7: Current next-decision authority and pass count reconciled. | PASS design sufficiency; independently assessed in EC-01/18 above, with actual caller and scope/refusal distinctions. |
| OPUS-R6-A8: Do not activate inert Chat rejection-log setting. | PASS design sufficiency; independently assessed in FC-01 above, with actual caller and scope/refusal distinctions. |
| OPUS-R6-A9: Early visibility of hosted baseline immutable-identity feasibility stop. | PASS design sufficiency; independently assessed in FC-10 above, with actual caller and scope/refusal distinctions. |
| OPUS-R6-A10: Read-only transcript SQLite as well as Chroma. | PASS design sufficiency; independently assessed in FC-04 above, with actual caller and scope/refusal distinctions. |
| IC-07: Missing vectors: zero only for sync/async without fallback; retain qualified async fallback on absent components and reject invalid present vectors first. | PASS design sufficiency; independently assessed in FC-08 above, with actual caller and scope/refusal distinctions. |
| IC-08: Keep pending records after partial/ambiguous failure/cancellation and same-ID no-extra-embedding retry; no newly automatic discard. | PASS design sufficiency; independently assessed in FC-02 above, with actual caller and scope/refusal distinctions. |
| IC-09: Use existing telemetry reason literals directly in the Chat memory_mcp observer union; real processor/provider forwarding stays unchanged and is tested. | PASS design sufficiency; independently assessed in FC-02 above, with actual caller and scope/refusal distinctions. |
| IC-10: Restore exactly35 historical Next gate lines from8d25d53a; only current gate changes subsequently. | PASS design sufficiency; independently assessed in EC-18 above, with actual caller and scope/refusal distinctions. |
| IC-11: Minimum new-binding evidence/admission and marker protection while preserving old backup file/default behavior; pre-existing vector/split completeness limitations recorded as FU014, with paired baseline proofs and no complete-recovery credit. | PASS design sufficiency; independently assessed in FC-03 above, with actual caller and scope/refusal distinctions. |
| OPUS-R7-A1: Name scored-graph except and recall gather typed-failure seams. | PASS design sufficiency; independently assessed in FC-08 above, with actual caller and scope/refusal distinctions. |
| OPUS-R7-A2: Close task admission before drain; late outer Agent arrival skips unavailable, no reopened sink. | PASS design sufficiency; independently assessed in FC-06 above, with actual caller and scope/refusal distinctions. |
| OPUS-R7-A3: Default no-file owned sink vs standalone logger separation; both inert Chat flags remain inert. | PASS design sufficiency; independently assessed in FC-01 above, with actual caller and scope/refusal distinctions. |
| OPUS-R7-A4: Explicit mutation.py empty dimension/graph-only FC11 purpose. | PASS design sufficiency; independently assessed in FC-11 above, with actual caller and scope/refusal distinctions. |
| OPUS-R7-A5: Wired metadata factor/access/incremental consumers, unchanged algorithms and explicit error projection. | PASS design sufficiency; independently assessed in FC-13 above, with actual caller and scope/refusal distinctions. |
| OPUS-R7-A6: Existing VectorInspectionTool query/search mismatch gets FU013/no positive credit, no incidental repair. | PASS design sufficiency; independently assessed in FC-13 above, with actual caller and scope/refusal distinctions. |
| OPUS-R7-A7: Collection suffix isolation chosen; tenant/database alternative not mixed in ad hoc. | PASS design sufficiency; independently assessed in FC-09 above, with actual caller and scope/refusal distinctions. |
| OPUS-R7-A8: Trace existing MCP constructors to the CollectionManager shared guard; no separate MCP counter/preflight protocol and no provider requirement for store-only reuse. | PASS design sufficiency; independently assessed in FC-02 above, with actual caller and scope/refusal distinctions. |
| OPUS-R7-A9: Mark old round1–4 authority historical/superseded. | PASS design sufficiency; independently assessed in EC-01 above, with actual caller and scope/refusal distinctions. |

## Reproduced checks, conduct and limits

All Git/admin and child invocations used exactly this prefix (command-audit.jsonl records argv, cwd, forced environment and exit):

```
python3 -B /var/folders/dh/wfnmsgpn1yl83xlbmc109sf40000gn/T/ingest-compat-iteration-4col5xog/pass3/inputs/read_only_command.py /tmp/astra-pass3-independent-y8_m6ocj --
```

| Check | Exact wrapped argv after prefix | Exit/result |
|---|---|---|
| Opening integrity | python3 -B INPUTS/check_integrity.py INPUTS/review-request.json | 0, PASS; start-integrity.txt |
| Controls extractor | python3 -B INPUTS/extract_current_controls.py | 0; JSON equal to frozen controls |
| Board | uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate | 0;36 tasks |
| Dashboard | uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py render --check | 0; current |
| Documentation | uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-documentation-lifecycle.py | 0;1012 Markdown files |
| Metadata | uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/check-package-metadata.py | 0;18 pyproject files |
| Whitespace | git diff --check 91ac63bad5e46eceddd252d5b7727f7a1d3c623a..f43368c503da19fd245730ee579806db95ed3748 | 0 |
| Correction and aggregate | git diff RANGE -- exact technical_diff_paths + status_diff_paths from request | 0 each; correction-delta.txt / aggregate-selected.diff |
| Product change boundary | git diff --name-only AGGREGATE_RANGE -- packages main.py scripts | 0; empty output |
| Historical vectors | git show 8d25d53a:docs/planning/active/command-refactor/{README.md,next-phase.md,tactical-plan.md}, three separate calls | 0 each;35 historical lines exact |
| Closing integrity | python3 -B INPUTS/check_integrity.py INPUTS/review-request.json | 0, PASS; end-integrity.json |

INPUTS abbreviates the exact supplied inputs directory used in the wrapper prefix. RANGE values are the complete hashes in the frozen identity section. No product imports, tests, builds, installs, resolution, downloads, provider/model operations or personal-state reads were executed. The admin scripts are the exact five requested exceptions. Static Python used -B. Static installed Chroma source was read only at `.venv/lib/python3.13/site-packages/chromadb/api/shared_system_client.py:14–62`; this supports the shared-system design concern and is not installed execution proof.

All output reports, extracted controls, selected diffs, hashes, inventories and audit files are in OWN. Wrapper cache/temp roots are OWN/uv-cache, OWN/xdg-cache and OWN/tmp. No supplied scratch/input file was written. No checkout, source, test, metadata, staging, commit, cleanup, personal configuration or .venv mutation occurred. No broad packages/repository YAML search was used: package discovery was confined to explicit packages/*/src roots, excluding the two dirty examples structurally before search. Only the supplied integrity helper read/hash/statted protected state. No raw peer reports or whole authority content were used. No web/model-card claim is treated as external verified fact; referenced release/model assertions remain future readiness verification.

Future evidence: every supported B/N operational path must succeed; exact public wrappers and stored data/IDs must be observed, not only helper calls. Use offline real counter assets, real converters/OCR and canonical installed origins; run normal and optimized modes. Required mutants include ignored binding, same-dimension foreign envelope, hidden truncation, invalid indices/result, swallowed typed errors, fallback on present foreign graph vectors, duplicate MCP staging/discard, unknown observer reason, marker overwrite/rebind, default-origin creation, global log fan-out, late-task reopening, shared ephemeral collection collision, empty-dimension failure, implicit embedder and stale cache success. Each rejection needs a named canonical-origin call-phase assertion; setup/import/collection failure earns no rejection credit. No such mutants were executed here.

Known baseline debt remains failed/unwaived: root Ruff534; root collection test_display conflict7196; legacy formatting and MAINT oracle debt. FU013 and FU014 are separate source-classified defects, not fresh runtime failures reproduced here. No runtime, dependency feasibility, model quality, MAINT acceptance, human UAT or delivery assurance follows this review.

## Closing receipt and next gate

```json
{
  "outcome": "PASS",
  "request_sha256": "0b9247701339f8fe25dce08d70ec08e8785fbe20c01ea1f4054bc4c51a0a202d",
  "candidate": "f43368c503da19fd245730ee579806db95ed3748",
  "branch": "feature/cmd-ingest-001",
  "logical_index_sha256": "d5b9549f8299653d66f6890c54af31f072a63687088a369be3dff0fac9be5e8d",
  "protected_entries": 17689,
  "failures": []
}
```

This seat verifies bounded proposed design/source feasibility. Controller must reconcile all three fresh seats against this exact candidate and both score thresholds, without replacing/reissuing seats. This is pass3/4/global8; at most one further full correction/review pass remains, blocked/incomplete included. After pass4 stop for maintainer guidance. No Gate A, construction, model activation, reset/migration, MAINT acceptance or delivery authority is granted.
