# REM-CMD-INGEST-001 — compatibility cycle pass 1/4 (global round 6) — Opus seat review

Seat: claude-opus-5-5, high effort. Fresh, read-only design/source-feasibility review.
Candidate `8d25d53ac944ace99e3ae430364075b0c1200ff6` on `feature/cmd-ingest-001`;
amendment base `91ac63bad5e46eceddd252d5b7727f7a1d3c623a`.
Private scratch: `/private/tmp/claude-501/-Users-chuckrussell-Dev-gendev-agent-framework/30d95a73-4ec3-4b90-8f63-b610f782d20c/scratchpad/rev-ingest-p1-pdvAta/`
(outside the checkout and all supplied input paths).

## Outcome

**CHANGES_REQUESTED** — three mandatory findings (M1–M3), ten advisories.

| Score | Value | Threshold (controller gate, not a scoring target) |
| --- | --- | --- |
| Coverage | **7.7 / 10** | ≥ 9.5 — not met |
| Overall | **8.0 / 10** | ≥ 9.5 — not met |

The revision is a large, mostly accurate improvement: the normative annex, B01–B08,
FC-01–14, the fresh-store/sidecar design, the MCP reclassification, FC-09 profile
correction and FC-10 origin handling are source-backed and feasible. Three seams
are wrong or missing in ways that a construction directive would inherit:
graph path scoring is not actually wired in maintained recall (M1); the FC-03
exception is broader than its safety rationale and conflicts with the maintainer's
compatibility premise (M2); and maintained conversation extraction swallows
storage/embedding refusals and then acknowledges the turn (M3).

## Mandatory findings

### M1 — FC-08 / REM §E / DI-22 misclassify graph path scoring as maintained recall

- Evidence. `MemoryController.__init__` accepts `graph_scorer=None` and stores it
  (`packages/friday-memory/src/friday_memory/controller/memory_controller.py:137,181`).
  `_retrieve_graph_with_scoring` returns unscored base results when no scorer is
  present (`memory_controller.py:1589-1591`). Neither maintained composition root
  injects one: Chat `build_framework_memory_adapter`
  (`packages/friday-chat/src/friday_chat/adapters.py:1810-1817`) and Runtime
  `_create_memory_controller` (`packages/friday-runtime/src/friday_runtime/di.py:299-306`).
  A repository-wide search finds no `graph_scorer=` or `GraphPathScorer(` in any
  maintained `src` (only the docstring at `graph_scorer.py:125` and tests at
  `tests_memory/test_controller_lifecycle.py:95-103,345-360`). Stored graph-edge
  vectors therefore have **no maintained similarity consumer**. They are written by
  extraction (`extractor.py:572-592`) and MAINT REEMBED (`pipeline.py:1029-1060`),
  and they are preserved by recovery. The scorer itself silently returns 0.0 for
  mismatched lengths (`graph_scorer.py:34-35`).
- Defect. Annex FC-08 says "Maintained recall uses synchronous precomputed graph
  scoring". The consumer table (row "Maintained sync graph scorer and semantic
  recall"), REM line 707 and DI-22 ("maintained sync graph scoring") say the same.
  The FC-08 node (`test_recall_propagates_embedding_refusals`: "Controller/scorer,
  Chat recall, Runtime agent and recall_memory tool") cannot show graph-vector
  identity refusal through Chat/Runtime public consumers without newly wiring a
  scorer, which the annex forbids. The REM §E "check the selected graph vector
  provenance at operation preflight" rule would also add a new failure mode to
  recall paths that never compare graph vectors (EC-11). DI-34 explicitly
  requires actual-maintained versus public-unwired classification.
- Narrow fix (document only). Reclassify both `filter_paths_sync` and async
  `score_path` fallback as *public-injectable, not wired in maintained Chat/Runtime
  composition*. In maintained routes, graph vectors are write/preserve-only:
  extraction, MAINT REEMBED, recovery snapshot/rollback. Keep identity envelopes on
  those writes and snapshots. Apply the "foreign/unknown provenance fails the
  semantic operation; absent vector → existing zero" rule to the injected scorer
  API only. State that unscored maintained recall gains no graph-vector preflight.
  Keep "no new wiring". Correct REM line 707, DI-22 and the annex row.
- Future proof. Add a spy witness that actual Chat and Runtime recall perform zero
  graph-vector comparisons. Add a public injected-scorer B/N positive and a
  same-dimension foreign-identity R negative, labelled as capability proof rather
  than route proof. Keep FC-08 maintained-recall propagation tests for the query
  embedding, vector and insight/summary paths.

### M2 — FC-03 legacy physical-copy restriction is broader than its safety rationale and is not maintainer-dispositioned

- Evidence. The identity hazard is restore. `BackupManager.restore_backup` copies
  every manifest file back over `memory_dir` (`backup.py:273-326`), and
  `_find_files_to_backup` recursively includes `vector/**`
  (`backup.py:137-156`). So a restore can overwrite or clone
  `embedding-space.json`, including its incarnation. `create_backup`
  only reads the source and writes under the backup root (`backup.py:158-238`).
  The live namespace is mutated only if the backup root lies inside it (default
  `memory_dir/backups`, `backup.py:68-70`). `python -m friday_memory.maintenance
  backup` is **enabled** today (`__main__.py:346-362`). Only restore and
  non-dry-run mutations fail closed (`__main__.py:330-343,365-367`). Other public
  callers include `MemoryReorganizer.backup()` and the `backup_first` paths
  (`reorganizer.py:227-238,250-270,289,329,357,900,1162-1164`), plus the public Tools
  `MemoryMaintenanceTool` (`friday_tools/memory/maintenance.py:41-43`).
- Defect. FC-03 refuses legacy create *and* live restore for every bound
  namespace. Under the fresh-store policy, every supported B and N namespace is
  bound, so the only operational CLI backup command and the public create API stop
  working everywhere. The remedy points to the Memory-v2 snapshot API, which has
  no module-CLI equivalent. The authorization record shows this restriction was
  the author's chosen disposition ("Choose a bounded explicit compatibility
  exception"). The maintainer did not decide it: the authorization only directs
  incorporating findings. That conflicts with the maintainer's acceptance premise
  (REM 668-671: keep existing consumers operational under an admitted namespace),
  and the annex's own rule says an exception needs maintainer disposition.
  Declaring an exception does not make it compatible.
- Narrow fix. Limit the exception to the hazards: (a) live restore onto any
  bound or pending namespace; (b) restore of a bound artifact to any destination,
  which would be a clone; (c) a backup root that resolves inside the vector
  namespace. Keep `create_backup` operational under store-only OPEN_BOUND
  admission. The copy includes the sidecar as evidence, causes no namespace
  mutation and keeps the legacy manifest classes. Alternatively, obtain and record
  explicit maintainer approval of the broader create restriction, with its
  operator remedy.
- Future proof. FC-03 node: B and N positive admitted `create_backup` through the
  public API and through module `backup`, with unchanged live bytes, sidecar and
  mtimes. R: refused restore (live bound, bound-artifact clone, pending) and an
  in-namespace backup root, all before any directory creation or copy. Keep the
  maintained v2 snapshot/restore positive.

### M3 — maintained conversation extraction swallows guarded refusals, then acknowledges the turn

- Evidence. `MemoryExtractor._store_extractions` catches and logs every
  storage and embedding exception:
  - an edge-embedding failure stores the edge with `embedding=None`
    (`extractor.py:572-592`);
  - relationship storage failures (`extractor.py:602-603`);
  - batched insights, then a per-insight fallback (`extractor.py:652-680`);
  - the turn summary (`extractor.py:684-700`).

  Chat's maintained background `_extract_turns` re-queues a turn only when the
  result carries `error`. Otherwise it marks the turn `persistence_state="completed"`
  (`adapters.py:1145-1184`). The Runtime Agent archive path logs and drops the
  failure (`friday_agent/base.py:498-522`). Compaction, by contrast, aborts
  before `mark_turns_compacted` (`compactor.py:435-462`), so the annex is right
  that compaction already reports failures.
- Defect. Under the new shared guards, overflow, readiness, identity and
  invalid-result refusals during maintained extraction become logged warnings.
  The turn is then acknowledged and loses retry eligibility, which the annex R
  definition forbids: "no swallowed error, successful no-op, lost retry
  eligibility". The edge path also turns a refusal into a vectorless edge, which
  FC-08's "genuinely absent vector" rule would then bless. FC-06 is scoped only to
  the public-unwired `MemoryConsolidator`. FC-08 addresses background *callers*,
  but the false acknowledgement originates inside the extractor. The extractor.py
  allowlist purpose ("embedding-role/capability/envelope propagation and narrow
  shape/refusal checks") does not clearly authorize changing failure aggregation.
  EC-08 and EC-14 are therefore not met.
- Narrow fix. Add an FC-06-equivalent clause for maintained extraction:
  1. Shared typed guard, readiness, identity, overflow and invalid-result errors
     in `_store_extractions` surface as an extraction failure (the result
     `error`, or a typed raise).
  2. Retry stays idempotent because records already use stable IDs with
     `upsert=True`.
  3. A vectorless edge is allowed only when no embedding model is configured,
     never as the result of a refusal.
  4. Mixed outcomes report failure.
  5. Unrelated non-guard errors keep their current policy.

  Extend the extractor.py purpose narrowly. Prompts, ontology and filtering stay
  unchanged.
- Future proof. B and N full-extraction positive. R: an injected refusal for an
  edge, an insight batch plus its fallback, and a summary. Each must re-queue the
  turn in Chat `pending_extraction`, store no vectorless edge, and not record a
  `completed` observation. Runtime agent background-extraction failure must be
  observable. Use canonical call-phase witnesses.

## Advisories (non-blocking)

| ID | Impact | Observation and recommended narrow disposition |
| --- | --- | --- |
| A1 | high | FC-09 feasibility: chromadb 1.4.0 (`uv.lock:489-490`) gives every non-persistent client the same identifier `"ephemeral"` (`.venv/.../chromadb/api/shared_system_client.py:58-62`, static read). So all `EphemeralClient`s in a process share one in-memory system. Runtime uses fixed `{base}_short/_long/_decayed` names (`di.py:291-297`). Two ephemeral kernels, possibly with different embedding identities, would share and mix collections. Name the isolation mechanism (per-incarnation tenant/database or collection naming within `vector.py`/`di.py`). Test two kernels with different identities in one process. |
| A2 | medium-high | Store-level swallow seams that FC-08/FC-13 require to propagate are unnamed: `CollectionManager.get_all` uses `return_exceptions=True` and returns warnings plus empty results (`collection_manager.py:421-431`); `_fetch_recent_insights`/`_fetch_recent_summaries`/`get_insights_by_author` catch everything (`memory_controller.py:326,1038,1193`). Name them and make the CollectionManager purpose cover the propagation change. Add a per-read identity-failure R test on priming insights. Chat MEMQ `query_memory_records` already projects explicit warnings (`adapters.py:593-640`), which is acceptable. |
| A3 | medium | Add explicit public-unwired dispositions for Tools `MemoryMaintenanceTool` (backup plus full reorganize), `MemoryResetTool` (`clear()` on the graph/front vector store) and `GraphInspectionTool`/`VectorInspectionTool` (`friday_tools/memory/maintenance.py:13-118`, `inspection.py:12-120`). Do the same for Chat `FrameworkMaintenanceAdapter.reorganize`/`reorganize_memory` legacy `MemoryReorganizer` paths: non-dry-run is disabled by `reorganization_execute_status` (`adapters.py:780-799,1050-1066`), the dry-run analyzer/pruner/synthesizer still runs if the method is called, and maintained `/reorganize` goes through the coordinator (`commands/registry.py:393-430`). |
| A4 | medium | Runtime `_friday_tools_catalog` imports **every** `friday_tools` module through `pkgutil.walk_packages` at registry build and raises `ToolProviderLoadError` on any import failure (`friday_runtime/tool_loading.py:60-83`). Name it as the concrete minimal-install witness that the new `readers/document_ingestion.py` (and any new `friday_llm.embedding_limits`) imports with no Docling or counter extras. |
| A5 | medium | FC-05: `MemorySynthesizer` accepts duck-typed embedders (`embed_query`, `.embed`, a bare callable; `synthesizer.py:707-737`) and uses query-role `embed_query` for stored text. State that only identity-bearing guarded services qualify. Duck-typed callables either refuse, which must then join the disclosed exception list, or have a defined qualification route. |
| A6 | low-medium | FC-11 says "any real provider probe". The maintenance preflight also probes the SYNTHESIZER LLM (`pipeline.py:512-534`) before the embedding probe (`pipeline.py:536-559`). Clarify whether LLM probes must also follow namespace admission, matching the REM matrix's "no model/provider" on refused rows. |
| A7 | low | EC-18 coherence: the REM "Next decision" paragraph (`REM:1344-1350`) still says the maintainer authorizes "up to three further full fresh councils (rounds2–4)". That contradicts the current four-pass, round 6–9 authority stated at `REM:29-33` and in the authorization JSON. Mark it historical or update it. |
| A8 | low | FC-01: Chat `logging.extraction_rejections_file` (`config.py:272-274`; packaged template line 9, `.friday/extraction_rejections.log`) has no consumer in `src`. Record it as inert so an implementer does not wire a second rejection handler outside the layout manifest. |
| A9 | low-medium | B02's hosted default `text-embedding-3-small` (`adapters.py:1749`; CLI `container.py:63-67`) may not meet the hosted immutable-identity rule (REM 728-738, annex 75-82). That would make Gate A hard-stop on the default non-pool baseline. The design correctly treats this as a stop rather than an exclusion; give the maintainer early visibility. |
| A10 | low | FC-04: the analyzer also opens transcript SQLite with `sqlite3.connect(path)`, which creates absent files (`analyzer.py:103,206`), in addition to Chroma (`analyzer.py:137-146`). Make "read-only, no creation" explicit (`mode=ro` URI) for the transcript database as well. |

## Criterion rows — EC-01..18

| ID | Verdict | Evidence |
| --- | --- | --- |
| EC-01 | Met | Request SHA, helper, wrapper, extractor and controls hashes verified. The extracted controls equal the frozen `current-controls.json` (`controls-copy.json`). Controls state pass 1/4, rounds 6–9, `implementation_approval: not_granted`, `product_changes_authorized: false`. Authorization JSON is design-only. No old verdict is reused. |
| EC-02 | **Not met** | The inventory is broad and independently confirmed: no Memory/LLM embedding imports in MCP, Speech, Sandbox, Finance, Moltbook, Optimization, Commands, Telemetry or Transcript; `friday-tui` is untracked caches only. However, graph scoring is misclassified (M1), extraction swallow seams are missing (M3), and several public wrappers and seams are unnamed (A2–A4). |
| EC-03 | Met | Chat uses the pool default and ignores `embedding.embedding_service` (`adapters.py:1735-1746`; `config.py:467-470`); FC-10 preserves this with a warning. Non-pool default `text-embedding-3-small` (`adapters.py:1748-1760`). Runtime pool, explicit extraction and legacy paths (`di.py:196-241,341-372`). Annex B01–B08 matches the source. |
| EC-04 | Met (advisory A2) | `embed_query`/`embed_documents` interfaces are retained. Query-envelope consumers identified: `CollectionManager.query(query_embedding)` (`collection_manager.py:174-248`), controller recall (`memory_controller.py:497-519`), `ChromaVectorStore.query` (`vector.py:195-230`), and the direct `_collection.add` in promote/demote/reactivate (`collection_manager.py:556-686`), which falls under the CollectionManager allowlist. |
| EC-05 | Met | REM 644-663 and annex 50-82: optional fields, artifact-bound readiness record, explicit hard stop for an unqualified baseline, alias-swap control. |
| EC-06 | Met (advisory A5) | LLM owns preparation, counting and result validation (REM 689-691, 783-836). Memory owns admission (REM 840-892). Role audit names the `embed_query` synthesis and `embed_documents` query-fallback callers (REM 793-803). |
| EC-07 | **Not met** | M1 (sync scorer is not maintained) and M3 (refusal manufactures "absent" edge vectors). Identity envelopes on graph writes (`pipeline.py:1049-1058`, `mutation.py:312-321`) are adequately specified. |
| EC-08 | **Not met** | M3. Separation of extraction LLM from embedding service is correct: Chat passes `embedding_model=embedding` (`adapters.py:2075`); Runtime uses an explicit `extraction_embedding_service` (`di.py:350-357`). |
| EC-09 | Met | FC-05 and FC-11, the v2 recovery identity design (REM 967-1047) and the direct-opener admission list (REM 951-965). `VectorCollectionDimension≤8192` confirmed (`mutation.py:196-200,255,300,314`). |
| EC-10 | Met | FC-07 matches the source: counts are taken before mutation (`promotion.py:423-431,463-471`) and tool text omits errors (`friday_tools/memory/lifecycle.py:38-53`). Compaction reports failures (`compactor.py:435-462,592-640`). Document/512 is limited to ingestion (REM 535-541, 692-694). |
| EC-11 | **Not met** | M2 adds an unapproved refusal mode to an enabled public CLI and API. Otherwise lazy assembly (REM 934-944) and startup/exit handling (REM 1146-1154) are adequate; A4 noted. |
| EC-12 | Met (advisory A1) | Changed-dimension, same-dimension/different-space, smaller-capacity N and the explicit fresh vector/graph/WAL layout (annex 21-36; REM 1083-1144). No deletion or migration is authorized. |
| EC-13 | Met (advisory A1) | Annex 37-39 and REM 684-688, 660-662. Ephemeral isolation feasibility depends on A1. |
| EC-14 | **Not met** | M3, with A2 contributing. Overflow and full-result validation design (REM 805-836) is otherwise strong. |
| EC-15 | **Not met** | DI-18/21/22/27-34 and the annex node table are comprehensive, but the FC-08 node targets a non-existent maintained route (M1), no extraction-acknowledgement node exists (M3), and FC-03 lacks a create positive (M2). Future Gate-A and installed tests were correctly not demanded now. |
| EC-16 | Partially met | Narrow rows are explicit (REM 1215-1265; annex 311-316). M3 needs a narrow extractor.py purpose extension. M1 must remain non-wiring. |
| EC-17 | Met (advisory A4) | Tools companion is coherent with FC-02/13 and does not touch MCP (`tools-document-adoption.md:9-20`). The Certifi floor (REM 294-331) and the Docling extra on Tools/Chat only are retained. FC-12: Memory pins `friday-framework-llm==0.1.0a4` (`friday-memory/pyproject.toml:11`); Runtime, CLI and Agent depend on Memory, so the extra is inherited. |
| EC-18 | Met (advisory A7) | Pins, status and board are coherent (five admin checks pass). Correction map claims no closure. Matrices and scores are below. |

## Criterion rows — FC-01..14

| ID | Verdict | Source reality / disposition |
| --- | --- | --- |
| FC-01 | Met (A8) | `configure_rejection_logging` runs `mkdir(parents=True)` and installs a FileHandler (`extraction_filter.py:43-67`), called from the `MemoryExtractor` constructor (`extractor.py:210-212`). Chat constructs it at startup (`adapters.py:2060-2090`) and Runtime in `_create_context_engine` (`di.py:359-373`). The packaged template places the log in `.friday/vector/` (`config_templates/config.example.yaml:71`). Deferral plus a stale-target refusal is feasible within allowed paths. |
| FC-02 | Met | Active opt-in route verified: Chat `prepare_mcp_memory` → `MCPMemoryIngester.prepare` (`adapters.py:309-336`) → `stage_mcp_snapshot` → `add_to_short_term` (`collection_manager.py:481-503`); receipts are in `memory_mcp.py:126-230`. Generic `except Exception → storage_failed` (`mcp.py:187-188`) needs typed overflow mapped to `oversized` before it, which is within the allowed mcp.py purpose. Single-record, no-split semantics are coherent. |
| FC-03 | **Not met** | See M2. |
| FC-04 | Met (A10) | Root probing (`analyzer.py:137-146`) and SQLite opens (`analyzer.py:103,146,206`) verified. Store-only admission, read-only open and no provider are feasible. |
| FC-05 | Met (A5) | Root probing plus `PersistentClient` (`synthesizer.py:174-191`). `collection.add(**add_kwargs)` without embeddings when `_embedding_function is None` (`synthesizer.py:707-795`). Module CLI disables non-dry-run (`__main__.py:435-446`). |
| FC-06 | Met for its declared scope | `MemoryConsolidator` has no src callers (exports only, `context/__init__.py:23`, `friday_memory/__init__.py:32`). `mark_events_consolidated` follows `_summarize_turns`, whose per-batch `except` swallows storage (`consolidator.py:198,358-369`). Scope is insufficient for the maintained analogue; see M3. |
| FC-07 | Met | See EC-10. |
| FC-08 | **Not met** | M1, with M3 interplay. Recall gather `return_exceptions` (`memory_controller.py:522-527`) and the graph `except` (`memory_controller.py:1639-1644`) are correctly targeted. |
| FC-09 | Met (A1) | Runtime builds a persistent `CollectionManager(path=chroma_path)` for every profile (`di.py:282-297`). Graph parent `mkdir` is unconditional (`di.py:246-247`). Core factories are at `profiles.py:56-115`. The correction is necessary and feasible subject to A1. |
| FC-10 | Met | Chat precedence (`adapters.py:1740-1746`). `FridayConfig` `default_factory` env fallbacks are forwarded as plain values (`container.py:70-72,109-133`). A typed internal sentinel is feasible. The "stop if origin cannot be preserved" clause is appropriate. |
| FC-11 | Met (A6) | Embedding probe ordering (`pipeline.py:536-559`). Chat maintenance probe issues a real `embed_documents` call (`friday_chat/reorganization/mutation.py:157-160`). Observed-row dimension and the 8192 ceiling (`mutation.py:628-640,196-200`). |
| FC-12 | Met (A4) | Dependency edges verified (`friday-*/pyproject.toml`). Memory keeps `tiktoken>=0.5.0` (`friday-memory/pyproject.toml:15`). |
| FC-13 | Met (A2, A3) | Agent `recall_memory`/`store_fact` are decorated Runtime builtins (`friday_agent/tools/builtins.py:90-200`). Multi-agent wrapper at `di.py:309-335`. MEMQ projection at `adapters.py:593-660`. Public preprocessing is classified as not a second chunk plan. |
| FC-14 | Met | Thresholds recorded and not retuned. Quality is separated into a later envelope (annex 266-273). |

## Original mandatory / high-medium requirement disposition (judged independently)

| Theme / IDs | Independent judgement |
| --- | --- |
| EC-01 rejection logging (OPUS-M1) | Closed at design level by FC-01 (A8 minor). |
| EC-02 MCP route (OPUS-M2) | Closed by FC-02. |
| EC-03 physical backup (SOL-R5-M01, OPUS-M3) | Safety closed, but **compatibility not closed**: the disposition over-restricts create (M2). |
| EC-04 analyzer (SOL-R5-M02, OPUS-M3) | Closed by FC-04 (A10). |
| EC-05 hidden embedder (OPUS-M3) | Closed by FC-05 (A5). |
| EC-06 consolidation acknowledgement (SOL-R5-M03, ASTRA-R5-001) | Closed for the consolidator; the same defect class in maintained extraction is **open** (M3). |
| EC-07 lifecycle counts (ASTRA-R5-002) | Closed by FC-07. |
| EC-08 recall/graph (OPUS-M4) | **Not closed**: the route premise is wrong (M1). |
| EC-09 profiles (OPUS-M5) | Closed by FC-09, with feasibility caveat A1. |
| OPUS-A1/A3/A5 (FC-10) | Closed. |
| OPUS-A4, ASTRA-R5-A02/OPUS-A8 (FC-11) | Closed (A6 minor). |
| SOL-R5-A02/OPUS-A6/A7/A11 (FC-13) | Substantially closed (A2, A3). |
| OPUS-A10 (FC-12) | Closed (A4 witness). |
| OPUS-A2 (FC-14) | Closed. |

## Independent consumer / disposition matrix (B = baseline, N = replacement, R = refusal)

Wiring class: **M** = maintained Chat/Runtime route; **P** = public, unwired; **I** = inactive/stub; **U** = unaffected.

| # | Consumer (source) | Class | Annex/REM coverage | B / N / R requirement | My disposition |
| --- | --- | --- | --- | --- | --- |
| 1 | `LiteLLMEmbeddingService` incl. LRU query cache (`friday_llm/embeddings.py:75-283,149-214`) | M | LLM row, FC-10/12, REM §E | B: same selection and cache; N: new identity, cache bound to identity; R: overflow, shape, index, nonfinite | Covered |
| 2 | Chat `FrameworkEmbeddingService`, `embed_text` (no src callers) (`adapters.py:263-270,1735-1760`) | M | FC-10, B01/B02 | B: pool default, hint warning; N: pool swap | Covered |
| 3 | Runtime pool/legacy DI (`di.py:196-241`) | M | B04/B05 | B/N positive; unrelated unused service failure isolated | Covered |
| 4 | CLI `FridayConfig` → `RuntimeConfig` (`container.py:43-133`) | M(compat) | B06, FC-10 | origin sentinel; env/explicit vs fallback | Covered |
| 5 | Core `create_vector_store`/`create_graph_store` (`profiles.py:56-115`) | M | FC-09 | four profiles | Covered |
| 6 | `ChromaVectorStore` ctor `PersistentClient`/`EphemeralClient` + `get_or_create` (`vector.py:54-92`) | M | admission, FC-09 | admission before client | Covered; **A1** |
| 7 | `SimpleVectorStore` (Chat front, Runtime ephemeral) (`simple_vector.py:168,335`) | M | Core/Memory row | ephemeral identity | Covered |
| 8 | `CollectionManager` query, `get_all`, MCP, promote/demote/reactivate with direct `_collection.add` (`collection_manager.py:174-686`) | M | allowlist, FC-02/07 | envelope, admission, role | Covered; **A2** |
| 9 | `MemoryController.recall` gather, priming, fetch (`memory_controller.py:416-560,998-1200`) | M | FC-08 | typed propagation | Covered; **A2** |
| 10 | `GraphPathScorer` sync/async (`graph_scorer.py:221-345`) | **P** (not M) | FC-08 says maintained | public-injected B/N/R only | **M1** |
| 11 | `MemoryExtractor` storage (`extractor.py:548-700`) | M | FC-01, extraction row | B/N full extraction; R must re-queue | **M3** |
| 12 | Rejection logging (`extraction_filter.py:32-69`) | M | FC-01 | deferral, stale-target refusal | Covered (A8) |
| 13 | Chat `_extract_turns` acknowledgement (`adapters.py:1145-1184`) | M | FC-08 (callers) | retryable on refusal | **M3** |
| 14 | Agent `_archive_turn` → background extraction (`friday_agent/base.py:413-522`) | M | FC-13 | observable failure | **M3** |
| 15 | Agent `recall_memory`/`store_fact` builtins (`builtins.py:90-200`) | M (Runtime decorated) | FC-13 | B/N/R | Covered |
| 16 | `MultiAgentMemoryController` (`di.py:309-335`) | M (mode-gated) | FC-13 | shared space, visibility | Covered |
| 17 | `InSessionCompactor` (`compactor.py:173-640`; Chat `adapters.py:2050`) | M | compaction row | reports failures | Covered, verified |
| 18 | `MemoryConsolidator` (`consolidator.py:136-370`) | P | FC-06 | acknowledgement | Covered |
| 19 | `MemoryPromotionService` / `PromotionLifecycleMaintenanceRunner` (`promotion.py:300-570`; Chat `adapters.py:1040-1048`) | M | FC-07 | true counts | Covered |
| 20 | Tools `LifecycleTool` (`friday_tools/memory/lifecycle.py:10-55`) | P | FC-07 | text errors | Covered |
| 21 | `MCPMemoryIngester` + Chat persistence (`mcp.py:38-190`; `memory_mcp.py:126-230`) | M (opt-in) | FC-02 | oversized/storage_failed | Covered |
| 22 | MAINT pipeline preflight, REEMBED, SYNTHESIZE (`pipeline.py:512-559,901-1060`); Chat maintenance provider (`friday_chat/reorganization/mutation.py:150-175`) | M | FC-11, B01/B07 | admission before probe | Covered (A6) |
| 23 | Memory mutation participant (`mutation.py:196-330,628-640,1217-1330`) | M | FC-11, recovery | 8192, empty-store dimension | Covered |
| 24 | Recovery snapshot/restore (`recovery.py:363-563,1333-1376`) | M | REM v2 | same-namespace only | Covered |
| 25 | Pruner, synthesizer, fact checker root probing (`pruner.py:105-114`; `synthesizer.py:174-191`; `fact_checker.py:131-140`) | P/legacy | REM 951-965, FC-05, DI-28 | no fallthrough | Covered |
| 26 | `ConsistencyAnalyzer` SQLite (`analyzer.py:95-240`) | P | FC-04 | read-only, store-only | Covered (A10) |
| 27 | `BackupManager` (`backup.py:55-390`) | P | FC-03 | create B/N must work; restore R | **M2** |
| 28 | `MemoryReorganizer` + Chat legacy adapter methods (`reorganizer.py:84-1240`; `adapters.py:784-1113`) | P (execute disabled) | FC-03/04/05 row | dry-run admission | Covered (A3) |
| 29 | Module CLI `python -m friday_memory.maintenance` (`__main__.py:330-560`) | P | FC-03/05 row | backup enabled → M2 | **M2** |
| 30 | Tools `MemoryMaintenanceTool`, `MemoryResetTool`, inspection tools | P | not named | admission, backup | **A3** |
| 31 | smart_read, `large_file_processor`, `ToolOutputIngester` | P/M | REM routes | shared plan | Covered |
| 32 | `lifecycle/migration.py`, Chat migrate stub | I | annex row | no credit | Covered |
| 33 | Runtime tools catalog `walk_packages` (`tool_loading.py:60-96`) | M | ordinary registration row | import with no extras | **A4** |
| 34 | Chat MEMQ `query_memory_records`, ingested docs (`adapters.py:593-660`); `friday_commands/memory_queries.py` | M | FC-13 | store-only, explicit warnings | Covered |
| 35 | Transcript SQLite store; Telemetry | U | annex row | unchanged | Covered |
| 36 | MCP, Speech, Sandbox, Finance, Moltbook, Optimization, Commands (rg: no Memory/LLM-embedding imports) | U | annex row | minimal import | Covered |
| 37 | Tools codegen (`friday_tools/codegen/tool.py:23,160`, LLM only) | U | nonembedding row | unchanged | Covered |
| 38 | CLI `SessionConfig.embedding` dict (`session.py:46,87,116`) | I (inert) | — | none | Unaffected |
| 39 | Chat `logging.extraction_rejections_file` (`config.py:274`) | I (inert) | — | none | A8 |
| 40 | `packages/friday-tui` (untracked caches only; `git ls-files` empty) | — | — | — | Not a package |

## B01–B08 configuration matrix

| ID | Source-backed selection | B (baseline positive) | N (replacement positive) | Qualification / status |
| --- | --- | --- | --- | --- |
| B01 | Chat pool: memory = `embedding_pool.default_service` (`adapters.py:1740-1746`); maintenance = explicit pool service (`friday_chat/reorganization/mutation.py:266-296`) | Feasible; extraction shares the memory service | Feasible via profile swap and fresh namespace | Gate A: local LM Studio/Nomic identity attestation |
| B02 | Chat non-pool: `embedding.model or "text-embedding-3-small"`, LLM endpoint fallback (`adapters.py:1748-1760`) | Feasible if hosted identity qualifies | Feasible | **Hard-stop risk** (A9) |
| B03 | Sanitized Chat compatibility fixture | Must be created at Gate A (not inspected; dirty YAML excluded) | — | Absent revision not invented (annex 61) |
| B04 | Runtime pool, optional extraction service (`di.py:196-241,341-372`) | Feasible | Feasible | Gate A |
| B05 | Runtime legacy `embedding:` → `EmbeddingServiceConfig` (`di.py:217-231`) | Feasible | Feasible | Gate A |
| B06 | CLI `FridayConfig` env/default (`container.py:63-72`) | Feasible with origin sentinel (FC-10) | Feasible | Stop if origin is unpreservable |
| B07 | Chat inline `maintenance.embedding` (`config.py:516`; `friday_chat/reorganization/mutation.py:284-296`) | Feasible; same-space check when sharing a namespace | Feasible | Gate A |
| B08 | Memory `MaintenanceConfig.embedding` ("falls back … or ChromaDB default", `maintenance/models.py:466-469`) and injected `EmbeddingModel`s | Feasible for guarded services; Chroma default removed (FC-05) | Feasible | A5: duck-typed embedders |

## Checks (all Git/admin through the supplied wrapper; outputs in own scratch)

| Check | Command | Exit | Result |
| --- | --- | --- | --- |
| integrity-start | wrapper → `check_integrity.py review-request.json` | 0 | PASS, logical index `7ff069ba…087`, 17,673 protected entries, 0 failures (`start-integrity.json`) |
| current-controls | `python3 -B extract_current_controls.py` → `controls-copy.json` | 0 | Equal to frozen `current-controls.json` |
| board | `uv run --offline --frozen --no-sync --no-python-downloads python -B scripts/friday-dev-board.py validate` | 0 | "Development board validation passed: 36 tasks" |
| dashboard | `… scripts/friday-dev-board.py render --check` | 0 | "Planning dashboard is current" |
| docs | `… scripts/check-documentation-lifecycle.py` | 0 | "Documentation lifecycle validation passed: 1004 Markdown files checked" |
| metadata | `… scripts/check-package-metadata.py` | 0 | "Validated 18 pyproject.toml files …" |
| whitespace | `git diff --check 91ac63ba..8d25d53a` | 0 | No output |
| diffs | wrapper `git diff --stat` and `git diff` over the technical paths and status paths only | 0 | `tech-diff.patch` (870 lines), `status-diff.patch` (270 lines) |
| integrity-end | same helper, after the final shared inspection | 0 | PASS, identical index, candidate and branch, 0 failures (`end-integrity.json`) |

A first attempt to run the five admin checks returned exit 127 for every command. zsh did not word-split the wrapper variable, so no wrapper or child process started (`checks-attempt1-not-executed-zsh-wordsplit.txt`). The checks were then rerun correctly with argv arrays; those reruns are the results above. `command-audit.jsonl` records every wrapped invocation.

## Reproduced vs inspected vs future

- **Reproduced:** integrity start and end, controls extraction and comparison, five admin checks, amendment diffs.
- **Inspected statically:** full current REM (1,350 lines), annex (316), Tools companion (166), store policy, authorization, correction map, scope decisions, status deltas. Source in all maintained packages, cited above, including a static read of the installed chromadb source for A1.
- **Future and not requested:** Gate A model, dependency and counter feasibility; B/N/R and installed normal/`-O` execution; product imports or tests.

## Limits, isolation and output audit

- No writes to the checkout or to the supplied inputs. All outputs are in own scratch. No product imports, tests, builds, installs, downloads, provider calls or store operations.
- `authority.json` was not opened or grepped; only the verified extractor read it. No raw historical review reports or aggregate diffs were read; historical `report.md` links appeared only inside the status diff and were not followed.
- **Conduct deviation, disclosed:** one broad `rg 'extraction_rejections'` incidentally matched three lines (8, 9, 94) of the dirty `packages/friday-chat/config.example.yaml`. They were key/path lines identical in shape to the packaged template. I did not use them as evidence; FC-01 and A8 rely only on the packaged `config_templates/config.example.yaml` and `src`. Every later search excluded both dirty YAMLs. This was a read, not a write, and I did not open the file. I do not treat it as one of the request's defined BLOCKED triggers (a shared or input write, an authority/history isolation breach, or an unwrapped Git/admin command). The controller may weigh it differently.
- Static reads of installed `.venv` third-party source (chromadb) were used only for A1. No personal stores, `.friday-old` or exports were read; only the integrity helper touched them.

## Scores and rubric breakdowns

**Coverage 7.7 / 10**

| Component | Weight | Score | Rationale |
| --- | --- | --- | --- |
| All-framework direct/transitive consumer coverage | 4.0 | 3.1 | Broad and mostly verified. M1 misclassification, M3 missed seam, A2–A4 unnamed. |
| Baseline/replacement positive proof coverage | 3.0 | 2.4 | Strong B01–B08 and N design. FC-03 create positive is missing; the FC-08 positive is anchored to a non-existent route. |
| Negative identity/overflow/failure-effect coverage | 2.0 | 1.4 | Overflow and result guards are excellent. Extraction and get_all swallow loopholes remain. |
| Headless/minimal-install/nonembedding coverage | 1.0 | 0.8 | FC-12 is coherent. The tools-catalog import witness is unnamed. |

**Overall 8.0 / 10**

| Component | Weight | Score | Rationale |
| --- | --- | --- | --- |
| Framework consumer inventory | 2.0 | 1.55 | As above. |
| Operational configuration and API compatibility | 3.0 | 2.45 | FC-10 and B01–B08 are accurate; M2 conflicts with the premise. |
| Model replacement and namespace data safety | 2.5 | 2.0 | Sidecar, incarnation and v2 recovery design is strong. M1, M3 and A1 reduce it. |
| Bounded proof and reporting | 2.0 | 1.55 | Detailed node matrix; three nodes need correction. |
| Scope and authority | 0.5 | 0.45 | Clean design-only bounds; A7 stale paragraph. |

No acceptance, construction, Gate A or delivery follows from this review.
