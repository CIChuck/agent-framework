# REM-CMD-INGEST-001 — compatibility cycle pass3/4 (global round8) — Opus seat review

Reviewer: claude-opus-5-5, high effort, fresh independent read-only design/source-feasibility review.
Date: 2026-11-10 (request recorded 2026-11-11T03:32:36Z).
Review mode: correction delta first (f1916747..f43368c5, explicit technical/status paths), then the full current REM, normative annex and Tools companion, plus an independent all-framework consumer audit. This is not implementation conformance.

## Formal outcome

**VERIFIED** for design readiness of this document candidate. No mandatory findings. Six advisories are recorded below.

- **Coverage score: 9.5 / 10** (rubric breakdown in §3)
- **Overall score: 9.5 / 10** (rubric breakdown in §3)

Scope of the verdict:
- It is a static design/source-feasibility judgment of candidate `f43368c503da19fd245730ee579806db95ed3748` only.
- It grants no Gate-A, construction, model, store, reset, migration, MAINT-acceptance or delivery authority.
- No runtime, installed, quality or acceptance assurance follows from it.
- Missing product code, missing tests and the future Gate-A/model/installed proofs are intentionally future work. They are not findings here.

## 1. Pins, integrity and checks

| Item | Value / result |
| --- | --- |
| Request | `review-request.json` SHA256 `0b9247701339f8fe25dce08d70ec08e8785fbe20c01ea1f4054bc4c51a0a202d`. Verified before reading. |
| Helper hashes | check_integrity.py `6ef84653…e9ca`; read_only_command.py `cb0669f8…a248`; extract_current_controls.py `a9fd727a…4b81`; current-controls.json `ea18945e…20e8`. All match before and after the review. |
| Candidate / branch | `f43368c503da19fd245730ee579806db95ed3748` on `feature/cmd-ingest-001`. Base `91ac63ba…`; amendment base `f1916747…`. |
| Logical index | `d5b9549f8299653d66f6890c54af31f072a63687088a369be3dff0fac9be5e8d`. The helper measures it before status. |
| Start integrity (through the wrapper) | exit 0, PASS: 17689 protected entries, six preserved records, all pins. Output in `OWN/start-integrity.json`. |
| current-controls | Extractor inspected and run with `python3 -B`. Output `OWN/controls-copy.json` is byte-identical (cmp) to the frozen controls; SHA `ea18945e…`. Whole `authority.json` was never opened or grepped. |
| board validate | exit 0: "Development board validation passed: 36 tasks". |
| dashboard render --check | exit 0: "Planning dashboard is current". |
| docs lifecycle | exit 0: 1012 Markdown files checked. |
| package metadata | exit 0: 18 pyproject files validated. |
| whitespace `git diff --check base..candidate` | exit 0, empty output. |
| End integrity (through the wrapper) | exit 0, PASS, identical logical index, no failures. Output in `OWN/end-integrity.json`. It ran after the last shared/Git inspection. |

All four `uv` checks ran as `uv run --offline --frozen --no-sync --no-python-downloads python -B …` through the wrapper.

Procedural disclosure:
- My first attempt to run the five admin checks used zsh string variables, which zsh does not word-split. The shell returned 127 "no such file" for the whole string, and nothing was executed: the wrapper was never invoked and no command reached Git or uv. I then reran each check with an explicit argv through the wrapper; those runs are the results above.
- The static controls extractor was run directly with `-B`, as the request allows.
- The installed chromadb source was read statically with grep. This is permitted as a backend source read and is not execution proof.
- No other unwrapped Git/admin command was run.

## 2. Correction delta first (f1916747..f43368c5)

| Delta | Independent judgment |
| --- | --- |
| Causal boundary (annex §"Causal boundary") | Coherent and correctly scoped. Every edit must name the new embedding/config/identity change that requires it. Each finding is classified as a regression, a direct adaptation or a pre-existing unwaived baseline. A baseline label never waives a new unsafe effect; such a case stops readiness. MCP and backups are treated as consumers, not new features. |
| FC-02 retention and existing reasons | Matches source (§4, challenges 2–3). |
| FC-03 minimum binding | Matches source. FU-014 classification is source-correct (§4, challenge 4). Advisory A1 applies. |
| FC-08 absent and present matrix | Matches `graph_scorer.py` (challenge 1). |
| FC-01 no-file / standalone sink | Matches `extraction_filter.py` / `extractor.py`. |
| FC-06 close admission and late outer arrival | Matches `assembler.py` / `base.py`. |
| FC-09 suffix choice | Matches the static installed Chroma `SharedSystemClient` source. |
| FC-11 mutation scope | Matches `_collection_dimension`. |
| FC-13 metadata consumers and FU-013 | Matches source. |
| REM allowlist rows | Narrowed consistently to these purposes. |
| upgrade-log FU-013 / FU-014 | Statically accurate. Both are recorded as unwaived and given no positive credit. |
| Correction map | Adds pass2 corrections IC-07..IC-11, advisories OPUS-R7-A1..A9 and a history_restoration record. These are requirements only; I located every one in the normative text independently and did not take closure from the map. |
| Status docs, board and dashboard | The current gate moves to pass3/round8 with one further pass maximum. The execution-log entry records the pass2 CHANGES_REQUESTED scores as history only. |

**Challenge 5 (history).**
- I extracted README.md, next-phase.md and tactical-plan.md at 8d25d53a, 91ac63ba, f1916747 and f43368c5 with wrapped `git show`.
- Counting `**Next gate:**` lines and excluding each file's current-gate line: README 1, next-phase 17, tactical-plan 17. That is 35 historical lines.
- At f43368c5 all 35 are byte-identical to 8d25d53a. At f1916747 they were not (they had been altered). Only the current-gate line and the status header line differ.
- Restoration is confirmed. Current authority is pass3/global round8, with at most one more pass and then stop for guidance (`compatibility-iteration-authorization.json`, controls `additional_corrections_remaining: 1`).

## 3. Scores and rubrics

### Coverage — 9.5

| Rubric (weight) | Score | Basis |
| --- | ---: | --- |
| All-framework direct/transitive consumer coverage (4.0) | 3.85 | My sweep (§5) found no unlisted embedding caller, direct Chroma/SQLite opener or indirect vector writer missing from the annex table or REM allowlist. Residuals are A3 (scorer query-identity source) and minor unnamed but already-projected error dicts. |
| Baseline and replacement positive-proof coverage (3.0) | 2.85 | B and N positives are required for every maintained flow, including paired backup baselines and FU-013/014 with no credit. Residuals are A4 (`for_testing` origin) and A3. |
| Negative identity/overflow/failure-effect coverage (2.0) | 1.90 | Comprehensive R controls. A1 (marker-collision / restore-member witness) is not explicitly named. |
| Headless, minimal-install and non-embedding coverage (1.0) | 0.95 | FC-12 real catalog import, private copied-prefix control, lazy modules and `/read` independence. |
| **Total** | **9.55 → reported 9.5** | Rounded down; no score was adjusted toward the gate. |

### Overall — 9.5

| Rubric (weight) | Score | Basis |
| --- | ---: | --- |
| Framework consumer inventory (2.0) | 1.95 | Complete per the independent sweep. |
| Operational configuration and API compatibility (3.0) | 2.85 | B01–B08 are accurate to source. A2 (byte-oversize counter delta not named as an oracle exception) and A4 apply. |
| Model replacement and namespace data safety (2.5) | 2.35 | Strong. A1 and A3 are precision gaps, not unsafe designs. |
| Bounded proof and reporting (2.0) | 1.90 | Exact nodes and the normal/-O call-phase rule are present. A5 is a minor status-reference omission. |
| Scope and authority (0.5) | 0.50 | Causal boundary, no implied repairs, stop rules. |
| **Total** | **9.55 → reported 9.5** | |

## 4. Pass3 challenges — independent source findings

**1. Graph scorer.**
- `rg GraphPathScorer|graph_scorer= packages/*/src` finds no construction outside Memory itself.
- Chat `adapters.py:1810` builds `MemoryController(vector_store, graph_store, episodic_store, collection_manager, priming_config, recalc_interval)` with no `graph_scorer`.
- Runtime `di.py:299` builds it with no scorer either.
- So `_retrieve_graph_with_scoring` returns `base_result` early (`memory_controller.py:1590`). Maintained recall is unscored, makes zero graph-vector comparisons and needs no unused-vector preflight. Confirmed.
- Public API details:
  - Async `score_path` falls back only when `edge.embedding is None` / `target_node.embedding is None` and `embedding_fn` is given. Edge is computed first, then target, sequentially (`graph_scorer.py:248-258`).
  - Sync `score_path_sync` uses `embedding or []`, which gives zero.
  - `cosine_similarity` silently returns 0.0 on empty or mismatched input (`:36`).
- The annex FC-08 matrix correctly distinguishes these cases:
  - sync and async-without-fallback give zero;
  - async with a qualified `embedding_fn` fills only the absent components, scores them and does not backfill storage;
  - present foreign, unknown or invalid vectors fail before any fallback;
  - edge-only, target-only and both-absent witnesses with exact call counts, once-only preparation and normal/-O lanes are required;
  - no new wiring is added.
- Advisory A3 (identity source for the bare `query_embedding: list[float]`, and how `[]` is classified) is below.

**2. MCP retention.**
- `persist_mcp_interaction` (`memory_mcp.py:126-232`) has no discard call anywhere. The outer `try` only re-raises `CancelledError`.
- A `prepare_mcp_memory` exception becomes `MCPMemoryPersistenceError` (`:165`). An append failure falls back to readback (`:199-206`). A publish failure leaves the record pending (`:213-218`).
- Retry reuses the owned ID through `find_mcp_snapshot` and `_matching`, with no stage and therefore no embedding (`ingestion/mcp.py:101-115,154-160`).
- The existing contract `tests_chat/test_mcp_memory.py::test_public_retry_after_partial_outcome_preserves_owned_id` (parametrized false_append/ambiguous/readback/publish/cancel) asserts the same owned ID, unchanged `writes` and one row. `test_competing_pending_conflict_cannot_claim_or_delete_owner` keeps the pending record.
- The annex states this retention exactly and adds no cleanup, garbage collection, retry or schema. Confirmed.
- Pre-existing note: maintained `TurnProcessor` mints `uuid4()` turn IDs per turn (`processor.py:690`), so same-turn retry exists only for public callers. The annex correctly says records "remain pending … until a matching verified receipt", which is a baseline orphan and not a new effect.

**3. MCP reason boundary.**
- `MCPEventReason` (`friday_telemetry/models/mcp.py:27-79`) already contains `capped`, `unavailable`, `rejected`, `invalid_result`, `execution_error` and `blocked`, as well as `ingestion_disabled`, `skipped`, `pending` and `published`. The proposed union is a strict subset with no new literal.
- The processor forwards the reason verbatim: `observe=lambda name, reason: provider.emit_event("ingestion_decision", …)` (`processor.py:704-709`).
- `RuntimeMCPProvider.emit_event` increments `_ingestion_counts[reason]` before the strict `MCPEvent` export. Export exceptions are swallowed in `MCPTelemetryHelper.emit`, and `_observe` suppresses observer exceptions.
- So an off-contract literal would silently increment a bogus counter and drop export. The annex's requirements are therefore the right ones: a strict subset, with counts tested with export disabled and acceptance tested with export enabled.
- Guard placement: `prepare_mcp_memory` and `verify_mcp_memory` construct `MCPMemoryIngester(self.collection_manager)` (`adapters.py:316,333`). Staging goes `stage_mcp_snapshot → add_to_short_term → embedding_function.embed_documents` on the exact labelled/escaped stored text (`mcp.py:126-135,166`). So the guard is reached with no new counter, constructor or protocol.
- Typed-order risks that the annex must and does pre-empt:
  - the ingester's `except Exception → storage_failed` (`:187`);
  - `except ValueError → MCPMemoryOwnershipError` around `find_mcp_snapshot` (`:107`);
  - `except (ValueError, UnicodeError) → ineligible` (`:152`).
  - FC-02 explicitly requires typed refusals ahead of the ineligible/ValueError and storage_failed/Exception catches.
- Matching reuse stays store-only. I found no actual bypass and no newly introduced masking. Advisory A2 applies.

**4. Public physical backups.**
- `BackupManager(memory_dir, backup_root=None → memory_dir/backups)`.
- `_find_files_to_backup` copies fixed root `MEMORY_FILES` plus a recursive copy of `memory_dir/vector/**` only (`backup.py:137-156`).
- Restore copies every manifest member back unconditionally after an optional checksum pass (`:273-326`).
- FU-014 is source-correct:
  - The vector-directory form `D` copies only root files such as `chroma.sqlite3` and omits per-segment UUID directories.
  - One `memory_dir` cannot express Runtime's separate `runtime_data_root/memory/graph.json`.
  - Runtime constructs no BackupManager (callers are only the Memory `__main__`, `MemoryReorganizer` and the Tools `MemoryMaintenanceTool` wrapper).
  - Chat's `reorganize` passes the vector directory but keeps non-dry-run execution disabled.
- The old defaults are "nonrecursive" as claimed:
  - `D/backups` is outside the rglob scope in both forms.
  - In the vector form it sits inside the vector root, which is pre-existing and preserved under the causal boundary.
- The minimal fixed-marker selector (`D/embedding-space.json` vs `D/vector/embedding-space.json`, exactly one ready) fits the old signature. No configured identity is needed for create. Restore compares the receipt to the live marker.
- Nothing requires a new layout or engine. I found no unsafe introduced identity dependency that cannot be met within scope.
- Precision gap A1: in the parent form, rglob now captures `vector/embedding-space.json`, and an explicit `backup_dir` equal to a bound root could receive evidence named like a marker.
- Paired baseline/candidate proof is required before construction. No runtime failure is claimed here.

**5. History.** Confirmed in §2.

**6. Other source corrections.**
- **ContextAssembler.** `extract_context` creates an unretained `asyncio.create_task` (`assembler.py:420`). The Agent outer task `_safe_extract_context` awaits only that scheduling call (`base.py:500-520`). Runtime `shutdown` stops only MCP (`di.py:135-147`). FC-06's owned task/status (telemetry off), close-before-drain, late-arrival skipped-unavailable and no `set_extractor` revival are all necessary and fit the `assembler.py`/`di.py` rows.
- **Extractor.** The edge-embedding exception produces a warning and a vectorless edge (`extractor.py:574-592`). Batch storage then per-item fallback (`:657-680`) uses stable uuid5 record IDs (`:693,:711`). A top-level exception becomes `{"error": …}` (`:457-459`). Chat `_extract_turns` treats either a raise or a `result["error"]` as failure and requeues (`adapters.py:1145-1186`). FC-06 is accurate.
- **Logging.** `configure_rejection_logging` is module-global and mkdirs (`extraction_filter.py:32-69`). The extractor calls it at construction (`extractor.py:211-212`). Chat `logging.extraction_rejections` and `_file` have no consumer beyond their fields (`config.py:273-274`). The packaged log is `.friday/vector/extraction_rejections.log`. FC-01's per-owner, no-file and standalone separation is coherent.
- **Recall seams.** All are named:
  - recall `gather(return_exceptions=True)` unpack to `[]`/`{}` (`memory_controller.py:522-526`);
  - `CollectionManager.get_all` gather/warn (`collection_manager.py:421-431`);
  - `_retrieve_graph_with_scoring` broad except (`:1639`);
  - `_fetch_recent_*` and `get_insights_by_author` catches.
- **Profiles.** EPHEMERAL/TESTING use a `SimpleVectorStore` front store, but Runtime's lifecycle `CollectionManager(path=chroma_path)` builds `PersistentClient` regardless of profile (`di.py:286-291`; `vector.py:83-86`). Runtime also mkdirs the graph parent unconditionally (`di.py:248`). This confirms both FC-09's declared exception and its no-mkdir rule.
- **Chroma isolation.** Static chromadb 1.4.0 `SharedSystemClient` keys non-persistent systems by a shared identifier, so isolation by collection-name suffix is required. The tenant alternative is documented but not mixed in.
- **FC-11.** `_collection_dimension` infers from the first row and returns None when empty (`mutation.py:628-641`). The 8192 ceiling is at `:200,255,300,314`. The annex substitution and graph-only REEMBED purpose are exact.
- **Metadata consumers.** `flush_memory` ignores `flush_all` errors (`adapters.py:745-752`). `run_maintenance` incremental is at `:880-881`. Lifecycle commands project `errors`. This justifies FC-13's projection as a direct guard adaptation, since new per-read/write admission refusals would otherwise be swallowed.
- **FU-013.** `VectorInspectionTool` calls `controller.vector.search` (`inspection.py:134`). Neither vector adapter defines `search`. The issue is confirmed, the defect is pre-existing, and it receives no credit.

**7. B01–B08 and preservation.** See §6. FC-12 seams are confirmed:
- the Runtime catalog uses `pkgutil.walk_packages` + `import_module` (`tool_loading.py:60-79`);
- Memory pins `friday-framework-llm==0.1.0a4` (the extra can be requested there);
- Runtime and Chat also pin LLM directly, which is harmless because extras are unioned.

The Certifi floor, format feasibility and the Tools companion stay coherent with Gate-A stop semantics.

## 5. Independent all-framework consumer and disposition matrix

Method:
- Broad discovery ran only under `packages/*/src`, with both dirty example YAMLs excluded.
- Patterns: `embed_query|embed_documents|embed_text|.embed(|embedding_function|EmbeddingModel|embeddings=`; direct openers `chromadb|sqlite3.connect|PersistentClient`; indirect writers `store_insight|store_summary|add_to_short_term|store_document(s_batch)|collection.add|upsert|add_documents`; and Memory/embedding imports in every non-core package.

| Consumer (actual route) | Kind | Source evidence | Annex/REM disposition | Judgment |
| --- | --- | --- | --- | --- |
| LLM `LiteLLMEmbeddingService`, `model_library` resolver | Maintained, shared | `friday_llm/embeddings.py`, `model_library.py` | Shared guard; B01–B08; FC-10/12 | Covered |
| Chat `FrameworkEmbeddingService` (`embed_text` → query role, unused) | Maintained | `adapters.py:258-270`; no `.embed_text(` caller in src | Role audit (REM E) | Covered |
| Core `create_vector_store`/`graph_store`, `MemoryProfile` | Maintained factory | `profiles.py:56-115` | FC-09/10 | Covered |
| Memory `ChromaVectorStore` / `SimpleVectorStore` / `CollectionManager` | Maintained | `vector.py:83-91`, `simple_vector.py:154`, `collection_manager.py:131-150` | Admission and envelopes | Covered |
| Chat front `SimpleVectorStore` (in-memory) plus persistent lifecycle | Maintained | `adapters.py:1795-1799` | "vector/simple stores" row | Covered |
| Recall / priming / insight / summary / get_all catches | Maintained | §4.6 | FC-08 | Covered |
| GraphPathScorer sync and async | Public-injectable, unwired | §4.1 | FC-08 | Covered (A3) |
| Extraction edges / insights / summaries | Maintained (Chat; Runtime optional) | `extractor.py`; `di.py:345-374` | FC-06 | Covered |
| ContextAssembler inner task and Agent outer task | Maintained (Runtime/Agent) | §4.6 | FC-06 | Covered |
| MemoryConsolidator | Public-unwired | `consolidator.py` | FC-06 | Covered |
| Chat compaction (`compactor.py`) | Maintained | writer hit | Compaction row | Covered |
| Promotion / decay / reactivation (re-embed on promote) | Maintained | `collection_manager.py:560+` | FC-07, REM E | Covered |
| `hard_delete_expired` / orphan cleanup error dicts | Maintained via Reorganizer lifecycle | `collection_manager.py:792-858`; `reorganizer.py:919-957` projects `report.errors` | MAINT pipeline row and FC-13 wrapper truthfulness | Covered (projected) |
| MAINT pipeline, provider_contracts, mutation, recovery | Maintained | embedding hits | FC-05/11, REM recovery | Covered |
| Synthesizer (`embed_query` / `embed` / callable shapes), pruner, fact_checker, analyzer (`[D, D/vector]` probing; `sqlite3.connect` rw) | Public legacy | `synthesizer.py:179,706-730`, `pruner.py:110`, `fact_checker.py:136`, `analyzer.py:103,136,146,206` | FC-04/05, DI-28 | Covered |
| BackupManager / module / Reorganizer backup_first / Tools wrapper | Public legacy | §4.4 | FC-03 | Covered (A1) |
| MCP snapshot route | Active opt-in | §4.2–4.3 | FC-02 | Covered (A2) |
| `ToolOutputIngester`, `LargeFileProcessor`, `SemanticChunker`, smart_read | Public / injected | writer hits | REM allowlist | Covered |
| `DocumentIngestionPipeline` | Public, prepares only (no storage) | `ingestion/pipeline.py:280` | Legacy preprocessing row | Covered |
| `lifecycle/migration.py`, Chat migrate stub | Inactive | embedding hit | Inactive row | Covered |
| Multi-agent controller / coordinator | Runtime opt-in | `di.py:312-336`; `coordinator.py` writer hit | FC-13 | Covered |
| Agent `recall_memory` / `store_fact` (graph-only, no vector) | Injectable | `builtins.py:89-204` | Agent row | Covered |
| Agent workflows engine | Enum import only | `engine.py:20` | Unaffected | Correctly unaffected |
| Tools `MemoryStatsTool` | Session-state only, no store access | `inspection.py:12-51` | Not named; no embedding/store effect | Unaffected (no action) |
| Tools `GraphInspectionTool`, `VectorInspectionTool` (FU-013), `LifecycleTool`, `MemoryReset` | Injectable | `inspection.py`, `lifecycle.py`, `maintenance.py` | FC-07/13 | Covered |
| Runtime `_friday_tools_catalog` | Maintained startup | `tool_loading.py:60-79` | FC-12 witness | Covered |
| CLI container / `FridayConfig` | Compat | `container.py:43-135` | FC-10, B06 | Covered (A4) |
| Telemetry / Transcript | Unchanged contracts | No Memory/embedding imports in src | Unchanged | Covered |
| Commands, MCP, Speech, Sandbox, Finance, Moltbook, Optimization | No Memory/embedding imports (0 hits each) | sweep | Unchanged | Correctly unaffected |

No unlisted embedding caller, direct opener or vector writer was found outside the annex/REM inventory.

## 6. B01–B08 qualification and status

| ID | Actual source behavior | Requirement | Status |
| --- | --- | --- | --- |
| B01 | Chat pool chooses `embedding_pool.default_service` and ignores `embedding.embedding_service` (`adapters.py:1740-1746`) | Preserve; disclose the hint as legacy no-op plus a warning; test divergent names | Accurate |
| B02 | Non-pool default `text-embedding-3-small`, `api_base`/key fallback to LLM (`adapters.py:1748-1760`) | Preserve. The hosted immutable-identity risk is an early Gate-A hard stop and is not silently dropped | Accurate; qualification unknown → Gate-A stop |
| B03 | Sanitized compatibility fixture | Absent revision is not invented | Gate-A fixture |
| B04 | Runtime pool default memory binding; optional `memory_extraction.embedding_service` (`di.py:348-357`) | Separate qualification; same-space check | Accurate |
| B05 | Runtime legacy `EmbeddingServiceConfig` path (`di.py:206-230`) | Same guard | Accurate |
| B06 | `FridayConfig.chroma_path` default-factory env/default forwarded into `RuntimeConfig` (`container.py:70-126`) | Origin sentinel; otherwise stop | Accurate (A4: `for_testing` literal) |
| B07 | Chat inline `maintenance.embedding` | Same-space when sharing | Covered |
| B08 | `MaintenanceConfig.embedding` / injected `EmbeddingModel`; synthesizer three shapes | FC-05 wrapper | Accurate |

Unknown qualification for any family is a Gate-A hard stop (annex lines 101-118), not a silent exclusion.

## 7. B/N/R compatibility matrix (design requirement sufficiency)

| Flow | B (unchanged config, fields omitted) | N (changed dimension AND same-dimension different identity, smaller capacity, fresh namespace) | R | Credit rule |
| --- | --- | --- | --- | --- |
| `/ingest` text + four formats | Required (DI-07/33) | Required (DI-20/33) | DI-04/09/21 | Positive |
| Turn store / recall / priming / insights / summaries | FC-08, DI-33 | FC-14 | FC-08 typed propagation | Positive |
| Extraction → graph edges / insights / summaries | FC-06 | FC-06 / FC-14 | No vectorless edge after refusal | Positive |
| Background ContextAssembler | FC-06 | FC-06 | Telemetry-off status, late arrival | Positive |
| Compaction / lifecycle / promotion | FC-07 | FC-07 / FC-14 | False-return counts | Positive |
| MAINT synth / REEMBED / prune / fact-check | FC-05 / 11 | Variable dimension, graph-only empty | Admission before any probe; 8192 ceiling | Positive |
| v2 snapshot / rollback | DI-27 / 32 | DI-27 | Tamper / identity | Positive (complete recovery path) |
| Public BackupManager create / verify / restore / backup_first / Tools / module | Paired baseline, old file sets / defaults | Same | Receipt / marker / clone | Positive only on already-working layouts; FU-014 forms get no credit |
| MCP snapshot | FC-02 | FC-02 | Overflow / typed / ownership | Positive |
| Injected scorer (sync / async) | FC-08 capability | FC-08 | Foreign / invalid before fallback | Capability proof, separate from route |
| Maintained unscored graph route | Zero-comparison spy | Same | n/a | Route proof |
| MEMQ / inspection / analyzer (store-only, provider offline) | FC-04 / 13 | Same | Refusal before open | Positive (VectorInspection query branch FU-013: no credit) |
| Runtime four profiles / two kernels | FC-09 | FC-09 | Ephemeral isolation | Positive |
| Headless installs | FC-12 | n/a | Missing counter assets | Positive |

Both scenarios require real successes. Refusal-only coverage is explicitly rejected (annex lines 13-30, 47-51, 568-571).

## 8. EC-01..EC-18

| ID | Criterion (abbreviated) | Evidence | Result |
| --- | --- | --- | --- |
| EC-01 | Four-pass authority, pins, design-only | Authorization json; controls `current_pass 3`/`maximum 4`/`product_changes_authorized false`; REM 30-38, 1356-1364 | Pass |
| EC-02 | Independent framework inventory | §5 sweep | Pass |
| EC-03 | Unchanged catalog/pool selection | §6; annex 120-127; REM 667-689 | Pass |
| EC-04 | API compatibility; envelope consumers | REM 889-893; annex table; FC-05 shapes | Pass |
| EC-05 | Optional fields from qualified readiness; stop on unknown | REM 645-666; annex 97-118 | Pass |
| EC-06 | LLM owns preparation/guard; Memory owns admission | REM 690-693, 784-805; FC-02 same-service counting | Pass |
| EC-07 | No scorer injection; sync/async capability proofs | §4.1; FC-08 | Pass (A3) |
| EC-08 | Typed extraction failures, Chat retry, owned task telemetry-off | §4.6; FC-06 | Pass |
| EC-09 | Backups operational, minimum binding, FU-014 paired, logical-v2 separate | §4.4; FC-03 | Pass (A1) |
| EC-10 | Lifecycle / compaction / derived; no re-chunk | REM 128-132, 167-173; FC-07 | Pass |
| EC-11 | Every package/entrypoint; wiring classes | §5; annex 162-166 | Pass |
| EC-12 | Changed dimension and same-dimension N; fresh roots | Annex 21-36; REM 1093-1154 | Pass |
| EC-13 | Shared-name space; independent namespaces; unrelated-service failure isolation | Annex 37-39; REM 661-663 | Pass |
| EC-14 | Capacity / overflow / result validation on every path | REM 806-837; FC-02 | Pass |
| EC-15 | DI-18/21/22/27-33 and Gate-A sufficiency | REM 1300-1316; annex 568-576 | Pass |
| EC-16 | Narrow allowlist purposes | REM 1225-1277; annex 578-583; causal boundary | Pass |
| EC-17 | Companion / security / Certifi / minimal installs coherent | REM 295-333; companion; FC-12 | Pass |
| EC-18 | State and pins coherent; matrices; honest scores | §1-3, §5-7; 35-line history check | Pass (A5) |

## 9. FC-01..FC-14

| FC | Source route / classification | Normative contract located | Scope | B/N/R and install proof | Result |
| --- | --- | --- | --- | --- | --- |
| 01 | Global logger and mkdir at extractor init; Chat flags inert; packaged log inside vector/ | Annex 170-199 | Memory filter / extractor, Runtime / Chat wiring | Two owners, standalone, failed setup, first-use CREATE_FRESH | Pass |
| 02 | Active opt-in; prepare → stage → `add_to_short_term`; no discard | Annex 201-272 | `ingestion/mcp.py`, `memory_mcp.py`, Chat delegation | Two nodes; enabled/disabled export; retry write-count | Pass (A2) |
| 03 | Fixed files + `vector/**`; old defaults; Runtime does not construct it | Annex 274-322 | `backup.py` / `__main__` minimum | Paired baselines; FU-014 no credit | Pass (A1) |
| 04 | rw `sqlite3.connect`, `[D, D/vector]` | Annex 324-331 | `analyzer.py` | Provider-offline positive | Pass |
| 05 | Three callable shapes; possible Chroma default | Annex 333-349 | synthesizer + wrapper | All shapes B/N | Pass |
| 06 | Vectorless edge; fire-and-forget task; Chat requeue | Annex 351-392 | extractor / assembler / consolidator / Runtime / Chat | Three nodes | Pass |
| 07 | Lifecycle counts / tool text | Annex 394-399 | promotion, Tools lifecycle | Execute text and structure | Pass |
| 08 | Unscored maintained route; catch seams | Annex 401-430 | controller, collection_manager, graph_scorer | Two labelled proofs | Pass (A3) |
| 09 | Persistent lifecycle under EPHEMERAL; shared ephemeral system | Annex 432-453 | `di.py` / config / factories | Four profiles, two kernels | Pass |
| 10 | Divergent hint; lost CLI origin | Annex 455-462 | resolver / CLI | B01–B08 fixtures | Pass (A4) |
| 11 | Probe ordering; empty-dimension inference; 8192 | Annex 464-475 | pipeline / provider_contracts / mutation | Variable, same-dimension, over-ceiling | Pass |
| 12 | Catalog walk; Memory LLM pin | Annex 477-494 | LLM / Memory pyproject | Real installs, copied-prefix control | Pass |
| 13 | Agent / multi-agent / MEMQ / inspection / metadata consumers; FU-013 | Annex 496-526 | Tools wrappers, Chat projection | Provider-offline reads | Pass |
| 14 | Thresholds unchanged | Annex 528-535 | none | Later quality envelope | Pass |

## 10. Findings

**Mandatory: none.**

**Advisory A1 (medium impact; FC-03; direct identity adaptation).**
- *Causal path:*
  - In the parent form, the unchanged `_find_files_to_backup` rglob of `memory_dir/vector/**` (`backup.py:149-154`) automatically captures the new live `vector/embedding-space.json` as an ordinary data member.
  - The unchanged restore loop copies every member back with `shutil.copy2` (`:306-319`). That is a non-atomic in-place rewrite of the live ready marker, even with the same incarnation.
  - Separately, the old API still accepts an explicit `backup_dir` that resolves to the bound root (`D` in vector form, or `D/vector`). An evidence copy named like the marker would land on the fixed marker path.
- The annex already forbids both outcomes ("never overwrite/recreate a ready/pending binding marker"; "require unchanged … live binding"; file sets compared "apart from new binding evidence"). The final directive should state the implied mechanics so a builder does not read "does not change the old file-set rules" as license to restore that member.
- *Fix:*
  - Name the captured sidecar, and any pending/lock/temp marker artifacts, as binding evidence that restore's live-write set excludes.
  - Make receipt and evidence filenames disjoint from both fixed marker names.
  - Add witnesses for `backup_dir ∈ {D, D/vector}` and parent-form restore that prove marker bytes, inode, mtime and ctime are unchanged.
- *Scope:* within the existing `backup.py` row. No layout, engine or default change.
- *Proof:* paired baseline/candidate node `test_public_backup_identity_and_unchanged_baselines`.

**Advisory A2 (low; FC-02; existing-counter delta).**
- Byte-oversize currently reaches the observer as `skipped`: `MCPMemoryPreparation("oversized")` → `_skipped` → `_observe(...,"skipped")` (`mcp.py:70-71,137-138`; `memory_mcp.py:167-168,229`).
- The annex maps byte or token oversize to `capped`. Because no new MCP preparation status or protocol is allowed, byte and token overflow share one status, so the relabel is causally entailed and not an opportunistic repair.
- It still changes the existing `operational_diagnostics.ingestion_decisions` counts for byte-oversize from `("skipped", n)` to `("capped", n)`.
- *Fix:* list that exact counter delta among the named oracle exceptions (REM 1319-1321). Keep the receipt `ingestion_decision="skipped"` unchanged, as the annex already says. `test_unlisted_failed_and_oversized_outputs_stay_transcript_only` asserts only the receipt, so no old assertion body changes.

**Advisory A3 (low-medium; FC-08 / EC-07; public-injectable only).**
- The public scorer APIs take a bare `query_embedding: list[float]`. FC-08 requires "validate compatible query/stored-vector identity" while keeping old signatures, but does not say where the query identity comes from. The options are a scorer bound at construction to the admitted identity, or an optional typed envelope accepted alongside the bare list.
- It also does not say how an empty `[]` stored vector is classified. Today it is not None, so async does not fall back and the score is zero; it could instead be treated as an invalid present vector.
- *Fix:* freeze both at Gate A. Require a witness that a bare query vector without a bound identity refuses instead of comparing.
- *Scope:* `graph_scorer.py` row. No wiring change.

**Advisory A4 (low; FC-10 / B06).**
- `FridayConfig.for_testing()` passes the internal literal `.friday/test_chroma` (`container.py:99-107`). It is neither user-supplied nor the dataclass default, and FC-10 does not classify that origin.
- *Fix:* name it explicitly in the B06 fixture. It should be internal, not explicit (no CREATE_FRESH) unless a TESTING/ephemeral profile applies; otherwise apply the stop-and-reconcile rule.

**Advisory A5 (low; EC-18 status coherence).**
- REM "Next decision" (lines 1356-1360) cites the pass1/round6 reconciliation but not the pass2/round7 reconciliation, which the execution log and board events do record.
- *Fix:* add one reference at the next correction. History lines must stay byte-identical.

**Advisory A6 (informational; pre-existing, unwaived, no action in this unit).**
- In maintained Chat, MCP turn IDs are per-turn `uuid4`, so the pending records retained after a failed turn have no maintained retry path. They stay pending and non-retrievable.
- Classification: pre-existing baseline. It is not new and not a waiver. The annex correctly adds no cleanup.

## 11. Coverage, limits and conduct

- **Inspected:**
  - All required authority reads, read in full except the policy files: those were skimmed for applicable rules, and the validation policy was read for outcome rules.
  - The full current REM (1364 lines), annex (583) and Tools companion (166).
  - The correction-map requirement lists.
  - The amendment technical and status diffs, by explicit path only.
  - The source files cited above, plus `tests_chat/test_mcp_memory.py` by explicit path.
  - Installed chromadb 1.4.0 `__init__` and `shared_system_client`, statically.
- **Reproduced:** the five admin checks, the start/end integrity helper, the controls extraction and comparison, and the 35-line history byte comparison.
- **Not performed / future:**
  - No product imports, tests, builds, installs, model/provider/store operations or Gate-A work.
  - Runtime behavior of every cited seam is inferred from static source only.
  - Normal/-O installed proofs, real counter/model feasibility, B02 hosted-identity qualification and paired backup baselines remain future obligations.
  - Legacy Ruff/collection/format/MAINT debt remains unwaived background and was not rerun.
- **Not read:**
  - whole `authority.json`;
  - raw council-round directories or old peer reports;
  - unfiltered aggregate diffs;
  - personal stores, `.friday-old`, exports or the two dirty YAMLs (excluded from every broad search, which was confined to `packages/*/src`).
- **Outputs:** all outputs are in `OWN=/tmp/claude-501/rev-pass3-opus-dWxlAV`, which is outside the checkout and outside all supplied input and scratch paths: start/end integrity JSON, controls copy, check logs, amendment diffs, the `hist/` status-doc extracts, `command-audit.jsonl` (wrapper audit, 22 wrapped invocations, all exit 0), the uv/xdg/tmp caches and this report.
- **Writes:** no shared-checkout or input writes, staging, commits, worktrees or cleanup. No nested agents or delegates, and no repairs.
- **Procedural note:** the one non-executed zsh variable-expansion attempt is disclosed in §1. It invoked nothing.
